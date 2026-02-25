"""
Targeted attacks based on fundamental analysis findings:
1. Cumulative-rune-offset totient stream (specific page offsets based on all-page rune counts)
2. Column-by-column Vigenère crack on small pages with Friedman signals
3. Outguess data as key material (if available)
4. Bit-level XOR attacks (5-bit representation)
5. Running key from solved page plaintexts
6. Test mirror page P06↔P64 known-plaintext key recovery
"""

import os, sys, math
from collections import Counter

GP_RUNE_TO_INDEX = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C4':11,'\u16C7':12,'\u16C8':13,'\u16C9':14,
    '\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,'\u16D7':19,'\u16DA':20,'\u16DD':21,
    '\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,'\u16A3':26,'\u16E1':27,'\u16E0':28
}

LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

# English GP frequency (approximate from solved pages)
# From LP solved: E, TH, A, O, N, I, S, R are most common
ENGLISH_GP_FREQ = {
    0: 0.020,  # F
    1: 0.025,  # U
    2: 0.065,  # TH
    3: 0.065,  # O
    4: 0.055,  # R
    5: 0.030,  # C
    6: 0.018,  # G
    7: 0.025,  # W
    8: 0.050,  # H
    9: 0.060,  # N
    10: 0.063, # I
    11: 0.003, # J
    12: 0.008, # EO
    13: 0.018, # P
    14: 0.003, # X
    15: 0.055, # S
    16: 0.065, # T
    17: 0.020, # B
    18: 0.105, # E
    19: 0.022, # M
    20: 0.035, # L
    21: 0.025, # NG
    22: 0.010, # OE
    23: 0.035, # D
    24: 0.070, # A
    25: 0.008, # AE
    26: 0.018, # Y
    27: 0.008, # IA
    28: 0.015, # EA
}

def load_page(page_num):
    paths = [
        f"LiberPrimus/pages/page_{page_num:02d}/runes.txt",
        f"LiberPrimus/pages/page_{page_num}/runes.txt",
    ]
    for p in paths:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                text = f.read()
            return [GP_RUNE_TO_INDEX[c] for c in text if c in GP_RUNE_TO_INDEX]
    return None

def ioc(data):
    if len(data) <= 1:
        return 0
    freq = Counter(data)
    n = len(data)
    return sum(f*(f-1) for f in freq.values()) / (n*(n-1)) * 29

def to_text(indices):
    return ''.join(LATIN[i] for i in indices)

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i+2) == 0: return False
        i += 6
    return True

def generate_primes(count):
    primes = []
    n = 2
    while len(primes) < count:
        if is_prime(n):
            primes.append(n)
        n += 1
    return primes

def score_english(text):
    """Score using common English words and bigrams."""
    text = text.upper()
    words_3 = ['THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','HER','WAS','ONE','OUR','OUT','HAS','HIS','HOW','ITS','MAY','NEW','NOW','OLD','SEE','WAY','WHO','DID','GET','HAS','HIM','LET','SAY','SHE','TOO','USE']
    words_4 = ['THAT','WITH','HAVE','THIS','WILL','YOUR','FROM','THEY','BEEN','CALL','EACH','MAKE','LIKE','LONG','LOOK','MANY','MOST','OVER','SUCH','TAKE','THAN','THEM','THEN','SOME','TIME','VERY','WHEN','COME','KNOW','FIND','SEEK','PATH','SELF','THEM','WHAT']
    
    score = 0
    for w in words_3:
        score += text.count(w) * 3
    for w in words_4:
        score += text.count(w) * 5
    
    # Common bigrams
    for bg in ['TH','HE','IN','ER','AN','RE','ON','AT','EN','ND','TI','ES','OR','TE','OF','ED','IS','IT','AL','AR','ST','TO','NT','NG']:
        score += text.count(bg)
    
    return score

def chi_squared_vs_english(data):
    """Chi-squared test against expected English GP distribution."""
    freq = Counter(data)
    n = len(data)
    chi = 0
    for i in range(29):
        observed = freq.get(i, 0)
        expected = n * ENGLISH_GP_FREQ.get(i, 1/29)
        if expected > 0:
            chi += (observed - expected)**2 / expected
    return chi

# ============================================================================
def main():
    print("=" * 80)
    print("TARGETED ATTACKS BASED ON FUNDAMENTAL ANALYSIS")
    print("=" * 80)
    
    # Generate first 20000 primes for totient stream
    primes = generate_primes(20000)
    totient_stream = [(p - 1) % 29 for p in primes]
    
    # Load all pages to compute cumulative offsets
    all_pages = {}
    for pg in range(0, 75):
        data = load_page(pg)
        if data:
            all_pages[pg] = data
    
    unsolved = list(range(18, 55))
    
    # ======================================================================
    # ATTACK 1: CUMULATIVE RUNE OFFSET TOTIENT STREAM
    # ======================================================================
    print("\n" + "=" * 80)
    print("ATTACK 1: CUMULATIVE-RUNE-OFFSET TOTIENT")
    print("Offset = total runes in ALL pages before this page")
    print("=" * 80)
    
    # Compute cumulative rune count through ALL pages
    page_order = sorted(all_pages.keys())
    cumulative = {}
    cum = 0
    for pg in page_order:
        cumulative[pg] = cum
        cum += len(all_pages[pg])
    
    print(f"Page cumulative offsets:")
    for pg in unsolved:
        if pg in cumulative:
            print(f"  P{pg}: offset {cumulative[pg]}")
    
    # Test totient with cumulative offset ± small range
    hits = []
    for pg in unsolved:
        if pg not in all_pages:
            continue
        cipher = all_pages[pg]
        base_offset = cumulative.get(pg, 0)
        
        # Try offsets around the cumulative value ± 50
        for delta in range(-50, 51):
            offset = base_offset + delta
            if offset < 0 or offset + len(cipher) > len(totient_stream):
                continue
            
            # SUB mode (P55 method)
            plain = [(cipher[i] - totient_stream[offset + i]) % 29 for i in range(len(cipher))]
            ic = ioc(plain)
            if ic > 1.4:
                text = to_text(plain)
                sc = score_english(text)
                hits.append((pg, offset, delta, 'SUB', ic, sc, text[:80]))
            
            # ADD mode
            plain2 = [(cipher[i] + totient_stream[offset + i]) % 29 for i in range(len(cipher))]
            ic2 = ioc(plain2)
            if ic2 > 1.4:
                text2 = to_text(plain2)
                sc2 = score_english(text2)
                hits.append((pg, offset, delta, 'ADD', ic2, sc2, text2[:80]))
            
            # BEAUFORT mode
            plain3 = [(totient_stream[offset + i] - cipher[i]) % 29 for i in range(len(cipher))]
            ic3 = ioc(plain3)
            if ic3 > 1.4:
                text3 = to_text(plain3)
                sc3 = score_english(text3)
                hits.append((pg, offset, delta, 'BEAU', ic3, sc3, text3[:80]))
    
    if hits:
        hits.sort(key=lambda x: -x[4])
        print(f"\n  HITS (IoC > 1.4):")
        for pg, off, delta, mode, ic, sc, text in hits[:30]:
            print(f"    P{pg} offset={off} (base+{delta}) {mode}: IoC={ic:.4f} score={sc} | {text}")
    else:
        print(f"\n  No cumulative-offset totient hits")
    
    # Also test with F-skip
    print("\n  --- With F-skip ---")
    f_hits = []
    for pg in unsolved:
        if pg not in all_pages:
            continue
        cipher = all_pages[pg]
        base_offset = cumulative.get(pg, 0)
        
        for delta in range(-50, 51):
            offset = base_offset + delta
            if offset < 0 or offset + len(cipher) * 2 > len(totient_stream):
                continue
            
            plain = []
            key_idx = offset
            for c in cipher:
                if c == 0:  # F rune
                    plain.append(0)
                    # Don't advance key_idx
                else:
                    k = totient_stream[key_idx]
                    plain.append((c - k) % 29)
                    key_idx += 1
            
            ic = ioc(plain)
            if ic > 1.4:
                text = to_text(plain)
                sc = score_english(text)
                f_hits.append((pg, offset, delta, ic, sc, text[:80]))
    
    if f_hits:
        f_hits.sort(key=lambda x: -x[3])
        print(f"  F-skip HITS:")
        for pg, off, delta, ic, sc, text in f_hits[:20]:
            print(f"    P{pg} offset={off} (base+{delta}): IoC={ic:.4f} score={sc} | {text}")
    else:
        print(f"  No F-skip hits")
    
    # Also try: offset = cumulative count of NON-F runes (i.e., F-skip adjusted)
    print("\n  --- F-skip adjusted cumulative offset ---")
    # Count non-F runes cumulatively
    cum_nf = {}
    nf_count = 0
    for pg in page_order:
        cum_nf[pg] = nf_count
        nf_count += sum(1 for r in all_pages[pg] if r != 0)
    
    nf_hits = []
    for pg in unsolved:
        if pg not in all_pages:
            continue
        cipher = all_pages[pg]
        base_nf = cum_nf.get(pg, 0)
        
        for delta in range(-50, 51):
            offset = base_nf + delta
            if offset < 0 or offset + len(cipher) * 2 > len(totient_stream):
                continue
            
            # F-skip with non-F cumulative offset
            plain = []
            key_idx = offset
            for c in cipher:
                if c == 0:
                    plain.append(0)
                else:
                    if key_idx < len(totient_stream):
                        k = totient_stream[key_idx]
                        plain.append((c - k) % 29)
                        key_idx += 1
                    else:
                        plain.append(c)
            
            ic = ioc(plain)
            if ic > 1.4:
                text = to_text(plain)
                sc = score_english(text)
                nf_hits.append((pg, offset, delta, ic, sc, text[:80]))
    
    if nf_hits:
        nf_hits.sort(key=lambda x: -x[3])
        print(f"  Non-F cumulative HITS:")
        for pg, off, delta, ic, sc, text in nf_hits[:20]:
            print(f"    P{pg} offset={off} (base+{delta}): IoC={ic:.4f} score={sc} | {text}")
    else:
        print(f"  No non-F cumulative hits")

    tested_1 = len(unsolved) * 101 * 3  # pages * offsets * modes
    print(f"\n  Tested: {tested_1} cumulative-offset configurations")
    
    # ======================================================================
    # ATTACK 2: COLUMN-BY-COLUMN VIGENÈRE CRACK ON SMALL PAGES
    # ======================================================================
    print("\n" + "=" * 80)
    print("ATTACK 2: COLUMN-BY-COLUMN VIGENÈRE CRACKING")
    print("Testing pages with Friedman signals")
    print("=" * 80)
    
    targets = [
        (54, [13, 17, 19, 23, 24, 25, 9]),  # P54: strong period signals
        (49, [21, 15, 13, 11, 3, 7]),        # P49: strong autocorrelation at 21
        (22, [11, 13, 5, 7, 9]),             # P22: small page
    ]
    
    vig_hits = []
    for pg, periods in targets:
        cipher = load_page(pg)
        if not cipher:
            continue
        
        print(f"\n  P{pg} ({len(cipher)} runes):")
        
        for period in periods:
            # Split into columns
            columns = [[] for _ in range(period)]
            for i, c in enumerate(cipher):
                columns[i % period].append(c)
            
            # For each column, try all 29 shifts (SUB, ADD, BEAUFORT)
            for mode in ['SUB', 'ADD', 'BEAU']:
                best_key = []
                for col_idx in range(period):
                    col = columns[col_idx]
                    best_shift = 0
                    best_chi = float('inf')
                    
                    for shift in range(29):
                        if mode == 'SUB':
                            decrypted = [(c - shift) % 29 for c in col]
                        elif mode == 'ADD':
                            decrypted = [(c + shift) % 29 for c in col]
                        else:
                            decrypted = [(shift - c) % 29 for c in col]
                        
                        # Chi-squared against English
                        chi = chi_squared_vs_english(decrypted)
                        if chi < best_chi:
                            best_chi = chi
                            best_shift = shift
                    
                    best_key.append(best_shift)
                
                # Apply best key
                plain = []
                for i, c in enumerate(cipher):
                    s = best_key[i % period]
                    if mode == 'SUB':
                        plain.append((c - s) % 29)
                    elif mode == 'ADD':
                        plain.append((c + s) % 29)
                    else:
                        plain.append((s - c) % 29)
                
                ic = ioc(plain)
                text = to_text(plain)
                sc = score_english(text)
                
                key_text = [LATIN[k] for k in best_key]
                
                if ic > 1.3 or sc > 20:
                    vig_hits.append((pg, period, mode, ic, sc, text[:100], key_text))
                    print(f"    Period {period} {mode}: IoC={ic:.4f} score={sc}")
                    print(f"      Key: {key_text}")
                    print(f"      Text: {text[:100]}")
    
    if not vig_hits:
        print("\n  No column-by-column hits above threshold")
    
    # ======================================================================
    # ATTACK 3: RUNNING KEY FROM SOLVED PAGE PLAINTEXTS
    # ======================================================================
    print("\n" + "=" * 80)
    print("ATTACK 3: RUNNING KEY FROM SOLVED PLAINTEXTS")
    print("=" * 80)
    
    # Build running key from solved pages (direct gematria = Caesar 0)
    # Pages 5, 63: "THE PRIMES ARE SACRED..."
    # Pages 64, 68: solved with known Caesar shifts
    running_keys = {}
    
    # Caesar 0 pages (direct): compute plaintexts
    for pg in [5, 63]:
        data = load_page(pg)
        if data:
            running_keys[f'P{pg}_direct'] = data
    
    # Caesar 2 page 64
    data64 = load_page(64)
    if data64:
        running_keys['P64_caesar2'] = [(d - 2) % 29 for d in data64]
    
    # Page 68: Caesar 0
    data68 = load_page(68)
    if data68:
        running_keys['P68_direct'] = data68
    
    # Concatenate all solved plaintexts
    all_plain = []
    for pg in [5, 63, 68]:
        data = load_page(pg)
        if data:
            all_plain.extend(data)
    if data64:
        all_plain.extend([(d - 2) % 29 for d in data64])
    
    running_keys['all_solved'] = all_plain
    
    # Also add page 74
    data74 = load_page(74)
    if data74:
        running_keys['P74_direct'] = data74
    
    rk_hits = []
    for key_name, key_data in running_keys.items():
        if len(key_data) < 50:
            continue
            
        for pg in unsolved:
            cipher = all_pages.get(pg)
            if not cipher:
                continue
            
            max_start = min(len(key_data) - len(cipher), 500)
            if max_start < 0:
                max_start = 0
            
            for start in range(0, max_start + 1, 1):
                if start + len(cipher) > len(key_data):
                    break
                
                for mode in ['SUB', 'ADD', 'BEAU']:
                    plain = []
                    for i in range(len(cipher)):
                        k = key_data[start + i]
                        if mode == 'SUB':
                            plain.append((cipher[i] - k) % 29)
                        elif mode == 'ADD':
                            plain.append((cipher[i] + k) % 29)
                        else:
                            plain.append((k - cipher[i]) % 29)
                    
                    ic = ioc(plain)
                    if ic > 1.4:
                        text = to_text(plain)
                        sc = score_english(text)
                        rk_hits.append((pg, key_name, start, mode, ic, sc, text[:80]))
    
    if rk_hits:
        rk_hits.sort(key=lambda x: -x[4])
        print(f"  Running key HITS:")
        for pg, kn, st, mode, ic, sc, text in rk_hits[:20]:
            print(f"    P{pg} key={kn} start={st} {mode}: IoC={ic:.4f} score={sc} | {text}")
    else:
        print(f"  No running key hits")
    
    tested_3 = sum(1 for _ in rk_hits) if rk_hits else 0  # approximate
    
    # ======================================================================
    # ATTACK 4: BIT-LEVEL XOR
    # ======================================================================
    print("\n" + "=" * 80)
    print("ATTACK 4: 5-BIT XOR WITH TOTIENT STREAM")
    print("Each rune as 5-bit value, XOR with totient bits")
    print("=" * 80)
    
    # Convert totient stream to bits
    tot_bits = []
    for t in totient_stream[:10000]:
        for b in range(5):
            tot_bits.append((t >> b) & 1)
    
    bit_hits = []
    for pg in unsolved:
        cipher = all_pages.get(pg)
        if not cipher:
            continue
        
        base_offset = cumulative.get(pg, 0)
        
        for bit_offset in range(0, min(5000, len(tot_bits) - len(cipher)*5), 5):
            # XOR cipher bits with totient bits
            plain = []
            valid = True
            for i, c in enumerate(cipher):
                c_bits = [(c >> b) & 1 for b in range(5)]
                p_val = 0
                for b in range(5):
                    idx = bit_offset + i * 5 + b
                    if idx >= len(tot_bits):
                        valid = False
                        break
                    p_bit = c_bits[b] ^ tot_bits[idx]
                    p_val |= (p_bit << b)
                
                if not valid:
                    break
                
                if p_val >= 29:
                    valid = False
                    break
                
                plain.append(p_val)
            
            if not valid or len(plain) != len(cipher):
                continue
            
            ic = ioc(plain)
            if ic > 1.4:
                text = to_text(plain)
                sc = score_english(text)
                bit_hits.append((pg, bit_offset, ic, sc, text[:80]))
    
    if bit_hits:
        bit_hits.sort(key=lambda x: -x[2])
        print(f"  Bit-level XOR HITS:")
        for pg, off, ic, sc, text in bit_hits[:20]:
            print(f"    P{pg} bit_offset={off}: IoC={ic:.4f} score={sc} | {text}")
    else:
        print(f"  No bit-level XOR hits (most fail due to values >= 29)")
    
    # ======================================================================
    # ATTACK 5: MIRROR-PAGE KEY RECOVERY 
    # ======================================================================
    print("\n" + "=" * 80)
    print("ATTACK 5: MIRROR PAGE KEY RECOVERY")
    print("If P06↔P64 share same encryption, recover key stream")
    print("=" * 80)
    
    # P06 and P64 are confirmed mirrors
    p06 = load_page(6)
    p64 = load_page(64)
    
    if p06 and p64:
        print(f"P06: {len(p06)} runes, P64: {len(p64)} runes")
        
        # P64 solution: Caesar 2 SUB_REV → plaintext = (cipher - 2) % 29
        p64_plain = [(c - 2) % 29 for c in p64]
        
        min_len = min(len(p06), len(p64))
        
        # If P06 and P64 use same key: 
        # p06_cipher = (p06_plain + key) % 29
        # p64_cipher = (p64_plain + key) % 29
        # Then: p06_cipher - p64_cipher = p06_plain - p64_plain
        
        # First check: are they related by constant shift?
        diffs = [(p06[i] - p64[i]) % 29 for i in range(min_len)]
        diff_ioc = ioc(diffs)
        diff_counts = Counter(diffs)
        
        print(f"P06 - P64 difference: IoC={diff_ioc:.4f}")
        print(f"  Most common diffs: {diff_counts.most_common(5)}")
        
        # If same key stream: key = cipher - plaintext
        # For P64: key[i] = (p64_cipher[i] - p64_plain[i]) % 29 = 2 for all i (since Caesar 2)
        # Apply this recovered key to P06:
        # p06_plain = (p06_cipher - key) % 29 = (p06_cipher - 2) % 29
        p06_as_caesar2 = [(c - 2) % 29 for c in p06]
        ic_06 = ioc(p06_as_caesar2)
        text_06 = to_text(p06_as_caesar2[:100])
        print(f"\nP06 as Caesar 2: IoC={ic_06:.4f}")
        print(f"  Text: {text_06}")
        
        # Try all Caesar shifts on P06
        print(f"\nP06 all Caesar shifts:")
        for shift in range(29):
            plain = [(c - shift) % 29 for c in p06]
            ic = ioc(plain)
            sc = score_english(to_text(plain))
            if ic > 1.3 or sc > 30:
                print(f"  Shift {shift:2d}: IoC={ic:.4f} score={sc} | {to_text(plain[:60])}")
    
    # Also check: P01↔P59, P03↔P61, P05↔P63, P09↔P67
    print("\n  --- Mirror pair analysis ---")
    mirror_pairs = [(1, 59), (3, 61), (5, 63), (6, 64), (9, 67)]
    for p1, p2 in mirror_pairs:
        d1 = load_page(p1)
        d2 = load_page(p2)
        if d1 and d2:
            min_l = min(len(d1), len(d2))
            diffs = [(d1[i] - d2[i]) % 29 for i in range(min_l)]
            dc = Counter(diffs)
            di = ioc(diffs)
            unique = len(dc)
            
            if unique == 1:
                const = list(dc.keys())[0]
                print(f"  P{p1:2d}↔P{p2:2d}: CONSTANT DIFF = {const} (over {min_l} runes)")
            else:
                print(f"  P{p1:2d}↔P{p2:2d}: {unique} unique diffs, diff IoC={di:.4f}, top: {dc.most_common(3)}")

    # ======================================================================
    # ATTACK 6: DEEP TOTIENT WITH VERY LARGE OFFSETS
    # ======================================================================
    print("\n" + "=" * 80)
    print("ATTACK 6: DEEP TOTIENT OFFSETS (0-20000)")  
    print("testing large offsets on select pages")
    print("=" * 80)
    
    test_pages = [18, 21, 22, 49, 54]
    deep_hits = []
    
    for pg in test_pages:
        cipher = all_pages.get(pg)
        if not cipher:
            continue
        
        for offset in range(0, min(len(totient_stream) - len(cipher), 18000)):
            for mode in ['SUB', 'BEAU']:
                plain = []
                for i in range(len(cipher)):
                    k = totient_stream[offset + i]
                    if mode == 'SUB':
                        plain.append((cipher[i] - k) % 29)
                    else:
                        plain.append((k - cipher[i]) % 29)
                
                ic = ioc(plain)
                if ic > 1.5:
                    text = to_text(plain)
                    sc = score_english(text)
                    deep_hits.append((pg, offset, mode, ic, sc, text[:80]))
        
        print(f"  P{pg}: scanned offsets 0-18000")
    
    if deep_hits:
        deep_hits.sort(key=lambda x: -x[3])
        print(f"\n  Deep totient HITS (IoC > 1.5):")
        for pg, off, mode, ic, sc, text in deep_hits[:30]:
            print(f"    P{pg} offset={off} {mode}: IoC={ic:.4f} score={sc} | {text}")
    else:
        print(f"\n  No deep totient hits")


    # ======================================================================
    print("\n" + "=" * 80)
    print("ATTACK 7: AUTOKEY WITH TOTIENT SEED")
    print("Autokey where first key element is from totient, rest from plaintext")
    print("=" * 80)
    
    auto_hits = []
    for pg in unsolved:
        cipher = all_pages.get(pg)
        if not cipher or len(cipher) < 30:
            continue
        
        for seed_offset in range(0, 500):
            for seed_len in [1, 2, 3, 5, 7]:
                if seed_offset + seed_len > len(totient_stream):
                    break
                
                seed = totient_stream[seed_offset:seed_offset+seed_len]
                
                # Autokey decryption: p[i] = (c[i] - key[i]) % 29
                # where key[i] = seed[i] for i < seed_len, else p[i-seed_len]
                plain = []
                for i in range(len(cipher)):
                    if i < seed_len:
                        k = seed[i]
                    else:
                        k = plain[i - seed_len]
                    plain.append((cipher[i] - k) % 29)
                
                ic = ioc(plain)
                if ic > 1.5:
                    text = to_text(plain)
                    sc = score_english(text)
                    auto_hits.append((pg, seed_offset, seed_len, ic, sc, text[:80]))
        
        if pg in [18, 21, 49, 54]:
            print(f"  P{pg}: tested 500 seeds × 5 lengths")
    
    if auto_hits:
        auto_hits.sort(key=lambda x: -x[3])
        print(f"\n  Autokey+totient HITS:")
        for pg, so, sl, ic, sc, text in auto_hits[:20]:
            print(f"    P{pg} seed_off={so} seed_len={sl}: IoC={ic:.4f} score={sc} | {text}")
    else:
        print(f"\n  No autokey+totient hits")

    # ======================================================================
    print("\n" + "=" * 80)
    print("COMPREHENSIVE SUMMARY")
    print("=" * 80)
    
    total_all = (
        len(unsolved) * 101 * 5 +  # Attack 1 (3 modes + f-skip + nf)
        len(targets) * sum(len(p) for _, p in targets) * 3 +  # Attack 2
        0 +  # Attack 3 (variable)
        0 +  # Attack 4 (variable)
        29 +  # Attack 5 (mirror)
        len(test_pages) * 18000 * 2 +  # Attack 6
        len(unsolved) * 500 * 5  # Attack 7
    )
    
    print(f"\nTotal configurations tested: ~{total_all}")
    print(f"Attack 1 (cumulative totient): {'HITS' if hits or f_hits or nf_hits else 'No hits'}")
    print(f"Attack 2 (column-by-column): {'HITS' if vig_hits else 'No hits'}")
    print(f"Attack 3 (running key): {'HITS' if rk_hits else 'No hits'}")
    print(f"Attack 4 (bit XOR): {'HITS' if bit_hits else 'No hits'}")
    print(f"Attack 5 (mirror pages): see above")
    print(f"Attack 6 (deep totient 0-18K): {'HITS' if deep_hits else 'No hits'}")
    print(f"Attack 7 (autokey+totient): {'HITS' if auto_hits else 'No hits'}")

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()
