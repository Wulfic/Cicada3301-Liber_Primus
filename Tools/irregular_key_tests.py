"""
IRREGULAR KEY ADVANCEMENT + CONCATENATED ANALYSIS + NOVEL APPROACHES
=====================================================================
The solved LP pages use F-skip (don't advance key when cipher=F).
What if unsolved pages use DIFFERENT irregular key advancement rules?

This would produce flat IoC while using a SHORT key, defeating standard
periodic IoC analysis.

Also: test concatenated pages and novel cipher structures.
"""
import os, sys
from collections import Counter
from itertools import product

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

def keyword_to_gp(word):
    return [ENG2GP[c] for c in word.upper() if c in ENG2GP]

def sieve_primes(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = False
    return set(i for i in range(2, limit + 1) if is_prime[i])

prime_set = sieve_primes(200)

# Load pages
unsolved = {}
for pg in list(range(17, 55)) + [71]:
    data = load_page(pg)
    if data and len(data) > 50:
        unsolved[pg] = data

print(f"Loaded {len(unsolved)} unsolved pages")

# Keywords to test
keywords = ['DIVINITY', 'PRIMES', 'FIRFUMFERENFE', 'DEOR', 'SACRED', 'TOTIENT',
            'WELCOME', 'WISDOM', 'INSTAR', 'PILGRIM', 'CONSUMPTION',
            'ADHERENCE', 'PRESERVATION', 'PRIMALITY', 'EMERGENCE',
            'CIRCUMFERENCE', 'PATH', 'REARRANGING']

# ================================================================
# TEST 1: IRREGULAR KEY ADVANCEMENT PATTERNS
# ================================================================
print("\n" + "="*70)
print("TEST 1: IRREGULAR KEY ADVANCEMENT PATTERNS")
print("="*70)

def decrypt_irregular_key(cipher, key, skip_rule, mode='sub'):
    """
    Decrypt with irregular key advancement.
    skip_rule: function(cipher_val, plain_val, position) -> bool
    If skip_rule returns True, DON'T advance key.
    """
    plain = []
    ki = 0
    for i in range(len(cipher)):
        k = key[ki % len(key)]
        if mode == 'sub': p = (cipher[i] - k) % 29
        elif mode == 'add': p = (cipher[i] + k) % 29
        else: p = (k - cipher[i]) % 29  # beau
        
        plain.append(p)
        
        # Check if we should advance the key
        if not skip_rule(cipher[i], p, i):
            ki += 1
    
    return plain

# Define various skip rules
skip_rules = {
    'f_skip': lambda c, p, i: c == 0,           # Original: skip when cipher=F
    'f_skip_plain': lambda c, p, i: p == 0,      # Skip when PLAIN=F (after decryption)
    'prime_skip': lambda c, p, i: c in prime_set, # Skip when cipher val is prime GP index 
    'even_skip': lambda c, p, i: c % 2 == 0,     # Skip when cipher val is even
    'odd_skip': lambda c, p, i: c % 2 == 1,      # Skip when cipher val is odd
    'gt14_skip': lambda c, p, i: c > 14,         # Skip when cipher > 14
    'pos_prime': lambda c, p, i: (i+1) in prime_set, # Skip at prime positions
    'both_f': lambda c, p, i: c == 0 or p == 0,  # Skip when either cipher or plain = F
}

for rule_name, rule_fn in skip_rules.items():
    hits = []
    for pg in sorted(unsolved):
        cipher = unsolved[pg]
        if len(cipher) < 100: continue
        
        for kw in keywords:
            key = keyword_to_gp(kw)
            if not key: continue
            
            for mode in ['sub', 'add', 'beau']:
                plain = decrypt_irregular_key(cipher, key, rule_fn, mode)
                ic = ioc(plain)
                if ic > 1.4:
                    text = to_eng(plain[:50])
                    hits.append(f"    P{pg:02d} {mode} key={kw}: IoC={ic:.4f} {text}")
    
    if hits:
        print(f"\n  Rule: {rule_name}")
        for h in hits[:10]:  # Limit output
            print(h)
    else:
        # Report best
        best = (0, '', '', '')
        for pg in sorted(unsolved):
            cipher = unsolved[pg]
            if len(cipher) < 200: continue
            for kw in ['DIVINITY', 'PRIMES', 'FIRFUMFERENFE', 'SACRED']:
                key = keyword_to_gp(kw)
                if not key: continue
                plain = decrypt_irregular_key(cipher, key, rule_fn, 'sub')
                ic = ioc(plain)
                if ic > best[0]:
                    best = (ic, f"P{pg:02d}", kw, 'sub')
        print(f"  {rule_name}: best IoC={best[0]:.4f} {best[1]} key={best[2]}")

# ================================================================
# TEST 2: VARIABLE STEP KEY ADVANCEMENT
# ================================================================
print("\n" + "="*70)
print("TEST 2: VARIABLE STEP KEY ADVANCEMENT")
print("="*70)

def decrypt_variable_step(cipher, key, step_fn, mode='sub'):
    """Key advances by step_fn(cipher_val, plain_val, position) each step."""
    plain = []
    ki = 0
    for i in range(len(cipher)):
        k = key[ki % len(key)]
        if mode == 'sub': p = (cipher[i] - k) % 29
        elif mode == 'add': p = (cipher[i] + k) % 29
        else: p = (k - cipher[i]) % 29
        
        plain.append(p)
        step = step_fn(cipher[i], p, i)
        ki += step
    return plain

# Step functions
step_fns = {
    'step_cipher_mod': lambda c, p, i: (c % 5) + 1,     # Step by (cipher mod 5) + 1
    'step_plain_mod': lambda c, p, i: (p % 5) + 1,      # Step by plain mod 5 + 1
    'step_cipher_val': lambda c, p, i: c + 1,            # Step by cipher value + 1
    'step_position': lambda c, p, i: (i % 7) + 1,       # Step by position pattern
    'step_prime': lambda c, p, i: 1 if c not in prime_set else 2,  # Double step for primes
}

for step_name, step_fn in step_fns.items():
    best = (0, '', '', '')
    for pg in sorted(unsolved):
        cipher = unsolved[pg]
        if len(cipher) < 200: continue
        for kw in ['DIVINITY', 'PRIMES', 'FIRFUMFERENFE', 'DEOR', 'SACRED']:
            key = keyword_to_gp(kw)
            if not key: continue
            for mode in ['sub', 'add']:
                plain = decrypt_variable_step(cipher, key, step_fn, mode)
                ic = ioc(plain)
                if ic > best[0]:
                    best = (ic, f"P{pg:02d}", kw, mode)
                    if ic > 1.4:
                        text = to_eng(plain[:50])
                        print(f"  {step_name}: P{pg:02d} {mode} key={kw}: IoC={ic:.4f} {text}")
    
    print(f"  {step_name}: best IoC={best[0]:.4f} {best[1]} key={best[2]} mode={best[3]}")

# ================================================================
# TEST 3: GROMARK / RUNNING KEY DERIVED FROM PLAINTEXT
# ================================================================
print("\n" + "="*70)
print("TEST 3: GROMARK-STYLE (key derived from plaintext digits/values)")
print("="*70)

def gromark_decrypt(cipher, initial_key, mode='sub'):
    """
    Gromark: key advances based on running sum of plaintext values.
    Key[i] = sum of first i plaintext values mod 29.
    Initial key provides the starting key.
    """
    plain = []
    running = 0
    for i in range(len(cipher)):
        k = (initial_key + running) % 29
        if mode == 'sub': p = (cipher[i] - k) % 29
        elif mode == 'add': p = (cipher[i] + k) % 29
        else: p = (k - cipher[i]) % 29
        plain.append(p)
        running = (running + p) % 29
    return plain

def gromark_decrypt_v2(cipher, seed_key, mode='sub'):
    """
    Variant: key[i] = seed_key[i mod len(seed)] + running_sum
    """
    plain = []
    running = 0
    for i in range(len(cipher)):
        k = (seed_key[i % len(seed_key)] + running) % 29
        if mode == 'sub': p = (cipher[i] - k) % 29
        elif mode == 'add': p = (cipher[i] + k) % 29
        else: p = (k - cipher[i]) % 29
        plain.append(p)
        running = (running + p) % 29
    return plain

# Test Gromark v1 (single seed value)
print("\n3A: Gromark v1 (single seed + running plaintext sum):")
for pg in sorted(unsolved):
    cipher = unsolved[pg]
    if len(cipher) < 100: continue
    best = (0, 0, '')
    for seed in range(29):
        for mode in ['sub', 'add', 'beau']:
            plain = gromark_decrypt(cipher, seed, mode)
            ic = ioc(plain)
            if ic > best[0]:
                best = (ic, seed, mode)
    ic, seed, mode = best
    if ic > 1.3:
        plain = gromark_decrypt(cipher, seed, mode)
        text = to_eng(plain[:50])
        print(f"  P{pg:02d}: IoC={ic:.4f} seed={seed} mode={mode} {text}")

# Test Gromark v2 (keyword + running sum)
print("\n3B: Gromark v2 (keyword + running plaintext sum):")
for kw in ['DIVINITY', 'PRIMES', 'DEOR', 'SACRED']:
    key = keyword_to_gp(kw)
    for pg in sorted(unsolved):
        cipher = unsolved[pg]
        if len(cipher) < 200: continue
        for mode in ['sub', 'add']:
            plain = gromark_decrypt_v2(cipher, key, mode)
            ic = ioc(plain)
            if ic > 1.35:
                text = to_eng(plain[:50])
                print(f"  P{pg:02d} key={kw} mode={mode}: IoC={ic:.4f} {text}")

# ================================================================
# TEST 4: CONCATENATED PAGE ANALYSIS
# ================================================================
print("\n" + "="*70)
print("TEST 4: CONCATENATED PAGE ANALYSIS")
print("="*70)

# Concatenate all unsolved pages in order
all_concat = []
page_order = sorted(unsolved.keys())
for pg in page_order:
    all_concat.extend(unsolved[pg])

print(f"Total concatenated: {len(all_concat)} runes from {len(page_order)} pages")
print(f"Concatenated IoC: {ioc(all_concat):.4f}")

# Test periodic IoC on concatenated text
print("\nPeriodic IoC of concatenated text:")
for period in [8, 14, 29, 43, 58, 87, 116, 145, 203, 271, 290, 400, 500, 812]:
    subs = [[] for _ in range(period)]
    for i, v in enumerate(all_concat):
        subs[i % period].append(v)
    valid = [s for s in subs if len(s) > 5]
    if valid:
        avg_ioc = sum(ioc(s) for s in valid) / len(valid)
        print(f"  Period {period:4d}: avg IoC={avg_ioc:.4f} (sublength ~{len(all_concat)//period})")

# Concatenate in PRIME page order
prime_pages = [pg for pg in page_order if pg in prime_set]
comp_pages = [pg for pg in page_order if pg not in prime_set]
print(f"\nPrime-numbered pages: {prime_pages}")
print(f"Composite-numbered pages: {comp_pages}")

# Try: decrypt concatenated prime pages with DIVINITY
prime_concat = []
for pg in prime_pages:
    prime_concat.extend(unsolved[pg])
print(f"Prime pages concat: {len(prime_concat)} runes")
print(f"Prime pages IoC: {ioc(prime_concat):.4f}")

# Check periodic IoC of prime-pages-only concatenation
for period in [8, 29, 43]:
    subs = [[] for _ in range(period)]
    for i, v in enumerate(prime_concat):
        subs[i % period].append(v)
    valid = [s for s in subs if len(s) > 5]
    if valid:
        avg_ioc = sum(ioc(s) for s in valid) / len(valid)
        print(f"  Period {period}: avg IoC={avg_ioc:.4f}")

# ================================================================
# TEST 5: PROGRESSIVE/LINEAR KEY
# ================================================================
print("\n" + "="*70)
print("TEST 5: LINEAR KEY: key[i] = (a*i + b) mod 29")
print("="*70)

# For each (a, b), test key[i] = (a*i + b) mod 29
for pg in sorted(unsolved):
    cipher = unsolved[pg]
    if len(cipher) < 200: continue
    best = (0, 0, 0, '')
    
    for a in range(1, 29):
        for b in range(29):
            key = [(a * i + b) % 29 for i in range(len(cipher))]
            plain = [(cipher[i] - key[i]) % 29 for i in range(len(cipher))]
            ic = ioc(plain)
            if ic > best[0]:
                best = (ic, a, b, 'sub')
    
    ic, a, b, mode = best
    if ic > 1.2:
        print(f"  P{pg:02d}: IoC={ic:.4f} a={a} b={b}")

# ================================================================
# TEST 6: QUADRATIC KEY: key[i] = (a*i^2 + b*i + c) mod 29
# ================================================================
print("\n" + "="*70)
print("TEST 6: QUADRATIC KEY (sampled a values)")
print("="*70)

# This is O(29^3 * pages) - sample to keep reasonable
for pg in [17, 20, 25, 32, 40, 44, 50]:  # Large pages only
    if pg not in unsolved: continue
    cipher = unsolved[pg]
    n = len(cipher)
    best = (0, 0, 0, 0)
    
    for a in range(1, 29):
        for b in range(29):
            # Just test c=0 for speed
            key = [(a * i * i + b * i) % 29 for i in range(n)]
            plain = [(cipher[i] - key[i]) % 29 for i in range(n)]
            ic = ioc(plain)
            if ic > best[0]:
                best = (ic, a, b, 0)
    
    ic, a, b, c = best
    if ic > 1.2:
        print(f"  P{pg:02d}: IoC={ic:.4f} a={a} b={b}")

# ================================================================
# TEST 7: P19 KEY AS RUNNING KEY FOR ADJACENT PAGES
# ================================================================
print("\n" + "="*70)
print("TEST 7: P19 KEY EXTENDED FOR P20")
print("="*70)

p19_key = [24, 15, 2, 24, 4, 21, 11, 10, 20, 16, 9, 19, 26, 11, 7, 5, 11, 6, 27, 8, 22, 25, 21, 16, 25, 0, 27, 9, 21, 7, 27, 15, 21, 9, 3, 16, 5, 22, 18, 4, 5, 18, 23]

if 20 in unsolved:
    p20 = unsolved[20]
    print(f"P20 has {len(p20)} runes, P19 key has {len(p19_key)} values")
    
    # What if P19 key repeats for P20?
    for mode in ['sub', 'add', 'beau']:
        plain = [(p20[i] - p19_key[i % len(p19_key)]) % 29 if mode == 'sub'
                 else ((p20[i] + p19_key[i % len(p19_key)]) % 29 if mode == 'add'
                 else (p19_key[i % len(p19_key)] - p20[i]) % 29)
                 for i in range(len(p20))]
        ic = ioc(plain)
        text = to_eng(plain[:50])
        print(f"  P19 key repeating, mode={mode}: IoC={ic:.4f}  {text}")
    
    # What if P19 key is used as initial values for an autokey on P20?
    print("\n  P19 key as autokey primer for P20:")
    for mode in ['sub', 'add']:
        plain = []
        key_stream = list(p19_key)  # Start with P19 key
        for i in range(len(p20)):
            k = key_stream[i] if i < len(key_stream) else plain[i - len(p19_key)]
            if mode == 'sub': p = (p20[i] - k) % 29
            else: p = (p20[i] + k) % 29
            plain.append(p)
            if i >= len(key_stream):
                key_stream.append(p)  # Extend key with plaintext
        
        ic = ioc(plain)
        text = to_eng(plain[:50])
        print(f"  mode={mode}: IoC={ic:.4f}  {text}")
    
    # What if P19 key continues (the actual key is longer than 43)?
    # Test if P20's first cipher values, when decrypted with an extension of P19's pattern, give English
    print("\n  Trying to extend P19 key pattern into P20:")
    # Check if P19 key values have any mathematical relationship to position
    for a in range(29):
        for b in range(29):
            match = True
            for i in range(min(10, len(p19_key))):
                if (a * i + b) % 29 != p19_key[i]:
                    match = False
                    break
            if match:
                print(f"  Linear match: key[i] = ({a}*i + {b}) % 29 for first 10 values")

# ================================================================
# TEST 8: INTERLEAVE TEST - odd/even positions decrypted separately
# ================================================================
print("\n" + "="*70)
print("TEST 8: SPLIT CHANNEL ANALYSIS (odd/even, mod-3, etc.)")
print("="*70)

for pg in sorted(unsolved):
    cipher = unsolved[pg]
    if len(cipher) < 200: continue
    
    for split in [2, 3, 5, 7]:
        channels = [[] for _ in range(split)]
        for i, v in enumerate(cipher):
            channels[i % split].append(v)
        
        # Check IoC of each channel
        iocs = [ioc(ch) for ch in channels if len(ch) > 10]
        max_ioc = max(iocs) if iocs else 0
        avg_ioc = sum(iocs) / len(iocs) if iocs else 0
        
        if max_ioc > 1.3:
            print(f"  P{pg:02d} split={split}: avg={avg_ioc:.4f} max={max_ioc:.4f}")
            for j, ch in enumerate(channels):
                if ioc(ch) > 1.2:
                    print(f"    Channel {j}: IoC={ioc(ch):.4f} len={len(ch)} first={to_eng(ch[:20])}")

print("\n" + "="*70)
print("ALL IRREGULAR KEY TESTS COMPLETE")
print("="*70)
