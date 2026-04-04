#!/usr/bin/env python3
"""
ADFGVX-Style Fractionation Cipher Test for Liber Primus
=========================================================
ADFGVX explained:
1. A Polybius square (or similar fractionation table) maps each symbol → 2 coordinates
2. The coordinates form a stream that is then transposed

For 29 GP symbols, we use a 6×5 mixed table (30 positions, one unused):
- Row index: 0-5 (6 values)
- Col index: 0-4 (5 values)
- 29 positions used, position (5,4)=30 is null

After fractionation: every N-rune message becomes 2N coordinate values
Transposition: various methods (columnar, reverse, skip-2, etc.)

This EXPLAINS IoC ≈ 1.0: fractionated coordinates have near-uniform distribution.

The decipherment:
1. Un-transpose (find the right transposition)
2. Re-pair coordinates
3. Look up in fractionation table

We test P63 keywords for the Polybius square mixing key.
For transposition, we test various prime-width columnar transpositions.
"""

import sys, itertools
from pathlib import Path
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(__file__).resolve().parent.parent
PAGES_DIR = BASE / "pages"

RUNE_TO_IDX = {chr(k): v for k, v in [
    (0x16A0,0),(0x16A2,1),(0x16A6,2),(0x16A9,3),(0x16B1,4),(0x16B3,5),
    (0x16B7,6),(0x16B9,7),(0x16BB,8),(0x16BE,9),(0x16C1,10),(0x16C4,11),
    (0x16C7,12),(0x16C8,13),(0x16C9,14),(0x16CB,15),(0x16CF,16),(0x16D2,17),
    (0x16D6,18),(0x16D7,19),(0x16DA,20),(0x16DD,21),(0x16DF,22),(0x16DE,23),
    (0x16AA,24),(0x16AB,25),(0x16A3,26),(0x16E1,27),(0x16E0,28),
]}
IDX_TO = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
           'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA']

SEPARATORS = set('-. \n\r\t\u2022/')

def load_runes(page_num):
    path = PAGES_DIR / f"page_{page_num:02d}" / "runes.txt"
    if not path.exists():
        return [], []
    with open(path, encoding='utf-8') as f:
        text = f.read()
    words = []; current = []
    for ch in text:
        if ch in RUNE_TO_IDX:
            current.append(RUNE_TO_IDX[ch])
        elif ch in SEPARATORS:
            if current:
                words.append(tuple(current))
                current = []
    if current:
        words.append(tuple(current))
    flat = [r for w in words for r in w]
    return flat, words

def ioc(values):
    if len(values) < 2: return 0.0
    c = Counter(values)
    n = len(values)
    return sum(v*(v-1) for v in c.values()) / (n*(n-1))

def text_to_gp(text):
    """Convert text string to GP indices."""
    IDX = {v: k for k, v in enumerate(IDX_TO)}
    result = []
    i = 0
    text = text.upper()
    multichar = {'TH':2,'OE':22,'EA':28,'IO':27,'NG':21,'AE':25,'EO':12}
    while i < len(text):
        if i+2 <= len(text) and text[i:i+2] in multichar:
            result.append(multichar[text[i:i+2]])
            i += 2
        elif text[i] in IDX:
            result.append(IDX[text[i]])
            i += 1
        else:
            i += 1
    return result

def make_polybius_table(key_indices, rows=6, cols=5):
    """
    Create a 6×5 fractionation table (30 positions) from a key.
    The key permutes the 29 GP symbols in the table.
    Returns: table[row][col] = GP index, and inverse.
    """
    # Generate a permutation of 0-28 based on key
    # Use key to create a "key-mixed alphabet"
    used = set()
    alphabet = []
    # First insert key symbols
    for k in key_indices:
        if k not in used:
            alphabet.append(k)
            used.add(k)
    # Then fill remaining in order
    for i in range(29):
        if i not in used:
            alphabet.append(i)
            used.add(i)
    # alphabet is now a permutation of 0-28
    # Fill 6×5 table row by row (position 29 = null/unused)
    table = [[None]*cols for _ in range(rows)]
    inv_table = {}  # symbol -> (row, col)
    for idx, sym in enumerate(alphabet[:29]):  # only first 29
        r, c = divmod(idx, cols)
        if r < rows:
            table[r][c] = sym
            inv_table[sym] = (r, c)
    return table, inv_table, alphabet

def fractionate(flat, inv_table):
    """Convert flat list of GP indices to list of (row, col) pairs."""
    coords = []
    for sym in flat:
        if sym in inv_table:
            coords.extend(list(inv_table[sym]))
        else:
            coords.append(-1); coords.append(-1)
    return coords

def defractionate(coords, table, rows=6, cols=5):
    """Convert list of coordinate values back to GP indices."""
    result = []
    for i in range(0, len(coords)-1, 2):
        r, c = coords[i], coords[i+1]
        if 0 <= r < rows and 0 <= c < cols and table[r][c] is not None:
            result.append(table[r][c])
        else:
            result.append(-1)
    return result

def columnar_transpose(seq, width, key_order=None):
    """Apply columnar transposition."""
    if not seq:
        return seq
    # If no key_order, just use natural order
    rows = []
    for i in range(0, len(seq), width):
        rows.append(seq[i:i+width])
    if key_order is None:
        key_order = list(range(width))
    # Read columns in key_order
    result = []
    for col in key_order:
        for row in rows:
            if col < len(row):
                result.append(row[col])
    return result

def reverse_columnar(seq, width, key_order=None):
    """Reverse a columnar transposition."""
    if not seq:
        return seq
    n = len(seq)
    num_rows = (n + width - 1) // width
    last_row_cols = n % width if n % width else width
    
    if key_order is None:
        key_order = list(range(width))
    
    # Build columns with proper lengths
    col_len = {}
    for i, c in enumerate(key_order):
        col_len[c] = num_rows if i < last_row_cols or last_row_cols == 0 else num_rows - 1
    # Actually simpler:
    full_cols = n % width if n % width else width
    col_lengths = {}
    for i, c in enumerate(key_order):
        col_lengths[c] = num_rows if i < full_cols or full_cols == width else num_rows - 1
    
    # Extract columns
    columns = {}
    pos = 0
    for c in key_order:
        clen = num_rows  # simplified: use full rows
        columns[c] = seq[pos:pos+clen]
        pos += clen
        if pos > n:
            columns[c] = columns[c][:n-pos+clen]
            break
    
    # Reassemble row by row
    result = []
    for r in range(num_rows):
        for c in range(width):
            if c in columns and r < len(columns[c]):
                result.append(columns[c][r])
    return result

def split_into_rows_cols(coords, length):
    """
    ADFGVX style: split coordinate stream into row-stream and col-stream of length 'length',
    and attempt to recombine them as paired coordinates to produce 'length' decoded symbols.
    """
    if len(coords) < 2 * length:
        return None
    row_stream = coords[:length]
    col_stream = coords[length:]
    result = []
    for r, c in zip(row_stream, col_stream[:length]):
        result.append((r, c))
    return result

def score_plain(plain, word_sizes):
    """Quick score using LP vocabulary."""
    LP = {'THE','AND','FOR','ARE','NOT','YOU','ALL','THIS','THAT','WITH','HAVE','FROM',
          'SELF','TRUTH','SEEK','WITHIN','SACRED','HOLY','WISDOM','PATH','BEING','WAY',
          'EACH','KNOW','FOLLOW','COMMAND','LAW','INSTRUCTION','WELCOME','PILGRIM',
          'DIVINITY','PRIMES','SACRED','ENCRYPT','END','EMERGE','FIND','WILL',
          'ONE','YOUR','EVERY','DUTY','DEEP','ABOVE','SAME','OTHER','SONG'}
    words_text = []
    pos = 0
    for s in word_sizes:
        w = ''.join(IDX_TO[i] for i in plain[pos:pos+s] if 0 <= i < 29)
        words_text.append(w)
        pos += s
    score = 0
    for w in words_text:
        if w in LP:
            score += len(w) * 4
        elif len(w) >= 3 and any(lw in w for lw in LP if len(lw) >= 3):
            score += 4
    return score, words_text

# ======================================================
# Main ADFGVX test
# ======================================================

# P63 keywords (as GP sequences) for Polybius table mixing
KEYWORDS_GP = {
    'DIVINITY': text_to_gp('DIVINITY'),
    'SHADOWS': text_to_gp('SHADOWS'),
    'CABAL': text_to_gp('CABAL'),
    'MOURNFUL': text_to_gp('MOURNFUL'),
    'OBSCURA': text_to_gp('OBSCURA'),
    'VOID': text_to_gp('VOID'),
    'AETHEREAL': text_to_gp('AETHEREAL'),
    'BUFFERS': text_to_gp('BUFFERS'),
    'CARNAL': text_to_gp('CARNAL'),
    'ANALOG': text_to_gp('ANALOG'),
    'FORM': text_to_gp('FORM'),
    'CICADA': text_to_gp('CICADA'),
    'CONSUMPTION': text_to_gp('CONSUMPTION'),
    'ENCRYPT': text_to_gp('ENCRYPT'),
}

print("="*60)
print("ADFGVX FRACTIONATION CIPHER TEST")
print("="*60)

# Test pages 21-30 (best candidates)
test_pages = [21, 22, 23, 27, 28, 30]

for page_num in test_pages:
    flat, words = load_runes(page_num)
    if not flat:
        continue
    word_sizes = [len(w) for w in words]
    print(f"\nPage {page_num}: {len(flat)} runes, {len(words)} words")
    
    n = len(flat)
    best_results = []
    
    for kw_name, kw_gp in KEYWORDS_GP.items():
        table, inv_table, alphabet = make_polybius_table(kw_gp)
        
        # Fractionate the ciphertext
        cipher_coords = fractionate(flat, inv_table)
        if len(cipher_coords) < 2 * n:
            continue
        
        # The cipher_coords stream should be 2n long (n runes × 2 coords each)
        # Try different ADFGVX decryption approaches:
        
        # Approach 1: Split rows/cols and recombine at various cut points
        for split_pt in [n, n-5, n+5, n//2, n*2//3]:
            if split_pt <= 0 or split_pt >= len(cipher_coords):
                continue
            rows = cipher_coords[:split_pt]
            cols = cipher_coords[split_pt:]
            pairs = list(zip(rows, cols[:len(rows)]))
            plain = [table[r][c] if 0 <= r < 6 and 0 <= c < 5 and table[r][c] is not None else -1 
                     for r, c in pairs]
            if n <= len(plain) < n*2:
                plain = plain[:n]
            if len(plain) != n:
                continue
            score, wt = score_plain(plain, word_sizes)
            iv = ioc(plain)
            if score > 20 or iv > 1.3:
                best_results.append((iv, score, kw_name, f'split@{split_pt}', wt[:8]))
        
        # Approach 2: Columnar transposition reversal at prime widths
        for width in [7, 11, 13, 17, 19, 23, 29]:
            if width >= 2*n:
                continue
            # Try reversing width-columnar transposition on the coords
            unT_coords = reverse_columnar(cipher_coords, width)
            # Then pair and defractionate
            plain = defractionate(unT_coords[:2*n], table)[:n]
            if len(plain) != n:
                continue
            score, wt = score_plain(plain, word_sizes)
            iv = ioc(plain)
            if score > 20 or iv > 1.3:
                best_results.append((iv, score, kw_name, f'unT-col-w={width}', wt[:8]))
        
        # Approach 3: Direct defractionate (no transposition)
        plain = defractionate(cipher_coords, table)[:n]
        if len(plain) == n:
            score, wt = score_plain(plain, word_sizes)
            iv = ioc(plain)
            if score > 20 or iv > 1.3:
                best_results.append((iv, score, kw_name, 'no-transpose', wt[:8]))
        
        # Approach 4: Beaufort across fractionated coords
        # key_stream = keyword values repeating
        # coords[i] = key[i%len_kw] op plain_coord[i]
        for mode in ['sub', 'add']:
            # Decrypt coords with keyword as repeating key
            kw_extended = kw_gp * (2*n // len(kw_gp) + 1)
            if mode == 'sub':
                decrypted_coords = [(cipher_coords[i] - kw_extended[i]) % 6 
                                    if i % 2 == 0 else (cipher_coords[i] - kw_extended[i]) % 5
                                    for i in range(2*n)]
            else:
                decrypted_coords = [(cipher_coords[i] + kw_extended[i]) % 6
                                    if i % 2 == 0 else (cipher_coords[i] + kw_extended[i]) % 5
                                    for i in range(2*n)]
            plain = defractionate(decrypted_coords, table)[:n]
            if len(plain) == n:
                score, wt = score_plain(plain, word_sizes)
                iv = ioc(plain)
                if score > 20 or iv > 1.3:
                    best_results.append((iv, score, kw_name, f'coord-{mode}', wt[:8]))
    
    if best_results:
        best_results.sort(reverse=True)
        print(f"  TOP RESULTS:")
        for iv, score, kw, method, sample in best_results[:5]:
            print(f"  {kw}|{method}: IoC={iv:.4f} score={score}")
            print(f"  {' '.join(sample)}")
    else:
        print(f"  No ADFGVX results with IoC>1.3 or score>20")

# ======================================================
# BONUS: Test "TO BELIEVE TRUTH IS TO DESTROY POSSIBILITY" as running key
# ======================================================
print("\n" + "="*60)
print("P08 message as running key test")
print("="*60)

p08_text = "TOBELIEVETRUTHISTODESTROYPOSSIBILITY"
p08_gp = text_to_gp(p08_text)
# Extend by repeating
p08_long = (p08_gp * 200)[:2000]
print(f"P08 text GP key ({len(p08_gp)} elements): {p08_gp}")

for page_num in [21, 22, 23, 27, 28, 30, 31, 32]:
    flat, words = load_runes(page_num)
    if not flat:
        continue
    word_sizes = [len(w) for w in words]
    best = (0, 0, '', '')
    for mode in ['sub', 'add', 'beaufort']:
        key_seg = p08_long[:len(flat)]
        if mode == 'sub':
            plain = [(flat[i] - key_seg[i]) % 29 for i in range(len(flat))]
        elif mode == 'add':
            plain = [(flat[i] + key_seg[i]) % 29 for i in range(len(flat))]
        else:
            plain = [(key_seg[i] - flat[i]) % 29 for i in range(len(flat))]
        score, wt = score_plain(plain, word_sizes)
        iv = ioc(plain)
        if iv > best[0]:
            best = (iv, score, mode, ' '.join(wt[:8]))
    print(f"P{page_num:02d}: best IoC={best[0]:.4f} score={best[1]} mode={best[2]}: {best[3]}")

# ======================================================
# BONUS 2: Test page content cross-reference
# (Solved pages as running keys for unsolved near-neighbors)
# ======================================================
print("\n" + "="*60)
print("Solved page text as running key for near neighbors")
print("="*60)

# Load solved pages and test as keys for nearby unsolved
solved_pages = {
    17: None,  # YAHEOOPYJ → solved
    20: None,  # Deor + prime stream → solved (partially)
}

for solved_pg in [17, 9, 5, 16]:
    s_flat, _ = load_runes(solved_pg)
    if not s_flat:
        continue
    for target_pg in [21, 22, 23, 27, 28, 31, 32]:
        t_flat, t_words = load_runes(target_pg)
        if not t_flat:
            continue
        t_word_sizes = [len(w) for w in t_words]
        best_score = 0
        best_text = ''
        for mode in ['sub', 'add', 'beaufort']:
            key_seg = (s_flat * 10)[:len(t_flat)]
            if mode == 'sub':
                plain = [(t_flat[i] - key_seg[i]) % 29 for i in range(len(t_flat))]
            elif mode == 'add':
                plain = [(t_flat[i] + key_seg[i]) % 29 for i in range(len(t_flat))]
            else:
                plain = [(key_seg[i] - t_flat[i]) % 29 for i in range(len(t_flat))]
            score, wt = score_plain(plain, t_word_sizes)
            iv = ioc(plain)
            if score > best_score:
                best_score = score
                best_text = f"IoC={iv:.4f} mode={mode}: {' '.join(wt[:8])}"
        if best_score > 20:
            print(f"P{solved_pg}→P{target_pg}: score={best_score} {best_text}")

print("\nDone.")
