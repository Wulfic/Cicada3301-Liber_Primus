"""
GPU-Accelerated Hillclimber v4 -- Liber Primus P21-P54
======================================================
Changes vs v3:
  1. CONFIRMED CRIBS LOADED -- 590 LP_CANON words (len>=5) from v3 decode
     → 3058 canonical positions locked (never mutated)
     → Only 7753 free canonical positions in mutation set
     → enforce_cribs() called at init + stagnation scatter + chain restart
  2. Warmstart chain: v4 checkpoint → v3 checkpoint → v2 checkpoint
  3. All other v3 features preserved:
     - Hybrid scoring (quadgrams + LP word-slot bonus)
     - 65536 chains
     - Stagnation restart with nuclear scatter
     - Word-level refinement

Why cribs are now safe (unlike v2):
  - All 3058 crib positions come from LP_CANON words of length>=5
  - All cribs are word-boundary-aligned (word slots are preserved in cipher)
  - ALL are TTP-consistent (verified by extract_confirmed_cribs.py)
  - The v3 score was stuck for 7.3M steps -- cribs are needed to escape

Usage: python gpu_hillclimber_v4.py <gpu_id>
"""

import sys, os, time, math, json
from pathlib import Path
from collections import Counter
import numpy as np
import cupy as cp

sys.stdout.reconfigure(encoding='utf-8')

# --- Config -----------------------------------------------------------------
GPU_ID     = int(sys.argv[1]) if len(sys.argv) > 1 else 1
# v4: Same chain count as v3 but with confirmed cribs locked.
# 3058 canonical positions locked from v3 confirmed LP words.
# Only 7753 free canonical positions remain in mutation set.
N_CHAINS   = 65_536
SAVE_EVERY = 10_000
OUTFILE    = f'data/gpu_hill_v4_gpu{GPU_ID}.txt'
CHECKPOINT = f'data/gpu_hill_checkpoint_gpu{GPU_ID}_v4.json'
CRIBS_FILE = 'data/v3_confirmed_cribs.json'
M          = 29

# Word-slot scoring parameters
WORD_WEIGHT = 15.0   # nats per unit of (wl - min_HD); exact len-10 match = +150
MAX_LP_LEN  = 18     # ignore solved-page words longer than this (titles/concatenations)
N_LP_CAP    = 50     # max LP words to check per length in GPU kernel

# --- GP Alphabet -------------------------------------------------------------
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

def _gp_encode(phrase):
    w = phrase.upper().replace(' ', ''); r = []; i = 0
    while i < len(w):
        if i+1 < len(w) and w[i:i+2] in LETTER_TO_GP:
            r.append(LETTER_TO_GP[w[i:i+2]]); i += 2
        elif w[i] in LETTER_TO_GP:
            r.append(LETTER_TO_GP[w[i]]); i += 1
        else: i += 1
    return r

# --- Data Loading ------------------------------------------------------------
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

CIPHER   = np.array(cipher_list, dtype=np.int32)
N_CIPHER = len(CIPHER)
print(f'  Cipher length: {N_CIPHER} runes', flush=True)

# --- TTP constraints ---------------------------------------------------------
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

# --- Load confirmed cribs from v3 decode analysis ---------------------------
# These are LP_CANON words (len>=5) confirmed in v3 checkpoint decode.
# All 3058 canonical positions are TTP-consistent (verified).
# Removing these from INDEPENDENT_POS means the kernel never mutates them.
CONFIRMED_CRIBS  = []
FORCED_CRIBS_POS = {}
CRIB_CANON_SET   = set()
if Path(CRIBS_FILE).exists():
    crib_data = json.loads(Path(CRIBS_FILE).read_text())
    FORCED_CRIBS_POS = {int(k): v for k, v in crib_data['forced_cribs_pos'].items()}
    CRIB_CANON_SET   = set(FORCED_CRIBS_POS.keys())
    print(f'  Loaded {len(FORCED_CRIBS_POS)} confirmed cribs from {CRIBS_FILE}', flush=True)
else:
    print(f'  WARNING: Cribs file {CRIBS_FILE} not found -- running without cribs', flush=True)

# INDEPENDENT_POS built AFTER cribs are loaded, so crib positions are excluded
_all_canonical = [i for i in range(N_CIPHER) if LINK_MAP[i] == i]
INDEPENDENT_POS = np.array([i for i in _all_canonical if i not in CRIB_CANON_SET], dtype=np.int32)
N_INDEPENDENT   = len(INDEPENDENT_POS)
INDEPENDENT_SET = set(INDEPENDENT_POS.tolist())
print(f'  TTP: {sum(ln for _,_,ln in TTP_CONSTRAINTS)} linked -> {len(_all_canonical)} canonical -> {N_INDEPENDENT} free (after cribs)', flush=True)

def enforce_ttp(keys_np):
    for src_s, dst_s, ln in TTP_CONSTRAINTS:
        keys_np[:, dst_s:dst_s+ln] = keys_np[:, src_s:src_s+ln]

def enforce_cribs(keys_np):
    """Set confirmed crib positions to their required key values in all chains."""
    for canon_pos, key_val in FORCED_CRIBS_POS.items():
        keys_np[:, canon_pos] = key_val

# --- Singleton constraints ----------------------------------------------------
singleton_positions = []; singleton_cipher = []; pos = 0
for w in words_all:
    if len(w) == 1:
        singleton_positions.append(pos); singleton_cipher.append(w[0])
    pos += len(w)
SING_POS = np.array(singleton_positions, dtype=np.int32)
SING_CIP = np.array(singleton_cipher,   dtype=np.int32)
N_SING   = len(SING_POS)
print(f'  Singleton constraints: {N_SING}', flush=True)

SING_A0 = np.full(N_CIPHER, -1, dtype=np.int32)
SING_A1 = np.full(N_CIPHER, -1, dtype=np.int32)
for s, sp in enumerate(SING_POS):
    canon = int(LINK_MAP[sp])
    sc = int(SING_CIP[s])
    SING_A0[canon] = (sc - 10) % M   # key -> I
    SING_A1[canon] = (sc - 24) % M   # key -> A

def enforce_singletons(keys_np):
    rng_ = np.random.default_rng()
    for sp, sc in zip(SING_POS, SING_CIP):
        canon_sp = int(LINK_MAP[sp])
        a0 = (sc - 10) % M
        a1 = (sc - 24) % M
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
        if sp != canon_sp:
            keys_np[:, sp] = keys_np[:, canon_sp]

# --- Word-slot arrays (per-position) -----------------------------------------
# WS_START_ARR[i] = start of the word slot containing cipher position i
# WS_LEN_ARR[i]   = length of that word slot
WS_START_ARR = np.zeros(N_CIPHER, dtype=np.int32)
WS_LEN_ARR   = np.zeros(N_CIPHER, dtype=np.int32)
ki = 0
for w in words_all:
    wl = len(w)
    for t in range(wl):
        WS_START_ARR[ki + t] = ki
        WS_LEN_ARR[ki + t]   = wl
    ki += wl

# Flat word-slot arrays for SCORE_KERNEL
WORD_SLOTS = []
ki = 0
for w in words_all:
    WORD_SLOTS.append((ki, len(w)))
    ki += len(w)
N_WORD_SLOTS = len(WORD_SLOTS)
WS_FLAT_S = np.array([s for s, l in WORD_SLOTS], dtype=np.int32)
WS_FLAT_L = np.array([l for s, l in WORD_SLOTS], dtype=np.int32)
print(f'  Word slots: {N_WORD_SLOTS}', flush=True)

# --- LP vocabulary table for GPU word-slot scoring ----------------------------
print('Building LP word table...', flush=True)
solved_pages = list(range(0, 21)) + list(range(55, 75))

_lp_freq = Counter()
for pg in solved_pages:
    _, swords = load_page(pg)
    for sw in swords:
        if 2 <= len(sw) <= MAX_LP_LEN:
            _lp_freq[sw] += 1

# Boost canonical LP words (confirmed vocabulary from known LP passages)
_LP_CANON = [
    'CONSUMPTION','PRESERUATION','PRESERVATION','ADHERENCE',
    'SOMEWISDOM','DIUINITY','DIVINITY','CIRCUMFERENCE','CIRCUMFERENC',
    'THELOSSOF','THELOSSOFDIUINITY','PROGRAM','REALITY','MIND',
    'PRIMES','SACRED','ENCRYPTED','KNOWTHIS','KNOW','THIS',
    'WISDOM','AN','INSTRUCTION','BEHAVIORS','PRACTICES','LOSS',
    'PREPARED','DESTROY','FOLLOW','TRUTH','IMPOSE','NOTHING','OTHERS',
    'SEEK','WELCOME','PILGRIM','WITHIN','ALL','THE','THAT','WHICH',
    'CAUSE','THREE','AMASS','GREAT','WEALTH','NEUER','NEVER',
    'BECOME','ATTACHED','WHAT','YOU','OWN','QUESTION','DISCOVER',
    'YOURSELF','INSIDE','HOLY','BEING','EACH','FORM','EMERGE',
    'INSTAR','PARABLE','SHADOW','VOID','CARNAL','AETHEREAL',
    'DECEPTION','MOBIUS','OBSCURA','CABAL','INTELLIGENCE',
    'TOTIENT','PRIME','DIVINE','PATH','STRENGTH','PAIN',
]
for w in _LP_CANON:
    enc = tuple(_gp_encode(w))
    if enc and 2 <= len(enc) <= MAX_LP_LEN:
        _lp_freq[enc] = max(_lp_freq.get(enc, 0), 5)

# Sort by length, then frequency desc, cap per length
_vocab_by_len = {}
for word, freq in _lp_freq.items():
    l = len(word)
    _vocab_by_len.setdefault(l, []).append((freq, word))

lp_len_start_list = [0] * (MAX_LP_LEN + 2)
lp_len_cnt_list   = [0] * (MAX_LP_LEN + 1)
lp_words_rows     = []
for l in range(2, MAX_LP_LEN + 1):
    words_sorted = sorted(_vocab_by_len.get(l, []), reverse=True)[:N_LP_CAP]
    lp_len_start_list[l] = len(lp_words_rows)
    lp_len_cnt_list[l]   = len(words_sorted)
    for freq, w in words_sorted:
        padded = list(w) + [0] * (MAX_LP_LEN - len(w))
        lp_words_rows.append(padded)
lp_len_start_list[MAX_LP_LEN + 1] = len(lp_words_rows)

N_LP_TOTAL   = len(lp_words_rows)
LP_WORDS_NP  = np.array(lp_words_rows, dtype=np.int32)   # [N_LP_TOTAL, MAX_LP_LEN]
LP_LEN_START = np.array(lp_len_start_list, dtype=np.int32)
LP_LEN_CNT   = np.array(lp_len_cnt_list,   dtype=np.int32)
print(f'  LP vocab: {N_LP_TOTAL} words (capped {N_LP_CAP}/len), lengths 2-{MAX_LP_LEN}', flush=True)
for l in range(2, MAX_LP_LEN + 1):
    if lp_len_cnt_list[l] > 0:
        print(f'    len={l:2}: {lp_len_cnt_list[l]:3} words', flush=True)

# --- Quadgram scoring table ---------------------------------------------------
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

all_english_gp = []
for corpus_file in ['data/self_reliance.txt', 'data/emerson_essays.txt']:
    cp_path = Path(corpus_file)
    if cp_path.exists():
        raw = cp_path.read_text(encoding='utf-8', errors='ignore')
        cleaned = ''.join(c for c in raw.upper() if c.isalpha() or c == ' ')
        all_english_gp.extend(text_to_gp(cleaned))
        print(f'  Corpus {corpus_file}: {len(raw)} chars', flush=True)

qgram_count = Counter()
for _ in range(3):
    for i in range(len(all_known_gp) - 3):
        qgram_count[tuple(all_known_gp[i:i+4])] += 1
for i in range(len(all_english_gp) - 3):
    qgram_count[tuple(all_english_gp[i:i+4])] += 1

total_q = sum(qgram_count.values()) + M**4
print(f'  Quadgrams: {len(qgram_count)} distinct', flush=True)

QGRAM_TABLE = np.full(M**4, math.log(1.0 / total_q), dtype=np.float32)
for (a,b,c,d), cnt in qgram_count.items():
    idx = a*M**3 + b*M**2 + c*M + d
    QGRAM_TABLE[idx] = math.log((cnt + 1.0) / total_q)

# --- GPU Setup ----------------------------------------------------------------
print(f'\nInitializing GPU {GPU_ID}...', flush=True)
cp.cuda.Device(GPU_ID).use()

cp_cipher     = cp.array(CIPHER,       dtype=cp.int32)
cp_qgram      = cp.array(QGRAM_TABLE,  dtype=cp.float32)
cp_sing_a0    = cp.array(SING_A0,      dtype=cp.int32)
cp_sing_a1    = cp.array(SING_A1,      dtype=cp.int32)
cp_indep      = cp.array(INDEPENDENT_POS, dtype=cp.int32)
# Word-slot scoring arrays
cp_ws_s_arr   = cp.array(WS_START_ARR, dtype=cp.int32)   # [N_CIPHER]
cp_ws_l_arr   = cp.array(WS_LEN_ARR,   dtype=cp.int32)   # [N_CIPHER]
cp_ws_flat_s  = cp.array(WS_FLAT_S,    dtype=cp.int32)   # [N_WORD_SLOTS]
cp_ws_flat_l  = cp.array(WS_FLAT_L,    dtype=cp.int32)   # [N_WORD_SLOTS]
cp_lp_wf      = cp.array(LP_WORDS_NP.ravel(), dtype=cp.int32)  # [N_LP_TOTAL * MAX_LP_LEN]
cp_lp_ls      = cp.array(LP_LEN_START, dtype=cp.int32)   # [MAX_LP_LEN+2]
cp_lp_lc      = cp.array(LP_LEN_CNT,  dtype=cp.int32)    # [MAX_LP_LEN+1]

print(f'  GPU memory used: {cp.get_default_memory_pool().used_bytes()//1024//1024} MB', flush=True)

# --- Full-score kernel (used at init and chain restart) ---------------------
# Hybrid: quadgrams + LP word-slot bonus
SCORE_KERNEL = cp.RawKernel(r'''
extern "C" __global__
void score_keys(
    const int*   cipher,
    const int*   key,
    const float* qgram,
    float*       scores,
    const int*   ws_flat_s,
    const int*   ws_flat_l,
    const int*   lp_wf,
    const int*   lp_ls,
    const int*   lp_lc,
    float        word_wt,
    int          lp_lmax,
    int          N_CIPHER,
    int          N_CHAINS,
    int          N_WS
) {
    int chain = blockIdx.x * blockDim.x + threadIdx.x;
    if (chain >= N_CHAINS) return;
    const int* k = key + chain * N_CIPHER;
    float score = 0.0f;

    // -- Quadgram scoring --------------------------------------------------
    int plain[4];
    for (int i = 0; i < 4 && i < N_CIPHER; i++)
        plain[i] = (cipher[i] - k[i] + 29) % 29;
    for (int i = 4; i < N_CIPHER; i++) {
        int p = (cipher[i] - k[i] + 29) % 29;
        int idx = plain[(i-3)&3]*24389 + plain[(i-2)&3]*841 + plain[(i-1)&3]*29 + p;
        score += qgram[idx];
        plain[i&3] = p;
    }

    // -- Word-slot scoring -------------------------------------------------
    for (int wi = 0; wi < N_WS; wi++) {
        int ws = ws_flat_s[wi];
        int wl = ws_flat_l[wi];
        if (wl < 2 || wl > lp_lmax) continue;
        int nlp = lp_lc[wl];
        if (nlp == 0) continue;
        int lp_st  = lp_ls[wl];
        int best_hd = wl;
        for (int w2 = 0; w2 < nlp && best_hd > 0; w2++) {
            int base = (lp_st + w2) * lp_lmax;
            int hd = 0;
            for (int t = 0; t < wl; t++) {
                int pt = (cipher[ws+t] - k[ws+t] + 29) % 29;
                if (pt != lp_wf[base+t]) hd++;
                if (hd >= best_hd) break;
            }
            if (hd < best_hd) best_hd = hd;
        }
        score += word_wt * (float)(wl - best_hd);
    }

    scores[chain] = score;
}
''', 'score_keys')

# --- Fused Step Kernel (hot loop) --------------------------------------------
# Extends v2 with word-slot delta: changing position j affects exactly one
# word slot.  We compute the change in LP-word-closeness score for that slot.
# Performance: LP word table (~130 KB) fits in GPU L2 cache; key reads for
# the word slot overlap with already-cached quadgram reads. Overhead ~<5%.
STEP_KERNEL = cp.RawKernel(r'''
extern "C" __global__
void markov_step(
    const int*         cipher,
    int*               key,
    float*             scores,
    const float*       qgram,
    const int*         indep_pos,
    const int*         sing_a0,
    const int*         sing_a1,
    const int*         ws_s_arr,
    const int*         ws_l_arr,
    const int*         lp_wf,
    const int*         lp_ls,
    const int*         lp_lc,
    float              word_wt,
    int                lp_lmax,
    int                N_CIPHER,
    int                N_CHAINS,
    int                N_INDEPENDENT,
    float              temperature,
    unsigned long long step_seed
) {
    int chain = blockIdx.x * blockDim.x + threadIdx.x;
    if (chain >= N_CHAINS) return;

    // -- xorshift64 per-thread RNG -----------------------------------------
    unsigned long long rng = step_seed ^ ((unsigned long long)chain * 6364136223846793005ULL + 1442695040888963407ULL);
    rng ^= rng >> 33; rng *= 0xff51afd7ed558ccdULL;
    rng ^= rng >> 33; rng *= 0xc4ceb9fe1a85ec53ULL;
    rng ^= rng >> 33;
    #define NEXT_RNG() (rng ^= rng >> 12, rng ^= rng << 25, rng ^= rng >> 27, rng)

    // -- Pick random independent position ---------------------------------
    unsigned long long r1 = NEXT_RNG();
    int pos_idx = (int)(r1 % (unsigned long long)N_INDEPENDENT);
    int j = indep_pos[pos_idx];

    // -- Pick new key value ------------------------------------------------
    unsigned long long r2 = NEXT_RNG();
    int new_val;
    int a0 = sing_a0[j];
    if (a0 >= 0) {
        new_val = (r2 & 1ULL) ? sing_a1[j] : a0;
    } else {
        new_val = (int)(r2 % 29ULL);
    }

    int* k = key + chain * N_CIPHER;
    int old_val = k[j];
    if (old_val == new_val) return;

    // -- Delta: quadgram contribution --------------------------------------
    float d = 0.0f;
    int start_min = j - 3; if (start_min < 0) start_min = 0;
    int start_max = j;     if (start_max > N_CIPHER - 4) start_max = N_CIPHER - 4;

    for (int start = start_min; start <= start_max; start++) {
        int old_idx = 0, new_idx = 0;
        for (int t = 0; t < 4; t++) {
            int pos  = start + t;
            int c    = cipher[pos];
            int kold = (pos == j) ? old_val : k[pos];
            int knew = (pos == j) ? new_val : k[pos];
            int pold = (c - kold + 29) % 29;
            int pnew = (c - knew + 29) % 29;
            old_idx = old_idx * 29 + pold;
            new_idx = new_idx * 29 + pnew;
        }
        d += qgram[new_idx] - qgram[old_idx];
    }

    // -- Delta: word-slot contribution ------------------------------------
    // Changing position j affects exactly the one word slot containing j.
    // For each LP word of the same length, recompute HD (old vs new key).
    {
        int wl = ws_l_arr[j];
        if (wl >= 2 && wl <= lp_lmax) {
            int nlp = lp_lc[wl];
            if (nlp > 0) {
                int ws    = ws_s_arr[j];
                int ofs   = j - ws;          // offset of j within the word
                int old_pj = (cipher[j] - old_val + 29) % 29;
                int new_pj = (cipher[j] - new_val + 29) % 29;
                int lp_st  = lp_ls[wl];
                int best_old = wl, best_new = wl;

                for (int wi = 0; wi < nlp; wi++) {
                    int base = (lp_st + wi) * lp_lmax;
                    // Count mismatches at all positions except j (same for old/new)
                    int hd_nj = 0;
                    for (int t = 0; t < wl; t++) {
                        if (t == ofs) continue;
                        int pt = (cipher[ws+t] - k[ws+t] + 29) % 29;
                        if (pt != lp_wf[base+t]) hd_nj++;
                    }
                    int hd_old_wi = hd_nj + (old_pj != lp_wf[base+ofs] ? 1 : 0);
                    int hd_new_wi = hd_nj + (new_pj != lp_wf[base+ofs] ? 1 : 0);
                    if (hd_old_wi < best_old) best_old = hd_old_wi;
                    if (hd_new_wi < best_new) best_new = hd_new_wi;
                }
                d += word_wt * (float)((wl - best_new) - (wl - best_old));
            }
        }
    }

    // -- Metropolis acceptance ---------------------------------------------
    bool accept = (d >= 0.0f);
    if (!accept && temperature > 1e-9f) {
        unsigned long long r3 = NEXT_RNG();
        float rf = (float)(r3 >> 11) * (1.0f / 9007199254740992.0f);
        accept = (rf < expf(d / temperature));
    }

    if (accept) {
        k[j]          = new_val;
        scores[chain] += d;
    }

    #undef NEXT_RNG
}
''', 'markov_step')

# --- Initialise chains --------------------------------------------------------
print(f'\nInitialising {N_CHAINS} chains on GPU {GPU_ID}...', flush=True)
rng = np.random.default_rng(GPU_ID * 99991 + 33337)
KEYS = rng.integers(0, M, size=(N_CHAINS, N_CIPHER), dtype=np.int32)

# Old crib positions (v2 cribs, now freed): scatter these heavily on warmstart
OLD_CRIB_POSITIONS = list({
    31,32,33,34,35,36,37,38,39,40,           # CONSUMPTION
    476,477,478,479,480,481,482,              # KNOWTHIS
    599,600,601,602,603,604,605,              # PROGRAM
    1356,1357,1358,1359,1360,1361,1362,1363, # DIUINITY
    2093,2094,2095,2096,2097,2098,2099,2100,2101,2102,2103,  # ADHERENCE
    4131,4132,4133,4134,4135,4136,4137,4138,4139,4140,       # SOMEWISDOM
    4325,4326,4327,4328,4329,4330,4331,4332,4333,4334,4335,4336,4337,4338,4339,4340, # THELOSSOFDIUINITY
    3080,3081,3082,3083,3084,3085,3086,3087,3088,3089,3090,3091,3092,                # CIRCUMFERENCE
    8532,8533,8534,8535,8536,8537,8538,8539,8540,            # ADHERENCE2
})

warmstart_score = None

def _vectorized_warmstart(ck_key, scatter_old_cribs=False):
    """Seed all chains from ck_key with tiered perturbation (vectorized, fast for N=131K)."""
    n = N_CHAINS
    ni = N_INDEPENDENT
    # Tier sizes
    n_fine   = n // 10        # 10%: tiny perturb  (10-53 pos)
    n_small  = n // 3 - n_fine  # 23%: small perturb (214 pos)
    n_large  = 2*n//3 - n//3  # 33%: large perturb (2144 pos)
    # bottom 34%: near-random
    KEYS[:] = ck_key[np.newaxis, :]  # broadcast best key to all chains

    def _perturb(ci_start, ci_end, n_pos_lo, n_pos_hi):
        for ci in range(ci_start, ci_end):
            n_p = rng.integers(n_pos_lo, n_pos_hi + 1)
            pp  = rng.choice(INDEPENDENT_POS, size=n_p, replace=False)
            KEYS[ci, pp] = rng.integers(0, M, size=n_p)

    print(f'  Seeding {n} chains (tiered)...', flush=True)
    _perturb(0,       n_fine,      10,    max(10, ni//200))
    _perturb(n_fine,  n_fine+n_small, max(100, ni//50), max(200, ni//20))
    _perturb(n_fine+n_small, 2*n//3,  max(1000, ni//5), max(2000, ni//3))
    _perturb(2*n//3, n,             max(3000, ni//2), ni)

    if scatter_old_cribs:
        old_indep = [op for op in OLD_CRIB_POSITIONS if op < N_CIPHER and LINK_MAP[op] == op]
        for op in old_indep:
            KEYS[:, op] = rng.integers(0, M, size=n)
        print(f'  Scattered {len(old_indep)} former crib positions across all chains.', flush=True)

if Path(CHECKPOINT).exists():
    ck = json.loads(Path(CHECKPOINT).read_text())
    ck_key = np.array(ck['key'], dtype=np.int32)
    warmstart_score = float(ck.get('score', 0))
    warmstart_temp  = float(ck.get('temperature', 0))  # 0 → use default below
    print(f'Warmstart from {CHECKPOINT}: score={warmstart_score}, step={ck.get("step","?")}, T={warmstart_temp:.6f}', flush=True)
    _vectorized_warmstart(ck_key, scatter_old_cribs=False)
elif Path(f'data/gpu_hill_checkpoint_gpu{GPU_ID}_v3.json').exists():
    # Warmstart from v3 checkpoint (confirmed LP cribs already extracted from this)
    ck = json.loads(Path(f'data/gpu_hill_checkpoint_gpu{GPU_ID}_v3.json').read_text())
    ck_key = np.array(ck['key'], dtype=np.int32)
    warmstart_score = float(ck.get('score', 0))
    warmstart_temp  = float(ck.get('temperature', 0))
    print(f'Warmstart from v3 checkpoint: score={warmstart_score}, T={warmstart_temp:.6f}', flush=True)
    _vectorized_warmstart(ck_key, scatter_old_cribs=False)
elif Path(f'data/gpu_hill_checkpoint_gpu{GPU_ID}.json').exists():
    # Warmstart from v2 checkpoint, scatter old crib positions heavily
    ck = json.loads(Path(f'data/gpu_hill_checkpoint_gpu{GPU_ID}.json').read_text())
    ck_key = np.array(ck['key'], dtype=np.int32)
    warmstart_score = float(ck.get('score', 0))
    print(f'Warmstart from v2 checkpoint: score={warmstart_score}', flush=True)
    _vectorized_warmstart(ck_key, scatter_old_cribs=True)
else:
    print('Cold start (no checkpoint found).', flush=True)

enforce_singletons(KEYS)
enforce_ttp(KEYS)
enforce_cribs(KEYS)  # v4: enforce all 3058 confirmed LP word positions

cp_keys   = cp.array(KEYS, dtype=cp.int32)
cp_scores = cp.zeros(N_CHAINS, dtype=cp.float32)

def compute_all_scores():
    blk = 256; grd = (N_CHAINS + blk - 1) // blk
    SCORE_KERNEL((grd,), (blk,),
        (cp_cipher, cp_keys.ravel(), cp_qgram, cp_scores,
         cp_ws_flat_s, cp_ws_flat_l,
         cp_lp_wf, cp_lp_ls, cp_lp_lc,
         cp.float32(WORD_WEIGHT), cp.int32(MAX_LP_LEN),
         cp.int32(N_CIPHER), cp.int32(N_CHAINS), cp.int32(N_WORD_SLOTS)))
    cp.cuda.Stream.null.synchronize()

print('Computing initial scores...', flush=True)
compute_all_scores()
print(f'  Score range: {float(cp_scores.min()):.1f} .. {float(cp_scores.max()):.1f}', flush=True)
print(f'  Mean: {float(cp_scores.mean()):.1f}', flush=True)

# --- LP vocab for word scoring (Python-side, for logging) --------------------
LP_VOCAB = set()
for pg in solved_pages:
    _, swords = load_page(pg)
    for sw in swords:
        LP_VOCAB.add(''.join(IDX_TO[v] for v in sw))
for w in _LP_CANON:
    LP_VOCAB.add(w.upper())

def word_score(key_np):
    score = 0
    for wstart, wlen in WORD_SLOTS:
        if wstart + wlen > N_CIPHER: break
        dec = ''.join(IDX_TO[(int(CIPHER[wstart+i]) - int(key_np[wstart+i])) % M] for i in range(wlen))
        if dec in LP_VOCAB:
            score += wlen * 20 + 30
        elif any(lw in dec for lw in LP_VOCAB if len(lw) >= 5):
            score += 15
    return score

def word_refine_pass(key_np):
    """Apply Hamming-1 LP corrections at word boundaries."""
    # Build GP word table by length for fast lookup
    lp_gp_by_len = {}
    for pg in solved_pages:
        _, swords = load_page(pg)
        for sw in swords:
            if 2 <= len(sw) <= MAX_LP_LEN:
                lp_gp_by_len.setdefault(len(sw), set()).add(sw)
    for w in _LP_CANON:
        enc = tuple(_gp_encode(w))
        if enc and 2 <= len(enc) <= MAX_LP_LEN:
            lp_gp_by_len.setdefault(len(enc), set()).add(enc)

    key = key_np.copy(); fixes = 0
    for wstart, wlen in WORD_SLOTS:
        if wstart + wlen > N_CIPHER or wlen < 3: continue
        dec = tuple((int(CIPHER[wstart+i]) - int(key[int(LINK_MAP[wstart+i])])) % M for i in range(wlen))
        candidates = lp_gp_by_len.get(wlen, set())
        for cand in candidates:
            diffs = [(i, cand[i]) for i in range(wlen) if dec[i] != cand[i]]
            if len(diffs) != 1: continue
            di, new_plain = diffs[0]
            pos  = wstart + di
            canon = int(LINK_MAP[pos])
            if canon in CRIB_CANON_SET:
                continue  # v4: never overwrite locked LP word positions
            new_kv = (int(CIPHER[pos]) - new_plain) % M
            if SING_A0[canon] >= 0 and new_kv != SING_A0[canon] and new_kv != SING_A1[canon]:
                continue
            key[canon] = new_kv
            for src_s, dst_s, ln in TTP_CONSTRAINTS:
                for k_i in range(ln):
                    if LINK_MAP[src_s + k_i] == canon:
                        key[dst_s + k_i] = new_kv
                    if src_s + k_i == canon:
                        key[dst_s + k_i] = new_kv
            fixes += 1; break
    return key, fixes

WORD_REFINE_INTERVAL = 5

# --- Main loop ----------------------------------------------------------------
print(f'\n=== GPU {GPU_ID} hillclimber v3 starting (N_CHAINS={N_CHAINS}) ===', flush=True)
print(f'Output: {OUTFILE}', flush=True)
print(f'Scoring: quadgrams + word-slot LP (WORD_WEIGHT={WORD_WEIGHT})', flush=True)

T_START = 5.0 if warmstart_score else 8.0
T_END   = 0.00005
T_DECAY = 0.9999993

# Resume at exact temperature from last checkpoint (if available and < T_START)
_resume_temp = warmstart_temp if 'warmstart_temp' in dir() else 0
if 0 < _resume_temp < T_START:
    temperature = _resume_temp
    print(f'  Resuming at T={temperature:.6f} (from checkpoint)', flush=True)
else:
    temperature = T_START

_init_best_idx   = int(cp_scores.argmax())
_init_best_score = float(cp_scores[_init_best_idx])
if warmstart_score and warmstart_score > _init_best_score:
    global_best_score = warmstart_score
    global_best_key   = ck_key.copy()
    print(f'  Preserving warmstart key score={warmstart_score:.1f} > init {_init_best_score:.1f}', flush=True)
else:
    global_best_score = _init_best_score
    global_best_key   = cp_keys[_init_best_idx].get()

stagnation_window     = 25
stagnation_counter    = 0
last_improvement_score = global_best_score
WARM_RESTART_TEMP     = 5.0
exploration_lockout   = 0

blk = 256
grd = (N_CHAINS + blk - 1) // blk

with open(OUTFILE, 'w', encoding='utf-8') as fout:
    fout.write(f'GPU {GPU_ID} Hillclimber v3 -- Start {time.strftime("%H:%M:%S")}\n')
    fout.write(f'N_CHAINS={N_CHAINS}, T_START={T_START}, WORD_WEIGHT={WORD_WEIGHT}\n')
    fout.write('='*60 + '\n')

step       = 0
t_last     = time.time()
seed_state = (GPU_ID * 0xDEADBEEF + 3) & 0xFFFFFFFFFFFFFFFF
SEED_MUL   = 6364136223846793005
SEED_ADD   = 1442695040888963407
MASK64     = 0xFFFFFFFFFFFFFFFF

while True:
    step += 1

    seed_state = (seed_state * SEED_MUL + SEED_ADD) & MASK64
    STEP_KERNEL((grd,), (blk,),
        (cp_cipher, cp_keys.ravel(), cp_scores, cp_qgram,
         cp_indep, cp_sing_a0, cp_sing_a1,
         cp_ws_s_arr, cp_ws_l_arr,
         cp_lp_wf, cp_lp_ls, cp_lp_lc,
         cp.float32(WORD_WEIGHT), cp.int32(MAX_LP_LEN),
         cp.int32(N_CIPHER), cp.int32(N_CHAINS), cp.int32(N_INDEPENDENT),
         cp.float32(temperature), cp.uint64(int(seed_state))))

    temperature = max(T_END, temperature * T_DECAY)

    if step % SAVE_EVERY != 0:
        continue

    # -- Save block --------------------------------------------------------
    cp.cuda.Stream.null.synchronize()

    cur_best_idx   = int(cp_scores.argmax())
    cur_best_score = float(cp_scores[cur_best_idx])
    if cur_best_score > global_best_score:
        global_best_score = cur_best_score
        global_best_key   = cp_keys[cur_best_idx].get()

    elapsed = time.time() - t_last; rate = SAVE_EVERY / elapsed; t_last = time.time()

    ws = word_score(global_best_key)
    sing_hits = sum(
        1 for sp, sc in zip(SING_POS, SING_CIP)
        if (sc - int(global_best_key[sp])) % M in (10, 24)
    )

    # Decode first 30 words for preview
    plain_preview = []
    for wi, (wstart, wlen) in enumerate(WORD_SLOTS[:30]):
        if wstart + wlen > N_CIPHER: break
        plain_preview.append(''.join(
            IDX_TO[(int(CIPHER[wstart+i]) - int(global_best_key[wstart+i])) % M]
            for i in range(wlen)))
    preview = ' '.join(plain_preview)

    # Per-page IoC (sample 5 pages)
    ioc_strs = []
    for pg_check in [21, 25, 31, 40, 50]:
        if pg_check in page_offsets:
            ps = page_offsets[pg_check]
            pl = sum(len(r) for r, _ in [load_page(pg_check)])
            if pl > 20:
                dec = [(int(CIPHER[ps+j]) - int(global_best_key[ps+j])) % M for j in range(pl)]
                freq = Counter(dec)
                ioc_val = sum(f*(f-1) for f in freq.values()) / max(1, pl*(pl-1)) * M
                ioc_strs.append(f'P{pg_check}={ioc_val:.2f}')

    ioc_info = ' | '.join(ioc_strs) if ioc_strs else 'N/A'
    msg = (f'Step {step:,} | Score={global_best_score:.1f} | WordScore={ws} | '
           f'Singletons={sing_hits}/{N_SING} | '
           f'Temp={temperature:.6f} | Rate={rate:.0f}steps/s\n'
           f'  IoC: {ioc_info}\n'
           f'  Preview: {preview}\n')
    print(msg, end='', flush=True)

    # -- Stagnation detection ----------------------------------------------
    if global_best_score > last_improvement_score + 50:
        last_improvement_score = global_best_score
        stagnation_counter = 0
    else:
        stagnation_counter += 1

    if stagnation_counter >= stagnation_window and temperature < WARM_RESTART_TEMP:
        temperature = WARM_RESTART_TEMP
        stagnation_counter = 0
        keys_np = cp_keys.get(); best_np = global_best_key.copy(); n = N_CHAINS
        # Vectorized scatter. Top 15%: small perturbation (50-300 pos).
        fine_idx = rng.choice(n, size=n * 15 // 100, replace=False)
        fine_sizes = rng.integers(50, 300, size=len(fine_idx))
        for ci, n_p in zip(fine_idx, fine_sizes):
            pp = rng.choice(INDEPENDENT_POS, size=int(n_p), replace=False)
            keys_np[ci] = best_np.copy()
            keys_np[ci, pp] = rng.integers(0, M, size=int(n_p))
        # Bottom 50%: fully random keys (not loop-of-choice -- much faster).
        keys_np[n // 2:] = rng.integers(0, M, size=(n - n // 2, N_CIPHER), dtype=np.int32)
        enforce_singletons(keys_np)
        enforce_ttp(keys_np)
        enforce_cribs(keys_np)  # v4: always restore confirmed LP word positions
        # In-place GPU update -- avoids double VRAM allocation (old+new 3.81 GB each)
        cp_keys.set(keys_np.astype(np.int32))
        enforce_cribs(keys_np)  # v4: always restore confirmed LP word positions
        compute_all_scores()
        stagnation_counter  = -100
        exploration_lockout = 100
        print(f'  [nuclear-restart] T->{WARM_RESTART_TEMP}, chains scattered.', flush=True)

    # -- Save checkpoint ---------------------------------------------------
    ck_data = {
        'step':        step,
        'mode':        'sub',
        'score':       global_best_score,
        'wordscore':   ws,
        'singletons':  sing_hits,
        'temperature': temperature,
        'key':         list(map(int, global_best_key)),
    }
    Path(CHECKPOINT).write_text(json.dumps(ck_data))

    with open(OUTFILE, 'a', encoding='utf-8') as fout:
        fout.write(msg)

    # -- Chain restart: every 10 saves, revive worst 10% from best --------
    save_block = step // SAVE_EVERY
    if exploration_lockout > 0:
        exploration_lockout -= 1
    elif save_block % 25 == 0:
        # Revive worst 5% of chains from best -- SCORE_KERNEL is expensive at
        # N_CHAINS=131072 so we reduce call frequency (every 25 saves=250K steps).
        # Fewer chains revived per restart (5% vs 10%) keeps the restart fast.
        scores_np = cp_scores.get()
        n_revive  = N_CHAINS // 20   # 5%
        worst_idx = np.argsort(scores_np)[:n_revive]
        best_np   = cp_keys[int(np.argmax(scores_np))].get()
        keys_np   = cp_keys.get()
        for wi in worst_idx:
            n_p = rng.integers(200, 1500)
            pp  = rng.choice(INDEPENDENT_POS, size=n_p, replace=False)
            pv  = rng.integers(0, M, size=n_p)
            keys_np[wi] = best_np.copy()
            keys_np[wi, pp] = pv
        enforce_singletons(keys_np)
        enforce_ttp(keys_np)
        enforce_cribs(keys_np)  # v4: restore confirmed LP word positions
        cp_keys.set(keys_np.astype(np.int32))  # in-place, avoids double VRAM
        compute_all_scores()
        print(f'  [restart] Revived {n_revive} chains.', flush=True)

    # -- Word-level refinement ---------------------------------------------
    if save_block % WORD_REFINE_INTERVAL == 0 and save_block > 0:
        refined_key, n_fixes = word_refine_pass(global_best_key)
        if n_fixes > 0:
            keys_np = cp_keys.get()
            n_seeded = min(N_CHAINS // 50, 2624)  # 2% of chains, bounded for speed
            for si in range(n_seeded):
                ci = rng.integers(0, N_CHAINS)
                n_p = rng.integers(10, 50)
                pp = rng.choice(INDEPENDENT_POS, size=n_p, replace=False)
                pv = rng.integers(0, M, size=n_p)
                keys_np[ci] = refined_key.copy()
                keys_np[ci, pp] = pv
            enforce_singletons(keys_np)
            enforce_ttp(keys_np)
            enforce_cribs(keys_np)  # v4: restore locked LP positions after word-refine seeding
            cp_keys.set(keys_np.astype(np.int32))  # in-place, avoids double VRAM
            compute_all_scores()
            new_best_idx = int(cp_scores.argmax())
            new_best_sc  = float(cp_scores[new_best_idx])
            if new_best_sc > global_best_score:
                global_best_score = new_best_sc
                global_best_key   = cp_keys[new_best_idx].get()
            print(f'  [word-refine] {n_fixes} Hamming-1 fixes. Best={global_best_score:.1f}', flush=True)
