"""
GPU-Accelerated Hillclimber v2 — Liber Primus P21-P54
======================================================
Optimized over v1 with three major changes:

  OPT-1: Fused CUDA kernel  — delta + Metropolis accept/reject + key update
          all happen inside a single GPU kernel. Zero CPU roundtrip per step.
          v1 transferred 3×8KB between CPU and GPU every step (delta.get,
          rng.array, accept.cp.array). Eliminated entirely.

  OPT-2: TTP enforcement only at init + chain restart
          v1 called enforce_twotimepad_gpu() every single step, copying
          7.4 million int32 elements (28 MB) per step even though mirror
          positions were NEVER mutated in the hot loop. Removed.

  OPT-3: N_CHAINS 2000 → 4000
          RTX 2080 Ti has 11 GB VRAM. 4000 chains × 14529 × 4 bytes = 232 MB.
          Doubles throughput with no code change.

Expected speedup: 5-10× versus v1 (~232 steps/sec → ~1500-2000 steps/sec).

Usage: python gpu_hillclimber_v2.py <gpu_id>
  Automatically loads checkpoint from gpu_hill_checkpoint_gpu<N>.json if present.
"""

import sys, os, time, math, json
from pathlib import Path
from collections import Counter
import numpy as np
import cupy as cp

sys.stdout.reconfigure(encoding='utf-8')

# ─── Config ─────────────────────────────────────────────────────────────────
GPU_ID     = int(sys.argv[1]) if len(sys.argv) > 1 else 1
N_CHAINS   = 4000          # doubled from v1 (GPU has plenty of room)
SAVE_EVERY = 10_000
OUTFILE    = f'data/gpu_hill_v2_gpu{GPU_ID}.txt'
M          = 29

MODES = ['sub']  # SUB confirmed correct; single mode is faster

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
cipher_list = []; words_all = []; cum = 0; page_offsets = {}
for pg in range(21, 55):
    runes, words = load_page(pg)
    page_offsets[pg] = cum; cum += len(runes)
    cipher_list.extend(runes); words_all.extend(words)

CIPHER    = np.array(cipher_list, dtype=np.int32)
N_CIPHER  = len(CIPHER)
print(f'  Cipher length: {N_CIPHER} runes', flush=True)

# ─── TTP constraints ─────────────────────────────────────────────────────────
TTP_CONSTRAINTS = [
    (3001,  9727, 1312),
    (6298, 12311, 1468),
    (   0,  5803,  404),
    (2736,  8643,  265),
    ( 737,  8100,  172),
    ( 910,  8273,   97),
]
LINK_MAP = np.arange(N_CIPHER, dtype=np.int32)
for src_s, dst_s, ln in TTP_CONSTRAINTS:
    for i in range(ln):
        LINK_MAP[dst_s + i] = LINK_MAP[src_s + i]

INDEPENDENT_POS = np.array([i for i in range(N_CIPHER) if LINK_MAP[i] == i], dtype=np.int32)
N_INDEPENDENT   = len(INDEPENDENT_POS)
INDEPENDENT_SET = set(INDEPENDENT_POS.tolist())
print(f'  TTP: {sum(ln for _,_,ln in TTP_CONSTRAINTS)} linked → {N_INDEPENDENT} independent positions', flush=True)

# ─── Confirmed cribs (forced, never mutated) ──────────────────────────────────
def _gp_encode(phrase):
    w = phrase.upper().replace(' ', ''); r = []; i = 0
    while i < len(w):
        if i+1 < len(w) and w[i:i+2] in LETTER_TO_GP:
            r.append(LETTER_TO_GP[w[i:i+2]]); i += 2
        elif w[i] in LETTER_TO_GP:
            r.append(LETTER_TO_GP[w[i]]); i += 1
        else: i += 1
    return r

CONFIRMED_CRIBS = [
    ('CONSUMPTION',         31),
    ('KNOWTHIS',           476),
    ('PROGRAM',            599),
    ('DIUINITY',          1356),
    ('PRESERUATION',      2093),
    ('SOMEWISDOM',        4131),
    ('THELOSSOFDIUINITY', 4325),
    ('CIRCUMFERENCE',     3080),
    ('ADHERENCE',         8532),
]

FORCED_CRIBS_POS = {}
for phrase, start in CONFIRMED_CRIBS:
    for i, v in enumerate(_gp_encode(phrase)):
        FORCED_CRIBS_POS[start + i] = v

CRIB_CANON_SET = {int(LINK_MAP[p]) for p in FORCED_CRIBS_POS}
INDEPENDENT_POS = np.array([p for p in INDEPENDENT_POS if p not in CRIB_CANON_SET], dtype=np.int32)
N_INDEPENDENT   = len(INDEPENDENT_POS)
print(f'  Cribs: {len(CONFIRMED_CRIBS)} phrases, {len(FORCED_CRIBS_POS)} positions locked', flush=True)
print(f'  Mutable independent positions: {N_INDEPENDENT}', flush=True)

def enforce_cribs(keys_np):
    """Force confirmed crib key values (sub mode only)."""
    for pos, plain_val in FORCED_CRIBS_POS.items():
        keys_np[:, int(LINK_MAP[pos])] = (int(CIPHER[pos]) - plain_val) % M

def enforce_ttp(keys_np):
    """Propagate canonical key values to all mirror positions."""
    for src_s, dst_s, ln in TTP_CONSTRAINTS:
        keys_np[:, dst_s:dst_s+ln] = keys_np[:, src_s:src_s+ln]

# ─── Singleton constraints ────────────────────────────────────────────────────
singleton_positions = []; singleton_cipher = []; pos = 0
for w in words_all:
    if len(w) == 1:
        singleton_positions.append(pos); singleton_cipher.append(w[0])
    pos += len(w)
SING_POS = np.array(singleton_positions, dtype=np.int32)
SING_CIP = np.array(singleton_cipher,   dtype=np.int32)
N_SING   = len(SING_POS)
print(f'  Singleton constraints: {N_SING}', flush=True)

def allowed_vals_sub(s):
    """For sub mode: returns (val_if_I, val_if_A) for singleton s."""
    sc = int(SING_CIP[s])
    return (sc - 10) % M, (sc - 24) % M

# Build full-array allowed tables (size N_CIPHER, -1 for non-singletons)
SING_A0 = np.full(N_CIPHER, -1, dtype=np.int32)
SING_A1 = np.full(N_CIPHER, -1, dtype=np.int32)
for s, sp in enumerate(SING_POS):
    canon = int(LINK_MAP[sp])   # kernel visits canonical positions only
    a0, a1 = allowed_vals_sub(s)
    SING_A0[canon] = a0
    SING_A1[canon] = a1

def enforce_singletons(keys_np):
    """For sub mode: set singleton positions to I or A.
    Preserves existing valid A/I assignments; only randomly fixes invalid ones.
    This keeps optimized singleton configurations from checkpoint keys intact."""
    rng_ = np.random.default_rng()
    for sp, sc in zip(SING_POS, SING_CIP):
        canon_sp = int(LINK_MAP[sp])
        a0 = (sc - 10) % M  # key value that decrypts to I (GP 10)
        a1 = (sc - 24) % M  # key value that decrypts to A (GP 24)
        current = keys_np[:, canon_sp]
        invalid = ~((current == a0) | (current == a1))
        n_invalid = int(invalid.sum())
        if n_invalid > 0:
            rows = np.flatnonzero(invalid)
            choices = rng_.integers(0, 2, size=n_invalid)
            new_vals = np.where(choices == 0, a0, a1).astype(np.int32)
            keys_np[rows, canon_sp] = new_vals
            if sp != canon_sp:
                keys_np[rows, sp] = new_vals
        # Always sync mirror position with canonical position
        if sp != canon_sp:
            keys_np[:, sp] = keys_np[:, canon_sp]

# ─── Quadgram scoring table ───────────────────────────────────────────────────
print('Building GP quadgram table...', flush=True)

def text_to_gp(txt):
    txt = txt.upper(); r = []; i = 0
    while i < len(txt):
        if i+1 < len(txt) and txt[i:i+2] in LETTER_TO_GP:
            r.append(LETTER_TO_GP[txt[i:i+2]]); i += 2
        elif txt[i] in LETTER_TO_GP:
            r.append(LETTER_TO_GP[txt[i]]); i += 1
        else: i += 1
    return r

solved_pages = list(range(0, 21)) + [55,56,57,58,59,60,61,62,63,64,67,68,71,72,73,74]
all_known_gp = []
for pg in solved_pages:
    r, _ = load_page(pg)
    all_known_gp.extend(r)

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
]
for phrase in lp_phrases:
    all_known_gp.extend(text_to_gp(phrase))

# OPT-4: Augment quadgram table with large English corpus (Emerson essays)
# The LP plaintext IS English (Runeglish), so English quadgram frequency
# provides a much stronger signal than the tiny solved-page corpus alone.
# We weight LP-specific text 3x higher to preserve LP vocabulary bias.
all_english_gp = []
for corpus_file in ['data/self_reliance.txt', 'data/emerson_essays.txt']:
    cp_path = Path(corpus_file)
    if cp_path.exists():
        raw = cp_path.read_text(encoding='utf-8', errors='ignore')
        # Only keep alphabetic content, map to GP
        cleaned = ''.join(c for c in raw.upper() if c.isalpha() or c == ' ')
        all_english_gp.extend(text_to_gp(cleaned))
        print(f'  Corpus {corpus_file}: {len(raw)} chars -> {len(all_english_gp)} GP values', flush=True)

qgram_count = Counter()
# LP-specific text weighted 3x
for _ in range(3):
    for i in range(len(all_known_gp) - 3):
        qgram_count[tuple(all_known_gp[i:i+4])] += 1
# English corpus at 1x weight
for i in range(len(all_english_gp) - 3):
    qgram_count[tuple(all_english_gp[i:i+4])] += 1

total_q = sum(qgram_count.values()) + M**4
print(f'  Quadgrams: {len(qgram_count)} distinct (LP 3x weighted + English corpus)', flush=True)

QGRAM_TABLE = np.full(M**4, math.log(1.0 / total_q), dtype=np.float32)
for (a,b,c,d), cnt in qgram_count.items():
    idx = a*M**3 + b*M**2 + c*M + d
    QGRAM_TABLE[idx] = math.log((cnt + 1.0) / total_q)

# ─── GPU Setup ────────────────────────────────────────────────────────────────
print(f'\nInitializing GPU {GPU_ID}...', flush=True)
cp.cuda.Device(GPU_ID).use()

cp_cipher = cp.array(CIPHER,       dtype=cp.int32)
cp_qgram  = cp.array(QGRAM_TABLE,  dtype=cp.float32)
cp_sing_a0 = cp.array(SING_A0,     dtype=cp.int32)
cp_sing_a1 = cp.array(SING_A1,     dtype=cp.int32)
cp_indep  = cp.array(INDEPENDENT_POS, dtype=cp.int32)

print(f'  GPU memory used: {cp.get_default_memory_pool().used_bytes()//1024//1024} MB', flush=True)

# ─── Full-score kernel (used at init and chain restart) ─────────────────────
SCORE_KERNEL = cp.RawKernel(r'''
extern "C" __global__
void score_keys(
    const int*   cipher,
    const int*   key,
    const float* qgram,
    float*       scores,
    int          N_CIPHER,
    int          N_CHAINS
) {
    int chain = blockIdx.x * blockDim.x + threadIdx.x;
    if (chain >= N_CHAINS) return;
    const int* k = key + chain * N_CIPHER;
    float score = 0.0f;
    int plain[4];
    for (int i = 0; i < 4 && i < N_CIPHER; i++) {
        int c = cipher[i], kv = k[i];
        plain[i] = (c - kv + 29) % 29;
    }
    for (int i = 4; i < N_CIPHER; i++) {
        int c = cipher[i], kv = k[i];
        int p = (c - kv + 29) % 29;
        int idx = plain[(i-3)&3]*24389 + plain[(i-2)&3]*841 + plain[(i-1)&3]*29 + p;
        score += qgram[idx];
        plain[i&3] = p;
    }
    scores[chain] = score;
}
''', 'score_keys')

# ─────────────────────────────────────────────────────────────────────────────
# OPT-1: FUSED STEP KERNEL
# Each thread = one Markov chain.
# Per call: sample position + value → compute delta → Metropolis → update key.
# No data ever leaves the GPU. Uses a fast per-thread xorshift64 RNG seeded
# from a per-step host value XOR thread index.
# ─────────────────────────────────────────────────────────────────────────────
STEP_KERNEL = cp.RawKernel(r'''
extern "C" __global__
void markov_step(
    const int*   cipher,         // [N_CIPHER]
    int*         key,            // [N_CHAINS * N_CIPHER]  in/out
    float*       scores,         // [N_CHAINS]             in/out
    const float* qgram,          // [29^4]
    const int*   indep_pos,      // [N_INDEPENDENT]
    const int*   sing_a0,        // [N_CIPHER]  -1 if not singleton
    const int*   sing_a1,        // [N_CIPHER]  -1 if not singleton
    int          N_CIPHER,
    int          N_CHAINS,
    int          N_INDEPENDENT,
    float        temperature,
    unsigned long long step_seed  // changes every call
) {
    int chain = blockIdx.x * blockDim.x + threadIdx.x;
    if (chain >= N_CHAINS) return;

    // -- xorshift64 per-thread RNG --
    unsigned long long rng = step_seed ^ ((unsigned long long)chain * 6364136223846793005ULL + 1442695040888963407ULL);
    // Extra mix to decorrelate nearby chains
    rng ^= rng >> 33; rng *= 0xff51afd7ed558ccdULL;
    rng ^= rng >> 33; rng *= 0xc4ceb9fe1a85ec53ULL;
    rng ^= rng >> 33;

    // Helper: advance RNG, return uint64
    #define NEXT_RNG() (rng ^= rng >> 12, rng ^= rng << 25, rng ^= rng >> 27, rng)

    // -- Pick random independent position --
    unsigned long long r1 = NEXT_RNG();
    int pos_idx = (int)(r1 % (unsigned long long)N_INDEPENDENT);
    int j = indep_pos[pos_idx];

    // -- Pick new key value --
    unsigned long long r2 = NEXT_RNG();
    int new_val;
    int a0 = sing_a0[j];
    if (a0 >= 0) {
        // singleton: alternates between I-key and A-key
        new_val = (r2 & 1ULL) ? sing_a1[j] : a0;
    } else {
        new_val = (int)(r2 % 29ULL);
    }

    int* k = key + chain * N_CIPHER;
    int old_val = k[j];
    if (old_val == new_val) return;

    // -- Compute delta score (affected quadgrams only) --
    float d = 0.0f;
    int start_min = j - 3; if (start_min < 0) start_min = 0;
    int start_max = j;     if (start_max > N_CIPHER - 4) start_max = N_CIPHER - 4;

    for (int start = start_min; start <= start_max; start++) {
        int old_idx = 0, new_idx = 0;
        for (int t = 0; t < 4; t++) {
            int pos = start + t;
            int c   = cipher[pos];
            int kold = (pos == j) ? old_val : k[pos];
            int knew = (pos == j) ? new_val : k[pos];
            int pold = (c - kold + 29) % 29;
            int pnew = (c - knew + 29) % 29;
            old_idx = old_idx * 29 + pold;
            new_idx = new_idx * 29 + pnew;
        }
        d += qgram[new_idx] - qgram[old_idx];
    }

    // -- Metropolis acceptance --
    bool accept = (d >= 0.0f);
    if (!accept && temperature > 1e-9f) {
        // Map r3 to float in [0,1)
        unsigned long long r3 = NEXT_RNG();
        float rf = (float)(r3 >> 11) * (1.0f / 9007199254740992.0f);
        accept = (rf < expf(d / temperature));
    }

    if (accept) {
        k[j]        = new_val;
        scores[chain] += d;
    }

    #undef NEXT_RNG
}
''', 'markov_step')

# ─── Initialise chains ────────────────────────────────────────────────────────
print(f'\nInitialising {N_CHAINS} chains on GPU {GPU_ID}...', flush=True)
rng = np.random.default_rng(GPU_ID * 99991 + 11117)
KEYS = rng.integers(0, M, size=(N_CHAINS, N_CIPHER), dtype=np.int32)

# Warmstart from v1 or v2 checkpoint if available
CHECKPOINT = f'data/gpu_hill_checkpoint_gpu{GPU_ID}.json'
warmstart_score = None
if Path(CHECKPOINT).exists():
    ck = json.loads(Path(CHECKPOINT).read_text())
    ck_key = np.array(ck['key'], dtype=np.int32)
    warmstart_score = float(ck.get('score', 0))
    print(f'Warmstart from {CHECKPOINT}: score={warmstart_score}, step={ck.get("step","?")}', flush=True)
    # Seed all chains from best key + diversified perturbation sizes to escape basin
    # 10%: tiny (fine-tune near best), 23%: small, 33%: large, 34%: near-random
    for c_i in range(N_CHAINS):
        if c_i < N_CHAINS // 10:
            n_perturb = max(10, N_INDEPENDENT // 200)     # ~53 positions
        elif c_i < N_CHAINS // 3:
            n_perturb = max(100, N_INDEPENDENT // 50)     # ~214 positions
        elif c_i < 2 * N_CHAINS // 3:
            n_perturb = max(1000, N_INDEPENDENT // 5)     # ~2144 positions
        else:
            n_perturb = max(3000, N_INDEPENDENT // 2)    # ~5360 positions
        perturb_pos = rng.choice(INDEPENDENT_POS, size=n_perturb, replace=False)
        pvals       = rng.integers(0, M, size=n_perturb)
        KEYS[c_i]   = ck_key.copy()
        KEYS[c_i, perturb_pos] = pvals

enforce_singletons(KEYS)
enforce_cribs(KEYS)
enforce_ttp(KEYS)       # OPT-2: enforce TTP only here (not in hot loop)

cp_keys   = cp.array(KEYS, dtype=cp.int32)
cp_scores = cp.zeros(N_CHAINS, dtype=cp.float32)

def compute_all_scores():
    blk = 256; grd = (N_CHAINS + blk - 1) // blk
    SCORE_KERNEL((grd,), (blk,),
        (cp_cipher, cp_keys.ravel(), cp_qgram, cp_scores,
         cp.int32(N_CIPHER), cp.int32(N_CHAINS)))
    cp.cuda.Stream.null.synchronize()

print('Computing initial scores...', flush=True)
compute_all_scores()
print(f'  Initial score range: {float(cp_scores.min()):.1f} .. {float(cp_scores.max()):.1f}', flush=True)
print(f'  Mean: {float(cp_scores.mean()):.1f}', flush=True)

# ─── LP vocab for word scoring ────────────────────────────────────────────────
LP_VOCAB = {
    'AN','INSTRUCTION','SOME','WISDOM','THE','PRIMES','ARE','SACRED','ALL',
    'THINGS','SHOULD','BE','ENCRYPTED','KNOW','THIS','WARNING','WELCOME',
    'PILGRIM','LOSS','DIVINITY','DIUINITY','CIRCUMFERENCE','PRACTICES','THREE',
    'BEHAVIORS','CAUSE','CONSUMPTION','PRESERVATION','PRESERUATION','ADHERENCE','AMASS',
    'GREAT','WEALTH','NEVER','BECOME','ATTACHED','TO','WHAT','YOU','OWN',
    'PREPARED','DESTROY','PROGRAM','YOUR','MIND','REALITY','SEEK','TRUTH',
    'WITHIN','HOLY','BEING','EACH','FOLLOW','END','EMERGE','WILL','EVERY',
    'DEEP','ABOVE','SAME','OTHER','ONE','DIVINE','FROM','A','I','IS','TO',
    'OF','IN','NOT','WITH','HAVE','SELF','PATH','QUESTION','DISCOVER',
    'INSIDE','YOURSELF','IMPOSE','NOTHING','OTHERS','CHAPTER','INTUS',
    'PARABLE','INSTAR','BUTTERFLY','SHADOW','FORM','AND','FOR','BUT','BY',
    'AS','AT','THIS','THAT','WHICH','WEDONOT','DONOT','FOLLOWYOURTRUTH',
    'PROGRAMYOURMIND','THELOSSOFDIUINITY','SOMEWISDOM','CONSUMPTIONPRESERUATION',
    'DECEPTION','ABOUT','FROM','MOST','SACRED','STRONG','STRONGENCE',
    'LOSSOF','THELOSSOF','NOTWORTH','WORTH','BUFFER','AETHEREAL','CARNAL','OBSCURA',
    'MOBIUS','PRIMAL','PRIME','CEASING','CEASE','LOSE','PATTERN','PATTERNS',
    'KNOWLEDGE','BUILD','BEGIN','DETAIL','PROFUNDITY','WHOLE','SIMPLY',
}

# Build LP vocabulary index: GP-encoded tuples by length
LP_VOCAB_GP = {}  # length → set of GP-encoded tuples
for w in LP_VOCAB:
    enc = tuple(_gp_encode(w))
    if len(enc) >= 2:
        LP_VOCAB_GP.setdefault(len(enc), set()).add(enc)
# Also add solved-page words
for pg in solved_pages:
    _, swords = load_page(pg)
    for sw in swords:
        if len(sw) >= 2:
            LP_VOCAB_GP.setdefault(len(sw), set()).add(sw)

# Build word slot positions: (global_start_pos, word_length)
WORD_SLOTS = []
ki = 0
for w in words_all:
    WORD_SLOTS.append((ki, len(w)))
    ki += len(w)

def word_score(key_np):
    """Score decoded words against LP vocabulary."""
    score = 0
    for wstart, wlen in WORD_SLOTS:
        if wstart + wlen > N_CIPHER:
            break
        dec = tuple((int(CIPHER[wstart+i]) - int(key_np[wstart+i])) % M for i in range(wlen))
        txt = ''.join(IDX_TO[v] for v in dec)
        if txt in LP_VOCAB:
            score += len(txt) * 20 + 30
        elif any(lw in txt for lw in LP_VOCAB if len(lw) >= 5):
            score += 15
    return score

def word_refine_pass(key_np):
    """
    Word-level refinement: for each word slot, if the current decode is
    Hamming-1 from an LP vocab word of the same length, AND the change is
    TTP-consistent + doesn't conflict with locked cribs, apply the fix.
    Returns (refined_key, n_fixes).
    """
    key = key_np.copy()
    fixes = 0
    for wstart, wlen in WORD_SLOTS:
        if wstart + wlen > N_CIPHER or wlen < 3:
            continue
        dec = tuple((int(CIPHER[wstart+i]) - int(key[wstart+i])) % M for i in range(wlen))
        candidates = LP_VOCAB_GP.get(wlen, set())
        for cand in candidates:
            diffs = [(i, cand[i]) for i in range(wlen) if dec[i] != cand[i]]
            if len(diffs) != 1:
                continue  # only Hamming-1 corrections
            di, new_plain = diffs[0]
            pos = wstart + di
            canon = int(LINK_MAP[pos])
            if canon in CRIB_CANON_SET:
                continue  # locked crib position
            new_kv = (int(CIPHER[pos]) - new_plain) % M
            # Check singleton constraint
            if SING_A0[canon] >= 0 and new_kv != SING_A0[canon] and new_kv != SING_A1[canon]:
                continue  # violates singleton
            # Apply to canonical + propagate via TTP
            key[canon] = new_kv
            for src_s, dst_s, ln in TTP_CONSTRAINTS:
                for k_i in range(ln):
                    if LINK_MAP[src_s + k_i] == canon:
                        key[dst_s + k_i] = new_kv
                    if src_s + k_i == canon:
                        key[dst_s + k_i] = new_kv
            fixes += 1
            break  # applied one fix for this word, move on
    return key, fixes

# Word-refine interval (in save-blocks): every 5 save-blocks = every 50K steps
WORD_REFINE_INTERVAL = 5

# ─── Main loop ────────────────────────────────────────────────────────────────
print(f'\n=== GPU {GPU_ID} hillclimber v2 starting (N_CHAINS={N_CHAINS}) ===', flush=True)
print(f'Output: {OUTFILE}', flush=True)

# T=3.0 on warmstart: high enough that e^(-delta/T) gives real acceptance probability
# for typical delta~5-50 nats. T=0.08 was effectively frozen (e^(-5/0.08) ~ 0).
T_START = 3.0 if warmstart_score else 8.0
T_END   = 0.00005
T_DECAY = 0.9999993   # slightly slower cooling for more chains

temperature       = T_START
# Preserve warmstart key if checkpoint was better than any initialised chain.
# This prevents the checkpoint from being overwritten with a degraded key when
# the diversified population hasn't yet recovered the old best.
_init_best_idx   = int(cp_scores.argmax())
_init_best_score = float(cp_scores[_init_best_idx])
if warmstart_score and warmstart_score > _init_best_score:
    global_best_score = warmstart_score
    global_best_key   = ck_key.copy()   # preserve original checkpoint key exactly
    print(f'  Preserving checkpoint key (warmstart {warmstart_score:.1f} > init {_init_best_score:.1f})', flush=True)
else:
    global_best_score = _init_best_score
    global_best_key   = cp_keys[_init_best_idx].get()

# -- Stagnation detection for warm restarts --
stagnation_window   = 25   # save blocks (250K steps) without 50-point improvement
stagnation_counter  = 0
last_improvement_score = global_best_score
WARM_RESTART_TEMP   = 3.0  # must be high enough for real basin hopping (was 0.02=frozen)
exploration_lockout = 0    # blocks remaining where chain-restart is suppressed

blk = 256
grd = (N_CHAINS + blk - 1) // blk

with open(OUTFILE, 'w', encoding='utf-8') as fout:
    fout.write(f'GPU {GPU_ID} Hillclimber v2 — Start {time.strftime("%H:%M:%S")}\n')
    fout.write(f'N_CHAINS={N_CHAINS}, T_START={T_START}\n')
    fout.write('='*60 + '\n')

step     = 0
t_last   = time.time()
# Use a 64-bit seed that changes every step via a fast LCG
seed_state = (GPU_ID * 0xDEADBEEF + 1) & 0xFFFFFFFFFFFFFFFF
SEED_MUL   = 6364136223846793005
SEED_ADD   = 1442695040888963407
MASK64     = 0xFFFFFFFFFFFFFFFF

while True:
    step += 1

    # ── OPT-1: Fused GPU step — no CPU involvement until SAVE_EVERY ──────
    seed_state = (seed_state * SEED_MUL + SEED_ADD) & MASK64
    STEP_KERNEL((grd,), (blk,),
        (cp_cipher, cp_keys.ravel(), cp_scores, cp_qgram,
         cp_indep, cp_sing_a0, cp_sing_a1,
         cp.int32(N_CIPHER), cp.int32(N_CHAINS), cp.int32(N_INDEPENDENT),
         cp.float32(temperature), cp.uint64(int(seed_state))))
    # No synchronize() needed here — kernel is fire-and-forget.
    # The sync happens implicitly when we read cp_scores at SAVE_EVERY.

    temperature = max(T_END, temperature * T_DECAY)

    # ── OPT-2: NO enforce_twotimepad_gpu() here ───────────────────────────
    # Mirror positions are never mutated (STEP_KERNEL only touches indep_pos).
    # TTP is enforced only at init and chain restarts below.

    if step % SAVE_EVERY != 0:
        continue

    # ──────────────────────────────────────────────────────────────────────
    # SAVE BLOCK (every SAVE_EVERY steps) — this is the only place we sync
    # ──────────────────────────────────────────────────────────────────────
    cp.cuda.Stream.null.synchronize()   # flush all pending GPU work

    cur_best_idx   = int(cp_scores.argmax())
    cur_best_score = float(cp_scores[cur_best_idx])
    if cur_best_score > global_best_score:
        global_best_score = cur_best_score
        global_best_key   = cp_keys[cur_best_idx].get()

    elapsed = time.time() - t_last
    rate    = SAVE_EVERY / elapsed
    t_last  = time.time()

    ws        = word_score(global_best_key)
    sing_hits = sum(
        1 for sp, sc in zip(SING_POS, SING_CIP)
        if (sc - int(global_best_key[sp])) % M in (10, 24)
    )

    # Noise attractor detection
    NOISE_PATTERNS = ['DPTS', 'CDPI', 'TSUH', 'EATSUH', 'TSEATS']
    full_decode_str = ''.join(
        IDX_TO[(int(CIPHER[i]) - int(global_best_key[i])) % M]
        for i in range(min(N_CIPHER, 5000))  # sample first 5K for speed
    )
    noise_count = sum(full_decode_str.count(p) for p in NOISE_PATTERNS)

    # Per-page IoC for top-level health check (sample 5 pages)
    page_ioc_strs = []
    for pg_check in [21, 25, 31, 40, 50]:
        if pg_check in page_offsets:
            ps = page_offsets[pg_check]
            pl = sum(len(r) for r, _ in [load_page(pg_check)])
            if pl > 20:
                dec = [(int(CIPHER[ps+j]) - int(global_best_key[ps+j])) % M for j in range(pl)]
                freq = Counter(dec)
                ioc_val = sum(f*(f-1) for f in freq.values()) / max(1, pl*(pl-1)) * M
                page_ioc_strs.append(f'P{pg_check}={ioc_val:.2f}')

    # Decode first 30 words using word slot positions
    plain_preview = []
    for wi, (wstart, wlen) in enumerate(WORD_SLOTS[:30]):
        if wstart + wlen > N_CIPHER:
            break
        word_dec = []
        for i in range(wlen):
            word_dec.append(IDX_TO[(int(CIPHER[wstart+i]) - int(global_best_key[wstart+i])) % M])
        plain_preview.append(''.join(word_dec))
    preview = ' '.join(plain_preview)

    ioc_info = ' | '.join(page_ioc_strs) if page_ioc_strs else 'N/A'
    msg = (f'Step {step:,} | Score={global_best_score:.1f} | WordScore={ws} | '
           f'Singletons={sing_hits}/{N_SING} | '
           f'Noise={noise_count} | '
           f'Temp={temperature:.7f} | Rate={rate:.0f}steps/s\n'
           f'  IoC: {ioc_info}\n'
           f'  Preview: {preview}\n')
    print(msg, end='', flush=True)

    # ── Stagnation detection: warm restart if score plateaus ──────────
    if global_best_score > last_improvement_score + 50:
        last_improvement_score = global_best_score
        stagnation_counter = 0
    else:
        stagnation_counter += 1
    if stagnation_counter >= stagnation_window and temperature < WARM_RESTART_TEMP:
        temperature = WARM_RESTART_TEMP
        stagnation_counter = 0
        # Nuclear scatter: diversify the population to escape the current basin.
        # Top 15% stay near best (preserve memory); bottom 50% get large scatter.
        keys_np  = cp_keys.get()
        best_np  = global_best_key.copy()
        n        = N_CHAINS
        for ci_idx in range(n * 15 // 100):
            ci  = rng.integers(0, n)
            n_p = rng.integers(50, 300)
            pp  = rng.choice(INDEPENDENT_POS, size=n_p, replace=False)
            keys_np[ci]     = best_np.copy()
            keys_np[ci, pp] = rng.integers(0, M, size=n_p)
        for ci in range(n // 2, n):
            n_p = rng.integers(2000, N_INDEPENDENT)
            pp  = rng.choice(INDEPENDENT_POS, size=n_p, replace=False)
            keys_np[ci]     = best_np.copy()
            keys_np[ci, pp] = rng.integers(0, M, size=n_p)
        enforce_singletons(keys_np)
        enforce_cribs(keys_np)
        enforce_ttp(keys_np)
        cp_keys = cp.array(keys_np, dtype=cp.int32)
        compute_all_scores()
        # Set stagnation_counter to -100 so next nuclear restart is 125 blocks away
        # and lock out chain restarts for 100 blocks so scattered chains can converge.
        stagnation_counter  = -100
        exploration_lockout = 100
        print(f'  [nuclear-restart] Stagnated {stagnation_window} blocks, '
              f'T→{WARM_RESTART_TEMP}, chains scattered (50% large-perturbed). '
              f'Lockout=100 blocks.', flush=True)

    # Save checkpoint (JSON — compatible with v1 checkpoint format)
    ck_data = {
        'step':       step,
        'mode':       'sub',
        'score':      global_best_score,
        'wordscore':  ws,
        'singletons': sing_hits,
        'noise':      noise_count,
        'key':        list(map(int, global_best_key)),
    }
    Path(CHECKPOINT).write_text(json.dumps(ck_data))

    with open(OUTFILE, 'a', encoding='utf-8') as fout:
        fout.write(msg)

    # ── Chain restart: every 10 saves, revive worst 10% from best ────────
    save_block = step // SAVE_EVERY
    # Skip chain restart during exploration lockout (after nuclear scatter)
    if exploration_lockout > 0:
        exploration_lockout -= 1
    elif save_block % 10 == 0:
        scores_np = cp_scores.get()
        worst_idx = np.argsort(scores_np)[:N_CHAINS // 10]
        best_np   = cp_keys[int(np.argmax(scores_np))].get()
        keys_np   = cp_keys.get()
        for wi in worst_idx:
            n_p = rng.integers(200, 1500)  # wider scatter than before (was 100-500)
            pp  = rng.choice(INDEPENDENT_POS, size=n_p, replace=False)
            pv  = rng.integers(0, M, size=n_p)
            keys_np[wi] = best_np.copy()
            keys_np[wi, pp] = pv
        enforce_singletons(keys_np)
        enforce_cribs(keys_np)
        enforce_ttp(keys_np)   # OPT-2: only enforce TTP here
        cp_keys = cp.array(keys_np, dtype=cp.int32)
        compute_all_scores()
        print(f'  [restart] Revived {len(worst_idx)} chains, re-scored.', flush=True)

    # ── Word-level refinement: periodically patch Hamming-1 LP words ─────
    if save_block % WORD_REFINE_INTERVAL == 0 and save_block > 0:
        refined_key, n_fixes = word_refine_pass(global_best_key)
        if n_fixes > 0:
            # Seed a few chains with the refined key (varying perturbation)
            keys_np = cp_keys.get()
            n_seeded = min(N_CHAINS // 20, 200)  # 5% of chains
            for si in range(n_seeded):
                ci = rng.integers(0, N_CHAINS)
                n_p = rng.integers(10, 50)
                pp = rng.choice(INDEPENDENT_POS, size=n_p, replace=False)
                pv = rng.integers(0, M, size=n_p)
                keys_np[ci] = refined_key.copy()
                keys_np[ci, pp] = pv
            enforce_singletons(keys_np)
            enforce_cribs(keys_np)
            enforce_ttp(keys_np)
            cp_keys = cp.array(keys_np, dtype=cp.int32)
            compute_all_scores()
            new_best_idx = int(cp_scores.argmax())
            new_best_sc  = float(cp_scores[new_best_idx])
            if new_best_sc > global_best_score:
                global_best_score = new_best_sc
                global_best_key   = cp_keys[new_best_idx].get()
            print(f'  [word-refine] Applied {n_fixes} Hamming-1 LP corrections, '
                  f'seeded {n_seeded} chains. Best={global_best_score:.1f}', flush=True)
