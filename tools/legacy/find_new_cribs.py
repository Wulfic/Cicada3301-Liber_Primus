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
for pg in range(21, 55):
    p = Path(f'pages/page_{pg:02d}/runes.txt')
    if p.exists():
        for ch in p.read_text(encoding='utf-8'):
            if ch in RUNE_TO_IDX:
                cipher.append(RUNE_TO_IDX[ch])

N = len(cipher)
print(f'Cipher length: {N}')

PHRASES = [
    'THE PRIMES ARE SACRED',
    'ALL THINGS SHOULD BE ENCRYPTED',
    'FOLLOWYOURTRUTH',
    'IMPOSE NOTHING ON OTHERS',
    'AMASS GREAT WEALTH',
    'NEVER BECOME ATTACHED',
    'DESTROYALLTHATYOUOWN',
    'DISCOVER TRUTH INSIDE YOURSELF',
    'SEEKTRUTH WITHIN',
    'WELCOMEPILGRIM',
    'AN INSTRUCTION',
    'CONSUMPTION PRESERVATION ADHERENCE',
    'THREE BEHAVIORS WHICH CAUSE LOSS',
    'CIRCUMFERENCE',
    'WELCOME PILGRIM TO THE SACRED TEXT',
    'PROGRAM YOUR MIND PROGRAM REALITY',
    'AN END EVERY END IS A BEGINNING',
]

# Already known crib starts: don't flag these
KNOWN_POSITIONS = set()
for phrase2, start in [
    ('CONSUMPTION', 31), ('KNOWTHIS', 476), ('PROGRAM', 599),
    ('DIUINITY', 1356), ('PRESERUATION', 2093), ('SOMEWISDOM', 4131),
    ('THELOSSOFDIUINITY', 4325), ('ADHERENCE', 8532)
]:
    for i in range(len(encode(phrase2))):
        KNOWN_POSITIONS.add(start + i)

print()
print('Searching for high-confidence phrases (>=80% match):')
print('=' * 70)

results = []
for phrase in PHRASES:
    enc = encode(phrase)
    L = len(enc)
    if L < 4:
        continue
    # Find top 3 positions
    hits = []
    for start in range(N - L + 1):
        # Skip positions already known
        if any((start + j) in KNOWN_POSITIONS for j in range(L)):
            continue
        m = sum(1 for j in range(L) if (cipher[start+j] - KEY[start+j]) % 29 == enc[j])
        if m * 100 // L >= 80:
            hits.append((m, start))
    hits.sort(reverse=True)
    for m, start in hits[:3]:
        pct = 100 * m // L
        decoded = ''.join(IDX_TO[(cipher[start+j] - KEY[start+j]) % 29] for j in range(L))
        results.append((pct, m, L, start, phrase, decoded))

results.sort(reverse=True)
for pct, m, L, start, phrase, decoded in results:
    print(f'  {pct:3d}% ({m:2d}/{L:2d}) pos={start:5d} | {phrase}')
    print(f'         decoded: {decoded}')
    print()
