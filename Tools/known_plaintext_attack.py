"""
Known Plaintext Attack on Liber Primus Unsolved Pages

KEY INSIGHT: Word boundaries (dots/separators) are NOT encrypted.
Single-rune words MUST decrypt to either "I" (GP index 10) or "A" (GP index 24).
This gives us known plaintext at specific positions in the keystream.

For a stream cipher: plaintext = (ciphertext - key) mod 29
So: key[pos] = (ciphertext[pos] - plaintext[pos]) mod 29

If single-rune word at position P has cipher value C:
   If plaintext = "I" (10): key[P] = (C - 10) % 29
   If plaintext = "A" (24): key[P] = (C - 24) % 29

We recover key values at those positions, then check if they match ANY known sequence.
"""

import os
import sys
import math
from collections import Counter
from itertools import product

# Gematria Primus mapping
GP_RUNE_TO_INDEX = {
    '\u16A0': 0,  # F
    '\u16A2': 1,  # U
    '\u16A6': 2,  # TH
    '\u16A9': 3,  # O
    '\u16B1': 4,  # R
    '\u16B3': 5,  # C/K
    '\u16B7': 6,  # G
    '\u16B9': 7,  # W
    '\u16BB': 8,  # H
    '\u16BE': 9,  # N
    '\u16C1': 10, # I
    '\u16C2': 11, # J
    '\u16C7': 12, # EO
    '\u16C8': 13, # P
    '\u16C9': 14, # X
    '\u16CB': 15, # S
    '\u16CF': 16, # T
    '\u16D2': 17, # B
    '\u16D6': 18, # E
    '\u16D7': 19, # M
    '\u16DA': 20, # L
    '\u16DD': 21, # NG
    '\u16DF': 22, # OE
    '\u16DE': 23, # D
    '\u16AA': 24, # A
    '\u16AB': 25, # AE
    '\u16A3': 26, # Y
    '\u16E1': 27, # IA
    '\u16E0': 28, # EA
}

GP_INDEX_TO_LATIN = {
    0: 'F', 1: 'U', 2: 'TH', 3: 'O', 4: 'R', 5: 'C', 6: 'G', 7: 'W',
    8: 'H', 9: 'N', 10: 'I', 11: 'J', 12: 'EO', 13: 'P', 14: 'X',
    15: 'S', 16: 'T', 17: 'B', 18: 'E', 19: 'M', 20: 'L', 21: 'NG',
    22: 'OE', 23: 'D', 24: 'A', 25: 'AE', 26: 'Y', 27: 'IA', 28: 'EA'
}

GP_INDEX_TO_PRIME = {
    0: 2, 1: 3, 2: 5, 3: 7, 4: 11, 5: 13, 6: 17, 7: 19, 8: 23, 9: 29,
    10: 31, 11: 37, 12: 41, 13: 43, 14: 47, 15: 53, 16: 59, 17: 61,
    18: 67, 19: 71, 20: 73, 21: 79, 22: 83, 23: 89, 24: 97, 25: 101,
    26: 103, 27: 107, 28: 109
}

def sieve_primes(n):
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n + 1, i):
                sieve[j] = False
    return [i for i in range(len(sieve)) if sieve[i]]

PRIMES = sieve_primes(500000)

def euler_totient(n):
    if n <= 0:
        return 0
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

# Pre-compute totient stream
print("Pre-computing totient stream...")
TOT_STREAM = [euler_totient(PRIMES[i]) % 29 for i in range(min(50000, len(PRIMES)))]
print(f"Totient stream: {len(TOT_STREAM)} values computed")

def load_page_runes(page_num):
    """Load runes from a page file, return list of rune indices and word structure."""
    page_dir = f"c:\\Users\\tyler\\Repos\\Cicada3301\\LiberPrimus\\pages\\page_{page_num:02d}"
    rune_file = os.path.join(page_dir, "runes.txt")
    if not os.path.exists(rune_file):
        return None, None
    
    with open(rune_file, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    all_runes = []
    words = []
    pos = 0
    current_word = []
    word_start = 0
    
    for char in content:
        if char in GP_RUNE_TO_INDEX:
            idx = GP_RUNE_TO_INDEX[char]
            all_runes.append(idx)
            if not current_word:
                word_start = pos
            current_word.append(idx)
            pos += 1
        elif char in ('\u2022', '.', '\n', ' ', '-', '/', '%'):
            if current_word:
                words.append((word_start, len(current_word), list(current_word)))
                current_word = []
        elif char == "'":
            pass  # apostrophe within word
        elif char not in ('\r', '\t', '\ufeff'):
            # Any other separator
            if current_word:
                words.append((word_start, len(current_word), list(current_word)))
                current_word = []
    
    if current_word:
        words.append((word_start, len(current_word), list(current_word)))
    
    return all_runes, words

# Two-rune common English words in GP
TWO_RUNE_WORDS = {
    (2, 18): "THE", (10, 9): "IN", (10, 16): "IT", (10, 15): "IS",
    (3, 9): "ON", (3, 4): "OR", (3, 0): "OF", (24, 16): "AT",
    (24, 15): "AS", (24, 9): "AN", (17, 18): "BE", (17, 26): "BY",
    (23, 3): "DO", (6, 3): "GO", (8, 18): "HE", (10, 0): "IF",
    (19, 18): "ME", (19, 26): "MY", (9, 3): "NO", (15, 3): "SO",
    (16, 3): "TO", (1, 13): "UP", (1, 15): "US", (7, 18): "WE",
    (24, 19): "AM",
}

def check_totient_match(key_positions_and_values, max_offset=40000, stream=None):
    if stream is None:
        stream = TOT_STREAM
    if not key_positions_and_values:
        return []
    
    max_pos = max(p for p, v in key_positions_and_values)
    best = []
    
    for offset in range(min(max_offset, len(stream) - max_pos)):
        matches = 0
        for pos, val in key_positions_and_values:
            if offset + pos < len(stream) and stream[offset + pos] == val:
                matches += 1
        if matches >= max(3, len(key_positions_and_values) * 0.4):
            best.append((offset, matches, len(key_positions_and_values)))
    
    best.sort(key=lambda x: -x[1])
    return best[:20]

def check_fskip_totient(all_runes, key_positions_and_values, max_offset=40000):
    if not key_positions_and_values:
        return []
    
    # Build F-skip mapping
    fskip_map = {}
    key_idx = 0
    for i, rune_val in enumerate(all_runes):
        fskip_map[i] = key_idx
        if rune_val != 0:
            key_idx += 1
    
    remapped = [(fskip_map.get(pos, pos), val) for pos, val in key_positions_and_values]
    return check_totient_match(remapped, max_offset)

def check_periodic(key_positions_and_values, max_period=200):
    if len(key_positions_and_values) < 3:
        return []
    
    results = []
    for period in range(1, min(max_period + 1, max(p for p, v in key_positions_and_values) + 1)):
        groups = {}
        for pos, val in key_positions_and_values:
            g = pos % period
            if g not in groups:
                groups[g] = []
            groups[g].append(val)
        
        consistent = sum(Counter(vals).most_common(1)[0][1] if len(vals) > 1 else 1 
                        for vals in groups.values())
        total = len(key_positions_and_values)
        
        if total > 0 and consistent >= total * 0.8:
            results.append((period, consistent, total))
    
    results.sort(key=lambda x: (-x[1]/x[2], x[0]))
    return results[:20]

def check_linear(key_positions_and_values):
    if len(key_positions_and_values) < 3:
        return []
    
    results = []
    for a in range(29):
        for b in range(29):
            matches = sum(1 for pos, val in key_positions_and_values 
                         if (a * pos + b) % 29 == val)
            if matches >= max(3, len(key_positions_and_values) * 0.6):
                results.append((a, b, matches))
    
    results.sort(key=lambda x: -x[2])
    return results[:10]

def main():
    print("=" * 80)
    print("KNOWN PLAINTEXT ATTACK ON LIBER PRIMUS")
    print("=" * 80)
    
    unsolved_pages = list(range(18, 55))
    
    all_page_data = {}
    
    # Phase 1: Survey all pages
    print("\n--- PHASE 1: SURVEY ALL PAGES FOR SINGLE-RUNE WORDS ---\n")
    
    for page_num in sorted(unsolved_pages):
        runes, words = load_page_runes(page_num)
        if runes is None or len(runes) == 0:
            continue
        
        singles = []
        two_rune = []
        for start, length, rune_indices in words:
            if length == 1:
                c = rune_indices[0]
                singles.append({
                    'pos': start, 'cipher': c,
                    'key_sub_I': (c - 10) % 29, 'key_sub_A': (c - 24) % 29,
                    'key_beau_I': (10 + c) % 29, 'key_beau_A': (24 + c) % 29,
                })
            elif length == 2:
                two_rune.append({'pos': start, 'cipher': rune_indices})
        
        if singles:
            all_page_data[page_num] = {
                'runes': runes, 'words': words, 
                'singles': singles, 'two_rune': two_rune,
                'total_runes': len(runes), 'total_words': len(words)
            }
            
            rune_chars = {v: k for k, v in GP_RUNE_TO_INDEX.items()}
            print(f"Page {page_num:2d}: {len(runes):4d} runes, {len(words):3d} words, "
                  f"{len(singles):2d} single-rune, {len(two_rune):3d} two-rune")
            for sw in singles:
                rc = rune_chars[sw['cipher']]
                print(f"    Pos {sw['pos']:4d}: {rc}({sw['cipher']:2d}) | "
                      f"Vig: I->{sw['key_sub_I']:2d} A->{sw['key_sub_A']:2d} | "
                      f"Beau: I->{sw['key_beau_I']:2d} A->{sw['key_beau_A']:2d}")
    
    if not all_page_data:
        print("No pages with single-rune words found!")
        return
    
    # Phase 2: Check totient stream for each page
    print("\n" + "=" * 80)
    print("PHASE 2: TOTIENT STREAM MATCHING (Vigenere & Beaufort)")
    print("=" * 80)
    
    for page_num in sorted(all_page_data.keys()):
        data = all_page_data[page_num]
        singles = data['singles']
        runes = data['runes']
        n = len(singles)
        
        if n < 2:
            continue
        
        print(f"\n{'='*60}")
        print(f"PAGE {page_num}: {n} single-rune constraints, {data['total_runes']} total runes")
        
        # For each cipher mode x plaintext combo, check totient
        modes = [
            ("Vig", lambda c, p: (c - p) % 29),     # key = cipher - plain
            ("Beau", lambda c, p: (p + c) % 29),     # key = plain + cipher  
            ("Sub", lambda c, p: (p - c) % 29),      # key = plain - cipher
        ]
        
        best_overall = None
        
        if n <= 15:
            # Try all 2^n combos
            for mode_name, key_func in modes:
                for combo in range(2**n):
                    key_vals = []
                    for i, sw in enumerate(singles):
                        pt = 24 if (combo >> i) & 1 else 10
                        key_vals.append((sw['pos'], key_func(sw['cipher'], pt)))
                    
                    # Check regular totient
                    matches = check_totient_match(key_vals, max_offset=40000)
                    if matches and matches[0][1] >= max(3, n * 0.6):
                        label = "".join("A" if (combo >> i) & 1 else "I" for i in range(n))
                        if best_overall is None or matches[0][1] > best_overall[2]:
                            best_overall = (mode_name, label, matches[0][1], matches[0][2], matches[0][0])
                        if matches[0][1] >= n * 0.8:
                            print(f"  [{mode_name}] {label}: totient offset {matches[0][0]}: "
                                  f"{matches[0][1]}/{matches[0][2]} matches!")
                    
                    # Check F-skip totient
                    fskip = check_fskip_totient(runes, key_vals, max_offset=40000)
                    if fskip and fskip[0][1] >= max(3, n * 0.6):
                        label = "".join("A" if (combo >> i) & 1 else "I" for i in range(n))
                        if best_overall is None or fskip[0][1] > best_overall[2]:
                            best_overall = (f"{mode_name}+Fskip", label, fskip[0][1], fskip[0][2], fskip[0][0])
                        if fskip[0][1] >= n * 0.8:
                            print(f"  [{mode_name}+Fskip] {label}: offset {fskip[0][0]}: "
                                  f"{fskip[0][1]}/{fskip[0][2]} matches!")
        else:
            # Too many combos, try all-I and all-A
            for mode_name, key_func in modes:
                for pt_val, pt_name in [(10, "all-I"), (24, "all-A")]:
                    key_vals = [(sw['pos'], key_func(sw['cipher'], pt_val)) for sw in singles]
                    
                    matches = check_totient_match(key_vals, max_offset=40000)
                    if matches and matches[0][1] >= max(3, n * 0.3):
                        print(f"  [{mode_name}] {pt_name}: totient offset {matches[0][0]}: "
                              f"{matches[0][1]}/{matches[0][2]} matches")
                    
                    fskip = check_fskip_totient(runes, key_vals, max_offset=40000)
                    if fskip and fskip[0][1] >= max(3, n * 0.3):
                        print(f"  [{mode_name}+Fskip] {pt_name}: offset {fskip[0][0]}: "
                              f"{fskip[0][1]}/{fskip[0][2]} matches")
        
        if best_overall:
            print(f"  BEST: {best_overall[0]} combo={best_overall[1]} "
                  f"offset={best_overall[4]} score={best_overall[2]}/{best_overall[3]}")
    
    # Phase 3: Pattern detection
    print("\n" + "=" * 80)
    print("PHASE 3: LINEAR & PERIODIC PATTERN DETECTION")
    print("=" * 80)
    
    for page_num in sorted(all_page_data.keys()):
        data = all_page_data[page_num]
        singles = data['singles']
        n = len(singles)
        
        if n < 3:
            continue
        
        print(f"\n--- PAGE {page_num}: {n} constraints ---")
        
        for mode_name, key_name, key_func in [
            ("Vig", "key_sub", lambda sw, pt: (sw['cipher'] - pt) % 29),
            ("Beau", "key_beau", lambda sw, pt: (pt + sw['cipher']) % 29),
        ]:
            for pt_val, pt_name in [(10, "I"), (24, "A")]:
                key_vals = [(sw['pos'], key_func(sw, pt_val)) for sw in singles]
                
                # Check Caesar (all same value)
                vals = [v for _, v in key_vals]
                if len(set(vals)) == 1:
                    print(f"  *** [{mode_name} {pt_name}] ALL KEY VALUES = {vals[0]} (CAESAR!)")
                
                # Check linear
                linear = check_linear(key_vals)
                if linear and linear[0][2] >= n * 0.8:
                    a, b, m = linear[0]
                    print(f"  [{mode_name} {pt_name}] Linear: key=({a}*pos+{b})%29, {m}/{n} match")
                
                # Check periodic
                periodic = check_periodic(key_vals, max_period=100)
                if periodic:
                    for period, cons, total in periodic[:3]:
                        if cons >= total * 0.9 and period <= 50:
                            print(f"  [{mode_name} {pt_name}] Period {period}: {cons}/{total}")
        
        # Try all combos for small n
        if n <= 12:
            for mode_name, key_func in [("Vig", lambda c, p: (c-p)%29), ("Beau", lambda c, p: (p+c)%29)]:
                for combo in range(2**n):
                    key_vals = []
                    for i, sw in enumerate(singles):
                        pt = 24 if (combo >> i) & 1 else 10
                        key_vals.append((sw['pos'], key_func(sw['cipher'], pt)))
                    
                    vals = [v for _, v in key_vals]
                    if len(set(vals)) == 1:
                        label = "".join("A" if (combo >> i) & 1 else "I" for i in range(n))
                        print(f"  *** [{mode_name}] Combo {label}: ALL KEY = {vals[0]} (CAESAR!)")
                    
                    linear = check_linear(key_vals)
                    if linear and linear[0][2] == n:
                        label = "".join("A" if (combo >> i) & 1 else "I" for i in range(n))
                        a, b, m = linear[0]
                        print(f"  *** [{mode_name}] Combo {label}: PERFECT LINEAR key=({a}*pos+{b})%29")
    
    # Phase 4: Cross-validate with 2-rune words
    print("\n" + "=" * 80)
    print("PHASE 4: TWO-RUNE WORD VALIDATION (Caesar shifts)")
    print("=" * 80)
    
    for page_num in sorted(all_page_data.keys()):
        data = all_page_data[page_num]
        two_rune = data['two_rune']
        
        if not two_rune:
            continue
        
        for shift in range(29):
            decoded = []
            for tw in two_rune:
                p0 = (tw['cipher'][0] - shift) % 29
                p1 = (tw['cipher'][1] - shift) % 29
                word = TWO_RUNE_WORDS.get((p0, p1))
                if word:
                    decoded.append((tw['pos'], word))
            
            if len(decoded) >= max(2, len(two_rune) * 0.08):
                print(f"  Page {page_num} shift {shift:2d}: {len(decoded)}/{len(two_rune)} "
                      f"({100*len(decoded)/len(two_rune):.0f}%) - "
                      f"{', '.join(w for _, w in decoded[:8])}")
    
    # Phase 5: P19's key on known-plaintext positions
    print("\n" + "=" * 80)
    print("PHASE 5: P19 KEY PATTERN CHECK")
    print("=" * 80)
    
    P19_KEY = [24,15,2,24,4,21,11,10,20,16,9,19,26,11,7,5,11,6,27,8,22,25,21,16,25,0,27,9,21,7,27,15,21,9,3,16,5,22,18,4,5,18,23,28,28,28,28]
    
    for page_num in sorted(all_page_data.keys()):
        data = all_page_data[page_num]
        singles = data['singles']
        
        if len(singles) < 2:
            continue
        
        # Try P19 key at various offsets
        best_p19 = (0, 0)
        for offset in range(len(P19_KEY)):
            for pt_val in [10, 24]:
                matches = 0
                for sw in singles:
                    key_pos = (sw['pos'] + offset) % len(P19_KEY)
                    expected_key = P19_KEY[key_pos]
                    actual_key = (sw['cipher'] - pt_val) % 29
                    if expected_key == actual_key:
                        matches += 1
                if matches > best_p19[1]:
                    best_p19 = (offset, matches)
        
        if best_p19[1] >= 2:
            print(f"  Page {page_num}: P19 key best match: offset {best_p19[0]}, {best_p19[1]}/{len(singles)}")
    
    # Phase 6: Key value distribution analysis
    print("\n" + "=" * 80)
    print("PHASE 6: KEY VALUE DISTRIBUTION")
    print("=" * 80)
    
    for page_num in sorted(all_page_data.keys()):
        data = all_page_data[page_num]
        singles = data['singles']
        
        if len(singles) < 5:
            continue
        
        for pt_val, pt_name in [(10, "I"), (24, "A")]:
            key_vals = [(sw['cipher'] - pt_val) % 29 for sw in singles]
            freq = Counter(key_vals)
            
            # Check if distribution is uniform (random) or peaked (pattern)
            max_freq = max(freq.values())
            avg_freq = len(key_vals) / 29
            
            if max_freq >= avg_freq * 3:
                most_common = freq.most_common(3)
                print(f"  Page {page_num} [{pt_name}]: peaked distribution! "
                      f"Most common: {most_common}")
    
    print("\n\nDONE - Known Plaintext Attack Complete")

if __name__ == "__main__":
    main()
