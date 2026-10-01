#!/usr/bin/env python3
"""
F-Skip Verified Key Solver + Single-Rune Word Keystream Analysis
Tests verified hill-climbed keys WITH F-skip rule on all unsolved pages.
Also extracts keystream constraints from single-rune words.
"""
import json
import os
import sys
import math
from collections import Counter

# Gematria Primus: index -> (rune, latin, prime)
GP = [
    ('ᚠ', 'F', 2),   ('ᚢ', 'U', 3),   ('ᚦ', 'TH', 5),  ('ᚩ', 'O', 7),
    ('ᚱ', 'R', 11),   ('ᚳ', 'CK', 13),  ('ᚷ', 'G', 17),  ('ᚹ', 'W', 19),
    ('ᚻ', 'H', 23),   ('ᚾ', 'N', 29),   ('ᛁ', 'I', 31),   ('ᛂ', 'J', 37),
    ('ᛇ', 'EO', 41),  ('ᛈ', 'P', 43),   ('ᛉ', 'X', 47),   ('ᛋ', 'S', 53),
    ('ᛏ', 'T', 59),   ('ᛒ', 'B', 61),   ('ᛖ', 'E', 67),   ('ᛗ', 'M', 71),
    ('ᛚ', 'L', 73),   ('ᛝ', 'NG', 79),  ('ᛟ', 'OE', 83),  ('ᛞ', 'D', 89),
    ('ᚪ', 'A', 97),   ('ᚫ', 'AE', 101), ('ᚣ', 'Y', 103),  ('ᛡ', 'IA', 107),
    ('ᛠ', 'EA', 109),
]

RUNE_TO_IDX = {r[0]: i for i, r in enumerate(GP)}
IDX_TO_LATIN = {i: r[1] for i, r in enumerate(GP)}
SEPARATORS = set('•-.:;\'"')
DIGITS = set('0123456789')

def read_rune_page(page_num):
    """Read rune text for a page from the runes_full.txt or runeglish directory."""
    # Try to get raw runes from RuneSolver-style data
    rune_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'runeglish', 
                             f'page_{page_num:02d}_runeglish.txt')
    if os.path.exists(rune_file):
        with open(rune_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return None

def extract_rune_indices(page_num):
    """Extract rune indices from page image directory or runeglish."""
    # First try to find rune text directly
    page_dir = os.path.join(os.path.dirname(__file__), '..', 'pages', f'page_{page_num:02d}')
    rune_file = os.path.join(page_dir, 'runes.txt') if os.path.isdir(page_dir) else None
    
    text = None
    if rune_file and os.path.exists(rune_file):
        with open(rune_file, 'r', encoding='utf-8') as f:
            text = f.read().strip()
    
    if text is None:
        # Fall back to runes_full.txt parsing or RuneSolver data
        return None
    
    return parse_rune_text(text)

def parse_rune_text(text):
    """Parse rune text into list of (index, is_separator) tuples."""
    result = []
    for ch in text:
        if ch in RUNE_TO_IDX:
            result.append(('rune', RUNE_TO_IDX[ch]))
        elif ch in SEPARATORS or ch == ' ' or ch == '\n':
            result.append(('sep', ch))
        elif ch in DIGITS:
            result.append(('digit', ch))
        # ignore other chars like /
    return result

def get_rune_sequences_from_runeglish(page_num):
    """Get rune indices from runeglish file (already in latin, need to reverse to indices)."""
    rune_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'runeglish',
                             f'page_{page_num:02d}_runeglish.txt')
    if not os.path.exists(rune_file):
        return None, None
    
    with open(rune_file, 'r', encoding='utf-8') as f:
        text = f.read().strip()
    
    # Runeglish uses hyphens as word separators
    # Letters are already in latin form
    LATIN_TO_IDX = {}
    for i, (r, lat, p) in enumerate(GP):
        LATIN_TO_IDX[lat] = i
    
    rune_indices = []
    words = []
    current_word = []
    
    # Parse character by character  
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == '-' or ch == '.' or ch == '\n':
            if current_word:
                words.append(current_word[:])
                current_word = []
            i += 1
        elif ch == '/':
            # Line continuation
            i += 1
        else:
            # Try to match a digraph first (2 chars)
            matched = False
            if i + 1 < len(text):
                digraph = text[i:i+2]
                if digraph in LATIN_TO_IDX:
                    idx = LATIN_TO_IDX[digraph]
                    rune_indices.append(idx)
                    current_word.append(idx)
                    i += 2
                    matched = True
            if not matched:
                ch_upper = ch.upper()
                if ch_upper in LATIN_TO_IDX:
                    idx = LATIN_TO_IDX[ch_upper]
                    rune_indices.append(idx)
                    current_word.append(idx)
                    i += 1
                else:
                    i += 1
    
    if current_word:
        words.append(current_word[:])
    
    return rune_indices, words

def get_page_rune_data(page_num):
    """Get rune indices and word structure for a page.
    Returns (rune_indices, words, word_positions) where word_positions maps word_idx to starting rune position."""
    # Try page directory first
    page_dir = os.path.join(os.path.dirname(__file__), '..', 'pages', f'page_{page_num:02d}')
    rune_file = os.path.join(page_dir, 'runes.txt') if os.path.isdir(page_dir) else None
    
    if rune_file and os.path.exists(rune_file):
        with open(rune_file, 'r', encoding='utf-8') as f:
            text = f.read().strip()
        
        rune_indices = []
        words = []
        current_word = []
        word_positions = []
        rune_pos = 0
        
        for ch in text:
            if ch in RUNE_TO_IDX:
                idx = RUNE_TO_IDX[ch]
                if not current_word:
                    word_positions.append(rune_pos)
                rune_indices.append(idx)
                current_word.append(idx)
                rune_pos += 1
            elif ch in SEPARATORS or ch == ' ' or ch == '\n':
                if current_word:
                    words.append(current_word[:])
                    current_word = []
        
        if current_word:
            word_positions.append(rune_pos - len(current_word))
            words.append(current_word[:])
        
        return rune_indices, words, word_positions
    
    # Fall back to runeglish
    rune_indices, words = get_rune_sequences_from_runeglish(page_num)
    if rune_indices is not None:
        word_positions = []
        pos = 0
        for w in words:
            word_positions.append(pos)
            pos += len(w)
        return rune_indices, words, word_positions
    
    return None, None, None

def compute_ioc(indices):
    """Compute Index of Coincidence for a sequence of indices."""
    if len(indices) < 2:
        return 0.0
    counts = Counter(indices)
    n = len(indices)
    total = sum(c * (c - 1) for c in counts.values())
    return total / (n * (n - 1)) * 29  # Normalized: 1.0 = random, ~1.73 = English

def decrypt_vigenere_sub(cipher_indices, key, f_skip=False):
    """Decrypt using Vigenère SUB: plain = (cipher - key) % 29"""
    result = []
    key_pos = 0
    for c in cipher_indices:
        k = key[key_pos % len(key)]
        p = (c - k) % 29
        result.append(p)
        if f_skip:
            if p != 0:  # Skip key advancement when plaintext is F (index 0)
                key_pos += 1
        else:
            key_pos += 1
    return result

def decrypt_vigenere_add(cipher_indices, key, f_skip=False):
    """Decrypt using Vigenère ADD: plain = (cipher + key) % 29"""
    result = []
    key_pos = 0
    for c in cipher_indices:
        k = key[key_pos % len(key)]
        p = (c + k) % 29
        result.append(p)
        if f_skip:
            if p != 0:
                key_pos += 1
        else:
            key_pos += 1
    return result

def decrypt_beaufort(cipher_indices, key, f_skip=False):
    """Decrypt using Beaufort: plain = (key - cipher) % 29"""
    result = []
    key_pos = 0
    for c in cipher_indices:
        k = key[key_pos % len(key)]
        p = (k - c) % 29
        result.append(p)
        if f_skip:
            if p != 0:
                key_pos += 1
        else:
            key_pos += 1
    return result

def indices_to_text(indices):
    """Convert GP indices to readable text."""
    return ''.join(IDX_TO_LATIN[i] for i in indices)

def count_english_words(text, words_set):
    """Count how many common English words appear in the text."""
    text_lower = text.lower()
    count = 0
    for w in words_set:
        if w in text_lower:
            count += 1
    return count

def check_single_rune_words(words, word_positions, decrypt_fn, key):
    """Check if all single-rune words decrypt to I (10) or A (24)."""
    matches = 0
    total = 0
    for i, w in enumerate(words):
        if len(w) == 1:
            total += 1
            # Get the position in the rune stream
            pos = word_positions[i]
            p = decrypt_fn([w[0]], key)[0]  # simplified - doesn't account for F-skip position
            if p == 10 or p == 24:
                matches += 1
    return matches, total

# Common English words to look for in decrypted text
COMMON_WORDS = {
    'the', 'and', 'that', 'have', 'for', 'not', 'with', 'you', 'this',
    'but', 'from', 'they', 'her', 'she', 'will', 'one', 'all', 'would',
    'there', 'their', 'what', 'about', 'when', 'make', 'like', 'been',
    'who', 'him', 'some', 'could', 'them', 'than', 'other', 'into',
    'which', 'each', 'only', 'come', 'its', 'over', 'such', 'after',
    'also', 'most', 'know', 'being', 'truth', 'divine', 'wisdom',
    'consciousness', 'self', 'mind', 'soul', 'spirit', 'light',
    'sacred', 'power', 'knowledge', 'seek', 'path', 'within',
    'world', 'life', 'death', 'time', 'must', 'shall', 'through',
}

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

def prime_totient_stream(length, start_idx=0):
    """Generate keystream using φ(prime) = prime-1 mod 29, starting from prime at start_idx."""
    primes = generate_primes(length + start_idx + 10)
    stream = []
    for i in range(length):
        p = primes[start_idx + i]
        stream.append((p - 1) % 29)
    return stream

def main():
    # Load verified keys
    keys_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'verified_keys.json')
    with open(keys_file, 'r') as f:
        verified_keys = json.load(f)
    
    print("=" * 80)
    print("F-SKIP VERIFIED KEY SOLVER + SINGLE-RUNE WORD ANALYSIS")
    print("=" * 80)
    
    # Test pages 21-30 first (high priority), then 31-54
    test_pages = list(range(21, 55))
    
    best_results = []
    
    for page_num in test_pages:
        rune_indices, words, word_positions = get_page_rune_data(page_num)
        if rune_indices is None:
            print(f"\nPage {page_num}: No rune data found, skipping")
            continue
        
        # Count single-rune words
        single_rune_words = [(i, w[0], word_positions[i]) for i, w in enumerate(words) if len(w) == 1]
        
        key_str = str(page_num)
        if key_str not in verified_keys:
            print(f"\nPage {page_num}: No verified key, skipping")
            continue
        
        key = verified_keys[key_str]
        key_len = len(key)
        
        print(f"\n{'='*60}")
        print(f"PAGE {page_num} | {len(rune_indices)} runes | {len(words)} words | "
              f"{len(single_rune_words)} single-rune words | key len {key_len}")
        print(f"{'='*60}")
        
        # Test all modes with and without F-skip
        modes = [
            ("SUB", decrypt_vigenere_sub),
            ("ADD", decrypt_vigenere_add),
            ("BEAUFORT", decrypt_beaufort),
        ]
        
        for mode_name, decrypt_fn in modes:
            for f_skip in [False, True]:
                skip_str = "+FSKIP" if f_skip else ""
                plain_indices = decrypt_fn(rune_indices, key, f_skip=f_skip)
                
                ioc = compute_ioc(plain_indices)
                text = indices_to_text(plain_indices)
                
                # Check single-rune words
                srw_match = 0
                for wi, cipher_val, rune_pos in single_rune_words:
                    # For F-skip, the actual key position depends on history
                    # Use the full decryption
                    plain_val = plain_indices[rune_pos]
                    if plain_val == 10 or plain_val == 24:
                        srw_match += 1
                
                srw_total = len(single_rune_words)
                word_count = count_english_words(text, COMMON_WORDS)
                
                if ioc > 1.3 or srw_match > srw_total * 0.5 or word_count >= 3:
                    print(f"\n  {mode_name}{skip_str}: IoC={ioc:.2f} | SRW={srw_match}/{srw_total} | "
                          f"EngWords={word_count}")
                    # Show first 200 chars of text
                    print(f"  Text: {text[:200]}")
                    
                    best_results.append({
                        'page': page_num,
                        'mode': f"{mode_name}{skip_str}",
                        'ioc': ioc,
                        'srw': f"{srw_match}/{srw_total}",
                        'eng_words': word_count,
                        'text_preview': text[:100]
                    })
    
    # === SINGLE-RUNE WORD KEYSTREAM ANALYSIS ===
    print(f"\n\n{'='*80}")
    print("SINGLE-RUNE WORD KEYSTREAM CONSTRAINT ANALYSIS")
    print(f"{'='*80}")
    
    for page_num in test_pages:
        rune_indices, words, word_positions = get_page_rune_data(page_num)
        if rune_indices is None:
            continue
        
        single_rune_words = [(i, w[0], word_positions[i]) for i, w in enumerate(words) if len(w) == 1]
        if len(single_rune_words) < 3:
            continue
        
        print(f"\nPage {page_num}: {len(single_rune_words)} single-rune words")
        
        # For each single-rune word, compute possible key values for SUB mode
        # plain = (cipher - key) % 29
        # If plain = I (10): key = (cipher - 10) % 29
        # If plain = A (24): key = (cipher - 24) % 29
        for wi, cipher_val, rune_pos in single_rune_words:
            key_if_I = (cipher_val - 10) % 29
            key_if_A = (cipher_val - 24) % 29
            print(f"  pos={rune_pos:3d} cipher={cipher_val:2d} ({GP[cipher_val][1]:3s}) "
                  f"-> key_if_I={key_if_I:2d} key_if_A={key_if_A:2d}")
        
        # Check: do the key values match prime-totient stream?
        for start_offset in range(0, 200, 50):
            stream = prime_totient_stream(len(rune_indices) + 10, start_idx=start_offset)
            matches_I = 0
            matches_A = 0
            matches_either = 0
            for wi, cipher_val, rune_pos in single_rune_words:
                key_if_I = (cipher_val - 10) % 29
                key_if_A = (cipher_val - 24) % 29
                stream_val = stream[rune_pos] if rune_pos < len(stream) else -1
                if stream_val == key_if_I:
                    matches_I += 1
                    matches_either += 1
                elif stream_val == key_if_A:
                    matches_A += 1
                    matches_either += 1
            
            if matches_either > 1:
                print(f"  Prime-totient(offset={start_offset}): {matches_either}/{len(single_rune_words)} "
                      f"matches (I:{matches_I} A:{matches_A})")
        
        # Check: key values consistent with repeating key of length 71 or 83?
        for key_len in [71, 83]:
            # Group single-rune words by position mod key_len
            groups = {}
            for wi, cipher_val, rune_pos in single_rune_words:
                mod_pos = rune_pos % key_len
                key_if_I = (cipher_val - 10) % 29
                key_if_A = (cipher_val - 24) % 29
                if mod_pos not in groups:
                    groups[mod_pos] = []
                groups[mod_pos].append((key_if_I, key_if_A))
            
            # Check consistency within groups
            consistent = True
            for mod_pos, candidates in groups.items():
                if len(candidates) > 1:
                    # All entries must share at least one common value
                    possible_keys = set(candidates[0])
                    for c in candidates[1:]:
                        possible_keys &= set(c)
                    if not possible_keys:
                        consistent = False
                        break
            
            if consistent and len(groups) > 0:
                n_constrained = sum(1 for g in groups.values() if len(g) > 1)
                print(f"  Key-len {key_len}: CONSISTENT | {len(groups)} key positions constrained, "
                      f"{n_constrained} with multiple constraints")
    
    # === PRIME TOTIENT STREAM DIRECT TEST ===
    print(f"\n\n{'='*80}")
    print("PRIME TOTIENT STREAM DIRECT TEST (P56 method)")
    print(f"{'='*80}")
    
    for page_num in test_pages:
        rune_indices, words, word_positions = get_page_rune_data(page_num)
        if rune_indices is None:
            continue
        
        single_rune_words = [(i, w[0], word_positions[i]) for i, w in enumerate(words) if len(w) == 1]
        
        best_offset = -1
        best_srw = 0
        best_ioc = 0
        
        for start_offset in range(0, 1000):
            stream = prime_totient_stream(len(rune_indices), start_idx=start_offset)
            # Decrypt: plain = (cipher - stream) % 29
            plain = [(c - s) % 29 for c, s in zip(rune_indices, stream)]
            
            # Quick check: count single-rune word matches
            srw_match = 0
            for wi, cipher_val, rune_pos in single_rune_words:
                if rune_pos < len(plain):
                    if plain[rune_pos] == 10 or plain[rune_pos] == 24:
                        srw_match += 1
            
            if srw_match > best_srw or (srw_match == best_srw and start_offset == 0):
                best_srw = srw_match
                best_offset = start_offset
                ioc = compute_ioc(plain)
                best_ioc = ioc
        
        if best_srw > 0 or page_num <= 30:
            stream = prime_totient_stream(len(rune_indices), start_idx=best_offset)
            plain = [(c - s) % 29 for c, s in zip(rune_indices, stream)]
            text = indices_to_text(plain)
            ioc = compute_ioc(plain)
            print(f"\n  Page {page_num}: Best offset={best_offset} SRW={best_srw}/{len(single_rune_words)} "
                  f"IoC={ioc:.2f}")
            if best_srw >= 3 or ioc > 1.3:
                print(f"  Text: {text[:150]}")
    
    # === SUMMARY ===
    print(f"\n\n{'='*80}")
    print("BEST RESULTS SUMMARY")
    print(f"{'='*80}")
    
    if best_results:
        best_results.sort(key=lambda x: x['ioc'], reverse=True)
        for r in best_results[:20]:
            print(f"  Page {r['page']:2d} | {r['mode']:15s} | IoC={r['ioc']:.2f} | "
                  f"SRW={r['srw']} | EngWords={r['eng_words']}")
            print(f"    {r['text_preview']}")
    else:
        print("  No results met the threshold criteria.")

if __name__ == '__main__':
    main()
