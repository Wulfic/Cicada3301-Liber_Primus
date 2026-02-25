#!/usr/bin/env python3
"""
LFSR-based Stream Cipher Attack + Known Plaintext LFSR Solver
=============================================================
Based on community insight that unsolved LP pages show flat frequency
distribution consistent with LFSR-generated key stream.

Approach 1: GF(29) LFSR brute force (order 2-3)
Approach 2: Known Plaintext Attack - assume page title, derive key stream,
            check if it follows LFSR recurrence
Approach 3: Single-rune word constraint (must be 'I' or 'A')
Approach 4: Binary LFSR (5-bit grouping) with various polynomials
"""

import os, sys
from collections import Counter
from itertools import product

# Gematria Primus
RUNE_TO_SHIFT = {
    'ᚠ': 0, 'ᚢ': 1, 'ᚦ': 2, 'ᚩ': 3, 'ᚱ': 4, 'ᚳ': 5, 'ᚷ': 6, 'ᚹ': 7,
    'ᚻ': 8, 'ᚾ': 9, 'ᛁ': 10, 'ᛂ': 11, 'ᛇ': 12, 'ᛈ': 13, 'ᛉ': 14, 'ᛋ': 15,
    'ᛏ': 16, 'ᛒ': 17, 'ᛖ': 18, 'ᛗ': 19, 'ᛚ': 20, 'ᛝ': 21, 'ᛟ': 22, 'ᛞ': 23,
    'ᚪ': 24, 'ᚫ': 25, 'ᚣ': 26, 'ᛡ': 27, 'ᛠ': 28, 'ᛄ': 11
}
SHIFT_TO_ENGLISH = {
    0: 'F', 1: 'U', 2: 'TH', 3: 'O', 4: 'R', 5: 'C', 6: 'G', 7: 'W',
    8: 'H', 9: 'N', 10: 'I', 11: 'J', 12: 'EO', 13: 'P', 14: 'X', 15: 'S',
    16: 'T', 17: 'B', 18: 'E', 19: 'M', 20: 'L', 21: 'NG', 22: 'OE', 23: 'D',
    24: 'A', 25: 'AE', 26: 'Y', 27: 'IA', 28: 'EA'
}

# Title prefixes to try as known plaintext
KNOWN_PREFIXES = [
    # Common LP page titles/starts
    ('A KOAN', [24, 5, 3, 24, 9]),   # A=24, K(C)=5, O=3, A=24, N=9
    ('AN END', [24, 9, 18, 9, 23]),
    ('A WARNING', [24, 7, 24, 4, 9, 10, 9, 6]),
    ('SOME WISDOM', [15, 3, 19, 18, 7, 10, 15, 23, 3, 19]),
    ('THE INSTAR', [2, 18, 10, 9, 15, 16, 24, 4]),  # TH=2
    ('A COMMANDMENT', [24, 5, 3, 19, 19, 24, 9, 23, 19, 18, 9, 16]),
    ('AN INSTRUCTION', [24, 9, 10, 9, 15, 16, 4, 1, 5, 16, 10, 3, 9]),
    ('WELCOME PILGRIM', [7, 18, 20, 5, 3, 19, 18, 13, 10, 20, 6, 4, 10, 19]),
    ('A LOSS OF DIVINITY', [24, 20, 3, 15, 15, 3, 0, 23, 10, 1, 10, 9, 10, 16, 26]),
    ('THE LOSS OF DIVINITY', [2, 18, 20, 3, 15, 15, 3, 0, 23, 10, 1, 10, 9, 10, 16, 26]),
    ('THE CIRCUMFERENCE', [2, 18, 5, 10, 4, 5, 1, 19, 0, 18, 4, 18, 9, 5, 18]),
    ('A PARABLE', [24, 13, 24, 4, 24, 17, 20, 18]),
    ('COMMAND YOUR', [5, 3, 19, 19, 24, 9, 23, 26, 3, 1, 4]),
    ('BELIEVE NOTHING', [17, 18, 20, 10, 18, 1, 18, 9, 3, 2, 10, 9, 6]),
    ('CONSUME DIVIDE', [5, 3, 9, 15, 1, 19, 18, 23, 10, 1, 10, 23, 18]),
    ('WISDOM IS', [7, 10, 15, 23, 3, 19, 10, 15]),
    ('I HAVE', [10, 8, 24, 1, 18]),
    ('WE ARE', [7, 18, 24, 4, 18]),
    ('IT IS', [10, 16, 10, 15]),
    ('THERE IS', [2, 18, 4, 18, 10, 15]),
    ('DO NOT', [23, 3, 9, 3, 16]),
]

def extract_rune_shifts(rune_text):
    """Extract shift values from rune text."""
    return [RUNE_TO_SHIFT[ch] for ch in rune_text if ch in RUNE_TO_SHIFT]

def decode_to_runeglish(shifts):
    return ''.join(SHIFT_TO_ENGLISH.get(s, '?') for s in shifts)

def calc_ioc(shifts):
    if len(shifts) < 2:
        return 0
    freq = Counter(shifts)
    n = len(shifts)
    return sum(f * (f-1) for f in freq.values()) / (n * (n-1)) * 29 if n > 1 else 0

def score_text(runeglish):
    text = runeglish.upper()
    bigrams = ['TH', 'HE', 'IN', 'ER', 'AN', 'RE', 'ON', 'AT', 'EN', 'ND',
               'ES', 'OR', 'TE', 'ED', 'IS', 'IT', 'AL', 'AR', 'ST', 'TO',
               'NT', 'NG', 'SE', 'HA', 'AS', 'OU', 'LE', 'VE', 'CO', 'ME']
    score = sum(text.count(bg) * 10 for bg in bigrams)
    words = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN',
             'WAS', 'ONE', 'OUR', 'OUT', 'HAD', 'HAS', 'HIS', 'HOW', 'ITS',
             'MAY', 'NOW', 'OLD', 'SEE', 'WAY', 'WHO', 'DID', 'THAT', 'WITH',
             'HAVE', 'THIS', 'WILL', 'YOUR', 'FROM', 'THEY', 'BEEN', 'SOME',
             'WHEN', 'WHAT', 'THERE', 'WHICH', 'THEIR', 'SHALL', 'EACH',
             'FIND', 'HERE', 'KNOW', 'TRUTH', 'LIGHT', 'PATH', 'WISDOM']
    for w in words:
        score += text.count(w) * len(w) * 3
    return score

def mod_inverse(a, m=29):
    """Modular inverse using extended GCD."""
    if a == 0:
        return None
    return pow(a, -1, m)

def load_page_runes(page_dir):
    runes_file = os.path.join(page_dir, 'runes.txt')
    if os.path.exists(runes_file):
        with open(runes_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return None

def find_single_rune_words(rune_text):
    """Find positions and values of single-rune words (must be I=10 or A=24)."""
    # Split by separators
    words = []
    current_word = []
    pos = 0  # Position in rune-only stream
    word_start_pos = 0
    
    for ch in rune_text:
        if ch in RUNE_TO_SHIFT:
            if not current_word:
                word_start_pos = pos
            current_word.append((pos, RUNE_TO_SHIFT[ch]))
            pos += 1
        elif ch in '-•\n ':  # Word separator
            if len(current_word) == 1:
                words.append(current_word[0])  # (position, shift_value)
            current_word = []
    
    if len(current_word) == 1:
        words.append(current_word[0])
    
    return words


def gf29_lfsr_order2(a, b, s0, s1, length):
    """Generate GF(29) LFSR sequence of given length.
    s_n = a*s_{n-1} + b*s_{n-2} mod 29"""
    seq = [s0, s1]
    for _ in range(length - 2):
        seq.append((a * seq[-1] + b * seq[-2]) % 29)
    return seq


def gf29_lfsr_order3(a, b, c, s0, s1, s2, length):
    """Generate GF(29) order-3 LFSR sequence.
    s_n = a*s_{n-1} + b*s_{n-2} + c*s_{n-3} mod 29"""
    seq = [s0, s1, s2]
    for _ in range(length - 3):
        seq.append((a * seq[-1] + b * seq[-2] + c * seq[-3]) % 29)
    return seq


def solve_lfsr_order2(key_stream):
    """Given >= 4 values of key stream, solve for order-2 LFSR parameters.
    s_2 = a*s_1 + b*s_0 mod 29
    s_3 = a*s_2 + b*s_1 mod 29
    Returns (a, b) or None if system is singular."""
    if len(key_stream) < 4:
        return None
    s0, s1, s2, s3 = key_stream[:4]
    
    # Matrix: [[s1, s0], [s2, s1]] * [a, b]^T = [s2, s3]^T
    det = (s1 * s1 - s2 * s0) % 29
    det_inv = mod_inverse(det)
    if det_inv is None:
        return None
    
    a = ((s1 * s2 - s0 * s3) * det_inv) % 29
    b = ((s1 * s3 - s2 * s2) * det_inv) % 29
    
    # Verify
    if (a * s1 + b * s0) % 29 != s2:
        return None
    if (a * s2 + b * s1) % 29 != s3:
        return None
    
    return (a, b)


def solve_lfsr_order3(key_stream):
    """Given >= 6 values, solve for order-3 LFSR parameters.
    Uses first 6 values to solve 3x3 system."""
    if len(key_stream) < 6:
        return None
    s = key_stream[:6]
    
    # s3 = a*s2 + b*s1 + c*s0
    # s4 = a*s3 + b*s2 + c*s1
    # s5 = a*s4 + b*s3 + c*s2
    
    # Build matrix and solve using Gaussian elimination mod 29
    matrix = [
        [s[2], s[1], s[0], s[3]],
        [s[3], s[2], s[1], s[4]],
        [s[4], s[3], s[2], s[5]]
    ]
    
    # Gaussian elimination mod 29
    for col in range(3):
        # Find pivot
        pivot = None
        for row in range(col, 3):
            if matrix[row][col] % 29 != 0:
                pivot = row
                break
        if pivot is None:
            return None
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
        
        inv = mod_inverse(matrix[col][col] % 29)
        if inv is None:
            return None
        
        for j in range(4):
            matrix[col][j] = (matrix[col][j] * inv) % 29
        
        for row in range(3):
            if row != col and matrix[row][col] % 29 != 0:
                factor = matrix[row][col] % 29
                for j in range(4):
                    matrix[row][j] = (matrix[row][j] - factor * matrix[col][j]) % 29
    
    a, b, c = matrix[0][3] % 29, matrix[1][3] % 29, matrix[2][3] % 29
    
    # Verify all 6 values
    for i in range(3, 6):
        expected = (a * s[i-1] + b * s[i-2] + c * s[i-3]) % 29
        if expected != s[i]:
            return None
    
    return (a, b, c)


def verify_lfsr_continuation(key_stream, params, order):
    """Verify that key stream continues to follow LFSR pattern beyond the initial solve points."""
    if order == 2:
        a, b = params
        for i in range(2, len(key_stream)):
            expected = (a * key_stream[i-1] + b * key_stream[i-2]) % 29
            if expected != key_stream[i]:
                return i  # First failure position
        return len(key_stream)  # All match
    elif order == 3:
        a, b, c = params
        for i in range(3, len(key_stream)):
            expected = (a * key_stream[i-1] + b * key_stream[i-2] + c * key_stream[i-3]) % 29
            if expected != key_stream[i]:
                return i
        return len(key_stream)


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    repo_dir = os.path.dirname(base_dir)
    pages_dir = os.path.join(repo_dir, 'LiberPrimus', 'pages')
    
    print("=" * 80)
    print("LFSR-BASED STREAM CIPHER ATTACK + KNOWN PLAINTEXT SOLVER")
    print("=" * 80)
    
    # Load unsolved pages
    unsolved_pages = {}
    for p in range(17, 55):
        page_dir = os.path.join(pages_dir, f'page_{p:02d}')
        rune_text = load_page_runes(page_dir)
        if rune_text:
            shifts = extract_rune_shifts(rune_text)
            if len(shifts) > 20:
                single_words = find_single_rune_words(rune_text)
                unsolved_pages[p] = {
                    'shifts': shifts, 
                    'rune_text': rune_text,
                    'single_words': single_words
                }
    
    print(f"\nLoaded {len(unsolved_pages)} unsolved pages")
    for p in sorted(unsolved_pages.keys()):
        sw = unsolved_pages[p]['single_words']
        sw_info = f", {len(sw)} single-rune words at positions {[s[0] for s in sw[:5]]}" if sw else ""
        print(f"  Page {p}: {len(unsolved_pages[p]['shifts'])} runes{sw_info}")
    
    modes = ['sub', 'beaufort', 'add']
    mode_funcs = {
        'sub': lambda c, k: (c - k) % 29,
        'beaufort': lambda c, k: (k - c) % 29,
        'add': lambda c, k: (c + k) % 29,
    }
    
    best_results = []
    
    # ==================== ATTACK 1: Known Plaintext → LFSR Detection ====================
    print("\n" + "=" * 80)
    print("ATTACK 1: Known Plaintext -> LFSR Parameter Detection")
    print("For each assumed prefix, derive key stream and check for LFSR structure")
    print("=" * 80)
    
    for page_num in sorted(unsolved_pages.keys()):
        cipher = unsolved_pages[page_num]['shifts']
        n = len(cipher)
        
        for title, prefix_shifts in KNOWN_PREFIXES:
            if len(prefix_shifts) < 4:
                continue
            
            for mode_name, mode_func in mode_funcs.items():
                # Derive key stream from known plaintext
                key_stream = []
                for i in range(len(prefix_shifts)):
                    if i < n:
                        # Reverse the mode to get key from cipher and plain
                        if mode_name == 'sub':
                            k = (cipher[i] - prefix_shifts[i]) % 29
                        elif mode_name == 'beaufort':
                            k = (prefix_shifts[i] + cipher[i]) % 29
                        elif mode_name == 'add':
                            k = (prefix_shifts[i] - cipher[i]) % 29  # Fix: key = plain - cipher if plain = cipher + key
                            # Actually: if plain = (cipher + key) % 29, then key = (plain - cipher) % 29
                        key_stream.append(k)
                
                if len(key_stream) < 4:
                    continue
                
                # Try order-2 LFSR
                params2 = solve_lfsr_order2(key_stream)
                if params2:
                    a, b = params2
                    # Generate full key stream
                    full_key = gf29_lfsr_order2(a, b, key_stream[0], key_stream[1], n)
                    # Decrypt
                    plain = [mode_func(cipher[i], full_key[i]) for i in range(n)]
                    ioc = calc_ioc(plain)
                    
                    if ioc > 1.25:
                        runeglish = decode_to_runeglish(plain)
                        txt_score = score_text(runeglish)
                        print(f"  ** Page {page_num} [{title}] {mode_name} LFSR(2) a={a} b={b}: IoC={ioc:.3f} score={txt_score}")
                        print(f"     Text: {runeglish[:150]}")
                        best_results.append({
                            'page': page_num, 'title': title, 'mode': mode_name,
                            'order': 2, 'params': params2, 'ioc': ioc,
                            'score': txt_score, 'text': runeglish[:200]
                        })
                
                # Try order-3 LFSR
                if len(key_stream) >= 6:
                    params3 = solve_lfsr_order3(key_stream)
                    if params3:
                        a, b, c = params3
                        full_key = gf29_lfsr_order3(a, b, c, key_stream[0], key_stream[1], key_stream[2], n)
                        plain = [mode_func(cipher[i], full_key[i]) for i in range(n)]
                        ioc = calc_ioc(plain)
                        
                        if ioc > 1.25:
                            runeglish = decode_to_runeglish(plain)
                            txt_score = score_text(runeglish)
                            print(f"  ** Page {page_num} [{title}] {mode_name} LFSR(3) a={a} b={b} c={c}: IoC={ioc:.3f} score={txt_score}")
                            print(f"     Text: {runeglish[:150]}")
                            best_results.append({
                                'page': page_num, 'title': title, 'mode': mode_name,
                                'order': 3, 'params': params3, 'ioc': ioc,
                                'score': txt_score, 'text': runeglish[:200]
                            })
    
    print(f"\n  Attack 1 results: {len(best_results)} hits with IoC > 1.25")
    
    # ==================== ATTACK 2: GF(29) LFSR Order-2 Smart Search ====================
    print("\n" + "=" * 80)
    print("ATTACK 2: GF(29) LFSR Order-2 - Smart Search via basis linearity")
    print("Uses LFSR linearity: stream(s0,s1) = s0*basis(1,0) + s1*basis(0,1)")
    print("Only 29*28 = 812 (a,b) pairs to test, then solve s0,s1 analytically")
    print("=" * 80)
    
    # Test on 5 largest pages
    target_pages = sorted(unsolved_pages.keys(),
                         key=lambda p: len(unsolved_pages[p]['shifts']),
                         reverse=True)[:5]
    
    for page_num in target_pages:
        cipher = unsolved_pages[page_num]['shifts']
        n = len(cipher)
        
        print(f"\n--- Page {page_num} ({n} runes) ---")
        
        for a in range(29):
            for b in range(1, 29):
                # Generate basis streams once per (a,b)
                basis0 = gf29_lfsr_order2(a, b, 1, 0, n)
                basis1 = gf29_lfsr_order2(a, b, 0, 1, n)
                
                # For each mode, try all (s0,s1) efficiently
                # Key insight: plain[i] = cipher[i] - (s0*b0[i] + s1*b1[i]) mod 29
                # This is affine in (s0,s1). We sample a few (s0,s1) values;
                # if none give high IoC, skip.
                
                for mode_name, mode_func in mode_funcs.items():
                    best_ioc_for_ab = 0
                    
                    # Sample 29 values along s0 axis (s1=1) and 29 along s1 axis (s0=1)
                    for s0 in range(29):
                        s1 = 1
                        full_key = [(s0 * basis0[i] + s1 * basis1[i]) % 29 for i in range(n)]
                        plain = [mode_func(cipher[i], full_key[i]) for i in range(n)]
                        ioc = calc_ioc(plain)
                        if ioc > best_ioc_for_ab:
                            best_ioc_for_ab = ioc
                        
                        if ioc > 1.35:
                            runeglish = decode_to_runeglish(plain)
                            txt_score = score_text(runeglish)
                            print(f"  ** a={a} b={b} s0={s0} s1={s1} {mode_name}: IoC={ioc:.3f} score={txt_score}")
                            print(f"     Text: {runeglish[:150]}")
                            best_results.append({
                                'page': page_num, 'params': (a,b,s0,s1),
                                'mode': mode_name, 'ioc': ioc, 'score': txt_score,
                                'text': runeglish[:200], 'type': 'LFSR_order2'
                            })
                    
                    for s1 in range(29):
                        s0 = 1
                        full_key = [(s0 * basis0[i] + s1 * basis1[i]) % 29 for i in range(n)]
                        plain = [mode_func(cipher[i], full_key[i]) for i in range(n)]
                        ioc = calc_ioc(plain)
                        
                        if ioc > 1.35:
                            runeglish = decode_to_runeglish(plain)
                            txt_score = score_text(runeglish)
                            print(f"  ** a={a} b={b} s0={s0} s1={s1} {mode_name}: IoC={ioc:.3f} score={txt_score}")
                            print(f"     Text: {runeglish[:150]}")
                            best_results.append({
                                'page': page_num, 'params': (a,b,s0,s1),
                                'mode': mode_name, 'ioc': ioc, 'score': txt_score,
                                'text': runeglish[:200], 'type': 'LFSR_order2'
                            })
            
            if a % 10 == 9:
                print(f"  Progress: a={a}/28")
    
    # ==================== ATTACK 3: Single-Rune Word Constraints ====================
    print("\n" + "=" * 80)
    print("ATTACK 3: Single-Rune Word Constraints")
    print("Single-rune words must be 'I'(10) or 'A'(24)")
    print("Using these constraints to derive LFSR parameters")
    print("=" * 80)
    
    for page_num in sorted(unsolved_pages.keys()):
        single_words = unsolved_pages[page_num]['single_words']
        cipher = unsolved_pages[page_num]['shifts']
        n = len(cipher)
        
        if len(single_words) < 4:
            continue
        
        # For each combination of I/A assignments to single-rune words
        # and each mode, derive key values at those positions
        # Then check if they fit an LFSR
        
        print(f"\n  Page {page_num}: {len(single_words)} single-rune words")
        
        # Try first 4 single-rune words with all I/A combinations (2^4 = 16)
        words_to_try = single_words[:min(6, len(single_words))]
        n_words = len(words_to_try)
        
        for assignment in product([10, 24], repeat=n_words):
            for mode_name, mode_func in mode_funcs.items():
                # Derive key values at single-word positions
                key_values = {}
                for (pos, cipher_val), plain_val in zip(words_to_try, assignment):
                    if mode_name == 'sub':
                        k = (cipher_val - plain_val) % 29
                    elif mode_name == 'beaufort':
                        k = (plain_val + cipher_val) % 29
                    elif mode_name == 'add':
                        k = (plain_val - cipher_val) % 29
                    key_values[pos] = k
                
                # Check if these key values are consistent with any order-2 LFSR
                # For order-2: k[n] = a*k[n-1] + b*k[n-2] mod 29
                # Need at least 4 key values at known positions
                positions = sorted(key_values.keys())
                
                if len(positions) >= 4:
                    # Check if CONSECUTIVE positions among our known positions
                    # form LFSR structure
                    # This is harder with non-consecutive positions...
                    # For now, try brute-forcing a,b and checking consistency
                    
                    found_lfsr = False
                    for a in range(29):
                        for b in range(29):
                            if a == 0 and b == 0:
                                continue
                            
                            # We know key at positions in key_values
                            # Try to find s0, s1 such that LFSR(a,b,s0,s1)[pos] = key_values[pos]
                            # for all known positions
                            
                            # Generate basis streams
                            basis0 = gf29_lfsr_order2(a, b, 1, 0, n)
                            basis1 = gf29_lfsr_order2(a, b, 0, 1, n)
                            
                            # For each pair of known positions, solve for s0, s1
                            p0, p1 = positions[0], positions[1]
                            # key[p0] = s0*basis0[p0] + s1*basis1[p0]
                            # key[p1] = s0*basis0[p1] + s1*basis1[p1]
                            
                            det = (basis0[p0] * basis1[p1] - basis0[p1] * basis1[p0]) % 29
                            det_inv = mod_inverse(det)
                            if det_inv is None:
                                continue
                            
                            s0 = ((key_values[p0] * basis1[p1] - key_values[p1] * basis1[p0]) * det_inv) % 29
                            s1 = ((basis0[p0] * key_values[p1] - basis0[p1] * key_values[p0]) * det_inv) % 29
                            
                            # Verify against ALL known positions
                            match = True
                            for pos in positions[2:]:
                                expected = (s0 * basis0[pos] + s1 * basis1[pos]) % 29
                                if expected != key_values[pos]:
                                    match = False
                                    break
                            
                            if match:
                                # LFSR consistent! Decrypt full page
                                full_key = [(s0 * basis0[i] + s1 * basis1[i]) % 29 for i in range(n)]
                                plain = [mode_func(cipher[i], full_key[i]) for i in range(n)]
                                ioc = calc_ioc(plain)
                                
                                if ioc > 1.3:
                                    runeglish = decode_to_runeglish(plain)
                                    txt_score = score_text(runeglish)
                                    assign_str = '/'.join('I' if v==10 else 'A' for v in assignment)
                                    print(f"  ** Page {page_num} [{assign_str}] {mode_name} LFSR(2) a={a} b={b}: IoC={ioc:.3f} score={txt_score}")
                                    print(f"     Text: {runeglish[:150]}")
                                    found_lfsr = True
                                    best_results.append({
                                        'page': page_num, 'assignment': assign_str,
                                        'mode': mode_name, 'order': 2,
                                        'params': (a,b,s0,s1), 'ioc': ioc,
                                        'score': txt_score, 'text': runeglish[:200]
                                    })
    
    # ==================== ATTACK 4: Binary LFSR (5-bit groups) ====================
    print("\n" + "=" * 80)
    print("ATTACK 4: Binary LFSR with 5-bit grouping")
    print("Binary LFSR degree 5-16, output grouped into 5-bit mod-29 values")
    print("=" * 80)
    
    # Known maximal-length LFSR polynomials (taps as bit positions)
    # These produce maximum period 2^n - 1
    maximal_polys = {
        5: [[5, 3], [5, 4, 3, 2], [5, 4, 2, 1]],
        6: [[6, 5], [6, 5, 4, 1], [6, 5, 3, 2]],
        7: [[7, 6], [7, 6, 5, 4], [7, 5, 4, 3]],
        8: [[8, 6, 5, 4], [8, 7, 6, 1], [8, 7, 2, 1]],
        9: [[9, 5], [9, 8, 6, 5], [9, 8, 7, 2]],
        10: [[10, 7], [10, 9, 7, 6], [10, 9, 4, 1]],
        11: [[11, 9], [11, 10, 9, 7]],
        12: [[12, 11, 10, 4], [12, 11, 8, 6]],
        16: [[16, 15, 13, 4], [16, 14, 13, 11]],
    }
    
    for page_num in target_pages[:3]:
        cipher = unsolved_pages[page_num]['shifts']
        n = len(cipher)
        
        print(f"\n--- Page {page_num} ({n} runes) ---")
        
        for degree, polys in maximal_polys.items():
            n_states = 2**degree - 1  # Maximal period
            
            for taps in polys:
                # Try a sample of initial states
                sample_size = min(1000, n_states)
                step = max(1, n_states // sample_size)
                
                for init_state in range(1, n_states + 1, step):
                    # Generate binary LFSR
                    state = init_state
                    bits = []
                    for _ in range(n * 5 + 10):  # Need 5 bits per rune
                        bit = state & 1
                        bits.append(bit)
                        feedback = 0
                        for tap in taps:
                            feedback ^= (state >> (tap - 1)) & 1
                        state = ((state >> 1) | (feedback << (degree - 1))) & ((1 << degree) - 1)
                    
                    # Group bits into 5-bit values mod 29
                    key_stream = []
                    for i in range(0, len(bits) - 4, 5):
                        val = sum(bits[i+j] << j for j in range(5))
                        key_stream.append(val % 29)
                    
                    if len(key_stream) < n:
                        continue
                    
                    for mode_name, mode_func in mode_funcs.items():
                        plain = [mode_func(cipher[i], key_stream[i]) for i in range(n)]
                        ioc = calc_ioc(plain)
                        
                        if ioc > 1.35:
                            runeglish = decode_to_runeglish(plain)
                            txt_score = score_text(runeglish)
                            print(f"  ** LFSR deg={degree} taps={taps} init={init_state} {mode_name}: IoC={ioc:.3f} score={txt_score}")
                            print(f"     Text: {runeglish[:150]}")
                            best_results.append({
                                'page': page_num, 'type': f'binary_LFSR_deg{degree}',
                                'taps': taps, 'init': init_state,
                                'mode': mode_name, 'ioc': ioc, 'score': txt_score,
                                'text': runeglish[:200]
                            })
            
            if degree <= 10:
                print(f"  Degree {degree}: {len(polys)} polynomials × {sample_size} states × 3 modes tested")
    
    # ==================== SUMMARY ====================
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    
    if best_results:
        best_results.sort(key=lambda x: x.get('ioc', 0), reverse=True)
        print(f"\nTop {min(20, len(best_results))} results:")
        for i, r in enumerate(best_results[:20]):
            page = r.get('page', '?')
            ioc = r.get('ioc', 0)
            score = r.get('score', 0)
            rtype = r.get('type', r.get('title', r.get('assignment', '?')))
            mode = r.get('mode', '?')
            print(f"  {i+1}. Page {page}: IoC={ioc:.3f} score={score} [{rtype}] {mode}")
            print(f"     {r.get('text', '')[:120]}")
    else:
        print("\nNo results with IoC above threshold found.")
        print("LFSR-based approach also did not produce readable text.")
    
    print(f"\nTotal compelling results: {len(best_results)}")

if __name__ == '__main__':
    main()
