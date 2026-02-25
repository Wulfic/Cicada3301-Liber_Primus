#!/usr/bin/env python3
"""
Hill Cipher Brute Force Attack (2x2 mod 29)
=============================================
A 2x2 Hill cipher encrypts pairs of values: [c1,c2] = [[a,b],[c,d]] * [p1,p2] mod 29

CRITICAL INSIGHT: Hill cipher naturally produces FLAT IoC (~1.0) from English
plaintext because each output depends on two inputs. This perfectly matches
ALL unsolved pages 18-54 having IoC close to 1.0.

Only 29^4 = 707K matrices to test. With det != 0 mod 29: ~683K valid matrices.
We decrypt and check IoC of output. Any IoC > 1.4 indicates English-like text.

Tests on: P20 (812 runes), P32, P44, P50 (largest pages for best IoC signal)
"""
import sys, os, time
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

GP = {'\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
      '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
      '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
      '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
      '\u16A3':26,'\u16E1':27,'\u16E0':28}
IDX2LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

def calc_ioc(vals):
    if len(vals) < 20: return 0
    counts = Counter(vals)
    n = len(vals)
    total = sum(c * (c - 1) for c in counts.values())
    return total / (n * (n - 1) / 29)

def mod_inv(a, m=29):
    """Modular inverse using extended Euclidean algorithm."""
    if a % m == 0:
        return None
    g, x, _ = extended_gcd(a % m, m)
    if g != 1:
        return None
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x, y = extended_gcd(b % a, a)
    return g, y - (b // a) * x, x

def hill_decrypt_2x2(cipher, inv_matrix):
    """Decrypt using 2x2 Hill cipher inverse matrix."""
    a, b, c, d = inv_matrix
    plain = []
    for i in range(0, len(cipher) - 1, 2):
        c1, c2 = cipher[i], cipher[i + 1]
        p1 = (a * c1 + b * c2) % 29
        p2 = (c * c1 + d * c2) % 29
        plain.append(p1)
        plain.append(p2)
    return plain

def count_english(text):
    """Count English word fragments."""
    words = {'THE':10,'AND':10,'FOR':10,'ARE':10,'BUT':10,'NOT':10,'YOU':10,'ALL':10,
             'ONE':10,'OUR':10,'HIS':10,'WHO':10,
             'THAT':20,'WITH':20,'HAVE':20,'THIS':20,'WILL':20,'YOUR':20,'FROM':20,
             'THEY':20,'EACH':20,'WHEN':20,'THAN':20,'WHAT':20,'WERE':20,'SOME':20,
             'THERE':30,'THEIR':30,'WHICH':30,'THESE':30,'THOSE':30,'EVERY':30,
             'ABOUT':30,'WOULD':30,'BEING':30,'SHALL':30,'TRUTH':30,'WORLD':30,
             'WITHIN':40,'SACRED':40,'WISDOM':40,'DIVINE':40,'SPIRIT':40}
    score = 0
    for w, s in words.items():
        cnt = text.count(w)
        score += cnt * s
    return score

def load_page(page_dir):
    """Load runes from a page directory."""
    runes_path = os.path.join('LiberPrimus/pages', page_dir, 'runes.txt')
    if not os.path.exists(runes_path):
        return None
    with open(runes_path, 'r', encoding='utf-8') as f:
        text = f.read()
    return [GP[ch] for ch in text if ch in GP]

def main():
    print("=" * 70)
    print("HILL CIPHER 2x2 BRUTE FORCE (mod 29)")
    print("=" * 70)
    
    # Precompute all modular inverses
    inv_table = {}
    for i in range(29):
        inv_table[i] = mod_inv(i, 29)
    
    # Load pages
    pages_to_test = {}
    for page_name in ['page_20', 'page_32', 'page_44', 'page_50', 'page_18', 'page_22', 'page_25']:
        data = load_page(page_name)
        if data and len(data) > 50:
            pages_to_test[page_name] = data
            print(f"  Loaded {page_name}: {len(data)} runes")
    
    if not pages_to_test:
        print("ERROR: No pages loaded!")
        return
    
    # For efficiency, precompute valid inverse matrices
    print(f"\nPrecomputing valid 2x2 inverse matrices mod 29...")
    start = time.time()
    
    valid_matrices = []
    for a in range(29):
        for b in range(29):
            for c in range(29):
                for d in range(29):
                    det = (a * d - b * c) % 29
                    if det == 0:
                        continue
                    det_inv = inv_table[det]
                    if det_inv is None:
                        continue
                    # Inverse matrix: det_inv * [[d, -b], [-c, a]]
                    ia = (det_inv * d) % 29
                    ib = (det_inv * (-b)) % 29
                    ic = (det_inv * (-c)) % 29
                    id_ = (det_inv * a) % 29
                    valid_matrices.append((a, b, c, d, ia, ib, ic, id_))
    
    elapsed = time.time() - start
    print(f"  {len(valid_matrices)} valid matrices computed in {elapsed:.1f}s")
    
    # For speed, use only ONE page for the brute force sweep, then verify hits on others
    # Use the largest page for best IoC discrimination
    primary_page = max(pages_to_test.items(), key=lambda x: len(x[1]))
    pname, pdata = primary_page
    print(f"\nPrimary sweep on {pname} ({len(pdata)} runes)")
    
    # Make even length
    if len(pdata) % 2 != 0:
        pdata = pdata[:-1]
    
    # BRUTE FORCE
    IOC_THRESHOLD = 1.35  # English GP IoC is ~1.7, random is ~1.0
    hits = []
    
    start = time.time()
    tested = 0
    for a, b, c, d, ia, ib, ic, id_ in valid_matrices:
        plain = hill_decrypt_2x2(pdata, (ia, ib, ic, id_))
        ioc = calc_ioc(plain)
        if ioc > IOC_THRESHOLD:
            text = ''.join(IDX2LAT[v] for v in plain)
            score = count_english(text)
            hits.append((ioc, score, a, b, c, d, text[:120]))
        
        tested += 1
        if tested % 100000 == 0:
            elapsed = time.time() - start
            rate = tested / elapsed if elapsed > 0 else 0
            print(f"  Tested {tested}/{len(valid_matrices)} ({rate:.0f}/s) hits={len(hits)}")
    
    elapsed = time.time() - start
    print(f"\nBrute force complete: {tested} matrices in {elapsed:.1f}s, {len(hits)} hits above IoC>{IOC_THRESHOLD}")
    
    # Sort by IoC
    hits.sort(key=lambda x: (-x[0], -x[1]))
    
    print(f"\n{'='*70}")
    print(f"TOP HITS ON {pname}")
    print(f"{'='*70}")
    for i, (ioc, score, a, b, c, d, text) in enumerate(hits[:30]):
        print(f"  #{i+1} IoC={ioc:.4f} eng={score:3d} matrix=[[{a},{b}],[{c},{d}]]")
        print(f"    {text[:100]}")
    
    # Verify top hits on ALL pages
    if hits:
        print(f"\n{'='*70}")
        print("CROSS-PAGE VERIFICATION OF TOP HITS")
        print(f"{'='*70}")
        for i, (ioc, score, a, b, c, d, _text) in enumerate(hits[:10]):
            det = (a * d - b * c) % 29
            det_inv = inv_table[det]
            ia = (det_inv * d) % 29
            ib = (det_inv * (-b)) % 29
            ic = (det_inv * (-c)) % 29
            id_ = (det_inv * a) % 29
            
            print(f"\n  Matrix [[{a},{b}],[{c},{d}]]:")
            for pg_name, pg_data in pages_to_test.items():
                pd = pg_data if len(pg_data) % 2 == 0 else pg_data[:-1]
                plain = hill_decrypt_2x2(pd, (ia, ib, ic, id_))
                pioc = calc_ioc(plain)
                ptext = ''.join(IDX2LAT[v] for v in plain)
                pscore = count_english(ptext)
                print(f"    {pg_name}: IoC={pioc:.4f} eng={pscore:3d} {ptext[:60]}")

if __name__ == '__main__':
    main()
