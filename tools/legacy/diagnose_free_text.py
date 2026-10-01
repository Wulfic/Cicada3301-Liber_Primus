"""
Honest validation: are we finding real signal or forcing the text to say what we want?
Checks:
 1) How much of the decoded text is forced by cribs vs free?
 2) Do suspicious patterns repeat in free areas (sign of hillclimber noise)?
 3) Do LP-appropriate words appear in completely free regions?
 4) What does a blind random-key decode look like vs our current decode?
"""
import json, numpy as np, random
from pathlib import Path

M = 29
RUNE_TO_IDX = {chr(k): v for k, v in [
    (0x16A0,0),(0x16A2,1),(0x16A6,2),(0x16A9,3),(0x16B1,4),(0x16B3,5),
    (0x16B7,6),(0x16B9,7),(0x16BB,8),(0x16BE,9),(0x16C1,10),(0x16C4,11),
    (0x16C7,12),(0x16C8,13),(0x16C9,14),(0x16CB,15),(0x16CF,16),(0x16D2,17),
    (0x16D6,18),(0x16D7,19),(0x16DA,20),(0x16DD,21),(0x16DF,22),(0x16DE,23),
    (0x16AA,24),(0x16AB,25),(0x16A3,26),(0x16E1,27),(0x16E0,28)]}
IDX_TO = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA']
LETTER_TO_GP = {
    'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
    'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
    'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':14,
    'TH':2,'OE':22,'AE':25,'NG':21,'EO':12,'IO':27,'EA':28
}
def dec(seq): return ''.join(IDX_TO[v] for v in seq if 0 <= v < M)
def enc(phrase):
    w = phrase.upper().replace(' ', '')
    r = []
    i = 0
    while i < len(w):
        if i+1 < len(w) and w[i:i+2] in LETTER_TO_GP:
            r.append(LETTER_TO_GP[w[i:i+2]]); i += 2
        elif w[i] in LETTER_TO_GP:
            r.append(LETTER_TO_GP[w[i]]); i += 1
        else:
            i += 1
    return r

# Load cipher
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

TTP = [(3001,9727,1312),(6298,12311,1468),(0,5803,404),(2736,8643,265),(737,8100,172),(910,8273,97)]
LINK_MAP = np.arange(len(CIPHER), dtype=np.int32)
for s, d, l in TTP:
    for i in range(l):
        LINK_MAP[d+i] = LINK_MAP[s+i]

ck = json.load(open('data/gpu_hill_checkpoint_gpu1.json'))
KEY = np.array(ck['key'], dtype=np.int32)[LINK_MAP]
PLAIN = (CIPHER - KEY) % M

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

crib_canon = set()
for phrase, pos in CONFIRMED_CRIBS:
    e = enc(phrase)
    for i in range(len(e)):
        crib_canon.add(pos + i)

# TTP slave positions
ttp_slave = set()
for s, d, l in TTP:
    for i in range(l):
        ttp_slave.add(d + i)

free_pos = [i for i in range(len(CIPHER)) if i not in crib_canon and i not in ttp_slave]

print(f"=== POSITION ACCOUNTING ===")
print(f"  Total rune positions : {len(CIPHER):,}")
print(f"  Crib-locked (forced) : {len(crib_canon):,}  ({100*len(crib_canon)/len(CIPHER):.1f}%)")
print(f"  TTP slaves (derived) : {len(ttp_slave):,}  ({100*len(ttp_slave)/len(CIPHER):.1f}%)")
print(f"  Truly free           : {len(free_pos):,}  ({100*len(free_pos)/len(CIPHER):.1f}%)")
print()

# ---------------------------------------------------------------
# CHECK 1: Repeating noise patterns in free regions
# If the same short pattern keeps appearing it's the hillclimber
# fitting to n-gram statistics rather than real text.
# ---------------------------------------------------------------
full_decoded = dec(PLAIN)
print("=== PATTERN REPETITION IN FULL DECODE ===")
test_patterns = ['DPTS', 'CDPI', 'TSUH', 'SEATU', 'EATSUH', 'CDPIOPR', 'TSEATS']
for pat in test_patterns:
    count = full_decoded.count(pat)
    # How many times in a random English text of equal length?
    # LP 29-gram model: rough estimate 1/29^len(pat) * len(full) for random
    random_expected = len(full_decoded) / (29 ** len(pat)) * (29/2)  # rough
    print(f"  '{pat}' ({len(pat)} chars): {count:3d} occurrences  (random noise expected: <1)")

print()

# ---------------------------------------------------------------
# CHECK 2: LP vocabulary hits in completely free regions
# ---------------------------------------------------------------
LP_VOCAB = [
    'TRUTH','LIGHT','DARK','SEEK','KNOWLEDGE','WISDOM','MIND','SOUL','BODY',
    'FOLLOW','SACRED','PATH','LEARN','GUIDE','BLIND','AWAKE','SLEEP','DEATH',
    'LIFE','BEGIN','END','WELCOME','PILGRIM','JOURNEY','PRIME','NUMBER',
    'SEQUENCE','CICADA','RUNE','LANGUAGE','WORD','HEAR','SEE','FEEL',
    'BECOME','MASTER','SERVANT','FREE','SLAVE','CONTROL','DECEPTION',
    'SACRIFICE','CONSUME','CONSUME','DIVINE','MORTAL','IMMORTAL',
    'BEYOND','WITHIN','WITHOUT','THROUGH','AGAINST','TOWARD',
    'WEDONOT','DONOT','WEARE','THEYARE','YOUARE','WESHALL','YOUSHALL',
]

print("=== LP VOCABULARY IN COMPLETELY FREE REGIONS ===")
print("(These are positions NOT in any crib, NOT TTP-derived)")
hits = []
for word in LP_VOCAB:
    e = enc(word)
    n = len(e)
    for pos in range(len(CIPHER) - n):
        # Only count if ALL positions in the word are free
        if not all(p not in crib_canon and p not in ttp_slave for p in range(pos, pos+n)):
            continue
        if all(PLAIN[pos+i] == e[i] for i in range(n)):
            pg = next((p for p in sorted(page_offsets, reverse=True) if page_offsets[p] <= pos), '?')
            hits.append((word, pos, pg, pos - page_offsets[pg]))

print(f"  Total vocabulary hits in free regions: {len(hits)}")
for word, pos, pg, offset in hits[:25]:
    ctx_start = max(0, pos - 15)
    ctx_end = min(len(PLAIN), pos + len(enc(word)) + 15)
    context = dec(PLAIN[ctx_start:ctx_end])
    print(f"  {word:<20s} @P{pg}+{offset:4d}: ...{context}...")

print()

# ---------------------------------------------------------------
# CHECK 3: Compare quadgram density: crib regions vs free regions
# If the cribs are inflating the score it should be obvious
# ---------------------------------------------------------------
print("=== FREE TEXT SAMPLE (80-char windows, no cribs nearby) ===")
shown = 0
for start in range(0, len(CIPHER) - 80, 60):
    region = range(start, start + 80)
    if any(p in crib_canon for p in region):
        continue
    if any(p in ttp_slave for p in region):
        continue
    decoded = dec(PLAIN[start:start+80])
    pg = next((p for p in sorted(page_offsets, reverse=True) if page_offsets[p] <= start), '?')
    print(f"  P{pg}+{start-page_offsets[pg]:4d}: {decoded}")
    shown += 1
    if shown >= 15:
        break

print()

# ---------------------------------------------------------------
# CHECK 4: Gold standard comparison - what does a random key produce?
# This shows the baseline "noise floor"
# ---------------------------------------------------------------
print("=== BASELINE: RANDOM KEY DECODE (what noise looks like) ===")
rng = np.random.default_rng(42)
random_key = rng.integers(0, M, size=len(CIPHER), dtype=np.int32)
random_plain = (CIPHER - random_key) % M
random_decoded = dec(random_plain)
print(f"  Random key sample: {random_decoded[:200]}")
print()

random_hits = []
for word in LP_VOCAB:
    e = enc(word)
    n = len(e)
    for pos in range(len(CIPHER) - n):
        if all(random_plain[pos+i] == e[i] for i in range(n)):
            random_hits.append(word)
            if len(random_hits) >= 20:
                break
    if len(random_hits) >= 20:
        break
print(f"  LP vocab hits in random decode (first 20): {random_hits}")
print(f"  Our decode LP vocab free hits: {len(hits)}")
print()

# ---------------------------------------------------------------
# FINAL VERDICT
# ---------------------------------------------------------------
print("=== HONEST ASSESSMENT ===")
repeating = sum(1 for pat in test_patterns if full_decoded.count(pat) > 3)
print(f"  Suspicious repeating patterns: {repeating}/{len(test_patterns)}")
print(f"  LP vocabulary in free regions: {len(hits)} hits")
print(f"  Step: {ck['step']}, Score: {ck['score']:.0f}")
print()
print("  INTERPRETATION:")
if repeating > 3:
    print("  WARNING: Multiple noise patterns repeat >3x - hillclimber may be in a local optimum")
    print("  The free text is NOT converging to real language yet.")
else:
    print("  Pattern repetition low - free text may be approaching real language.")
if len(hits) > 10:
    print(f"  {len(hits)} LP vocabulary words in free regions is encouraging signal.")
else:
    print("  Few LP vocabulary hits in free regions - most readable text is near cribs.")
