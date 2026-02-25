#!/usr/bin/env python3
"""
Comprehensive cipher survey on large unsolved pages.
Testing self-key, combined operations, and cross-page patterns.
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

def ioc(vals, alpha=29):
    c = Counter(vals)
    n = len(vals)
    if n < 2: return 0
    return sum(f*(f-1) for f in c.values()) / (n*(n-1)) * alpha

def to_text(vals, limit=30):
    return ''.join(IDX2LAT[v] for v in vals[:limit])

# Load pages
pages = {}
for page_dir in sorted(glob.glob('LiberPrimus/pages/page_*/runes.txt')):
    pnum = int(page_dir.replace('\\','/').split('page_')[1].split('/')[0])
    with open(page_dir, 'r', encoding='utf-8') as f:
        text = f.read()
    vals = [GP[ch] for ch in text if ch in GP]
    if vals:
        pages[pnum] = vals

# Focus on large unsolved pages
targets = [(pnum, vals) for pnum, vals in pages.items() if 18 <= pnum <= 54 and len(vals) > 200]
targets.sort(key=lambda x: -len(x[1]))
print("Target pages:")
for pnum, vals in targets[:10]:
    print(f"  P{pnum}: {len(vals)} runes, IoC={ioc(vals):.3f}")

# === TEST 1: Self-key ciphers ===
# plain[i] = f(cipher[i], cipher[i-k]) for various k and operations
print("\n=== TEST 1: Self-key ciphers ===")
for pnum, vals in targets[:5]:
    best_ic = 0
    best_desc = ""
    for lag in range(1, 30):
        for mode, fn in [
            (f'SUB lag={lag}', lambda a,b: (a-b)%29),
            (f'ADD lag={lag}', lambda a,b: (a+b)%29),
            (f'BEAU lag={lag}', lambda a,b: (b-a)%29),
        ]:
            result = [fn(vals[i], vals[i-lag]) for i in range(lag, len(vals))]
            ic = ioc(result)
            if ic > best_ic:
                best_ic = ic
                best_desc = mode
                best_result = result
        # Also try: plain[i] = (cipher[i] + i) % 29 (position-dependent)
    
    if best_ic > 1.1:
        print(f"  P{pnum}: Best self-key = {best_desc}, IoC={best_ic:.4f}")
        print(f"    Start: {to_text(best_result)}")

# === TEST 2: Position-dependent ciphers ===
# plain[i] = (cipher[i] + f(i)) % 29 for various f(i)
print("\n=== TEST 2: Position-dependent ciphers ===")
import math

def sieve_primes(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit+1, i):
                is_prime[j] = False
    return [i for i in range(limit+1) if is_prime[i]]

all_primes = sieve_primes(10000)

for pnum, vals in targets[:3]:
    n = len(vals)
    print(f"\n  P{pnum} ({n} runes):")
    
    tests = [
        ("i % 29", lambda i: i % 29),
        ("i^2 % 29", lambda i: (i*i) % 29),
        ("fib(i) % 29", None),  # will compute separately
        ("prime[i] % 29", lambda i: all_primes[i] % 29 if i < len(all_primes) else 0),
        ("totient(prime[i]) % 29", lambda i: (all_primes[i]-1) % 29 if i < len(all_primes) else 0),
        ("i*(i+1)/2 % 29", lambda i: (i*(i+1)//2) % 29),
    ]
    
    # Fibonacci
    fibs = [0, 1]
    for _ in range(n + 10):
        fibs.append(fibs[-1] + fibs[-2])
    
    for desc, fn in tests:
        if desc == "fib(i) % 29":
            fn = lambda i: fibs[i] % 29
        
        for mode_name, mode_fn in [('SUB', lambda c,k: (c-k)%29), ('ADD', lambda c,k: (c+k)%29), ('BEAU', lambda c,k: (k-c)%29)]:
            result = [mode_fn(vals[i], fn(i)) for i in range(n)]
            ic = ioc(result)
            if ic > 1.15:
                print(f"    {mode_name}({desc}): IoC={ic:.4f}, start={to_text(result)}")

# === TEST 3: Two-page combined operations ===
# What if page A XOR/SUB/ADD with page B gives plaintext?
print("\n=== TEST 3: Cross-page operations ===")
# For pages of same length
same_length_pairs = []
for p1, v1 in pages.items():
    for p2, v2 in pages.items():
        if p1 < p2 and 18 <= p1 <= 54 and 18 <= p2 <= 54:
            if len(v1) == len(v2) and len(v1) > 100:
                same_length_pairs.append((p1, p2))

print(f"Same-length page pairs: {len(same_length_pairs)}")
for p1, p2 in same_length_pairs:
    v1, v2 = pages[p1], pages[p2]
    for mode, fn in [('SUB', lambda a,b: (a-b)%29), ('ADD', lambda a,b: (a+b)%29)]:
        result = [fn(v1[i], v2[i]) for i in range(len(v1))]
        ic = ioc(result)
        if ic > 1.3:
            print(f"  P{p1} {mode} P{p2}: IoC={ic:.4f}")

# For ALL unsolved pages, try combining consecutive pages
print("\n  Consecutive page operations:")
sorted_pages = sorted([(p, v) for p, v in pages.items() if 18 <= p <= 54], key=lambda x: x[0])
for idx in range(len(sorted_pages) - 1):
    p1, v1 = sorted_pages[idx]
    p2, v2 = sorted_pages[idx + 1]
    min_len = min(len(v1), len(v2))
    if min_len < 100:
        continue
    for mode, fn in [('SUB', lambda a,b: (a-b)%29), ('ADD', lambda a,b: (a+b)%29)]:
        result = [fn(v1[i], v2[i]) for i in range(min_len)]
        ic = ioc(result)
        if ic > 1.2:
            print(f"  P{p1} {mode} P{p2}: IoC={ic:.4f}, start={to_text(result)}")

# === TEST 4: Bifid cipher with natural GP ordering ===
print("\n=== TEST 4: Bifid cipher (5x6 grid, standard GP order) ===")
# Grid: value v -> row = v//6, col = v%6
# For period p, bifid decryption:
# 1. Take p ciphertext values, convert to (row, col) pairs
# 2. Flatten pairs to sequence of coordinates
# 3. Split: first p coords = rows, last p coords = cols
# 4. Pair up (row_i, col_i) -> plaintext value = row_i * 6 + col_i

def bifid_decrypt(cipher_vals, period, grid_width=6):
    result = []
    for start in range(0, len(cipher_vals) - period + 1, period):
        block = cipher_vals[start:start+period]
        if len(block) < period:
            break
        # Convert to coordinates
        coords = []
        for v in block:
            coords.append((v // grid_width, v % grid_width))
        # Flatten: all rows then all cols
        flat = [c[0] for c in coords] + [c[1] for c in coords]
        # Re-pair: (flat[0], flat[1]), (flat[2], flat[3]), ...
        for i in range(0, 2*period, 2):
            val = flat[i] * grid_width + flat[i+1]
            if val < 29:
                result.append(val)
            else:
                result.append(0)  # overflow
    return result

for pnum, vals in targets[:5]:
    for period in [2, 3, 4, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        for grid_w in [5, 6]:
            result = bifid_decrypt(vals, period, grid_w)
            if result:
                ic = ioc(result)
                if ic > 1.2:
                    print(f"  P{pnum} period={period} grid={29//grid_w}x{grid_w}: IoC={ic:.4f}, start={to_text(result)}")

# === TEST 5: Multiplicative cipher ===
print("\n=== TEST 5: Multiplicative ciphers ===")
# plain = (cipher * k) % 29 or plain = (cipher * k + s) % 29
# 29 is prime, so all k from 1-28 have multiplicative inverses
for pnum, vals in targets[:3]:
    for k in range(1, 29):
        for s in range(29):
            result = [(v * k + s) % 29 for v in vals]
            ic = ioc(result)
            if ic > 1.5:
                print(f"  P{pnum} affine k={k} s={s}: IoC={ic:.4f}")

print("\nDone.")
