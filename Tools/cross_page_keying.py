#!/usr/bin/env python3
"""
Cross-Page Keying Test
======================
Test if the raw rune values of one page serve as the running key for another.
Key hypothesis: Page 18's runes might be the key for Page 19.

Also test: P17→P18, P20→P19, P19→P20, etc.
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

P19_KEY = [24, 15, 2, 24, 4, 21, 11, 10, 20, 16, 9, 19, 26, 11, 7, 5, 11, 6, 27, 8, 22, 25, 21, 16, 25, 0, 27, 9, 21, 7, 27, 15, 21, 9, 3, 16, 5, 22, 18, 4, 5, 18, 23]

def load_page(page_num):
    import os
    path = f'LiberPrimus/pages/page_{page_num:02d}/runes.txt'
    if not os.path.exists(path):
        path = f'LiberPrimus/pages/page_{page_num}/runes.txt'
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    return [GP[ch] for ch in text if ch in GP]

def calc_ioc(vals):
    if len(vals) < 20: return 0
    counts = Counter(vals)
    n = len(vals)
    total = sum(c * (c - 1) for c in counts.values())
    return total / (n * (n - 1) / 29)

def count_english(text):
    words = {'THE':10,'AND':10,'FOR':10,'ARE':10,'BUT':10,'NOT':10,'YOU':10,'ALL':10,
             'ONE':10,'OUR':10,'HIS':10,'WHO':10,
             'THAT':20,'WITH':20,'HAVE':20,'THIS':20,'WILL':20,'YOUR':20,'FROM':20,
             'EACH':20,'WHEN':20,'THAN':20,'WHAT':20,'WERE':20,'SOME':20,
             'KNOW':20,'MIND':20,'MUST':20,'PATH':20,'SEEK':20,
             'THERE':30,'THEIR':30,'BEING':30,'WORLD':30,'TRUTH':30,
             'WITHIN':40,'SACRED':40,'WISDOM':40,'DIVINE':40,'PRIMES':40,'DIVINITY':60}
    score = 0
    for w, s in words.items():
        score += text.count(w) * s
    return score

def main():
    print("=" * 70)
    print("CROSS-PAGE KEYING TEST")
    print("=" * 70)
    
    # Load all relevant pages
    pages = {}
    for p in range(17, 55):
        data = load_page(p)
        if data:
            pages[p] = data
    print(f"Loaded {len(pages)} pages: {sorted(pages.keys())}")
    for p in sorted(pages.keys()):
        print(f"  P{p}: {len(pages[p])} runes")
    
    # ============================================
    # TEST 1: Does P18 rune values match P19 key?
    # ============================================
    print("\n" + "=" * 70)
    print("TEST 1: P18 runes vs P19 key")
    print("=" * 70)
    
    p18 = pages.get(18, [])
    p19 = pages.get(19, [])
    
    if p18 and p19:
        # Compare first 43 rune values of P18 against P19 key
        print(f"P18 first 43: {p18[:43]}")
        print(f"P19 key:      {P19_KEY}")
        
        matches = sum(1 for i in range(min(43, len(p18))) if p18[i] == P19_KEY[i])
        print(f"Exact matches: {matches}/43")
        
        # What about P18 reversed?
        p18_rev = list(reversed(p18))
        matches_rev = sum(1 for i in range(min(43, len(p18_rev))) if p18_rev[i] == P19_KEY[i])
        print(f"P18 reversed matches: {matches_rev}/43")
        
        # What about P18 with an offset?
        best_offset = (-1, 0)
        for offset in range(len(p18) - 43):
            m = sum(1 for i in range(43) if p18[offset + i] == P19_KEY[i])
            if m > best_offset[1]:
                best_offset = (offset, m)
        print(f"Best offset: {best_offset[0]} with {best_offset[1]} matches")
        
        # What about (P18[i] + constant) % 29?
        for const in range(29):
            shifted_p18 = [(v + const) % 29 for v in p18[:43]]
            m = sum(1 for i in range(43) if shifted_p18[i] == P19_KEY[i])
            if m > 5:
                print(f"  P18+{const}: {m}/43 matches")
    
    # ============================================
    # TEST 2: Cross-page keying (all combinations)
    # ============================================
    print("\n" + "=" * 70)
    print("TEST 2: Cross-page keying (ADD/SUB/BEAU)")
    print("=" * 70)
    
    results = []
    page_nums = sorted(pages.keys())
    
    for key_page in page_nums:
        for cipher_page in page_nums:
            if key_page == cipher_page:
                continue
            
            kdata = pages[key_page]
            cdata = pages[cipher_page]
            n = min(len(kdata), len(cdata))
            if n < 50:
                continue
            
            for mode in ['ADD', 'SUB', 'BEAU']:
                plain = []
                for i in range(n):
                    if mode == 'ADD':
                        plain.append((cdata[i] + kdata[i]) % 29)
                    elif mode == 'SUB':
                        plain.append((cdata[i] - kdata[i]) % 29)
                    else:
                        plain.append((kdata[i] - cdata[i]) % 29)
                
                ioc = calc_ioc(plain)
                text = ''.join(IDX2LAT[v] for v in plain)
                score = count_english(text)
                
                if ioc > 1.2 or score > 80:
                    results.append((ioc, score, f"P{cipher_page}_key_P{key_page}_{mode}", text[:80]))
    
    results.sort(key=lambda x: (-x[0], -x[1]))
    print(f"\nResults with IoC > 1.2 or score > 80:")
    for ioc, score, label, text in results[:20]:
        print(f"  IoC={ioc:.4f} eng={score:3d} {label}")
        print(f"    {text[:70]}")
    
    # ============================================
    # TEST 3: Concatenated pages as running key
    # ============================================
    print("\n" + "=" * 70)
    print("TEST 3: Concatenated pages as running key")
    print("=" * 70)
    
    # Concatenate all page rune values
    all_runes = []
    for p in page_nums:
        all_runes.extend(pages[p])
    print(f"Total concatenated runes: {len(all_runes)}")
    
    # Use this concatenation as key for individual pages
    results2 = []
    offset = 0
    for p in page_nums:
        n = len(pages[p])
        # Use runes of OTHER pages as key (skip this page's contribution)
        # Simple: use all_runes starting at an offset after this page
        key_start = offset + n  # Start after this page
        key = all_runes[key_start:key_start + n]
        if len(key) < n:
            key = all_runes[:n]  # Wrap around
        
        for mode in ['ADD', 'SUB', 'BEAU']:
            plain = []
            for i in range(min(n, len(key))):
                if mode == 'ADD':
                    plain.append((pages[p][i] + key[i]) % 29)
                elif mode == 'SUB':
                    plain.append((pages[p][i] - key[i]) % 29)
                else:
                    plain.append((key[i] - pages[p][i]) % 29)
            
            ioc = calc_ioc(plain)
            text = ''.join(IDX2LAT[v] for v in plain)
            score = count_english(text)
            
            if ioc > 1.15 or score > 60:
                results2.append((ioc, score, f"P{p}_{mode}_concat", text[:80]))
        
        offset += n
    
    results2.sort(key=lambda x: (-x[0], -x[1]))
    print(f"\nResults above threshold:")
    for ioc, score, label, text in results2[:15]:
        print(f"  IoC={ioc:.4f} eng={score:3d} {label}")
        print(f"    {text[:70]}")
    
    # ============================================
    # TEST 4: P18 plaintext as key for P19
    # ============================================
    print("\n" + "=" * 70)
    print("TEST 4: P18 claimed plaintext as P19 key")
    print("=" * 70)
    
    # P18 claimed plaintext (first 53 runes)
    p18_plain_text = "BEING OF ALL I WILL ASC THE OATH IS SWORN TO THE ONE WITHIN THE ABOVE THE WAY"
    # Convert to GP with digraphs
    p18_gp = []
    text_upper = p18_plain_text.upper()
    i = 0
    E2GP_local = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,'K':5,'L':20,'M':19,
        'N':9,'O':3,'P':13,'R':4,'S':15,'T':16,'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}
    while i < len(text_upper):
        if i + 1 < len(text_upper):
            di = text_upper[i:i+2]
            if di == 'TH': p18_gp.append(2); i += 2; continue
            elif di == 'NG': p18_gp.append(21); i += 2; continue
            elif di == 'OE': p18_gp.append(22); i += 2; continue
            elif di == 'AE': p18_gp.append(25); i += 2; continue
            elif di == 'IA': p18_gp.append(27); i += 2; continue
            elif di == 'EA': p18_gp.append(28); i += 2; continue
            elif di == 'EO': p18_gp.append(12); i += 2; continue
        ch = text_upper[i]
        if ch in E2GP_local:
            p18_gp.append(E2GP_local[ch])
        i += 1
    
    print(f"P18 claimed plaintext GP: {p18_gp[:43]}")
    print(f"P19 key:                  {P19_KEY}")
    
    m = sum(1 for i in range(min(43, len(p18_gp))) if p18_gp[i] == P19_KEY[i])
    print(f"Direct match: {m}/{min(43, len(p18_gp))}")
    
    # Try P18 plaintext shifted
    for shift in range(29):
        shifted = [(v + shift) % 29 for v in p18_gp[:43]]
        m = sum(1 for i in range(min(43, len(shifted))) if shifted[i] == P19_KEY[i])
        if m > 5:
            print(f"  P18_plain+{shift}: {m}/43 matches")
    
    # ============================================
    # TEST 5: What if P19 key = P17 key (YAHEOOPYJ) repeated/extended?
    # ============================================
    print("\n" + "=" * 70)
    print("TEST 5: P17 key YAHEOOPYJ relationship to P19 key")
    print("=" * 70)
    
    yaheoopyj = [26, 24, 8, 18, 3, 3, 13, 26, 11]  # Y-A-H-E-O-O-P-Y-J
    print(f"YAHEOOPYJ: {yaheoopyj}")
    
    # Check if P19 key is some transformation of YAHEOOPYJ repeated
    for shift in range(29):
        key_extended = [(yaheoopyj[i % len(yaheoopyj)] + shift) % 29 for i in range(43)]
        m = sum(1 for i in range(43) if key_extended[i] == P19_KEY[i])
        if m > 5:
            print(f"  YAHEOOPYJ+{shift} repeated: {m}/43 matches")
    
    # Check cumulative YAHEOOPYJ
    yah_cum = [sum(yaheoopyj[:i+1]) % 29 for i in range(43)]
    m = sum(1 for i in range(43) if yah_cum[i] == P19_KEY[i])
    print(f"  YAHEOOPYJ cumulative: {m}/43 matches")

if __name__ == '__main__':
    main()
