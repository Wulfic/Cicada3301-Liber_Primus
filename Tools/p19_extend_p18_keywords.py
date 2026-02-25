#!/usr/bin/env python3
"""
P19 Plaintext Extension + P18 Keyword Attack
=============================================
1. Extend P19 decryption by guessing what follows "DEOR"
2. Test P63 grid keywords on P18 systematically
"""
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

GP = {'\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
      '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
      '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
      '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
      '\u16A3':26,'\u16E1':27,'\u16E0':28}
IDX2LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
E2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,'K':5,'L':20,'M':19,
        'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}

def text_to_gp(text):
    """Convert English text to GP values, handling digraphs."""
    result = []
    i = 0
    text = text.upper()
    while i < len(text):
        if i + 1 < len(text):
            digraph = text[i:i+2]
            if digraph == 'TH':
                result.append(2); i += 2; continue
            elif digraph == 'NG':
                result.append(21); i += 2; continue
            elif digraph == 'OE':
                result.append(22); i += 2; continue
            elif digraph == 'AE':
                result.append(25); i += 2; continue
            elif digraph == 'IA':
                result.append(27); i += 2; continue
            elif digraph == 'EA':
                result.append(28); i += 2; continue
            elif digraph == 'EO':
                result.append(12); i += 2; continue
            elif digraph == 'IO':
                result.append(27); i += 2; continue  # Map IO → IA
        ch = text[i]
        if ch in E2GP:
            result.append(E2GP[ch])
        i += 1
    return result

def calc_ioc(vals):
    if len(vals) < 20: return 0
    counts = Counter(vals)
    n = len(vals)
    total = sum(c * (c - 1) for c in counts.values())
    return total / (n * (n - 1) / 29)

def count_english(text):
    words = {'THE':10,'AND':10,'FOR':10,'ARE':10,'BUT':10,'NOT':10,'YOU':10,'ALL':10,
             'ONE':10,'OUR':10,'HIS':10,'WHO':10,'MAN':10,'OLD':10,'HIM':10,
             'THAT':20,'WITH':20,'HAVE':20,'THIS':20,'WILL':20,'YOUR':20,'FROM':20,
             'THEY':20,'EACH':20,'WHEN':20,'THAN':20,'WHAT':20,'SOME':20,
             'KNOW':20,'MIND':20,'MUST':20,'FIND':20,'SEEK':20,'PATH':20,
             'THERE':30,'THEIR':30,'WHICH':30,'THESE':30,'THOSE':30,
             'ABOUT':30,'WOULD':30,'BEING':30,'SHALL':30,'TRUTH':30,'WORLD':30,
             'WITHIN':40,'SACRED':40,'WISDOM':40,'DIVINE':40,'PRIMES':40,'SPIRIT':40,'DIVINITY':60}
    score = 0
    for w, s in words.items():
        score += text.count(w) * s
    return score

def main():
    # Load P19
    with open('LiberPrimus/pages/page_19/runes.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    p19 = [GP[ch] for ch in text if ch in GP]
    print(f"P19: {len(p19)} runes")
    
    # Verified P19 key (ADD mode, first 43 values)
    key_43 = [24, 15, 2, 24, 4, 21, 11, 10, 20, 16, 9, 19, 26, 11, 7, 5, 11, 6, 27, 8, 22, 25, 21, 16, 25, 0, 27, 9, 21, 7, 27, 15, 21, 9, 3, 16, 5, 22, 18, 4, 5, 18, 23]
    
    # Verify first 43 runes
    plain_43 = [(p19[i] + key_43[i]) % 29 for i in range(43)]
    text_43 = ''.join(IDX2LAT[v] for v in plain_43)
    print(f"Verified first 43: {text_43}")
    
    # The plaintext ends at position 42 with 'R' (4) from "DEOR"
    # Position 43 onward we need to guess
    
    print("\n" + "=" * 70)
    print("PART 1: EXTEND P19 DECRYPTION")
    print("=" * 70)
    
    # Try extending with various likely continuations
    continuations = [
        # After "REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR"
        "KEY", "POEM", "KOAN", "RIDDLE", "CIPHER", "CODE", 
        "KEYISWITHIN", "KEYISTHEDIVINE",
        "ISSAKRED", "ISSACRED",
        # Possible sentence continuations
        "ANDTHEWAY", "ANDTHETRUTH", "ANDTHELIGHT",
        "WHOMADETHEWORLD", "THEPATHIS",
        # About the Deor poem specifically
        "THATLIESWITHIN", "THATISTHEKEY", 
        "REFRAIN", "REFRAINISTHEKEY",
        # Longer phrases
        "BUTFIRSTYOUMUST", "ANDYOUWILLFIND",
        "THEKEYISNOTCOERCED",  # matches key fragment!
    ]
    
    print(f"\nTesting {len(continuations)} continuation guesses...")
    for cont in continuations:
        gp_vals = text_to_gp(cont)
        if not gp_vals:
            continue
        
        # In ADD mode: plaintext = (cipher + key) % 29
        # So key = (plaintext - cipher) % 29
        max_extend = min(len(gp_vals), len(p19) - 43)
        new_key_vals = []
        for j in range(max_extend):
            pos = 43 + j
            new_key_vals.append((gp_vals[j] - p19[pos]) % 29)
        
        # Try extending the key and decrypting MORE
        extended_key = key_43 + new_key_vals
        # Decrypt first 43 + extension + some more
        extended_len = min(len(extended_key) + 50, len(p19))
        
        # Check if continuing with this extended key produces reasonable text
        # Decrypt positions beyond the extension to see if the key pattern continues
        
        # Show what the key looks like at the extension
        key_text = ''.join(IDX2LAT[v] for v in new_key_vals)
        
        # Decrypt using extended key with potential pattern
        full_plain = [(p19[i] + extended_key[i % len(extended_key)]) % 29 for i in range(min(len(extended_key), len(p19)))]
        full_text = ''.join(IDX2LAT[v] for v in full_plain)
        
        print(f"  '{cont}' → key extension: [{','.join(str(v) for v in new_key_vals[:10])}]  key_text={key_text[:20]}")
    
    # ============================================
    # Now let's look at what key values would make common English words
    # at positions 43-60
    # ============================================
    print("\n--- Checking positions 43-60 for specific words ---")
    
    # If position 43 starts a new sentence or continues "DEOR"
    # Let's check what each possible next GP value decrypts to
    print(f"  Cipher values at positions 43-60: {p19[43:61]}")
    
    for word in ["KEY", "POEM", "KOAN", "AND", "THE", "THAT", "FOR", "BUT", "WHICH", "WITHIN", "SACRED"]:
        gp = text_to_gp(word)
        keys = [(gp[j] - p19[43+j]) % 29 for j in range(len(gp)) if 43+j < len(p19)]
        key_letters = ''.join(IDX2LAT[v] for v in keys)
        print(f"  If '{word}' at pos 43: key would be {keys} = '{key_letters}'")
    
    # ============================================
    # PART 2: P18 keyword attack with P63 grid terms
    # ============================================
    print("\n" + "=" * 70)
    print("PART 2: P18 KEYWORD ATTACK (P63 Grid Terms)")
    print("=" * 70)
    
    # Load P18
    with open('LiberPrimus/pages/page_18/runes.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    p18 = [GP[ch] for ch in text if ch in GP]
    print(f"P18: {len(p18)} runes")
    
    # Keywords from P63 grid
    keywords = {
        'VOID': [1, 3, 10, 23],
        'AETHEREAL': [24, 18, 2, 18, 4, 18, 24, 20],
        'CARNAL': [5, 24, 4, 9, 24, 20],
        'ANALOG': [24, 9, 24, 20, 3, 6],
        'MOURNFUL': [19, 3, 1, 4, 9, 0, 1, 20],
        'OBSCURA': [3, 17, 15, 5, 1, 4, 24],
        'MOBIUS': [19, 3, 17, 10, 1, 15],
        'CABAL': [5, 24, 17, 24, 20],
        'SHADOWS': [15, 8, 24, 23, 3, 7, 15],
        'BUFFERS': [17, 1, 0, 0, 18, 4, 15],
        'SUOID': [15, 1, 3, 10, 23],
        'FORM': [0, 3, 4, 19],
        'DIVINITY': [23, 10, 1, 10, 9, 10, 16, 26],
        'FIRFUMFERENFE': [0, 10, 4, 0, 1, 19, 0, 18, 4, 18, 9, 0, 18],
        'YAHEOOPYJ': [26, 24, 8, 18, 3, 3, 13, 26, 11],
        # Number sequences from grid
        'NUM_ROW1': [272 % 29, 138 % 29, 131 % 29, 151 % 29],  # [11, 22, 15, 6]
        'NUM_ALL': [272 % 29, 138 % 29, 131 % 29, 151 % 29, 226 % 29, 245 % 29, 18],
        # Combinations
        'VOIDCARNAL': [1, 3, 10, 23, 5, 24, 4, 9, 24, 20],
        'AETHEREALCABAL': [24, 18, 2, 18, 4, 18, 24, 20, 5, 24, 17, 24, 20],
        'SHADOWSCABAL': [15, 8, 24, 23, 3, 7, 15, 5, 24, 17, 24, 20],
    }
    
    results = []
    for name, key in keywords.items():
        for mode in ['SUB', 'ADD', 'BEAU']:
            # Standard Vigenère
            dec = []
            for i in range(len(p18)):
                k = key[i % len(key)]
                if mode == 'SUB':
                    dec.append((p18[i] - k) % 29)
                elif mode == 'ADD':
                    dec.append((p18[i] + k) % 29)
                else:
                    dec.append((k - p18[i]) % 29)
            ioc = calc_ioc(dec)
            text = ''.join(IDX2LAT[v] for v in dec)
            score = count_english(text)
            results.append((ioc, score, f"{name}_{mode}", text[:80]))
            
            # F-skip variant
            dec_fs = []
            key_idx = 0
            for i in range(len(p18)):
                if p18[i] == 0:  # F-skip
                    dec_fs.append(0)
                else:
                    k = key[key_idx % len(key)]
                    if mode == 'SUB':
                        dec_fs.append((p18[i] - k) % 29)
                    elif mode == 'ADD':
                        dec_fs.append((p18[i] + k) % 29)
                    else:
                        dec_fs.append((k - p18[i]) % 29)
                    key_idx += 1
            ioc_fs = calc_ioc(dec_fs)
            text_fs = ''.join(IDX2LAT[v] for v in dec_fs)
            score_fs = count_english(text_fs)
            results.append((ioc_fs, score_fs, f"{name}_{mode}_fskip", text_fs[:80]))
    
    # ALSO test on P20
    print("\n--- Also testing keywords on P20 ---")
    with open('LiberPrimus/pages/page_20/runes.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    p20 = [GP[ch] for ch in text if ch in GP]
    
    p20_results = []
    for name, key in keywords.items():
        for mode in ['SUB', 'ADD', 'BEAU']:
            dec = []
            for i in range(len(p20)):
                k = key[i % len(key)]
                if mode == 'SUB':
                    dec.append((p20[i] - k) % 29)
                elif mode == 'ADD':
                    dec.append((p20[i] + k) % 29)
                else:
                    dec.append((k - p20[i]) % 29)
            ioc = calc_ioc(dec)
            text = ''.join(IDX2LAT[v] for v in dec)
            score = count_english(text)
            p20_results.append((ioc, score, f"P20_{name}_{mode}", text[:80]))
    
    # Print P18 results
    print("\n--- P18 TOP RESULTS (by IoC) ---")
    results.sort(key=lambda x: (-x[0], -x[1]))
    for ioc, score, label, text in results[:15]:
        print(f"  IoC={ioc:.4f} eng={score:3d} {label}")
        print(f"    {text[:70]}")
    
    print("\n--- P18 TOP RESULTS (by score) ---")
    results.sort(key=lambda x: (-x[1], -x[0]))
    for ioc, score, label, text in results[:15]:
        print(f"  IoC={ioc:.4f} eng={score:3d} {label}")
        print(f"    {text[:70]}")
    
    # Print P20 results
    print("\n--- P20 TOP RESULTS (by IoC) ---")
    p20_results.sort(key=lambda x: (-x[0], -x[1]))
    for ioc, score, label, text in p20_results[:10]:
        print(f"  IoC={ioc:.4f} eng={score:3d} {label}")
        print(f"    {text[:70]}")

if __name__ == '__main__':
    main()
