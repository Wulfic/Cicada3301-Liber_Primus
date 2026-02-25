"""
GEMATRIA PRIME VALUE CIPHER TESTS + DEOR RUNNING KEY + EXTENDED VIGENERE
=========================================================================
Key insight from wiki: "THE PRIMES ARE SACRED, THE TOTIENT FUNCTION IS SACRED"
P19 hint: "REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR"

What if the cipher operates on GEMATRIA PRIME VALUES (2,3,5,...,109) instead of 
ordinal GP indices (0-28)?

Also: exhaustive Deor running key at all 1047 offsets.
Also: extended Vigenere period testing (40-200) on large pages.
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

# GEMATRIA PRIME VALUES - the actual primes assigned to each rune
GP_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109]

# Mapping: ordinal index -> prime value
IDX_TO_PRIME = {i: GP_PRIMES[i] for i in range(29)}
# Reverse: prime value -> ordinal index
PRIME_TO_IDX = {GP_PRIMES[i]: i for i in range(29)}

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

def keyword_to_gp(word):
    return [ENG2GP[c] for c in word.upper() if c in ENG2GP]

# Load Deor poem
def load_deor():
    """Load Deor poem and tokenize to GP values"""
    deor_path = 'Analysis/Reference_Docs/deor_poem.txt'
    if not os.path.exists(deor_path):
        for p in ['LiberPrimus/reference/deor.txt', 'Analysis/Reference_Docs/deor.txt']:
            if os.path.exists(p):
                deor_path = p
                break
    
    if not os.path.exists(deor_path):
        return None
    
    with open(deor_path, 'r', encoding='utf-8') as f:
        text = f.read().upper()
    
    # OE tokenizer
    tokens = []
    digraphs = ['TH', 'EO', 'NG', 'OE', 'AE', 'IA', 'EA']
    text = text.replace('Þ', 'TH').replace('þ', 'TH').replace('Ð', 'TH').replace('ð', 'TH').replace('Æ', 'AE').replace('æ', 'AE')
    
    i = 0
    while i < len(text):
        if i + 1 < len(text):
            digraph = text[i:i+2]
            if digraph in digraphs and digraph in ENG2GP:
                # Map individual letters for digraphs not in ENG2GP
                pass
            # Try as individual letter first
        ch = text[i]
        if ch in ENG2GP:
            # Check digraphs first
            found_digraph = False
            if i + 1 < len(text):
                for dg in digraphs:
                    if text[i:i+len(dg)] == dg:
                        # Map as single GP value
                        dg_map = {'TH': 2, 'EO': 12, 'NG': 21, 'OE': 22, 'AE': 25, 'IA': 27, 'EA': 28}
                        if dg in dg_map:
                            tokens.append(dg_map[dg])
                            i += len(dg)
                            found_digraph = True
                            break
            if not found_digraph:
                tokens.append(ENG2GP[ch])
                i += 1
        else:
            i += 1
    return tokens

# Load all unsolved pages
unsolved = {}
for pg in list(range(17, 55)) + [71]:
    data = load_page(pg)
    if data and len(data) > 50:
        unsolved[pg] = data

print(f"Loaded {len(unsolved)} unsolved pages")

# ================================================================
# TEST 1: GEMATRIA PRIME VALUE ARITHMETIC
# ================================================================
print("\n" + "="*70)
print("TEST 1: GEMATRIA PRIME ARITHMETIC")
print("="*70)

def gp_prime_sub(cipher, key):
    """Subtract using Gematria prime values, result mapped back through primes"""
    plain = []
    for i in range(len(cipher)):
        c_prime = IDX_TO_PRIME[cipher[i]]
        k_prime = IDX_TO_PRIME[key[i % len(key)]]
        # Subtract in prime space, mod 113 (next prime after 109)
        result_prime = (c_prime - k_prime) % 113
        # Find closest prime in our set
        if result_prime in PRIME_TO_IDX:
            plain.append(PRIME_TO_IDX[result_prime])
        else:
            # Not a valid GP prime - indicates wrong approach or find nearest
            plain.append(result_prime % 29)
    return plain

def gp_prime_add(cipher, key):
    """Add using Gematria prime values"""
    plain = []
    for i in range(len(cipher)):
        c_prime = IDX_TO_PRIME[cipher[i]]
        k_prime = IDX_TO_PRIME[key[i % len(key)]]
        result_prime = (c_prime + k_prime) % 113
        if result_prime in PRIME_TO_IDX:
            plain.append(PRIME_TO_IDX[result_prime])
        else:
            plain.append(result_prime % 29)
    return plain

# Test with various keywords  
keywords = ['DIVINITY', 'PRIMES', 'DEOR', 'PATH', 'REARRANGING', 'WELCOME',
            'PILGRIM', 'WISDOM', 'INSTAR', 'CONSUMPTION', 'ADHERENCE',
            'CIRCUMFERENCE', 'PRESERVATION', 'PRIMALITY', 'EMERGENCE',
            'AN', 'THE', 'SACRED', 'TOTIENT', 'FIRFUMFERENFE']

print("\nGP Prime Arithmetic with keywords:")
for kw in keywords:
    seed = keyword_to_gp(kw)
    if not seed: continue
    for pg in sorted(unsolved):
        cipher = unsolved[pg]
        for mode_name, mode_fn in [('prime_sub', gp_prime_sub), ('prime_add', gp_prime_add)]:
            plain = mode_fn(cipher, seed)
            ic = ioc(plain)
            if ic > 1.4:
                text = to_eng(plain[:60])
                print(f"  P{pg:02d} {mode_name} key={kw}  IoC={ic:.4f}  {text}")

# ================================================================
# TEST 2: PRIME PERMUTATION CIPHER
# ================================================================
print("\n" + "="*70)
print("TEST 2: ALPHABET PERMUTATION VIA PRIMES")
print("="*70)

# "Rearranging the primes" = permuting the alphabet using prime indices
# Try various prime-based permutations

# Permutation 1: Map index i to prime[i] mod 29
perm1 = [GP_PRIMES[i] % 29 for i in range(29)]
print(f"Perm1 (prime mod 29): {perm1}")

# Check if it's a valid permutation (all unique)
if len(set(perm1)) == 29:
    print("  Valid permutation!")
    inv_perm1 = [0]*29
    for i in range(29):
        inv_perm1[perm1[i]] = i
    
    for pg in sorted(unsolved):
        cipher = unsolved[pg]
        plain = [inv_perm1[v] for v in cipher]
        ic = ioc(plain)
        if ic > 1.4:
            print(f"  P{pg:02d}: IoC={ic:.4f}  {to_eng(plain[:60])}")
else:
    print(f"  NOT a valid permutation (collisions: {29 - len(set(perm1))} duplicates)")
    # Still try applying it
    for pg in sorted(unsolved):
        cipher = unsolved[pg]
        plain = [GP_PRIMES[v] % 29 for v in cipher]
        ic = ioc(plain)
        if ic > 1.4:
            print(f"  P{pg:02d} (forward): IoC={ic:.4f}  {to_eng(plain[:60])}")

# Permutation 2: Sort primes by value, use index order of sorted primes
# The primes are already sorted. What about sorting them by a different criterion?

# Permutation 3: Map each cipher value through (prime * k) % 29 for various k
print("\nMultiplicative prime mapping: (prime[cipher] * k) % 29")
for k in range(1, 29):
    mapping = [(GP_PRIMES[i] * k) % 29 for i in range(29)]
    if len(set(mapping)) == 29:  # Valid permutation
        inv_map = [0]*29
        for i in range(29):
            inv_map[mapping[i]] = i
        
        for pg in sorted(unsolved):
            cipher = unsolved[pg]
            plain = [inv_map[v] for v in cipher]
            ic = ioc(plain)
            if ic > 1.5:
                print(f"  k={k} P{pg:02d}: IoC={ic:.4f}  {to_eng(plain[:60])}")

# ================================================================
# TEST 3: DEOR RUNNING KEY AT ALL OFFSETS
# ================================================================
print("\n" + "="*70)
print("TEST 3: DEOR RUNNING KEY AT ALL OFFSETS")
print("="*70)

deor = load_deor()
if deor:
    print(f"Deor GP values: {len(deor)} tokens")
    print(f"First 30: {to_eng(deor[:30])}")
    
    # For each page, try Deor starting at each offset
    best_per_page = {}
    for pg in sorted(unsolved):
        cipher = unsolved[pg]
        n = len(cipher)
        best = (0, 0, '')
        
        for offset in range(len(deor) - n + 1):
            key = deor[offset:offset+n]
            # SUB mode
            plain_sub = [(cipher[i] - key[i]) % 29 for i in range(n)]
            ic_sub = ioc(plain_sub)
            if ic_sub > best[0]:
                best = (ic_sub, offset, 'sub')
            
            # ADD mode
            plain_add = [(cipher[i] + key[i]) % 29 for i in range(n)]
            ic_add = ioc(plain_add)
            if ic_add > best[0]:
                best = (ic_add, offset, 'add')
            
            # BEAU mode
            plain_beau = [(key[i] - cipher[i]) % 29 for i in range(n)]
            ic_beau = ioc(plain_beau)
            if ic_beau > best[0]:
                best = (ic_beau, offset, 'beau')
        
        ic, off, mode = best
        # Compute the actual plaintext
        key = deor[off:off+len(cipher)]
        if mode == 'sub':
            plain = [(cipher[i] - key[i]) % 29 for i in range(len(cipher))]
        elif mode == 'add':
            plain = [(cipher[i] + key[i]) % 29 for i in range(len(cipher))]
        else:
            plain = [(key[i] - cipher[i]) % 29 for i in range(len(cipher))]
        
        best_per_page[pg] = (ic, off, mode)
        
        if ic > 1.2:
            text = to_eng(plain[:60])
            print(f"  P{pg:02d} (n={len(cipher)}): best IoC={ic:.4f} offset={off} mode={mode}")
            print(f"    {text}")
    
    # Also try with F-skip
    print("\nDeor running key with F-skip:")
    for pg in sorted(unsolved):
        cipher = unsolved[pg]
        n = len(cipher)
        best = (0, 0, '')
        
        for offset in range(min(len(deor), 500)):  # limit offsets for speed
            ki = 0
            plain = []
            for i in range(n):
                if cipher[i] == 0:
                    plain.append(0)
                    continue
                if offset + ki >= len(deor):
                    break
                k = deor[offset + ki]
                plain.append((cipher[i] - k) % 29)
                ki += 1
            
            if len(plain) == n:
                ic = ioc(plain)
                if ic > best[0]:
                    best = (ic, offset, 'fskip_sub')
        
        ic, off, mode = best
        if ic > 1.2:
            # Reconstruct
            ki = 0
            plain = []
            for i in range(n):
                if cipher[i] == 0:
                    plain.append(0)
                    continue
                k = deor[off + ki]
                plain.append((cipher[i] - k) % 29)
                ki += 1
            text = to_eng(plain[:60])
            print(f"  P{pg:02d}: best IoC={ic:.4f} offset={off} mode=fskip_sub")
            print(f"    {text}")
else:
    print("DEOR NOT FOUND - trying to locate...")
    import glob
    deor_files = glob.glob('**/*deor*', recursive=True)
    print(f"  Files matching 'deor': {deor_files}")

# ================================================================
# TEST 4: EXTENDED VIGENERE PERIOD TESTING (periods 40-200)
# ================================================================
print("\n" + "="*70)
print("TEST 4: EXTENDED VIGENERE (periods 40-200, large pages)")
print("="*70)

large_pages = {pg: v for pg, v in unsolved.items() if len(v) > 700}
print(f"Testing {len(large_pages)} pages with >700 runes: {sorted(large_pages.keys())}")

for pg in sorted(large_pages):
    vals = large_pages[pg]
    best = (0, 0)
    for period in range(40, min(201, len(vals)//3)):
        subs = [[] for _ in range(period)]
        for i, v in enumerate(vals):
            subs[i % period].append(v)
        valid_subs = [s for s in subs if len(s) > 1]
        if valid_subs:
            avg_ioc = sum(ioc(s) for s in valid_subs) / len(valid_subs)
            if avg_ioc > best[0]:
                best = (avg_ioc, period)
    
    ic, period = best
    print(f"  P{pg:02d} (n={len(vals)}): best period={period} IoC={ic:.4f}")
    if ic > 1.3:
        print(f"    ** SIGNIFICANT SIGNAL **")

# ================================================================
# TEST 5: VIGENERE WITH GP PRIMES AS KEY (instead of indices)
# ================================================================
print("\n" + "="*70)
print("TEST 5: PRIMES AS VIGENERE KEY (sequential primes as key stream)")
print("="*70)

# Key[i] = prime[i] % 29 (using sequential primes as key, reduced mod 29)
def sieve_primes(limit):
    """Simple sieve of Eratosthenes"""
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = False
    return [i for i in range(2, limit + 1) if is_prime[i]]

primes = sieve_primes(50000)

for pg in sorted(unsolved):
    cipher = unsolved[pg]
    n = len(cipher)
    
    # Use first n primes as key (mod 29)
    key = [primes[i] % 29 for i in range(n)]
    
    for mode_name in ['sub', 'add', 'beau']:
        if mode_name == 'sub':
            plain = [(cipher[i] - key[i]) % 29 for i in range(n)]
        elif mode_name == 'add':
            plain = [(cipher[i] + key[i]) % 29 for i in range(n)]
        else:
            plain = [(key[i] - cipher[i]) % 29 for i in range(n)]
        
        ic = ioc(plain)
        if ic > 1.3:
            text = to_eng(plain[:60])
            print(f"  P{pg:02d} {mode_name}: IoC={ic:.4f}  {text}")

# Also try with offset (skip first K primes)
print("\nWith prime offset 0-200:")
for pg in sorted(unsolved):
    cipher = unsolved[pg]
    n = len(cipher)
    best = (0, 0, '')
    
    for offset in range(min(201, len(primes) - n)):
        key = [primes[offset + i] % 29 for i in range(n)]
        
        plain_sub = [(cipher[i] - key[i]) % 29 for i in range(n)]
        ic_sub = ioc(plain_sub)
        if ic_sub > best[0]:
            best = (ic_sub, offset, 'sub')
        
        plain_add = [(cipher[i] + key[i]) % 29 for i in range(n)]
        ic_add = ioc(plain_add)
        if ic_add > best[0]:
            best = (ic_add, offset, 'add')
    
    ic, off, mode = best
    if ic > 1.25:
        key = [primes[off + i] % 29 for i in range(len(cipher))]
        if mode == 'sub':
            plain = [(cipher[i] - key[i]) % 29 for i in range(len(cipher))]
        else:
            plain = [(cipher[i] + key[i]) % 29 for i in range(len(cipher))]
        text = to_eng(plain[:60])
        print(f"  P{pg:02d}: best IoC={ic:.4f} offset={off} mode={mode}")
        print(f"    {text}")

# ================================================================
# TEST 6: REARRANGED PRIMES - PRIME VALUE BASED PERMUTATION CIPHER
# ================================================================
print("\n" + "="*70)
print("TEST 6: REARRANGED PRIMES INTERPRETATION")
print("="*70)

# Interpretation: "Rearranging the prime numbers" means applying a PERMUTATION
# to the ciphertext based on prime positions.
# Read cipher at prime positions first, then composite positions.

for pg in sorted(unsolved):
    cipher = unsolved[pg]
    n = len(cipher)
    
    # Extract prime-indexed values, then composite
    prime_set = set(sieve_primes(n + 100))
    prime_pos = [i for i in range(n) if i in prime_set]
    comp_pos = [i for i in range(n) if i not in prime_set]
    
    # Rearrangement 1: prime positions first, then composites
    rearranged1 = [cipher[i] for i in prime_pos] + [cipher[i] for i in comp_pos]
    ic1 = ioc(rearranged1)  # IoC doesn't change with permutation!
    
    # But what about: READ the text by interleaving prime and non-prime positions?
    # This would change the text's structure but not IoC
    
    # More useful: use prime factorization to determine a columnar read pattern
    # Try reading the cipher arranged in columns of width p, for various primes p
    for width in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]:
        if width >= n: continue
        # Fill row by row, read column by column
        rows = (n + width - 1) // width
        cols_read = []
        for col in range(width):
            for row in range(rows):
                idx = row * width + col
                if idx < n:
                    cols_read.append(cipher[idx])
        
        # Now try Vigenere with DIVINITY key on the rearranged text
        key = keyword_to_gp('DIVINITY')
        plain = [(cols_read[i] - key[i % len(key)]) % 29 for i in range(len(cols_read))]
        ic = ioc(plain)
        if ic > 1.4:
            text = to_eng(plain[:60])
            print(f"  P{pg:02d} width={width} DIVINITY: IoC={ic:.4f}  {text}")

print("\n" + "="*70)
print("ALL TESTS COMPLETE")
print("="*70)
