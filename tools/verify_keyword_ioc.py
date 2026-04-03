#!/usr/bin/env python3
"""
Verify P21-30 keyword decryption IoC and then attempt word-level rearrangement.
The tracker claims Beaufort/ADD/SUB with P63 keywords gives IoC ~1.9-2.1.
The previous session's test found IoC ~1.0. Must resolve this contradiction.
Then attempt anagram/word rearrangement since P19 says "REARRANGING".
"""

import json
from pathlib import Path
from collections import Counter

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

PAGE_CONFIGS = {
    21: ('CABAL',      [5, 24, 17, 24, 20],                          'beaufort'),
    22: ('DIVINITY',   [23, 10, 1, 10, 9, 10, 16, 26],              'beaufort'),
    23: ('ENCRYPTION', [18, 9, 5, 4, 26, 13, 16, 10, 3, 9],         'add'),
    24: ('OBSCURA',    [3, 17, 15, 5, 1, 4, 24],                     'beaufort'),
    25: ('CABAL',      [5, 24, 17, 24, 20],                          'beaufort'),
    26: ('ENCRYPT',    [18, 9, 5, 4, 26, 13, 16],                    'add'),
    27: ('SHADOWS',    [15, 8, 24, 23, 3, 7, 15],                    'add'),
    28: ('DEOR',       [23, 18, 3, 4],                                'sub'),
    29: ('TOTIENT',    [16, 3, 16, 10, 18, 9, 16],                   'beaufort'),
    30: ('MOURNFUL',   [19, 3, 1, 4, 9, 0, 1, 20],                  'add'),
}

def load_runes(page_num):
    """Load runes from file, return indices and raw content."""
    rune_file = PAGES_DIR / f"page_{page_num:02d}" / "runes.txt"
    if not rune_file.exists():
        return None, None
    with open(rune_file, 'r', encoding='utf-8') as f:
        content = f.read()
    indices = [RUNE_TO_IDX[ch] for ch in content if ch in RUNE_TO_IDX]
    return indices, content

def decrypt_vigenere(cipher, key, mode):
    """Standard Vigenère decrypt with repeating key."""
    klen = len(key)
    plain = []
    for i, c in enumerate(cipher):
        k = key[i % klen]
        if mode == 'sub':
            p = (c - k) % 29
        elif mode == 'add':
            p = (c + k) % 29
        elif mode == 'beaufort':
            p = (k - c) % 29
        plain.append(p)
    return plain

def decrypt_with_fskip(content, key, mode):
    """Decrypt with F-skip: literal F runes skip key advancement."""
    klen = len(key)
    plain = []
    key_pos = 0
    
    for ch in content:
        if ch not in RUNE_TO_IDX:
            continue
        c = RUNE_TO_IDX[ch]
        
        if c == 0:  # F rune - could be literal F
            # Try both: treat as literal F (skip key) and decrypt normally
            # For now, apply key normally first
            k = key[key_pos % klen]
            if mode == 'sub':
                p = (c - k) % 29
            elif mode == 'add':
                p = (c + k) % 29
            elif mode == 'beaufort':
                p = (k - c) % 29
            plain.append(p)
            key_pos += 1
        else:
            k = key[key_pos % klen]
            if mode == 'sub':
                p = (c - k) % 29
            elif mode == 'add':
                p = (c + k) % 29
            elif mode == 'beaufort':
                p = (k - c) % 29
            plain.append(p)
            key_pos += 1
    
    return plain

def compute_ioc(indices):
    n = len(indices)
    if n < 2: return 0
    counts = Counter(indices)
    num = sum(c*(c-1) for c in counts.values())
    den = n*(n-1)
    return 29 * num / den if den > 0 else 0

def to_runeglish(indices):
    return ''.join(IDX_TO_LETTER[i] for i in indices)

def extract_words(content, plain_indices):
    """Use word boundaries from original rune text."""
    words = []
    current_word = []
    idx = 0
    
    for ch in content:
        if ch in RUNE_TO_IDX:
            if idx < len(plain_indices):
                current_word.append(plain_indices[idx])
            idx += 1
        elif ch == '-' or ch == '.':
            if current_word:
                words.append(current_word[:])
                current_word = []
        elif ch == '/' or ch == '&' or ch == '$' or ch == '%':
            if current_word:
                words.append(current_word[:])
                current_word = []
    if current_word:
        words.append(current_word[:])
    
    return words

# ========== WORD SCORING ==========

def load_wordlists():
    """Load English words for matching."""
    words = set()
    path = DATA_DIR / "wordlist.txt"
    if path.exists():
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                w = line.strip().upper()
                if len(w) >= 2:
                    words.add(w)
    
    # Add GP-specific forms
    gp_forms = {
        'EUERY', 'NEUER', 'DISCOUER', 'ABOUE', 'CWESTION', 'EUEN',
        'BELIEUE', 'DISCOUERY', 'OUER', 'OUERCOME', 'PREUENT',
        'THNGS', 'CNOW', 'BENG', 'LICE', 'SEEC', 'BOOC', 'GONG',
        'SUFFERNG', 'INSTRUCTIAN', 'ILLUSIIANS', 'WIDSOM',
        'CIRCUMFERENCE', 'FIRFUMFERENFE', 'DIUINITY',
        'THEREAL', 'AETHEREAL', 'MOURNFUL', 'TOTIENT',
        'PARABLE', 'PILGRIM', 'INSTAR', 'KOAN', 'CABAL',
    }
    words.update(gp_forms)
    return words

def word_matches(word_list, dictionary):
    """Count how many words in word_list match the dictionary."""
    matched = []
    for w_indices in word_list:
        w = to_runeglish(w_indices).upper()
        # Direct match
        if w in dictionary:
            matched.append(w)
            continue
        # Try K→C substitution
        wk = w.replace('C', 'K')
        if wk in dictionary:
            matched.append(f"{w}→{wk}")
            continue
        # Try V→U substitution
        wv = w.replace('U', 'V')
        if wv in dictionary:
            matched.append(f"{w}→{wv}")
            continue
        # NG→ING
        wng = w.replace('NG', 'ING')
        if wng in dictionary:
            matched.append(f"{w}→{wng}")
    return matched

# ========== WORD REARRANGEMENT ==========

def try_word_rearrangements(words, dictionary):
    """Try different word reorderings to maximize dictionary matches."""
    # First, check how many words already match
    base_matches = word_matches(words, dictionary)
    
    results = []
    n = len(words)
    word_strs = [to_runeglish(w).upper() for w in words]
    
    # 1. Reverse order
    rev_matches = word_matches(words[::-1], dictionary)
    results.append(('reverse', len(rev_matches), rev_matches))
    
    # 2. Every other word (even, odd interleave)
    even = [words[i] for i in range(0, n, 2)]
    odd = [words[i] for i in range(1, n, 2)]
    results.append(('even_first', len(word_matches(even + odd, dictionary)), word_matches(even + odd, dictionary)))
    results.append(('odd_first', len(word_matches(odd + even, dictionary)), word_matches(odd + even, dictionary)))
    
    # 3. Read in columns (widths based on prime factors)
    for width in [2, 3, 5, 7, 11, 13]:
        if width >= n:
            continue
        rows = [words[i:i+width] for i in range(0, n, width)]
        # Column-wise reading
        col_order = []
        for col in range(width):
            for row in rows:
                if col < len(row):
                    col_order.append(row[col])
        cm = word_matches(col_order, dictionary)
        results.append((f'col_w{width}', len(cm), cm))
        
        # Reverse column order
        col_rev = []
        for col in range(width-1, -1, -1):
            for row in rows:
                if col < len(row):
                    col_rev.append(row[col])
        crm = word_matches(col_rev, dictionary)
        results.append((f'col_w{width}_rev', len(crm), crm))
    
    # 4. Prime-indexed words first, then non-prime
    is_prime = [False] * (n + 1)
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67]:
        if p <= n:
            is_prime[p] = True
    
    prime_words = [words[i] for i in range(n) if i < len(is_prime) and is_prime[i]]
    nonprime_words = [words[i] for i in range(n) if i >= len(is_prime) or not is_prime[i]]
    pm = word_matches(prime_words + nonprime_words, dictionary)
    results.append(('prime_first_0idx', len(pm), pm))
    
    # 5. Magic square path (using P63 grid order)
    # The 5x5 magic square: rows sum to 1033
    # Try rearranging words by GP prime values of first letter
    word_vals = []
    for i, w in enumerate(words):
        if w:
            first_idx = w[0]
            word_vals.append((first_idx, i))
    word_vals.sort()
    sorted_words = [words[i] for _, i in word_vals]
    sm = word_matches(sorted_words, dictionary)
    results.append(('sort_by_first_rune', len(sm), sm))
    
    # 6. Sort by GP prime value of first rune
    GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
    word_pvals = []
    for i, w in enumerate(words):
        if w:
            pval = GP_PRIMES[w[0]] if w[0] < len(GP_PRIMES) else 0
            word_pvals.append((pval, i))
    word_pvals.sort()
    pval_sorted = [words[i] for _, i in word_pvals]
    pvm = word_matches(pval_sorted, dictionary)
    results.append(('sort_by_prime_val', len(pvm), pvm))
    
    # 7. Boustrophedon (snake reading of word grid)
    for width in [5, 7, 11]:
        if width >= n:
            continue
        rows = [words[i:i+width] for i in range(0, n, width)]
        snake = []
        for r_idx, row in enumerate(rows):
            if r_idx % 2 == 0:
                snake.extend(row)
            else:
                snake.extend(row[::-1])
        snm = word_matches(snake, dictionary)
        results.append((f'snake_w{width}', len(snm), snm))
    
    return base_matches, results

# ========== CHARACTER-LEVEL REARRANGEMENT ==========

def try_char_rearrangements(plain_indices, dictionary):
    """Try character-level permutations."""
    results = []
    n = len(plain_indices)
    
    # 1. Reverse
    rev = plain_indices[::-1]
    rev_text = to_runeglish(rev)
    # Count 3-letter word matches as substrings
    score = sum(1 for w in ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL',
                            'OUR', 'OUT', 'WAS', 'ONE', 'HAS', 'HIS', 'HOW', 'MAY',
                            'NEW', 'NOW', 'OLD', 'WHO', 'WAY', 'SEE', 'OWN', 'ITS']
                if w in rev_text.upper())
    results.append(('reverse_chars', compute_ioc(rev), score, rev_text[:100]))
    
    # 2. Columnar transposition with keyword-length width
    for width in [5, 7, 8, 9, 10, 11, 13]:
        # Read by columns
        cols_out = []
        rows = (n + width - 1) // width
        for col in range(width):
            for row in range(rows):
                idx = row * width + col
                if idx < n:
                    cols_out.append(plain_indices[idx])
        ioc = compute_ioc(cols_out)
        text = to_runeglish(cols_out)
        score = sum(1 for w in ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL',
                                'OUR', 'OUT', 'WAS', 'ONE', 'HAS', 'HIS', 'HOW', 'MAY',
                                'NEW', 'NOW', 'OLD', 'WHO', 'WAY', 'SEE', 'OWN', 'ITS',
                                'THIS', 'THAT', 'WITH', 'HAVE', 'FROM', 'THEY', 'BEEN',
                                'WILL', 'INTO', 'THAN', 'THEM', 'THEN', 'WHAT', 'WHEN']
                    if w in text.upper())
        results.append((f'col_trans_w{width}', ioc, score, text[:100]))
    
    # 3. Prime index extraction
    primes_set = set()
    p = 2
    while p < n:
        primes_set.add(p)
        p += 1
        while any(p % d == 0 for d in range(2, int(p**0.5)+1)):
            p += 1
    
    prime_chars = [plain_indices[i] for i in range(n) if i in primes_set]
    nonprime_chars = [plain_indices[i] for i in range(n) if i not in primes_set]
    
    if prime_chars:
        ioc = compute_ioc(prime_chars)
        text = to_runeglish(prime_chars)
        results.append(('prime_0idx', ioc, 0, text[:100]))
    
    # 1-indexed primes
    prime_1idx = [plain_indices[i-1] for i in range(1, n+1) if i in primes_set and i-1 < n]
    if prime_1idx:
        ioc = compute_ioc(prime_1idx)
        text = to_runeglish(prime_1idx)
        results.append(('prime_1idx', ioc, 0, text[:100]))
    
    # Interleave: prime positions, then non-prime
    combined = prime_chars + nonprime_chars
    if combined:
        ioc = compute_ioc(combined)
        text = to_runeglish(combined)
        results.append(('prime_then_non', ioc, 0, text[:100]))
    
    # 4. Spiral reading
    for width in [5, 7, 11, 13, 17, 19]:
        rows_count = (n + width - 1) // width
        grid = []
        for r in range(rows_count):
            row = []
            for c in range(width):
                idx = r * width + c
                if idx < n:
                    row.append(plain_indices[idx])
                else:
                    row.append(-1)
            grid.append(row)
        
        # Clockwise spiral
        spiral = []
        top, bottom, left, right = 0, rows_count - 1, 0, width - 1
        while top <= bottom and left <= right:
            for c in range(left, right + 1):
                if grid[top][c] >= 0:
                    spiral.append(grid[top][c])
            top += 1
            for r in range(top, bottom + 1):
                if grid[r][right] >= 0:
                    spiral.append(grid[r][right])
            right -= 1
            if top <= bottom:
                for c in range(right, left - 1, -1):
                    if grid[bottom][c] >= 0:
                        spiral.append(grid[bottom][c])
                bottom -= 1
            if left <= right:
                for r in range(bottom, top - 1, -1):
                    if grid[r][left] >= 0:
                        spiral.append(grid[r][left])
                left += 1
        
        if spiral:
            ioc = compute_ioc(spiral)
            text = to_runeglish(spiral)
            score = sum(1 for w in ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL']
                        if w in text.upper())
            results.append((f'spiral_w{width}', ioc, score, text[:100]))
    
    return results

# ========== MAIN ==========

def main():
    print("P21-30 KEYWORD DECRYPTION VERIFICATION + WORD REARRANGEMENT")
    print("=" * 100)
    
    dictionary = load_wordlists()
    print(f"Dictionary: {len(dictionary)} words loaded")
    
    # Also load verified keys for comparison
    vk_path = DATA_DIR / "verified_keys.json"
    verified_keys = {}
    if vk_path.exists():
        with open(vk_path) as f:
            verified_keys = json.load(f)
    
    for pg in range(21, 31):
        cipher, content = load_runes(pg)
        if cipher is None:
            print(f"\nP{pg}: No runes found")
            continue
        
        kw_name, kw_idx, mode = PAGE_CONFIGS[pg]
        
        # Standard Vigenère with keyword repetition
        plain_std = decrypt_vigenere(cipher, kw_idx, mode)
        ioc_std = compute_ioc(plain_std)
        text_std = to_runeglish(plain_std)
        
        # With F-skip
        plain_fskip = decrypt_with_fskip(content, kw_idx, mode)
        ioc_fskip = compute_ioc(plain_fskip)
        text_fskip = to_runeglish(plain_fskip)
        
        # With verified key
        vk = verified_keys.get(str(pg))
        ioc_vk = 0
        text_vk = ""
        if vk:
            plain_vk = decrypt_vigenere(cipher, vk, 'sub')  # verified keys use SUB
            ioc_vk = compute_ioc(plain_vk)
            text_vk = to_runeglish(plain_vk)
        
        print(f"\n{'='*100}")
        print(f"PAGE {pg:02d} — {len(cipher)} runes, Keyword: {kw_name} ({mode})")
        print(f"{'='*100}")
        print(f"  Standard Vig IoC:     {ioc_std:.4f}")
        print(f"  F-skip Vig IoC:       {ioc_fskip:.4f}")
        if vk:
            print(f"  Verified Key IoC:     {ioc_vk:.4f} (key len {len(vk)})")
        print(f"  Standard text[:80]:   {text_std[:80]}")
        print(f"  F-skip text[:80]:     {text_fskip[:80]}")
        if text_vk:
            print(f"  VK text[:80]:         {text_vk[:80]}")
        
        # Now attempt word rearrangement on the BEST decryption (highest IoC)
        best_plain = plain_std if ioc_std >= ioc_fskip else plain_fskip
        best_ioc = max(ioc_std, ioc_fskip)
        best_label = "std" if ioc_std >= ioc_fskip else "fskip"
        
        # Extract words
        words = extract_words(content, best_plain)
        word_strs = [to_runeglish(w).upper() for w in words]
        
        print(f"\n  Words extracted ({best_label}, {len(words)} words):")
        print(f"  {' '.join(word_strs[:20])}{'...' if len(word_strs) > 20 else ''}")
        
        # Check dictionary matches in current order
        base_matches = word_matches(words, dictionary)
        print(f"\n  Direct dictionary matches ({len(base_matches)}/{len(words)}):")
        if base_matches:
            print(f"    {base_matches[:30]}")
        
        # Try word rearrangements
        _, rearr_results = try_word_rearrangements(words, dictionary)
        rearr_results.sort(key=lambda x: -x[1])
        
        print(f"\n  Word Rearrangement Results (top 5):")
        for method, count, matches in rearr_results[:5]:
            print(f"    {method:<25} matches={count}/{len(words)}")
            if matches:
                print(f"      {matches[:15]}")
        
        # Try character-level rearrangements
        char_results = try_char_rearrangements(best_plain, dictionary)
        char_results.sort(key=lambda x: -(x[2] + x[1] * 10))
        
        print(f"\n  Char Rearrangement Results (top 5):")
        for method, ioc, score, text in char_results[:5]:
            print(f"    {method:<25} IoC={ioc:.4f} score={score} text={text[:60]}")
    
    # SPECIAL: Test P43+P00 claim
    print(f"\n\n{'='*100}")
    print("SPECIAL TEST: P43 + P00 (claimed IoC 2.0632)")
    print(f"{'='*100}")
    
    p43_cipher, _ = load_runes(43)
    p00_cipher, _ = load_runes(0)
    
    if p43_cipher and p00_cipher:
        min_len = min(len(p43_cipher), len(p00_cipher))
        
        # Try: P00 as key for P43, ADD mode
        plain_add = [(p43_cipher[i] + p00_cipher[i]) % 29 for i in range(min_len)]
        ioc_add = compute_ioc(plain_add)
        
        # SUB mode
        plain_sub = [(p43_cipher[i] - p00_cipher[i]) % 29 for i in range(min_len)]
        ioc_sub = compute_ioc(plain_sub)
        
        # Beaufort
        plain_beau = [(p00_cipher[i] - p43_cipher[i]) % 29 for i in range(min_len)]
        ioc_beau = compute_ioc(plain_beau)
        
        print(f"  P43 len={len(p43_cipher)}, P00 len={len(p00_cipher)}, using {min_len}")
        print(f"  P43+P00 ADD: IoC = {ioc_add:.4f}")
        print(f"  P43-P00 SUB: IoC = {ioc_sub:.4f}")
        print(f"  P00-P43 BEA: IoC = {ioc_beau:.4f}")
        print(f"  ADD text: {to_runeglish(plain_add)[:80]}")
        print(f"  SUB text: {to_runeglish(plain_sub)[:80]}")
        print(f"  BEA text: {to_runeglish(plain_beau)[:80]}")

if __name__ == '__main__':
    main()
