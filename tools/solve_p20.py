#!/usr/bin/env python3
"""
Deep solver for Page 20's non-prime stream (646 runes).
After Caesar 16, IoC = 2.01 (English-like frequencies, scrambled order).
P19 hint: "REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR K"
"""
import os
import sys
from collections import Counter
from pathlib import Path
import math

BASE = Path(__file__).resolve().parent.parent

RUNE_TO_IDX = {
    '\u16A0': 0, '\u16A2': 1, '\u16A6': 2, '\u16A9': 3, '\u16B1': 4,
    '\u16B3': 5, '\u16B7': 6, '\u16B9': 7, '\u16BB': 8, '\u16BE': 9,
    '\u16C1': 10, '\u16C4': 11, '\u16C7': 12, '\u16C8': 13, '\u16C9': 14,
    '\u16CB': 15, '\u16CF': 16, '\u16D2': 17, '\u16D6': 18, '\u16D7': 19,
    '\u16DA': 20, '\u16DD': 21, '\u16DF': 22, '\u16DE': 23, '\u16AA': 24,
    '\u16AB': 25, '\u16A3': 26, '\u16E1': 27, '\u16E0': 28,
}
IDX_TO_LETTER = [
    'F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S',
    'T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA'
]
GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i*i <= n:
        if n%i == 0 or n%(i+2) == 0: return False
        i += 6
    return True

def compute_ioc(indices):
    n = len(indices)
    if n < 2: return 0
    counts = Counter(indices)
    return 29 * sum(c*(c-1) for c in counts.values()) / (n*(n-1))

def to_rg(indices):
    return ''.join(IDX_TO_LETTER[i] for i in indices)

# Load P20
with open(BASE / 'pages' / 'page_20' / 'runes.txt', 'r', encoding='utf-8') as f:
    p20_text = f.read()

# Extract all runes with their positions
all_runes = []
pos = 0
for ch in p20_text:
    if ch in RUNE_TO_IDX:
        all_runes.append((pos, RUNE_TO_IDX[ch]))
        pos += 1
    # Skip separators (they're not runes)

total = len(all_runes)
print(f"Total runes in P20: {total}")

# Separate prime-indexed and non-prime-indexed (0-based)
prime_stream = [(i, idx) for i, idx in all_runes if is_prime(i)]
nonprime_stream = [(i, idx) for i, idx in all_runes if not is_prime(i)]
print(f"Prime-position runes: {len(prime_stream)}")
print(f"Non-prime-position runes: {len(nonprime_stream)}")

# Also try value-based separation: rune VALUES that are prime
prime_value_stream = [(i, idx) for i, idx in all_runes if GP_PRIMES[idx] in [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109] and is_prime(GP_PRIMES[idx])]
# Actually ALL GP values are prime, so this is all runes. The tracker says:
# "Prime-valued letters: TH, O, C, W, J, P, B, M, D" (but ALL are prime)
# Let me re-read: "Rune VALUES (prime vs non-prime gematria values)"
# Actually the GP indices are NOT the values. The INDICES are 0-28, and the VALUES are the primes.
# Maybe "prime value" means the INDEX is prime? Indices 2,3,5,7,11,13,17,19,23 are prime.
prime_idx_runes = [(i, idx) for i, idx in all_runes if is_prime(idx)]
nonprime_idx_runes = [(i, idx) for i, idx in all_runes if not is_prime(idx)]
print(f"\nPrime-INDEX runes (idx in [2,3,5,7,11,13,17,19,23]): {len(prime_idx_runes)}")
print(f"Non-prime-INDEX runes: {len(nonprime_idx_runes)}")

# Extract just the cipher indices for non-prime POSITION stream
np_cipher = [idx for _, idx in nonprime_stream]

# Apply Caesar shifts and check IoC
print("\n=== Caesar shifts on non-prime POSITION stream ===")
best_shift = 0
best_ioc = 0
for shift in range(29):
    shifted = [(x - shift) % 29 for x in np_cipher]
    ioc = compute_ioc(shifted)
    if ioc > 1.5:
        text = to_rg(shifted)
        print(f"  Caesar {shift}: IoC={ioc:.4f} text={text[:80]}")
    if ioc > best_ioc:
        best_ioc = ioc
        best_shift = shift

print(f"\nBest Caesar shift: {best_shift} with IoC={best_ioc:.4f}")

# Apply best Caesar to get the "correct letters, wrong order" text
np_plain = [(x - best_shift) % 29 for x in np_cipher]
np_text = to_rg(np_plain)
n = len(np_plain)
print(f"\nNon-prime stream after Caesar {best_shift}: {n} runes")
print(f"Text: {np_text[:200]}")

# Also preserve word structure
ki = 0
words = []
cur_word = []
for ch in p20_text:
    if ch in RUNE_TO_IDX:
        if not is_prime(ki):
            cur_word.append((np_plain[sum(1 for j in range(ki) if not is_prime(j))] if sum(1 for j in range(ki) if not is_prime(j)) < len(np_plain) else 0))
        ki += 1
    elif ch in '\u2022':  # bullet separator
        if cur_word:
            words.append(cur_word[:])
            cur_word = []

# Score function
COMMON_WORDS = {'THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','HER',
    'WAS','ONE','OUR','OUT','DAY','HAS','HIS','HOW','ITS','MAY','NEW','NOW',
    'OLD','SEE','WAY','WHO','DID','THIS','THAT','WITH','HAVE','FROM','THEY',
    'BEEN','SAID','EACH','WILL','INTO','THAN','THEM','THEN','WHAT','WHEN',
    'LIKE','LONG','LOOK','MANY','SOME','TIME','VERY','YOUR','KNOW','JUST',
    'COME','MADE','FIND','BACK','ONLY','SELF','AN','TO','IN','IS','IT','AT',
    'BE','BY','DO','GO','IF','ME','MY','NO','ON','OR','SO','UP','WE','OF',
    'A','I','BEING','TRUTH','WITHIN','SACRED','WISDOM','FOLLOW','INSTRUCTION',
    'PILGRIMAGE','DIVINITY','INSTAR','CIRCUMFERENCE','CONSUMPTION'}

def score_text(text):
    """Score text for readable English words."""
    words = text.split()
    score = 0
    for w in words:
        if w in COMMON_WORDS:
            score += len(w) * 15
        elif w.replace('C','K') in COMMON_WORDS or w.replace('U','V') in COMMON_WORDS:
            score += len(w) * 12
    return score

# === TRANSPOSITION ATTEMPTS ===
print("\n=== Transposition attempts on non-prime stream ===")

results = []

# 1. Read at prime positions within the stream
primes_in_range = [p for p in range(n) if is_prime(p)]
prime_read = [np_plain[p] for p in primes_in_range if p < n]
if prime_read:
    text = to_rg(prime_read)
    ioc = compute_ioc(prime_read)
    results.append(('prime_positions', ioc, text[:120]))

# 2. Reverse reading
rev = list(reversed(np_plain))
text = to_rg(rev)
ioc = compute_ioc(rev)  # Same IoC, different order
results.append(('reversed', ioc, text[:120]))

# 3. Columnar transposition with various widths
for width in [2,3,5,7,11,13,17,19,23,29,31,34,37,38,41,43,47]:
    if width >= n: continue
    nrows = math.ceil(n / width)
    # Read by columns
    col_read = []
    for col in range(width):
        for row in range(nrows):
            idx = row * width + col
            if idx < n:
                col_read.append(np_plain[idx])
    text = to_rg(col_read)
    ioc = compute_ioc(col_read)  # Same letters, same IoC
    # Score the word-separated version
    # Actually need to check if this produces readable text
    # Quick check: look for common English trigrams
    tri_score = 0
    for i in range(len(text) - 2):
        tri = text[i:i+3]
        if tri in {'THE','AND','FOR','ING','ION','THA','ENT','HER','WAS','HIS',
                    'ALL','BUT','ARE','NOT','YOU','CAN','HAS','HIS','OUR','OUT'}:
            tri_score += 1
    if tri_score > 5:
        results.append((f'columnar_w{width}', ioc, f'trigrams={tri_score}: {text[:100]}'))

# 4. Diagonal reading with various widths
for width in [17, 19, 23, 29, 31, 34, 37, 38]:
    if width >= n: continue
    nrows = math.ceil(n / width)
    diag_read = []
    for d in range(width + nrows - 1):
        for row in range(nrows):
            col = d - row
            if 0 <= col < width:
                idx = row * width + col
                if idx < n:
                    diag_read.append(np_plain[idx])
    text = to_rg(diag_read)
    tri_score = 0
    for i in range(len(text) - 2):
        tri = text[i:i+3]
        if tri in {'THE','AND','FOR','ING','ION','THA','ENT','HER','WAS','HIS',
                    'ALL','BUT','ARE','NOT','YOU','CAN'}:
            tri_score += 1
    if tri_score > 5:
        results.append((f'diagonal_w{width}', compute_ioc(diag_read), f'trigrams={tri_score}: {text[:100]}'))

# 5. Spiral reading
for width in [17, 19, 23, 25, 26, 29, 34]:
    height = math.ceil(n / width)
    grid = []
    for r in range(height):
        row = []
        for c in range(width):
            idx = r * width + c
            if idx < n:
                row.append(np_plain[idx])
            else:
                row.append(0)
        grid.append(row)
    
    # Clockwise spiral
    spiral = []
    top, bottom, left, right = 0, height-1, 0, width-1
    while top <= bottom and left <= right:
        for c in range(left, right+1):
            if len(spiral) < n: spiral.append(grid[top][c])
        top += 1
        for r in range(top, bottom+1):
            if len(spiral) < n: spiral.append(grid[r][right])
        right -= 1
        if top <= bottom:
            for c in range(right, left-1, -1):
                if len(spiral) < n: spiral.append(grid[bottom][c])
            bottom -= 1
        if left <= right:
            for r in range(bottom, top-1, -1):
                if len(spiral) < n: spiral.append(grid[r][left])
            left += 1
    
    text = to_rg(spiral[:n])
    tri_score = 0
    for i in range(len(text) - 2):
        tri = text[i:i+3]
        if tri in {'THE','AND','FOR','ING','ION','THA','ENT','HER','WAS','HIS',
                    'ALL','BUT','ARE','NOT','YOU','CAN'}:
            tri_score += 1
    if tri_score > 5:
        results.append((f'spiral_w{width}', compute_ioc(spiral[:n]), f'trigrams={tri_score}: {text[:100]}'))

# 6. Sort positions by their rune VALUE (Gematria prime value)
# and read in that order
gp_sorted = sorted(range(n), key=lambda i: GP_PRIMES[np_plain[i]])
gp_read = [np_plain[i] for i in gp_sorted]
text = to_rg(gp_read)
results.append(('gp_value_sorted', compute_ioc(gp_read), text[:120]))

# 7. Read every k-th character (skip cipher)
for k in [2, 3, 5, 7, 11, 13]:
    for start in range(k):
        skip_read = [np_plain[i] for i in range(start, n, k)]
        if len(skip_read) > 20:
            text = to_rg(skip_read)
            tri_score = 0
            for i in range(len(text) - 2):
                tri = text[i:i+3]
                if tri in {'THE','AND','FOR','ING','ION','THA','ENT','HER','WAS','HIS',
                            'ALL','BUT','ARE','NOT','YOU','CAN'}:
                    tri_score += 1
            if tri_score > 3:
                results.append((f'every_{k}th_start{start}', compute_ioc(skip_read), f'trigrams={tri_score}: {text[:100]}'))

# 8. Fibonacci-indexed positions
fibs = [0, 1]
while fibs[-1] < n:
    fibs.append(fibs[-1] + fibs[-2])
fibs = [f for f in fibs if f < n]
fib_read = [np_plain[f] for f in fibs]
text = to_rg(fib_read)
results.append(('fibonacci_positions', compute_ioc(fib_read), text[:120]))

# 9. Route cipher: write in rows, read in column order defined by keyword
for keyword_name, keyword_vals in [
    ('CABAL', [5,24,17,24,20]),
    ('DIVINITY', [23,10,1,10,9,10,16,26]),
    ('DEOR', [23,18,3,4]),
    ('SHADOWS', [15,8,24,23,3,7,15]),
]:
    klen = len(keyword_vals)
    nrows = math.ceil(n / klen)
    # Determine column order from keyword
    order = sorted(range(klen), key=lambda x: keyword_vals[x])
    
    route_read = []
    for col in order:
        for row in range(nrows):
            idx = row * klen + col
            if idx < n:
                route_read.append(np_plain[idx])
    
    text = to_rg(route_read)
    tri_score = 0
    for i in range(len(text) - 2):
        tri = text[i:i+3]
        if tri in {'THE','AND','FOR','ING','ION','THA','ENT','HER','WAS','HIS',
                    'ALL','BUT','ARE','NOT','YOU','CAN'}:
            tri_score += 1
    results.append((f'route_{keyword_name}', compute_ioc(route_read), f'trigrams={tri_score}: {text[:100]}'))

# 10. Deor-keyed transposition
with open(BASE / 'data' / 'deor_poem.txt', 'r', encoding='utf-8', errors='ignore') as f:
    deor_text = f.read()
deor_ints = []
for ch in deor_text.lower():
    if ch.isalpha():
        deor_ints.append(ord(ch) - ord('a'))

# Use Deor characters as transposition key offsets
if len(deor_ints) >= n:
    deor_key = deor_ints[:n]
    # Sort positions by Deor key value (ascending)
    deor_order = sorted(range(n), key=lambda i: (deor_key[i], i))
    deor_read = [np_plain[i] for i in deor_order]
    text = to_rg(deor_read)
    tri_score = 0
    for i in range(len(text) - 2):
        tri = text[i:i+3]
        if tri in {'THE','AND','FOR','ING','ION','THA','ENT','HER','WAS','HIS',
                    'ALL','BUT','ARE','NOT','YOU','CAN'}:
            tri_score += 1
    results.append((f'deor_transposition', compute_ioc(deor_read), f'trigrams={tri_score}: {text[:100]}'))

# Print all results sorted by trigram count
print("\n=== ALL TRANSPOSITION RESULTS ===")
results.sort(key=lambda x: -len(x[2]))  # Sort by info richness
for name, ioc, info in results[:30]:
    print(f"  {name}: IoC={ioc:.4f} {info}")

# === SECOND APPROACH: Use P20 non-prime positions but with VALUE-based prime check ===
print("\n\n=== VALUE-BASED SEPARATION ===")
# Rune at position i: if its GP INDEX is prime (2,3,5,7,11,13,17,19,23), it's "prime-valued"
# Non-prime indices: 0,1,4,6,8,9,10,12,14,15,16,18,20,21,22,24,25,26,27,28

all_indices = [idx for _, idx in all_runes]
prime_val_positions = [i for i in range(total) if is_prime(all_indices[i])]
nonprime_val_positions = [i for i in range(total) if not is_prime(all_indices[i])]
print(f"Prime-valued runes: {len(prime_val_positions)}")
print(f"Non-prime-valued runes: {len(nonprime_val_positions)}")

# Extract and analyze prime-valued stream
pv_stream = [all_indices[i] for i in prime_val_positions]
pv_ioc = compute_ioc(pv_stream)
print(f"Prime-valued stream IoC: {pv_ioc:.4f}")

# Apply Caesar shifts
for shift in range(29):
    shifted = [(x - shift) % 29 for x in pv_stream]
    ioc = compute_ioc(shifted)
    if ioc > 1.5:
        text = to_rg(shifted)
        print(f"  Caesar {shift} on prime-valued: IoC={ioc:.4f} text={text[:80]}")

npv_stream = [all_indices[i] for i in nonprime_val_positions]
npv_ioc = compute_ioc(npv_stream)
print(f"\nNon-prime-valued stream IoC: {npv_ioc:.4f}")

for shift in range(29):
    shifted = [(x - shift) % 29 for x in npv_stream]
    ioc = compute_ioc(shifted)
    if ioc > 1.5:
        text = to_rg(shifted)
        print(f"  Caesar {shift} on non-prime-valued: IoC={ioc:.4f} text={text[:80]}")
