"""
MATHEMATICAL KEY STREAM TESTS + TWO-LAYER CIPHERS
===================================================
Premise: The totient cipher on P55/P73 used key[i] = prime[i]-1 = phi(prime[i]).
"THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED"
What if unsolved pages use DIFFERENT mathematical key streams?

Also: P19 hint "REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR"

TEST PLAN:
1. Euler totient of sequential integers phi(n) as key stream
2. Various math sequences as key: Fibonacci, factorial mod 29, etc
3. "Rearranged primes" - primes indexed by primes, reverse primes, etc
4. Two-layer: Atbash first then Vigenere, or Vigenere then Atbash
5. Progressive/rotating key: key derived from ciphertext or plaintext
6. Key = GP primes in Deor order (map Deor chars to their GP primes)
7. Totient of rune GP prime values
"""
import os, sys, math
from collections import Counter

os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
GP_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109]
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':14}

def to_eng(vals): return ''.join(LATIN[v] for v in vals)
def ioc(values, alpha=29):
    n = len(values)
    if n < 2: return 0
    counts = Counter(values)
    return sum(c*(c-1) for c in counts.values()) / (n*(n-1)) * alpha

def load_page(pg):
    for p in [f'LiberPrimus/pages/page_{pg:02d}/runes.txt', f'LiberPrimus/pages/page_{pg}/runes.txt']:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                return [GP[c] for c in f.read() if c in GP]
    return None

def sieve_primes(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = False
    return [i for i in range(2, limit + 1) if is_prime[i]]

def euler_totient(n):
    """Compute Euler's totient function phi(n)"""
    result = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result

# Precompute totients up to 50000
MAX_N = 50000
all_primes = sieve_primes(MAX_N)
prime_set = set(all_primes)

# Precompute totients using sieve method
totients = list(range(MAX_N + 1))  # phi[i] starts as i
for p in range(2, MAX_N + 1):
    if totients[p] == p:  # p is prime
        for m in range(p, MAX_N + 1, p):
            totients[m] -= totients[m] // p

# Fibonacci sequence mod 29
def fibonacci_mod(n, mod=29):
    seq = [0, 1]
    for i in range(2, n):
        seq.append((seq[-1] + seq[-2]) % mod)
    return seq

# Load pages
unsolved = {}
for pg in list(range(17, 55)) + [71]:
    data = load_page(pg)
    if data and len(data) > 50:
        unsolved[pg] = data

print(f"Loaded {len(unsolved)} unsolved pages")
print(f"Precomputed {len(all_primes)} primes and totients up to {MAX_N}")

# ================================================================
# TEST 1: TOTIENT OF ALL INTEGERS (not just primes) 
# ================================================================
print("\n" + "="*70)
print("TEST 1: phi(n) AS KEY STREAM (n = offset, offset+1, offset+2, ...)")
print("="*70)

# phi(n) mod 29 as key stream, with various starting offsets
# Check offsets 0 to 10000
for pg in sorted(unsolved):
    cipher = unsolved[pg]
    n = len(cipher)
    best = (0, 0, '')
    
    for offset in range(0, 10001, 1):
        if offset + n > MAX_N: break
        key = [totients[offset + i] % 29 for i in range(n)]
        
        # SUB
        plain = [(cipher[i] - key[i]) % 29 for i in range(n)]
        ic = ioc(plain)
        if ic > best[0]:
            best = (ic, offset, 'sub')
        
        # ADD
        plain = [(cipher[i] + key[i]) % 29 for i in range(n)]
        ic = ioc(plain)
        if ic > best[0]:
            best = (ic, offset, 'add')
        
        # BEAU
        plain = [(key[i] - cipher[i]) % 29 for i in range(n)]
        ic = ioc(plain)
        if ic > best[0]:
            best = (ic, offset, 'beau')
    
    ic, off, mode = best
    if ic > 1.3 and len(cipher) > 100:
        key = [totients[off + i] % 29 for i in range(len(cipher))]
        if mode == 'sub': plain = [(cipher[i] - key[i]) % 29 for i in range(len(cipher))]
        elif mode == 'add': plain = [(cipher[i] + key[i]) % 29 for i in range(len(cipher))]
        else: plain = [(key[i] - cipher[i]) % 29 for i in range(len(cipher))]
        text = to_eng(plain[:60])
        print(f"  P{pg:02d} (n={len(cipher)}): IoC={ic:.4f} offset={off} mode={mode}")
        print(f"    {text}")

# Summary: report best per page
print("\n  Best per page (all sizes):")
for pg in sorted(unsolved):
    cipher = unsolved[pg]
    n = len(cipher)
    best = (0, 0, '')
    for offset in range(0, min(5001, MAX_N - n)):
        key = [totients[offset + i] % 29 for i in range(n)]
        plain = [(cipher[i] - key[i]) % 29 for i in range(n)]
        ic = ioc(plain)
        if ic > best[0]: best = (ic, offset, 'sub')
    ic, off, mode = best
    if ic > 1.2:
        print(f"    P{pg:02d}: IoC={ic:.4f} at offset={off}")

# ================================================================
# TEST 2: FIBONACCI, FACTORIAL, TRIANGULAR NUMBERS as key
# ================================================================
print("\n" + "="*70)
print("TEST 2: MATHEMATICAL SEQUENCES AS KEY STREAM")
print("="*70)

# Generate various sequences
max_len = max(len(v) for v in unsolved.values()) + 10

# Fibonacci mod 29
fib = fibonacci_mod(max_len + 2)

# Triangular numbers mod 29: T(n) = n*(n+1)/2
triangular = [(i*(i+1)//2) % 29 for i in range(max_len)]

# Powers of 2 mod 29
pow2 = [pow(2, i, 29) for i in range(max_len)]

# Powers of 3 mod 29
pow3 = [pow(3, i, 29) for i in range(max_len)]

# Factorial mod 29 (small at first then 0)
factorial = [1]
for i in range(1, max_len):
    factorial.append((factorial[-1] * i) % 29)

# Sum of digits of prime[i]
def digit_sum(n): return sum(int(d) for d in str(n))
prime_digit_sums = [digit_sum(p) % 29 for p in all_primes[:max_len]]

# Prime gaps
prime_gaps = [all_primes[i+1] - all_primes[i] for i in range(len(all_primes)-1)]
prime_gaps_mod29 = [g % 29 for g in prime_gaps[:max_len]]

# Mobius function
def mobius(n):
    if n == 1: return 1
    factors = 0
    temp = n
    p = 2
    while p * p <= temp:
        if temp % p == 0:
            temp //= p
            if temp % p == 0: return 0  # p^2 divides n
            factors += 1
        p += 1
    if temp > 1: factors += 1
    return 1 if factors % 2 == 0 else -1

# Use (mobius(n) + 1) to stay in range [0,2], then expand
mobius_seq = [(mobius(i+2) + 1) % 29 for i in range(max_len)]

# COLLATZ sequence lengths as key
def collatz_length(n):
    count = 0
    while n > 1:
        if n % 2 == 0: n //= 2
        else: n = 3 * n + 1
        count += 1
        if count > 10000: break
    return count
collatz = [collatz_length(i+2) % 29 for i in range(max_len)]

sequences = {
    'fibonacci': fib[:max_len],
    'triangular': triangular,
    'pow2': pow2,
    'pow3': pow3,
    'prime_digit_sum': prime_digit_sums[:max_len],
    'prime_gaps': prime_gaps_mod29[:max_len],
    # 'mobius': mobius_seq, # too slow for large n
    'collatz': collatz,
}

for seq_name, seq in sequences.items():
    if len(seq) < 50: continue
    hits = []
    for pg in sorted(unsolved):
        cipher = unsolved[pg]
        n = min(len(cipher), len(seq))
        if n < 50: continue
        
        for mode in ['sub', 'add', 'beau']:
            if mode == 'sub': plain = [(cipher[i] - seq[i]) % 29 for i in range(n)]
            elif mode == 'add': plain = [(cipher[i] + seq[i]) % 29 for i in range(n)]
            else: plain = [(seq[i] - cipher[i]) % 29 for i in range(n)]
            
            ic = ioc(plain)
            if ic > 1.35 and n > 100:
                text = to_eng(plain[:50])
                hits.append(f"    P{pg:02d} {mode}: IoC={ic:.4f} {text}")
    
    if hits:
        print(f"\n  {seq_name}:")
        for h in hits:
            print(h)
    else:
        # Report best for this sequence
        best = (0, 0, '')
        for pg in sorted(unsolved):
            cipher = unsolved[pg]
            n = min(len(cipher), len(seq))
            if n < 100: continue
            plain = [(cipher[i] - seq[i]) % 29 for i in range(n)]
            ic = ioc(plain)
            if ic > best[0]: best = (ic, pg, 'sub')
        print(f"  {seq_name}: best IoC={best[0]:.4f} on P{best[1]:02d} ({best[2]})")

# Also test shifted sequences
print("\n  With offsets (best of 0-500):")
for seq_name, seq in sequences.items():
    if len(seq) < 1500: continue
    best_overall = (0, 0, 0, '')
    for pg in sorted(unsolved):
        cipher = unsolved[pg]
        n = len(cipher)
        if n < 100: continue
        for offset in range(min(501, len(seq) - n)):
            plain = [(cipher[i] - seq[offset + i]) % 29 for i in range(n)]
            ic = ioc(plain)
            if ic > best_overall[0]:
                best_overall = (ic, pg, offset, 'sub')
    
    ic, pg, off, mode = best_overall
    if ic > 1.2:
        print(f"    {seq_name}: best IoC={ic:.4f} P{pg:02d} offset={off}")

# ================================================================
# TEST 3: REARRANGED PRIMES - Creative Interpretations
# ================================================================
print("\n" + "="*70)
print("TEST 3: 'REARRANGED PRIMES' CREATIVE TESTS")
print("="*70)

# 3A: Primes indexed by primes: key[i] = prime[prime[i]] (the prime[i]-th prime)
print("\n3A: prime-indexed primes")
# prime[0]=2, prime[1]=3, prime[2]=5 -> prime[prime[0]]=prime[2]=5, prime[prime[1]]=prime[3]=7, prime[prime[2]]=prime[5]=13
pip = [all_primes[p-1] if p <= len(all_primes) else 0 for p in all_primes[:max_len]]  # prime-indexed prime
pip_mod29 = [p % 29 for p in pip[:max_len]]

for pg in sorted(unsolved):
    cipher = unsolved[pg]
    n = min(len(cipher), len(pip_mod29))
    if n < 50: continue
    for mode in ['sub', 'add', 'beau']:
        if mode == 'sub': plain = [(cipher[i] - pip_mod29[i]) % 29 for i in range(n)]
        elif mode == 'add': plain = [(cipher[i] + pip_mod29[i]) % 29 for i in range(n)]
        else: plain = [(pip_mod29[i] - cipher[i]) % 29 for i in range(n)]
        ic = ioc(plain)
        if ic > 1.3 and n > 100:
            text = to_eng(plain[:50])
            print(f"  P{pg:02d} {mode}: IoC={ic:.4f} {text}")

# 3B: Reverse primes (read prime sequence backwards from some starting point)
print("\n3B: Reverse prime sequence")
rev_primes = list(reversed([p % 29 for p in all_primes[:5000]]))
for pg in sorted(unsolved):
    cipher = unsolved[pg]
    n = min(len(cipher), len(rev_primes))
    if n < 100: continue
    best = (0, 0, '')
    for offset in range(min(501, len(rev_primes) - n)):
        key = rev_primes[offset:offset+n]
        plain = [(cipher[i] - key[i]) % 29 for i in range(n)]
        ic = ioc(plain)
        if ic > best[0]: best = (ic, offset, 'sub')
    ic, off, mode = best
    if ic > 1.25:
        print(f"  P{pg:02d}: IoC={ic:.4f} offset={off}")

# 3C: GP primes used as INDEX into another text
# Map each cipher rune to its GP prime value, use that as an index into the Deor
print("\n3C: GP prime values as indices into Deor text")
deor_path = 'Analysis/Reference_Docs/deor_poem.txt'
with open(deor_path, 'r', encoding='utf-8') as f:
    deor_raw = f.read().upper()
    deor_raw = deor_raw.replace('Þ', 'TH').replace('Ð', 'TH').replace('Æ', 'AE')
    # Simple: just extract alphabetic chars
    deor_chars = [c for c in deor_raw if c.isalpha()]
    deor_gp = [ENG2GP.get(c, 0) for c in deor_chars]

print(f"  Deor has {len(deor_chars)} chars, {len(deor_gp)} GP values")

# For each cipher rune, look up its GP prime value, use that to index Deor
for pg in [20, 17, 25, 32, 40, 44, 50]:  # focus on large pages
    if pg not in unsolved: continue
    cipher = unsolved[pg]
    n = len(cipher)
    
    # key[i] = deor_gp[GP_PRIMES[cipher[i]]]  (GP prime of cipher rune used as index)
    # This only works if all GP primes < len(deor_gp)
    if max(GP_PRIMES) < len(deor_gp):
        key = [deor_gp[GP_PRIMES[v]] for v in cipher]
        for mode in ['sub', 'add', 'beau']:
            if mode == 'sub': plain = [(cipher[i] - key[i]) % 29 for i in range(n)]
            elif mode == 'add': plain = [(cipher[i] + key[i]) % 29 for i in range(n)]
            else: plain = [(key[i] - cipher[i]) % 29 for i in range(n)]
            ic = ioc(plain)
            if ic > 1.3:
                text = to_eng(plain[:50])
                print(f"  P{pg:02d} {mode}: IoC={ic:.4f} {text}")

# ================================================================
# TEST 4: TWO-LAYER CIPHERS
# ================================================================
print("\n" + "="*70)
print("TEST 4: TWO-LAYER CIPHERS")
print("="*70)

def atbash(vals):
    return [(28 - v) % 29 for v in vals]

def atbash_shift(vals, shift):
    return [(28 - v + shift) % 29 for v in vals]

keywords_short = ['DIVINITY', 'PRIMES', 'FIRFUMFERENFE', 'DEOR', 'SACRED', 'TOTIENT', 'WELCOME', 'WISDOM']

# 4A: Atbash first, then Vigenere
print("\n4A: Atbash → Vigenere")
for pg in sorted(unsolved):
    cipher = unsolved[pg]
    # Apply Atbash first
    intermediate = atbash(cipher)
    for kw in keywords_short:
        key = [ENG2GP[c] for c in kw.upper() if c in ENG2GP]
        if not key: continue
        n = len(cipher)
        plain = [(intermediate[i] - key[i % len(key)]) % 29 for i in range(n)]
        ic = ioc(plain)
        if ic > 1.4 and n > 100:
            text = to_eng(plain[:50])
            print(f"  P{pg:02d} Atbash+Vig({kw}): IoC={ic:.4f} {text}")

# 4B: Atbash+3 first, then Vigenere
print("\n4B: Atbash+3 → Vigenere")
for pg in sorted(unsolved):
    cipher = unsolved[pg]
    for shift in [1, 2, 3, 4, 5]:
        intermediate = atbash_shift(cipher, shift)
        for kw in keywords_short:
            key = [ENG2GP[c] for c in kw.upper() if c in ENG2GP]
            if not key: continue
            n = len(cipher)
            plain = [(intermediate[i] - key[i % len(key)]) % 29 for i in range(n)]
            ic = ioc(plain)
            if ic > 1.4 and n > 100:
                text = to_eng(plain[:50])
                print(f"  P{pg:02d} Atbash+{shift}+Vig({kw}): IoC={ic:.4f} {text}")

# 4C: Vigenere first, then Atbash
print("\n4C: Vigenere → Atbash")
for pg in sorted(unsolved):
    cipher = unsolved[pg]
    for kw in keywords_short:
        key = [ENG2GP[c] for c in kw.upper() if c in ENG2GP]
        if not key: continue
        n = len(cipher)
        intermediate = [(cipher[i] - key[i % len(key)]) % 29 for i in range(n)]
        plain = atbash(intermediate)
        ic = ioc(plain)
        if ic > 1.4 and n > 100:
            text = to_eng(plain[:50])
            print(f"  P{pg:02d} Vig({kw})+Atbash: IoC={ic:.4f} {text}")

# 4D: Vigenere first, then Totient
print("\n4D: Vigenere → Totient (or vice versa)")
for pg in sorted(unsolved):
    cipher = unsolved[pg]
    n = len(cipher)
    for kw in keywords_short:
        key_kw = [ENG2GP[c] for c in kw.upper() if c in ENG2GP]
        if not key_kw: continue
        
        # Vigenere then totient
        intermediate = [(cipher[i] - key_kw[i % len(key_kw)]) % 29 for i in range(n)]
        key_tot = [(all_primes[i] - 1) % 29 for i in range(n)]
        plain = [(intermediate[i] - key_tot[i]) % 29 for i in range(n)]
        ic = ioc(plain)
        if ic > 1.35 and n > 100:
            text = to_eng(plain[:50])
            print(f"  P{pg:02d} Vig({kw})+Tot: IoC={ic:.4f} {text}")
        
        # Totient then Vigenere
        intermediate2 = [(cipher[i] - key_tot[i]) % 29 for i in range(n)]
        plain2 = [(intermediate2[i] - key_kw[i % len(key_kw)]) % 29 for i in range(n)]
        ic2 = ioc(plain2)
        if ic2 > 1.35 and n > 100:
            text = to_eng(plain2[:50])
            print(f"  P{pg:02d} Tot+Vig({kw}): IoC={ic2:.4f} {text}")

# ================================================================
# TEST 5: P19 KEY ANALYSIS - DEEPER
# ================================================================
print("\n" + "="*70)
print("TEST 5: P19 KEY -- DEEPER ANALYSIS")
print("="*70)

p19_key = [24, 15, 2, 24, 4, 21, 11, 10, 20, 16, 9, 19, 26, 11, 7, 5, 11, 6, 27, 8, 22, 25, 21, 16, 25, 0, 27, 9, 21, 7, 27, 15, 21, 9, 3, 16, 5, 22, 18, 4, 5, 18, 23]
print(f"P19 key ({len(p19_key)} values): {to_eng(p19_key)}")

# Are the key values themselves a cipher message?
# Check if key, when decrypted with various methods, gives readable text
# Try Atbash on key
key_atbash = [(28 - v) % 29 for v in p19_key]
print(f"  Key atbash: {to_eng(key_atbash)}")

# Try Caesar shifts on key
for shift in range(1, 29):
    shifted = [(v + shift) % 29 for v in p19_key]
    text = to_eng(shifted)
    # Check for common English patterns
    if 'THE' in text or 'AND' in text or 'NOT' in text or 'FOR' in text:
        print(f"  Key+{shift}: {text}")

# Check: is the key derived from Deor poem?
print(f"\n  Checking if P19 key matches Deor at any offset...")
for off in range(len(deor_gp) - len(p19_key) + 1):
    segment = deor_gp[off:off+len(p19_key)]
    # Exact match?
    if segment == p19_key:
        print(f"  EXACT MATCH at Deor offset {off}!")
    # Constant difference?
    diffs = [(p19_key[i] - segment[i]) % 29 for i in range(len(p19_key))]
    if len(set(diffs)) == 1:
        print(f"  Constant diff {diffs[0]} at offset {off}")

# Check: is key related to GP prime values of Deor?
print(f"\n  Checking if key = phi(prime) relationship...")
for i in range(len(p19_key)):
    v = p19_key[i]
    prime = GP_PRIMES[v] if v < 29 else 0
    print(f"    K[{i:2d}]={v:2d}={LATIN[v]:3s}  prime={prime:3d}  phi(prime)={prime-1 if prime > 1 else 0:3d}  phi%29={((prime-1)%29) if prime > 1 else 0}", end='')
    if i < len(all_primes):
        print(f"  prime[{i}]={all_primes[i]}  phi={all_primes[i]-1}  %29={(all_primes[i]-1)%29}", end='')
    print()

# Check: is the P19 key = totient values at some offset?
print(f"\n  Is P19 key = phi(n+offset) mod 29 at some offset?")
for offset in range(0, 10001):
    if offset + len(p19_key) > MAX_N: break
    match = True
    for i in range(len(p19_key)):
        if totients[offset + i] % 29 != p19_key[i]:
            match = False
            break
    if match:
        print(f"  MATCH at offset {offset}!")

# Partial matches
print(f"\n  Best partial match of P19 key vs totient stream:")
best_match = (0, 0)
for offset in range(0, 10001):
    if offset + len(p19_key) > MAX_N: break
    matches = sum(1 for i in range(len(p19_key)) if totients[offset + i] % 29 == p19_key[i])
    if matches > best_match[0]:
        best_match = (matches, offset)
print(f"  Best: {best_match[0]}/{len(p19_key)} matching at offset {best_match[1]}")

# ================================================================
# TEST 6: FOCUSED P20 INVESTIGATION
# ================================================================
print("\n" + "="*70)
print("TEST 6: FOCUSED P20 INVESTIGATION")  
print("="*70)

if 20 in unsolved:
    p20 = unsolved[20]
    print(f"P20: {len(p20)} runes, IoC={ioc(p20):.4f}")
    print(f"First 30: {to_eng(p20[:30])}")
    
    # P19 hint: "WILL SHOW A PATH TO THE DEOR"
    # Maybe P20's key IS the Deor poem, but with F-skip and specific mode?
    
    # F-skip Deor running key on P20 with all 3 modes
    print("\nP20 with Deor F-skip running key:")
    for offset in range(min(500, len(deor_gp) - len(p20))):
        for mode in ['sub', 'add', 'beau']:
            ki = 0
            plain = []
            for i in range(len(p20)):
                if p20[i] == 0:
                    plain.append(0)  # F passes through
                    continue
                if offset + ki >= len(deor_gp):
                    break
                k = deor_gp[offset + ki]
                if mode == 'sub': plain.append((p20[i] - k) % 29)
                elif mode == 'add': plain.append((p20[i] + k) % 29)
                else: plain.append((k - p20[i]) % 29)
                ki += 1
            
            if len(plain) == len(p20):
                ic = ioc(plain)
                if ic > 1.3:
                    text = to_eng(plain[:50])
                    print(f"  offset={offset} mode={mode}: IoC={ic:.4f} {text}")
    
    # Try: Atbash(P20) then Deor running key
    print("\nP20: Atbash → Deor running key:")
    p20_atbash = atbash(p20)
    for offset in range(min(500, len(deor_gp) - len(p20))):
        key = deor_gp[offset:offset+len(p20)]
        plain = [(p20_atbash[i] - key[i]) % 29 for i in range(len(p20))]
        ic = ioc(plain)
        if ic > 1.3:
            text = to_eng(plain[:50])
            print(f"  offset={offset}: IoC={ic:.4f} {text}")
    
    # Try: totient(offset) on P20 for ALL offsets
    print("\nP20: totient key stream best 5:")
    results = []
    for offset in range(min(10001, MAX_N - len(p20))):
        key = [totients[offset + i] % 29 for i in range(len(p20))]
        for mode in ['sub', 'add', 'beau']:
            if mode == 'sub': plain = [(p20[i] - key[i]) % 29 for i in range(len(p20))]
            elif mode == 'add': plain = [(p20[i] + key[i]) % 29 for i in range(len(p20))]
            else: plain = [(key[i] - p20[i]) % 29 for i in range(len(p20))]
            ic = ioc(plain)
            results.append((ic, offset, mode))
    
    results.sort(reverse=True)
    for ic, offset, mode in results[:5]:
        key = [totients[offset + i] % 29 for i in range(len(p20))]
        if mode == 'sub': plain = [(p20[i] - key[i]) % 29 for i in range(len(p20))]
        elif mode == 'add': plain = [(p20[i] + key[i]) % 29 for i in range(len(p20))]
        else: plain = [(key[i] - p20[i]) % 29 for i in range(len(p20))]
        text = to_eng(plain[:50])
        print(f"  IoC={ic:.4f} offset={offset} mode={mode}: {text}")

print("\n" + "="*70)
print("ALL MATHEMATICAL KEY STREAM TESTS COMPLETE")
print("="*70)
