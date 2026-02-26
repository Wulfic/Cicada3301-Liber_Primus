#!/usr/bin/env python3
"""
Targeted Small Page Analysis + Key Chaining Hypothesis
=======================================================
1. Raw IoC survey of ALL pages
2. Focus on P54 (IoC ~1.66) and P49 (small)
3. Adjacent page plaintext sum hypothesis
4. Backward key chaining: P19_key = P20 plaintext?
5. Forward key chaining from solved pages (P16 plaintext → P17 key)
6. Comprehensive simple cipher scan on P54
"""
import os, sys, io, math
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

GP_RUNES = list("\u16A0\u16A2\u16A6\u16A9\u16B1\u16B3\u16B7\u16B9\u16BB\u16BE\u16C1\u16C2\u16C7\u16C8\u16C9\u16CB\u16CF\u16D2\u16D6\u16D7\u16DA\u16DD\u16DF\u16DE\u16AA\u16AB\u16A3\u16E1\u16E0")
GP_RUNE_TO_IDX = {r: i for i, r in enumerate(GP_RUNES)}
GP_RUNE_TO_IDX['\u16C4'] = 11
MOD = 29
GP_LETTERS = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
              'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]

LATIN_TO_GP = {
    'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
    'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
    'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15
}

def load_runes(page_num):
    f = f"c:\\Users\\tyler\\Repos\\Cicada3301\\LiberPrimus\\pages\\page_{page_num:02d}\\runes.txt"
    if not os.path.exists(f): return None
    with open(f, 'r', encoding='utf-8') as fh:
        return [GP_RUNE_TO_IDX[c] for c in fh.read() if c in GP_RUNE_TO_IDX]

def ioc(v):
    if len(v)<2: return 0
    c=Counter(v); n=len(v)
    return sum(x*(x-1) for x in c.values())/(n*(n-1))*MOD

def to_text(idx):
    return ''.join(GP_LETTERS[i] for i in idx)

def text_to_gp(text):
    """Convert English text to GP indices, handling digraphs."""
    result = []
    i = 0
    t = text.upper()
    while i < len(t):
        if i+1 < len(t):
            digraph = t[i:i+2]
            if digraph in ['TH', 'NG', 'EO', 'OE', 'AE', 'IA', 'EA']:
                idx = GP_LETTERS.index(digraph)
                result.append(idx)
                i += 2
                continue
        c = t[i]
        if c in LATIN_TO_GP:
            result.append(LATIN_TO_GP[c])
        i += 1
    return result

COMMON_WORDS = {"THE","AND","FOR","ARE","NOT","YOU","ALL","HER","WAS","ONE",
    "OUR","OUT","HAS","HIS","HOW","MAN","NEW","NOW","OLD","SEE","WAY","WHO",
    "DID","GET","HIM","LET","SAY","SHE","TOO","BUT","CAN","HAD","ITS","MAY",
    "WILL","EACH","MAKE","LIKE","SOME","THEM","THAN","BEEN","HAVE","FROM",
    "INTO","WITH","THAT","THIS","WHAT","WHEN","THEY","COME","MADE","FIND",
    "MORE","ONLY","JUST","OVER","SUCH","ALSO","VERY","AFTER","BEING","THEIR",
    "THESE","THOSE","UNDER","ABOUT","COULD","EVERY","FIRST","SHALL","THERE",
    "THINK","WHERE","WHICH","WHILE","WORLD","WOULD","MIGHT","NEVER","STILL",
    "TRUTH","KNOW","MUST","SELF","SOUL","MIND","LIFE","DEAD","FEAR","FIRE",
    "FORM","GOOD","LORD","KING","WISE","WORD","WORK","PATH","RUNE",
    "WITHIN","FOLLOW","PILGRIM","WISDOM","CONSUMPTION","CIRCUMFERENCE",
    "PRIMES","NUMBERS","REARRANGING","SHOW","DEOR","DIVINITY","INSTAR",
    "SACRED","TOTIENT","FUNCTION","EMERGE","PARABLE","TUNNELING","SURFACE",
    "SHED","KOAN","MASTER","STUDY","INSTRUCTION","COMMAND","LOSS","PRESERVE"}

def word_score(text):
    sc=0; tu=text.upper()
    for w in COMMON_WORDS:
        st=0
        while True:
            p=tu.find(w,st)
            if p<0: break
            sc+=len(w); st=p+1
    return sc

# =========================================================================
# SECTION 1: Raw IoC survey of ALL pages
# =========================================================================
print("="*80)
print("SECTION 1: Raw IoC survey of ALL pages")
print("="*80)

all_pages = {}
for pn in range(0, 75):
    r = load_runes(pn)
    if r and len(r) > 2:
        all_pages[pn] = r
        ic = ioc(r)
        if len(r) > 10:
            # Expected English GP IoC is roughly 1.7-2.0
            marker = ""
            if ic > 1.5 and len(r) > 30: marker = " *** HIGH IOC"
            if ic > 2.0 and len(r) > 30: marker = " *** VERY HIGH IOC"
            if ic < 1.1 and len(r) > 50: marker = " (flat/poly)"
            print(f"  Page {pn:2d}: {len(r):4d} runes, IoC = {ic:.3f}{marker}")

# =========================================================================
# SECTION 2: P54 comprehensive analysis
# =========================================================================
print("\n" + "="*80)
print("SECTION 2: P54 comprehensive analysis")
print("="*80)

p54 = all_pages.get(54, [])
print(f"P54: {len(p54)} runes")
print(f"P54 raw IoC: {ioc(p54):.3f}")
print(f"P54 values: {p54}")
print(f"P54 text: {to_text(p54)}")

# Frequency analysis
p54_freq = Counter(p54)
print(f"\nP54 frequency distribution (sorted by count):")
for val, cnt in p54_freq.most_common():
    pct = 100*cnt/len(p54)
    print(f"  {GP_LETTERS[val]:3s} (idx={val:2d}): {cnt:2d} ({pct:.1f}%)")

# Try all 28 Caesar shifts
print(f"\nP54 Caesar shift scan:")
for shift in range(MOD):
    shifted = [(v - shift) % MOD for v in p54]
    txt = to_text(shifted)
    ws = word_score(txt)
    ic = ioc(shifted)
    if ws > 15 or shift < 5:
        print(f"  shift={shift:2d}: ws={ws:3d} IoC={ic:.3f} {txt[:80]}")

# Try Vigenere with all short keys (k=2..10)
print(f"\nP54 Vigenere frequency analysis:")
for k in range(2, min(20, len(p54)//4)):
    cols = [[] for _ in range(k)]
    for i, v in enumerate(p54):
        cols[i%k].append(v)
    avg_ioc = sum(ioc(c) for c in cols) / k
    if avg_ioc > 1.6 or k <= 5:
        print(f"  k={k}: avg_col_IoC={avg_ioc:.3f} (cols: {', '.join(f'{ioc(c):.2f}' for c in cols)})")

# Try Vigenere with DIVINITY key
divinity = [23, 10, 1, 10, 9, 10, 16, 26]
for mode in ["SUB", "ADD", "BEAUFORT"]:
    if mode == "SUB":
        plain = [(p54[i] - divinity[i % len(divinity)]) % MOD for i in range(len(p54))]
    elif mode == "ADD":
        plain = [(p54[i] + divinity[i % len(divinity)]) % MOD for i in range(len(p54))]
    else:
        plain = [(divinity[i % len(divinity)] - p54[i]) % MOD for i in range(len(p54))]
    txt = to_text(plain)
    ws = word_score(txt)
    ic = ioc(plain)
    print(f"  DIVINITY/{mode}: IoC={ic:.3f} ws={ws}")
    if ws > 15:
        print(f"    {txt}")

# Try P55 totient method on P54
print(f"\nP54 with P55 totient cipher:")
def sieve_primes(n):
    s=[True]*(n+1); s[0]=s[1]=False
    for i in range(2,int(n**0.5)+1):
        if s[i]:
            for j in range(i*i,n+1,i): s[j]=False
    return [i for i in range(2,n+1) if s[i]]
PRIMES = sieve_primes(50000)

def euler_totient(n):
    result = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result

# Totient cipher: key[i] = euler_totient(prime[i]) mod 29
for prime_offset in range(0, 200, 10):
    key = [euler_totient(PRIMES[prime_offset + i]) % MOD for i in range(len(p54))]
    for mode in ["SUB", "ADD", "BEAUFORT"]:
        if mode == "SUB":
            plain = [(p54[i] - key[i]) % MOD for i in range(len(p54))]
        elif mode == "ADD":
            plain = [(p54[i] + key[i]) % MOD for i in range(len(p54))]
        else:
            plain = [(key[i] - p54[i]) % MOD for i in range(len(p54))]
        txt = to_text(plain)
        ws = word_score(txt)
        ic = ioc(plain)
        if ic > 1.5 or ws > 30:
            print(f"  totient/off={prime_offset}/{mode}: IoC={ic:.3f} ws={ws}")
            print(f"    {txt[:80]}")

# =========================================================================
# SECTION 2b: P49 comprehensive analysis
# =========================================================================
print("\n" + "="*80)
print("SECTION 2b: P49 comprehensive analysis")
print("="*80)

p49 = all_pages.get(49, [])
print(f"P49: {len(p49)} runes")
print(f"P49 raw IoC: {ioc(p49):.3f}")
print(f"P49 text: {to_text(p49)}")

# Frequency analysis
p49_freq = Counter(p49)
print(f"\nP49 frequency distribution:")
for val, cnt in p49_freq.most_common():
    pct = 100*cnt/len(p49)
    print(f"  {GP_LETTERS[val]:3s} (idx={val:2d}): {cnt:2d} ({pct:.1f}%)")

# Caesar shifts on P49
print(f"\nP49 Caesar shift scan:")
for shift in range(MOD):
    shifted = [(v - shift) % MOD for v in p49]
    txt = to_text(shifted)
    ws = word_score(txt)
    if ws > 15 or shift < 5:
        print(f"  shift={shift:2d}: ws={ws:3d} IoC={ioc(shifted):.3f} {txt[:80]}")

# =========================================================================
# SECTION 3: Adjacent page plaintext sum/difference hypothesis
# =========================================================================
print("\n" + "="*80)
print("SECTION 3: Adjacent page sum/diff hypothesis")
print("="*80)

# Test: if cipher_N = (plain_N + plain_{N+1}) mod 29
# Then with solved pages, consecutive solved pages should satisfy this
# Test with pages 03-04 (both solved with DIVINITY key, continuous text)

# Let's test with known solved plaintext pairs
# Pages 03-04: continuous text with DIVINITY key

# Get plaintext of solved pages
solved_texts = {
    3: "WELCOMEWELCOMEPILGRIMTOTHEGREATJOURNEYTOWARDTHEENDOFALLTHINGSITISNOTANEASYTRIPBUTFORTHOSEWHOFINDTHEIRWAYHEREITIS"
       "ANECESSARYONEALONGTHEWAYYOUWILLFINDANENDTOALLSTRUGGLEANDSUFFERINGYOURINNOCENCEYOURILLUSIONSYOURCERTAINTYANDYOUR"
       "REALITYULTIMATELYYOUWILLDISCOVERANENDTOSELF",
    4: "ITISTHROUGHTHISPILGRIMAGETHATWESHAPEOURSELVESANDOURREALITIESJOURNEYDRIPWITHINANDYOUWILLARRIVEOUTSIDELIKETHE"
       "INSTARITISONLY THROUGHGOINGWITHINTHATWEMAYEMERGEWISDOMYOUAREABEINGUNTOYOURSELFYOUAREALAWUNTOYOURSELFEACH"
       "INTELLIGENCEISHOLYFORALLTHATLIVESISHOLYANINSTRUCTIONCOMMANDYOUROWNSELF"
}

print("Testing with known solved pages:")
for pn in [3, 4]:
    if pn in solved_texts:
        pt = text_to_gp(solved_texts[pn].replace(" ", ""))
        if pn in all_pages:
            cipher = all_pages[pn]
            if len(pt) > 20 and len(cipher) > 20:
                n = min(len(pt), len(cipher))
                # Derive key
                key_sub = [(cipher[i] - pt[i]) % MOD for i in range(n)]
                key_add = [(cipher[i] + pt[i]) % MOD for i in range(n)]
                print(f"  Page {pn}: {len(cipher)} cipher, {len(pt)} plain, using {n}")
                print(f"    Key(SUB) first 20: {key_sub[:20]}")
                print(f"    Key(ADD) first 20: {key_add[:20]}")
                print(f"    Key(SUB) text: {to_text(key_sub[:30])}")

# =========================================================================
# SECTION 4: Forward key chaining from solved pages
# =========================================================================
print("\n" + "="*80)
print("SECTION 4: Forward key chaining from P16")
print("="*80)

# Page 16 is solved (cleartext). P17 is the first unsolved page.
# If P16 plaintext = key for P17, this should decrypt P17
p16_text = "ANINSTRUCTIONQUESTIONALLTHINGSDISCOVERTRUTHINSIDEYOURSELFFOLLOWYOURTRUTHIMPOSENOTHINGONOTHERS"
# Also the magic square with numbers, but let's try just the text part
p16_gp = text_to_gp(p16_text)
print(f"P16 plaintext as GP: {len(p16_gp)} values")
print(f"P16 GP text: {to_text(p16_gp[:40])}")

p17 = all_pages.get(17, [])
if p17:
    print(f"\nP17: {len(p17)} runes, IoC={ioc(p17):.3f}")
    n = min(len(p16_gp), len(p17))
    for mode in ["SUB", "ADD", "BEAUFORT"]:
        if n > 0:
            if mode == "SUB":
                plain = [(p17[i] - p16_gp[i % len(p16_gp)]) % MOD for i in range(len(p17))]
            elif mode == "ADD":
                plain = [(p17[i] + p16_gp[i % len(p16_gp)]) % MOD for i in range(len(p17))]
            else:
                plain = [(p16_gp[i % len(p16_gp)] - p17[i]) % MOD for i in range(len(p17))]
            txt = to_text(plain)
            ws = word_score(txt)
            ic = ioc(plain)
            print(f"  P16_text as key for P17 ({mode}): IoC={ic:.3f} ws={ws}")
            print(f"    {txt[:120]}")

# Also try pages 14-15 solved text as key for P16 (verification)
# And P15 text as key for P17
p14_15_text = "AKOANDURINGALESSONTHEMASTEREXPLAINEDTHEITHEIISTHEVOICEOFTHECIRCUMFERENCEHESAIDWHENASKEDBYASTUDENTTOE"
p14_15_gp = text_to_gp(p14_15_text)
if p17:
    n = min(len(p14_15_gp), len(p17))
    for mode in ["SUB", "ADD", "BEAUFORT"]:
        if mode == "SUB":
            plain = [(p17[i] - p14_15_gp[i % len(p14_15_gp)]) % MOD for i in range(len(p17))]
        elif mode == "ADD":
            plain = [(p17[i] + p14_15_gp[i % len(p14_15_gp)]) % MOD for i in range(len(p17))]
        else:
            plain = [(p14_15_gp[i % len(p14_15_gp)] - p17[i]) % MOD for i in range(len(p17))]
        txt = to_text(plain)
        ws = word_score(txt)
        ic = ioc(plain)
        if ic > 1.15 or ws > 30:
            print(f"  P14-15_text as key for P17 ({mode}): IoC={ic:.3f} ws={ws}")
            print(f"    {txt[:120]}")

# =========================================================================
# SECTION 5: Backward key chaining test
# =========================================================================
print("\n" + "="*80)
print("SECTION 5: Backward key chaining test") 
print("="*80)

# Hypothesis: P19 key (47 values) = first 47 chars of P20 plaintext
# If true, use those as key and decrypt P20
P19_KEY = [24,15,2,24,4,21,11,10,20,16,9,19,26,11,7,5,11,6,27,8,22,25,21,16,25,0,27,9,21,7,27,15,21,9,3,16,5,22,18,4,5,18,23,21,1,10,24]

p20 = all_pages.get(20, [])
if p20:
    print(f"P20: {len(p20)} runes")
    # If P19 key = P20 plaintext first 47:
    # Then P20 cipher = P20 plaintext + key_for_P20
    # We don't know key_for_P20, but we can check:
    # If P19key IS P20 plaintext, then cipher[i] - P19key[i] = P20_key[i]
    n47 = min(47, len(p20))
    derived_key = [(p20[i] - P19_KEY[i]) % MOD for i in range(n47)]
    print(f"  If P19_key = P20_plain (first 47):")
    print(f"    Derived P20_key: {derived_key}")
    print(f"    Key text: {to_text(derived_key)}")
    print(f"    Key IoC: {ioc(derived_key):.3f}")
    
    # Check if derived key is periodic
    for period in range(2, 24):
        match = 0
        total = 0
        for i in range(period, n47):
            if derived_key[i] == derived_key[i % period]:
                match += 1
            total += 1
        if total > 0 and match/total > 0.8:
            print(f"    Period {period}: {match}/{total} matches ({100*match/total:.0f}%)")
    
    # Also check: is the derived key the DIVINITY key?
    divinity = [23, 10, 1, 10, 9, 10, 16, 26]
    div_matches = sum(1 for i in range(n47) if derived_key[i] == divinity[i % len(divinity)])
    print(f"    DIVINITY key matches: {div_matches}/{n47}")
    
    # Also try: P19key = P20 plaintext under SUB mode, cipher = plain - key
    # cipher[i] = P20_plain[i] - P20_key[i] => P20_key[i] = P19key[i] - cipher[i] (if plain=P19key)
    derived_key2 = [(P19_KEY[i] - p20[i]) % MOD for i in range(n47)]
    print(f"\n  Alternative: cipher = plain - key:")
    print(f"    Derived P20_key: {derived_key2}")
    print(f"    Key text: {to_text(derived_key2)}")

# =========================================================================
# SECTION 6: Check P55 plaintext as key for P54
# =========================================================================
print("\n" + "="*80)
print("SECTION 6: P55 plaintext as key for P54")
print("="*80)

p55_text = "ANENDWITHINTHEDEEPWEBTHEREEXISTSAPAGETHATHASHESTORE"  # truncated
p55_gp = text_to_gp(p55_text)
print(f"P55 plaintext as GP: {len(p55_gp)} values")

if p54:
    n = min(len(p55_gp), len(p54))
    for mode in ["SUB", "ADD", "BEAUFORT"]:
        if mode == "SUB":
            plain = [(p54[i] - p55_gp[i]) % MOD for i in range(n)]
        elif mode == "ADD":
            plain = [(p54[i] + p55_gp[i]) % MOD for i in range(n)]
        else:
            plain = [(p55_gp[i] - p54[i]) % MOD for i in range(n)]
        txt = to_text(plain)
        ws = word_score(txt)
        ic = ioc(plain)
        print(f"  P55_text as P54 key ({mode}): IoC={ic:.3f} ws={ws}")
        print(f"    {txt[:80]}")

# Also try P54 plaintext as key for P53  
p53 = all_pages.get(53, [])
if p53:
    print(f"\nP53: {len(p53)} runes, IoC={ioc(p53):.3f}")

# =========================================================================
# SECTION 7: All solved page plaintexts as running keys
# =========================================================================
print("\n" + "="*80)
print("SECTION 7: All solved plaintexts as running keys for P18")
print("="*80)

p18 = all_pages.get(18, [])
solved_plaintext_sources = {
    "P01_warning": "AWARNINGBELIEVENOTHING FROMTHISBOOKEXCEPTWHATYOUKNOWTOBETRUETEST"
        "THEKNOWLEDGEFINDYOURTRUTHEXPERIENCEYOURDEATHDONOTEDITORCHANGETHISBOOKOR"
        "THEMESSAGECONTAINEDWITHINEITHER THEWORDSORTHEIRNUMBERSFORALLISSACRED",
    "P03_welcome": solved_texts[3],
    "P04_wisdom": solved_texts[4],
    "P06_koan": "AKOANAMANDECIDEDTOGOANDSTUDYWITHAMASTER"
        "HEWENTTOTHEDOOROFTHEMASTERWHOAREYOUWHOWISHESTOSTUDYHHEREASKEDTHE"
        "MASTERTHESTUDENTTOLDTHEMASTERHISNAMETHATISNOTWHAT YOUARETHATISONLY"
        "WHATYOUARECALLEDWHOAREYOUWHOWISHESTOSTUDYHEREHASKEDAGAIN",
    "P10_loss": "THELOSSOFDIVINITY THECIRCUMFERENCEPRACTICESTHREEBEHAVIORSWHICHCAUSE"
        "THELOSSOFDIVINITY CONSUMPTIONWECONSUMETOOMUCHBECAUSEWEBELIEVE"
        "THEFOLLOWINGTWOERRORSWITHINTHEDCEPTIONWEDONOTHAVEENOUGHORTHEREISNOT"
        "ENOUGHWEHAVEWHATWEHAVENOWBYLUCKANDWEWILLNOTBESTRONGENOUGHLATERTOOBTAIN"
        "WHATWENEEDMOSTTHINGSARENOTWORTHCONSUMING",
    "P14_koan2": p14_15_text,
    "P16_instr": p16_text,
    "P55_anend": "ANENDWITHINTHEDEEPWEBTHEREEXISTSAPAGETHATHASHESTORE"
        "AEANDSOMETHINGITISTHEDUTYOFEVERYPILGRIMTOSEEKOUTTHISPAGE",
}

if p18:
    for name, text in solved_plaintext_sources.items():
        gp = text_to_gp(text.replace(" ", ""))
        if len(gp) < 50:
            continue
        n = min(len(gp), len(p18))
        for mode in ["SUB", "ADD", "BEAUFORT"]:
            if mode == "SUB":
                plain = [(p18[i] - gp[i % len(gp)]) % MOD for i in range(len(p18))]
            elif mode == "ADD":
                plain = [(p18[i] + gp[i % len(gp)]) % MOD for i in range(len(p18))]
            else:
                plain = [(gp[i % len(gp)] - p18[i]) % MOD for i in range(len(p18))]
            txt = to_text(plain)
            ws = word_score(txt)
            ic = ioc(plain)
            if ic > 1.15 or ws > 40:
                print(f"  {name}/{mode}: IoC={ic:.3f} ws={ws}")
                print(f"    {txt[:100]}")

# =========================================================================
# SECTION 8: P54 with F-skip Vigenere (DIVINITY and FIRFUMFERENFE)
# =========================================================================
print("\n" + "="*80)
print("SECTION 8: P54 F-skip Vigenere scan")
print("="*80)

def fskip_decrypt(cipher, key, mode="SUB"):
    plain = []
    ki = 0
    for c in cipher:
        if c == 0:  # F rune
            plain.append(0)
            # Key counter does NOT advance
        else:
            k = key[ki % len(key)]
            if mode == "SUB":
                p = (c - k) % MOD
            elif mode == "ADD":
                p = (c + k) % MOD
            else:
                p = (k - c) % MOD
            plain.append(p)
            ki += 1
    return plain

known_keys = {
    "DIVINITY": [23, 10, 1, 10, 9, 10, 16, 26],
    "FIRFUMFERENFE": text_to_gp("FIRFUMFERENFE"),
    "CIRCUMFERENCE": text_to_gp("CIRCUMFERENCE"),
    "CONSUMPTION": text_to_gp("CONSUMPTION"),
    "PRESERVATION": text_to_gp("PRESERVATION"),
    "ADHERENCE": text_to_gp("ADHERENCE"),
    "INSTAR": text_to_gp("INSTAR"),
    "PILGRIM": text_to_gp("PILGRIM"),
    "WISDOM": text_to_gp("WISDOM"),
    "SACRED": text_to_gp("SACRED"),
    "PRIMES": text_to_gp("PRIMES"),
    "TOTIENT": text_to_gp("TOTIENT"),
    "PARABLE": text_to_gp("PARABLE"),
    "SHADOWS": text_to_gp("SHADOWS"),
    "CABAL": text_to_gp("CABAL"),
    "MOBIUS": text_to_gp("MOBIUS"),
    "VOID": text_to_gp("VOID"),
    "DEOR": text_to_gp("DEOR"),
}

for page_num in [54, 49, 17, 18]:
    pg = all_pages.get(page_num, [])
    if not pg:
        continue
    print(f"\nPage {page_num} ({len(pg)} runes, raw IoC={ioc(pg):.3f}):")
    
    for key_name, key_vals in known_keys.items():
        for mode in ["SUB", "ADD", "BEAUFORT"]:
            # With F-skip
            plain_fs = fskip_decrypt(pg, key_vals, mode)
            txt_fs = to_text(plain_fs)
            ws_fs = word_score(txt_fs)
            ic_fs = ioc(plain_fs)
            
            # Without F-skip  
            if mode == "SUB":
                plain_nf = [(pg[i] - key_vals[i % len(key_vals)]) % MOD for i in range(len(pg))]
            elif mode == "ADD":
                plain_nf = [(pg[i] + key_vals[i % len(key_vals)]) % MOD for i in range(len(pg))]
            else:
                plain_nf = [(key_vals[i % len(key_vals)] - pg[i]) % MOD for i in range(len(pg))]
            txt_nf = to_text(plain_nf)
            ws_nf = word_score(txt_nf)
            ic_nf = ioc(plain_nf)
            
            if ws_fs > 30 or ic_fs > 1.6:
                print(f"  {key_name}/{mode}/F-skip: IoC={ic_fs:.3f} ws={ws_fs}")
                print(f"    {txt_fs[:80]}")
            if ws_nf > 30 or ic_nf > 1.6:
                print(f"  {key_name}/{mode}/no-skip: IoC={ic_nf:.3f} ws={ws_nf}")
                print(f"    {txt_nf[:80]}")

# =========================================================================
# SECTION 9: Atbash / reversal ciphers
# =========================================================================
print("\n" + "="*80)
print("SECTION 9: Atbash and reversal on all unsolved pages")
print("="*80)

for page_num in range(17, 55):
    pg = all_pages.get(page_num, [])
    if not pg or len(pg) < 30:
        continue
    
    # Atbash: val -> (28 - val) mod 29
    atbash = [(28 - v) % MOD for v in pg]
    txt = to_text(atbash)
    ws = word_score(txt)
    ic = ioc(atbash)
    if ws > 30 or ic > 1.5:
        print(f"  P{page_num} Atbash: IoC={ic:.3f} ws={ws}")
        print(f"    {txt[:80]}")
    
    # Reverse the entire text
    rev = list(reversed(pg))
    txt = to_text(rev)
    ws = word_score(txt)
    ic = ioc(rev)
    if ws > 30 or ic > 1.5:
        print(f"  P{page_num} Reversed: IoC={ic:.3f} ws={ws}")
        print(f"    {txt[:80]}")
    
    # Atbash + shift
    for shift in range(1, MOD):
        atbash_shift = [(28 - v + shift) % MOD for v in pg]
        txt = to_text(atbash_shift)
        ws = word_score(txt)
        if ws > 40:
            print(f"  P{page_num} Atbash+shift{shift}: IoC={ioc(atbash_shift):.3f} ws={ws}")
            print(f"    {txt[:80]}")

# =========================================================================
# SECTION 10: P54 Hill cipher 2x2 brute force
# =========================================================================
print("\n" + "="*80)
print("SECTION 10: P54 Hill cipher 2x2")
print("="*80)

def mod_inv(a, m=29):
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None

if p54 and len(p54) >= 4:
    # Hill cipher 2x2: [a b; c d] * [p1; p2] = [c1; c2] mod 29
    # Decrypt: inv_matrix * [c1; c2] = [p1; p2]
    best_hill = []
    for a in range(MOD):
        for b in range(MOD):
            for c in range(MOD):
                for d in range(MOD):
                    det = (a*d - b*c) % MOD
                    inv_det = mod_inv(det)
                    if inv_det is None:
                        continue
                    # Inverse matrix: inv_det * [d -b; -c a]
                    ia = (inv_det * d) % MOD
                    ib = (inv_det * (-b)) % MOD
                    ic2 = (inv_det * (-c)) % MOD
                    id2 = (inv_det * a) % MOD
                    
                    # Decrypt
                    plain = []
                    for i in range(0, len(p54)-1, 2):
                        p1 = (ia * p54[i] + ib * p54[i+1]) % MOD
                        p2 = (ic2 * p54[i] + id2 * p54[i+1]) % MOD
                        plain.extend([p1, p2])
                    
                    ic_val = ioc(plain)
                    if ic_val > 2.0:
                        txt = to_text(plain)
                        ws = word_score(txt)
                        if ws > 20:
                            best_hill.append((ic_val, ws, (a,b,c,d), txt[:80]))
    
    best_hill.sort(key=lambda x: (-x[0], -x[1]))
    print(f"Top 10 Hill 2x2 (from {len(best_hill)} candidates):")
    for ic_val, ws, key, txt in best_hill[:10]:
        print(f"  key={key}: IoC={ic_val:.3f} ws={ws}")
        print(f"    {txt}")

print("\nDONE")
