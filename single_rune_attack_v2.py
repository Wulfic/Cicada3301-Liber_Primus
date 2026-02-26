#!/usr/bin/env python3
"""
SINGLE-RUNE WORD ATTACK - PHASE 2
===================================
1. Validate on solved P19: what do single-rune words actually decrypt to?
2. Broader search with mathematical key functions (no sympy dependency)
3. Per-page period search with PROPER consistency check
4. LFSR linear consistency check
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os, json, re
from collections import Counter, defaultdict
from math import gcd

GP_RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛂᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
GP_RUNE_TO_IDX = {r: i for i, r in enumerate(GP_RUNES)}
GP_NAMES = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]
GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
MOD = 29

PAGES_DIR = r"LiberPrimus\pages"
P19_KEY = [24,15,2,24,4,21,11,10,20,16,9,19,26,11,7,5,11,6,27,8,22,25,21,16,25,0,27,9,21,7,27,15,21,9,3,16,5,22,18,4,5,18,23,21,1,10,24]

def load_runes(page_num):
    folder = f"page_{page_num:02d}"
    path = os.path.join(PAGES_DIR, folder, "runes.txt")
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return f.read().strip()

def split_words(text):
    return [t for t in re.split(r'[-\s.&$]+', text) if t.strip()]

def get_rune_values(text):
    """Get flat list of (rune_char, rune_idx) for all runes in text."""
    result = []
    for ch in text:
        if ch in GP_RUNE_TO_IDX:
            result.append((ch, GP_RUNE_TO_IDX[ch]))
    return result

def find_single_rune_words_with_positions(text):
    """Find single-rune words with their position in the rune stream."""
    singles = []
    rune_pos = 0
    for word in split_words(text):
        word_runes = [(ch, GP_RUNE_TO_IDX[ch]) for ch in word if ch in GP_RUNE_TO_IDX]
        if len(word_runes) == 1:
            ch, val = word_runes[0]
            # Compute key_pos (with F-skip)
            key_pos = compute_key_pos_at(text, rune_pos)
            singles.append({
                'rune_pos': rune_pos,
                'key_pos': key_pos,
                'rune': ch,
                'c_val': val,
            })
        rune_pos += len(word_runes)
    return singles

def compute_key_pos_at(text, target_rune_pos):
    """Compute key counter at given rune position, considering F-skip."""
    key_pos = 0
    rune_pos = 0
    for ch in text:
        if ch in GP_RUNE_TO_IDX:
            if rune_pos == target_rune_pos:
                return key_pos
            if GP_RUNE_TO_IDX[ch] != 0:
                key_pos += 1
            rune_pos += 1
    return key_pos

def decrypt_beaufort_fskip(text, key):
    """Decrypt with Beaufort cipher + F-skip."""
    result = []
    key_pos = 0
    for ch in text:
        if ch in GP_RUNE_TO_IDX:
            c = GP_RUNE_TO_IDX[ch]
            if c == 0:  # F-skip
                result.append(0)
            else:
                k = key[key_pos % len(key)]
                p = (k - c) % MOD
                result.append(p)
                key_pos += 1
    return result

def sieve_primes(n):
    """Simple sieve of Eratosthenes."""
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]

primes_list = sieve_primes(100000)

# ============================================================================
# SECTION 1: VALIDATION — What do P19's single-rune words actually decrypt to?
# ============================================================================
print("=" * 80)
print("SECTION 1: P19 VALIDATION — What are single-rune words in solved text?")
print("=" * 80)

p19_text = load_runes(19)
p19_singles = find_single_rune_words_with_positions(p19_text)
p19_decrypted = decrypt_beaufort_fskip(p19_text, P19_KEY)

print(f"P19 has {len(p19_singles)} single-rune words:")
plaintext_values = Counter()
for s in p19_singles:
    p_val = p19_decrypted[s['rune_pos']]
    p_name = GP_NAMES[p_val]
    plaintext_values[p_val] += 1
    print(f"  rune_pos={s['rune_pos']:3d} key_pos={s['key_pos']:3d} "
          f"cipher={GP_NAMES[s['c_val']]:>3s}({s['c_val']:2d}) "
          f"key={P19_KEY[s['key_pos'] % 47]:2d} "
          f"plaintext={p_name:>3s}({p_val:2d})")

print(f"\nPlaintext value distribution for P19 single-rune words:")
for val, count in sorted(plaintext_values.items(), key=lambda x: -x[1]):
    print(f"  {GP_NAMES[val]:>3s}({val:2d}): {count}")

# What are the most common single-letter OE words?
print(f"\nDoes I(10) or A(24) appear? I={plaintext_values.get(10,0)}, A={plaintext_values.get(24,0)}")

# Also check solved pages 0-16 for single-rune words
print("\n--- Checking ALL solved pages for single-rune word plaintext values ---")
# Pages 0-16 solve with various methods; let's just check pages that use known methods
# For simplicity, check page 00 (= page 17 first 262 runes, same cipher)
# Actually, we need to check what method each solved page uses. 
# Let's check the easier ones: pages solved with Caesar

# Pages with known Caesar shifts from batch_attack_solutions.json:
# P59=Caesar28, P63=Caesar0, P64=Caesar2, P68=Caesar0
# Pages 0-16 use various methods from the Liber Primus solving

# Let me check pages 55-74 which are mostly solved with simpler methods
for pn in range(55, 75):
    text = load_runes(pn)
    if text is None:
        continue
    singles = find_single_rune_words_with_positions(text)
    if not singles:
        continue
    # Try Caesar shifts 0-28
    for shift in range(MOD):
        all_runes = get_rune_values(text)
        decrypted = [(v - shift) % MOD for _, v in all_runes]
        # Check if this produces reasonable text (IoC > 1.5)
        counts = Counter(decrypted)
        n = len(decrypted)
        if n < 20:
            continue
        ioc = sum(c*(c-1) for c in counts.values()) / (n*(n-1)) * MOD if n > 1 else 0
        if ioc > 1.5:
            print(f"\n  P{pn} Caesar({shift}) IoC={ioc:.3f}, {len(singles)} singles:")
            for s in singles:
                p_val = (s['c_val'] - shift) % MOD
                print(f"    pos={s['rune_pos']:3d} cipher={GP_NAMES[s['c_val']]:>3s} -> plaintext={GP_NAMES[p_val]:>3s}({p_val})")
            break

# ============================================================================
# SECTION 2: BROADER SEARCH — What if singles can be ANY common OE letter?
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 2: Mathematical key functions — broad plaintext candidates")
print("=" * 80)

# Based on P19 validation, determine which plaintext values are valid for singles
# For now, test multiple hypotheses:
valid_plains_narrow = {10, 24}  # I, A
valid_plains_broad = {10, 24, 3, 22, 23}  # I, A, O, OE, D (common OE 1-letter words)
valid_plains_any = set(range(29))  # Any value

# Collect all singles
all_singles = {}
for pn in range(17, 55):
    text = load_runes(pn)
    if text is None:
        continue
    singles = find_single_rune_words_with_positions(text)
    if singles:
        all_singles[pn] = singles

total = sum(len(v) for v in all_singles.values())
print(f"Total single-rune words across P17-P54: {total}")

# ============================================================================
# SECTION 3: Per-page period search with proper P19 validation
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 3: P19 period validation — does period 47 work?")
print("=" * 80)

# First verify the algorithm works on P19
p19_s = all_singles.get(19, [])
print(f"P19 singles: {len(p19_s)}")

# For Beaufort mode, check period 47
for mode_name, key_func in [("BEAU", lambda c, k: (k - c) % MOD), ("SUB", lambda c, k: (c - k) % MOD)]:
    for period in [47]:
        groups = defaultdict(list)
        for s in p19_s:
            groups[s['key_pos'] % period].append(s)
        
        # For each group with 2+ entries, check if consistent with KNOWN key
        all_ok = True
        for slot, g in groups.items():
            if len(g) < 2:
                continue
            # What does key[slot] decrypt each to?
            k = P19_KEY[slot]
            plains = set()
            for gs in g:
                p = key_func(gs['c_val'], k)
                plains.add(p)
            # All should produce the same plaintext (same key, same slot)
            if len(plains) > 1:
                all_ok = False
                print(f"    INCONSISTENT at slot {slot}: {plains}")
        
        # Check what plaintext each single produces with the known key
        for s in p19_s:
            k = P19_KEY[s['key_pos'] % period]
            p = key_func(s['c_val'], k)
            print(f"    {mode_name} slot={s['key_pos']%period:2d} key_pos={s['key_pos']:3d} "
                  f"cipher={s['c_val']:2d} key={k:2d} -> plain={GP_NAMES[p]:>3s}({p:2d})")

# ============================================================================
# SECTION 4: Per-page — find ALL consistent periods for each page
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 4: Per-page consistent period search (using P19-derived valid set)")
print("=" * 80)

# After checking P19 in Section 1, we know the valid plaintext values
# For now, let's use a broader set and see which periods work
# Use the actual P19 single-rune word plaintext values as the valid set

# Temporarily use ALL values (no constraint - just period consistency)
# The test: for a given period L, do all singles at the same slot (key_pos % L)
# have the same cipher value? (They should if key is the same and plaintext is the same)
# Actually no - different words can have different plaintexts at the same key slot.
# The constraint is: plaintext must be in valid_set, which is at most 2-5 values.
# So: for each group, the set of cipher values should map to valid_plains under SOME key k.
# I.e., for each c_val in the group, (c_val - k) % 29 must be in valid_plains (for SUB)
# or (k - c_val) % 29 must be in valid_plains (for BEAU)

def check_period_consistency(singles, period, mode, valid_plains):
    """Check if singles are consistent with a periodic key of given period.
    Returns (total_constrained_slots, consistent_slots, key_assignments)"""
    groups = defaultdict(list)
    for s in singles:
        groups[s['key_pos'] % period].append(s)
    
    total_constrained = 0
    consistent = 0
    key_assignments = {}
    
    for slot, g in groups.items():
        c_vals = set(gs['c_val'] for gs in g)
        
        # Find all key values k such that ALL c_vals map to valid_plains
        valid_keys = []
        for k in range(MOD):
            if mode == 'sub':
                plains = {(c - k) % MOD for c in c_vals}
            elif mode == 'beau':
                plains = {(k - c) % MOD for c in c_vals}
            if plains.issubset(valid_plains):
                valid_keys.append(k)
        
        if len(g) >= 2:
            total_constrained += 1
            if valid_keys:
                consistent += 1
                key_assignments[slot] = valid_keys
            
    return total_constrained, consistent, key_assignments

# First test on P19 with period=47 and valid_plains from Section 1
print("Testing P19 with period=47 (known correct):")
p19_plains_from_decrypt = set()
for s in p19_singles:
    p_val = p19_decrypted[s['rune_pos']]
    p19_plains_from_decrypt.add(p_val)
print(f"  P19 singles decrypt to: {sorted(p19_plains_from_decrypt)} = {[GP_NAMES[v] for v in sorted(p19_plains_from_decrypt)]}")

for valid_set_name, valid_set in [
    ("P19_actual", p19_plains_from_decrypt),
    ("I_A", {10, 24}),
    ("I_A_O", {10, 24, 3}),
    ("all_vowels", {1, 3, 10, 18, 22, 24}),  # U, O, I, E, OE, A
    ("any", set(range(29))),
]:
    tc, c, ka = check_period_consistency(p19_s, 47, 'beau', valid_set)
    print(f"  {valid_set_name:15s}: {c}/{tc} constrained slots consistent")

# Now test ALL unsolved pages with various valid sets
print("\n--- Testing unsolved pages ---")
sorted_pages = sorted(all_singles.items(), key=lambda x: len(x[1]), reverse=True)

for pn, singles in sorted_pages[:10]:
    if pn == 19:
        continue
    text = load_runes(pn)
    rune_count = sum(1 for ch in text if ch in GP_RUNE_TO_IDX)
    n_s = len(singles)
    
    for mode in ['sub', 'beau']:
        for valid_set_name, valid_set in [("I_A", {10, 24}), ("vowels", {1, 3, 10, 18, 22, 24})]:
            best_period = None
            best_score = -1
            best_tc = 0
            
            for period in range(2, min(rune_count, 300)):
                tc, c, ka = check_period_consistency(singles, period, mode, valid_set)
                if tc > 0 and c == tc and tc >= 2:
                    if tc > best_score:
                        best_score = tc
                        best_period = period
                        best_tc = tc
            
            if best_period and best_score >= 2:
                print(f"  P{pn} {mode}/{valid_set_name}: period={best_period} "
                      f"({best_score} slots ALL consistent)")
                # Show key assignments
                tc, c, ka = check_period_consistency(singles, best_period, mode, valid_set)
                for slot in sorted(ka.keys()):
                    keys = ka[slot]
                    if len(keys) <= 5:
                        print(f"    slot {slot:3d}: possible keys = {keys}")

# ============================================================================
# SECTION 5: Mathematical key function search (no sympy)
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 5: Mathematical key functions")
print("=" * 80)

# Generate Fibonacci numbers mod 29
fibs = [0, 1]
for _ in range(1000):
    fibs.append((fibs[-1] + fibs[-2]) % MOD)

def euler_totient(n):
    """Simple totient calculation."""
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

# For each page, test if a mathematical key function produces valid single-rune words
for pn, singles in sorted_pages[:10]:
    if pn == 19:
        continue
    text = load_runes(pn)
    n_s = len(singles)
    
    print(f"\n  Page {pn} ({n_s} singles):")
    
    key_functions = {
        "pos%29": lambda p: p % 29,
        "prime[p]%29": lambda p: primes_list[min(p, len(primes_list)-1)] % 29,
        "GP_prime[p%29]": lambda p: GP_PRIMES[p % 29] % 29,
        "fib[p]%29": lambda p: fibs[p] if p < len(fibs) else 0,
        "2^p%29": lambda p: pow(2, p, 29),
        "3^p%29": lambda p: pow(3, p, 29),
        "5^p%29": lambda p: pow(5, p, 29),
        "7^p%29": lambda p: pow(7, p, 29),
        "11^p%29": lambda p: pow(11, p, 29),
        "p^2%29": lambda p: (p*p) % 29,
        "p^3%29": lambda p: (p*p*p) % 29,
        "totient(p+1)%29": lambda p: euler_totient(p+1) % 29,
        "prime[p]*p%29": lambda p: (primes_list[min(p, len(primes_list)-1)] * p) % 29,
    }
    
    for mode in ['sub', 'beau']:
        for valid_set_name, valid_set in [("I_A", {10, 24}), ("vowels", {1, 3, 10, 18, 22, 24})]:
            expected = n_s * len(valid_set) / 29
            
            for kf_name, kf in key_functions.items():
                match = 0
                for s in singles:
                    k = kf(s['key_pos'])
                    if mode == 'sub':
                        p = (s['c_val'] - k) % MOD
                    elif mode == 'beau':
                        p = (k - s['c_val']) % MOD
                    if p in valid_set:
                        match += 1
                
                if match > expected * 2.5 and match >= 4:
                    print(f"    {mode}/{valid_set_name}/{kf_name}: {match}/{n_s} (expected={expected:.1f})")

# ============================================================================
# SECTION 6: Linear key search (k = a*pos + b)
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 6: Linear key k = a*pos + b mod 29")  
print("=" * 80)

for pn, singles in sorted_pages[:10]:
    if pn == 19:
        continue
    n_s = len(singles)
    
    for mode in ['sub', 'beau']:
        best_count = 0
        best_params = None
        
        for a in range(MOD):
            for b in range(MOD):
                match = 0
                for s in singles:
                    k = (a * s['key_pos'] + b) % MOD
                    if mode == 'sub':
                        p = (s['c_val'] - k) % MOD
                    elif mode == 'beau':
                        p = (k - s['c_val']) % MOD
                    if p in {10, 24}:  # I or A
                        match += 1
                if match > best_count:
                    best_count = match
                    best_params = (a, b)
        
        expected = n_s * 2 / 29
        if best_count > expected * 2:
            print(f"  P{pn} {mode}: k={best_params[0]}*p+{best_params[1]}: "
                  f"{best_count}/{n_s} match (expected={expected:.1f})")

# ============================================================================
# SECTION 7: Exponential key search (k = g^pos mod 29)
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 7: Exponential key k = g^pos * c mod 29")
print("=" * 80)

for pn, singles in sorted_pages[:8]:
    if pn == 19:
        continue
    n_s = len(singles)
    
    for mode in ['sub', 'beau']:
        best_count = 0
        best_params = None
        
        for g in range(2, MOD):
            for c in range(1, MOD):
                match = 0
                for s in singles:
                    k = (c * pow(g, s['key_pos'], MOD)) % MOD
                    if mode == 'sub':
                        p = (s['c_val'] - k) % MOD
                    elif mode == 'beau':
                        p = (k - s['c_val']) % MOD
                    if p in {10, 24}:
                        match += 1
                if match > best_count:
                    best_count = match
                    best_params = (g, c)
        
        expected = n_s * 2 / 29
        if best_count > expected * 2:
            print(f"  P{pn} {mode}: k={best_params[1]}*{best_params[0]}^p: "
                  f"{best_count}/{n_s} match (expected={expected:.1f})")

# ============================================================================
# SECTION 8: LFSR check — can key values be produced by a linear recurrence?
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 8: LFSR degree-2 and degree-3 check")
print("=" * 80)

# For LFSR of degree d over GF(29):
# k[n] = sum(c_i * k[n-i] for i=1..d) mod 29
# We need to find consecutive positions to check this.
# Since singles are sparse, we check pairs/triples of close positions.

# For each page, if we have 3+ consecutive key positions that are close,
# try to find LFSR coefficients.

def mod_inverse(a, m):
    """Extended Euclidean algorithm for modular inverse."""
    if gcd(a, m) != 1:
        return None
    g, x, _ = extended_gcd(a, m)
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x, y = extended_gcd(b % a, a)
    return g, y - (b // a) * x, x

print("Looking for consecutive key positions on same page...")

for pn, singles in sorted_pages[:10]:
    if pn == 19:
        continue
    
    # Sort by key_pos
    sorted_singles = sorted(singles, key=lambda s: s['key_pos'])
    
    # Find consecutive pairs (key_pos differ by 1)
    consec_pairs = []
    for i in range(len(sorted_singles) - 1):
        d = sorted_singles[i+1]['key_pos'] - sorted_singles[i]['key_pos']
        if d == 1:
            consec_pairs.append((sorted_singles[i], sorted_singles[i+1]))
    
    # Find consecutive triples
    consec_triples = []
    for i in range(len(sorted_singles) - 2):
        d1 = sorted_singles[i+1]['key_pos'] - sorted_singles[i]['key_pos']
        d2 = sorted_singles[i+2]['key_pos'] - sorted_singles[i+1]['key_pos']
        if d1 == 1 and d2 == 1:
            consec_triples.append((sorted_singles[i], sorted_singles[i+1], sorted_singles[i+2]))
    
    if consec_pairs:
        print(f"\n  P{pn}: {len(consec_pairs)} consecutive pairs, {len(consec_triples)} triples")
        for pair in consec_pairs:
            print(f"    Pair: key_pos={pair[0]['key_pos']},{pair[1]['key_pos']} "
                  f"c_vals={pair[0]['c_val']},{pair[1]['c_val']}")

# ============================================================================
# SECTION 9: Outguess data analysis
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 9: Outguess data — checking for additional keys/info")
print("=" * 80)

outguess_files = [f for f in os.listdir('.') if f.startswith('outguess_')]
for ogf in sorted(outguess_files):
    with open(ogf, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    print(f"\n  {ogf}: {len(content)} bytes")
    # Show first 200 chars
    preview = content[:200].replace('\n', ' ').replace('\r', '')
    print(f"    Preview: {preview[:150]}")
    
    # Check if it contains runes
    rune_count = sum(1 for ch in content if ch in GP_RUNE_TO_IDX)
    if rune_count > 0:
        print(f"    Contains {rune_count} runes!")
    
    # Check if it looks like a key or message
    if content.strip().isdigit() or all(c in '0123456789 ,\n\r' for c in content.strip()):
        print(f"    Looks like numerical data!")

# ============================================================================
# SECTION 10: P19 key analysis — what makes it work?
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 10: P19 key structure analysis")
print("=" * 80)

print(f"P19 key ({len(P19_KEY)} values): {P19_KEY}")
print(f"Key as GP names: {[GP_NAMES[k] for k in P19_KEY]}")

# Key value distribution
kcounts = Counter(P19_KEY)
print(f"Key value counts: {dict(sorted(kcounts.items()))}")
print(f"Unique values: {len(kcounts)}/29")
print(f"Missing values: {sorted(set(range(29)) - set(P19_KEY))}")
missing_names = [GP_NAMES[v] for v in sorted(set(range(29)) - set(P19_KEY))]
print(f"Missing as names: {missing_names}")

# Check for LFSR structure in the key itself
print("\nLFSR check on P19 key:")
for degree in range(2, 8):
    # Try all possible LFSR polynomials of given degree
    # k[n] = c1*k[n-1] + c2*k[n-2] + ... + cd*k[n-d] mod 29
    # Only need first degree+1 values to determine, then verify rest
    if degree > len(P19_KEY) // 2:
        break
    
    # Use first 'degree' values as initial state, solve for coefficients using next 'degree' values
    # This is a system of linear equations mod 29
    # For degree=2: k[2] = c1*k[1] + c2*k[0], k[3] = c1*k[2] + c2*k[1]
    found = False
    
    # Brute force for small degrees
    if degree == 2:
        for c1 in range(MOD):
            for c2 in range(MOD):
                valid = True
                for i in range(2, len(P19_KEY)):
                    predicted = (c1 * P19_KEY[i-1] + c2 * P19_KEY[i-2]) % MOD
                    if predicted != P19_KEY[i]:
                        valid = False
                        break
                if valid:
                    print(f"  Degree 2: k[n] = {c1}*k[n-1] + {c2}*k[n-2] mod 29 WORKS!")
                    found = True
    elif degree == 3:
        for c1 in range(MOD):
            for c2 in range(MOD):
                for c3 in range(MOD):
                    valid = True
                    for i in range(3, min(10, len(P19_KEY))):  # Quick check first 7
                        predicted = (c1*P19_KEY[i-1] + c2*P19_KEY[i-2] + c3*P19_KEY[i-3]) % MOD
                        if predicted != P19_KEY[i]:
                            valid = False
                            break
                    if valid:
                        # Full check
                        for i in range(3, len(P19_KEY)):
                            predicted = (c1*P19_KEY[i-1] + c2*P19_KEY[i-2] + c3*P19_KEY[i-3]) % MOD
                            if predicted != P19_KEY[i]:
                                valid = False
                                break
                        if valid:
                            print(f"  Degree 3: k[n] = {c1}*k[n-1] + {c2}*k[n-2] + {c3}*k[n-3] mod 29 WORKS!")
                            found = True
    
    if not found and degree <= 3:
        print(f"  Degree {degree}: No LFSR found")

# Differences
diffs = [(P19_KEY[i+1] - P19_KEY[i]) % MOD for i in range(len(P19_KEY)-1)]
print(f"\nKey differences mod 29: {diffs}")

# Check if key correlates with primes or Fibonacci
print("\nCorrelation with mathematical sequences:")
for name, seq_func in [
    ("prime[i]%29", lambda i: primes_list[i] % 29),
    ("fib[i]%29", lambda i: fibs[i]),
    ("2^i%29", lambda i: pow(2, i, 29)),
    ("3^i%29", lambda i: pow(3, i, 29)),
    ("i%29", lambda i: i % 29),
    ("i^2%29", lambda i: (i*i) % 29),
]:
    matches = sum(1 for i in range(len(P19_KEY)) if P19_KEY[i] == seq_func(i))
    print(f"  {name}: {matches}/{len(P19_KEY)} direct matches")
    # Also check shifted
    for shift in range(1, MOD):
        matches_s = sum(1 for i in range(len(P19_KEY)) if P19_KEY[i] == (seq_func(i) + shift) % MOD)
        if matches_s >= 5:
            print(f"    +{shift}: {matches_s}/{len(P19_KEY)} matches")

print("\n\nDONE")
