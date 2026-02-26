#!/usr/bin/env python3
"""
REARRANGED PRIMES CIPHER: Multiple interpretations of "rearranging the primes numbers"

1. Alphabetical sort of prime number English names → substitution cipher
2. Alphabetical sort combined with Deor poem as running key
3. Alphabetical sort combined with known keywords (DIVINITY, etc.)
4. Other rearrangement methods (digit sum, reverse digits, etc.)
"""
import os, sys, io, math
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

# ============ CORRECT GP MAPPING ============
GP = {
    '\u16A0':0, '\u16A2':1, '\u16A6':2, '\u16A9':3, '\u16B1':4, '\u16B3':5, '\u16B7':6, '\u16B9':7,
    '\u16BB':8, '\u16BE':9, '\u16C1':10, '\u16C2':11, '\u16C4':11,
    '\u16C7':12, '\u16C8':13, '\u16C9':14, '\u16CB':15, '\u16CF':16, '\u16D2':17, '\u16D6':18,
    '\u16D7':19, '\u16DA':20, '\u16DD':21, '\u16DF':22, '\u16DE':23, '\u16AA':24, '\u16AB':25,
    '\u16A3':26, '\u16E1':27, '\u16E0':28
}
LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
         'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]

def ioc(values, sz=29):
    n = len(values)
    if n < 2: return 0
    counts = Counter(values)
    return sum(c*(c-1) for c in counts.values()) / (n*(n-1)) * sz

def to_latin(vals):
    return ''.join(LATIN[v] for v in vals)

def load_page(pg):
    for p in [f'LiberPrimus/pages/page_{pg:02d}/runes.txt']:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                return [GP[c] for c in f.read() if c in GP]
    return None

# English word scoring
COMMON_WORDS_3 = {'THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','HER','WAS','ONE','OUR','OUT','HIS','HAS','HAD','WHO','CAN','ITS','LET','SAY','HER','NOW','OLD','NEW','WAY','MAY','DAY','TOO','USE'}
COMMON_WORDS_4 = {'THAT','WITH','HAVE','THIS','WILL','YOUR','FROM','THEY','BEEN','CALL','WHAT','WHEN','MAKE','LIKE','LONG','LOOK','MANY','SOME','THAN','THEM','WERE','SAID','EACH','WHICH','THEIR','TIME','VERY','JUST','KNOW','TAKE','COME','COULD','OVER','SUCH','INTO','MOST','ALSO','BACK'}
COMMON_WORDS_5 = {'WHICH','THERE','THEIR','ABOUT','COULD','OTHER','AFTER','THREE','THESE','FIRST','WOULD','WHERE','BEING','SHALL','THOSE','EVERY','GREAT','STILL'}

def word_score(text):
    score = 0
    for i in range(len(text)-2):
        w3 = text[i:i+3]
        if w3 in COMMON_WORDS_3: score += 3
        if i < len(text)-3:
            w4 = text[i:i+4]
            if w4 in COMMON_WORDS_4: score += 5
        if i < len(text)-4:
            w5 = text[i:i+5]
            if w5 in COMMON_WORDS_5: score += 8
    return score

# ============ ALPHABETICAL REARRANGEMENT ============
def num_to_english(n):
    ones = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    teens = ["ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", 
             "seventeen", "eighteen", "nineteen"]
    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
    
    if n == 0: return "zero"
    if n < 10: return ones[n]
    if n < 20: return teens[n-10]
    if n < 100: 
        return tens[n//10] + ("-" + ones[n%10] if n%10 != 0 else "")
    if n < 1000:
        result = ones[n//100] + " hundred"
        if n % 100 != 0:
            result += " " + num_to_english(n % 100)
        return result
    return str(n)

# Build the alphabetical substitution
primes_with_names = [(GP_PRIMES[i], num_to_english(GP_PRIMES[i]), i) for i in range(29)]
primes_sorted = sorted(primes_with_names, key=lambda x: x[1])

# New position for each original GP index
alpha_perm = [0] * 29  # alpha_perm[old_idx] = new_idx
for new_idx, (prime, name, old_idx) in enumerate(primes_sorted):
    alpha_perm[old_idx] = new_idx

# Also build inverse: inv_perm[new_idx] = old_idx
inv_perm = [0] * 29
for old_idx in range(29):
    inv_perm[alpha_perm[old_idx]] = old_idx

print("=" * 80)
print("ALPHABETICAL PRIME REARRANGEMENT")
print("=" * 80)
print("Sorted primes (by English name):")
for new_idx, (prime, name, old_idx) in enumerate(primes_sorted):
    print(f"  {new_idx:2d}: {name:25s} = {prime:3d} → GP index {old_idx:2d} ({LATIN[old_idx]})")

print(f"\nForward permutation (old → new): {alpha_perm}")
print(f"Inverse permutation (new → old): {inv_perm}")
print(f"Is bijection: {sorted(alpha_perm) == list(range(29))}")

# ============ DEOR TOKENIZER ============
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,'K':5,'L':20,'M':19,
           'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':14}

def tokenize_oe(text):
    text = text.upper().replace(' ', '').replace('\n', '')
    for ch in '.,;:!?\'"()[]{}–—-0123456789':
        text = text.replace(ch, '')
    values = []
    i = 0
    while i < len(text):
        if text[i] == 'Þ' or text[i] == 'Ð':
            values.append(2); i += 1
        elif text[i] == 'Æ':
            values.append(25); i += 1
        elif i + 1 < len(text):
            digraph = text[i:i+2]
            if digraph == 'TH': values.append(2); i += 2
            elif digraph == 'NG': values.append(21); i += 2
            elif digraph == 'OE': values.append(22); i += 2
            elif digraph == 'AE': values.append(25); i += 2
            elif digraph in ('IA', 'IO'): values.append(27); i += 2
            elif digraph == 'EA': values.append(28); i += 2
            elif digraph == 'EO': values.append(12); i += 2
            elif text[i] in ENG2GP: values.append(ENG2GP[text[i]]); i += 1
            else: i += 1
        elif text[i] in ENG2GP:
            values.append(ENG2GP[text[i]]); i += 1
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

deor = tokenize_oe(DEOR_OE)
print(f"\nDeor tokens: {len(deor)}")

# ============ KNOWN KEYS ============
DIVINITY = [23, 10, 1, 10, 9, 10, 16, 26]  # D-I-V(U)-I-N-I-T-Y

unsolved_pages = list(range(17, 55))

# ============ SECTION 1: Pure alphabetical substitution ============
print(f"\n{'='*80}")
print("SECTION 1: Pure alphabetical substitution on all pages")
print(f"{'='*80}")

for pg in unsolved_pages:
    p = load_page(pg)
    if not p: continue
    
    # Forward: apply alpha_perm[cipher_val]
    fwd = [alpha_perm[v] for v in p]
    # Inverse: apply inv_perm[cipher_val]
    inv = [inv_perm[v] for v in p]
    
    ic_fwd = ioc(fwd)
    ic_inv = ioc(inv)
    ws_fwd = word_score(to_latin(fwd))
    ws_inv = word_score(to_latin(inv))
    
    if ic_fwd > 1.15 or ic_inv > 1.15 or ws_fwd > 30 or ws_inv > 30:
        print(f"  P{pg:02d}: fwd IoC={ic_fwd:.3f} ws={ws_fwd}  inv IoC={ic_inv:.3f} ws={ws_inv}")
        if ws_fwd > ws_inv:
            print(f"    fwd: {to_latin(fwd)[:80]}")
        else:
            print(f"    inv: {to_latin(inv)[:80]}")

# ============ SECTION 2: Alpha substitution + Vigenere with known keywords ============
print(f"\n{'='*80}")
print("SECTION 2: Alpha substitution + Vigenere/Beaufort with known keywords")
print(f"{'='*80}")

keywords = {
    'DIVINITY': DIVINITY,
    'CIRCUMFERENCE': [5,10,4,5,1,19,0,18,4,18,9,5,18],  # C-I-R-C-U-M-F-E-R-E-N-C-E
    'FIRFUMFERENFE': [0,10,4,0,1,19,0,18,4,18,9,0,18],  # With F as F
}

for pg in unsolved_pages:
    p = load_page(pg)
    if not p: continue
    
    for subst_label, perm in [("FWD", alpha_perm), ("INV", inv_perm)]:
        substituted = [perm[v] for v in p]
        
        for kw_name, key in keywords.items():
            klen = len(key)
            for mode in ['sub', 'beau', 'add']:
                # With F-skip
                result = []
                ki = 0
                for v in substituted:
                    if v == 0:  # F-skip
                        result.append(0)
                        continue
                    kv = key[ki % klen]
                    if mode == 'sub': result.append((v - kv) % 29)
                    elif mode == 'beau': result.append((kv - v) % 29)
                    else: result.append((v + kv) % 29)
                    ki += 1
                
                ic = ioc(result)
                ws = word_score(to_latin(result))
                if ic > 1.3 or ws > 50:
                    print(f"  P{pg:02d} {subst_label}+{kw_name}/{mode}(F-skip): IoC={ic:.3f} ws={ws}")
                    print(f"    {to_latin(result)[:80]}")

# ============ SECTION 3: Alpha substitution + Deor running key ============
print(f"\n{'='*80}")
print("SECTION 3: Alpha substitution + Deor running key")
print(f"{'='*80}")

for pg in unsolved_pages:
    p = load_page(pg)
    if not p: continue
    
    for subst_label, perm in [("FWD", alpha_perm), ("INV", inv_perm)]:
        substituted = [perm[v] for v in p]
        
        for mode in ['sub', 'beau', 'add']:
            # No F-skip, cycling deor
            result = []
            for i, v in enumerate(substituted):
                dk = deor[i % len(deor)]
                if mode == 'sub': result.append((v - dk) % 29)
                elif mode == 'beau': result.append((dk - v) % 29)
                else: result.append((v + dk) % 29)
            
            ic = ioc(result)
            ws = word_score(to_latin(result))
            if ic > 1.2 or ws > 40:
                print(f"  P{pg:02d} {subst_label}+DEOR/{mode}: IoC={ic:.3f} ws={ws}")
                print(f"    {to_latin(result)[:80]}")

# ============ SECTION 4: Try other rearrangements ============
print(f"\n{'='*80}")
print("SECTION 4: Other rearrangement methods")
print(f"{'='*80}")

# 4a: Sort primes by digit sum
digit_sum_sorted = sorted(range(29), key=lambda i: (sum(int(d) for d in str(GP_PRIMES[i])), GP_PRIMES[i]))
ds_perm = [0]*29
for new_idx, old_idx in enumerate(digit_sum_sorted):
    ds_perm[old_idx] = new_idx
print(f"Digit sum permutation: {ds_perm}")
print(f"Is bijection: {sorted(ds_perm) == list(range(29))}")

# 4b: Sort primes by number of prime factors of (prime-1) [Euler totient related]
def count_prime_factors(n):
    if n <= 1: return 0
    count = 0
    d = 2
    while d * d <= n:
        while n % d == 0:
            count += 1
            n //= d
        d += 1
    if n > 1: count += 1
    return count

factcount_sorted = sorted(range(29), key=lambda i: (count_prime_factors(GP_PRIMES[i]-1), GP_PRIMES[i]))
fc_perm = [0]*29
for new_idx, old_idx in enumerate(factcount_sorted):
    fc_perm[old_idx] = new_idx
print(f"Factor count permutation: {fc_perm}")

# 4c: Sort primes by their position in the Fibonacci sequence (or nearest Fibonacci)
fibs = [1, 1]
while fibs[-1] < 200:
    fibs.append(fibs[-1] + fibs[-2])
fib_set = set(fibs)
fibonacci_sorted = sorted(range(29), key=lambda i: (GP_PRIMES[i] not in fib_set, min(abs(GP_PRIMES[i] - f) for f in fibs), GP_PRIMES[i]))
fib_perm = [0]*29
for new_idx, old_idx in enumerate(fibonacci_sorted):
    fib_perm[old_idx] = new_idx
print(f"Fibonacci proximity permutation: {fib_perm}")

# 4d: Sort primes using their RESIDUE mod small primes
for modulus in [7, 11, 13, 29]:
    mod_sorted = sorted(range(29), key=lambda i: (GP_PRIMES[i] % modulus, GP_PRIMES[i]))
    mod_perm = [0]*29
    for new_idx, old_idx in enumerate(mod_sorted):
        mod_perm[old_idx] = new_idx
    
    # Test on P18 only
    p18 = load_page(18)
    if p18:
        fwd = [mod_perm[v] for v in p18]
        ic = ioc(fwd)
        ws = word_score(to_latin(fwd))
        if ic > 1.15 or ws > 20:
            print(f"  Mod {modulus} on P18: IoC={ic:.3f} ws={ws}")

# 4e: Rotate alphabet by prime index
for rotation in range(1, 29):
    rot_perm = [(i + rotation) % 29 for i in range(29)]
    p18 = load_page(18)
    if p18:
        # Substitution + DIVINITY
        substituted = [rot_perm[v] for v in p18]
        for mode in ['sub', 'beau']:
            result = []
            ki = 0
            for v in substituted:
                if v == 0:
                    result.append(0)
                    continue
                kv = DIVINITY[ki % 8]
                if mode == 'sub': result.append((v - kv) % 29)
                else: result.append((kv - v) % 29)
                ki += 1
            ic = ioc(result)
            ws = word_score(to_latin(result))
            if ic > 1.3 or ws > 30:
                print(f"  Rot {rotation:2d} + DIVINITY/{mode} on P18: IoC={ic:.3f} ws={ws}")

# ============ SECTION 5: Alpha subst as TRANSPOSITION (not substitution) ============
print(f"\n{'='*80}")
print("SECTION 5: Alpha permutation as reading-order transposition")
print(f"{'='*80}")

# What if "rearranging" means reading the ciphertext in a different ORDER
# based on the prime number alphabetical sort?
# For each position i in the text, the new position is alpha_perm[cipher[i]] 
# ... but that doesn't make sense for transposition

# More natural: write text into slots ordered by sorted primes
# blocks of 29, each block slot[j] gets text[i] where j = sorted_position[i % 29]
for pg in [17, 18, 19, 20, 25, 32]:
    p = load_page(pg)
    if not p: continue
    n = len(p)
    
    # Transpose in blocks of 29
    transposed = list(p)  # copy
    for block_start in range(0, n - 28, 29):
        block = p[block_start:block_start+29]
        if len(block) < 29: break
        for j in range(29):
            transposed[block_start + alpha_perm[j]] = block[j]
    
    ic = ioc(transposed)
    ws = word_score(to_latin(transposed))
    
    # Also try inverse
    inv_transposed = list(p)
    for block_start in range(0, n - 28, 29):
        block = p[block_start:block_start+29]
        if len(block) < 29: break
        for j in range(29):
            inv_transposed[block_start + inv_perm[j]] = block[j]
    
    ic2 = ioc(inv_transposed)
    ws2 = word_score(to_latin(inv_transposed))
    
    print(f"  P{pg:02d}: fwd_trans IoC={ic:.3f} ws={ws}  inv_trans IoC={ic2:.3f} ws={ws2}")
    
    # Combined with Vigenere DIVINITY
    for data, label in [(transposed, "fwd"), (inv_transposed, "inv")]:
        for mode in ['sub', 'beau']:
            result = []
            ki = 0
            for v in data:
                if v == 0:
                    result.append(0)
                    continue
                kv = DIVINITY[ki % 8]
                if mode == 'sub': result.append((v - kv) % 29)
                else: result.append((kv - v) % 29)
                ki += 1
            ic = ioc(result)
            ws = word_score(to_latin(result))
            if ic > 1.25 or ws > 30:
                print(f"    P{pg:02d} {label}_trans+DIVINITY/{mode}: IoC={ic:.3f} ws={ws}")
                print(f"      {to_latin(result)[:80]}")

# ============ SECTION 6: Deor poem → substituted → as key ============
print(f"\n{'='*80}")
print("SECTION 6: Deor poem with alpha-perm substitution as key")
print(f"{'='*80}")

# Apply the alpha permutation to the Deor poem tokens to get a modified key
deor_rearranged = [alpha_perm[v] for v in deor]
deor_inv_rearranged = [inv_perm[v] for v in deor]

for pg in unsolved_pages:
    p = load_page(pg)
    if not p: continue
    
    for deor_key, label in [(deor_rearranged, "DEOR_FWD"), (deor_inv_rearranged, "DEOR_INV")]:
        for mode in ['sub', 'beau', 'add']:
            result = []
            for i, v in enumerate(p):
                dk = deor_key[i % len(deor_key)]
                if mode == 'sub': result.append((v - dk) % 29)
                elif mode == 'beau': result.append((dk - v) % 29)
                else: result.append((v + dk) % 29)
            
            ic = ioc(result)
            ws = word_score(to_latin(result))
            if ic > 1.2 or ws > 40:
                print(f"  P{pg:02d} {label}/{mode}: IoC={ic:.3f} ws={ws}")
                print(f"    {to_latin(result)[:80]}")

# ============ SECTION 7: Combined: alpha-subst on cipher + deor-subst as key ============
print(f"\n{'='*80}")
print("SECTION 7: Alpha-subst(cipher) decrypted with alpha-subst(Deor)")
print(f"{'='*80}")

for pg in unsolved_pages:
    p = load_page(pg)
    if not p: continue
    
    for c_perm, c_label in [(alpha_perm, "C_FWD"), (inv_perm, "C_INV")]:
        c_subst = [c_perm[v] for v in p]
        for d_key, d_label in [(deor_rearranged, "D_FWD"), (deor_inv_rearranged, "D_INV"), (deor, "D_RAW")]:
            for mode in ['sub', 'beau']:
                result = []
                for i, v in enumerate(c_subst):
                    dk = d_key[i % len(d_key)]
                    if mode == 'sub': result.append((v - dk) % 29)
                    else: result.append((dk - v) % 29)
                
                ic = ioc(result)
                if ic > 1.2:
                    ws = word_score(to_latin(result))
                    print(f"  P{pg:02d} {c_label}+{d_label}/{mode}: IoC={ic:.3f} ws={ws}")
                    print(f"    {to_latin(result)[:80]}")

print(f"\n{'='*80}")
print("SECTION 8: Try the 'path' literally - use sorted primes as INDEX sequence into Deor")
print(f"{'='*80}")

# "A PATH to the Deor" - the sorted primes TELL YOU which characters of Deor to read
# The primes are [2,3,5,...,109]. Sorted alphabetically, they become:
# [89,83,11,59,53,5,41,47,43,19,97,109,101,107,103,7,17,79,71,73,61,67,13,31,37,3,29,23,2]
sorted_primes_values = [prime for prime, name, idx in primes_sorted]
print(f"Sorted primes: {sorted_primes_values}")

# Use these as indices into Deor
path_key = []
for sp in sorted_primes_values:
    if sp < len(deor):
        path_key.append(deor[sp])
print(f"PATH key (Deor at sorted-prime indices): {path_key}")
print(f"PATH key as text: {to_latin(path_key)}")
print(f"PATH key length: {len(path_key)}")

# Use this 29-char key as Vigenere
for pg in unsolved_pages:
    p = load_page(pg)
    if not p: continue
    
    for mode in ['sub', 'beau', 'add']:
        # With F-skip
        result = []
        ki = 0
        for v in p:
            if v == 0:
                result.append(0)
                continue
            kv = path_key[ki % len(path_key)]
            if mode == 'sub': result.append((v - kv) % 29)
            elif mode == 'beau': result.append((kv - v) % 29)
            else: result.append((v + kv) % 29)
            ki += 1
        
        ic = ioc(result)
        ws = word_score(to_latin(result))
        if ic > 1.2 or ws > 30:
            print(f"  P{pg:02d} PATH_KEY/{mode}(F-skip): IoC={ic:.3f} ws={ws}")
            print(f"    {to_latin(result)[:80]}")

# Without F-skip
for pg in unsolved_pages:
    p = load_page(pg)
    if not p: continue
    
    for mode in ['sub', 'beau', 'add']:
        result = [(p[i] - path_key[i % len(path_key)]) % 29 if mode == 'sub'
                  else (path_key[i % len(path_key)] - p[i]) % 29 if mode == 'beau'
                  else (p[i] + path_key[i % len(path_key)]) % 29
                  for i in range(len(p))]
        ic = ioc(result)
        ws = word_score(to_latin(result))
        if ic > 1.2 or ws > 30:
            print(f"  P{pg:02d} PATH_KEY/{mode}(no-skip): IoC={ic:.3f} ws={ws}")
            print(f"    {to_latin(result)[:80]}")

print("\nDONE")
