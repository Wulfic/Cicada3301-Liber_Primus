#!/usr/bin/env python3
"""
HILL CIPHER + NOVEL CIPHER ATTACK
===================================
Test ciphers that produce flat IoC (≈1.0):
1. Hill cipher (2x2 and 3x3 matrix mod 29)  
2. Affine cipher (P = (a*C + b) mod 29)
3. Polybius-based ciphers
4. Bifid cipher variants
5. Multiplicative cipher variants

Hill cipher is particularly promising because:
- It produces IoC ≈ 1.0 (matches our observation)
- It encrypts character PAIRS, so standard frequency analysis fails
- The key space for 2x2 is manageable (~406K invertible matrices)
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os, re
from collections import Counter
from math import gcd

GP_RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛂᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
GP_RUNE_TO_IDX = {r: i for i, r in enumerate(GP_RUNES)}
GP_NAMES = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]
MOD = 29
PAGES_DIR = r"LiberPrimus\pages"

def load_runes(page_num):
    folder = f"page_{page_num:02d}"
    path = os.path.join(PAGES_DIR, folder, "runes.txt")
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return f.read().strip()

def get_rune_stream(text):
    return [GP_RUNE_TO_IDX[ch] for ch in text if ch in GP_RUNE_TO_IDX]

def calc_ioc(values):
    if len(values) < 2:
        return 0
    counts = Counter(values)
    n = len(values)
    return sum(c*(c-1) for c in counts.values()) / (n*(n-1)) * MOD

def vals_to_text(vals):
    return ''.join(GP_NAMES[v] for v in vals)

def mod_inverse(a, m):
    """Modular inverse using extended Euclidean algorithm."""
    if gcd(a, m) != 1:
        return None
    g, x, _ = extended_gcd(a % m, m)
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x, y = extended_gcd(b % a, a)
    return g, y - (b // a) * x, x

def mat2_det(a, b, c, d, m):
    """Determinant of 2x2 matrix mod m."""
    return (a * d - b * c) % m

def mat2_inv(a, b, c, d, m):
    """Inverse of 2x2 matrix mod m. Returns (a',b',c',d') or None."""
    det = mat2_det(a, b, c, d, m)
    det_inv = mod_inverse(det, m)
    if det_inv is None:
        return None
    # Adjugate matrix
    return (d * det_inv % m, (-b % m) * det_inv % m,
            (-c % m) * det_inv % m, a * det_inv % m)

def hill2_decrypt(runes, inv_matrix):
    """Decrypt with 2x2 Hill cipher using inverse matrix."""
    a, b, c, d = inv_matrix
    result = []
    for i in range(0, len(runes) - 1, 2):
        x, y = runes[i], runes[i+1]
        p1 = (a * x + b * y) % MOD
        p2 = (c * x + d * y) % MOD
        result.extend([p1, p2])
    return result

# ============================================================================
# SECTION 1: Hill Cipher 2x2 — exhaustive search
# ============================================================================
print("=" * 80)
print("SECTION 1: Hill Cipher 2x2 exhaustive search")
print("=" * 80)

# Precompute all invertible 2x2 matrices and their inverses
print("Precomputing invertible matrices mod 29...")
invertible_matrices = []
for a in range(MOD):
    for b in range(MOD):
        for c in range(MOD):
            for d in range(MOD):
                inv = mat2_inv(a, b, c, d, MOD)
                if inv is not None:
                    invertible_matrices.append((a, b, c, d, inv))

print(f"Total invertible 2x2 matrices: {len(invertible_matrices)}")

# Test each matrix on select pages (top few unsolved pages)
test_pages = [17, 18, 20, 25, 32, 40, 44, 50]
best_per_page = {}

for pn in test_pages:
    text = load_runes(pn)
    if text is None:
        continue
    runes = get_rune_stream(text)
    n = len(runes)
    if n < 40:
        continue
    
    best_ioc = 0
    best_matrix = None
    
    for a, b, c, d, inv in invertible_matrices:
        plain = hill2_decrypt(runes, inv)
        ioc = calc_ioc(plain)
        if ioc > best_ioc:
            best_ioc = ioc
            best_matrix = (a, b, c, d)
    
    best_per_page[pn] = (best_ioc, best_matrix)
    print(f"  P{pn} ({n} runes): best IoC={best_ioc:.4f} matrix=[{best_matrix}]")
    
    if best_ioc > 1.3:
        inv = mat2_inv(*best_matrix, MOD)
        plain = hill2_decrypt(runes, inv)
        print(f"    Plaintext: {vals_to_text(plain[:80])}...")

# ============================================================================
# SECTION 2: Affine cipher exhaustive search
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 2: Affine cipher P = (a*C + b) mod 29")
print("=" * 80)

# Find values of a coprime to 29 (since 29 is prime, all 1-28 are coprime)
for pn in range(17, 55):
    text = load_runes(pn)
    if text is None:
        continue
    runes = get_rune_stream(text)
    
    best_ioc = 0
    best_ab = None
    
    for a in range(1, MOD):
        for b in range(MOD):
            plain = [(a * c + b) % MOD for c in runes]
            ioc = calc_ioc(plain)
            if ioc > best_ioc:
                best_ioc = ioc
                best_ab = (a, b)
    
    if best_ioc > 1.2:
        print(f"  P{pn}: best IoC={best_ioc:.4f} a={best_ab[0]} b={best_ab[1]}")

# ============================================================================
# SECTION 3: Periodic Affine (different a,b per position mod period)
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 3: Periodic affine (period 2-4)")
print("=" * 80)

for pn in [17, 18, 20, 25, 32, 44, 50]:
    text = load_runes(pn)
    if text is None:
        continue
    runes = get_rune_stream(text)
    n = len(runes)
    
    for period in [2, 3, 4]:
        best_ioc = 0
        best_params = None
        
        # For each position in the period, try all affine transformations
        # This is expensive for period > 2. Use greedy approach.
        
        if period == 2:
            for a1 in range(1, MOD):
                for b1 in range(MOD):
                    for a2 in range(1, MOD):
                        for b2 in range(MOD):
                            plain = []
                            for i, c in enumerate(runes):
                                if i % 2 == 0:
                                    plain.append((a1 * c + b1) % MOD)
                                else:
                                    plain.append((a2 * c + b2) % MOD)
                            ioc = calc_ioc(plain)
                            if ioc > best_ioc:
                                best_ioc = ioc
                                best_params = (a1, b1, a2, b2)
            
            if best_ioc > 1.25:
                print(f"  P{pn} period={period}: IoC={best_ioc:.4f} params={best_params}")
                plain = []
                for i, c in enumerate(runes):
                    if i % 2 == 0:
                        plain.append((best_params[0] * c + best_params[1]) % MOD)
                    else:
                        plain.append((best_params[2] * c + best_params[3]) % MOD)
                print(f"    {vals_to_text(plain[:80])}...")

# ============================================================================
# SECTION 4: Multiplication-only cipher 
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 4: Multiplicative cipher with periodic multiplier")
print("=" * 80)

for pn in range(17, 55):
    text = load_runes(pn)
    if text is None:
        continue
    runes = get_rune_stream(text)
    
    for period in range(1, 30):
        for mult in range(1, MOD):
            # P = mult^(pos mod period) * C mod 29
            plain = [(pow(mult, i % period, MOD) * c) % MOD for i, c in enumerate(runes)]
            ioc = calc_ioc(plain)
            if ioc > 1.3:
                print(f"  P{pn} mult={mult} period={period}: IoC={ioc:.4f}")
                print(f"    {vals_to_text(plain[:60])}...")

# ============================================================================
# SECTION 5: Pairwise sum/difference cipher
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 5: Pairwise operations (adjacent rune interactions)")
print("=" * 80)

for pn in range(17, 55):
    text = load_runes(pn)
    if text is None:
        continue
    runes = get_rune_stream(text)
    
    # Test: plaintext = C[i] + C[i+1] mod 29 (sliding window sum)
    for name, op in [
        ("sum", lambda a, b: (a + b) % MOD),
        ("diff", lambda a, b: (a - b) % MOD),
        ("xor", lambda a, b: (a ^ b) % MOD if (a ^ b) < MOD else (a + b) % MOD),
        ("prod", lambda a, b: (a * b) % MOD),
    ]:
        derived = [op(runes[i], runes[i+1]) for i in range(len(runes)-1)]
        ioc = calc_ioc(derived)
        if ioc > 1.2:
            print(f"  P{pn} {name}_adjacent: IoC={ioc:.4f}")

    # Test: plaintext at position i = C[i] + C[i+k] mod 29 for various k
    for k in [1, 2, 3, 5, 7, 11, 13, 29]:
        if k >= len(runes):
            break
        derived = [(runes[i] + runes[(i+k) % len(runes)]) % MOD for i in range(len(runes))]
        ioc = calc_ioc(derived)
        if ioc > 1.2:
            print(f"  P{pn} sum_skip_{k}: IoC={ioc:.4f}")

# ============================================================================
# SECTION 6: Polynomial cipher P = sum(a_i * C^i) mod 29
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 6: Power residue cipher P = C^k mod 29")
print("=" * 80)

for pn in range(17, 55):
    text = load_runes(pn)
    if text is None:
        continue
    runes = get_rune_stream(text)
    
    for k in range(2, 28):
        plain = [pow(c, k, MOD) if c != 0 else 0 for c in runes]
        ioc = calc_ioc(plain)
        if ioc > 1.2:
            print(f"  P{pn} C^{k}: IoC={ioc:.4f}")

# ============================================================================
# SECTION 7: Discrete log cipher
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 7: Discrete log / index cipher")
print("=" * 80)

# Precompute discrete logs for each generator
for g in [2, 3, 5, 7, 10, 11, 13, 14, 15]:
    # Check if g is a primitive root mod 29
    powers = set()
    for i in range(MOD):
        powers.add(pow(g, i, MOD))
    if len(powers) < MOD - 1:
        continue
    
    # Build log table
    log_table = {}
    for i in range(MOD - 1):
        val = pow(g, i, MOD)
        log_table[val] = i
    
    for pn in range(17, 55):
        text = load_runes(pn)
        if text is None:
            continue
        runes = get_rune_stream(text)
        
        # Replace each rune value with its discrete log (skip 0)
        plain = []
        for c in runes:
            if c == 0:
                plain.append(0)
            elif c in log_table:
                plain.append(log_table[c] % MOD)
        
        if len(plain) > 20:
            ioc = calc_ioc(plain)
            if ioc > 1.2:
                print(f"  P{pn} dlog_base_{g}: IoC={ioc:.4f}")
                print(f"    {vals_to_text(plain[:60])}...")

print("\n\nDONE")
