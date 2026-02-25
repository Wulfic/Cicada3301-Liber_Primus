#!/usr/bin/env python3
"""
P20 Focused Cipher Attack
==========================
Test specific cipher modes using prime numbers as keys on P20,
following P19's clue about "rearranging the prime numbers" to find
"a path to the Deor."

Tests:
1. Primes mod 29 as running key (ADD/SUB/BEAU)
2. Totient cipher (like P55/P73): (cipher - (prime-1)) % 29
3. Prime-indexed Deor poem characters as running key
4. Deor characters reordered by primes, then as key
5. Nth prime DIFFERENCES mod 29 as key
6. Cumulative sum of primes mod 29 as key
7. Prime factorization-based approaches
"""
import sys, os
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

GP = {'\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
      '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
      '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
      '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
      '\u16A3':26,'\u16E1':27,'\u16E0':28}
IDX2LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

E2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,'K':5,'L':20,'M':19,
        'N':9,'O':3,'P':13,'R':4,'S':15,'T':16,'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}

def sieve_primes(limit):
    """Generate primes up to limit."""
    is_p = [True] * (limit + 1)
    is_p[0] = is_p[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_p[i]:
            for j in range(i*i, limit + 1, i):
                is_p[j] = False
    return [i for i in range(limit + 1) if is_p[i]]

def calc_ioc(vals):
    if len(vals) < 2: return 0
    counts = Counter(vals)
    n = len(vals)
    total = sum(c * (c - 1) for c in counts.values())
    return total / (n * (n - 1) / 29) if n > 1 else 0

def count_english(text):
    words = {'THE':9,'AND':9,'FOR':9,'ARE':9,'BUT':9,'NOT':9,'YOU':9,'ALL':9,'HER':9,'WAS':9,'ONE':9,'OUR':9,
             'HIS':9,'WHO':9,'MAN':9,'OLD':9,'MAY':9,'DAY':9,'HIM':9,'LET':9,'SAY':9,'SHE':9,
             'THAT':16,'WITH':16,'HAVE':16,'THIS':16,'WILL':16,'YOUR':16,'FROM':16,'THEY':16,
             'EACH':16,'WHEN':16,'THAN':16,'WHAT':16,'WERE':16,'SOME':16,'LIKE':16,'SELF':16,
             'KNOW':16,'MIND':16,'MUST':16,'FIND':16,'SEEK':16,'PATH':16,'FREE':16,'SOUL':16,
             'THERE':25,'THEIR':25,'WHICH':25,'THESE':25,'THOSE':25,'AFTER':25,'EVERY':25,
             'ABOUT':25,'WOULD':25,'BEING':25,'SHALL':25,'TRUTH':25,'WORLD':25,'NEVER':25,
             'WITHIN':36,'SACRED':36,'WISDOM':36,'DIVINE':36,'PRIMES':36,'SPIRIT':36,'DIVINITY':64}
    score = 0
    for w, s in words.items():
        score += text.count(w) * s
    return score

def decrypt(cipher_vals, key_vals, mode):
    out = []
    for i, c in enumerate(cipher_vals):
        k = key_vals[i % len(key_vals)] if len(key_vals) <= len(cipher_vals) else key_vals[i]
        if mode == 'SUB':
            out.append((c - k) % 29)
        elif mode == 'ADD':
            out.append((c + k) % 29)
        elif mode == 'BEAU':
            out.append((k - c) % 29)
    return out

def load_deor_oe():
    """Load Deor poem in Old English (GP values)."""
    deor_text = """WELUND HIM BE WURMAN WRÆCES CUNNADE
ANHYDIG EORL EARFOÞA DREAG
HÆFDE HIM TO GESIÞÞE SORGE AND LONGAÞ
WINTERCEALDE WRÆCE WEAN OFT ONFOND
SIÞÞAN HINE NIÞHAD ON NEDE LEGDE
SWONCRE SEONOBENDE ON SYLLAN MONN
ÞÆS OFEREODE ÞISSES SWA MÆG

BEADOHILDE NE WÆS HYRE BROÞRA DEAÞ
ON SEFAN SWA SAR SWA HYRE SYLFRE ÞING
ÞÆT HEO GEAROLICE ONGIETAN HÆFDE
ÞÆT HEO EACEN WÆS ÆFRE NE MEAHTE
ÞRISTE GEÞENCAN HU YMBE ÞÆT SCEOLDE
ÞÆS OFEREODE ÞISSES SWA MÆG

WE ÞÆT MÆÞHILDE MONGE GEFRUGNON
WURDON GRUNDLEASE GEATAS FRIGE
ÞÆT HI SEO SORGLUFU SLÆP EALLE BINOM
ÞÆS OFEREODE ÞISSES SWA MÆG

ÐEODRIC AHTE ÞRITIG WINTRA
MÆRINGA BURG ÞÆT WÆS MONEGUM CUÞ
ÞÆS OFEREODE ÞISSES SWA MÆG

WE GEASCODAN EORMANRICES
WYLFENNE GEÞOHT AHTE WIDE FOLC
GOTENA RICES ÞÆT WÆS GRIM CYNING
SÆT SECG MONIG SORGUM GEBUNDEN
WEAN ON WENAN WYSCTE GENEAHHE
ÞÆT ÞÆS CYNERICES OFERCUMEN WÆRE
ÞÆS OFEREODE ÞISSES SWA MÆG

SITEþ SORGCEARIG SÆLUM BIDÆLED
ON SEFAN SWEORCEÞ SYLFUM ÞINCEÞ
ÞÆT SY ENDELEAS EARFOÐA DÆL
MÆG ÞONNE GEÞENCAN ÞÆT GEOND ÞAS WORULD
WITIG DRYHTEN WENDEÞ GENEAHHE
EORLE MONEGUM ARE GESCEAWAÐ
WISLICNE GRUND SUME ÞAS WELA DÆL"""
    
    # Convert OE to GP values (letter by letter)
    special = {'Þ': 2, 'Ð': 23, 'Æ': 25, 'Ý': 26, 'Ƿ': 7, 'Ȝ': 6}  # thorn, eth, ash, ...
    oe_to_gp = {**E2GP, **{k: v for k, v in special.items()}}
    oe_to_gp['Þ'] = 2  # thorn = TH(2)
    oe_to_gp['Ð'] = 23  # eth = D(23) or TH(2) -- let's try both
    
    vals = []
    for ch in deor_text.upper():
        if ch in oe_to_gp:
            vals.append(oe_to_gp[ch])
        elif ch in E2GP:
            vals.append(E2GP[ch])
    return vals

def main():
    primes = sieve_primes(10000)
    print(f"Generated {len(primes)} primes up to 10000")
    
    # Load P20
    with open('LiberPrimus/pages/page_20/runes.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    p20 = [GP[ch] for ch in text if ch in GP]
    n = len(p20)
    print(f"P20: {n} runes, raw IoC={calc_ioc(p20):.4f}")
    
    # Load Deor
    deor = load_deor_oe()
    print(f"Deor OE: {len(deor)} GP values")
    
    results = []
    
    # ============================================
    # TEST 1: Primes mod 29 as running key
    # ============================================
    print("\n=== TEST 1: Primes mod 29 as key ===")
    key_primes_mod29 = [p % 29 for p in primes[:n]]
    for mode in ['SUB', 'ADD', 'BEAU']:
        dec = decrypt(p20, key_primes_mod29, mode)
        ioc = calc_ioc(dec)
        text = ''.join(IDX2LAT[v] for v in dec)
        score = count_english(text)
        print(f"  primes_mod29 {mode}: IoC={ioc:.4f} score={score} {text[:60]}")
        results.append((ioc, score, f"primes_mod29_{mode}", text[:100]))
    
    # Also try with offset (skip first N primes)
    for offset in [1, 2, 5, 10, 20]:
        key = [primes[i+offset] % 29 for i in range(n)]
        for mode in ['SUB', 'ADD', 'BEAU']:
            dec = decrypt(p20, key, mode)
            ioc = calc_ioc(dec)
            text = ''.join(IDX2LAT[v] for v in dec)
            score = count_english(text)
            if score > 50 or ioc > 1.3:
                print(f"  primes_off{offset}_{mode}: IoC={ioc:.4f} score={score} {text[:60]}")
                results.append((ioc, score, f"primes_off{offset}_{mode}", text[:100]))
    
    # ============================================
    # TEST 2: Totient cipher (like P55/P73)
    # ============================================
    print("\n=== TEST 2: Totient cipher (prime-1) ===")
    for skip_f in [False, True]:
        label = "fskip" if skip_f else "noskip"
        # Totient: plaintext[i] = (cipher[i] - (prime[idx]-1)) % 29
        dec = []
        key_idx = 0
        for i in range(n):
            if skip_f and p20[i] == 0:  # F-skip
                dec.append(0)
            else:
                dec.append((p20[i] - (primes[key_idx] - 1)) % 29)
                key_idx += 1
        ioc = calc_ioc(dec)
        text = ''.join(IDX2LAT[v] for v in dec)
        score = count_english(text)
        print(f"  totient_{label}: IoC={ioc:.4f} score={score} {text[:80]}")
        results.append((ioc, score, f"totient_{label}", text[:100]))
        
        # Also try ADD mode totient
        dec2 = []
        key_idx = 0
        for i in range(n):
            if skip_f and p20[i] == 0:
                dec2.append(0)
            else:
                dec2.append((p20[i] + (primes[key_idx] - 1)) % 29)
                key_idx += 1
        ioc = calc_ioc(dec2)
        text = ''.join(IDX2LAT[v] for v in dec2)
        score = count_english(text)
        print(f"  totient_add_{label}: IoC={ioc:.4f} score={score} {text[:80]}")
        results.append((ioc, score, f"totient_add_{label}", text[:100]))
    
    # Try with different prime offsets for totient
    for prime_off in [0, 1, 2, 5, 10]:
        dec = [(p20[i] - (primes[i + prime_off] - 1)) % 29 for i in range(n)]
        ioc = calc_ioc(dec)
        text = ''.join(IDX2LAT[v] for v in dec)
        score = count_english(text)
        print(f"  totient_poff{prime_off}: IoC={ioc:.4f} score={score} {text[:60]}")
        results.append((ioc, score, f"totient_poff{prime_off}", text[:100]))
    
    # ============================================
    # TEST 3: Prime gaps as key
    # ============================================
    print("\n=== TEST 3: Prime gaps mod 29 ===")
    gaps = [primes[i+1] - primes[i] for i in range(n)]
    for mode in ['SUB', 'ADD', 'BEAU']:
        dec = decrypt(p20, gaps, mode)
        ioc = calc_ioc(dec)
        text = ''.join(IDX2LAT[v] for v in dec)
        score = count_english(text)
        print(f"  gaps_{mode}: IoC={ioc:.4f} score={score} {text[:60]}")
        results.append((ioc, score, f"gaps_{mode}", text[:100]))
    
    # ============================================
    # TEST 4: Cumulative primes mod 29
    # ============================================
    print("\n=== TEST 4: Cumulative sum of primes mod 29 ===")
    cum = []
    s = 0
    for i in range(n):
        s += primes[i]
        cum.append(s % 29)
    for mode in ['SUB', 'ADD', 'BEAU']:
        dec = decrypt(p20, cum, mode)
        ioc = calc_ioc(dec)
        text = ''.join(IDX2LAT[v] for v in dec)
        score = count_english(text)
        print(f"  cumprimes_{mode}: IoC={ioc:.4f} score={score} {text[:60]}")
        results.append((ioc, score, f"cumprimes_{mode}", text[:100]))
    
    # ============================================
    # TEST 5: Deor as running key
    # ============================================
    print("\n=== TEST 5: Deor poem as running key ===")
    for mode in ['SUB', 'ADD', 'BEAU']:
        dec = decrypt(p20, deor, mode)
        ioc = calc_ioc(dec)
        text = ''.join(IDX2LAT[v] for v in dec)
        score = count_english(text)
        print(f"  deor_{mode}: IoC={ioc:.4f} score={score} {text[:80]}")
        results.append((ioc, score, f"deor_{mode}", text[:100]))
    
    # Deor with different starting offsets
    for offset in [10, 20, 50, 100, 200]:
        if offset + n <= len(deor):
            key = deor[offset:offset+n]
            for mode in ['SUB', 'ADD', 'BEAU']:
                dec = decrypt(p20, key, mode)
                ioc = calc_ioc(dec)
                text = ''.join(IDX2LAT[v] for v in dec)
                score = count_english(text)
                if score > 60 or ioc > 1.3:
                    print(f"  deor_off{offset}_{mode}: IoC={ioc:.4f} score={score} {text[:60]}")
                    results.append((ioc, score, f"deor_off{offset}_{mode}", text[:100]))
    
    # ============================================
    # TEST 6: Deor characters at prime positions as key  
    # ============================================
    print("\n=== TEST 6: Deor[prime] as key ===")
    deor_at_primes = [deor[p] for p in primes if p < len(deor)]
    print(f"  Deor chars at prime positions: {len(deor_at_primes)}")
    if len(deor_at_primes) >= n:
        key = deor_at_primes[:n]
    else:
        key = deor_at_primes
    for mode in ['SUB', 'ADD', 'BEAU']:
        dec = decrypt(p20, key, mode)
        ioc = calc_ioc(dec)
        text = ''.join(IDX2LAT[v] for v in dec)
        score = count_english(text)
        print(f"  deor_at_primes_{mode}: IoC={ioc:.4f} score={score} {text[:80]}")
        results.append((ioc, score, f"deor_at_primes_{mode}", text[:100]))
    
    # ============================================  
    # TEST 7: Primes used to permute then decrypt
    # ============================================
    print("\n=== TEST 7: Read P20 at prime-permuted positions ===")
    # Read rune at position (prime[i] % n)
    permuted = [p20[primes[i] % n] for i in range(n)]
    ioc = calc_ioc(permuted)
    text = ''.join(IDX2LAT[v] for v in permuted)
    score = count_english(text)
    print(f"  prime_permute: IoC={ioc:.4f} score={score} {text[:60]}")
    results.append((ioc, score, "prime_permute", text[:100]))
    
    # Then apply Deor key
    for mode in ['SUB', 'ADD', 'BEAU']:
        dec = decrypt(permuted, deor, mode)
        ioc = calc_ioc(dec)
        text = ''.join(IDX2LAT[v] for v in dec)
        score = count_english(text)
        if score > 60 or ioc > 1.3:
            print(f"  prime_permute_deor_{mode}: IoC={ioc:.4f} score={score} {text[:60]}")
            results.append((ioc, score, f"prime_permute_deor_{mode}", text[:100]))
    
    # ============================================
    # TEST 8: Multiplicative cipher: cipher * prime^(-1) mod 29
    # ============================================
    print("\n=== TEST 8: Multiplicative cipher ===")
    # Find modular inverses mod 29
    inv = {}
    for a in range(1, 29):
        for b in range(1, 29):
            if (a * b) % 29 == 1:
                inv[a] = b
                break
    
    # cipher[i] * inverse(prime[i] mod 29) mod 29
    dec = []
    for i in range(n):
        p = primes[i] % 29
        if p in inv:
            dec.append((p20[i] * inv[p]) % 29)
        else:
            dec.append(p20[i])
    ioc = calc_ioc(dec)
    text = ''.join(IDX2LAT[v] for v in dec)
    score = count_english(text)
    print(f"  mult_prime_inv: IoC={ioc:.4f} score={score} {text[:60]}")
    results.append((ioc, score, "mult_prime_inv", text[:100]))
    
    # ============================================
    # TEST 9: Affine cipher with primes
    # ============================================
    print("\n=== TEST 9: Affine: (cipher - b) * inv(a) mod 29 for small a,b ===")
    for a in [2, 3, 5, 7, 11, 13, 17, 19, 23]:
        if a % 29 not in inv:
            continue
        for b in range(29):
            dec = [((p20[i] - b) * inv[a % 29]) % 29 for i in range(n)]
            ioc = calc_ioc(dec)
            text = ''.join(IDX2LAT[v] for v in dec)
            score = count_english(text)
            if score > 100 or ioc > 1.5:
                print(f"  affine_a{a}_b{b}: IoC={ioc:.4f} score={score} {text[:60]}")
                results.append((ioc, score, f"affine_a{a}_b{b}", text[:100]))
    
    # ============================================
    # TEST 10: XOR with primes
    # ============================================
    print("\n=== TEST 10: XOR cipher with primes ===")
    for offset in [0, 1, 2, 5]:
        dec = [p20[i] ^ (primes[i+offset] % 32) for i in range(n)]
        # Clamp to 0-28
        dec_clamped = [v % 29 for v in dec]
        ioc = calc_ioc(dec_clamped)
        text = ''.join(IDX2LAT[v] for v in dec_clamped)
        score = count_english(text)
        print(f"  xor_prime_off{offset}: IoC={ioc:.4f} score={score} {text[:60]}")
        results.append((ioc, score, f"xor_prime_off{offset}", text[:100]))
    
    # ============================================
    # TEST 11: Combined primes + Deor
    # ============================================
    print("\n=== TEST 11: Combined (primes + Deor) as key ===")
    # Key = (prime[i] + deor[i]) mod 29
    combined_key = [(primes[i] % 29 + deor[i % len(deor)]) % 29 for i in range(n)]
    for mode in ['SUB', 'ADD', 'BEAU']:
        dec = decrypt(p20, combined_key, mode)
        ioc = calc_ioc(dec)
        text = ''.join(IDX2LAT[v] for v in dec)
        score = count_english(text)
        print(f"  prime_plus_deor_{mode}: IoC={ioc:.4f} score={score} {text[:60]}")
        results.append((ioc, score, f"prime_plus_deor_{mode}", text[:100]))
    
    # Key = prime[i] * deor[i] mod 29
    mult_key = [(primes[i] % 29 * deor[i % len(deor)]) % 29 for i in range(n)]
    for mode in ['SUB', 'ADD', 'BEAU']:
        dec = decrypt(p20, mult_key, mode)
        ioc = calc_ioc(dec)
        text = ''.join(IDX2LAT[v] for v in dec)
        score = count_english(text)
        if score > 50:
            print(f"  prime_times_deor_{mode}: IoC={ioc:.4f} score={score} {text[:60]}")
            results.append((ioc, score, f"prime_times_deor_{mode}", text[:100]))
    
    # ============================================
    # TEST 12: F-skip variants
    # ============================================
    print("\n=== TEST 12: F-skip with primes mod 29 ===")
    for mode in ['SUB', 'ADD', 'BEAU']:
        dec = []
        key_idx = 0
        for i in range(n):
            if p20[i] == 0:  # F = literal
                dec.append(0)
            else:
                k = primes[key_idx] % 29
                if mode == 'SUB':
                    dec.append((p20[i] - k) % 29)
                elif mode == 'ADD':
                    dec.append((p20[i] + k) % 29)
                else:
                    dec.append((k - p20[i]) % 29)
                key_idx += 1
        ioc = calc_ioc(dec)
        text = ''.join(IDX2LAT[v] for v in dec)
        score = count_english(text)
        print(f"  fskip_primes_{mode}: IoC={ioc:.4f} score={score} {text[:80]}")
        results.append((ioc, score, f"fskip_primes_{mode}", text[:100]))
    
    # F-skip with Deor  
    for mode in ['SUB', 'ADD', 'BEAU']:
        dec = []
        key_idx = 0
        for i in range(n):
            if p20[i] == 0:
                dec.append(0)
            else:
                k = deor[key_idx % len(deor)]
                if mode == 'SUB':
                    dec.append((p20[i] - k) % 29)
                elif mode == 'ADD':
                    dec.append((p20[i] + k) % 29)
                else:
                    dec.append((k - p20[i]) % 29)
                key_idx += 1
        ioc = calc_ioc(dec)
        text = ''.join(IDX2LAT[v] for v in dec)
        score = count_english(text)
        print(f"  fskip_deor_{mode}: IoC={ioc:.4f} score={score} {text[:80]}")
        results.append((ioc, score, f"fskip_deor_{mode}", text[:100]))
    
    # ============================================
    # TEST 13: Nth prime as INDEX into alphabet
    # ============================================
    print("\n=== TEST 13: Substitution: map GP[i] → prime(GP[i]) mod 29 ===")
    prime_sub = [primes[v] % 29 for v in p20]
    ioc = calc_ioc(prime_sub)
    text = ''.join(IDX2LAT[v] for v in prime_sub)
    score = count_english(text)
    print(f"  prime_sub: IoC={ioc:.4f} score={score} {text[:80]}")
    results.append((ioc, score, "prime_sub", text[:100]))
    
    # Reverse: find v such that prime(v) % 29 == GP[i]
    # This is a lookup table
    rev_map = {}
    for v in range(29):
        for p_idx in range(200):
            if primes[p_idx] % 29 == v:
                rev_map[v] = p_idx % 29
                break
    if len(rev_map) == 29:
        rev_sub = [rev_map[v] for v in p20]
        ioc = calc_ioc(rev_sub)
        text = ''.join(IDX2LAT[v] for v in rev_sub)
        score = count_english(text)
        print(f"  prime_rev_sub: IoC={ioc:.4f} score={score} {text[:80]}")
        results.append((ioc, score, "prime_rev_sub", text[:100]))
    
    # ============================================
    # FINAL RESULTS
    # ============================================
    print("\n" + "=" * 70)
    print("TOP 20 RESULTS (by score)")
    print("=" * 70)
    results.sort(key=lambda x: (-x[1], -x[0]))
    seen = set()
    count = 0
    for ioc, score, label, text in results:
        key = text[:40]
        if key not in seen and count < 20:
            seen.add(key)
            print(f"  IoC={ioc:.4f} Score={score:4d} {label}")
            print(f"    {text}")
            count += 1

    print("\n" + "=" * 70)
    print("TOP 20 RESULTS (by IoC)")
    print("=" * 70)
    results.sort(key=lambda x: (-x[0], -x[1]))
    seen = set()
    count = 0
    for ioc, score, label, text in results:
        key = text[:40]
        if key not in seen and count < 20:
            seen.add(key)
            print(f"  IoC={ioc:.4f} Score={score:4d} {label}")
            print(f"    {text}")
            count += 1

if __name__ == '__main__':
    main()
