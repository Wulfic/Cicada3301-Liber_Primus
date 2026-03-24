#!/usr/bin/env python3
"""
Solver for Pages 21-30 of Liber Primus
=======================================
Strategy: Apply confirmed keyword + mode, then try word-level rearrangement.
P19 hint: "REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR K"

1. Keyword Vigenère decryption (known keys)
2. Word extraction (hyphen-delimited)
3. Word-level rearrangement by prime indices
4. English scoring via n-gram analysis
"""

import os
import sys
import json
import itertools
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
PAGES_DIR = BASE / "pages"
DATA_DIR = BASE / "data"

# === Gematria Primus ===
RUNE_TO_IDX = {
    'ᚠ': 0, 'ᚢ': 1, 'ᚦ': 2, 'ᚩ': 3, 'ᚱ': 4, 'ᚳ': 5, 'ᚷ': 6, 'ᚹ': 7,
    'ᚻ': 8, 'ᚾ': 9, 'ᛁ': 10, 'ᛄ': 11, 'ᛇ': 12, 'ᛈ': 13, 'ᛉ': 14, 'ᛋ': 15,
    'ᛏ': 16, 'ᛒ': 17, 'ᛖ': 18, 'ᛗ': 19, 'ᛚ': 20, 'ᛝ': 21, 'ᛟ': 22, 'ᛞ': 23,
    'ᚪ': 24, 'ᚫ': 25, 'ᚣ': 26, 'ᛡ': 27, 'ᛠ': 28,
}
IDX_TO_LETTER = [
    'F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S',
    'T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA'
]

# Confirmed keys for pages 21-30 from MASTER_TRACKER
PAGE_KEYS = {
    21: {'keyword': 'CABAL',     'mode': 'beaufort', 'indices': [5, 24, 17, 24, 20]},
    22: {'keyword': 'DIVINITY',  'mode': 'beaufort', 'indices': [23, 10, 1, 10, 9, 10, 16, 26]},
    23: {'keyword': 'ENCRYPTION','mode': 'add',      'indices': None},
    24: {'keyword': 'OBSCURA',   'mode': 'beaufort', 'indices': [3, 17, 15, 5, 1, 4, 24]},
    25: {'keyword': 'CABAL',     'mode': 'beaufort', 'indices': [5, 24, 17, 24, 20]},
    26: {'keyword': 'ENCRYPT',   'mode': 'add',      'indices': None},
    27: {'keyword': 'SHADOWS',   'mode': 'add',      'indices': [15, 8, 24, 23, 3, 7, 15]},
    28: {'keyword': 'DEOR',      'mode': 'sub',      'indices': None},
    29: {'keyword': 'TOTIENT',   'mode': 'beaufort', 'indices': None},
    30: {'keyword': 'MOURNFUL',  'mode': 'add',      'indices': [19, 3, 1, 4, 9, 0, 1, 20]},
}

# Convert keyword to GP indices
def keyword_to_indices(keyword):
    """Convert a keyword string to GP index array."""
    letter_to_idx = {}
    for i, l in enumerate(IDX_TO_LETTER):
        letter_to_idx[l] = i
    
    result = []
    kw = keyword.upper()
    i = 0
    while i < len(kw):
        # Check digraphs first (longest match)
        matched = False
        for length in [3, 2]:  # NG=3 chars, TH/EO/OE/AE/EA/IO/IA=2 chars
            if i + length <= len(kw):
                chunk = kw[i:i+length]
                if chunk in letter_to_idx:
                    result.append(letter_to_idx[chunk])
                    i += length
                    matched = True
                    break
        if not matched:
            ch = kw[i]
            if ch == 'K':
                ch = 'C'
            if ch == 'V':
                ch = 'U'
            if ch in letter_to_idx:
                result.append(letter_to_idx[ch])
            else:
                print(f"Warning: '{ch}' not in GP alphabet")
                result.append(0)
            i += 1
    return result

def load_runes(page_num):
    """Load rune file and return list of (rune_idx, is_separator, char) tuples."""
    rune_file = PAGES_DIR / f"page_{page_num:02d}" / "runes.txt"
    if not rune_file.exists():
        return None
    with open(rune_file, 'r', encoding='utf-8') as f:
        content = f.read()
    return content

def extract_rune_indices(content):
    """Extract just the rune indices (ignoring separators) from rune text."""
    indices = []
    for ch in content:
        if ch in RUNE_TO_IDX:
            indices.append(RUNE_TO_IDX[ch])
    return indices

def decrypt_vigenere(cipher_indices, key_indices, mode='sub'):
    """
    Decrypt using Vigenère with given mode.
    sub:     plain = (cipher - key) % 29
    add:     plain = (cipher + key) % 29
    beaufort: plain = (key - cipher) % 29
    """
    result = []
    klen = len(key_indices)
    for i, c in enumerate(cipher_indices):
        k = key_indices[i % klen]
        if mode == 'sub':
            p = (c - k) % 29
        elif mode == 'add':
            p = (c + k) % 29
        elif mode == 'beaufort':
            p = (k - c) % 29
        else:
            raise ValueError(f"Unknown mode: {mode}")
        result.append(p)
    return result

def indices_to_runeglish(indices):
    """Convert GP indices to runeglish string."""
    return ''.join(IDX_TO_LETTER[i] for i in indices)

def decrypt_page_with_structure(content, key_indices, mode):
    """
    Decrypt a page preserving word boundaries and punctuation.
    Returns list of (word_runeglish, word_indices) tuples for words,
    and the full decrypted runeglish with separators.
    """
    key_pos = 0
    klen = len(key_indices)
    words = []
    current_word_indices = []
    full_output = []
    
    for ch in content:
        if ch in RUNE_TO_IDX:
            c = RUNE_TO_IDX[ch]
            k = key_indices[key_pos % klen]
            if mode == 'sub':
                p = (c - k) % 29
            elif mode == 'add':
                p = (c + k) % 29
            elif mode == 'beaufort':
                p = (k - c) % 29
            else:
                raise ValueError(f"Unknown mode: {mode}")
            current_word_indices.append(p)
            full_output.append(IDX_TO_LETTER[p])
            key_pos += 1
        elif ch in '-':
            # Word boundary
            if current_word_indices:
                word_text = ''.join(IDX_TO_LETTER[i] for i in current_word_indices)
                words.append((word_text, list(current_word_indices)))
                current_word_indices = []
            full_output.append(' ')
        elif ch in '.':
            if current_word_indices:
                word_text = ''.join(IDX_TO_LETTER[i] for i in current_word_indices)
                words.append((word_text, list(current_word_indices)))
                current_word_indices = []
            full_output.append('.')
        elif ch in '&$/%\n\r':
            if current_word_indices:
                word_text = ''.join(IDX_TO_LETTER[i] for i in current_word_indices)
                words.append((word_text, list(current_word_indices)))
                current_word_indices = []
            if ch not in '\n\r':
                full_output.append(ch)
    
    # Final word
    if current_word_indices:
        word_text = ''.join(IDX_TO_LETTER[i] for i in current_word_indices)
        words.append((word_text, list(current_word_indices)))
    
    return words, ''.join(full_output)

def runeglish_to_english(rg):
    """
    Approximate conversion of Runeglish → English.
    Handles GP digraph rules:
    - TH → TH (already)
    - NG → NG, absorbs adjacent I (NGNG → NGING, BNG → BING)
    - IA → ION (sometimes)
    - C → K (sometimes) 
    - EO → EO (or context)
    - OE → OE
    """
    # Basic: just return as-is for now, since scoring handles it
    return rg

def compute_ioc(indices):
    """Compute Index of Coincidence."""
    n = len(indices)
    if n < 2:
        return 0
    counts = Counter(indices)
    numerator = sum(c * (c - 1) for c in counts.values())
    denominator = n * (n - 1)
    # Normalize to 29-letter alphabet (multiply by 29)
    return 29 * numerator / denominator if denominator > 0 else 0

# English word scoring
COMMON_WORDS = set()
def load_wordlist():
    global COMMON_WORDS
    wl_path = DATA_DIR / "wordlist.txt"
    if wl_path.exists():
        with open(wl_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                w = line.strip().upper()
                if 2 <= len(w) <= 15:
                    COMMON_WORDS.add(w)
    # Also add very common short words
    for w in ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER',
              'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'HAD', 'HAS', 'HIS', 'HOW', 'ITS',
              'MAY', 'NEW', 'NOW', 'OLD', 'SEE', 'WAY', 'WHO', 'DID', 'GOT', 'LET',
              'SAY', 'SHE', 'TOO', 'USE', 'THIS', 'THAT', 'WITH', 'HAVE', 'FROM',
              'THEY', 'BEEN', 'SAID', 'EACH', 'WILL', 'INTO', 'THAN', 'THEM', 'THEN',
              'WHAT', 'WHEN', 'MAKE', 'LIKE', 'LONG', 'LOOK', 'MANY', 'SOME', 'TIME',
              'VERY', 'YOUR', 'KNOW', 'JUST', 'COME', 'MADE', 'FIND', 'BACK', 'ONLY',
              'SELF', 'BEING', 'TRUTH', 'WITHIN', 'SACRED', 'WISDOM', 'FOLLOW',
              'INSTRUCTION', 'PILGRIMAGE', 'DIVINITY', 'CIRCUMFERENCE', 'CONSUMPTION',
              'A', 'I', 'OF', 'TO', 'IN', 'IS', 'IT', 'AN', 'AS', 'AT', 'BE', 'BY',
              'DO', 'GO', 'IF', 'ME', 'MY', 'NO', 'ON', 'OR', 'SO', 'UP', 'WE']:
        COMMON_WORDS.add(w)

# GP-aware word matching
def gp_word_matches_english(rg_word):
    """
    Check if a runeglish word could match an English word, accounting for GP rules.
    Returns list of possible English words.
    """
    # Direct check
    if rg_word in COMMON_WORDS:
        return [rg_word]
    
    matches = []
    # Try C→K substitution
    if 'C' in rg_word:
        variant = rg_word.replace('C', 'K')
        if variant in COMMON_WORDS:
            matches.append(variant)
    
    # Try U→V substitution
    if 'U' in rg_word:
        variant = rg_word.replace('U', 'V')
        if variant in COMMON_WORDS:
            matches.append(variant)
    
    # Try IA→ION
    if 'IA' in rg_word:
        variant = rg_word.replace('IA', 'ION')
        if variant in COMMON_WORDS:
            matches.append(variant)
    
    # Try NG→ING (if preceded by non-I)
    for i in range(len(rg_word) - 1):
        if rg_word[i:i+2] == 'NG':
            if i == 0 or rg_word[i-1] != 'I':
                variant = rg_word[:i] + 'ING' + rg_word[i+2:]
                if variant in COMMON_WORDS:
                    matches.append(variant)
    
    return matches

def score_word_sequence(words):
    """Score a sequence of runeglish words for English-likeness."""
    score = 0
    for word_text, _ in words:
        w = word_text.upper()
        if w in COMMON_WORDS:
            score += len(w) * 10
        else:
            matches = gp_word_matches_english(w)
            if matches:
                score += len(w) * 8
            elif len(w) <= 3:
                # Short words get small penalty
                score -= 1
            else:
                score -= 2
    
    # Bigram bonus for common word pairs
    for i in range(len(words) - 1):
        w1 = words[i][0].upper()
        w2 = words[i+1][0].upper()
        pair = f"{w1} {w2}"
        if pair in {'THE SELF', 'OF THE', 'IN THE', 'TO THE', 'AND THE', 'IS THE',
                     'IT IS', 'YOU ARE', 'ALL THINGS', 'FOR ALL', 'THAT LIVES',
                     'IS HOLY', 'EACH INTELLIGENCE', 'AN INSTRUCTION',
                     'SOME WISDOM', 'A WARNING', 'A KOAN', 'BELIEVE NOTHING',
                     'FROM THIS', 'THIS BOOK', 'DO NOT', 'YOUR OWN'}:
            score += 50
    
    return score

def primes_up_to(n):
    """Sieve of Eratosthenes."""
    if n < 2:
        return []
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n+1, i):
                sieve[j] = False
    return [i for i in range(n+1) if sieve[i]]

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i+2) == 0: return False
        i += 6
    return True

def try_prime_word_rearrangement(words):
    """
    Try rearranging words based on prime indices.
    P19: "REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH"
    
    Several strategies:
    1. Read words at prime positions (2,3,5,7,11,13...)
    2. Read words at non-prime positions, then prime positions
    3. Use word lengths as indices
    4. Use GP values of first letter as sort key
    """
    n = len(words)
    results = []
    
    # Strategy 1: Extract words at prime-indexed positions (0-based)
    prime_words = [words[i] for i in range(n) if is_prime(i)]
    non_prime_words = [words[i] for i in range(n) if not is_prime(i)]
    
    # 1a: prime positions only
    if prime_words:
        score = score_word_sequence(prime_words)
        results.append(('prime_positions_only', prime_words, score))
    
    # 1b: prime then non-prime
    combined = prime_words + non_prime_words
    score = score_word_sequence(combined)
    results.append(('prime_then_nonprime', combined, score))
    
    # 1c: non-prime then prime
    combined2 = non_prime_words + prime_words
    score = score_word_sequence(combined2)
    results.append(('nonprime_then_prime', combined2, score))
    
    # Strategy 2: Sort words by their GP value sum
    def gp_sum(word_tuple):
        return sum(word_tuple[1])
    sorted_by_gp = sorted(words, key=gp_sum)
    score = score_word_sequence(sorted_by_gp)
    results.append(('sorted_by_gp_sum', sorted_by_gp, score))
    
    # Strategy 3: Sort words by length
    sorted_by_len = sorted(words, key=lambda w: len(w[1]))
    score = score_word_sequence(sorted_by_len)
    results.append(('sorted_by_length', sorted_by_len, score))
    
    # Strategy 4: Read words at positions given by prime sequence
    # i.e., word[2], word[3], word[5], word[7], word[11]...
    primes = primes_up_to(n)
    prime_indexed = [words[p] for p in primes if p < n]
    if prime_indexed:
        score = score_word_sequence(prime_indexed)
        results.append(('words_at_prime_indices', prime_indexed, score))
    
    # Strategy 5: Use prime-th letters within each word (character-level prime extraction)
    # This would create new words from prime-positioned characters
    
    # Strategy 6: Reverse word order
    reversed_words = list(reversed(words))
    score = score_word_sequence(reversed_words)
    results.append(('reversed', reversed_words, score))
    
    # Strategy 7: Every other word (interleave two streams)
    even_words = [words[i] for i in range(0, n, 2)]
    odd_words = [words[i] for i in range(1, n, 2)]
    interleaved = list(zip(even_words, odd_words))
    flat = [w for pair in interleaved for w in pair]
    if len(even_words) > len(odd_words):
        flat.append(even_words[-1])
    score = score_word_sequence(flat)
    results.append(('interleaved_even_odd', flat, score))
    
    # Strategy 8: Read in columns (treating words as a grid)
    for ncols in [2, 3, 5, 7, 11, 13]:
        if ncols <= n:
            col_order = []
            for col in range(ncols):
                for row in range(0, n, ncols):
                    if row + col < n:
                        col_order.append(words[row + col])
            score = score_word_sequence(col_order)
            results.append((f'columnar_{ncols}cols', col_order, score))
    
    # Strategy 9: Fibonacci-indexed words
    fibs = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233]
    fib_words = [words[f % n] for f in fibs if f < n * 3]
    # Deduplicate while preserving order
    seen = set()
    fib_unique = []
    for w in fib_words:
        key = id(w)
        if key not in seen:
            seen.add(key)
            fib_unique.append(w)
    if fib_unique:
        score = score_word_sequence(fib_unique)
        results.append(('fibonacci_indexed', fib_unique, score))
    
    # Strategy 10: Sort by first letter GP index
    sorted_by_first = sorted(words, key=lambda w: w[1][0] if w[1] else 0)
    score = score_word_sequence(sorted_by_first)
    results.append(('sorted_by_first_letter', sorted_by_first, score))
    
    return sorted(results, key=lambda x: -x[2])

def try_character_level_prime_rearrangement(plain_indices):
    """
    Try reading characters at prime positions from the decrypted text.
    """
    n = len(plain_indices)
    results = []
    
    # Characters at prime positions (1-indexed)
    prime_chars = [plain_indices[i-1] for i in range(2, n+1) if is_prime(i)]
    if prime_chars:
        text = indices_to_runeglish(prime_chars)
        ioc = compute_ioc(prime_chars)
        results.append(('prime_chars_1indexed', text, ioc, prime_chars))
    
    # Characters at prime positions (0-indexed)
    prime_chars_0 = [plain_indices[i] for i in range(n) if is_prime(i)]
    if prime_chars_0:
        text = indices_to_runeglish(prime_chars_0)
        ioc = compute_ioc(prime_chars_0)
        results.append(('prime_chars_0indexed', text, ioc, prime_chars_0))
    
    # Non-prime positions (0-indexed)
    nonprime_chars = [plain_indices[i] for i in range(n) if not is_prime(i)]
    if nonprime_chars:
        text = indices_to_runeglish(nonprime_chars)
        ioc = compute_ioc(nonprime_chars)
        results.append(('nonprime_chars', text, ioc, nonprime_chars))
    
    # Columnar transposition with prime-width columns
    for width in [5, 7, 11, 13, 17, 19, 23, 29]:
        if width < n:
            rows = []
            for i in range(0, n, width):
                rows.append(plain_indices[i:i+width])
            # Read by columns
            col_read = []
            for col in range(width):
                for row in rows:
                    if col < len(row):
                        col_read.append(row[col])
            text = indices_to_runeglish(col_read)
            ioc = compute_ioc(col_read)
            results.append((f'columnar_w{width}', text, ioc, col_read))
    
    return sorted(results, key=lambda x: -x[2])

def try_deor_rearrangement(words, plain_indices):
    """
    P19 says "...A PATH TO THE DEOR K"
    Deor poem has 7 stanzas with refrain pattern.
    Try using Deor structure for rearrangement.
    """
    results = []
    
    # Load Deor poem
    deor_path = DATA_DIR / "deor_poem.txt"
    if deor_path.exists():
        with open(deor_path, 'r', encoding='utf-8', errors='ignore') as f:
            deor = f.read()
        
        # Convert Deor to GP indices for use as key
        deor_lower = deor.lower()
        deor_indices = []
        letter_to_idx = {}
        for i, l in enumerate(IDX_TO_LETTER):
            letter_to_idx[l.lower()] = i
        
        i = 0
        while i < len(deor_lower):
            matched = False
            for length in [2, 1]:
                if i + length <= len(deor_lower):
                    chunk = deor_lower[i:i+length]
                    if chunk in letter_to_idx:
                        deor_indices.append(letter_to_idx[chunk])
                        i += length
                        matched = True
                        break
            if not matched:
                i += 1
        
        if deor_indices:
            # Beaufort with Deor as key
            n = len(plain_indices)
            deor_key = deor_indices[:n] if len(deor_indices) >= n else (deor_indices * (n // len(deor_indices) + 1))[:n]
            beaufort = [(deor_key[i] - plain_indices[i]) % 29 for i in range(n)]
            text = indices_to_runeglish(beaufort)
            ioc = compute_ioc(beaufort)
            results.append(('beaufort_deor', text[:200], ioc))
            
            # SUB with Deor
            sub_result = [(plain_indices[i] - deor_key[i]) % 29 for i in range(n)]
            text2 = indices_to_runeglish(sub_result)
            ioc2 = compute_ioc(sub_result)
            results.append(('sub_deor', text2[:200], ioc2))
            
            # ADD with Deor
            add_result = [(plain_indices[i] + deor_key[i]) % 29 for i in range(n)]
            text3 = indices_to_runeglish(add_result)
            ioc3 = compute_ioc(add_result)
            results.append(('add_deor', text3[:200], ioc3))
    
    return sorted(results, key=lambda x: -x[2])

def analyze_page(page_num, verbose=True):
    """Full analysis of a single page."""
    config = PAGE_KEYS.get(page_num)
    if not config:
        print(f"No key config for page {page_num}")
        return None
    
    content = load_runes(page_num)
    if not content:
        print(f"No runes.txt for page {page_num}")
        return None
    
    # Get key indices
    key_indices = config['indices']
    if key_indices is None:
        key_indices = keyword_to_indices(config['keyword'])
    
    mode = config['mode']
    keyword = config['keyword']
    
    # Decrypt preserving structure
    words, full_text = decrypt_page_with_structure(content, key_indices, mode)
    cipher_indices = extract_rune_indices(content)
    plain_indices = decrypt_vigenere(cipher_indices, key_indices, mode)
    ioc = compute_ioc(plain_indices)
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"PAGE {page_num} — Keyword: {keyword}, Mode: {mode}")
        print(f"{'='*70}")
        print(f"Rune count: {len(cipher_indices)}")
        print(f"IoC after keyword decrypt: {ioc:.4f}")
        print(f"Word count: {len(words)}")
        print(f"\nDecrypted text (with spaces):")
        print(full_text[:500])
        print(f"\n--- Words extracted ({len(words)} total) ---")
        for i, (wt, wi) in enumerate(words):
            eng = gp_word_matches_english(wt)
            marker = f" -> {eng}" if eng else ""
            print(f"  [{i:3d}] {wt}{marker}")
    
    # Try word-level rearrangements
    if verbose:
        print(f"\n--- Word-level rearrangement results ---")
    rearrangements = try_prime_word_rearrangement(words)
    for name, reordered, score in rearrangements[:5]:
        text = ' '.join(w[0] for w in reordered[:20])
        if verbose:
            print(f"  {name}: score={score}, text={text[:100]}...")
    
    # Try character-level prime rearrangement
    if verbose:
        print(f"\n--- Character-level prime extraction ---")
    char_results = try_character_level_prime_rearrangement(plain_indices)
    for name, text, r_ioc, indices in char_results[:5]:
        if verbose:
            print(f"  {name}: IoC={r_ioc:.4f}, text={text[:100]}...")
    
    # Try Deor-based second layer
    if verbose:
        print(f"\n--- Deor-based second layer ---")
    deor_results = try_deor_rearrangement(words, plain_indices)
    for name, text, r_ioc in deor_results[:3]:
        if verbose:
            print(f"  {name}: IoC={r_ioc:.4f}, text={text[:100]}...")
    
    return {
        'page': page_num,
        'ioc': ioc,
        'words': words,
        'plain_indices': plain_indices,
        'full_text': full_text,
        'rearrangements': rearrangements,
        'char_results': char_results,
        'deor_results': deor_results,
    }

def main():
    load_wordlist()
    print(f"Loaded {len(COMMON_WORDS)} words in dictionary")
    
    all_results = {}
    
    for page_num in range(21, 31):
        result = analyze_page(page_num, verbose=True)
        if result:
            all_results[page_num] = result
    
    # Cross-page analysis
    print(f"\n{'='*70}")
    print(f"CROSS-PAGE SUMMARY")
    print(f"{'='*70}")
    
    for pn, r in sorted(all_results.items()):
        best_rearr = r['rearrangements'][0] if r['rearrangements'] else ('none', [], 0)
        best_char = r['char_results'][0] if r['char_results'] else ('none', '', 0, [])
        print(f"P{pn}: IoC={r['ioc']:.4f}, words={len(r['words'])}, "
              f"best_word_rearr={best_rearr[0]}(score={best_rearr[2]}), "
              f"best_char_extract={best_char[0]}(IoC={best_char[2]:.4f})")

if __name__ == "__main__":
    main()
