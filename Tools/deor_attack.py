"""
DEOR POEM KNOWN-PLAINTEXT ATTACK on P20
Hint: "REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR"

Key insight: Old English has þ=TH and æ=AE which map directly to GP runes!

Strategy:
1. Convert Deor poem to GP values (both OE and modern English)
2. Known-Plaintext Attack: if P20 plaintext = Deor, recover key and check for prime patterns
3. Running key attack: Deor as Vigenère running key
4. Prime-transposition: rearrange cipher by prime positions, then apply key
5. Various "rearranged primes" interpretations
"""
import os, re
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
              'FIND','MAKE','JUST','KNOW','TRUTH','SACRED','WISDOM','WITHIN',
              'PRIME','BEING','WORLD','NEVER','EVERY','THERE','ABOUT','WHICH']:
        score += t.count(w) * 5
    # Deor-specific words
    for w in ['DEOR','WAYLAND','WELUND','WELAND','EXILE','SORROW','HARDSHIP',
              'PASSED','AWAY','THAT','MAETHHILD','THEODRIC','EORMANRIC',
              'BEADOHILD','NITHHAD','HEORRENDA','KINGDOM','WINTER','LORD',
              'POET','GRIM','KING','DARK','MIND','THINK','WORLD','WISE',
              'GLORY','WOES','NAME','LAND','RIGHT','GAVE']:
        score += t.count(w) * 8
    return score

# ===== ENGLISH TO GP CONVERSION =====
def english_to_gp(text_str):
    """Convert English text to GP index values, handling digraphs."""
    result = []
    text_upper = text_str.upper()
    i = 0
    while i < len(text_upper):
        if i + 2 <= len(text_upper):
            di = text_upper[i:i+2]
            dmap = {'TH':2, 'EO':12, 'NG':21, 'OE':22, 'AE':25, 'IA':27, 'EA':28}
            if di in dmap:
                result.append(dmap[di])
                i += 2
                continue
        ch = text_upper[i]
        smap = {'F':0,'U':1,'V':1,'O':3,'R':4,'C':5,'K':5,'G':6,'W':7,'H':8,'N':9,
                'I':10,'J':11,'P':13,'X':14,'S':15,'Z':15,'T':16,'B':17,'E':18,'M':19,
                'L':20,'D':23,'A':24,'Y':26}
        if ch in smap:
            result.append(smap[ch])
        # Skip spaces, punctuation, etc.
        i += 1
    return result

def old_english_to_gp(text_str):
    """Convert Old English to GP, handling þ=TH, ð=TH, æ=AE."""
    # First replace OE special chars
    t = text_str
    t = t.replace('þ', 'th').replace('Þ', 'th')
    t = t.replace('ð', 'th').replace('Ð', 'th')
    t = t.replace('æ', 'ae').replace('Æ', 'ae')
    return english_to_gp(t)

def primes_up_to(n):
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n+1, i): sieve[j] = False
    return [i for i in range(2, n+1) if sieve[i]]

PRIMES = primes_up_to(100000)

# ===== DEOR POEM TEXT =====
DEOR_OE = """Welund him be wurman wraeces cunnade,
anhydig eorl earfotha dreag,
haefde him to gesiththe sorge ond longath,
wintercealde wraece wean oft onfond,
siththan hine Nithhad on nede legde,
swoncre seonobende on syllan monn.
Thaes ofereode thisses swa maeg.

Beadohilde ne waes hyre brothra death
on sefan swa sar swa hyre sylfre thing,
thaet heo gearolice ongieten haefde
thaet heo eacen waes aefre ne meahte
thriste gethencan hu ymb thaet sceolde.
Thaes ofereode thisses swa maeg.

We thaet Maethhilde monge gefrugnon
wurdon grundlease Geates frige,
thaet hi seithsorga slaep ealle binom.
Thaes ofereode thisses swa maeg.

Theodric ahte thritig wintra
Maeringa burg thaet waes monegum cuth.
Thaes ofereode thisses swa maeg.

We geascodan Eormanrices
wylfenne gethoht ahte wide folc
Gotena rices. Thaet waes grim cyning.
Saet secg monig sorgum gebunden,
wean on wenan wyscte geneahhe
thaet thaes cynerices ofercumen waere.
Thaes ofereode thisses swa maeg.

Siteth sorgcearig saelum bidaeled
on sefan sweorceth sylfum thinceth
thaet sy endeleas earfotha dael.
Maeg thonne gethencan thaet geond thas woruld
witig Dryhten wendeth geneahhe,
eorle monegum are gesceawath
wislicne blaed sumum weana dael.
Thaet ic bi me sylfum secgan wille,
thaet ic hwile waes Heodeninga scop
dryhtne dyre. Me waes Deor noma.
Ahte ic fela wintra folgath tilne,
holdne hlaford oththaet Heorrenda nu,
leothcraeftig monn londryht gethah
thaet me eorla hleo aer gesealde.
Thaes ofereode thisses swa maeg."""

DEOR_MODERN = """Wayland knew the worm of exile.
The strong minded earl suffered hardships.
He had for companions sorrow and longing,
winter cold exile woe he often found,
since Nithhad laid necessity upon him,
supple sinew bonds on the better man.
That passed away so may this.

To Beadohild her brothers death was not
so painful in her mind as her own problem,
that she had clearly perceived
that she was pregnant nor could she ever
confidently think how that should turn out.
That passed away so may this.

We have heard that about Maethhild
the Geats lusts became boundless
that sorrowful love took all sleep from them.
That passed away so may this.

Theodric held for thirty winters
the fortress of the Maerings that was known to many.
That passed away so may this.

We have learned of Eormanrics
wolflike thought he owned the wide folk
of the Goths kingdom. That was a grim king.
Many a man sat bound in sorrows,
woe in expectation wished often
that the kingdom were overcome.
That passed away so may this.

He sits sorrow anxious deprived of joy,
darkens in his mind thinks to himself
that his share of hardships is endless.
He may then think that throughout this world
the wise Lord turns often,
shows honor to many an earl
certain glory to some a share of woes.
That I will say about myself,
that I was for a while the poet of the Heodenings,
dear to my lord. Deor was my name.
I had for many winters a good office,
a loyal lord until Heorrenda now,
a song crafty man received the land right
that the protector of earls formerly gave me.
That passed away so may this."""

# ===== LOAD DATA =====
print("=" * 80)
print("DEOR POEM KNOWN-PLAINTEXT ATTACK ON P20")
print("=" * 80)

d20 = load_page(20)
print(f"P20 cipher length: {len(d20)} runes")

deor_oe_gp = old_english_to_gp(DEOR_OE)
deor_modern_gp = english_to_gp(DEOR_MODERN)

print(f"Deor OE GP length: {len(deor_oe_gp)} values")
print(f"Deor Modern GP length: {len(deor_modern_gp)} values")
print(f"Deor OE first 50 GP: {text(deor_oe_gp[:50])}")
print(f"Deor Modern first 50 GP: {text(deor_modern_gp[:50])}")

# ===== SECTION 1: DEOR AS RUNNING KEY =====
print(f"\n{'='*80}")
print("SECTION 1: Deor poem as Vigenère running key")
print("=" * 80)

for name, key_gp in [("OE", deor_oe_gp), ("Modern", deor_modern_gp)]:
    for start in range(0, min(50, len(key_gp) - len(d20) + 1)):
        k_seg = key_gp[start:start + len(d20)]
        if len(k_seg) < len(d20): continue
        
        for mode in ['SUB', 'ADD', 'BEAU']:
            if mode == 'SUB': dec = [(d20[i] - k_seg[i]) % 29 for i in range(len(d20))]
            elif mode == 'ADD': dec = [(d20[i] + k_seg[i]) % 29 for i in range(len(d20))]
            else: dec = [(k_seg[i] - d20[i]) % 29 for i in range(len(d20))]
            
            ic = ioc29(dec)
            sc = score_english(dec)
            if ic > 1.25 or sc > 50:
                print(f"  {name} start={start} {mode}: IoC={ic:.4f} score={sc}")
                print(f"    {text(dec)[:100]}")

# Also test with key repeating
for name, key_gp in [("OE", deor_oe_gp), ("Modern", deor_modern_gp)]:
    rkey = key_gp * (len(d20) // len(key_gp) + 1)
    rkey = rkey[:len(d20)]
    for mode in ['SUB', 'ADD', 'BEAU']:
        if mode == 'SUB': dec = [(d20[i] - rkey[i]) % 29 for i in range(len(d20))]
        elif mode == 'ADD': dec = [(d20[i] + rkey[i]) % 29 for i in range(len(d20))]
        else: dec = [(rkey[i] - d20[i]) % 29 for i in range(len(d20))]
        
        ic = ioc29(dec)
        sc = score_english(dec)
        print(f"  {name} REPEAT {mode}: IoC={ic:.4f} score={sc}")
        if ic > 1.2 or sc > 30:
            print(f"    {text(dec)[:100]}")

# ===== SECTION 2: KNOWN PLAINTEXT ATTACK =====
print(f"\n{'='*80}")
print("SECTION 2: Known Plaintext Attack (assume P20 plaintext = Deor)")
print("=" * 80)

for name, plain_gp in [("OE", deor_oe_gp), ("Modern", deor_modern_gp)]:
    if len(plain_gp) < len(d20):
        print(f"  {name}: GP too short ({len(plain_gp)} < {len(d20)}), padding with repeat")
        plain_gp = plain_gp * (len(d20) // len(plain_gp) + 1)
        plain_gp = plain_gp[:len(d20)]
    
    for start in range(max(1, len(plain_gp) - len(d20) + 1)):
        p_seg = plain_gp[start:start+len(d20)]
        if len(p_seg) < len(d20): continue
        
        # Recover key: k = (c - p) mod 29
        key_sub = [(d20[i] - p_seg[i]) % 29 for i in range(len(d20))]
        # k = (p - c) mod 29  
        key_add = [(p_seg[i] - d20[i]) % 29 for i in range(len(d20))]
        # k = (c + p) mod 29
        key_beau = [(d20[i] + p_seg[i]) % 29 for i in range(len(d20))]
        
        for kname, key in [("c-p", key_sub), ("p-c", key_add), ("c+p", key_beau)]:
            # Check if key is prime-related
            # Check: is key[i] = prime[i] % 29 for some offset?
            for offset in range(0, 200):
                if offset + len(d20) >= len(PRIMES): break
                prime_key = [PRIMES[i+offset] % 29 for i in range(len(d20))]
                match = sum(1 for i in range(len(d20)) if key[i] == prime_key[i])
                if match > len(d20) * 0.3:
                    print(f"  {name} start={start} key={kname}: prime offset={offset} match={match}/{len(d20)} ({100*match/len(d20):.1f}%)")
            
            # Check: is key[i] = φ(prime[i]) % 29 for some offset?
            for offset in range(0, 200):
                if offset + len(d20) >= len(PRIMES): break
                tot_key = [(PRIMES[i+offset]-1) % 29 for i in range(len(d20))]
                match = sum(1 for i in range(len(d20)) if key[i] == tot_key[i])
                if match > len(d20) * 0.3:
                    print(f"  {name} start={start} key={kname}: totient offset={offset} match={match}/{len(d20)} ({100*match/len(d20):.1f}%)")
            
            # Check if key has pattern: constant, repeating, arithmetic
            if len(set(key[:30])) <= 3:
                print(f"  {name} start={start} key={kname}: SIMPLE KEY! unique values in first 30: {set(key[:30])}")
            
        if start >= 30: break  # Don't check too many offsets

# ===== SECTION 3: PRIME TRANSPOSITION =====
print(f"\n{'='*80}")
print("SECTION 3: Prime-position transposition on P20")
print("=" * 80)

# Extract runes at prime positions vs non-prime positions
prime_set = set(PRIMES[:200])  # primes up to ~1200
prime_pos_vals = [d20[i] for i in range(len(d20)) if i in prime_set]
nonprime_pos_vals = [d20[i] for i in range(len(d20)) if i not in prime_set]
print(f"  Runes at PRIME positions: {len(prime_pos_vals)}, IoC={ioc29(prime_pos_vals):.4f}")
print(f"  Runes at NON-PRIME positions: {len(nonprime_pos_vals)}, IoC={ioc29(nonprime_pos_vals):.4f}")

# Try reading runes in prime order vs original order
# "Rearranging by primes": read position prime[0]=2, prime[1]=3, prime[2]=5,...
prime_order = [d20[PRIMES[i]] for i in range(len(PRIMES)) if PRIMES[i] < len(d20)]
remaining = [d20[i] for i in range(len(d20)) if i not in set(PRIMES[:len(prime_order)])]
print(f"  Prime-ordered runes ({len(prime_order)}): IoC={ioc29(prime_order):.4f}")
print(f"  Remaining runes ({len(remaining)}): IoC={ioc29(remaining):.4f}")

# Interleave prime-position and non-prime-position runes
for arrangement in ['prime_first', 'nonprime_first', 'interleave']:
    if arrangement == 'prime_first':
        rearranged = prime_pos_vals + nonprime_pos_vals
    elif arrangement == 'nonprime_first':
        rearranged = nonprime_pos_vals + prime_pos_vals
    else:
        rearranged = []
        for i in range(max(len(prime_pos_vals), len(nonprime_pos_vals))):
            if i < len(prime_pos_vals): rearranged.append(prime_pos_vals[i])
            if i < len(nonprime_pos_vals): rearranged.append(nonprime_pos_vals[i])
    
    # Apply totient cipher after transposition
    for offset in [0, 1, 2, 3, 5, 10, 50, 100]:
        tot_key = [(PRIMES[i+offset]-1) % 29 for i in range(len(rearranged))]
        dec = [(rearranged[i] - tot_key[i]) % 29 for i in range(len(rearranged))]
        ic = ioc29(dec)
        sc = score_english(dec)
        if ic > 1.3 or sc > 50:
            print(f"  {arrangement} + totient offset={offset}: IoC={ic:.4f} score={sc}")
            print(f"    {text(dec)[:100]}")

# ===== SECTION 4: COLUMNAR TRANSPOSITION WITH PRIME-BASED COLUMNS =====
print(f"\n{'='*80}")
print("SECTION 4: Columnar transposition recovery")
print("=" * 80)

# Try reading P20 in columns of various widths, then check IoC
for width in range(2, 60):
    rows = (len(d20) + width - 1) // width
    # Read column by column
    col_read = []
    for c in range(width):
        for r in range(rows):
            idx = r * width + c
            if idx < len(d20):
                col_read.append(d20[idx])
    
    ic = ioc29(col_read[:len(d20)])
    if ic > 1.15:
        print(f"  width={width}: IoC={ic:.4f} (reading columns)")
    
    # Also try: read by column, then apply totient
    for offset in [0, 1]:
        tot_key = [(PRIMES[i+offset]-1) % 29 for i in range(len(col_read))]
        dec = [(col_read[i] - tot_key[i]) % 29 for i in range(min(len(col_read), len(tot_key)))]
        ic2 = ioc29(dec)
        if ic2 > 1.3:
            print(f"  width={width} + totient off={offset}: IoC={ic2:.4f}")
            print(f"    {text(dec)[:80]}")

# ===== SECTION 5: AUTOKEY WITH DEOR SEED =====
print(f"\n{'='*80}")
print("SECTION 5: Autokey cipher with Deor poem as seed")
print("=" * 80)

for name, seed_gp in [("OE", deor_oe_gp), ("Modern", deor_modern_gp)]:
    for seed_len in [5, 10, 20, 50, 100]:
        if seed_len > len(seed_gp): continue
        seed = seed_gp[:seed_len]
        
        for mode in ['SUB', 'ADD']:
            # Autokey: key extends with plaintext
            key = list(seed)
            result = []
            for i in range(len(d20)):
                k = key[i] if i < len(key) else key[-1]
                if mode == 'SUB': p = (d20[i] - k) % 29
                else: p = (d20[i] + k) % 29
                result.append(p)
                if i >= len(key) - 1:
                    key.append(p)
            
            ic = ioc29(result)
            sc = score_english(result)
            if ic > 1.3 or sc > 50:
                print(f"  {name} seed_len={seed_len} {mode}: IoC={ic:.4f} score={sc}")
                print(f"    {text(result)[:100]}")

# ===== SECTION 6: DEOR RUNNING KEY ON ALL UNSOLVED PAGES =====
print(f"\n{'='*80}")
print("SECTION 6: Deor running key on ALL unsolved pages (extended)")
print("=" * 80)

unsolved = list(range(17, 55))
for pn in unsolved:
    d = load_page(pn)
    if not d: continue
    
    for name, key_gp in [("OE", deor_oe_gp), ("Mod", deor_modern_gp)]:
        if len(key_gp) < len(d):
            rk = key_gp * (len(d) // len(key_gp) + 1)
        else:
            rk = key_gp
        
        for start in range(0, min(20, max(1, len(rk) - len(d)))):
            ks = rk[start:start+len(d)]
            if len(ks) < len(d): continue
            
            for mode in ['SUB', 'ADD', 'BEAU']:
                if mode == 'SUB': dec = [(d[i] - ks[i]) % 29 for i in range(len(d))]
                elif mode == 'ADD': dec = [(d[i] + ks[i]) % 29 for i in range(len(d))]
                else: dec = [(ks[i] - d[i]) % 29 for i in range(len(d))]
                
                ic = ioc29(dec)
                sc = score_english(dec)
                if ic > 1.35 or sc > 80:
                    print(f"  P{pn:02d} {name} start={start} {mode}: IoC={ic:.4f} score={sc}")
                    print(f"    {text(dec)[:100]}")

# ===== SECTION 7: SHIFTED PRIME SEQUENCE ATTACK =====
print(f"\n{'='*80}")
print("SECTION 7: Novel prime key derivations on P20")
print("=" * 80)

# Try: prime[i]^2 mod 29, prime[i]*i mod 29, etc.
key_fns = {
    'p_mod29': lambda i,off: PRIMES[i+off] % 29,
    'p-1_mod29': lambda i,off: (PRIMES[i+off]-1) % 29,
    'p^2_mod29': lambda i,off: (PRIMES[i+off]**2) % 29,
    'p*i_mod29': lambda i,off: (PRIMES[i+off]*i) % 29,
    'p+i_mod29': lambda i,off: (PRIMES[i+off]+i) % 29,
    'p_xor_i_mod29': lambda i,off: (PRIMES[i+off]^i) % 29,
    'prime_idx_mod29': lambda i,off: (i+off) % 29,
    'p_digit_sum_mod29': lambda i,off: sum(int(d) for d in str(PRIMES[i+off])) % 29,
    'gap_mod29': lambda i,off: (PRIMES[i+off+1]-PRIMES[i+off]) % 29 if i+off+1 < len(PRIMES) else 0,
}

best_results = []
for kname, kfn in key_fns.items():
    for offset in range(0, 500, 1):
        if offset + len(d20) + 1 >= len(PRIMES): break
        try:
            key = [kfn(i, offset) for i in range(len(d20))]
        except:
            break
        
        for mode in ['SUB', 'ADD', 'BEAU']:
            if mode == 'SUB': dec = [(d20[i] - key[i]) % 29 for i in range(len(d20))]
            elif mode == 'ADD': dec = [(d20[i] + key[i]) % 29 for i in range(len(d20))]
            else: dec = [(key[i] - d20[i]) % 29 for i in range(len(d20))]
            
            ic = ioc29(dec)
            if ic > 1.25:
                sc = score_english(dec)
                best_results.append((ic, sc, kname, offset, mode, text(dec)[:60]))

best_results.sort(reverse=True)
print("  Top 15 results:")
for ic, sc, kname, off, mode, t in best_results[:15]:
    print(f"    {kname} off={off} {mode}: IoC={ic:.4f} score={sc} -- {t}")

print(f"\n{'='*80}")
print("DEOR ATTACK COMPLETE")
print("=" * 80)
