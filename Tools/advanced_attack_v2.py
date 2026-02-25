#!/usr/bin/env python3
"""
Advanced Cipher Attacks on Liber Primus Unsolved Pages

Tests fundamentally different cipher types than the prime stream:
1. Alberti cipher (rotating disk) - systematic parameter search
2. Autokey cipher variants
3. Multi-layer ciphers (prime stream + Vigenere, etc.)
4. Running key from solved pages
5. Atbash + stream combinations
6. Interleaving/deinterleaving approaches
"""

import os
import sys
import math
from collections import Counter
from pathlib import Path
from itertools import product

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

# Expected English frequency for GP runes (from solved pages analysis)
ENGLISH_FREQ = {
    0: 0.02, 1: 0.03, 2: 0.07, 3: 0.08, 4: 0.06,
    5: 0.03, 6: 0.02, 7: 0.02, 8: 0.06, 9: 0.07,
    10: 0.07, 11: 0.005, 12: 0.01, 13: 0.02, 14: 0.001,
    15: 0.06, 16: 0.09, 17: 0.015, 18: 0.13, 19: 0.025,
    20: 0.04, 21: 0.03, 22: 0.01, 23: 0.04, 24: 0.08,
    25: 0.01, 26: 0.02, 27: 0.01, 28: 0.02,
}


def load_page_runes(page_num):
    """Load rune text from a page file. Returns (shifts, word_boundaries, raw_text)."""
    page_dir = Path(f"c:/Users/tyler/Repos/Cicada3301/LiberPrimus/pages/page_{page_num:02d}")
    rune_file = page_dir / "runes.txt"
    
    if not rune_file.exists():
        return None, None, None
    
    with open(rune_file, 'r', encoding='utf-8') as f:
        raw_text = f.read().strip()
    
    # Remove section markers
    for marker in ['&', '$', '%']:
        raw_text = raw_text.replace(marker, '')
    raw_text = raw_text.strip()
    
    shifts = []
    word_boundaries = []
    
    for ch in raw_text:
        if ch in RUNE_TO_SHIFT:
            shifts.append(RUNE_TO_SHIFT[ch])
        elif ch in SEPARATORS:
            if shifts and (not word_boundaries or word_boundaries[-1] != len(shifts)):
                word_boundaries.append(len(shifts))
    
    return shifts, word_boundaries, raw_text


def calculate_ioc(shifts):
    """Calculate Index of Coincidence normalized to 29 symbols."""
    if len(shifts) < 2:
        return 0
    n = len(shifts)
    freq = Counter(shifts)
    total = sum(count * (count - 1) for count in freq.values())
    return (total * 29) / (n * (n - 1))


def shifts_to_latin(shifts, word_boundaries=None):
    """Convert shifts to Latin text."""
    if word_boundaries is None:
        word_boundaries = []
    result = []
    wb_set = set(word_boundaries)
    for i, s in enumerate(shifts):
        if i in wb_set:
            result.append(' ')
        result.append(SHIFT_TO_LATIN.get(s, '?'))
    return ''.join(result)


def score_english(shifts, word_boundaries=None):
    """Score how English-like a decrypted text is."""
    if not shifts or len(shifts) < 5:
        return 0
    
    n = len(shifts)
    score = 0
    
    # IoC
    ioc = calculate_ioc(shifts)
    score += max(0, (ioc - 1.0) * 200)
    
    # Frequency correlation
    freq = Counter(shifts)
    total = sum(freq.values())
    chi_sq = 0
    for s in range(29):
        observed = freq.get(s, 0) / total
        expected = ENGLISH_FREQ.get(s, 0.01)
        chi_sq += (observed - expected) ** 2 / expected
    score += max(0, 100 - chi_sq * 10)
    
    # Common words
    latin = shifts_to_latin(shifts, word_boundaries)
    words = latin.split(' ')
    common_words = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL',
                    'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'HIS', 'HAS', 'HAD',
                    'THAT', 'WITH', 'HAVE', 'THIS', 'WILL', 'YOUR', 'FROM',
                    'THEY', 'BEEN', 'SAID', 'EACH', 'WHICH', 'THEIR',
                    'THERE', 'THEM', 'THEN', 'THAN', 'SOME', 'WHAT',
                    'WHEN', 'WERE', 'INTO', 'MORE', 'LIKE', 'ONLY',
                    'WE', 'AN', 'IN', 'IS', 'IT', 'OF', 'TO', 'IF', 'NO',
                    'DO', 'BE', 'AS', 'AT', 'OR', 'SO', 'BY', 'ON', 'HE',
                    'A', 'I', 'WHO', 'ITS', 'OWN', 'SET', 'MAN', 'CAN',
                    'BEING', 'THOSE', 'THESE', 'TRUTH', 'WISDOM',
                    'CONSCIOUSNESS', 'MIND', 'SOUL', 'LIGHT', 'DARK'}
    word_score = 0
    for w in words:
        wc = w.strip().upper()
        if wc in common_words:
            word_score += len(wc) * 5
    score += word_score / max(1, len(words)) * 50
    
    return score


def generate_primes(n):
    """Generate first n primes."""
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


# ==================== ALBERTI CIPHER ====================

def alberti_decrypt(cipher_shifts, raw_text, letter_rot, space_rot, clockwise=True):
    """
    Decrypt using Alberti cipher (rotating disk).
    
    The inner disk (cipher alphabet) rotates relative to the outer disk (plaintext alphabet).
    After each letter, the disk rotates by letter_rot positions.
    After each space/separator, the disk rotates by space_rot positions.
    """
    # Build inner disk starting at identity
    inner = list(range(29))  # inner[cipher_index] = plaintext_index
    
    plaintext = []
    rune_idx = 0
    
    for ch in raw_text:
        if ch in RUNE_TO_SHIFT:
            cipher_shift = RUNE_TO_SHIFT[ch]
            # Decrypt: find the plaintext shift for this cipher shift
            plain_shift = inner[cipher_shift]
            plaintext.append(plain_shift)
            rune_idx += 1
            
            # Rotate inner disk by letter_rot
            if clockwise:
                inner = inner[letter_rot:] + inner[:letter_rot]
            else:
                inner = inner[-letter_rot:] + inner[:-letter_rot] if letter_rot > 0 else inner
                
        elif ch in SEPARATORS:
            # Rotate inner disk by space_rot
            if space_rot > 0:
                if clockwise:
                    inner = inner[space_rot:] + inner[:space_rot]
                else:
                    inner = inner[-space_rot:] + inner[:-space_rot]
    
    return plaintext


def test_alberti_on_page(page_num):
    """Test Alberti cipher with various rotation parameters."""
    shifts, wb, raw_text = load_page_runes(page_num)
    if shifts is None or len(shifts) < 10:
        return []
    
    results = []
    
    # Test letter rotations 1-28, space rotations 0-28, both directions
    # But this is 28 * 29 * 2 = 1624 combos per page - too slow for all pages
    # Focus on promising values first
    for clockwise in [True, False]:
        for letter_rot in range(1, 29):
            for space_rot in [0, 1, letter_rot, 29 - letter_rot]:
                plain = alberti_decrypt(shifts, raw_text, letter_rot, space_rot, clockwise)
                sc = score_english(plain, wb)
                ioc = calculate_ioc(plain)
                
                if sc > 150 or ioc > 1.2:
                    direction = "CW" if clockwise else "CCW"
                    label = f"ALBERTI_L{letter_rot}_S{space_rot}_{direction}"
                    latin = shifts_to_latin(plain, wb)
                    results.append((sc, ioc, label, latin[:200], plain))
    
    results.sort(key=lambda x: x[0], reverse=True)
    return results[:10]


# ==================== AUTOKEY CIPHER ====================

def autokey_decrypt(cipher_shifts, primer, mode='sub'):
    """
    Autokey cipher: key stream starts with primer, then uses plaintext.
    
    mode='sub': plain = (cipher - key) % 29
    mode='beaufort': plain = (key - cipher) % 29
    mode='add': plain = (cipher + key) % 29 (then key is still plaintext)
    """
    key_stream = list(primer)
    plaintext = []
    
    for i, c in enumerate(cipher_shifts):
        if i < len(key_stream):
            k = key_stream[i]
        else:
            k = plaintext[i - len(primer)]
        
        if mode == 'sub':
            p = (c - k) % 29
        elif mode == 'beaufort':
            p = (k - c) % 29
        elif mode == 'add':
            p = (c + k) % 29
        else:
            p = c
        
        plaintext.append(p)
    
    return plaintext


def test_autokey_on_page(page_num):
    """Test autokey cipher with various primers."""
    shifts, wb, raw_text = load_page_runes(page_num)
    if shifts is None or len(shifts) < 10:
        return []
    
    results = []
    
    # Single-character primers (all 29 shifts)
    for primer_val in range(29):
        for mode in ['sub', 'beaufort', 'add']:
            plain = autokey_decrypt(shifts, [primer_val], mode)
            sc = score_english(plain, wb)
            ioc = calculate_ioc(plain)
            
            if sc > 120 or ioc > 1.2:
                label = f"AUTOKEY_{SHIFT_TO_LATIN[primer_val]}_{mode}"
                latin = shifts_to_latin(plain, wb)
                results.append((sc, ioc, label, latin[:200], plain))
    
    # Keyword primers
    primers = {
        'DEOR': [23, 18, 3, 4],  # D=23, E=18, O=3, R=4
        'DIVINITY': [23, 10, 7, 10, 9, 10, 16, 26],
        'CICADA': [5, 10, 5, 24, 23, 24],
        'PRIME': [13, 4, 10, 19, 18],
        'LIBER': [20, 10, 17, 18, 4],
        'PRIMUS': [13, 4, 10, 19, 1, 15],
        'TRUTH': [16, 4, 1, 16, 8],
        'SHADOW': [15, 8, 24, 23, 3, 7],
        'WISDOM': [7, 10, 15, 23, 3, 19],
        'FIRFUMFERENFE': [0, 10, 4, 0, 1, 19, 0, 18, 4, 18, 9, 0, 18],
        'WELCOME': [7, 18, 20, 5, 3, 19, 18],
        'INSTAR': [10, 9, 15, 16, 24, 4],
        'PARABLE': [13, 24, 4, 24, 17, 20, 18],
        'AN_END': [24, 9, 18, 9, 23],
        'CONSUMPTION': [5, 3, 9, 15, 1, 19, 13, 16, 10, 3, 9],
    }
    
    for kw_name, primer in primers.items():
        for mode in ['sub', 'beaufort', 'add']:
            plain = autokey_decrypt(shifts, primer, mode)
            sc = score_english(plain, wb)
            ioc = calculate_ioc(plain)
            
            if sc > 120 or ioc > 1.2:
                label = f"AUTOKEY_{kw_name}_{mode}"
                latin = shifts_to_latin(plain, wb)
                results.append((sc, ioc, label, latin[:200], plain))
    
    results.sort(key=lambda x: x[0], reverse=True)
    return results[:10]


# ==================== MULTI-LAYER CIPHERS ====================

def test_multilayer_on_page(page_num):
    """Test multi-layer cipher combinations."""
    shifts, wb, raw_text = load_page_runes(page_num)
    if shifts is None or len(shifts) < 10:
        return []
    
    n = len(shifts)
    results = []
    primes = generate_primes(n + 100)
    
    # Layer 1: Caesar + Prime Stream
    for caesar_shift in range(29):
        caesar_result = [(s + caesar_shift) % 29 for s in shifts]
        
        # Then prime stream with totient
        totient_stream = [(primes[i] - 1) % 29 for i in range(n)]
        plain = [(caesar_result[i] - totient_stream[i]) % 29 for i in range(n)]
        sc = score_english(plain, wb)
        ioc = calculate_ioc(plain)
        
        if sc > 150 or ioc > 1.3:
            label = f"CAESAR{caesar_shift}+PRIMETOT_sub"
            latin = shifts_to_latin(plain, wb)
            results.append((sc, ioc, label, latin[:200], plain))
    
    # Layer 1: Atbash + Prime Stream
    atbash = [(28 - s) % 29 for s in shifts]
    for offset in range(29):
        stream = [(primes[i] + offset) % 29 for i in range(n)]
        plain = [(atbash[i] - stream[i]) % 29 for i in range(n)]
        sc = score_english(plain, wb)
        ioc = calculate_ioc(plain)
        
        if sc > 150 or ioc > 1.3:
            label = f"ATBASH+PRIME_off{offset}"
            latin = shifts_to_latin(plain, wb)
            results.append((sc, ioc, label, latin[:200], plain))
    
    # Layer 1: Vigenere(DEOR) + Prime Stream
    deor_key = [23, 18, 3, 4]  # D, E, O, R GP shifts
    deor_decrypted = [(shifts[i] - deor_key[i % 4]) % 29 for i in range(n)]
    for offset in range(29):
        stream = [(primes[i] + offset) % 29 for i in range(n)]
        plain = [(deor_decrypted[i] - stream[i]) % 29 for i in range(n)]
        sc = score_english(plain, wb)
        ioc = calculate_ioc(plain)
        
        if sc > 150 or ioc > 1.3:
            label = f"VIGD_DEOR+PRIME_off{offset}"
            latin = shifts_to_latin(plain, wb)
            results.append((sc, ioc, label, latin[:200], plain))
    
    # Layer 1: Beaufort(DEOR) + Prime Stream  
    deor_beau = [(deor_key[i % 4] - shifts[i]) % 29 for i in range(n)]
    for offset in range(29):
        stream = [(primes[i] + offset) % 29 for i in range(n)]
        plain = [(deor_beau[i] - stream[i]) % 29 for i in range(n)]
        sc = score_english(plain, wb)
        ioc = calculate_ioc(plain)
        
        if sc > 150 or ioc > 1.3:
            label = f"BEAU_DEOR+PRIME_off{offset}"
            latin = shifts_to_latin(plain, wb)
            results.append((sc, ioc, label, latin[:200], plain))
    
    # Layer 1: Prime Stream + Vigenere(DEOR)
    for offset in range(29):
        stream = [(primes[i] + offset) % 29 for i in range(n)]
        after_stream = [(shifts[i] - stream[i]) % 29 for i in range(n)]
        plain = [(after_stream[i] - deor_key[i % 4]) % 29 for i in range(n)]
        sc = score_english(plain, wb)
        ioc = calculate_ioc(plain)
        
        if sc > 150 or ioc > 1.3:
            label = f"PRIME_off{offset}+VIGD_DEOR"
            latin = shifts_to_latin(plain, wb)
            results.append((sc, ioc, label, latin[:200], plain))
    
    # GP-value-based stream: use the rune's own GP prime as part of the key
    # Each rune at position i: key = GP_prime_of_rune_at_i
    gp_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109]
    for offset in range(29):
        plain = [(shifts[i] - (gp_primes[shifts[i]] + offset)) % 29 for i in range(n)]
        sc = score_english(plain, wb)
        ioc = calculate_ioc(plain)
        
        if sc > 120 or ioc > 1.2:
            label = f"SELFGP_off{offset}"
            latin = shifts_to_latin(plain, wb)
            results.append((sc, ioc, label, latin[:200], plain))
    
    # Cumulative sum stream: key[i] = sum of first i primes
    cumsum = []
    s = 0
    for i in range(n):
        s += primes[i]
        cumsum.append(s % 29)
    
    for offset in range(29):
        stream = [(c + offset) % 29 for c in cumsum]
        plain = [(shifts[i] - stream[i]) % 29 for i in range(n)]
        sc = score_english(plain, wb)
        ioc = calculate_ioc(plain)
        
        if sc > 120 or ioc > 1.2:
            label = f"CUMPRIMESUM_off{offset}"
            latin = shifts_to_latin(plain, wb)
            results.append((sc, ioc, label, latin[:200], plain))
    
    # Product-based stream: key[i] = product of i-th prime's digits
    def digit_product(n):
        p = 1
        for d in str(n):
            p *= int(d) if d != '0' else 1
        return p
    
    for offset in range(29):
        stream = [(digit_product(primes[i]) + offset) % 29 for i in range(n)]
        plain = [(shifts[i] - stream[i]) % 29 for i in range(n)]
        sc = score_english(plain, wb)
        ioc = calculate_ioc(plain)
        
        if sc > 120 or ioc > 1.2:
            label = f"DIGPROD_off{offset}"
            latin = shifts_to_latin(plain, wb)
            results.append((sc, ioc, label, latin[:200], plain))
    
    results.sort(key=lambda x: x[0], reverse=True)
    return results[:10]


# ==================== RUNNING KEY ====================

def get_solved_plaintext():
    """Get plaintext from known solved pages to use as running key."""
    # P57 plaintext (PARABLE)
    p57 = "PARABLE LIKE THE INSTAR TUNNELING TO THE SURFACE WE MUST SHED OUR OWN CIRCUMFERENCES FIND THE DIVINITY WITHIN AND EMERGE"
    
    # Convert to shifts
    latin_to_shift = {}
    for s, l in SHIFT_TO_LATIN.items():
        latin_to_shift[l] = s
    
    solved_shifts = []
    i = 0
    text = p57.replace(' ', '-')
    while i < len(text):
        if text[i] == '-':
            i += 1
            continue
        # Try 2-char digraphs first
        found = False
        if i + 1 < len(text):
            digraph = text[i:i+2]
            if digraph in latin_to_shift:
                solved_shifts.append(latin_to_shift[digraph])
                i += 2
                found = True
        if not found:
            ch = text[i]
            if ch in latin_to_shift:
                solved_shifts.append(latin_to_shift[ch])
            i += 1
    
    return solved_shifts


def test_running_key_on_page(page_num):
    """Test running key cipher using plaintext from solved pages."""
    shifts, wb, raw_text = load_page_runes(page_num)
    if shifts is None or len(shifts) < 10:
        return []
    
    n = len(shifts)
    results = []
    
    running_key = get_solved_plaintext()
    if not running_key or len(running_key) < 10:
        return []
    
    # Extend running key by repeating
    extended_key = (running_key * ((n // len(running_key)) + 2))[:n]
    
    for mode_name, mode_fn in [('SUB', lambda c, k: (c - k) % 29),
                                ('BEAU', lambda c, k: (k - c) % 29),
                                ('ADD', lambda c, k: (c + k) % 29)]:
        plain = [mode_fn(shifts[i], extended_key[i]) for i in range(n)]
        sc = score_english(plain, wb)
        ioc = calculate_ioc(plain)
        
        if sc > 100 or ioc > 1.2:
            label = f"RUNKEY_P57_{mode_name}"
            latin = shifts_to_latin(plain, wb)
            results.append((sc, ioc, label, latin[:200], plain))
    
    # Try using the running key from different starting positions
    for start in range(0, min(50, len(running_key))):
        offset_key = (running_key[start:] + running_key[:start])
        extended_key = (offset_key * ((n // len(offset_key)) + 2))[:n]
        
        plain = [(shifts[i] - extended_key[i]) % 29 for i in range(n)]
        sc = score_english(plain, wb)
        ioc = calculate_ioc(plain)
        
        if sc > 120 or ioc > 1.2:
            label = f"RUNKEY_P57_start{start}"
            latin = shifts_to_latin(plain, wb)
            results.append((sc, ioc, label, latin[:200], plain))
    
    results.sort(key=lambda x: x[0], reverse=True)
    return results[:5]


# ==================== INTERLEAVING ATTACKS ====================

def test_deinterleave_on_page(page_num):
    """Test deinterleaving: maybe runes from different streams are interleaved."""
    shifts, wb, raw_text = load_page_runes(page_num)
    if shifts is None or len(shifts) < 20:
        return []
    
    n = len(shifts)
    results = []
    
    # Try extracting every 2nd, 3rd, ... rune
    for stride in range(2, 8):
        for offset in range(stride):
            subset = shifts[offset::stride]
            if len(subset) < 10:
                continue
            ioc = calculate_ioc(subset)
            sc = score_english(subset)
            
            if ioc > 1.2 or sc > 120:
                label = f"DEINTERLEAVE_stride{stride}_off{offset}"
                latin = shifts_to_latin(subset)
                results.append((sc, ioc, label, latin[:200], subset))
    
    # Try reading columns of different widths (transposition detection)
    for width in [7, 11, 13, 17, 19, 23, 29, 31]:
        if width >= n:
            continue
        # Read by columns
        nrows = (n + width - 1) // width
        column_read = []
        for col in range(width):
            for row in range(nrows):
                idx = row * width + col
                if idx < n:
                    column_read.append(shifts[idx])
        
        ioc = calculate_ioc(column_read)
        sc = score_english(column_read)
        
        if ioc > 1.2 or sc > 120:
            label = f"COLREAD_w{width}"
            latin = shifts_to_latin(column_read)
            results.append((sc, ioc, label, latin[:200], column_read))
    
    results.sort(key=lambda x: x[0], reverse=True)
    return results[:5]


# ==================== MAIN ====================

def main():
    print("=" * 80)
    print("ADVANCED CIPHER ATTACKS ON LIBER PRIMUS")
    print("=" * 80)
    
    # Test pages - focus on a diverse subset first for speed
    # Include small, medium, and large pages
    test_pages = [21, 22, 23, 24, 26, 27, 28, 29, 30, 31, 33, 34, 35, 36, 37, 38, 39,
                  41, 43, 45, 46, 47, 48, 49, 51, 52, 53, 54]
    
    all_alberti = {}
    all_autokey = {}
    all_multilayer = {}
    all_deinterleave = {}
    
    print(f"\n--- Testing {len(test_pages)} pages ---\n")
    
    for page_num in test_pages:
        shifts, wb, raw = load_page_runes(page_num)
        if shifts is None or len(shifts) < 10:
            continue
        
        print(f"Page {page_num:02d} ({len(shifts)} runes):")
        
        # Alberti
        alberti_results = test_alberti_on_page(page_num)
        if alberti_results:
            all_alberti[page_num] = alberti_results
            best = alberti_results[0]
            print(f"  Alberti:    Best Score={best[0]:.1f} IoC={best[1]:.4f} [{best[2]}]")
        else:
            print(f"  Alberti:    No results above threshold")
        
        # Autokey
        autokey_results = test_autokey_on_page(page_num)
        if autokey_results:
            all_autokey[page_num] = autokey_results
            best = autokey_results[0]
            print(f"  Autokey:    Best Score={best[0]:.1f} IoC={best[1]:.4f} [{best[2]}]")
        else:
            print(f"  Autokey:    No results above threshold")
        
        # Multi-layer
        ml_results = test_multilayer_on_page(page_num)
        if ml_results:
            all_multilayer[page_num] = ml_results
            best = ml_results[0]
            print(f"  MultiLayer: Best Score={best[0]:.1f} IoC={best[1]:.4f} [{best[2]}]")
        else:
            print(f"  MultiLayer: No results above threshold")
        
        # Deinterleave
        di_results = test_deinterleave_on_page(page_num)
        if di_results:
            all_deinterleave[page_num] = di_results
            best = di_results[0]
            print(f"  Deinterl:   Best Score={best[0]:.1f} IoC={best[1]:.4f} [{best[2]}]")
        else:
            print(f"  Deinterl:   No results above threshold")
    
    # Collect all results globally
    print("\n" + "=" * 80)
    print("GLOBAL TOP RESULTS")
    print("=" * 80)
    
    global_results = []
    for attack_name, results_dict in [("ALBERTI", all_alberti), ("AUTOKEY", all_autokey), 
                                       ("MULTILAYER", all_multilayer), ("DEINTERLEAVE", all_deinterleave)]:
        for pg, results in results_dict.items():
            for sc, ioc, label, text, plain in results:
                global_results.append((sc, ioc, pg, label, text, plain))
    
    global_results.sort(key=lambda x: x[0], reverse=True)
    
    print("\nTop 30 by score:")
    for rank, (sc, ioc, pg, label, text, plain) in enumerate(global_results[:30], 1):
        print(f"  #{rank}: Page {pg:02d} Score={sc:.1f} IoC={ioc:.4f} [{label}]")
        print(f"       {text[:120]}")
    
    # Check for IoC breakthroughs 
    print("\n\nResults with IoC > 1.3:")
    breakthroughs = [(sc, ioc, pg, label, text, plain) for sc, ioc, pg, label, text, plain in global_results if ioc > 1.3]
    if breakthroughs:
        for sc, ioc, pg, label, text, plain in breakthroughs:
            print(f"  Page {pg:02d}: Score={sc:.1f} IoC={ioc:.4f} [{label}]")
            print(f"  Text: {text[:200]}")
    else:
        print("  None found.")
    
    # Save results
    output_file = "c:/Users/tyler/Repos/Cicada3301/results_advanced_attack_v2.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("ADVANCED CIPHER ATTACK RESULTS V2\n")
        f.write("=" * 80 + "\n\n")
        
        for rank, (sc, ioc, pg, label, text, plain) in enumerate(global_results[:100], 1):
            f.write(f"#{rank}: Page {pg:02d} Score={sc:.1f} IoC={ioc:.4f} [{label}]\n")
            f.write(f"   {text[:200]}\n\n")
    
    print(f"\nResults saved to: {output_file}")


if __name__ == '__main__':
    main()
