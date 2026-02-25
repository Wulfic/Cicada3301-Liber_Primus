"""
AUTOKEY CIPHER EXHAUSTIVE TEST
================================
Autokey ciphers produce:
- Flat frequency distributions (polyalphabetic) ✓
- No periodic signal ✓  
- Standard Vigenère attacks fail ✓
This matches ALL observed characteristics of unsolved LP pages.

Tests:
1. Plaintext autokey: K[i] = seed[i] for i < len(seed), K[i] = P[i-len(seed)] for i >= len(seed)
2. Ciphertext autokey: K[i] = seed[i] for i < len(seed), K[i] = C[i-len(seed)] for i >= len(seed)
3. Both with SUB, ADD, BEAU modes
4. Seeds: all single values 0-28, all pairs (0-28)^2, known keywords
5. F-skip variants
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

# ================================================================
# AUTOKEY DECRYPTION FUNCTIONS
# ================================================================

def autokey_plaintext_sub(cipher, seed):
    """Plaintext autokey SUB: P[i] = (C[i] - K[i]) % 29, K[i>=s] = P[i-s]"""
    n = len(cipher)
    s = len(seed)
    plain = []
    for i in range(n):
        if i < s:
            k = seed[i]
        else:
            k = plain[i - s]
        p = (cipher[i] - k) % 29
        plain.append(p)
    return plain

def autokey_plaintext_add(cipher, seed):
    """Plaintext autokey ADD: P[i] = (C[i] + K[i]) % 29, K[i>=s] = P[i-s]"""
    n = len(cipher)
    s = len(seed)
    plain = []
    for i in range(n):
        if i < s:
            k = seed[i]
        else:
            k = plain[i - s]
        p = (cipher[i] + k) % 29
        plain.append(p)
    return plain

def autokey_plaintext_beau(cipher, seed):
    """Plaintext autokey BEAU: P[i] = (K[i] - C[i]) % 29, K[i>=s] = P[i-s]"""
    n = len(cipher)
    s = len(seed)
    plain = []
    for i in range(n):
        if i < s:
            k = seed[i]
        else:
            k = plain[i - s]
        p = (k - cipher[i]) % 29
        plain.append(p)
    return plain

def autokey_cipher_sub(cipher, seed):
    """Ciphertext autokey SUB: P[i] = (C[i] - K[i]) % 29, K[i>=s] = C[i-s]"""
    n = len(cipher)
    s = len(seed)
    plain = []
    for i in range(n):
        if i < s:
            k = seed[i]
        else:
            k = cipher[i - s]
        p = (cipher[i] - k) % 29
        plain.append(p)
    return plain

def autokey_cipher_add(cipher, seed):
    """Ciphertext autokey ADD: P[i] = (C[i] + K[i]) % 29, K[i>=s] = C[i-s]"""
    n = len(cipher)
    s = len(seed)
    plain = []
    for i in range(n):
        if i < s:
            k = seed[i]
        else:
            k = cipher[i - s]
        p = (cipher[i] + k) % 29
        plain.append(p)
    return plain

def autokey_cipher_beau(cipher, seed):
    """Ciphertext autokey BEAU: P[i] = (K[i] - C[i]) % 29, K[i>=s] = C[i-s]"""
    n = len(cipher)
    s = len(seed)
    plain = []
    for i in range(n):
        if i < s:
            k = seed[i]
        else:
            k = cipher[i - s]
        p = (k - cipher[i]) % 29
        plain.append(p)
    return plain

# F-skip variants
def autokey_fskip_plaintext_sub(cipher, seed):
    """F-skip plaintext autokey: when C[i]=0, output 0 and don't advance key"""
    n = len(cipher)
    s = len(seed)
    plain = []
    key_used = []  # plaintext values used as key
    for i in range(n):
        if cipher[i] == 0:
            plain.append(0)
            continue
        ki = len(key_used)
        if ki < s:
            k = seed[ki]
        else:
            k = key_used[ki - s]
        p = (cipher[i] - k) % 29
        plain.append(p)
        key_used.append(p)
    return plain

def autokey_fskip_plaintext_add(cipher, seed):
    n = len(cipher)
    s = len(seed)
    plain = []
    key_used = []
    for i in range(n):
        if cipher[i] == 0:
            plain.append(0)
            continue
        ki = len(key_used)
        if ki < s:
            k = seed[ki]
        else:
            k = key_used[ki - s]
        p = (cipher[i] + k) % 29
        plain.append(p)
        key_used.append(p)
    return plain

def autokey_fskip_plaintext_beau(cipher, seed):
    n = len(cipher)
    s = len(seed)
    plain = []
    key_used = []
    for i in range(n):
        if cipher[i] == 0:
            plain.append(0)
            continue
        ki = len(key_used)
        if ki < s:
            k = seed[ki]
        else:
            k = key_used[ki - s]
        p = (k - cipher[i]) % 29
        plain.append(p)
        key_used.append(p)
    return plain

# All autokey functions
AUTOKEY_MODES = {
    'pt_sub': autokey_plaintext_sub,
    'pt_add': autokey_plaintext_add, 
    'pt_beau': autokey_plaintext_beau,
    'ct_sub': autokey_cipher_sub,
    'ct_add': autokey_cipher_add,
    'ct_beau': autokey_cipher_beau,
    'fskip_pt_sub': autokey_fskip_plaintext_sub,
    'fskip_pt_add': autokey_fskip_plaintext_add,
    'fskip_pt_beau': autokey_fskip_plaintext_beau,
}

# ================================================================
# LOAD ALL UNSOLVED PAGES
# ================================================================
unsolved = {}
for pg in list(range(17, 55)) + [71]:
    data = load_page(pg)
    if data and len(data) > 50:
        unsolved[pg] = data

# Also add pages 57 and any other potentially unsolved
for pg in [57, 65, 66, 69, 70, 72]:
    data = load_page(pg)
    if data and len(data) > 5:
        unsolved[pg] = data

print(f"Loaded {len(unsolved)} unsolved pages")
print(f"Pages: {sorted(unsolved.keys())}")

# ================================================================
# TEST 1: ALL SINGLE-VALUE SEEDS (0-28) × 9 MODES × ALL PAGES
# ================================================================
print("\n" + "="*70)
print("TEST 1: SINGLE-VALUE SEEDS (29 seeds × 9 modes)")
print("="*70)

IOC_THRESHOLD = 1.5
hits = []

for pg in sorted(unsolved):
    cipher = unsolved[pg]
    for seed_val in range(29):
        seed = [seed_val]
        for mode_name, mode_fn in AUTOKEY_MODES.items():
            try:
                plain = mode_fn(cipher, seed)
                ic = ioc(plain)
                if ic > IOC_THRESHOLD:
                    text = to_eng(plain[:80])
                    hits.append((pg, mode_name, seed_val, ic, len(cipher), text))
            except:
                pass

print(f"Hits with IoC > {IOC_THRESHOLD}: {len(hits)}")
for pg, mode, sv, ic, ln, text in sorted(hits, key=lambda x: -x[3]):
    print(f"  P{pg:02d} {mode:15s} seed=[{sv}]({LATIN[sv]})  IoC={ic:.4f}  len={ln}")
    print(f"    {text}")

# ================================================================
# TEST 2: KEYWORD SEEDS (known words) × 9 MODES × ALL PAGES  
# ================================================================
print("\n" + "="*70)
print("TEST 2: KEYWORD SEEDS × 9 MODES")
print("="*70)

keywords = ['DIVINITY', 'PRIMES', 'DEOR', 'PATH', 'REARRANGING', 'WELCOME',
            'PILGRIM', 'WISDOM', 'INSTAR', 'CONSUMPTION', 'ADHERENCE',
            'CIRCUMFERENCE', 'PRESERVATION', 'PRIMALITY', 'EMERGENCE',
            'LOSS', 'SACRED', 'PARABLE', 'COMMAND', 'INTUS',
            'AN', 'THE', 'FIRFUMFERENFE', 'NOTCOERCED']

hits2 = []
for pg in sorted(unsolved):
    cipher = unsolved[pg]
    for kw in keywords:
        seed = keyword_to_gp(kw)
        if not seed: continue
        for mode_name, mode_fn in AUTOKEY_MODES.items():
            try:
                plain = mode_fn(cipher, seed)
                ic = ioc(plain)
                if ic > IOC_THRESHOLD:
                    text = to_eng(plain[:80])
                    hits2.append((pg, mode_name, kw, ic, len(cipher), text))
            except:
                pass

print(f"Hits with IoC > {IOC_THRESHOLD}: {len(hits2)}")
for pg, mode, kw, ic, ln, text in sorted(hits2, key=lambda x: -x[3]):
    print(f"  P{pg:02d} {mode:15s} seed={kw}  IoC={ic:.4f}  len={ln}")
    print(f"    {text}")

# ================================================================
# TEST 3: TWO-VALUE SEEDS (29×29 = 841) × 3 BEST MODES × LARGE PAGES
# ================================================================
print("\n" + "="*70)
print("TEST 3: TWO-VALUE SEEDS (841 seeds × 3 modes × large pages only)")
print("="*70)

# Only test large pages (more reliable IoC)
large_pg = {pg: v for pg, v in unsolved.items() if len(v) > 200}
print(f"Testing {len(large_pg)} pages with >200 runes")

# Only 3 most likely modes (plaintext autokey is more common than ciphertext)
test3_modes = {
    'pt_sub': autokey_plaintext_sub,
    'pt_beau': autokey_plaintext_beau,
    'fskip_pt_sub': autokey_fskip_plaintext_sub,
}

hits3 = []
for pg in sorted(large_pg):
    cipher = large_pg[pg]
    best_for_page = (0, None, None, None)
    for s1 in range(29):
        for s2 in range(29):
            seed = [s1, s2]
            for mode_name, mode_fn in test3_modes.items():
                try:
                    plain = mode_fn(cipher, seed)
                    ic = ioc(plain)
                    if ic > best_for_page[0]:
                        best_for_page = (ic, mode_name, seed[:], to_eng(plain[:60]))
                    if ic > IOC_THRESHOLD:
                        text = to_eng(plain[:60])
                        hits3.append((pg, mode_name, (s1,s2), ic, len(cipher), text))
                except:
                    pass
    ic, mode, seed, text = best_for_page
    print(f"  P{pg:02d} (n={len(cipher)}): best IoC={ic:.4f} mode={mode} seed={seed}")
    if text:
        print(f"    {text}")

print(f"\nHits with IoC > {IOC_THRESHOLD}: {len(hits3)}")
for pg, mode, sv, ic, ln, text in sorted(hits3, key=lambda x: -x[3])[:30]:
    print(f"  P{pg:02d} {mode:18s} seed={sv}  IoC={ic:.4f}")
    print(f"    {text}")

# ================================================================
# TEST 4: ALL 9 MODES × TWO-VALUE SEEDS × ALL PAGES (quick scan)
# ================================================================
print("\n" + "="*70)
print("TEST 4: ALL 9 MODES × TWO-VALUE SEEDS × ALL PAGES (threshold 1.45)")
print("="*70)

hits4 = []
for pg in sorted(unsolved):
    cipher = unsolved[pg]
    for s1 in range(29):
        for s2 in range(29):
            seed = [s1, s2]
            for mode_name, mode_fn in AUTOKEY_MODES.items():
                try:
                    plain = mode_fn(cipher, seed)
                    ic = ioc(plain)
                    if ic > 1.45:
                        text = to_eng(plain[:60])
                        hits4.append((pg, mode_name, (s1,s2), ic, len(cipher), text))
                except:
                    pass

# Deduplicate: per page, keep best
best_per_page = {}
for pg, mode, sv, ic, ln, text in hits4:
    key = pg
    if key not in best_per_page or ic > best_per_page[key][3]:
        best_per_page[key] = (pg, mode, sv, ic, ln, text)

print(f"Total hits with IoC > 1.45: {len(hits4)}")
print(f"Pages with hits: {sorted(best_per_page.keys())}")
for pg in sorted(best_per_page):
    _, mode, sv, ic, ln, text = best_per_page[pg]
    print(f"  P{pg:02d} {mode:18s} seed={sv}  IoC={ic:.4f} len={ln}")
    print(f"    {text}")

# ================================================================
# TEST 5: DIVINITY KEY AS AUTOKEY SEED
# ================================================================
print("\n" + "="*70)
print("TEST 5: DIVINITY KEY [23,10,1,10,9,10,16,26] AS AUTOKEY SEED")
print("="*70)

divinity_seed = [23, 10, 1, 10, 9, 10, 16, 26]
hits5 = []
for pg in sorted(unsolved):
    cipher = unsolved[pg]
    for mode_name, mode_fn in AUTOKEY_MODES.items():
        try:
            plain = mode_fn(cipher, divinity_seed)
            ic = ioc(plain)
            if ic > 1.3:
                text = to_eng(plain[:80])
                hits5.append((pg, mode_name, ic, len(cipher), text))
        except:
            pass

print(f"Hits with IoC > 1.3: {len(hits5)}")
for pg, mode, ic, ln, text in sorted(hits5, key=lambda x: -x[2]):
    print(f"  P{pg:02d} {mode:15s}  IoC={ic:.4f}  len={ln}")
    print(f"    {text}")

# ================================================================
# TEST 6: P19 KEY (43 values) AS AUTOKEY SEED
# ================================================================
print("\n" + "="*70)
print("TEST 6: P19 KEY (43 values) AS AUTOKEY SEED")
print("="*70)
p19_key = [24, 15, 2, 24, 4, 21, 11, 10, 20, 16, 9, 19, 26, 11, 7, 5, 11, 6, 27, 8, 22, 25, 21, 16, 25, 0, 27, 9, 21, 7, 27, 15, 21, 9, 3, 16, 5, 22, 18, 4, 5, 18, 23]

hits6 = []
for pg in sorted(unsolved):
    cipher = unsolved[pg]
    for mode_name, mode_fn in AUTOKEY_MODES.items():
        try:
            plain = mode_fn(cipher, p19_key)
            ic = ioc(plain)
            if ic > 1.3:
                text = to_eng(plain[:80])
                hits6.append((pg, mode_name, ic, len(cipher), text))
        except:
            pass

print(f"Hits with IoC > 1.3: {len(hits6)}")
for pg, mode, ic, ln, text in sorted(hits6, key=lambda x: -x[2]):
    print(f"  P{pg:02d} {mode:15s}  IoC={ic:.4f}  len={ln}")
    print(f"    {text}")

print("\n" + "="*70)
print("ALL AUTOKEY TESTS COMPLETE")
print("="*70)
