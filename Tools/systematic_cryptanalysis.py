"""
COMPREHENSIVE PERIODIC IoC ANALYSIS + KASISKI EXAMINATION
For ALL unsolved Liber Primus pages.

This is the fundamental cryptanalysis that should be done FIRST:
1. Periodic IoC at periods 1-40 (detects Vigenère key lengths)
2. Kasiski examination (repeated n-gram spacing GCDs)
3. Monographic frequency analysis (detects simple substitution vs polyalphabetic)
4. Check P19 first 43 runes plaintext
"""
import os, sys, math
from collections import Counter
from itertools import combinations

os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

# GP Mapping
GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

def to_english(gp_values):
    return ''.join(LATIN[v] for v in gp_values)

def ioc(values, alpha=29):
    n = len(values)
    if n < 2: return 0
    counts = Counter(values)
    return sum(c*(c-1) for c in counts.values()) / (n*(n-1)) * alpha

def load_page(pg):
    for p in [f'LiberPrimus/pages/page_{pg:02d}/runes.txt', f'LiberPrimus/pages/page_{pg}/runes.txt']:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                raw = f.read()
                return [GP[c] for c in raw if c in GP]
    return None

def periodic_ioc(values, period, alpha=29):
    """Average IoC of subsequences taken at given period.
    High value at a specific period suggests that period as key length."""
    subsequences = [[] for _ in range(period)]
    for i, v in enumerate(values):
        subsequences[i % period].append(v)
    iocs = [ioc(sub, alpha) for sub in subsequences if len(sub) >= 2]
    return sum(iocs) / len(iocs) if iocs else 0

def kasiski(values, ngram_len=3, top=10):
    """Find repeated n-grams and compute GCDs of their spacings."""
    positions = {}
    for i in range(len(values) - ngram_len + 1):
        key = tuple(values[i:i+ngram_len])
        if key not in positions:
            positions[key] = []
        positions[key].append(i)
    
    # Get spacings for repeated n-grams
    spacings = []
    for key, pos_list in positions.items():
        if len(pos_list) >= 2:
            for i in range(len(pos_list)):
                for j in range(i+1, len(pos_list)):
                    spacings.append(pos_list[j] - pos_list[i])
    
    if not spacings:
        return []
    
    # Factor each spacing and count factor frequencies
    factor_counts = Counter()
    for s in spacings:
        for f in range(2, min(s+1, 41)):
            if s % f == 0:
                factor_counts[f] += 1
    
    return factor_counts.most_common(top)

def chi_squared_vs_flat(values, alpha=29):
    """Chi-squared statistic vs uniform distribution. 
    Higher = more structured (more deviation from random)."""
    n = len(values)
    if n == 0: return 0
    expected = n / alpha
    counts = Counter(values)
    chi2 = sum((counts.get(i, 0) - expected)**2 / expected for i in range(alpha))
    return chi2

# === P19 PLAINTEXT VERIFICATION ===
print("=" * 80)
print("P19 PLAINTEXT VERIFICATION")
print("=" * 80)
p19 = load_page(19)
if p19:
    print(f"P19: {len(p19)} runes")
    p19_key = [24, 15, 2, 24, 4, 21, 11, 10, 20, 16, 9, 19, 26, 11, 7, 5, 11, 6, 27, 8, 22, 25, 21, 16, 25, 0, 27, 9, 21, 7, 27, 15, 21, 9, 3, 16, 5, 22, 18, 4, 5, 18, 23]
    # ADD mode: plain = (cipher + key) % 29
    plain = [(p19[i] + p19_key[i]) % 29 for i in range(43)]
    print(f"P19 first 43 plaintext (ADD): {to_english(plain)}")
    # SUB mode: plain = (cipher - key) % 29
    plain_sub = [(p19[i] - p19_key[i]) % 29 for i in range(43)]
    print(f"P19 first 43 plaintext (SUB): {to_english(plain_sub)}")
    # BEAU mode: plain = (key - cipher) % 29
    plain_beau = [(p19_key[i] - p19[i]) % 29 for i in range(43)]
    print(f"P19 first 43 plaintext (BEAU): {to_english(plain_beau)}")

# === LOAD ALL PAGES ===
print("\n" + "=" * 80)
print("LOADING ALL UNSOLVED PAGES")
print("=" * 80)

# Known solved pages (exclude these)
solved = {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,55,56,57,58,59,60,61,62,63,64,67,73,74}
# Note: Some pages in 55-74 range are solved via known methods

pages = {}
for pg in range(17, 75):
    if pg in solved:
        continue
    data = load_page(pg)
    if data and len(data) > 0:
        pages[pg] = data
        
print(f"Loaded {len(pages)} unsolved pages")
for pg in sorted(pages):
    print(f"  P{pg:02d}: {len(pages[pg]):5d} runes  IoC={ioc(pages[pg]):.4f}  chi2={chi_squared_vs_flat(pages[pg]):.1f}")

# === PERIODIC IoC ANALYSIS ===
print("\n" + "=" * 80)
print("PERIODIC IoC ANALYSIS (periods 1-40)")
print("=" * 80)
print("Looking for periods where avg IoC is significantly above 1.0")
print("(IoC > 1.5 suggests correct Vigenère key length)")
print()

for pg in sorted(pages):
    vals = pages[pg]
    if len(vals) < 50:  # Skip tiny pages
        continue
    
    # Find best periods
    period_iocs = []
    for period in range(1, min(41, len(vals)//4)):
        pic = periodic_ioc(vals, period)
        period_iocs.append((period, pic))
    
    # Sort by IoC descending
    period_iocs.sort(key=lambda x: -x[1])
    best = period_iocs[:5]
    
    # Check if any period gives IoC > 1.3
    has_signal = any(pic > 1.3 for _, pic in best)
    
    if has_signal:
        marker = "*** SIGNAL ***"
    else:
        marker = ""
    
    print(f"P{pg:02d} ({len(vals):4d} runes): {marker}")
    for period, pic in best[:5]:
        bar = '█' * int(pic * 10)
        print(f"  period={period:2d}: IoC={pic:.4f} {bar}")
    print()

# === KASISKI EXAMINATION ===  
print("\n" + "=" * 80)
print("KASISKI EXAMINATION (repeated trigram analysis)")
print("=" * 80)

for pg in sorted(pages):
    vals = pages[pg]
    if len(vals) < 100:  # Need enough text
        continue
    
    kas = kasiski(vals, ngram_len=3, top=5)
    if kas:
        top_factor = kas[0]
        print(f"P{pg:02d}: Top factors: {kas[:5]}")

# === FREQUENCY ANALYSIS (flatness) ===
print("\n" + "=" * 80)
print("FREQUENCY DISTRIBUTION ANALYSIS")
print("=" * 80)
print("Flat distribution = polyalphabetic cipher")
print("Peaked distribution = monoalphabetic or transposition")
print()

for pg in sorted(pages):
    vals = pages[pg]
    if len(vals) < 50:
        continue
    
    counts = Counter(vals)
    # Compute max frequency and min frequency
    max_freq = max(counts.values()) / len(vals) * 100
    min_freq = min(counts.get(i, 0) for i in range(29)) / len(vals) * 100
    range_freq = max_freq - min_freq
    
    # Expected for flat: 1/29 = 3.45%
    # Expected for English-like: peaks at common letters
    
    chi2 = chi_squared_vs_flat(vals)
    chi2_norm = chi2 / len(vals) * 100  # Normalize by length
    
    print(f"P{pg:02d}: chi2_norm={chi2_norm:.2f}  max={max_freq:.1f}%  min={min_freq:.1f}%  range={range_freq:.1f}%  ", end="")
    
    if chi2_norm < 5:
        print("[VERY FLAT - polyalphabetic]")
    elif chi2_norm < 15:
        print("[MODERATELY FLAT]")
    else:
        print("[PEAKED - possible mono/transposition]")

# === SPECIAL CHECKS ===
print("\n" + "=" * 80)
print("SPECIAL PATTERN CHECKS")
print("=" * 80)

# 1. Check if any page is an anagram/transposition of known plaintext
# (Transposition preserves frequency distribution)
# Compare frequency profiles of unsolved pages to solved pages
print("\nCheck for Atbash (reversal) patterns:")
for pg in sorted(pages):
    vals = pages[pg]
    atbash = [(28 - v) % 29 for v in vals]
    at_ioc = ioc(atbash)
    # Atbash + various shifts
    for shift in range(29):
        shifted = [(28 - v + shift) % 29 for v in vals]
        pic = ioc(shifted)
        if pic > 1.5:
            print(f"  P{pg:02d}: Atbash+shift{shift}: IoC={pic:.4f}")

# 2. Check affine cipher (multiplicative + additive)
print("\nAffine cipher check (multiply then shift):")
for pg in sorted(pages):
    vals = pages[pg]
    if len(vals) < 100:
        continue
    for mult in range(1, 29):
        if math.gcd(mult, 29) != 1:
            continue
        for add in range(29):
            transformed = [(v * mult + add) % 29 for v in vals]
            pic = ioc(transformed)
            if pic > 1.5:
                print(f"  P{pg:02d}: mult={mult} add={add}: IoC={pic:.4f} | {to_english(transformed)[:50]}")

# 3. Check if any pages have significantly different IoC when F-runes (0) are removed
print("\nF-rune removal effect:")
for pg in sorted(pages):
    vals = pages[pg]
    no_f = [v for v in vals if v != 0]
    f_count = len(vals) - len(no_f)
    ioc_with_f = ioc(vals)
    ioc_no_f = ioc(no_f, alpha=28) if len(no_f) > 1 else 0  
    # IoC on 28-alphabet (excluding F) 
    ioc_no_f_29 = ioc(no_f, alpha=29) if len(no_f) > 1 else 0
    if abs(ioc_with_f - ioc_no_f_29) > 0.15 or f_count == 0:
        print(f"  P{pg:02d}: F-count={f_count}  with_F={ioc_with_f:.4f}  no_F(29)={ioc_no_f_29:.4f}  no_F(28)={ioc_no_f:.4f}")

# 4. Check bigram IoC (paired characters)
print("\nBigram analysis:")
for pg in sorted(pages):
    vals = pages[pg]
    if len(vals) < 100:
        continue
    bigrams = [vals[i]*29 + vals[i+1] for i in range(0, len(vals)-1, 2)]
    big_ioc = ioc(bigrams, alpha=29*29)
    if big_ioc > 1.2:
        print(f"  P{pg:02d}: Bigram IoC = {big_ioc:.4f}")

# 5. Check if doubling up (odd/even interleave split) reveals anything
print("\nOdd/Even position split IoC:")
for pg in sorted(pages):
    vals = pages[pg]
    if len(vals) < 100:
        continue
    even = [vals[i] for i in range(0, len(vals), 2)]
    odd = [vals[i] for i in range(1, len(vals), 2)]
    even_ioc = ioc(even)
    odd_ioc = ioc(odd)
    if even_ioc > 1.3 or odd_ioc > 1.3:
        print(f"  P{pg:02d}: even_IoC={even_ioc:.4f}  odd_IoC={odd_ioc:.4f}")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
