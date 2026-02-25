"""
CLEAN SYSTEMATIC CRYPTANALYSIS - v2
Excludes small pages (< 100 runes) from affine check.
Focus on: P19 plaintext, periodic IoC, Kasiski, frequency.
"""
import os, sys, math
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

def periodic_ioc(values, period, alpha=29):
    subs = [[] for _ in range(period)]
    for i, v in enumerate(values):
        subs[i % period].append(v)
    iocs = [ioc(sub, alpha) for sub in subs if len(sub) >= 2]
    return sum(iocs) / len(iocs) if iocs else 0

def kasiski(values, ngram_len=3, top=10):
    positions = {}
    for i in range(len(values) - ngram_len + 1):
        key = tuple(values[i:i+ngram_len])
        if key not in positions:
            positions[key] = []
        positions[key].append(i)
    spacings = []
    for key, pos_list in positions.items():
        if len(pos_list) >= 2:
            for i in range(len(pos_list)):
                for j in range(i+1, len(pos_list)):
                    spacings.append(pos_list[j] - pos_list[i])
    factor_counts = Counter()
    for s in spacings:
        for f in range(2, min(s+1, 41)):
            if s % f == 0:
                factor_counts[f] += 1
    return factor_counts.most_common(top)

# === P19 PLAINTEXT ===
print("=" * 70)
print("P19 PLAINTEXT")
print("=" * 70)
p19 = load_page(19)
p19_key = [24,15,2,24,4,21,11,10,20,16,9,19,26,11,7,5,11,6,27,8,22,25,21,16,25,0,27,9,21,7,27,15,21,9,3,16,5,22,18,4,5,18,23]
for mode in ['ADD','SUB','BEAU']:
    if mode == 'ADD':
        plain = [(p19[i] + p19_key[i]) % 29 for i in range(43)]
    elif mode == 'SUB':
        plain = [(p19[i] - p19_key[i]) % 29 for i in range(43)]
    else:
        plain = [(p19_key[i] - p19[i]) % 29 for i in range(43)]
    print(f"  {mode}: {to_eng(plain)}")

# Also try: what if the key IS the plaintext? (i.e. plain=key)
print(f"  KEY as text: {to_eng(p19_key)}")
print(f"  P19 raw first 43: {to_eng(p19[:43])}")

# === LOAD PAGES ===
pages = {}
for pg in range(17, 75):
    data = load_page(pg)
    if data and len(data) > 0:
        pages[pg] = data

# === PAGE INVENTORY ===
print(f"\n{'='*70}")
print("PAGE INVENTORY")
print(f"{'='*70}")
for pg in sorted(pages):
    v = pages[pg]
    f_count = sum(1 for x in v if x == 0)
    print(f"  P{pg:02d}: {len(v):5d} runes  IoC={ioc(v):.4f}  F-count={f_count:3d}  non-F={len(v)-f_count}")

# === PERIODIC IoC ===
print(f"\n{'='*70}")
print("PERIODIC IoC - TOP 5 PERIODS PER PAGE (pages > 100 runes)")
print(f"{'='*70}")
for pg in sorted(pages):
    v = pages[pg]
    if len(v) < 100: continue
    pics = [(p, periodic_ioc(v, p)) for p in range(1, min(41, len(v)//4))]
    pics.sort(key=lambda x: -x[1])
    marker = " *** SIGNAL ***" if pics[0][1] > 1.3 else ""
    print(f"P{pg:02d} ({len(v):4d}):{marker}")
    for period, pic in pics[:5]:
        print(f"  p={period:2d}: {pic:.4f} {'|'*int(pic*10)}")

# === KASISKI ===
print(f"\n{'='*70}")
print("KASISKI EXAMINATION (top factor frequencies)")
print(f"{'='*70}")
for pg in sorted(pages):
    v = pages[pg]
    if len(v) < 100: continue
    kas = kasiski(v, 3, 5)
    if kas:
        top3 = [(f, c) for f, c in kas[:3]]
        print(f"P{pg:02d}: {top3}")

# === FREQUENCY FLATNESS ===
print(f"\n{'='*70}")
print("FREQUENCY FLATNESS")
print(f"{'='*70}")
for pg in sorted(pages):
    v = pages[pg]
    if len(v) < 50: continue
    counts = Counter(v)
    freqs = [counts.get(i, 0)/len(v) for i in range(29)]
    max_f, min_f = max(freqs), min(freqs)
    chi2 = sum((counts.get(i,0) - len(v)/29)**2 / (len(v)/29) for i in range(29))
    chi2_norm = chi2 / len(v) * 100
    label = "FLAT" if chi2_norm < 5 else ("MODERATE" if chi2_norm < 15 else "PEAKED")
    print(f"  P{pg:02d}: chi2n={chi2_norm:5.2f} max={max_f*100:.1f}% min={min_f*100:.1f}% [{label}]")

# === AFFINE CIPHER CHECK (pages > 200 runes only) ===
print(f"\n{'='*70}")
print("AFFINE CIPHER CHECK (pages > 200 runes)")
print(f"{'='*70}")
for pg in sorted(pages):
    v = pages[pg]
    if len(v) < 200: continue
    found = False
    for mult in range(1, 29):
        if math.gcd(mult, 29) != 1: continue
        for add in range(29):
            transformed = [(x * mult + add) % 29 for x in v]
            pic = ioc(transformed)
            if pic > 1.5:
                print(f"  P{pg:02d}: mult={mult} add={add}: IoC={pic:.4f} | {to_eng(transformed)[:40]}")
                found = True
    if not found:
        pass  # silent

# === BIGRAM IoC ===
print(f"\n{'='*70}")
print("BIGRAM IoC (pages > 100 runes)")
print(f"{'='*70}")
for pg in sorted(pages):
    v = pages[pg]
    if len(v) < 100: continue
    bigrams = [v[i]*29+v[i+1] for i in range(0, len(v)-1, 2)]
    bic = ioc(bigrams, alpha=29*29)
    if bic > 1.15:
        print(f"  P{pg:02d}: Bigram IoC = {bic:.4f}")

# === ODD/EVEN SPLIT ===
print(f"\n{'='*70}")
print("ODD/EVEN POSITION SPLIT IoC (pages > 100 runes)")
print(f"{'='*70}")
for pg in sorted(pages):
    v = pages[pg]
    if len(v) < 100: continue
    even = [v[i] for i in range(0, len(v), 2)]
    odd = [v[i] for i in range(1, len(v), 2)]
    e_ioc, o_ioc = ioc(even), ioc(odd)
    if max(e_ioc, o_ioc) > 1.2:
        print(f"  P{pg:02d}: even={e_ioc:.4f}  odd={o_ioc:.4f}")

# === SPECIAL: Check if P27 = prefix of P44 ===
print(f"\n{'='*70}")
print("SPECIAL CHECKS")
print(f"{'='*70}")
if 27 in pages and 44 in pages:
    p27, p44 = pages[27], pages[44]
    match = sum(1 for i in range(min(len(p27), len(p44))) if p27[i] == p44[i])
    print(f"P27 vs P44 first {len(p27)}: {match}/{len(p27)} match")
    if match == len(p27):
        print("  P27 IS an exact prefix of P44!")
        # Check the P44 remainder
        remainder = p44[len(p27):]
        print(f"  P44 remainder: {len(remainder)} runes, IoC={ioc(remainder):.4f}")
        # Maybe the remainder has different properties
        for period in [1,2,3,5,7,29]:
            pic = periodic_ioc(remainder, period)
            print(f"    Period {period}: IoC={pic:.4f}")

# === Check F-rune positions (are they periodic/structural?) ===
print(f"\nF-rune position analysis (top pages):")
for pg in [20, 25, 32, 40, 44, 50]:
    if pg not in pages: continue
    v = pages[pg]
    f_pos = [i for i, x in enumerate(v) if x == 0]
    if len(f_pos) < 2: continue
    gaps = [f_pos[i+1]-f_pos[i] for i in range(len(f_pos)-1)]
    avg_gap = sum(gaps)/len(gaps) if gaps else 0
    gap_counter = Counter(gaps)
    print(f"  P{pg:02d}: {len(f_pos)} F-runes, avg gap={avg_gap:.1f}, top gaps: {gap_counter.most_common(5)}")

# === Check pages with IoC significantly above 1.0 ===
print(f"\nPages with raw IoC > 1.05:")
for pg in sorted(pages):
    v = pages[pg]
    if ioc(v) > 1.05:
        print(f"  P{pg:02d}: IoC={ioc(v):.4f} ({len(v)} runes)")

print(f"\n{'='*70}")
print("DONE")
print(f"{'='*70}")
