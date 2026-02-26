#!/usr/bin/env python3
"""
Fundamental Cryptanalysis v2 of Unsolved LP Pages

1. Periodic IoC analysis (find key length for polyalphabetic ciphers)
2. Kasiski examination (repeated n-gram distances)
3. Autocorrelation analysis
4. Hill cipher brute force (2x2 matrices)
5. P19 key as running key for P18 and P20
6. Self-inverse/differencing operations
"""

import os, sys, io, re, math
from collections import Counter, defaultdict
from itertools import product as iprod

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# CORRECT GP mapping
GP_RUNES = list("ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛂᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ")
GP_RUNE_TO_IDX = {r: i for i, r in enumerate(GP_RUNES)}
GP_RUNE_TO_IDX['\u16C4'] = 11
GP_LETTERS = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

def load_runes(page_num):
    rpath = f'LiberPrimus/pages/page_{page_num:02d}/runes.txt'
    if not os.path.exists(rpath): return None
    with open(rpath, 'r', encoding='utf-8') as f:
        text = f.read().strip()
    return [GP_RUNE_TO_IDX[ch] for ch in text if ch in GP_RUNE_TO_IDX]

def calc_ioc(vals):
    if len(vals) < 10: return 0
    freq = Counter(vals)
    n = len(vals)
    return sum(f*(f-1) for f in freq.values()) / (n*(n-1)) * 29 if n > 1 else 0

def idx_to_text(indices):
    return ''.join(GP_LETTERS[v] for v in indices)

def word_score(text):
    words = ['THE','AND','THAT','THIS','WITH','FROM','HAVE','WILL','YOUR','WHAT',
             'THERE','THEIR','BEEN','SOME','WERE','WHICH','WHEN','THEM','NOT','FOR',
             'BUT','ARE','ALL','CAN','YOU','ONE','HIS','HER','WAS','OUR']
    return sum(text.count(w) * len(w)**2 for w in words)

# ============================================================
# ANALYSIS 1: Periodic IoC for all unsolved pages
# ============================================================
print("=" * 80)
print("ANALYSIS 1: Periodic IoC (finding key length)")
print("=" * 80)

target_pages = list(range(18, 55))

for page in target_pages:
    cipher = load_runes(page)
    if cipher is None: continue
    n = len(cipher)
    
    results = []
    for period in range(1, min(100, n//3)):
        columns_ioc = []
        for col in range(period):
            column = cipher[col::period]
            if len(column) >= 5:
                columns_ioc.append(calc_ioc(column))
        if columns_ioc:
            avg_ioc = sum(columns_ioc) / len(columns_ioc)
            results.append((period, avg_ioc))
    
    results.sort(key=lambda x: x[1], reverse=True)
    top5 = results[:5]
    top_str = ', '.join([f'k={p}:{ioc:.2f}' for p, ioc in top5])
    # Flag if any period gives IoC > 1.15
    flag = " ***" if top5 and top5[0][1] > 1.15 else ""
    print(f"P{page:02d} ({n:4d}r): {top_str}{flag}")

# ============================================================
# ANALYSIS 2: Kasiski + Autocorrelation for key pages
# ============================================================
print("\n" + "=" * 80)
print("ANALYSIS 2: Kasiski + Autocorrelation")
print("=" * 80)

for page in [18, 19, 20, 21, 25, 32, 40, 44]:
    cipher = load_runes(page)
    if cipher is None: continue
    n = len(cipher)
    
    # Autocorrelation
    auto_peaks = []
    for lag in range(1, min(100, n//2)):
        matches = sum(1 for i in range(n - lag) if cipher[i] == cipher[i + lag])
        expected = (n - lag) / 29
        ratio = matches / expected if expected > 0 else 0
        if ratio > 1.15:
            auto_peaks.append((lag, ratio))
    
    auto_peaks.sort(key=lambda x: x[1], reverse=True)
    top_auto = auto_peaks[:5] if auto_peaks else []
    
    # Kasiski trigrams
    trigram_positions = defaultdict(list)
    for i in range(n - 2):
        tri = tuple(cipher[i:i+3])
        trigram_positions[tri].append(i)
    
    distances = []
    for tri, positions in trigram_positions.items():
        if len(positions) >= 2:
            for i in range(len(positions)):
                for j in range(i+1, len(positions)):
                    distances.append(positions[j] - positions[i])
    
    factor_counts = Counter()
    for d in distances:
        for f in range(2, min(d+1, 100)):
            if d % f == 0:
                factor_counts[f] += 1
    
    print(f"\nP{page:02d} ({n}r):")
    if top_auto:
        print(f"  Autocorrelation peaks: {top_auto[:5]}")
    else:
        print(f"  No autocorrelation peaks above 1.15")
    
    if factor_counts:
        top_factors = factor_counts.most_common(5)
        print(f"  Kasiski top factors: {top_factors}")

# ============================================================
# ANALYSIS 3: Hill Cipher (2x2 only on small pages)
# ============================================================
print("\n" + "=" * 80)
print("ANALYSIS 3: Hill Cipher 2x2")
print("=" * 80)

def mod_inverse(a, m):
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None

for page in [22, 49, 54]:  # Smallest pages
    cipher = load_runes(page)
    if cipher is None: continue
    n = len(cipher)
    print(f"\nP{page:02d} ({n}r) Hill 2x2 brute force...")
    
    best_score = 0
    best_result = None
    
    for a in range(29):
        for d in range(29):
            det_partial = (a*d) % 29
            for b in range(29):
                for c in range(29):
                    det = (det_partial - b*c) % 29
                    if det == 0: continue
                    di = mod_inverse(det, 29)
                    if di is None: continue
                    
                    # Compute inverse matrix
                    ia = (d * di) % 29
                    ib = ((-b % 29) * di) % 29
                    ic = ((-c % 29) * di) % 29
                    id_ = (a * di) % 29
                    
                    # Decrypt
                    plain = []
                    for i in range(0, n - 1, 2):
                        p0 = (ia * cipher[i] + ib * cipher[i+1]) % 29
                        p1 = (ic * cipher[i] + id_ * cipher[i+1]) % 29
                        plain.extend([p0, p1])
                    
                    ioc = calc_ioc(plain)
                    if ioc > 1.4:
                        text = idx_to_text(plain)
                        ws = word_score(text)
                        score = ioc + ws * 0.01
                        if score > best_score:
                            best_score = score
                            best_result = (a, b, c, d, ioc, ws, text[:80])
    
    if best_result:
        a, b, c, d, ioc, ws, text = best_result
        print(f"  Best: [[{a},{b}],[{c},{d}]] IoC={ioc:.2f} wscore={ws}")
        print(f"  Text: {text}")
    else:
        print(f"  No solution found")

# ============================================================
# ANALYSIS 4: Self-inverse operations
# ============================================================
print("\n" + "=" * 80)
print("ANALYSIS 4: Self-inverse / differencing operations")
print("=" * 80)

for page in target_pages:
    cipher = load_runes(page)
    if cipher is None: continue
    n = len(cipher)
    
    tests = {}
    
    # Differencing: d[i] = (c[i+1] - c[i]) % 29
    diffs = [(cipher[i+1] - cipher[i]) % 29 for i in range(n-1)]
    tests['diff'] = diffs
    
    # Second differencing
    diffs2 = [(diffs[i+1] - diffs[i]) % 29 for i in range(len(diffs)-1)]
    tests['diff2'] = diffs2
    
    # Cumulative sum
    cum = []
    acc = 0
    for v in cipher:
        acc = (acc + v) % 29
        cum.append(acc)
    tests['cumsum'] = cum
    
    # Mirror add
    mirror = [(cipher[i] + cipher[n-1-i]) % 29 for i in range(n)]
    tests['mirror_add'] = mirror
    
    # XOR-like (addition mod 29 of adjacent)
    adj_add = [(cipher[i] + cipher[i+1]) % 29 for i in range(n-1)]
    tests['adj_add'] = adj_add
    
    for name, vals in tests.items():
        ioc = calc_ioc(vals)
        if ioc > 1.3:
            text = idx_to_text(vals)
            ws = word_score(text)
            print(f"  P{page:02d} {name}: IoC={ioc:.2f}, wscore={ws}")
            if ws > 20:
                print(f"    Text: {text[:100]}")

# ============================================================
# ANALYSIS 5: Frequency comparison to solved pages
# ============================================================
print("\n" + "=" * 80)
print("ANALYSIS 5: Frequency distribution comparison")
print("=" * 80)

# For each unsolved page, check how uniform the frequency distribution is
for page in target_pages:
    cipher = load_runes(page)
    if cipher is None: continue
    n = len(cipher)
    
    freq = Counter(cipher)
    # Calculate chi-squared against uniform distribution
    expected = n / 29
    chi_sq = sum((freq.get(i, 0) - expected)**2 / expected for i in range(29))
    
    # Count how many runes appear
    present = len(freq)
    
    # Calculate max/min ratio
    if freq:
        max_f = max(freq.values())
        min_f = min(freq.values()) if len(freq) == 29 else 0
        ratio = max_f / min_f if min_f > 0 else float('inf')
    else:
        ratio = 0
    
    # Flag if distribution is very uniform (low chi-squared) or very skewed
    flag = ""
    if chi_sq < 15:  # Very uniform
        flag = " [VERY UNIFORM]"
    elif chi_sq > 60:  # Significantly non-uniform
        flag = " [NON-UNIFORM ***]"
    
    print(f"  P{page:02d} ({n:4d}r): chi²={chi_sq:6.1f}, present={present}/29, max/min={ratio:.1f}{flag}")

# ============================================================
# ANALYSIS 6: P19 key chain test
# ============================================================
print("\n" + "=" * 80)
print("ANALYSIS 6: Key chaining (P18 plaintext = P19 key?)")
print("=" * 80)

P19_KEY = [24, 15, 2, 24, 4, 21, 11, 10, 20, 16, 9, 19, 26, 11, 7, 5, 11, 6, 27, 8, 22, 25, 21, 16, 25, 0, 27, 9, 21, 7, 27, 15, 21, 9, 3, 16, 5, 22, 18, 4, 5, 18, 23, 21, 1, 10, 24]

# If P19's key = P18's plaintext, then P18 decrypts to the key text
# P18 cipher + P19_KEY (repeating) = P18 plaintext, and P18 plaintext should = P19 key
# This is circular: we need cipher + key = key (repeated)
# i.e., cipher[i] + key[i%47] = key[i%47] for all i, meaning cipher[i] = 0 for all i
# That's clearly not the case.

# BUT: maybe the key for P19 comes from P18's plaintext where P18 has a DIFFERENT key
# So: P18_plain = decrypt(P18_cipher, SOME_KEY)
# And: P19_KEY = P18_plain[0:47] repeating
# This means P18's plaintext starts with the P19 key text

# Let me check: can I find P18's key if P18's plaintext starts with P19's key?
p18_cipher = load_runes(18)
if p18_cipher:
    n18 = len(p18_cipher)
    print(f"P18: {n18} runes, P19 key: {len(P19_KEY)} values")
    
    # If P18 plain = P19_KEY (repeating), then:
    # For ADD: P18_cipher + P18_key = P19_KEY[i%47]
    # P18_key = (P19_KEY[i%47] - P18_cipher) % 29
    
    for mode in ['add', 'sub', 'beaufort']:
        if mode == 'add':
            p18_key = [(P19_KEY[i % 47] - p18_cipher[i]) % 29 for i in range(n18)]
        elif mode == 'sub':
            p18_key = [(p18_cipher[i] - P19_KEY[i % 47]) % 29 for i in range(n18)]
        else:
            p18_key = [(P19_KEY[i % 47] + p18_cipher[i]) % 29 for i in range(n18)]
        
        # Check if this key has any periodicity
        for period in range(1, min(50, n18//3)):
            matches = 0
            total = 0
            for i in range(period, n18):
                if p18_key[i] == p18_key[i % period]:
                    matches += 1
                total += 1
            ratio = matches / total if total > 0 else 0
            if ratio > 0.9:
                print(f"  P18 {mode}: key period={period}, match_ratio={ratio:.3f}")
                print(f"    Key (first {period}): {p18_key[:period]}")
                # Try decrypting with this periodic key
                test_key = p18_key[:period]
                if mode == 'add':
                    test_plain = [(p18_cipher[i] + test_key[i % period]) % 29 for i in range(n18)]
                elif mode == 'sub':
                    test_plain = [(p18_cipher[i] - test_key[i % period]) % 29 for i in range(n18)]
                else:
                    test_plain = [(test_key[i % period] - p18_cipher[i]) % 29 for i in range(n18)]
                text = idx_to_text(test_plain)
                ws = word_score(text)
                ioc = calc_ioc(test_plain)
                print(f"    Decrypted IoC={ioc:.2f}, wscore={ws}")
                if ws > 20:
                    print(f"    Text: {text[:100]}")

print("\n\nDONE.")
