#!/usr/bin/env python3
"""
Deep bifid cipher investigation on LP unsolved pages.
- Try keyword-keyed grids with many Cicada-related words
- Test both 5x6 and 6x5 grids
- Test all periods 2-50
- Try reversed GP ordering, frequency-based ordering
- Try TRIFID (3D fractionation) as well
"""

import os, glob, itertools
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

def to_text(vals, limit=80):
    return ''.join(IDX2LAT[v] for v in vals[:limit])

# Load pages
pages_vals = {}
for page_dir in sorted(glob.glob('LiberPrimus/pages/page_*/runes.txt')):
    pnum = int(page_dir.replace('\\','/').split('page_')[1].split('/')[0])
    with open(page_dir, 'r', encoding='utf-8') as f:
        text = f.read()
    vals = [GP[ch] for ch in text if ch in GP]
    if vals:
        pages_vals[pnum] = vals

def keyword_to_gp(word):
    result = []
    i = 0
    word_upper = word.upper()
    while i < len(word_upper):
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

def make_keyed_alphabet(keyword_vals):
    """Create a keyed alphabet: keyword values first (deduped), then remaining in order."""
    seen = set()
    result = []
    for v in keyword_vals:
        if v not in seen:
            result.append(v)
            seen.add(v)
    for v in range(29):
        if v not in seen:
            result.append(v)
            seen.add(v)
    return result

def bifid_decrypt_keyed(ciphertext, period, grid_perm, grid_w):
    """
    Bifid decrypt using a permuted grid.
    grid_perm: maps GP value -> grid position (0-28)
    grid_w: grid width
    """
    inv_perm = [0]*29  # grid position -> GP value
    for v, pos in enumerate(grid_perm):
        inv_perm[pos] = v
    
    result = []
    for block_start in range(0, len(ciphertext), period):
        block = ciphertext[block_start:block_start+period]
        blen = len(block)
        
        # Map cipher values to grid positions, then to row/col
        positions = [grid_perm[v] for v in block]
        rows = [p // grid_w for p in positions]
        cols = [p % grid_w for p in positions]
        
        # Bifid recombination: interleave  
        coords = rows + cols
        
        for i in range(blen):
            r = coords[i]
            c = coords[i + blen]
            pos = r * grid_w + c
            if pos >= 29:
                pos = pos % 29  # wrap
            result.append(inv_perm[pos])
    
    return result

# Keywords to test
keywords = [
    "DIVINITY", "FIRFUMFERENFE", "CIRCUMFERENCE", "PRIMES", "CONSUMPTION",
    "SACRED", "TOTIENT", "VOID", "SHADOWS", "MOBIUS", "ENCRYPTION",
    "ANALOG", "AETHEREAL", "MOURNFUL", "CARNAL", "BUFFERS", "OBSCURA",
    "WELCOME", "WARNING", "KOAN", "PARABLE", "WISDOM", "FOLLY",
    "INSTAR", "PILGRIM", "DEOR", "CABAL", "LIBER", "PRIMUS",
    "GEMATRIA", "RUNE", "CIPHER", "AN", "SOME", "TRUTH", "COMMAND",
    "AWAKEN", "EMERGENCE", "LOSS", "INTERCONNECTEDNESS", "DEPTH",
    "SELFRELIANCE", "EMERSON",  # Referenced in solved pages
]

# Test pages (large unsolved ones)
target_pages = [p for p in pages_vals if 18 <= p <= 54 and len(pages_vals[p]) >= 200]

print(f"=== BIFID: Testing {len(keywords)} keywords x 2 grid sizes x {len(target_pages)} pages ===")

best_results = []

for kw_text in keywords:
    kw_gp = keyword_to_gp(kw_text)
    keyed_alpha = make_keyed_alphabet(kw_gp)
    
    # grid_perm: value v -> position in grid = keyed_alpha.index(v)
    grid_perm = [0]*29
    for pos, v in enumerate(keyed_alpha):
        grid_perm[v] = pos
    
    for grid_w in [5, 6]:
        for pnum in target_pages:
            vals = pages_vals[pnum]
            
            # Test a set of periods
            best_ic = 0
            best_period = 0
            for period in range(2, 51):
                dec = bifid_decrypt_keyed(vals, period, grid_perm, grid_w)
                ic = ioc(dec)
                if ic > best_ic:
                    best_ic = ic
                    best_period = period
            
            if best_ic > 1.3:
                dec = bifid_decrypt_keyed(vals, best_period, grid_perm, grid_w)
                lat = to_text(dec, 50)
                best_results.append((best_ic, pnum, kw_text, grid_w, best_period, lat))

best_results.sort(key=lambda x: -x[0])
print(f"\n=== Top 30 bifid results (IoC > 1.3) ===")
for ic, pnum, kw, gw, per, lat in best_results[:30]:
    print(f"  P{pnum} BIFID({kw}, {gw}x?, per={per}): IoC={ic:.4f}")
    print(f"    {lat}")

if not best_results:
    print("  No results above IoC 1.3")
    # Show best anyway
    print("\n=== Best below 1.3 ===")
    all_best = []
    for kw_text in keywords[:10]:
        kw_gp = keyword_to_gp(kw_text)
        keyed_alpha = make_keyed_alphabet(kw_gp)
        grid_perm = [0]*29
        for pos, v in enumerate(keyed_alpha):
            grid_perm[v] = pos
        for grid_w in [6]:
            for pnum in [32]:
                vals = pages_vals[pnum]
                for period in [2, 5, 11, 17, 23, 37, 47]:
                    dec = bifid_decrypt_keyed(vals, period, grid_perm, grid_w)
                    ic = ioc(dec)
                    all_best.append((ic, pnum, kw_text, grid_w, period))
    all_best.sort(key=lambda x: -x[0])
    for ic, pnum, kw, gw, per in all_best[:10]:
        print(f"  P{pnum} BIFID({kw}, {gw}x?, per={per}): IoC={ic:.4f}")

# ============ TRIFID CIPHER ============
print("\n=== TRIFID CIPHER (3x3x3+2 = 29) ===")
# Trifid with 3x3x4 cube (3*3*4=36, > 29) or 3x10 (30 >= 29)
# Actually for mod-29 alphabet, we need a 3D arrangement
# Use layer=v//9, row=(v%9)//3, col=v%3 for a 4x3x3 scheme (4*3*3=36)
# Or layer=v//10, row=(v%10)//3.33... - tricky with 29

# Simpler: use base-3 representation as close to balanced as possible
# 3^3 = 27 < 29, so we need 3^3 + 2 extra. Use 3 layers of 3x3 + 2 overflow
def trifid_decrypt(ciphertext, period):
    """Trifid with 3 coordinates: v = 9*a + 3*b + c for v < 27, special for 27,28"""
    result = []
    for block_start in range(0, len(ciphertext), period):
        block = ciphertext[block_start:block_start+period]
        blen = len(block)
        
        # Split into 3 coordinates
        coord1 = []  # layer
        coord2 = []  # row  
        coord3 = []  # col
        for v in block:
            if v < 27:
                coord1.append(v // 9)
                coord2.append((v % 9) // 3)
                coord3.append(v % 3)
            elif v == 27:
                coord1.append(0)
                coord2.append(0)
                coord3.append(0)  # map to 0 same as F? Or special
            else:  # v == 28
                coord1.append(0)
                coord2.append(0)
                coord3.append(1)
        
        # Trifid recombination: concatenate all coords, then re-group by 3
        all_coords = coord1 + coord2 + coord3  # 3*blen values
        
        for i in range(blen):
            a = all_coords[i*3]
            b = all_coords[i*3 + 1]
            c = all_coords[i*3 + 2]
            v = a * 9 + b * 3 + c
            if v >= 29:
                v = v % 29
            result.append(v)
    
    return result

for pnum in target_pages:
    vals = pages_vals[pnum]
    best_ic = 0
    best_per = 0
    for period in range(2, 51):
        dec = trifid_decrypt(vals, period)
        ic = ioc(dec)
        if ic > best_ic:
            best_ic = ic
            best_per = period
    if best_ic > 1.15:
        dec = trifid_decrypt(vals, best_per)
        lat = to_text(dec, 50)
        print(f"  P{pnum} TRIFID(per={best_per}): IoC={best_ic:.4f}, {lat}")

# ============ ADFGVX-style cipher ============
print("\n=== ADFGVX-style fractionation + columnar transposition ===")
# ADFGVX uses a 6x6 grid with columnar transposition
# For 29-letter alphabet, use 5x6=30 grid
# The concept: encrypt by substituting each letter with its row-col pair,
# then columnar-transpose the expanded text, then re-pair

# This is essentially bifid but with transposition instead of period-based recombination
# Let's try: standard grid, but columnar transpose with keyword

def adfgvx_decrypt(ciphertext, key_perm, grid_w=6):
    """
    ADFGVX-style: 
    1. Reverse columnar transposition on the fractionated text
    2. Read pairs to get row,col
    3. Look up in grid
    """
    n = len(ciphertext)
    frac_len = 2 * n  # each original letter produces 2 fractionated symbols
    ncols = len(key_perm)
    nrows = frac_len // ncols
    extra = frac_len % ncols
    
    # We'd need to know the exact fractionated text to reverse this
    # This is complex. Skip for now.
    pass

# Instead, let me do something simpler: check digram IoC of LP ciphertext
print("\n=== Digram frequency analysis ===")
for pnum in [25, 32, 44, 50]:
    vals = pages_vals[pnum]
    # Digram IoC
    digrams = [(vals[i], vals[i+1]) for i in range(len(vals)-1)]
    c = Counter(digrams)
    n = len(digrams)
    dig_ioc = sum(f*(f-1) for f in c.values()) / (n*(n-1)) * (29*29)
    print(f"  P{pnum}: digram IoC = {dig_ioc:.4f} (expected random: 1.0, English: ~1.7)")
    
    # Also check: reversed digrams
    rev_digrams = [(vals[i+1], vals[i]) for i in range(len(vals)-1)]
    rev_c = Counter(rev_digrams)
    rev_ioc = sum(f*(f-1) for f in rev_c.values()) / (n*(n-1)) * (29*29)
    
    # Skip-1 digrams
    skip_digrams = [(vals[i], vals[i+2]) for i in range(len(vals)-2)]
    skip_c = Counter(skip_digrams)
    skip_n = len(skip_digrams)
    skip_ioc = sum(f*(f-1) for f in skip_c.values()) / (skip_n*(skip_n-1)) * (29*29)
    print(f"    skip-1 digram IoC = {skip_ioc:.4f}")

# ============ Check why bifid gives elevated IoC ============
print("\n=== Bifid on LP pages CONFIRMATION ===")
def bifid_decrypt_standard(ciphertext, period, grid_w=6):
    result = []
    for block_start in range(0, len(ciphertext), period):
        block = ciphertext[block_start:block_start+period]
        blen = len(block)
        rows = [v // grid_w for v in block]
        cols = [v % grid_w for v in block]
        coords = rows + cols
        for i in range(blen):
            r = coords[i]
            c = coords[i + blen]
            v = r * grid_w + c
            if v >= 29:
                v = v % 29
            result.append(v)
    return result

for pnum in [25, 32, 44, 50, 40]:
    vals = pages_vals[pnum]
    print(f"\n  P{pnum} ({len(vals)} runes):")
    for period in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 37, 41, 47]:
        for gw in [5, 6]:
            dec = bifid_decrypt_standard(vals, period, gw)
            ic = ioc(dec)
            if ic > 1.15:
                print(f"    gw={gw} per={period:2d}: IoC={ic:.4f}")

# Also test: what's the MONOGRAM IoC of the ciphertext itself?
print("\n=== Ciphertext IoC confirmation ===")
for pnum in [25, 32, 44, 50, 40]:
    vals = pages_vals[pnum]
    ic = ioc(vals)
    print(f"  P{pnum}: monogram IoC = {ic:.4f}")

print("\nDone.")
