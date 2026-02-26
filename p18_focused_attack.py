#!/usr/bin/env python3
"""
P18 Focused Attack — Test k=20 and key chaining P18→P19.
Also brute force small periods and test known keywords.
"""
import os, sys
from collections import Counter
from itertools import product
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ─── CORRECT GP MAPPING ───
GP_RUNES = list("ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛂᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ")
GP_RUNE_TO_IDX = {r: i for i, r in enumerate(GP_RUNES)}
GP_RUNE_TO_IDX['\u16C4'] = 11
MOD = 29
GP_LETTERS = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
              'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

# Expected English-GP distribution (no-digraph: each letter→1 rune)
ENG_FREQ = {'A':8.167,'B':1.492,'C':2.782,'D':4.253,'E':12.702,'F':2.228,
    'G':2.015,'H':6.094,'I':6.966,'J':0.153,'K':0.772,'L':4.025,
    'M':2.406,'N':6.749,'O':7.507,'P':1.929,'Q':0.095,'R':5.987,
    'S':6.327,'T':9.056,'U':2.758,'V':0.978,'W':2.360,'X':0.150,
    'Y':1.974,'Z':0.074}
ENG_TO_GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,
    'I':10,'J':11,'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,
    'R':4,'S':15,'T':16,'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}
GP_EXP = [0.0]*29
for lt, fr in ENG_FREQ.items():
    GP_EXP[ENG_TO_GP[lt]] += fr
s = sum(GP_EXP)
GP_EXP = [f/s for f in GP_EXP]

COMMON_WORDS = {"THE","AND","FOR","ARE","NOT","YOU","ALL","HER","WAS","ONE",
    "OUR","OUT","HAS","HIS","HOW","MAN","NEW","NOW","OLD","SEE","WAY","WHO",
    "DID","GET","HIM","LET","SAY","SHE","TOO","BUT","CAN","HAD",
    "ITS","MAY","TWO","WILL","EACH","MAKE","LIKE","SOME","THEM","THAN",
    "BEEN","HAVE","FROM","INTO","WITH","THAT","THIS","WHAT","WHEN","THEY",
    "COME","MADE","FIND","MORE","ONLY","JUST","OVER","SUCH","ALSO","VERY",
    "AFTER","BEING","GREAT","THEIR","THESE","THOSE","UNDER",
    "ABOUT","COULD","EVERY","FIRST","SHALL","THERE","THINK","WHERE",
    "WHICH","WHILE","WORLD","WOULD","MIGHT","NEVER","STILL","TRUTH",
    "KNOW","MUST","SELF","SOUL","MIND","LIFE","DEAD","FEAR","FIRE","FORM",
    "GOOD","LORD","KING","WISE","WORD","WORK","PATH","RUNE","DIVINITY",
    "WITHIN","FOLLOW","PILGRIM","WISDOM","CONSUMPTION","CIRCUMFERENCE",
    "PRIMES","NUMBERS","REARRANGING","SHOW","DEOR"}

def load_runes(page_num):
    f = f"c:\\Users\\tyler\\Repos\\Cicada3301\\LiberPrimus\\pages\\page_{page_num}\\runes.txt"
    if not os.path.exists(f): return None
    with open(f, 'r', encoding='utf-8') as fh:
        txt = fh.read()
    return [GP_RUNE_TO_IDX[c] for c in txt if c in GP_RUNE_TO_IDX]

def ioc(v):
    if len(v)<2: return 0
    c=Counter(v); n=len(v)
    return sum(x*(x-1) for x in c.values())/(n*(n-1))*MOD

def chi2(counts, exp, n):
    return sum((counts.get(i,0)-exp[i]*n)**2/(exp[i]*n+1e-9) for i in range(MOD))

def to_text(idx):
    return ''.join(GP_LETTERS[i] for i in idx)

def word_score(text):
    sc=0; tu=text.upper()
    for w in COMMON_WORDS:
        st=0
        while True:
            p=tu.find(w,st)
            if p<0: break
            sc+=len(w); st=p+1
    return sc

P19_KEY = [24,15,2,24,4,21,11,10,20,16,9,19,26,11,7,5,11,6,27,8,22,25,21,16,25,0,27,9,21,7,27,15,21,9,3,16,5,22,18,4,5,18,23,21,1,10,24]

p18 = load_runes(18)
p19 = load_runes(19)
print(f"P18: {len(p18)} runes")
print(f"P19: {len(p19)} runes")
print(f"P18 first 50 indices: {p18[:50]}")

# ═══════════════════════════════════════════════════════════════════════
# PHASE 1: KEY CHAINING P18→P19
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("PHASE 1: KEY CHAINING — Does P18 plaintext = P19 key?")
print("="*80)

# If P18_plain[j] = P19_key[j], then the P18 key can be derived:
# SUB mode: P18_plain = (P18_cipher - key) mod 29 → key[j] = (P18_cipher[j] - P19_key[j]) mod 29
# ADD mode: P18_plain = (P18_cipher + key) mod 29 → key[j] = (P19_key[j] - P18_cipher[j]) mod 29
# BEAUFORT: P18_plain = (key - P18_cipher) mod 29 → key[j] = (P19_key[j] + P18_cipher[j]) mod 29

for mode_name, key_fn in [("SUB", lambda c,p: (c-p)%MOD), 
                           ("ADD", lambda c,p: (p-c)%MOD),
                           ("BEAUFORT", lambda c,p: (p+c)%MOD)]:
    derived = [key_fn(p18[j], P19_KEY[j]) for j in range(47)]
    print(f"\n  {mode_name} mode — Derived P18 key (first 47):")
    print(f"    {derived}")
    print(f"    As text: {to_text(derived)}")
    print(f"    IoC of key: {ioc(derived):.3f}")
    
    # Check if key is periodic
    print(f"    Periodicity check:")
    for period in range(1, 25):
        matches = sum(1 for i in range(period, 47) if derived[i] == derived[i % period])
        total = 47 - period
        ratio = matches / total if total > 0 else 0
        if ratio > 0.5 or period <= 5:
            print(f"      k={period}: {matches}/{total} matches = {ratio:.1%}")
    
    # Check if key has patterns
    diffs = [(derived[i+1] - derived[i]) % MOD for i in range(46)]
    print(f"    First differences: {diffs[:20]}...")
    
    # Try using this derived key as periodic key for ALL of P18
    for test_period in range(1, 48):
        # Check if derived key is consistent at this period
        slots = [[] for _ in range(test_period)]
        for j in range(47):
            slots[j % test_period].append(derived[j])
        consistent = all(len(set(sl))==1 for sl in slots if sl)
        if consistent and test_period <= 47:
            key = [sl[0] for sl in slots]
            # Decrypt full P18
            if mode_name == "SUB":
                plain = [(p18[i] - key[i%len(key)])%MOD for i in range(len(p18))]
            elif mode_name == "ADD":
                plain = [(p18[i] + key[i%len(key)])%MOD for i in range(len(p18))]
            else:
                plain = [(key[i%len(key)] - p18[i])%MOD for i in range(len(p18))]
            txt = to_text(plain)
            ic = ioc(plain)
            ws = word_score(txt)
            print(f"\n    *** CONSISTENT at period {test_period}! ***")
            print(f"        Key: {key}")
            print(f"        IoC: {ic:.3f}  WordScore: {ws}")
            print(f"        Text: {txt[:150]}")
            
            # If P18 plaintext used as full P19 key
            if len(plain) >= len(p19):
                p19_plain_sub = [(p19[i]-plain[i])%MOD for i in range(len(p19))]
                p19_plain_add = [(p19[i]+plain[i])%MOD for i in range(len(p19))]
                for nm, pp in [("P19_SUB",p19_plain_sub),("P19_ADD",p19_plain_add)]:
                    t = to_text(pp[:80])
                    ic2 = ioc(pp)
                    ws2 = word_score(to_text(pp))
                    print(f"        {nm}: IoC={ic2:.3f} ws={ws2} Text={t[:100]}")
    
    # Even if not periodic, try using the 47-value derived key on full P18
    # with cycling
    if mode_name == "SUB":
        full_plain = [(p18[i] - derived[i%47])%MOD for i in range(len(p18))]
    elif mode_name == "ADD":
        full_plain = [(p18[i] + derived[i%47])%MOD for i in range(len(p18))]
    else:
        full_plain = [(derived[i%47] - p18[i])%MOD for i in range(len(p18))]
    txt = to_text(full_plain)
    ic = ioc(full_plain)
    ws = word_score(txt)
    print(f"\n    Using derived key cycled at period 47:")
    print(f"        IoC: {ic:.3f}  WordScore: {ws}")
    print(f"        Text: {txt[:150]}")
    # Verify first 47 match P19 key
    match47 = sum(1 for i in range(47) if full_plain[i] == P19_KEY[i])
    print(f"        First 47 match P19 key: {match47}/47")

# ═══════════════════════════════════════════════════════════════════════
# PHASE 2: Vigenère attack at k=20 (the best period with enough runes/column)
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("PHASE 2: Vigenère frequency analysis at k=20")
print("="*80)

for test_k in [10, 13, 20, 26, 52, 5, 4]:
    if test_k >= len(p18)//2:
        continue
    cols = [[] for _ in range(test_k)]
    for i,v in enumerate(p18):
        cols[i%test_k].append(v)
    
    n_per_col = len(p18) // test_k
    
    print(f"\n  k={test_k} ({n_per_col} runes/col):")
    
    # Per-column IoC
    col_iocs = [ioc(c) for c in cols]
    avg_col_ioc = sum(col_iocs)/len(col_iocs)
    print(f"    Avg column IoC: {avg_col_ioc:.3f}")
    print(f"    Col IoCs: {[f'{x:.2f}' for x in col_iocs]}")
    
    # Frequency analysis: for each column, find best shift
    for mode_name in ["SUB", "ADD", "BEAUFORT"]:
        key = []
        for col in cols:
            best_s, best_chi = 0, float('inf')
            for s in range(MOD):
                if mode_name == "SUB":
                    shifted = [(v-s)%MOD for v in col]
                elif mode_name == "ADD":
                    shifted = [(v+s)%MOD for v in col]
                else:
                    shifted = [(s-v)%MOD for v in col]
                counts = Counter(shifted)
                ch = chi2(counts, GP_EXP, len(col))
                if ch < best_chi:
                    best_chi = ch; best_s = s
            key.append(best_s)
        
        if mode_name == "SUB":
            plain = [(p18[i]-key[i%test_k])%MOD for i in range(len(p18))]
        elif mode_name == "ADD":
            plain = [(p18[i]+key[i%test_k])%MOD for i in range(len(p18))]
        else:
            plain = [(key[i%test_k]-p18[i])%MOD for i in range(len(p18))]
        
        txt = to_text(plain)
        ic = ioc(plain)
        ws = word_score(txt)
        
        if ic > 1.15 or ws > 20:
            print(f"    {mode_name}: IoC={ic:.3f} ws={ws}")
            print(f"      Key: {key}")
            print(f"      KeyText: {to_text(key)}")
            print(f"      Text: {txt[:120]}")

# ═══════════════════════════════════════════════════════════════════════
# PHASE 3: Known keywords with F-skip
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("PHASE 3: Known keywords (including F-skip)")
print("="*80)

YAHEOOPYJ = [26,24,8,18,3,3,13,26,11]
DIVINITY = [23,10,1,10,9,10,16,26]
VOID = [1,3,10,23]
AETHEREAL = [24,18,16,8,18,4,18,24,20]
CARNAL = [5,24,4,9,24,20]
SUOID = [15,1,3,10,23]
MOBIUS = [19,3,17,10,1,15]

P19_KEY_TEXT = P19_KEY  # 47 values

keywords = {
    "YAHEOOPYJ": YAHEOOPYJ,
    "DIVINITY": DIVINITY, 
    "VOID": VOID,
    "AETHEREAL": AETHEREAL,
    "CARNAL": CARNAL,
    "SUOID": SUOID,
    "MOBIUS": MOBIUS,
    "P19_KEY_47": P19_KEY,
}

# Also try YAHEOOPYJ with various shifts
for sh in range(1, 29):
    keywords[f"YAHEOOPYJ+{sh}"] = [(v+sh)%MOD for v in YAHEOOPYJ]

def fskip_decrypt(cipher, key, mode):
    """F-skip decryption: when cipher rune = F(0), skip key advance."""
    plain = []
    ki = 0
    for c in cipher:
        if c == 0:
            plain.append(0)  # F stays F
        else:
            k = key[ki % len(key)]
            if mode == "SUB":
                plain.append((c - k) % MOD)
            elif mode == "ADD":
                plain.append((c + k) % MOD)
            else:
                plain.append((k - c) % MOD)
            ki += 1
    return plain

best_kw = []
for name, key in keywords.items():
    for mode in ["SUB", "ADD", "BEAUFORT"]:
        for use_fskip in [False, True]:
            if use_fskip:
                plain = fskip_decrypt(p18, key, mode)
            else:
                if mode == "SUB":
                    plain = [(p18[i]-key[i%len(key)])%MOD for i in range(len(p18))]
                elif mode == "ADD":
                    plain = [(p18[i]+key[i%len(key)])%MOD for i in range(len(p18))]
                else:
                    plain = [(key[i%len(key)]-p18[i])%MOD for i in range(len(p18))]
            
            txt = to_text(plain)
            ic = ioc(plain)
            ws = word_score(txt)
            ident = f"{name}/{mode}{'_fskip' if use_fskip else ''}"
            best_kw.append((ic, ws, ident, txt[:80]))

best_kw.sort(key=lambda x: (-x[0], -x[1]))
print("Top 15 keyword results:")
for ic, ws, nm, txt in best_kw[:15]:
    print(f"  {nm}: IoC={ic:.3f} ws={ws}  Text={txt[:60]}")

# ═══════════════════════════════════════════════════════════════════════
# PHASE 4: Brute force k=2,3,4,5 (both regular and F-skip)
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("PHASE 4: Brute force small periods (k=2,3,4,5)")
print("="*80)

for k in [2, 3, 4]:  # Skip k=5 (29^5 too slow)
    print(f"\n  k={k}: {29**k} combos...")
    best = []
    for keyvals in product(range(MOD), repeat=k):
        key = list(keyvals)
        for mode in ["SUB", "ADD"]:
            if mode == "SUB":
                plain = [(p18[i]-key[i%k])%MOD for i in range(len(p18))]
            else:
                plain = [(p18[i]+key[i%k])%MOD for i in range(len(p18))]
            ic = ioc(plain)
            if ic > 1.35:
                txt = to_text(plain)
                ws = word_score(txt)
                if ws > 30 or ic > 1.5:
                    best.append((ic, ws, key, mode, txt[:60]))
    
    best.sort(key=lambda x: (-x[0], -x[1]))
    if best:
        print(f"    Found {len(best)} candidates")
        for ic, ws, key, mode, txt in best[:5]:
            print(f"    {key} {mode}: IoC={ic:.3f} ws={ws}  {txt}")
    else:
        print(f"    No candidates above threshold")

# ═══════════════════════════════════════════════════════════════════════
# PHASE 5: Autokey with various seeds  
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("PHASE 5: Autokey cipher")
print("="*80)

seeds = {"YAHEOOPYJ": YAHEOOPYJ, "DIVINITY": DIVINITY, "VOID": VOID,
         "AETHEREAL": AETHEREAL, "P19KEY": P19_KEY}

for name, seed in seeds.items():
    for mode in ["PT_SUB", "PT_ADD", "CT_SUB", "CT_ADD"]:
        plain = []
        for i, c in enumerate(p18):
            if i < len(seed):
                k = seed[i]
            else:
                if mode.startswith("PT"):
                    k = plain[i - len(seed)]
                else:
                    k = p18[i - len(seed)]
            if mode.endswith("SUB"):
                plain.append((c - k) % MOD)
            else:
                plain.append((c + k) % MOD)
        
        txt = to_text(plain)
        ic = ioc(plain)
        ws = word_score(txt)
        if ic > 1.15 or ws > 30:
            print(f"  {name}/{mode}: IoC={ic:.3f} ws={ws}  {txt[:80]}")

# ═══════════════════════════════════════════════════════════════════════
# PHASE 6: Key chaining with prime-based modifications
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("PHASE 6: Rearranging primes as key")
print("="*80)

GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]

# P19 says "rearranging the primes numbers will show a path to the deor"
# What if we use primes mod 29 as key?
primes_mod29 = [p % MOD for p in GP_PRIMES]
print(f"  GP primes mod 29: {primes_mod29}")

# What if we rearrange primes by sorting, or by Deor poem order?
primes_sorted = sorted(GP_PRIMES)
primes_sorted_mod = [p % MOD for p in primes_sorted]

# Try various prime-based keys
prime_keys = {
    "primes_mod29": primes_mod29,
    "primes_sorted_mod29": primes_sorted_mod,
    "totient_primes": [(p-1) % MOD for p in GP_PRIMES],  # φ(p) = p-1
    "prime_indices": list(range(29)),  # trivial 0-28
    "prime_diffs": [(GP_PRIMES[i+1]-GP_PRIMES[i])%MOD for i in range(28)],
}

# Missing primes from telnet gap (73-1223) - first 50
def sieve_primes(limit):
    s = [True]*(limit+1); s[0]=s[1]=False
    for i in range(2,int(limit**0.5)+1):
        if s[i]:
            for j in range(i*i,limit+1,i): s[j]=False
    return [i for i in range(2,limit+1) if s[i]]
all_primes = sieve_primes(1224)
missing = [p for p in all_primes if p >= 73]
missing_mod29 = [p % MOD for p in missing[:50]]
prime_keys["missing_primes_mod29_50"] = missing_mod29

for name, key in prime_keys.items():
    if not key:
        continue
    for mode in ["SUB", "ADD", "BEAUFORT"]:
        if mode == "SUB":
            plain = [(p18[i]-key[i%len(key)])%MOD for i in range(len(p18))]
        elif mode == "ADD":
            plain = [(p18[i]+key[i%len(key)])%MOD for i in range(len(p18))]
        else:
            plain = [(key[i%len(key)]-p18[i])%MOD for i in range(len(p18))]
        txt = to_text(plain)
        ic = ioc(plain)
        ws = word_score(txt)
        if ic > 1.15 or ws > 30:
            print(f"  {name}/{mode}: IoC={ic:.3f} ws={ws}  {txt[:80]}")

# ═══════════════════════════════════════════════════════════════════════
# PHASE 7: Apply best approaches to other pages with elevated IoC
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("PHASE 7: Frequency analysis on other elevated-IoC pages")
print("="*80)

targets = [(26,17),(29,24),(30,17),(35,26),(23,31),(22,11),(36,18),(51,14),(52,15),(21,61)]

for page_num, test_k in targets:
    cipher = load_runes(page_num)
    if not cipher:
        continue
    
    n_per_col = len(cipher) // test_k
    cols = [[] for _ in range(test_k)]
    for i,v in enumerate(cipher):
        cols[i%test_k].append(v)
    
    for mode in ["SUB","ADD","BEAUFORT"]:
        key = []
        for col in cols:
            best_s, best_chi = 0, float('inf')
            for s in range(MOD):
                if mode == "SUB":
                    sh = [(v-s)%MOD for v in col]
                elif mode == "ADD":
                    sh = [(v+s)%MOD for v in col]
                else:
                    sh = [(s-v)%MOD for v in col]
                cc = Counter(sh)
                ch = chi2(cc, GP_EXP, len(col))
                if ch < best_chi:
                    best_chi = ch; best_s = s
            key.append(best_s)
        
        if mode == "SUB":
            plain = [(cipher[i]-key[i%test_k])%MOD for i in range(len(cipher))]
        elif mode == "ADD":
            plain = [(cipher[i]+key[i%test_k])%MOD for i in range(len(cipher))]
        else:
            plain = [(key[i%test_k]-cipher[i])%MOD for i in range(len(cipher))]
        
        txt = to_text(plain)
        ic = ioc(plain)
        ws = word_score(txt)
        
        if ic > 1.25 or ws > 40:
            print(f"  P{page_num} k={test_k} {mode}: IoC={ic:.3f} ws={ws}")
            print(f"    Key: {key}")
            print(f"    Text: {txt[:100]}")

# ═══════════════════════════════════════════════════════════════════════
# PHASE 8: P18 autocorrelation structure deep dive
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("PHASE 8: P18 structural analysis")
print("="*80)

# Detailed matches at specific lags
for lag in [20, 40, 60, 80, 86, 64, 47, 29, 10, 5]:
    matches = sum(1 for i in range(len(p18)-lag) if p18[i] == p18[i+lag])
    expected = (len(p18)-lag)/MOD
    ratio = matches/expected if expected>0 else 0
    print(f"  lag={lag:3d}: {matches:2d} matches / {expected:.1f} expected = {ratio:.3f}×")

# Check if cipher has segments that repeat
print("\n  Segment repetition check:")
for seg_len in [20, 26, 29, 43, 47, 52, 60, 65, 86, 87, 130]:
    if seg_len >= len(p18):
        continue
    n_segs = len(p18) // seg_len
    if n_segs < 2:
        continue
    segs = [p18[i*seg_len:(i+1)*seg_len] for i in range(n_segs)]
    # Compare all pairs
    pair_matches = []
    for i in range(n_segs):
        for j in range(i+1, n_segs):
            m = sum(1 for a,b in zip(segs[i],segs[j]) if a==b)
            pair_matches.append(m)
    avg_match = sum(pair_matches)/len(pair_matches) if pair_matches else 0
    expected = seg_len / MOD
    print(f"    seg_len={seg_len:3d}: {n_segs} segs, avg_match={avg_match:.1f}/{seg_len}, expected={expected:.1f}")

# ═══════════════════════════════════════════════════════════════════════
# PHASE 9: Running key with Deor poem on P18
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("PHASE 9: Deor poem as running key on P18")
print("="*80)

# Load Deor poem
deor_path = "c:\\Users\\tyler\\Repos\\Cicada3301\\LiberPrimus\\deor_poem.txt"
deor_runes = None
if os.path.exists(deor_path):
    with open(deor_path, 'r', encoding='utf-8') as f:
        dtxt = f.read()
    deor_runes = [GP_RUNE_TO_IDX[c] for c in dtxt if c in GP_RUNE_TO_IDX]
    print(f"  Deor runes loaded: {len(deor_runes)} values")
else:
    # Try alternative paths
    for alt in ["LiberPrimus/deor_poem.txt", "LiberPrimus/pages/deor/runes.txt",
                "Assets/deor.txt"]:
        alt_full = os.path.join("c:\\Users\\tyler\\Repos\\Cicada3301", alt)
        if os.path.exists(alt_full):
            with open(alt_full, 'r', encoding='utf-8') as f:
                dtxt = f.read()
            deor_runes = [GP_RUNE_TO_IDX[c] for c in dtxt if c in GP_RUNE_TO_IDX]
            print(f"  Deor runes from {alt}: {len(deor_runes)} values")
            break

if deor_runes is None:
    # Hard-code the Deor poem from the community 
    print("  Deor poem file not found, skipping")
else:
    # Use Deor as running key on P18
    n = min(len(p18), len(deor_runes))
    for offset in range(0, min(50, len(deor_runes)-len(p18)+1)):
        for mode in ["SUB", "ADD", "BEAUFORT"]:
            dk = deor_runes[offset:offset+len(p18)]
            if len(dk) < len(p18):
                continue
            if mode == "SUB":
                plain = [(p18[i]-dk[i])%MOD for i in range(len(p18))]
            elif mode == "ADD":
                plain = [(p18[i]+dk[i])%MOD for i in range(len(p18))]
            else:
                plain = [(dk[i]-p18[i])%MOD for i in range(len(p18))]
            txt = to_text(plain)
            ic = ioc(plain)
            ws = word_score(txt)
            if ic > 1.20 or ws > 40:
                print(f"  offset={offset} {mode}: IoC={ic:.3f} ws={ws}  {txt[:80]}")

# ═══════════════════════════════════════════════════════════════════════
# PHASE 10: Reverse approach — what if P19 key IS P18 plaintext?
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("PHASE 10: P19 key as English text -> P18 plaintext fragment")
print("="*80)

# P19 key: [24,15,2,24,4,21,11,10,20,16,9,19,26,11,7,5,11,6,27,8,22,25,21,16,25,0,27,9,21,7,27,15,21,9,3,16,5,22,18,4,5,18,23,21,1,10,24]
p19_key_text = to_text(P19_KEY)
print(f"  P19 key as GP text: {p19_key_text}")

# If this IS P18's plaintext (first 47 runes), what would P18's key be?
# P18_cipher[j] = encrypt(P18_plain[j], key[j])
# For SUB: cipher = (plain + key) mod 29 → key = (cipher - plain) mod 29
# Actually depends on encrypt direction. Let me try all.

# If P18 was encrypted with SUB: cipher = (plain - key) mod 29 → key = (plain - cipher) mod 29
# If P18 was encrypted with ADD: cipher = (plain + key) mod 29 → key = (cipher - plain) mod 29

# The P19 key text reads: A-S-TH-A-R-NG-J-I-L-T-N-M-Y-J-W-C-J-G-IA-H-OE-AE-NG-T-AE-F-IA-N-NG-W-IA-S-NG-N-O-T-C-OE-E-R-C-E-D-NG-U-I-A
# This seems to contain "NOT COERCED" at the end: N-O-T-C-OE-E-R-C-E-D

# If P18 plaintext starts with this text, and it's meaningful, read it as:
# "A STARING JILT... NOT COERCED"  
# or with digraphs: "A S TH A R NG J I L T..."
# With digraphs expanded: "A-S-TH-A-R-NG-J-I-L-T" = "ASTARNGJ ILT" → "A STAR(NG)JILT"?
# With no digraphs: index 2=TH is just letter name, not actual TH

# Actually try reading the P19 key using LETTER NAMES:
letter_names = []
for idx in P19_KEY:
    letter_names.append(GP_LETTERS[idx])
print(f"  P19 key as letter names: {'-'.join(letter_names)}")

# Check if there's a sensible reading
# Positions 34-46: O-T-C-OE-E-R-C-E-D-NG-U-I-A
# = "OT COERCED NGUIA" → "NOT COERCED" (with N at position 33)
# Full: "ASTHARNG JILT NM YJW CJG IA H OE AE NG T AE F IA N NG W IA S NG N OT C OE R C E D NG U I A"
# Or collapse: "ASTHARNG JILTNMYJWCJGIAHOEAENGTAEFIANNGWIASNGNOT COERCED NGUIA"
# Hmm, the end DOES spell "NOT COERCED" clearly!

# ═══════════════════════════════════════════════════════════════════════
# PHASE 11: Deeper k=20 analysis with digraph-aware frequency
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("PHASE 11: k=20 deep analysis — all combinations of top-2 shifts per column")
print("="*80)

test_k = 20
cols = [[] for _ in range(test_k)]
for i,v in enumerate(p18):
    cols[i%test_k].append(v)

# Get top-3 shifts per column for SUB mode
col_top3 = []
for col in cols:
    shifts = []
    for s in range(MOD):
        shifted = [(v-s)%MOD for v in col]
        counts = Counter(shifted)
        ch = chi2(counts, GP_EXP, len(col))
        shifts.append((ch, s))
    shifts.sort()
    col_top3.append([s for _,s in shifts[:3]])

print(f"  Top-3 shifts per column (SUB mode): {col_top3}")

# Try all combinations of top-2 per column: 2^20 = 1,048,576 — too many
# Instead try: top-1 for all, then perturb one column at a time
base_key = [ct[0] for ct in col_top3]
base_plain = [(p18[i]-base_key[i%test_k])%MOD for i in range(len(p18))]
base_txt = to_text(base_plain)
base_ic = ioc(base_plain)
base_ws = word_score(base_txt)
print(f"\n  Base key (top-1 each): {base_key}")
print(f"  Base IoC: {base_ic:.3f}  ws: {base_ws}")
print(f"  Base text: {base_txt[:120]}")

# Try perturbing each column to rank 2 or 3
print(f"\n  Single-column perturbations:")
for ci in range(test_k):
    for rank in [1, 2]:
        if rank >= len(col_top3[ci]):
            continue
        test_key = base_key.copy()
        test_key[ci] = col_top3[ci][rank]
        plain = [(p18[i]-test_key[i%test_k])%MOD for i in range(len(p18))]
        txt = to_text(plain)
        ic = ioc(plain)
        ws = word_score(txt)
        if ic > base_ic + 0.05 or ws > base_ws + 10:
            print(f"    col{ci} rank{rank}: IoC={ic:.3f} ws={ws}  delta_ic={ic-base_ic:+.3f}")

# Also try k=20 with ADD mode
print(f"\n  ADD mode base:")
add_base_key = []
for col in cols:
    shifts = []
    for s in range(MOD):
        shifted = [(v+s)%MOD for v in col]
        counts = Counter(shifted)
        ch = chi2(counts, GP_EXP, len(col))
        shifts.append((ch, s))
    shifts.sort()
    add_base_key.append(shifts[0][1])

add_plain = [(p18[i]+add_base_key[i%test_k])%MOD for i in range(len(p18))]
add_txt = to_text(add_plain)
add_ic = ioc(add_plain)
add_ws = word_score(add_txt)
print(f"  Key: {add_base_key}")
print(f"  IoC: {add_ic:.3f}  ws: {add_ws}")
print(f"  Text: {add_txt[:120]}")

print("\nDONE")
