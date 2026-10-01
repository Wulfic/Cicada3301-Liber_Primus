#!/usr/bin/env python3
"""
Deep Analysis of Verified Keys — Finding the Key Generation Pattern
====================================================================
The verified_keys.json contains hill-climbed 71/83-element keys for all pages.
These keys produce high IoC (correct letter frequencies).

Questions to answer:
1. Do the keys contain the P63 keywords embedded?
2. Is there a relationship between keys for different pages?
3. Do consecutive pages share key material (like P11-P12)?
4. Can we find the SOURCE that generated these keys?
5. After applying these keys, what's the remaining transformation?
"""

import json
import sys
import math
from pathlib import Path
from collections import Counter

BASE = Path(__file__).resolve().parent.parent
DATA_DIR = BASE / "data"
PAGES_DIR = BASE / "pages"

IDX_TO_LETTER = [
    'F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S',
    'T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA'
]

RUNE_TO_IDX = {
    'ᚠ': 0, 'ᚢ': 1, 'ᚦ': 2, 'ᚩ': 3, 'ᚱ': 4, 'ᚳ': 5, 'ᚷ': 6, 'ᚹ': 7,
    'ᚻ': 8, 'ᚾ': 9, 'ᛁ': 10, 'ᛄ': 11, 'ᛇ': 12, 'ᛈ': 13, 'ᛉ': 14, 'ᛋ': 15,
    'ᛏ': 16, 'ᛒ': 17, 'ᛖ': 18, 'ᛗ': 19, 'ᛚ': 20, 'ᛝ': 21, 'ᛟ': 22, 'ᛞ': 23,
    'ᚪ': 24, 'ᚫ': 25, 'ᚣ': 26, 'ᛡ': 27, 'ᛠ': 28,
}

PAGE_KEYWORDS = {
    21: ('CABAL',     'beaufort', [5, 24, 17, 24, 20]),
    22: ('DIVINITY',  'beaufort', [23, 10, 1, 10, 9, 10, 16, 26]),
    24: ('OBSCURA',   'beaufort', [3, 17, 15, 5, 1, 4, 24]),
    25: ('CABAL',     'beaufort', [5, 24, 17, 24, 20]),
    27: ('SHADOWS',   'add',      [15, 8, 24, 23, 3, 7, 15]),
    28: ('DEOR',      'sub',      [23, 18, 3, 4]),
    29: ('TOTIENT',   'beaufort', [16, 3, 16, 10, 18, 9, 16]),
    30: ('MOURNFUL',  'add',      [19, 3, 1, 4, 9, 0, 1, 20]),
}

def load_runes(page_num):
    rune_file = PAGES_DIR / f"page_{page_num:02d}" / "runes.txt"
    if not rune_file.exists():
        return None
    with open(rune_file, 'r', encoding='utf-8') as f:
        content = f.read()
    return [RUNE_TO_IDX[ch] for ch in content if ch in RUNE_TO_IDX]

def compute_ioc(indices):
    n = len(indices)
    if n < 2: return 0
    counts = Counter(indices)
    num = sum(c*(c-1) for c in counts.values())
    den = n*(n-1)
    return 29 * num / den if den > 0 else 0

def main():
    vk_path = DATA_DIR / "verified_keys.json"
    with open(vk_path, 'r') as f:
        vk = json.load(f)
    
    # ===== 1. Key length analysis =====
    print("=" * 80)
    print("1. KEY LENGTH DISTRIBUTION")
    print("=" * 80)
    len_71_pages = []
    len_83_pages = []
    other_pages = []
    for pg_str in sorted(vk.keys(), key=int):
        pg = int(pg_str)
        klen = len(vk[pg_str])
        if klen == 71:
            len_71_pages.append(pg)
        elif klen == 83:
            len_83_pages.append(pg)
        else:
            other_pages.append((pg, klen))
    
    print(f"Key length 71 ({len(len_71_pages)} pages): {len_71_pages}")
    print(f"Key length 83 ({len(len_83_pages)} pages): {len_83_pages}")
    if other_pages:
        print(f"Other lengths: {other_pages}")
    
    # ===== 2. Overlaps between consecutive pages =====
    print("\n" + "=" * 80)
    print("2. KEY OVERLAPS BETWEEN CONSECUTIVE PAGES")
    print("=" * 80)
    
    pages_sorted = sorted(vk.keys(), key=int)
    for i in range(len(pages_sorted) - 1):
        pg1 = pages_sorted[i]
        pg2 = pages_sorted[i+1]
        k1 = vk[pg1]
        k2 = vk[pg2]
        
        if len(k1) != len(k2):
            continue
        
        klen = len(k1)
        # Check for shifted overlap (like P11-P12)
        for shift in range(1, klen):
            # Does k1[shift:] == k2[:klen-shift]?
            overlap = k1[shift:]
            match = k2[:klen-shift]
            if overlap == match:
                print(f"P{int(pg1):02d}→P{int(pg2):02d}: EXACT OVERLAP at shift {shift} ({klen-shift} elements)")
                break
        else:
            # Check for partial overlaps (90%+ match)
            for shift in range(-klen+1, klen):
                if shift > 0:
                    seg1 = k1[shift:]
                    seg2 = k2[:klen-shift]
                elif shift < 0:
                    seg1 = k1[:klen+shift]
                    seg2 = k2[-shift:]
                else:
                    seg1 = k1
                    seg2 = k2
                
                matches = sum(1 for a, b in zip(seg1, seg2) if a == b)
                overlap_len = len(seg1)
                if overlap_len > 10 and matches / overlap_len > 0.85:
                    print(f"P{int(pg1):02d}→P{int(pg2):02d}: {matches}/{overlap_len} match at shift {shift} ({100*matches/overlap_len:.0f}%)")
                    break
    
    # ===== 3. Check for keyword embedding =====
    print("\n" + "=" * 80)
    print("3. KEYWORD EMBEDDING CHECK")
    print("=" * 80)
    
    for pg, (kw, mode, kw_idx) in PAGE_KEYWORDS.items():
        pg_str = str(pg)
        if pg_str not in vk:
            continue
        key = vk[pg_str]
        klen = len(key)
        kwlen = len(kw_idx)
        
        # Check if keyword repeats through the key
        # If key was generated from keyword, maybe key[i] relates to kw_idx[i % kwlen]
        
        # Method 1: Check (key[i] - kw_idx[i % kwlen]) % 29 pattern
        diffs = [(key[i] - kw_idx[i % kwlen]) % 29 for i in range(klen)]
        diff_counter = Counter(diffs)
        
        # Method 2: Check (kw_idx[i % kwlen] - key[i]) % 29 pattern
        diffs2 = [(kw_idx[i % kwlen] - key[i]) % 29 for i in range(klen)]
        diff_counter2 = Counter(diffs2)
        
        print(f"\nP{pg:02d} ({kw}/{mode}): keylen={klen}")
        print(f"  key - kw pattern: top diffs = {diff_counter.most_common(5)}")
        print(f"  kw - key pattern: top diffs = {diff_counter2.most_common(5)}")
        
        # Check if diffs form a pattern (like an LFSR or running key)
        diffs_str = ''.join(IDX_TO_LETTER[d] for d in diffs[:30])
        print(f"  key-kw residue (first 30): {diffs_str}")
    
    # ===== 4. Apply verified keys and analyze text =====
    print("\n" + "=" * 80)
    print("4. DECRYPTED TEXT ANALYSIS (Verified Keys)")
    print("=" * 80)
    
    for pg in range(21, 55):
        pg_str = str(pg)
        if pg_str not in vk:
            continue
        
        key = vk[pg_str]
        klen = len(key)
        cipher = load_runes(pg)
        if cipher is None:
            continue
        
        # Try SUB mode (most common)
        plain_sub = [(c - key[i % klen]) % 29 for i, c in enumerate(cipher)]
        ioc_sub = compute_ioc(plain_sub)
        
        # Also try ADD
        plain_add = [(c + key[i % klen]) % 29 for i, c in enumerate(cipher)]
        ioc_add = compute_ioc(plain_add)
        
        # Use best
        if ioc_sub >= ioc_add:
            plain = plain_sub
            ioc = ioc_sub
            mode = 'sub'
        else:
            plain = plain_add
            ioc = ioc_add
            mode = 'add'
        
        text = ''.join(IDX_TO_LETTER[p] for p in plain)
        
        # Word analysis: split on common English separators
        # Count how many common English words appear as substrings
        common_3 = ['THE', 'AND', 'FOR', 'NOT', 'ALL', 'BUT', 'HIS', 'HER', 'WAS', 'ONE',
                     'OUR', 'OUT', 'ARE', 'YOU', 'HAS', 'HAD', 'WHO', 'CAN']
        found = []
        for w in common_3:
            count = text.count(w)
            if count > 0:
                found.append(f"{w}×{count}")
        
        if ioc > 1.5 or pg <= 30:
            print(f"P{pg:02d}: keylen={klen}, mode={mode}, IoC={ioc:.4f}, len={len(cipher)}")
            print(f"  Found words: {', '.join(found[:15])}")
            print(f"  Text preview: {text[:120]}")
    
    # ===== 5. Inter-page key element differences =====
    print("\n" + "=" * 80)
    print("5. KEY DIFFERENCES BETWEEN PAGES WITH SAME LENGTH")
    print("=" * 80)
    
    # For pages 21-30, compare their key element differences
    for pg1 in range(21, 30):
        for pg2 in range(pg1+1, 31):
            pg1_s, pg2_s = str(pg1), str(pg2)
            if pg1_s not in vk or pg2_s not in vk:
                continue
            k1, k2 = vk[pg1_s], vk[pg2_s]
            if len(k1) != len(k2):
                continue
            
            # Difference
            diffs = [(k1[i] - k2[i]) % 29 for i in range(len(k1))]
            diff_counter = Counter(diffs)
            
            # Sum difference
            diff_sum = sum(diffs) % 29
            
            # Is the difference constant (simple shift)?
            if len(diff_counter) == 1:
                print(f"P{pg1:02d}-P{pg2:02d}: CONSTANT DIFF = {list(diff_counter.keys())[0]}")
            elif diff_counter.most_common(1)[0][1] > len(k1) * 0.5:
                top_val, top_count = diff_counter.most_common(1)[0]
                print(f"P{pg1:02d}-P{pg2:02d}: Dominant diff={top_val} ({top_count}/{len(k1)}), sum={diff_sum}")
    
    # ===== 6. Running key hypothesis: check if keys relate to known plaintexts =====
    print("\n" + "=" * 80)
    print("6. RUNNING KEY TEST: DO KEYS MATCH KNOWN PLAINTEXT SOURCES?")
    print("=" * 80)
    
    # Load Deor poem
    deor_path = DATA_DIR / "deor_poem.txt"
    deor_indices = []
    if deor_path.exists():
        with open(deor_path, 'r', encoding='utf-8', errors='ignore') as f:
            deor = f.read().upper()
        letter_to_idx = {}
        for i, l in enumerate(IDX_TO_LETTER):
            letter_to_idx[l] = i
        i = 0
        while i < len(deor):
            matched = False
            for length in [2, 1]:
                if i + length <= len(deor):
                    chunk = deor[i:i+length]
                    if chunk in letter_to_idx:
                        deor_indices.append(letter_to_idx[chunk])
                        i += length
                        matched = True
                        break
            if not matched:
                i += 1
    
    if deor_indices:
        print(f"Deor poem: {len(deor_indices)} GP indices loaded")
        
        # For each page's key, check if it matches any offset of Deor
        for pg in [21, 22, 24, 25, 27, 28, 29, 30]:
            pg_str = str(pg)
            if pg_str not in vk:
                continue
            key = vk[pg_str]
            klen = len(key)
            
            best_offset = -1
            best_match = 0
            
            for offset in range(len(deor_indices) - klen):
                segment = deor_indices[offset:offset+klen]
                matches = sum(1 for a, b in zip(key, segment) if a == b)
                if matches > best_match:
                    best_match = matches
                    best_offset = offset
            
            pct = 100 * best_match / klen if klen > 0 else 0
            print(f"P{pg:02d}: best Deor match = {best_match}/{klen} ({pct:.1f}%) at offset {best_offset}")
    
    # ===== 7. LFSR/autokey check =====
    print("\n" + "=" * 80)
    print("7. LFSR / AUTOKEY CHECK")
    print("=" * 80)
    
    # For each verified key, check if it follows a linear recurrence
    for pg in [21, 22, 28, 30]:
        pg_str = str(pg)
        if pg_str not in vk:
            continue
        key = vk[pg_str]
        klen = len(key)
        
        print(f"\nP{pg:02d} key (first 20): {key[:20]}")
        print(f"  Differences:  {[(key[i+1] - key[i]) % 29 for i in range(min(19, klen-1))]}")
        
        # Check for period in the key itself
        for period in range(2, klen//2):
            matches = sum(1 for i in range(klen - period) if key[i] == key[i+period])
            pct = matches / (klen - period)
            if pct > 0.5:
                print(f"  Period {period}: {pct:.2%} match")
                break

if __name__ == '__main__':
    main()
