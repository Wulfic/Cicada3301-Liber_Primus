#!/usr/bin/env python3
"""
Advanced Transposition Attack for Liber Primus Pages 21-54
==========================================================
Targets pages where substitution cipher is solved (correct letter frequency)
but text remains scrambled (wrong order).

New methods NOT previously tested:
1. Prime-index extraction (read chars at prime positions)
2. Fibonacci-index extraction 
3. Totient-based permutation (φ(n) mod len)
4. Columnar transposition with keyword-derived column orders
5. Route cipher (spiral reading)
6. Scytale cipher
7. Turning grille simulation
8. Word-level rearrangement using rune word boundaries
9. Block-based permutations
10. Mathematical sequence-based reading orders
"""

import os
import sys
import math
import itertools
from collections import Counter

# ============================================================
# Gematria Primus Mapping
# ============================================================

RUNE_TO_INDEX = {
    'ᚠ': 0, 'ᚢ': 1, 'ᚦ': 2, 'ᚩ': 3, 'ᚱ': 4, 'ᚳ': 5, 'ᚷ': 6, 'ᚹ': 7,
    'ᚻ': 8, 'ᚾ': 9, 'ᛁ': 10, 'ᛂ': 11, 'ᛇ': 12, 'ᛈ': 13, 'ᛉ': 14,
    'ᛋ': 15, 'ᛏ': 16, 'ᛒ': 17, 'ᛖ': 18, 'ᛗ': 19, 'ᛚ': 20, 'ᛝ': 21,
    'ᛟ': 22, 'ᛞ': 23, 'ᚪ': 24, 'ᚫ': 25, 'ᚣ': 26, 'ᛡ': 27, 'ᛠ': 28,
    'ᛄ': 11  # Alternate J rune
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

# Common English words for scoring
COMMON_WORDS = [
    'THE', 'AND', 'THAT', 'HAVE', 'FOR', 'NOT', 'WITH', 'YOU', 'THIS', 'BUT',
    'HIS', 'FROM', 'THEY', 'BEEN', 'HAVE', 'SAID', 'EACH', 'WHICH', 'THEIR',
    'WILL', 'OTHER', 'ABOUT', 'MANY', 'THEN', 'THEM', 'THESE', 'SOME', 'HER',
    'WOULD', 'MAKE', 'LIKE', 'TIME', 'JUST', 'KNOW', 'TAKE', 'PEOPLE', 'INTO',
    'YEAR', 'YOUR', 'GOOD', 'COULD', 'THAN', 'LOOK', 'ONLY', 'COME', 'MADE',
    'AFTER', 'ALSO', 'DID', 'MANY', 'BEFORE', 'MUST', 'THROUGH', 'BACK',
    'SHOULD', 'WHERE', 'MUCH', 'EVERY', 'WELL', 'WHAT', 'EVEN', 'MOST',
    'WHO', 'ARE', 'WAS', 'ONE', 'ALL', 'HAD', 'HAS', 'WHEN', 'CAN', 'THERE',
    'USE', 'BEEN', 'MAY', 'ITS', 'NOW', 'FIND', 'LONG', 'DOWN', 'DAY', 'GET',
    # Cicada-specific words
    'DIVINITY', 'TRUTH', 'WISDOM', 'SACRED', 'PRIMES', 'TOTIENT', 'PILGRIM',
    'CIRCUMFERENCE', 'CONSUMPTION', 'BELIEVE', 'NOTHING', 'EVERYTHING',
    'SPIRIT', 'SOUL', 'DEATH', 'FAITH', 'PATH', 'KOAN', 'MASTER', 'VOID',
    'SHADOWS', 'CABAL', 'AETHEREAL', 'WARNING', 'ENCRYPT', 'CIPHER',
    'LOSS', 'BEING', 'THINGS', 'WORLD',
]

# Common English trigrams
TRIGRAMS = [
    'THE', 'AND', 'ING', 'ENT', 'ION', 'HER', 'FOR', 'THA', 'NTH', 'INT',
    'ERE', 'TIO', 'VER', 'EST', 'ALL', 'ATE', 'OUS', 'ITH', 'HIS', 'TER',
    'COM', 'MEN', 'NOT', 'OFT', 'WIT', 'ARE', 'HAS', 'ERS', 'ONE', 'OUR',
    'STH', 'ATI', 'ORT', 'HAT', 'HAN', 'MAN', 'AIN', 'OUT', 'WAS', 'STO',
]

BIGRAMS = [
    'TH', 'HE', 'IN', 'ER', 'AN', 'RE', 'ON', 'AT', 'EN', 'ND',
    'TI', 'ES', 'OR', 'TE', 'OF', 'ED', 'IS', 'IT', 'AL', 'AR',
    'ST', 'TO', 'NT', 'NG', 'SE', 'HA', 'AS', 'OU', 'IO', 'LE',
    'VE', 'CO', 'ME', 'DE', 'HI', 'RI', 'RO', 'IC', 'NE', 'EA',
]


def word_to_indices(word):
    """Convert a word to Gematria Primus indices (digraph-aware)."""
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
    """Convert index array to Latin text."""
    return ''.join(INDEX_TO_LATIN.get(i, '?') for i in indices)


def load_page_runes(page_num):
    """Load rune indices from a page file. Returns (indices, raw_text)."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rune_path = os.path.join(base, 'LiberPrimus', 'pages', f'page_{page_num:02d}', 'runes.txt')
    if not os.path.exists(rune_path):
        return [], ""
    raw = open(rune_path, 'r', encoding='utf-8').read()
    indices = [RUNE_TO_INDEX[c] for c in raw if c in RUNE_TO_INDEX]
    return indices, raw


def load_page_words(page_num):
    """Load rune data preserving word boundaries. Returns list of index-lists (words)."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rune_path = os.path.join(base, 'LiberPrimus', 'pages', f'page_{page_num:02d}', 'runes.txt')
    if not os.path.exists(rune_path):
        return []
    raw = open(rune_path, 'r', encoding='utf-8').read()
    
    separators = {'-', ' ', '.', '/', '\n', '\r', ':', '&', '$', '%', '•', '"', "'", '\t'}
    words = []
    current_word = []
    for c in raw:
        if c in RUNE_TO_INDEX:
            current_word.append(RUNE_TO_INDEX[c])
        elif c in separators or c == '•':
            if current_word:
                words.append(current_word)
                current_word = []
    if current_word:
        words.append(current_word)
    return words


def calculate_ioc(indices):
    """Normalized IoC (English ~1.73, random ~1.0)."""
    freq = [0] * 29
    for idx in indices:
        freq[idx] += 1
    n = len(indices)
    if n <= 1:
        return 0
    ioc = sum(f * (f - 1) for f in freq) / (n * (n - 1))
    return ioc * 29


def score_english(text):
    """Score text for English-likeness using words, trigrams, bigrams."""
    text_upper = text.upper()
    score = 0
    
    # Word scoring (higher weight for longer words)
    for word in COMMON_WORDS:
        count = text_upper.count(word)
        score += count * len(word) * 2
    
    # Trigram scoring
    for tri in TRIGRAMS:
        score += text_upper.count(tri) * 3
    
    # Bigram scoring
    for bi in BIGRAMS:
        score += text_upper.count(bi) * 1
    
    # Penalize rare letters
    for ch in text_upper:
        if ch in 'XJQZ':
            score -= 2
    
    return score


def sieve_primes(limit):
    """Generate list of primes up to limit."""
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = False
    return [i for i in range(2, limit + 1) if is_prime[i]]


def fibonacci_sequence(limit):
    """Generate Fibonacci numbers up to limit."""
    fibs = [1, 1]
    while fibs[-1] < limit:
        fibs.append(fibs[-1] + fibs[-2])
    return [f for f in fibs if f < limit]


# ============================================================
# Cipher Operations
# ============================================================

def caesar_decrypt(indices, shift):
    return [(i - shift) % 29 for i in indices]


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


# ============================================================
# TRANSPOSITION METHODS (New Approaches)
# ============================================================

def read_at_positions(text_indices, positions):
    """Read characters at specific positions from the text."""
    n = len(text_indices)
    return [text_indices[p] for p in positions if p < n]


def prime_position_read(text_indices):
    """Read characters at prime-numbered positions (0-indexed)."""
    n = len(text_indices)
    primes = sieve_primes(n)
    return [text_indices[p] for p in primes if p < n]


def non_prime_position_read(text_indices):
    """Read characters at non-prime positions."""
    n = len(text_indices)
    prime_set = set(sieve_primes(n))
    return [text_indices[i] for i in range(n) if i not in prime_set]


def fibonacci_position_read(text_indices):
    """Read characters at Fibonacci-numbered positions."""
    n = len(text_indices)
    fibs = fibonacci_sequence(n)
    return [text_indices[f] for f in fibs if f < n]


def prime_permutation(text_indices):
    """Rearrange text: first all chars at prime positions, then non-prime."""
    n = len(text_indices)
    prime_set = set(sieve_primes(n))
    primes = [text_indices[i] for i in range(n) if i in prime_set]
    non_primes = [text_indices[i] for i in range(n) if i not in prime_set]
    return primes + non_primes


def inverse_prime_permutation(text_indices):
    """Undo prime permutation: interleave prime and non-prime back to original positions."""
    n = len(text_indices)
    prime_positions = sorted([i for i in range(n) if i in set(sieve_primes(n))])
    non_prime_positions = sorted([i for i in range(n) if i not in set(sieve_primes(n))])
    
    result = [0] * n
    for j, pos in enumerate(prime_positions):
        if j < len(text_indices):
            result[pos] = text_indices[j]
    for j, pos in enumerate(non_prime_positions):
        idx = len(prime_positions) + j
        if idx < len(text_indices):
            result[pos] = text_indices[idx]
    return result


def spiral_read(text_indices, rows, cols):
    """Read in spiral order from a grid."""
    if rows * cols < len(text_indices):
        return text_indices  # Can't form grid
    
    # Pad if needed
    padded = text_indices + [0] * (rows * cols - len(text_indices))
    grid = []
    for r in range(rows):
        grid.append(padded[r*cols:(r+1)*cols])
    
    result = []
    top, bottom, left, right = 0, rows - 1, 0, cols - 1
    
    while top <= bottom and left <= right:
        # Right
        for c in range(left, right + 1):
            result.append(grid[top][c])
        top += 1
        # Down
        for r in range(top, bottom + 1):
            result.append(grid[r][right])
        right -= 1
        # Left
        if top <= bottom:
            for c in range(right, left - 1, -1):
                result.append(grid[bottom][c])
            bottom -= 1
        # Up
        if left <= right:
            for r in range(bottom, top - 1, -1):
                result.append(grid[r][left])
            left += 1
    
    return result[:len(text_indices)]


def inverse_spiral_read(text_indices, rows, cols):
    """Undo spiral reading - text was written spirally, read left-to-right."""
    if rows * cols < len(text_indices):
        return text_indices
    
    n = len(text_indices)
    padded = text_indices + [0] * (rows * cols - n)
    
    # Build the spiral order of positions
    positions = []
    top, bottom, left, right = 0, rows - 1, 0, cols - 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            positions.append(top * cols + c)
        top += 1
        for r in range(top, bottom + 1):
            positions.append(r * cols + right)
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                positions.append(bottom * cols + c)
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                positions.append(r * cols + left)
            left += 1
    
    # Place characters: text[i] goes to position positions[i]
    grid_flat = [0] * (rows * cols)
    for i, pos in enumerate(positions):
        if i < len(padded):
            grid_flat[pos] = padded[i]
    
    return grid_flat[:n]


def boustrophedon_read(text_indices, width):
    """Read alternating left-to-right and right-to-left rows."""
    n = len(text_indices)
    rows = (n + width - 1) // width
    result = []
    for r in range(rows):
        start = r * width
        end = min(start + width, n)
        row = text_indices[start:end]
        if r % 2 == 1:
            row = row[::-1]
        result.extend(row)
    return result


def inverse_boustrophedon(text_indices, width):
    """Undo boustrophedon: re-reverse odd rows."""
    # Boustrophedon is its own inverse
    return boustrophedon_read(text_indices, width)


def columnar_transposition(text_indices, key_order):
    """Apply columnar transposition with given column order."""
    ncols = len(key_order)
    n = len(text_indices)
    nrows = (n + ncols - 1) // ncols
    
    # Pad
    padded = text_indices + [0] * (nrows * ncols - n)
    
    # Write row-by-row, read column-by-column in key order
    result = []
    for col in key_order:
        for row in range(nrows):
            idx = row * ncols + col
            if idx < n:
                result.append(padded[idx])
    return result[:n]


def inverse_columnar_transposition(text_indices, key_order):
    """Undo columnar transposition."""
    ncols = len(key_order)
    n = len(text_indices)
    nrows = (n + ncols - 1) // ncols
    
    # Figure out how many full columns vs short ones
    full_cols = n - (nrows - 1) * ncols  # Number of columns with nrows elements
    
    result = [0] * n
    pos = 0
    for col in key_order:
        col_len = nrows if col < full_cols else nrows - 1
        for row in range(col_len):
            idx = row * ncols + col
            if idx < n and pos < n:
                result[idx] = text_indices[pos]
                pos += 1
    
    return result


def rail_fence_decrypt(text_indices, rails):
    """Decrypt rail fence / zigzag cipher."""
    n = len(text_indices)
    if rails <= 1 or rails >= n:
        return text_indices
    
    # Calculate the length of each rail
    rail_lens = [0] * rails
    rail_idx = 0
    direction = 1
    for i in range(n):
        rail_lens[rail_idx] += 1
        if rail_idx == 0:
            direction = 1
        elif rail_idx == rails - 1:
            direction = -1
        rail_idx += direction
    
    # Split text into rails
    rail_texts = []
    pos = 0
    for r in range(rails):
        rail_texts.append(text_indices[pos:pos + rail_lens[r]])
        pos += rail_lens[r]
    
    # Read off in zigzag order
    result = []
    rail_positions = [0] * rails
    rail_idx = 0
    direction = 1
    for i in range(n):
        result.append(rail_texts[rail_idx][rail_positions[rail_idx]])
        rail_positions[rail_idx] += 1
        if rail_idx == 0:
            direction = 1
        elif rail_idx == rails - 1:
            direction = -1
        rail_idx += direction
    
    return result


def scytale_decrypt(text_indices, turns):
    """Scytale cipher (transposition with wrap-around)."""
    n = len(text_indices)
    cols = turns
    rows = (n + cols - 1) // cols
    
    padded = text_indices + [0] * (rows * cols - n)
    result = []
    for c in range(cols):
        for r in range(rows):
            idx = r * cols + c
            if idx < n:
                result.append(padded[idx])
    return result[:n]


def inverse_scytale(text_indices, turns):
    """Undo scytale (read down columns, write across rows)."""
    n = len(text_indices)
    rows = turns
    cols = (n + rows - 1) // rows
    
    padded = text_indices + [0] * (rows * cols - n)
    result = []
    for c in range(cols):
        for r in range(rows):
            idx = r * cols + c
            if idx < n:
                result.append(padded[idx])
    return result[:n]


def skip_cipher(text_indices, skip, offset=0):
    """Read every skip-th character starting at offset."""
    n = len(text_indices)
    result = []
    positions_used = set()
    pos = offset
    while len(positions_used) < n:
        if pos not in positions_used and pos < n:
            result.append(text_indices[pos])
            positions_used.add(pos)
        pos = (pos + skip) % n
        if pos in positions_used:
            # Find next unused position
            for p in range(n):
                if p not in positions_used:
                    pos = p
                    break
            else:
                break
    return result


def block_swap(text_indices, block_size):
    """Swap adjacent blocks of block_size characters."""
    n = len(text_indices)
    result = list(text_indices)
    for i in range(0, n - block_size, block_size * 2):
        end1 = min(i + block_size, n)
        end2 = min(i + 2 * block_size, n)
        block1 = result[i:end1]
        block2 = result[end1:end2]
        result[i:i+len(block2)] = block2
        result[i+len(block2):i+len(block2)+len(block1)] = block1
    return result


def reverse_text(text_indices):
    """Simply reverse the text."""
    return text_indices[::-1]


def totient_permutation(text_indices):
    """Permute using Euler's totient function: position i -> φ(i+2) mod n."""
    n = len(text_indices)
    result = [0] * n
    for i in range(n):
        new_pos = euler_totient(i + 2) % n
        result[new_pos] = text_indices[i]
    return result


def euler_totient(n):
    """Compute Euler's totient function."""
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


def interleave_halves(text_indices):
    """Split text in half and interleave."""
    n = len(text_indices)
    mid = n // 2
    first_half = text_indices[:mid]
    second_half = text_indices[mid:]
    result = []
    for i in range(max(len(first_half), len(second_half))):
        if i < len(first_half):
            result.append(first_half[i])
        if i < len(second_half):
            result.append(second_half[i])
    return result


def deinterleave(text_indices):
    """Undo interleaving: extract even and odd positions."""
    evens = text_indices[0::2]
    odds = text_indices[1::2]
    return evens + odds


def interleave_n(text_indices, n_parts):
    """Split into n parts and interleave."""
    parts = [[] for _ in range(n_parts)]
    for i, c in enumerate(text_indices):
        parts[i % n_parts].append(c)
    return [c for part in parts for c in part]


def deinterleave_n(text_indices, n_parts):
    """Undo n-way interleave."""
    n = len(text_indices)
    part_size = n // n_parts
    remainder = n % n_parts
    
    parts = []
    pos = 0
    for p in range(n_parts):
        size = part_size + (1 if p < remainder else 0)
        parts.append(text_indices[pos:pos+size])
        pos += size
    
    result = []
    max_len = max(len(p) for p in parts)
    for i in range(max_len):
        for p in parts:
            if i < len(p):
                result.append(p[i])
    return result


# ============================================================
# WORD-LEVEL OPERATIONS (using rune word boundaries)  
# ============================================================

def decrypt_words(words, key, mode='SUB'):
    """Decrypt a list of words (each a list of indices)."""
    flat = [idx for word in words for idx in word]
    decrypted = vigenere_decrypt(flat, key, mode)
    
    # Re-split into words
    result_words = []
    pos = 0
    for word in words:
        result_words.append(decrypted[pos:pos+len(word)])
        pos += len(word)
    return result_words


def words_to_text(words):
    """Convert list of word-index-lists to text string."""
    word_texts = []
    for word in words:
        word_texts.append(indices_to_text(word))
    return ' '.join(word_texts)


def try_word_rearrangements(words, max_size=8):
    """Try rearranging words in small groups to find readable text."""
    best_score = 0
    best_text = ""
    
    n = len(words)
    if n <= max_size:
        # Try all permutations (only feasible for small word counts)
        for perm in itertools.permutations(range(n)):
            reordered = [words[i] for i in perm]
            text = words_to_text(reordered)
            s = score_english(text)
            if s > best_score:
                best_score = s
                best_text = text
    else:
        # Try block rearrangements
        for block_size in [2, 3, 4, 5]:
            blocks = []
            for i in range(0, n, block_size):
                blocks.append(words[i:i+block_size])
            
            # Try reversing blocks
            reversed_blocks = blocks[::-1]
            reordered = [w for block in reversed_blocks for w in block]
            text = words_to_text(reordered)
            s = score_english(text)
            if s > best_score:
                best_score = s
                best_text = text
                
            # Try alternating blocks
            for perm in itertools.permutations(range(min(len(blocks), 5))):
                reordered_blocks = [blocks[i] for i in perm] + blocks[len(perm):]
                reordered = [w for block in reordered_blocks for w in block]
                text = words_to_text(reordered)
                s = score_english(text)
                if s > best_score:
                    best_score = s
                    best_text = text
    
    return best_score, best_text


# ============================================================
# MAIN ATTACK PIPELINE
# ============================================================

def attack_page_transposition(page_num, cipher_indices, description=""):
    """Try all transposition methods on pre-decrypted text."""
    n = len(cipher_indices)
    base_text = indices_to_text(cipher_indices)
    base_score = score_english(base_text)
    
    results = []
    
    print(f"\n{'='*80}")
    print(f"ATTACKING PAGE {page_num} - {description}")
    print(f"Length: {n} runes, Base score: {base_score}")
    print(f"Base text (first 100): {base_text[:100]}")
    print(f"{'='*80}")
    
    # 1. Reverse
    r = reverse_text(cipher_indices)
    text = indices_to_text(r)
    s = score_english(text)
    results.append(('REVERSE', s, text))
    
    # 2. Prime position extractions
    r = prime_position_read(cipher_indices)
    if r:
        text = indices_to_text(r)
        s = score_english(text)
        results.append(('PRIME_POSITIONS', s, text))
    
    r = non_prime_position_read(cipher_indices)
    if r:
        text = indices_to_text(r)
        s = score_english(text)
        results.append(('NON_PRIME_POSITIONS', s, text))
    
    # 3. Prime permutation and inverse
    r = prime_permutation(cipher_indices)
    text = indices_to_text(r)
    s = score_english(text)
    results.append(('PRIME_PERMUTATION', s, text))
    
    r = inverse_prime_permutation(cipher_indices)
    text = indices_to_text(r)
    s = score_english(text)
    results.append(('INV_PRIME_PERMUTATION', s, text))
    
    # 4. Fibonacci positions
    r = fibonacci_position_read(cipher_indices)
    if r:
        text = indices_to_text(r)
        s = score_english(text)
        results.append(('FIBONACCI_POSITIONS', s, text))
    
    # 5. Interleave/Deinterleave
    for n_parts in [2, 3, 5, 7]:
        r = interleave_n(cipher_indices, n_parts)
        text = indices_to_text(r)
        s = score_english(text)
        results.append((f'INTERLEAVE_{n_parts}', s, text))
        
        r = deinterleave_n(cipher_indices, n_parts)
        text = indices_to_text(r)
        s = score_english(text)
        results.append((f'DEINTERLEAVE_{n_parts}', s, text))
    
    # 6. Boustrophedon
    for width in [7, 11, 13, 17, 19, 23, 29, 31, 37]:
        r = boustrophedon_read(cipher_indices, width)
        text = indices_to_text(r)
        s = score_english(text)
        results.append((f'BOUSTROPHEDON_W{width}', s, text))
    
    # 7. Rail fence (decrypt)
    for rails in [2, 3, 4, 5, 6, 7]:
        r = rail_fence_decrypt(cipher_indices, rails)
        text = indices_to_text(r)
        s = score_english(text)
        results.append((f'RAIL_FENCE_{rails}', s, text))
    
    # 8. Scytale
    for turns in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]:
        r = scytale_decrypt(cipher_indices, turns)
        text = indices_to_text(r)
        s = score_english(text)
        results.append((f'SCYTALE_{turns}', s, text))
        
        r = inverse_scytale(cipher_indices, turns)
        text = indices_to_text(r)
        s = score_english(text)
        results.append((f'INV_SCYTALE_{turns}', s, text))
    
    # 9. Spiral reading  
    for rows in range(2, 30):
        cols = n // rows
        if cols < 2 or rows * cols < n - rows:
            continue
        r = spiral_read(cipher_indices, rows, cols)
        text = indices_to_text(r)
        s = score_english(text)
        results.append((f'SPIRAL_{rows}x{cols}', s, text))
        
        r = inverse_spiral_read(cipher_indices, rows, cols)
        text = indices_to_text(r)
        s = score_english(text)
        results.append((f'INV_SPIRAL_{rows}x{cols}', s, text))
    
    # 10. Skip cipher
    for skip in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]:
        for offset in [0]:
            r = skip_cipher(cipher_indices, skip, offset)
            text = indices_to_text(r)
            s = score_english(text)
            results.append((f'SKIP_{skip}_OFF{offset}', s, text))
    
    # 11. Block swaps
    for bs in [2, 3, 5, 7, 11, 13]:
        r = block_swap(cipher_indices, bs)
        text = indices_to_text(r)
        s = score_english(text)
        results.append((f'BLOCK_SWAP_{bs}', s, text))
    
    # 12. Columnar transposition with keyword-derived orders
    keywords = ['CABAL', 'DIVINITY', 'PRIMES', 'TOTIENT', 'SHADOWS', 'DEOR', 'VOID', 
                'SACRED', 'WISDOM', 'TRUTH', 'AETHEREAL', 'MOURNFUL', 'OBSCURA',
                'CICADA', 'PILGRIM', 'KOAN']
    for kw in keywords:
        key_idx = word_to_indices(kw)
        if len(key_idx) < 2:
            continue
        # Create column order from key (alphabetical ordering)
        order = sorted(range(len(key_idx)), key=lambda x: key_idx[x])
        
        r = columnar_transposition(cipher_indices, order)
        text = indices_to_text(r)
        s = score_english(text)
        results.append((f'COLUMNAR_{kw}', s, text))
        
        r = inverse_columnar_transposition(cipher_indices, order)
        text = indices_to_text(r)
        s = score_english(text)
        results.append((f'INV_COLUMNAR_{kw}', s, text))
    
    # 13. Totient permutation
    r = totient_permutation(cipher_indices)
    text = indices_to_text(r)
    s = score_english(text)
    results.append(('TOTIENT_PERM', s, text))
    
    # Sort by score
    results.sort(key=lambda x: x[1], reverse=True)
    
    # Report top results
    print(f"\n--- TOP 15 RESULTS (base score: {base_score}) ---")
    for method, score, text in results[:15]:
        improvement = score - base_score
        marker = " *** IMPROVEMENT ***" if improvement > 10 else ""
        print(f"  {method:35s} Score: {score:6.0f} (d{improvement:+5.0f}){marker}")
        if score > base_score + 20:
            print(f"    Text: {text[:120]}")
    
    return results


def attack_pages_21_30():
    """Attack pages 21-30 with known keywords + transposition."""
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
    
    all_results = {}
    
    for page_num, (keyword, mode) in page_keys.items():
        indices, raw = load_page_runes(page_num)
        if not indices:
            print(f"Page {page_num}: No rune data found")
            continue
        
        key = word_to_indices(keyword)
        decrypted = vigenere_decrypt(indices, key, mode)
        
        desc = f"Key={keyword}/{mode}"
        results = attack_page_transposition(page_num, decrypted, desc)
        all_results[page_num] = results
    
    return all_results


def attack_pages_31_54():
    """Attack pages 31-54 with Caesar shifts + transposition."""
    # Caesar shifts from previous analysis
    caesar_shifts = {
        31: 15, 32: 11, 33: 0, 34: 0, 35: 23, 36: 0, 37: 0, 38: 6,
        39: 0, 40: 0, 41: 13, 42: 5, 43: 23, 44: 5, 45: 20, 46: 22,
        47: 0, 48: 11, 49: 0, 50: 6, 51: 19, 52: 0, 53: 0, 54: 0,
    }
    
    all_results = {}
    
    # Focus on top-scoring pages first
    priority_pages = [32, 44, 50, 40, 43, 48, 41, 42, 45, 31, 38, 35, 46, 51]
    
    for page_num in priority_pages:
        shift = caesar_shifts.get(page_num, 0)
        indices, raw = load_page_runes(page_num)
        if not indices:
            print(f"Page {page_num}: No rune data found")
            continue
        
        decrypted = caesar_decrypt(indices, shift)
        
        desc = f"Caesar_{shift}"
        results = attack_page_transposition(page_num, decrypted, desc)
        all_results[page_num] = results
    
    return all_results


def try_second_substitution_layer(page_num, first_decrypted, first_method=""):
    """After first decryption, try a second substitution layer."""
    keywords = ['CABAL', 'DIVINITY', 'PRIMES', 'TOTIENT', 'SHADOWS', 'DEOR', 'VOID',
                'SACRED', 'WISDOM', 'TRUTH', 'AETHEREAL', 'MOURNFUL', 'OBSCURA',
                'CICADA', 'PILGRIM', 'KOAN', 'WARNING', 'BELIEVE', 'NOTHING',
                'ENCRYPT', 'CONSUMPTION', 'PATH', 'DEATH']
    
    best_score = 0
    best_result = None
    
    for kw in keywords:
        key = word_to_indices(kw)
        for mode in ['SUB', 'ADD', 'BEAUFORT']:
            result = vigenere_decrypt(first_decrypted, key, mode)
            text = indices_to_text(result)
            s = score_english(text)
            ioc = calculate_ioc(result)
            
            if s > best_score:
                best_score = s
                best_result = (kw, mode, s, ioc, text)
    
    if best_result:
        kw, mode, s, ioc, text = best_result
        print(f"  Page {page_num}: Best 2nd-layer: {kw}/{mode} Score={s:.0f} IoC={ioc:.4f}")
        print(f"    Text: {text[:100]}")
    
    return best_result


def comprehensive_attack():
    """Run all attack vectors on target pages."""
    print("=" * 80)
    print("COMPREHENSIVE TRANSPOSITION ATTACK")
    print("Liber Primus Pages 21-54")
    print("=" * 80)
    
    # Phase 1: Pages 21-30 (keyword + transposition)
    print("\n\n" + "=" * 80)
    print("PHASE 1: PAGES 21-30 (Keyword Decrypted + Transposition)")
    print("=" * 80)
    
    results_21_30 = attack_pages_21_30()
    
    # Phase 2: Pages 31-54 (Caesar + transposition)
    print("\n\n" + "=" * 80)
    print("PHASE 2: PAGES 31-54 (Caesar Shifted + Transposition)")
    print("=" * 80)
    
    # Just do top priority pages for now
    results_31_54 = {}
    priority_pages = [32, 44, 50, 40]
    
    caesar_shifts = {
        31: 15, 32: 11, 33: 0, 34: 0, 35: 23, 36: 0, 37: 0, 38: 6,
        39: 0, 40: 0, 41: 13, 42: 5, 43: 23, 44: 5, 45: 20, 46: 22,
        47: 0, 48: 11, 49: 0, 50: 6, 51: 19, 52: 0, 53: 0, 54: 0,
    }
    
    for page_num in priority_pages:
        shift = caesar_shifts.get(page_num, 0)
        indices, raw = load_page_runes(page_num)
        if not indices:
            continue
        decrypted = caesar_decrypt(indices, shift)
        desc = f"Caesar_{shift}"
        results = attack_page_transposition(page_num, decrypted, desc)
        results_31_54[page_num] = results
    
    # Phase 3: Double encryption tests
    print("\n\n" + "=" * 80)
    print("PHASE 3: DOUBLE ENCRYPTION TESTS (Substitution after substitution)")  
    print("=" * 80)
    
    page_keys = {
        21: ('CABAL', 'BEAUFORT'),
        22: ('DIVINITY', 'BEAUFORT'),
        23: ('ENCRYPTION', 'ADD'),
        24: ('OBSCURA', 'BEAUFORT'),
    }
    
    for page_num, (keyword, mode) in page_keys.items():
        indices, raw = load_page_runes(page_num)
        if not indices:
            continue
        key = word_to_indices(keyword)
        first_decrypted = vigenere_decrypt(indices, key, mode)
        try_second_substitution_layer(page_num, first_decrypted, f"{keyword}/{mode}")
    
    # Summary
    print("\n\n" + "=" * 80)
    print("SUMMARY OF BEST RESULTS")
    print("=" * 80)
    
    all_improvements = []
    for page_num in sorted(list(results_21_30.keys()) + list(results_31_54.keys())):
        results = results_21_30.get(page_num, results_31_54.get(page_num, []))
        if results:
            best = results[0]
            method, score, text = best
            all_improvements.append((page_num, method, score, text))
    
    all_improvements.sort(key=lambda x: x[2], reverse=True)
    
    print(f"\n{'Page':>6} {'Method':>35} {'Score':>8} {'Preview'}")
    print("-" * 120)
    for page_num, method, score, text in all_improvements[:20]:
        print(f"  {page_num:>4}  {method:>35}  {score:>6.0f}  {text[:60]}")
    
    return results_21_30, results_31_54


if __name__ == '__main__':
    comprehensive_attack()
