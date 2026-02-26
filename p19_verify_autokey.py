#!/usr/bin/env python3
"""
P19 FULL VERIFICATION & WORD BOUNDARY INVESTIGATION
=====================================================
1. Fully decrypt P19 with ADD mode (no F-skip) and verify plaintext
2. Check whether dashes correspond to word boundaries in the plaintext
3. If dashes ARE NOT word boundaries, check which pages DO have word separators
4. Try autokey on unsolved pages with various seeds  
5. Also check if solved pages 55-74 have word-separated runes
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os, re
from collections import Counter, defaultdict

GP_RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛂᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
GP_RUNE_TO_IDX = {r: i for i, r in enumerate(GP_RUNES)}
GP_NAMES = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]
GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
MOD = 29
PAGES_DIR = r"LiberPrimus\pages"

P19_KEY = [24,15,2,24,4,21,11,10,20,16,9,19,26,11,7,5,11,6,27,8,22,25,21,16,25,0,27,9,21,7,27,15,21,9,3,16,5,22,18,4,5,18,23,21,1,10,24]
DIVINITY = [23, 10, 1, 10, 9, 10, 16, 26]

def load_runes(page_num):
    folder = f"page_{page_num:02d}"
    path = os.path.join(PAGES_DIR, folder, "runes.txt")
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return f.read().strip()

def get_rune_stream(text):
    """Extract flat stream of rune values, ignoring all non-rune characters."""
    return [GP_RUNE_TO_IDX[ch] for ch in text if ch in GP_RUNE_TO_IDX]

def decrypt_add_no_fskip(rune_values, key):
    """Decrypt with ADD mode: P = (C + K) mod 29, cycling key."""
    return [(c + key[i % len(key)]) % MOD for i, c in enumerate(rune_values)]

def decrypt_sub_no_fskip(rune_values, key):
    """Decrypt with SUB mode: P = (C - K) mod 29, cycling key."""
    return [(c - key[i % len(key)]) % MOD for i, c in enumerate(rune_values)]

def decrypt_beau_no_fskip(rune_values, key):
    """Decrypt with Beaufort: P = (K - C) mod 29, cycling key."""
    return [(key[i % len(key)] - c) % MOD for i, c in enumerate(rune_values)]

def vals_to_text(vals):
    """Convert rune values to GP name text."""
    return ''.join(GP_NAMES[v] for v in vals)

def calc_ioc(values):
    if len(values) < 2:
        return 0
    counts = Counter(values)
    n = len(values)
    return sum(c*(c-1) for c in counts.values()) / (n*(n-1)) * MOD

# ============================================================================
# SECTION 1: Full P19 decryption verification
# ============================================================================
print("=" * 80)
print("SECTION 1: Full P19 decryption (ADD mode, no F-skip)")
print("=" * 80)

p19_text = load_runes(19)
p19_runes = get_rune_stream(p19_text)
print(f"P19: {len(p19_runes)} runes")

# Decrypt with ADD mode
p19_plain = decrypt_add_no_fskip(p19_runes, P19_KEY)
p19_plain_text = vals_to_text(p19_plain)
ioc = calc_ioc(p19_plain)
print(f"IoC: {ioc:.4f}")
print(f"Plaintext (continuous): {p19_plain_text}")

# Now show word boundaries from dashes
print(f"\nPlaintext with dash-boundaries preserved:")
key_pos = 0
result_parts = []
for segment in re.split(r'[-.]', p19_text):
    seg_runes = [GP_RUNE_TO_IDX[ch] for ch in segment if ch in GP_RUNE_TO_IDX]
    if not seg_runes:
        result_parts.append('')
        continue
    seg_plain2 = []
    for c in seg_runes:
        p = (c + P19_KEY[key_pos % len(P19_KEY)]) % MOD
        seg_plain2.append(p)
        key_pos += 1
    result_parts.append(vals_to_text(seg_plain2))

print(' | '.join(p for p in result_parts if p))

# ============================================================================
# SECTION 2: Check solved pages for word boundary patterns
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 2: Word boundary analysis on solved pages")
print("=" * 80)

# Check pages that use known Caesar shifts
caesar_pages = {59: 28, 63: 0, 64: 2, 68: 0}

for pn, shift in caesar_pages.items():
    text = load_runes(pn)
    if text is None:
        continue
    
    # Decrypt with Caesar
    runes = get_rune_stream(text)
    plain = [(c - shift) % MOD for c in runes]
    plain_text = vals_to_text(plain)
    
    # Show with dash boundaries
    key_pos = 0
    parts = []
    for segment in re.split(r'[-.]', text):
        seg_runes = [GP_RUNE_TO_IDX[ch] for ch in segment if ch in GP_RUNE_TO_IDX]
        if not seg_runes:
            parts.append('')
            continue
        seg_plain = [(c - shift) % MOD for c in seg_runes]
        parts.append(vals_to_text(seg_plain))
    
    dash_words = [p for p in parts if p]
    n_singles = sum(1 for w in dash_words if len(w) <= 2)  # 1-2 char GP names = single rune
    
    print(f"\n  P{pn} (Caesar {shift}): {len(runes)} runes, {len(dash_words)} dash-segments, {n_singles} single-rune segments")
    print(f"  First 10 segments: {dash_words[:10]}")
    print(f"  Continuous: {plain_text[:100]}...")

# Check pages solved with totient (page 55)
for pn in [55, 56, 57, 58, 60, 61, 62, 65, 66, 67, 69, 70, 71, 72, 73, 74]:
    text = load_runes(pn)
    if text is None:
        continue
    runes = get_rune_stream(text)
    if len(runes) < 20:
        continue
    
    # Just check how many dash-segments are single-rune
    parts = [p for p in re.split(r'[-.]', text) if p.strip()]
    rune_parts = []
    for p in parts:
        runes_in_part = [ch for ch in p if ch in GP_RUNE_TO_IDX]
        if runes_in_part:
            rune_parts.append(len(runes_in_part))
    
    n_singles = sum(1 for ln in rune_parts if ln == 1)
    if rune_parts:
        avg_len = sum(rune_parts) / len(rune_parts)
        print(f"\n  P{pn}: {sum(rune_parts)} runes, {len(rune_parts)} segments, "
              f"{n_singles} singles, avg_len={avg_len:.1f}")

# ============================================================================
# SECTION 3: Unsolved pages — check if dashes are word boundaries or formatting
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 3: Dash-segment statistics for unsolved pages")
print("=" * 80)

for pn in range(17, 55):
    text = load_runes(pn)
    if text is None:
        continue
    
    # Split ONLY on dashes and periods
    parts = [p for p in re.split(r'[-.]', text) if p.strip()]
    rune_parts = []
    for p in parts:
        runes_in_part = [ch for ch in p if ch in GP_RUNE_TO_IDX]
        if runes_in_part:
            rune_parts.append(len(runes_in_part))
    
    # Also split on dashes, periods, AND newlines
    parts_with_nl = [p for p in re.split(r'[-.\s]+', text) if p.strip()]
    rune_parts_nl = []
    for p in parts_with_nl:
        runes_in_part = [ch for ch in p if ch in GP_RUNE_TO_IDX]
        if runes_in_part:
            rune_parts_nl.append(len(runes_in_part))
    
    n_singles_dash = sum(1 for ln in rune_parts if ln == 1)
    n_singles_nl = sum(1 for ln in rune_parts_nl if ln == 1)
    
    avg_dash = sum(rune_parts) / len(rune_parts) if rune_parts else 0
    avg_nl = sum(rune_parts_nl) / len(rune_parts_nl) if rune_parts_nl else 0
    
    print(f"  P{pn}: runes={sum(rune_parts):3d} | "
          f"dash-only: {len(rune_parts):3d} segs, {n_singles_dash:2d} singles, avg={avg_dash:.1f} | "
          f"dash+NL:   {len(rune_parts_nl):3d} segs, {n_singles_nl:2d} singles, avg={avg_nl:.1f}")

# ============================================================================
# SECTION 4: AUTOKEY cipher test
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 4: Autokey cipher with known seeds")
print("=" * 80)

def autokey_decrypt_sub(ciphertext, seed):
    """Autokey Vigenère subtract: P_i = (C_i - K_i) mod 29
    where K starts with seed, then extends with previous plaintext."""
    key = list(seed)
    plaintext = []
    for i, c in enumerate(ciphertext):
        k = key[i] if i < len(key) else plaintext[i - len(seed)]
        p = (c - k) % MOD
        plaintext.append(p)
        if i >= len(seed) - 1:
            pass  # key auto-extends with plaintext
    return plaintext

def autokey_decrypt_add(ciphertext, seed):
    """Autokey ADD: P_i = (C_i + K_i) mod 29"""
    plaintext = []
    for i, c in enumerate(ciphertext):
        if i < len(seed):
            k = seed[i]
        else:
            k = plaintext[i - len(seed)]
        p = (c + k) % MOD
        plaintext.append(p)
    return plaintext

def autokey_decrypt_beau(ciphertext, seed):
    """Autokey Beaufort: P_i = (K_i - C_i) mod 29"""
    plaintext = []
    for i, c in enumerate(ciphertext):
        if i < len(seed):
            k = seed[i]
        else:
            k = plaintext[i - len(seed)]
        p = (k - c) % MOD
        plaintext.append(p)
    return plaintext

def autokey_decrypt_sub_cipher_feedback(ciphertext, seed):
    """Autokey with ciphertext feedback: K extends with previous CIPHERTEXT."""
    plaintext = []
    for i, c in enumerate(ciphertext):
        if i < len(seed):
            k = seed[i]
        else:
            k = ciphertext[i - len(seed)]
        p = (c - k) % MOD
        plaintext.append(p)
    return plaintext

def autokey_decrypt_add_cipher_feedback(ciphertext, seed):
    """Autokey ADD with ciphertext feedback."""
    plaintext = []
    for i, c in enumerate(ciphertext):
        if i < len(seed):
            k = seed[i]
        else:
            k = ciphertext[i - len(seed)]
        p = (c + k) % MOD
        plaintext.append(p)
    return plaintext

def autokey_decrypt_beau_cipher_feedback(ciphertext, seed):
    """Autokey Beaufort with ciphertext feedback."""
    plaintext = []
    for i, c in enumerate(ciphertext):
        if i < len(seed):
            k = seed[i]
        else:
            k = ciphertext[i - len(seed)]
        p = (k - c) % MOD
        plaintext.append(p)
    return plaintext

# Seeds to try
seeds = {
    "DIVINITY": DIVINITY,
    "P19_KEY": P19_KEY,
    "PRIMES_1": [2, 3, 5, 7, 11, 13, 17, 19, 23, 29],
    "PRIMES_GP": [v % MOD for v in GP_PRIMES],
    "FIBONACCI": [0, 1, 1, 2, 3, 5, 8, 13, 21],
    "FIB_MOD29": [0, 1, 1, 2, 3, 5, 8, 13, 21],
    "CONSTANT_0": [0],
    "CONSTANT_1": [1],
    "NOTCOERCED": [9, 3, 16, 5, 22, 18, 4, 5, 18, 23],  # N,O,T,C,OE,E,R,C,E,D
    "CIRCUMFERENCE": [5, 10, 4, 5, 1, 19, 0, 18, 4, 18, 9, 5, 18],
    "FIRFUMFERENFE": [0, 10, 4, 0, 1, 19, 0, 18, 4, 18, 9, 0, 18],
}

# Also try single values 0-28 as seeds
for v in range(29):
    seeds[f"SINGLE_{v}"] = [v]

autokey_methods = [
    ("AK_SUB_PT", autokey_decrypt_sub),
    ("AK_ADD_PT", autokey_decrypt_add),
    ("AK_BEAU_PT", autokey_decrypt_beau),
    ("AK_SUB_CT", autokey_decrypt_sub_cipher_feedback),
    ("AK_ADD_CT", autokey_decrypt_add_cipher_feedback),
    ("AK_BEAU_CT", autokey_decrypt_beau_cipher_feedback),
]

best_results = []

for pn in range(17, 55):
    text = load_runes(pn)
    if text is None:
        continue
    runes = get_rune_stream(text)
    
    for seed_name, seed in seeds.items():
        for method_name, method in autokey_methods:
            try:
                plain = method(runes, seed)
                ioc = calc_ioc(plain)
                if ioc > 1.25:
                    plain_text = vals_to_text(plain[:60])
                    best_results.append((ioc, pn, method_name, seed_name))
                    print(f"  P{pn} {method_name}/{seed_name}: IoC={ioc:.4f}")
                    print(f"    {plain_text}...")
            except Exception as e:
                pass

if not best_results:
    print("  No autokey combination produced IoC > 1.25")
else:
    print(f"\n  Total results with IoC > 1.25: {len(best_results)}")
    best_results.sort(reverse=True)
    print("  Top 10:")
    for ioc, pn, method, seed in best_results[:10]:
        print(f"    P{pn} {method}/{seed}: IoC={ioc:.4f}")

# ============================================================================
# SECTION 5: Autokey with DEOR poem as seed
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 5: Autokey with Deor poem text as seed")
print("=" * 80)

# Load Deor poem
deor_path = os.path.join("Analysis", "Reference_Docs", "deor_poem.txt")
if os.path.exists(deor_path):
    with open(deor_path, 'r', encoding='utf-8') as f:
        deor_text = f.read()
    
    # Tokenize Deor into GP values (simple: map each letter)
    letter_to_gp = {
        'a': 24, 'b': 17, 'c': 5, 'd': 23, 'e': 18, 'f': 0, 'g': 6,
        'h': 8, 'i': 10, 'j': 11, 'k': 5, 'l': 20, 'm': 19, 'n': 9,
        'o': 3, 'p': 13, 'q': 5, 'r': 4, 's': 15, 't': 16, 'u': 1,
        'v': 1, 'w': 7, 'x': 14, 'y': 26, 'z': 15,
    }
    
    # Extract only OE text (before any modern English translation)
    # Simple: just take alphabetic characters
    deor_values = []
    for ch in deor_text.lower():
        if ch in letter_to_gp:
            deor_values.append(letter_to_gp[ch])
    
    print(f"Deor poem tokenized: {len(deor_values)} values")
    
    for pn in range(17, 55):
        text = load_runes(pn)
        if text is None:
            continue
        runes = get_rune_stream(text)
        
        for method_name, method in autokey_methods:
            try:
                plain = method(runes, deor_values)
                ioc = calc_ioc(plain)
                if ioc > 1.25:
                    print(f"  P{pn} {method_name}/DEOR: IoC={ioc:.4f}")
                    print(f"    {vals_to_text(plain[:60])}...")
            except:
                pass
else:
    print("  Deor poem file not found")

# ============================================================================
# SECTION 6: Running key with Deor (not autokey — whole Deor as key)
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 6: Running key — full Deor poem as key (no autokey)")  
print("=" * 80)

if 'deor_values' in dir():
    for pn in range(17, 55):
        text = load_runes(pn)
        if text is None:
            continue
        runes = get_rune_stream(text)
        if len(runes) > len(deor_values):
            continue
        
        # Try different starting positions within Deor
        best_ioc = 0
        best_start = 0
        for start in range(0, min(len(deor_values) - len(runes), 100)):
            key_slice = deor_values[start:start+len(runes)]
            for mode in ['sub', 'beau', 'add']:
                if mode == 'sub':
                    plain = [(c - k) % MOD for c, k in zip(runes, key_slice)]
                elif mode == 'beau':
                    plain = [(k - c) % MOD for c, k in zip(runes, key_slice)]
                elif mode == 'add':
                    plain = [(c + k) % MOD for c, k in zip(runes, key_slice)]
                ioc = calc_ioc(plain)
                if ioc > best_ioc:
                    best_ioc = ioc
                    best_start = start
        
        if best_ioc > 1.2:
            print(f"  P{pn}: best IoC={best_ioc:.4f} at Deor offset {best_start}")

# ============================================================================
# SECTION 7: Progressive key (key = cumulative sum of ciphertext)
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 7: Progressive/cumulative key schemes")
print("=" * 80)

for pn in range(17, 55):
    text = load_runes(pn)
    if text is None:
        continue
    runes = get_rune_stream(text)
    
    for scheme_name, key_func in [
        ("cumsum", lambda rs: [sum(rs[:i+1]) % MOD for i in range(len(rs))]),
        ("cumsum_prev", lambda rs: [0] + [sum(rs[:i]) % MOD for i in range(1, len(rs))]),
        ("cumxor", lambda rs: [0] + [rs[0]] + [rs[i-1] ^ rs[i-2] for i in range(2, len(rs))]),
        ("pos_times_cipher", lambda rs: [(i * c) % MOD for i, c in enumerate(rs)]),
    ]:
        key = key_func(runes)
        for mode in ['sub', 'add', 'beau']:
            if mode == 'sub':
                plain = [(c - k) % MOD for c, k in zip(runes, key)]
            elif mode == 'add':
                plain = [(c + k) % MOD for c, k in zip(runes, key)]
            elif mode == 'beau':
                plain = [(k - c) % MOD for c, k in zip(runes, key)]
            ioc = calc_ioc(plain)
            if ioc > 1.25:
                print(f"  P{pn} {scheme_name}/{mode}: IoC={ioc:.4f}")
                print(f"    {vals_to_text(plain[:60])}...")

# ============================================================================
# SECTION 8: Verify autokey_output.txt existence and content
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 8: Prior autokey results check")
print("=" * 80)

if os.path.exists("autokey_output.txt"):
    with open("autokey_output.txt", 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    print(f"autokey_output.txt exists: {len(content)} bytes")
    # Show just the summary/best results
    for line in content.split('\n'):
        if 'IoC' in line and any(x in line for x in ['1.2', '1.3', '1.4', '1.5', '1.6', '1.7', '1.8']):
            print(f"  {line.strip()}")
else:
    print("  autokey_output.txt not found")

print("\n\nDONE")
