#!/usr/bin/env python3
"""
P21-30 Keyword Decryption + Rearrangement Solver

After keyword Vigenère, letters are correct but order is wrong.
P19 hint: "REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR K"
This script applies correct keywords, then tests prime-based rearrangements.
"""

import os, sys, math
from collections import Counter
from itertools import combinations

# Gematria Primus
GP_RUNE_TO_IDX = {
    'ᚠ':0, 'ᚢ':1, 'ᚦ':2, 'ᚩ':3, 'ᚱ':4, 'ᚳ':5, 'ᚷ':6, 'ᚹ':7,
    'ᚻ':8, 'ᚾ':9, 'ᛁ':10, 'ᛄ':11, 'ᛇ':12, 'ᛈ':13, 'ᛉ':14, 'ᛋ':15,
    'ᛏ':16, 'ᛒ':17, 'ᛖ':18, 'ᛗ':19, 'ᛚ':20, 'ᛝ':21, 'ᛟ':22, 'ᛞ':23,
    'ᚪ':24, 'ᚫ':25, 'ᚣ':26, 'ᛡ':27, 'ᛠ':28
}

IDX_TO_LATIN = {
    0:'F', 1:'U', 2:'TH', 3:'O', 4:'R', 5:'C', 6:'G', 7:'W',
    8:'H', 9:'N', 10:'I', 11:'J', 12:'EO', 13:'P', 14:'X', 15:'S',
    16:'T', 17:'B', 18:'E', 19:'M', 20:'L', 21:'NG', 22:'OE', 23:'D',
    24:'A', 25:'AE', 26:'Y', 27:'IA', 28:'EA'
}

GP_PRIMES = {
    0:2, 1:3, 2:5, 3:7, 4:11, 5:13, 6:17, 7:19, 8:23, 9:29,
    10:31, 11:37, 12:41, 13:43, 14:47, 15:53, 16:59, 17:61, 18:67,
    19:71, 20:73, 21:79, 22:83, 23:89, 24:97, 25:101, 26:103, 27:107, 28:109
}

# Keywords and modes for P21-30
PAGE_CONFIG = {
    21: ('CABAL',    'beaufort', [5, 24, 17, 24, 20]),
    22: ('DIVINITY', 'beaufort', [23, 10, 1, 10, 9, 10, 16, 26]),
    23: ('ENCRYPTION','add',    [18, 9, 5, 4, 26, 13, 16, 10, 3, 9]),
    24: ('OBSCURA',  'beaufort', [3, 17, 15, 5, 1, 4, 24]),
    25: ('CABAL',    'beaufort', [5, 24, 17, 24, 20]),
    26: ('ENCRYPT',  'add',     [18, 9, 5, 4, 26, 13, 16]),
    27: ('SHADOWS',  'add',     [15, 8, 24, 23, 3, 7, 15]),
    28: ('DEOR',     'sub',     [23, 18, 3, 4]),
    29: ('TOTIENT',  'beaufort', [16, 3, 16, 10, 18, 9, 16]),
    30: ('MOURNFUL', 'add',     [19, 3, 1, 4, 9, 0, 1, 20]),
}

def load_english_words(path='data/wordlist.txt'):
    """Load English wordlist for scoring."""
    try:
        with open(path) as f:
            words = set(w.strip().upper() for w in f if len(w.strip()) >= 2)
        return words
    except:
        return set()

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i+2) == 0: return False
        i += 6
    return True

def primes_up_to(n):
    """Generate all primes up to n."""
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n+1, i):
                sieve[j] = False
    return [i for i in range(n+1) if sieve[i]]

def fibonacci_up_to(n):
    """Generate Fibonacci numbers up to n."""
    fibs = [1, 2]
    while fibs[-1] < n:
        fibs.append(fibs[-1] + fibs[-2])
    return [f for f in fibs if f <= n]

def parse_runes(text):
    """Parse rune text: extract rune indices and word structure."""
    rune_indices = []
    word_boundaries = []  # list of (start, end) for each word
    current_word_start = 0
    
    i = 0
    chars = list(text)
    pos = 0
    
    for ch in text:
        if ch in GP_RUNE_TO_IDX:
            rune_indices.append(GP_RUNE_TO_IDX[ch])
        elif ch == '-':
            if pos > current_word_start:
                word_boundaries.append((current_word_start, pos))
            current_word_start = pos
        elif ch == '.':
            if pos > current_word_start:
                word_boundaries.append((current_word_start, pos))
            current_word_start = pos
        elif ch in '\n\r':
            continue
        elif ch in '&$%/':
            continue
        else:
            continue  # skip unknown
        pos += 1  # only count rune positions
    
    # Last word
    if pos > current_word_start:
        word_boundaries.append((current_word_start, pos))
    
    return rune_indices

def parse_runes_with_words(text):
    """Parse runes preserving word structure. Returns list of words, each word is list of GP indices."""
    words = []
    current_word = []
    
    for ch in text:
        if ch in GP_RUNE_TO_IDX:
            current_word.append(GP_RUNE_TO_IDX[ch])
        elif ch in '-. \n\r':
            if current_word:
                words.append(current_word)
                current_word = []
        elif ch in '&$%/':
            if current_word:
                words.append(current_word)
                current_word = []
    
    if current_word:
        words.append(current_word)
    
    return words

def decrypt(cipher_indices, key_indices, mode):
    """Apply keyword cipher."""
    result = []
    key_len = len(key_indices)
    key_pos = 0
    
    for ci in cipher_indices:
        k = key_indices[key_pos % key_len]
        if mode == 'beaufort':
            p = (k - ci) % 29
        elif mode == 'add':
            p = (ci + k) % 29
        elif mode == 'sub':
            p = (ci - k) % 29
        else:
            raise ValueError(f"Unknown mode: {mode}")
        result.append(p)
        key_pos += 1
    
    return result

def decrypt_words(cipher_words, key_indices, mode):
    """Decrypt preserving word structure."""
    result_words = []
    key_pos = 0
    key_len = len(key_indices)
    
    for word in cipher_words:
        dec_word = []
        for ci in word:
            k = key_indices[key_pos % key_len]
            if mode == 'beaufort':
                p = (k - ci) % 29
            elif mode == 'add':
                p = (ci + k) % 29
            elif mode == 'sub':
                p = (ci - k) % 29
            dec_word.append(p)
            key_pos += 1
        result_words.append(dec_word)
    
    return result_words

def indices_to_text(indices):
    """Convert GP indices to runeglish text."""
    return ''.join(IDX_TO_LATIN[i] for i in indices)

def words_to_text(words):
    """Convert word list (each word = list of GP indices) to text."""
    return ' '.join(indices_to_text(w) for w in words)

def compute_ioc(indices):
    """Compute Index of Coincidence."""
    if len(indices) < 2:
        return 0
    freq = Counter(indices)
    n = len(indices)
    return 29 * sum(c*(c-1) for c in freq.values()) / (n * (n-1))

def score_text(text, wordlist):
    """Score decoded text by counting English word matches."""
    # Normalize: handle digraphs
    t = text.upper()
    # Apply GP digraph rules for scoring
    t = t.replace('NG', 'NG')  # no change needed
    
    # Split into words
    words = t.split()
    score = 0
    matched = []
    
    for word in words:
        # Direct match
        if word in wordlist:
            score += len(word) ** 2
            matched.append(word)
            continue
        # Try IA -> ION
        w2 = word.replace('IA', 'ION')
        if w2 in wordlist:
            score += len(w2) ** 2
            matched.append(w2)
            continue
        # Try C -> K
        w3 = word.replace('C', 'K')
        if w3 in wordlist:
            score += len(w3) ** 2
            matched.append(w3)
            continue
        # Try U -> V
        w4 = word.replace('U', 'V')
        if w4 in wordlist:
            score += len(w4) ** 2
            matched.append(w4)
            continue
    
    return score, matched

def rearrange_prime_positions(indices, zero_indexed=False):
    """Extract characters at prime positions."""
    primes = set(primes_up_to(len(indices)))
    offset = 0 if zero_indexed else 1
    prime_chars = [indices[i] for i in range(len(indices)) if (i + offset) in primes]
    non_prime = [indices[i] for i in range(len(indices)) if (i + offset) not in primes]
    return prime_chars, non_prime

def rearrange_prime_first(indices, zero_indexed=False):
    """Prime-position chars first, then non-prime."""
    p, np = rearrange_prime_positions(indices, zero_indexed)
    return p + np

def rearrange_prime_interleave(indices, zero_indexed=False):
    """Interleave prime and non-prime position chars."""
    p, np = rearrange_prime_positions(indices, zero_indexed)
    result = []
    pi, ni = 0, 0
    for i in range(len(indices)):
        if i % 2 == 0 and pi < len(p):
            result.append(p[pi]); pi += 1
        elif ni < len(np):
            result.append(np[ni]); ni += 1
        elif pi < len(p):
            result.append(p[pi]); pi += 1
    return result

def rearrange_by_gp_value(indices):
    """Sort characters by their GP prime value."""
    return [x for _, x in sorted(enumerate(indices), key=lambda t: GP_PRIMES[t[1]])]

def rearrange_grid_cols(indices, width):
    """Write into rows of given width, read columns."""
    if width <= 0 or width >= len(indices):
        return indices
    rows = (len(indices) + width - 1) // width
    # Pad with None
    padded = indices + [None] * (rows * width - len(indices))
    result = []
    for col in range(width):
        for row in range(rows):
            v = padded[row * width + col]
            if v is not None:
                result.append(v)
    return result

def rearrange_grid_rows_from_cols(indices, width):
    """Write into columns (top to bottom, left to right), read rows."""
    if width <= 0 or width >= len(indices):
        return indices
    rows = (len(indices) + width - 1) // width
    padded = indices + [None] * (rows * width - len(indices))
    # Write into columns
    grid = [[None]*width for _ in range(rows)]
    pos = 0
    for col in range(width):
        for row in range(rows):
            if pos < len(indices):
                grid[row][col] = indices[pos]
                pos += 1
    # Read rows
    result = []
    for row in range(rows):
        for col in range(width):
            if grid[row][col] is not None:
                result.append(grid[row][col])
    return result

def rearrange_reverse(indices):
    return indices[::-1]

def rearrange_skip(indices, skip):
    """Read every skip-th character."""
    result = []
    visited = set()
    start = 0
    while len(result) < len(indices):
        pos = start
        while pos < len(indices):
            if pos not in visited:
                result.append(indices[pos])
                visited.add(pos)
            pos += skip
        start += 1
        if start >= skip:
            break
    # Add any remaining
    for i in range(len(indices)):
        if i not in visited:
            result.append(indices[i])
    return result

def rearrange_fibonacci_positions(indices):
    """Read at Fibonacci-indexed positions."""
    fibs = set(fibonacci_up_to(len(indices)))
    fib_chars = [indices[i] for i in range(len(indices)) if (i+1) in fibs]
    non_fib = [indices[i] for i in range(len(indices)) if (i+1) not in fibs]
    return fib_chars, non_fib

def rearrange_word_reverse(words):
    """Reverse word order."""
    return words[::-1]

def rearrange_words_prime_indexed(words):
    """Prime-indexed words first, then rest."""
    primes = set(primes_up_to(len(words) + 1))
    pw = [words[i] for i in range(len(words)) if (i+1) in primes]
    npw = [words[i] for i in range(len(words)) if (i+1) not in primes]
    return pw + npw

def rearrange_words_by_length(words):
    """Sort words by length."""
    return sorted(words, key=len)

def rearrange_words_by_gp_sum(words):
    """Sort words by sum of GP prime values."""
    return sorted(words, key=lambda w: sum(GP_PRIMES[i] for i in w))

def rearrange_words_by_first_char(words):
    """Sort words by first character's GP value."""
    return sorted(words, key=lambda w: GP_PRIMES[w[0]] if w else 0)

def read_at_prime_indices(indices):
    """Use prime number sequence as positions to read. p[0]=2nd char, p[1]=3rd char, etc."""
    primes = primes_up_to(len(indices))
    return [indices[p-1] for p in primes if p <= len(indices)]

def undo_columnar_transposition(ct, ncols):
    """Undo a columnar transposition: text was written in columns, read in rows -> reverse: write in rows, read in columns = original."""
    n = len(ct)
    nrows = (n + ncols - 1) // ncols
    # Number of long columns (columns with nrows elements)
    num_long = n - (nrows - 1) * ncols  # or n % ncols if nonzero, else ncols
    if n % ncols == 0:
        num_long = ncols
    else:
        num_long = n % ncols
    
    # Distribute ct into columns
    cols = []
    pos = 0
    for c in range(ncols):
        col_len = nrows if c < num_long else nrows - 1
        cols.append(ct[pos:pos+col_len])
        pos += col_len
    
    # Read rows
    result = []
    for r in range(nrows):
        for c in range(ncols):
            if r < len(cols[c]):
                result.append(cols[c][r])
    return result

def undo_columnar_by_key_order(ct, key_order):
    """Undo columnar transposition with a specific column reading order."""
    ncols = len(key_order)
    n = len(ct)
    nrows = (n + ncols - 1) // ncols
    num_long = n % ncols if n % ncols != 0 else ncols
    
    # The key_order tells us which column was read first
    # Build inverse: inv[key_order[i]] = i (original column position)
    sorted_order = sorted(range(ncols), key=lambda i: key_order[i])
    
    # Distribute ct into columns in key_order
    cols = [[] for _ in range(ncols)]
    pos = 0
    for rank in range(ncols):
        col_idx = sorted_order[rank]
        col_len = nrows if col_idx < num_long else nrows - 1
        cols[col_idx] = ct[pos:pos+col_len]
        pos += col_len
    
    # Read rows
    result = []
    for r in range(nrows):
        for c in range(ncols):
            if r < len(cols[c]):
                result.append(cols[c][r])
    return result

def run_tests(page_num, cipher_indices, cipher_words, key_indices, mode, wordlist):
    """Run all rearrangement tests on a page."""
    print(f"\n{'='*70}")
    print(f"PAGE {page_num}: Keyword={PAGE_CONFIG[page_num][0]}, Mode={mode}")
    print(f"{'='*70}")
    
    # Decrypt
    dec_flat = decrypt(cipher_indices, key_indices, mode)
    dec_words = decrypt_words(cipher_words, key_indices, mode)
    
    ioc = compute_ioc(dec_flat)
    text = words_to_text(dec_words)
    score, matched = score_text(text, wordlist)
    print(f"  Decrypted: IoC={ioc:.4f}, Score={score}, Words={len(matched)}")
    print(f"  Text (first 200): {text[:200]}")
    
    results = []
    
    # --- CHARACTER-LEVEL REARRANGEMENTS ---
    
    # 1. Prime positions only (0-indexed and 1-indexed)
    for zi in [True, False]:
        label = f"prime_pos_{'0idx' if zi else '1idx'}"
        p, np = rearrange_prime_positions(dec_flat, zi)
        ioc_p = compute_ioc(p)
        txt_p = indices_to_text(p)
        sc, mt = score_text(txt_p, wordlist)
        results.append((sc, ioc_p, label, txt_p[:150], mt[:10]))
    
    # 2. Non-prime positions only
    for zi in [True, False]:
        label = f"nonprime_pos_{'0idx' if zi else '1idx'}"
        p, np = rearrange_prime_positions(dec_flat, zi)
        ioc_np = compute_ioc(np)
        txt_np = indices_to_text(np)
        sc, mt = score_text(txt_np, wordlist)
        results.append((sc, ioc_np, label, txt_np[:150], mt[:10]))
    
    # 3. Prime first + non-prime
    for zi in [True, False]:
        label = f"prime_then_nonprime_{'0idx' if zi else '1idx'}"
        arr = rearrange_prime_first(dec_flat, zi)
        ioc_a = compute_ioc(arr)
        txt = indices_to_text(arr)
        sc, mt = score_text(txt, wordlist)
        results.append((sc, ioc_a, label, txt[:150], mt[:10]))
    
    # 4. Reverse
    arr = rearrange_reverse(dec_flat)
    txt = indices_to_text(arr)
    sc, mt = score_text(txt, wordlist)
    results.append((sc, compute_ioc(arr), "reverse", txt[:150], mt[:10]))
    
    # 5. Grid columnar (read columns) - try prime widths
    for w in [5, 7, 11, 13, 17, 19, 23, 29, 31]:
        if w < len(dec_flat):
            arr = rearrange_grid_cols(dec_flat, w)
            txt = indices_to_text(arr)
            sc, mt = score_text(txt, wordlist)
            results.append((sc, compute_ioc(arr), f"grid_cols_w{w}", txt[:150], mt[:10]))
    
    # 6. Grid rows from cols (undo columnar)
    for w in [5, 7, 11, 13, 17, 19, 23, 29, 31]:
        if w < len(dec_flat):
            arr = rearrange_grid_rows_from_cols(dec_flat, w)
            txt = indices_to_text(arr)
            sc, mt = score_text(txt, wordlist)
            results.append((sc, compute_ioc(arr), f"grid_rows_w{w}", txt[:150], mt[:10]))
    
    # 7. Undo columnar transposition with various column orders
    for ncols in [5, 7, 11, 13]:
        if ncols < len(dec_flat):
            # Try reading columns in prime number order
            # e.g., for ncols=5: column order by primes [2,3,5,7,11] -> ranks [0,1,2,3,4]
            prime_order = list(range(ncols))  # natural order
            arr = undo_columnar_transposition(dec_flat, ncols)
            txt = indices_to_text(arr)
            sc, mt = score_text(txt, wordlist)
            results.append((sc, compute_ioc(arr), f"undo_col_w{ncols}", txt[:150], mt[:10]))
    
    # 8. Skip reading (every Nth)
    for skip in [2, 3, 5, 7, 11, 13]:
        arr = rearrange_skip(dec_flat, skip)
        txt = indices_to_text(arr)
        sc, mt = score_text(txt, wordlist)
        results.append((sc, compute_ioc(arr), f"skip_{skip}", txt[:150], mt[:10]))
    
    # 9. Fibonacci positions
    fib_chars, non_fib = rearrange_fibonacci_positions(dec_flat)
    if fib_chars:
        txt = indices_to_text(fib_chars)
        sc, mt = score_text(txt, wordlist)
        results.append((sc, compute_ioc(fib_chars), "fibonacci_pos", txt[:150], mt[:10]))
    
    # 10. Sort by GP prime value
    arr = rearrange_by_gp_value(dec_flat)
    txt = indices_to_text(arr)
    sc, mt = score_text(txt, wordlist)
    results.append((sc, compute_ioc(arr), "sort_by_gp_value", txt[:150], mt[:10]))
    
    # 11. Read at positions given by prime sequence: read[0]=text[2-1], read[1]=text[3-1], etc.
    arr = read_at_prime_indices(dec_flat)
    if arr:
        txt = indices_to_text(arr)
        sc, mt = score_text(txt, wordlist)
        results.append((sc, compute_ioc(arr), "read_at_primes", txt[:150], mt[:10]))
    
    # --- WORD-LEVEL REARRANGEMENTS ---
    
    # 12. Reverse word order
    rw = rearrange_word_reverse(dec_words)
    txt = words_to_text(rw)
    sc, mt = score_text(txt, wordlist)
    flat_rw = [i for w in rw for i in w]
    results.append((sc, compute_ioc(flat_rw), "words_reverse", txt[:150], mt[:10]))
    
    # 13. Prime-indexed words first
    rw = rearrange_words_prime_indexed(dec_words)
    txt = words_to_text(rw)
    sc, mt = score_text(txt, wordlist)
    flat_rw = [i for w in rw for i in w]
    results.append((sc, compute_ioc(flat_rw), "words_prime_first", txt[:150], mt[:10]))
    
    # 14. Sort words by length
    rw = rearrange_words_by_length(dec_words)
    txt = words_to_text(rw)
    sc, mt = score_text(txt, wordlist)
    flat_rw = [i for w in rw for i in w]
    results.append((sc, compute_ioc(flat_rw), "words_by_length", txt[:150], mt[:10]))
    
    # 15. Sort words by GP sum
    rw = rearrange_words_by_gp_sum(dec_words)
    txt = words_to_text(rw)
    sc, mt = score_text(txt, wordlist)
    flat_rw = [i for w in rw for i in w]
    results.append((sc, compute_ioc(flat_rw), "words_by_gp_sum", txt[:150], mt[:10]))
    
    # 16. Sort words by first character
    rw = rearrange_words_by_first_char(dec_words)
    txt = words_to_text(rw)
    sc, mt = score_text(txt, wordlist)
    flat_rw = [i for w in rw for i in w]
    results.append((sc, compute_ioc(flat_rw), "words_by_first_char", txt[:150], mt[:10]))
    
    # 17. Try treating each word's characters as needing internal rearrangement
    # Sort each word's chars by GP value
    rw = [sorted(w, key=lambda x: GP_PRIMES[x]) for w in dec_words]
    txt = words_to_text(rw)
    sc, mt = score_text(txt, wordlist)
    flat_rw = [i for w in rw for i in w]
    results.append((sc, compute_ioc(flat_rw), "words_internal_sort_gp", txt[:150], mt[:10]))
    
    # 18. Reverse each word internally
    rw = [w[::-1] for w in dec_words]
    txt = words_to_text(rw)
    sc, mt = score_text(txt, wordlist)
    flat_rw = [i for w in rw for i in w]
    results.append((sc, compute_ioc(flat_rw), "words_internal_reverse", txt[:150], mt[:10]))
    
    # Sort results by score descending
    results.sort(key=lambda x: x[0], reverse=True)
    
    print(f"\n  Top 15 rearrangements (by English word score):")
    for i, (sc, ioc, label, txt, matched) in enumerate(results[:15]):
        if sc > 0:
            print(f"  {i+1:2d}. [{label:30s}] Score={sc:5d} IoC={ioc:.4f} Words={matched}")
            print(f"      {txt[:120]}")
    
    if not any(r[0] > 0 for r in results):
        print("  No English words found in any rearrangement.")
    
    return results

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(base_dir)
    
    wordlist = load_english_words()
    print(f"Loaded {len(wordlist)} English words")
    
    for page in range(21, 31):
        keyword, mode, key_indices = PAGE_CONFIG[page]
        
        rune_path = f'pages/page_{page:02d}/runes.txt'
        if not os.path.exists(rune_path):
            print(f"\nPage {page}: runes.txt not found")
            continue
        
        with open(rune_path, encoding='utf-8') as f:
            rune_text = f.read().strip()
        
        # Parse runes flat
        cipher_flat = parse_runes(rune_text)
        # Parse runes with word structure
        cipher_words = parse_runes_with_words(rune_text)
        
        if not cipher_flat:
            print(f"\nPage {page}: no runes parsed")
            continue
        
        print(f"\nPage {page}: {len(cipher_flat)} runes, {len(cipher_words)} words")
        
        run_tests(page, cipher_flat, cipher_words, key_indices, mode, wordlist)

if __name__ == '__main__':
    main()
