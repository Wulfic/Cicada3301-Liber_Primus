"""
show_current_decode.py — Decode entire P21-54 cipher using the current
hillclimber checkpoint key, annotating known LP vocabulary and crib positions.

Usage:
  python Tools/show_current_decode.py [--full]  (--full shows all pages raw)
"""

import json, sys
from pathlib import Path
import numpy as np
import re

# ── GP alphabet ───────────────────────────────────────────────────────────────
M = 29
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

def encode(text):
    text = text.upper()
    enc = []
    i = 0
    while i < len(text):
        digraph = text[i:i+2]
        if digraph in LETTER_TO_GP:
            enc.append(LETTER_TO_GP[digraph]); i += 2
        elif text[i] in LETTER_TO_GP:
            enc.append(LETTER_TO_GP[text[i]]); i += 1
        else:
            i += 1
    return enc

def gp_to_text(indices):
    return ''.join(IDX_TO[i] if 0 <= i < len(IDX_TO) else '?' for i in indices)

# ── Load cipher ───────────────────────────────────────────────────────────────
def load_page(pg):
    path = Path(f'pages/page_{pg:02d}/runes.txt')
    if not path.exists():
        return [], []
    text = path.read_text(encoding='utf-8')
    runes = []; words = []; curr = []; word_starts = []
    pos = 0
    for ch in text:
        if ch in RUNE_TO_IDX:
            if not curr:
                word_starts.append(pos)
            runes.append(RUNE_TO_IDX[ch])
            curr.append(RUNE_TO_IDX[ch])
            pos += 1
        elif ch in '-. \n\r\t\u2022/' and curr:
            words.append((word_starts[-1], tuple(curr)))
            curr = []
    if curr:
        words.append((word_starts[-1] if word_starts else 0, tuple(curr)))
    return runes, words

cipher_list = []; words_all = []; page_offsets = {}; cum = 0
for pg in range(21, 55):
    runes, words = load_page(pg)
    if runes:
        page_offsets[pg] = cum
        cum += len(runes)
        cipher_list.extend(runes)
        words_all.extend([(ws + page_offsets[pg] - cum + len(runes), wv) for ws, wv in words])

# Recompute words_all with correct global offsets
words_all = []
cum = 0
for pg in range(21, 55):
    runes, words = load_page(pg)
    if runes:
        for ws, wv in words:
            words_all.append((cum + ws, wv))
        cum += len(runes)

CIPHER = np.array(cipher_list, dtype=np.int32)
N = len(CIPHER)

# ── Load checkpoint ───────────────────────────────────────────────────────────
ck = json.load(open('data/gpu_hill_checkpoint_gpu1.json'))
KEY = np.array(ck['key'], dtype=np.int32)
step = ck['step']
score = ck['score']

DECODE = [(int(CIPHER[i]) - int(KEY[i])) % M for i in range(N)]

# ── Known LP vocabulary (for annotation) ─────────────────────────────────────
LP_VOCAB = set("""CONSUMPTION PRESERVATION ADHERENCE CIRCUMFERENCE DIVINITY DIUINITY
DIUINTY LOSSOF THELOSSOF INSTRUCTION SOMEWISDOM ANINSTRUCTION AKOAM KOAN
WELCOME PILGRIM TRUTH PATH WALK CEASING CEASE SEEK PATTERN PATTERNS WHOLE
SIMPLY DETAIL PROFUNDITY BEGIN BUILD KNOWLEDGE WISDOM LOSE WHAT KNOW THIS
PROGRAM FOLLOW YOUR FOLLOWYOUR WEFOLLOW DECEPTION NOTFEAR FEAR
STRONGENCE PARABLE SACRED PRESACRED THINGS WORTH DESTROY OWN ALL THAT YOU
BEHAVIORS THREE PRACTICES CAUSE LOSS THREE BEHAVIORS TOIL NOTWORTH
PRESERVATION PRESERUATION AETHERIC CARNAL OBSCURA FORM MOBIUS AETHEREAL
BUFFER ETHEREAL PRIMES PRIMES ARE SACRED PRIME NUMBERS REMEMBER FORGET
SPIRITU SPIRITUAL MORTAL IMMORTAL DIVINE LIFE DEATH LIGHT DARKNESS SHADOW
ONENESS UNITY ALL NOTHING EVERYTHING VOID EMPTY""".split())

# Also load LP vocabulary from key_search_corpus if available
try:
    for ln in open('data/key_search_corpus.txt', encoding='utf-8'):
        w = ln.strip().upper()
        if w:
            LP_VOCAB.add(w)
except FileNotFoundError:
    pass

# ── Confirmed cribs ───────────────────────────────────────────────────────────
CONFIRMED_CRIBS = [
    ('CONSUMPTION',          31),
    ('KNOWTHIS',            476),
    ('PROGRAM',             599),
    ('DIUINITY',           1356),
    ('PRESERUATION',       2093),
    ('CIRCUMFERENCE',      3080),
    ('SOMEWISDOM',         4131),
    ('THELOSSOFDIUINITY',  4325),
    ('ADHERENCE',          8532),
]
CRIB_REGIONS = {}  # pos → phrase_tag
for phrase, start in CONFIRMED_CRIBS:
    enc = encode(phrase)
    for i, v in enumerate(enc):
        CRIB_REGIONS[start + i] = phrase[:8]

# ── Helper: find LP vocab in decoded text ─────────────────────────────────────
def find_lp_words(decoded_str):
    """Return all LP vocabulary word occurrences as (start, end, word) in decoded string."""
    hits = []
    s = decoded_str.upper()
    for w in sorted(LP_VOCAB, key=len, reverse=True):
        idx = 0
        while True:
            pos = s.find(w, idx)
            if pos < 0:
                break
            hits.append((pos, pos + len(w), w))
            idx = pos + 1
    # Remove overlapping (keep longest)
    hits.sort(key=lambda x: (x[0], -(x[1]-x[0])))
    filtered = []
    covered = set()
    for s_i, e_i, w in hits:
        if not any(p in covered for p in range(s_i, e_i)):
            filtered.append((s_i, e_i, w))
            covered.update(range(s_i, e_i))
    return filtered

# ── Print each page's decode with LP word annotations ────────────────────────
print(f'Hillclimber decode — step {step}, score {score:.1f}')
print(f'Checking {N} runes across pages 21-54\n')
print('═' * 80)

pages_sorted = sorted(page_offsets.items())
full_mode = '--full' in sys.argv

for i, (pg, start) in enumerate(pages_sorted):
    end = pages_sorted[i+1][1] if i+1 < len(pages_sorted) else N
    length = end - start
    decoded = DECODE[start:end]
    dec_str = gp_to_text(decoded)
    
    # Find LP vocabulary hits in this page's decode
    lp_hits = find_lp_words(dec_str)
    lp_char_count = sum(e - s for s, e, _ in lp_hits)
    lp_density = lp_char_count / max(1, len(dec_str))
    
    # Check crib positions in this page
    cribs_here = [(CRIB_REGIONS.get(start+j), j) for j in range(length)
                  if (start+j) in CRIB_REGIONS]
    crib_starts = sorted(set((v, j) for v, j in cribs_here if j > 0 and
                             (start+j-1) not in CRIB_REGIONS))
    
    # Compact display
    tag = f'P{pg:02d}  +{start:5d}..+{end-1:5d}  ({length:4d} runes)  LP-density: {lp_density*100:4.1f}%'
    
    # List LP words found
    lp_word_list = sorted(set(w for _, _, w in lp_hits))
    
    print(f'\n{tag}')
    if cribs_here:
        print(f'  CRIBS: {", ".join(set(v for v,_ in cribs_here if v))}')
    
    # Show LP vocabulary found
    if lp_word_list:
        print(f'  LP-vocab: {", ".join(lp_word_list[:15])}')
    
    # Show annotated decode (first 100 chars)
    if lp_density > 0.2 or cribs_here or full_mode:
        # Build annotated string: LP hits in UPPER, noise in lower
        annotated = list(dec_str.lower())
        for s_i, e_i, w in lp_hits:
            for k in range(s_i, e_i):
                annotated[k] = annotated[k].upper()
        ann_str = ''.join(annotated)
        
        # Show in 80-char chunks
        chunk_size = 78
        for chunk_start in range(0, min(len(ann_str), 300), chunk_size):
            chunk = ann_str[chunk_start:chunk_start+chunk_size]
            offset = start + chunk_start
            print(f'   g+{offset:<5d}: {chunk}')

# ── Print full inter-crib gap analysis ───────────────────────────────────────
print('\n\n' + '═' * 80)
print('INTER-CRIB GAP ANALYSIS')
print('═' * 80)

crib_boundaries = sorted([(s, s+len(encode(p))-1, p) for p,s in CONFIRMED_CRIBS])

for ci, (cs, ce, phrase) in enumerate(crib_boundaries):
    # Decode right after this crib, up to next crib
    next_start = crib_boundaries[ci+1][0] if ci+1 < len(crib_boundaries) else N
    gap_start = ce + 1
    gap_end = next_start - 1
    if gap_start >= gap_end:
        continue
    
    gap_len = gap_end - gap_start + 1
    decoded = DECODE[gap_start:gap_end+1]
    dec_str = gp_to_text(decoded)
    lp_hits = find_lp_words(dec_str)
    lp_chars = sum(e - s for s, e, _ in lp_hits)
    lp_dens = lp_chars / max(1, len(dec_str))
    
    next_phrase = crib_boundaries[ci+1][2] if ci+1 < len(crib_boundaries) else 'END'
    print(f'\nGap after {phrase:<20s} → {next_phrase:<20s}  '
          f'({gap_len} runes, LP-density {lp_dens*100:.1f}%)')
    
    if lp_dens > 0.05 or gap_len < 50:
        annotated = list(dec_str.lower())
        for s_i, e_i, _w in lp_hits:
            for k in range(s_i, e_i):
                annotated[k] = annotated[k].upper()
        ann_str = ''.join(annotated)
        print(f'  g{gap_start}: {ann_str[:120]}')

print('\nDone.')
