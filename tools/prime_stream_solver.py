#!/usr/bin/env python3
"""
Prime Stream Cipher Solver — Liber Primus Pages 21-54
======================================================
Approach: Based on P55/P56 proven method and community research.
P56 uses: plain[i] = (cipher[i] - (prime[i] - 1)) % 29 = (cipher[i] - φ(prime[i])) % 29

Key idea: The unsolved pages likely use a similar prime-based stream cipher
but with "rearranged" primes (as P19 hints). Test multiple prime orderings:
1. Sequential primes starting from different offsets
2. GP-ordered primes (2,3,5,...,109 then continue)
3. Fibonacci-indexed primes
4. Spiral/magic-square-ordered primes
5. Single-rune word constraint validation

Also test:
- φ(prime) vs prime-1 vs prime itself as keystream values
- MOD 29 vs raw subtraction
- Different starting prime indices
"""

import os
import sys
import json
import math
from pathlib import Path
from collections import Counter, defaultdict
from itertools import product

BASE = Path(__file__).resolve().parent.parent
PAGES_DIR = BASE / "pages"
DATA_DIR = BASE / "data"

# GP Alphabet
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
GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]

# Generate lots of primes
def sieve_primes(n):
    """Sieve of Eratosthenes up to n."""
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n+1, i):
                is_prime[j] = False
    return [i for i in range(2, n+1) if is_prime[i]]

ALL_PRIMES = sieve_primes(50000)  # More than enough
PRIME_SET = set(ALL_PRIMES)

def euler_totient(n):
    """Compute Euler's totient of n."""
    if n <= 1:
        return 1
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

def compute_ioc(indices):
    n = len(indices)
    if n < 2: return 0
    counts = Counter(indices)
    num = sum(c*(c-1) for c in counts.values())
    den = n*(n-1)
    return 29 * num / den if den > 0 else 0

def to_runeglish(indices):
    return ''.join(IDX_TO_LETTER[i] for i in indices)

def load_page_structured(page_num):
    """Load page with structure: returns list of (position, rune_idx, is_single_word)."""
    rune_file = PAGES_DIR / f"page_{page_num:02d}" / "runes.txt"
    if not rune_file.exists():
        return None
    with open(rune_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse structure
    rune_indices = []
    rune_positions = []  # Global position of each rune
    word_lengths = []
    current_word_len = 0
    word_start_positions = []  # Position where each word starts
    single_rune_word_positions = []  # Rune positions that are single-rune words
    
    pos = 0
    word_start = 0
    
    separators = set('-.\n /&$%•')  # Include • (bullet) as separator
    
    for ch in content:
        if ch in RUNE_TO_IDX:
            rune_indices.append(RUNE_TO_IDX[ch])
            rune_positions.append(pos)
            current_word_len += 1
            pos += 1
        elif ch in separators or ch == '"':
            if current_word_len > 0:
                if current_word_len == 1:
                    single_rune_word_positions.append(pos - 1)
                word_lengths.append(current_word_len)
                current_word_len = 0
    
    if current_word_len > 0:
        if current_word_len == 1:
            single_rune_word_positions.append(pos - 1)
        word_lengths.append(current_word_len)
    
    return {
        'indices': rune_indices,
        'content': content,
        'single_rune_positions': single_rune_word_positions,
        'word_lengths': word_lengths,
        'num_runes': len(rune_indices),
    }

# ========== PRIME SEQUENCE GENERATORS ==========

def sequential_primes(start_idx, length):
    """Primes starting from the start_idx-th prime."""
    return ALL_PRIMES[start_idx:start_idx + length]

def fibonacci_indexed_primes(length):
    """Primes at Fibonacci-numbered positions."""
    fib = [0, 1]
    while fib[-1] < len(ALL_PRIMES):
        fib.append(fib[-1] + fib[-2])
    
    result = []
    fib_idx = 0
    while len(result) < length:
        if fib_idx < len(fib) and fib[fib_idx] < len(ALL_PRIMES):
            result.append(ALL_PRIMES[fib[fib_idx]])
        else:
            break
        fib_idx += 1
    
    # If we run out of Fibonacci indices, cycle
    if len(result) < length:
        cycle = result[:]
        while len(result) < length:
            result.extend(cycle)
        result = result[:length]
    
    return result

def gp_primes_extended(length):
    """Start with GP primes (2-109), then continue with next primes."""
    result = list(GP_PRIMES)
    if length <= len(result):
        return result[:length]
    # Continue from 113 onwards
    idx = ALL_PRIMES.index(109) + 1
    while len(result) < length and idx < len(ALL_PRIMES):
        result.append(ALL_PRIMES[idx])
        idx += 1
    return result[:length]

def reversed_gp_primes(length):
    """GP primes in reverse order, then continue."""
    result = list(reversed(GP_PRIMES))
    if len(result) < length:
        idx = ALL_PRIMES.index(109) + 1
        while len(result) < length and idx < len(ALL_PRIMES):
            result.append(ALL_PRIMES[idx])
            idx += 1
    return result[:length]

def prime_of_prime(length):
    """p(p(i)) — prime at prime-indexed positions."""
    result = []
    i = 0
    while len(result) < length and i < len(ALL_PRIMES):
        pidx = ALL_PRIMES[i]
        if pidx < len(ALL_PRIMES):
            result.append(ALL_PRIMES[pidx])
        i += 1
    return result[:length] if result else ALL_PRIMES[:length]

def totient_ordered_primes(length):
    """Primes ordered by their totient function values."""
    # For primes, φ(p) = p-1, so this is just sequential order
    # Instead, use φ(composite) values to reorder
    return ALL_PRIMES[:length]

def spiral_ordered_primes(length):
    """Primes reordered using the Fibonacci spiral from the 4x4 grid."""
    # Grid ordinal positions from Fibonacci spiral (ascending):
    # 0,1,2,3,5,8,13,21,34,55,89,144,233,377,610,987
    spiral_indices = [0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]
    result = []
    for idx in spiral_indices:
        if idx < len(ALL_PRIMES):
            result.append(ALL_PRIMES[idx])
    
    # Cycle
    cycle = result[:]
    while len(result) < length:
        result.extend(cycle)
    return result[:length]

def telnet_gap_primes(length):
    """Primes from the telnet gap (73 to 1229)."""
    gap_start = ALL_PRIMES.index(73)
    gap_end = ALL_PRIMES.index(1229) if 1229 in PRIME_SET else len(ALL_PRIMES)
    gap_primes = ALL_PRIMES[gap_start:gap_end]
    
    result = []
    while len(result) < length:
        result.extend(gap_primes)
    return result[:length]

# ========== KEYSTREAM FUNCTIONS ==========

def ks_totient(primes):
    """keystream[i] = φ(prime[i]) % 29 = (prime[i] - 1) % 29 for primes."""
    return [(p - 1) % 29 for p in primes]

def ks_prime_mod29(primes):
    """keystream[i] = prime[i] % 29."""
    return [p % 29 for p in primes]

def ks_prime_index_mod29(primes):
    """keystream[i] = index_of(prime[i]) % 29."""
    prime_to_idx = {p: i for i, p in enumerate(ALL_PRIMES)}
    return [prime_to_idx.get(p, 0) % 29 for p in primes]

def ks_totient_raw(primes):
    """keystream[i] = euler_totient(prime[i]) % 29."""
    return [euler_totient(p) % 29 for p in primes]

# ========== DECRYPTION MODES ==========

def decrypt_stream(cipher, keystream, mode):
    """Decrypt with stream cipher."""
    plain = []
    for i, c in enumerate(cipher):
        if i >= len(keystream):
            break
        k = keystream[i]
        if mode == 'sub':
            p = (c - k) % 29
        elif mode == 'add':
            p = (c + k) % 29
        elif mode == 'beaufort':
            p = (k - c) % 29
        plain.append(p)
    return plain

# ========== SCORING ==========

# English bigram log-probabilities (approximate, for 29-char alphabet)
# Use simple frequency-based scoring
COMMON_WORDS = {'THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','HER','WAS','ONE',
    'OUR','OUT','HAD','HAS','HIS','HOW','ITS','MAY','NEW','NOW','OLD','SEE','WAY','WHO',
    'THIS','THAT','WITH','HAVE','FROM','THEY','BEEN','SAID','EACH','WILL','INTO','THAN',
    'THEM','THEN','WHAT','WHEN','MAKE','LIKE','LONG','LOOK','MANY','SOME','TIME','YOUR',
    'KNOW','JUST','COME','MADE','FIND','ONLY','SELF','BEING','TRUTH','WITHIN','SACRED',
    'WISDOM','FOLLOW','BELIEVE','NOTHING','BOOK','THINGS','SHOULD','PRIMES','TOTIENT',
    'PILGRIM','JOURNEY','TOWARD','THROUGH','DISCOVER','EMERGE','HOLY','INTELLIGENCE',
    'COMMAND','OWN','INSTRUCTION','KOAN','DIVINITY',
    'DEATH','EXPERIENCE','TEST','KNOWLEDGE','PARABLE','INSTAR',
    'SUFFER','STRUGGLE','REALITY','SHAPE','PILGRIMAGE',
    'SHADOWS','VOID','CIRCUMFERENCE','END','WELCOME','WARNING',
    'ENCRYPTION','ENCRYPTED','OBSCURA','FORM',
}

def score_quick(text):
    """Quick score: count common trigrams and words in text."""
    text = text.upper()
    score = 0
    for w in ['THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','OUR','HAS','HIS',
              'WAS','ONE','CAN','HER','OUT','NOW','WHO','WAY','OLD','ITS','MAY']:
        score += text.count(w) * len(w) * 3
    for w in ['THIS','THAT','WITH','HAVE','FROM','THEY','WILL','EACH','BEEN','SAID',
              'INTO','THAN','THEM','WHAT','WHEN','YOUR','SOME','MAKE','FIND','ONLY',
              'KNOW','COME','SELF','JUST','LONG','MANY','TIME','LIKE']:
        score += text.count(w) * len(w) * 4
    for w in ['BEING','TRUTH','WITHIN','WISDOM','SACRED','PRIMES','TOTIENT',
              'FOLLOW','BELIEVE','NOTHING','PILGRIM','JOURNEY','THROUGH',
              'DISCOVER','COMMAND','INSTRUCTION','DIVINITY','DEATH']:
        score += text.count(w) * len(w) * 8
    return score

# ========== SINGLE-RUNE WORD ANALYSIS ==========

def analyze_single_rune_words(page_data, test_name, keystream, mode):
    """Check if keystream values at single-rune word positions produce I or A."""
    cipher = page_data['indices']
    
    # Find single-rune word positions by re-parsing content
    content = page_data['content']
    separators = set('-.\n /&$%•"')
    
    pos = 0
    word_start = -1
    word_len = 0
    single_positions = []
    
    for ch in content:
        if ch in RUNE_TO_IDX:
            if word_len == 0:
                word_start = pos
            word_len += 1
            pos += 1
        elif ch in separators:
            if word_len == 1:
                single_positions.append(word_start)
            word_len = 0
    if word_len == 1:
        single_positions.append(word_start)
    
    matches_i = 0
    matches_a = 0
    total = len(single_positions)
    
    for sp in single_positions:
        if sp >= len(cipher) or sp >= len(keystream):
            continue
        c = cipher[sp]
        k = keystream[sp]
        
        if mode == 'sub':
            p = (c - k) % 29
        elif mode == 'add':
            p = (c + k) % 29
        elif mode == 'beaufort':
            p = (k - c) % 29
        else:
            p = (c - k) % 29
        
        if p == 10:  # I
            matches_i += 1
        elif p == 24:  # A
            matches_a += 1
    
    return matches_i, matches_a, total, single_positions

# ========== F-SKIP STREAM ==========

def decrypt_stream_fskip(content, keystream, mode):
    """Stream cipher with F-skip: if cipher rune is F AND decrypts to F, skip key."""
    cipher_indices = []
    plain = []
    key_pos = 0
    
    for ch in content:
        if ch not in RUNE_TO_IDX:
            continue
        c = RUNE_TO_IDX[ch]
        
        if c == 0 and key_pos < len(keystream):
            # This might be a literal F (skip key)
            # Try decrypting normally first
            k = keystream[key_pos]
            if mode == 'sub':
                p = (c - k) % 29
            elif mode == 'add':
                p = (c + k) % 29
            elif mode == 'beaufort':
                p = (k - c) % 29
            
            if p == 0:  # Decrypts to F = literal F, skip key
                plain.append(0)
                # Don't advance key_pos
            else:
                plain.append(p)
                key_pos += 1
        else:
            if key_pos < len(keystream):
                k = keystream[key_pos]
                if mode == 'sub':
                    p = (c - k) % 29
                elif mode == 'add':
                    p = (c + k) % 29
                elif mode == 'beaufort':
                    p = (k - c) % 29
                plain.append(p)
                key_pos += 1
            else:
                plain.append(c)
    
    return plain

# ========== MAIN ==========

def test_page(page_num, verbose=True):
    """Test all prime stream methods on a page."""
    page_data = load_page_structured(page_num)
    if page_data is None:
        return None
    
    cipher = page_data['indices']
    content = page_data['content']
    n = page_data['num_runes']
    
    results = []
    
    # Prime sequence generators
    generators = {
        'seq': lambda l, off: sequential_primes(off, l),
        'gp_ext': lambda l, off: gp_primes_extended(l),
        'fib_idx': lambda l, off: fibonacci_indexed_primes(l),
        'spiral': lambda l, off: spiral_ordered_primes(l),
        'gap': lambda l, off: telnet_gap_primes(l),
        'rev_gp': lambda l, off: reversed_gp_primes(l),
    }
    
    # Keystream functions
    ks_funcs = {
        'totient': ks_totient,         # φ(p) = p-1 for primes
        'p_mod29': ks_prime_mod29,     # p % 29
        'idx_mod29': ks_prime_index_mod29,  # index(p) % 29
    }
    
    modes = ['sub', 'add', 'beaufort']
    
    # Test sequential primes at various offsets
    for offset in list(range(0, 30)) + list(range(30, 500, 10)) + [1000, 2000, 3000, 5000]:
        if offset + n >= len(ALL_PRIMES):
            continue
        
        for ks_name, ks_func in ks_funcs.items():
            primes = sequential_primes(offset, n)
            keystream = ks_func(primes)
            
            for mode in modes:
                plain = decrypt_stream(cipher, keystream, mode)
                ioc = compute_ioc(plain)
                text = to_runeglish(plain)
                score = score_quick(text)
                
                # Check single-rune words
                mi, ma, total_sw, _ = analyze_single_rune_words(page_data, '', keystream, mode)
                
                if ioc > 1.2 or score > 100 or (total_sw > 0 and (mi + ma) > total_sw * 0.5):
                    results.append((f'seq_off{offset}_{ks_name}_{mode}', ioc, score, 
                                  mi, ma, total_sw, text[:100]))
                
                # Also test with F-skip
                plain_fs = decrypt_stream_fskip(content, keystream, mode)
                ioc_fs = compute_ioc(plain_fs)
                text_fs = to_runeglish(plain_fs)
                score_fs = score_quick(text_fs)
                
                if ioc_fs > 1.2 or score_fs > 100:
                    results.append((f'seq_off{offset}_{ks_name}_{mode}_fskip', ioc_fs, score_fs,
                                  0, 0, 0, text_fs[:100]))
    
    # Test non-sequential orderings
    for gen_name, gen_func in generators.items():
        if gen_name == 'seq':
            continue  # Already tested above
        
        primes = gen_func(n, 0)
        if len(primes) < n:
            continue
        
        for ks_name, ks_func in ks_funcs.items():
            keystream = ks_func(primes)
            
            for mode in modes:
                plain = decrypt_stream(cipher, keystream, mode)
                ioc = compute_ioc(plain)
                text = to_runeglish(plain)
                score = score_quick(text)
                mi, ma, total_sw, _ = analyze_single_rune_words(page_data, '', keystream, mode)
                
                results.append((f'{gen_name}_{ks_name}_{mode}', ioc, score,
                              mi, ma, total_sw, text[:100]))
    
    # Sort by combined metric
    results.sort(key=lambda x: -(x[2] + x[1] * 30 + (x[3] + x[4]) * 20))
    
    if verbose:
        print(f"\n{'='*120}")
        print(f"PAGE {page_num:02d} — {n} runes, {len(page_data['word_lengths'])} words")
        
        # Show single-rune word info
        content = page_data['content']
        separators = set('-.\n /&$%•"')
        pos = 0
        word_len = 0
        singles = []
        for ch in content:
            if ch in RUNE_TO_IDX:
                if word_len == 0:
                    word_start_pos = pos
                word_len += 1
                pos += 1
            elif ch in separators:
                if word_len == 1:
                    singles.append((word_start_pos, cipher[word_start_pos]))
                word_len = 0
        if word_len == 1:
            singles.append((word_start_pos, cipher[word_start_pos]))
        
        print(f"  Single-rune words: {len(singles)}")
        for sp, sc in singles[:10]:
            # For each, show what key value is needed for I vs A
            ki = (sc - 10) % 29
            ka = (sc - 24) % 29
            print(f"    pos={sp}: cipher={IDX_TO_LETTER[sc]}({sc}) → need key={ki} for I, key={ka} for A")
        
        print(f"{'='*120}")
        print(f"{'Method':<50} {'IoC':>7} {'Score':>6} {'I':>3} {'A':>3} {'Tot':>3} | Text")
        print("-" * 120)
        
        for method, ioc, score, mi, ma, tsw, text in results[:25]:
            ia_pct = f"{(mi+ma)*100//tsw}%" if tsw > 0 else "n/a"
            print(f"{method:<50} {ioc:>7.4f} {score:>6} {mi:>3} {ma:>3} {tsw:>3} | {text[:55]}")
    
    return results

def main():
    print("PRIME STREAM CIPHER SOLVER — LIBER PRIMUS")
    print("=" * 120)
    print(f"Primes available: {len(ALL_PRIMES)} (up to {ALL_PRIMES[-1]})")
    
    # Focus on key pages with word boundaries first (not P23/P25 which lack hyphens)
    priority_pages = [21, 22, 24, 26, 27, 28, 29, 30]
    
    all_results = {}
    for pg in priority_pages:
        results = test_page(pg)
        if results:
            all_results[pg] = results
    
    # Summary
    print(f"\n\n{'='*120}")
    print("BEST RESULTS PER PAGE")
    print("=" * 120)
    for pg in sorted(all_results.keys()):
        if all_results[pg]:
            best = all_results[pg][0]
            method, ioc, score, mi, ma, tsw, text = best
            print(f"P{pg:02d}: {method:<45} IoC={ioc:.4f} Score={score:>5} I/A={mi+ma}/{tsw}")
    
    # Deeper analysis: What key values does each single-rune word need?
    print(f"\n\n{'='*120}")
    print("SINGLE-RUNE WORD KEYSTREAM ANALYSIS")
    print("=" * 120)
    
    for pg in priority_pages:
        page_data = load_page_structured(pg)
        if page_data is None:
            continue
        
        cipher = page_data['indices']
        content = page_data['content']
        
        separators = set('-.\n /&$%•"')
        pos = 0
        word_len = 0
        singles = []
        
        for ch in content:
            if ch in RUNE_TO_IDX:
                if word_len == 0:
                    ws = pos
                word_len += 1
                pos += 1
            elif ch in separators:
                if word_len == 1:
                    singles.append((ws, cipher[ws]))
                word_len = 0
        if word_len == 1:
            singles.append((ws, cipher[ws]))
        
        if not singles:
            print(f"\nP{pg:02d}: No single-rune words")
            continue
        
        print(f"\nP{pg:02d} ({len(singles)} single-rune words):")
        print(f"  {'Pos':>5} {'Cipher':>8} {'Key_I':>6} {'Key_A':>6}")
        
        key_for_I = []
        key_for_A = []
        
        for sp, sc in singles:
            ki = (sc - 10) % 29  # key needed for plaintext = I
            ka = (sc - 24) % 29  # key needed for plaintext = A
            key_for_I.append((sp, ki))
            key_for_A.append((sp, ka))
            print(f"  {sp:>5} {IDX_TO_LETTER[sc]:>8}({sc:>2}) {ki:>6} {ka:>6}")
        
        # Check if key values for "all I" or "all A" match any prime sequence
        print(f"\n  Testing if key_for_I matches φ(prime[pos]) at sequential offsets:")
        
        best_match_offset = -1
        best_match_count = 0
        
        for offset in range(0, 2000):
            match_i = 0
            match_a = 0
            for sp, ki in key_for_I:
                if offset + sp < len(ALL_PRIMES):
                    expected = (ALL_PRIMES[offset + sp] - 1) % 29
                    if expected == ki:
                        match_i += 1
            for sp, ka in key_for_A:
                if offset + sp < len(ALL_PRIMES):
                    expected = (ALL_PRIMES[offset + sp] - 1) % 29
                    if expected == ka:
                        match_a += 1
            
            total_match = max(match_i, match_a)
            if total_match > best_match_count:
                best_match_count = total_match
                best_match_offset = offset
                best_mode = 'I' if match_i >= match_a else 'A'
        
        print(f"  Best: offset={best_match_offset}, matches={best_match_count}/{len(singles)} ({best_mode})")
        
        # Also check p%29 keystream
        best_match_offset2 = -1
        best_match_count2 = 0
        
        for offset in range(0, 2000):
            match_i = 0
            match_a = 0
            for sp, ki in key_for_I:
                if offset + sp < len(ALL_PRIMES):
                    expected = ALL_PRIMES[offset + sp] % 29
                    if expected == ki:
                        match_i += 1
            for sp, ka in key_for_A:
                if offset + sp < len(ALL_PRIMES):
                    expected = ALL_PRIMES[offset + sp] % 29
                    if expected == ka:
                        match_a += 1
            
            total_match2 = max(match_i, match_a)
            if total_match2 > best_match_count2:
                best_match_count2 = total_match2
                best_match_offset2 = offset
                best_mode2 = 'I' if match_i >= match_a else 'A'
        
        print(f"  p%29: offset={best_match_offset2}, matches={best_match_count2}/{len(singles)} ({best_mode2})")

if __name__ == '__main__':
    main()
