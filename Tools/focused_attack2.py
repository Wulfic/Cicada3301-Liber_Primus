#!/usr/bin/env python3
"""
Focused attack script:
1. P02 period-35 Vigenere key recovery & hill-climbing
2. Totient cipher with P63 grid numbers as offsets
3. GP prime sequence as running key
4. Primes-based autokey (the P19 hint)
"""

import os, sys, random, math
from collections import Counter

# GP mapping with J fix
GP_RUNES = list("ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛞᛟᛡᛠᚪᚫᚣ")
GP_LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','D','OE','A','EA','IA','AE','Y']
GP_RUNE_TO_IDX = {r: i for i, r in enumerate(GP_RUNES)}

def runes_to_indices(text):
    return [GP_RUNE_TO_IDX[ch] for ch in text if ch in GP_RUNE_TO_IDX]

def indices_to_latin(indices):
    return ''.join(GP_LATIN[i] for i in indices)

def load_page(pn):
    path = os.path.join('LiberPrimus', 'pages', f'page_{pn:02d}', 'runes.txt')
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    return runes_to_indices(text)

def ioc29(indices):
    if len(indices) < 2: return 0
    c = Counter(indices)
    n = len(indices)
    return 29 * sum(v*(v-1) for v in c.values()) / (n*(n-1))

# English letter frequencies for GP (29-symbol alphabet)
# Based on solved LP pages
GP_ENGLISH_FREQ = None  # We'll compute from solved pages

def compute_gp_english_freq():
    """Compute expected GP letter frequencies from solved pages."""
    global GP_ENGLISH_FREQ
    all_plain = []
    
    # Load known solutions - read decoded.txt files
    for pn in list(range(3, 17)) + [55, 59, 63, 64, 68]:
        dec_path = os.path.join('LiberPrimus', 'pages', f'page_{pn:02d}', 'decoded.txt')
        if os.path.exists(dec_path):
            with open(dec_path, 'r', encoding='utf-8') as f:
                text = f.read().strip().upper()
            # Convert to GP indices
            j = 0
            while j < len(text):
                found = False
                if j + 2 <= len(text):
                    for idx, lat in enumerate(GP_LATIN):
                        if len(lat) == 2 and text[j:j+2] == lat:
                            all_plain.append(idx)
                            j += 2
                            found = True
                            break
                if not found:
                    ch = text[j]
                    for idx, lat in enumerate(GP_LATIN):
                        if len(lat) == 1 and ch == lat:
                            all_plain.append(idx)
                            found = True
                            break
                    j += 1
    
    if not all_plain:
        # Fallback: use English digraph-adjusted frequencies
        GP_ENGLISH_FREQ = [1/29] * 29
        return
    
    counts = Counter(all_plain)
    total = sum(counts.values())
    GP_ENGLISH_FREQ = [counts.get(i, 0) / total for i in range(29)]

def chi_squared(indices):
    """Chi-squared statistic against English GP frequency."""
    if GP_ENGLISH_FREQ is None:
        compute_gp_english_freq()
    n = len(indices)
    if n < 5:
        return float('inf')
    counts = Counter(indices)
    chi2 = 0
    for i in range(29):
        expected = n * GP_ENGLISH_FREQ[i]
        if expected > 0:
            observed = counts.get(i, 0)
            chi2 += (observed - expected) ** 2 / expected
    return chi2

# English word scoring
COMMON_WORDS = {'THE','AND','OF','TO','IN','IS','IT','THAT','FOR','WAS','ON','ARE',
    'AS','WITH','HIS','THEY','BE','AT','ONE','HAVE','THIS','FROM','OR','HAD','BY',
    'NOT','BUT','SOME','WHAT','THERE','WE','CAN','OUT','OTHER','WERE','ALL','YOUR',
    'WHEN','UP','USE','HOW','EACH','WHICH','THEIR','IF','DO','WILL','AN','ABOUT',
    'MANY','THEN','SO','HER','WOULD','MAKE','HIM','INTO','HAS','TWO','MORE','NO',
    'WAY','COULD','MY','THAN','BEEN','WHO','ITS','NOW','DID','GET','COME','MADE',
    'MAY','AFTER','ALSO','MUST','SAID','FIND','YOU','WITHIN','THROUGH','SELF',
    'BEING','UNTO','HOLY','SACRED','WISDOM','TRUTH','PATH','DIVINITY','BELIEVE',
    'NOTHING','KNOW','QUESTION','COMMAND','PILGRIM','JOURNEY','END','SHALL','BEFORE',
    'UPON','ONLY','BECAUSE','MOST','SUCH','OUR','OVER','LIKE','EVERY','GREAT',
    'THINGS','SHOULD','WORLD','LIFE','GOOD','GIVE','MAN','FIRST','EVEN','NEW',
    'TAKE','VERY','LONG','OWN','OLD','THINK','TELL','HELP','ASK','HIGH','KEEP',
    'LAST','LET','MIGHT','NAME','NEVER','SAME','ANOTHER','WHILE','OFTEN',
    'NEED','UNDER','WORD','WORK','BACK','MUCH','GO','RIGHT','LOOK','SHE','HE',
    'WHERE','HERE','LOSS','DEATH','BORN','EARTH','LIGHT','DARK','SPIRIT','SOUL',
    'MIND','BODY','EYE','SEE','HEAR','SPEAK','VOICE','MASTER','STUDENT','KOAN',
    'PARABLE','INSTAR','WARNING','INSTRUCTION','WELCOME'}

def word_score(text):
    """Enhanced scoring: count matched words weighted by length."""
    score = 0
    found = set()
    for w in COMMON_WORDS:
        if len(w) >= 3 and w in text:
            score += len(w) ** 2
            found.add(w)
    return score, found

def keyword_to_idx(word):
    indices = []
    i = 0
    w = word.upper()
    while i < len(w):
        if i+2 <= len(w):
            d = w[i:i+2]
            if d == 'TH': indices.append(2); i += 2; continue
            elif d == 'EO': indices.append(12); i += 2; continue
            elif d == 'NG': indices.append(21); i += 2; continue
            elif d == 'OE': indices.append(23); i += 2; continue
            elif d == 'EA': indices.append(25); i += 2; continue
            elif d == 'IA': indices.append(26); i += 2; continue
            elif d == 'AE': indices.append(27); i += 2; continue
        ch = w[i]
        m = {'F':0,'U':1,'O':3,'R':4,'C':5,'G':6,'W':7,'H':8,'N':9,'I':10,'J':11,
             'P':13,'X':14,'S':15,'T':16,'B':17,'E':18,'M':19,'L':20,'D':22,'A':24,'Y':28}
        if ch in m:
            indices.append(m[ch])
        i += 1
    return indices

os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/..')
compute_gp_english_freq()
OUT = open('focused_attack_results.txt', 'w', encoding='utf-8')

def log(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', 'replace').decode())
    OUT.write(msg + '\n')
    OUT.flush()

# Generate primes
def sieve_primes(n):
    """Generate all primes up to n."""
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n+1, i):
                is_prime[j] = False
    return [i for i in range(2, n+1) if is_prime[i]]

PRIMES = sieve_primes(50000)

# ============================================================
# ATTACK 1: P02 Period-35 Vigenere Key Recovery
# ============================================================
log("=" * 60)
log("ATTACK 1: P02 PERIOD-35 VIGENERE KEY RECOVERY")
log("=" * 60)

p02 = load_page(2)
log(f"P02: {len(p02)} runes")

# Column IoC analysis for various periods
log("\nPeriod scan:")
for period in range(2, 70):
    cols = [[] for _ in range(period)]
    for i, v in enumerate(p02):
        cols[i % period].append(v)
    avg_ic = sum(ioc29(c) for c in cols if len(c) > 1) / max(period, 1)
    if avg_ic > 1.3:
        log(f"  Period {period}: avg col IoC = {avg_ic:.4f} (cols have {len(p02)//period}-{len(p02)//period+1} elements)")

# For the best period, try to recover key via frequency analysis
for best_period in [35, 18, 36]:
    log(f"\nKey recovery for period {best_period}:")
    cols = [[] for _ in range(best_period)]
    for i, v in enumerate(p02):
        cols[i % best_period].append(v)
    
    # For each column, find best shift via chi-squared
    key = []
    for ci, col in enumerate(cols):
        best_shift = 0
        best_chi = float('inf')
        for shift in range(29):
            shifted = [(v + shift) % 29 for v in col]
            chi = chi_squared(shifted)
            if chi < best_chi:
                best_chi = chi
                best_shift = shift
        key.append(best_shift)
    
    # Decrypt with recovered key
    dec = [(p02[i] + key[i % best_period]) % 29 for i in range(len(p02))]
    text = indices_to_latin(dec)
    ic = ioc29(dec)
    sc, words = word_score(text)
    log(f"  Key (SUB): {key}")
    log(f"  IoC={ic:.4f}, word_score={sc}, words={sorted(words)}")
    log(f"  Text: {text[:150]}")
    
    # Also try ADD mode
    dec_add = [(p02[i] - key[i % best_period]) % 29 for i in range(len(p02))]
    text_add = indices_to_latin(dec_add)
    ic_add = ioc29(dec_add)
    sc_add, words_add = word_score(text_add)
    log(f"  Key (ADD): IoC={ic_add:.4f}, word_score={sc_add}")
    log(f"  Text: {text_add[:150]}")
    
    # Hill-climbing on key
    log(f"\n  Hill-climbing refinement (period {best_period})...")
    best_key = list(key)
    best_score = max(sc, sc_add)
    best_mode = 'sub' if sc >= sc_add else 'add'
    
    for iteration in range(5000):
        trial_key = list(best_key)
        pos = random.randint(0, best_period - 1)
        trial_key[pos] = random.randint(0, 28)
        
        if best_mode == 'sub':
            dec_trial = [(p02[i] + trial_key[i % best_period]) % 29 for i in range(len(p02))]
        else:
            dec_trial = [(p02[i] - trial_key[i % best_period]) % 29 for i in range(len(p02))]
        text_trial = indices_to_latin(dec_trial)
        sc_trial, _ = word_score(text_trial)
        
        if sc_trial > best_score:
            best_score = sc_trial
            best_key = trial_key
    
    if best_mode == 'sub':
        dec_final = [(p02[i] + best_key[i % best_period]) % 29 for i in range(len(p02))]
    else:
        dec_final = [(p02[i] - best_key[i % best_period]) % 29 for i in range(len(p02))]
    text_final = indices_to_latin(dec_final)
    ic_final = ioc29(dec_final)
    sc_final, words_final = word_score(text_final)
    log(f"  After hill-climbing: IoC={ic_final:.4f}, score={sc_final}, words={sorted(words_final)}")
    log(f"  Text: {text_final[:200]}")

# ============================================================
# ATTACK 2: TOTIENT WITH P63 GRID NUMBERS AS OFFSETS
# ============================================================
log("\n\n" + "=" * 60)
log("ATTACK 2: TOTIENT CIPHER WITH P63 GRID NUMBERS AS OFFSETS")
log("=" * 60)

grid_numbers = [272, 138, 131, 151, 226, 245, 18]

# Load all unsolved pages
unsolved = {}
for pn in list(range(2, 3)) + list(range(18, 55)):
    indices = load_page(pn)
    if indices and len(indices) > 20:
        unsolved[pn] = indices

for offset in grid_numbers:
    log(f"\n  Totient offset={offset}:")
    for pn, cipher in sorted(unsolved.items()):
        for mode in ['sub', 'add', 'beaufort']:
            result = []
            ki = offset
            for c in cipher:
                p_val = PRIMES[ki] if ki < len(PRIMES) else PRIMES[ki % len(PRIMES)]
                tot = (p_val - 1) % 29
                if mode == 'sub':
                    p = (c - tot) % 29
                elif mode == 'add':
                    p = (c + tot) % 29
                else:
                    p = (tot - c) % 29
                result.append(p)
                if p != 0:  # F-skip
                    ki += 1
            
            ic = ioc29(result)
            if ic > 1.4:
                text = indices_to_latin(result)
                sc, words = word_score(text)
                if sc > 30:
                    log(f"    P{pn:02d}/{mode}: IoC={ic:.3f}, score={sc}, words={sorted(words)[:8]}")
                    log(f"      {text[:100]}")

# ============================================================
# ATTACK 3: PRIME SEQUENCE AS RUNNING KEY
# ============================================================
log("\n\n" + "=" * 60)
log("ATTACK 3: PRIME SEQUENCE AS RUNNING KEY")
log("=" * 60)

# Try different prime-based key streams
for pn, cipher in sorted(unsolved.items()):
    n = len(cipher)
    
    # Method 1: primes mod 29
    key_primes_mod29 = [PRIMES[i] % 29 for i in range(n)]
    
    # Method 2: prime gaps
    key_gaps = [PRIMES[i+1] - PRIMES[i] for i in range(n)]
    key_gaps_mod29 = [g % 29 for g in key_gaps]
    
    # Method 3: totient values (p-1) mod 29
    key_totient = [(PRIMES[i] - 1) % 29 for i in range(n)]
    
    # Method 4: cumulative prime sum mod 29
    cum_sum = 0
    key_cumsum = []
    for i in range(n):
        cum_sum += PRIMES[i]
        key_cumsum.append(cum_sum % 29)
    
    # Method 5: prime products mod 29
    prod = 1
    key_prod = []
    for i in range(n):
        prod = (prod * PRIMES[i]) % 29
        key_prod.append(prod)
    
    for key_name, key in [
        ('primes_mod29', key_primes_mod29),
        ('prime_gaps', key_gaps_mod29),
        ('totient_vals', key_totient),
        ('cumulative_sum', key_cumsum),
        ('prime_products', key_prod),
    ]:
        for mode in ['sub', 'add', 'beaufort']:
            if mode == 'sub':
                dec = [(c - k) % 29 for c, k in zip(cipher, key)]
            elif mode == 'add':
                dec = [(c + k) % 29 for c, k in zip(cipher, key)]
            else:
                dec = [(k - c) % 29 for c, k in zip(cipher, key)]
            
            ic = ioc29(dec)
            if ic > 1.4:
                text = indices_to_latin(dec)
                sc, words = word_score(text)
                if sc > 30:
                    log(f"  P{pn:02d} {key_name}/{mode}: IoC={ic:.3f}, score={sc}")
                    log(f"    {text[:100]}")
    
    # Method 6: prime-indexed starting at various offsets
    for start_offset in grid_numbers:
        key_offset = [PRIMES[i + start_offset] % 29 for i in range(n)]
        for mode in ['sub', 'add']:
            if mode == 'sub':
                dec = [(c - k) % 29 for c, k in zip(cipher, key_offset)]
            else:
                dec = [(c + k) % 29 for c, k in zip(cipher, key_offset)]
            ic = ioc29(dec)
            if ic > 1.5:
                text = indices_to_latin(dec)
                sc, words = word_score(text)
                if sc > 40:
                    log(f"  P{pn:02d} primes_offset{start_offset}/{mode}: IoC={ic:.3f}, score={sc}")
                    log(f"    {text[:100]}")

# ============================================================
# ATTACK 4: "REARRANGING THE PRIMES" - UNIQUE INTERPRETATION
# ============================================================
log("\n\n" + "=" * 60)
log("ATTACK 4: REARRANGING THE PRIMES - NOVEL APPROACHES")
log("=" * 60)

# Idea: use primes to REARRANGE (permute) the ciphertext
for pn in [20, 32, 44, 50, 40, 25]:
    cipher = unsolved.get(pn)
    if not cipher:
        continue
    n = len(cipher)
    
    # Method A: Read at prime positions first, then non-prime positions
    prime_set = set(PRIMES[:n])
    prime_positions = [i for i in range(n) if (i+1) in prime_set or i in prime_set]  # 1-indexed and 0-indexed
    non_prime_positions = [i for i in range(n) if i not in prime_positions]
    
    for order_name, order in [
        ('prime_first', prime_positions + non_prime_positions),
        ('nonprime_first', non_prime_positions + prime_positions),
    ]:
        if len(order) != n:
            continue
        reordered = [cipher[i] for i in order if i < n]
        for shift in range(29):
            dec = [(v + shift) % 29 for v in reordered]
            text = indices_to_latin(dec)
            sc, words = word_score(text)
            if sc > 50:
                log(f"  P{pn:02d} {order_name}/shift={shift}: score={sc}")
                log(f"    {text[:100]}")
    
    # Method B: Use prime-indexed runes as key for non-prime runes
    prime_vals_0 = [cipher[i] for i in range(n) if i in set(PRIMES[:n])]
    nonprime_idx = [i for i in range(n) if i not in set(PRIMES[:n])]
    
    if prime_vals_0:
        key_from_primes = prime_vals_0 * (len(nonprime_idx) // len(prime_vals_0) + 1)
        nonprime_cipher = [cipher[i] for i in nonprime_idx]
        for mode in ['sub', 'add', 'beaufort']:
            if mode == 'sub':
                dec = [(c - k) % 29 for c, k in zip(nonprime_cipher, key_from_primes)]
            elif mode == 'add':
                dec = [(c + k) % 29 for c, k in zip(nonprime_cipher, key_from_primes)]
            else:
                dec = [(k - c) % 29 for c, k in zip(nonprime_cipher, key_from_primes)]
            ic = ioc29(dec)
            if ic > 1.4:
                text = indices_to_latin(dec)
                sc, words = word_score(text)
                if sc > 30:
                    log(f"  P{pn:02d} prime_as_key/{mode}: IoC={ic:.3f}, score={sc}")
                    log(f"    {text[:100]}")

# ============================================================
# ATTACK 5: COLUMNAR TRANSPOSITION WITH PRIME COLUMN ORDER
# ============================================================
log("\n\n" + "=" * 60)
log("ATTACK 5: COLUMNAR TRANSPOSITION (PRIME-BASED COLUMN ORDERS)")
log("=" * 60)

# For each page, try columnar transposition with column order based on primes
for pn in [20, 32, 44, 50, 40, 25, 2]:
    cipher = unsolved.get(pn)
    if not cipher:
        continue
    n = len(cipher)
    
    # Try various column counts
    for num_cols in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]:
        if num_cols >= n:
            continue
        
        # Fill grid row by row
        num_rows = (n + num_cols - 1) // num_cols
        grid = []
        for r in range(num_rows):
            row = []
            for c in range(num_cols):
                idx = r * num_cols + c
                if idx < n:
                    row.append(cipher[idx])
                else:
                    row.append(None)
            grid.append(row)
        
        # Read columns in various orders
        # Order 1: Natural order (baseline)
        # Order 2: Prime-indexed columns first
        primes_in_range = [p for p in PRIMES if p < num_cols]
        non_primes = [i for i in range(num_cols) if i not in primes_in_range]
        
        for order_name, col_order in [
            ('prime_cols_first', primes_in_range + non_primes),
            ('reverse_cols', list(reversed(range(num_cols)))),
        ]:
            if len(col_order) != num_cols:
                continue
            
            reordered = []
            for col_idx in col_order:
                for row in grid:
                    if row[col_idx] is not None:
                        reordered.append(row[col_idx])
            
            for shift in range(29):
                dec = [(v + shift) % 29 for v in reordered]
                text = indices_to_latin(dec)
                sc, words = word_score(text)
                if sc > 60:
                    log(f"  P{pn:02d} cols={num_cols}/{order_name}/shift={shift}: score={sc}")
                    log(f"    {text[:100]}")

# ============================================================
# ATTACK 6: VARIANT TOTIENT - DIFFERENT SKIP VALUES
# ============================================================
log("\n\n" + "=" * 60)
log("ATTACK 6: TOTIENT CIPHER WITH DIFFERENT SKIP VALUES (0-28)")
log("=" * 60)

# The standard totient skips on F (value 0). What if a different value is skipped?
small_pages = [(len(v), pn, v) for pn, v in unsolved.items() if len(v) < 300]
small_pages.sort()

for length, pn, cipher in small_pages[:10]:
    best_result = None
    best_score = 0
    
    for skip_val in range(29):
        for offset in range(500):
            for mode in ['sub', 'add']:
                result = []
                ki = offset
                for c in cipher:
                    if ki >= len(PRIMES):
                        break
                    p_val = PRIMES[ki]
                    tot = (p_val - 1) % 29
                    if mode == 'sub':
                        p = (c - tot) % 29
                    else:
                        p = (c + tot) % 29
                    result.append(p)
                    if p != skip_val:
                        ki += 1
                
                if len(result) != len(cipher):
                    continue
                
                ic = ioc29(result)
                text = indices_to_latin(result)
                sc, words = word_score(text)
                if sc > best_score:
                    best_score = sc
                    best_result = (skip_val, offset, mode, ic, text[:80], sorted(words))
    
    if best_result and best_score > 30:
        skip_val, offset, mode, ic, preview, words = best_result
        log(f"  P{pn:02d} ({length}r): skip={skip_val}, offset={offset}, mode={mode}, IoC={ic:.3f}, score={best_score}")
        log(f"    Words: {words[:10]}")
        log(f"    {preview}")

# ============================================================
# ATTACK 7: GP PRIMES (2,3,5,7,11,13,17,19,23,29) AS KEY
# ============================================================
log("\n\n" + "=" * 60)
log("ATTACK 7: GEMATRIA PRIMUS PRIMES AS KEY")
log("=" * 60)

# The GP "primes" are: F=0,U=1,TH=2,O=3,R=4,C=5,G=6,W=7,H=8,N=9,I=10...
# But the PRIMES among the GP INDICES (0-28) are: 2,3,5,7,11,13,17,19,23
gp_prime_indices = [2, 3, 5, 7, 11, 13, 17, 19, 23]  # 9 values
gp_prime_key = gp_prime_indices  # period 9

# Also try the VALUES from P63: THE PRIMES ARE SACRED
# P63 says "SUOID CARNAL OBSCURA FORM MOBIUS ANALOGUOID MOURNFUL AETHEREAL CABAL"
# These might be KEYS for specific pages

for pn, cipher in sorted(unsolved.items()):
    for mode in ['sub', 'add', 'beaufort']:
        # Standard repeating key
        ext = gp_prime_key * (len(cipher) // len(gp_prime_key) + 1)
        if mode == 'sub':
            dec = [(c - k) % 29 for c, k in zip(cipher, ext)]
        elif mode == 'add':
            dec = [(c + k) % 29 for c, k in zip(cipher, ext)]
        else:
            dec = [(k - c) % 29 for c, k in zip(cipher, ext)]
        
        ic = ioc29(dec)
        text = indices_to_latin(dec)
        sc, words = word_score(text)
        if sc > 30:
            log(f"  P{pn:02d} gp_primes/{mode}: IoC={ic:.3f}, score={sc}")
            log(f"    {text[:100]}")
        
        # F-skip version
        dec2 = []
        ki = 0
        for c in cipher:
            k = gp_prime_key[ki % len(gp_prime_key)]
            if mode == 'sub':
                p = (c - k) % 29
            elif mode == 'add':
                p = (c + k) % 29
            else:
                p = (k - c) % 29
            dec2.append(p)
            if p != 0:
                ki += 1
        
        ic2 = ioc29(dec2)
        text2 = indices_to_latin(dec2)
        sc2, words2 = word_score(text2)
        if sc2 > 30:
            log(f"  P{pn:02d} gp_primes_fskip/{mode}: IoC={ic2:.3f}, score={sc2}")
            log(f"      {text2[:100]}")

# ============================================================
# ATTACK 8: DEOR POEM GP VALUES AS RUNNING KEY
# ============================================================
log("\n\n" + "=" * 60)
log("ATTACK 8: DEOR POEM AS GP RUNNING KEY")
log("=" * 60)

deor_path = os.path.join('LiberPrimus', 'reference', 'research', 'deor_poem.txt')
deor_text = ""
if os.path.exists(deor_path):
    with open(deor_path, 'r', encoding='utf-8') as f:
        deor_text = f.read().strip().upper()
else:
    # Try alternate paths
    for alt in ['Analysis/Reference_Docs/deor_poem.txt', 'deor_poem.txt']:
        if os.path.exists(alt):
            with open(alt, 'r', encoding='utf-8') as f:
                deor_text = f.read().strip().upper()
            break

if not deor_text:
    # Known Deor poem refrain
    deor_text = "THAES OFEREODE THISSES SWA MAEG"

# Convert to GP indices
deor_gp = []
j = 0
while j < len(deor_text):
    found = False
    if j + 2 <= len(deor_text):
        for idx, lat in enumerate(GP_LATIN):
            if len(lat) == 2 and deor_text[j:j+2] == lat:
                deor_gp.append(idx)
                j += 2
                found = True
                break
    if not found:
        ch = deor_text[j]
        for idx, lat in enumerate(GP_LATIN):
            if len(lat) == 1 and ch == lat:
                deor_gp.append(idx)
                found = True
                break
        j += 1

log(f"Deor GP key: {len(deor_gp)} values")

if deor_gp:
    for pn in [18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]:
        cipher = unsolved.get(pn)
        if not cipher:
            continue
        
        for offset in range(min(len(deor_gp) - len(cipher), 50)):
            key = deor_gp[offset:offset+len(cipher)]
            if len(key) < len(cipher):
                key = key * (len(cipher) // len(key) + 1)
            
            for mode in ['sub', 'add', 'beaufort']:
                if mode == 'sub':
                    dec = [(c - k) % 29 for c, k in zip(cipher, key)]
                elif mode == 'add':
                    dec = [(c + k) % 29 for c, k in zip(cipher, key)]
                else:
                    dec = [(k - c) % 29 for c, k in zip(cipher, key)]
                
                ic = ioc29(dec)
                text = indices_to_latin(dec)
                sc, words = word_score(text)
                if sc > 40:
                    log(f"  P{pn:02d} deor_offset={offset}/{mode}: IoC={ic:.3f}, score={sc}")
                    log(f"    {text[:100]}")

log("\n\n=== FOCUSED ATTACK COMPLETE ===")
OUT.close()
