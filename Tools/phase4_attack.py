#!/usr/bin/env python3
"""
Phase 4 Attack — Novel keystream hypotheses for Liber Primus unsolved pages.

Sections:
1. Totient of ALL integers (not just primes): φ(n) for n=1,2,3,...
2. Möbius function keystream: μ(n) mod 29
3. Carmichael function λ(n) mod 29
4. SHA-256 hash from P17 as keystream bytes
5. LFSR with Cicada-specific taps (167, 761, 3301)
6. Prime gaps as keystream
7. Composite number totients (skip primes)
8. Inverse totient: use the PLAINTEXT GP primes to lookup key
9. Totient with F-skip on unsolved pages
10. Interleaved prime sequences (odd-indexed, even-indexed primes)
"""

import os, sys, math, collections, hashlib

# ─── Gematria Primus ──────────────────────────────────────────────
RUNE_TO_INDEX = {
    '\u16A0':0,  '\u16A2':1,  '\u16A6':2,  '\u16A9':3,  '\u16B1':4,
    '\u16B3':5,  '\u16B7':6,  '\u16B9':7,  '\u16BB':8,  '\u16BE':9,
    '\u16C1':10, '\u16C2':11, '\u16C4':11, '\u16C7':12, '\u16C8':13,
    '\u16C9':14, '\u16CB':15, '\u16CF':16, '\u16D2':17, '\u16D6':18,
    '\u16D7':19, '\u16DA':20, '\u16DD':21, '\u16DF':22, '\u16DE':23,
    '\u16AA':24, '\u16AB':25, '\u16A3':26, '\u16E1':27, '\u16E0':28,
}
GP = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
      'Z','S','T','B','E','M','L','NG','D','A','AE','Y','IA','EA']

def to_text(indices):
    return ''.join(GP[i] for i in indices)

def load_page_runes(page_num):
    base = os.path.join(os.path.dirname(__file__), '..', 'LiberPrimus', 'pages')
    path = os.path.join(base, f'page_{page_num:02d}', 'runes.txt')
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read().strip()
    return [RUNE_TO_INDEX[ch] for ch in text if ch in RUNE_TO_INDEX]

def calculate_ioc(indices):
    if len(indices) < 2: return 0.0
    freq = collections.Counter(indices)
    n = len(indices)
    return sum(c*(c-1) for c in freq.values()) / (n*(n-1)) * 29

def score_english(indices):
    SIMPLE = 'FUTORHCGWHNIJPXZSTBEMLNDAAYWE'
    text = ''.join(SIMPLE[i % 29] for i in indices).upper()
    common = ['THE','AND','ING','HER','HAT','HIS','THA','ERE','FOR',
              'ENT','ION','TER','WAS','YOU','ITH','VER','ALL','WIT','THI','TIO']
    return sum(text.count(tri) for tri in common)

# ─── Number theory helpers ────────────────────────────────────────
def sieve_primes(limit):
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, limit + 1, i):
                sieve[j] = False
    return sieve, [i for i in range(2, limit + 1) if sieve[i]]

def euler_totient_range(limit):
    """Compute φ(n) for all n up to limit using sieve method."""
    phi = list(range(limit + 1))  # phi[n] = n initially
    for p in range(2, limit + 1):
        if phi[p] == p:  # p is prime
            for j in range(p, limit + 1, p):
                phi[j] -= phi[j] // p
    return phi

def mobius_range(limit):
    """Compute μ(n) for n up to limit."""
    mu = [0] * (limit + 1)
    mu[1] = 1
    is_prime = [True] * (limit + 1)
    primes = []
    for i in range(2, limit + 1):
        if is_prime[i]:
            primes.append(i)
            mu[i] = -1
        for p in primes:
            if i * p > limit:
                break
            is_prime[i * p] = False
            if i % p == 0:
                mu[i * p] = 0
                break
            else:
                mu[i * p] = -mu[i]
    return mu

def carmichael_range(limit, phi_arr, sieve_arr, primes):
    """Compute λ(n) for n up to limit."""
    from math import gcd
    lam = [0] * (limit + 1)
    lam[1] = 1
    # For prime powers: λ(p^k) = p^(k-1)(p-1) for odd p, special case for 2
    # For general n: λ(n) = lcm of λ for all prime power factors
    for n in range(2, limit + 1):
        if sieve_arr[n]:  # n is prime
            lam[n] = n - 1
        else:
            # Factor n and compute lcm of lambda of prime powers
            temp = n
            result = 1
            for p in primes:
                if p * p > temp:
                    break
                if temp % p == 0:
                    pk = 1
                    while temp % p == 0:
                        pk *= p
                        temp //= p
                    # lambda(p^k) = p^(k-1)*(p-1) for odd p
                    if p == 2 and pk >= 8:
                        lp = pk // 4
                    elif p == 2 and pk == 4:
                        lp = 2
                    elif p == 2 and pk == 2:
                        lp = 1
                    else:
                        lp = pk * (p - 1) // p
                    result = result * lp // gcd(result, lp)
            if temp > 1:
                lp = temp - 1
                result = result * lp // gcd(result, lp)
            lam[n] = result
    return lam

LIMIT = 25000
print("Computing number theory functions...")
PHI = euler_totient_range(LIMIT)
MU = mobius_range(LIMIT)
SIEVE, PRIMES = sieve_primes(LIMIT)
# Skip Carmichael for now (complex), test it if others show promise

# ─── Load pages ───────────────────────────────────────────────────
FOCUS = [20, 25, 32, 17, 40, 44, 50]
pages = {}
for pn in range(17, 55):
    idx = load_page_runes(pn)
    if idx and len(idx) > 30:
        pages[pn] = idx

print(f"Loaded {len(pages)} pages")
print("=" * 80)

# ═══════════════════════════════════════════════════════════════════
# SECTION 1: TOTIENT OF ALL INTEGERS
# ═══════════════════════════════════════════════════════════════════
print("\nSECTION 1: φ(n) for n=1,2,3,... as keystream")
print("Unlike prime-only totient, this uses ALL natural numbers")

for pn in FOCUS:
    if pn not in pages: continue
    ci = pages[pn]
    n = len(ci)
    best_ioc = 0
    best_off = 0
    for offset in range(0, min(15001, LIMIT - n), 100):
        key = [PHI[i + offset + 1] % 29 for i in range(n)]  # +1 because PHI[0]=0
        plain = [(ci[i] - key[i]) % 29 for i in range(n)]
        ic = calculate_ioc(plain)
        if ic > best_ioc:
            best_ioc = ic
            best_off = offset
    flag = " ***" if best_ioc > 1.3 else ""
    print(f"  P{pn:02d} ({n}): best IoC={best_ioc:.4f} at offset={best_off}{flag}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 2: MÖBIUS FUNCTION KEYSTREAM
# ═══════════════════════════════════════════════════════════════════
print("\nSECTION 2: μ(n) as keystream component")
print("μ(n) ∈ {-1, 0, 1}. Testing: key = μ(prime[i+offset]) * factor mod 29")

for pn in FOCUS[:3]:
    if pn not in pages: continue
    ci = pages[pn]
    n = len(ci)
    best_ioc = 0
    best_info = ""
    
    # Method 1: key = |μ(n+offset)| * φ(n+offset) mod 29 (squarefree filter on totient)
    for offset in range(1, min(10001, LIMIT - n)):
        key = [abs(MU[i + offset]) * PHI[i + offset] % 29 for i in range(n)]
        plain = [(ci[i] - key[i]) % 29 for i in range(n)]
        ic = calculate_ioc(plain)
        if ic > best_ioc:
            best_ioc = ic
            best_info = f"|μ|*φ offset={offset}"
    
    flag = " ***" if best_ioc > 1.3 else ""
    print(f"  P{pn:02d} ({n}): {best_ioc:.4f} [{best_info}]{flag}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 3: SHA-256 HASH FROM P17 AS KEYSTREAM
# ═══════════════════════════════════════════════════════════════════
print("\nSECTION 3: SHA-256 hash-derived keystream")
hash_str = "36367763AB73783C7AF284446C59466B4CD653239A311CB7116D4618DEE09A8425893DC7500B464FDAF1672D7BEF5E891C6E2274568926A49FB4F45132C2A8B4"

# Convert hex string to bytes, use as keystream
hash_bytes = bytes.fromhex(hash_str)
print(f"  Hash: {len(hash_bytes)} bytes = {len(hash_str)} hex chars")

# Method 1: Direct bytes mod 29
for pn in FOCUS:
    if pn not in pages: continue
    ci = pages[pn]
    n = len(ci)
    
    # Extend hash by repeated hashing
    extended = bytearray(hash_bytes)
    while len(extended) < n + 1000:
        extended.extend(hashlib.sha256(extended[-64:]).digest())
    
    best_ioc = 0
    best_info = ""
    for start in range(0, min(len(extended) - n, 200)):
        key = [extended[i + start] % 29 for i in range(n)]
        for mode in ['SUB', 'ADD']:
            if mode == 'SUB':
                plain = [(ci[i] - key[i]) % 29 for i in range(n)]
            else:
                plain = [(ci[i] + key[i]) % 29 for i in range(n)]
            ic = calculate_ioc(plain)
            if ic > best_ioc:
                best_ioc = ic
                best_info = f"start={start} {mode}"
    
    flag = " ***" if best_ioc > 1.3 else ""
    print(f"  P{pn:02d}: {best_ioc:.4f} [{best_info}]{flag}")

# Method 2: Use hash hex digits as GP indices (0-F -> 0-15)
hex_digits = [int(c, 16) for c in hash_str]
print(f"  Hex digits: {len(hex_digits)}")
for pn in FOCUS[:3]:
    if pn not in pages: continue
    ci = pages[pn]
    n = min(len(ci), len(hex_digits))
    for mode in ['SUB', 'ADD']:
        if mode == 'SUB':
            plain = [(ci[i] - hex_digits[i]) % 29 for i in range(n)]
        else:
            plain = [(ci[i] + hex_digits[i]) % 29 for i in range(n)]
        ic = calculate_ioc(plain)
        if ic > 1.2:
            print(f"  P{pn:02d} hex {mode}: IoC={ic:.4f}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 4: LFSR WITH CICADA-SPECIFIC TAPS
# ═══════════════════════════════════════════════════════════════════
print("\nSECTION 4: LFSR with Cicada-specific parameters")

def lfsr_keystream(taps, init_state, length, mod=29):
    """Generate LFSR keystream."""
    reg_len = max(taps) + 1
    state = list(init_state[:reg_len])
    while len(state) < reg_len:
        state.append(0)
    output = []
    for _ in range(length):
        output.append(state[0] % mod)
        feedback = sum(state[t] for t in taps) % mod
        state.pop(0)
        state.append(feedback)
    return output

# Try various LFSR configurations
# Taps based on Cicada numbers
tap_configs = [
    ([1, 2, 4], "taps 1,2,4"),
    ([2, 3, 5], "taps 2,3,5 (primes)"),
    ([0, 5, 12], "taps 0,5,12 (GP: F,C,EO)"),
    ([2, 5, 11, 17], "taps 2,5,11,17 (TH,C,J,T)"),
    ([0, 3, 6, 10], "taps related to 3301 digits"),
]

# Initial states based on Cicada numbers
init_configs = [
    ([1] + [0]*28, "1,0,0..."),
    ([3,3,0,1] + [0]*25, "3301"),
    ([1,6,7] + [0]*26, "167"),
    ([7,6,1] + [0]*26, "761"),
    (list(range(29)), "0-28 sequential"),
    ([2,3,5,7,11,13,17,19,23,0,2,8,12,14,18,24,1,3,9,13,15,21,25,2,10,14,16,20,22], "GP primes mod 29"),
]

best_overall = 0
best_config = ""
for taps, tap_name in tap_configs:
    for init, init_name in init_configs:
        for pn in [20, 25, 32]:
            if pn not in pages: continue
            ci = pages[pn]
            n = len(ci)
            key = lfsr_keystream(taps, init, n)
            
            for mode in ['SUB', 'ADD']:
                if mode == 'SUB':
                    plain = [(ci[i] - key[i]) % 29 for i in range(n)]
                else:
                    plain = [(ci[i] + key[i]) % 29 for i in range(n)]
                ic = calculate_ioc(plain)
                if ic > best_overall:
                    best_overall = ic
                    best_config = f"P{pn} {tap_name} init={init_name} {mode}"

print(f"  Best: IoC={best_overall:.4f} [{best_config}]")

# ═══════════════════════════════════════════════════════════════════
# SECTION 5: PRIME GAPS AS KEYSTREAM
# ═══════════════════════════════════════════════════════════════════
print("\nSECTION 5: Prime gaps as keystream")
gaps = [PRIMES[i+1] - PRIMES[i] for i in range(len(PRIMES)-1)]

for pn in FOCUS:
    if pn not in pages: continue
    ci = pages[pn]
    n = len(ci)
    best_ioc = 0
    best_off = 0
    for offset in range(0, min(10001, len(gaps) - n), 100):
        key = [gaps[i + offset] % 29 for i in range(n)]
        plain = [(ci[i] - key[i]) % 29 for i in range(n)]
        ic = calculate_ioc(plain)
        if ic > best_ioc:
            best_ioc = ic
            best_off = offset
    flag = " ***" if best_ioc > 1.3 else ""
    print(f"  P{pn:02d}: {best_ioc:.4f} at offset={best_off}{flag}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 6: COMPOSITE TOTIENTS (SKIP PRIMES)
# ═══════════════════════════════════════════════════════════════════
print("\nSECTION 6: φ(composite_n) as keystream (skip primes)")
composites = [n for n in range(4, LIMIT) if not SIEVE[n]]
print(f"  {len(composites)} composites up to {LIMIT}")

for pn in FOCUS[:3]:
    if pn not in pages: continue
    ci = pages[pn]
    n = len(ci)
    best_ioc = 0
    best_off = 0
    for offset in range(0, min(5001, len(composites) - n), 100):
        key = [PHI[composites[i + offset]] % 29 for i in range(n)]
        plain = [(ci[i] - key[i]) % 29 for i in range(n)]
        ic = calculate_ioc(plain)
        if ic > best_ioc:
            best_ioc = ic
            best_off = offset
    flag = " ***" if best_ioc > 1.3 else ""
    print(f"  P{pn:02d}: {best_ioc:.4f} at offset={best_off}{flag}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 7: TOTIENT WITH F-SKIP ON UNSOLVED PAGES
# ═══════════════════════════════════════════════════════════════════
print("\nSECTION 7: Totient with F-skip rule (P55/P73 method)")
print("Key: φ(prime[i]) mod 29, but when plaintext=F, don't advance prime index")

PRIMES_BIG = sieve_primes(600000)[1]

for pn in FOCUS:
    if pn not in pages: continue
    ci = pages[pn]
    n = len(ci)
    best_ioc = 0
    best_off = 0
    
    for offset in range(0, min(5001, len(PRIMES_BIG) - n - 50)):
        # F-skip decryption
        plain = []
        ki = offset
        for c in ci:
            if ki >= len(PRIMES_BIG):
                break
            key = (PRIMES_BIG[ki] - 1) % 29
            p = (c - key) % 29
            plain.append(p)
            if p != 0:  # Not F -> advance
                ki += 1
        
        if len(plain) == n:
            ic = calculate_ioc(plain)
            if ic > best_ioc:
                best_ioc = ic
                best_off = offset
    
    flag = " ***" if best_ioc > 1.3 else ""
    print(f"  P{pn:02d}: {best_ioc:.4f} offset={best_off}{flag}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 8: INTERLEAVED/REARRANGED PRIMES
# ═══════════════════════════════════════════════════════════════════
print("\nSECTION 8: Rearranged prime sequences")
print("'Rearranging the prime numbers will show a path'")

# Method 1: Interleave odd-indexed and even-indexed primes
interleaved = []
odd_primes = PRIMES[1::2]  # 3, 7, 13, 19, 29, ...
even_primes = PRIMES[0::2]  # 2, 5, 11, 17, 23, ...
for i in range(min(len(odd_primes), len(even_primes))):
    interleaved.extend([odd_primes[i], even_primes[i]])

# Method 2: Primes in reverse
reversed_primes = list(reversed(PRIMES[:5000]))

# Method 3: Primes sorted by their mod 29 residue
sorted_by_mod = sorted(PRIMES[:5000], key=lambda p: p % 29)

# Method 4: Twin primes only (p, p+2 both prime)
twins = [p for p in PRIMES if (p + 2) in set(PRIMES[:5000])]

arrangements = [
    (interleaved, "interleaved odd/even"),
    (reversed_primes, "reversed"),
    (sorted_by_mod, "sorted by mod 29"),
    (twins, "twin primes only"),
]

for arr, arr_name in arrangements:
    for pn in [20, 25, 32]:
        if pn not in pages: continue
        ci = pages[pn]
        n = len(ci)
        if len(arr) < n:
            continue
        key = [(arr[i] - 1) % 29 for i in range(n)]
        plain = [(ci[i] - key[i]) % 29 for i in range(n)]
        ic = calculate_ioc(plain)
        if ic > 1.1:
            print(f"  P{pn:02d} {arr_name}: IoC={ic:.4f}")

# Also try: primes at Fibonacci-indexed positions (extending further)
fib = [0, 1]
while len(fib) < 500:
    fib.append(fib[-1] + fib[-2])

# For each position i, use prime[fib[i] % len(PRIMES)]
for pn in [20, 25, 32]:
    if pn not in pages: continue
    ci = pages[pn]
    n = len(ci)
    nprimes = len(PRIMES)
    for cycle in [29, 113, 131, 233, 377]:
        key = [(PRIMES[fib[i % cycle] % nprimes] - 1) % 29 for i in range(n)]
        plain = [(ci[i] - key[i]) % 29 for i in range(n)]
        ic = calculate_ioc(plain)
        if ic > 1.1:
            print(f"  P{pn:02d} fib-prime cycle={cycle}: IoC={ic:.4f}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 9: TOTIENT STREAM WITH PAGE-SPECIFIC SEED
# ═══════════════════════════════════════════════════════════════════
print("\nSECTION 9: Totient with page-number-derived offset")
print("offset = various functions of page number")

def try_offset_formula(name, offset_func):
    results = []
    for pn in FOCUS:
        if pn not in pages: continue
        ci = pages[pn]
        n = len(ci)
        offset = offset_func(pn)
        if offset < 0 or offset + n >= len(PRIMES_BIG):
            continue
        key = [(PRIMES_BIG[i + offset] - 1) % 29 for i in range(n)]
        plain = [(ci[i] - key[i]) % 29 for i in range(n)]
        ic = calculate_ioc(plain)
        results.append((pn, ic, offset))
    
    avg = sum(r[1] for r in results) / max(len(results), 1)
    if avg > 1.05:
        print(f"  {name}: avg IoC={avg:.4f}")
        for pn, ic, off in results:
            if ic > 1.1:
                print(f"    P{pn}: IoC={ic:.4f} offset={off}")

formulas = [
    ("page^2", lambda p: p*p),
    ("page*29", lambda p: p*29),
    ("page*113", lambda p: p*113),
    ("page*131", lambda p: p*131),
    ("page*3301", lambda p: p*3301),
    ("φ(page*29)", lambda p: PHI[min(p*29, LIMIT-1)]),
    ("prime[page]", lambda p: PRIMES[min(p, len(PRIMES)-1)]),
    ("prime[page]^2 mod 10000", lambda p: (PRIMES[min(p, len(PRIMES)-1)]**2) % 10000),
    ("page*page*29", lambda p: p*p*29),
    ("(page+1)*1033", lambda p: (p+1)*1033),  # P63 magic square constant
]

for name, func in formulas:
    try_offset_formula(name, func)

# ═══════════════════════════════════════════════════════════════════
# SECTION 10: DEEP AUTOKEY — USE PLAINTEXT TO GENERATE NEXT KEY
# ═══════════════════════════════════════════════════════════════════
print("\nSECTION 10: Deep autokey with various feedback functions")
print("P[i] = C[i] - f(P[i-1], P[i-2], ...) mod 29")

for pn in [20, 25, 32]:
    if pn not in pages: continue
    ci = pages[pn]
    n = len(ci)
    
    print(f"\n  P{pn:02d} ({n} runes):")
    
    # Try different autokey functions with different initial seeds
    best_overall = 0
    best_config = ""
    
    for seed_val in range(29):
        # Autokey with φ: key[i] = φ(P[i-1]+2) where P[i-1]+2 maps to a "prime index"
        plain = []
        prev_p = seed_val
        for c in ci:
            key = PHI[min(prev_p + 2, LIMIT)] % 29
            p = (c - key) % 29
            plain.append(p)
            prev_p = p
        ic = calculate_ioc(plain)
        if ic > best_overall:
            best_overall = ic
            best_config = f"seed={seed_val} feedback=φ(P+2)"
        
        # Autokey with prime lookup
        plain2 = []
        prev_p = seed_val
        for c in ci:
            if prev_p < len(PRIMES):
                key = (PRIMES[prev_p] - 1) % 29
            else:
                key = prev_p % 29
            p = (c - key) % 29
            plain2.append(p)
            prev_p = p
        ic2 = calculate_ioc(plain2)
        if ic2 > best_overall:
            best_overall = ic2
            best_config = f"seed={seed_val} feedback=prime[P]-1"
    
    flag = " ***" if best_overall > 1.3 else ""
    print(f"    Best: IoC={best_overall:.4f} [{best_config}]{flag}")

print("\n" + "=" * 80)
print("PHASE 4 ATTACK COMPLETE")
print("=" * 80)
