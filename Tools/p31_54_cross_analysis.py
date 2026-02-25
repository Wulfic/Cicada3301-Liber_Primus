#!/usr/bin/env python3
"""
Pages 31-54 Cross-page Analysis:
1. Find best Caesar shift for each page
2. Apply Caesar, then check for shared Vigenère key length
3. If found, use combined data to crack the Vigenère
"""
import sys, os, math
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

GP = {'\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
      '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
      '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
      '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
      '\u16A3':26,'\u16E1':27,'\u16E0':28}

IDX2LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

# Known English GP frequency (from solved pages)
# Approximate expected frequencies for GP English
ENGLISH_FREQ = [0.035, 0.025, 0.065, 0.055, 0.045, 0.025, 0.015, 0.025, 0.045, 0.050,
                0.060, 0.001, 0.005, 0.020, 0.002, 0.050, 0.065, 0.020, 0.090, 0.025,
                0.035, 0.020, 0.008, 0.030, 0.065, 0.005, 0.015, 0.005, 0.010]

def load_runes(page):
    path = f'LiberPrimus/pages/page_{page:02d}/runes.txt'
    if not os.path.exists(path): return []
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    return [GP[c] for c in text if c in GP]

def ioc(data):
    N = len(data)
    if N < 2: return 0
    freq = [0] * 29
    for d in data:
        freq[d] += 1
    return 29 * sum(f*(f-1) for f in freq) / (N*(N-1))

def chi_squared(data, expected_freq):
    """Chi-squared statistic against expected frequency."""
    N = len(data)
    if N == 0: return float('inf')
    freq = [0] * 29
    for d in data:
        freq[d] += 1
    chi2 = 0
    for i in range(29):
        expected = N * expected_freq[i]
        if expected > 0:
            chi2 += (freq[i] - expected) ** 2 / expected
    return chi2

def best_caesar_shift(data):
    """Find best Caesar shift by chi-squared test."""
    best_shift = 0
    best_chi2 = float('inf')
    for shift in range(29):
        shifted = [(d - shift) % 29 for d in data]
        chi2 = chi_squared(shifted, ENGLISH_FREQ)
        if chi2 < best_chi2:
            best_chi2 = chi2
            best_shift = shift
    return best_shift, best_chi2

def periodic_ioc(data, period):
    """Average IoC across columns when text is arranged in rows of 'period' width."""
    if period < 1 or period > len(data) // 2:
        return 0
    total_ioc = 0
    count = 0
    for col in range(period):
        column = [data[i] for i in range(col, len(data), period)]
        if len(column) > 1:
            total_ioc += ioc(column)
            count += 1
    return total_ioc / count if count > 0 else 0

# ===== Step 1: Find best Caesar shift for each page =====
print("=" * 70)
print("STEP 1: BEST CAESAR SHIFTS FOR PAGES 31-54")
print("=" * 70)

page_data = {}
caesar_shifts = {}

for page in range(31, 55):
    data = load_runes(page)
    if not data:
        continue
    shift, chi2 = best_caesar_shift(data)
    page_data[page] = data
    caesar_shifts[page] = shift
    shifted = [(d - shift) % 29 for d in data]
    raw_ioc = ioc(data)
    shifted_ioc = ioc(shifted)
    print(f"P{page:02d}: {len(data):4d} runes, best Caesar={shift:2d}, chi2={chi2:6.1f}, raw_IoC={raw_ioc:.3f}, shifted_IoC={shifted_ioc:.3f}")

# ===== Step 2: Apply Caesar and check for shared Vigenère key length =====
print(f"\n{'='*70}")
print("STEP 2: POST-CAESAR COMBINED ANALYSIS")
print(f"{'='*70}")

# Combine all post-Caesar data
combined = []
page_shifted = {}
for page in sorted(page_data.keys()):
    shift = caesar_shifts[page]
    shifted = [(d - shift) % 29 for d in page_data[page]]
    page_shifted[page] = shifted
    combined.extend(shifted)

print(f"\nTotal combined runes (post-Caesar): {len(combined)}")
print(f"Combined IoC: {ioc(combined):.4f}")

# Check periodic IoC for combined data
print("\nPeriodic IoC analysis on COMBINED post-Caesar data:")
print(f"{'Period':>6} {'Avg IoC':>8}")
for period in range(1, 51):
    pic = periodic_ioc(combined, period)
    marker = "  ***" if pic > 1.3 else "  **" if pic > 1.2 else "  *" if pic > 1.1 else ""
    if pic > 1.0 or period <= 30:
        print(f"{period:6d} {pic:8.4f}{marker}")

# Also check per-page periodic IoC
print(f"\n{'='*70}")
print("STEP 3: PER-PAGE PERIODIC IOC (looking for shared key length)")
print(f"{'='*70}")

for period in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 19, 23, 29]:
    page_pics = []
    for page in sorted(page_shifted.keys()):
        pic = periodic_ioc(page_shifted[page], period)
        page_pics.append(pic)
    avg = sum(page_pics) / len(page_pics)
    high_count = sum(1 for p in page_pics if p > 1.3)
    marker = "  ***" if avg > 1.3 else "  **" if avg > 1.2 else "  *" if avg > 1.1 else ""
    print(f"Period {period:3d}: avg IoC = {avg:.4f}, pages with IoC>1.3: {high_count}/{len(page_pics)}{marker}")

# ===== Step 3: Same analysis on PAGES 21-30 =====
print(f"\n{'='*70}")
print("STEP 4: PAGES 21-30 PERIODIC IOC (raw, no Caesar)")
print(f"{'='*70}")

for page in range(21, 31):
    if page == 25: continue  # corrupted
    data = load_runes(page)
    if not data:
        continue
    print(f"\nP{page:02d} ({len(data)} runes), raw IoC={ioc(data):.4f}:")
    for period in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 19, 23, 29]:
        pic = periodic_ioc(data, period)
        marker = "  ***" if pic > 1.3 else "  **" if pic > 1.2 else "  *" if pic > 1.1 else ""
        if pic > 1.05:
            print(f"  Period {period:3d}: {pic:.4f}{marker}")

# ===== Step 4: Kasiski analysis on combined post-Caesar =====
print(f"\n{'='*70}")
print("STEP 5: KASISKI ANALYSIS ON COMBINED POST-CAESAR DATA")
print(f"{'='*70}")

def kasiski(data, min_len=3, max_len=6):
    """Find repeated sequences and their spacings."""
    spacings = []
    for seq_len in range(min_len, max_len + 1):
        seen = {}
        for i in range(len(data) - seq_len + 1):
            seq = tuple(data[i:i+seq_len])
            if seq in seen:
                for prev in seen[seq]:
                    spacings.append(i - prev)
                seen[seq].append(i)
            else:
                seen[seq] = [i]
    return spacings

spacings = kasiski(combined)
if spacings:
    # Find GCD of spacings
    from math import gcd
    from functools import reduce
    
    # Factor each spacing
    factor_counts = Counter()
    for s in spacings:
        for f in range(2, min(s+1, 100)):
            if s % f == 0:
                factor_counts[f] += 1
    
    print(f"Total repeated trigram spacings: {len(spacings)}")
    print(f"\nTop factors:")
    for factor, count in factor_counts.most_common(20):
        print(f"  Factor {factor:3d}: {count:5d} occurrences")

# ===== Step 5: Try shared Vigenère key on combined post-Caesar =====
print(f"\n{'='*70}")
print("STEP 6: VIGENÈRE KEY RECOVERY ON COMBINED POST-CAESAR (top periods)")
print(f"{'='*70}")

# For the top key lengths, try to recover the key
for kl in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 29]:
    # For each position in the key, find the best shift
    key = []
    total_col_ioc = 0
    for pos in range(kl):
        column = [combined[i] for i in range(pos, len(combined), kl)]
        if len(column) < 5:
            key.append(0)
            continue
        
        best_shift = 0
        best_chi2 = float('inf')
        for shift in range(29):
            shifted_col = [(c - shift) % 29 for c in column]
            chi2 = chi_squared(shifted_col, ENGLISH_FREQ)
            if chi2 < best_chi2:
                best_chi2 = chi2
                best_shift = shift
        key.append(best_shift)
        total_col_ioc += ioc(column)
    
    avg_col_ioc = total_col_ioc / kl
    
    # Apply the recovered key
    decrypted = [(combined[i] - key[i % kl]) % 29 for i in range(len(combined))]
    dec_ioc = ioc(decrypted)
    dec_text = ''.join(IDX2LAT[d] for d in decrypted[:100])
    
    key_letters = ''.join(IDX2LAT[k] for k in key)
    
    if dec_ioc > 1.2:
        print(f"\nKL={kl:2d}: col_IoC={avg_col_ioc:.3f}, dec_IoC={dec_ioc:.3f} ***")
        print(f"  Key: {key} = {key_letters}")
        print(f"  Preview: {dec_text}")
    elif dec_ioc > 1.0:
        print(f"\nKL={kl:2d}: col_IoC={avg_col_ioc:.3f}, dec_IoC={dec_ioc:.3f}")
        print(f"  Key: {key} = {key_letters}")
