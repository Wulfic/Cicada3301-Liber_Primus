"""
validate_crib_candidates.py — Cross-check a crib candidate against the
current hillclimber checkpoint key.

Usage:
  python Tools/validate_crib_candidates.py

For each candidate phrase+position, prints:
  - What the hillclimber currently decodes at that position
  - Whether it matches the candidate phrase
  - Hamming distance (how far off)
  - Whether the phrase's implied key values agree with current key at those positions
"""

import json, sys, os, re
from pathlib import Path
import numpy as np

# ── GP alphabet (same as gpu_hillclimber.py) ─────────────────────────────────
M = 29
IDX_TO = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA']
RUNE_TO_IDX = {chr(k): v for k, v in [
    (0x16A0,0),(0x16A2,1),(0x16A6,2),(0x16A9,3),(0x16B1,4),(0x16B3,5),
    (0x16B7,6),(0x16B9,7),(0x16BB,8),(0x16BE,9),(0x16C1,10),(0x16C4,11),
    (0x16C7,12),(0x16C8,13),(0x16C9,14),(0x16CB,15),(0x16CF,16),(0x16D2,17),
    (0x16D6,18),(0x16D7,19),(0x16DA,20),(0x16DD,21),(0x16DF,22),(0x16DE,23),
    (0x16AA,24),(0x16AB,25),(0x16A3,26),(0x16E1,27),(0x16E0,28)]}

# Letter → GP index (used for encoding candidate phrases)
LETTER_TO_GP = {
    'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
    'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
    'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':14,
    'TH':2,'OE':22,'AE':25,'NG':21,'EO':12,'IO':27,'EA':28
}

def encode_phrase(text):
    """Encode ASCII text to GP indices."""
    text = text.upper()
    enc = []
    i = 0
    while i < len(text):
        # Try digraphs first
        digraph = text[i:i+2]
        if digraph in LETTER_TO_GP:
            enc.append(LETTER_TO_GP[digraph])
            i += 2
        elif text[i] in LETTER_TO_GP:
            enc.append(LETTER_TO_GP[text[i]])
            i += 1
        else:
            i += 1  # skip unknown
    return enc

def gp_to_text(indices):
    return ''.join(IDX_TO[i] if 0 <= i < len(IDX_TO) else '?' for i in indices)

# ── Load cipher using same logic as gpu_hillclimber.py ────────────────────────
def load_page(pg):
    path = Path(f'pages/page_{pg:02d}/runes.txt')
    if not path.exists():
        return [], []
    text = path.read_text(encoding='utf-8')
    runes = []; words = []; curr = []
    for ch in text:
        if ch in RUNE_TO_IDX:
            runes.append(RUNE_TO_IDX[ch])
            curr.append(RUNE_TO_IDX[ch])
        elif ch in '-. \n\r\t\u2022/' and curr:
            words.append(tuple(curr))
            curr = []
    if curr:
        words.append(tuple(curr))
    return runes, words

print('Loading cipher stream...')
cipher_list = []
words_all = []
page_offsets = {}
cum = 0
for pg in range(21, 55):
    runes, words = load_page(pg)
    if runes:
        page_offsets[pg] = cum
        cum += len(runes)
        cipher_list.extend(runes)
        words_all.extend(words)

CIPHER = np.array(cipher_list, dtype=np.int32)
N = len(CIPHER)
print(f'  Cipher: {N} runes, {len(page_offsets)} pages loaded')
print(f'  Pages: {sorted(page_offsets.keys())}')

# ── Build TTP link map ─────────────────────────────────────────────────────────
TTP_PAIRS = [
    (0, 1312, 6727, 1312),
    (1312, 1423, 8139, 1423),
    (2735, 265, 6727, 265),
    (3001, 178, 9727, 178),
    (3179, 237, 9905, 237),
    (3417, 301, 10143, 301),
]
LINK_MAP = np.arange(N, dtype=np.int32)
for a_start, a_len, b_start, b_len in TTP_PAIRS:
    span = min(a_len, b_len, max(0, N - a_start), max(0, N - b_start))
    for k in range(span):
        pa, pb = a_start + k, b_start + k
        if pa < N and pb < N:
            canon = min(pa, pb)
            LINK_MAP[pa] = canon
            LINK_MAP[pb] = canon

# ── Load hillclimber checkpoint ───────────────────────────────────────────────
print('Loading checkpoint...')
ck = json.load(open('data/gpu_hill_checkpoint_gpu1.json'))
key_arr = np.array(ck['key'], dtype=np.int32)
step = ck['step']
score = ck['score']
print(f'  Step {step}, score {score:.1f}, key length {len(key_arr)}')

if len(key_arr) != N:
    print(f'ERROR: key length mismatch ({len(key_arr)} != {N})')
    sys.exit(1)

def decode_at(start, length):
    end = min(start + length, N)
    return [(int(CIPHER[start+i]) - int(key_arr[start+i])) % M for i in range(end - start)]

# ── Candidate phrases ─────────────────────────────────────────────────────────
# Confirmed cribs at their true global positions
_CONFIRMED_GLOBAL = [
    ('CONSUMPTION',         31),
    ('KNOWTHIS',           476),
    ('PROGRAM',            599),
    ('DIUINITY',          1356),
    ('PRESERUATION',      2093),
    ('CIRCUMFERENCE',     3080),
    ('SOMEWISDOM',        4131),
    ('THELOSSOFDIUINITY', 4325),
    ('ADHERENCE',         8532),
]

def global_to_page(gpos):
    sp = sorted(page_offsets.items())
    for i, (pg, start) in enumerate(sp):
        end = sp[i+1][1] if i+1 < len(sp) else N
        if start <= gpos < end:
            return pg, gpos - start
    return None, gpos

# Convert to page-relative and tag
CANDIDATES = []
for phrase, gpos in _CONFIRMED_GLOBAL:
    pg, offset = global_to_page(gpos)
    if pg:
        CANDIDATES.append((phrase, pg, offset, f'CONFIRMED g={gpos}'))

# Crib drag candidates (page-relative)
for phrase, pg, offset in [
    ('TODESTROYALLTHATYOUOWN', 26, 5),
    ('THINGSARENOTWORTHPRESERVING', 40, 338),
    ('CARNALOBSCURAFORMMOBIUS', 28, 99),
]:
    CANDIDATES.append((phrase, pg, offset, 'lp_crib_drag'))

print('\n=== Crib Candidate Validation ===')
header = f'{"Phrase":<35s}  {"Position":>10s}  {"%Match":>7s}  {"Ham":>4s}  {"Current Decode"}'
print(header)
print('-' * 100)

for phrase_text, pg, pg_offset, tag in CANDIDATES:
    if pg not in page_offsets:
        print(f'  {phrase_text:<35s}  P{pg}+{pg_offset:<5d}  [page not loaded]')
        continue

    start = page_offsets[pg] + pg_offset
    enc = encode_phrase(phrase_text)
    n = len(enc)

    if start + n > N:
        print(f'  {phrase_text:<35s}  P{pg}+{pg_offset:<5d}  [out of range]')
        continue

    # Check TTP consistency of implied key
    implied = {}
    ttp_ok = True
    for i, p in enumerate(enc):
        pos = start + i
        kv = (int(CIPHER[pos]) - p) % M
        canon = int(LINK_MAP[pos])
        if canon in implied:
            if implied[canon] != kv:
                ttp_ok = False
                break
        else:
            implied[canon] = kv

    if not ttp_ok:
        print(f'  {phrase_text:<35s}  P{pg}+{pg_offset:<5d}  [TTP CONFLICT — invalid]')
        continue

    # Compare to hillclimber
    current_decode = decode_at(start, n)
    matches = sum(cd == p for cd, p in zip(current_decode, enc))
    ham = n - matches
    pct = 100 * matches // n
    cur_text = gp_to_text(current_decode)[:35]

    flag = ''
    if ham == 0:
        flag = ' *** EXACT ***'
    elif pct >= 80:
        flag = ' *** STRONG ***'
    elif pct >= 50:
        flag = ' * partial'

    print(f'  {phrase_text:<35s}  P{pg}+{pg_offset:<5d}  {pct:6d}%  {ham:>4d}  {cur_text}  [{tag}]{flag}')

# ── Show hillclimber decode at key pages ──────────────────────────────────────
print('\n=== Hillclimber Decode at Key Positions ===')
for pg, pg_off, label in [
    (21,  0,  'P21 start'),
    (21, 31,  'P21+31 CONSUMPTION'),
    (26,  0,  'P26 start'),
    (26,  5,  'P26+5 candidate'),
    (27,  0,  'P27 start (g=3000)'),
    (28,  0,  'P28 start'),
    (28, 99,  'P28+99 carnal/obscura candidate'),
    (40,  0,  'P40 start'),
    (40,338,  'P40+338 things candidate'),
]:
    if pg not in page_offsets:
        continue
    start = page_offsets[pg] + pg_off
    length = 30
    decoded = decode_at(start, length)
    text = gp_to_text(decoded)
    print(f'  {label}')
    print(f'    Decode: {text}')

print('\nDone.')
