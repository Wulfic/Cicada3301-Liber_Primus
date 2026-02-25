#!/usr/bin/env python3
"""
Fractionation Cipher Attack - BIFID, TRIFID, PLAYFAIR, NIHILIST
================================================================
These ciphers perfectly explain IoC ≈ 1.0 because they split each symbol
into coordinates, mix them, then recombine. This inherently flattens frequency.

1. BIFID: 5×6 grid, period 2-50, keyword-ordered grids from P63
2. TRIFID: 3×3×4=36 or 3×10=30 grid with 29 values  
3. PLAYFAIR: digraph substitution on 5×6 grid
4. NIHILIST: Polybius coordinates + key addition
5. ADFGVX-style: Polybius + columnar transposition
"""

import os, sys, itertools
from collections import Counter

RUNE_TO_SHIFT = {
    '\u16a0': 0, '\u16a2': 1, '\u16a6': 2, '\u16a9': 3, '\u16b1': 4,
    '\u16b3': 5, '\u16b7': 6, '\u16b9': 7, '\u16bb': 8, '\u16be': 9,
    '\u16c1': 10, '\u16c2': 11, '\u16c7': 12, '\u16c8': 13, '\u16c9': 14,
    '\u16cb': 15, '\u16cf': 16, '\u16d2': 17, '\u16d6': 18, '\u16d7': 19,
    '\u16da': 20, '\u16dd': 21, '\u16df': 22, '\u16de': 23, '\u16aa': 24,
    '\u16ab': 25, '\u16a3': 26, '\u16e1': 27, '\u16e0': 28, '\u16c4': 11
}

SHIFT_TO_ENGLISH = {
    0:'F',1:'U',2:'TH',3:'O',4:'R',5:'C',6:'G',7:'W',8:'H',9:'N',
    10:'I',11:'J',12:'EO',13:'P',14:'X',15:'S',16:'T',17:'B',18:'E',
    19:'M',20:'L',21:'NG',22:'OE',23:'D',24:'A',25:'AE',26:'Y',
    27:'IA',28:'EA'
}

# P63 grid keywords with correct GP mappings (digraph-aware)
KEYWORDS_GP = {
    'SHADOWS': [15,8,24,23,3,7,15],
    'AETHEREAL': [24,18,2,18,4,18,24,20],
    'VOID': [1,3,10,23],
    'CABAL': [5,24,17,24,20],
    'OBSCURA': [3,17,15,5,1,4,24],
    'MOBIUS': [19,3,17,10,1,15],
    'CARNAL': [5,24,4,9,24,20],
    'FORM': [0,3,4,19],
    'MOURNFUL': [19,3,1,4,9,0,1,20],
    'ANALOG': [24,9,24,20,3,6],
    'DIVINITY': [23,10,1,10,9,10,16,26],
    'WARNING': [7,24,4,9,10,21],
    'PRIMES': [13,4,10,19,18,15],
    'CIRCUMFERENCE': [5,10,4,5,1,19,0,18,4,18,9,5,18],
}

def calc_ioc(shifts):
    if len(shifts) < 2: return 0
    freq = Counter(shifts)
    n = len(shifts)
    return sum(f*(f-1) for f in freq.values()) / (n*(n-1)) * 29

def decode(shifts):
    return ''.join(SHIFT_TO_ENGLISH.get(s, '?') for s in shifts)

def score_text(text):
    t = text.upper()
    bigrams = ['TH','HE','IN','ER','AN','RE','ON','AT','EN','ND','ES','OR',
               'TE','ED','IS','IT','AL','AR','ST','TO','HA','OU','SE','WH']
    score = sum(t.count(bg) * 10 for bg in bigrams)
    words = ['THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','WAS','ONE','OUR',
             'THAT','WITH','HAVE','THIS','WILL','YOUR','FROM','THEY','BEEN','SOME',
             'WHEN','WHAT','THERE','WHICH','SHALL','EACH','FIND','WISDOM','TRUTH',
             'WITHIN','DEEP','VOID','PRIMES','SACRED','DIVINE','SHADOW','SEEK']
    for w in words: score += t.count(w) * len(w) * 5
    return score

def parse_shifts(rune_text):
    return [RUNE_TO_SHIFT[ch] for ch in rune_text if ch in RUNE_TO_SHIFT]

def load_page(pages_dir, p):
    path = os.path.join(pages_dir, f'page_{p:02d}', 'runes.txt')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return None

# =========================================================================
# GRID GENERATION
# =========================================================================
def make_grid(keyword_gp=None, nrows=5, ncols=6):
    """Create a Polybius-style grid: 29 symbols in nrows×ncols positions.
    keyword_gp = list of GP shift values to place first (deduped)."""
    used = set()
    order = []
    if keyword_gp:
        for v in keyword_gp:
            if v not in used:
                order.append(v)
                used.add(v)
    for v in range(29):
        if v not in used:
            order.append(v)
            used.add(v)
    # order is now a permutation of 0-28
    # Build lookup tables
    val_to_pos = {}  # value -> (row, col)
    pos_to_val = {}  # (row, col) -> value
    for idx, val in enumerate(order):
        r, c = divmod(idx, ncols)
        val_to_pos[val] = (r, c)
        pos_to_val[(r, c)] = val
    return val_to_pos, pos_to_val, nrows, ncols

# =========================================================================
# BIFID CIPHER DECRYPTION
# =========================================================================
def bifid_decrypt(cipher_shifts, val_to_pos, pos_to_val, nrows, ncols, period):
    """Decrypt Bifid cipher with given period."""
    n = len(cipher_shifts)
    plaintext = []
    
    for start in range(0, n, period):
        block = cipher_shifts[start:start+period]
        p = len(block)
        if p < 2:
            plaintext.extend(block)
            continue
        
        # Step 1: Convert ciphertext block to coordinates
        coords = []
        for v in block:
            r, c = val_to_pos[v]
            coords.append((r, c))
        
        # Step 2: Flatten to pairs: (r0,c0), (r1,c1), ... -> r0,c0,r1,c1,...
        flat = []
        for r, c in coords:
            flat.append(r)
            flat.append(c)
        
        # Step 3: Split into first half (rows) and second half (cols)
        rows = flat[:p]
        cols = flat[p:]
        
        # Step 4: Recombine as (row_i, col_i) -> look up
        for i in range(p):
            r, c = rows[i], cols[i]
            # Clamp to valid positions
            r_clamped = r % nrows
            c_clamped = c % ncols
            pos = (r_clamped, c_clamped)
            if pos in pos_to_val:
                plaintext.append(pos_to_val[pos])
            else:
                plaintext.append(0)  # fallback
    
    return plaintext

# =========================================================================
# TRIFID CIPHER DECRYPTION (3 layers)
# =========================================================================
def make_trifid_grid(keyword_gp=None):
    """Create a 3D Trifid grid: 3×3×4=36 positions for 29 values."""
    used = set()
    order = []
    if keyword_gp:
        for v in keyword_gp:
            if v not in used:
                order.append(v)
                used.add(v)
    for v in range(29):
        if v not in used:
            order.append(v)
            used.add(v)
    
    val_to_tri = {}
    tri_to_val = {}
    for idx, val in enumerate(order):
        layer = idx // 9    # 0, 1, 2 (or 3 for overflow)
        rem = idx % 9
        row = rem // 3
        col = rem % 3
        val_to_tri[val] = (layer, row, col)
        tri_to_val[(layer, row, col)] = val
    return val_to_tri, tri_to_val

def trifid_decrypt(cipher_shifts, val_to_tri, tri_to_val, period):
    """Decrypt Trifid cipher."""
    n = len(cipher_shifts)
    plaintext = []
    
    for start in range(0, n, period):
        block = cipher_shifts[start:start+period]
        p = len(block)
        if p < 2:
            plaintext.extend(block)
            continue
        
        # Convert to coordinates
        coords = []
        for v in block:
            t = val_to_tri[v]
            coords.append(t)
        
        # Flatten: l0,r0,c0,l1,r1,c1,... 
        flat = []
        for l, r, c in coords:
            flat.append(l)
            flat.append(r)
            flat.append(c)
        
        # Split into thirds
        third = p
        layers = flat[:third]
        rows = flat[third:2*third]
        cols = flat[2*third:3*third]
        
        for i in range(p):
            if i < len(layers) and i < len(rows) and i < len(cols):
                l, r, c = layers[i] % 4, rows[i] % 3, cols[i] % 3
                pos = (l, r, c)
                if pos in tri_to_val:
                    plaintext.append(tri_to_val[pos])
                else:
                    plaintext.append(0)
    
    return plaintext

# =========================================================================
# PLAYFAIR CIPHER DECRYPTION (digraph substitution)
# =========================================================================
def playfair_decrypt(cipher_shifts, val_to_pos, pos_to_val, nrows, ncols):
    """Decrypt Playfair cipher (process pairs of runes)."""
    n = len(cipher_shifts)
    if n % 2 == 1:
        cipher_shifts = cipher_shifts + [0]  # pad
    
    plaintext = []
    for i in range(0, len(cipher_shifts), 2):
        a, b = cipher_shifts[i], cipher_shifts[i+1]
        ra, ca = val_to_pos[a]
        rb, cb = val_to_pos[b]
        
        if ra == rb:
            # Same row: shift left
            pa = pos_to_val.get((ra, (ca - 1) % ncols), 0)
            pb = pos_to_val.get((rb, (cb - 1) % ncols), 0)
        elif ca == cb:
            # Same column: shift up
            pa = pos_to_val.get(((ra - 1) % nrows, ca), 0)
            pb = pos_to_val.get(((rb - 1) % nrows, cb), 0)
        else:
            # Rectangle: swap columns
            pa = pos_to_val.get((ra, cb), 0)
            pb = pos_to_val.get((rb, ca), 0)
        
        plaintext.extend([pa, pb])
    
    return plaintext[:n]

# =========================================================================
# NIHILIST CIPHER DECRYPTION
# =========================================================================
def nihilist_decrypt(cipher_shifts, val_to_pos, pos_to_val, key_gp, nrows, ncols):
    """Decrypt Nihilist cipher.
    cipher_num = key_num + plain_num (Polybius coordinates as 2-digit numbers)."""
    n = len(cipher_shifts)
    key_len = len(key_gp)
    
    plaintext = []
    for i in range(n):
        cv = cipher_shifts[i]
        kv = key_gp[i % key_len]
        
        cr, cc = val_to_pos[cv]
        kr, kc = val_to_pos[kv]
        
        # Cipher number = key number + plain number
        # So: plain_num = cipher_num - key_num
        # As 2-digit: cipher_digit = (row+1)*10 + (col+1)
        c_num = (cr + 1) * 10 + (cc + 1)
        k_num = (kr + 1) * 10 + (kc + 1)
        
        p_num = c_num - k_num
        if p_num < 11:
            p_num += 60  # wrap around
        
        pr = (p_num // 10) - 1
        pc = (p_num % 10) - 1
        
        if 0 <= pr < nrows and 0 <= pc < ncols and (pr, pc) in pos_to_val:
            plaintext.append(pos_to_val[(pr, pc)])
        else:
            plaintext.append(0)
    
    return plaintext

# =========================================================================
# ADFGVX-STYLE: Polybius + Columnar Transposition
# =========================================================================
def adfgvx_decrypt(cipher_shifts, val_to_pos, pos_to_val, nrows, ncols, trans_key):
    """ADFGVX: each rune → 2 Polybius digits, then undo columnar transposition,
    then re-pair digits and look up."""
    n = len(cipher_shifts)
    
    # Step 1: Convert cipher to Polybius coordinates (2 digits each)
    polybius = []
    for v in cipher_shifts:
        r, c = val_to_pos[v]
        polybius.append(r)
        polybius.append(c)
    
    total = len(polybius)
    num_cols = len(trans_key)
    
    if num_cols < 2 or total < num_cols:
        return []
    
    # Step 2: Undo columnar transposition
    # Determine column lengths
    full_rows = total // num_cols
    extra = total % num_cols
    
    # Column order from key
    col_order = sorted(range(num_cols), key=lambda i: trans_key[i])
    
    # Read off columns in key order
    plain_cols = [[] for _ in range(num_cols)]
    idx = 0
    for col_idx in col_order:
        col_len = full_rows + (1 if col_idx < extra else 0)
        plain_cols[col_idx] = polybius[idx:idx+col_len]
        idx += col_len
    
    # Reconstruct row-by-row
    flat = []
    for row in range(full_rows + 1):
        for col in range(num_cols):
            if row < len(plain_cols[col]):
                flat.append(plain_cols[col][row])
    
    # Step 3: Re-pair and look up
    plaintext = []
    for i in range(0, len(flat) - 1, 2):
        r, c = flat[i] % nrows, flat[i+1] % ncols
        if (r, c) in pos_to_val:
            plaintext.append(pos_to_val[(r, c)])
        else:
            plaintext.append(0)
    
    return plaintext

# =========================================================================
# MAIN
# =========================================================================
def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    repo_dir = os.path.dirname(base_dir)
    pages_dir = os.path.join(repo_dir, 'LiberPrimus', 'pages')
    
    pages = {}
    for p in range(18, 55):
        rt = load_page(pages_dir, p)
        if rt:
            shifts = parse_shifts(rt)
            if len(shifts) > 20:
                pages[p] = shifts
    
    print(f"Loaded {len(pages)} pages")
    
    # Keywords for grid ordering
    keyword_list = ['SHADOWS', 'AETHEREAL', 'VOID', 'CABAL', 'OBSCURA', 
                    'MOBIUS', 'CARNAL', 'DIVINITY', 'PRIMES', 'CIRCUMFERENCE',
                    'FORM', 'MOURNFUL', 'ANALOG', 'WARNING']
    
    # Include natural order (no keyword)
    grid_configs = [('natural', None)]
    for kw in keyword_list:
        grid_configs.append((kw, KEYWORDS_GP[kw]))
    
    # Target pages (largest first for statistical significance)
    target_pages = sorted(pages.keys(), key=lambda p: len(pages[p]), reverse=True)[:8]
    
    IOC_THRESHOLD = 1.45
    SCORE_THRESHOLD = 1500
    
    all_results = []
    
    # =====================================================================
    print("\n" + "=" * 80)
    print("BIFID CIPHER DECRYPTION")
    print("Grid: 5×6 (30 positions, 29 used), various keyword orderings")
    print("Periods: primes 2-107 + selected composites")
    print("=" * 80)
    
    # Periods to test (all primes up to 107 plus some composites)
    test_periods = sorted(set([2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107] + 
                              list(range(2, 52)) + [109]))
    
    bifid_hits = 0
    total_bifid = 0
    
    for kw_name, kw_gp in grid_configs:
        v2p, p2v, nr, nc = make_grid(kw_gp, 5, 6)
        
        for page_num in target_pages:
            cipher = pages[page_num]
            n = len(cipher)
            
            for period in test_periods:
                if period > n:
                    continue
                total_bifid += 1
                
                plain = bifid_decrypt(cipher, v2p, p2v, nr, nc, period)
                ioc = calc_ioc(plain)
                
                if ioc > IOC_THRESHOLD:
                    text = decode(plain)
                    sc = score_text(text)
                    bifid_hits += 1
                    result = f"  P{page_num} grid={kw_name} period={period}: IoC={ioc:.3f} score={sc}"
                    print(result)
                    if sc > SCORE_THRESHOLD:
                        print(f"    {text[:80]}")
                        all_results.append(('BIFID', page_num, kw_name, period, ioc, sc, text[:120]))
    
    if bifid_hits == 0:
        print("  No Bifid hits above IoC threshold")
    print(f"  Tested {total_bifid} Bifid configurations")
    
    # Also test 6×5 grid orientation
    print("\n  --- Bifid 6×5 grid orientation ---")
    bifid65_hits = 0
    total_bifid65 = 0
    
    for kw_name, kw_gp in grid_configs[:5]:  # top 5 keywords for alternate grid
        v2p, p2v, nr, nc = make_grid(kw_gp, 6, 5)
        
        for page_num in target_pages[:5]:  # top 5 pages
            cipher = pages[page_num]
            n = len(cipher)
            
            for period in [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47]:
                if period > n:
                    continue
                total_bifid65 += 1
                
                plain = bifid_decrypt(cipher, v2p, p2v, nr, nc, period)
                ioc = calc_ioc(plain)
                
                if ioc > IOC_THRESHOLD:
                    text = decode(plain)
                    sc = score_text(text)
                    bifid65_hits += 1
                    result = f"  P{page_num} grid={kw_name}(6x5) period={period}: IoC={ioc:.3f} score={sc}"
                    print(result)
                    if sc > SCORE_THRESHOLD:
                        print(f"    {text[:80]}")
                        all_results.append(('BIFID_6x5', page_num, kw_name, period, ioc, sc, text[:120]))
    
    if bifid65_hits == 0:
        print("  No Bifid 6×5 hits")
    print(f"  Tested {total_bifid65} Bifid 6×5 configurations")
    
    # =====================================================================
    print("\n" + "=" * 80)
    print("TRIFID CIPHER DECRYPTION")
    print("Grid: 3×3×4=36 positions, 29 used")
    print("=" * 80)
    
    trifid_hits = 0
    total_trifid = 0
    
    for kw_name, kw_gp in grid_configs[:5]:
        v2t, t2v = make_trifid_grid(kw_gp)
        
        for page_num in target_pages[:5]:
            cipher = pages[page_num]
            n = len(cipher)
            
            for period in [2,3,5,7,11,13,17,19,23,29,31,37,41,43]:
                if period > n:
                    continue
                total_trifid += 1
                
                plain = trifid_decrypt(cipher, v2t, t2v, period)
                ioc = calc_ioc(plain)
                
                if ioc > IOC_THRESHOLD:
                    text = decode(plain)
                    sc = score_text(text)
                    trifid_hits += 1
                    result = f"  P{page_num} grid={kw_name} period={period}: IoC={ioc:.3f} score={sc}"
                    print(result)
                    if sc > SCORE_THRESHOLD:
                        print(f"    {text[:80]}")
                        all_results.append(('TRIFID', page_num, kw_name, period, ioc, sc, text[:120]))
    
    if trifid_hits == 0:
        print("  No Trifid hits above IoC threshold")
    print(f"  Tested {total_trifid} Trifid configurations")
    
    # =====================================================================
    print("\n" + "=" * 80)
    print("PLAYFAIR CIPHER DECRYPTION")
    print("Digraph substitution on 5×6 grid")
    print("=" * 80)
    
    playfair_hits = 0
    total_playfair = 0
    
    for kw_name, kw_gp in grid_configs:
        v2p, p2v, nr, nc = make_grid(kw_gp, 5, 6)
        
        for page_num in target_pages:
            cipher = pages[page_num]
            total_playfair += 1
            
            plain = playfair_decrypt(cipher, v2p, p2v, nr, nc)
            ioc = calc_ioc(plain)
            
            if ioc > IOC_THRESHOLD:
                text = decode(plain)
                sc = score_text(text)
                playfair_hits += 1
                result = f"  P{page_num} grid={kw_name}: IoC={ioc:.3f} score={sc}"
                print(result)
                if sc > SCORE_THRESHOLD:
                    print(f"    {text[:80]}")
                    all_results.append(('PLAYFAIR', page_num, kw_name, 0, ioc, sc, text[:120]))
    
    # Also test 6×5
    for kw_name, kw_gp in grid_configs[:5]:
        v2p, p2v, nr, nc = make_grid(kw_gp, 6, 5)
        for page_num in target_pages[:5]:
            cipher = pages[page_num]
            total_playfair += 1
            plain = playfair_decrypt(cipher, v2p, p2v, nr, nc)
            ioc = calc_ioc(plain)
            if ioc > IOC_THRESHOLD:
                text = decode(plain)
                sc = score_text(text)
                playfair_hits += 1
                result = f"  P{page_num} grid={kw_name}(6x5): IoC={ioc:.3f} score={sc}"
                print(result)
                all_results.append(('PLAYFAIR_6x5', page_num, kw_name, 0, ioc, sc, text[:120]))
    
    if playfair_hits == 0:
        print("  No Playfair hits above IoC threshold")
    print(f"  Tested {total_playfair} Playfair configurations")
    
    # =====================================================================
    print("\n" + "=" * 80)
    print("NIHILIST CIPHER DECRYPTION")
    print("Polybius coordinates + key subtraction")
    print("=" * 80)
    
    nihilist_hits = 0
    total_nihilist = 0
    
    for kw_name, kw_gp in grid_configs:
        if kw_gp is None:
            continue
        v2p, p2v, nr, nc = make_grid(None, 5, 6)  # Natural grid
        
        for page_num in target_pages[:5]:
            cipher = pages[page_num]
            total_nihilist += 1
            
            plain = nihilist_decrypt(cipher, v2p, p2v, kw_gp, nr, nc)
            ioc = calc_ioc(plain)
            
            if ioc > IOC_THRESHOLD:
                text = decode(plain)
                sc = score_text(text)
                nihilist_hits += 1
                result = f"  P{page_num} key={kw_name}: IoC={ioc:.3f} score={sc}"
                print(result)
                if sc > SCORE_THRESHOLD:
                    print(f"    {text[:80]}")
                    all_results.append(('NIHILIST', page_num, kw_name, 0, ioc, sc, text[:120]))
    
    if nihilist_hits == 0:
        print("  No Nihilist hits above IoC threshold")
    print(f"  Tested {total_nihilist} Nihilist configurations")
    
    # =====================================================================
    print("\n" + "=" * 80)
    print("ADFGVX-STYLE: Polybius + Columnar Transposition")
    print("=" * 80)
    
    adfgvx_hits = 0
    total_adfgvx = 0
    
    # Test column keys derived from P63 keywords
    for kw_name, kw_gp in grid_configs:
        if kw_gp is None or len(kw_gp) < 3:
            continue
        v2p, p2v, nr, nc = make_grid(None, 5, 6)
        trans_key = kw_gp  # Use keyword values as transposition key
        
        for page_num in target_pages[:5]:
            cipher = pages[page_num]
            total_adfgvx += 1
            
            plain = adfgvx_decrypt(cipher, v2p, p2v, nr, nc, trans_key)
            if not plain:
                continue
            ioc = calc_ioc(plain)
            
            if ioc > IOC_THRESHOLD:
                text = decode(plain)
                sc = score_text(text)
                adfgvx_hits += 1
                result = f"  P{page_num} key={kw_name}: IoC={ioc:.3f} score={sc}"
                print(result)
                if sc > SCORE_THRESHOLD:
                    print(f"    {text[:80]}")
                    all_results.append(('ADFGVX', page_num, kw_name, 0, ioc, sc, text[:120]))
    
    if adfgvx_hits == 0:
        print("  No ADFGVX hits above IoC threshold")
    print(f"  Tested {total_adfgvx} ADFGVX configurations")
    
    # =====================================================================
    print("\n" + "=" * 80)
    print("DOUBLE TRANSPOSITION (after simulated Vigenère layer)")
    print("Test if Vigenère + double transposition explains pages 21-30")
    print("=" * 80)
    
    # For pages 21-30 specifically, test Vigenère decryption followed by 
    # double columnar transposition
    dt_hits = 0
    total_dt = 0
    
    for kw_name, kw_gp in grid_configs:
        if kw_gp is None:
            continue
        key = kw_gp
        key_len = len(key)
        
        for page_num in range(21, 31):
            if page_num not in pages:
                continue
            cipher = pages[page_num]
            n = len(cipher)
            
            # Step 1: Vigenère decrypt
            vig_plain = [(cipher[i] - key[i % key_len]) % 29 for i in range(n)]
            vig_ioc = calc_ioc(vig_plain)
            
            if vig_ioc < 1.3:
                continue  # Not a valid Vigenère key
            
            total_dt += 1
            
            # Step 2: Try simple columnar transposition undos 
            # with various widths from other P63 keywords
            for width in [3,4,5,6,7,8,9,10,11,12,13,14,15,17,19,23,29]:
                if width >= n:
                    continue
                
                # Read-off by columns -> rows (standard columnar decrypt)
                rows_count = (n + width - 1) // width
                full_cols = n % width if n % width != 0 else width
                
                grid = [[] for _ in range(width)]
                idx = 0
                for col in range(width):
                    col_len = rows_count if col < full_cols else rows_count - 1
                    if n % width == 0:
                        col_len = rows_count
                    grid[col] = vig_plain[idx:idx+col_len]
                    idx += col_len
                
                # Read row by row
                result = []
                for row in range(rows_count):
                    for col in range(width):
                        if row < len(grid[col]):
                            result.append(grid[col][row])
                
                ioc = calc_ioc(result)
                if ioc > 1.55:
                    text = decode(result)
                    sc = score_text(text)
                    dt_hits += 1
                    if sc > SCORE_THRESHOLD:
                        print(f"  P{page_num} vig={kw_name} width={width}: IoC={ioc:.3f} score={sc}")
                        print(f"    {text[:80]}")
                        all_results.append(('VIG+TRANS', page_num, kw_name, width, ioc, sc, text[:120]))
    
    if dt_hits == 0:
        print("  No Vigenère+Transposition hits")
    print(f"  Tested {total_dt} Vigenère+Transposition configs")
    
    # =====================================================================
    print("\n" + "=" * 80)
    print("MOBIUS FUNCTION AS CIPHER SELECTOR")
    print("mu(n): -1 = subtract, 0 = skip, 1 = add (from totient/prime stream)")
    print("=" * 80)
    
    def mobius(n):
        """Compute Möbius function μ(n)."""
        if n <= 0: return 0
        if n == 1: return 1
        factors = 0
        d = 2
        temp = n
        while d * d <= temp:
            if temp % d == 0:
                factors += 1
                temp //= d
                if temp % d == 0:
                    return 0  # squared factor
            d += 1
        if temp > 1:
            factors += 1
        return -1 if factors % 2 == 1 else 1
    
    def euler_totient(n):
        if n <= 0: return 0
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
    
    primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,
              101,103,107,109,113,127,131,137,139,149,151,157,163,167,173,179,181,191,193,
              197,199,211,223,227,229,233,239,241,251,257,263,269,271,277,281,283,293,307,
              311,313,317,331,337,347,349,353,359,367,373,379,383,389,397,401,409,419,421,
              431,433,439,443,449,457,461,463,467,479,487,491,499,503,509,521,523,541,547,
              557,563,569,571,577,587,593,599,601,607,613,617,619,631,641,643,647,653,659,
              661,673,677,683,691,701,709,719,727,733,739,743,751,757,761,769,773,787,797,
              809,811,821,823,827,829,839,853,857,859,863,877,881,883,887,907,911,919,929,
              937,941,947,953,967,971,977,983,991,997,1009,1013,1019,1021,1031,1033,1039,
              1049,1051,1061,1063,1069,1087,1091,1093,1097,1103,1109,1117,1123,1129,1151,
              1153,1163,1171,1181,1187,1193,1201,1213,1217,1223,1229,1231,1237,1249,1259,
              1277,1279,1283,1289,1291,1297,1301,1303,1307,1319,1321,1327,1361,1367,1373,
              1381,1399,1409,1423,1427,1429,1433,1439,1447,1451,1453,1459,1471,1481,1483,
              1487,1489,1493,1499,1511,1523,1531,1543,1549,1553,1559,1567,1571,1579,1583,
              1597,1601,1607,1609,1613,1619,1621,1627,1637,1657,1663,1667,1669,1693,1697,
              1699,1709,1721,1723,1733,1741,1747,1753,1759,1777,1783,1787,1789,1801,1811,
              1823,1831,1847,1861,1867,1871,1873,1877,1879,1889,1901,1907,1913,1931,1933,
              1949,1951,1973,1979,1987,1993,1997,1999]
    
    totients = [euler_totient(p) for p in primes[:2500]]
    
    mobius_hits = 0
    total_mobius = 0
    
    for page_num in target_pages[:5]:
        cipher = pages[page_num]
        n = len(cipher)
        
        for offset in range(0, 200, 5):
            total_mobius += 1
            
            # Möbius-controlled totient stream
            plain = []
            key_idx = offset
            for i in range(n):
                if key_idx >= len(totients):
                    break
                mu_val = mobius(key_idx + 1)
                if mu_val == 0:
                    # Skip this position in key stream
                    plain.append(cipher[i])  # pass through
                elif mu_val == 1:
                    plain.append((cipher[i] - totients[key_idx]) % 29)
                else:  # mu_val == -1
                    plain.append((cipher[i] + totients[key_idx]) % 29)
                key_idx += 1
            
            if len(plain) < 20:
                continue
            
            ioc = calc_ioc(plain)
            if ioc > IOC_THRESHOLD:
                text = decode(plain)
                sc = score_text(text)
                mobius_hits += 1
                print(f"  P{page_num} offset={offset}: IoC={ioc:.3f} score={sc}")
                if sc > SCORE_THRESHOLD:
                    print(f"    {text[:80]}")
                    all_results.append(('MOBIUS', page_num, 'totient', offset, ioc, sc, text[:120]))
    
    if mobius_hits == 0:
        print("  No Möbius hits")
    print(f"  Tested {total_mobius} Möbius configurations")
    
    # =====================================================================
    print("\n" + "=" * 80)
    print("CHAOCIPHER SIMULATION")
    print("Two rotating mixed alphabets, self-modifying after each character")
    print("=" * 80)
    
    def chaocipher_decrypt(cipher, left_alphabet, right_alphabet):
        """Decrypt using Chaocipher algorithm."""
        left = list(left_alphabet)
        right = list(right_alphabet)
        plain = []
        
        for ci in cipher:
            # Find cipher value in left alphabet
            if ci not in left:
                plain.append(ci)
                continue
            idx = left.index(ci)
            # Plaintext is at same position in right alphabet
            plain.append(right[idx])
            
            # Permute left alphabet
            # Remove from position, put at position 0, then shift
            extracted = left.pop(idx)
            left.insert(0, extracted)
            # Move position 1 to position 13 (nadir)
            nadir = min(13, len(left) - 1)
            item = left.pop(1)
            left.insert(nadir, item)
            
            # Permute right alphabet
            extracted = right.pop(idx)
            right.insert(0, extracted)
            # Move position 2 to nadir
            item = right.pop(2)
            right.insert(nadir, item)
        
        return plain
    
    chaocipher_hits = 0
    total_chaocipher = 0
    
    # Test with keyword-derived initial alphabets
    for kw_name, kw_gp in grid_configs:
        if kw_gp is None:
            left = list(range(29))
            right = list(range(29))
        else:
            # Left: keyword first, then remaining
            used = set()
            left = []
            for v in kw_gp:
                if v not in used:
                    left.append(v)
                    used.add(v)
            for v in range(29):
                if v not in used:
                    left.append(v)
                    used.add(v)
            right = list(range(29))  # natural order
        
        # Also test with reversed right alphabet
        for right_variant in [list(range(29)), list(range(28, -1, -1))]:
            for page_num in target_pages[:5]:
                cipher = pages[page_num]
                total_chaocipher += 1
                
                plain = chaocipher_decrypt(cipher, left, right_variant)
                ioc = calc_ioc(plain)
                
                if ioc > IOC_THRESHOLD:
                    text = decode(plain)
                    sc = score_text(text)
                    chaocipher_hits += 1
                    print(f"  P{page_num} left={kw_name}: IoC={ioc:.3f} score={sc}")
                    if sc > SCORE_THRESHOLD:
                        print(f"    {text[:80]}")
                        all_results.append(('CHAOCIPHER', page_num, kw_name, 0, ioc, sc, text[:120]))
    
    if chaocipher_hits == 0:
        print("  No Chaocipher hits")
    print(f"  Tested {total_chaocipher} Chaocipher configurations")
    
    # =====================================================================
    print("\n" + "=" * 80)
    print("SOLITAIRE / PONTIFEX CIPHER")
    print("Card deck-based stream cipher adapted to 29 symbols")
    print("=" * 80)
    
    def solitaire_keystream(deck, length):
        """Generate keystream using Solitaire/Pontifex algorithm adapted to 29+2=31 cards."""
        d = list(deck)
        n_cards = len(d)
        joker_a = n_cards - 2  # 29
        joker_b = n_cards - 1  # 30
        ks = []
        
        iterations = 0
        max_iter = length * 10
        
        while len(ks) < length and iterations < max_iter:
            iterations += 1
            
            # Step 1: Move joker A down 1
            pos = d.index(joker_a)
            d.pop(pos)
            new_pos = (pos + 1) % (n_cards)
            if new_pos == 0: new_pos = n_cards - 1
            d.insert(new_pos, joker_a)
            
            # Step 2: Move joker B down 2
            pos = d.index(joker_b)
            d.pop(pos)
            new_pos = (pos + 2) % (n_cards)
            if new_pos == 0: new_pos = n_cards - 1
            d.insert(new_pos, joker_b)
            
            # Step 3: Triple cut
            pos_a = d.index(joker_a)
            pos_b = d.index(joker_b)
            first_joker = min(pos_a, pos_b)
            last_joker = max(pos_a, pos_b)
            d = d[last_joker+1:] + d[first_joker:last_joker+1] + d[:first_joker]
            
            # Step 4: Count cut
            bottom = d[-1]
            if bottom == joker_b:
                bottom = joker_a
            cut_val = min(bottom, n_cards - 1)
            d = d[cut_val:-1] + d[:cut_val] + [d[-1]]
            
            # Step 5: Output
            top = d[0]
            if top == joker_b:
                top = joker_a
            output_card = d[min(top + 1, n_cards - 1)]
            
            if output_card not in (joker_a, joker_b):
                ks.append(output_card % 29)
        
        return ks
    
    solitaire_hits = 0
    total_solitaire = 0
    
    for kw_name, kw_gp in grid_configs[:5]:
        # Build initial deck based on keyword
        if kw_gp is None:
            deck = list(range(31))  # 0-28 = cards, 29,30 = jokers
        else:
            used = set()
            deck = []
            for v in kw_gp:
                if v not in used:
                    deck.append(v)
                    used.add(v)
            for v in range(29):
                if v not in used:
                    deck.append(v)
                    used.add(v)
            deck.extend([29, 30])  # jokers
        
        for page_num in target_pages[:3]:  # top 3 pages (expensive)
            cipher = pages[page_num]
            n = len(cipher)
            total_solitaire += 1
            
            ks = solitaire_keystream(deck, n)
            if len(ks) < n:
                continue
            
            # Try subtraction and addition
            for mode in ['sub', 'add']:
                if mode == 'sub':
                    plain = [(cipher[i] - ks[i]) % 29 for i in range(n)]
                else:
                    plain = [(cipher[i] + ks[i]) % 29 for i in range(n)]
                
                ioc = calc_ioc(plain)
                if ioc > IOC_THRESHOLD:
                    text = decode(plain)
                    sc = score_text(text)
                    solitaire_hits += 1
                    print(f"  P{page_num} deck={kw_name} mode={mode}: IoC={ioc:.3f} score={sc}")
                    if sc > SCORE_THRESHOLD:
                        print(f"    {text[:80]}")
                        all_results.append(('SOLITAIRE', page_num, kw_name, 0, ioc, sc, text[:120]))
    
    if solitaire_hits == 0:
        print("  No Solitaire hits")
    print(f"  Tested {total_solitaire} Solitaire configurations")

    # =====================================================================
    print("\n" + "=" * 80)
    print("NUMBER-THEORETIC FUNCTION VARIANTS")
    print("Möbius μ(n), Liouville λ(n), divisor σ(n) as key streams")
    print("=" * 80)
    
    def liouville(n):
        """Compute Liouville's lambda function."""
        if n <= 0: return 0
        omega = 0
        d = 2
        temp = n
        while d * d <= temp:
            while temp % d == 0:
                omega += 1
                temp //= d
            d += 1
        if temp > 1:
            omega += 1
        return (-1) ** omega
    
    def divisor_sum(n):
        """Sum of divisors σ(n)."""
        if n <= 0: return 0
        s = 0
        for d in range(1, int(n**0.5) + 1):
            if n % d == 0:
                s += d
                if d != n // d:
                    s += n // d
        return s
    
    def omega(n):
        """Number of distinct prime factors."""
        if n <= 1: return 0
        count = 0
        d = 2
        temp = n
        while d * d <= temp:
            if temp % d == 0:
                count += 1
                while temp % d == 0:
                    temp //= d
            d += 1
        if temp > 1:
            count += 1
        return count
    
    nt_hits = 0
    total_nt = 0
    
    # Pre-compute sequences
    max_n = 2500
    tot_seq = [euler_totient(n) % 29 for n in range(1, max_n)]
    mob_seq = [mobius(n) % 29 for n in range(1, max_n)]  # -1 → 28, 0 → 0, 1 → 1
    lio_seq = [liouville(n) % 29 for n in range(1, max_n)]  # -1 → 28, 1 → 1
    div_seq = [divisor_sum(n) % 29 for n in range(1, max_n)]
    omg_seq = [omega(n) for n in range(1, max_n)]
    
    # Totient of primes (as used in P55): totient(prime[n]) = prime[n] - 1
    tot_prime_seq = [(p - 1) % 29 for p in primes[:max_n]]
    
    # Cumulative totient (running sum)
    cum_tot = []
    s = 0
    for n in range(1, max_n):
        s += euler_totient(n)
        cum_tot.append(s % 29)
    
    streams = {
        'divisor_sum': div_seq,
        'cumulative_totient': cum_tot,
        'omega': omg_seq,
        'totient_squared': [(euler_totient(n)**2) % 29 for n in range(1, max_n)],
        'prime_minus_1_div2': [((p-1)//2) % 29 for p in primes[:max_n]],
        'totient_xor_n': [(euler_totient(n) ^ n) % 29 for n in range(1, max_n)],
    }
    
    for stream_name, stream in streams.items():
        for page_num in target_pages[:5]:
            cipher = pages[page_num]
            n = len(cipher)
            
            for offset in range(0, 100, 5):
                if offset + n > len(stream):
                    break
                total_nt += 1
                
                key = stream[offset:offset+n]
                for mode in ['sub', 'add']:
                    if mode == 'sub':
                        plain = [(cipher[i] - key[i]) % 29 for i in range(n)]
                    else:
                        plain = [(cipher[i] + key[i]) % 29 for i in range(n)]
                    
                    ioc = calc_ioc(plain)
                    if ioc > IOC_THRESHOLD:
                        text = decode(plain)
                        sc = score_text(text)
                        nt_hits += 1
                        print(f"  P{page_num} stream={stream_name} offset={offset} mode={mode}: IoC={ioc:.3f} score={sc}")
                        if sc > SCORE_THRESHOLD:
                            print(f"    {text[:80]}")
                            all_results.append(('NT_FUNC', page_num, stream_name, offset, ioc, sc, text[:120]))
    
    if nt_hits == 0:
        print("  No number-theoretic function hits")
    print(f"  Tested {total_nt} number-theoretic configurations")
    
    # =====================================================================
    print("\n" + "=" * 80)
    print("QUADRATIC / POLYNOMIAL KEY FUNCTIONS")
    print("key[i] = (a*i^2 + b*i + c) % 29")
    print("=" * 80)
    
    poly_hits = 0
    total_poly = 0
    
    for page_num in target_pages[:3]:
        cipher = pages[page_num]
        n = len(cipher)
        
        for a in range(1, 29):  # coefficient of i^2
            for b in range(0, 29, 3):  # coefficient of i (sampled)
                total_poly += 1
                key = [(a * i * i + b * i) % 29 for i in range(n)]
                plain = [(cipher[i] - key[i]) % 29 for i in range(n)]
                ioc = calc_ioc(plain)
                
                if ioc > IOC_THRESHOLD:
                    text = decode(plain)
                    sc = score_text(text)
                    poly_hits += 1
                    if sc > SCORE_THRESHOLD:
                        print(f"  P{page_num} a={a} b={b}: IoC={ioc:.3f} score={sc}")
                        print(f"    {text[:80]}")
                        all_results.append(('QUADRATIC', page_num, f'a={a},b={b}', 0, ioc, sc, text[:120]))
    
    if poly_hits == 0:
        print("  No polynomial key hits")
    print(f"  Tested {total_poly} polynomial key configurations")
    
    # =====================================================================
    # SUMMARY
    # =====================================================================
    print("\n" + "=" * 80)
    print("COMPREHENSIVE SUMMARY")
    print("=" * 80)
    
    if all_results:
        print(f"\n{len(all_results)} potential hits found:\n")
        for r in sorted(all_results, key=lambda x: -x[5]):
            cipher_type, pnum, key_info, param, ioc, sc, text = r
            print(f"  {cipher_type} P{pnum} key={key_info} param={param}: IoC={ioc:.3f} score={sc}")
            print(f"    {text[:80]}")
    else:
        print("\nNO VIABLE HITS across all fractionation and advanced ciphers.")
        print("\nCipher types tested this run:")
        print("  - Bifid (5×6, 6×5 grids, 15 keyword orderings, periods 2-109)")
        print("  - Trifid (3×3×4 grid, 5 keywords, periods 2-43)")
        print("  - Playfair (5×6, 6×5 grids, 15 keyword orderings)")
        print("  - Nihilist (14 keyword keys)")
        print("  - ADFGVX (Polybius + columnar transpose, 14 keys)")
        print("  - Double transposition (Vigenère + columnar, 14 keywords)")
        print("  - Möbius function controlled totient stream")
        print("  - Chaocipher (15 keyword alphabets × 2 right variants)")
        print("  - Solitaire/Pontifex (5 deck orderings)")
        print("  - Number-theoretic functions (6 streams × 20 offsets)")
        print("  - Quadratic polynomial keys (28×10 coefficients)")
    
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()
