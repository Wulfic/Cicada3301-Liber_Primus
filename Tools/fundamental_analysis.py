"""
Fundamental Cryptanalysis of Unsolved Liber Primus Pages
- Kasiski test (repeated n-gram analysis for key period)
- Friedman test (per-column IoC for each possible period)
- Chi-squared against English GP distribution
- Autocorrelation analysis
- Bigram / trigram repeat analysis
"""

import os, sys, math
from collections import Counter

GP_RUNE_TO_INDEX = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C4':11,'\u16C7':12,'\u16C8':13,'\u16C9':14,
    '\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,'\u16D7':19,'\u16DA':20,'\u16DD':21,
    '\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,'\u16A3':26,'\u16E1':27,'\u16E0':28
}

LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

# English letter frequencies mapped to GP (approximate from solved pages)
# We'll compute this from solved pages dynamically

def load_page(page_num):
    """Load rune indices from a page."""
    paths = [
        f"LiberPrimus/pages/page_{page_num:02d}/runes.txt",
        f"LiberPrimus/pages/page_{page_num}/runes.txt",
    ]
    for p in paths:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                text = f.read()
            return [GP_RUNE_TO_INDEX[c] for c in text if c in GP_RUNE_TO_INDEX]
    return None

def ioc(data):
    """Normalized IoC (random=1.0, English≈1.73)"""
    if len(data) <= 1:
        return 0
    freq = Counter(data)
    n = len(data)
    return sum(f*(f-1) for f in freq.values()) / (n*(n-1)) * 29

def kasiski_test(data, min_gram=3, max_gram=6):
    """Find repeated n-grams and compute GCD of distances."""
    distances = []
    
    for gram_len in range(min_gram, max_gram + 1):
        positions = {}
        for i in range(len(data) - gram_len + 1):
            gram = tuple(data[i:i+gram_len])
            if gram not in positions:
                positions[gram] = []
            positions[gram].append(i)
        
        for gram, pos_list in positions.items():
            if len(pos_list) >= 2:
                for j in range(len(pos_list)):
                    for k in range(j+1, len(pos_list)):
                        d = pos_list[k] - pos_list[j]
                        if d > 0:
                            distances.append(d)
    
    return distances

def factorize(n):
    """Get all factors of n."""
    factors = set()
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            factors.add(i)
            factors.add(n // i)
    factors.add(n)
    return factors

def kasiski_key_lengths(distances, max_period=100):
    """From Kasiski distances, find most likely key lengths."""
    factor_counts = Counter()
    for d in distances:
        for f in factorize(d):
            if 2 <= f <= max_period:
                factor_counts[f] += 1
    return factor_counts.most_common(20)

def friedman_test(data, max_period=None):
    """For each period k, compute average per-column IoC."""
    n = len(data)
    if max_period is None:
        max_period = min(n // 3, 200)
    
    results = []
    for k in range(2, max_period + 1):
        columns = [[] for _ in range(k)]
        for i, val in enumerate(data):
            columns[i % k].append(val)
        
        # Average IoC across columns
        col_iocs = [ioc(col) for col in columns if len(col) > 1]
        if col_iocs:
            avg_ioc = sum(col_iocs) / len(col_iocs)
            results.append((k, avg_ioc))
    
    return results

def autocorrelation(data, max_lag=None):
    """Compute autocorrelation: count of matching positions at each lag."""
    n = len(data)
    if max_lag is None:
        max_lag = min(n // 2, 200)
    
    results = []
    expected = n / 29  # expected matches for random
    
    for lag in range(1, max_lag + 1):
        matches = sum(1 for i in range(n - lag) if data[i] == data[i + lag])
        total = n - lag
        ratio = matches / total if total > 0 else 0
        # Normalize: random = 1/29 ≈ 0.0345
        results.append((lag, matches, total, ratio))
    
    return results

def chi_squared_test(data, expected_freq=None):
    """Chi-squared test against uniform and expected English."""
    freq = Counter(data)
    n = len(data)
    
    # Against uniform
    expected_uniform = n / 29
    chi_sq_uniform = sum((freq.get(i, 0) - expected_uniform)**2 / expected_uniform for i in range(29))
    
    return chi_sq_uniform

def analyze_solved_pages():
    """Compute GP frequency distribution from solved pages."""
    solved = [3, 4, 5, 14, 15, 55, 56, 57, 59, 60, 61, 62, 63, 64, 67, 68, 73, 74]
    
    # For solved pages that use simple Caesar, load and decrypt
    # For now, approximate using known English GP frequencies
    # These are the expected GP index frequencies for English text
    # Based on standard English letter frequencies adapted to GP
    
    # We'll collect from solved pages' known plaintexts
    all_indices = []
    
    for pg in solved:
        data = load_page(pg)
        if data:
            # Pages with Caesar 0 (direct): 5, 63, 68
            if pg in [5, 63, 68]:
                all_indices.extend(data)
            # Pages with Caesar 2: 64
            elif pg == 64:
                all_indices.extend([(d - 2) % 29 for d in data])
    
    if not all_indices:
        return None
    
    freq = Counter(all_indices)
    n = len(all_indices)
    return {i: freq.get(i, 0) / n for i in range(29)}

def main():
    print("=" * 80)
    print("FUNDAMENTAL CRYPTANALYSIS OF UNSOLVED LIBER PRIMUS PAGES")
    print("=" * 80)
    
    # First, get English GP frequency from solved pages
    print("\n--- ENGLISH GP FREQUENCY FROM SOLVED PAGES ---")
    eng_freq = analyze_solved_pages()
    if eng_freq:
        total = sum(eng_freq.values())
        sorted_freq = sorted(eng_freq.items(), key=lambda x: -x[1])
        print(f"Top 10 GP indices by frequency (from solved pages):")
        for idx, fr in sorted_freq[:10]:
            print(f"  {LATIN[idx]:3s} (idx {idx:2d}): {fr:.4f}")
    
    # Analyze unsolved pages
    unsolved_pages = list(range(18, 55))  # 18-54
    
    print("\n" + "=" * 80)
    print("KASISKI + FRIEDMAN ANALYSIS")
    print("=" * 80)
    
    for pg_num in unsolved_pages:
        data = load_page(pg_num)
        if not data:
            continue
        
        n = len(data)
        raw_ioc = ioc(data)
        chi_sq = chi_squared_test(data)
        
        # Skip very small pages for meaningful analysis
        if n < 50:
            continue
        
        print(f"\n{'='*60}")
        print(f"PAGE {pg_num}: {n} runes, raw IoC={raw_ioc:.4f}, chi²={chi_sq:.1f}")
        print(f"{'='*60}")
        
        # --- KASISKI TEST ---
        distances = kasiski_test(data, min_gram=3, max_gram=5)
        if distances:
            key_lengths = kasiski_key_lengths(distances)
            if key_lengths:
                print(f"\n  KASISKI top periods (by factor frequency):")
                for period, count in key_lengths[:10]:
                    print(f"    Period {period:3d}: {count:4d} factor hits")
        else:
            print(f"\n  KASISKI: No repeated trigrams found")
        
        # --- FRIEDMAN TEST ---
        max_p = min(n // 3, 150)
        friedman = friedman_test(data, max_p)
        
        # Find periods with IoC significantly above 1.0
        threshold = 1.25  # Significantly above random
        high_ioc_periods = [(k, ioc_val) for k, ioc_val in friedman if ioc_val > threshold]
        
        if high_ioc_periods:
            print(f"\n  FRIEDMAN periods with avg column IoC > {threshold}:")
            for k, ioc_val in sorted(high_ioc_periods, key=lambda x: -x[1])[:15]:
                print(f"    Period {k:3d}: avg column IoC = {ioc_val:.4f}")
        else:
            # Show top 10 anyway
            top_friedman = sorted(friedman, key=lambda x: -x[1])[:10]
            print(f"\n  FRIEDMAN top 10 periods (none above {threshold}):")
            for k, ioc_val in top_friedman:
                print(f"    Period {k:3d}: avg column IoC = {ioc_val:.4f}")
        
        # --- AUTOCORRELATION ---
        max_lag = min(n // 2, 100)
        auto = autocorrelation(data, max_lag)
        expected_ratio = 1.0 / 29  # ≈ 0.0345
        
        high_auto = [(lag, matches, total, ratio) for lag, matches, total, ratio in auto 
                      if ratio > expected_ratio * 1.5]
        
        if high_auto:
            print(f"\n  AUTOCORRELATION peaks (ratio > {expected_ratio*1.5:.4f}):")
            for lag, matches, total, ratio in sorted(high_auto, key=lambda x: -x[3])[:10]:
                print(f"    Lag {lag:3d}: {matches}/{total} matches, ratio={ratio:.4f} (expected {expected_ratio:.4f})")
        else:
            top_auto = sorted(auto, key=lambda x: -x[3])[:5]
            print(f"\n  AUTOCORRELATION top 5 (none significantly above random):")
            for lag, matches, total, ratio in top_auto:
                print(f"    Lag {lag:3d}: {matches}/{total} matches, ratio={ratio:.4f}")
    
    # === CROSS-PAGE ANALYSIS ===
    print("\n" + "=" * 80)
    print("CROSS-PAGE CONCATENTATION FRIEDMAN TEST")
    print("=" * 80)
    
    # Concatenate ALL unsolved pages
    all_unsolved = []
    page_boundaries = []
    for pg_num in unsolved_pages:
        data = load_page(pg_num)
        if data:
            page_boundaries.append((pg_num, len(all_unsolved), len(all_unsolved) + len(data)))
            all_unsolved.extend(data)
    
    if all_unsolved:
        n = len(all_unsolved)
        print(f"\nAll unsolved concatenated: {n} runes")
        
        # Friedman on concatenated
        friedman_all = friedman_test(all_unsolved, min(n // 10, 500))
        high_all = [(k, v) for k, v in friedman_all if v > 1.15]
        
        if high_all:
            print(f"\n  FRIEDMAN on concatenated (IoC > 1.15):")
            for k, v in sorted(high_all, key=lambda x: -x[1])[:20]:
                print(f"    Period {k:3d}: avg column IoC = {v:.4f}")
        else:
            top_all = sorted(friedman_all, key=lambda x: -x[1])[:15]
            print(f"\n  FRIEDMAN top 15 (none above 1.15):")
            for k, v in top_all:
                print(f"    Period {k:3d}: avg column IoC = {v:.4f}")
    
    # === SPECIAL: Test if any page has non-uniform distribution at ALL ===
    print("\n" + "=" * 80)
    print("DISTRIBUTION UNIFORMITY TEST")
    print("=" * 80)
    
    # Chi-squared critical value for 28 df at 0.05 = 41.34
    chi_crit = 41.34
    
    for pg_num in unsolved_pages:
        data = load_page(pg_num)
        if not data or len(data) < 30:
            continue
        
        chi = chi_squared_test(data)
        raw = ioc(data)
        
        # Check for ANY deviation from uniform
        flag = "*** NON-UNIFORM ***" if chi > chi_crit else ""
        if chi > chi_crit or raw > 1.05:
            print(f"  Page {pg_num:2d}: n={len(data):4d}, IoC={raw:.4f}, chi²={chi:.1f} {flag}")
    
    print("\n  (Only showing pages with chi² > 41.34 or IoC > 1.05)")
    print(f"  chi² critical value (df=28, α=0.05) = {chi_crit}")

    # === SOLVED PAGE COMPARISON ===
    print("\n" + "=" * 80)
    print("SOLVED PAGE IoC FOR REFERENCE")
    print("=" * 80)
    
    solved_pages = [3, 4, 5, 14, 15, 55, 56, 57, 59, 60, 61, 63, 64, 67, 68, 73, 74]
    for pg in solved_pages:
        data = load_page(pg)
        if data:
            print(f"  Page {pg:2d}: n={len(data):4d}, raw IoC={ioc(data):.4f}")

    # === DIFFERENTIAL ANALYSIS: Compare consecutive pages ===
    print("\n" + "=" * 80)
    print("XOR / DIFFERENCE BETWEEN CONSECUTIVE PAGES")
    print("=" * 80)
    
    prev_data = None
    prev_pg = None
    for pg_num in unsolved_pages:
        data = load_page(pg_num)
        if not data:
            continue
        
        if prev_data is not None:
            # XOR (mod 29 difference) between consecutive pages
            min_len = min(len(prev_data), len(data))
            if min_len > 50:
                diff = [(data[i] - prev_data[i]) % 29 for i in range(min_len)]
                diff_ioc = ioc(diff)
                xor = [(data[i] + prev_data[i]) % 29 for i in range(min_len)]
                xor_ioc = ioc(xor)
                
                if diff_ioc > 1.1 or xor_ioc > 1.1:
                    print(f"  P{prev_pg} vs P{pg_num}: diff_IoC={diff_ioc:.4f}, sum_IoC={xor_ioc:.4f} {'*** SIGNAL ***' if max(diff_ioc, xor_ioc) > 1.3 else ''}")
        
        prev_data = data
        prev_pg = pg_num
    
    print("\n  (Only showing pairs where IoC > 1.1)")

    # === KEY STREAM ANALYSIS: Test if cipher - cipher gives structure ===
    print("\n" + "=" * 80)
    print("SAME-KEY-OFFSET TEST (pairs of pages at same presumed offset)")
    print("=" * 80)
    print("If two pages use the same key stream, their difference = plaintext1 - plaintext2")
    
    pages_data = {}
    for pg_num in unsolved_pages:
        data = load_page(pg_num)
        if data and len(data) > 50:
            pages_data[pg_num] = data
    
    # Test all pairs of similar-length pages
    pg_list = list(pages_data.keys())
    best_pairs = []
    
    for i in range(len(pg_list)):
        for j in range(i+1, len(pg_list)):
            p1, p2 = pg_list[i], pg_list[j]
            d1, d2 = pages_data[p1], pages_data[p2]
            min_len = min(len(d1), len(d2))
            if min_len < 50:
                continue
            
            diff = [(d1[k] - d2[k]) % 29 for k in range(min_len)]
            diff_ioc_val = ioc(diff)
            
            if diff_ioc_val > 1.2:
                best_pairs.append((p1, p2, diff_ioc_val, min_len))
    
    if best_pairs:
        best_pairs.sort(key=lambda x: -x[2])
        print(f"\n  Page pairs with diff IoC > 1.2:")
        for p1, p2, d_ioc, ml in best_pairs[:20]:
            print(f"    P{p1:2d} - P{p2:2d}: diff IoC = {d_ioc:.4f} (over {ml} runes)")
    else:
        print("\n  No page pair differences have IoC > 1.2")
        # Show best anyway
        all_pairs = []
        for i in range(len(pg_list)):
            for j in range(i+1, len(pg_list)):
                p1, p2 = pg_list[i], pg_list[j]
                d1, d2 = pages_data[p1], pages_data[p2]
                min_len = min(len(d1), len(d2))
                if min_len < 50:
                    continue
                diff = [(d1[k] - d2[k]) % 29 for k in range(min_len)]
                all_pairs.append((p1, p2, ioc(diff), min_len))
        
        all_pairs.sort(key=lambda x: -x[2])
        print(f"  Top 10 pairs by diff IoC:")
        for p1, p2, d_ioc, ml in all_pairs[:10]:
            print(f"    P{p1:2d} - P{p2:2d}: diff IoC = {d_ioc:.4f} (over {ml} runes)")

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()
