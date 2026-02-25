#!/usr/bin/env python3
"""
Alberti Progressive Cipher + Interleave Attack
===============================================
1. Alberti: alphabet rotates cumulatively per-letter/per-space/per-punct
2. Interleave: extract every-nth rune as separate messages  
3. GP-prime feedback: key depends on ciphertext rune's prime value
4. Totient-feedback: key depends on totient of ciphertext rune's prime value
"""

import os, sys
from collections import Counter

RUNE_TO_SHIFT = {
    '\u16a0': 0, '\u16a2': 1, '\u16a6': 2, '\u16a9': 3, '\u16b1': 4,
    '\u16b3': 5, '\u16b7': 6, '\u16b9': 7, '\u16bb': 8, '\u16be': 9,
    '\u16c1': 10, '\u16c2': 11, '\u16c7': 12, '\u16c8': 13, '\u16c9': 14,
    '\u16cb': 15, '\u16cf': 16, '\u16d2': 17, '\u16d6': 18, '\u16d7': 19,
    '\u16da': 20, '\u16dd': 21, '\u16df': 22, '\u16de': 23, '\u16aa': 24,
    '\u16ab': 25, '\u16a3': 26, '\u16e1': 27, '\u16e0': 28, '\u16c4': 11
}

SHIFT_TO_GP_PRIME = {
    0:2, 1:3, 2:5, 3:7, 4:11, 5:13, 6:17, 7:19, 8:23, 9:29,
    10:31, 11:37, 12:41, 13:43, 14:47, 15:53, 16:59, 17:61,
    18:67, 19:71, 20:73, 21:79, 22:83, 23:89, 24:97, 25:101,
    26:103, 27:107, 28:109
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
             'WITHIN','DEEP','PAGE','DUTY','PILGRIM','SEEK','WARNING']
    for w in words: score += t.count(w) * len(w) * 5
    return score

def parse_chars_with_types(rune_text):
    """Parse rune text into (shift, type) pairs.
    type: 'l' = letter, 's' = separator, 'p' = punctuation."""
    result = []
    for ch in rune_text:
        if ch in RUNE_TO_SHIFT:
            result.append((RUNE_TO_SHIFT[ch], 'l'))
        elif ch in '-\u2022 ':
            result.append((None, 's'))
        elif ch in '.':
            result.append((None, 'p'))
    return result

def parse_shifts(rune_text):
    return [RUNE_TO_SHIFT[ch] for ch in rune_text if ch in RUNE_TO_SHIFT]

def load_page(pages_dir, p):
    path = os.path.join(pages_dir, f'page_{p:02d}', 'runes.txt')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return None

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    repo_dir = os.path.dirname(base_dir)
    pages_dir = os.path.join(repo_dir, 'LiberPrimus', 'pages')
    
    # Load pages with both raw text and shift arrays
    pages = {}
    for p in range(18, 55):
        rt = load_page(pages_dir, p)
        if rt:
            shifts = parse_shifts(rt)
            if len(shifts) > 20:
                pages[p] = {'text': rt, 'shifts': shifts, 'typed': parse_chars_with_types(rt)}
    
    print("=" * 80)
    print("ALBERTI PROGRESSIVE CIPHER ATTACK")
    print("Cumulative shift: per-letter, per-space, per-punctuation")
    print("=" * 80)
    
    # Test most promising pages first (largest for statistical reliability)
    target_pages = sorted(pages.keys(), key=lambda p: len(pages[p]['shifts']), reverse=True)[:10]
    
    all_hits = []
    
    for page_num in target_pages:
        pdata = pages[page_num]
        cipher = pdata['shifts']
        typed = pdata['typed']
        n = len(cipher)
        
        best_for_page = None
        
        # Brute force letter_step (0-28), sample space_step and punct_step
        for letter_step in range(29):
            for space_step in range(0, 29, 3):  # Sample every 3rd value
                for punct_step in range(0, 29, 7):  # Sample every 7th
                    for initial_shift in range(0, 29, 7):  # Sample initial shifts
                        # Apply Alberti cipher
                        shift = initial_shift
                        plain_idx = 0
                        plain = []
                        
                        for val, typ in typed:
                            if typ == 'l':
                                p = (val - shift) % 29
                                plain.append(p)
                                shift = (shift + letter_step) % 29
                            elif typ == 's':
                                shift = (shift + space_step) % 29
                            elif typ == 'p':
                                shift = (shift + punct_step) % 29
                        
                        if len(plain) != n:
                            continue
                        
                        ioc = calc_ioc(plain)
                        if ioc > 1.35:
                            text = decode(plain)
                            s = score_text(text)
                            if best_for_page is None or ioc > best_for_page[0]:
                                best_for_page = (ioc, s, letter_step, space_step, punct_step, initial_shift, text[:120])
                            all_hits.append((ioc, s, page_num, letter_step, space_step, punct_step, initial_shift))
        
        if best_for_page:
            ioc, s, ls, ss, ps, init, text = best_for_page
            print(f"  P{page_num} letter={ls} space={ss} punct={ps} init={init}: IoC={ioc:.3f} score={s}")
            print(f"    {text}")
        else:
            print(f"  P{page_num}: No Alberti hits")
    
    # Now try the Beaufort variant: (shift - val) % 29
    print("\n--- Alberti BEAUFORT mode ---")
    for page_num in target_pages[:5]:
        pdata = pages[page_num]
        cipher = pdata['shifts']
        typed = pdata['typed']
        n = len(cipher)
        
        best_for_page = None
        
        for letter_step in range(29):
            for space_step in range(0, 29, 3):
                for punct_step in range(0, 29, 7):
                    shift = 0
                    plain = []
                    
                    for val, typ in typed:
                        if typ == 'l':
                            p = (shift - val) % 29
                            plain.append(p)
                            shift = (shift + letter_step) % 29
                        elif typ == 's':
                            shift = (shift + space_step) % 29
                        elif typ == 'p':
                            shift = (shift + punct_step) % 29
                    
                    if len(plain) != n:
                        continue
                    
                    ioc = calc_ioc(plain)
                    if ioc > 1.35:
                        text = decode(plain)
                        s = score_text(text)
                        if best_for_page is None or ioc > best_for_page[0]:
                            best_for_page = (ioc, s, letter_step, space_step, punct_step, text[:120])
        
        if best_for_page:
            ioc, s, ls, ss, ps, text = best_for_page
            print(f"  P{page_num} letter={ls} space={ss} punct={ps}: IoC={ioc:.3f} score={s}")
            print(f"    {text}")
    
    # ==================== INTERLEAVE ATTACK ====================
    print("\n" + "=" * 80)
    print("INTERLEAVE ATTACK")
    print("Extract every nth rune starting at different offsets")
    print("Check if sub-streams have higher IoC than full text")
    print("=" * 80)
    
    for page_num in target_pages[:10]:
        cipher = pages[page_num]['shifts']
        n = len(cipher)
        
        for num_streams in [2, 3, 5, 7, 11, 13]:
            if num_streams > n // 5: continue
            
            streams = [[] for _ in range(num_streams)]
            for i, s in enumerate(cipher):
                streams[i % num_streams].append(s)
            
            iocs = [calc_ioc(s) for s in streams if len(s) >= 10]
            avg_ioc = sum(iocs) / len(iocs) if iocs else 0
            max_ioc = max(iocs) if iocs else 0
            
            if max_ioc > 1.25:
                print(f"  P{page_num} {num_streams}-interleave: avg_IoC={avg_ioc:.3f} max_IoC={max_ioc:.3f}")
                for j, (stream, ioc) in enumerate(zip(streams, iocs)):
                    if ioc > 1.2:
                        text = decode(stream)
                        print(f"    Stream {j}: IoC={ioc:.3f} len={len(stream)} -> {text[:80]}")
    
    # ==================== GP-PRIME FEEDBACK ====================
    print("\n" + "=" * 80)
    print("GP-PRIME FEEDBACK CIPHER")
    print("Key[i] depends on GP prime value of cipher rune")
    print("=" * 80)
    
    for page_num in target_pages[:5]:
        cipher = pages[page_num]['shifts']
        n = len(cipher)
        
        # Variant 1: key[i] = GP_prime[cipher[i]] mod 29 
        plain1 = [(cipher[i] - SHIFT_TO_GP_PRIME[cipher[i]] % 29) % 29 for i in range(n)]
        ioc1 = calc_ioc(plain1)
        if ioc1 > 1.2:
            text = decode(plain1)
            s = score_text(text)
            print(f"  P{page_num} prime_feedback sub: IoC={ioc1:.3f} score={s}")
            print(f"    {text[:120]}")
        
        # Variant 2: key[i] = totient(GP_prime[cipher[i]]) mod 29
        plain2 = [(cipher[i] - (SHIFT_TO_GP_PRIME[cipher[i]] - 1) % 29) % 29 for i in range(n)]
        ioc2 = calc_ioc(plain2)
        if ioc2 > 1.2:
            text = decode(plain2)
            s = score_text(text)
            print(f"  P{page_num} totient_feedback sub: IoC={ioc2:.3f} score={s}")
            print(f"    {text[:120]}")
        
        # Variant 3: key[i] = GP_prime[cipher[i-1]] mod 29 (delayed feedback)
        plain3 = [(cipher[0] - 0) % 29]
        for i in range(1, n):
            k = SHIFT_TO_GP_PRIME[cipher[i-1]] % 29
            plain3.append((cipher[i] - k) % 29)
        ioc3 = calc_ioc(plain3)
        if ioc3 > 1.2:
            text = decode(plain3)
            s = score_text(text)
            print(f"  P{page_num} delayed_prime_feedback: IoC={ioc3:.3f} score={s}")
            print(f"    {text[:120]}")
        
        # Variant 4: Cumulative prime sum
        cum_prime = 0
        plain4 = []
        for i in range(n):
            plain4.append((cipher[i] - cum_prime % 29) % 29)
            cum_prime += SHIFT_TO_GP_PRIME[cipher[i]]
        ioc4 = calc_ioc(plain4)
        if ioc4 > 1.2:
            text = decode(plain4)
            s = score_text(text)
            print(f"  P{page_num} cumulative_prime_sum: IoC={ioc4:.3f} score={s}")
            print(f"    {text[:120]}")
        
        # Variant 5: XOR with shifted GP prime
        for shift_val in range(29):
            plain5 = [(cipher[i] ^ (SHIFT_TO_GP_PRIME[cipher[i]] + shift_val)) % 29 for i in range(n)]
            ioc5 = calc_ioc(plain5)
            if ioc5 > 1.3:
                text = decode(plain5)
                s = score_text(text)
                print(f"  P{page_num} xor_prime+{shift_val}: IoC={ioc5:.3f} score={s}")
                print(f"    {text[:80]}")
    
    # ==================== GROMARK CIPHER ====================
    print("\n" + "=" * 80)
    print("GROMARK CIPHER")
    print("Running key generated from plaintext digits/values")
    print("key[n] = plain[n-k] for various feedback delays k")
    print("Plus initial primer from keyword")
    print("=" * 80)
    
    for page_num in target_pages[:5]:
        cipher = pages[page_num]['shifts']
        n = len(cipher)
        
        # For each possible initial key (primer) length and value
        for primer_len in [1, 2, 3]:
            for primer_total in range(29**primer_len) if primer_len <= 2 else range(0, 29**3, 29):
                primer = []
                val = primer_total
                for _ in range(primer_len):
                    primer.append(val % 29)
                    val //= 29
                
                for delay in [1, 2, 3]:
                    # Sub mode
                    plain = []
                    for i in range(n):
                        if i < primer_len:
                            k = primer[i]
                        else:
                            # Gromark: key comes from previous plaintext
                            k = plain[i - delay] if i >= delay else primer[i % primer_len]
                        p = (cipher[i] - k) % 29
                        plain.append(p)
                    
                    ioc = calc_ioc(plain)
                    if ioc > 1.4:
                        text = decode(plain)
                        s = score_text(text)
                        print(f"  P{page_num} gromark primer={primer} delay={delay}: IoC={ioc:.3f} score={s}")
                        print(f"    {text[:100]}")
    
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()
