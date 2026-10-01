"""
Extract confirmed cribs from the current GPU hillclimber v3 checkpoint.
Identifies long genuine LP words in the decode and outputs them as 
FORCED_CRIBS for the next hillclimber run.

Only uses LP_CANON words (not polluted LP_VOCAB from ciphered pages).
"""
import json
import sys
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

IDX_TO = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA']
RUNE_TO_IDX = {chr(k): v for k, v in [
    (0x16A0,0),(0x16A2,1),(0x16A6,2),(0x16A9,3),(0x16B1,4),(0x16B3,5),
    (0x16B7,6),(0x16B9,7),(0x16BB,8),(0x16BE,9),(0x16C1,10),(0x16C4,11),
    (0x16C7,12),(0x16C8,13),(0x16C9,14),(0x16CB,15),(0x16CF,16),(0x16D2,17),
    (0x16D6,18),(0x16D7,19),(0x16DA,20),(0x16DD,21),(0x16DF,22),(0x16DE,23),
    (0x16AA,24),(0x16AB,25),(0x16A3,26),(0x16E1,27),(0x16E0,28)]}
M = 29

LETTER_TO_GP = {
    'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
    'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
    'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':14,
    'TH':2,'OE':22,'AE':25,'NG':21,'EO':12,'IO':27,'EA':28
}
def gp_encode(phrase):
    w = phrase.upper().replace(' ', ''); r = []; i = 0
    while i < len(w):
        if i+1 < len(w) and w[i:i+2] in LETTER_TO_GP:
            r.append(LETTER_TO_GP[w[i:i+2]]); i += 2
        elif w[i] in LETTER_TO_GP:
            r.append(LETTER_TO_GP[w[i]]); i += 1
        else: i += 1
    return tuple(r)

# LP_CANON - only definitive LP words
LP_CANON = [
    'CONSUMPTION','PRESERUATION','PRESERVATION','ADHERENCE',
    'SOMEWISDOM','DIUINITY','DIVINITY','CIRCUMFERENCE','CIRCUMFERENCES',
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
    'TOTIENT','PRIME','DIVINE',
    # Additional confirmed from solved pages (U/V variants)
    'HAUE','SEEC','CNOW','CUESTION','DISCOUER','BELIEUE','DIUINE',
    'PRESERUE','DIUINITE','BELEIUE','CONSUMPTION',
    # Short LP words that are unambiguous
    'AN','OF','TO','IS','IT','IN','AS','OR','DO','WE',
    'I','A',  # singletons - handled separately
    # From LP1/LP2 solved content
    'PAIN','STRENGTH','FUNCTION','ATTACHED','BEHAUIORS',
    'INTELLIGENCE','PROGRAM','PATH','ERRORS',
    # From P05/P63 magic square keywords  
    'SHADOWS','AETHEREAL','BUFFERS','CARNAL','ANALOG','MOBIUS',
    'OBSCURA','FORM','VOID','MOURNFUL','CABAL',
    # LP archaic U/V spellings
    'DISCOUER','DISCOUERY','THEMSELUES','OURSELUES',
    'BELEIUE','BELIEUE','UERSE','UERSES',
    'SECUENCES','SECUENCE','CNOWTHIS',
    'CUESTION','CUESTIONS','DIUINITE',
    'OUER','ADUANCE','ADUANCED',
    'GIUE','GIUEN','LIUE','LIUED',
    'MOUE','MOUED','LOUE','LOUED',
    'LEAUE','LEAUES','HAUING',
    'RECEIUE','RECEIUED','PERCEIUE',
    'CONCEIUE','PRESERUE','PRESERUED',
    'OBSERUE','RESERUED','DESERUED',
]

# Build GP-encoded LP canon set
LP_CANON_GP = {}  # plain_str -> gp_tuple
for w in LP_CANON:
    enc = gp_encode(w)
    if enc:
        LP_CANON_GP[w.upper()] = enc
        # Also map the GP-encoded form back 
        dec = ''.join(IDX_TO[v] for v in enc)
        LP_CANON_GP[dec] = enc

# Build LP canon by GP-tuple for quick lookup
LP_BY_TUPLE = {}
for w, enc in LP_CANON_GP.items():
    LP_BY_TUPLE[enc] = w

def load_page(pg):
    path = Path(f'pages/page_{pg:02d}/runes.txt')
    if not path.exists(): return None, None
    text = path.read_text(encoding='utf-8')
    runes = []; words = []; curr = []
    for ch in text:
        if ch in RUNE_TO_IDX:
            runes.append(RUNE_TO_IDX[ch]); curr.append(RUNE_TO_IDX[ch])
        elif ch in '-. \n\r\t\u2022/' and curr:
            words.append(tuple(curr)); curr = []
    if curr: words.append(tuple(curr))
    return runes, words

# Load cipher
cipher_list = []; words_all = []; cum = 0; page_offsets = {}
for pg in range(21, 55):
    runes, words = load_page(pg)
    if runes is None: continue
    page_offsets[pg] = cum; cum += len(runes)
    cipher_list.extend(runes)
    words_all.extend([(pg, cum - len(runes) + sum(len(w) for w in words[:i]), w) 
                      for i, w in enumerate(words)])

# Reconstruct correct word positions
CIPHER = cipher_list
N_CIPHER = len(CIPHER)

# Rebuild properly
words_with_pos = []; ki = 0; cum2 = 0
for pg in range(21, 55):
    runes, words = load_page(pg)
    if runes is None: continue
    for w in words:
        words_with_pos.append((pg, ki, len(w), w))
        ki += len(w)
    cum2 += len(runes)

# TTP link map
TTP_CONSTRAINTS = [
    (3001,  9727, 1312), (6298, 12311, 1468), (0, 5803, 404),
    (2736, 8643, 265),   (737,  8100,  172),  (910, 8273, 97),
]
LINK_MAP = list(range(N_CIPHER))
for src_s, dst_s, ln in TTP_CONSTRAINTS:
    for i in range(ln):
        LINK_MAP[dst_s + i] = LINK_MAP[src_s + i]

# Load checkpoint (accept optional path as argv[1])
ck_path = sys.argv[1] if len(sys.argv) > 1 else 'data/gpu_hill_checkpoint_gpu1_v3.json'
ck = json.loads(Path(ck_path).read_text())
KEY = ck['key']

print(f'Checkpoint: {ck_path}  score={ck.get("score",0):.1f}, step={ck.get("step",0):,}', flush=True)
print(f'Words to scan: {len(words_with_pos)}', flush=True)
print()

# Find all LP_CANON matches in current decode
CONFIRMED_CRIBS = []  # (start_pos, plaintext_gp_tuple)
CRIB_DETAILS = []

for pg, wstart, wlen, cipher_word in words_with_pos:
    # Decode this word slot
    decoded = tuple((CIPHER[wstart+i] - KEY[wstart+i]) % M for i in range(wlen))
    decoded_str = ''.join(IDX_TO[v] for v in decoded)
    
    # Check against CLEAN LP_CANON
    if decoded_str in LP_CANON_GP or decoded in LP_BY_TUPLE:
        # Only include words with length >= MIN_LEN (short words like I, A, AN, IS etc. 
        # are too ambiguous to be useful cribs)
        MIN_LEN = 5  # Only words of 5+ runes are reliable enough to lock
        if wlen >= MIN_LEN:
            CONFIRMED_CRIBS.append((wstart, decoded))
            CRIB_DETAILS.append((pg, wstart, wlen, decoded_str, cipher_word))

print(f'LP_CANON matches (len>=5): {len(CONFIRMED_CRIBS)}')
print()
print('All confirmed cribs:')
for pg, wstart, wlen, decoded_str, cipher_word in CRIB_DETAILS:
    print(f'  P{pg:02d} pos={wstart:5d}: "{decoded_str}" (len={wlen})')

print()

# Verify TTP consistency for cribs
print('TTP CONSISTENCY CHECK:')
ttp_violations = 0
for pg, wstart, wlen, decoded_str, cipher_word in CRIB_DETAILS:
    # Check if any position in this word is a TTP slave
    violations = []
    decoded = tuple((CIPHER[wstart+i] - KEY[wstart+i]) % M for i in range(wlen))
    for j in range(wlen):
        pos = wstart + j
        canon_pos = LINK_MAP[pos]
        if canon_pos != pos:  # TTP slave
            # Check that master position key also decodes correctly
            master_key = KEY[canon_pos]
            slave_expected = (CIPHER[pos] - master_key) % M
            if slave_expected != decoded[j]:
                violations.append((pos, canon_pos, slave_expected, decoded[j]))
    if violations:
        print(f'  TTP VIOLATION at "{decoded_str}" pos={wstart}: {violations}')
        ttp_violations += 1

if ttp_violations == 0:
    print('  ALL cribs TTP-consistent!')

print()

# Build FORCED_CRIBS_POS: {canonical_pos: required_key_value}
FORCED_CRIBS_POS = {}
for pg, wstart, wlen, decoded_str, cipher_word in CRIB_DETAILS:
    decoded = tuple((CIPHER[wstart+i] - KEY[wstart+i]) % M for i in range(wlen))
    for j in range(wlen):
        pos = wstart + j
        canon_pos = LINK_MAP[pos]
        key_val = (CIPHER[pos] - decoded[j]) % M
        
        # Check TTP consistency: all slaves of this canonical position should agree
        if canon_pos in FORCED_CRIBS_POS:
            existing = FORCED_CRIBS_POS[canon_pos]
            if existing != key_val:
                print(f'  CONFLICT at canon_pos={canon_pos}: new={key_val} existing={existing} (from {decoded_str})')
                continue
        FORCED_CRIBS_POS[canon_pos] = key_val

print(f'Total FORCED_CRIBS_POS (canonical positions): {len(FORCED_CRIBS_POS)}')

# Save cribs
output = {
    'source_checkpoint': 'gpu_hill_checkpoint_gpu1_v3.json',
    'checkpoint_score': ck['score'],
    'checkpoint_step': ck['step'],
    'cribs': [
        {'start': wstart, 'page': pg, 'word': decoded_str, 'length': wlen}
        for pg, wstart, wlen, decoded_str, _ in CRIB_DETAILS
    ],
    'forced_cribs_pos': {str(k): v for k, v in FORCED_CRIBS_POS.items()},
    'n_forced': len(FORCED_CRIBS_POS),
}
Path('data/v3_confirmed_cribs.json').write_text(json.dumps(output, indent=2))
out_path = 'data/v3_confirmed_cribs.json' if len(sys.argv) <= 2 else sys.argv[2]
Path(out_path).write_text(json.dumps(output, indent=2))
print(f'Saved to {out_path}')

# Show statistics
print()
print('Crib coverage:')
print(f'  Total cipher positions: {N_CIPHER}')
print(f'  Confirmed crib positions (canonical): {len(FORCED_CRIBS_POS)}')
print(f'  TTP-derived positions: {sum(1 for i in range(N_CIPHER) if LINK_MAP[i] != i)}')
print(f'  True free positions: {N_CIPHER - len(FORCED_CRIBS_POS) - sum(1 for i in range(N_CIPHER) if LINK_MAP[i] != i)}')

# Show by length histogram
from collections import Counter
crib_lengths = Counter(wlen for _, _, wlen, _, _ in CRIB_DETAILS)
print(f'  Crib words by length: {dict(sorted(crib_lengths.items()))}')
