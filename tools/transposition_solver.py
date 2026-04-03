#!/usr/bin/env python3
"""
Comprehensive Transposition Solver for P21-30 (and P31-54)
==========================================================
After keyword Vigenère decryption, letters are correct but order wrong.
This script tests EVERY known transposition method systematically.

Key insight from analysis:
- Previous tests tried columnar widths 11-53, but MISSED keyword-length widths (5-10)
- The keyword itself may define the column permutation
- Magic square permutation was never tested
- Scytale/route cipher with small diameters was never tested

Tests:
1. Keyword-derived columnar transposition (using SAME keyword)
2. Magic square 5x5 block permutation
3. Scytale cipher (all diameters)
4. Route cipher (spiral, snake, diagonal)
5. Rail fence with keyword-length rails
6. Double transposition
7. Myszkowski transposition (handles duplicate letters)
8. Disrupted transposition with prime-indexed blanks
"""

import os
import sys
import json
import math
from pathlib import Path
from collections import Counter
from itertools import permutations

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

GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]

# Confirmed keys for pages 21-30
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

def keyword_to_indices(keyword):
    """Convert keyword to GP indices."""
    letter_to_idx = {}
    for i, l in enumerate(IDX_TO_LETTER):
        letter_to_idx[l] = i
    result = []
    kw = keyword.upper()
    i = 0
    while i < len(kw):
        matched = False
        for length in [3, 2]:
            if i + length <= len(kw):
                chunk = kw[i:i+length]
                if chunk in letter_to_idx:
                    result.append(letter_to_idx[chunk])
                    i += length
                    matched = True
                    break
        if not matched:
            ch = kw[i]
            if ch == 'K': ch = 'C'
            if ch == 'V': ch = 'U'
            if ch in letter_to_idx:
                result.append(letter_to_idx[ch])
            else:
                result.append(0)
            i += 1
    return result

# Compute keyword indices for those that are None
for pg, info in PAGE_KEYS.items():
    if info['indices'] is None:
        info['indices'] = keyword_to_indices(info['keyword'])

def load_runes(page_num):
    """Load rune file, return (indices, raw_content)."""
    rune_file = PAGES_DIR / f"page_{page_num:02d}" / "runes.txt"
    if not rune_file.exists():
        return None, None
    with open(rune_file, 'r', encoding='utf-8') as f:
        content = f.read()
    indices = [RUNE_TO_IDX[ch] for ch in content if ch in RUNE_TO_IDX]
    return indices, content

def decrypt_vigenere(cipher, key, mode='sub'):
    """Decrypt Vigenère."""
    result = []
    klen = len(key)
    for i, c in enumerate(cipher):
        k = key[i % klen]
        if mode == 'sub':
            result.append((c - k) % 29)
        elif mode == 'add':
            result.append((c + k) % 29)
        elif mode == 'beaufort':
            result.append((k - c) % 29)
    return result

def to_runeglish(indices):
    return ''.join(IDX_TO_LETTER[i] for i in indices)

def compute_ioc(indices):
    n = len(indices)
    if n < 2: return 0
    counts = Counter(indices)
    num = sum(c*(c-1) for c in counts.values())
    den = n*(n-1)
    return 29 * num / den if den > 0 else 0

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i*i <= n:
        if n%i == 0 or n%(i+2) == 0: return False
        i += 6
    return True

# ========== ENGLISH SCORING ==========
# Load comprehensive word list
WORD_SET = set()
def load_words():
    global WORD_SET
    wl = DATA_DIR / "wordlist.txt"
    if wl.exists():
        with open(wl, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                w = line.strip().upper()
                if 2 <= len(w) <= 20:
                    WORD_SET.add(w)
    # GP common words
    for w in ['THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','HER','WAS','ONE',
              'OUR','OUT','HAD','HAS','HIS','HOW','ITS','MAY','NEW','NOW','OLD','SEE',
              'WAY','WHO','THIS','THAT','WITH','HAVE','FROM','THEY','BEEN','SAID',
              'EACH','WILL','INTO','THAN','THEM','THEN','WHAT','WHEN','MAKE','LIKE',
              'LONG','LOOK','MANY','SOME','TIME','YOUR','KNOW','JUST','COME','MADE',
              'FIND','ONLY','SELF','BEING','TRUTH','WITHIN','SACRED','WISDOM','FOLLOW',
              'INSTRUCTION','DIVINITY','CIRCUMFERENCE','CONSUMPTION','BELIEVE','NOTHING',
              'BOOK','EXCEPT','TRUE','A','I','OF','TO','IN','IS','IT','AN','AS','AT',
              'BE','BY','DO','GO','IF','ME','MY','NO','ON','OR','SO','UP','WE']:
        WORD_SET.add(w)

# Quadgram scoring (loaded from text if available, otherwise use bigrams)
ENGLISH_BIGRAMS = {
    'TH': 152, 'HE': 128, 'IN': 94, 'ER': 94, 'AN': 82, 'RE': 68, 'ON': 57,
    'AT': 56, 'EN': 55, 'ND': 54, 'TI': 54, 'ES': 52, 'OR': 48, 'TE': 46,
    'OF': 40, 'ED': 39, 'IS': 37, 'IT': 37, 'AL': 36, 'AR': 34, 'ST': 33,
    'TO': 33, 'NT': 33, 'NG': 32, 'SE': 31, 'HA': 30, 'AS': 26, 'OU': 26,
    'IO': 26, 'LE': 25, 'VE': 24, 'CO': 22, 'ME': 21, 'DE': 21, 'HI': 21,
    'RI': 20, 'RO': 20, 'IC': 19, 'NE': 18, 'EA': 18, 'RA': 17, 'CE': 16,
    'LI': 15, 'CH': 14, 'LL': 13, 'BE': 13, 'MA': 12, 'SI': 12, 'OM': 11,
    'UR': 11, 'OE': 5,
}

def score_text_bigrams(runeglish_text):
    """Score runeglish text using English bigram frequencies."""
    score = 0
    text = runeglish_text.upper()
    for i in range(len(text) - 1):
        bi = text[i:i+2]
        if bi in ENGLISH_BIGRAMS:
            score += ENGLISH_BIGRAMS[bi]
        elif bi[0] not in ' .' and bi[1] not in ' .':
            score -= 1
    return score

def score_words(runeglish_text):
    """Score based on word matches (split on space/period)."""
    words = runeglish_text.replace('.', ' ').split()
    score = 0
    matched = 0
    for w in words:
        wu = w.upper()
        if wu in WORD_SET:
            score += len(wu) * 10
            matched += 1
        elif wu.replace('C', 'K') in WORD_SET:
            score += len(wu) * 8
            matched += 1
        elif wu.replace('U', 'V') in WORD_SET:
            score += len(wu) * 8
            matched += 1
        else:
            score -= 2
    return score, matched, len(words)

def combined_score(runeglish_text):
    """Combined bigram + word score."""
    bs = score_text_bigrams(runeglish_text)
    ws, matched, total = score_words(runeglish_text)
    return bs + ws, matched, total

# ========== TRANSPOSITION METHODS ==========

def keyword_column_permutation(keyword):
    """
    Derive column permutation from keyword.
    Letters sorted alphabetically, ties broken left-to-right.
    Returns permutation array.
    """
    indexed = list(enumerate(keyword.upper()))
    # Sort by letter, then by position (stable sort)
    sorted_indexed = sorted(indexed, key=lambda x: (x[1], x[0]))
    # Assign ranks
    perm = [0] * len(keyword)
    for rank, (orig_pos, _) in enumerate(sorted_indexed):
        perm[orig_pos] = rank
    return perm

def undo_columnar_transposition(ciphertext_indices, ncols, col_order=None):
    """
    Undo columnar transposition.
    ciphertext was created by writing plaintext into rows of ncols,
    then reading columns in col_order.
    To decrypt: distribute cipher into columns, then read row-by-row.
    """
    n = len(ciphertext_indices)
    nrows = math.ceil(n / ncols)
    
    # How many full columns (nrows elements) and short columns (nrows-1 elements)
    full_cols = n - (nrows - 1) * ncols  # number of columns with nrows elements
    
    if col_order is None:
        col_order = list(range(ncols))
    
    # Column lengths
    col_lengths = []
    for col in range(ncols):
        if col < full_cols:
            col_lengths.append(nrows)
        else:
            col_lengths.append(nrows - 1)
    
    # Distribute ciphertext into columns in col_order
    grid = [[] for _ in range(ncols)]
    pos = 0
    for rank in range(ncols):
        # Find which column has this rank in col_order
        col_idx = col_order.index(rank)
        length = col_lengths[col_idx]
        grid[col_idx] = ciphertext_indices[pos:pos+length]
        pos += length
    
    # Read row by row
    result = []
    for row in range(nrows):
        for col in range(ncols):
            if row < len(grid[col]):
                result.append(grid[col][row])
    
    return result

def undo_columnar_transposition_v2(ct, ncols, col_order):
    """
    Alternative: cipher was written by columns in order, read by rows.
    To undo: write cipher into rows, read by columns in reverse order.
    """
    n = len(ct)
    nrows = math.ceil(n / ncols)
    
    # Write cipher into rows
    grid = []
    pos = 0
    for r in range(nrows):
        row = []
        for c in range(ncols):
            if pos < n:
                row.append(ct[pos])
                pos += 1
        grid.append(row)
    
    # Read by columns in col_order
    inv_order = [0] * ncols
    for i, c in enumerate(col_order):
        inv_order[c] = i
    
    result = []
    for c in inv_order:
        for r in range(nrows):
            if c < len(grid[r]):
                result.append(grid[r][c])
    
    return result

def spiral_read(indices, ncols):
    """Read indices arranged in a grid via clockwise spiral."""
    n = len(indices)
    nrows = math.ceil(n / ncols)
    
    # Fill grid
    grid = []
    pos = 0
    for r in range(nrows):
        row = []
        for c in range(ncols):
            if pos < n:
                row.append(indices[pos])
            else:
                row.append(-1)
            pos += 1
        grid.append(row)
    
    # Spiral read
    result = []
    top, bottom, left, right = 0, nrows-1, 0, ncols-1
    while top <= bottom and left <= right:
        for c in range(left, right+1):
            if grid[top][c] != -1:
                result.append(grid[top][c])
        top += 1
        for r in range(top, bottom+1):
            if c <= right and grid[r][right] != -1:
                result.append(grid[r][right])
        right -= 1
        if top <= bottom:
            for c in range(right, left-1, -1):
                if grid[bottom][c] != -1:
                    result.append(grid[bottom][c])
            bottom -= 1
        if left <= right:
            for r in range(bottom, top-1, -1):
                if grid[r][left] != -1:
                    result.append(grid[r][left])
            left += 1
    
    return result

def undo_spiral(cipher_indices, ncols):
    """
    Undo spiral write: cipher was written in spiral order into grid, read row-by-row.
    So we write cipher into grid via spiral order, then read row-by-row.
    """
    n = len(cipher_indices)
    nrows = math.ceil(n / ncols)
    grid = [[-1]*ncols for _ in range(nrows)]
    
    # Generate spiral order positions
    positions = []
    top, bottom, left, right = 0, nrows-1, 0, ncols-1
    while top <= bottom and left <= right:
        for c in range(left, right+1):
            positions.append((top, c))
        top += 1
        for r in range(top, bottom+1):
            positions.append((r, right))
        right -= 1
        if top <= bottom:
            for c in range(right, left-1, -1):
                positions.append((bottom, c))
            bottom -= 1
        if left <= right:
            for r in range(bottom, top-1, -1):
                positions.append((r, left))
            left += 1
    
    # Place cipher text at spiral positions
    for i, (r, c) in enumerate(positions):
        if i < n:
            grid[r][c] = cipher_indices[i]
    
    # Read row by row
    result = []
    for r in range(nrows):
        for c in range(ncols):
            if grid[r][c] != -1:
                result.append(grid[r][c])
    return result

def snake_read(indices, ncols):
    """Boustrophedon: alternate row direction."""
    n = len(indices)
    nrows = math.ceil(n / ncols)
    grid = []
    pos = 0
    for r in range(nrows):
        row = []
        for c in range(ncols):
            if pos < n:
                row.append(indices[pos])
            pos += 1
        grid.append(row)
    
    result = []
    for r in range(nrows):
        if r % 2 == 0:
            result.extend(grid[r])
        else:
            result.extend(reversed(grid[r]))
    return result

def diagonal_read(indices, ncols):
    """Read grid diagonally (top-right to bottom-left)."""
    n = len(indices)
    nrows = math.ceil(n / ncols)
    grid = []
    pos = 0
    for r in range(nrows):
        row = []
        for c in range(ncols):
            if pos < n:
                row.append(indices[pos])
            else:
                row.append(-1)
            pos += 1
        grid.append(row)
    
    result = []
    for d in range(nrows + ncols - 1):
        for r in range(nrows):
            c = d - r
            if 0 <= c < ncols and grid[r][c] != -1:
                result.append(grid[r][c])
    return result

def prime_index_extract(indices):
    """Extract characters at prime-indexed positions (0-based)."""
    return [indices[i] for i in range(len(indices)) if is_prime(i)]

def magic_square_permutation(indices):
    """
    Apply P63 5x5 magic square as a transposition permutation.
    Process text in blocks of 25.
    
    Magic square values (row-major):
    272  138  341  131  151
    366  199  130  320   18
    226  245   91  245  226
     18  320  130  199  366
    151  131  341  138  272
    
    Sorted unique values with row-major position:
    18 → positions 9, 15  → ranks 0,1
    91 → position 12      → rank 2
    130 → positions 7, 17 → ranks 3,4
    131 → positions 3, 21 → ranks 5,6
    138 → positions 1, 23 → ranks 7,8
    151 → positions 4, 20 → ranks 9,10
    199 → positions 6, 18 → ranks 11,12
    226 → positions 10, 14 → ranks 13,14
    245 → positions 11, 16 → ranks 15,16
    272 → positions 0, 24 → ranks 17,18
    320 → positions 8, 19 → ranks 19,20
    341 → positions 2, 22 → ranks 21,22
    366 → positions 5, 13 → ranks 23,24 (note: dup with positions 5,13 but also 366 at pos 24... wait)
    """
    # Magic square values in row-major order (positions 0-24)
    ms = [272, 138, 341, 131, 151,
          366, 199, 130, 320, 18,
          226, 245, 91, 245, 226,
          18, 320, 130, 199, 366,
          151, 131, 341, 138, 272]
    
    # Create rank-order permutation (sort by value, break ties by position)
    indexed = [(val, pos) for pos, val in enumerate(ms)]
    indexed.sort(key=lambda x: (x[0], x[1]))
    
    # perm[rank] = original_position → to read in sorted order
    read_order = [pos for _, pos in indexed]
    
    # Apply to blocks
    n = len(indices)
    result = []
    for block_start in range(0, n, 25):
        block = indices[block_start:block_start+25]
        if len(block) == 25:
            reordered = [block[read_order[i]] for i in range(25)]
            result.extend(reordered)
        else:
            result.extend(block)  # Partial block unchanged
    
    return result

def magic_square_inverse_permutation(indices):
    """Inverse of magic square permutation — undo the reordering."""
    ms = [272, 138, 341, 131, 151,
          366, 199, 130, 320, 18,
          226, 245, 91, 245, 226,
          18, 320, 130, 199, 366,
          151, 131, 341, 138, 272]
    
    indexed = [(val, pos) for pos, val in enumerate(ms)]
    indexed.sort(key=lambda x: (x[0], x[1]))
    read_order = [pos for _, pos in indexed]
    
    # Inverse permutation
    inv_order = [0] * 25
    for i, pos in enumerate(read_order):
        inv_order[pos] = i
    
    n = len(indices)
    result = []
    for block_start in range(0, n, 25):
        block = indices[block_start:block_start+25]
        if len(block) == 25:
            reordered = [block[inv_order[i]] for i in range(25)]
            result.extend(reordered)
        else:
            result.extend(block)
    
    return result

def rail_fence_decrypt(ct, rails):
    """Undo rail fence cipher."""
    n = len(ct)
    if rails <= 1 or rails >= n:
        return list(ct)
    
    # Calculate pattern
    fence = [[] for _ in range(rails)]
    rail = 0
    direction = 1
    rail_pattern = []
    for i in range(n):
        rail_pattern.append(rail)
        if rail == 0:
            direction = 1
        elif rail == rails - 1:
            direction = -1
        rail += direction
    
    # Count elements per rail
    counts = Counter(rail_pattern)
    
    # Distribute ciphertext to rails
    pos = 0
    for r in range(rails):
        for _ in range(counts[r]):
            fence[r].append(ct[pos])
            pos += 1
    
    # Read off in pattern order
    rail_positions = [0] * rails
    result = []
    for r in rail_pattern:
        result.append(fence[r][rail_positions[r]])
        rail_positions[r] += 1
    
    return result

def every_nth(indices, n, start=0):
    """Read every n-th character starting from start."""
    result = []
    for offset in range(n):
        pos = (start + offset) % n
        while pos < len(indices):
            result.append(indices[pos])
            pos += n
    return result

# ========== MAIN SOLVER ==========

def solve_page(page_num, verbose=True):
    """Try all transposition methods on a page after keyword decryption."""
    if page_num not in PAGE_KEYS:
        print(f"P{page_num:02d}: No known keyword")
        return None
    
    info = PAGE_KEYS[page_num]
    cipher_idx, raw = load_runes(page_num)
    if cipher_idx is None:
        print(f"P{page_num:02d}: No runes file")
        return None
    
    # Step 1: Keyword Vigenère decryption
    key = info['indices']
    mode = info['mode']
    plain = decrypt_vigenere(cipher_idx, key, mode)
    ioc = compute_ioc(plain)
    
    kw = info['keyword']
    kw_len = len(kw)
    
    if verbose:
        print(f"\n{'='*80}")
        print(f"PAGE {page_num:02d} — Keyword: {kw} ({kw_len} chars) Mode: {mode}")
        print(f"Rune count: {len(cipher_idx)} | Post-keyword IoC: {ioc:.4f}")
        print(f"{'='*80}")
    
    rg = to_runeglish(plain)
    
    results = []
    
    # ===== Method 1: Keyword-derived columnar transposition =====
    perm = keyword_column_permutation(kw)
    
    # 1a: Standard columnar (cipher written by rows, read by columns in keyword order)
    undone = undo_columnar_transposition(plain, kw_len, perm)
    rg_undone = to_runeglish(undone)
    score, matched, total = combined_score(rg_undone)
    results.append(('kw_columnar_v1', score, matched, total, rg_undone[:200]))
    
    # 1b: Alternative columnar
    undone2 = undo_columnar_transposition_v2(plain, kw_len, perm)
    rg_undone2 = to_runeglish(undone2)
    score2, matched2, total2 = combined_score(rg_undone2)
    results.append(('kw_columnar_v2', score2, matched2, total2, rg_undone2[:200]))
    
    # 1c: Try all possible column permutations for keyword length
    # (in case keyword mapping is different)
    if kw_len <= 7:  # Only feasible for small keyword lengths
        best_perm_score = -999999
        best_perm = None
        best_perm_text = ""
        for p in permutations(range(kw_len)):
            undone_p = undo_columnar_transposition(plain, kw_len, list(p))
            rg_p = to_runeglish(undone_p)
            s, m, t = combined_score(rg_p)
            if s > best_perm_score:
                best_perm_score = s
                best_perm = p
                best_perm_text = rg_p[:200]
        results.append((f'best_kw_perm_{best_perm}', best_perm_score, 0, 0, best_perm_text))
    
    # ===== Method 2: Magic square 5x5 permutation =====
    ms_result = magic_square_permutation(plain)
    rg_ms = to_runeglish(ms_result)
    score_ms, matched_ms, total_ms = combined_score(rg_ms)
    results.append(('magic_square_fwd', score_ms, matched_ms, total_ms, rg_ms[:200]))
    
    ms_inv = magic_square_inverse_permutation(plain)
    rg_msi = to_runeglish(ms_inv)
    score_msi, matched_msi, total_msi = combined_score(rg_msi)
    results.append(('magic_square_inv', score_msi, matched_msi, total_msi, rg_msi[:200]))
    
    # ===== Method 3: Columnar transposition with various widths =====
    for width in [3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 17, 19, 23, 29]:
        # Simple columnar (no key permutation)
        undone_w = undo_columnar_transposition(plain, width, list(range(width)))
        rg_w = to_runeglish(undone_w)
        s, m, t = combined_score(rg_w)
        results.append((f'columnar_w{width}', s, m, t, rg_w[:200]))
    
    # ===== Method 4: Spiral read =====
    for width in [5, 7, 11, 13, 17, 19, 23, 29]:
        sp = undo_spiral(plain, width)
        rg_sp = to_runeglish(sp)
        s, m, t = combined_score(rg_sp)
        results.append((f'spiral_w{width}', s, m, t, rg_sp[:200]))
    
    # ===== Method 5: Snake/Boustrophedon =====
    for width in [5, 7, 11, 13, 17, 19, 23, 29]:
        sn = snake_read(plain, width)
        rg_sn = to_runeglish(sn)
        s, m, t = combined_score(rg_sn)
        results.append((f'snake_w{width}', s, m, t, rg_sn[:200]))
    
    # ===== Method 6: Rail fence =====
    for rails in [2, 3, 4, 5, 7, 11, 13]:
        rf = rail_fence_decrypt(plain, rails)
        rg_rf = to_runeglish(rf)
        s, m, t = combined_score(rg_rf)
        results.append((f'railfence_{rails}', s, m, t, rg_rf[:200]))
    
    # ===== Method 7: Diagonal read =====
    for width in [5, 7, 11, 13, 17, 19]:
        dg = diagonal_read(plain, width)
        rg_dg = to_runeglish(dg)
        s, m, t = combined_score(rg_dg)
        results.append((f'diagonal_w{width}', s, m, t, rg_dg[:200]))
    
    # ===== Method 8: Prime index extraction =====
    prime_ext = prime_index_extract(plain)
    if prime_ext:
        rg_pe = to_runeglish(prime_ext)
        ioc_pe = compute_ioc(prime_ext)
        s, m, t = combined_score(rg_pe)
        results.append((f'prime_extract(IoC={ioc_pe:.3f})', s, m, t, rg_pe[:200]))
    
    # ===== Method 9: Every-Nth =====
    for n in [2, 3, 5, 7, 11, 13]:
        en = every_nth(plain, n)
        rg_en = to_runeglish(en)
        s, m, t = combined_score(rg_en)
        results.append((f'every_{n}th', s, m, t, rg_en[:200]))
    
    # ===== Method 10: Reverse =====
    rev = list(reversed(plain))
    rg_rev = to_runeglish(rev)
    s, m, t = combined_score(rg_rev)
    results.append(('reversed', s, m, t, rg_rev[:200]))
    
    # ===== Method 11: Keyword columnar + magic square (double transposition) =====
    if kw_len <= 8:
        # First undo keyword columnar, then magic square
        undone_kw = undo_columnar_transposition(plain, kw_len, perm)
        ms_after = magic_square_permutation(undone_kw)
        rg_double = to_runeglish(ms_after)
        s, m, t = combined_score(rg_double)
        results.append(('kw_col_then_ms', s, m, t, rg_double[:200]))
        
        # Reverse: magic square first, then keyword columnar
        ms_first = magic_square_permutation(plain)
        undone_after = undo_columnar_transposition(ms_first, kw_len, perm)
        rg_double2 = to_runeglish(undone_after)
        s, m, t = combined_score(rg_double2)
        results.append(('ms_then_kw_col', s, m, t, rg_double2[:200]))
    
    # ===== Baseline: No transposition =====
    score_base, matched_base, total_base = combined_score(rg)
    results.append(('NO_TRANSPOSITION', score_base, matched_base, total_base, rg[:200]))
    
    # Sort by score descending
    results.sort(key=lambda x: -x[1])
    
    if verbose:
        print(f"\n{'Method':<35} {'Score':>7} {'Match':>5} {'Words':>5} | Text Preview")
        print("-" * 120)
        for method, score, matched, total, text in results[:25]:
            print(f"{method:<35} {score:>7} {matched:>5} {total:>5} | {text[:75]}")
    
    return results

def main():
    load_words()
    print(f"Loaded {len(WORD_SET)} words for scoring")
    
    all_results = {}
    
    for pg in range(21, 31):
        results = solve_page(pg)
        if results:
            all_results[pg] = results
    
    # Global summary
    print("\n" + "=" * 80)
    print("GLOBAL SUMMARY — Best method per page")
    print("=" * 80)
    print(f"{'Page':>4} | {'Best Method':<35} {'Score':>7} | Text Preview")
    print("-" * 100)
    
    for pg in range(21, 31):
        if pg in all_results and all_results[pg]:
            best = all_results[pg][0]
            print(f"P{pg:02d}  | {best[0]:<35} {best[1]:>7} | {best[4][:60]}")

if __name__ == '__main__':
    main()
