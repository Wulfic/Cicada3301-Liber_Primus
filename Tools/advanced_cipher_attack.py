#!/usr/bin/env python3
"""
Advanced Cipher Attack for Liber Primus Pages 21-54
====================================================
Tries methods NOT yet systematically tested:
1. phi(prime) totient cipher (worked on pages 55, 73)
2. Alberti rotating disk cipher
3. Vigstream with various streams (primes, fibonacci)
4. Autokey cipher with various seeds
5. Running key with solved page texts
6. Combined: keyword + phi(prime) second layer
7. Combined: Caesar + vigstream second layer
"""

import os
import sys
import math
from collections import Counter

# ============================================================
# Gematria Primus 
# ============================================================

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

COMMON_WORDS = [
    'THE', 'AND', 'THAT', 'HAVE', 'FOR', 'NOT', 'WITH', 'YOU', 'THIS', 'BUT',
    'HIS', 'FROM', 'THEY', 'BEEN', 'SAID', 'EACH', 'WHICH', 'THEIR',
    'WILL', 'OTHER', 'ABOUT', 'MANY', 'THEN', 'THEM', 'THESE', 'SOME', 'HER',
    'WOULD', 'MAKE', 'LIKE', 'TIME', 'JUST', 'KNOW', 'TAKE', 'PEOPLE', 'INTO',
    'YEAR', 'YOUR', 'GOOD', 'COULD', 'THAN', 'LOOK', 'ONLY', 'COME', 'MADE',
    'AFTER', 'ALSO', 'DID', 'BEFORE', 'MUST', 'THROUGH', 'SHOULD', 'WHERE',
    'MUCH', 'EVERY', 'WELL', 'WHAT', 'EVEN', 'MOST', 'WHO', 'ARE', 'WAS',
    'ONE', 'ALL', 'HAD', 'HAS', 'WHEN', 'CAN', 'THERE',
    'DIVINITY', 'TRUTH', 'WISDOM', 'SACRED', 'PRIMES', 'TOTIENT', 'PILGRIM',
    'CIRCUMFERENCE', 'CONSUMPTION', 'BELIEVE', 'NOTHING', 'EVERYTHING',
    'SPIRIT', 'SOUL', 'DEATH', 'FAITH', 'PATH', 'KOAN', 'MASTER', 'VOID',
    'SHADOWS', 'CABAL', 'WARNING', 'LOSS', 'BEING', 'THINGS', 'WORLD',
    'WITHIN', 'DUTY', 'SEEK', 'FIND', 'PAGE', 'HASH', 'DEEP', 'WEB',
    'ENCRYPT', 'CIPHER', 'KEY', 'INSTAR', 'EMERGE',
]

TRIGRAMS = ['THE', 'AND', 'ING', 'ENT', 'ION', 'HER', 'FOR', 'THA', 'NTH', 'INT',
            'ERE', 'TIO', 'VER', 'EST', 'ALL', 'ATE', 'OUS', 'ITH', 'HIS', 'TER']


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


def calculate_ioc(indices):
    freq = [0] * 29
    for idx in indices:
        freq[idx] += 1
    n = len(indices)
    if n <= 1:
        return 0
    ioc = sum(f * (f - 1) for f in freq) / (n * (n - 1))
    return ioc * 29


def score_english(text):
    text_upper = text.upper()
    score = 0
    for word in COMMON_WORDS:
        count = text_upper.count(word)
        score += count * len(word) * 2
    for tri in TRIGRAMS:
        score += text_upper.count(tri) * 3
    for ch in text_upper:
        if ch in 'XJQZ':
            score -= 1
    return score


def sieve_primes(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = False
    return [i for i in range(2, limit + 1) if is_prime[i]]


def euler_totient(n):
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


# ============================================================
# CIPHER METHODS
# ============================================================

def phi_prime_decrypt(indices, operation='sub', start_prime_idx=0):
    """
    phi(prime) totient cipher - worked on pages 55, 73.
    P[i] = (C[i] - phi(prime[i])) mod 29
    """
    primes = sieve_primes(max(len(indices) * 20, 10000))
    result = []
    prime_idx = start_prime_idx
    for c in indices:
        if prime_idx >= len(primes):
            break
        shift = euler_totient(primes[prime_idx]) % 29
        if operation == 'sub':
            result.append((c - shift) % 29)
        else:
            result.append((c + shift) % 29)
        prime_idx += 1
    return result


def phi_prime_decrypt_with_f_skip(indices, operation='sub'):
    """
    phi(prime) with the F-skip rule: if result is F (index 0),
    don't advance the prime counter.
    """
    primes = sieve_primes(max(len(indices) * 20, 10000))
    result = []
    prime_idx = 0
    for c in indices:
        if prime_idx >= len(primes):
            break
        shift = euler_totient(primes[prime_idx]) % 29
        if operation == 'sub':
            plain = (c - shift) % 29
        else:
            plain = (c + shift) % 29
        result.append(plain)
        if plain != 0:  # Don't advance for F
            prime_idx += 1
    return result


def prime_stream_decrypt(indices, operation='sub'):
    """
    Vigstream with prime values (not totients).
    P[i] = (C[i] - prime[i]) mod 29
    """
    primes = sieve_primes(max(len(indices) * 20, 10000))
    result = []
    for i, c in enumerate(indices):
        if i >= len(primes):
            break
        shift = primes[i] % 29
        if operation == 'sub':
            result.append((c - shift) % 29)
        else:
            result.append((c + shift) % 29)
    return result


def fibonacci_stream_decrypt(indices, operation='sub'):
    """Vigstream with Fibonacci numbers mod 29."""
    fibs = [0, 1]
    while len(fibs) < len(indices) + 10:
        fibs.append((fibs[-1] + fibs[-2]) % 29)
    
    result = []
    for i, c in enumerate(indices):
        shift = fibs[i] % 29
        if operation == 'sub':
            result.append((c - shift) % 29)
        else:
            result.append((c + shift) % 29)
    return result


def lucas_stream_decrypt(indices, operation='sub'):
    """Vigstream with Lucas numbers mod 29."""
    lucas = [2, 1]
    while len(lucas) < len(indices) + 10:
        lucas.append((lucas[-1] + lucas[-2]) % 29)
    
    result = []
    for i, c in enumerate(indices):
        shift = lucas[i] % 29
        if operation == 'sub':
            result.append((c - shift) % 29)
        else:
            result.append((c + shift) % 29)
    return result


def autokey_decrypt(indices, seed_key, operation='sub'):
    """
    Autokey cipher: key extends with plaintext.
    """
    result = []
    key = list(seed_key)
    for i, c in enumerate(indices):
        k = key[i] if i < len(key) else result[i - len(seed_key)]
        if operation == 'sub':
            p = (c - k) % 29
        elif operation == 'add':
            p = (c + k) % 29
        else:  # beaufort
            p = (k - c) % 29
        result.append(p)
    return result


def autokey_decrypt_ciphertext(indices, seed_key, operation='sub'):
    """
    Autokey cipher using CIPHERTEXT for key extension (not plaintext).
    """
    result = []
    key = list(seed_key)
    for i, c in enumerate(indices):
        k = key[i] if i < len(key) else indices[i - len(seed_key)]
        if operation == 'sub':
            p = (c - k) % 29
        elif operation == 'add':
            p = (c + k) % 29
        else:  # beaufort
            p = (k - c) % 29
        result.append(p)
    return result


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


def alberti_decrypt(indices, letter_rot=1, space_rot=0, clockwise=True):
    """
    Alberti cipher / dual disk cipher.
    The outer disk rotates after each letter by letter_rot positions.
    """
    # Build the shifting alphabet
    alphabet = list(range(29))
    offset = 0
    direction = 1 if clockwise else -1
    
    result = []
    for c in indices:
        # Decrypt: find position on shifted outer disk, output inner disk position
        shifted_pos = (c - offset) % 29
        result.append(shifted_pos)
        # Rotate after each letter
        offset = (offset + letter_rot * direction) % 29
    
    return result


def alberti_decrypt_full(indices, letter_rot, space_rot=0, clockwise=True, word_boundaries=None):
    """
    Full Alberti with word-boundary-aware rotation.
    word_boundaries: set of positions where a word boundary occurs (before this position).
    """
    offset = 0
    direction = 1 if clockwise else -1
    result = []
    
    for i, c in enumerate(indices):
        if word_boundaries and i in word_boundaries:
            offset = (offset + space_rot * direction) % 29
        shifted_pos = (c - offset) % 29
        result.append(shifted_pos)
        offset = (offset + letter_rot * direction) % 29
    
    return result


def progressive_key_decrypt(indices, initial_shift=0, step=1, operation='sub'):
    """
    Progressive shift: shift increases by step each character.
    P[i] = (C[i] - (initial + i*step)) mod 29
    """
    result = []
    for i, c in enumerate(indices):
        shift = (initial_shift + i * step) % 29
        if operation == 'sub':
            result.append((c - shift) % 29)
        else:
            result.append((c + shift) % 29)
    return result


def triangular_stream_decrypt(indices, operation='sub'):
    """Vigstream with triangular numbers mod 29."""
    result = []
    for i, c in enumerate(indices):
        tri = ((i + 1) * (i + 2) // 2) % 29
        if operation == 'sub':
            result.append((c - tri) % 29)
        else:
            result.append((c + tri) % 29)
    return result


def prime_gap_stream_decrypt(indices, operation='sub'):
    """Vigstream with prime gaps (differences between consecutive primes)."""
    primes = sieve_primes(max(len(indices) * 20, 10000))
    gaps = [primes[i+1] - primes[i] for i in range(len(primes) - 1)]
    
    result = []
    for i, c in enumerate(indices):
        if i >= len(gaps):
            break
        shift = gaps[i] % 29
        if operation == 'sub':
            result.append((c - shift) % 29)
        else:
            result.append((c + shift) % 29)
    return result


def totient_stream_decrypt(indices, operation='sub'):
    """Vigstream with totient of sequential integers (not primes)."""
    result = []
    for i, c in enumerate(indices):
        n = i + 2  # Start from 2
        shift = euler_totient(n) % 29
        if operation == 'sub':
            result.append((c - shift) % 29)
        else:
            result.append((c + shift) % 29)
    return result


# ============================================================
# COMBINED ATTACKS
# ============================================================

def attack_page_all_methods(page_num, pre_decrypted=None, pre_key_info="raw"):
    """Try all cipher methods on a page."""
    if pre_decrypted is None:
        indices, raw = load_page_runes(page_num)
    else:
        indices = pre_decrypted
    
    if not indices:
        return []
    
    n = len(indices)
    base_text = indices_to_text(indices)
    base_score = score_english(base_text)
    base_ioc = calculate_ioc(indices)
    
    results = []
    
    # ---- Stream ciphers (direct on raw runes) ----
    
    # 1. phi(prime) totient cipher
    for op in ['sub', 'add']:
        r = phi_prime_decrypt(indices, op)
        text = indices_to_text(r)
        s = score_english(text)
        ioc = calculate_ioc(r)
        results.append((f'PHI_PRIME_{op.upper()}', s, ioc, text))
    
    # 2. phi(prime) with F-skip
    for op in ['sub', 'add']:
        r = phi_prime_decrypt_with_f_skip(indices, op)
        text = indices_to_text(r)
        s = score_english(text)
        ioc = calculate_ioc(r)
        results.append((f'PHI_PRIME_FSKIP_{op.upper()}', s, ioc, text))
    
    # 3. phi(prime) with offset starting positions
    for start in [1, 2, 5, 10, 20, 50, 100]:
        r = phi_prime_decrypt(indices, 'sub', start_prime_idx=start)
        text = indices_to_text(r)
        s = score_english(text)
        ioc = calculate_ioc(r)
        results.append((f'PHI_PRIME_SUB_START{start}', s, ioc, text))
    
    # 4. Prime stream (raw primes, not totients)
    for op in ['sub', 'add']:
        r = prime_stream_decrypt(indices, op)
        text = indices_to_text(r)
        s = score_english(text)
        ioc = calculate_ioc(r)
        results.append((f'PRIME_STREAM_{op.upper()}', s, ioc, text))
    
    # 5. Fibonacci stream
    for op in ['sub', 'add']:
        r = fibonacci_stream_decrypt(indices, op)
        text = indices_to_text(r)
        s = score_english(text)
        ioc = calculate_ioc(r)
        results.append((f'FIBONACCI_{op.upper()}', s, ioc, text))
    
    # 6. Lucas stream
    for op in ['sub', 'add']:
        r = lucas_stream_decrypt(indices, op)
        text = indices_to_text(r)
        s = score_english(text)
        ioc = calculate_ioc(r)
        results.append((f'LUCAS_{op.upper()}', s, ioc, text))
    
    # 7. Triangular numbers
    for op in ['sub', 'add']:
        r = triangular_stream_decrypt(indices, op)
        text = indices_to_text(r)
        s = score_english(text)
        ioc = calculate_ioc(r)
        results.append((f'TRIANGULAR_{op.upper()}', s, ioc, text))
    
    # 8. Prime gaps
    for op in ['sub', 'add']:
        r = prime_gap_stream_decrypt(indices, op)
        text = indices_to_text(r)
        s = score_english(text)
        ioc = calculate_ioc(r)
        results.append((f'PRIME_GAP_{op.upper()}', s, ioc, text))
    
    # 9. Totient of sequential integers
    for op in ['sub', 'add']:
        r = totient_stream_decrypt(indices, op)
        text = indices_to_text(r)
        s = score_english(text)
        ioc = calculate_ioc(r)
        results.append((f'TOTIENT_SEQ_{op.upper()}', s, ioc, text))
    
    # 10. Alberti cipher (progressive rotation)
    for letter_rot in range(1, 29):
        for cw in [True, False]:
            r = alberti_decrypt(indices, letter_rot, clockwise=cw)
            text = indices_to_text(r)
            s = score_english(text)
            ioc = calculate_ioc(r)
            direction = 'CW' if cw else 'CCW'
            results.append((f'ALBERTI_ROT{letter_rot}_{direction}', s, ioc, text))
    
    # 11. Progressive shift
    for step in range(1, 29):
        for init in [0]:
            for op in ['sub']:
                r = progressive_key_decrypt(indices, init, step, op)
                text = indices_to_text(r)
                s = score_english(text)
                ioc = calculate_ioc(r)
                results.append((f'PROGRESSIVE_STEP{step}', s, ioc, text))
    
    # 12. Autokey with keyword seeds
    keywords = ['DIVINITY', 'CABAL', 'PRIMES', 'TOTIENT', 'SHADOWS', 'DEOR',
                'VOID', 'SACRED', 'WISDOM', 'TRUTH', 'AETHEREAL', 'MOURNFUL',
                'OBSCURA', 'CICADA', 'PILGRIM', 'KOAN', 'INSTAR', 'ENCRYPT']
    for kw in keywords:
        key = word_to_indices(kw)
        for op in ['sub', 'add', 'beaufort']:
            r = autokey_decrypt(indices, key, op)
            text = indices_to_text(r)
            s = score_english(text)
            ioc = calculate_ioc(r)
            results.append((f'AUTOKEY_{kw}_{op.upper()}', s, ioc, text))
    
    # 13. Autokey with ciphertext extension
    for kw in keywords[:8]:  # Top keywords only
        key = word_to_indices(kw)
        for op in ['sub', 'add']:
            r = autokey_decrypt_ciphertext(indices, key, op)
            text = indices_to_text(r)
            s = score_english(text)
            ioc = calculate_ioc(r)
            results.append((f'AUTOKEY_CT_{kw}_{op.upper()}', s, ioc, text))
    
    # Sort by score
    results.sort(key=lambda x: x[1], reverse=True)
    
    return results


def main():
    print("=" * 80)
    print("ADVANCED CIPHER ATTACK - Liber Primus Pages 21-54")
    print("Methods: phi(prime), Alberti, vigstream, autokey, progressive")
    print("=" * 80)
    
    all_best = []
    
    # ---- PHASE 1: Direct attack on raw runes (no pre-decryption) ----
    print("\n\nPHASE 1: DIRECT CIPHER ATTACK ON RAW RUNES")
    print("=" * 80)
    
    # Test on priority pages
    test_pages = [21, 22, 23, 24, 25, 28, 29, 30, 32, 40, 44, 50]
    
    for page_num in test_pages:
        indices, raw = load_page_runes(page_num)
        if not indices:
            continue
        
        base_text = indices_to_text(indices)
        base_score = score_english(base_text)
        base_ioc = calculate_ioc(indices)
        
        results = attack_page_all_methods(page_num)
        
        print(f"\n--- PAGE {page_num} (len={len(indices)}, base_score={base_score}, base_ioc={base_ioc:.4f}) ---")
        for method, score, ioc, text in results[:5]:
            improvement = score - base_score
            if improvement > 0:
                print(f"  {method:45s} Score:{score:5.0f} IoC:{ioc:.4f} d{improvement:+5.0f}")
                if improvement > 30:
                    print(f"    {text[:120]}")
        
        if results:
            best = results[0]
            all_best.append((page_num, best[0], best[1], best[2], best[3]))
    
    # ---- PHASE 2: Keyword decrypted + second layer ----
    print("\n\nPHASE 2: KEYWORD DECRYPTION + SECOND CIPHER LAYER")
    print("=" * 80)
    
    page_keys_21_30 = {
        21: ('CABAL', 'BEAUFORT'),
        22: ('DIVINITY', 'BEAUFORT'),
        23: ('ENCRYPTION', 'ADD'),
        24: ('OBSCURA', 'BEAUFORT'),
        25: ('CABAL', 'BEAUFORT'),
        28: ('DEOR', 'SUB'),
        29: ('TOTIENT', 'BEAUFORT'),
    }
    
    for page_num, (keyword, mode) in page_keys_21_30.items():
        indices, raw = load_page_runes(page_num)
        if not indices:
            continue
        
        key = word_to_indices(keyword)
        first_decrypted = vigenere_decrypt(indices, key, mode)
        base_text = indices_to_text(first_decrypted)
        base_score = score_english(base_text)
        base_ioc = calculate_ioc(first_decrypted)
        
        # Now try second layer ciphers on the first-decrypted text
        results = attack_page_all_methods(page_num, first_decrypted, f"{keyword}/{mode}")
        
        print(f"\n--- PAGE {page_num} (after {keyword}/{mode}, base_score={base_score}, ioc={base_ioc:.4f}) ---")
        for method, score, ioc, text in results[:5]:
            improvement = score - base_score
            if improvement > 0:
                print(f"  {method:45s} Score:{score:5.0f} IoC:{ioc:.4f} d{improvement:+5.0f}")
                if improvement > 30:
                    print(f"    {text[:120]}")
    
    # ---- PHASE 3: Caesar + second layer ----
    print("\n\nPHASE 3: CAESAR + SECOND CIPHER LAYER")
    print("=" * 80)
    
    caesar_shifts = {32: 11, 44: 5, 50: 6, 40: 0}
    
    for page_num, shift in caesar_shifts.items():
        indices, raw = load_page_runes(page_num)
        if not indices:
            continue
        
        first_decrypted = caesar_decrypt(indices, shift)
        base_text = indices_to_text(first_decrypted)
        base_score = score_english(base_text)
        base_ioc = calculate_ioc(first_decrypted)
        
        # Now try second layer
        results = attack_page_all_methods(page_num, first_decrypted, f"Caesar_{shift}")
        
        print(f"\n--- PAGE {page_num} (after Caesar {shift}, base_score={base_score}, ioc={base_ioc:.4f}) ---")
        for method, score, ioc, text in results[:5]:
            improvement = score - base_score
            if improvement > 0:
                print(f"  {method:45s} Score:{score:5.0f} IoC:{ioc:.4f} d{improvement:+5.0f}")
                if improvement > 30:
                    print(f"    {text[:120]}")
    
    # ---- SUMMARY ----
    print("\n\n" + "=" * 80)
    print("OVERALL BEST RESULTS")
    print("=" * 80)
    all_best.sort(key=lambda x: x[2], reverse=True)
    for page_num, method, score, ioc, text in all_best[:20]:
        print(f"  Page {page_num:2d}: {method:45s} Score:{score:5.0f} IoC:{ioc:.4f}")
        print(f"          {text[:100]}")


if __name__ == '__main__':
    main()
