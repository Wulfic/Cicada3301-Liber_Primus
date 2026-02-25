#!/usr/bin/env python3
"""
Phase 3 Attack — Novel cipher-breaking approaches for Liber Primus unsolved pages.

Sections:
1. Outguess binary data as keystream (bytes mod 29)
2. Very large totient offsets (50k–500k sparse sampling)
3. Alternative prime functions (p^2, 2^p, gaps, digit sums, etc.)
4. Multi-layer ciphers (Atbash + totient, shift + totient)
5. Word-length crib analysis (extract word-length fingerprints)
6. Cross-page difference (detect shared keystreams)
7. Gromark / additive running key
8. Modular exponentiation keystreams (primitive roots)
"""

import os, sys, math, collections, itertools

# ─── Gematria Primus ──────────────────────────────────────────────
RUNE_TO_INDEX = {
    '\u16A0':0,  '\u16A2':1,  '\u16A6':2,  '\u16A9':3,  '\u16B1':4,
    '\u16B3':5,  '\u16B7':6,  '\u16B9':7,  '\u16BB':8,  '\u16BE':9,
    '\u16C1':10, '\u16C2':11, '\u16C4':11, '\u16C7':12, '\u16C8':13,
    '\u16C9':14, '\u16CB':15, '\u16CF':16, '\u16D2':17, '\u16D6':18,
    '\u16D7':19, '\u16DA':20, '\u16DD':21, '\u16DF':22, '\u16DE':23,
    '\u16AA':24, '\u16AB':25, '\u16A3':26, '\u16E1':27, '\u16E0':28,
}
INDEX_TO_LETTER = list("FUÞORHCGWHNIJYPEAXSMBLNGEADOEY")[:29]
# More intuitive letter mapping
INDEX_TO_LETTER = ['F','U','TH','O','R','C','G','W','H','N',
                   'I','J','EO','P','X','Z','S','T','B','E',
                   'M','L','NG','D','A','AE','Y','IA','EA']

def runes_to_indices(text):
    return [RUNE_TO_INDEX[ch] for ch in text if ch in RUNE_TO_INDEX]

def indices_to_text(indices):
    simple = "FUTORHCGWHNIJPXZSTBEMLNDAAYWE"  # 29 single chars
    return ''.join(simple[i % 29] for i in indices)

# ─── Helpers ──────────────────────────────────────────────────────
def load_page_runes(page_num):
    base = os.path.join(os.path.dirname(__file__), '..', 'LiberPrimus', 'pages')
    path = os.path.join(base, f'page_{page_num:02d}', 'runes.txt')
    if not os.path.exists(path):
        return None, None
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read().strip()
    indices = runes_to_indices(text)
    return text, indices

def calculate_ioc(indices):
    if len(indices) < 2:
        return 0.0
    freq = collections.Counter(indices)
    n = len(indices)
    return sum(c*(c-1) for c in freq.values()) / (n*(n-1)) * 29

def sieve_primes(limit):
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, limit + 1, i):
                sieve[j] = False
    return [i for i in range(2, limit + 1) if sieve[i]]

def score_english(indices):
    """Score how English-like a sequence is using common trigrams."""
    text = indices_to_text(indices).upper()
    common = ['THE','AND','ING','HER','HAT','HIS','THA','ERE','FOR',
              'ENT','ION','TER','WAS','YOU','ITH','VER','ALL','WIT',
              'THI','TIO']
    score = sum(text.count(tri) for tri in common)
    return score

# English frequency for scoring
ENG_FREQ = [0.015, 0.025, 0.018, 0.084, 0.034, 0.047, 0.029, 0.023,
            0.058, 0.028, 0.070, 0.004, 0.012, 0.063, 0.021, 0.010,
            0.063, 0.075, 0.129, 0.032, 0.049, 0.011, 0.092, 0.042,
            0.072, 0.033, 0.018, 0.022, 0.020]

def freq_score(indices):
    """Chi-squared distance from expected English GP frequencies."""
    if not indices:
        return 999.0
    n = len(indices)
    freq = collections.Counter(indices)
    chi2 = sum((freq.get(i, 0)/n - ENG_FREQ[i])**2 / max(ENG_FREQ[i], 0.001) for i in range(29))
    return chi2

# ─── Load pages ───────────────────────────────────────────────────
UNSOLVED_PAGES = list(range(17, 55))  # 17..54
FOCUS_PAGES = [20, 25, 32, 40, 44, 50, 17]  # Large pages for reliable IoC

pages = {}
for pn in UNSOLVED_PAGES:
    text, indices = load_page_runes(pn)
    if indices and len(indices) > 30:
        pages[pn] = {'text': text, 'indices': indices, 'n': len(indices)}

print("=" * 80)
print("PHASE 3 ATTACK — LIBER PRIMUS")
print("=" * 80)
print(f"Loaded {len(pages)} unsolved pages")

PRIMES = sieve_primes(6_000_000)  # enough for 500k offset + longest page

# ═══════════════════════════════════════════════════════════════════
# SECTION 1: OUTGUESS BINARY DATA AS KEYSTREAM
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("SECTION 1: OUTGUESS BINARY DATA AS KEYSTREAM")
print("=" * 80)

outguess_files = {
    17: os.path.join(os.path.dirname(__file__), '..', 'outguess_17.txt'),
    21: os.path.join(os.path.dirname(__file__), '..', 'outguess_21.txt'),
    43: os.path.join(os.path.dirname(__file__), '..', 'outguess_43.txt'),
}

# Try using outguess bytes as keystream for their respective page
# Also try: bytes from outguess_17 on ALL pages (maybe it's one master key)
for og_page, og_path in outguess_files.items():
    with open(og_path, 'rb') as f:
        og_bytes = f.read()
    
    print(f"\n  outguess_{og_page:02d}.txt ({len(og_bytes)} bytes)")
    
    # Try multiple offsets (skip shared header at 0, try after header at 1417, 2004)
    offsets_to_try = [0, 1417, 2004, 3038, 4096, 8192, 16384, 32768]
    
    for target_page in [og_page] + FOCUS_PAGES:
        if target_page not in pages:
            continue
        ci = pages[target_page]['indices']
        n = len(ci)
        
        best_ioc = 0
        best_info = ""
        
        for start_off in offsets_to_try:
            if start_off + n > len(og_bytes):
                continue
            key_bytes = og_bytes[start_off:start_off + n]
            
            # Method 1: bytes mod 29 as key, subtract
            key_mod29 = [b % 29 for b in key_bytes]
            plain_sub = [(ci[i] - key_mod29[i]) % 29 for i in range(n)]
            ioc_sub = calculate_ioc(plain_sub)
            if ioc_sub > best_ioc:
                best_ioc = ioc_sub
                best_info = f"off={start_off} SUB byte%29"
            
            # Method 2: bytes mod 29 as key, add
            plain_add = [(ci[i] + key_mod29[i]) % 29 for i in range(n)]
            ioc_add = calculate_ioc(plain_add)
            if ioc_add > best_ioc:
                best_ioc = ioc_add
                best_info = f"off={start_off} ADD byte%29"
            
            # Method 3: XOR byte with index, mod 29
            plain_xor = [(ci[i] ^ key_bytes[i]) % 29 for i in range(n)]
            ioc_xor = calculate_ioc(plain_xor)
            if ioc_xor > best_ioc:
                best_ioc = ioc_xor
                best_info = f"off={start_off} XOR%29"
            
            # Method 4: Use phi(byte_as_index_into_primes) — treat bytes as prime indices
            plain_phi = []
            for i in range(n):
                pidx = key_bytes[i] % len(PRIMES)
                k = (PRIMES[pidx] - 1) % 29
                plain_phi.append((ci[i] - k) % 29)
            ioc_phi = calculate_ioc(plain_phi)
            if ioc_phi > best_ioc:
                best_ioc = ioc_phi
                best_info = f"off={start_off} phi(prime[byte])"
        
        flag = " ***" if best_ioc > 1.3 else ""
        if target_page == og_page or best_ioc > 1.2:
            print(f"    P{target_page:02d} ({n} runes): best IoC={best_ioc:.4f} [{best_info}]{flag}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 2: VERY LARGE TOTIENT OFFSETS (50k–500k)
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("SECTION 2: VERY LARGE TOTIENT OFFSETS (50k–500k sparse)")
print("=" * 80)

# Sparse sampling: test every 500th offset from 15000 to 500000
test_pages = [(20, 812), (25, 1729), (32, 1894)]
for pn, expected_n in test_pages:
    if pn not in pages:
        continue
    ci = pages[pn]['indices']
    n = len(ci)
    best_ioc = 0
    best_off = 0
    
    for offset in range(15000, 500001, 500):
        if offset + n >= len(PRIMES):
            break
        plain = [(ci[i] - (PRIMES[i + offset] - 1)) % 29 for i in range(n)]
        ioc = calculate_ioc(plain)
        if ioc > best_ioc:
            best_ioc = ioc
            best_off = offset
    
    print(f"  P{pn:02d} ({n} runes): best IoC={best_ioc:.4f} at offset={best_off}")
    
    # If anything promising, do fine-grained search around it
    if best_ioc > 1.15:
        print(f"    Fine-grained search around offset {best_off}...")
        for off2 in range(max(0, best_off - 500), best_off + 500):
            if off2 + n >= len(PRIMES):
                break
            plain = [(ci[i] - (PRIMES[i + off2] - 1)) % 29 for i in range(n)]
            ioc = calculate_ioc(plain)
            if ioc > best_ioc:
                best_ioc = ioc
                best_off = off2
        print(f"    Refined: IoC={best_ioc:.4f} at offset={best_off}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 3: ALTERNATIVE PRIME FUNCTIONS AS KEYSTREAM
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("SECTION 3: ALTERNATIVE PRIME FUNCTIONS AS KEYSTREAM")
print("=" * 80)

# For each function, generate keystream and test
def prime_squared_key(primes, n, offset=0):
    return [(primes[i+offset]**2) % 29 for i in range(n)]

def power_of_2_mod_prime(primes, n, offset=0):
    return [pow(2, primes[i+offset], 29) for i in range(n)]

def prime_gap_key(primes, n, offset=0):
    return [(primes[i+offset+1] - primes[i+offset]) % 29 for i in range(n)]

def digit_sum_key(primes, n, offset=0):
    return [sum(int(d) for d in str(primes[i+offset])) % 29 for i in range(n)]

def prime_mod_key(primes, n, offset=0, mod=30):
    """primes mod different modulus, then mod 29"""
    return [(primes[i+offset] % mod) % 29 for i in range(n)]

def prime_xor_key(primes, n, offset=0):
    """XOR consecutive primes"""
    return [(primes[i+offset] ^ primes[i+offset+1]) % 29 for i in range(n)]

def totient_squared_key(primes, n, offset=0):
    """phi(p)^2 mod 29"""
    return [((primes[i+offset]-1)**2) % 29 for i in range(n)]

def prime_product_mod_key(primes, n, offset=0):
    """p[i]*p[i+1] mod 29"""
    return [(primes[i+offset] * primes[i+offset+1]) % 29 for i in range(n)]

functions = [
    ("p^2 mod 29", prime_squared_key),
    ("2^p mod 29", power_of_2_mod_prime),
    ("gap mod 29", prime_gap_key),
    ("digit_sum mod 29", digit_sum_key),
    ("p mod 30 mod 29", lambda p,n,o=0: prime_mod_key(p,n,o,30)),
    ("p XOR p_next mod 29", prime_xor_key),
    ("phi^2 mod 29", totient_squared_key),
    ("p*p_next mod 29", prime_product_mod_key),
]

for pn in FOCUS_PAGES:
    if pn not in pages:
        continue
    ci = pages[pn]['indices']
    n = len(ci)
    
    results = []
    for fname, func in functions:
        best_ioc = 0
        best_off = 0
        # Test offsets 0, 100, 200, ..., 5000
        for offset in range(0, 5001, 100):
            try:
                key = func(PRIMES, n, offset)
                plain = [(ci[i] - key[i]) % 29 for i in range(n)]
                ioc = calculate_ioc(plain)
                if ioc > best_ioc:
                    best_ioc = ioc
                    best_off = offset
            except:
                break
        results.append((best_ioc, fname, best_off))
    
    results.sort(reverse=True)
    print(f"\n  P{pn:02d} ({n} runes) — top 3 functions:")
    for ioc, fname, off in results[:3]:
        flag = " ***" if ioc > 1.3 else ""
        print(f"    {fname}: IoC={ioc:.4f} at offset={off}{flag}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 4: MULTI-LAYER CIPHERS
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("SECTION 4: MULTI-LAYER CIPHERS")
print("=" * 80)
print("Testing: first_layer → then totient(offset=0..5000)")

def atbash(indices):
    return [(28 - i) % 29 for i in indices]

def caesar(indices, shift):
    return [(i + shift) % 29 for i in indices]

def reverse_indices(indices):
    return list(reversed(indices))

layers = [
    ("Atbash first", atbash),
    ("Caesar(1) first", lambda idx: caesar(idx, 1)),
    ("Caesar(3) first", lambda idx: caesar(idx, 3)),
    ("Caesar(13) first", lambda idx: caesar(idx, 13)),
    ("Reverse order", reverse_indices),
]

for pn in FOCUS_PAGES:
    if pn not in pages:
        continue
    ci = pages[pn]['indices']
    n = len(ci)
    
    print(f"\n  P{pn:02d} ({n} runes):")
    for layer_name, layer_func in layers:
        # Apply first layer
        intermediate = layer_func(ci)
        
        # Then try totient at various offsets
        best_ioc = 0
        best_off = 0
        for offset in range(0, 5001, 50):
            if offset + n >= len(PRIMES):
                break
            plain = [(intermediate[i] - (PRIMES[i+offset] - 1)) % 29 for i in range(n)]
            ioc = calculate_ioc(plain)
            if ioc > best_ioc:
                best_ioc = ioc
                best_off = offset
        
        flag = " ***" if best_ioc > 1.3 else ""
        if best_ioc > 1.1:
            print(f"    {layer_name}: best IoC={best_ioc:.4f} at totient_off={best_off}{flag}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 5: WORD-LENGTH FINGERPRINT ANALYSIS
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("SECTION 5: WORD-LENGTH FINGERPRINT ANALYSIS")
print("=" * 80)

for pn in sorted(pages.keys()):
    text = pages[pn]['text']
    # Split on word separators (interpunct •)
    words = [w.strip() for w in text.replace('\n', ' ').split('•') if w.strip()]
    # Convert words to rune lengths
    word_lengths = []
    for w in words:
        rune_count = sum(1 for ch in w if ch in RUNE_TO_INDEX)
        if rune_count > 0:
            word_lengths.append(rune_count)
    
    single_rune_count = sum(1 for wl in word_lengths if wl == 1)
    avg_len = sum(word_lengths) / max(len(word_lengths), 1)
    
    # Show first 30 word lengths
    wl_str = ','.join(str(wl) for wl in word_lengths[:40])
    if pn in [17, 18, 19, 20, 25, 32, 40, 44, 50]:
        print(f"  P{pn:02d}: {len(word_lengths)} words, avg={avg_len:.1f}, "
              f"single_rune={single_rune_count}")
        print(f"    First 40 word lengths: [{wl_str}]")

# Find pages with distinctive word patterns (e.g., starting with short words)
print("\n  Single-rune word positions (known plaintext = I or A):")
for pn in [20, 25, 32, 40, 44, 50]:
    if pn not in pages:
        continue
    text = pages[pn]['text']
    # Find exact positions of single-rune words
    words = text.replace('\n', ' ').split('•')
    pos = 0  # running rune position
    single_positions = []
    for w in words:
        w_stripped = w.strip()
        word_runes = [ch for ch in w_stripped if ch in RUNE_TO_INDEX]
        if len(word_runes) == 1:
            single_positions.append((pos, RUNE_TO_INDEX[word_runes[0]]))
        pos += len(word_runes)
    
    print(f"  P{pn:02d}: {len(single_positions)} single-rune words")
    if single_positions:
        # For each, compute candidate key values (plaintext = I=10 or A=24)
        for sp_pos, sp_val in single_positions[:5]:
            key_if_I = (sp_val - 10) % 29  # SUB: C - P = K
            key_if_A = (sp_val - 24) % 29
            print(f"    pos={sp_pos}: cipher={sp_val}, "
                  f"key_if_I={key_if_I}, key_if_A={key_if_A}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 6: CROSS-PAGE DIFFERENCE (SHARED KEYSTREAM DETECTION)
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("SECTION 6: CROSS-PAGE DIFFERENCE (SHARED KEYSTREAM)")
print("=" * 80)
print("If two pages use the same keystream, (C1-C2) mod 29 has elevated IoC")

# Test all pairs of reasonably-sized pages
page_nums = sorted(pages.keys())
best_pairs = []

for i in range(len(page_nums)):
    for j in range(i+1, len(page_nums)):
        pn1, pn2 = page_nums[i], page_nums[j]
        ci1 = pages[pn1]['indices']
        ci2 = pages[pn2]['indices']
        min_len = min(len(ci1), len(ci2))
        if min_len < 100:
            continue
        
        diff = [(ci1[k] - ci2[k]) % 29 for k in range(min_len)]
        ioc = calculate_ioc(diff)
        if ioc > 1.15:
            best_pairs.append((ioc, pn1, pn2, min_len))

best_pairs.sort(reverse=True)
if best_pairs:
    print(f"  Top 10 page pairs with elevated difference IoC:")
    for ioc, pn1, pn2, mlen in best_pairs[:10]:
        print(f"    P{pn1:02d} vs P{pn2:02d}: diff IoC={ioc:.4f} (overlap={mlen})")
else:
    print("  No pairs with diff IoC > 1.15")

# Also try with shifted alignment
print("\n  Testing shifted alignment (pages sharing keystream at different offsets):")
best_shifted = []
for pn1 in FOCUS_PAGES:
    for pn2 in FOCUS_PAGES:
        if pn1 >= pn2 or pn1 not in pages or pn2 not in pages:
            continue
        ci1 = pages[pn1]['indices']
        ci2 = pages[pn2]['indices']
        
        for shift in range(0, min(500, len(ci1)), 50):
            overlap = min(len(ci1) - shift, len(ci2))
            if overlap < 100:
                continue
            diff = [(ci1[k + shift] - ci2[k]) % 29 for k in range(overlap)]
            ioc = calculate_ioc(diff)
            if ioc > 1.1:
                best_shifted.append((ioc, pn1, pn2, shift, overlap))

best_shifted.sort(reverse=True)
if best_shifted:
    for ioc, pn1, pn2, shift, ov in best_shifted[:5]:
        print(f"    P{pn1:02d}[+{shift}] vs P{pn2:02d}: IoC={ioc:.4f} (overlap={ov})")
else:
    print("  No shifted pairs with IoC > 1.1")

# ═══════════════════════════════════════════════════════════════════
# SECTION 7: GROMARK / ADDITIVE RUNNING KEY
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("SECTION 7: GROMARK CIPHER (ADDITIVE RUNNING KEY)")
print("=" * 80)
print("Key expands via: K[i+m] = (K[i] + K[i+1]) mod 29 (Fibonacci-like)")

# In Gromark cipher, a short initial key (primer) generates a running key
# by adding pairs: K[i+m] = (K[i] + K[i+1]) mod 29
# We try primer lengths 2-8 with all possible values (exhaustive for short)

def gromark_decrypt(cipher_indices, primer):
    """Decrypt using Gromark cipher with given primer."""
    m = len(primer)
    key = list(primer)
    n = len(cipher_indices)
    # Extend key
    while len(key) < n:
        key.append((key[-m] + key[-m+1]) % 29)
    return [(cipher_indices[i] - key[i]) % 29 for i in range(n)]

# For primer length 2: 29*29 = 841 combos (fast)
# For primer length 3: 29^3 = 24389 (manageable)
for pn in FOCUS_PAGES[:3]:  # Top 3 large pages
    if pn not in pages:
        continue
    ci = pages[pn]['indices']
    n = len(ci)
    
    print(f"\n  P{pn:02d} ({n} runes):")
    
    # Primer length 2
    best_ioc2 = 0
    best_primer2 = None
    for a in range(29):
        for b in range(29):
            plain = gromark_decrypt(ci, [a, b])
            ioc = calculate_ioc(plain)
            if ioc > best_ioc2:
                best_ioc2 = ioc
                best_primer2 = (a, b)
    
    print(f"    Primer len 2: best IoC={best_ioc2:.4f} primer={best_primer2}")
    if best_ioc2 > 1.3:
        plain = gromark_decrypt(ci, list(best_primer2))
        print(f"    Text: {indices_to_text(plain[:60])}")
    
    # Primer length 3 (24k combos)
    best_ioc3 = 0
    best_primer3 = None
    for a in range(29):
        for b in range(29):
            for c in range(29):
                plain = gromark_decrypt(ci, [a, b, c])
                ioc = calculate_ioc(plain)
                if ioc > best_ioc3:
                    best_ioc3 = ioc
                    best_primer3 = (a, b, c)
    
    print(f"    Primer len 3: best IoC={best_ioc3:.4f} primer={best_primer3}")
    if best_ioc3 > 1.3:
        plain = gromark_decrypt(ci, list(best_primer3))
        print(f"    Text: {indices_to_text(plain[:60])}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 8: MODULAR EXPONENTIATION KEYSTREAMS
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("SECTION 8: MODULAR EXPONENTIATION KEYSTREAMS")
print("=" * 80)
print("K[i] = g^i mod p mod 29, for small generators and primes")

# The idea: a primitive root g modulo a prime p generates a pseudorandom
# sequence. Try small p values and generators.
test_moduli = [3301, 167, 761, 1033, 29, 31, 37, 41, 43, 47, 53, 59, 
               61, 67, 71, 73, 79, 83, 89, 97, 127, 131, 137, 139]

for pn in FOCUS_PAGES[:3]:
    if pn not in pages:
        continue
    ci = pages[pn]['indices']
    n = len(ci)
    
    best_ioc = 0
    best_params = ""
    
    for modulus in test_moduli:
        for gen in [2, 3, 5, 7, 11, 13]:
            key = [pow(gen, i, modulus) % 29 for i in range(n)]
            
            # Check if key has enough variety (not degenerate)
            if len(set(key[:100])) < 10:
                continue
            
            for mode in ['SUB', 'ADD']:
                if mode == 'SUB':
                    plain = [(ci[i] - key[i]) % 29 for i in range(n)]
                else:
                    plain = [(ci[i] + key[i]) % 29 for i in range(n)]
                ioc = calculate_ioc(plain)
                if ioc > best_ioc:
                    best_ioc = ioc
                    best_params = f"g={gen} mod {modulus} {mode}"
    
    flag = " ***" if best_ioc > 1.3 else ""
    print(f"  P{pn:02d} ({n} runes): best IoC={best_ioc:.4f} [{best_params}]{flag}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 9: SINGLE-RUNE WORD KEYSTREAM RECONSTRUCTION
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("SECTION 9: SINGLE-RUNE WORD KEYSTREAM RECONSTRUCTION")
print("=" * 80)
print("Use known single-rune words (I=10 or A=24) to probe keystream")

for pn in [20, 25, 32, 40, 44, 50]:
    if pn not in pages:
        continue
    text = pages[pn]['text']
    ci = pages[pn]['indices']
    n = len(ci)
    
    # Extract word boundaries and single-rune positions
    words = text.replace('\n', ' ').split('\u2022')  # interpunct
    pos = 0
    single_rune_data = []  # (position_in_indices, cipher_value)
    for w in words:
        w_stripped = w.strip()
        word_runes = [ch for ch in w_stripped if ch in RUNE_TO_INDEX]
        if len(word_runes) == 1:
            single_rune_data.append((pos, RUNE_TO_INDEX[word_runes[0]]))
        pos += len(word_runes)
    
    if len(single_rune_data) < 3:
        continue
    
    print(f"\n  P{pn:02d}: {len(single_rune_data)} single-rune words at positions:")
    
    # For each single-rune word, compute key candidates
    key_candidates = {}  # position -> set of possible key values
    for spos, sval in single_rune_data:
        # SUB mode: C = P + K mod 29, so K = C - P
        key_if_I_sub = (sval - 10) % 29
        key_if_A_sub = (sval - 24) % 29
        key_candidates[spos] = {
            'I_sub': key_if_I_sub,
            'A_sub': key_if_A_sub,
            'I_add': (10 - sval) % 29,  # ADD: C = P - K, K = P - C
            'A_add': (24 - sval) % 29,
        }
    
    # Check if key candidates match totient stream at some offset
    # For each offset, check how many single-rune positions match
    print(f"    Checking totient stream matches (offsets 0-50000)...")
    best_match = 0
    best_offset_info = ""
    
    for offset in range(0, min(50001, len(PRIMES) - n)):
        totient_key = [(PRIMES[i + offset] - 1) % 29 for i in range(n)]
        
        for pt_mode in ['I_sub', 'A_sub', 'I_add', 'A_add']:
            match_count = 0
            for spos, candidates in key_candidates.items():
                if spos < n and totient_key[spos] == candidates[pt_mode]:
                    match_count += 1
            
            if match_count > best_match:
                best_match = match_count
                best_offset_info = f"offset={offset}, mode={pt_mode}, matches={match_count}/{len(single_rune_data)}"
    
    # Also check if ALL single-rune words can simultaneously be I or A
    # with the SAME keystream (mixing I and A assignments)
    best_mix_match = 0
    best_mix_info = ""
    
    for offset in range(0, min(50001, len(PRIMES) - n), 100):
        totient_key = [(PRIMES[i + offset] - 1) % 29 for i in range(n)]
        
        mix_match = 0
        for spos, candidates in key_candidates.items():
            if spos < n:
                tk = totient_key[spos]
                if tk == candidates['I_sub'] or tk == candidates['A_sub']:
                    mix_match += 1
        
        if mix_match > best_mix_match:
            best_mix_match = mix_match
            best_mix_info = f"offset={offset}, mixed I/A SUB, matches={mix_match}/{len(single_rune_data)}"
    
    print(f"    Best uniform: {best_offset_info}")
    print(f"    Best mixed:   {best_mix_info}")
    
    # Expected random matches: n_single * 2/29 for mixed (one of two values)
    expected = len(single_rune_data) * 2 / 29
    print(f"    Expected random: {expected:.1f}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 10: GP PRIME VALUE CIPHER
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("SECTION 10: GP PRIME VALUE ARITHMETIC")
print("=" * 80)
print("Test: decrypt using GP prime values instead of indices (0-28)")

# GP prime values for each index
GP_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
             53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109]

def indices_to_gp_primes(indices):
    return [GP_PRIMES[i] for i in indices]

def gp_primes_to_indices(primes_list):
    prime_to_idx = {p: i for i, p in enumerate(GP_PRIMES)}
    return [prime_to_idx.get(p, -1) for p in primes_list]

# Test: operate on GP prime values instead of indices
for pn in FOCUS_PAGES[:3]:
    if pn not in pages:
        continue
    ci = pages[pn]['indices']
    n = len(ci)
    ci_primes = indices_to_gp_primes(ci)
    
    best_ioc = 0
    best_info = ""
    
    for offset in range(0, 5001, 100):
        if offset + n >= len(PRIMES):
            break
        
        # Method: (GP_prime[cipher] - totient) mod 109 — where 109 is largest GP prime
        for mod_val in [109, 113, 127, 29]:
            plain_primes = [(ci_primes[i] - (PRIMES[i+offset]-1)) % mod_val for i in range(n)]
            # Map back: find closest GP prime value
            plain_idx = []
            for pp in plain_primes:
                # Find the GP prime closest to pp (or pp itself if it's a GP prime)
                if pp in GP_PRIMES[:29]:
                    plain_idx.append(GP_PRIMES.index(pp))
                else:
                    plain_idx.append(pp % 29)
            
            ioc = calculate_ioc(plain_idx)
            if ioc > best_ioc:
                best_ioc = ioc
                best_info = f"offset={offset} mod {mod_val}"
    
    flag = " ***" if best_ioc > 1.3 else ""
    print(f"  P{pn:02d} ({n} runes): best IoC={best_ioc:.4f} [{best_info}]{flag}")

print("\n" + "=" * 80)
print("PHASE 3 ATTACK COMPLETE")
print("=" * 80)
