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
    runes = []
    i = 0
    w = phrase.upper().replace(' ', '')
    while i < len(w):
        if i+2 < len(w) and w[i:i+3] in LP_MAP:
            runes.append(LP_MAP[w[i:i+3]]); i += 3
        elif i+1 < len(w) and w[i:i+2] in LP_MAP:
            runes.append(LP_MAP[w[i:i+2]]); i += 2
        elif w[i] in LP_MAP:
            runes.append(LP_MAP[w[i]]); i += 1
        else:
            i += 1
    return runes

ck = json.loads(Path('data/gpu_hill_checkpoint_gpu1.json').read_text())
KEY = ck['key']

cipher = []
page_offsets = {}
cum = 0
for pg in range(21, 55):
    p = Path(f'pages/page_{pg:02d}/runes.txt')
    if p.exists():
        page_offsets[pg] = cum
        for ch in p.read_text(encoding='utf-8'):
            if ch in RUNE_TO_IDX:
                cipher.append(RUNE_TO_IDX[ch])
        cum = len(cipher)

anchors = json.loads(Path('data/key_anchors.json').read_text())['anchors']
print('Existing anchors near 4310-4345:')
for k in sorted(int(x) for x in anchors if 4310 <= int(x) <= 4345):
    kv = anchors[str(k)]
    dc = (cipher[k] - KEY[k]) % 29
    print(f'  pos {k}: anchor={IDX_TO[kv]:4s} | checkpoint_decode={IDX_TO[dc]:4s}')
print()

# Test ELOSSOFDIUINITY at 4314
phrase = 'ELOSSOFDIUINITY'
enc = encode(phrase)
print(f'encode({phrase}) = {enc} ({len(enc)} runes)')
pos = 4314
decoded = [IDX_TO[(cipher[pos+j] - KEY[pos+j]) % 29] for j in range(len(enc))]
matches = sum(IDX_TO[e] == d for e, d in zip(enc, decoded))
print(f'  @{pos}: {matches}/{len(enc)} matches | got: {"".join(decoded)}')
for j, (e, d) in enumerate(zip(enc, decoded)):
    if IDX_TO[e] != d:
        print(f'    mismatch pos {pos+j}: expected {IDX_TO[e]}, got {d}')
print()

# Show word boundaries in P32 near positions 4313–4345
print('P32 word boundaries near positions 4313-4345:')
p = Path('pages/page_32/runes.txt')
txt = p.read_text(encoding='utf-8')
p32_start = page_offsets[32]
print(f'  P32 starts at global pos {p32_start}')
curr = []
pos2 = p32_start
words = []
for ch in txt:
    if ch in RUNE_TO_IDX:
        curr.append(RUNE_TO_IDX[ch])
        pos2 += 1
    elif ch in '-. /\n\r\t' and curr:
        words.append((pos2 - len(curr), len(curr)))
        curr = []
if curr:
    words.append((pos2 - len(curr), len(curr)))

for ws, wl in words:
    if 4310 <= ws <= 4360:
        decoded_w = [IDX_TO[(cipher[ws+j] - KEY[ws+j]) % 29] for j in range(wl)]
        print(f'  pos={ws:5d} len={wl:2d} | {"".join(decoded_w)}')

# Test whole-phrase "THELOSSOFDIUINITY" aligned to word starts
print()
print('Testing THELOSSOFDIUINITY at all word-start positions in P32 (first 50 words):')
enc_full = encode('THELOSSOFDIUINITY')
print(f'  encode("THELOSSOFDIUINITY") = {len(enc_full)} runes')
for ws, wl in words[:50]:
    if wl == len(enc_full):
        decoded_w = [IDX_TO[(cipher[ws+j] - KEY[ws+j]) % 29] for j in range(wl)]
        m = sum(IDX_TO[e] == d for e, d in zip(enc_full, decoded_w))
        if m >= 12:
            print(f'  pos={ws} len={wl}: {m}/{len(enc_full)} matches | {"".join(decoded_w)}')
