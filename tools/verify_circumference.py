import json
from pathlib import Path

RUNE_TO_IDX = {chr(k): v for k, v in [
    (0x16A0,0),(0x16A2,1),(0x16A6,2),(0x16A9,3),(0x16B1,4),(0x16B3,5),
    (0x16B7,6),(0x16B9,7),(0x16BB,8),(0x16BE,9),(0x16C1,10),(0x16C4,11),
    (0x16C7,12),(0x16C8,13),(0x16C9,14),(0x16CB,15),(0x16CF,16),(0x16D2,17),
    (0x16D6,18),(0x16D7,19),(0x16DA,20),(0x16DD,21),(0x16DF,22),(0x16DE,23),
    (0x16AA,24),(0x16AB,25),(0x16A3,26),(0x16E1,27),(0x16E0,28)
]}
IDX_TO = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA']
LP_MAP = {'F':0,'U':1,'TH':2,'O':3,'R':4,'C':5,'G':6,'W':7,'H':8,'N':9,'I':10,'J':11,
          'EO':12,'P':13,'X':14,'S':15,'T':16,'B':17,'E':18,'M':19,'L':20,'NG':21,
          'OE':22,'D':23,'A':24,'AE':25,'Y':26,'IO':27,'EA':28,'V':1,'Q':5,'K':5,'Z':14}

def encode(phrase):
    runes = []; i = 0; w = phrase.upper().replace(' ', '')
    while i < len(w):
        if i+1 < len(w) and w[i:i+2] in LP_MAP:
            runes.append(LP_MAP[w[i:i+2]]); i += 2
        elif w[i] in LP_MAP:
            runes.append(LP_MAP[w[i]]); i += 1
        else:
            i += 1
    return runes

ck = json.loads(Path('data/gpu_hill_checkpoint_gpu1.json').read_text())
KEY = ck['key']
cipher = []
page_offsets = {}; cum = 0
for pg in range(21, 55):
    p = Path(f'pages/page_{pg:02d}/runes.txt')
    if p.exists():
        page_offsets[pg] = cum
        for ch in p.read_text(encoding='utf-8'):
            if ch in RUNE_TO_IDX: cipher.append(RUNE_TO_IDX[ch])
        cum = len(cipher)

# Check CIRCUMFERENCE at pos 3080 word boundaries
phrase = 'CIRCUMFERENCE'
enc = encode(phrase)
print(f'CIRCUMFERENCE encoded: {enc} ({len(enc)} runes)')
print()

for crib_pos in [3080, 9806]:
    decoded = [IDX_TO[(cipher[crib_pos+j] - KEY[crib_pos+j]) % 29] for j in range(len(enc))]
    matches = sum(IDX_TO[e] == d for e, d in zip(enc, decoded))
    page_num = max(pg for pg, off in page_offsets.items() if off <= crib_pos)
    pg_start = page_offsets[page_num]
    pos_in_page = crib_pos - pg_start
    print(f'pos={crib_pos} (P{page_num}+{pos_in_page}): {matches}/{len(enc)} matches')
    print(f'  decoded: {"".join(decoded)}')
    print(f'  expected: {phrase}')
    for j, (e, d) in enumerate(zip(enc, decoded)):
        if IDX_TO[e] != d:
            print(f'  mismatch at pos {crib_pos+j}: expected {IDX_TO[e]} got {d} (off by {(LP_MAP[IDX_TO[e]] - LP_MAP.get(d, -1)) % 29})')
    print()

# Check the LINK_MAP to confirm they are TTP-linked
import numpy as np
TTP_CONSTRAINTS = [
    (3001, 9727, 1312),
    (6298, 12311, 1468),
    (   0,  5803,  404),
    (2736,  8643,  265),
    ( 737,  8100,  172),
    ( 910,  8273,   97),
]
LINK_MAP = np.arange(len(cipher), dtype=np.int32)
for src_s, dst_s, ln in TTP_CONSTRAINTS:
    for i in range(ln):
        LINK_MAP[dst_s + i] = LINK_MAP[src_s + i]

print(f'LINK_MAP[3080] = {LINK_MAP[3080]} (canonical for 3080)')
print(f'LINK_MAP[9806] = {LINK_MAP[9806]} (canonical for 9806)')
print(f'TTP-linked? {LINK_MAP[3080] == LINK_MAP[9806] and LINK_MAP[3080] == 3080}')
print()

# Show word boundaries around pos 3080 in P27
p27_start = page_offsets[27]
p = Path('pages/page_27/runes.txt')
txt = p.read_text(encoding='utf-8')
curr = []; pos = p27_start; words = []
for ch in txt:
    if ch in RUNE_TO_IDX: curr.append(RUNE_TO_IDX[ch]); pos += 1
    elif ch in '-. /\n\r\t' and curr: words.append((pos - len(curr), len(curr))); curr = []
if curr: words.append((pos - len(curr), len(curr)))

print(f'P27 word boundaries near pos 3080 (P27 starts at {p27_start}):')
for ws, wl in words:
    if 3070 <= ws <= 3100:
        decoded_w = [IDX_TO[(cipher[ws+j] - KEY[ws+j]) % 29] for j in range(wl)]
        is_match = (ws == 3080) and wl == len(enc)
        print(f'  pos={ws:5d} len={wl:2d} {"<-- CHECK" if is_match else "       "} | {"".join(decoded_w)}')
