"""Comprehensive audit of ALL unsolved pages with FIXED GP mapping.
Measures: rune count, IoC, frequency distribution, bigram analysis."""

import os
from collections import Counter
import math

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

def load_page(pg):
    for p in [f'LiberPrimus/pages/page_{pg:02d}/runes.txt', f'LiberPrimus/pages/page_{pg}/runes.txt']:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                raw = f.read()
                runes = [GP[c] for c in raw if c in GP]
                words = []
                current = []
                for c in raw:
                    if c in GP:
                        current.append(GP[c])
                    elif current:
                        words.append(current)
                        current = []
                if current:
                    words.append(current)
                return runes, words, raw
    return None, None, None

def ioc(values):
    n = len(values)
    if n < 2:
        return 0
    counts = Counter(values)
    return sum(c * (c-1) for c in counts.values()) / (n * (n-1))

def friedman_key_length(values, max_k=60):
    """Estimate key length using Friedman/Kasiski method."""
    n = len(values)
    results = []
    for k in range(1, min(max_k+1, n)):
        total_ioc = 0
        count = 0
        for offset in range(k):
            stream = values[offset::k]
            if len(stream) > 1:
                total_ioc += ioc(stream)
                count += 1
        if count > 0:
            avg_ioc = total_ioc / count
            results.append((k, avg_ioc))
    return sorted(results, key=lambda x: -x[1])

def entropy(values):
    n = len(values)
    counts = Counter(values)
    return -sum((c/n) * math.log2(c/n) for c in counts.values())

# Known solved pages for IoC reference
print("="*100)
print("REFERENCE: IoC of known-solved pages")
print("="*100)
for pg in [0, 3, 5, 7, 10, 14, 55, 56, 57, 58, 59, 63, 64, 68, 73]:
    runes, words, raw = load_page(pg)
    if runes:
        print(f"  Page {pg:02d}: {len(runes):4d} runes, IoC*29={ioc(runes)*29:.3f}, entropy={entropy(runes):.3f}")

# Audit ALL pages 18-54
print()
print("="*100)
print("AUDIT: Pages 18-54 (unsolved or partially solved)")
print("="*100)
print(f"{'Page':>6} {'Runes':>6} {'Words':>6} {'IoC*29':>8} {'Entropy':>8} {'UniqueR':>8} {'Top3':>20} {'Classification':>20}")
print("-"*100)

page_data = {}
for pg in range(18, 55):
    runes, words, raw = load_page(pg)
    if runes is None or len(runes) == 0:
        continue
    
    ioc_val = ioc(runes) * 29
    ent = entropy(runes)
    unique = len(set(runes))
    counts = Counter(runes)
    top3 = counts.most_common(3)
    top3_str = ','.join(f"{LATIN[v]}:{c}" for v,c in top3)
    
    # Classify
    if ioc_val > 1.6:
        cls = "HIGH IoC"
    elif ioc_val > 1.2:
        cls = "MEDIUM IoC"
    else:
        cls = "LOW IoC (~random)"
    
    print(f"  {pg:4d} {len(runes):6d} {len(words):6d} {ioc_val:8.3f} {ent:8.3f} {unique:8d} {top3_str:>20} {cls:>20}")
    page_data[pg] = {'runes': runes, 'words': words, 'ioc': ioc_val, 'raw': raw}

# Friedman analysis on high-IoC pages
print()
print("="*100)
print("FRIEDMAN KEY LENGTH ESTIMATION (top 10 key lengths by sub-stream IoC)")
print("="*100)

high_ioc_pages = [pg for pg, d in page_data.items() if d['ioc'] > 1.4]
for pg in sorted(high_ioc_pages):
    runes = page_data[pg]['runes']
    results = friedman_key_length(runes, 50)
    top10 = results[:10]
    print(f"\n  Page {pg:02d} ({len(runes)} runes, IoC*29={page_data[pg]['ioc']:.3f}):")
    for k, avg_ioc in top10:
        marker = ""
        if avg_ioc * 29 > 1.8:
            marker = " ← PROMISING"
        print(f"    k={k:3d}: sub-IoC*29={avg_ioc*29:.3f}{marker}")

# Detailed frequency analysis for high-IoC pages
print()
print("="*100)
print("FREQUENCY ANALYSIS: High-IoC pages vs English GP distribution")
print("="*100)

# Known English GP frequency from solved pages (e.g., accumulate from pages 0,3,5,7,10)
ref_counts = Counter()
for pg in [0, 3, 5, 7, 10, 14, 55, 56, 57, 58, 59, 63, 64, 68, 73]:
    runes, _, _ = load_page(pg)
    if runes:
        ref_counts.update(runes)

ref_total = sum(ref_counts.values())
print(f"\nReference distribution ({ref_total} runes from solved pages):")
for i in range(29):
    bar = '#' * int(ref_counts[i] / ref_total * 200)
    print(f"  {LATIN[i]:3s} ({i:2d}): {ref_counts[i]/ref_total*100:5.1f}% {bar}")

# Compare each high-IoC page
for pg in sorted(high_ioc_pages):
    runes = page_data[pg]['runes']
    counts = Counter(runes)
    total = len(runes)
    
    # Chi-squared test against reference
    chi_sq = 0
    for v in range(29):
        obs = counts.get(v, 0)
        exp = ref_counts.get(v, 0) / ref_total * total
        if exp > 0:
            chi_sq += (obs - exp)**2 / exp
    
    print(f"\n  Page {pg:02d}: chi-sq={chi_sq:.1f} (vs reference distribution)")
    deviations = []
    for v in range(29):
        obs_pct = counts.get(v, 0) / total * 100
        exp_pct = ref_counts.get(v, 0) / ref_total * 100
        diff = abs(obs_pct - exp_pct)
        if diff > 2.0:
            deviations.append(f"{LATIN[v]}({obs_pct:.1f}% vs {exp_pct:.1f}%)")
    if deviations:
        print(f"    Notable deviations: {', '.join(deviations)}")
    else:
        print(f"    Frequencies closely match English!")

# === Caesar shift scan on the HIGH IoC pages ===
print()
print("="*100)
print("CAESAR SHIFT SCAN: High-IoC pages (simple shift 0-28)")
print("="*100)

for pg in sorted(high_ioc_pages):
    runes = page_data[pg]['runes']
    best_shift = -1
    best_chi = float('inf')
    
    for shift in range(29):
        shifted = [(r + shift) % 29 for r in runes]
        counts = Counter(shifted)
        total = len(shifted)
        chi = 0
        for v in range(29):
            obs = counts.get(v, 0)
            exp = ref_counts.get(v, 0) / ref_total * total
            if exp > 0:
                chi += (obs - exp)**2 / exp
        if chi < best_chi:
            best_chi = chi
            best_shift = shift
    
    # Decrypt with best shift and show first 50 runes
    shifted = [(r + best_shift) % 29 for r in runes]
    text = ''.join(LATIN[v] for v in shifted[:80])
    print(f"  Page {pg:02d}: best shift={best_shift}, chi-sq={best_chi:.1f}")
    print(f"    First 80: {text}")
