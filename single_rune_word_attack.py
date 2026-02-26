#!/usr/bin/env python3
"""
SINGLE-RUNE WORD ATTACK
========================
Every single-letter word in English must be "I" or "A".
In Gematria Primus: I=10, A=24.

For each single-rune word at position p with cipher value C:
  - SUB mode: K = (C - P) mod 29
  - BEAU mode: K = (P + C) mod 29  [since P = K - C mod 29]
  - ADD mode: K = (P - C) mod 29

Each position yields exactly 2 candidate key values (one for I, one for A).
If the keystream has structure (periodic, LFSR, mathematical), we can recover it.
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os, json
from collections import Counter, defaultdict
from itertools import product
from math import gcd

GP_RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛂᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
GP_RUNE_TO_IDX = {r: i for i, r in enumerate(GP_RUNES)}
GP_IDX_TO_RUNE = {i: r for i, r in enumerate(GP_RUNES)}
GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
GP_NAMES = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]
MOD = 29

PAGES_DIR = r"LiberPrimus\pages"
UNSOLVED_RANGE = range(17, 55)  # pages 17-54

def load_runes(page_num):
    """Load rune text for a page, preserving spaces."""
    folder = f"page_{page_num:02d}"
    path = os.path.join(PAGES_DIR, folder, "runes.txt")
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return f.read().strip()

def split_into_words(text):
    """Split rune text into words. Words are separated by '-', newlines, '.', spaces."""
    import re
    # Replace all separators with a common delimiter
    tokens = re.split(r'[-\s.&$]+', text)
    return [t for t in tokens if t.strip()]

def parse_rune_positions(text):
    """Parse rune text into list of (rune_char, rune_index, word_length).
    Returns: list of all runes with their global position and what word they belong to.
    Also returns: list of (word_start_pos, word_length, [rune_indices])
    """
    runes = []
    words = []
    pos = 0
    for token in split_into_words(text):
        word_runes = []
        for ch in token:
            if ch in GP_RUNE_TO_IDX:
                runes.append((ch, pos, len([c for c in token if c in GP_RUNE_TO_IDX])))
                word_runes.append(pos)
                pos += 1
        if word_runes:
            words.append((word_runes[0], len(word_runes), word_runes))
    return runes, words

def find_single_rune_words(text):
    """Find all single-rune words and their positions."""
    runes, words = parse_rune_positions(text)
    singles = []
    for word_start, word_len, word_indices in words:
        if word_len == 1:
            rune_char = None
            for ch, pos, wl in runes:
                if pos == word_start:
                    rune_char = ch
                    break
            if rune_char:
                c_val = GP_RUNE_TO_IDX[rune_char]
                singles.append({
                    'pos': word_start,
                    'rune': rune_char,
                    'c_val': c_val,
                    'k_if_I_sub': (c_val - 10) % MOD,
                    'k_if_A_sub': (c_val - 24) % MOD,
                    'k_if_I_beau': (10 + c_val) % MOD,
                    'k_if_A_beau': (24 + c_val) % MOD,
                    'k_if_I_add': (10 - c_val) % MOD,
                    'k_if_A_add': (24 - c_val) % MOD,
                })
    return singles

def compute_fskip_key_pos(text, target_pos):
    """Compute key counter position considering F-skip.
    F-skip: when cipher rune = F (index 0), key doesn't advance."""
    key_pos = 0
    pos = 0
    for ch in text:
        if ch in GP_RUNE_TO_IDX:
            if pos == target_pos:
                return key_pos
            if GP_RUNE_TO_IDX[ch] != 0:  # Not F
                key_pos += 1
            pos += 1
    return key_pos

print("=" * 80)
print("SINGLE-RUNE WORD ATTACK ON LIBER PRIMUS")
print("=" * 80)

# ============================================================================
# SECTION 1: Collect all single-rune words across unsolved pages
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 1: Single-rune word inventory")
print("=" * 80)

all_singles = {}
total_singles = 0

for pn in UNSOLVED_RANGE:
    text = load_runes(pn)
    if text is None:
        continue
    singles = find_single_rune_words(text)
    if singles:
        # Also compute F-skip key positions
        for s in singles:
            s['key_pos'] = compute_fskip_key_pos(text, s['pos'])
        all_singles[pn] = singles
        total_singles += len(singles)
        print(f"  P{pn}: {len(singles)} single-rune words")
        for s in singles:
            print(f"    pos={s['pos']:4d} key_pos={s['key_pos']:4d} rune={s['rune']}({s['c_val']:2d}/{GP_NAMES[s['c_val']]:>3s})"
                  f"  K_sub: I→{s['k_if_I_sub']:2d} A→{s['k_if_A_sub']:2d}"
                  f"  K_beau: I→{s['k_if_I_beau']:2d} A→{s['k_if_A_beau']:2d}")

print(f"\nTotal single-rune words: {total_singles}")

# ============================================================================
# SECTION 2: Per-page periodicity analysis
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 2: Periodicity analysis of candidate key values")
print("=" * 80)

for pn, singles in all_singles.items():
    if len(singles) < 3:
        continue
    print(f"\n  Page {pn} ({len(singles)} single-rune words):")
    
    # For each cipher mode, check if any period L makes all single-rune positions consistent
    for mode_name, k_i_key, k_a_key in [
        ("SUB", 'k_if_I_sub', 'k_if_A_sub'),
        ("BEAU", 'k_if_I_beau', 'k_if_A_beau'),
        ("ADD", 'k_if_I_add', 'k_if_A_add'),
    ]:
        best_period = None
        best_count = 0
        
        # Try periods 1-200
        for period in range(1, 201):
            # Group singles by key_pos mod period
            groups = defaultdict(list)
            for s in singles:
                groups[s['key_pos'] % period].append(s)
            
            # For each group, check if there's a consistent key value
            # Each position has 2 candidates. Check if all positions in a group share a common value.
            consistent = True
            for slot, group_singles in groups.items():
                if len(group_singles) < 2:
                    continue
                # Find intersection of candidate keys
                possible = None
                for gs in group_singles:
                    candidates = {gs[k_i_key], gs[k_a_key]}
                    if possible is None:
                        possible = candidates
                    else:
                        possible = possible & candidates
                if not possible:
                    consistent = False
                    break
            
            if consistent:
                # Count how many slots had multiple entries that agreed
                constrained_slots = sum(1 for slot, g in groups.items() if len(g) >= 2)
                if constrained_slots > best_count:
                    best_count = constrained_slots
                    best_period = period
        
        if best_period and best_count >= 2:
            print(f"    {mode_name}: period={best_period} with {best_count} constrained slots agreeing")
            # Show the key values at constrained slots
            groups = defaultdict(list)
            for s in singles:
                groups[s['key_pos'] % best_period].append(s)
            for slot in sorted(groups.keys()):
                g = groups[slot]
                if len(g) >= 2:
                    possible = None
                    for gs in g:
                        candidates = {gs[k_i_key], gs[k_a_key]}
                        if possible is None:
                            possible = candidates
                        else:
                            possible = possible & candidates
                    positions = [gs['key_pos'] for gs in g]
                    print(f"      slot {slot:3d}: key={possible} (from positions {positions})")

# ============================================================================
# SECTION 3: Cross-page consistency (same key across all pages)
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 3: Cross-page periodicity (shared key hypothesis)")
print("=" * 80)

# Collect ALL single-rune words with their positions across all pages
all_combined = []
for pn, singles in all_singles.items():
    for s in singles:
        all_combined.append({**s, 'page': pn})

print(f"Total constraints: {len(all_combined)}")

# Test if a single periodic key works across all pages
for mode_name, k_i_key, k_a_key in [
    ("SUB", 'k_if_I_sub', 'k_if_A_sub'),
    ("BEAU", 'k_if_I_beau', 'k_if_A_beau'),
]:
    print(f"\n  Mode: {mode_name}")
    for period in [8, 29, 47, 58, 59, 131, 167, 761]:  # Known candidate periods
        groups = defaultdict(list)
        for s in all_combined:
            groups[s['key_pos'] % period].append(s)
        
        # Count consistent slots
        consistent_slots = 0
        inconsistent_slots = 0
        for slot, g in groups.items():
            if len(g) < 2:
                continue
            possible = None
            for gs in g:
                candidates = {gs[k_i_key], gs[k_a_key]}
                if possible is None:
                    possible = candidates
                else:
                    possible = possible & candidates
            if possible:
                consistent_slots += 1
            else:
                inconsistent_slots += 1
        
        total_multi = consistent_slots + inconsistent_slots
        if total_multi > 0:
            pct = 100.0 * consistent_slots / total_multi
            print(f"    period={period:4d}: {consistent_slots}/{total_multi} multi-entry slots consistent ({pct:.1f}%)")

# ============================================================================
# SECTION 4: Key value distribution analysis
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 4: Key value distribution (which values appear most?)")
print("=" * 80)

for mode_name, k_i_key, k_a_key in [
    ("SUB", 'k_if_I_sub', 'k_if_A_sub'),
    ("BEAU", 'k_if_I_beau', 'k_if_A_beau'),
]:
    print(f"\n  Mode: {mode_name}")
    # If all singles decrypt to I, what's the distribution?
    i_counts = Counter(s[k_i_key] for s in all_combined)
    a_counts = Counter(s[k_a_key] for s in all_combined)
    
    print(f"    If ALL are I: top values = {i_counts.most_common(10)}")
    print(f"    If ALL are A: top values = {a_counts.most_common(10)}")
    
    # Combined (either I or A)
    both_counts = Counter()
    for s in all_combined:
        both_counts[s[k_i_key]] += 1
        both_counts[s[k_a_key]] += 1
    print(f"    Either I or A: top values = {both_counts.most_common(10)}")

# ============================================================================
# SECTION 5: Pages with most constraints — exhaustive check
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 5: Per-page exhaustive period search (top pages)")
print("=" * 80)

# Sort pages by number of single-rune words
sorted_pages = sorted(all_singles.items(), key=lambda x: len(x[1]), reverse=True)

for pn, singles in sorted_pages[:8]:
    text = load_runes(pn)
    rune_count = sum(1 for ch in text if ch in GP_RUNE_TO_IDX)
    n_singles = len(singles)
    print(f"\n  Page {pn}: {n_singles} singles, {rune_count} total runes")
    
    # For each mode, find ALL consistent periods
    for mode_name, k_i_key, k_a_key in [
        ("SUB", 'k_if_I_sub', 'k_if_A_sub'),
        ("BEAU", 'k_if_I_beau', 'k_if_A_beau'),
    ]:
        consistent_periods = []
        max_period = min(rune_count, 500)
        
        for period in range(1, max_period + 1):
            groups = defaultdict(list)
            for s in singles:
                groups[s['key_pos'] % period].append(s)
            
            consistent = True
            n_constrained = 0
            for slot, g in groups.items():
                if len(g) < 2:
                    continue
                possible = None
                for gs in g:
                    candidates = {gs[k_i_key], gs[k_a_key]}
                    if possible is None:
                        possible = candidates
                    else:
                        possible = possible & candidates
                if not possible:
                    consistent = False
                    break
                n_constrained += 1
            
            if consistent and n_constrained >= 2:
                consistent_periods.append((period, n_constrained))
        
        if consistent_periods:
            # Sort by constrained slots descending
            consistent_periods.sort(key=lambda x: -x[1])
            top = consistent_periods[:15]
            print(f"    {mode_name}: {len(consistent_periods)} consistent periods, top: {top}")

# ============================================================================
# SECTION 6: Difference analysis between key positions
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 6: Key position differences and GCD analysis")
print("=" * 80)

for pn, singles in sorted_pages[:8]:
    if len(singles) < 4:
        continue
    print(f"\n  Page {pn} ({len(singles)} singles):")
    positions = [s['key_pos'] for s in singles]
    
    # All pairwise differences
    diffs = []
    for i in range(len(positions)):
        for j in range(i+1, len(positions)):
            diffs.append(abs(positions[j] - positions[i]))
    
    # GCD of all differences
    g = diffs[0]
    for d in diffs[1:]:
        g = gcd(g, d)
    
    print(f"    Positions: {positions}")
    print(f"    GCD of all pairwise diffs: {g}")
    
    # Factor frequencies of differences
    factor_counts = Counter()
    for d in diffs:
        for f in range(2, min(d+1, 200)):
            if d % f == 0:
                factor_counts[f] += 1
    if factor_counts:
        top_factors = factor_counts.most_common(10)
        print(f"    Most common factors: {top_factors}")

# ============================================================================
# SECTION 7: Cipher value analysis — what runes appear as single words?
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 7: Cipher rune distribution for single-rune words")
print("=" * 80)

cipher_vals = Counter(s['c_val'] for s in all_combined)
print(f"Cipher value distribution:")
for val, count in sorted(cipher_vals.items()):
    print(f"  {GP_NAMES[val]:>3s}({val:2d}): {'#' * count} ({count})")

# If cipher is simple shift (Caesar), all singles should map to same key
# I.e., all c_vals should be either (10+k)%29 or (24+k)%29 for some fixed k
# That means c_vals should have at most 2 distinct values (if they differ by 14)
unique_cvals = sorted(set(s['c_val'] for s in all_combined))
print(f"\nUnique cipher values at single-rune positions: {unique_cvals}")
print(f"Count: {len(unique_cvals)} (Caesar would require <=2, differing by 14)")

# Check if any pair of values differs by 14 and covers most singles
for v1 in range(29):
    v2 = (v1 + 14) % 29
    covered = sum(1 for s in all_combined if s['c_val'] in (v1, v2))
    if covered > total_singles * 0.4:
        k = (v1 - 10) % 29
        print(f"  Caesar k={k}: values {v1},{v2} cover {covered}/{total_singles}")

# ============================================================================
# SECTION 8: Running key test — if key = position or prime-based
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 8: Mathematical key functions (k = f(position))")
print("=" * 80)

import sympy
primes_list = list(sympy.primerange(2, 10000))

for pn, singles in sorted_pages[:5]:
    if len(singles) < 5:
        continue
    print(f"\n  Page {pn} ({len(singles)} singles):")
    
    for mode_name, k_i_key, k_a_key in [
        ("SUB", 'k_if_I_sub', 'k_if_A_sub'),
        ("BEAU", 'k_if_I_beau', 'k_if_A_beau'),
    ]:
        # Test: k = position mod 29
        match_pos_mod = sum(1 for s in singles if (s['key_pos'] % MOD) in (s[k_i_key], s[k_a_key]))
        
        # Test: k = prime(position) mod 29
        match_prime_mod = 0
        for s in singles:
            if s['key_pos'] < len(primes_list):
                pk = primes_list[s['key_pos']] % MOD
                if pk in (s[k_i_key], s[k_a_key]):
                    match_prime_mod += 1
        
        # Test: k = nth_prime_GP (position into GP primes, cycling)
        match_gp_prime = 0
        for s in singles:
            pk = GP_PRIMES[s['key_pos'] % len(GP_PRIMES)] % MOD
            if pk in (s[k_i_key], s[k_a_key]):
                match_gp_prime += 1
        
        # Test: k = Fibonacci(position) mod 29
        fibs = [0, 1]
        for _ in range(1000):
            fibs.append((fibs[-1] + fibs[-2]) % MOD)
        match_fib = sum(1 for s in singles if fibs[s['key_pos']] in (s[k_i_key], s[k_a_key]))
        
        # Test: k = totient(position+1) mod 29
        match_totient = 0
        for s in singles:
            t = sympy.totient(s['key_pos'] + 1) % MOD
            if t in (s[k_i_key], s[k_a_key]):
                match_totient += 1
        
        # Test: k = position^2 mod 29
        match_sq = sum(1 for s in singles if ((s['key_pos']**2) % MOD) in (s[k_i_key], s[k_a_key]))
        
        # Test: k = 2^position mod 29
        match_exp = sum(1 for s in singles if (pow(2, s['key_pos'], MOD)) in (s[k_i_key], s[k_a_key]))
        
        # Test: k = 3^position mod 29
        match_exp3 = sum(1 for s in singles if (pow(3, s['key_pos'], MOD)) in (s[k_i_key], s[k_a_key]))
        
        expected = len(singles) * 4 / 29  # Expected matches by chance (2 candidates out of 29)
        
        results = [
            ("pos%29", match_pos_mod),
            ("prime(pos)%29", match_prime_mod),
            ("GP_prime[pos]%29", match_gp_prime),
            ("fib(pos)%29", match_fib),
            ("totient(pos+1)%29", match_totient),
            ("pos²%29", match_sq),
            ("2^pos%29", match_exp),
            ("3^pos%29", match_exp3),
        ]
        
        significant = [(name, cnt) for name, cnt in results if cnt > expected * 2]
        if significant:
            print(f"    {mode_name} significant: {significant} (expected={expected:.1f})")
        else:
            best = max(results, key=lambda x: x[1])
            print(f"    {mode_name} best: {best} (expected={expected:.1f})")

# ============================================================================
# SECTION 9: LFSR consistency check
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 9: LFSR consistency check")
print("=" * 80)
print("Testing if key values at known positions are consistent with LFSR over GF(29)")

def solve_lfsr_gf29(known_values, degree, mod=29):
    """Try to find LFSR coefficients that generate the known values.
    known_values: list of (position, value) pairs
    Returns coefficients if found, None otherwise.
    """
    # We need at least 2*degree consecutive values
    # Since we don't have consecutive values, we need to check if positions
    # can be connected via an LFSR of given degree
    
    # For sparse positions, this is much harder.
    # Instead, check: for each assignment of I/A to singles,
    # can we find an LFSR that produces those key values?
    pass

# For each page with enough singles, try brute-force I/A assignment
for pn, singles in sorted_pages[:5]:
    if len(singles) < 5:
        continue
    
    text = load_runes(pn)
    rune_count = sum(1 for ch in text if ch in GP_RUNE_TO_IDX)
    
    print(f"\n  Page {pn} ({len(singles)} singles, {rune_count} runes):")
    
    for mode_name, k_i_key, k_a_key in [
        ("SUB", 'k_if_I_sub', 'k_if_A_sub'),
        ("BEAU", 'k_if_I_beau', 'k_if_A_beau'),
    ]:
        # For each I/A assignment, compute key values at those positions
        # Then check if they could come from a simple linear function: k = a*pos + b mod 29
        n = len(singles)
        
        best_linear_count = 0
        best_linear_params = None
        
        # Testing linear keys: k(p) = a*p + b mod 29
        for a in range(MOD):
            for b in range(MOD):
                match = 0
                for s in singles:
                    k_predicted = (a * s['key_pos'] + b) % MOD
                    if k_predicted in (s[k_i_key], s[k_a_key]):
                        match += 1
                if match > best_linear_count:
                    best_linear_count = match
                    best_linear_params = (a, b)
        
        expected = n * 4 / 29  # 2 candidate values out of 29
        if best_linear_count > expected * 2 or best_linear_count >= n * 0.6:
            print(f"    {mode_name} LINEAR k={best_linear_params[0]}*pos+{best_linear_params[1]}: "
                  f"{best_linear_count}/{n} match (expected={expected:.1f})")
        
        # Testing quadratic: k(p) = a*p^2 + b*p + c mod 29
        best_quad_count = 0
        best_quad_params = None
        
        for a in range(MOD):
            for b in range(MOD):
                for c in range(MOD):
                    match = 0
                    for s in singles:
                        p = s['key_pos']
                        k_predicted = (a * p * p + b * p + c) % MOD
                        if k_predicted in (s[k_i_key], s[k_a_key]):
                            match += 1
                    if match > best_quad_count:
                        best_quad_count = match
                        best_quad_params = (a, b, c)
                        if match == n:
                            break
                if best_quad_count == n:
                    break
            if best_quad_count == n:
                break
        
        if best_quad_count > best_linear_count and (best_quad_count > expected * 2 or best_quad_count >= n * 0.6):
            print(f"    {mode_name} QUADRATIC k={best_quad_params[0]}*p²+{best_quad_params[1]}*p+{best_quad_params[2]}: "
                  f"{best_quad_count}/{n} match (expected={expected:.1f})")

# ============================================================================
# SECTION 10: Full decryption attempt with best key functions
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 10: Trying promising key functions for full decryption")
print("=" * 80)

def decrypt_with_key_func(text, key_func, mode='sub'):
    """Decrypt rune text using a key function k(position)."""
    result = []
    key_pos = 0
    for token in split_into_words(text):
        word = []
        for ch in token:
            if ch in GP_RUNE_TO_IDX:
                c = GP_RUNE_TO_IDX[ch]
                if c == 0:  # F-skip
                    word.append(0)
                else:
                    k = key_func(key_pos) % MOD
                    if mode == 'sub':
                        p = (c - k) % MOD
                    elif mode == 'beau':
                        p = (k - c) % MOD
                    elif mode == 'add':
                        p = (c + k) % MOD
                    word.append(p)
                    key_pos += 1
        result.append(word)
    return result

def calc_ioc(values):
    if len(values) < 2:
        return 0
    counts = Counter(values)
    n = len(values)
    numerator = sum(c * (c - 1) for c in counts.values())
    denominator = n * (n - 1)
    return (numerator / denominator) * MOD if denominator > 0 else 0

# Test a range of mathematical key functions on all unsolved pages
key_functions = [
    ("constant_0", lambda p: 0),
    ("pos_mod29", lambda p: p % 29),
    ("prime_pos_mod29", lambda p: primes_list[p % len(primes_list)] % 29),
    ("gp_prime_cycle", lambda p: GP_PRIMES[p % len(GP_PRIMES)] % 29),
    ("fib_mod29", lambda p: fibs[p] if p < len(fibs) else 0),
    ("2^p_mod29", lambda p: pow(2, p, 29)),
    ("3^p_mod29", lambda p: pow(3, p, 29)),
    ("5^p_mod29", lambda p: pow(5, p, 29)),
    ("7^p_mod29", lambda p: pow(7, p, 29)),
    ("11^p_mod29", lambda p: pow(11, p, 29)),
    ("13^p_mod29", lambda p: pow(13, p, 29)),
    ("p_squared_mod29", lambda p: (p * p) % 29),
    ("p_cubed_mod29", lambda p: (p * p * p) % 29),
]

best_results = []

for pn in UNSOLVED_RANGE:
    text = load_runes(pn)
    if text is None:
        continue
    
    for kf_name, kf in key_functions:
        for mode in ['sub', 'beau']:
            decrypted = decrypt_with_key_func(text, kf, mode)
            flat = [v for word in decrypted for v in word]
            ioc = calc_ioc(flat)
            if ioc > 1.3:
                # Check word scores
                ws = sum(1 for word in decrypted if len(word) >= 2 
                         and all(GP_NAMES[v] in "AEIOUY" or len(GP_NAMES[v]) > 1 
                                 for v in word[:1]))
                best_results.append((ioc, pn, kf_name, mode))
                print(f"  P{pn} {kf_name}/{mode}: IoC={ioc:.4f}")

if not best_results:
    print("  No key function produced IoC > 1.3 on any page")

# ============================================================================
# SECTION 11: P19 key pattern matching
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 11: Test P19 key (47 values) on pages with single-rune word validation")
print("=" * 80)

P19_KEY = [24, 15, 2, 24, 4, 21, 11, 10, 20, 16, 9, 19, 26, 11, 7, 5, 11, 6, 27, 8, 22, 25, 21, 16, 25, 0, 27, 9, 21, 7, 27, 15, 21, 9, 3, 16, 5, 22, 18, 4, 5, 18, 23, 21, 1, 10, 24]

for pn in UNSOLVED_RANGE:
    if pn == 19:
        continue
    text = load_runes(pn)
    if text is None:
        continue
    singles = all_singles.get(pn, [])
    
    for mode in ['sub', 'beau']:
        # Decrypt with P19 key (cycling)
        decrypted = decrypt_with_key_func(text, lambda p: P19_KEY[p % len(P19_KEY)], mode)
        flat = [v for word in decrypted for v in word]
        ioc = calc_ioc(flat)
        
        # Check single-rune word consistency
        if singles:
            consistent = 0
            for s in singles:
                k = P19_KEY[s['key_pos'] % len(P19_KEY)]
                if mode == 'sub':
                    p_val = (s['c_val'] - k) % MOD
                elif mode == 'beau':
                    p_val = (k - s['c_val']) % MOD
                if p_val in (10, 24):  # I or A
                    consistent += 1
            n_s = len(singles)
            expected_match = n_s * 2 / 29
            if consistent > expected_match * 2 or ioc > 1.2:
                print(f"  P{pn} P19key/{mode}: IoC={ioc:.4f}, single-word match={consistent}/{n_s} (expected={expected_match:.1f})")

# ============================================================================
# SECTION 12: "DIVINITY" key with single-rune word validation
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 12: DIVINITY key validation against single-rune words")
print("=" * 80)

DIVINITY = [23, 10, 1, 10, 9, 10, 16, 26]

for pn, singles in all_singles.items():
    for mode in ['sub', 'beau']:
        consistent = 0
        details = []
        for s in singles:
            k = DIVINITY[s['key_pos'] % len(DIVINITY)]
            if mode == 'sub':
                p_val = (s['c_val'] - k) % MOD
            elif mode == 'beau':
                p_val = (k - s['c_val']) % MOD
            if p_val in (10, 24):
                consistent += 1
                details.append(f"pos{s['key_pos']}→{'I' if p_val==10 else 'A'}")
        
        n_s = len(singles)
        expected = n_s * 2 / 29
        if consistent > expected * 2:
            print(f"  P{pn} DIVINITY/{mode}: match={consistent}/{n_s} (expected={expected:.1f}) {details}")

print("\n\nDONE")
