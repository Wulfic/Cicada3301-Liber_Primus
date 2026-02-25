"""
COMPREHENSIVE ATTACK on pages 17-54 using approaches NOT yet tried with correct GP mapping:
1. Autokey Vigenère (plaintext extends keyword)
2. Kasiski analysis (repeated bigrams/trigrams → key length)
3. Stride analysis (read every Nth rune, check IoC)
4. Totient cipher with wide offset range
5. All pages concatenated as single ciphertext
6. All grid keywords + F-skip brute force
"""
import os, sys
from collections import Counter
from math import gcd

RUNE_TO_INDEX = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,'\u16C7':12,'\u16C8':13,'\u16C9':14,
    '\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,'\u16D7':19,'\u16DA':20,'\u16DD':21,
    '\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,'\u16A3':26,'\u16E1':27,'\u16E0':28
}
GP = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
      'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
BASE = r"c:\Users\tyler\Repos\Cicada3301\LiberPrimus\pages"

def load_page(pn):
    path = os.path.join(BASE, f"page_{pn:02d}", "runes.txt")
    if not os.path.exists(path): return []
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    rune_text = ''.join(line for line in lines if not (line.strip() and line.strip()[0].isascii() and line.strip()[0].isalpha()))
    return [RUNE_TO_INDEX[c] for c in rune_text if c in RUNE_TO_INDEX]

def keyword_to_gp(word):
    result = []; i = 0; word = word.upper()
    while i < len(word):
        if i+1 < len(word):
            di = word[i:i+2]
            dmap = {'TH':2,'EO':12,'NG':21,'OE':22,'AE':25,'IA':27,'IO':27,'EA':28}
            if di in dmap: result.append(dmap[di]); i += 2; continue
        smap = {'F':0,'U':1,'V':1,'O':3,'R':4,'C':5,'K':5,'G':6,'W':7,'H':8,'N':9,
                'I':10,'J':11,'P':13,'X':14,'S':15,'Z':15,'T':16,'B':17,'E':18,'M':19,
                'L':20,'D':23,'A':24,'Y':26}
        if word[i] in smap: result.append(smap[word[i]])
        i += 1
    return result

def ioc29(vals):
    if len(vals) < 2: return 0
    ct = Counter(vals); n = len(vals)
    return 29 * sum(c*(c-1) for c in ct.values()) / (n*(n-1))

def text(vals): return ''.join(GP[v] for v in vals)

def score_english(vals):
    t = text(vals).upper()
    score = 0
    for w in ['THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','HER','WAS',
              'ONE','OUR','OUT','HIS','HAS','ITS','WHO','OWN','SAY','SHE','LET']:
        score += t.count(w) * 3
    for w in ['OF','TO','IN','IS','IT','AN','OR','IF','NO','SO','BY','AS','AT','WE','BE']:
        score += t.count(w) * 2
    for w in ['THAT','THIS','WITH','FROM','THEY','HAVE','BEEN','EACH','WILL',
              'YOUR','WHAT','WHEN','THEM','SOME','INTO','THAN','ONLY','SELF',
              'FIND','MAKE','JUST','KNOW','TRUTH','SACRED','WISDOM']:
        score += t.count(w) * 5
    return score

# ===== LOAD ALL UNSOLVED PAGES =====
UNSOLVED = list(range(17, 55)) + [56, 57, 71, 73]
pages = {}
for pn in range(0, 75):
    data = load_page(pn)
    if data: pages[pn] = data

print("=" * 80)
print("SECTION 1: RAW CIPHERTEXT IoC FOR ALL PAGES (correct GP mapping)")
print("=" * 80)
for pn in sorted(pages.keys()):
    d = pages[pn]
    ic = ioc29(d)
    status = "✓ SOLVED" if pn in [0,1,2,3,4,5,6,7,8,9,10,13,14,15,16,55,56,57,58,59,60,61,62,63,64,67,68,73,74] else "UNSOLVED"
    freq_top3 = Counter(d).most_common(3)
    top3_str = ', '.join(f'{GP[v]}:{c}' for v,c in freq_top3)
    print(f"  P{pn:02d}: {len(d):4d} runes, IoC={ic:.4f} [{status}] top: {top3_str}")

# ===== SECTION 2: KASISKI EXAMINATION =====
print(f"\n{'='*80}")
print("SECTION 2: KASISKI ANALYSIS (repeated trigrams → key length)")
print("=" * 80)
for pn in range(17, 55):
    if pn not in pages: continue
    d = pages[pn]
    if len(d) < 50: continue
    # Find repeated trigrams
    trigrams = {}
    for i in range(len(d) - 2):
        t3 = (d[i], d[i+1], d[i+2])
        if t3 in trigrams:
            trigrams[t3].append(i)
        else:
            trigrams[t3] = [i]
    
    # Compute distances between repeats
    distances = []
    for t3, positions in trigrams.items():
        if len(positions) >= 2:
            for j in range(1, len(positions)):
                distances.append(positions[j] - positions[0])
    
    if distances:
        # GCD of all distances suggests key length
        g = distances[0]
        for dist in distances[1:]:
            g = gcd(g, dist)
        
        # Factor frequency
        factors = Counter()
        for dist in distances:
            for f in range(2, min(30, dist+1)):
                if dist % f == 0:
                    factors[f] += 1
        
        if factors:
            top_factors = factors.most_common(5)
            factor_str = ', '.join(f'{f}:{c}' for f,c in top_factors)
            print(f"  P{pn:02d}: {len(distances):3d} repeat distances, GCD={g}, top factors: {factor_str}")

# ===== SECTION 3: STRIDE ANALYSIS =====
print(f"\n{'='*80}")
print("SECTION 3: STRIDE ANALYSIS (every Nth rune, check IoC)")
print("=" * 80)
for pn in [20, 25, 32, 40, 44, 50, 57, 17]:  # Largest pages first
    if pn not in pages: continue
    d = pages[pn]
    print(f"\n  P{pn:02d} ({len(d)} runes):")
    for stride in range(2, 30):
        if stride > len(d) // 5: break
        best_ic = 0
        for offset in range(stride):
            sub = d[offset::stride]
            if len(sub) >= 20:
                ic = ioc29(sub)
                if ic > best_ic: best_ic = ic
        if best_ic > 1.3:
            print(f"    stride={stride}: best IoC={best_ic:.4f}")

# ===== SECTION 4: AUTOKEY VIGENÈRE =====
print(f"\n{'='*80}")
print("SECTION 4: AUTOKEY VIGENERE (keyword seeds, plaintext extends key)")
print("=" * 80)

def autokey_decrypt(cipher, seed, mode='SUB'):
    """Autokey: key = seed + plaintext[0] + plaintext[1] + ..."""
    key = list(seed)
    result = []
    for i, c in enumerate(cipher):
        ki = i
        if ki < len(key):
            k = key[ki]
        else:
            break  # Should not happen if we extend properly
        if mode == 'SUB': p = (c - k) % 29
        elif mode == 'ADD': p = (c + k) % 29
        elif mode == 'BEAU': p = (k - c) % 29
        result.append(p)
        key.append(p)  # Extend key with plaintext
    return result

keywords = ['DIVINITY','FIRFUMFERENFE','YAHEOOPYJ','VOID','AETHEREAL','CARNAL',
            'ANALOG','MOURNFUL','CABAL','OBSCURA','MOBIUS','SHADOWS','BUFFERS',
            'SUOID','TRUTH','SACRED','WISDOM','INSTAR','EMERGE','PILGRIM',
            'CIRCUMFERENCE','CONSUMPTION','PRESERVATION','ADHERENCE',
            'PRIMES','TOTIENT','WELCOME','REALITY','CICADA','KOAN']

for pn in range(17, 55):
    if pn not in pages: continue
    d = pages[pn]
    best_ic = 0; best_kw = ''; best_mode = ''; best_text = ''
    
    for kw in keywords:
        key = keyword_to_gp(kw)
        if not key: continue
        for mode in ['SUB', 'ADD', 'BEAU']:
            dec = autokey_decrypt(d, key, mode)
            ic = ioc29(dec)
            if ic > best_ic:
                best_ic = ic; best_kw = kw; best_mode = mode; best_text = text(dec)[:80]
    
    if best_ic > 1.2:
        print(f"  P{pn:02d}: IoC={best_ic:.4f} key={best_kw} mode={best_mode}")
        print(f"    {best_text}")

# ===== SECTION 5: TOTIENT WITH EXTENDED OFFSETS =====
print(f"\n{'='*80}")
print("SECTION 5: TOTIENT φ(prime) WITH EXTENDED OFFSETS (0 to 500)")
print("=" * 80)

def primes_up_to(n):
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n+1, i): sieve[j] = False
    return [i for i in range(2, n+1) if sieve[i]]

PRIMES = primes_up_to(50000)

def totient_decrypt(cipher, offset, mode='SUB'):
    result = []
    ki = 0
    for c in cipher:
        pi = ki + offset
        if pi >= len(PRIMES): break
        k = (PRIMES[pi] - 1) % 29  # φ(prime) = prime - 1
        if mode == 'SUB': p = (c - k) % 29
        elif mode == 'ADD': p = (c + k) % 29
        elif mode == 'BEAU': p = (k - c) % 29
        result.append(p)
        ki += 1
    return result

for pn in range(17, 55):
    if pn not in pages: continue
    d = pages[pn]
    best_ic = 0; best_off = 0; best_mode = ''; best_text = ''
    
    for offset in range(0, 500):
        for mode in ['SUB', 'ADD', 'BEAU']:
            dec = totient_decrypt(d, offset, mode)
            if len(dec) < len(d): continue
            ic = ioc29(dec)
            if ic > best_ic:
                best_ic = ic; best_off = offset; best_mode = mode; best_text = text(dec)[:80]
    
    if best_ic > 1.2:
        print(f"  P{pn:02d}: IoC={best_ic:.4f} offset={best_off} mode={best_mode}")
        print(f"    {best_text}")

# ===== SECTION 6: ALL PAGES CONCATENATED =====
print(f"\n{'='*80}")
print("SECTION 6: ALL UNSOLVED PAGES CONCATENATED - Stride & Kasiski")
print("=" * 80)

concat = []
for pn in range(17, 55):
    if pn in pages:
        concat.extend(pages[pn])
print(f"Total concatenated runes (P17-P54): {len(concat)}")
print(f"Concatenated IoC: {ioc29(concat):.4f}")

# Stride analysis on concat
for stride in range(2, 50):
    best_ic = 0
    for offset in range(stride):
        sub = concat[offset::stride]
        if len(sub) >= 50:
            ic = ioc29(sub)
            if ic > best_ic: best_ic = ic
    if best_ic > 1.15:
        print(f"  stride={stride}: best IoC={best_ic:.4f}")

# ===== SECTION 7: F-SKIP KEYWORD BRUTE FORCE (small F count pages) =====
print(f"\n{'='*80}")
print("SECTION 7: F-SKIP BRUTE FORCE (pages with ≤ 12 F runes)")
print("=" * 80)

def decrypt_fskip_set(cipher, key, mode, skip_positions):
    result = []; ki = 0; kl = len(key)
    for i, c in enumerate(cipher):
        if i in skip_positions:
            result.append(0); continue
        k = key[ki % kl]
        if mode == 'SUB': p = (c - k) % 29
        elif mode == 'ADD': p = (c + k) % 29
        elif mode == 'BEAU': p = (k - c) % 29
        result.append(p)
        ki += 1
    return result

for pn in range(17, 55):
    if pn not in pages: continue
    d = pages[pn]
    f_positions = [i for i, c in enumerate(d) if c == 0]
    n_f = len(f_positions)
    if n_f > 12: continue  # Skip pages with too many F positions
    
    best_overall_ic = 0
    best_overall = None
    
    for kw in keywords:
        key = keyword_to_gp(kw)
        if not key: continue
        for mode in ['SUB', 'ADD', 'BEAU']:
            for mask in range(2**n_f):
                skip = set()
                for bi, pos in enumerate(f_positions):
                    if mask & (1 << bi): skip.add(pos)
                dec = decrypt_fskip_set(d, key, mode, skip)
                ic = ioc29(dec)
                if ic > best_overall_ic:
                    best_overall_ic = ic
                    best_overall = (kw, mode, mask, text(dec)[:80])
    
    if best_overall_ic > 1.3 and best_overall:
        kw, mode, mask, t = best_overall
        lits = [f_positions[i] for i in range(n_f) if mask & (1 << i)]
        print(f"  P{pn:02d}: IoC={best_overall_ic:.4f} key={kw} mode={mode} fskip@{lits}")
        print(f"    {t}")

print(f"\n{'='*80}")
print("ATTACK COMPLETE")
print("=" * 80)
