"""Full IoC survey of all unsolved pages (18-54) + cross-page analysis"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import Counter
import os

GP = {'\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
      '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
      '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
      '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
      '\u16A3':26,'\u16E1':27,'\u16E0':28}
IDX = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

def ioc(data):
    if len(data) < 2: return 0
    c = Counter(data)
    n = len(data)
    return sum(v*(v-1) for v in c.values()) / (n*(n-1)) * 29

def load(p):
    rf = 'LiberPrimus/pages/page_%02d/runes.txt' % p
    if not os.path.exists(rf): return []
    with open(rf, 'r', encoding='utf-8') as f:
        return [GP[c] for c in f.read() if c in GP]

def chi_flat(data, mod=29):
    """Chi-squared test against uniform distribution"""
    n = len(data)
    if n == 0: return 0
    c = Counter(data)
    expected = n / mod
    return sum((c.get(i,0) - expected)**2 / expected for i in range(mod))

# Survey all pages 18-54
print("=" * 80)
print("COMPREHENSIVE IoC SURVEY - PAGES 18-54")
print("=" * 80)
print()
print("%-6s %6s %8s %8s %8s %12s %s" % ("Page", "Runes", "IoC*29", "Chi_flat", "F_count", "F_percent", "Best_period"))

all_pages = {}
for pg in range(18, 55):
    data = load(pg)
    if not data:
        print("P%02d: NO DATA" % pg)
        continue
    all_pages[pg] = data
    ic = ioc(data)
    chi = chi_flat(data)
    f_count = data.count(0)
    f_pct = f_count / len(data) * 100

    # Find best period
    best_per = 0
    best_per_ioc = 0
    for per in range(2, min(50, len(data)//3)):
        cols = [[] for _ in range(per)]
        for i, v in enumerate(data):
            cols[i % per].append(v)
        avg = sum(ioc(c) for c in cols) / per
        if avg > best_per_ioc:
            best_per_ioc = avg
            best_per = per

    mark = ''
    if ic > 1.3: mark = ' *** HIGH IoC'
    elif ic > 1.1: mark = ' ** Moderate IoC'
    print("P%02d   %6d %8.3f %8.1f %8d %11.1f%% per=%d(%.2f)%s" % (
        pg, len(data), ic, chi, f_count, f_pct, best_per, best_per_ioc, mark))

# Check which pages have near-uniform distribution (strong cipher)
# vs elevated IoC (weaker cipher or partial solution)
print()
print("=" * 80)
print("PAGES GROUPED BY IoC")
print("=" * 80)
flat = [(pg, ioc(d)) for pg, d in all_pages.items() if ioc(d) < 1.1]
moderate = [(pg, ioc(d)) for pg, d in all_pages.items() if 1.1 <= ioc(d) < 1.3]
elevated = [(pg, ioc(d)) for pg, d in all_pages.items() if ioc(d) >= 1.3]

print("\nFLAT (IoC < 1.1) - Strong cipher, polyalphabetic:")
for pg, ic in flat:
    print("  P%02d: IoC=%.3f (%d runes)" % (pg, ic, len(all_pages[pg])))

print("\nMODERATE (1.1 <= IoC < 1.3) - Partial structure:")
for pg, ic in moderate:
    print("  P%02d: IoC=%.3f (%d runes)" % (pg, ic, len(all_pages[pg])))

print("\nELEVATED (IoC >= 1.3) - Weaker cipher or cleartext:")
for pg, ic in elevated:
    print("  P%02d: IoC=%.3f (%d runes)" % (pg, ic, len(all_pages[pg])))

# F-rune (value 0) analysis
print()
print("=" * 80)
print("F RUNE ANALYSIS")
print("=" * 80)
print("Expected F percentage for uniform = %.1f%%" % (100/29))
for pg, data in sorted(all_pages.items()):
    f_pct = data.count(0) / len(data) * 100
    if abs(f_pct - 100/29) > 2:
        print("  P%02d: F=%.1f%% (%d/%d) - %s" % (
            pg, f_pct, data.count(0), len(data),
            'ELEVATED' if f_pct > 100/29 + 2 else 'DEPLETED'))

# Cross-page overlap detection
print()
print("=" * 80)
print("CROSS-PAGE RUNE OVERLAPS (>50 rune prefix match)")
print("=" * 80)
pages_list = sorted(all_pages.items())
for i in range(len(pages_list)):
    pa, da = pages_list[i]
    for j in range(i+1, len(pages_list)):
        pb, db = pages_list[j]
        # Check if da is prefix of db or vice versa
        minlen = min(len(da), len(db))
        match = 0
        for k in range(minlen):
            if da[k] == db[k]:
                match += 1
            else:
                break
        if match > 50:
            print("  P%02d[:] == P%02d[:%d] (%d rune prefix match)" % (pa, pb, match, match))

# Combined text analysis
print()
print("=" * 80)
print("COMBINED ANALYSIS - ALL PAGES 21-54")
print("=" * 80)
combined = []
for pg in range(21, 55):
    if pg in all_pages:
        combined.extend(all_pages[pg])
print("Total runes: %d" % len(combined))
print("Combined IoC: %.3f" % ioc(combined))

# Check periodic IoC of combined text
print("\nCombined periodic IoC:")
for per in range(2, 100):
    cols = [[] for _ in range(per)]
    for i, v in enumerate(combined):
        cols[i % per].append(v)
    avg = sum(ioc(c) for c in cols) / per
    if avg > 1.05:
        print("  Period %d: %.3f %s" % (per, avg, '***' if avg > 1.2 else '**' if avg > 1.1 else ''))

print("\nDone.")
