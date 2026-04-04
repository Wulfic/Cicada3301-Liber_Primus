"""
GPU-Accelerated Hillclimber for Liber Primus P21-P54
=====================================================
Uses CuPy on dual RTX 2080 Ti GPUs.

Strategy:
 - Key = running sequence of GP values, length 14529 (= total P21-P54 runes)
 - Singleton constraints: each single-rune word MUST decrypt to I(10) or A(24)
 - Score: GP quadgram log-frequency table built from known LP + English text
 - Each GPU runs N_CHAINS independent Markov chains (simulated annealing)
 - Per chain: randomly perturb key[j], accept if score improves or by temp schedule
 - Output best candidates to file every SAVE_EVERY steps

Run:
  python gpu_hillclimber.py 0   # GPU 0 (modes: sub, add)
  python gpu_hillclimber.py 1   # GPU 1 (modes: beaufort + word-boundary search)

Usage: python gpu_hillclimber.py <gpu_id>

Outputs:
  data/gpu_hill_gpu0.txt
  data/gpu_hill_gpu1.txt
"""

import sys, os, time, math, json
from pathlib import Path
from collections import Counter
import numpy as np
import cupy as cp

sys.stdout.reconfigure(encoding='utf-8')

# ─── Config ─────────────────────────────────────────────────────────────────
GPU_ID    = int(sys.argv[1]) if len(sys.argv) > 1 else 0
N_CHAINS  = 2000           # parallel Markov chains per GPU
MAX_STEPS = 5_000_000      # total steps per chain (will run indefinitely until killed)
SAVE_EVERY = 10_000        # steps between saving results (print every ~45s)
OUTFILE   = f'data/gpu_hill_gpu{GPU_ID}.txt'
M         = 29

# Cipher modes to test on this GPU
if GPU_ID == 0:
    MODES = ['sub', 'add']
else:
    MODES = ['sub', 'add']  # sub confirmed correct mode

# ─── GP Alphabet ─────────────────────────────────────────────────────────────
IDX_TO = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA']
RUNE_TO_IDX = {chr(k): v for k, v in [
    (0x16A0,0),(0x16A2,1),(0x16A6,2),(0x16A9,3),(0x16B1,4),(0x16B3,5),
    (0x16B7,6),(0x16B9,7),(0x16BB,8),(0x16BE,9),(0x16C1,10),(0x16C4,11),
    (0x16C7,12),(0x16C8,13),(0x16C9,14),(0x16CB,15),(0x16CF,16),(0x16D2,17),
    (0x16D6,18),(0x16D7,19),(0x16DA,20),(0x16DD,21),(0x16DF,22),(0x16DE,23),
    (0x16AA,24),(0x16AB,25),(0x16A3,26),(0x16E1,27),(0x16E0,28)]}

LETTER_TO_GP = {
    'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
    'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
    'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':14,
    'TH':2,'OE':22,'AE':25,'NG':21,'EO':12,'IO':27,'EA':28
}

# ─── Data Loading ────────────────────────────────────────────────────────────
def load_page(pg):
    path = Path(f'pages/page_{pg:02d}/runes.txt')
    if not path.exists(): return [], []
    text = path.read_text(encoding='utf-8')
    runes = []; words = []; curr = []
    for ch in text:
        if ch in RUNE_TO_IDX:
            runes.append(RUNE_TO_IDX[ch]); curr.append(RUNE_TO_IDX[ch])
        elif ch in '-. \n\r\t\u2022/' and curr:
            words.append(tuple(curr)); curr = []
    if curr: words.append(tuple(curr))
    return runes, words

print('Loading cipher stream...', flush=True)
cipher_list = []
words_all = []
cum = 0
page_offsets = {}
for pg in range(21, 55):
    runes, words = load_page(pg)
    page_offsets[pg] = cum
    cum += len(runes)
    cipher_list.extend(runes)
    words_all.extend(words)

CIPHER = np.array(cipher_list, dtype=np.int32)
N_CIPHER = len(CIPHER)
print(f'  Cipher length: {N_CIPHER} runes', flush=True)

# ─── Two-time-pad constraints ───────────────────────────────────────────────
# Pairs of cipher regions with IDENTICAL cipher text → same key was reused.
# Enforcing key[src+i] == key[dst+i] reduces search space by ~26%.
TTP_CONSTRAINTS = [
    (3001,  9727, 1312),  # P27-P31 == P44[0:1312]
    (6298, 12311, 1468),  # P33[91:]+P34+P35+P36+P37+P38+P39[0:119] == P50
    (   0,  5803,  404),  # P21+P22 == P32[1490:1894]
    (2736,  8643,  265),  # P26 == P40[756:1021]
    ( 737,  8100,  172),  # P24[0:172] == P40[213:385]
    ( 910,  8273,   97),  # P24[173:270] == P40[386:483]
]

# Build link_map: position → canonical (lowest-index) position in its equivalence class
LINK_MAP = np.arange(N_CIPHER, dtype=np.int32)
for src_s, dst_s, ln in TTP_CONSTRAINTS:
    for i in range(ln):
        LINK_MAP[dst_s + i] = LINK_MAP[src_s + i]  # dst becomes canonical of src

INDEPENDENT_POS = np.array([i for i in range(N_CIPHER) if LINK_MAP[i] == i], dtype=np.int32)
N_INDEPENDENT = len(INDEPENDENT_POS)
print(f'  TTP constraints: {sum(ln for _,_,ln in TTP_CONSTRAINTS)} linked positions '
      f'→ {N_INDEPENDENT} independent key positions (was {N_CIPHER})', flush=True)

# ─── Confirmed crib anchors (key permanently fixed for sub mode) ─────────────
# These are phrases confirmed with near-perfect or perfect crib match in sub mode.
# Removing these positions from INDEPENDENT_POS prevents the hillclimber from
# accidentally mutating away from the known correct key values.
def _gp_encode(phrase):
    """Encode phrase string to GP rune indices using digraph priority."""
    w = phrase.upper().replace(' ', '')
    r = []; i = 0
    while i < len(w):
        if i+1 < len(w) and w[i:i+2] in LETTER_TO_GP:
            r.append(LETTER_TO_GP[w[i:i+2]]); i += 2
        elif w[i] in LETTER_TO_GP:
            r.append(LETTER_TO_GP[w[i]]); i += 1
        else:
            i += 1
    return r

# (phrase, global_start_position) — all confirmed for sub mode
CONFIRMED_CRIBS = [
    ('CONSUMPTION',         31),
    ('KNOWTHIS',           476),
    ('PROGRAM',            599),
    ('DIUINITY',          1356),
    ('PRESERUATION',      2093),
    ('SOMEWISDOM',        4131),
    ('THELOSSOFDIUINITY', 4325),   # 15/16 perfect match + LP context confirms
    ('CIRCUMFERENCE',     3080),   # 13/13 perfect match; TTP-1 verified at 9806
    ('ADHERENCE',         8532),
]

# Build pos→required_plain_value map
FORCED_CRIBS_POS = {}   # global_pos → plain rune index
for _phrase, _start in CONFIRMED_CRIBS:
    for _i, _v in enumerate(_gp_encode(_phrase)):
        FORCED_CRIBS_POS[_start + _i] = _v

# Canonical positions that are locked (exclude from mutation)
CRIB_CANON_SET = {int(LINK_MAP[p]) for p in FORCED_CRIBS_POS}

# Remove locked positions from the mutable independent set
INDEPENDENT_POS = np.array([p for p in INDEPENDENT_POS if p not in CRIB_CANON_SET], dtype=np.int32)
N_INDEPENDENT = len(INDEPENDENT_POS)
print(f'  Confirmed cribs: {len(CONFIRMED_CRIBS)} phrases, {len(FORCED_CRIBS_POS)} positions locked', flush=True)
print(f'  Mutable independent positions after crib removal: {N_INDEPENDENT}', flush=True)


def enforce_cribs(keys_np, mode_str):
    """Force confirmed crib key values on all chains for the given mode."""
    for pos, plain_val in FORCED_CRIBS_POS.items():
        c = int(CIPHER[pos])
        if   mode_str == 'sub':     kv = (c - plain_val) % M
        elif mode_str == 'add':     kv = (plain_val - c) % M
        else:                       kv = (plain_val + c) % M  # beaufort
        keys_np[:, int(LINK_MAP[pos])] = kv

def enforce_twotimepad_gpu(keys_cp):
    """Copy canonical key values to all mirror positions (pure GPU slice ops)."""
    for src_s, dst_s, ln in TTP_CONSTRAINTS:
        keys_cp[:, dst_s:dst_s+ln] = keys_cp[:, src_s:src_s+ln]

# ─── Singleton constraints ────────────────────────────────────────────────────
# Positions where single-rune words occur; key must decrypt to I(10) or A(24)
singleton_positions = []
singleton_cipher    = []
pos = 0
for w in words_all:
    if len(w) == 1:
        singleton_positions.append(pos)
        singleton_cipher.append(w[0])
    pos += len(w)

SING_POS = np.array(singleton_positions, dtype=np.int32)
SING_CIP = np.array(singleton_cipher, dtype=np.int32)
N_SING   = len(SING_POS)
print(f'  Singleton constraints: {N_SING}', flush=True)

# For each singleton, precompute allowed key values: {(c-10)%29, (c-24)%29} for sub
# or {(c+10)%29, (c+24)%29} for add, or {(10-c)%29, (24-c)%29} for beaufort
# We'll compute these per mode at runtime

# ─── Quadgram scoring table ───────────────────────────────────────────────────
print('Building GP quadgram table from known LP text...', flush=True)

# Build from solved LP pages (0-20) + LP2 cleartext
def text_to_gp(txt):
    txt = txt.upper()
    result = []
    i = 0
    while i < len(txt):
        if i+1 < len(txt) and txt[i:i+2] in LETTER_TO_GP:
            result.append(LETTER_TO_GP[txt[i:i+2]])
            i += 2
        elif txt[i] in LETTER_TO_GP:
            result.append(LETTER_TO_GP[txt[i]])
            i += 1
        else:
            i += 1
    return result

solved_pages = list(range(0, 21)) + [55,56,57,58,59,60,61,62,63,64,67,68,71,72,73,74]
all_known_gp = []
for pg in solved_pages:
    r, _ = load_page(pg)
    all_known_gp.extend(r)

# Also add common English LP phrases
lp_phrases = [
    "SOME WISDOM THE PRIMES ARE SACRED ALL THINGS SHOULD BE ENCRYPTED KNOW THIS",
    "AN INSTRUCTION PROGRAM YOUR MIND PROGRAM REALITY",
    "THE LOSS OF DIVINITY THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS",
    "CONSUMPTION PRESERVATION ADHERENCE",
    "AMASS GREAT WEALTH NEVER BECOME ATTACHED TO WHAT YOU OWN",
    "BE PREPARED TO DESTROY ALL THAT YOU OWN",
    "QUESTION ALL THINGS DISCOVER TRUTH INSIDE YOURSELF",
    "FOLLOW YOUR TRUTH IMPOSE NOTHING ON OTHERS",
    "WELCOME PILGRIM TO THE SACRED TEXT",
    "SEEK TRUTH WITHIN THE PRIMES ARE SACRED",
    "THE DIVINE BEING WITHIN YOU IS THE PATH",
    "AN END EVERY END IS A BEGINNING",
    "A WARNING DO NOT SHARE THIS WITH OTHERS",
]
for phrase in lp_phrases:
    all_known_gp.extend(text_to_gp(phrase))

# Count quadgrams
qgram_count = Counter()
for i in range(len(all_known_gp) - 3):
    q = tuple(all_known_gp[i:i+4])
    qgram_count[q] += 1
bigram_count = Counter()
for i in range(len(all_known_gp) - 1):
    bigram_count[tuple(all_known_gp[i:i+2])] += 1

total_q = sum(qgram_count.values()) + M**4  # Laplace smoothing
print(f'  Quadgrams collected: {len(qgram_count)} distinct, {total_q} total', flush=True)

# Build flat 29^4 table
QGRAM_TABLE = np.full(M**4, math.log(1.0 / total_q), dtype=np.float32)
for (a,b,c,d), cnt in qgram_count.items():
    idx = a*M**3 + b*M**2 + c*M + d
    QGRAM_TABLE[idx] = math.log((cnt + 1.0) / total_q)

# Also build bigram table for faster partial scoring
total_b = sum(bigram_count.values()) + M**2
BIGRAM_TABLE = np.full(M**2, math.log(1.0 / total_b), dtype=np.float32)
for (a,b), cnt in bigram_count.items():
    BIGRAM_TABLE[a*M + b] = math.log((cnt + 1.0) / total_b)

print(f'  Bigrams: {len(bigram_count)} distinct', flush=True)

# ─── Known region: P27-P31 = P44[0:1312] ────────────────────────────────────
# At these positions (3001-4312), plaintext is IDENTICAL to plaintext at (9727-11038)
# This gives us cross-position constraints
P27_P31_START = 3001
P27_P31_END   = 4313  # exclusive
P44_START     = 9727

# ─── GPU Setup ───────────────────────────────────────────────────────────────
print(f'\nInitializing GPU {GPU_ID}...', flush=True)
cp.cuda.Device(GPU_ID).use()

# Transfer constants to GPU
cp_cipher   = cp.array(CIPHER, dtype=cp.int32)
cp_qgram    = cp.array(QGRAM_TABLE, dtype=cp.float32)
cp_bigram   = cp.array(BIGRAM_TABLE, dtype=cp.float32)
cp_sing_pos = cp.array(SING_POS, dtype=cp.int32)
cp_sing_cip = cp.array(SING_CIP, dtype=cp.int32)

M29 = cp.int32(M)
print(f'  GPU memory used: {cp.get_default_memory_pool().used_bytes()//1024//1024} MB', flush=True)

# ─── Scoring kernel ─────────────────────────────────────────────────────────
SCORE_KERNEL = cp.RawKernel(r'''
extern "C" __global__
void score_keys(
    const int*   cipher,       // [N_CIPHER]
    const int*   key,          // [N_CHAINS * N_CIPHER]
    const float* qgram,        // [29^4]
    float*       scores,       // [N_CHAINS]  output
    int          N_CIPHER,
    int          N_CHAINS,
    int          mode          // 0=sub, 1=add, 2=beaufort
) {
    int chain = blockIdx.x * blockDim.x + threadIdx.x;
    if (chain >= N_CHAINS) return;

    const int* k = key + chain * N_CIPHER;
    float score = 0.0f;

    // Compute plaintext and accumulate quadgram log-probs
    // Use sliding window: plain[i] = decrypt(cipher[i], k[i])
    int plain[4];
    for (int i = 0; i < 4 && i < N_CIPHER; i++) {
        int c = cipher[i], kv = k[i];
        if (mode == 0) plain[i] = (c - kv + 29) % 29;       // sub
        else if (mode == 1) plain[i] = (c + kv) % 29;        // add
        else plain[i] = (kv - c + 29) % 29;                  // beaufort
    }
    for (int i = 4; i < N_CIPHER; i++) {
        // New plaintext value
        int c = cipher[i], kv = k[i];
        int p;
        if (mode == 0) p = (c - kv + 29) % 29;
        else if (mode == 1) p = (c + kv) % 29;
        else p = (kv - c + 29) % 29;

        // Quadgram: plain[i-3..i]
        int idx = plain[(i-3)&3]*24389 + plain[(i-2)&3]*841 + plain[(i-1)&3]*29 + p;
        score += qgram[idx];

        plain[i&3] = p;
    }
    scores[chain] = score;
}
''', 'score_keys')

# ─── Delta-score kernel (single position change) ────────────────────────────
DELTA_KERNEL = cp.RawKernel(r'''
extern "C" __global__
void delta_score(
    const int*   cipher,
    const int*   key,          // [N_CHAINS * N_CIPHER]
    const float* qgram,
    const int*   positions,    // [N_CHAINS] changed position per chain
    const int*   new_vals,     // [N_CHAINS] new key value per chain
    float*       delta,        // [N_CHAINS] output: new_score - old_score
    int          N_CIPHER,
    int          N_CHAINS,
    int          mode
) {
    int chain = blockIdx.x * blockDim.x + threadIdx.x;
    if (chain >= N_CHAINS) return;

    const int* k = key + chain * N_CIPHER;
    int j   = positions[chain];
    int nv  = new_vals[chain];
    int ov  = k[j];  // old value

    // Compute affected quadgrams: those using positions j-3..j+3
    // Each position i contributes to quadgrams starting at (i-3)..(i)
    // Affected: start positions max(0,j-3)..min(j, N_CIPHER-4)
    float d = 0.0f;

    for (int start = max(0, j-3); start <= min(j, N_CIPHER-4); start++) {
        // Old quadgram
        int old_idx = 0;
        int new_idx = 0;
        for (int t = 0; t < 4; t++) {
            int pos = start + t;
            int c = cipher[pos];
            int kv = (pos == j) ? ov : k[pos];
            int kv_new = (pos == j) ? nv : k[pos];
            int pold, pnew;
            if (mode == 0) { pold = (c - kv + 29) % 29; pnew = (c - kv_new + 29) % 29; }
            else if (mode == 1) { pold = (c + kv) % 29; pnew = (c + kv_new) % 29; }
            else { pold = (kv - c + 29) % 29; pnew = (kv_new - c + 29) % 29; }
            old_idx = old_idx * 29 + pold;
            new_idx = new_idx * 29 + pnew;
        }
        d += qgram[new_idx] - qgram[old_idx];
    }
    delta[chain] = d;
}
''', 'delta_score')

# ─── Singleton check kernel ─────────────────────────────────────────────────
SING_KERNEL = cp.RawKernel(r'''
extern "C" __global__
void check_singletons(
    const int*  key,           // [N_CHAINS * N_CIPHER]
    const int*  sing_pos,      // [N_SING]
    const int*  sing_cip,      // [N_SING]
    int*        sing_hits,     // [N_CHAINS] output
    int         N_CIPHER,
    int         N_CHAINS,
    int         N_SING,
    int         mode
) {
    int chain = blockIdx.x * blockDim.x + threadIdx.x;
    if (chain >= N_CHAINS) return;
    const int* k = key + chain * N_CIPHER;
    int hits = 0;
    for (int s = 0; s < N_SING; s++) {
        int p = sing_pos[s];
        int c = sing_cip[s];
        int kv = k[p];
        int dec;
        if (mode == 0) dec = (c - kv + 29) % 29;
        else if (mode == 1) dec = (c + kv) % 29;
        else dec = (kv - c + 29) % 29;
        if (dec == 10 || dec == 24) hits++;
    }
    sing_hits[chain] = hits;
}
''', 'check_singletons')

# ─── Word-boundary scoring helper (CPU) ─────────────────────────────────────
LP_VOCAB = {
    'AN','INSTRUCTION','SOME','WISDOM','THE','PRIMES','ARE','SACRED','ALL',
    'THINGS','SHOULD','BE','ENCRYPTED','KNOW','THIS','WARNING','WELCOME',
    'PILGRIM','LOSS','DIVINITY','CIRCUMFERENCE','PRACTICES','THREE',
    'BEHAVIORS','CAUSE','CONSUMPTION','PRESERVATION','ADHERENCE','AMASS',
    'GREAT','WEALTH','NEVER','BECOME','ATTACHED','TO','WHAT','YOU','OWN',
    'PREPARED','DESTROY','PROGRAM','YOUR','MIND','REALITY','SEEK','TRUTH',
    'WITHIN','HOLY','BEING','EACH','FOLLOW','END','EMERGE','WILL','EVERY',
    'DEEP','ABOVE','SAME','OTHER','ONE','DIVINE','FROM','A','I','IS','TO',
    'OF','IN','NOT','WITH','HAVE','SELF','PATH','QUESTION','DISCOVER',
    'INSIDE','YOURSELF','IMPOSE','NOTHING','OTHERS','CHAPTER','INTUS',
    'PARABLE','INSTAR','BUTTERFLY','SHADOW','FORM','AND','FOR','BUT','BY',
    'AS','AT','THIS','THAT','WHICH','CAUSE','THAT'
}

def word_score(plain_seq_words):
    """Score decrypted word-boundary text."""
    score = 0
    for w_plain in plain_seq_words:
        txt = ''.join(IDX_TO[v] for v in w_plain)
        if txt in LP_VOCAB:
            score += len(txt) * 20 + 30
        elif any(lw in txt for lw in LP_VOCAB if len(lw) >= 4):
            score += 15
    return score

# ─── Initialize chains ───────────────────────────────────────────────────────
print(f'\nInitializing {N_CHAINS} chains on GPU {GPU_ID}...', flush=True)

rng = np.random.default_rng(GPU_ID * 12345 + 67890)

# Initialize keys randomly
KEYS = rng.integers(0, M, size=(N_CHAINS, N_CIPHER), dtype=np.int32)

# Enforce singleton constraints for mode[0]
def enforce_singletons(keys_np, mode_str):
    for idx, (sp, sc) in enumerate(zip(SING_POS, SING_CIP)):
        # Randomly pick I or A for each chain at this singleton
        # sub:      plain = (c - key) % 29  → key = (c - plain) % 29
        # add:      plain = (c + key) % 29  → key = (plain - c) % 29
        # beaufort: plain = (key - c) % 29  → key = (plain + c) % 29
        if mode_str == 'sub':
            choices_i = (sc - 10) % M
            choices_a = (sc - 24) % M
        elif mode_str == 'add':
            choices_i = (10 - sc) % M
            choices_a = (24 - sc) % M
        else:  # beaufort
            choices_i = (10 + sc) % M
            choices_a = (24 + sc) % M
        # Random split between I and A for initialization
        ia = rng.integers(0, 2, size=N_CHAINS)
        val = np.where(ia == 0, choices_i, choices_a)
        # Always write to CANONICAL position so TTP enforcement propagates it
        canon_sp = int(LINK_MAP[sp])
        keys_np[:, canon_sp] = val
        keys_np[:, sp] = val  # also set sp directly (sp==canon_sp unless sp is mirror)

mode_idx = 0

# ─── Warmstart from checkpoint if available ──────────────────────────────────
CHECKPOINT = f'data/gpu_hill_checkpoint_gpu{GPU_ID}.json'
if Path(CHECKPOINT).exists():
    import json
    ck = json.loads(Path(CHECKPOINT).read_text())
    ck_mode = ck.get('mode', MODES[0])
    ck_key  = np.array(ck['key'], dtype=np.int32)
    if ck_mode in MODES:
        mode_idx = MODES.index(ck_mode)
    print(f'Warmstart from {CHECKPOINT}: mode={ck_mode}, score={ck.get("score","?")}, step={ck.get("step","?")}', flush=True)
    # Seed all chains from best key with small perturbation
    for c_i in range(N_CHAINS):
        perturb = rng.integers(0, N_CIPHER, size=max(1, N_CIPHER // (20 + c_i // 100)))
        pvals   = rng.integers(0, M, size=len(perturb))
        KEYS[c_i] = ck_key.copy()
        KEYS[c_i, perturb] = pvals
else:
    enforce_singletons(KEYS, MODES[mode_idx])

# Always enforce singletons after initialization
enforce_singletons(KEYS, MODES[mode_idx])
# Enforce confirmed crib positions (remove any drift from warmstart perturbations)
enforce_cribs(KEYS, MODES[mode_idx])
# Enforce TTP constraints (mirror positions = canonical positions)
for src_s, dst_s, ln in TTP_CONSTRAINTS:
    KEYS[:, dst_s:dst_s+ln] = KEYS[:, src_s:src_s+ln]

cp_keys   = cp.array(KEYS, dtype=cp.int32)

# Compute initial scores
def compute_all_scores(cp_k, mode_int):
    scores = cp.zeros(N_CHAINS, dtype=cp.float32)
    blk = 256
    grd = (N_CHAINS + blk - 1) // blk
    SCORE_KERNEL((grd,), (blk,),
        (cp_cipher, cp_k.ravel(), cp_qgram, scores,
         cp.int32(N_CIPHER), cp.int32(N_CHAINS), cp.int32(mode_int)))
    cp.cuda.Stream.null.synchronize()
    return scores

MODE_INT = {'sub': 0, 'add': 1, 'beaufort': 2}

print('Computing initial scores...', flush=True)
mode_str  = MODES[mode_idx]
mode_int  = MODE_INT[mode_str]
cp_scores = compute_all_scores(cp_keys, mode_int)
best_scores = cp_scores.copy()
best_keys   = cp_keys.copy()

print(f'  Initial score range: {float(cp_scores.min()):.1f} .. {float(cp_scores.max()):.1f}', flush=True)
print(f'  Mean: {float(cp_scores.mean()):.1f}', flush=True)

# ─── Singleton precomputed allowed values per mode ───────────────────────────
def make_allowed(mode_str):
    """For each singleton position, list of 2 allowed key values."""
    allowed_0 = np.zeros(N_SING, dtype=np.int32)  # key if I(10)
    allowed_1 = np.zeros(N_SING, dtype=np.int32)  # key if A(24)
    for s, (sp, sc) in enumerate(zip(SING_POS, SING_CIP)):
        if mode_str == 'sub':
            allowed_0[s] = (sc - 10) % M
            allowed_1[s] = (sc - 24) % M
        elif mode_str == 'add':
            allowed_0[s] = (10 - sc) % M   # FIX: was (sc+10)%M
            allowed_1[s] = (24 - sc) % M   # FIX: was (sc+24)%M
        elif mode_str == 'beaufort':
            allowed_0[s] = (10 + sc) % M
            allowed_1[s] = (24 + sc) % M
    return allowed_0, allowed_1

# Position sets for singletons (kept for reference)
singleton_set = set(SING_POS.tolist())

# ─── Main hillclimbing loop ──────────────────────────────────────────────────
print(f'\n=== GPU {GPU_ID} hillclimber starting ===', flush=True)
print(f'Mode schedule: {MODES}', flush=True)
print(f'Output file: {OUTFILE}', flush=True)
print(flush=True)

with open(OUTFILE, 'w', encoding='utf-8') as fout:
    fout.write(f'GPU {GPU_ID} Hillclimber — Start {time.strftime("%H:%M:%S")}\n')
    fout.write(f'Modes: {MODES}, Chains: {N_CHAINS}\n')
    fout.write('='*60 + '\n')
    fout.flush()

# Temperature schedule — start lower if warmstarting from checkpoint
T_START = 0.1 if Path(CHECKPOINT).exists() else 0.5
T_END   = 0.0001
T_DECAY = 0.9999995

temperature = T_START
global_best_score = float(cp_scores.max())
global_best_key   = cp_keys[int(cp_scores.argmax())].get()
global_best_mode  = mode_str

blk = 256
grd = (N_CHAINS + blk - 1) // blk

allowed_0, allowed_1 = make_allowed(mode_str)
cp_allowed_0 = cp.array(allowed_0, dtype=cp.int32)
cp_allowed_1 = cp.array(allowed_1, dtype=cp.int32)

step = 0
t_last = time.time()
accept_count = 0

while True:
    step += 1

    # Cooldown: after 2M steps on one mode, switch
    if step % 2_000_000 == 0:
        mode_idx = (mode_idx + 1) % len(MODES)
        mode_str = MODES[mode_idx]
        mode_int = MODE_INT[mode_str]
        allowed_0, allowed_1 = make_allowed(mode_str)
        cp_allowed_0 = cp.array(allowed_0, dtype=cp.int32)
        cp_allowed_1 = cp.array(allowed_1, dtype=cp.int32)
        # Re-enforce singletons, cribs, and TTP
        keys_np = cp_keys.get()
        enforce_singletons(keys_np, mode_str)
        enforce_cribs(keys_np, mode_str)
        for src_s, dst_s, ln in TTP_CONSTRAINTS:
            keys_np[:, dst_s:dst_s+ln] = keys_np[:, src_s:src_s+ln]
        cp_keys = cp.array(keys_np, dtype=cp.int32)
        cp_scores = compute_all_scores(cp_keys, mode_int)
        temperature = T_START  # reset temperature
        print(f'Step {step}: Switched to mode={mode_str}, temp reset to {T_START}', flush=True)

    # ── Sample random positions from INDEPENDENT (canonical) positions only ──
    pos_arr = rng.choice(INDEPENDENT_POS, size=N_CHAINS).astype(np.int32)

    # ── Sample new key values ──
    new_vals = rng.integers(0, M, size=N_CHAINS).astype(np.int32)
    # Vectorized singleton enforcement
    pos_is_sing = np.isin(pos_arr, SING_POS)
    if pos_is_sing.any():
        sing_idx = np.searchsorted(SING_POS, pos_arr)
        sing_idx = np.clip(sing_idx, 0, N_SING - 1)
        ia = rng.integers(0, 2, size=N_CHAINS).astype(np.int32)
        sing_new = np.where(ia == 0, allowed_0[sing_idx], allowed_1[sing_idx])
        new_vals = np.where(pos_is_sing, sing_new, new_vals)

    cp_pos  = cp.array(pos_arr, dtype=cp.int32)
    cp_nval = cp.array(new_vals, dtype=cp.int32)

    # ── Compute delta scores ──
    cp_delta = cp.zeros(N_CHAINS, dtype=cp.float32)
    DELTA_KERNEL((grd,), (blk,),
        (cp_cipher, cp_keys.ravel(), cp_qgram, cp_pos, cp_nval, cp_delta,
         cp.int32(N_CIPHER), cp.int32(N_CHAINS), cp.int32(mode_int)))
    cp.cuda.Stream.null.synchronize()

    # ── Metropolis acceptance ──
    delta_np = cp_delta.get()
    rand_np  = rng.random(N_CHAINS).astype(np.float32)
    accept   = delta_np > 0
    accept  |= rand_np < np.exp(np.clip(delta_np / temperature, -50, 10))

    # Apply accepted moves (CPU loop — bottleneck, but simpler)
    # For performance, batch apply on GPU
    accept_cp = cp.array(accept.astype(np.int32), dtype=cp.int32)
    # Apply: key[chain, pos] = new_val if accept[chain] else key[chain, pos]
    chain_idx = cp.arange(N_CHAINS, dtype=cp.int32)
    cp_keys[chain_idx[accept_cp.astype(bool)], cp_pos[accept_cp.astype(bool)]] = \
        cp_nval[accept_cp.astype(bool)]
    cp_scores += cp_delta * accept_cp.astype(cp.float32)

    # ── Enforce two-time-pad constraints (mirror = canonical) ──
    enforce_twotimepad_gpu(cp_keys)

    accept_count += int(accept.sum())
    temperature = max(T_END, temperature * T_DECAY)

    # ── Track global best ──
    cur_best_idx = int(cp_scores.argmax())
    cur_best_score = float(cp_scores[cur_best_idx])
    if cur_best_score > global_best_score:
        global_best_score = cur_best_score
        global_best_key   = cp_keys[cur_best_idx].get()
        global_best_mode  = mode_str

    # ── Periodic save ──
    if step % SAVE_EVERY == 0:
        elapsed = time.time() - t_last
        rate = SAVE_EVERY / elapsed
        t_last = time.time()

        # Decode best key
        key = global_best_key
        words_dec = []
        ki = 0
        for w in words_all[:200]:
            dec = []
            for c in w:
                kv = int(key[ki % N_CIPHER])
                if global_best_mode == 'sub': p = (c - kv) % M
                elif global_best_mode == 'add': p = (c + kv) % M
                else: p = (kv - c) % M
                dec.append(p); ki += 1
            words_dec.append(tuple(dec))

        # Word score
        ws = word_score(words_dec)

        # Singleton count
        sing_hits2 = 0
        for sp, sc in zip(SING_POS, SING_CIP):
            kv = int(key[sp])
            if global_best_mode == 'sub': dec = (sc - kv) % M
            elif global_best_mode == 'add': dec = (sc + kv) % M
            else: dec = (kv - sc) % M
            if dec in (10, 24): sing_hits2 += 1

        first_100_words = ' '.join(''.join(IDX_TO[v] for v in w) for w in words_dec[:30])

        msg = (f'Step {step:,} | Mode={global_best_mode} | '
               f'Score={global_best_score:.1f} | WordScore={ws} | '
               f'Singletons={sing_hits2}/{N_SING} | '
               f'AcceptRate={accept_count/SAVE_EVERY:.3f} | '
               f'Temp={temperature:.6f} | Rate={rate:.0f}steps/s\n'
               f'  Best text (first 30 words): {first_100_words}\n')
        print(msg, end='', flush=True)

        # Always save full-key checkpoint to JSON (overwrite with best)
        import json as _json
        _ck = {'step': step, 'mode': global_best_mode,
               'score': float(global_best_score), 'wordscore': ws,
               'singletons': sing_hits2,
               'key': list(map(int, global_best_key))}
        Path(CHECKPOINT).write_text(_json.dumps(_ck))

        with open(OUTFILE, 'a', encoding='utf-8') as fout:
            fout.write(msg)

            # If promising, save full key
            if sing_hits2 >= N_SING * 0.8 or ws >= 500:
                fout.write(f'  PROMISING! Key first 200: {list(map(int, key[:200]))}\n')

            # Also save all-time best full decryption if score is very high or word score is high
            if ws >= 300:
                full_text = []
                ki = 0
                for w in words_all:
                    dec = []
                    for c in w:
                        kv = int(key[ki % N_CIPHER])
                        if global_best_mode == 'sub': p = (c - kv) % M
                        elif global_best_mode == 'add': p = (c + kv) % M
                        else: p = (kv - c) % M
                        dec.append(p); ki += 1
                    full_text.append(''.join(IDX_TO[v] for v in dec))
                fout.write(f'  HIGH SCORE FULL TEXT: {" ".join(full_text[:100])}\n')
            # end with open

        accept_count = 0

        # Every 10 saves, also restart worst 10% of chains from best
        if (step // SAVE_EVERY) % 10 == 0:
            scores_np = cp_scores.get()
            worst_idx = np.argsort(scores_np)[:N_CHAINS//10]
            best_idx  = int(np.argmax(scores_np))
            best_key_np = cp_keys[best_idx].get()
            for wi in worst_idx:
                # Restart with perturbation of best (only perturb INDEPENDENT positions)
                perturbed = best_key_np.copy()
                n_perturb = rng.integers(50, 200)
                perturb_pos = rng.choice(INDEPENDENT_POS, size=n_perturb)
                perturb_val = rng.integers(0, M, size=n_perturb)
                perturbed[perturb_pos] = perturb_val
                # Re-enforce singletons (at canonical positions)
                for s, (sp, sc) in enumerate(zip(SING_POS, SING_CIP)):
                    canon_sp = int(LINK_MAP[sp])
                    v = allowed_0[s] if rng.integers(0,2)==0 else allowed_1[s]
                    perturbed[canon_sp] = v
                    perturbed[sp] = v
                # Re-enforce confirmed cribs on this chain
                for pos, plain_val in FORCED_CRIBS_POS.items():
                    c = int(CIPHER[pos])
                    kv = (c - plain_val) % M  # sub mode always correct here
                    perturbed[int(LINK_MAP[pos])] = kv
                # Re-enforce TTP on this single chain
                for src_s, dst_s, ln in TTP_CONSTRAINTS:
                    perturbed[dst_s:dst_s+ln] = perturbed[src_s:src_s+ln]
                cp_keys[wi] = cp.array(perturbed, dtype=cp.int32)
            cp_scores = compute_all_scores(cp_keys, mode_int)
