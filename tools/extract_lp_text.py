"""
LP text extraction from the best available sub-mode key.
- Shows extended context (full page decode)
- Marks confirmed anchor positions with [*]
- Uses crib-anchor correction: at known-perfect positions, the key IS correct;
  at other positions we use the hillclimber's best estimate.
- Also attempts LP text reconstruction by applying per-crib knowledge.
"""

import json
from pathlib import Path
from collections import Counter

# ─── Alphabet ────────────────────────────────────────────────────────────────
IDX_TO = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S',
          'T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA']
M = 29

LETTER_TO_GP = {
    'F':0,'U':1,'TH':2,'O':3,'R':4,'C':5,'K':5,'G':6,'W':7,'H':8,
    'N':9,'I':10,'J':11,'Y':26,'EO':12,'P':13,'X':14,'Z':14,'S':15,
    'T':16,'B':17,'E':18,'M':19,'L':20,'NG':21,'OE':22,'D':23,'A':24,
    'AE':25,'IO':27,'IG':21,'IA':27,'EA':28,'V':1,'Q':5,
}

RUNE_TO_IDX = {chr(k): v for k, v in [
    (0x16A0,0),(0x16A2,1),(0x16A6,2),(0x16A9,3),(0x16B1,4),(0x16B3,5),
    (0x16B7,6),(0x16B9,7),(0x16BB,8),(0x16BE,9),(0x16C1,10),(0x16C4,11),
    (0x16C7,12),(0x16C8,13),(0x16C9,14),(0x16CB,15),(0x16CF,16),(0x16D2,17),
    (0x16D6,18),(0x16D7,19),(0x16DA,20),(0x16DD,21),(0x16DF,22),(0x16DE,23),
    (0x16AA,24),(0x16AB,25),(0x16A3,26),(0x16E1,27),(0x16E0,28)]}

def encode(word):
    runes, i, w = [], 0, word.upper()
    while i < len(w):
        if w[i] == ' ': i+=1; continue
        if i+2<len(w) and w[i:i+3] in LETTER_TO_GP:
            runes.append(LETTER_TO_GP[w[i:i+3]]); i+=3
        elif i+1<len(w) and w[i:i+2] in LETTER_TO_GP:
            runes.append(LETTER_TO_GP[w[i:i+2]]); i+=2
        elif w[i] in LETTER_TO_GP:
            runes.append(LETTER_TO_GP[w[i]]); i+=1
        else:
            i+=1
    return runes

def decode_idx_to_str(rune_indices):
    return ''.join(IDX_TO[v] for v in rune_indices)

# ─── Load cipher from pages ───────────────────────────────────────────────────
def load_page(pg):
    path = Path(f'pages/page_{pg:02d}/runes.txt')
    if not path.exists(): return []
    return [RUNE_TO_IDX[c] for c in path.read_text('utf-8') if c in RUNE_TO_IDX]

cipher = []
page_offsets = {}
for pg in range(21, 55):
    page_offsets[pg] = len(cipher)
    cipher.extend(load_page(pg))
N = len(cipher)
# reverse lookup: global pos → page
pos_to_page = {}
pages_sorted = sorted(page_offsets.items())
for i, (pg, start) in enumerate(pages_sorted):
    end = pages_sorted[i+1][1] if i+1 < len(pages_sorted) else N
    for p in range(start, end): pos_to_page[p] = pg

# ─── Load checkpoint ─────────────────────────────────────────────────────────
with open('data/gpu_hill_checkpoint_gpu0.json') as f:
    ckpt = json.load(f)
key = ckpt['key']

# ─── Apply confirmed anchor corrections ──────────────────────────────────────
# These are positions where the plaintext is KNOWN (perfect crib match).
# key is already correct here, but let's document them.
CONFIRMED_CRIBS = [
    ("CONSUMPTION",           31),
    ("KNOW THIS",            476),
    ("PROGRAM",              599),
    ("DIVINITY",            1356),   # actually "DIUINITY"
    ("PRESERVATION",        2093),   # as "PRESERUATION"
    ("SOME WISDOM",         4131),
    ("ADHERENCE",           8532),
]

# Additional near-perfect: 15/16 on "THE LOSS OF DIVINITY" at 4325
# Only first char wrong (B→TH), fix it:
MANUAL_CORRECTIONS = {
    4325: encode("TH")[0],   # force TH at start of "THE LOSS OF DIVINITY"
}

confirmed_positions = set()
confirmed_plain = {}

for phrase, start in CONFIRMED_CRIBS:
    plain_runes = encode(phrase)
    for i, rv in enumerate(plain_runes):
        pos = start + i
        confirmed_positions.add(pos)
        confirmed_plain[pos] = rv

# Apply manual corrections to key
key_corrected = list(key)
for pos, val in MANUAL_CORRECTIONS.items():
    # key[pos] such that (cipher[pos] - key[pos]) % M == val
    key_corrected[pos] = (cipher[pos] - val) % M
    confirmed_plain[pos] = val
    confirmed_positions.add(pos)

# ─── Decode with corrected key ────────────────────────────────────────────────
def decode_pos(pos):
    return (cipher[pos] - key_corrected[pos]) % M

# ─── LP vocabulary look for context highlighting ─────────────────────────────
LP_VOCAB = [
    "CONSUMPTION","PRESERVATION","ADHERENCE","DIVINITY","DIUINITY",
    "PRIMES","SACRED","WISDOM","INSTRUCTION","PROGRAM","CIRCUMFERENCE",
    "DECEPTION","REALITY","WITHIN","WITHOUT","BEHAVIOR","BEHAVIORS",
    "THELOSSOFDIVINITY","THELOSS","LOSS","TRUTH","QUESTION","KNOWLEDGE",
    "ALL THINGS","ALLTHINGS","ENCRYPT","ENCRYPTED","BELONG","ENOUGH",
    "PROGRAM YOUR MIND","SOME WISDOM","KNOW THIS","FOLLOW","FOLLOW YOUR TRUTH",
    "NEVER","ATTACHED","WEALTH","DESTROY","AMASS","IMPOSE","NOTHING",
    "BEAUTIFULLY","SACRED","PRESERUATION","PRESERNATION","ADHERENCE",
]
LP_ENCODED = {tuple(encode(w)): w for w in LP_VOCAB}

def find_vocab_hits(plain_seq, start_pos=0):
    hits = {}
    for seq, word in LP_ENCODED.items():
        seq = list(seq)
        L = len(seq)
        for i in range(len(plain_seq) - L + 1):
            if plain_seq[i:i+L] == seq:
                for j in range(L):
                    hits[start_pos+i+j] = word
    return hits

# ─── Per-page decode output ───────────────────────────────────────────────────
print("=" * 80)
print("LP TEXT EXTRACTION — GPU0 Sub Mode Checkpoint")
print(f"Key source: {ckpt['mode']} mode, step={ckpt['step']:,}, score={ckpt['score']:.0f}")
print("Confirmed cribs (key known exactly):", len(confirmed_positions), "positions")
print("=" * 80)

total_lines = []

for pg in range(21, 55):
    start = page_offsets[pg]
    pg_idx = list(page_offsets.keys()).index(pg)
    next_pg = list(page_offsets.keys())[pg_idx+1] if pg_idx+1 < len(page_offsets) else None
    end = page_offsets[next_pg] if next_pg else N

    plain_seq = [decode_pos(p) for p in range(start, end)]
    plain_str = decode_idx_to_str(plain_seq)
    vocab_hits = find_vocab_hits(plain_seq, start)

    # Count anchors in this page
    anchors_here = sum(1 for p in range(start, end) if p in confirmed_positions)

    print(f"\n{'='*80}")
    print(f"P{pg} | pos {start}...{end-1} | len={end-start} | confirmed_anchors={anchors_here}")
    print(f"{'='*80}")

    # Print with position markers every 30 chars and anchor highlighting
    line = []
    col = 0
    for i, rv in enumerate(plain_seq):
        pos = start + i
        letter = IDX_TO[rv]
        if pos in confirmed_positions:
            letter = f"[{letter}]"
        elif pos in vocab_hits:
            letter = f"{letter}"
        line.append(letter)
        col += 1
        if col >= 100:
            print("  " + "".join(line))
            line = []; col = 0
    if line:
        print("  " + "".join(line))

    # Show vocabulary hits
    vhit_words = sorted(set(vocab_hits.values()))
    if vhit_words:
        print(f"  Vocabulary: {', '.join(vhit_words)}")

    total_lines.append((pg, plain_str, anchors_here, vhit_words))

print("\n" + "=" * 80)
print("SUMMARY: LP vocabulary hit counts per page")
print("=" * 80)
for pg, txt, anc, vw in total_lines:
    start = page_offsets[pg]
    print(f"P{pg:2d} (pos={start:5d}): anchors={anc:3d}  vocab_hits=[{', '.join(vw[:5])}{',...' if len(vw)>5 else ''}]")

# ─── Save decoded text to file ────────────────────────────────────────────────
out_path = Path("data/lp_extraction.txt")
with open(out_path, "w", encoding="utf-8") as f:
    f.write("LP TEXT EXTRACTION — GPU0 Sub Mode (corrected key)\n")
    f.write(f"Mode: sub | Step: {ckpt['step']:,} | Score: {ckpt['score']:.0f}\n\n")
    for pg, plain_str, anc, vw in total_lines:
        start = page_offsets[pg]
        f.write(f"\nP{pg} (pos={start}):\n  {plain_str}\n")
        if vw:
            f.write(f"  Vocab: {', '.join(vw)}\n")
print(f"\nFull extraction saved to {out_path}")
