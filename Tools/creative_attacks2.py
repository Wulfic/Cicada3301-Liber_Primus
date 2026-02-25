"""Creative attacks:
1. P19 autokey continuation (first 43 runes solved, rest via autokey)
2. Berlekamp-Massey on P19 key stream
3. Known key stream applied to other pages
4. 'Rearranging primes' literal interpretation"""

import os
from collections import Counter

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

primes = primes_up_to(100000)

# === P19 known data ===
KNOWN_KEY = [24,15,2,24,4,21,11,10,20,16,9,19,26,11,7,5,11,6,27,8,22,25,21,16,25,0,27,9,21,7,27,15,21,9,3,16,5,22,18,4,5,18,23]
KNOWN_PLAIN = [4,18,24,4,4,24,21,10,21,2,18,13,4,10,19,18,15,9,1,19,17,18,4,15,7,10,20,20,15,8,3,7,24,13,24,2,16,3,2,18,23,12,4]

cipher19, words19 = load_page(19)
N19 = len(cipher19)
key_stream_43 = [(KNOWN_PLAIN[i] - cipher19[i]) % 29 for i in range(43)]

print(f"P19: {N19} runes")
print(f"Key stream (43): {key_stream_43}")

# === BERLEKAMP-MASSEY ===
print("\n" + "="*80)
print("BERLEKAMP-MASSEY on P19 key stream (43 values)")
print("="*80)

def modinv(a, m=29):
    if a == 0: return None
    g, x, _ = extended_gcd(a % m, m)
    if g != 1: return None
    return x % m

def extended_gcd(a, b):
    if a == 0: return b, 0, 1
    g, x, y = extended_gcd(b % a, a)
    return g, y - (b // a) * x, x

def berlekamp_massey_gf29(seq):
    n = len(seq)
    C = [1]
    B = [1]
    L = 0
    m = 1
    b_val = 1
    
    for i in range(n):
        d = seq[i]
        for j in range(1, len(C)):
            if i - j >= 0:
                d = (d + C[j] * seq[i - j]) % 29
        
        if d == 0:
            m += 1
        else:
            T = list(C)
            inv_b = modinv(b_val)
            if inv_b is None:
                m += 1
                continue
            
            coeff = (29 - d * inv_b % 29) % 29
            while len(C) < len(B) + m:
                C.append(0)
            for j in range(len(B)):
                C[j + m] = (C[j + m] + coeff * B[j]) % 29
            
            if 2 * L <= i:
                L = i + 1 - L
                B = T
                b_val = d
                m = 1
            else:
                m += 1
    
    return L, C

L, C = berlekamp_massey_gf29(key_stream_43)
print(f"LFSR complexity: {L}")
print(f"Connection polynomial (first 20): {C[:min(L+2, 20)]}")

if L < 22:  # Less than half the sequence = might be real
    print(f"\n  Complexity {L} < 22 (half of 43) — potentially real LFSR!")
    
    # Extend
    ext = list(key_stream_43)
    while len(ext) < N19:
        val = 0
        for j in range(1, min(len(C), len(ext)+1)):
            val = (val - C[j] * ext[len(ext) - j]) % 29
        ext.append(val)
    
    # Decrypt
    plain = [(cipher19[i] + ext[i]) % 29 for i in range(N19)]
    ic = ioc(plain) * 29
    
    pos = 0
    wds = []
    for word in words19:
        wn = len(word)
        word_dec = plain[pos:pos+wn]
        wds.append(''.join(LATIN[v] for v in word_dec))
        pos += wn
    
    print(f"  IoC*29 = {ic:.3f}")
    print(f"  Words: {' '.join(wds[:20])}")
    
    # Also try on other pages
    if ic > 1.3:
        print(f"\n  PROMISING! Trying on other pages...")
        for pg in range(18, 55):
            if pg == 19: continue
            runes, words = load_page(pg)
            if not runes: continue
            n = len(runes)
            
            for offset in range(0, min(5000, len(ext) - n)):
                key = ext[offset:offset+n]
                for mode_name, fn in [("ADD", lambda c,k: (c+k)%29), ("SUB", lambda c,k: (c-k)%29)]:
                    dec = [fn(runes[i], key[i]) for i in range(n)]
                    ic2 = ioc(dec) * 29
                    if ic2 > 1.4:
                        text = ''.join(LATIN[v] for v in dec[:60])
                        print(f"    P{pg:02d} off={offset} {mode_name}: IoC={ic2:.3f} | {text}")
else:
    print(f"  Complexity {L} ≥ 22 — key stream appears random (no short LFSR)")
    print(f"  This means the P19 cipher (beyond position 43) is NOT a simple LFSR continuation")

# === AUTOKEY VARIANTS ===
print("\n" + "="*80)
print("AUTOKEY CONTINUATION (P19 positions 43+)")
print("="*80)

best_autokey = []
for K in range(1, 60):
    for mode in ['ADD', 'SUB']:
        plain = list(KNOWN_PLAIN[:43])
        for i in range(43, N19):
            if i - K < 0: break
            kv = plain[i - K]
            if mode == 'ADD':
                plain.append((cipher19[i] + kv) % 29)
            else:
                plain.append((cipher19[i] - kv) % 29)
        
        if len(plain) == N19:
            ic = ioc(plain) * 29
            best_autokey.append((ic, K, mode, plain))

    # Cipher feedback autokey
    for mode in ['ADD', 'SUB']:
        plain = list(KNOWN_PLAIN[:43])
        for i in range(43, N19):
            if i - K < 0: break
            kv = cipher19[i - K]
            if mode == 'ADD':
                plain.append((cipher19[i] + kv) % 29)
            else:
                plain.append((cipher19[i] - kv) % 29)
        
        if len(plain) == N19:
            ic = ioc(plain) * 29
            best_autokey.append((ic, K, f"cipher_{mode}", plain))

best_autokey.sort(key=lambda x: -x[0])
print("Top 10 autokey results:")
for ic, K, mode, plain in best_autokey[:10]:
    pos = 0
    wds = []
    for word in words19:
        wn = len(word)
        word_dec = plain[pos:pos+wn]
        wds.append(''.join(LATIN[v] for v in word_dec))
        pos += wn
    print(f"  K={K:2d} {mode:12s} IoC*29={ic:.3f}")
    print(f"    Words 8-15: {' '.join(wds[8:15])}")

# === REARRANGING PRIMES on P20 ===
print("\n" + "="*80)
print("ATTACK: 'Rearranging primes' on P20")
print("="*80)

runes20, words20 = load_page(20)
n20 = len(runes20)
print(f"P20: {n20} runes, {len(words20)} words")

# Separate into prime-value and non-prime-value runes
prime_vals = set(primes_up_to(28))  # {2,3,5,7,11,13,17,19,23}
prime_val_runes = [(i, runes20[i]) for i in range(n20) if runes20[i] in prime_vals]
non_prime_val_runes = [(i, runes20[i]) for i in range(n20) if runes20[i] not in prime_vals]

print(f"  Prime-value runes: {len(prime_val_runes)}")
print(f"  Non-prime-value runes: {len(non_prime_val_runes)}")
print(f"  Prime values in GP: {sorted(prime_vals)} = {[LATIN[v] for v in sorted(prime_vals)]}")

# IoC of each subset
pv_runes = [v for _, v in prime_val_runes]
npv_runes = [v for _, v in non_prime_val_runes]
print(f"  Prime-value IoC*29: {ioc(pv_runes)*29:.3f} ({len(pv_runes)} runes)")
print(f"  Non-prime IoC*29: {ioc(npv_runes)*29:.3f} ({len(npv_runes)} runes)")

# Also separate by prime-INDEXED positions
prime_idx = set(p for p in primes if p < n20)
prime_pos_runes = [runes20[i] for i in range(n20) if i in prime_idx]
non_prime_pos_runes = [runes20[i] for i in range(n20) if i not in prime_idx]
print(f"  Prime-indexed runes: {len(prime_pos_runes)}")
print(f"  Non-prime-indexed runes: {len(non_prime_pos_runes)}")
print(f"  Prime-indexed IoC*29: {ioc(prime_pos_runes)*29:.3f}")
print(f"  Non-prime-indexed IoC*29: {ioc(non_prime_pos_runes)*29:.3f}")

# Frequency of prime-value runes — are they restricted to certain GP values?
pv_counts = Counter(pv_runes)
print(f"\n  Prime-value rune distribution:")
for v in sorted(prime_vals):
    if pv_counts[v] > 0:
        print(f"    GP {v:2d} ({LATIN[v]:3s}): {pv_counts[v]}")

# This analysis was done before — prime-valued runes use only 9 GP values
# which are {2,3,5,7,11,13,17,19,23} = {TH,O,C,W,J,P,B,M,D}
# IoC of this restricted alphabet should be compared to random over 9 values

# IoC normalized to 9 values: random = 1/9 = 0.111, English-like = higher
ic_prime_9 = ioc(pv_runes)
print(f"\n  IoC of prime-valued stream (raw): {ic_prime_9:.4f}")
print(f"  Random IoC over 9 values: {1/9:.4f}")
print(f"  Ratio: {ic_prime_9 / (1/9):.3f}x random")

# Try Beaufort with 'Deor' poem on prime-valued runes
# First, let's load the Deor poem GP values
# From community research: Deor poem was used for P20 prime stream
# Let me check if there's a Deor poem file
deor_path = None
for candidate in ['LiberPrimus/reference/deor.txt', 'Tools/deor.txt', 'deor.txt',
                   'LiberPrimus/reference/research/deor.txt']:
    if os.path.exists(candidate):
        deor_path = candidate
        break

if deor_path:
    with open(deor_path, 'r', encoding='utf-8') as f:
        deor_text = f.read()
    print(f"\n  Found Deor poem at: {deor_path}")
    print(f"  Deor text length: {len(deor_text)} chars")
else:
    print(f"\n  Deor poem not found in repository")
    print(f"  Checking for Deor references in Tools/...")

print("\nDone.")
