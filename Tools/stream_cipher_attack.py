"""Comprehensive stream cipher attack on ALL unsolved pages.
Test mathematical sequences as key streams: primes, cumulative primes, 
prime gaps, LFSR over GF(29), Fibonacci, etc."""

import os
from collections import Counter
import math

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

def load_page(pg):
    for p in [f'LiberPrimus/pages/page_{pg:02d}/runes.txt']:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                raw = f.read()
                runes = [GP[c] for c in raw if c in GP]
                words = []
                current = []
                for c in raw:
                    if c in GP:
                        current.append(GP[c])
                    elif current:
                        words.append(current)
                        current = []
                if current:
                    words.append(current)
                return runes, words
    return None, None

def ioc(values):
    n = len(values)
    if n < 2: return 0
    counts = Counter(values)
    return sum(c * (c-1) for c in counts.values()) / (n * (n-1))

def primes_up_to(n):
    sieve = [True] * (n+1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5)+1):
        if sieve[i]:
            for j in range(i*i, n+1, i):
                sieve[j] = False
    return [i for i in range(n+1) if sieve[i]]

def totient(n):
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

primes = primes_up_to(100000)
MAX_RUNES = 2000

# === Generate key streams ===
def gen_streams(n):
    """Generate various mathematical sequences of length n."""
    streams = {}
    
    # 1. Primes mod 29
    streams["primes_mod29"] = [primes[i] % 29 for i in range(n)]
    
    # 2. Cumulative primes mod 29
    cum = 0
    s = []
    for i in range(n):
        cum += primes[i]
        s.append(cum % 29)
    streams["cum_primes_mod29"] = s
    
    # 3. Prime gaps mod 29 (difference between consecutive primes)
    streams["prime_gaps_mod29"] = [(primes[i+1] - primes[i]) % 29 for i in range(n)]
    
    # 4. Totient of primes mod 29 (= prime-1 mod 29)
    streams["totient_primes_mod29"] = [(primes[i] - 1) % 29 for i in range(n)]
    
    # 5. Totient of natural numbers mod 29
    streams["totient_n_mod29"] = [totient(i+1) % 29 for i in range(n)]
    
    # 6. Fibonacci mod 29
    fib = [1, 1]
    while len(fib) < n:
        fib.append((fib[-1] + fib[-2]) % 29)
    streams["fib_mod29"] = fib[:n]
    
    # 7. Lucas numbers mod 29
    luc = [2, 1]
    while len(luc) < n:
        luc.append((luc[-1] + luc[-2]) % 29)
    streams["lucas_mod29"] = luc[:n]
    
    # 8. Natural numbers mod 29
    streams["natural_mod29"] = [i % 29 for i in range(n)]
    
    # 9. Triangular numbers mod 29
    streams["triangular_mod29"] = [(i*(i+1)//2) % 29 for i in range(n)]
    
    # 10. Powers of 2 mod 29
    streams["pow2_mod29"] = [pow(2, i, 29) for i in range(n)]
    
    # 11. Powers of 3 mod 29
    streams["pow3_mod29"] = [pow(3, i, 29) for i in range(n)]
    
    # 12. Powers of 11 mod 29 (generator 11, IRC research hint)
    streams["pow11_mod29"] = [pow(11, i, 29) for i in range(n)]
    
    # 13. Powers of 18 mod 29 (another generator)
    streams["pow18_mod29"] = [pow(18, i, 29) for i in range(n)]
    
    # 14. Square roots mod 29 (quadratic residues)
    streams["squares_mod29"] = [(i*i) % 29 for i in range(n)]
    
    # 15. Prime counting function mod 29
    pi = [0] * (n + 10)
    count = 0
    prime_set = set(primes_up_to(n + 10))
    for i in range(n + 10):
        if i in prime_set:
            count += 1
        pi[i] = count
    streams["prime_count_mod29"] = [pi[i] % 29 for i in range(n)]
    
    # 16. Mobius function mod 29
    mobius = [0] * max(n+1, 10)
    mobius[1] = 1
    for i in range(1, len(mobius)):
        for j in range(2*i, len(mobius), i):
            mobius[j] -= mobius[i]
    streams["mobius_mod29"] = [(mobius[i+1] % 29 + 29) % 29 for i in range(n)]
    
    # 17. Cumulative totient mod 29
    cum = 0
    ct = []
    for i in range(n):
        cum += totient(i + 2)
        ct.append(cum % 29)
    streams["cum_totient_mod29"] = ct
    
    # 18. i-th prime index-based (prime[i]*i mod 29)
    streams["prime_x_index_mod29"] = [(primes[i] * i) % 29 for i in range(n)]
    
    # 19. XOR-like: prime[i] XOR i, mod 29
    streams["prime_xor_i_mod29"] = [(primes[i] ^ i) % 29 for i in range(n)]
    
    # 20. Collatz-like on primes
    def collatz_step(x):
        if x % 2 == 0:
            return x // 2
        return 3 * x + 1
    streams["collatz_primes_mod29"] = [0] * n
    for i in range(n):
        x = primes[i]
        for _ in range(10):
            x = collatz_step(x)
        streams["collatz_primes_mod29"][i] = x % 29
    
    return streams

# LFSR over GF(29) — order 2 and 3
def lfsr_gf29(seed, taps, n):
    """Linear Feedback Shift Register over GF(29)."""
    order = len(seed)
    state = list(seed)
    output = []
    for _ in range(n):
        output.append(state[0])
        # Calculate feedback
        fb = 0
        for j, tap in enumerate(taps):
            fb = (fb + tap * state[j]) % 29
        state = state[1:] + [fb]
    return output

# Generate LFSR streams with various seeds and taps
def gen_lfsr_streams(n):
    streams = {}
    # Order 2: try seeds from prime pairs, taps from small values
    for s1 in range(1, 29, 7):
        for s2 in range(1, 29, 7):
            for t1 in range(1, 29, 7):
                for t2 in range(1, 29, 7):
                    key = f"lfsr2_s{s1}_{s2}_t{t1}_{t2}"
                    streams[key] = lfsr_gf29([s1, s2], [t1, t2], n)
    return streams

# Load all unsolved pages
pages = {}
for pg in range(18, 55):
    runes, words = load_page(pg)
    if runes and len(runes) > 10:
        pages[pg] = (runes, words)

print(f"Loaded {len(pages)} unsolved pages")
print(f"Testing mathematical sequence streams...")

# Generate streams
max_n = max(len(r) for r, w in pages.values())
streams = gen_streams(max_n + 100)

# Also test with offsets
OFFSETS = [0, 1, 2, 3, 5, 7, 10, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 71, 83, 100]

results = []

for pg, (runes, words) in pages.items():
    n = len(runes)
    
    for stream_name, stream in streams.items():
        for offset in OFFSETS:
            if offset + n > len(stream):
                continue
            
            key = stream[offset:offset+n]
            
            for mode in ['SUB', 'ADD']:
                if mode == 'SUB':
                    dec = [(runes[i] - key[i]) % 29 for i in range(n)]
                else:
                    dec = [(runes[i] + key[i]) % 29 for i in range(n)]
                
                ic = ioc(dec) * 29
                
                if ic > 1.4:  # Only report promising results
                    # Check single-rune words
                    pos = 0
                    single_ok = 0
                    single_total = 0
                    for word in words:
                        if len(word) == 1:
                            single_total += 1
                            if dec[pos] in [24, 10]:
                                single_ok += 1
                        pos += len(word)
                    
                    results.append((pg, stream_name, offset, mode, ic, single_ok, single_total, dec, words))

print(f"\nResults with IoC*29 > 1.4: {len(results)}")

# Sort by IoC
results.sort(key=lambda x: -x[4])

print("\n" + "="*100)
print("TOP 50 RESULTS BY IoC*29 (> 1.4)")
print("="*100)

for r in results[:50]:
    pg, sname, offset, mode, ic, s_ok, s_tot, dec, words = r
    
    # First 8 words
    pos = 0
    wds = []
    for word in words[:8]:
        wn = len(word)
        word_dec = dec[pos:pos+wn]
        wds.append(''.join(LATIN[v] for v in word_dec))
        pos += wn
    
    print(f"  P{pg:02d} {sname:25s} off={offset:3d} {mode:3s} IoC={ic:.3f} singles={s_ok}/{s_tot}")
    print(f"    Text: {' '.join(wds)}")

# === LFSR attack (limited due to combinatorial explosion) ===
print("\n" + "="*100)
print("LFSR OVER GF(29) - ORDER 2 SCAN")
print("  Testing order-2 LFSR with various seeds and taps")
print("="*100)

lfsr_results = []
# For each page, try LFSR order 2
for pg in [21, 22, 23, 24, 26, 27, 28, 29, 30, 31, 33, 34, 35, 36, 37, 38, 39, 41, 42, 43, 45, 46, 47, 48, 49, 51, 52, 53, 54]:
    if pg not in pages:
        continue
    runes, words = pages[pg]
    n = len(runes)
    
    # Order 2: s[n] = (a*s[n-1] + b*s[n-2]) mod 29
    best_ic = 0
    best_params = None
    
    for a in range(29):
        for b in range(1, 29):  # b can't be 0 for order 2
            # Seed from first two cipher values (or try known seeds)
            for seed in [[1, 1], [primes[0] % 29, primes[1] % 29], [3, 5]]:
                stream = lfsr_gf29(seed, [a, b], n)
                
                for mode in ['SUB', 'ADD']:
                    if mode == 'SUB':
                        dec = [(runes[i] - stream[i]) % 29 for i in range(n)]
                    else:
                        dec = [(runes[i] + stream[i]) % 29 for i in range(n)]
                    
                    ic = ioc(dec) * 29
                    if ic > best_ic:
                        best_ic = ic
                        best_params = (a, b, seed, mode, dec)
    
    if best_params and best_ic > 1.3:
        a, b, seed, mode, dec = best_params
        pos = 0
        wds = []
        for word in words[:8]:
            wn = len(word)
            word_dec = dec[pos:pos+wn]
            wds.append(''.join(LATIN[v] for v in word_dec))
            pos += wn
        
        print(f"  P{pg:02d}: best IoC*29={best_ic:.3f} a={a} b={b} seed={seed} {mode}")
        print(f"    Text: {' '.join(wds)}")
        lfsr_results.append((pg, best_ic, best_params))
    elif best_params:
        a, b, seed, mode, dec = best_params
        print(f"  P{pg:02d}: best IoC*29={best_ic:.3f} (below threshold)")

print("\nDone.")
