#!/usr/bin/env python3
"""
"REARRANGING THE PRIME NUMBERS WILL SHOW A PATH TO THE DEOR"

Explore ALL possible interpretations of "rearranging primes":
1. Transposition: read runes in order of prime values
2. Sort by GP prime value of each rune 
3. Extract at prime-INDEXED positions vs non-prime positions
4. Map position i → prime[i] mod N
5. Read in order: positions whose GP values are primes 2,3,5,7,11...
6. Permutation cipher using prime factorization
7. Use the DEOR poem as a running key after rearranging
8. Interleave prime-indexed and non-prime-indexed runes

Test on P20 first (812 runes, directly after the P19 hint),
then on all unsolved pages.
"""

import os, sys, io
from collections import Counter
import math

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# CORRECT GP MAPPING
GP_RUNES = list("ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛂᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ")
GP_LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
            'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
GP_RUNE_TO_IDX = {r: i for i, r in enumerate(GP_RUNES)}
GP_RUNE_TO_IDX['\u16C4'] = 11

LETTER_TO_IDX = {}
for i, lt in enumerate(GP_LATIN):
    LETTER_TO_IDX[lt] = i
for i, lt in enumerate(GP_LATIN):
    if len(lt) == 1: LETTER_TO_IDX[lt] = i
LETTER_TO_IDX['V'] = 1; LETTER_TO_IDX['K'] = 5; LETTER_TO_IDX['Z'] = 15; LETTER_TO_IDX['Q'] = 5

def runes_to_indices(text):
    return [GP_RUNE_TO_IDX[ch] for ch in text if ch in GP_RUNE_TO_IDX]

def indices_to_latin(indices):
    return ''.join(GP_LATIN[i] for i in indices)

def ioc29(indices):
    if len(indices) < 2: return 0
    c = Counter(indices)
    n = len(indices)
    return 29 * sum(v*(v-1) for v in c.values()) / (n*(n-1))

def load_page(pn):
    path = os.path.join('LiberPrimus', 'pages', f'page_{pn:02d}', 'runes.txt')
    if not os.path.exists(path): return None
    with open(path, 'r', encoding='utf-8') as f: return runes_to_indices(f.read())

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i*i <= n:
        if n % i == 0 or n % (i+2) == 0: return False
        i += 6
    return True

def gen_primes(n):
    primes = []
    c = 2
    while len(primes) < n:
        if is_prime(c): primes.append(c)
        c += 1
    return primes

COMMON_WORDS = set(['THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','HER','WAS','ONE','OUR',
    'OUT','HAS','HIS','WHO','THAT','THIS','WITH','HAVE','FROM','THEY','BEEN','SAID',
    'EACH','WHICH','THEIR','WILL','OTHER','ABOUT','INTO','THAN','THEM','THEN','WHEN',
    'SOME','WHAT','WERE','THERE','THOSE','BEING','WOULD','COULD','SHOULD','WISDOM',
    'SACRED','PRIME','DEATH','DEOR','PATH','TRUTH','KNOW','FIND','WITHIN','THROUGH',
    'SELF','HOLY','LOSS','DIVINITY','PILGRIM','INSTAR','CIRCUMFERENCE','EMERGE',
    'TOTIENT','ENCRYPTION','PRIMES','NUMBERS','REARRANGING','SHADOW','AETHEREAL',
    'CABAL','MOURNFUL','VOID','CONSUMPTION','PRESERVATION','ADHERENCE'])

def word_score(text):
    score = 0
    for w in COMMON_WORDS:
        idx = 0
        while True:
            pos = text.find(w, idx)
            if pos == -1: break
            score += len(w) ** 2
            idx = pos + 1
    return score

os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/..')
primes = gen_primes(5000)

# Load the Deor poem from outguess
deor_text = ""
for fn in ['outguess_00.txt', 'outguess_08.txt', 'outguess_17.txt', 'outguess_21.txt', 'outguess_43.txt']:
    path = os.path.join('.', fn)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if 'DEOR' in content.upper() or len(content) > 100:
                deor_text = content
                break

print("=" * 80)
print("REARRANGING PRIMES - COMPREHENSIVE TRANSPOSITION ATTACK")
print("=" * 80)

# ====================== TEST ON P20 FIRST ======================
for target_pn in [20, 19, 18, 21, 25, 32, 40, 44, 50, 57]:
    cipher = load_page(target_pn)
    if not cipher: continue
    n = len(cipher)
    
    print(f"\n{'='*60}")
    print(f"PAGE {target_pn}: {n} runes")
    print(f"{'='*60}")
    
    results = []
    
    # === METHOD 1: Sort positions by GP prime value of rune ===
    # "Rearranging the prime numbers" = sort runes by their prime value
    prime_vals = [(GP_PRIMES[c], i) for i, c in enumerate(cipher)]
    sorted_by_prime = [cipher[i] for _, i in sorted(prime_vals)]
    text = indices_to_latin(sorted_by_prime)
    ic = ioc29(sorted_by_prime)
    ws = word_score(text)
    results.append(('sort_by_prime', ic, ws, text[:80]))
    
    # Stable sort — within same prime value, keep original order
    sorted_stable = [cipher[i] for _, i in sorted(prime_vals, key=lambda x: x[0])]
    text = indices_to_latin(sorted_stable)
    ws = word_score(text)
    results.append(('sort_by_prime_stable', ioc29(sorted_stable), ws, text[:80]))
    
    # === METHOD 2: Extract prime-indexed positions ===
    prime_positions = [cipher[i] for i in range(n) if is_prime(i)]
    non_prime_positions = [cipher[i] for i in range(n) if not is_prime(i)]
    
    text_p = indices_to_latin(prime_positions)
    text_np = indices_to_latin(non_prime_positions)
    results.append(('prime_idx_extract', ioc29(prime_positions), word_score(text_p), f"[{len(prime_positions)}r] {text_p[:60]}"))
    results.append(('nonprime_idx_extract', ioc29(non_prime_positions), word_score(text_np), f"[{len(non_prime_positions)}r] {text_np[:60]}"))
    
    # === METHOD 3: Interleave prime-indexed and non-prime-indexed ===
    interleaved = []
    pi, npi = 0, 0
    for i in range(n):
        if i % 2 == 0 and pi < len(prime_positions):
            interleaved.append(prime_positions[pi]); pi += 1
        elif npi < len(non_prime_positions):
            interleaved.append(non_prime_positions[npi]); npi += 1
        elif pi < len(prime_positions):
            interleaved.append(prime_positions[pi]); pi += 1
    
    text_il = indices_to_latin(interleaved)
    results.append(('interleave_prime_nonprime', ioc29(interleaved), word_score(text_il), text_il[:80]))
    
    # Reverse order: non-prime first, then prime
    interleaved2 = []
    pi, npi = 0, 0
    for i in range(n):
        if i % 2 == 0 and npi < len(non_prime_positions):
            interleaved2.append(non_prime_positions[npi]); npi += 1
        elif pi < len(prime_positions):
            interleaved2.append(prime_positions[pi]); pi += 1
        elif npi < len(non_prime_positions):
            interleaved2.append(non_prime_positions[npi]); npi += 1
    
    text_il2 = indices_to_latin(interleaved2)
    results.append(('interleave_nonprime_prime', ioc29(interleaved2), word_score(text_il2), text_il2[:80]))
    
    # === METHOD 4: Read at positions prime[0], prime[1], prime[2]... ===
    prime_read = []
    for i in range(len(primes)):
        if primes[i] < n:
            prime_read.append(cipher[primes[i]])
        else:
            break
    text_pr = indices_to_latin(prime_read)
    results.append(('read_at_prime_positions', ioc29(prime_read), word_score(text_pr), f"[{len(prime_read)}r] {text_pr[:60]}"))
    
    # === METHOD 5: Transposition where position i → position prime[i] mod n ===
    reordered = [0] * n
    for i in range(n):
        dest = primes[i] % n
        reordered[dest] = cipher[i]
    text_ro = indices_to_latin(reordered)
    results.append(('pos_to_prime_mod_n', ioc29(reordered), word_score(text_ro), text_ro[:80]))
    
    # Reverse: read FROM position prime[i] mod n
    reordered2 = [cipher[primes[i] % n] for i in range(n)]
    text_ro2 = indices_to_latin(reordered2)
    results.append(('read_from_prime_mod_n', ioc29(reordered2), word_score(text_ro2), text_ro2[:80]))
    
    # === METHOD 6: Separate by GP prime value being itself prime ===
    # Some GP values are prime (2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109)
    # ALL GP values are prime by definition! So this doesn't help.
    # But what about indices? Rune INDEX being prime vs not:
    prime_idx_runes = [cipher[i] for i in range(n) if is_prime(cipher[i])]  # rune with prime INDEX 
    nonprime_idx_runes = [cipher[i] for i in range(n) if not is_prime(cipher[i])]
    
    if prime_idx_runes:
        text_pir = indices_to_latin(prime_idx_runes)
        results.append(('value_is_prime_idx', ioc29(prime_idx_runes), word_score(text_pir), 
                        f"[{len(prime_idx_runes)}r] {text_pir[:60]}"))
    if nonprime_idx_runes:
        text_npir = indices_to_latin(nonprime_idx_runes)
        results.append(('value_nonprime_idx', ioc29(nonprime_idx_runes), word_score(text_npir), 
                        f"[{len(nonprime_idx_runes)}r] {text_npir[:60]}"))
    
    # === METHOD 7: GP prime value IS prime → treat as "prime runes" ===
    # All GP values are prime, so separate by whether the VALUE is in a specific subset
    # The first 10 primes (2,3,5,7,11,13,17,19,23,29) map to GP indices 0-9
    # These are: F,U,TH,O,R,C,G,W,H,N
    # The remaining 19 (31-109) map to GP indices 10-28
    small_prime_runes = [cipher[i] for i in range(n) if GP_PRIMES[cipher[i]] <= 29]
    large_prime_runes = [cipher[i] for i in range(n) if GP_PRIMES[cipher[i]] > 29]
    
    if small_prime_runes and large_prime_runes:
        text_sp = indices_to_latin(small_prime_runes)
        text_lp = indices_to_latin(large_prime_runes)
        results.append(('small_prime_value', ioc29(small_prime_runes), word_score(text_sp),
                        f"[{len(small_prime_runes)}r] {text_sp[:60]}"))
        results.append(('large_prime_value', ioc29(large_prime_runes), word_score(text_lp),
                        f"[{len(large_prime_runes)}r] {text_lp[:60]}"))
    
    # === METHOD 8: Columnar transposition with prime column counts ===
    for num_cols in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]:
        if num_cols > n // 2: break
        
        # Write by rows, read by columns
        rows = (n + num_cols - 1) // num_cols
        grid = []
        for r in range(rows):
            row = []
            for c in range(num_cols):
                idx = r * num_cols + c
                if idx < n:
                    row.append(cipher[idx])
            grid.append(row)
        
        # Read by columns
        col_read = []
        for c in range(num_cols):
            for r in range(rows):
                if c < len(grid[r]):
                    col_read.append(grid[r][c])
        
        text_cr = indices_to_latin(col_read)
        ic = ioc29(col_read)
        ws = word_score(text_cr)
        if ws > 20 or ic > 1.2:
            results.append((f'columnar_{num_cols}cols', ic, ws, text_cr[:80]))
        
        # Also try: write by columns, read by rows
        rows2 = (n + num_cols - 1) // num_cols
        grid2 = []
        for c in range(num_cols):
            col = []
            for r in range(rows2):
                idx = c * rows2 + r
                if idx < n:
                    col.append(cipher[idx])
            grid2.append(col)
        
        # Read by rows
        row_read = []
        for r in range(rows2):
            for c in range(num_cols):
                if r < len(grid2[c]):
                    row_read.append(grid2[c][r])
        
        text_rr = indices_to_latin(row_read)
        ic2 = ioc29(row_read)
        ws2 = word_score(text_rr)
        if ws2 > 20 or ic2 > 1.2:
            results.append((f'rev_columnar_{num_cols}cols', ic2, ws2, text_rr[:80]))
    
    # === METHOD 9: Rail fence / zigzag with prime number of rails ===
    for rails in [2, 3, 5, 7]:
        if rails > n // 2: break
        
        # Encode: write in zigzag pattern
        fence = [[] for _ in range(rails)]
        rail = 0
        direction = 1
        for i in range(n):
            fence[rail].append(cipher[i])
            rail += direction
            if rail == rails - 1 or rail == 0:
                direction *= -1
        
        # Read rail by rail
        zigzag_read = []
        for r in range(rails):
            zigzag_read.extend(fence[r])
        
        text_zz = indices_to_latin(zigzag_read)
        ic_zz = ioc29(zigzag_read)
        ws_zz = word_score(text_zz)
        if ws_zz > 20 or ic_zz > 1.2:
            results.append((f'zigzag_{rails}rails', ic_zz, ws_zz, text_zz[:80]))
        
        # Decode: undo zigzag
        # The input IS in zigzag form, need to reconstruct original order
        # First, determine the length of each rail
        rail_lengths = [0] * rails
        rail = 0; direction = 1
        for i in range(n):
            rail_lengths[rail] += 1
            rail += direction
            if rail == rails - 1 or rail == 0: direction *= -1
        
        # Assign cipher characters to rails
        rail_data = []
        pos = 0
        for r in range(rails):
            rail_data.append(cipher[pos:pos+rail_lengths[r]])
            pos += rail_lengths[r]
        
        # Read in zigzag order
        rail_idx = [0] * rails
        zigzag_dec = []
        rail = 0; direction = 1
        for i in range(n):
            zigzag_dec.append(rail_data[rail][rail_idx[rail]])
            rail_idx[rail] += 1
            rail += direction
            if rail == rails - 1 or rail == 0: direction *= -1
        
        text_zzd = indices_to_latin(zigzag_dec)
        ic_zzd = ioc29(zigzag_dec)
        ws_zzd = word_score(text_zzd)
        if ws_zzd > 20 or ic_zzd > 1.2:
            results.append((f'unzigzag_{rails}rails', ic_zzd, ws_zzd, text_zzd[:80]))
    
    # === METHOD 10: Scytale cipher (wrap around cylinder of prime circumference) ===
    for circumf in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]:
        if circumf > n // 2: break
        
        # Read down then across
        scytale = [cipher[(i * circumf) % n] for i in range(n)]
        text_sc = indices_to_latin(scytale)
        ic_sc = ioc29(scytale)
        ws_sc = word_score(text_sc)
        if ws_sc > 20 or ic_sc > 1.2:
            results.append((f'scytale_{circumf}', ic_sc, ws_sc, text_sc[:80]))
    
    # Print all results sorted by word score
    results.sort(key=lambda x: (-x[2], -x[1]))
    for method, ic, ws, text in results[:15]:
        if ws > 0 or ic > 1.15:
            print(f"  {method:30s}: IoC={ic:.4f} wscore={ws:3d}  {text}")

# ====================== SPECIAL: P20 DUAL-LAYER ANALYSIS ======================
print("\n" + "=" * 80)
print("SPECIAL: P20 DUAL-LAYER (prime-valued vs non-prime-valued runes)")
print("=" * 80)

p20 = load_page(20)
if p20:
    n = len(p20)
    
    # Separate by whether the rune's GP PRIME VALUE is ≤ 29 (first 10 primes)
    # Community found: "prime-valued runes" (TH,O,C,W,J,P,B,M,D = indices with certain primes)
    # Actually, the P20 analysis says: runes whose GP VALUES are prime
    # ALL GP values are prime, so this interpretation can't be right
    # 
    # The CORRECT interpretation from COMPREHENSIVE_CLUE_SUMMARY.md:
    # "Prime-valued runes" = runes at positions where the INDEX is a prime number
    # vs "non-prime" = runes at composite/0/1 positions
    
    # Layer 1: Runes at prime positions
    prime_pos = [p20[i] for i in range(n) if is_prime(i)]
    nonprime_pos = [p20[i] for i in range(n) if not is_prime(i)]
    
    print(f"P20: {n} runes total")
    print(f"  Prime positions: {len(prime_pos)} runes, IoC = {ioc29(prime_pos):.4f}")
    print(f"  Non-prime positions: {len(nonprime_pos)} runes, IoC = {ioc29(nonprime_pos):.4f}")
    print(f"  Prime text: {indices_to_latin(prime_pos)[:80]}")
    print(f"  NonPrime text: {indices_to_latin(nonprime_pos)[:80]}")
    
    # Try shift/Caesar on each layer
    for layer_name, layer in [('prime', prime_pos), ('nonprime', nonprime_pos)]:
        best = (0, 0, '')
        for shift in range(29):
            dec = [(c - shift) % 29 for c in layer]
            text = indices_to_latin(dec)
            ws = word_score(text)
            if ws > best[0]:
                best = (ws, shift, text[:80])
        ws, shift, text = best
        print(f"  {layer_name} best shift={shift}: wscore={ws}  {text}")
    
    # Try separation by GP INDEX being in first 10 (F-N) vs rest (I-EA)  
    low_idx = [p20[i] for i in range(n) if p20[i] < 10]
    high_idx = [p20[i] for i in range(n) if p20[i] >= 10]
    print(f"\n  Low-index runes (F-N, idx 0-9): {len(low_idx)}, IoC = {ioc29(low_idx):.4f}")
    print(f"  High-index runes (I-EA, idx 10-28): {len(high_idx)}, IoC = {ioc29(high_idx):.4f}")
    
    # What the community ACTUALLY found: separate by whether the GP prime is itself prime-indexed
    # I.e., is GP_PRIMES[rune_idx] the Nth prime where N is prime?
    # Prime-indexed primes: prime[2]=5, prime[3]=7, prime[5]=13, prime[7]=19, prime[11]=37, prime[13]=43...
    # Actually this is getting confusing. Let me read what they actually did.
    
    # From COMPREHENSIVE_CLUE_SUMMARY.md:  
    # "Prime-valued runes (237 runes, letters: TH, O, C, W, J, P, B, M, D)"
    # These are GP indices: TH=2, O=3, C=5, W=7, J=11, P=13, B=17, M=19, D=23
    # Notice: these indices ARE themselves prime numbers!
    # So the separation is: rune INDEX is prime (2,3,5,7,11,13,17,19,23) vs composite/0/1
    
    prime_indices_set = {2, 3, 5, 7, 11, 13, 17, 19, 23}  # prime GP indices
    prime_valued = [p20[i] for i in range(n) if p20[i] in prime_indices_set]
    non_prime_valued = [p20[i] for i in range(n) if p20[i] not in prime_indices_set]
    
    print(f"\n  Runes with prime GP INDEX (TH,O,C,W,J,P,B,M,D): {len(prime_valued)}, IoC = {ioc29(prime_valued):.4f}")
    print(f"  Runes with non-prime GP INDEX: {len(non_prime_valued)}, IoC = {ioc29(non_prime_valued):.4f}")
    print(f"  Prime-valued text: {indices_to_latin(prime_valued)[:80]}")
    print(f"  Non-prime text: {indices_to_latin(non_prime_valued)[:80]}")
    
    # Try Caesar shifts on non-prime-valued layer (community says shift -2 yields "THE" 6x)
    for shift in range(29):
        dec = [(c - shift) % 29 for c in non_prime_valued]
        text = indices_to_latin(dec)
        the_count = text.count('THE')
        if the_count >= 3:
            ws = word_score(text)
            print(f"  NonPrime shift-{shift}: 'THE' x{the_count}, wscore={ws}  {text[:80]}")

print("\n=== REARRANGING PRIMES ANALYSIS COMPLETE ===")
