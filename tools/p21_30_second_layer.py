#!/usr/bin/env python3
"""
P21-30 Second Layer Analysis.
Step 1: Apply known keywords with proper F-skip handling.
Step 2: Check singleton constraint.
Step 3: Try prime-based rearrangement and other transpositions.
"""

import sys, os, math, time
from collections import Counter
from pathlib import Path

N = 29

RUNES = list("\u16A0\u16A2\u16A6\u16A9\u16B1\u16B3\u16B7\u16B9\u16BB\u16BE\u16C1\u16C4\u16C7\u16C8\u16C9\u16CB\u16CF\u16D2\u16D6\u16D7\u16DA\u16DD\u16DF\u16DE\u16AA\u16AB\u16A3\u16E1\u16E0")
RUNEGLISH = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X",
             "S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]
GP = {r: i for i, r in enumerate(RUNES)}
SEPS_CHARS = set(".-\u2022 \n")

# Keywords from P63 and their modes (from MASTER_TRACKER)
PAGE_KEYS = {
    21: ("CABAL", "beaufort"),
    22: ("DIVINITY", "beaufort"),
    23: ("ENCRYPTION", "add"),
    24: ("OBSCURA", "beaufort"),
    25: ("CABAL", "beaufort"),
    26: ("ENCRYPT", "add"),
    27: ("SHADOWS", "add"),
    28: ("DEOR", "sub"),
    29: ("TOTIENT", "beaufort"),
    30: ("MOURNFUL", "add"),
}

# GP digraph parsing for keywords
DIGRAPHS = {"TH":2, "EO":12, "NG":21, "OE":22, "AE":25, "IA":27, "EA":28}
SINGLES_MAP = {"F":0, "U":1, "O":3, "R":4, "C":5, "G":6, "W":7, "H":8, "N":9,
               "I":10, "J":11, "P":13, "X":14, "S":15, "T":16, "B":17, "E":18,
               "M":19, "L":20, "D":23, "A":24, "Y":26}

def parse_keyword(word):
    """Parse a keyword into GP indices, handling digraphs."""
    indices = []
    word = word.upper()
    i = 0
    while i < len(word):
        if i+1 < len(word) and word[i:i+2] in DIGRAPHS:
            indices.append(DIGRAPHS[word[i:i+2]])
            i += 2
        elif word[i] in SINGLES_MAP:
            # Handle K -> C, V -> U
            ch = word[i]
            if ch == 'K': ch = 'C'
            if ch == 'V': ch = 'U'
            indices.append(SINGLES_MAP.get(ch, 0))
            i += 1
        else:
            # Unknown char, try direct
            i += 1
    return indices

def load_page_raw(page_num):
    """Load page and return raw text, flat indices, and word structure."""
    path = Path(f"pages/page_{page_num:02d}/runes.txt")
    if not path.exists(): return None, None, None
    text = path.read_text(encoding='utf-8')
    flat = []
    words = []
    current = []
    separators = []  # Track separators between words
    
    for ch in text:
        if ch in GP:
            current.append(GP[ch])
            flat.append(GP[ch])
        elif ch in SEPS_CHARS:
            if current:
                words.append(current)
                current = []
    if current:
        words.append(current)
    
    return text, flat, words

def ioc(vals):
    n = len(vals)
    if n < 2: return 0.0
    freq = Counter(vals)
    return sum(f*(f-1) for f in freq.values()) * N / (n*(n-1))

def decrypt_vigenere(flat, key, mode):
    """Standard Vigenère/Beaufort decryption without F-skip."""
    result = []
    kl = len(key)
    for i, c in enumerate(flat):
        k = key[i % kl]
        if mode == "sub":
            result.append((c - k) % N)
        elif mode == "add":
            result.append((c + k) % N)
        else:  # beaufort
            result.append((k - c) % N)
    return result

def decrypt_with_fskip(flat, key, mode, fskip_mask):
    """
    Vigenère with F-skip: for positions in fskip_mask,
    output F (0) directly and don't advance key counter.
    """
    result = []
    ki = 0
    kl = len(key)
    for i, c in enumerate(flat):
        if i in fskip_mask:
            result.append(0)  # F
            # Don't advance key counter
        else:
            k = key[ki % kl]
            if mode == "sub":
                result.append((c - k) % N)
            elif mode == "add":
                result.append((c + k) % N)
            else:  # beaufort
                result.append((k - c) % N)
            ki += 1
    return result

def vals_to_runeglish(vals, words):
    """Convert flat decrypted values back to runeglish words."""
    pos = 0
    result = []
    for w in words:
        rg = ''.join(RUNEGLISH[vals[pos+i]] for i in range(len(w)))
        result.append(rg)
        pos += len(w)
    return result

def check_singletons(vals, words):
    """Check which single-rune words decrypt to I (10) or A (24)."""
    pos = 0
    total = 0
    passing = 0
    details = []
    for w in words:
        if len(w) == 1:
            total += 1
            v = vals[pos]
            ok = v in (10, 24)
            if ok: passing += 1
            details.append((pos, v, RUNEGLISH[v], ok))
        pos += len(w)
    return total, passing, details

def get_primes_up_to(n):
    """Sieve of Eratosthenes."""
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n+1, i):
                sieve[j] = False
    return [i for i in range(n+1) if sieve[i]]

def rearrange_by_primes(text_vals, nr):
    """Extract characters at prime and non-prime indices."""
    primes_set = set(get_primes_up_to(nr))
    prime_chars = [text_vals[i] for i in range(nr) if i in primes_set]
    nonprime_chars = [text_vals[i] for i in range(nr) if i not in primes_set]
    
    # Also try 1-indexed primes
    prime_chars_1 = [text_vals[i] for i in range(nr) if (i+1) in primes_set]
    nonprime_chars_1 = [text_vals[i] for i in range(nr) if (i+1) not in primes_set]
    
    # Interleave: prime then nonprime
    interleaved = prime_chars + nonprime_chars
    interleaved_1 = prime_chars_1 + nonprime_chars_1
    
    # Reverse: nonprime then prime
    rev_interleaved = nonprime_chars + prime_chars
    
    return {
        'prime_0idx': prime_chars,
        'nonprime_0idx': nonprime_chars,
        'prime_1idx': prime_chars_1,
        'interleaved_0': interleaved,
        'interleaved_1': interleaved_1,
        'rev_interleaved': rev_interleaved,
    }

def unscramble_by_primes(text_vals, nr):
    """Try using prime indices as a permutation to unscramble."""
    primes = get_primes_up_to(nr * 2)
    results = {}
    
    # Method: read positions in order given by primes mod nr
    for offset in range(10):
        perm = [(primes[i + offset]) % nr for i in range(nr)]
        # Check if it's a valid permutation (all unique)
        if len(set(perm)) == nr:
            results[f'prime_perm_off{offset}'] = [text_vals[p] for p in perm]
    
    # Method: positions sorted by (prime[i] mod nr)
    idx_prime_pairs = [(primes[i] % nr, i) for i in range(nr)]
    idx_prime_pairs.sort()
    perm = [p[1] for p in idx_prime_pairs]
    if len(set(perm)) == nr:
        results['prime_sort_perm'] = [text_vals[p] for p in perm]
    
    return results

def columnar_transposition(text_vals, width):
    """Read text into grid row by row, read out column by column."""
    nr = len(text_vals)
    rows = (nr + width - 1) // width
    # Pad with -1
    padded = text_vals + [-1] * (rows * width - nr)
    
    result = []
    for col in range(width):
        for row in range(rows):
            v = padded[row * width + col]
            if v >= 0:
                result.append(v)
    return result

def reverse_columnar(text_vals, width):
    """Assume text was written column-by-column, read row-by-row."""
    nr = len(text_vals)
    rows = (nr + width - 1) // width
    full_cols = nr % width if nr % width != 0 else width
    
    result = []
    cols_data = []
    idx = 0
    for col in range(width):
        col_len = rows if col < full_cols else rows - 1
        cols_data.append(text_vals[idx:idx+col_len])
        idx += col_len
    
    for row in range(rows):
        for col in range(width):
            if row < len(cols_data[col]):
                result.append(cols_data[col][row])
    return result

def spiral_read(text_vals, width):
    """Read text in spiral order from a grid."""
    nr = len(text_vals)
    rows = (nr + width - 1) // width
    padded = text_vals + [-1] * (rows * width - nr)
    grid = [padded[i*width:(i+1)*width] for i in range(rows)]
    
    result = []
    top, bottom, left, right = 0, rows-1, 0, width-1
    while top <= bottom and left <= right:
        for c in range(left, right+1):
            if grid[top][c] >= 0: result.append(grid[top][c])
        top += 1
        for r in range(top, bottom+1):
            if grid[r][right] >= 0: result.append(grid[r][right])
        right -= 1
        if top <= bottom:
            for c in range(right, left-1, -1):
                if grid[bottom][c] >= 0: result.append(grid[bottom][c])
            bottom -= 1
        if left <= right:
            for r in range(bottom, top-1, -1):
                if grid[r][left] >= 0: result.append(grid[r][left])
            left += 1
    return result

def score_text(vals):
    """Score based on common English patterns."""
    # Common English bigrams in GP
    score = 0
    bigrams = {
        (16,8): 50, (8,18): 40, (10,9): 30, (18,4): 25, (24,9): 30,
        (9,23): 25, (16,10): 20, (10,16): 18, (10,15): 15,
        (24,20): 15, (15,16): 20, (18,9): 15, (24,16): 18,
        (16,18): 15, (8,24): 12, (18,15): 12, (3,0): 12,
        (0,3): 10, (4,18): 10, (24,4): 10, (16,3): 10,
        (24,9): 20, (9,3): 10, (10,20): 10, (18,24): 10,
    }
    for i in range(len(vals)-1):
        score += bigrams.get((vals[i], vals[i+1]), 0)
    return score

def vals_to_text(vals):
    return ''.join(RUNEGLISH[v] for v in vals)

def main():
    os.chdir(Path(__file__).parent.parent)
    
    print("=" * 70)
    print("P21-30 SECOND LAYER ANALYSIS")
    print("=" * 70)
    
    primes = get_primes_up_to(5000)
    prime_set = set(primes)
    
    for pn in range(21, 31):
        keyword, mode = PAGE_KEYS[pn]
        key = parse_keyword(keyword)
        
        text, flat, words = load_page_raw(pn)
        if flat is None:
            print(f"\nP{pn}: No data found")
            continue
        
        nr = len(flat)
        
        # Find positions of F rune (index 0) in ciphertext
        f_positions = [i for i, v in enumerate(flat) if v == 0]
        
        print(f"\n{'='*70}")
        print(f"PAGE {pn}: {nr} runes, {len(words)} words")
        print(f"  Keyword: {keyword} = {key} (len {len(key)}), Mode: {mode}")
        print(f"  F-rune positions in ciphertext: {f_positions} ({len(f_positions)} total)")
        
        # === Step 1: Standard Vigenere (no F-skip) ===
        plain_noFS = decrypt_vigenere(flat, key, mode)
        ic_noFS = ioc(plain_noFS)
        total_s, pass_s, details_s = check_singletons(plain_noFS, words)
        rg_words = vals_to_runeglish(plain_noFS, words)
        
        print(f"\n  [No F-skip] IoC={ic_noFS:.4f} | Singles: {pass_s}/{total_s}")
        print(f"    Text: {' '.join(rg_words[:20])}...")
        for pos, v, rg, ok in details_s:
            print(f"    Single@{pos}: {rg} ({'OK' if ok else 'FAIL'})")
        
        # === Step 2: F-skip with all combinations ===
        if len(f_positions) <= 16:
            best_fs = None
            best_fs_score = -1
            
            for mask_bits in range(1 << len(f_positions)):
                fskip_set = set()
                for j in range(len(f_positions)):
                    if (mask_bits >> j) & 1:
                        fskip_set.add(f_positions[j])
                
                plain_fs = decrypt_with_fskip(flat, key, mode, fskip_set)
                t, p, d = check_singletons(plain_fs, words)
                
                # Only consider if ALL singletons pass
                if p == t and t > 0:
                    ic_fs = ioc(plain_fs)
                    bg = score_text(plain_fs)
                    sc = ic_fs * 100 + bg * 0.5
                    if sc > best_fs_score:
                        best_fs_score = sc
                        best_fs = {
                            'mask': fskip_set,
                            'plain': plain_fs,
                            'ioc': ic_fs,
                            'bg': bg,
                            'score': sc,
                            'singleton_details': d,
                        }
            
            if best_fs:
                rg = vals_to_runeglish(best_fs['plain'], words)
                print(f"\n  [Best F-skip (all singles pass)] IoC={best_fs['ioc']:.4f} bg={best_fs['bg']} score={best_fs['score']:.1f}")
                print(f"    F-skip at: {sorted(best_fs['mask'])}")
                print(f"    Text: {' '.join(rg[:20])}...")
                for pos, v, rl, ok in best_fs['singleton_details']:
                    print(f"    Single@{pos}: {rl}")
            else:
                # No F-skip combo makes all singletons pass
                # Find best by IoC alone
                best_ic = ic_noFS
                best_mask = set()
                for mask_bits in range(1 << len(f_positions)):
                    fskip_set = set()
                    for j in range(len(f_positions)):
                        if (mask_bits >> j) & 1:
                            fskip_set.add(f_positions[j])
                    plain_fs = decrypt_with_fskip(flat, key, mode, fskip_set)
                    ic_fs = ioc(plain_fs)
                    if ic_fs > best_ic:
                        best_ic = ic_fs
                        best_mask = fskip_set
                
                if best_mask:
                    plain_best = decrypt_with_fskip(flat, key, mode, best_mask)
                    rg = vals_to_runeglish(plain_best, words)
                    t2, p2, d2 = check_singletons(plain_best, words)
                    print(f"\n  [Best IoC F-skip] IoC={best_ic:.4f} (mask: {sorted(best_mask)})")
                    print(f"    Singles: {p2}/{t2}")
                    print(f"    Text: {' '.join(rg[:20])}...")
                else:
                    print(f"\n  [F-skip] No improvement found. {2**len(f_positions)} combos tested.")
        else:
            print(f"\n  [F-skip] Too many F positions ({len(f_positions)}) — skipping exhaustive search")
        
        # === Step 3: Second-layer analysis on no-F-skip result ===
        print(f"\n  --- Second-layer transforms (on standard Vigenere result) ---")
        
        # 3a: Prime-indexed extraction
        rearr = rearrange_by_primes(plain_noFS, nr)
        for name, vals in rearr.items():
            if len(vals) > 5:
                ic_r = ioc(vals)
                if ic_r > 1.3:
                    print(f"    {name}: IoC={ic_r:.4f} | {vals_to_text(vals[:30])}...")
        
        # 3b: Columnar transposition with various widths
        test_widths = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]
        for w in test_widths:
            # Forward columnar
            ct = columnar_transposition(plain_noFS, w)
            ic_ct = ioc(ct)
            bg_ct = score_text(ct)
            if ic_ct > 1.5 and bg_ct > score_text(plain_noFS) * 1.2:
                print(f"    Columnar(w={w}): IoC={ic_ct:.4f} bg={bg_ct} | {vals_to_text(ct[:30])}...")
            
            # Reverse columnar
            rct = reverse_columnar(plain_noFS, w)
            ic_rct = ioc(rct)
            bg_rct = score_text(rct)
            if ic_rct > 1.5 and bg_rct > score_text(plain_noFS) * 1.2:
                print(f"    RevColumnar(w={w}): IoC={ic_rct:.4f} bg={bg_rct} | {vals_to_text(rct[:30])}...")
            
            # Spiral
            sp = spiral_read(plain_noFS, w)
            ic_sp = ioc(sp)
            bg_sp = score_text(sp)
            if ic_sp > 1.5 and bg_sp > score_text(plain_noFS) * 1.2:
                print(f"    Spiral(w={w}): IoC={ic_sp:.4f} bg={bg_sp} | {vals_to_text(sp[:30])}...")
        
        # 3c: Word-level rearrangement by prime order
        rg_words_noFS = vals_to_runeglish(plain_noFS, words)
        word_count = len(rg_words_noFS)
        
        # Read words at prime-indexed positions (0-indexed)
        prime_words_0 = [rg_words_noFS[i] for i in range(word_count) if i in prime_set]
        nonprime_words_0 = [rg_words_noFS[i] for i in range(word_count) if i not in prime_set]
        
        # Read words at prime-indexed positions (1-indexed)
        prime_words_1 = [rg_words_noFS[i] for i in range(word_count) if (i+1) in prime_set]
        nonprime_words_1 = [rg_words_noFS[i] for i in range(word_count) if (i+1) not in prime_set]
        
        print(f"\n    Word rearrangement ({word_count} words):")
        print(f"    Prime words (0-idx): {' '.join(prime_words_0[:15])}...")
        print(f"    Non-prime words (0-idx): {' '.join(nonprime_words_0[:15])}...")
        print(f"    Prime words (1-idx): {' '.join(prime_words_1[:15])}...")
        
        # 3d: Reverse word order
        rev_words = rg_words_noFS[::-1]
        print(f"    Reversed words: {' '.join(rev_words[:15])}...")
        
        # 3e: Magic square path (5x5 grid reading)
        # The 5x5 magic square from P63 might define reading order
        # Magic square positions (1-25, row by row):
        MS_5x5 = [
            [272, 138, 341, 131, 151],
            [366, 199, 130, 320, 18],
            [226, 245, 91, 245, 226],
            [18, 320, 130, 199, 366],
            [151, 131, 341, 138, 272],
        ]
        # Flatten and get ranking (order by value)
        ms_flat = [(MS_5x5[r][c], r*5+c) for r in range(5) for c in range(5)]
        ms_flat.sort()  # Sort by value
        ms_order = [pos for _, pos in ms_flat]  # Reading order
        
        # If word count >= 25, try reading first 25 words in magic-square order
        if word_count >= 25:
            ms_rearranged = [rg_words_noFS[ms_order[i]] for i in range(25)]
            print(f"    Magic square order (first 25 words): {' '.join(ms_rearranged)}")
    
    print(f"\n{'='*70}")
    print("ANALYSIS COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()
