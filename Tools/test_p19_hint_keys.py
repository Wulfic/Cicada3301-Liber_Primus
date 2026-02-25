"""
TEST HYPOTHESES FROM P19 HINT:
"REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR"

Concrete tests:
1. Keywords from hint: PRIMES, DEOR, PATH, REARRANGING, PRIMENUMBERS
2. Deor at prime indices: key[i] = deor[prime(i) % len(deor)]
3. Deor at REARRANGED prime positions (reversed, sorted by value, etc.)
4. Prime sequence as direct key: key = [2,3,5,7,11,...] mod 29
5. Use P19 43-char key as repeating key for other pages
6. Gematria value of "PRIMES" as key
7. Primes rearranged = sorted/permuted prime-position runes from each page
"""
import os, math
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
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':14}

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

def sieve_primes(n):
    is_prime = [True] * (n+1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5)+1):
        if is_prime[i]:
            for j in range(i*i, n+1, i):
                is_prime[j] = False
    return [i for i in range(2, n+1) if is_prime[i]]

def first_n_primes(n):
    primes = []
    candidate = 2
    while len(primes) < n:
        if all(candidate % p != 0 for p in primes if p*p <= candidate):
            primes.append(candidate)
        candidate += 1
    return primes

def tokenize_oe_text(text):
    text = text.upper().replace(' ','').replace('\n','')
    for ch in '.,;:!?\'"()[]{}–—-0123456789':
        text = text.replace(ch, '')
    values = []
    i = 0
    while i < len(text):
        if text[i] in ('Þ','Ð'):
            values.append(2); i += 1
        elif text[i] == 'Æ':
            values.append(25); i += 1
        elif i + 1 < len(text):
            d = text[i:i+2]
            if d == 'TH': values.append(2); i += 2
            elif d == 'NG': values.append(21); i += 2
            elif d == 'OE': values.append(22); i += 2
            elif d == 'AE': values.append(25); i += 2
            elif d in ('IA','IO'): values.append(27); i += 2
            elif d == 'EA': values.append(28); i += 2
            elif d == 'EO': values.append(12); i += 2
            elif text[i] in ENG2GP: values.append(ENG2GP[text[i]]); i += 1
            else: i += 1
        elif text[i] in ENG2GP: values.append(ENG2GP[text[i]]); i += 1
        else: i += 1
    return values

DEOR_OE = """Welund him be wurman wræces cunnade,
anhydig eorl earfoþa dreag,
hæfde him to gesiþþe sorge ond longaþ,
wintercealde wræce; wean oft onfond,
siþþan hine Niðhad on nede legde,
swoncre seonobende on syllan monn.
Þæs ofereode, þisses swa mæg.
Beadohilde ne wæs hyre broþra deaþ
on sefan swa sar swa hyre sylfre þing,
þæt heo gearolice ongieten hæfde
þæt heo eacen wæs; æfre ne meahte
þriste geþencan, hu ymb þæt sceolde.
Þæs ofereode, þisses swa mæg.
We þæt Mæðhilde monge gefrugnon
wurdon grundlease Geates frige,
þæt hi seo sorglufu slæp ealle binom.
Þæs ofereode, þisses swa mæg.
Ðeodric ahte þritig wintra
Mæringa burg; þæt wæs monegum cuþ.
Þæs ofereode, þisses swa mæg.
We geascodan Eormanrices
wylfenne geþoht; ahte wide folc
Gotena rices. Þæt wæs grim cyning.
Sæt secg monig sorgum gebunden,
wean on wenan, wyscte geneahhe
þæt þæs cynerices ofercumen wære.
Þæs ofereode, þisses swa mæg.
Siteð sorgcearig, sælum bedæled,
on sefan sweorceð, sylfum þinceð
þæt sy endeleas earfoða dæl.
Mæg þonne geþencan, þæt geond þas woruld
witig Dryhten wendeþ geneahhe,
eorle monegum are gesceawað,
wislicne blæd, sumum weana dæl.
Þæt ic bi me sylfum secgan wille,
þæt ic hwile wæs Heodeninga scop,
dryhtne dyre. Me wæs Deor noma.
Ahte ic fela wintra folgað tilne,
holdne hlaford, oþþæt Heorrenda nu,
leoðcræftig monn londryht geþah,
þæt me eorla hleo ær gesealde.
Þæs ofereode, þisses swa mæg."""

deor = tokenize_oe_text(DEOR_OE)
print(f"Deor tokens: {len(deor)}")

# Load unsolved pages
pages = {}
for pg in range(17, 55):
    data = load_page(pg)
    if data and len(data) > 0:
        pages[pg] = data
# Also P71
pg71 = load_page(71)
if pg71:
    pages[71] = pg71

print(f"Loaded {len(pages)} unsolved pages")

# ================================================================
# TEST 1: Keywords from P19 hint as Vigenère keys
# ================================================================
print("\n" + "="*70)
print("TEST 1: KEYWORDS AS VIGENÈRE KEYS")
print("="*70)

keywords = {
    "PRIMES": [13, 4, 10, 19, 18, 15],
    "DEOR": [23, 18, 3, 4],
    "PATH": [13, 24, 16, 8],
    "REARRANGING": [4, 18, 24, 4, 4, 24, 9, 6, 10, 9, 6],
    "PRIMENUMBERS": [13, 4, 10, 19, 18, 9, 1, 19, 17, 18, 4, 15],
    "THEDEOR": [16, 8, 18, 23, 18, 3, 4],
    "NOTCOERCED": [9, 3, 16, 5, 3, 18, 4, 5, 18, 23],
    "DIVINITY": [23, 10, 1, 10, 9, 10, 16, 26],
    "WELCOME": [7, 18, 20, 5, 3, 19, 18],
    "PILGRIM": [13, 10, 20, 6, 4, 10, 19],
    "WISDOM": [7, 10, 15, 23, 3, 19],
    "EMERGENCE": [18, 19, 18, 4, 6, 18, 9, 5, 18],
    "CONSUMPTION": [5, 3, 9, 15, 1, 19, 13, 16, 10, 3, 9],
    "CIRCUMFERENCE": [5, 10, 4, 5, 1, 19, 0, 18, 4, 18, 9, 5, 18],
    "ADHERENCE": [24, 23, 8, 18, 4, 18, 9, 5, 18],
    "AN": [24, 9],
    "INSTAR": [10, 9, 15, 16, 24, 4],
}

for kw_name, key in keywords.items():
    for pg in sorted(pages):
        vals = pages[pg]
        n = len(vals)
        klen = len(key)
        
        for mode in ['SUB', 'ADD', 'BEAU']:
            result = []
            for i in range(n):
                k = key[i % klen]
                c = vals[i]
                if mode == 'SUB':
                    result.append((c - k) % 29)
                elif mode == 'ADD':
                    result.append((c + k) % 29)
                else:
                    result.append((k - c) % 29)
            
            ic = ioc(result)
            if ic > 1.5:
                print(f"  ** {kw_name} {mode} P{pg:02d}: IoC={ic:.4f} | {to_eng(result)[:60]}")
            
            # Also try F-skip
            result_fs = []
            ki = 0
            for i in range(n):
                c = vals[i]
                if c == 0:
                    result_fs.append(0)
                else:
                    k = key[ki % klen]
                    if mode == 'SUB':
                        result_fs.append((c - k) % 29)
                    elif mode == 'ADD':
                        result_fs.append((c + k) % 29)
                    else:
                        result_fs.append((k - c) % 29)
                    ki += 1
            
            ic_fs = ioc(result_fs)
            if ic_fs > 1.5:
                print(f"  ** {kw_name} {mode}+Fskip P{pg:02d}: IoC={ic_fs:.4f} | {to_eng(result_fs)[:60]}")

# ================================================================
# TEST 2: Deor at prime indices as running key
# ================================================================
print("\n" + "="*70)
print("TEST 2: DEOR AT PRIME INDICES AS KEY")
print("="*70)

# For each page, key[i] = deor[prime(i) % len(deor)]
# where prime(i) is the i-th prime number
max_needed = max(len(v) for v in pages.values())
primes_needed = first_n_primes(max_needed)
print(f"Max primes needed: {max_needed}, largest prime: {primes_needed[-1]}")

for pg in sorted(pages):
    vals = pages[pg]
    n = len(vals)
    
    for mode in ['SUB', 'ADD', 'BEAU']:
        # key[i] = deor[prime(i) mod len(deor)]
        key = [deor[primes_needed[i] % len(deor)] for i in range(n)]
        
        if mode == 'SUB':
            result = [(vals[i] - key[i]) % 29 for i in range(n)]
        elif mode == 'ADD':
            result = [(vals[i] + key[i]) % 29 for i in range(n)]
        else:
            result = [(key[i] - vals[i]) % 29 for i in range(n)]
        
        ic = ioc(result)
        if ic > 1.3:
            print(f"  P{pg:02d} {mode}: IoC={ic:.4f} | {to_eng(result)[:60]}")

# Also try: position-indexed into deor via primes
# key[i] = deor[prime_position] where we check if position i is prime
print("\n  Variant: deor sampled at prime positions matching text positions")
all_primes_set = set(sieve_primes(2000))
for pg in sorted(pages):
    vals = pages[pg]
    n = len(vals)
    
    for mode in ['SUB', 'ADD', 'BEAU']:
        # key[i] = deor[i] if i is prime, else deor[nearest_prime(i)]
        # Actually, simpler: key uses ONLY prime positions from deor
        prime_deor_vals = [deor[i] for i in range(len(deor)) if i in all_primes_set]
        key = [prime_deor_vals[i % len(prime_deor_vals)] for i in range(n)]
        
        if mode == 'SUB':
            result = [(vals[i] - key[i]) % 29 for i in range(n)]
        elif mode == 'ADD':
            result = [(vals[i] + key[i]) % 29 for i in range(n)]
        else:
            result = [(key[i] - vals[i]) % 29 for i in range(n)]
        
        ic = ioc(result)
        if ic > 1.3:
            print(f"  P{pg:02d} {mode} (prime-sampled deor): IoC={ic:.4f} | {to_eng(result)[:60]}")

# ================================================================
# TEST 3: Prime sequence as direct key
# ================================================================
print("\n" + "="*70)
print("TEST 3: PRIME SEQUENCE AS DIRECT KEY")
print("="*70)

for pg in sorted(pages):
    vals = pages[pg]
    n = len(vals)
    
    for mode in ['SUB', 'ADD', 'BEAU']:
        # key[i] = prime(i) mod 29
        key = [primes_needed[i] % 29 for i in range(n)]
        
        if mode == 'SUB':
            result = [(vals[i] - key[i]) % 29 for i in range(n)]
        elif mode == 'ADD':
            result = [(vals[i] + key[i]) % 29 for i in range(n)]
        else:
            result = [(key[i] - vals[i]) % 29 for i in range(n)]
        
        ic = ioc(result)
        if ic > 1.3:
            print(f"  P{pg:02d} {mode}: IoC={ic:.4f} | {to_eng(result)[:60]}")

# ================================================================
# TEST 4: P19 key (43 values) as repeating key for other pages
# ================================================================
print("\n" + "="*70)
print("TEST 4: P19 KEY AS REPEATING KEY")
print("="*70)

p19_key = [24,15,2,24,4,21,11,10,20,16,9,19,26,11,7,5,11,6,27,8,22,25,21,16,25,0,27,9,21,7,27,15,21,9,3,16,5,22,18,4,5,18,23]
p19_klen = len(p19_key)

for pg in sorted(pages):
    vals = pages[pg]
    n = len(vals)
    
    for mode in ['SUB', 'ADD', 'BEAU']:
        result = []
        for i in range(n):
            k = p19_key[i % p19_klen]
            c = vals[i]
            if mode == 'SUB':
                result.append((c - k) % 29)
            elif mode == 'ADD':
                result.append((c + k) % 29)
            else:
                result.append((k - c) % 29)
        
        ic = ioc(result)
        if ic > 1.3:
            print(f"  P{pg:02d} {mode}: IoC={ic:.4f} | {to_eng(result)[:60]}")

# ================================================================
# TEST 5: P19 PLAINTEXT as continuing key for P20+
# ================================================================
print("\n" + "="*70)
print("TEST 5: P19 PLAINTEXT AS CONTINUING KEY")
print("="*70)

p19_plain = "REARRANGINGTHEPRIMESNUMBERSWILLSHOWAPATHTOTHEDEOR"
p19_plain_gp = [ENG2GP[c] for c in p19_plain if c in ENG2GP]
print(f"P19 plaintext as GP: {len(p19_plain_gp)} values")
print(f"  Values: {p19_plain_gp}")

# Use this as repeating key
for pg in sorted(pages):
    if pg == 19: continue
    vals = pages[pg]
    n = len(vals)
    klen = len(p19_plain_gp)
    
    for mode in ['SUB', 'ADD', 'BEAU']:
        result = []
        for i in range(n):
            k = p19_plain_gp[i % klen]
            c = vals[i]
            if mode == 'SUB':
                result.append((c - k) % 29)
            elif mode == 'ADD':
                result.append((c + k) % 29)
            else:
                result.append((k - c) % 29)
        
        ic = ioc(result)
        if ic > 1.3:
            print(f"  P{pg:02d} {mode}: IoC={ic:.4f} | {to_eng(result)[:60]}")

# ================================================================
# TEST 6: Totient of primes as key (like P55/P73)
# ================================================================
print("\n" + "="*70)
print("TEST 6: TOTIENT OF PRIMES AS KEY (P55/P73 method)")
print("="*70)

for pg in sorted(pages):
    vals = pages[pg]
    n = len(vals)
    
    # Standard totient: plain[i] = (cipher[i] - (prime[i]-1)) % 29
    for offset in range(5):
        result = [(vals[i] - (primes_needed[i+offset] - 1)) % 29 for i in range(n)]
        ic = ioc(result)
        if ic > 1.3:
            print(f"  P{pg:02d} offset={offset}: IoC={ic:.4f} | {to_eng(result)[:60]}")
        
        # F-skip variant
        result_fs = []
        ki = offset
        for i in range(n):
            if vals[i] == 0:
                result_fs.append(0)
            else:
                result_fs.append((vals[i] - (primes_needed[ki] - 1)) % 29)
                ki += 1
        ic_fs = ioc(result_fs)
        if ic_fs > 1.3:
            print(f"  P{pg:02d} offset={offset}+Fskip: IoC={ic_fs:.4f} | {to_eng(result_fs)[:60]}")

# ================================================================
# TEST 7: Multiplicative cipher (affine on mod 29)
# ================================================================
print("\n" + "="*70)
print("TEST 7: MULTIPLICATIVE CIPHER (unsolved pages > 200 runes)")
print("="*70)

# For completeness - check multiplicative-only (no additive)
for pg in sorted(pages):
    vals = pages[pg]
    if len(vals) < 200: continue
    for mult in range(2, 29):
        if math.gcd(mult, 29) != 1: continue
        result = [(v * mult) % 29 for v in vals]
        ic = ioc(result)
        if ic > 1.5:
            print(f"  P{pg:02d} mult={mult}: IoC={ic:.4f} | {to_eng(result)[:50]}")

# ================================================================
# TEST 8: Skip cipher (read every Nth rune)
# ================================================================
print("\n" + "="*70)
print("TEST 8: SKIP CIPHER (every Nth rune, large pages)")
print("="*70)

for pg in [17, 20, 25, 32, 40, 44, 50]:
    if pg not in pages: continue
    vals = pages[pg]
    n = len(vals)
    
    for skip in range(2, 50):
        if math.gcd(skip, n) not in [1, skip]:  # Only if coprime or multiple
            continue
        # Read every skip-th rune starting from 0
        reordered = [vals[(i * skip) % n] for i in range(n)]
        ic = ioc(reordered)  # IoC doesn't change with reordering!
        # But we can check if the reordered text has better periodic IoC
        for period in [2, 3, 5, 7, 29]:
            subs = [reordered[j] for j in range(0, n, period)]
            pic = ioc(subs)
            if pic > 1.5 and period <= 7:
                print(f"  P{pg:02d} skip={skip} period={period}: sub-IoC={pic:.4f}")

print("\n" + "="*70)
print("ALL TESTS COMPLETE")
print("="*70)
