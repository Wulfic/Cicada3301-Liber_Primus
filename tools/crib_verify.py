"""
Crib Verification Tool
======================
Tests candidate LP phrases against the current checkpoint key.
For each candidate: computes match rate, checks TTP twin, and reports
whether the phrase should be added to FORCED_CRIBS.

Usage: python crib_verify.py [checkpoint_file]
"""

import sys, os, json
import numpy as np
from pathlib import Path

CHECKPOINT = sys.argv[1] if len(sys.argv) > 1 else 'data/gpu_hill_checkpoint_gpu1.json'
M = 29

# ─── GP alphabet (identical to hillclimber) ─────────────────────────────────
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
IDX_TO = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA']

def encode(phrase):
    """Encode phrase string to GP rune list, digraph-aware."""
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

def decode_idx(idx):
    return IDX_TO[idx] if 0 <= idx < M else '?'

def decode_seq(seq):
    return ''.join(decode_idx(v) for v in seq)

# ─── Load cipher ─────────────────────────────────────────────────────────────
print('Loading cipher...', flush=True)
cipher_list = []
page_offsets = {}
cum = 0
for pg in range(21, 55):
    path = Path(f'pages/page_{pg:02d}/runes.txt')
    if not path.exists():
        continue
    text = path.read_text(encoding='utf-8')
    runes = [RUNE_TO_IDX[c] for c in text if c in RUNE_TO_IDX]
    page_offsets[pg] = cum
    cum += len(runes)
    cipher_list.extend(runes)

CIPHER = np.array(cipher_list, dtype=np.int32)
N = len(CIPHER)
print(f'  Cipher: {N} runes across pages 21-54', flush=True)

# Reverse lookup: position → page
pos_to_page = {}
for pg, off in page_offsets.items():
    nxt = next((page_offsets[p] for p in sorted(page_offsets) if p > pg), N)
    for i in range(off, nxt):
        pos_to_page[i] = pg

# ─── TTP link map ─────────────────────────────────────────────────────────────
TTP_CONSTRAINTS = [
    (3001,  9727, 1312),
    (6298, 12311, 1468),
    (   0,  5803,  404),
    (2736,  8643,  265),
    ( 737,  8100,  172),
    ( 910,  8273,   97),
]

LINK_MAP = np.arange(N, dtype=np.int32)
for src_s, dst_s, ln in TTP_CONSTRAINTS:
    for i in range(ln):
        LINK_MAP[dst_s + i] = LINK_MAP[src_s + i]

def get_ttp_twin(pos):
    """Return (twin_pos, twin_src) for a position, or None."""
    for src_s, dst_s, ln in TTP_CONSTRAINTS:
        if src_s <= pos < src_s + ln:
            return dst_s + (pos - src_s), 'src→dst'
        if dst_s <= pos < dst_s + ln:
            return src_s + (pos - dst_s), 'dst→src'
    return None, None

# ─── Load checkpoint ─────────────────────────────────────────────────────────
print(f'Loading checkpoint: {CHECKPOINT}', flush=True)
ck = json.load(open(CHECKPOINT))
KEY_CANON = np.array(ck['key'], dtype=np.int32)
KEY = KEY_CANON[LINK_MAP]  # full key via TTP expansion
MODE = ck.get('mode', 'sub')
print(f'  Mode: {MODE} | Step: {ck["step"]:,} | Score: {ck["score"]:,.0f}', flush=True)

# Decode
if MODE == 'sub':
    PLAIN = (CIPHER - KEY) % M
elif MODE == 'add':
    PLAIN = (KEY - CIPHER) % M
else:
    PLAIN = (KEY - CIPHER) % M  # beaufort: plain = key - cipher

# ─── Candidate phrases ───────────────────────────────────────────────────────
# Format: (phrase, start_pos, notes)
CANDIDATES = [
    # Already confirmed cribs — re-verify to show current match quality
    ('CONSUMPTION',         31,    'P21 confirmed'),
    ('KNOWTHIS',           476,    'P23 confirmed'),
    ('PROGRAM',            599,    'P23 confirmed'),
    ('DIUINITY',          1356,    'P25 confirmed'),
    ('PRESERUATION',      2093,    'P25 confirmed'),
    ('SOMEWISDOM',        4131,    'P31 confirmed'),
    ('THELOSSOFDIUINITY', 4325,    'P32 confirmed'),
    ('CIRCUMFERENCE',     3080,    'P27 confirmed'),
    ('ADHERENCE',         8532,    'P40 confirmed'),

    # High-priority candidates from decode output
    ('FOLLOWYOURTRUTH',   2311,    'P25 10/14 in 1.77M ck'),
    ('PROGRAMYOURMIND',   5280,    'P32 11/15 in 1.77M ck'),

    # LP phrase extensions around confirmed cribs
    ('LOSSOF',              25,    'P21 before CONSUMPTION?'),
    ('THELOSSOF',           22,    'P21 before CONSUMPTION?'),
    ('THELOSSOFCONSUMPTION', 22,   'P21 extended?'),
    ('PRIMALITY',         3093,    'P27 after CIRCUMFERENCE'),
    ('PRIMAL',            3093,    'P27 after CIRCUMFERENCE'),
    ('THECIRCUMFERENCE',  3074,    'P27 before CIRCUMFERENCE'),

    # Phrases visible in extraction output
    ('THREEBEHAVIORS',    5103,    'P32 visible in extraction?'),
    ('PRACTICESSOME',     3110,    'P27 after CIRCUMFERENCE+PRIMAL?'),
    ('WITHIN',            3134,    'P27'),
    ('DECEPTION',         3191,    'P27'),
    
    # P32 after THELOSSOFDIUINITY
    ('THEPRIMES',         4353,    'P32 after THELOSSOFDIUINITY'),
    ('SACRED',            4353,    'P32 after THELOSSOFDIUINITY'),
    
    # Adjacent to SOMEWISDOM at 4131
    ('SOMEWISDOMTHE',     4131,    'P31 SOMEWISDOM+THE'),
    ('WISDOMTHAT',        4141,    'P31 after SOMEWISDOM'),

    # P25 around PRESERUATION at 2093
    ('PRESERUATIONOF',    2093,    'P25 PRESERUATION+OF'),
    ('THEPRESERUATION',   2087,    'P25 before PRESERUATION'),

    # TTP regions — P37-P50 (TTP-2: 6298→12311, 1468 runes)
    ('PRIMESARE',         6350,    'P37 in TTP-2 src region'),
    ('SACRED',            6350,    'P37 in TTP-2'),
    ('PRESERUATION',      6350,    'P37 in TTP-2'),

    # P21 TTP twin region in P32 (TTP-3: 0→5803, 404 runes)
    # CONSUMPTION twin at pos 5834, KNOWTHIS twin at 5803+476=6279(out of range)
    ('CONSUMPTION',       5834,    'P32 TTP twin of P21 CONSUMPTION'),
    ('LOSSOF',            5828,    'P32 TTP twin of P21 LOSSOF?'),

    # P24/P40 TTP (737→8100, 172) and (910→8273, 97)
    ('PRIMES',             737,    'P24 TTP-5 src'),
    ('SACRED',             737,    'P24 TTP-5 src'),
]

# ─── Verify function ─────────────────────────────────────────────────────────
def verify_crib(phrase, pos, notes=''):
    enc = encode(phrase)
    n = len(enc)
    if pos < 0 or pos + n > N:
        return

    # Match against decoded text
    matches = sum(1 for i, v in enumerate(enc) if PLAIN[pos + i] == v)
    match_pct = 100 * matches / n

    # TTP twin check
    twin_pos, twin_dir = get_ttp_twin(pos)
    twin_str = ''
    if twin_pos is not None and twin_pos + n <= N:
        t_matches = sum(1 for i, v in enumerate(enc) if PLAIN[twin_pos + i] == v)
        twin_str = f' | TTP twin @{twin_pos}(P{pos_to_page.get(twin_pos,"?")}): {t_matches}/{n}'

    # What the key implies at this position
    implied_key = [(CIPHER[pos + i] - enc[i]) % M for i in range(n)]
    actual_key  = [int(KEY[pos + i]) for i in range(n)]
    key_agree   = sum(1 for a, b in zip(implied_key, actual_key) if a == b)

    # Decode surrounding context
    ctx_start = max(0, pos - 10)
    ctx_end   = min(N, pos + n + 10)
    ctx_plain = PLAIN[ctx_start:ctx_end]
    ctx_str   = decode_seq(ctx_plain)
    ctx_highlighted = ctx_str[:pos - ctx_start] + '[' + ctx_str[pos - ctx_start:pos - ctx_start + n] + ']' + ctx_str[pos - ctx_start + n:]

    pg = pos_to_page.get(pos, '?')
    star = '***' if matches == n else ('**' if match_pct >= 80 else ('*' if match_pct >= 60 else ''))
    print(f"  {star:3s} {phrase:<25s} @{pos:5d}(P{pg}): {matches:2d}/{n} ({match_pct:5.1f}%)  keyAgree={key_agree}/{n}{twin_str}")
    print(f"       ctx: ...{ctx_highlighted}...")
    if matches == n:
        print(f"       implied_key: {implied_key}")
    print()

# ─── Run verifications ───────────────────────────────────────────────────────
print('\n' + '='*80)
print('CRIB VERIFICATION RESULTS')
print('='*80)
print(f'Checkpoint: mode={MODE}, step={ck["step"]:,}, score={ck["score"]:,.0f}')
print()

print('--- CONFIRMED CRIBS (sanity check) ---')
for phrase, pos, notes in CANDIDATES[:9]:
    verify_crib(phrase, pos, notes)

print('--- NEW CANDIDATES ---')
for phrase, pos, notes in CANDIDATES[9:]:
    verify_crib(phrase, pos, notes)

# ─── Sliding window search for best position of high-value phrases ────────────
print('='*80)
print('SLIDING WINDOW SEARCH (best position for each phrase, ±50 around hint)')
print('='*80)

SLIDING_CANDIDATES = [
    ('FOLLOWYOURTRUTH',    2311, 50),
    ('PROGRAMYOURMIND',    5280, 50),
    ('PRIMALITY',          3093, 20),
    ('PRIMAL',             3093, 20),
    ('THECIRCUMFERENCE',   3074, 20),
    ('LOSSOFCONSUMPTION',    22, 20),
    ('THREEBEHAVIORS',     5100, 100),
    ('PRACTICESTHEPRIMES', 3110, 100),
    ('FOLLOWYOURTRUTHAND', 2311, 50),
    ('PROGRAMYOURSELF',    5280, 50),
]

for phrase, hint_pos, window in SLIDING_CANDIDATES:
    enc = encode(phrase)
    n = len(enc)
    best_pos = hint_pos
    best_m = -1
    for p in range(max(0, hint_pos - window), min(N - n, hint_pos + window + 1)):
        m = sum(1 for i, v in enumerate(enc) if PLAIN[p + i] == v)
        if m > best_m:
            best_m = m; best_pos = p
    match_pct = 100 * best_m / n
    ctx_start = max(0, best_pos - 8)
    ctx_end   = min(N, best_pos + n + 8)
    ctx = decode_seq(PLAIN[ctx_start:ctx_end])
    mark = ctx[:best_pos-ctx_start] + '[' + ctx[best_pos-ctx_start:best_pos-ctx_start+n] + ']' + ctx[best_pos-ctx_start+n:]
    pg = pos_to_page.get(best_pos, '?')
    print(f"  {phrase:<25s} best@{best_pos}(P{pg}): {best_m}/{n} ({match_pct:.0f}%)  ...{mark}...")

print()
print('Done.')
