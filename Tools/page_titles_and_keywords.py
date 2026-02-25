#!/usr/bin/env python3
"""
Examine page titles and structural features of dot-format pages.
Also try Vigenère with known keywords from solved pages at all offsets.
"""

import os, glob
from collections import Counter

GP = {
    '\u16A0':0, '\u16A2':1, '\u16A6':2, '\u16A9':3, '\u16B1':4, '\u16B3':5, '\u16B7':6, '\u16B9':7,
    '\u16BB':8, '\u16BE':9, '\u16C1':10, '\u16C2':11, '\u16C4':11,
    '\u16C7':12, '\u16C8':13, '\u16C9':14, '\u16CB':15, '\u16CF':16, '\u16D2':17, '\u16D6':18,
    '\u16D7':19, '\u16DA':20, '\u16DD':21, '\u16DF':22, '\u16DE':23, '\u16AA':24, '\u16AB':25,
    '\u16A3':26, '\u16E1':27, '\u16E0':28
}
IDX2LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}

def ioc(vals, alpha=29):
    c = Counter(vals)
    n = len(vals)
    if n < 2: return 0
    return sum(f*(f-1) for f in c.values()) / (n*(n-1)) * alpha

def to_text(vals, limit=50):
    return ''.join(IDX2LAT[v] for v in vals[:limit])

# Load all pages with their raw text
pages_text = {}
pages_vals = {}
for page_dir in sorted(glob.glob('LiberPrimus/pages/page_*/runes.txt')):
    pnum = int(page_dir.replace('\\','/').split('page_')[1].split('/')[0])
    with open(page_dir, 'r', encoding='utf-8') as f:
        text = f.read()
    vals = [GP[ch] for ch in text if ch in GP]
    if vals:
        pages_text[pnum] = text
        pages_vals[pnum] = vals

# Classify pages by format
print("=== Page Format Analysis ===")
for pnum in sorted(pages_text.keys()):
    if 18 <= pnum <= 54:
        text = pages_text[pnum]
        has_dot = '•' in text or '.' in text
        has_hyphen = '-' in text
        first_line = text.split('\n')[0].strip()
        
        # Get first line runes
        first_runes = [GP[ch] for ch in first_line if ch in GP]
        first_text = to_text(first_runes, 40)
        
        # Check if first line is a title (shorter, all one segment)
        is_title = len(first_runes) < 20 and ('•' in first_line or '/' not in first_line)
        
        fmt = "DOT" if has_dot and not has_hyphen else "HYPH" if has_hyphen and not has_dot else "BOTH" if has_dot and has_hyphen else "NONE"
        print(f"  P{pnum:02d} [{fmt}] {len(pages_vals[pnum]):4d} runes, first: {first_text}")

# === Try ALL known keywords from solved pages as Vigenère keys ===
print("\n=== Vigenère with ALL known keywords ===")

# Known keywords from solved pages (from wiki)
keywords = {
    "DIVINITY": [23, 10, 1, 10, 9, 10, 16, 26],
    "FIRFUMFERENFE": None,  # compute
    "DEOR": [23, 18, 3, 4],
    "CABAL": None,
    "CONSUMPTION": None,
    "PRIMES": None,
    "SACRED": None,
    "TOTIENT": None,
    "VOID": None,
    "SHADOWS": None,
    "MOBIUS": None,
    "ENCRYPTION": None,
    "ANALOG": None,
    "AETHEREAL": None,
    "MOURNFUL": None,
    "CARNAL": None,
    "BUFFERS": None,
    "OBSCURA": None,
    "YAHEOOPYJ": None,
    "INSTAR": None,
    "PILGRIM": None,
    "CIRCUMFERENCE": None,
    "WELCOME": None,
    "WARNING": None,
    "KOAN": None,
    "PARABLE": None,
    "WISDOM": None,
    "FOLLY": None,
}

# Convert keywords to GP
def keyword_to_gp(word):
    result = []
    i = 0
    word_upper = word.upper()
    while i < len(word_upper):
        # Check for digraphs first
        if i + 1 < len(word_upper):
            digraph = word_upper[i:i+2]
            digraph_map = {'TH': 2, 'NG': 21, 'EO': 12, 'OE': 22, 'AE': 25, 'IA': 27, 'EA': 28}
            if digraph in digraph_map:
                result.append(digraph_map[digraph])
                i += 2
                continue
        if word_upper[i] in ENG2GP:
            result.append(ENG2GP[word_upper[i]])
        i += 1
    return result

for kname in keywords:
    keywords[kname] = keyword_to_gp(kname)

# Test each keyword on each unsolved page
best_results = []
for pnum, vals in pages_vals.items():
    if not (18 <= pnum <= 54) or len(vals) < 100:
        continue
    for kname, kvals in keywords.items():
        if not kvals or len(kvals) < 2:
            continue
        for mode_name, mode_fn in [('SUB', lambda c,k: (c-k)%29), ('ADD', lambda c,k: (c+k)%29), ('BEAU', lambda c,k: (k-c)%29)]:
            result = [mode_fn(vals[i], kvals[i % len(kvals)]) for i in range(len(vals))]
            ic = ioc(result)
            if ic > 1.2:
                lat = to_text(result, 30)
                best_results.append((ic, pnum, kname, mode_name, lat))

best_results.sort(key=lambda x: -x[0])
for ic, pnum, kname, mode, lat in best_results[:30]:
    print(f"  P{pnum} {mode}({kname}): IoC={ic:.4f}, start={lat}")

# === Also try the keyword as Atbash+shift ===
print("\n=== Atbash + shift on unsolved pages ===")
for pnum, vals in pages_vals.items():
    if not (18 <= pnum <= 54) or len(vals) < 200:
        continue
    for shift in range(29):
        result = [(28 - v + shift) % 29 for v in vals]
        ic = ioc(result)
        if ic > 1.2:
            print(f"  P{pnum} atbash+{shift}: IoC={ic:.4f}")

# === Try known key at different starting offsets ===
# The DIVINITY key was used for P03, P04, P61, P62
# What if it's used with an offset for unsolved pages?
print("\n=== DIVINITY key with offset ===")
div_key = keywords["DIVINITY"]
for pnum in [18, 19, 20, 21, 22, 23, 24, 25, 32]:
    vals = pages_vals[pnum]
    for start_offset in range(len(div_key)):
        for mode_name, fn in [('SUB', lambda c,k: (c-k)%29), ('ADD', lambda c,k: (c+k)%29), ('BEAU', lambda c,k: (k-c)%29)]:
            shifted_key = div_key[start_offset:] + div_key[:start_offset]
            result = [fn(vals[i], shifted_key[i % len(shifted_key)]) for i in range(len(vals))]
            ic = ioc(result)
            if ic > 1.2:
                print(f"  P{pnum} {mode_name} DIVINITY offset={start_offset}: IoC={ic:.4f}")

print("\nDone.")
