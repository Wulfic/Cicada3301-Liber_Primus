#!/usr/bin/env python3
"""
Concatenated-Page + Prime Rearrangement Attack
================================================
Hypothesis: Unsolved dash-separated pages (18-55) may be one continuous ciphertext.
The totient stream key index may be CONTINUOUS across pages.
Also: P19 says "REARRANGING THE PRIMES" — test prime-based permutations.

1. Concatenate all dash-separated unsolved pages → one stream → totient decrypt
2. Concatenate in different PAGE ORDERINGS (by prime permutation)
3. Try totient stream across concatenated pages with F-skip variants
4. Test wide columnar transposition on concatenated pages
5. Test rearranging individual page runes by prime-position permutation
"""

import os, sys
from collections import Counter, OrderedDict

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
             'WITHIN','DEEP','VOID','PRIMES','SACRED','DIVINE','SHADOW','SEEK',
             'PATH','KNOW','SELF','BEING','MIND']
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

def has_dash_separator(rune_text):
    return '-' in rune_text

def has_bullet_separator(rune_text):
    return '\u2022' in rune_text or '•' in rune_text

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

def gen_primes(limit):
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, limit+1, i):
                sieve[j] = False
    return [i for i in range(2, limit+1) if sieve[i]]

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

PRIMES = gen_primes(20000)
TOTIENTS_OF_PRIMES = [euler_totient(p) for p in PRIMES]

IOC_THRESHOLD = 1.45
SCORE_THRESHOLD = 2000

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    repo_dir = os.path.dirname(base_dir)
    pages_dir = os.path.join(repo_dir, 'LiberPrimus', 'pages')
    
    # Load ALL pages with metadata
    all_pages = OrderedDict()
    for p in range(0, 75):
        rt = load_page(pages_dir, p)
        if rt:
            shifts = parse_shifts(rt)
            if len(shifts) > 5:
                all_pages[p] = {
                    'raw': rt,
                    'shifts': shifts,
                    'n': len(shifts),
                    'has_dash': has_dash_separator(rt),
                    'has_bullet': has_bullet_separator(rt)
                }
    
    # Classify pages by separator
    dash_pages = {p: d for p, d in all_pages.items() if d['has_dash'] and 18 <= p <= 54}
    bullet_pages = {p: d for p, d in all_pages.items() if d['has_bullet'] and 18 <= p <= 54}
    
    print(f"Total pages loaded: {len(all_pages)}")
    print(f"Unsolved dash pages (18-54): {sorted(dash_pages.keys())}")
    print(f"  Total dash runes: {sum(d['n'] for d in dash_pages.values())}")
    print(f"Unsolved bullet pages (18-54): {sorted(bullet_pages.keys())}")
    print(f"  Total bullet runes: {sum(d['n'] for d in bullet_pages.values())}")
    
    all_results = []
    
    # =====================================================================
    print("\n" + "=" * 80)
    print("ATTACK 1: CONTINUOUS TOTIENT STREAM ACROSS CONCATENATED PAGES")
    print("Pages concatenated in order, totient key index continuous")
    print("=" * 80)
    
    # Concatenate dash pages in order
    dash_order = sorted(dash_pages.keys())
    concat_dash = []
    page_boundaries = [0]
    for p in dash_order:
        concat_dash.extend(dash_pages[p]['shifts'])
        page_boundaries.append(len(concat_dash))
    
    total_n = len(concat_dash)
    print(f"  Concatenated {len(dash_order)} dash pages: {total_n} runes total")
    
    contig_hits = 0
    total_contig = 0
    
    for offset in range(0, 500, 1):
        for skip_val in [0, -1]:  # -1 means no skip
            total_contig += 1
            
            plain = []
            key_idx = offset
            for i in range(total_n):
                if key_idx >= len(TOTIENTS_OF_PRIMES):
                    break
                k = TOTIENTS_OF_PRIMES[key_idx] % 29
                p_val = (concat_dash[i] - k) % 29
                plain.append(p_val)
                
                if skip_val == -1 or p_val != skip_val:
                    key_idx += 1
            
            if len(plain) < 100:
                continue
            
            # Check IoC on sliding windows
            for w_start in range(0, min(len(plain), 2000), 200):
                window = plain[w_start:w_start+500]
                if len(window) < 100:
                    continue
                ioc = calc_ioc(window)
                if ioc > IOC_THRESHOLD:
                    text = decode(window[:100])
                    sc = score_text(text)
                    contig_hits += 1
                    
                    # Find which page this window belongs to
                    page_at = 'unknown'
                    for idx, (start, end) in enumerate(zip(page_boundaries[:-1], page_boundaries[1:])):
                        if start <= w_start < end:
                            page_at = f'P{dash_order[idx]}'
                            break
                    
                    if sc > SCORE_THRESHOLD:
                        print(f"  offset={offset} skip={skip_val} window@{w_start} ({page_at}): IoC={ioc:.3f} score={sc}")
                        print(f"    {text[:80]}")
                        all_results.append(('CONTIG_TOT', 0, f'off={offset}', w_start, ioc, sc, text[:80]))
    
    if contig_hits == 0:
        print("  No continuous totient hits on concatenated dash pages")
    print(f"  Tested {total_contig} continuous configurations")
    
    # Also try Beaufort mode
    print("\n  --- Beaufort mode ---")
    beau_hits = 0
    for offset in range(0, 500, 1):
        for skip_val in [0, -1]:
            plain = []
            key_idx = offset
            for i in range(total_n):
                if key_idx >= len(TOTIENTS_OF_PRIMES):
                    break
                k = TOTIENTS_OF_PRIMES[key_idx] % 29
                p_val = (k - concat_dash[i]) % 29
                plain.append(p_val)
                
                if skip_val == -1 or p_val != skip_val:
                    key_idx += 1
            
            if len(plain) < 100:
                continue
            
            for w_start in range(0, min(len(plain), 2000), 200):
                window = plain[w_start:w_start+500]
                if len(window) < 100:
                    continue
                ioc = calc_ioc(window)
                if ioc > IOC_THRESHOLD:
                    text = decode(window[:100])
                    sc = score_text(text)
                    beau_hits += 1
                    if sc > SCORE_THRESHOLD:
                        page_at = 'unknown'
                        for idx, (start, end) in enumerate(zip(page_boundaries[:-1], page_boundaries[1:])):
                            if start <= w_start < end:
                                page_at = f'P{dash_order[idx]}'
                                break
                        print(f"  BEAU offset={offset} skip={skip_val} window@{w_start} ({page_at}): IoC={ioc:.3f} score={sc}")
                        print(f"    {text[:80]}")
                        all_results.append(('CONTIG_BEAU', 0, f'off={offset}', w_start, ioc, sc, text[:80]))
    
    if beau_hits == 0:
        print("  No Beaufort continuous hits")
    
    # =====================================================================
    print("\n" + "=" * 80)
    print("ATTACK 2: REARRANGED PAGE ORDER")
    print("P19 says 'REARRANGING THE PRIMES' — try different page orderings")
    print("=" * 80)
    
    import itertools
    
    # Test specific rearrangements of a subset
    # The dash pages 21-30 specifically (10 pages, index-based permutation)
    dash_21_30 = [p for p in dash_order if 21 <= p <= 30]
    
    rearrange_hits = 0
    total_rearrange = 0
    
    # Test ordering by prime values
    # Instead of page order [21,22,23,...,30], try ordering by nth prime
    orderings_to_test = [
        ('natural', dash_21_30),
        ('reversed', list(reversed(dash_21_30))),
        ('by_size_asc', sorted(dash_21_30, key=lambda p: dash_pages[p]['n'] if p in dash_pages else 0)),
        ('by_size_desc', sorted(dash_21_30, key=lambda p: dash_pages[p]['n'] if p in dash_pages else 0, reverse=True)),
        ('odd_then_even', [p for p in dash_21_30 if p % 2 == 1] + [p for p in dash_21_30 if p % 2 == 0]),
        ('prime_pages_first', sorted(dash_21_30, key=lambda p: (0 if is_prime(p) else 1, p))),
        ('interleaved', [dash_21_30[i] for i in range(0, len(dash_21_30), 2)] + [dash_21_30[i] for i in range(1, len(dash_21_30), 2)]),
    ]
    
    # Add prime-number based orderings
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    if len(dash_21_30) <= 10:
        # Order pages by mapping: page i → position prime[i] % len
        for p_offset in range(10):
            perm = []
            used = set()
            for i in range(len(dash_21_30)):
                pos = (small_primes[(i + p_offset) % len(small_primes)]) % len(dash_21_30)
                while pos in used:
                    pos = (pos + 1) % len(dash_21_30)
                perm.append(pos)
                used.add(pos)
            reordered = [dash_21_30[perm[i]] for i in range(len(dash_21_30))]
            orderings_to_test.append((f'prime_perm_{p_offset}', reordered))
    
    for order_name, page_order in orderings_to_test:
        concat = []
        for p in page_order:
            if p in dash_pages:
                concat.extend(dash_pages[p]['shifts'])
        
        if len(concat) < 100:
            continue
        
        for offset in range(0, 200, 5):
            total_rearrange += 1
            
            plain = []
            key_idx = offset
            for i in range(len(concat)):
                if key_idx >= len(TOTIENTS_OF_PRIMES):
                    break
                k = TOTIENTS_OF_PRIMES[key_idx] % 29
                p_val = (concat[i] - k) % 29
                plain.append(p_val)
                if p_val != 0:  # F-skip
                    key_idx += 1
            
            if len(plain) < 100:
                continue
            
            # Check first page-sized window
            window = plain[:500]
            ioc = calc_ioc(window)
            if ioc > IOC_THRESHOLD:
                text = decode(window[:100])
                sc = score_text(text)
                rearrange_hits += 1
                if sc > SCORE_THRESHOLD:
                    print(f"  order={order_name} offset={offset}: IoC={ioc:.3f} score={sc}")
                    print(f"    {text[:80]}")
                    all_results.append(('REARRANGE', 0, order_name, offset, ioc, sc, text[:80]))
    
    if rearrange_hits == 0:
        print("  No rearranged page order hits")
    print(f"  Tested {total_rearrange} page rearrangement configurations")
    
    # =====================================================================
    print("\n" + "=" * 80)
    print("ATTACK 3: PRIME-POSITION PERMUTATION WITHIN EACH PAGE")
    print("'Rearranging the primes': permute runes at prime positions")
    print("=" * 80)
    
    perm_hits = 0
    total_perm = 0
    
    target_pages = sorted(dash_pages.keys(), key=lambda p: dash_pages[p]['n'], reverse=True)[:8]
    
    for page_num in target_pages:
        cipher = dash_pages[page_num]['shifts']
        n = len(cipher)
        
        # Extract prime-position and composite-position runes
        prime_pos = [i for i in range(1, n+1) if is_prime(i)]
        composite_pos = [i for i in range(1, n+1) if not is_prime(i) and i > 1]
        
        prime_runes = [cipher[i-1] for i in prime_pos]
        composite_runes = [cipher[i-1] for i in composite_pos]
        
        # Test 1: Interleave prime and composite position runes
        interleaved = []
        pi, ci = 0, 0
        for i in range(n):
            if pi < len(prime_runes) and (ci >= len(composite_runes) or i % 2 == 0):
                interleaved.append(prime_runes[pi])
                pi += 1
            elif ci < len(composite_runes):
                interleaved.append(composite_runes[ci])
                ci += 1
        
        total_perm += 1
        ioc = calc_ioc(interleaved)
        if ioc > IOC_THRESHOLD:
            print(f"  P{page_num} interleaved prime/composite: IoC={ioc:.3f}")
            perm_hits += 1
        
        # Test 2: Reverse prime-position runes, keep composites
        reversed_primes = list(reversed(prime_runes))
        test2 = list(cipher)
        for idx, pos in enumerate(prime_pos):
            if idx < len(reversed_primes):
                test2[pos-1] = reversed_primes[idx]
        
        total_perm += 1
        ioc = calc_ioc(test2)
        if ioc > IOC_THRESHOLD:
            print(f"  P{page_num} reversed prime positions: IoC={ioc:.3f}")
            perm_hits += 1
        
        # Test 3: Sort prime-position runes, then apply totient stream
        sorted_primes = sorted(prime_runes)
        test3 = list(cipher)
        for idx, pos in enumerate(prime_pos):
            if idx < len(sorted_primes):
                test3[pos-1] = sorted_primes[idx]
        
        for offset in range(0, 50, 5):
            total_perm += 1
            plain = []
            key_idx = offset
            for i in range(n):
                if key_idx >= len(TOTIENTS_OF_PRIMES):
                    break
                k = TOTIENTS_OF_PRIMES[key_idx] % 29
                p_val = (test3[i] - k) % 29
                plain.append(p_val)
                if p_val != 0:
                    key_idx += 1
            
            if len(plain) < 20:
                continue
            ioc = calc_ioc(plain)
            if ioc > IOC_THRESHOLD:
                text = decode(plain)
                sc = score_text(text)
                perm_hits += 1
                if sc > SCORE_THRESHOLD:
                    print(f"  P{page_num} sorted+totient offset={offset}: IoC={ioc:.3f} score={sc}")
                    print(f"    {text[:80]}")
                    all_results.append(('PERM_SORT', page_num, 'sorted_prime', offset, ioc, sc, text[:80]))
        
        # Test 4: Read columns from a grid where width = number of primes up to n
        n_primes_in_n = len(prime_pos)
        widths_to_test = [n_primes_in_n] + [p for p in PRIMES if p < n//2 and p > 5][:10]
        
        for width in widths_to_test:
            if width >= n or width < 3:
                continue
            total_perm += 1
            
            # Write runes into rows of given width, read by columns
            nrows = (n + width - 1) // width
            grid = []
            for r in range(nrows):
                row = cipher[r*width:(r+1)*width]
                grid.append(row)
            
            # Read by columns
            col_read = []
            for c in range(width):
                for r in range(nrows):
                    if c < len(grid[r]):
                        col_read.append(grid[r][c])
            
            # Apply totient stream
            plain = []
            key_idx = 0
            for i in range(len(col_read)):
                if key_idx >= len(TOTIENTS_OF_PRIMES):
                    break
                k = TOTIENTS_OF_PRIMES[key_idx] % 29
                p_val = (col_read[i] - k) % 29
                plain.append(p_val)
                if p_val != 0:
                    key_idx += 1
            
            if len(plain) < 20:
                continue
            ioc = calc_ioc(plain)
            if ioc > IOC_THRESHOLD:
                text = decode(plain)
                sc = score_text(text)
                perm_hits += 1
                if sc > SCORE_THRESHOLD:
                    print(f"  P{page_num} grid_width={width}+totient: IoC={ioc:.3f} score={sc}")
                    print(f"    {text[:80]}")
                    all_results.append(('GRID_TOT', page_num, f'w={width}', 0, ioc, sc, text[:80]))
    
    if perm_hits == 0:
        print("  No prime-position permutation hits")
    print(f"  Tested {total_perm} permutation configurations")
    
    # =====================================================================
    print("\n" + "=" * 80)
    print("ATTACK 4: WIDE COLUMNAR TRANSPOSITION ON CONCATENATED PAGES")
    print("If pages 21-54 are one text, try columnar widths 71-199 (primes)")
    print("=" * 80)
    
    # Use all unsolved pages concatenated
    all_unsolved = []
    for p in range(18, 55):
        if p in all_pages:
            all_unsolved.extend(all_pages[p]['shifts'])
    
    total_all = len(all_unsolved)
    print(f"  All unsolved 18-54 concatenated: {total_all} runes")
    
    wide_hits = 0
    total_wide = 0
    
    # Test prime widths
    prime_widths = [p for p in PRIMES if 29 <= p <= 300]
    
    for width in prime_widths:
        if width >= total_all:
            continue
        total_wide += 1
        
        # Standard columnar: write by rows, read by columns
        nrows = (total_all + width - 1) // width
        
        col_read = []
        for c in range(width):
            for r in range(nrows):
                idx = r * width + c
                if idx < total_all:
                    col_read.append(all_unsolved[idx])
        
        # Check IoC of result
        ioc = calc_ioc(col_read[:2000])
        if ioc > IOC_THRESHOLD:
            text = decode(col_read[:100])
            sc = score_text(text)
            wide_hits += 1
            if sc > SCORE_THRESHOLD:
                print(f"  width={width}: IoC={ioc:.3f} score={sc}")
                print(f"    {text[:80]}")
            
            # Also try totient decrypt on the transposed result
            plain = []
            key_idx = 0
            for i in range(len(col_read)):
                if key_idx >= len(TOTIENTS_OF_PRIMES):
                    break
                k = TOTIENTS_OF_PRIMES[key_idx] % 29
                p_val = (col_read[i] - k) % 29
                plain.append(p_val)
                if p_val != 0:
                    key_idx += 1
            
            ioc2 = calc_ioc(plain[:2000])
            if ioc2 > 1.55:
                text2 = decode(plain[:100])
                sc2 = score_text(text2)
                if sc2 > SCORE_THRESHOLD:
                    print(f"  width={width}+totient: IoC={ioc2:.3f} score={sc2}")
                    print(f"    {text2[:80]}")
                    all_results.append(('WIDE_TRANS_TOT', 0, f'w={width}', 0, ioc2, sc2, text2[:80]))
    
    if wide_hits == 0:
        print("  No wide columnar transposition hits")
    print(f"  Tested {total_wide} wide columnar widths")
    
    # =====================================================================
    print("\n" + "=" * 80)
    print("ATTACK 5: PAGE-SPECIFIC TOTIENT WITH PAGE NUMBER AS OFFSET")
    print("Each page uses totient stream starting at index = f(page_number)")
    print("=" * 80)
    
    pgoff_hits = 0
    total_pgoff = 0
    
    for page_num in sorted(all_pages.keys()):
        if not (18 <= page_num <= 54):
            continue
        cipher = all_pages[page_num]['shifts']
        n = len(cipher)
        
        # Try various functions of page number as offset
        offsets_to_try = [
            page_num,                                    # direct
            page_num * page_num,                         # squared
            page_num * 29,                               # page * alphabet_size
            PRIMES[page_num] if page_num < len(PRIMES) else 0,  # prime[page_num]
            euler_totient(page_num),                     # totient(page_num)
            sum(all_pages[p]['n'] for p in sorted(all_pages.keys()) if p < page_num and 18 <= p <= 54),  # cumulative rune count
        ]
        
        for off_idx, offset in enumerate(offsets_to_try):
            if offset >= len(TOTIENTS_OF_PRIMES) - n:
                continue
            total_pgoff += 1
            
            for skip_val in [0, -1]:
                plain = []
                key_idx = offset
                for i in range(n):
                    if key_idx >= len(TOTIENTS_OF_PRIMES):
                        break
                    k = TOTIENTS_OF_PRIMES[key_idx] % 29
                    p_val = (cipher[i] - k) % 29
                    plain.append(p_val)
                    if skip_val == -1 or p_val != skip_val:
                        key_idx += 1
                
                if len(plain) < 20:
                    continue
                ioc = calc_ioc(plain)
                if ioc > IOC_THRESHOLD:
                    text = decode(plain)
                    sc = score_text(text)
                    pgoff_hits += 1
                    labels = ['direct', 'squared', 'page*29', 'prime[pg]', 'totient(pg)', 'cumul_runes']
                    if sc > SCORE_THRESHOLD:
                        print(f"  P{page_num} offset_type={labels[off_idx]}({offset}) skip={skip_val}: IoC={ioc:.3f} score={sc}")
                        print(f"    {text[:80]}")
                        all_results.append(('PG_OFFSET', page_num, labels[off_idx], offset, ioc, sc, text[:80]))
    
    if pgoff_hits == 0:
        print("  No page-specific offset hits")
    print(f"  Tested {total_pgoff} page-specific offset configurations")
    
    # =====================================================================
    print("\n" + "=" * 80)
    print("ATTACK 6: BULLET PAGES — SEPARATE TREATMENT")
    print("Large bullet pages (P20,23,25,32,40,44,50) may use different cipher")
    print("=" * 80)
    
    # Concatenate bullet pages  
    bullet_order = sorted(bullet_pages.keys())
    concat_bullet = []
    for p in bullet_order:
        concat_bullet.extend(bullet_pages[p]['shifts'])
    
    print(f"  Concatenated {len(bullet_order)} bullet pages: {len(concat_bullet)} runes")
    
    bullet_hits = 0
    total_bullet = 0
    
    for offset in range(0, 500, 1):
        for skip_val in [0, -1]:
            total_bullet += 1
            
            plain = []
            key_idx = offset
            for i in range(len(concat_bullet)):
                if key_idx >= len(TOTIENTS_OF_PRIMES):
                    break
                k = TOTIENTS_OF_PRIMES[key_idx] % 29
                p_val = (concat_bullet[i] - k) % 29
                plain.append(p_val)
                if skip_val == -1 or p_val != skip_val:
                    key_idx += 1
            
            if len(plain) < 100:
                continue
            
            for w_start in range(0, min(len(plain), 5000), 500):
                window = plain[w_start:w_start+500]
                if len(window) < 100:
                    continue
                ioc = calc_ioc(window)
                if ioc > IOC_THRESHOLD:
                    text = decode(window[:100])
                    sc = score_text(text)
                    bullet_hits += 1
                    if sc > SCORE_THRESHOLD:
                        print(f"  BULLET offset={offset} skip={skip_val} window@{w_start}: IoC={ioc:.3f} score={sc}")
                        print(f"    {text[:80]}")
                        all_results.append(('BULLET_CONTIG', 0, f'off={offset}', w_start, ioc, sc, text[:80]))
    
    if bullet_hits == 0:
        print("  No concatenated bullet page hits")
    print(f"  Tested {total_bullet} bullet configurations")
    
    # =====================================================================
    # SUMMARY
    # =====================================================================
    print("\n" + "=" * 80)
    print("COMPREHENSIVE SUMMARY")
    print("=" * 80)
    
    if all_results:
        print(f"\n{len(all_results)} potential hits:\n")
        for r in sorted(all_results, key=lambda x: -x[5]):
            print(f"  {r[0]} key={r[2]} param={r[3]}: IoC={r[4]:.3f} score={r[5]}")
            print(f"    {r[6]}")
    else:
        print("\nNO VIABLE HITS across all concatenation and rearrangement attacks.")
        print("\nAttacks tested:")
        print("  - Continuous totient on concatenated dash pages (500 offsets, F-skip + no-skip)")
        print("  - Beaufort mode continuous totient")
        print("  - Rearranged page orderings (17 arrangements)")
        print("  - Prime-position permutation within pages")
        print("  - Grid transposition + totient on individual pages")
        print("  - Wide columnar transposition on all concatenated pages (prime widths 29-300)")
        print("  - Page-number-derived offset (6 functions per page)")
        print("  - Concatenated bullet pages with totient stream")
    
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()
