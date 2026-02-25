#!/usr/bin/env python3
"""
1. Verify bifid IoC is an artifact by testing on random data
2. Test missing primes 73-1223 as running key
3. Test Euler totient of missing primes as running key
4. More creative approaches
"""

import os, random, glob
from collections import Counter
from math import gcd

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

def to_text(vals, limit=60):
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

# ============== TEST 1: Bifid on random data ==============
print("=== TEST 1: Bifid IoC on RANDOM data ===")
def bifid_decrypt(ciphertext, period, grid_w=6):
    """Standard bifid decryption with given grid width."""
    grid_h = (29 + grid_w - 1) // grid_w  # ceiling
    result = []
    for block_start in range(0, len(ciphertext), period):
        block = ciphertext[block_start:block_start+period]
        blen = len(block)
        # Extract rows and cols
        rows = [v // grid_w for v in block]
        cols = [v % grid_w for v in block]
        # Interleave: first half rows, second half cols
        coords = rows + cols
        # Re-pair as (coords[0], coords[blen]), (coords[1], coords[blen+1]), ...
        for i in range(blen):
            r = coords[i]
            c = coords[i + blen]
            v = r * grid_w + c
            if v >= 29:
                v = v % 29
            result.append(v)
    return result

# Test on 10 random sequences
for trial in range(10):
    random_data = [random.randint(0, 28) for _ in range(1900)]
    for period in [2, 5, 11, 17]:
        dec = bifid_decrypt(random_data, period, 6)
        ic = ioc(dec)
        if trial == 0:
            print(f"  Random trial {trial}, period={period}: IoC={ic:.4f}")

# Average over many trials
print("  Average over 100 trials:")
for period in [2, 5, 11, 17, 37]:
    ics = []
    for _ in range(100):
        random_data = [random.randint(0, 28) for _ in range(1900)]
        dec = bifid_decrypt(random_data, period, 6)
        ics.append(ioc(dec))
    avg = sum(ics)/len(ics)
    print(f"  period={period}: avg IoC={avg:.4f} (min={min(ics):.4f}, max={max(ics):.4f})")

# ============== TEST 2: Missing primes as key ==============
print("\n=== TEST 2: Missing primes 73-1223 as key ===")
def sieve_primes(n):
    is_prime = [True] * (n+1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5)+1):
        if is_prime[i]:
            for j in range(i*i, n+1, i):
                is_prime[j] = False
    return [i for i in range(2, n+1) if is_prime[i]]

all_primes = sieve_primes(2000)
# First 20 primes: 2,3,5,...,71 (indices 0-19)
first_20 = all_primes[:20]
# Missing primes: 73 to 1223
missing_primes = [p for p in all_primes if 73 <= p <= 1223]
print(f"  First 20 primes: {first_20}")
print(f"  Missing primes count: {len(missing_primes)}")
print(f"  Missing primes (first 20): {missing_primes[:20]}")

# Key from missing primes mod 29
mp_key = [p % 29 for p in missing_primes]
print(f"  Key (mod 29, first 20): {mp_key[:20]}")

# Also try totient of missing primes
from sympy import totient as euler_totient
mp_totient_key = [euler_totient(p) % 29 for p in missing_primes]
print(f"  Totient key (first 20): {mp_totient_key[:20]}")

# Also try: the primes themselves as direct values (p - 2 mod 29, since prime[0]=2)
mp_shifted_key = [(p - 2) % 29 for p in missing_primes]

for pnum in sorted(pages_vals.keys()):
    if not (18 <= pnum <= 54) or len(pages_vals[pnum]) < 100:
        continue
    vals = pages_vals[pnum]
    
    for key_name, key_vals in [("mod29", mp_key), ("totient", mp_totient_key), ("shifted", mp_shifted_key)]:
        for mode_name, fn in [('SUB', lambda c,k: (c-k)%29), ('ADD', lambda c,k: (c+k)%29), ('BEAU', lambda c,k: (k-c)%29)]:
            result = [fn(vals[i], key_vals[i % len(key_vals)]) for i in range(len(vals))]
            ic = ioc(result)
            if ic > 1.2:
                lat = to_text(result, 40)
                print(f"  P{pnum} {mode_name}({key_name}): IoC={ic:.4f}, start={lat}")
    
    # Also try: key = cumulated missing primes mod 29
    cum_key = []
    s = 0
    for p in missing_primes:
        s += p
        cum_key.append(s % 29)
    for mode_name, fn in [('SUB', lambda c,k: (c-k)%29), ('ADD', lambda c,k: (c+k)%29), ('BEAU', lambda c,k: (k-c)%29)]:
        result = [fn(vals[i], cum_key[i % len(cum_key)]) for i in range(len(vals))]
        ic = ioc(result)
        if ic > 1.2:
            lat = to_text(result, 40)
            print(f"  P{pnum} {mode_name}(cumulated): IoC={ic:.4f}, start={lat}")

# ============== TEST 3: Prime index as key ==============
print("\n=== TEST 3: nth prime as key ===")
# Use prime(i+1) mod 29 as the key for position i (starting from prime[0]=2 or prime[1]=3)
prime_keys = {
    "prime_from_0": [all_primes[i] % 29 for i in range(min(2000, len(all_primes)))],
    "prime_from_20": [all_primes[i+20] % 29 for i in range(min(180, len(all_primes)-20))],
    "prime_from_1": [all_primes[i+1] % 29 for i in range(min(1999, len(all_primes)-1))],
}

for pnum in sorted(pages_vals.keys()):
    if not (18 <= pnum <= 54) or len(pages_vals[pnum]) < 100:
        continue
    vals = pages_vals[pnum]
    
    for key_name, key_vals in prime_keys.items():
        keylen = len(key_vals)
        for mode_name, fn in [('SUB', lambda c,k: (c-k)%29), ('ADD', lambda c,k: (c+k)%29), ('BEAU', lambda c,k: (k-c)%29)]:
            result = [fn(vals[i], key_vals[i % keylen]) for i in range(len(vals))]
            ic = ioc(result)
            if ic > 1.2:
                lat = to_text(result, 40)
                print(f"  P{pnum} {mode_name}({key_name}): IoC={ic:.4f}, start={lat}")

# ============== TEST 4: F-skip with various keys ==============
print("\n=== TEST 4: F-skip with known keys ===")
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}

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

fskip_keys = {
    "DIVINITY": keyword_to_gp("DIVINITY"),
    "CIRCUMFERENCE": keyword_to_gp("CIRCUMFERENCE"),
    "PRIMES": keyword_to_gp("PRIMES"),
    "CONSUMPTION": keyword_to_gp("CONSUMPTION"),
    "WELCOME": keyword_to_gp("WELCOME"),
    "FIRFUMFERENFE": keyword_to_gp("FIRFUMFERENFE"),
}

for pnum in sorted(pages_vals.keys()):
    if not (18 <= pnum <= 54) or len(pages_vals[pnum]) < 100:
        continue
    vals = pages_vals[pnum]
    
    for key_name, key in fskip_keys.items():
        if not key: continue
        for mode_name, mode_fn in [('SUB', lambda c,k: (c-k)%29), ('ADD', lambda c,k: (c+k)%29), ('BEAU', lambda c,k: (k-c)%29)]:
            # F-skip: when cipher rune = 0 (F), output F and don't advance key
            result = []
            ki = 0
            for v in vals:
                if v == 0:
                    result.append(0)  # F passes through
                else:
                    result.append(mode_fn(v, key[ki % len(key)]))
                    ki += 1
            ic = ioc(result)
            if ic > 1.2:
                lat = to_text(result, 40)
                print(f"  P{pnum} F-skip {mode_name}({key_name}): IoC={ic:.4f}, start={lat}")

# ============== TEST 5: Use page number as key derivation ==============
print("\n=== TEST 5: Page-number-derived keys ===")
for pnum in sorted(pages_vals.keys()):
    if not (18 <= pnum <= 54) or len(pages_vals[pnum]) < 100:
        continue
    vals = pages_vals[pnum]
    
    # Try: key = page number repeated
    for mode_name, fn in [('SUB', lambda c,k: (c-k)%29), ('ADD', lambda c,k: (c+k)%29), ('BEAU', lambda c,k: (k-c)%29)]:
        result = [fn(v, pnum % 29) for v in vals]
        ic = ioc(result)
        if ic > 1.2:
            print(f"  P{pnum} {mode_name}(shift={pnum%29}): IoC={ic:.4f}")
    
    # Key from digits of page number
    digits = [int(d) for d in str(pnum)]
    for mode_name, fn in [('SUB', lambda c,k: (c-k)%29), ('ADD', lambda c,k: (c+k)%29), ('BEAU', lambda c,k: (k-c)%29)]:
        result = [fn(vals[i], digits[i % len(digits)]) for i in range(len(vals))]
        ic = ioc(result)
        if ic > 1.2:
            print(f"  P{pnum} {mode_name}(digits={digits}): IoC={ic:.4f}")
    
    # Key = prime(page_number) mod 29
    pprime = all_primes[pnum] if pnum < len(all_primes) else 0
    for mode_name, fn in [('SUB', lambda c,k: (c-k)%29), ('ADD', lambda c,k: (c+k)%29), ('BEAU', lambda c,k: (k-c)%29)]:
        result = [fn(v, pprime % 29) for v in vals]
        ic = ioc(result)
        if ic > 1.2:
            print(f"  P{pnum} {mode_name}(prime[{pnum}]={pprime}%29={pprime%29}): IoC={ic:.4f}")

print("\nDone.")
