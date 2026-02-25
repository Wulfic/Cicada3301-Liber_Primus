#!/usr/bin/env python3
"""
P20 'Rearranging the Prime Numbers' - systematic transposition attack.
P19 says: "REARRANGING THE PRIME NUMBERS WILL SHOW A PATH TO THE DEOR"

Try various interpretations:
1. Read P20 at prime positions, rearranged by prime properties
2. Use primes as a transposition key
3. Column transposition with prime-length columns
4. Route cipher through prime-dimensioned grids
"""

GP = {
    '\u16A0':0, '\u16A2':1, '\u16A6':2, '\u16A9':3, '\u16B1':4, '\u16B3':5, '\u16B7':6, '\u16B9':7,
    '\u16BB':8, '\u16BE':9, '\u16C1':10, '\u16C2':11, '\u16C4':11,
    '\u16C7':12, '\u16C8':13, '\u16C9':14, '\u16CB':15, '\u16CF':16, '\u16D2':17, '\u16D6':18,
    '\u16D7':19, '\u16DA':20, '\u16DD':21, '\u16DF':22, '\u16DE':23, '\u16AA':24, '\u16AB':25,
    '\u16A3':26, '\u16E1':27, '\u16E0':28
}
IDX2LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

with open('LiberPrimus/pages/page_20/runes.txt', 'r', encoding='utf-8') as f:
    text = f.read()
p20_vals = [GP[ch] for ch in text if ch in GP]
n = len(p20_vals)
print(f"P20: {n} runes")

from collections import Counter
import math

def sieve_primes(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit+1, i):
                is_prime[j] = False
    return [i for i in range(limit+1) if is_prime[i]]

def ioc(vals, alpha_size=29):
    c = Counter(vals)
    n = len(vals)
    if n < 2:
        return 0
    return sum(f*(f-1) for f in c.values()) / (n*(n-1)) * alpha_size

def to_text(vals):
    return ''.join(IDX2LAT[v] for v in vals)

all_primes = sieve_primes(10000)
prime_set = set(all_primes)

# === APPROACH 1: Prime-indexed positions, various rearrangements ===
print("\n=== APPROACH 1: Extract at prime positions, rearrange ===")
prime_pos = [p for p in all_primes if p < n]
prime_runes = [p20_vals[p] for p in prime_pos]
print(f"  {len(prime_runes)} runes at prime positions")
print(f"  IoC: {ioc(prime_runes):.4f}")

# Sort by: prime value, rune value, etc.
# a) Sort runes by their prime position (already done - that's the original order)
# b) Reverse order
rev_runes = prime_runes[::-1]
print(f"  Reversed: IoC={ioc(rev_runes):.4f}")

# === APPROACH 2: Use primes as write/read order for transposition ===
print("\n=== APPROACH 2: Columnar transposition with prime column widths ===")
prime_widths = [p for p in all_primes if p <= 50 and n % p != 0][:20]
for width in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
    rows = math.ceil(n / width)
    # Write row-by-row, read column-by-column
    grid = [None] * (rows * width)
    for i in range(n):
        grid[i] = p20_vals[i]
    
    col_read = []
    for c in range(width):
        for r in range(rows):
            idx = r * width + c
            if idx < n and grid[idx] is not None:
                col_read.append(grid[idx])
    
    ic = ioc(col_read)
    if ic > 1.15:
        print(f"  width={width}: IoC={ic:.4f}, start={to_text(col_read[:20])}")

# === APPROACH 3: Rearrange using prime permutation ===
# "Rearranging the prime numbers" - what if the PRIMES themselves are the permutation?
# E.g., position 0 -> prime[0]=2, position 1 -> prime[1]=3, etc.
print("\n=== APPROACH 3: Prime permutation transposition ===")
# Write at consecutive positions, read at prime-mapped positions
# Or vice versa
for desc, read_fn in [
    ("write sequential, read at prime[i] mod n", lambda i: all_primes[i] % n),
    ("write at prime[i] mod n, read sequential", None),
]:
    if read_fn:
        try:
            result = [p20_vals[read_fn(i)] for i in range(n)]
            ic = ioc(result)
            if ic > 1.1:
                print(f"  {desc}: IoC={ic:.4f}, start={to_text(result[:25])}")
        except:
            pass
    else:
        buf = [0] * n
        for i in range(n):
            buf[all_primes[i] % n] = p20_vals[i]
        ic = ioc(buf)
        if ic > 1.1:
            print(f"  {desc}: IoC={ic:.4f}, start={to_text(buf[:25])}")

# === APPROACH 4: Interleave prime and non-prime position runes ===
print("\n=== APPROACH 4: Various interleaving of prime/non-prime positions ===")
prime_pos_set = set(prime_pos)
non_prime_runes = [p20_vals[i] for i in range(n) if i not in prime_pos_set]
print(f"  Prime position runes: {len(prime_runes)}, Non-prime: {len(non_prime_runes)}")

# Interleave: alternate prime, non-prime
interleaved = []
pi, ni = 0, 0
for i in range(n):
    if i % 2 == 0 and pi < len(prime_runes):
        interleaved.append(prime_runes[pi])
        pi += 1
    elif ni < len(non_prime_runes):
        interleaved.append(non_prime_runes[ni])
        ni += 1
ic = ioc(interleaved)
print(f"  Interleved (alt P/NP): IoC={ic:.4f}")

# === APPROACH 5: 812 = 4 × 203 = 4 × 7 × 29 ===
print("\n=== APPROACH 5: Grid dimensions of 812 ===")
print(f"  812 = 2^2 × 7 × 29")
print(f"  Factors: ", end="")
factors = []
for i in range(2, n+1):
    if n % i == 0:
        factors.append(i)
print(factors[:20])

# Try each factor pair as grid dimensions
for width in factors:
    if width > n // 2:
        break
    height = n // width
    
    # Column-major read (write row-major, read column-major)
    col_read = []
    for c in range(width):
        for r in range(height):
            col_read.append(p20_vals[r * width + c])
    ic = ioc(col_read)
    if ic > 1.15:
        print(f"  Grid {height}x{width} col-read: IoC={ic:.4f}, start={to_text(col_read[:25])}")
    
    # Also try with Deor cipher first, then transposition
    # Skip this for now since basic Deor didn't work

# === APPROACH 6: Use the DEOR poem rune GP values to create a transposition key ===
# "Show a path TO THE DEOR" - the path (reading order) is determined by the Deor text
print("\n=== APPROACH 6: Deor-based transposition key ===")
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}
special = {'\u00de': 2, '\u00fe': 2, '\u00d0': 23, '\u00f0': 23, '\u00e6': 25}

with open('Analysis/Reference_Docs/deor_poem.txt', 'r', encoding='utf-8') as f:
    deor_text = f.read()

# OE section only
oe_section = deor_text.split('DEOR POEM (MODERN ENGLISH')[0].replace('DEOR POEM (OLD ENGLISH)', '').strip()
deor_vals = []
for ch in oe_section:
    if ch in special:
        deor_vals.append(special[ch])
    elif ch.upper() in ENG2GP:
        deor_vals.append(ENG2GP[ch.upper()])

# Use first 812 Deor values as transposition key (rank ordering)
# But we only have 1106 Deor values
deor_key = deor_vals[:n]
print(f"  Deor key values (first {len(deor_key)})")

# Create ranking: sort by deor value, breaking ties by position
ranked = sorted(range(len(deor_key)), key=lambda i: (deor_key[i], i))
# Read P20 in ranked order
trans_result = [p20_vals[ranked[i]] for i in range(len(deor_key))]
ic = ioc(trans_result)
print(f"  Deor-ranked read: IoC={ic:.4f}, start={to_text(trans_result[:25])}")

# Inverse: write P20, read in Deor-rank order
inv_ranked = [0] * len(deor_key)
for i, r in enumerate(ranked):
    inv_ranked[r] = i
trans_result2 = [p20_vals[inv_ranked[i]] for i in range(len(deor_key))]
ic2 = ioc(trans_result2)
print(f"  Inverse Deor-rank: IoC={ic2:.4f}, start={to_text(trans_result2[:25])}")

# === APPROACH 7: Combined Vigenere + transposition ===
# What if P20 = Vigenere(transposed plaintext)?
# Or transposed(Vigenere(plaintext))?
# Try undoing Vigenere with DEOR key, then columnar transposition
print("\n=== APPROACH 7: Vigenere(DEOR) then columnar transposition ===")
deor_key_short = [23, 18, 3, 4]  # D=23, E=18, O=3, R=4
for mode, fn in [('SUB', lambda c,k: (c-k)%29), ('ADD', lambda c,k: (c+k)%29), ('BEAU', lambda c,k: (k-c)%29)]:
    decoded = [fn(p20_vals[i], deor_key_short[i%4]) for i in range(n)]
    # Try columnar with key factors of 812
    for width in [4, 7, 14, 28, 29, 58, 116, 203]:
        if n % width != 0:
            continue
        height = n // width
        col_read = []
        for c in range(width):
            for r in range(height):
                col_read.append(decoded[r * width + c])
        ic = ioc(col_read)
        if ic > 1.2:
            print(f"  {mode}+col(w={width}): IoC={ic:.4f}, start={to_text(col_read[:25])}")

print("\nDone.")
