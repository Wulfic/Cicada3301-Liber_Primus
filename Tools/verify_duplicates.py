#!/usr/bin/env python3
"""
Verify P27/P44 Identity and Find All Duplicate/Related Pages
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

def load_page(page_num):
    path = f'LiberPrimus/pages/page_{page_num:02d}/runes.txt'
    if not os.path.exists(path):
        path = f'LiberPrimus/pages/page_{page_num}/runes.txt'
    if not os.path.exists(path):
        return None, None
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    vals = [GP[ch] for ch in raw if ch in GP]
    return raw, vals

def main():
    print("=" * 70)
    print("DUPLICATE PAGE DETECTION")
    print("=" * 70)
    
    pages = {}
    raw_pages = {}
    for p in range(17, 55):
        raw, vals = load_page(p)
        if vals:
            pages[p] = vals
            raw_pages[p] = raw
    
    # ============================================
    # Check P27 vs P44 in detail
    # ============================================
    print("\n--- P27 vs P44 ---")
    p27 = pages[27]
    p44 = pages[44]
    print(f"P27: {len(p27)} runes")
    print(f"P44: {len(p44)} runes")
    
    n = min(len(p27), len(p44))
    diffs = []
    for i in range(n):
        if p27[i] != p44[i]:
            diffs.append(i)
    print(f"Differences in first {n} positions: {len(diffs)}")
    if diffs:
        print(f"First diff at: {diffs[:10]}")
    else:
        print("*** P27 is an EXACT PREFIX of P44! ***")
    
    # Check raw text too
    raw27 = raw_pages[27].strip()
    raw44 = raw_pages[44].strip()
    print(f"\nRaw P27 length: {len(raw27)}")
    print(f"Raw P44 length: {len(raw44)}")
    print(f"P44 starts with P27? {raw44.startswith(raw27)}")
    
    # Find where they differ in raw text
    for i in range(min(len(raw27), len(raw44))):
        if raw27[i] != raw44[i]:
            print(f"First raw diff at position {i}: P27='{raw27[i]}' P44='{raw44[i]}'")
            print(f"  Context P27: ...{raw27[max(0,i-10):i+10]}...")
            print(f"  Context P44: ...{raw44[max(0,i-10):i+10]}...")
            break
    else:
        if len(raw27) < len(raw44):
            print(f"P27 raw is exact prefix of P44 raw!")
        else:
            print(f"P27 and P44 raw texts are IDENTICAL!")
    
    # ============================================
    # Systematic duplicate detection (all pairs)
    # ============================================
    print("\n" + "=" * 70)
    print("SYSTEMATIC DUPLICATE DETECTION")
    print("=" * 70)
    
    page_nums = sorted(pages.keys())
    for i in range(len(page_nums)):
        for j in range(i + 1, len(page_nums)):
            pi, pj = page_nums[i], page_nums[j]
            a, b = pages[pi], pages[pj]
            n = min(len(a), len(b))
            if n < 10:
                continue
            
            # Check how many positions match
            matches = sum(1 for k in range(n) if a[k] == b[k])
            match_pct = matches / n * 100
            
            if match_pct > 30:  # More than 30% match is notable
                print(f"  P{pi} vs P{pj}: {matches}/{n} = {match_pct:.1f}% match")
            
            # Also check with constant offset
            if match_pct < 10:  # Only check offset if not already matching
                for offset in range(1, 29):
                    shifted_matches = sum(1 for k in range(n) if (a[k] + offset) % 29 == b[k])
                    if shifted_matches / n > 0.5:
                        print(f"  P{pi}+{offset} vs P{pj}: {shifted_matches}/{n} = {shifted_matches/n*100:.1f}% match")
    
    # ============================================
    # Check if P27 is a KNOWN section of P44
    # ============================================
    print("\n--- Where does P27 appear in P44? ---")
    # Search for P27 as subsequence within P44
    best_start = -1
    best_matches = 0
    for start in range(len(p44) - len(p27) + 1):
        m = sum(1 for i in range(len(p27)) if p27[i] == p44[start + i])
        if m > best_matches:
            best_matches = m
            best_start = start
    print(f"Best alignment: start={best_start}, matches={best_matches}/{len(p27)} ({best_matches/len(p27)*100:.1f}%)")
    
    # Show P44's structure - is P27 at the beginning?
    if best_start == 0:
        print(f"P27 matches the BEGINNING of P44")
        print(f"P44 continues for {len(p44) - len(p27)} more runes after P27")
        
        # Show what comes after P27 in P44
        remaining = p44[len(p27):]
        rem_text = ''.join(IDX2LAT[v] for v in remaining[:50])
        print(f"P44 after P27 position: {rem_text}...")
    
    print("\n--- Rune frequency comparison ---")
    from collections import Counter
    freq27 = Counter(p27)
    freq44 = Counter(p44)
    print("  P27 top 5:", freq27.most_common(5))
    print("  P44 top 5:", freq44.most_common(5))

if __name__ == '__main__':
    main()
