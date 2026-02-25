#!/usr/bin/env python3
"""
Comprehensive Prime Stream Cipher Attack on Liber Primus Unsolved Pages

Systematically tests the proven P55/73 cipher method (prime-based stream cipher)
with all parameter variations on unsolved pages 21-54.

KEY INSIGHT: P55/73 was solved with:
  plaintext = (cipher_shift - (prime_n + 57)) % 29
  which equals: (cipher_shift - (prime_n - 1)) % 29  [since 57 ≡ -1 mod 29]
  This is the RuneSolver's vigstream with primestream + totient (subtract 1)

ATTACK VECTORS:
1. Prime stream with ALL 29 offsets (0-28)
2. Both directions: SUB (cipher - stream) and BEAUFORT (stream - cipher) and ADD (cipher + stream)
3. With and without F-skip at position 56
4. Stream starting position offsets
5. Fibonacci, Lucas, and totient(prime) streams
6. Prime-position splitting (like P20)
"""

import os
import sys
import math
from collections import Counter
from pathlib import Path

# ==================== GEMATRIA PRIMUS ====================

RUNE_TO_SHIFT = {
    'ᚠ': 0,  'ᚢ': 1,  'ᚦ': 2,  'ᚩ': 3,  'ᚱ': 4,
    'ᚳ': 5,  'ᚷ': 6,  'ᚹ': 7,  'ᚻ': 8,  'ᚾ': 9,
    'ᛁ': 10, 'ᛂ': 11, 'ᛇ': 12, 'ᛈ': 13, 'ᛉ': 14,
    'ᛋ': 15, 'ᛏ': 16, 'ᛒ': 17, 'ᛖ': 18, 'ᛗ': 19,
    'ᛚ': 20, 'ᛝ': 21, 'ᛟ': 22, 'ᛞ': 23, 'ᚪ': 24,
    'ᚫ': 25, 'ᚣ': 26, 'ᛡ': 27, 'ᛠ': 28,
    'ᛄ': 11,  # Alternative form of ᛂ (J)
}

SHIFT_TO_LATIN = {
    0: 'F', 1: 'U', 2: 'TH', 3: 'O', 4: 'R',
    5: 'CK', 6: 'G', 7: 'W', 8: 'H', 9: 'N',
    10: 'I', 11: 'J', 12: 'EO', 13: 'P', 14: 'X',
    15: 'S', 16: 'T', 17: 'B', 18: 'E', 19: 'M',
    20: 'L', 21: 'NG', 22: 'OE', 23: 'D', 24: 'A',
    25: 'AE', 26: 'Y', 27: 'IA', 28: 'EA',
}

SEPARATORS = set(['-', '•', ' ', '.', ':', "'", ',', '\n', '\r', '&', '$', '%', '/', '"', '\t'])

# English-like frequency for GP shifts (approximate from solved pages)
# Based on English letter frequency adapted to GP alphabet
ENGLISH_FREQ = {
    0: 0.02,   # F
    1: 0.03,   # U
    2: 0.07,   # TH (common digraph)
    3: 0.08,   # O
    4: 0.06,   # R
    5: 0.03,   # CK
    6: 0.02,   # G
    7: 0.02,   # W
    8: 0.06,   # H
    9: 0.07,   # N
    10: 0.07,  # I
    11: 0.005, # J
    12: 0.01,  # EO
    13: 0.02,  # P
    14: 0.001, # X
    15: 0.06,  # S
    16: 0.09,  # T
    17: 0.015, # B
    18: 0.13,  # E
    19: 0.025, # M
    20: 0.04,  # L
    21: 0.03,  # NG
    22: 0.01,  # OE
    23: 0.04,  # D
    24: 0.08,  # A
    25: 0.01,  # AE
    26: 0.02,  # Y
    27: 0.01,  # IA
    28: 0.02,  # EA
}

# Common English bigrams in GP representation
COMMON_BIGRAMS = {
    (2, 18): 5,  # TH-E
    (8, 18): 4,  # H-E
    (10, 9): 4, # I-N
    (18, 4): 3,  # E-R
    (24, 9): 3, # A-N
    (4, 18): 3,  # R-E
    (3, 9): 3,   # O-N
    (16, 8): 3,  # T-H
    (9, 23): 3,  # N-D
    (15, 16): 3, # S-T
    (18, 15): 3, # E-S
    (18, 9): 3,  # E-N
    (3, 4): 2,   # O-R
    (16, 3): 2,  # T-O
    (10, 16): 2, # I-T
    (24, 16): 2, # A-T
    (24, 20): 2, # A-L
    (10, 15): 2, # I-S
}


def generate_primes(n):
    """Generate first n prime numbers."""
    primes = []
    candidate = 2
    while len(primes) < n:
        is_prime = True
        for p in primes:
            if p * p > candidate:
                break
            if candidate % p == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(candidate)
        candidate += 1
    return primes


def generate_fibonacci(n):
    """Generate first n Fibonacci numbers."""
    fibs = [0, 1]
    while len(fibs) < n:
        fibs.append(fibs[-1] + fibs[-2])
    return fibs[:n]


def generate_lucas(n):
    """Generate first n Lucas numbers."""
    lucas = [2, 1]
    while len(lucas) < n:
        lucas.append(lucas[-1] + lucas[-2])
    return lucas[:n]


def generate_totient_primes(n):
    """Generate φ(prime) = prime - 1 for first n primes."""
    primes = generate_primes(n)
    return [p - 1 for p in primes]


def load_page_runes(page_num):
    """Load rune text from a page file and extract just the rune shifts."""
    page_dir = Path(f"c:/Users/tyler/Repos/Cicada3301/LiberPrimus/pages/page_{page_num:02d}")
    rune_file = page_dir / "runes.txt"
    
    if not rune_file.exists():
        return None, None
    
    with open(rune_file, 'r', encoding='utf-8') as f:
        raw_text = f.read().strip()
    
    # Remove section markers
    for marker in ['&', '$', '%']:
        raw_text = raw_text.replace(marker, '')
    raw_text = raw_text.strip()
    
    # Extract rune shifts (skipping separators)
    shifts = []
    word_boundaries = []  # Track where words start/end
    
    for i, ch in enumerate(raw_text):
        if ch in RUNE_TO_SHIFT:
            shifts.append(RUNE_TO_SHIFT[ch])
        elif ch in SEPARATORS:
            if shifts and (not word_boundaries or word_boundaries[-1] != len(shifts)):
                word_boundaries.append(len(shifts))
    
    return shifts, word_boundaries


def calculate_ioc(shifts):
    """Calculate Index of Coincidence normalized to 29 symbols."""
    if len(shifts) < 2:
        return 0
    n = len(shifts)
    freq = Counter(shifts)
    total = sum(count * (count - 1) for count in freq.values())
    return (total * 29) / (n * (n - 1)) if n > 1 else 0


def score_plaintext(shifts, word_boundaries=None):
    """Score a decrypted text based on multiple English-like metrics."""
    if not shifts:
        return 0
    
    n = len(shifts)
    score = 0
    
    # 1. IoC Score (English ~1.73, random ~1.0)
    ioc = calculate_ioc(shifts)
    ioc_score = max(0, (ioc - 1.0) * 200)  # Scale: 1.73 → 146
    score += ioc_score
    
    # 2. Frequency correlation with English
    freq = Counter(shifts)
    total = sum(freq.values())
    chi_sq = 0
    for s in range(29):
        observed = freq.get(s, 0) / total
        expected = ENGLISH_FREQ.get(s, 0.01)
        chi_sq += (observed - expected) ** 2 / expected
    freq_score = max(0, 100 - chi_sq * 10)
    score += freq_score
    
    # 3. Bigram score
    bigram_score = 0
    for i in range(len(shifts) - 1):
        pair = (shifts[i], shifts[i+1])
        if pair in COMMON_BIGRAMS:
            bigram_score += COMMON_BIGRAMS[pair]
    bigram_score = bigram_score / max(1, n) * 100
    score += bigram_score
    
    # 4. Check for common English patterns in GP: THE, AND, FOR, etc.
    latin = shifts_to_latin(shifts, word_boundaries)
    word_score = 0
    common_words = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL',
                    'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'HIS', 'HAS', 'HAD',
                    'THAT', 'WITH', 'HAVE', 'THIS', 'WILL', 'YOUR', 'FROM',
                    'THEY', 'BEEN', 'SAID', 'EACH', 'WHICH', 'THEIR',
                    'THERE', 'THEM', 'THEN', 'THAN', 'SOME', 'WHAT',
                    'WHEN', 'WERE', 'INTO', 'MORE', 'LIKE', 'ONLY',
                    'WE', 'AN', 'IN', 'IS', 'IT', 'OF', 'TO', 'IF', 'NO',
                    'DO', 'BE', 'AS', 'AT', 'OR', 'SO', 'BY', 'ON', 'HE',
                    'WHO', 'ITS', 'OWN', 'SET', 'MAN', 'CAN', 'SEE',
                    'THOSE', 'THESE', 'SHALL', 'WOULD', 'COULD',
                    'A', 'I']
    
    words = latin.split(' ')
    for w in words:
        w_clean = w.strip().upper()
        if w_clean in common_words:
            word_score += len(w_clean) * 5
    word_score = word_score / max(1, len(words)) * 50
    score += word_score
    
    return score


def shifts_to_latin(shifts, word_boundaries=None):
    """Convert shifts to Latin text, inserting spaces at word boundaries."""
    if word_boundaries is None:
        word_boundaries = []
    
    result = []
    wb_set = set(word_boundaries)
    for i, s in enumerate(shifts):
        if i in wb_set:
            result.append(' ')
        result.append(SHIFT_TO_LATIN.get(s, '?'))
    return ''.join(result)


def decrypt_stream(cipher_shifts, stream, mode='sub', start_pos=0):
    """
    Decrypt using a stream cipher.
    
    mode: 'sub' = (cipher - stream) % 29  [RuneSolver vigstream]
          'beaufort' = (stream - cipher) % 29
          'add' = (cipher + stream) % 29
    start_pos: starting position in the stream
    """
    result = []
    stream_len = len(stream)
    
    for i, c in enumerate(cipher_shifts):
        stream_idx = (i + start_pos) % stream_len
        s = stream[stream_idx]
        
        if mode == 'sub':
            p = (c - s) % 29
        elif mode == 'beaufort':
            p = (s - c) % 29
        elif mode == 'add':
            p = (c + s) % 29
        else:
            p = c
        
        result.append(p)
    
    return result


def build_prime_stream(length, offset=0, f_skip=True):
    """
    Build a prime-based stream of given length.
    
    offset: constant added to each prime before mod 29
    f_skip: if True, position 56 uses value 1 instead of 263
    """
    primes = generate_primes(length + 10)
    stream = []
    
    for i in range(length):
        if f_skip and i == 56:
            val = (1 + offset) % 29
        else:
            val = (primes[i] + offset) % 29
        stream.append(val)
    
    return stream


def build_totient_prime_stream(length, f_skip=True):
    """Build stream using φ(prime) = prime - 1 (the P55/73 proven method)."""
    return build_prime_stream(length, offset=-1, f_skip=f_skip)
    # Note: offset=-1 means (prime - 1) mod 29, which equals (prime + 57) mod 29


def extract_prime_positions(shifts, word_boundaries):
    """Extract runes at prime-number positions (1-indexed), like P20."""
    prime_set = set(generate_primes(len(shifts) + 100))
    prime_shifts = []
    prime_wb = []
    non_prime_shifts = []
    non_prime_wb = []
    
    wb_set = set(word_boundaries)
    
    for i, s in enumerate(shifts):
        pos = i + 1  # 1-indexed position
        if pos in prime_set:
            if i in wb_set:
                prime_wb.append(len(prime_shifts))
            prime_shifts.append(s)
        else:
            if i in wb_set:
                non_prime_wb.append(len(non_prime_shifts))
            non_prime_shifts.append(s)
    
    return prime_shifts, prime_wb, non_prime_shifts, non_prime_wb


def run_attack_on_page(page_num, top_n=5):
    """Run all attack variations on a single page and return top results."""
    shifts, word_boundaries = load_page_runes(page_num)
    if shifts is None or len(shifts) < 10:
        return []
    
    n = len(shifts)
    results = []
    
    # ============ ATTACK 1: Prime Stream with offset variations ============
    for offset in range(29):
        for f_skip in [True, False]:
            stream = build_prime_stream(n + 10, offset=offset, f_skip=f_skip)
            
            for mode in ['sub', 'beaufort', 'add']:
                plain = decrypt_stream(shifts, stream, mode=mode)
                sc = score_plaintext(plain, word_boundaries)
                latin = shifts_to_latin(plain, word_boundaries)
                
                f_label = "Fskip" if f_skip else "NoFskip"
                label = f"PRIME_off{offset}_{mode}_{f_label}"
                results.append((sc, label, latin[:200], plain))
    
    # ============ ATTACK 2: Stream starting position offsets ============
    # For the totient prime stream (proven P55/73 method), try different start positions
    for start_pos in range(1, min(30, n)):
        stream = build_totient_prime_stream(n + start_pos + 10)
        plain = decrypt_stream(shifts, stream, mode='sub', start_pos=start_pos)
        sc = score_plaintext(plain, word_boundaries)
        latin = shifts_to_latin(plain, word_boundaries)
        label = f"TOTIENT_start{start_pos}_sub"
        results.append((sc, label, latin[:200], plain))
    
    # ============ ATTACK 3: Fibonacci stream ============
    fibs = generate_fibonacci(n + 10)
    for offset in range(29):
        fib_stream = [(f + offset) % 29 for f in fibs]
        for mode in ['sub', 'beaufort']:
            plain = decrypt_stream(shifts, fib_stream, mode=mode)
            sc = score_plaintext(plain, word_boundaries)
            latin = shifts_to_latin(plain, word_boundaries)
            label = f"FIB_off{offset}_{mode}"
            results.append((sc, label, latin[:200], plain))
    
    # ============ ATTACK 4: Lucas stream ============
    lucas = generate_lucas(n + 10)
    for offset in range(29):
        luc_stream = [(l + offset) % 29 for l in lucas]
        for mode in ['sub', 'beaufort']:
            plain = decrypt_stream(shifts, luc_stream, mode=mode)
            sc = score_plaintext(plain, word_boundaries)
            latin = shifts_to_latin(plain, word_boundaries)
            label = f"LUCAS_off{offset}_{mode}"
            results.append((sc, label, latin[:200], plain))
    
    # ============ ATTACK 5: Reversed prime stream ============
    for offset in range(29):
        stream = build_prime_stream(n + 10, offset=offset, f_skip=True)
        rev_stream = list(reversed(stream[:n]))
        for mode in ['sub', 'beaufort']:
            plain = decrypt_stream(shifts, rev_stream, mode=mode)
            sc = score_plaintext(plain, word_boundaries)
            latin = shifts_to_latin(plain, word_boundaries)
            label = f"REVPRIME_off{offset}_{mode}"
            results.append((sc, label, latin[:200], plain))
    
    # ============ ATTACK 6: GP shift index stream (0,1,2,...,28,0,1,...) ============
    gp_stream = [i % 29 for i in range(n)]
    for offset in range(29):
        shifted_gp = [(g + offset) % 29 for g in gp_stream]
        for mode in ['sub', 'beaufort']:
            plain = decrypt_stream(shifts, shifted_gp, mode=mode)
            sc = score_plaintext(plain, word_boundaries)
            latin = shifts_to_latin(plain, word_boundaries)
            label = f"GPSEQ_off{offset}_{mode}"
            results.append((sc, label, latin[:200], plain))
    
    # ============ ATTACK 7: Position-dependent (prime positions) splitting ============
    prime_shifts, prime_wb, nonprime_shifts, nonprime_wb = extract_prime_positions(shifts, word_boundaries)
    
    # Try Beaufort with DEOR on prime positions (like P20)
    deor_key = [23, 12, 3, 4]  # D=23, EO=12, O=3, R=4
    if prime_shifts:
        plain_prime = []
        for i, c in enumerate(prime_shifts):
            k = deor_key[i % len(deor_key)]
            plain_prime.append((k - c) % 29)  # Beaufort
        sc = score_plaintext(plain_prime, prime_wb)
        latin = shifts_to_latin(plain_prime, prime_wb)
        results.append((sc, "PRIMEPOS_BEAUFORT_DEOR", latin[:200], plain_prime))
        
        # Try Vigenere SUB with DEOR on prime positions
        plain_prime_vig = []
        for i, c in enumerate(prime_shifts):
            k = deor_key[i % len(deor_key)]
            plain_prime_vig.append((c - k) % 29)
        sc = score_plaintext(plain_prime_vig, prime_wb)
        latin = shifts_to_latin(plain_prime_vig, prime_wb)
        results.append((sc, "PRIMEPOS_VIGENERE_DEOR", latin[:200], plain_prime_vig))
    
    # Try various keywords on prime positions
    keywords = {
        'DIVINITY': [23, 10, 7, 10, 9, 10, 16, 26],
        'FIRFUMFERENFE': [0, 10, 4, 0, 1, 19, 0, 18, 4, 18, 9, 0, 18],
        'WISDOM': [7, 10, 15, 23, 3, 19],
        'PRIME': [13, 4, 10, 19, 18],
        'CICADA': [5, 10, 5, 24, 23, 24],
        'LIBER': [20, 10, 17, 18, 4],
        'PRIMUS': [13, 4, 10, 19, 1, 15],
        'TRUTH': [16, 4, 1, 16, 8],
        'SHADOW': [15, 8, 24, 23, 3, 7],
    }
    
    for kw_name, kw_shifts in keywords.items():
        if prime_shifts:
            # On prime positions
            for mode_name, mode_fn in [('BEAU', lambda c, k: (k - c) % 29), 
                                        ('SUB', lambda c, k: (c - k) % 29)]:
                plain = [mode_fn(c, kw_shifts[i % len(kw_shifts)]) for i, c in enumerate(prime_shifts)]
                sc = score_plaintext(plain, prime_wb)
                latin = shifts_to_latin(plain, prime_wb)
                results.append((sc, f"PRIMEPOS_{mode_name}_{kw_name}", latin[:200], plain))
        
        if nonprime_shifts:
            # On non-prime positions
            for mode_name, mode_fn in [('BEAU', lambda c, k: (k - c) % 29),
                                        ('SUB', lambda c, k: (c - k) % 29)]:
                plain = [mode_fn(c, kw_shifts[i % len(kw_shifts)]) for i, c in enumerate(nonprime_shifts)]
                sc = score_plaintext(plain, nonprime_wb)
                latin = shifts_to_latin(plain, nonprime_wb)
                results.append((sc, f"NONPRIMEPOS_{mode_name}_{kw_name}", latin[:200], plain))
    
    # ============ ATTACK 8: Combined prime+keyword ============
    # Prime stream on non-prime positions while DEOR on prime positions
    if prime_shifts and nonprime_shifts:
        for offset in range(29):
            np_stream = build_prime_stream(len(nonprime_shifts) + 10, offset=offset)
            np_plain = decrypt_stream(nonprime_shifts, np_stream, mode='sub')
            np_sc = score_plaintext(np_plain, nonprime_wb)
            
            # Combine with DEOR Beaufort on prime positions
            p_plain = [(deor_key[i % len(deor_key)] - c) % 29 for i, c in enumerate(prime_shifts)]
            p_sc = score_plaintext(p_plain, prime_wb)
            
            combined_sc = np_sc + p_sc
            label = f"COMBINED_DEOR+PRIME_off{offset}"
            results.append((combined_sc, label, f"P:{shifts_to_latin(p_plain, prime_wb)[:80]} NP:{shifts_to_latin(np_plain, nonprime_wb)[:80]}", None))
    
    # Sort by score descending
    results.sort(key=lambda x: x[0], reverse=True)
    return results[:top_n]


def verify_p55_solution():
    """Verify that our implementation correctly solves P55/73."""
    shifts, wb = load_page_runes(55)
    if shifts is None:
        print("WARNING: Cannot load page 55 runes to verify")
        return False
    
    # P55/73 solution: (cipher - (prime + 57)) % 29 with F-skip at position 56
    # Which is the same as the totient stream (prime - 1) 
    stream = build_totient_prime_stream(len(shifts) + 10)
    plain = decrypt_stream(shifts, stream, mode='sub')
    latin = shifts_to_latin(plain, wb)
    ioc = calculate_ioc(plain)
    
    print(f"=== P55 VERIFICATION ===")
    print(f"  Rune count: {len(shifts)}")
    print(f"  IoC after decryption: {ioc:.4f}")
    print(f"  Decrypted text: {latin[:200]}")
    print(f"  Score: {score_plaintext(plain, wb):.1f}")
    
    # Check if IoC is significantly above random
    if ioc > 1.3:
        print("  ✓ IoC > 1.3 - Solution appears valid!")
        return True
    else:
        print("  ✗ IoC <= 1.3 - Solution may not be correct")
        # Try with different page format handling
        return False


def main():
    print("=" * 80)
    print("PRIME STREAM CIPHER ATTACK ON LIBER PRIMUS")
    print("=" * 80)
    
    # Step 1: Verify our implementation on known solution P55
    print("\n--- STEP 1: Verify implementation on P55 ---")
    verify_p55_solution()
    
    # Step 2: Attack all unsolved pages
    unsolved_pages = list(range(17, 55))  # Pages 17-54
    
    print(f"\n--- STEP 2: Attacking {len(unsolved_pages)} unsolved pages ---")
    print(f"Testing: prime stream (29 offsets × 3 modes × 2 F-skip) = {29*3*2} variations")
    print(f"  + Fibonacci (29 offsets × 2 modes) = {29*2} variations")
    print(f"  + Lucas (29 offsets × 2 modes) = {29*2} variations")
    print(f"  + Reversed prime (29 offsets × 2 modes) = {29*2} variations")
    print(f"  + GP sequence (29 offsets × 2 modes) = {29*2} variations")
    print(f"  + Starting position offsets (29 positions)")
    print(f"  + Position-dependent splitting + keywords")
    print()
    
    all_results = {}
    
    for page_num in unsolved_pages:
        shifts, wb = load_page_runes(page_num)
        if shifts is None or len(shifts) < 10:
            print(f"  Page {page_num:02d}: SKIPPED (no data or too short)")
            continue
        
        print(f"  Page {page_num:02d}: {len(shifts)} runes... ", end='', flush=True)
        top = run_attack_on_page(page_num, top_n=10)
        all_results[page_num] = top
        
        if top:
            best_score = top[0][0]
            best_method = top[0][1]
            print(f"Best: {best_score:.1f} [{best_method}]")
        else:
            print("No results")
    
    # Step 3: Report
    print("\n" + "=" * 80)
    print("TOP RESULTS BY PAGE")
    print("=" * 80)
    
    # Collect all results for global ranking
    global_results = []
    
    for page_num in sorted(all_results.keys()):
        top = all_results[page_num]
        if not top:
            continue
        
        shifts, wb = load_page_runes(page_num)
        raw_ioc = calculate_ioc(shifts)
        
        print(f"\n--- Page {page_num:02d} ({len(shifts)} runes, raw IoC={raw_ioc:.4f}) ---")
        for rank, (sc, label, text, plain) in enumerate(top[:5], 1):
            dec_ioc = calculate_ioc(plain) if plain else 0
            print(f"  #{rank}: Score={sc:.1f} IoC={dec_ioc:.4f} [{label}]")
            # Show first 120 chars of text
            display_text = text[:120] if text else "(combined)"
            print(f"       {display_text}")
            
            global_results.append((sc, page_num, label, text, plain))
    
    # Global top 20
    global_results.sort(key=lambda x: x[0], reverse=True)
    
    print("\n" + "=" * 80)
    print("GLOBAL TOP 20 RESULTS ACROSS ALL PAGES")
    print("=" * 80)
    
    for rank, (sc, page_num, label, text, plain) in enumerate(global_results[:20], 1):
        dec_ioc = calculate_ioc(plain) if plain else 0
        print(f"  #{rank}: Page {page_num:02d} Score={sc:.1f} IoC={dec_ioc:.4f} [{label}]")
        display_text = text[:150] if text else "(combined)"
        print(f"       {display_text}")
    
    # Highlight any results with IoC > 1.3 (potential breakthrough)
    breakthroughs = [(sc, pg, label, text, plain) for sc, pg, label, text, plain in global_results if plain and calculate_ioc(plain) > 1.3]
    
    if breakthroughs:
        print("\n" + "!" * 80)
        print("POTENTIAL BREAKTHROUGHS (IoC > 1.3)")
        print("!" * 80)
        for sc, pg, label, text, plain in breakthroughs:
            dec_ioc = calculate_ioc(plain)
            print(f"\n  Page {pg:02d}: Score={sc:.1f} IoC={dec_ioc:.4f}")
            print(f"  Method: {label}")
            print(f"  Full text: {shifts_to_latin(plain)}")
    else:
        print("\n  No results with IoC > 1.3 found.")
        print("  This suggests the unsolved pages use a different cipher system")
        print("  than the simple prime stream from P55/73.")
    
    # Save detailed results
    output_file = "c:/Users/tyler/Repos/Cicada3301/results_prime_stream_attack.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("PRIME STREAM CIPHER ATTACK RESULTS\n")
        f.write("=" * 80 + "\n\n")
        
        for page_num in sorted(all_results.keys()):
            top = all_results[page_num]
            if not top:
                continue
            shifts, wb = load_page_runes(page_num)
            f.write(f"\n--- Page {page_num:02d} ({len(shifts)} runes) ---\n")
            for rank, (sc, label, text, plain) in enumerate(top[:10], 1):
                dec_ioc = calculate_ioc(plain) if plain else 0
                f.write(f"  #{rank}: Score={sc:.1f} IoC={dec_ioc:.4f} [{label}]\n")
                f.write(f"       {text[:200]}\n")
        
        f.write(f"\n\nGLOBAL TOP 50:\n")
        for rank, (sc, pg, label, text, plain) in enumerate(global_results[:50], 1):
            dec_ioc = calculate_ioc(plain) if plain else 0
            f.write(f"  #{rank}: Page {pg:02d} Score={sc:.1f} IoC={dec_ioc:.4f} [{label}]\n")
            f.write(f"       {text[:200]}\n")
    
    print(f"\nDetailed results saved to: {output_file}")


if __name__ == '__main__':
    main()
