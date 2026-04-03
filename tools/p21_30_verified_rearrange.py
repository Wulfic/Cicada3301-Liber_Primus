#!/usr/bin/env python3
"""
P21-30 Verified Key + Rearrangement Solver

Uses the actual 71/83-element hill-climbed keys from verified_keys.json
with the modes specified in the MASTER_TRACKER. Then tests prime-based
rearrangement strategies.
"""

import os, sys, json, math
from collections import Counter

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

# Modes per page from MASTER_TRACKER
PAGE_MODES = {
    21: 'beaufort', 22: 'beaufort', 23: 'add', 24: 'beaufort', 25: 'beaufort',
    26: 'add', 27: 'add', 28: 'sub', 29: 'beaufort', 30: 'add'
}

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
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n+1, i):
                sieve[j] = False
    return [i for i in range(n+1) if sieve[i]]

def fibonacci_up_to(n):
    fibs = [1, 2]
    while fibs[-1] < n:
        fibs.append(fibs[-1] + fibs[-2])
    return [f for f in fibs if f <= n]

def parse_runes(text):
    """Parse rune text into list of GP indices."""
    return [GP_RUNE_TO_IDX[ch] for ch in text if ch in GP_RUNE_TO_IDX]

def parse_rune_structure(text):
    """Parse runes preserving word/sentence structure. Returns list of 'tokens' where each token is either a word (list of indices) or a separator string."""
    tokens = []
    current_word = []
    
    for ch in text:
        if ch in GP_RUNE_TO_IDX:
            current_word.append(GP_RUNE_TO_IDX[ch])
        elif ch in '-':
            if current_word:
                tokens.append(('word', current_word))
                current_word = []
            tokens.append(('sep', ' '))
        elif ch == '.':
            if current_word:
                tokens.append(('word', current_word))
                current_word = []
            tokens.append(('sep', '. '))
        elif ch in '&$':
            if current_word:
                tokens.append(('word', current_word))
                current_word = []
        elif ch in '\n\r':
            pass
    
    if current_word:
        tokens.append(('word', current_word))
    
    return tokens

def decrypt(cipher, key, mode):
    """Decrypt with given mode."""
    result = []
    kl = len(key)
    for i, c in enumerate(cipher):
        k = key[i % kl]
        if mode == 'beaufort':
            result.append((k - c) % 29)
        elif mode == 'add':
            result.append((c + k) % 29)
        elif mode == 'sub':
            result.append((c - k) % 29)
    return result

def decrypt_fskip(cipher, key, mode):
    """Decrypt with F-skip rule: skip key advancement when rune is F (idx 0)."""
    result = []
    kl = len(key)
    key_pos = 0
    for c in cipher:
        if c == 0:  # F rune
            result.append(0)  # literal F
        else:
            k = key[key_pos % kl]
            if mode == 'beaufort':
                result.append((k - c) % 29)
            elif mode == 'add':
                result.append((c + k) % 29)
            elif mode == 'sub':
                result.append((c - k) % 29)
            key_pos += 1
    return result

def indices_to_text(indices):
    return ''.join(IDX_TO_LATIN[i] for i in indices)

def compute_ioc(indices):
    if len(indices) < 2:
        return 0
    freq = Counter(indices)
    n = len(indices)
    return 29 * sum(c*(c-1) for c in freq.values()) / (n * (n-1))

def load_english_words(path='data/wordlist.txt'):
    try:
        with open(path) as f:
            return set(w.strip().upper() for w in f if len(w.strip()) >= 2)
    except:
        return set()

def score_text_words(text, wordlist):
    """Score by matching words (space-separated) against wordlist."""
    words = text.replace('.', ' ').split()
    score = 0
    matched = []
    for w in words:
        wu = w.upper()
        # Direct match
        if wu in wordlist:
            score += len(wu) ** 2
            matched.append(wu)
            continue
        # GP digraph rules
        for transform in [
            lambda x: x.replace('NG', 'ING'),
            lambda x: x.replace('IA', 'ION'),
            lambda x: x.replace('C', 'K'),
            lambda x: x.replace('U', 'V'),
            lambda x: x.replace('TH', 'THE') if x.startswith('TH') else x,
        ]:
            w2 = transform(wu)
            if w2 in wordlist:
                score += len(w2) ** 2
                matched.append(w2)
                break
    return score, matched

def rearrange_by_positions(indices, positions):
    """Read indices at the given positions (0-indexed)."""
    return [indices[p] for p in positions if 0 <= p < len(indices)]

# ============================================================================
# REARRANGEMENT STRATEGIES
# ============================================================================

def test_rearrangements(dec_flat, dec_text_with_words, wordlist, label_prefix=""):
    """Test many rearrangement strategies on decrypted flat indices."""
    n = len(dec_flat)
    results = []
    
    # --- 1. Prime position extraction (various indexing) ---
    prime_set_0 = set(primes_up_to(n))  # 0-indexed prime positions
    prime_set_1 = set(p - 1 for p in primes_up_to(n + 1) if p > 0)  # 1-indexed -> 0-based
    
    for label, pset in [("prime_0idx", prime_set_0), ("prime_1idx", prime_set_1)]:
        prime_chars = [dec_flat[i] for i in range(n) if i in pset]
        nonprime_chars = [dec_flat[i] for i in range(n) if i not in pset]
        
        for sub_label, arr in [
            (f"{label}_only", prime_chars),
            (f"nonprime_{label[6:]}_only", nonprime_chars),
            (f"{label}_then_nonprime", prime_chars + nonprime_chars),
            (f"nonprime_then_{label}", nonprime_chars + prime_chars),
        ]:
            if arr:
                txt = indices_to_text(arr)
                sc, mt = score_text_words(txt, wordlist)
                results.append((sc, compute_ioc(arr), sub_label, txt[:200], mt[:15]))
    
    # --- 2. Grid/columnar transposition ---
    for width in [5, 7, 11, 13, 17, 19, 23, 29, 31]:
        if width >= n or width <= 1:
            continue
        rows = (n + width - 1) // width
        
        # Read columns (undo row-major write, column-first read)
        col_read = []
        for c in range(width):
            for r in range(rows):
                idx = r * width + c
                if idx < n:
                    col_read.append(dec_flat[idx])
        txt = indices_to_text(col_read)
        sc, mt = score_text_words(txt, wordlist)
        results.append((sc, compute_ioc(col_read), f"grid_col_w{width}", txt[:200], mt[:15]))
        
        # Undo columnar: text was written in columns, read rows -> to undo: write rows, read columns
        # = same as above? No. Undo columnar means original was arranged in rows then read by columns.
        # To reverse: write into columns, read rows.
        col_write = [[] for _ in range(width)]
        for i, v in enumerate(dec_flat):
            col_write[i % width].append(v)
        row_read = []
        max_rows = max(len(c) for c in col_write) if col_write else 0
        for r in range(max_rows):
            for c in range(width):
                if r < len(col_write[c]):
                    row_read.append(col_write[c][r])
        txt = indices_to_text(row_read)
        sc, mt = score_text_words(txt, wordlist)
        results.append((sc, compute_ioc(row_read), f"undo_col_w{width}", txt[:200], mt[:15]))
    
    # --- 3. Skip/stride reading ---
    for skip in [2, 3, 5, 7, 11, 13]:
        arr = []
        visited = [False] * n
        pos = 0
        while pos < n:
            if not visited[pos]:
                arr.append(dec_flat[pos])
                visited[pos] = True
            pos += skip
        # Fill remaining
        for i in range(n):
            if not visited[i]:
                arr.append(dec_flat[i])
                visited[i] = True
        txt = indices_to_text(arr)
        sc, mt = score_text_words(txt, wordlist)
        results.append((sc, compute_ioc(arr), f"skip_{skip}", txt[:200], mt[:15]))
    
    # --- 4. Reverse ---
    arr = dec_flat[::-1]
    txt = indices_to_text(arr)
    sc, mt = score_text_words(txt, wordlist)
    results.append((sc, compute_ioc(arr), "reverse", txt[:200], mt[:15]))
    
    # --- 5. Fibonacci positions ---
    fibs = set(fibonacci_up_to(n))
    fib_chars = [dec_flat[i] for i in range(n) if (i+1) in fibs]
    if fib_chars:
        txt = indices_to_text(fib_chars)
        sc, mt = score_text_words(txt, wordlist)
        results.append((sc, compute_ioc(fib_chars), "fibonacci", txt[:200], mt[:15]))
    
    # --- 6. Spiral reading through rectangle ---
    for width in [11, 13, 17, 19, 23]:
        if width >= n:
            continue
        rows = (n + width - 1) // width
        grid = []
        for r in range(rows):
            row = []
            for c in range(width):
                idx = r * width + c
                row.append(dec_flat[idx] if idx < n else -1)
            grid.append(row)
        
        # Spiral: right, down, left, up
        spiral = []
        top, bottom, left, right = 0, rows-1, 0, width-1
        while top <= bottom and left <= right:
            for c in range(left, right+1):
                if grid[top][c] >= 0: spiral.append(grid[top][c])
            top += 1
            for r in range(top, bottom+1):
                if grid[r][right] >= 0: spiral.append(grid[r][right])
            right -= 1
            if top <= bottom:
                for c in range(right, left-1, -1):
                    if grid[bottom][c] >= 0: spiral.append(grid[bottom][c])
                bottom -= 1
            if left <= right:
                for r in range(bottom, top-1, -1):
                    if grid[r][left] >= 0: spiral.append(grid[r][left])
                left += 1
        
        txt = indices_to_text(spiral)
        sc, mt = score_text_words(txt, wordlist)
        results.append((sc, compute_ioc(spiral), f"spiral_w{width}", txt[:200], mt[:15]))
    
    # --- 7. Zigzag / rail fence ---
    for nrails in [2, 3, 5, 7]:
        if nrails >= n:
            continue
        # Decode rail fence
        rail_lens = [0] * nrails
        rail = 0
        direction = 1
        for i in range(n):
            rail_lens[rail] += 1
            if rail == 0:
                direction = 1
            elif rail == nrails - 1:
                direction = -1
            rail += direction
        
        # Assign chars to rails
        rails = []
        pos = 0
        for r in range(nrails):
            rails.append(dec_flat[pos:pos+rail_lens[r]])
            pos += rail_lens[r]
        
        # Read in zigzag order
        arr = []
        rail_ptrs = [0] * nrails
        rail = 0
        direction = 1
        for i in range(n):
            if rail_ptrs[rail] < len(rails[rail]):
                arr.append(rails[rail][rail_ptrs[rail]])
                rail_ptrs[rail] += 1
            if rail == 0:
                direction = 1
            elif rail == nrails - 1:
                direction = -1
            rail += direction
        
        txt = indices_to_text(arr)
        sc, mt = score_text_words(txt, wordlist)
        results.append((sc, compute_ioc(arr), f"railfence_{nrails}", txt[:200], mt[:15]))
    
    # --- 8. Reading at positions defined by prime sequence ---
    # Position i -> read at prime(i)-th position
    primes_list = primes_up_to(n)
    if primes_list:
        arr = [dec_flat[p] for p in primes_list if p < n]
        txt = indices_to_text(arr)
        sc, mt = score_text_words(txt, wordlist)
        results.append((sc, compute_ioc(arr), "read_at_primes_seq", txt[:200], mt[:15]))
    
    # --- 9. Permutation by GP prime values ---
    # Sort positions by GP prime value of decrypted char
    sorted_positions = sorted(range(n), key=lambda i: GP_PRIMES[dec_flat[i]])
    arr = [dec_flat[p] for p in sorted_positions]
    txt = indices_to_text(arr)
    sc, mt = score_text_words(txt, wordlist)
    results.append((sc, compute_ioc(arr), "sort_by_gp_value", txt[:200], mt[:15]))
    
    return results


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(base_dir)
    
    with open('data/verified_keys.json') as f:
        verified_keys = json.load(f)
    
    wordlist = load_english_words()
    print(f"Loaded {len(wordlist)} English words")
    
    all_results = {}
    
    for page in range(21, 31):
        mode = PAGE_MODES[page]
        key = verified_keys.get(str(page), [])
        if not key:
            print(f"\nPage {page}: no verified key found")
            continue
        
        rune_path = f'pages/page_{page:02d}/runes.txt'
        if not os.path.exists(rune_path):
            print(f"\nPage {page}: runes.txt not found")
            continue
        
        with open(rune_path, encoding='utf-8') as f:
            rune_text = f.read().strip()
        
        cipher = parse_runes(rune_text)
        print(f"\n{'='*70}")
        print(f"PAGE {page}: {len(cipher)} runes, Key len={len(key)}, Mode={mode}")
        print(f"{'='*70}")
        
        # Try both with and without F-skip
        for fskip_label, decrypt_fn in [("no_fskip", decrypt), ("fskip", decrypt_fskip)]:
            dec = decrypt_fn(cipher, key, mode)
            ioc = compute_ioc(dec)
            txt = indices_to_text(dec)
            
            # Also try all 3 modes for completeness
            for alt_mode in ['beaufort', 'add', 'sub']:
                dec_alt = decrypt_fn(cipher, key, alt_mode)
                ioc_alt = compute_ioc(dec_alt)
                label = f"P{page}_{alt_mode}_{fskip_label}"
                
                if ioc_alt > 1.4:  # Only print high-IoC results
                    txt_alt = indices_to_text(dec_alt)
                    print(f"\n  [{label}] IoC={ioc_alt:.4f}")
                    print(f"    Text: {txt_alt[:200]}")
                    
                    # Run rearrangement tests on high-IoC results
                    results = test_rearrangements(dec_alt, txt_alt, wordlist, label)
                    results.sort(key=lambda x: x[0], reverse=True)
                    
                    print(f"    Top 10 rearrangements:")
                    for i, (sc, rioc, rl, rtxt, rmt) in enumerate(results[:10]):
                        if sc > 0:
                            print(f"    {i+1:2d}. [{rl:30s}] Score={sc:5d} IoC={rioc:.4f} Words={rmt}")
                            print(f"        {rtxt[:120]}")
                    
                    all_results[label] = (ioc_alt, results)
        
        # Also show the tracker-specified mode result
        dec = decrypt(cipher, key, mode)
        ioc = compute_ioc(dec)
        txt = indices_to_text(dec)
        dec_fskip = decrypt_fskip(cipher, key, mode)
        ioc_fskip = compute_ioc(dec_fskip)
        txt_fskip = indices_to_text(dec_fskip)
        
        if ioc <= 1.4 and ioc_fskip <= 1.4:
            print(f"\n  Tracker mode ({mode}): IoC={ioc:.4f} (no fskip), {ioc_fskip:.4f} (fskip)")
            print(f"    Neither exceeds IoC 1.4 threshold")
            print(f"    Text (no fskip): {txt[:150]}")
    
    # Summary
    print(f"\n\n{'='*70}")
    print("SUMMARY: All high-IoC (>1.4) decryptions found")
    print(f"{'='*70}")
    for label, (ioc, results) in sorted(all_results.items(), key=lambda x: -x[1][0]):
        best_sc = results[0][0] if results else 0
        print(f"  {label}: IoC={ioc:.4f}, Best rearrangement score={best_sc}")

if __name__ == '__main__':
    main()
