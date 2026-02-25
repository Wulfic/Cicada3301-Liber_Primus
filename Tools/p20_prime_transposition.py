#!/usr/bin/env python3
"""
P20 Prime Position + Transposition Attack
==========================================
P19 clue: "REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR [KEY]"

Focus on extracting prime-position runes and trying ALL transposition methods.
Also try using the Deor poem in various combination approaches.
"""
import sys, os, math, itertools
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

GP = {'\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
      '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
      '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
      '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
      '\u16A3':26,'\u16E1':27,'\u16E0':28}
IDX2LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i+2) == 0: return False
        i += 6
    return True

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

def columnar_untranspose(data, ncols):
    """Undo columnar transposition with ncols columns."""
    n = len(data)
    nrows = math.ceil(n / ncols)
    # Full columns have nrows elements, short columns have nrows-1
    full_cols = n % ncols if n % ncols != 0 else ncols
    
    result = [0] * n
    idx = 0
    for col in range(ncols):
        col_len = nrows if col < full_cols else nrows - 1
        for row in range(col_len):
            result[row * ncols + col] = data[idx]
            idx += 1
    return result

def rail_fence_decode(data, nrails):
    """Decode rail fence cipher."""
    n = len(data)
    # Build the zigzag pattern
    fence = [[None] * n for _ in range(nrails)]
    rail = 0
    direction = 1
    for i in range(n):
        fence[rail][i] = True
        rail += direction
        if rail == nrails - 1 or rail == 0:
            direction = -direction
    
    # Fill from data
    idx = 0
    for r in range(nrails):
        for c in range(n):
            if fence[r][c] is True:
                fence[r][c] = data[idx]
                idx += 1
    
    # Read in zigzag order
    result = []
    rail = 0
    direction = 1
    for i in range(n):
        result.append(fence[rail][i])
        rail += direction
        if rail == nrails - 1 or rail == 0:
            direction = -direction
    return result

def every_nth(data, n, start=0):
    """Read every nth element starting at start."""
    return [data[i] for i in range(start, len(data), n)]

def spiral_read(data, ncols):
    """Read data arranged in grid in spiral order."""
    n = len(data)
    nrows = math.ceil(n / ncols)
    # Place data in grid
    grid = []
    idx = 0
    for r in range(nrows):
        row = []
        for c in range(ncols):
            if idx < n:
                row.append(data[idx])
                idx += 1
            else:
                row.append(None)
        grid.append(row)
    
    # Spiral read
    result = []
    top, bottom, left, right = 0, nrows-1, 0, ncols-1
    while top <= bottom and left <= right:
        for c in range(left, right+1):
            if grid[top][c] is not None:
                result.append(grid[top][c])
        top += 1
        for r in range(top, bottom+1):
            if grid[r][right] is not None:
                result.append(grid[r][right])
        right -= 1
        if top <= bottom:
            for c in range(right, left-1, -1):
                if grid[bottom][c] is not None:
                    result.append(grid[bottom][c])
            bottom -= 1
        if left <= right:
            for r in range(bottom, top-1, -1):
                if grid[r][left] is not None:
                    result.append(grid[r][left])
            left += 1
    return result

def main():
    print("=" * 70)
    print("P20 PRIME POSITION + TRANSPOSITION ATTACK")
    print("=" * 70)
    
    # Load P20
    with open('LiberPrimus/pages/page_20/runes.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    p20 = [GP[ch] for ch in text if ch in GP]
    print(f"P20 total runes: {len(p20)}")
    
    # Extract prime positions (0-indexed and 1-indexed)
    prime_0 = [i for i in range(len(p20)) if is_prime(i)]
    prime_1 = [i-1 for i in range(1, len(p20)+1) if is_prime(i)]
    
    # Also extract composite (non-prime) positions
    comp_0 = [i for i in range(len(p20)) if not is_prime(i)]
    
    print(f"Prime positions (0-idx): {len(prime_0)}")
    print(f"Prime positions (1-idx): {len(prime_1)}")
    print(f"Composite positions: {len(comp_0)}")
    
    # Also separate by prime GP VALUES
    prime_val_pos = [i for i, v in enumerate(p20) if is_prime(v)]
    nonprime_val_pos = [i for i, v in enumerate(p20) if not is_prime(v)]
    print(f"Prime GP value runes: {len(prime_val_pos)}")
    print(f"Non-prime GP value runes: {len(nonprime_val_pos)}")
    
    results = []
    
    # Test each extraction
    for label, positions in [
        ("prime_0idx", prime_0),
        ("prime_1idx", prime_1),
        ("composite", comp_0),
        ("prime_val", prime_val_pos),
        ("nonprime_val", nonprime_val_pos),
    ]:
        stream = [p20[i] for i in positions]
        n = len(stream)
        raw_ioc = calc_ioc(stream)
        raw_text = ''.join(IDX2LAT[v] for v in stream)
        
        print(f"\n--- {label}: {n} runes, raw IoC={raw_ioc:.4f} ---")
        
        # Try Caesar shifts
        for shift in range(29):
            shifted = [(v + shift) % 29 for v in stream]
            ioc = calc_ioc(shifted)
            text = ''.join(IDX2LAT[v] for v in shifted)
            score = count_english(text)
            if score > 50:
                results.append((ioc, score, f"{label}_caesar{shift}", text[:80]))
        
        # Try columnar transposition
        for ncols in range(2, min(50, n//2)):
            try:
                untrans = columnar_untranspose(stream, ncols)
                text = ''.join(IDX2LAT[v] for v in untrans)
                ioc = calc_ioc(untrans)
                score = count_english(text)
                if score > 50 or ioc > 1.3:
                    results.append((ioc, score, f"{label}_col{ncols}", text[:80]))
                
                # Also try columnar + Caesar
                for shift in [1, 2, 3, 5, 7, 11, 13]:
                    shifted = [(v + shift) % 29 for v in untrans]
                    text = ''.join(IDX2LAT[v] for v in shifted)
                    score = count_english(text)
                    if score > 60:
                        results.append((calc_ioc(shifted), score, f"{label}_col{ncols}_shift{shift}", text[:80]))
            except:
                pass
        
        # Try rail fence
        for nrails in range(2, min(15, n//2)):
            try:
                decoded = rail_fence_decode(stream, nrails)
                text = ''.join(IDX2LAT[v] for v in decoded)
                ioc = calc_ioc(decoded)
                score = count_english(text)
                if score > 50 or ioc > 1.3:
                    results.append((ioc, score, f"{label}_rail{nrails}", text[:80]))
            except:
                pass
        
        # Try every-nth reading
        for step in range(2, min(20, n//3)):
            for start in range(step):
                reread = every_nth(stream, step, start)
                if len(reread) > 20:
                    text = ''.join(IDX2LAT[v] for v in reread)
                    score = count_english(text)
                    if score > 30:
                        results.append((calc_ioc(reread), score, f"{label}_every{step}_start{start}", text[:80]))
        
        # Try diagonal reading
        for ncols in [11, 13, 17, 19, 23, 29, 41, 47, 53, 83]:
            if ncols >= n:
                continue
            nrows = math.ceil(n / ncols)
            # Read by diagonals
            diag = []
            for d in range(nrows + ncols - 1):
                for r in range(nrows):
                    c = d - r
                    if 0 <= c < ncols:
                        idx = r * ncols + c
                        if idx < n:
                            diag.append(stream[idx])
            if len(diag) > 20:
                text = ''.join(IDX2LAT[v] for v in diag)
                score = count_english(text)
                if score > 50:
                    results.append((calc_ioc(diag), score, f"{label}_diag{ncols}", text[:80]))
        
        # Try spiral read
        for ncols in [7, 11, 13, 17, 19, 23, 47]:
            if ncols >= n:
                continue
            try:
                spiral = spiral_read(stream, ncols)
                text = ''.join(IDX2LAT[v] for v in spiral)
                score = count_english(text)
                if score > 50:
                    results.append((calc_ioc(spiral), score, f"{label}_spiral{ncols}", text[:80]))
            except:
                pass
    
    # ============================================
    # TARGETED: 2x83 transposition on prime stream (from old analysis)
    # ============================================
    print("\n--- TARGETED: 2x83 and nearby transpositions ---")
    for label, positions in [("prime_0idx", prime_0), ("prime_1idx", prime_1)]:
        stream = [p20[i] for i in positions]
        n = len(stream)
        for ncols in [2, 83, n//2]:
            if ncols < 2 or ncols >= n:
                continue
            # Standard columnar
            try:
                untrans = columnar_untranspose(stream, ncols)
                text = ''.join(IDX2LAT[v] for v in untrans)
                ioc = calc_ioc(untrans)
                score = count_english(text)
                print(f"  {label} col{ncols}: IoC={ioc:.4f} score={score} {text[:60]}")
                if score > 30:
                    results.append((ioc, score, f"TARGET_{label}_col{ncols}", text[:80]))
            except:
                pass
            
            # Row-by-row vs column-by-column reading
            nrows = math.ceil(n / ncols)
            # Read columns first
            col_first = []
            for c in range(ncols):
                for r in range(nrows):
                    idx = r * ncols + c
                    if idx < n:
                        col_first.append(stream[idx])
            text = ''.join(IDX2LAT[v] for v in col_first)
            ioc = calc_ioc(col_first)
            score = count_english(text)
            print(f"  {label} col_first_{ncols}x{nrows}: IoC={ioc:.4f} score={score} {text[:60]}")
            if score > 30:
                results.append((ioc, score, f"TARGET_{label}_colfirst{ncols}", text[:80]))
    
    # ============================================
    # RESULTS
    # ============================================
    print("\n" + "=" * 70)
    print("TOP RESULTS (sorted by score)")
    print("=" * 70)
    results.sort(key=lambda x: (-x[1], -x[0]))
    seen = set()
    for ioc, score, label, text in results[:30]:
        key = (score, text[:40])
        if key not in seen:
            seen.add(key)
            print(f"  IoC={ioc:.4f} Score={score:4d} {label}")
            print(f"    {text}")

if __name__ == '__main__':
    main()
