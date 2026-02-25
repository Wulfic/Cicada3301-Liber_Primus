#!/usr/bin/env python3
"""
Deep Analysis Script - Verify claimed solutions and find structural clues
=========================================================================
1. Verify the keyword decryptions for pages 21-30 actually produce high IoC
2. Look at the STRUCTURE of solved pages for cipher method clues
3. Analyze page lengths and mathematical properties
4. Cross-reference with community solvers
5. Check if pages 31-54 might actually be contiguous text split across pages
"""

import os
import sys
import math
from collections import Counter

RUNE_TO_INDEX = {
    'ᚠ': 0, 'ᚢ': 1, 'ᚦ': 2, 'ᚩ': 3, 'ᚱ': 4, 'ᚳ': 5, 'ᚷ': 6, 'ᚹ': 7,
    'ᚻ': 8, 'ᚾ': 9, 'ᛁ': 10, 'ᛂ': 11, 'ᛇ': 12, 'ᛈ': 13, 'ᛉ': 14,
    'ᛋ': 15, 'ᛏ': 16, 'ᛒ': 17, 'ᛖ': 18, 'ᛗ': 19, 'ᛚ': 20, 'ᛝ': 21,
    'ᛟ': 22, 'ᛞ': 23, 'ᚪ': 24, 'ᚫ': 25, 'ᚣ': 26, 'ᛡ': 27, 'ᛠ': 28,
    'ᛄ': 11
}

INDEX_TO_LATIN = {
    0: 'F', 1: 'U', 2: 'TH', 3: 'O', 4: 'R', 5: 'C', 6: 'G', 7: 'W',
    8: 'H', 9: 'N', 10: 'I', 11: 'J', 12: 'EO', 13: 'P', 14: 'X',
    15: 'S', 16: 'T', 17: 'B', 18: 'E', 19: 'M', 20: 'L', 21: 'NG',
    22: 'OE', 23: 'D', 24: 'A', 25: 'AE', 26: 'Y', 27: 'IA', 28: 'EA'
}

LATIN_TO_INDEX = {}
for idx, lat in INDEX_TO_LATIN.items():
    LATIN_TO_INDEX[lat] = idx


def word_to_indices(word):
    indices = []
    i = 0
    word = word.upper()
    while i < len(word):
        if i < len(word) - 1:
            two = word[i:i+2]
            if two in LATIN_TO_INDEX:
                indices.append(LATIN_TO_INDEX[two])
                i += 2
                continue
        if word[i] in LATIN_TO_INDEX:
            indices.append(LATIN_TO_INDEX[word[i]])
        i += 1
    return indices


def indices_to_text(indices):
    return ''.join(INDEX_TO_LATIN.get(i, '?') for i in indices)


def load_page_runes(page_num):
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rune_path = os.path.join(base, 'LiberPrimus', 'pages', f'page_{page_num:02d}', 'runes.txt')
    if not os.path.exists(rune_path):
        return [], ""
    raw = open(rune_path, 'r', encoding='utf-8').read()
    indices = [RUNE_TO_INDEX[c] for c in raw if c in RUNE_TO_INDEX]
    return indices, raw


def load_page_with_separators(page_num):
    """Load page preserving word/line boundaries."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rune_path = os.path.join(base, 'LiberPrimus', 'pages', f'page_{page_num:02d}', 'runes.txt')
    if not os.path.exists(rune_path):
        return [], [], ""
    raw = open(rune_path, 'r', encoding='utf-8').read()
    
    indices = []
    word_starts = [0]  # Track word boundaries by position in indices
    
    for c in raw:
        if c in RUNE_TO_INDEX:
            indices.append(RUNE_TO_INDEX[c])
        elif c in '-. /\n\r\t:&$%':
            if indices and len(indices) != word_starts[-1]:
                word_starts.append(len(indices))
        elif c == '\xe2\x80\xa2' or c == '•':
            if indices and len(indices) != word_starts[-1]:
                word_starts.append(len(indices))
    
    return indices, word_starts, raw


def calculate_ioc(indices):
    freq = [0] * 29
    for idx in indices:
        freq[idx] += 1
    n = len(indices)
    if n <= 1:
        return 0
    ioc = sum(f * (f - 1) for f in freq) / (n * (n - 1))
    return ioc * 29


def vigenere_decrypt(indices, key, mode='SUB'):
    result = []
    for i, c in enumerate(indices):
        k = key[i % len(key)]
        if mode == 'SUB':
            result.append((c - k) % 29)
        elif mode == 'ADD':
            result.append((c + k) % 29)
        elif mode == 'BEAUFORT':
            result.append((k - c) % 29)
    return result


def caesar_decrypt(indices, shift):
    return [(i - shift) % 29 for i in indices]


def compute_coset_ioc(indices, key_length):
    """Compute average IoC across cosets for a given key length."""
    if key_length < 1 or key_length >= len(indices):
        return 0
    
    cosets = [[] for _ in range(key_length)]
    for i, idx in enumerate(indices):
        cosets[i % key_length].append(idx)
    
    total_ioc = 0
    count = 0
    for coset in cosets:
        if len(coset) > 1:
            ioc = calculate_ioc(coset)
            total_ioc += ioc
            count += 1
    
    return total_ioc / count if count > 0 else 0


def find_key_length(indices, max_length=50):
    """Find best key length by IoC analysis."""
    results = []
    for kl in range(1, min(max_length, len(indices) // 2)):
        ioc = compute_coset_ioc(indices, kl)
        results.append((kl, ioc))
    
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def frequency_analysis(indices):
    """Detailed frequency analysis."""
    freq = Counter(indices)
    n = len(indices)
    
    # Expected English frequency in GP (approximation)
    # E(18), T(16), A(24), O(3), I(10), N(9), S(15), H(8), R(4) are most common
    english_order = [18, 16, 24, 3, 10, 9, 15, 8, 4, 23, 20, 1, 7, 19, 0, 26, 6, 17, 13, 5, 14, 11, 27, 25, 2, 28, 12, 22, 21]
    
    sorted_freq = freq.most_common()
    
    return sorted_freq


def sieve_primes(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = False
    return [i for i in range(2, limit + 1) if is_prime[i]]


def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True


def main():
    print("=" * 80)
    print("DEEP STRUCTURAL ANALYSIS - Liber Primus")
    print("=" * 80)
    
    # ---- 1. Page metadata ----
    print("\n\n1. PAGE METADATA (Length, IoC, Key Length Detection)")
    print("-" * 80)
    print(f"{'Page':>4} {'Len':>5} {'IoC':>7} {'Prime?':>6} {'Best KL':>8} {'KL IoC':>8}")
    
    page_data = {}
    for p in range(17, 55):
        indices, raw = load_page_runes(p)
        if not indices:
            continue
        ioc = calculate_ioc(indices)
        n = len(indices)
        prime = "YES" if is_prime(n) else ""
        
        # Find best key length
        kl_results = find_key_length(indices, 60)
        best_kl = kl_results[0] if kl_results else (0, 0)
        
        # Show top 3 key lengths
        top_kls = [(kl, ioc_val) for kl, ioc_val in kl_results[:5] if ioc_val > 1.2]
        
        page_data[p] = {
            'indices': indices,
            'raw': raw,
            'length': n,
            'ioc': ioc,
            'best_kl': best_kl,
            'top_kls': top_kls,
        }
        
        kl_str = f"{best_kl[0]:>3} ({best_kl[1]:.3f})"
        extra_kls = ", ".join([f"{kl}({v:.2f})" for kl, v in top_kls[1:4]])
        print(f"  {p:>2}  {n:>5}  {ioc:>6.4f}  {prime:>6}  {kl_str:>15}  [{extra_kls}]")
    
    # ---- 2. Verify keyword decryptions for pages 21-30 ----
    print("\n\n2. VERIFY KEYWORD DECRYPTIONS (Pages 21-30)")
    print("-" * 80)
    
    page_keys = {
        21: ('CABAL', 'BEAUFORT'),
        22: ('DIVINITY', 'BEAUFORT'),
        23: ('ENCRYPTION', 'ADD'),
        24: ('OBSCURA', 'BEAUFORT'),
        25: ('CABAL', 'BEAUFORT'),
        26: ('ENCRYPT', 'ADD'),
        27: ('SHADOWS', 'ADD'),
        28: ('DEOR', 'SUB'),
        29: ('TOTIENT', 'BEAUFORT'),
        30: ('MOURNFUL', 'ADD'),
    }
    
    for pg, (kw, mode) in page_keys.items():
        if pg not in page_data:
            continue
        indices = page_data[pg]['indices']
        n = len(indices)
        
        key = word_to_indices(kw)
        decrypted = vigenere_decrypt(indices, key, mode)
        dec_ioc = calculate_ioc(decrypted)
        
        text = indices_to_text(decrypted)
        
        # Check if key length matches
        kl_match = len(key) in [kl for kl, _ in page_data[pg]['top_kls']]
        
        # Also try all 29 Caesar shifts and see which gives best IoC
        best_caesar_ioc = 0
        best_caesar_shift = 0
        for shift in range(29):
            shifted = caesar_decrypt(indices, shift)
            s_ioc = calculate_ioc(shifted)
            if s_ioc > best_caesar_ioc:
                best_caesar_ioc = s_ioc
                best_caesar_shift = shift
        
        print(f"  Page {pg}: {kw:12s}/{mode:8s} key_len={len(key)} IoC={dec_ioc:.4f} "
              f"KL_match={'YES' if kl_match else 'NO':3s} "
              f"Best_Caesar={best_caesar_shift}({best_caesar_ioc:.4f})")
        print(f"    Key indices: {key}")
        print(f"    Text[0:80]: {text[:80]}")
        
        # Check coset IoC with this key length
        coset_ioc = compute_coset_ioc(indices, len(key))
        print(f"    Coset IoC at KL={len(key)}: {coset_ioc:.4f}")
    
    # ---- 3. Full key length scan for key pages ----
    print("\n\n3. KEY LENGTH DETECTION (Pages 21-30)")
    print("-" * 80)
    
    for pg in [21, 22, 23, 24, 25]:
        if pg not in page_data:
            continue
        indices = page_data[pg]['indices']
        n = len(indices)
        
        print(f"\n  Page {pg} (length {n}):")
        kl_results = find_key_length(indices, 80)
        for kl, ioc in kl_results[:15]:
            marker = " ***" if ioc > 1.4 else ""
            kl_prime = " [PRIME]" if is_prime(kl) else ""
            print(f"    KL={kl:3d} IoC={ioc:.4f}{kl_prime}{marker}")
    
    # ---- 4. Caesar IoC scan for pages 31-54 ----
    print("\n\n4. CAESAR SHIFT IoC SCAN (Pages 31-54)")
    print("-" * 80)
    
    for pg in range(31, 55):
        if pg not in page_data:
            continue
        indices = page_data[pg]['indices']
        n = len(indices)
        
        best_shift = 0
        best_ioc = 0
        all_iocs = []
        for shift in range(29):
            shifted = caesar_decrypt(indices, shift)
            ioc = calculate_ioc(shifted)
            all_iocs.append((shift, ioc))
            if ioc > best_ioc:
                best_ioc = ioc
                best_shift = shift
        
        # Also check key length for the best Caesar result
        best_shifted = caesar_decrypt(indices, best_shift)
        coset_results = find_key_length(best_shifted, 40)
        top_kl = coset_results[0] if coset_results else (0, 0)
        
        print(f"  P{pg}: len={n} best_caesar={best_shift} ioc={best_ioc:.4f} "
              f"after_caesar_KL={top_kl[0]}({top_kl[1]:.3f})")
    
    # ---- 5. Check if consecutive pages form contiguous text ----
    print("\n\n5. CROSS-PAGE ANALYSIS (Are pages contiguous?)")
    print("-" * 80)
    
    # Concatenate pages 31-54 and check IoC with different overall key lengths
    all_indices = []
    page_boundaries = []
    for pg in range(31, 55):
        if pg not in page_data:
            continue
        page_boundaries.append(len(all_indices))
        all_indices.extend(page_data[pg]['indices'])
    
    print(f"  Combined pages 31-54: {len(all_indices)} runes")
    combined_ioc = calculate_ioc(all_indices)
    print(f"  Combined IoC: {combined_ioc:.4f}")
    
    combined_kl = find_key_length(all_indices, 100)
    print(f"  Top key lengths for combined text:")
    for kl, ioc in combined_kl[:20]:
        marker = " ***" if ioc > 1.2 else ""
        kl_prime = " [PRIME]" if is_prime(kl) else ""
        print(f"    KL={kl:3d} IoC={ioc:.4f}{kl_prime}{marker}")
    
    # ---- 6. Try treating all pages 21-30 as one text with one key ----
    print("\n\n6. COMBINED PAGES 21-30 KEY LENGTH ANALYSIS")
    print("-" * 80)
    
    all_21_30 = []
    for pg in range(21, 31):
        if pg not in page_data:
            continue
        all_21_30.extend(page_data[pg]['indices'])
    
    print(f"  Combined pages 21-30: {len(all_21_30)} runes")
    combined_ioc_21 = calculate_ioc(all_21_30)
    print(f"  Combined IoC: {combined_ioc_21:.4f}")
    
    combined_kl_21 = find_key_length(all_21_30, 100)
    print(f"  Top key lengths:")
    for kl, ioc in combined_kl_21[:20]:
        marker = " ***" if ioc > 1.2 else ""
        kl_prime = " [PRIME]" if is_prime(kl) else ""
        print(f"    KL={kl:3d} IoC={ioc:.4f}{kl_prime}{marker}")
    
    # ---- 7. Look at solved page structure ----
    print("\n\n7. SOLVED PAGE STRUCTURE (for comparison)")
    print("-" * 80)
    
    solved_pages = [1, 3, 5, 9, 55, 59, 63, 64, 68]
    for pg in solved_pages:
        indices, raw = load_page_runes(pg)
        if not indices:
            continue
        n = len(indices)
        ioc = calculate_ioc(indices)
        kl_results = find_key_length(indices, 40)
        best_kl = kl_results[0] if kl_results else (0, 0)
        prime_len = "PRIME" if is_prime(n) else ""
        
        print(f"  Page {pg:2d}: len={n:5d} IoC={ioc:.4f} best_KL={best_kl[0]:3d}({best_kl[1]:.3f}) {prime_len}")
    
    
    # ---- 8. Check if keyword-found IoCs are actually better than random ----
    print("\n\n8. KEYWORD IoC VALIDATION (Is claimed high IoC real?)")
    print("-" * 80)
    
    for pg, (kw, mode) in page_keys.items():
        if pg not in page_data:
            continue
        indices = page_data[pg]['indices']
        n = len(indices)
        
        key = word_to_indices(kw)
        decrypted = vigenere_decrypt(indices, key, mode)
        dec_ioc = calculate_ioc(decrypted)
        
        # Compare with random keys of same length
        import random
        random.seed(42)
        random_iocs = []
        for _ in range(100):
            rand_key = [random.randint(0, 28) for _ in range(len(key))]
            rand_dec = vigenere_decrypt(indices, rand_key, mode)
            rand_ioc = calculate_ioc(rand_dec)
            random_iocs.append(rand_ioc)
        
        avg_rand_ioc = sum(random_iocs) / len(random_iocs)
        max_rand_ioc = max(random_iocs)
        
        significant = dec_ioc > max_rand_ioc
        
        print(f"  P{pg}: {kw:12s} IoC={dec_ioc:.4f} vs rand_avg={avg_rand_ioc:.4f} "
              f"rand_max={max_rand_ioc:.4f} {'SIGNIFICANT' if significant else 'NOT SIGNIFICANT'}")


if __name__ == '__main__':
    main()
