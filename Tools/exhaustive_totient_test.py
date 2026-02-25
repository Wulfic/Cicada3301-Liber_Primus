"""
EXHAUSTIVE TOTIENT CIPHER TEST

The totient cipher (confirmed for P55/P73):
  plain[i] = (cipher[i] - (prime[offset+ki] - 1)) % 29
  With F-skip: skip F runes (value 0), don't advance ki

Why this might work for ALL unsolved pages:
- Produces FLAT frequency distribution (primes equidistributed mod 29)
- No periodic signal (primes aren't periodic)
- Both properties match all large unsolved pages!

Test: all unsolved pages × prime offsets 0-10000 × F-skip yes/no
"""
import os, sys
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

# Generate large prime sieve
def sieve_primes(limit):
    is_prime = bytearray([1]) * (limit + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = 0
    return [i for i in range(2, limit + 1) if is_prime[i]]

# We need primes up to offset 10000 + max page length (1894)
# prime(12000) ≈ 128,000, so sieve up to 150,000
print("Generating primes...")
primes = sieve_primes(200000)
print(f"Generated {len(primes)} primes (max: {primes[-1]})")

# Precompute totient values mod 29: phi(prime) = prime - 1
totient_mod29 = [(p - 1) % 29 for p in primes]

# Load unsolved pages
pages = {}
for pg in range(17, 55):
    data = load_page(pg)
    if data and len(data) > 0:
        pages[pg] = data
# Also check P71
pg71 = load_page(71)
if pg71: pages[71] = pg71

print(f"Loaded {len(pages)} pages")

# ================================================================
# EXHAUSTIVE TOTIENT TEST
# ================================================================
MAX_OFFSET = 10000
THRESHOLD = 1.4  # Below English ~1.73 but well above random 1.0

print(f"\nTesting totient cipher: offsets 0-{MAX_OFFSET}, threshold IoC > {THRESHOLD}")
print(f"{'='*70}")

results = []

for pg in sorted(pages):
    vals = pages[pg]
    n = len(vals)
    f_positions = set(i for i, v in enumerate(vals) if v == 0)
    non_f_count = n - len(f_positions)
    
    best_ic = 0
    best_params = None
    
    for fskip in [True, False]:
        for offset in range(MAX_OFFSET):
            # Check if we have enough primes
            needed = offset + n + 1
            if needed >= len(totient_mod29):
                break
            
            if fskip:
                result = []
                ki = 0
                for i in range(n):
                    if vals[i] == 0:
                        result.append(0)
                    else:
                        result.append((vals[i] - totient_mod29[offset + ki]) % 29)
                        ki += 1
            else:
                result = [(vals[i] - totient_mod29[offset + i]) % 29 for i in range(n)]
            
            ic = ioc(result)
            
            if ic > best_ic:
                best_ic = ic
                best_params = (offset, fskip, to_eng(result)[:80])
            
            if ic > THRESHOLD:
                fskip_str = "+Fskip" if fskip else ""
                print(f"  P{pg:02d} offset={offset}{fskip_str}: IoC={ic:.4f} | {to_eng(result)[:60]}")
                results.append((pg, offset, fskip, ic, to_eng(result)[:80]))
    
    # Report best for this page even if below threshold
    if best_params:
        offset, fskip, text = best_params
        fskip_str = "+Fskip" if fskip else ""
        print(f"  P{pg:02d} BEST: offset={offset}{fskip_str} IoC={best_ic:.4f} | {text[:50]}")

# ================================================================
# Also try: plain[i] = (cipher[i] + totient) instead of subtract
# ================================================================
print(f"\n{'='*70}")
print("VARIANT: ADD mode totient")
print(f"{'='*70}")

for pg in sorted(pages):
    vals = pages[pg]
    n = len(vals)
    
    best_ic = 0
    best_params = None
    
    for fskip in [True, False]:
        for offset in range(MAX_OFFSET):
            needed = offset + n + 1
            if needed >= len(totient_mod29):
                break
            
            if fskip:
                result = []
                ki = 0
                for i in range(n):
                    if vals[i] == 0:
                        result.append(0)
                    else:
                        result.append((vals[i] + totient_mod29[offset + ki]) % 29)
                        ki += 1
            else:
                result = [(vals[i] + totient_mod29[offset + i]) % 29 for i in range(n)]
            
            ic = ioc(result)
            
            if ic > best_ic:
                best_ic = ic
                best_params = (offset, fskip, to_eng(result)[:80])
            
            if ic > THRESHOLD:
                fskip_str = "+Fskip" if fskip else ""
                print(f"  P{pg:02d} offset={offset}{fskip_str}: IoC={ic:.4f} | {to_eng(result)[:60]}")
    
    if best_params:
        offset, fskip, text = best_params
        fskip_str = "+Fskip" if fskip else ""
        print(f"  P{pg:02d} BEST: offset={offset}{fskip_str} IoC={best_ic:.4f} | {text[:50]}")

# ================================================================
# Also try: BEAUFORT mode: plain[i] = (totient - cipher[i]) % 29
# ================================================================
print(f"\n{'='*70}")
print("VARIANT: BEAUFORT mode totient")
print(f"{'='*70}")

for pg in sorted(pages):
    vals = pages[pg]
    n = len(vals)
    
    best_ic = 0
    best_params = None
    
    for fskip in [True, False]:
        for offset in range(MAX_OFFSET):
            needed = offset + n + 1
            if needed >= len(totient_mod29):
                break
            
            if fskip:
                result = []
                ki = 0
                for i in range(n):
                    if vals[i] == 0:
                        result.append(0)
                    else:
                        result.append((totient_mod29[offset + ki] - vals[i]) % 29)
                        ki += 1
            else:
                result = [(totient_mod29[offset + i] - vals[i]) % 29 for i in range(n)]
            
            ic = ioc(result)
            
            if ic > best_ic:
                best_ic = ic
                best_params = (offset, fskip, to_eng(result)[:80])
            
            if ic > THRESHOLD:
                fskip_str = "+Fskip" if fskip else ""
                print(f"  P{pg:02d} offset={offset}{fskip_str}: IoC={ic:.4f} | {to_eng(result)[:60]}")
    
    if best_params:
        offset, fskip, text = best_params
        fskip_str = "+Fskip" if fskip else ""
        print(f"  P{pg:02d} BEST: offset={offset}{fskip_str} IoC={best_ic:.4f} | {text[:50]}")

# ================================================================
# VARIANT: Use prime directly (not totient)
# plain[i] = (cipher[i] - prime[offset+i]) % 29
# ================================================================
print(f"\n{'='*70}")
print("VARIANT: Prime directly (not totient)")
print(f"{'='*70}")

prime_mod29 = [p % 29 for p in primes]

for pg in sorted(pages):
    vals = pages[pg]
    n = len(vals)
    
    best_ic = 0
    best_params = None
    
    for fskip in [True, False]:
        for offset in range(MAX_OFFSET):
            needed = offset + n + 1
            if needed >= len(prime_mod29):
                break
            
            if fskip:
                result = []
                ki = 0
                for i in range(n):
                    if vals[i] == 0:
                        result.append(0)
                    else:
                        result.append((vals[i] - prime_mod29[offset + ki]) % 29)
                        ki += 1
            else:
                result = [(vals[i] - prime_mod29[offset + i]) % 29 for i in range(n)]
            
            ic = ioc(result)
            
            if ic > best_ic:
                best_ic = ic
                best_params = (offset, fskip, to_eng(result)[:80])
            
            if ic > THRESHOLD:
                fskip_str = "+Fskip" if fskip else ""
                print(f"  P{pg:02d} offset={offset}{fskip_str}: IoC={ic:.4f} | {to_eng(result)[:60]}")
    
    if best_params:
        offset, fskip, text = best_params
        fskip_str = "+Fskip" if fskip else ""
        print(f"  P{pg:02d} BEST: offset={offset}{fskip_str} IoC={best_ic:.4f} | {text[:50]}")

print(f"\n{'='*70}")
print("ALL TOTIENT TESTS COMPLETE")
print(f"{'='*70}")
