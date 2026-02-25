#!/usr/bin/env python3
"""
Skip-Variant Stream + PGP Key Material + Cross-Page Attack
============================================================
P55 uses: (cipher[i] - totient(prime[key_idx])) % 29 with F-skip (val=0).
What if other pages use:
1. Different skip values (1-28 instead of 0)
2. Skip on ciphertext value instead of plaintext
3. PGP public key bytes as key stream
4. Cross-page cipher interactions
5. Deor poem with skip mechanisms
6. Composite number totients (not just primes)
7. Different number-theoretic functions with skip
"""

import os, sys, base64
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
             'PATH','KNOW','SELF','BEING','MIND','SOUL','LIGHT']
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

# Generate prime table
def gen_primes(limit):
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, limit+1, i):
                sieve[j] = False
    return [i for i in range(2, limit+1) if sieve[i]]

PRIMES = gen_primes(20000)
TOTIENTS_OF_PRIMES = [euler_totient(p) for p in PRIMES]

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    repo_dir = os.path.dirname(base_dir)
    pages_dir = os.path.join(repo_dir, 'LiberPrimus', 'pages')
    
    pages = {}
    for p in range(0, 75):
        rt = load_page(pages_dir, p)
        if rt:
            shifts = parse_shifts(rt)
            if len(shifts) > 10:
                pages[p] = shifts
    
    unsolved = {p: s for p, s in pages.items() if 18 <= p <= 54}
    print(f"Loaded {len(pages)} total pages, {len(unsolved)} unsolved (18-54)")
    
    target_pages = sorted(unsolved.keys(), key=lambda p: len(unsolved[p]), reverse=True)[:8]
    
    IOC_THRESHOLD = 1.45
    SCORE_THRESHOLD = 2000
    all_results = []
    
    # =====================================================================
    print("\n" + "=" * 80)
    print("ATTACK 1: VARIABLE SKIP-VALUE TOTIENT STREAM")
    print("P55 mechanism but with skip on plaintext values 0-28")
    print("=" * 80)
    
    skip_hits = 0
    total_skip = 0
    
    for page_num in target_pages:
        cipher = unsolved[page_num]
        n = len(cipher)
        
        for skip_val in range(29):
            for offset in range(0, 100, 2):
                for mode in ['sub', 'beau']:
                    total_skip += 1
                    
                    plain = []
                    key_idx = offset
                    for i in range(n):
                        if key_idx >= len(TOTIENTS_OF_PRIMES):
                            break
                        k = TOTIENTS_OF_PRIMES[key_idx] % 29
                        
                        if mode == 'sub':
                            p_val = (cipher[i] - k) % 29
                        else:
                            p_val = (k - cipher[i]) % 29
                        
                        plain.append(p_val)
                        
                        # Skip: don't advance key if plaintext == skip_val
                        if p_val != skip_val:
                            key_idx += 1
                    
                    if len(plain) < 20:
                        continue
                    
                    ioc = calc_ioc(plain)
                    if ioc > IOC_THRESHOLD:
                        text = decode(plain)
                        sc = score_text(text)
                        skip_hits += 1
                        if sc > SCORE_THRESHOLD:
                            print(f"  P{page_num} skip={skip_val} offset={offset} mode={mode}: IoC={ioc:.3f} score={sc}")
                            print(f"    {text[:80]}")
                            all_results.append(('SKIP_TOTIENT', page_num, f'skip={skip_val}', offset, ioc, sc, text[:120]))
    
    if skip_hits == 0:
        print("  No variable-skip totient hits above threshold")
    print(f"  Total skip hits found: {skip_hits}")
    print(f"  Tested {total_skip} variable-skip configurations")
    
    # =====================================================================
    print("\n" + "=" * 80)
    print("ATTACK 2: CIPHERTEXT-DEPENDENT KEY ADVANCEMENT")
    print("Key advances by f(cipher[i]) instead of +1")
    print("=" * 80)
    
    cdep_hits = 0
    total_cdep = 0
    
    GP_PRIMES_29 = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
    
    for page_num in target_pages[:5]:
        cipher = unsolved[page_num]
        n = len(cipher)
        
        for advance_mode in ['cipher_val', 'cipher_plus1', 'cipher_prime', 'cipher_tot']:
            for offset in range(0, 50, 2):
                total_cdep += 1
                
                plain = []
                key_idx = offset
                for i in range(n):
                    if key_idx >= len(TOTIENTS_OF_PRIMES):
                        break
                    k = TOTIENTS_OF_PRIMES[key_idx] % 29
                    p_val = (cipher[i] - k) % 29
                    plain.append(p_val)
                    
                    # Advance key by function of ciphertext
                    if advance_mode == 'cipher_val':
                        key_idx += cipher[i] + 1  # advance by cipher value
                    elif advance_mode == 'cipher_plus1':
                        key_idx += cipher[i]  # advance by cipher value (0 = no advance = skip)
                    elif advance_mode == 'cipher_prime':
                        key_idx += GP_PRIMES_29[cipher[i]] % 7 + 1  # advance by prime%7+1
                    elif advance_mode == 'cipher_tot':
                        key_idx += euler_totient(cipher[i] + 2) % 5 + 1  # advance by totient
                
                if len(plain) < 20:
                    continue
                ioc = calc_ioc(plain)
                if ioc > IOC_THRESHOLD:
                    text = decode(plain)
                    sc = score_text(text)
                    cdep_hits += 1
                    if sc > SCORE_THRESHOLD:
                        print(f"  P{page_num} adv={advance_mode} offset={offset}: IoC={ioc:.3f} score={sc}")
                        print(f"    {text[:80]}")
                        all_results.append(('CDEP_ADV', page_num, advance_mode, offset, ioc, sc, text[:120]))
    
    if cdep_hits == 0:
        print("  No ciphertext-dependent advancement hits")
    print(f"  Tested {total_cdep} configurations")
    
    # =====================================================================
    print("\n" + "=" * 80)
    print("ATTACK 3: PGP PUBLIC KEY AS KEY MATERIAL")
    print("Extract raw bytes from PGP key, convert to mod-29 key stream")
    print("=" * 80)
    
    # Load and decode PGP key
    pgp_path = os.path.join(repo_dir, 'Assets', '6D854CD7933322A601C3286D181F01E57A35090F.asc')
    pgp_bytes = b''
    try:
        with open(pgp_path, 'r') as f:
            lines = f.readlines()
        # Extract base64 data between headers
        b64_data = ''
        in_block = False
        for line in lines:
            line = line.strip()
            if line.startswith('-----BEGIN'):
                in_block = True
                continue
            if line.startswith('-----END'):
                in_block = False
                continue
            if line.startswith('Comment:') or line.startswith('='):
                continue
            if in_block and line:
                b64_data += line
        pgp_bytes = base64.b64decode(b64_data)
        print(f"  PGP key: {len(pgp_bytes)} raw bytes extracted")
    except Exception as e:
        print(f"  Error loading PGP key: {e}")
    
    pgp_hits = 0
    total_pgp = 0
    
    if pgp_bytes:
        # Multiple representations
        pgp_streams = {}
        pgp_streams['raw_mod29'] = [b % 29 for b in pgp_bytes]
        pgp_streams['nibble_high'] = [(b >> 4) % 29 for b in pgp_bytes]
        pgp_streams['nibble_low'] = [(b & 0x0F) % 29 for b in pgp_bytes]
        pgp_streams['byte_pairs'] = [((pgp_bytes[i] << 8 | pgp_bytes[i+1]) % 29) for i in range(0, len(pgp_bytes)-1, 2)]
        pgp_streams['xor_adjacent'] = [(pgp_bytes[i] ^ pgp_bytes[i+1]) % 29 for i in range(len(pgp_bytes)-1)]
        pgp_streams['sum_adjacent'] = [(pgp_bytes[i] + pgp_bytes[i+1]) % 29 for i in range(len(pgp_bytes)-1)]
        
        # Also use the PGP key fingerprint
        fp = '6D854CD7933322A601C3286D181F01E57A35090F'
        fp_bytes = bytes.fromhex(fp)
        pgp_streams['fingerprint'] = [b % 29 for b in fp_bytes]
        
        for stream_name, stream in pgp_streams.items():
            for page_num in target_pages:
                cipher = unsolved[page_num]
                n = len(cipher)
                
                for offset in range(0, min(100, len(stream) - n), 10):
                    if offset + n > len(stream):
                        break
                    total_pgp += 1
                    
                    key = stream[offset:offset+n]
                    for mode_name, mode_fn in [('sub', lambda c, k: (c-k)%29), ('beau', lambda c, k: (k-c)%29)]:
                        plain = [mode_fn(cipher[i], key[i]) for i in range(n)]
                        ioc = calc_ioc(plain)
                        
                        if ioc > IOC_THRESHOLD:
                            text = decode(plain)
                            sc = score_text(text)
                            pgp_hits += 1
                            if sc > SCORE_THRESHOLD:
                                print(f"  P{page_num} stream={stream_name} offset={offset} mode={mode_name}: IoC={ioc:.3f} score={sc}")
                                print(f"    {text[:80]}")
                                all_results.append(('PGP_KEY', page_num, stream_name, offset, ioc, sc, text[:120]))
    
    if pgp_hits == 0:
        print("  No PGP key material hits")
    print(f"  Tested {total_pgp} PGP key configurations")
    
    # =====================================================================
    print("\n" + "=" * 80)
    print("ATTACK 4: CROSS-PAGE KEY DERIVATION")
    print("Page N's ciphertext/solved-text as key for page M")
    print("=" * 80)
    
    cross_hits = 0
    total_cross = 0
    
    # Use solved page ciphertexts as running keys  
    # P55-73 are solved or partially solved; also try adjacent page ciphertext
    for key_page_num in sorted(pages.keys()):
        key_stream = pages[key_page_num]
        if len(key_stream) < 50:
            continue
        
        for page_num in target_pages[:5]:
            if page_num == key_page_num:
                continue
            cipher = unsolved[page_num]
            n = len(cipher)
            
            if len(key_stream) < n:
                continue
            
            total_cross += 1
            
            for mode_name, mode_fn in [('sub', lambda c, k: (c-k)%29), ('beau', lambda c, k: (k-c)%29), ('add', lambda c, k: (c+k)%29)]:
                plain = [mode_fn(cipher[i], key_stream[i]) for i in range(n)]
                ioc = calc_ioc(plain)
                
                if ioc > IOC_THRESHOLD:
                    text = decode(plain)
                    sc = score_text(text)
                    cross_hits += 1
                    if sc > SCORE_THRESHOLD:
                        print(f"  P{page_num} key=P{key_page_num} mode={mode_name}: IoC={ioc:.3f} score={sc}")
                        print(f"    {text[:80]}")
                        all_results.append(('CROSS_PAGE', page_num, f'P{key_page_num}', 0, ioc, sc, text[:120]))
    
    if cross_hits == 0:
        print("  No cross-page hits")
    print(f"  Tested {total_cross} cross-page configurations")
    
    # =====================================================================
    print("\n" + "=" * 80)
    print("ATTACK 5: TOTIENT OF CONSECUTIVE INTEGERS (not just primes)")
    print("key[i] = totient(n+i) for various starting n, with skip mechanism")
    print("=" * 80)
    
    # Pre-compute totient sequence for consecutive integers 1..5000
    max_n = 5000
    tot_seq = [euler_totient(n) % 29 for n in range(1, max_n + 1)]
    
    consec_hits = 0
    total_consec = 0
    
    for page_num in target_pages[:5]:
        cipher = unsolved[page_num]
        n = len(cipher)
        
        for start in range(0, 500, 3):
            if start + n > len(tot_seq):
                break
            total_consec += 1
            
            key = tot_seq[start:start+n]
            
            # Simple stream (no skip)
            for mode in ['sub', 'beau']:
                if mode == 'sub':
                    plain = [(cipher[i] - key[i]) % 29 for i in range(n)]
                else:
                    plain = [(key[i] - cipher[i]) % 29 for i in range(n)]
                
                ioc = calc_ioc(plain)
                if ioc > IOC_THRESHOLD:
                    text = decode(plain)
                    sc = score_text(text)
                    consec_hits += 1
                    if sc > SCORE_THRESHOLD:
                        print(f"  P{page_num} start={start+1} mode={mode}: IoC={ioc:.3f} score={sc}")
                        print(f"    {text[:80]}")
                        all_results.append(('CONSEC_TOT', page_num, 'consec', start+1, ioc, sc, text[:120]))
            
            # With skip mechanism (on various values)
            for skip_val in [0, 1, 3, 9, 18]:
                total_consec += 1
                plain = []
                key_idx = start
                for i in range(n):
                    if key_idx >= len(tot_seq):
                        break
                    p_val = (cipher[i] - tot_seq[key_idx]) % 29
                    plain.append(p_val)
                    if p_val != skip_val:
                        key_idx += 1
                
                if len(plain) < 20:
                    continue
                ioc = calc_ioc(plain)
                if ioc > IOC_THRESHOLD:
                    text = decode(plain)
                    sc = score_text(text)
                    consec_hits += 1
                    if sc > SCORE_THRESHOLD:
                        print(f"  P{page_num} start={start+1} skip={skip_val}: IoC={ioc:.3f} score={sc}")
                        print(f"    {text[:80]}")
                        all_results.append(('CONSEC_TOT_SKIP', page_num, f'skip={skip_val}', start+1, ioc, sc, text[:120]))
    
    if consec_hits == 0:
        print("  No consecutive-integer totient hits")
    print(f"  Tested {total_consec} configurations")
    
    # =====================================================================
    print("\n" + "=" * 80)
    print("ATTACK 6: GP PRIME ARITHMETIC IN GF(113)")
    print("Operations in a larger field (mod 113, the next prime after 109)")
    print("=" * 80)
    
    GP_PRIME_VAL = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
    
    def mod_inverse(a, m):
        """Extended GCD for modular inverse."""
        if a == 0: return 0
        g, x, _ = extended_gcd(a % m, m)
        if g != 1: return 0
        return x % m
    
    def extended_gcd(a, b):
        if a == 0: return b, 0, 1
        g, x, y = extended_gcd(b % a, a)
        return g, y - (b // a) * x, x
    
    gf_hits = 0
    total_gf = 0
    
    for page_num in target_pages[:5]:
        cipher = unsolved[page_num]
        n = len(cipher)
        
        for mod_p in [113, 127, 131]:  # Primes near/above 109
            for offset in range(0, 50, 2):
                total_gf += 1
                
                # Map cipher values to GP prime values, apply totient stream in GF(mod_p), 
                # then map back via GP primes
                # Build inverse mapping: prime_val -> gp_index
                prime_to_idx = {}
                for idx, pv in enumerate(GP_PRIME_VAL):
                    prime_to_idx[pv % mod_p] = idx
                
                plain = []
                for i in range(n):
                    c_prime = GP_PRIME_VAL[cipher[i]]
                    key_idx = i + offset
                    if key_idx >= len(TOTIENTS_OF_PRIMES):
                        break
                    k = TOTIENTS_OF_PRIMES[key_idx]
                    
                    # Subtraction in GF(mod_p)
                    p_prime = (c_prime - k) % mod_p
                    
                    # Map back to GP index
                    if p_prime in prime_to_idx:
                        plain.append(prime_to_idx[p_prime])
                    else:
                        # Find closest GP prime
                        best = min(range(29), key=lambda j: abs(GP_PRIME_VAL[j] % mod_p - p_prime))
                        plain.append(best)
                
                if len(plain) < 20:
                    continue
                ioc = calc_ioc(plain)
                if ioc > IOC_THRESHOLD:
                    text = decode(plain)
                    sc = score_text(text)
                    gf_hits += 1
                    if sc > SCORE_THRESHOLD:
                        print(f"  P{page_num} mod={mod_p} offset={offset}: IoC={ioc:.3f} score={sc}")
                        print(f"    {text[:80]}")
                        all_results.append(('GF_PRIME', page_num, f'mod{mod_p}', offset, ioc, sc, text[:120]))
    
    if gf_hits == 0:
        print("  No GF(p) arithmetic hits")
    print(f"  Tested {total_gf} GF(p) configurations")
    
    # =====================================================================
    print("\n" + "=" * 80)
    print("ATTACK 7: AUTOKEY WITH SKIP MECHANISM")
    print("Autokey where key advances only when plaintext != skip_val")
    print("=" * 80)
    
    autokey_hits = 0
    total_autokey = 0
    
    for page_num in target_pages[:5]:
        cipher = unsolved[page_num]
        n = len(cipher)
        
        for initial_key_len in range(1, 6):
            # For length-1 initial keys, try all 29
            # For longer, sample
            if initial_key_len == 1:
                initial_keys = [[k] for k in range(29)]
            elif initial_key_len == 2:
                initial_keys = [[a, b] for a in range(0, 29, 3) for b in range(0, 29, 3)]
            elif initial_key_len == 3:
                initial_keys = [[a, b, c] for a in range(0, 29, 5) for b in range(0, 29, 5) for c in range(0, 29, 5)]
            else:
                # Use P63 keyword GP values
                from itertools import combinations
                kw_vals = [[15,8,24,23,3,7,15], [24,18,2,18,4,18,24,20], [1,3,10,23], 
                          [5,24,17,24,20], [3,17,15,5,1,4,24], [19,3,17,10,1,15]]
                initial_keys = [kv[:initial_key_len] for kv in kw_vals if len(kv) >= initial_key_len]
            
            for init_key in initial_keys:
                total_autokey += 1
                
                # Autokey decrypt: plain[i] = cipher[i] - key[i], key extends with plaintext
                plain = []
                key = list(init_key)
                for i in range(n):
                    if i < len(key):
                        k = key[i]
                    else:
                        break
                    p_val = (cipher[i] - k) % 29
                    plain.append(p_val)
                    key.append(p_val)  # extend key with plaintext
                
                ioc = calc_ioc(plain)
                if ioc > IOC_THRESHOLD:
                    text = decode(plain)
                    sc = score_text(text)
                    autokey_hits += 1
                    if sc > SCORE_THRESHOLD:
                        print(f"  P{page_num} init={init_key}: IoC={ioc:.3f} score={sc}")
                        print(f"    {text[:80]}")
                        all_results.append(('AUTOKEY_SKIP', page_num, str(init_key), 0, ioc, sc, text[:120]))
    
    if autokey_hits == 0:
        print("  No autokey hits")
    print(f"  Tested {total_autokey} autokey configurations")
    
    # =====================================================================
    print("\n" + "=" * 80)
    print("ATTACK 8: MULTIPLICATIVE STREAM IN GF(29)")
    print("plain = cipher * inverse(key) mod 29 (where key from number-theoretic stream)")
    print("=" * 80)
    
    # Only values coprime to 29 are invertible; 29 is prime so all 1-28 are invertible
    def mod_inv_29(a):
        return pow(a, 27, 29)  # Fermat's little theorem: a^(p-2) mod p
    
    mult_hits = 0
    total_mult = 0
    
    for page_num in target_pages[:5]:
        cipher = unsolved[page_num]
        n = len(cipher)
        
        for offset in range(0, 100, 2):
            total_mult += 1
            
            plain = []
            for i in range(n):
                key_idx = i + offset
                if key_idx >= len(TOTIENTS_OF_PRIMES):
                    break
                k = TOTIENTS_OF_PRIMES[key_idx] % 29
                if k == 0:
                    plain.append(cipher[i])  # can't divide by 0
                    continue
                p_val = (cipher[i] * mod_inv_29(k)) % 29
                plain.append(p_val)
            
            if len(plain) < 20:
                continue
            ioc = calc_ioc(plain)
            if ioc > IOC_THRESHOLD:
                text = decode(plain)
                sc = score_text(text)
                mult_hits += 1
                if sc > SCORE_THRESHOLD:
                    print(f"  P{page_num} offset={offset}: IoC={ioc:.3f} score={sc}")
                    print(f"    {text[:80]}")
                    all_results.append(('MULT_STREAM', page_num, 'totient_mult', offset, ioc, sc, text[:120]))
            
            # Also try multiplicative with prime values directly
            total_mult += 1
            plain2 = []
            for i in range(n):
                key_idx = i + offset
                if key_idx >= len(PRIMES):
                    break
                k = PRIMES[key_idx] % 29
                if k == 0:
                    plain2.append(cipher[i])
                    continue
                p_val = (cipher[i] * mod_inv_29(k)) % 29
                plain2.append(p_val)
            
            if len(plain2) < 20:
                continue
            ioc2 = calc_ioc(plain2)
            if ioc2 > IOC_THRESHOLD:
                text2 = decode(plain2)
                sc2 = score_text(text2)
                mult_hits += 1
                if sc2 > SCORE_THRESHOLD:
                    print(f"  P{page_num} prime_mult offset={offset}: IoC={ioc2:.3f} score={sc2}")
                    print(f"    {text2[:80]}")
                    all_results.append(('MULT_PRIME', page_num, 'prime_mult', offset, ioc2, sc2, text2[:120]))
    
    if mult_hits == 0:
        print("  No multiplicative stream hits")
    print(f"  Tested {total_mult} multiplicative configurations")
    
    # =====================================================================
    print("\n" + "=" * 80)
    print("ATTACK 9: TOTIENT STREAM WITH PRIME-INDEX SKIP")
    print("Like P55 but skip when position IS/ISN'T prime, or when key_idx is prime")
    print("=" * 80)
    
    def is_prime(n):
        if n < 2: return False
        if n < 4: return True
        if n % 2 == 0 or n % 3 == 0: return False
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0: return False
            i += 6
        return True
    
    pidx_hits = 0
    total_pidx = 0
    
    for page_num in target_pages[:5]:
        cipher = unsolved[page_num]
        n = len(cipher)
        
        for mode in ['prime_pos_only', 'composite_pos_only', 'prime_pos_double', 'prime_idx_skip']:
            for offset in range(0, 100, 5):
                total_pidx += 1
                
                plain = []
                key_idx = offset
                for i in range(n):
                    if key_idx >= len(TOTIENTS_OF_PRIMES):
                        break
                    
                    if mode == 'prime_pos_only':
                        # Only apply key at prime positions; copy cipher otherwise
                        if is_prime(i + 1):
                            k = TOTIENTS_OF_PRIMES[key_idx] % 29
                            plain.append((cipher[i] - k) % 29)
                            key_idx += 1
                        else:
                            plain.append(cipher[i])
                    elif mode == 'composite_pos_only':
                        if not is_prime(i + 1):
                            k = TOTIENTS_OF_PRIMES[key_idx] % 29
                            plain.append((cipher[i] - k) % 29)
                            key_idx += 1
                        else:
                            plain.append(cipher[i])
                    elif mode == 'prime_pos_double':
                        # At prime positions, advance key by 2
                        k = TOTIENTS_OF_PRIMES[key_idx] % 29
                        plain.append((cipher[i] - k) % 29)
                        if is_prime(i + 1):
                            key_idx += 2
                        else:
                            key_idx += 1
                    elif mode == 'prime_idx_skip':
                        # Skip key values that are themselves prime
                        while key_idx < len(TOTIENTS_OF_PRIMES) and is_prime(TOTIENTS_OF_PRIMES[key_idx]):
                            key_idx += 1
                        if key_idx >= len(TOTIENTS_OF_PRIMES):
                            break
                        k = TOTIENTS_OF_PRIMES[key_idx] % 29
                        plain.append((cipher[i] - k) % 29)
                        key_idx += 1
                
                if len(plain) < 20:
                    continue
                ioc = calc_ioc(plain)
                if ioc > IOC_THRESHOLD:
                    text = decode(plain)
                    sc = score_text(text)
                    pidx_hits += 1
                    if sc > SCORE_THRESHOLD:
                        print(f"  P{page_num} mode={mode} offset={offset}: IoC={ioc:.3f} score={sc}")
                        print(f"    {text[:80]}")
                        all_results.append(('PIDX_SKIP', page_num, mode, offset, ioc, sc, text[:120]))
    
    if pidx_hits == 0:
        print("  No prime-index skip hits")
    print(f"  Tested {total_pidx} prime-index skip configurations")
    
    # =====================================================================
    print("\n" + "=" * 80)
    print("ATTACK 10: COMBINED AFFINE + STREAM")
    print("plain = (a * cipher + stream[i]) mod 29 for all multipliers a")
    print("=" * 80)
    
    affine_hits = 0
    total_affine = 0
    
    for page_num in target_pages[:3]:
        cipher = unsolved[page_num]
        n = len(cipher)
        
        for a in range(1, 29):  # Skip 0
            for offset in range(0, 50, 5):
                total_affine += 1
                
                plain = []
                for i in range(n):
                    key_idx = i + offset
                    if key_idx >= len(TOTIENTS_OF_PRIMES):
                        break
                    k = TOTIENTS_OF_PRIMES[key_idx] % 29
                    # Affine: first multiply, then add/subtract stream
                    p_val = (a * cipher[i] - k) % 29
                    plain.append(p_val)
                
                if len(plain) < 20:
                    continue
                ioc = calc_ioc(plain)
                if ioc > IOC_THRESHOLD:
                    text = decode(plain)
                    sc = score_text(text)
                    affine_hits += 1
                    if sc > SCORE_THRESHOLD:
                        print(f"  P{page_num} a={a} offset={offset}: IoC={ioc:.3f} score={sc}")
                        print(f"    {text[:80]}")
                        all_results.append(('AFFINE_STREAM', page_num, f'a={a}', offset, ioc, sc, text[:120]))
    
    if affine_hits == 0:
        print("  No affine+stream hits")
    print(f"  Tested {total_affine} affine+stream configurations")
    
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
        print("\nNO VIABLE HITS across all skip-variant and advanced stream attacks.")
        print("\nCipher types tested this run:")
        print("  - Variable skip-value totient stream (skip=0-28, offsets 0-98)")
        print("  - Ciphertext-dependent key advancement (4 modes)")
        print("  - PGP public key as key material (7 representations)")
        print("  - Cross-page cipher key derivation")
        print("  - Consecutive-integer totient stream with skip")
        print("  - GP prime arithmetic in GF(113/127/131)")
        print("  - Autokey with extended initial keys")
        print("  - Multiplicative stream in GF(29)")
        print("  - Prime-position key advancement variants")
        print("  - Combined affine + stream cipher")
    
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()
