#!/usr/bin/env python3
"""
Simulated annealing Vigenere solver for P22 (kl=33) and P49 (kl=21).
Also tests other key lengths and all 3 modes.
"""
import sys, os, math, random
from pathlib import Path
from collections import Counter

OUT = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sa_results.txt'), 'w', encoding='utf-8')
def pr(*a, **kw):
    print(*a, **kw)
    print(*a, **kw, file=OUT, flush=True)

GP = {'\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
      '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
      '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
      '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
      '\u16A3':26,'\u16E1':27,'\u16E0':28}
IDX2LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
MOD = 29

def load_runes(pnum):
    for fmt in [f"page_{pnum:02d}", f"page_{pnum}"]:
        p = Path(rf"c:\Users\tyler\Repos\Cicada3301\LiberPrimus\pages\{fmt}\runes.txt")
        if p.exists():
            return [GP[ch] for ch in p.read_text(encoding='utf-8') if ch in GP]
    return []

def to_lat(idx): return ''.join(IDX2LAT[i] for i in idx)

# Quadgram-like scoring using bigrams and trigrams
# English bigram log-probabilities (approximate, tuned for GP output)
BIGRAM_SCORES = {}
common_bi = [
    ('TH',12),('HE',10),('IN',9),('ER',8),('AN',8),('RE',7),('ON',7),('AT',7),
    ('EN',7),('ND',6),('TI',6),('ES',6),('OR',6),('TE',6),('OF',5),('ED',5),
    ('IS',5),('IT',5),('AL',5),('AR',5),('ST',5),('TO',5),('NT',5),('NG',5),
    ('SE',4),('HA',4),('AS',4),('OU',4),('IO',4),('LE',4),('VE',4),('CO',4),
    ('ME',4),('DE',4),('HI',4),('RI',4),('RO',4),('IC',3),('NE',3),('EA',3),
    ('RA',3),('CE',3),('LI',3),('CH',3),('LL',3),('BE',3),('MA',3),('SI',3),
    ('OM',3),('UR',3),('WI',3),('EL',3),('OE',2),('IA',2),('AE',2),
]
for bi, sc in common_bi:
    BIGRAM_SCORES[bi] = sc

def score_bigram(lat):
    """Fast bigram scoring."""
    s = 0
    for i in range(len(lat)-1):
        bg = lat[i:i+2]
        if bg in BIGRAM_SCORES:
            s += BIGRAM_SCORES[bg]
    return s

def decrypt_with_key(cipher, key, mode):
    """Decrypt cipher with given key array."""
    kl = len(key)
    result = []
    for i, c in enumerate(cipher):
        k = key[i % kl]
        if mode == 'sub':
            result.append((c - k) % MOD)
        elif mode == 'add':
            result.append((c + k) % MOD)
        elif mode == 'beau':
            result.append((k - c) % MOD)
    return result

def sa_solve(cipher, kl, mode, iterations=50000, restarts=5):
    """Simulated annealing to find the best key of length kl."""
    n = len(cipher)
    best_key = None
    best_score = -1e9
    best_text = ""
    
    for restart in range(restarts):
        # Random initial key
        key = [random.randint(0, MOD-1) for _ in range(kl)]
        dec = decrypt_with_key(cipher, key, mode)
        lat = to_lat(dec)
        cur_score = score_bigram(lat)
        
        temp = 10.0
        
        for it in range(iterations):
            # Mutate: change one key position
            pos = random.randint(0, kl-1)
            old_val = key[pos]
            new_val = random.randint(0, MOD-1)
            if new_val == old_val:
                new_val = (old_val + random.randint(1, MOD-1)) % MOD
            
            key[pos] = new_val
            
            # Recalculate only affected positions (optimization)
            new_dec = decrypt_with_key(cipher, key, mode)
            new_lat = to_lat(new_dec)
            new_score = score_bigram(new_lat)
            
            # Accept or reject
            delta = new_score - cur_score
            if delta > 0 or random.random() < math.exp(delta / max(temp, 0.01)):
                cur_score = new_score
                dec = new_dec
                lat = new_lat
            else:
                key[pos] = old_val  # Revert
            
            # Cool down
            temp *= 0.99995
            
            if cur_score > best_score:
                best_score = cur_score
                best_key = key[:]
                best_text = lat
        
    return best_key, best_score, best_text

def main():
    random.seed(42)
    
    pages_config = [
        (22, [7, 8, 11, 13, 33, 29, 131]),  # Test various key lengths for P22
        (49, [6, 7, 8, 11, 21, 22, 33, 66]),  # Test various key lengths for P49
    ]
    
    for page_num, key_lengths in pages_config:
        cipher = load_runes(page_num)
        if not cipher:
            pr(f"Could not load page {page_num}")
            continue
        
        pr(f"\n{'='*70}")
        pr(f"PAGE {page_num} ({len(cipher)} runes)")
        pr(f"{'='*70}")
        
        all_results = []
        
        for kl in key_lengths:
            for mode in ['sub', 'add', 'beau']:
                key, sc, text = sa_solve(cipher, kl, mode, iterations=80000, restarts=3)
                
                key_lat = ''.join(IDX2LAT[k] for k in key)
                tag = f"kl={kl} {mode}"
                all_results.append((sc, tag, key, text))
                
                if sc > 50:
                    pr(f"  {tag}: score={sc}")
                    pr(f"    key={key_lat}")
                    pr(f"    text={text[:120]}")
        
        all_results.sort(reverse=True)
        pr(f"\n--- TOP 10 P{page_num} SA RESULTS ---")
        for i, (sc, tag, key, text) in enumerate(all_results[:10]):
            key_lat = ''.join(IDX2LAT[k] for k in key)
            pr(f"  #{i+1} score={sc} {tag}")
            pr(f"    key={key_lat}")
            pr(f"    text={text[:150]}")
    
    # Also try autokey cipher
    pr(f"\n\n{'='*70}")
    pr("AUTOKEY CIPHER TEST")
    pr(f"{'='*70}")
    
    for page_num in [22, 49]:
        cipher = load_runes(page_num)
        pr(f"\nPage {page_num} ({len(cipher)} runes):")
        
        PRIMERS = {
            'DIVINITY': [23,10,1,10,9,10,16,26],
            'FIRFUMFER': [0,10,4,0,1,19,0,18,4,18,9,0,18],
            'MOBIUS': [19,3,17,10,1,15],
            'CICADA': [5,10,5,24,23,24],
            'PILGRIM': [13,10,20,6,4,10,19],
            'WELCOME': [7,18,20,5,3,19,18],
            'WISDOM': [7,10,15,23,3,19],
            'SACRED': [15,24,5,4,18,23],
            'BELIEVE': [17,18,20,10,18,1,18],
            'INSTAR': [10,9,15,16,24,4],
            'TRUTH': [16,4,1,2],
        }
        
        best_autokey = []
        
        for primer_name, primer in PRIMERS.items():
            for mode in ['sub', 'add', 'beau']:
                for feedback in ['plaintext', 'ciphertext']:
                    # Autokey decryption
                    dec = []
                    key_stream = list(primer)
                    
                    for i, c in enumerate(cipher):
                        if i < len(key_stream):
                            k = key_stream[i]
                        else:
                            # Extend key from feedback
                            if feedback == 'plaintext' and dec:
                                k = dec[-1]
                            elif feedback == 'ciphertext':
                                k = cipher[i - len(primer)]
                            else:
                                k = 0
                        
                        if mode == 'sub': p = (c - k) % MOD
                        elif mode == 'add': p = (c + k) % MOD
                        elif mode == 'beau': p = (k - c) % MOD
                        
                        dec.append(p)
                        if len(key_stream) <= i + len(primer):
                            if feedback == 'plaintext':
                                key_stream.append(p)
                            else:
                                key_stream.append(c)
                    
                    lat = to_lat(dec)
                    sc = score_bigram(lat)
                    
                    tag = f"{primer_name} {mode} {feedback}"
                    best_autokey.append((sc, tag, lat))
        
        best_autokey.sort(reverse=True)
        pr(f"\n  Top 10 autokey for P{page_num}:")
        for i, (sc, tag, lat) in enumerate(best_autokey[:10]):
            pr(f"    #{i+1} sc={sc} {tag}: {lat[:100]}")
    
    pr("\nDone.")
    OUT.close()

if __name__ == '__main__':
    main()
