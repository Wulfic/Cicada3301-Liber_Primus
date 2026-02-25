"""
DEOR-PRIME FUSION + MISSING PRIMES KEY
========================================
Novel hypothesis from community research:

1. "REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR"
   - What if: map Deor text → GP primes → totient → key?
   - key[i] = (GP_PRIMES[Deor[i]] - 1) % 29
   
2. Missing primes from telnet (73-1223, primes 21-200)
   - These 180 values as a repeating key

3. Deor refrain "Thaes ofereode thisses swa maeg" as key

4. The telnet's first 20 GP primes → indexed into Deor text

5. The "wisdom & folly" files content as potential key source

6. F-rune positions in cipher as key modifier
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

all_primes = sieve_primes(50000)

# Load Deor and tokenize
def load_deor_gp():
    deor_path = 'Analysis/Reference_Docs/deor_poem.txt'
    with open(deor_path, 'r', encoding='utf-8') as f:
        text = f.read().upper()
    
    text = text.replace('Þ', 'TH').replace('þ', 'TH').replace('Ð', 'TH').replace('ð', 'TH')
    text = text.replace('Æ', 'AE').replace('æ', 'AE')
    
    tokens = []
    digraphs = {'TH': 2, 'EO': 12, 'NG': 21, 'OE': 22, 'AE': 25, 'IA': 27, 'EA': 28}
    
    i = 0
    while i < len(text):
        found = False
        if i + 1 < len(text):
            for dg, val in digraphs.items():
                if text[i:i+len(dg)] == dg:
                    tokens.append(val)
                    i += len(dg)
                    found = True
                    break
        if not found:
            ch = text[i]
            if ch in ENG2GP:
                tokens.append(ENG2GP[ch])
            i += 1
    return tokens

deor_gp = load_deor_gp()
print(f"Deor GP tokens: {len(deor_gp)}")
print(f"First 30: {to_eng(deor_gp[:30])}")

# Load unsolved pages
unsolved = {}
for pg in list(range(17, 55)) + [71]:
    data = load_page(pg)
    if data and len(data) > 50:
        unsolved[pg] = data
print(f"Loaded {len(unsolved)} unsolved pages")

# ================================================================
# TEST 1: DEOR-ORDERED PRIMES AS TOTIENT KEY
# ================================================================
print("\n" + "="*70)
print("TEST 1: DEOR-ORDERED PRIMES AS TOTIENT KEY")
print("="*70)

# key[i] = (GP_PRIMES[Deor[i]] - 1) % 29  (totient of Deor-ordered primes)
deor_prime_key = [(GP_PRIMES[v] - 1) % 29 for v in deor_gp]
print(f"Deor-prime totient key: first 30 = {deor_prime_key[:30]}")
print(f"As text: {to_eng(deor_prime_key[:30])}")

for pg in sorted(unsolved):
    cipher = unsolved[pg]
    n = min(len(cipher), len(deor_prime_key))
    if n < 50: continue
    
    for offset in range(min(500, len(deor_prime_key) - n + 1)):
        key = deor_prime_key[offset:offset+n]
        
        for mode in ['sub', 'add', 'beau']:
            if mode == 'sub': plain = [(cipher[i] - key[i]) % 29 for i in range(n)]
            elif mode == 'add': plain = [(cipher[i] + key[i]) % 29 for i in range(n)]
            else: plain = [(key[i] - cipher[i]) % 29 for i in range(n)]
            
            ic = ioc(plain)
            if ic > 1.3 and n > 100:
                text = to_eng(plain[:60])
                print(f"  P{pg:02d} offset={offset} mode={mode}: IoC={ic:.4f}")
                print(f"    {text}")

# Also with F-skip
print("\nWith F-skip:")
for pg in sorted(unsolved):
    cipher = unsolved[pg]
    n = len(cipher)
    best = (0, 0, '')
    
    for offset in range(min(300, len(deor_prime_key))):
        ki = 0
        plain = []
        for i in range(n):
            if cipher[i] == 0:
                plain.append(0)
                continue
            if offset + ki >= len(deor_prime_key): break
            k = deor_prime_key[offset + ki]
            plain.append((cipher[i] - k) % 29)
            ki += 1
        
        if len(plain) == n:
            ic = ioc(plain)
            if ic > best[0]:
                best = (ic, offset, 'fskip_sub')
    
    ic, off, mode = best
    if ic > 1.3 and n > 100:
        ki = 0
        plain = []
        for i in range(n):
            if cipher[i] == 0:
                plain.append(0)
                continue
            k = deor_prime_key[off + ki]
            plain.append((cipher[i] - k) % 29)
            ki += 1
        text = to_eng(plain[:60])
        print(f"  P{pg:02d} offset={off}: IoC={ic:.4f}")
        print(f"    {text}")

# ================================================================
# TEST 2: DIRECT DEOR PRIMES (no totient)
# ================================================================
print("\n" + "="*70)
print("TEST 2: DEOR GP PRIMES DIRECT (key = GP_PRIMES[Deor[i]] % 29)")
print("="*70)

deor_direct_key = [GP_PRIMES[v] % 29 for v in deor_gp]
print(f"First 30: {deor_direct_key[:30]}")

for pg in sorted(unsolved):
    cipher = unsolved[pg]
    n = min(len(cipher), len(deor_direct_key))
    if n < 100: continue
    best = (0, 0, '')
    
    for offset in range(min(500, len(deor_direct_key) - n + 1)):
        key = deor_direct_key[offset:offset+n]
        plain = [(cipher[i] - key[i]) % 29 for i in range(n)]
        ic = ioc(plain)
        if ic > best[0]: best = (ic, offset, 'sub')
        
        plain = [(cipher[i] + key[i]) % 29 for i in range(n)]
        ic = ioc(plain)
        if ic > best[0]: best = (ic, offset, 'add')
    
    ic, off, mode = best
    if ic > 1.2:
        key = deor_direct_key[off:off+len(cipher)]
        if mode == 'sub': plain = [(cipher[i] - key[i]) % 29 for i in range(len(cipher))]
        else: plain = [(cipher[i] + key[i]) % 29 for i in range(len(cipher))]
        text = to_eng(plain[:60])
        print(f"  P{pg:02d}: IoC={ic:.4f} offset={off} mode={mode}")
        print(f"    {text}")

# ================================================================
# TEST 3: MISSING PRIMES KEY (73-1223, the 200 "gap" primes)
# ================================================================
print("\n" + "="*70)
print("TEST 3: MISSING PRIMES FROM TELNET (73-1223)")
print("="*70)

# The telnet listed 2-71 then jumped to 1229. The gap: primes 73 to 1223
telnet_present = set(all_primes[:20])  # 2, 3, 5, ..., 71 (first 20 primes)
gap_start = 73
gap_end = 1223  # Last missing prime before 1229
missing_primes = [p for p in all_primes if gap_start <= p <= gap_end]
print(f"Missing primes: {len(missing_primes)} (from {missing_primes[0]} to {missing_primes[-1]})")

# Use missing primes mod 29 as repeating key
missing_key = [p % 29 for p in missing_primes]
print(f"Missing primes key first 29: {missing_key[:29]}")
print(f"As text: {to_eng(missing_key[:29])}")

for pg in sorted(unsolved):
    cipher = unsolved[pg]
    n = len(cipher)
    
    for mode in ['sub', 'add', 'beau']:
        key = [missing_key[i % len(missing_key)] for i in range(n)]
        if mode == 'sub': plain = [(cipher[i] - key[i]) % 29 for i in range(n)]
        elif mode == 'add': plain = [(cipher[i] + key[i]) % 29 for i in range(n)]
        else: plain = [(key[i] - cipher[i]) % 29 for i in range(n)]
        
        ic = ioc(plain)
        if ic > 1.35 and n > 100:
            text = to_eng(plain[:60])
            print(f"  P{pg:02d} {mode}: IoC={ic:.4f} {text}")

# Also: use missing primes - 1 (totient) as key
print("\nMissing primes totient key (missing_prime - 1) % 29:")
missing_tot_key = [(p - 1) % 29 for p in missing_primes]
for pg in sorted(unsolved):
    cipher = unsolved[pg]
    n = len(cipher)
    key = [missing_tot_key[i % len(missing_tot_key)] for i in range(n)]
    plain = [(cipher[i] - key[i]) % 29 for i in range(n)]
    ic = ioc(plain)
    if ic > 1.35 and n > 100:
        text = to_eng(plain[:60])
        print(f"  P{pg:02d} sub: IoC={ic:.4f} {text}")

# ================================================================
# TEST 4: DEOR REFRAIN AS KEY
# ================================================================
print("\n" + "="*70)
print("TEST 4: DEOR REFRAIN 'THAES OFEREODE THISSES SWA MAEG'")
print("="*70)

# The refrain appears 7 times in the Deor
# "Þæs ofereode, þisses swa mæg" → TH AE S | O F E R E O D E | TH I S S E S | S W A | M AE G
refrain_text = "THAESOFEREODETHISSESSWAMAEG"
# Tokenize manually
refrain_gp = []
refrain_tokens = [
    ('TH', 2), ('AE', 25), ('S', 15),
    ('O', 3), ('F', 0), ('E', 18), ('R', 4), ('E', 18), ('O', 3), ('D', 23), ('E', 18),
    ('TH', 2), ('I', 10), ('S', 15), ('S', 15), ('E', 18), ('S', 15),
    ('S', 15), ('W', 7), ('A', 24),
    ('M', 19), ('AE', 25), ('G', 6)
]
refrain_gp = [v for _, v in refrain_tokens]
print(f"Refrain GP ({len(refrain_gp)} values): {to_eng(refrain_gp)}")

for pg in sorted(unsolved):
    cipher = unsolved[pg]
    n = len(cipher)
    
    for mode in ['sub', 'add', 'beau']:
        key = [refrain_gp[i % len(refrain_gp)] for i in range(n)]
        if mode == 'sub': plain = [(cipher[i] - key[i]) % 29 for i in range(n)]
        elif mode == 'add': plain = [(cipher[i] + key[i]) % 29 for i in range(n)]
        else: plain = [(key[i] - cipher[i]) % 29 for i in range(n)]
        ic = ioc(plain)
        if ic > 1.35 and n > 100:
            text = to_eng(plain[:60])
            print(f"  P{pg:02d} {mode}: IoC={ic:.4f} {text}")

# With F-skip
for pg in sorted(unsolved):
    cipher = unsolved[pg]
    n = len(cipher)
    for mode in ['sub', 'add']:
        ki = 0
        plain = []
        for i in range(n):
            if cipher[i] == 0:
                plain.append(0)
                continue
            k = refrain_gp[ki % len(refrain_gp)]
            if mode == 'sub': plain.append((cipher[i] - k) % 29)
            else: plain.append((cipher[i] + k) % 29)
            ki += 1
        ic = ioc(plain)
        if ic > 1.35 and n > 100:
            text = to_eng(plain[:60])
            print(f"  P{pg:02d} fskip_{mode}: IoC={ic:.4f} {text}")

# ================================================================
# TEST 5: INTERLEAVED DEOR + PRIMES (combine both)
# ================================================================
print("\n" + "="*70)
print("TEST 5: COMBINED DEOR+PRIME KEYS")
print("="*70)

# 5A: key[i] = (Deor[i] + prime[i]) % 29
print("5A: key = (Deor[i] + prime[i]) % 29")
for pg in sorted(unsolved):
    cipher = unsolved[pg]
    n = min(len(cipher), len(deor_gp))
    if n < 100: continue
    best = (0, 0, '')
    
    for offset in range(min(200, len(deor_gp) - n + 1)):
        key = [(deor_gp[offset+i] + all_primes[i] % 29) % 29 for i in range(n)]
        plain = [(cipher[i] - key[i]) % 29 for i in range(n)]
        ic = ioc(plain)
        if ic > best[0]: best = (ic, offset, 'sub')
    
    ic, off, mode = best
    if ic > 1.25:
        key = [(deor_gp[off+i] + all_primes[i] % 29) % 29 for i in range(len(cipher))]
        plain = [(cipher[i] - key[i]) % 29 for i in range(len(cipher))]
        text = to_eng(plain[:60])
        print(f"  P{pg:02d}: IoC={ic:.4f} offset={off}")
        print(f"    {text}")

# 5B: key[i] = (Deor[i] * prime[i]) % 29
print("\n5B: key = (Deor[i] * prime[i]) % 29")
for pg in sorted(unsolved):
    cipher = unsolved[pg]
    n = min(len(cipher), len(deor_gp))
    if n < 100: continue
    best = (0, 0, '')
    
    for offset in range(min(200, len(deor_gp) - n + 1)):
        key = [(deor_gp[offset+i] * all_primes[i]) % 29 for i in range(n)]
        plain = [(cipher[i] - key[i]) % 29 for i in range(n)]
        ic = ioc(plain)
        if ic > best[0]: best = (ic, offset, 'sub')
    
    ic, off, mode = best
    if ic > 1.25:
        print(f"  P{pg:02d}: IoC={ic:.4f} offset={off}")

# 5C: key[i] = Deor[prime[i] % len(Deor)]  (primes index into Deor)
print("\n5C: key[i] = Deor[prime[i] % len(Deor)]")
for pg in sorted(unsolved):
    cipher = unsolved[pg]
    n = len(cipher)
    key = [deor_gp[all_primes[i] % len(deor_gp)] for i in range(n)]
    
    for mode in ['sub', 'add']:
        if mode == 'sub': plain = [(cipher[i] - key[i]) % 29 for i in range(n)]
        else: plain = [(cipher[i] + key[i]) % 29 for i in range(n)]
        ic = ioc(plain)
        if ic > 1.3 and n > 100:
            text = to_eng(plain[:60])
            print(f"  P{pg:02d} {mode}: IoC={ic:.4f} {text}")

# Also with offset
for pg in sorted(unsolved):
    cipher = unsolved[pg]
    n = len(cipher)
    best = (0, 0, '')
    for off in range(500):
        key = [deor_gp[(all_primes[off+i]) % len(deor_gp)] for i in range(n)]
        plain = [(cipher[i] - key[i]) % 29 for i in range(n)]
        ic = ioc(plain)
        if ic > best[0]: best = (ic, off, 'sub')
    ic, off, mode = best
    if ic > 1.25 and n > 100:
        print(f"  P{pg:02d}: IoC={ic:.4f} prime_offset={off}")

# ================================================================
# TEST 6: TOTIENT WITH DEOR-PERMUTED PRIME ORDERING
# ================================================================
print("\n" + "="*70)
print("TEST 6: TOTIENT WITH DEOR-BASED PRIME REORDERING")
print("="*70)

# "Rearranging the primes" = use Deor text to determine which prime to use at each position
# For position i: look up Deor[i mod deor_len] = value v
# Then use the v-th prime (not the i-th prime) in the totient formula

for pg in sorted(unsolved):
    cipher = unsolved[pg]
    n = len(cipher)
    
    for offset in range(min(200, len(deor_gp))):
        key = []
        for i in range(n):
            deor_val = deor_gp[(offset + i) % len(deor_gp)]
            # Map Deor value to a prime index
            prime_idx = deor_val  # Deor value 0-28 maps to that prime index
            key.append((all_primes[prime_idx] - 1) % 29)
        
        for mode in ['sub', 'add']:
            if mode == 'sub': plain = [(cipher[i] - key[i]) % 29 for i in range(n)]
            else: plain = [(cipher[i] + key[i]) % 29 for i in range(n)]
            ic = ioc(plain)
            if ic > 1.35 and n > 100:
                text = to_eng(plain[:60])
                print(f"  P{pg:02d} offset={offset} {mode}: IoC={ic:.4f}")
                print(f"    {text}")

# ================================================================  
# TEST 7: MULTIPLICATIVE INVERSE CIPHER
# ================================================================
print("\n" + "="*70)
print("TEST 7: MULTIPLICATIVE CIPHER (affine with GP primes)")
print("="*70)

# For each rune with GP index v, compute: v * GP_PRIMES[key] mod 29
# This is an affine cipher where the multiplier comes from the key
for pg in sorted(unsolved):
    cipher = unsolved[pg]
    n = len(cipher)
    if n < 100: continue
    
    # Try all multipliers that have inverses mod 29 (gcd(m, 29) = 1, i.e., all m != 0)
    for mult in range(1, 29):
        # Check if mult has inverse mod 29
        try:
            inv = pow(mult, -1, 29)
        except:
            continue
        
        plain = [(v * inv) % 29 for v in cipher]
        ic = ioc(plain)
        if ic > 1.4:
            text = to_eng(plain[:60])
            print(f"  P{pg:02d} mult={mult}: IoC={ic:.4f} {text}")

# ================================================================
# TEST 8: BEAUFORT WITH DEOR (all positions)
# ================================================================
print("\n" + "="*70)  
print("TEST 8: PRIME-TOTIENT BEAUFORT WITH DEOR KEY")
print("="*70)

# key[i] = (GP_PRIMES[Deor[i]] - 1) mod 29
# plain[i] = key[i] - cipher[i] mod 29  (Beaufort)
for pg in sorted(unsolved):
    cipher = unsolved[pg]
    n = min(len(cipher), len(deor_prime_key))
    if n < 100: continue
    best = (0, 0, '')
    
    for offset in range(min(500, len(deor_prime_key) - n + 1)):
        key = deor_prime_key[offset:offset+n]
        plain = [(key[i] - cipher[i]) % 29 for i in range(n)]
        ic = ioc(plain)
        if ic > best[0]: best = (ic, offset, 'beau')
    
    ic, off, mode = best
    if ic > 1.2:
        key = deor_prime_key[off:off+n]
        plain = [(key[i] - cipher[i]) % 29 for i in range(n)]
        text = to_eng(plain[:60])
        print(f"  P{pg:02d}: IoC={ic:.4f} offset={off}")

# ================================================================
# SUMMARY: Report best results across all tests
# ================================================================
print("\n" + "="*70)
print("ALL DEOR-PRIME FUSION TESTS COMPLETE")
print("="*70)
