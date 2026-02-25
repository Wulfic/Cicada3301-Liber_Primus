"""
FOCUSED ANALYSIS:
1. P68: IoC=1.85, 611 runes - is it cleartext/simple substitution?
2. Cross-page differential analysis (superimposition attack)
3. P27-P44 relationship investigation
4. OE frequency profile from solved pages for key recovery reference
"""
import os
from collections import Counter

os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

def to_eng(vals): return ''.join(LATIN[v] for v in vals)
def ioc(values, alpha=29):
    n = len(values)
    if n < 2: return 0
    counts = Counter(values)
    return sum(c*(c-1) for c in counts.values()) / (n*(n-1)) * alpha

def load_page(pg):
    for p in [f'LiberPrimus/pages/page_{pg:02d}/runes.txt', f'LiberPrimus/pages/page_{pg}/runes.txt']:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                return [GP[c] for c in f.read() if c in GP]
    return None

# ================================================================
# P68 INVESTIGATION
# ================================================================
print("="*70)
print("P68 INVESTIGATION (IoC=1.85, 611 runes)")
print("="*70)

p68 = load_page(68)
if p68:
    print(f"Length: {len(p68)}")
    print(f"IoC: {ioc(p68):.4f}")
    
    # Frequency distribution
    counts = Counter(p68)
    print("\nFrequency distribution:")
    for v in sorted(counts, key=lambda x: -counts[x]):
        bar = '#' * int(counts[v] / len(p68) * 500)
        print(f"  {LATIN[v]:3s} ({v:2d}): {counts[v]:3d} ({counts[v]/len(p68)*100:5.1f}%) {bar}")
    
    # Missing values
    missing = [v for v in range(29) if v not in counts]
    print(f"\nMissing GP values: {[LATIN[v] for v in missing]}")
    
    # Raw text (first 200 chars)
    print(f"\nRaw text: {to_eng(p68[:200])}...")
    print(f"Last 100: ...{to_eng(p68[-100:])}")
    
    # F-rune (0) positions
    f_pos = [i for i, v in enumerate(p68) if v == 0]
    print(f"\nF-runes: {len(f_pos)} at positions {f_pos}")
    
    # Word analysis (F-delimited)
    words = []
    current = []
    for v in p68:
        if v == 0:
            if current: words.append(current)
            current = []
        else: current.append(v)
    if current: words.append(current)
    print(f"Words (F-delimited): {len(words)}")
    for i, w in enumerate(words[:20]):
        print(f"  Word {i}: {to_eng(w)} ({len(w)} runes)")
    
    # Check ALL 29 Caesar shifts for readable text
    print("\n29 Caesar shifts (first 50 chars):")
    for shift in range(29):
        shifted = [(v + shift) % 29 for v in p68]
        ic = ioc(shifted)
        print(f"  Shift {shift:2d}: {to_eng(shifted[:50])}...")
    
    # Atbash
    atbash = [(28 - v) % 29 for v in p68]
    print(f"\nAtbash: {to_eng(atbash[:80])}...")
    
    # Atbash + shifts 
    for s in range(29):
        at_shift = [(28 - v + s) % 29 for v in p68]
        print(f"  Atbash+{s:2d}: {to_eng(at_shift[:50])}...")

# ================================================================
# CROSS-PAGE DIFFERENTIAL ANALYSIS
# ================================================================
print("\n" + "="*70)
print("CROSS-PAGE DIFFERENTIAL ANALYSIS")
print("="*70)

# Load ~270-rune pages
target_pages = {}
for pg in [19,21,24,26,28,29,30,31,34,35,41,42,43,45,46,47,48]:
    data = load_page(pg)
    if data:
        target_pages[pg] = data

print(f"Loaded {len(target_pages)} ~270-rune pages")

# For each pair, compute the difference and check its IoC
# If two pages use the same cipher with different short keys,
# the difference should have periodic structure
print("\nPairwise differences (min length, IoC of diff):")
best_pairs = []
for pg_a in sorted(target_pages):
    for pg_b in sorted(target_pages):
        if pg_b <= pg_a: continue
        va, vb = target_pages[pg_a], target_pages[pg_b]
        min_len = min(len(va), len(vb))
        diff = [(va[i] - vb[i]) % 29 for i in range(min_len)]
        ic_diff = ioc(diff)
        
        if ic_diff > 1.15:  # Above random
            best_pairs.append((pg_a, pg_b, ic_diff, min_len))

best_pairs.sort(key=lambda x: -x[2])
print(f"\nTop 20 pairs with IoC(diff) > 1.15:")
for pg_a, pg_b, ic, mn in best_pairs[:20]:
    print(f"  P{pg_a:02d} - P{pg_b:02d}: IoC(diff)={ic:.4f}  (len={mn})")

# For the best pair, check periodic IoC of the difference
if best_pairs:
    pg_a, pg_b, _, _ = best_pairs[0]
    va, vb = target_pages[pg_a], target_pages[pg_b]
    min_len = min(len(va), len(vb))
    diff = [(va[i] - vb[i]) % 29 for i in range(min_len)]
    
    print(f"\nBest pair P{pg_a:02d}-P{pg_b:02d} periodic IoC:")
    for period in range(1, 30):
        subs = [[] for _ in range(period)]
        for i, v in enumerate(diff):
            subs[i % period].append(v)
        avg_ioc = sum(ioc(s) for s in subs if len(s) > 1) / max(1, sum(1 for s in subs if len(s) > 1))
        if avg_ioc > 1.3:
            print(f"  period={period}: IoC={avg_ioc:.4f}")

# Also check: do any pages differ by a CONSTANT?
print("\nConstant-difference check (all pairs):")
for pg_a in sorted(target_pages):
    for pg_b in sorted(target_pages):
        if pg_b <= pg_a: continue
        va, vb = target_pages[pg_a], target_pages[pg_b]
        min_len = min(len(va), len(vb))
        diff = [(va[i] - vb[i]) % 29 for i in range(min_len)]
        counts = Counter(diff)
        most_common_val, most_common_count = counts.most_common(1)[0]
        if most_common_count / min_len > 0.1:  # > 10% same value
            print(f"  P{pg_a:02d}-P{pg_b:02d}: most common diff={most_common_val} ({LATIN[most_common_val]}) {most_common_count}/{min_len} = {most_common_count/min_len*100:.1f}%")

# ================================================================
# LARGE PAGE CROSS-ANALYSIS
# ================================================================  
print("\n" + "="*70)
print("LARGE PAGE CROSS-ANALYSIS")
print("="*70)

# Load large pages
large_pages = {}
for pg in [17, 20, 25, 32, 40, 44, 50, 57]:
    data = load_page(pg)
    if data:
        large_pages[pg] = data

print(f"Large pages: {[(pg, len(v)) for pg, v in sorted(large_pages.items())]}")

# Check pairwise differences
print("\nPairwise difference IoC (large pages):")
for pg_a in sorted(large_pages):
    for pg_b in sorted(large_pages):
        if pg_b <= pg_a: continue
        va, vb = large_pages[pg_a], large_pages[pg_b]
        min_len = min(len(va), len(vb))
        diff = [(va[i] - vb[i]) % 29 for i in range(min_len)]
        ic_diff = ioc(diff)
        if ic_diff > 1.05:
            print(f"  P{pg_a:02d} - P{pg_b:02d}: IoC(diff)={ic_diff:.4f}  (len={min_len})")

# ================================================================
# P27-P44 SPECIAL INVESTIGATION
# ================================================================
print("\n" + "="*70)
print("P27-P44 SPECIAL INVESTIGATION")
print("="*70)

p27 = load_page(27)
p44 = load_page(44)
if p27 and p44:
    print(f"P27: {len(p27)} runes")
    print(f"P44: {len(p44)} runes")
    print(f"P27 = P44[:234]: {p27 == p44[:234]}")
    
    remainder = p44[234:]
    print(f"\nP44 remainder (234 onwards): {len(remainder)} runes")
    print(f"Remainder IoC: {ioc(remainder):.4f}")
    print(f"Remainder text: {to_eng(remainder[:100])}...")
    
    # Check if P27 appears elsewhere in P44
    for start in range(1, len(p44) - len(p27) + 1):
        match = sum(1 for i in range(len(p27)) if p44[start + i] == p27[i])
        if match > len(p27) * 0.5:
            print(f"  High match at offset {start}: {match}/{len(p27)}")
    
    # Check if P27 appears in other large pages
    for pg_name, data in large_pages.items():
        if pg_name == 44: continue
        for start in range(len(data) - len(p27) + 1):
            match = sum(1 for i in range(len(p27)) if data[start + i] == p27[i])
            if match > len(p27) * 0.3:
                print(f"  P27 vs P{pg_name}[{start}:]: {match}/{len(p27)} match")

# ================================================================
# OE FREQUENCY PROFILE FROM SOLVED PAGES
# ================================================================
print("\n" + "="*70)
print("OE FREQUENCY PROFILE FROM SOLVED PLAINTEXT")
print("="*70)

# Load known solved plaintext
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':14}

# Manually enter known solved plaintext from memory (key phrases)
solved_texts = [
    "AN INSTRUCTION A COMMAND WITHIN AMASS YOUR SELF YOUR ENERGIES AND BREATHE INTUS",
    "IT IS ONLY THROUGH GOING WITHIN THAT WE MAY EMERGE",
    "WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS",
    "SOME WISDOM THE PRIMES ARE SACRED",
    "AN INSTAR IS A LARVAL STAGE",
    "CONSUMPTION SHALL HAVE BEAUTY AND ADHERENCE SHALL HAVE CONSUMPTION",
    "THE LOSS OF DIVINITY THE CIRCUMFERENCE CONSUMPTION HAVE BEAUTY",
    "LIKE THE INSTAR WE TOO MUST SHED OUR THAT WHICH BY NOW FEELS LIKE OUR VERY BODY",
    "FROM BIRTH HAVE WE NOT BEEN SHARK FIN THROUGH THE GREAT OCEAN",
    "WITHIN YOU IS THE DIVINE A GOLDEN HOLY LIGHT",
    "THE UNINITIATED WOULD BELIEVE THAT WE HAD LOST OUR MINDS",
    "PARABLE THE WISE MAN LET A FOOL BELIEVE HE WAS A FOOL",
    "A WORD OF WISDOM PERHAPS OF A TRUTH GAZE UNTIL THE TRUTH REVEALS",
]

all_gp = []
for text in solved_texts:
    for ch in text.upper():
        if ch in ENG2GP:
            all_gp.append(ENG2GP[ch])

total = len(all_gp)
print(f"Total solved GP values: {total}")
freq = Counter(all_gp)
print("\nOE/English frequency profile (from solved LP):")
for v in sorted(range(29), key=lambda x: -freq.get(x, 0)):
    f = freq.get(v, 0) / total * 100
    bar = '#' * int(f * 5)
    print(f"  {LATIN[v]:3s} ({v:2d}): {f:5.1f}% {bar}")

# Top 5 most common
top5 = freq.most_common(5)
print(f"\nTop 5: {[(LATIN[v], f'{c/total*100:.1f}%') for v, c in top5]}")

print("\n" + "="*70)
print("DONE")
print("="*70)
