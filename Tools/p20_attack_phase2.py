"""
P20 Attack Phase 2:
1. Verify if Latin IoC 1.8052 is artifact of GP digraph expansion
2. Try 47-char Vigenere with Deor poem windows 
3. Try first 47 primes mod 29 as key
4. Try P19's key rotations on P20
5. Try F-skip totient higher offsets
"""
import os
import random
from collections import Counter

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C4':11,'\u16C7':12,'\u16C8':13,'\u16C9':14,
    '\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,'\u16D7':19,'\u16DA':20,'\u16DD':21,
    '\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,'\u16A3':26,'\u16E1':27,'\u16E0':28
}
LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]

def ioc29(data):
    if len(data) <= 1: return 0
    freq = Counter(data)
    n = len(data)
    return sum(f*(f-1) for f in freq.values()) / (n*(n-1)) * 29

def ioc26(text):
    """IoC on Latin text using 26 letters."""
    t = text.upper()
    chars = [c for c in t if c.isalpha()]
    if len(chars) <= 1: return 0
    freq = Counter(chars)
    n = len(chars)
    return sum(f*(f-1) for f in freq.values()) / (n*(n-1)) * 26

def to_latin(indices):
    return ''.join(LATIN[i] for i in indices)

def sieve(n):
    s = [True] * (n + 1)
    s[0] = s[1] = False
    for i in range(2, int(n**0.5) + 1):
        if s[i]:
            for j in range(i*i, n+1, i):
                s[j] = False
    return [i for i in range(2, n+1) if s[i]]

def totient(n):
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

def load_runes(pg):
    for p in [f'LiberPrimus/pages/page_{pg:02d}/runes.txt', f'LiberPrimus/pages/page_{pg}/runes.txt']:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                return [GP[c] for c in f.read() if c in GP]
    return None

LATIN_TO_VAL = {
    'A': 24, 'B': 17, 'C': 5, 'D': 23, 'E': 18, 'F': 0, 'G': 6, 'H': 8,
    'I': 10, 'J': 11, 'K': 5, 'L': 20, 'M': 19, 'N': 9, 'O': 3, 'P': 13,
    'Q': 5, 'R': 4, 'S': 15, 'T': 16, 'U': 1, 'V': 1, 'W': 7, 'X': 14,
    'Y': 26, 'Z': 15
}

def tokenize_oe(text):
    vals = []
    for ch in text:
        c = ch.upper()
        if c in LATIN_TO_VAL:
            vals.append(LATIN_TO_VAL[c])
        elif c in ('Þ','þ','Ð','ð'):
            vals.append(2)
        elif c in ('Æ','æ'):
            vals.append(25)
    return vals

DEOR_TEXT = """Welund him be wurman wræces cunnade,
anhydig eorl earfoþa dreag,
hæfde him to gesiþþe sorge ond longaþ,
wintercealde wræce; wean oft onfond,
siþþan hine Niðhad on nede legde,
swoncre seonobende on syllan monn.
Þæs ofereode, þisses swa mæg!
Beadohilde ne wæs hyre broþra deaþ
on sefan swa sar swa hyre sylfre þing,
þæt heo gearolice ongieten hæfde
þæt heo eacen wæs; æfre ne meahte
þriste geþencan, hu ymb þæt sceolde.
Þæs ofereode, þisses swa mæg!
We þæt Mæðhilde monge gefrugnon
wurdon grundlease Geates frige,
þæt hi seo sorglufu slæp ealle binom.
Þæs ofereode, þisses swa mæg!
Ðeodric ahte þritig wintra
Mæringa burg; þæt wæs monegum cuþ.
Þæs ofereode, þisses swa mæg!
We geascodan Eormanrices
wylfenne geþoht; ahte wide folc
Gotena rices. Þæt wæs grim cyning.
Sæt secg monig sorgum gebunden,
wean on wenan, wyscte geneahhe
þæt þæs cynerices ofercumen wære.
Þæs ofereode, þisses swa mæg!
Siteð sorgcearig, sælum bidæled,
on sefan sweorceð, sylfum þinceð
þæt sy endeleas earfoða dæl.
Mæg þonne geþencan, þæt geond þas woruld
witig dryhten wendeþ geneahhe,
eorle monegum are gesceawað,
wislicne blæd, sumum weana dæl.
Þæt ic bi me sylfum secgan wille,
þæt ic hwile wæs Heodeninga scop,
dryhtne dyre. Me wæs Deor nama.
Ahte ic fela wintra folgað tilne,
holdne hlaford, oþþæt Heorrenda nu,
leoðcræftig monn londryht geþah,
þæt me eorla hleo ær gesealde.
Þæs ofereode, þisses swa mæg!"""

deor_vals = tokenize_oe(DEOR_TEXT)
p20 = load_runes(20)

print(f"P20: {len(p20)} runes")
print(f"Deor: {len(deor_vals)} GP values")
print()

# ================================================================
# 1. VERIFY: Is Latin IoC 1.8 an artifact?
# ================================================================
print("=== IoC ARTIFACT CHECK ===")

# Generate random GP text, convert to Latin, check IoC
random.seed(42)
for trial in range(3):
    rand_gp = [random.randint(0, 28) for _ in range(812)]
    rand_latin = to_latin(rand_gp)
    latin_ioc = ioc26(rand_latin)
    gp_ioc = ioc29(rand_gp)
    print(f"Random GP (812): GP IoC={gp_ioc:.4f}, Latin IoC(26)={latin_ioc:.4f} (Latin chars: {len(rand_latin)})")

# Check P20
p20_latin = to_latin(p20)
print(f"P20: GP IoC={ioc29(p20):.4f}, Latin IoC(26)={ioc26(p20_latin):.4f} (Latin chars: {len(p20_latin)})")

# Check with shift 16
p20_shift16 = [(v + 16) % 29 for v in p20]
p20_s16_latin = to_latin(p20_shift16)
print(f"P20+16: GP IoC={ioc29(p20_shift16):.4f}, Latin IoC(26)={ioc26(p20_s16_latin):.4f} (Latin chars: {len(p20_s16_latin)})")
print()

# Extract non-prime positions and check
primes = sieve(900)
primes_set = set(primes)
non_prime_pos_runes = [p20[i] for i in range(len(p20)) if (i+1) not in primes_set]
non_prime_shifted = [(v + 16) % 29 for v in non_prime_pos_runes]
np_latin = to_latin(non_prime_shifted)
print(f"Non-prime(shift16): {len(non_prime_pos_runes)} runes, GP IoC={ioc29(non_prime_shifted):.4f}, Latin IoC(26)={ioc26(np_latin):.4f}")

# Compare to random subset
rand_sub = [random.randint(0, 28) for _ in range(671)]
rand_sub_latin = to_latin(rand_sub)
print(f"Random 671: GP IoC={ioc29(rand_sub):.4f}, Latin IoC(26)={ioc26(rand_sub_latin):.4f}")
print()

# ================================================================
# 2. 47-CHAR VIGENERE WITH DEOR WINDOWS
# ================================================================
print("=== 47-CHAR VIGENERE WITH DEOR POEM WINDOWS ===")
KEY47_P19 = [24,15,2,24,4,21,11,10,20,16,9,19,26,11,7,5,11,6,27,8,22,25,21,16,25,0,27,9,21,7,27,15,21,9,3,16,5,22,18,4,5,18,23,28,28,28,28]

best_deor_window = []
for offset in range(len(deor_vals) - 46):
    key = deor_vals[offset:offset+47]
    for mode_name, mode_fn in [('SUB', lambda c, k: (c - k) % 29),
                                ('ADD', lambda c, k: (c + k) % 29),
                                ('BEAU', lambda c, k: (k - c) % 29)]:
        plain = [mode_fn(p20[i], key[i % 47]) for i in range(len(p20))]
        ic = ioc29(plain)
        if ic > 1.25:
            best_deor_window.append((ic, offset, mode_name, to_latin(plain[:60])))

best_deor_window.sort(reverse=True)
if best_deor_window:
    print(f"Found {len(best_deor_window)} hits:")
    for ic, off, mode, text in best_deor_window[:10]:
        print(f"  offset={off} mode={mode} IoC={ic:.4f} | {text}")
else:
    print("No hits above IoC 1.25")
print()

# ================================================================
# 3. FIRST 47 PRIMES MOD 29 AS KEY
# ================================================================
print("=== FIRST 47 PRIMES MOD 29 AS KEY ===")
all_primes = sieve(250)
first47primes = all_primes[:47]
key_primes47 = [p % 29 for p in first47primes]
print(f"First 47 primes: {first47primes}")
print(f"Mod 29: {key_primes47}")

for mode_name, mode_fn in [('SUB', lambda c, k: (c - k) % 29),
                            ('ADD', lambda c, k: (c + k) % 29),
                            ('BEAU', lambda c, k: (k - c) % 29)]:
    plain = [mode_fn(p20[i], key_primes47[i % 47]) for i in range(len(p20))]
    ic = ioc29(plain)
    print(f"  {mode_name}: IoC={ic:.4f} | {to_latin(plain[:60])}")

# Try sorted primes
sorted_key = sorted(key_primes47)
print(f"\nSorted: {sorted_key}")
for mode_name, mode_fn in [('SUB', lambda c, k: (c - k) % 29),
                            ('ADD', lambda c, k: (c + k) % 29)]:
    plain = [mode_fn(p20[i], sorted_key[i % 47]) for i in range(len(p20))]
    ic = ioc29(plain)
    print(f"  {mode_name}: IoC={ic:.4f}")

# Try reverse sorted
rev_key = sorted(key_primes47, reverse=True)
for mode_name, mode_fn in [('SUB', lambda c, k: (c - k) % 29),
                            ('ADD', lambda c, k: (c + k) % 29)]:
    plain = [mode_fn(p20[i], rev_key[i % 47]) for i in range(len(p20))]
    ic = ioc29(plain)
    print(f"  Rev {mode_name}: IoC={ic:.4f}")

# Totient of first 47 primes mod 29
key_tot47 = [totient(p) % 29 for p in first47primes]
print(f"\nTotient: {key_tot47}")
for mode_name, mode_fn in [('SUB', lambda c, k: (c - k) % 29),
                            ('ADD', lambda c, k: (c + k) % 29),
                            ('BEAU', lambda c, k: (k - c) % 29)]:
    plain = [mode_fn(p20[i], key_tot47[i % 47]) for i in range(len(p20))]
    ic = ioc29(plain)
    print(f"  {mode_name}: IoC={ic:.4f} | {to_latin(plain[:40])}")

print()

# ================================================================
# 4. P19 KEY ROTATIONS ON P20
# ================================================================
print("=== P19 KEY (47 values) ROTATIONS ON P20 ===")
best_rotations = []
for rot in range(47):
    rotated_key = KEY47_P19[rot:] + KEY47_P19[:rot]
    for mode_name, mode_fn in [('SUB', lambda c, k: (c - k) % 29),
                                ('ADD', lambda c, k: (c + k) % 29),
                                ('BEAU', lambda c, k: (k - c) % 29)]:
        plain = [mode_fn(p20[i], rotated_key[i % 47]) for i in range(len(p20))]
        ic = ioc29(plain)
        if ic > 1.15:
            best_rotations.append((ic, rot, mode_name, to_latin(plain[:60])))

best_rotations.sort(reverse=True)
if best_rotations:
    print(f"Found {len(best_rotations)} hits above IoC 1.15:")
    for ic, rot, mode, text in best_rotations[:5]:
        print(f"  rot={rot} mode={mode} IoC={ic:.4f} | {text}")
else:
    print("No hits above IoC 1.15")
print()

# ================================================================
# 5. F-SKIP TOTIENT HIGH OFFSETS (5000-20000)
# ================================================================
print("=== F-SKIP TOTIENT HIGH OFFSETS (5000-20000) ON P20 ===")
big_primes = sieve(250000)
big_tot = [totient(p) % 29 for p in big_primes[:21000]]

best_fskip_high = []
for offset in range(5000, 20000):
    for mode_name, mode_fn in [('SUB', lambda c, k: (c - k) % 29),
                                ('ADD', lambda c, k: (c + k) % 29)]:
        plain = []
        ki = offset
        for ci in p20:
            if ki >= len(big_tot):
                break
            plain.append(mode_fn(ci, big_tot[ki]))
            if plain[-1] != 0:  # F-skip
                ki += 1
        if len(plain) == len(p20):
            ic = ioc29(plain)
            if ic > 1.25:
                best_fskip_high.append((ic, offset, mode_name, to_latin(plain[:50])))

best_fskip_high.sort(reverse=True)
if best_fskip_high:
    print(f"Found {len(best_fskip_high)} hits:")
    for ic, off, mode, text in best_fskip_high[:10]:
        print(f"  offset={off} mode={mode} IoC={ic:.4f} | {text}")
else:
    print("No F-skip totient hits (offsets 5000-20000)")
print()

# ================================================================
# 6. NON-F-SKIP TOTIENT (no F-skip) ON P20
# ================================================================
print("=== NON-F-SKIP TOTIENT ON P20 (offsets 0-20000) ===")
best_nofskip = []
for offset in range(20000):
    for mode_name, mode_fn in [('SUB', lambda c, k: (c - k) % 29),
                                ('ADD', lambda c, k: (c + k) % 29)]:
        if offset + len(p20) > len(big_tot):
            break
        plain = [mode_fn(p20[i], big_tot[offset + i]) for i in range(len(p20))]
        ic = ioc29(plain)
        if ic > 1.25:
            best_nofskip.append((ic, offset, mode_name, to_latin(plain[:50])))

best_nofskip.sort(reverse=True)
if best_nofskip:
    print(f"Found {len(best_nofskip)} hits:")
    for ic, off, mode, text in best_nofskip[:10]:
        print(f"  offset={off} mode={mode} IoC={ic:.4f} | {text}")
else:
    print("No non-F-skip totient hits (offsets 0-20000)")
print()

# ================================================================
# 7. VIGENERE KEY FROM DEOR TITLE "DEOR"
# ================================================================
print("=== SHORT DEOR KEYS ===")
# DEOR = D(23), E(18), O(3), R(4)
deor_key_short = [23, 18, 3, 4]
for mode_name, mode_fn in [('SUB', lambda c, k: (c - k) % 29),
                            ('ADD', lambda c, k: (c + k) % 29),
                            ('BEAU', lambda c, k: (k - c) % 29)]:
    plain = [mode_fn(p20[i], deor_key_short[i % 4]) for i in range(len(p20))]
    ic = ioc29(plain)
    print(f"  DEOR {mode_name}: IoC={ic:.4f}")

# OFEREODE = O(3),F(0),E(18),R(4),E(18),O(3),D(23),E(18)
ofe_key = [3, 0, 18, 4, 18, 3, 23, 18]
for mode_name, mode_fn in [('SUB', lambda c, k: (c - k) % 29),
                            ('ADD', lambda c, k: (c + k) % 29)]:
    plain = [mode_fn(p20[i], ofe_key[i % 8]) for i in range(len(p20))]
    ic = ioc29(plain)
    print(f"  OFEREODE {mode_name}: IoC={ic:.4f}")

# THAESOFEREODE
tasofe = tokenize_oe("thaesofereode")
for mode_name, mode_fn in [('SUB', lambda c, k: (c - k) % 29),
                            ('ADD', lambda c, k: (c + k) % 29)]:
    plain = [mode_fn(p20[i], tasofe[i % len(tasofe)]) for i in range(len(p20))]
    ic = ioc29(plain)
    print(f"  THAESOFEREODE({len(tasofe)}) {mode_name}: IoC={ic:.4f}")

# THISSESSWAMAG
tssm = tokenize_oe("thissesswamag")
for mode_name, mode_fn in [('SUB', lambda c, k: (c - k) % 29),
                            ('ADD', lambda c, k: (c + k) % 29)]:
    plain = [mode_fn(p20[i], tssm[i % len(tssm)]) for i in range(len(p20))]
    ic = ioc29(plain)
    print(f"  THISSESSWAMAG({len(tssm)}) {mode_name}: IoC={ic:.4f}")

print()

# ================================================================
# 8. ALL P63 KEYWORDS ON P20
# ================================================================
print("=== P63 KEYWORDS ON P20 ===")
keywords = ['VOID','AETHEREAL','CARNAL','ANALOG','MOURNFUL','CABAL','SHADOWS','OBSCURA','MOBIUS','BUFFERS',
            'DIVINITY','FIRFUMFERENFE','CIRCUMFERENCE','CONSUMPTION','INSTAR']
for kw in keywords:
    kw_vals = tokenize_oe(kw)
    for mode_name, mode_fn in [('SUB', lambda c, k: (c - k) % 29),
                                ('ADD', lambda c, k: (c + k) % 29),
                                ('BEAU', lambda c, k: (k - c) % 29)]:
        plain = [mode_fn(p20[i], kw_vals[i % len(kw_vals)]) for i in range(len(p20))]
        ic = ioc29(plain)
        if ic > 1.2:
            print(f"  {kw} {mode_name}: IoC={ic:.4f}")

print()
print("=== ATTACK COMPLETE ===")
