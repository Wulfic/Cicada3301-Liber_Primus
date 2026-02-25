"""
Comprehensive transposition attack on P20's non-prime shift-16 stream.
646 = 2 × 17 × 19 (all prime factors!)
P19 hint: "REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR"
"""

import os
import re
from collections import Counter
from itertools import permutations
import math

# The shift-16 stream (646 chars) - read from file
with open('p20_non_prime_shift16_result.txt', 'r', encoding='utf-8') as f:
    stream = f.read().strip()

print(f"Stream length: {len(stream)}")
print(f"646 = 2 × 17 × 19")
print()

# Common English bigrams/trigrams for scoring
COMMON_WORDS = ['THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','HER','WAS','ONE','OUR',
    'OUT','HIS','HAS','ITS','HAD','HOW','MAN','NEW','NOW','OLD','SEE','WAY',
    'WHO','DID','GET','HIM','LET','SAY','SHE','TOO','USE','WITH','THAT','THIS',
    'WILL','EACH','FROM','HAVE','BEEN','CALL','COME','MAKE','THAN','THEM','THEN',
    'THEY','WHAT','WHEN','YOUR','SAID','WERE','INTO','SOME','TIME','VERY','WHICH',
    'WOULD','ABOUT','COULD','OTHER','THEIR','THERE','SHALL','THESE','THOSE','THROUGH',
    'WITHIN','WITHOUT','BEFORE','AFTER','BETWEEN','UNDER','UNTIL','WHILE','EVERY',
    'LIGHT','SHADOW','TRUTH','PATH','KNOW','SEEK','FIND','WISDOM','DIVINE','SACRED']

# Old English words (Deor-related)
OE_WORDS = ['EODE','SEFA','MONNE','THONE','THES','THAES','WAES','MAEG','SCEALL',
    'OFEREODE','THISSES','THAET','THAEL','DEOR','WELUND','BEADOHILDE','MAETHHILDE',
    'GEAT','THEODRIC','EORMANRIC','HIM','MID','THET','THE','THAT','WAS','HEART',
    'MIND','SPIRIT','WENT','PATH','GLORY','SORROW','COMFORT','OVERCOME']

def score_text(text):
    """Score English-likeness of text."""
    score = 0
    t = text.upper()
    
    # Word matches
    for w in COMMON_WORDS:
        if w in t:
            score += len(w) * 3
    for w in OE_WORDS:
        if w in t:
            score += len(w) * 5
    
    # Common bigrams
    bigrams = ['TH','HE','IN','EN','AN','RE','ER','ON','NT','ES','ST','TE','ED','IS',
               'IT','NG','OF','OR','HA','TO','AT','EA','ND']
    for bg in bigrams:
        score += t.count(bg) * 2
    
    # Common trigrams
    trigrams = ['THE','AND','ING','HER','HAT','HIS','THA','ERE','FOR','ENT','ION',
                'TER','WAS','HEN','ATE','ALL','HAD','VER']
    for tg in trigrams:
        score += t.count(tg) * 3
    
    # Penalize rare patterns
    rare = ['XZ','QJ','ZX','JQ','WW','XX','ZZ','QQ']
    for r in rare:
        score -= t.count(r) * 5
    
    return score

def ioc(text):
    freq = Counter(text.upper())
    n = len(text)
    if n <= 1: return 0
    return sum(f*(f-1) for f in freq.values()) / (n*(n-1)) * 26  # Using 26 for Latin alphabet

# Score the original
orig_score = score_text(stream)
print(f"Original score: {orig_score}")
print(f"Original IoC (26-letter): {ioc(stream):.4f}")
print()

best_results = []

def try_transposition(name, result_text):
    sc = score_text(result_text)
    if sc > orig_score * 1.2:  # At least 20% better than original
        best_results.append((sc, name, result_text[:200]))
    return sc

# ============================================================
# 1. COLUMNAR TRANSPOSITION - various widths
# ============================================================
print("=== COLUMNAR TRANSPOSITION (natural read order) ===")

for ncols in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 34, 37, 38]:
    nrows = math.ceil(len(stream) / ncols)
    
    # Write into grid row by row, read column by column
    grid = [''] * ncols
    for i, c in enumerate(stream):
        grid[i % ncols] += c
    result_col_first = ''.join(grid)
    
    # Write into grid column by column, read row by row
    nrows2 = math.ceil(len(stream) / ncols)
    grid2 = [''] * nrows2
    full_cols = len(stream) % ncols if len(stream) % ncols != 0 else ncols
    idx = 0
    cols_data = []
    for c in range(ncols):
        col_len = nrows2 if c < full_cols else nrows2 - 1
        cols_data.append(stream[idx:idx+col_len])
        idx += col_len
    
    result_row_read = []
    for r in range(nrows2):
        for c in range(ncols):
            if r < len(cols_data[c]):
                result_row_read.append(cols_data[c][r])
    result_row_read = ''.join(result_row_read)
    
    sc1 = try_transposition(f"Col-first ncols={ncols}", result_col_first)
    sc2 = try_transposition(f"Row-read ncols={ncols}", result_row_read)
    
    if ncols in [17, 19, 34, 38]:
        print(f"  ncols={ncols}: col-first score={sc1}, row-read score={sc2}")
        print(f"    Col-first: {result_col_first[:100]}")
        print(f"    Row-read:  {result_row_read[:100]}")
        print()

# ============================================================
# 2. ROUTE CIPHERS on 17×38 and 19×34 grids
# ============================================================
print("=== ROUTE CIPHERS ===")

def spiral_read(grid, nrows, ncols):
    """Read grid in clockwise spiral from top-left."""
    result = []
    top, bottom, left, right = 0, nrows - 1, 0, ncols - 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            if top < nrows and c < ncols and grid[top][c]:
                result.append(grid[top][c])
        top += 1
        for r in range(top, bottom + 1):
            if r < nrows and right < ncols and grid[r][right]:
                result.append(grid[r][right])
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                if bottom < nrows and c < ncols and grid[bottom][c]:
                    result.append(grid[bottom][c])
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                if r < nrows and left < ncols and grid[r][left]:
                    result.append(grid[r][left])
            left += 1
    return ''.join(result)

def snake_read(grid, nrows, ncols):
    """Read grid in boustrophedon (alternating direction per row)."""
    result = []
    for r in range(nrows):
        if r % 2 == 0:
            for c in range(ncols):
                if c < len(grid[r]):
                    result.append(grid[r][c])
        else:
            for c in range(ncols - 1, -1, -1):
                if c < len(grid[r]):
                    result.append(grid[r][c])
    return ''.join(result)

def diagonal_read(grid, nrows, ncols):
    """Read grid diagonally."""
    result = []
    for d in range(nrows + ncols - 1):
        for r in range(max(0, d - ncols + 1), min(nrows, d + 1)):
            c = d - r
            if c < ncols and c < len(grid[r]):
                result.append(grid[r][c])
    return ''.join(result)

for nrows, ncols in [(17, 38), (38, 17), (19, 34), (34, 19), (2, 323), (323, 2)]:
    if nrows * ncols < len(stream):
        continue
    
    # Fill grid row by row
    grid = []
    for r in range(nrows):
        row = []
        for c in range(ncols):
            idx = r * ncols + c
            if idx < len(stream):
                row.append(stream[idx])
        grid.append(row)
    
    # Column-first read
    col_result = []
    for c in range(ncols):
        for r in range(nrows):
            if c < len(grid[r]):
                col_result.append(grid[r][c])
    col_result = ''.join(col_result)
    
    spiral = spiral_read(grid, nrows, ncols)
    snake = snake_read(grid, nrows, ncols)
    diag = diagonal_read(grid, nrows, ncols)
    
    sc_col = try_transposition(f"Route col {nrows}x{ncols}", col_result)
    sc_spiral = try_transposition(f"Route spiral {nrows}x{ncols}", spiral)
    sc_snake = try_transposition(f"Route snake {nrows}x{ncols}", snake)
    sc_diag = try_transposition(f"Route diag {nrows}x{ncols}", diag)
    
    print(f"  Grid {nrows}×{ncols}: col={sc_col}, spiral={sc_spiral}, snake={sc_snake}, diag={sc_diag}")
    
    # Also try: fill grid column by column, read row by row
    grid2 = [[''] * ncols for _ in range(nrows)]
    for i, ch in enumerate(stream):
        c = i // nrows
        r = i % nrows
        if c < ncols:
            grid2[r][c] = ch
    
    row_result = ''
    for r in range(nrows):
        row_result += ''.join(grid2[r])
    # Already tried this above as "row-read"

print()

# ============================================================
# 3. KEYED COLUMNAR with prime-sequence keys
# ============================================================
print("=== KEYED COLUMNAR TRANSPOSITION ===")

def keyed_columnar_decrypt(ciphertext, key_order):
    """Decrypt columnar transposition given column read order."""
    ncols = len(key_order)
    nrows = math.ceil(len(ciphertext) / ncols)
    
    # Calculate column lengths
    extra = len(ciphertext) % ncols
    if extra == 0:
        extra = ncols
    
    col_lens = []
    for c in range(ncols):
        col_lens.append(nrows if c < extra else nrows - 1)
    
    # Split ciphertext into columns by key order
    cols = [''] * ncols
    idx = 0
    for k in range(ncols):
        # Which column position does the k-th read column go to?
        col_idx = key_order[k]
        clen = col_lens[col_idx]
        cols[col_idx] = ciphertext[idx:idx+clen]
        idx += clen
    
    # Read row by row
    result = []
    for r in range(nrows):
        for c in range(ncols):
            if r < len(cols[c]):
                result.append(cols[c][r])
    return ''.join(result)

# Try keyed columnar with small prime widths and all permutations
for ncols in [2, 3, 4, 5]:
    # Use first ncols primes as potential key ordering
    small_primes = [2, 3, 5, 7, 11, 13][:ncols]
    # Rank them to get column order
    for perm in permutations(range(ncols)):
        result = keyed_columnar_decrypt(stream, list(perm))
        sc = try_transposition(f"Keyed-col w={ncols} key={perm}", result)

# Try with widths 17 and 19 using first few permutations of prime ordering
for ncols in [17, 19]:
    # Generate key from first ncols primes sorted
    primes_for_key = []
    p = 2
    while len(primes_for_key) < ncols:
        if all(p % d != 0 for d in range(2, int(p**0.5)+1)):
            primes_for_key.append(p)
        p += 1
    
    # Natural order (0,1,2,...) - already tested as basic columnar
    # Try: key based on prime values mod ncols
    key_mod = [p % ncols for p in primes_for_key]
    # This might have collisions, use ranking instead
    key_ranked = sorted(range(ncols), key=lambda i: primes_for_key[i] % (ncols + 1))
    
    result = keyed_columnar_decrypt(stream, key_ranked)
    sc = try_transposition(f"Keyed-col w={ncols} prime-ranked", result)
    print(f"  Width {ncols}, prime-ranked key: score={sc}")
    
    # Reverse order
    result_rev = keyed_columnar_decrypt(stream, list(range(ncols-1, -1, -1)))
    sc_rev = try_transposition(f"Keyed-col w={ncols} reverse", result_rev)
    print(f"  Width {ncols}, reverse key: score={sc_rev}")

print()

# ============================================================
# 4. RAIL FENCE / ZIGZAG
# ============================================================
print("=== RAIL FENCE CIPHER ===")

def rail_fence_decrypt(ciphertext, rails):
    n = len(ciphertext)
    pattern = list(range(rails)) + list(range(rails-2, 0, -1))
    cycle = len(pattern)
    
    # Assign each position to a rail
    rail_assignment = [pattern[i % cycle] for i in range(n)]
    
    # Count chars per rail
    rail_counts = [0] * rails
    for r in rail_assignment:
        rail_counts[r] += 1
    
    # Split ciphertext into rails
    rail_strings = []
    idx = 0
    for r in range(rails):
        rail_strings.append(ciphertext[idx:idx+rail_counts[r]])
        idx += rail_counts[r]
    
    # Read back
    rail_indices = [0] * rails
    result = []
    for i in range(n):
        r = rail_assignment[i]
        result.append(rail_strings[r][rail_indices[r]])
        rail_indices[r] += 1
    
    return ''.join(result)

for rails in range(2, 30):
    result = rail_fence_decrypt(stream, rails)
    sc = try_transposition(f"Rail fence {rails} rails", result)
    if sc > orig_score * 1.1:
        print(f"  {rails} rails: score={sc}")

print()

# ============================================================
# 5. SKIP / DECIMATION CIPHER
# ============================================================
print("=== SKIP/DECIMATION CIPHER ===")

for skip in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
    if math.gcd(skip, len(stream)) != 1:
        continue  # Skip must be coprime with length for full coverage
    
    result = []
    pos = 0
    for _ in range(len(stream)):
        result.append(stream[pos])
        pos = (pos + skip) % len(stream)
    result = ''.join(result)
    
    sc = try_transposition(f"Skip-{skip}", result)
    if sc > orig_score * 1.1:
        print(f"  Skip {skip}: score={sc}")

# Also try: read every prime-th position  
print()
print("=== PRIME POSITION READS ===")

def sieve_primes(n):
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n+1, i):
                sieve[j] = False
    return [i for i in range(2, n+1) if sieve[i]]

primes = sieve_primes(700)
# Read characters at prime positions
prime_chars = [stream[p-1] for p in primes if p <= len(stream)]
prime_text = ''.join(prime_chars)
sc = score_text(prime_text)
print(f"  Prime positions ({len(prime_chars)} chars): score={sc}")
print(f"    Text: {prime_text[:100]}")

# Non-prime positions
non_prime_set = set(primes)
non_prime_chars = [stream[i] for i in range(len(stream)) if (i+1) not in non_prime_set]
non_prime_text = ''.join(non_prime_chars)
sc2 = score_text(non_prime_text)
print(f"  Non-prime positions ({len(non_prime_chars)} chars): score={sc2}")
print(f"    Text: {non_prime_text[:100]}")

print()

# ============================================================
# 6. PRIME-VALUE-BASED REARRANGEMENT
# ============================================================
print("=== PRIME-VALUE REARRANGEMENT ===")

# GP values for shifted text
GP_LATIN_TO_IDX = {'F':0,'U':1,'TH':2,'O':3,'R':4,'C':5,'G':6,'W':7,'H':8,'N':9,
    'I':10,'J':11,'EO':12,'P':13,'X':14,'S':15,'T':16,'B':17,'E':18,'M':19,
    'L':20,'NG':21,'OE':22,'D':23,'A':24,'AE':25,'Y':26,'IA':27,'EA':28}
GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]

# Parse the shifted stream back to GP indices
# Need to handle digraphs carefully
def text_to_gp_indices(text):
    """Parse GP Latin transcription to indices."""
    indices = []
    i = 0
    t = text.upper()
    while i < len(t):
        matched = False
        # Try 2-char digraphs first
        for dg in ['TH','NG','EO','OE','AE','IA','EA']:
            if t[i:i+len(dg)] == dg:
                indices.append(GP_LATIN_TO_IDX[dg])
                i += len(dg)
                matched = True
                break
        if not matched:
            ch = t[i]
            if ch in GP_LATIN_TO_IDX:
                indices.append(GP_LATIN_TO_IDX[ch])
            i += 1
    return indices

gp_indices = text_to_gp_indices(stream)
print(f"Stream parsed to {len(gp_indices)} GP indices (from {len(stream)} chars)")

# Sort by associated prime value
sorted_by_prime = sorted(range(len(gp_indices)), key=lambda i: (GP_PRIMES[gp_indices[i]], i))
rearranged = ''.join(stream[i] for i in sorted_by_prime[:len(stream)])
# This won't work directly because text_to_gp_indices changes length

# Instead, work with the raw 646 non-prime GP index values
# Load the original P20 data

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C4':11,'\u16C7':12,'\u16C8':13,'\u16C9':14,
    '\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,'\u16D7':19,'\u16DA':20,'\u16DD':21,
    '\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,'\u16A3':26,'\u16E1':27,'\u16E0':28
}
LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

with open('LiberPrimus/pages/page_20/runes.txt', 'r', encoding='utf-8') as f:
    p20_all = [GP[c] for c in f.read() if c in GP]

print(f"P20 full: {len(p20_all)} runes")

# Extract non-prime positions
primes_set = set(sieve_primes(len(p20_all) + 1))
non_prime_indices_raw = [p20_all[i] for i in range(len(p20_all)) if (i+1) not in primes_set]
print(f"Non-prime runes: {len(non_prime_indices_raw)}")

# Apply shift 16
shifted = [(v + 16) % 29 for v in non_prime_indices_raw]
shifted_text = ''.join(LATIN[v] for v in shifted)
print(f"Shifted text length: {len(shifted_text)} chars")

# Verify it matches
print(f"Match with file: {shifted_text[:50] == stream[:50]}")
print()

# Sort the 646 shifted indices by their GP prime value
sorted_by_prime_idx = sorted(range(len(shifted)), key=lambda i: (GP_PRIMES[shifted[i]], i))
rearranged_vals = [shifted[i] for i in sorted_by_prime_idx]
rearranged_text = ''.join(LATIN[v] for v in rearranged_vals)
sc = score_text(rearranged_text)
print(f"Sorted by prime value: score={sc}")
print(f"  Text: {rearranged_text[:150]}")

# Sort by prime value, then read in groups
print()
print("Grouped by GP prime value:")
for val in range(29):
    positions = [i for i in range(len(shifted)) if shifted[i] == val]
    if positions:
        print(f"  {LATIN[val]:3s} (prime={GP_PRIMES[val]:3d}): {len(positions)} occurrences at positions {positions[:10]}{'...' if len(positions) > 10 else ''}")

print()

# ============================================================
# 7. INTERLEAVE PRIME / NON-PRIME STREAMS
# ============================================================
print("=== INTERLEAVE PRIME AND NON-PRIME STREAMS ===")

# Get prime-position runes (166)
prime_position_indices = [p20_all[i] for i in range(len(p20_all)) if (i+1) in primes_set]
print(f"Prime-position runes: {len(prime_position_indices)}")

# These were decoded with Beaufort+Deor. Load the decoded text from file
with open('Analysis/Outputs/deor_stream_beaufort.txt', 'r', encoding='utf-8') as f:
    decoded_prime_text = f.read().strip()
print(f"Decoded prime stream: {decoded_prime_text[:60]}...")

# Interleave the two streams back into 812-position text
full_decoded = [None] * len(p20_all)
prime_idx = 0
non_prime_idx = 0
for i in range(len(p20_all)):
    if (i+1) in primes_set:
        # Use decoded prime text character
        if prime_idx < len(decoded_prime_text):
            full_decoded[i] = decoded_prime_text[prime_idx]
        prime_idx += 1
    else:
        # Use shifted non-prime text character
        if non_prime_idx < len(shifted_text):
            full_decoded[i] = shifted_text[non_prime_idx]
        non_prime_idx += 1

interleaved = ''.join(c if c else '?' for c in full_decoded)
sc_inter = score_text(interleaved)
print(f"Interleaved (prime decoded + non-prime shifted16): score={sc_inter}")
print(f"  First 200 chars: {interleaved[:200]}")
print()

# ============================================================
# 8. PRINT TOP RESULTS
# ============================================================
print("=" * 60)
print("TOP TRANSPOSITION RESULTS")
print("=" * 60)
best_results.sort(reverse=True)
for sc, name, text in best_results[:20]:
    print(f"  Score {sc:4d}: {name}")
    print(f"           {text[:120]}")
    print()
