"""
Focused P20 attack: verify shift-16 claim, try prime-based transpositions,
and test "rearranging the primes" interpretations.

P20 = 812 runes, 166 words
P19 hint: "REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR"
"""
import os
from collections import Counter
import math

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C4':11,'\u16C7':12,'\u16C8':13,'\u16C9':14,
    '\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,'\u16D7':19,'\u16DA':20,'\u16DD':21,
    '\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,'\u16A3':26,'\u16E1':27,'\u16E0':28
}
LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]

def load_runes(pg):
    for p in [f'LiberPrimus/pages/page_{pg:02d}/runes.txt', f'LiberPrimus/pages/page_{pg}/runes.txt']:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                return [GP[c] for c in f.read() if c in GP]
    return None

def ioc29(data):
    """IoC using 29-symbol alphabet."""
    if len(data) <= 1: return 0
    freq = Counter(data)
    n = len(data)
    return sum(f*(f-1) for f in freq.values()) / (n*(n-1)) * 29

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

# English frequency in GP (approximate, from known solved pages)
# Computed from P55/P73 solutions
ENGLISH_GP_FREQ = None  # We'll compute expected IoC differently

# ================================================================
# LOAD P20
# ================================================================
p20 = load_runes(20)
print(f"P20: {len(p20)} runes")
print(f"P20 IoC (29-symbol): {ioc29(p20):.4f}")
print(f"P20 factorization: 812 = 4 × 7 × 29")
print()

# ================================================================
# 1. ALL SHIFTS: check IoC for each Caesar shift
# ================================================================
print("=== CAESAR SHIFTS (IoC for each shift value) ===")
for shift in range(29):
    shifted = [(v + shift) % 29 for v in p20]
    ic = ioc29(shifted)
    marker = " <<<" if ic > 1.15 else ""
    if shift == 16 or ic > 1.1:
        print(f"  Shift {shift:2d}: IoC = {ic:.4f}{marker}  | {to_latin(shifted[:40])}")
print()

# IMPORTANT: IoC doesn't change with Caesar shift! (just relabels values)
# So all shifts give the same IoC. The original IoC claim must have been on
# a SUBSET of runes after shift.
print("NOTE: IoC is invariant under Caesar shift.")
print(f"Full P20 IoC: {ioc29(p20):.4f} (same for all shifts)")
print()

# ================================================================
# 2. Verify prime-position extraction and its IoC
# ================================================================
primes_list = sieve(900)
primes_set = set(primes_list)

# 1-indexed prime positions
prime_pos_runes = [p20[i] for i in range(len(p20)) if (i+1) in primes_set]
non_prime_pos_runes = [p20[i] for i in range(len(p20)) if (i+1) not in primes_set]

print(f"=== PRIME POSITION EXTRACTION (1-indexed) ===")
print(f"Prime positions: {len(prime_pos_runes)} runes (pi({len(p20)}) = {len(prime_pos_runes)})")
print(f"Non-prime positions: {len(non_prime_pos_runes)} runes")
print(f"Prime IoC: {ioc29(prime_pos_runes):.4f}")
print(f"Non-prime IoC: {ioc29(non_prime_pos_runes):.4f}")
print()

# Try 0-indexed prime positions
prime_pos_0 = [p20[i] for i in range(len(p20)) if i in primes_set]
non_prime_pos_0 = [p20[i] for i in range(len(p20)) if i not in primes_set]
print(f"0-indexed prime positions: {len(prime_pos_0)} runes")
print(f"0-indexed non-prime: {len(non_prime_pos_0)} runes")
print(f"0-indexed prime IoC: {ioc29(prime_pos_0):.4f}")
print(f"0-indexed non-prime IoC: {ioc29(non_prime_pos_0):.4f}")
print()

# Check: what gives 166 + 646 = 812?
# 166 could be word count. Check if selecting one rune per word works.
with open('LiberPrimus/pages/page_20/runes.txt', 'r', encoding='utf-8') as f:
    raw = f.read().strip()

# Words are separated by dots
words_raw = raw.split('\u00B7')  # middle dot
if len(words_raw) <= 1:
    words_raw = raw.split('.')
if len(words_raw) <= 1:
    # Try looking for the separator
    # Actually GP text uses ᛫ (U+16EB) as word separator
    words_raw = raw.split('\u16EB')
    
print(f"Word count (split by separator): {len(words_raw)}")

# Also try: split by any non-rune character
import re
words_by_nonrune = re.split('[^' + ''.join(GP.keys()) + ']+', raw)
words_by_nonrune = [w for w in words_by_nonrune if w]
print(f"Word count (split by non-rune chars): {len(words_by_nonrune)}")

# Did the 166 come from extracting every rune at a prime-valued GEMATRIA index?
# i.e., runes whose index IS a prime number (2,3,5,7,11,13,17,19,23)
# That's indices 2,3,5,7,11,13,17,19,23 → 9 values out of 29
prime_valued = [v for v in p20 if v in {2,3,5,7,11,13,17,19,23}]
non_prime_valued = [v for v in p20 if v not in {2,3,5,7,11,13,17,19,23}]
print(f"\nPrime-GP-index runes (idx in {{2,3,5,7,11,13,17,19,23}}): {len(prime_valued)}")
print(f"Non-prime-GP-index runes: {len(non_prime_valued)}")
print(f"Prime-valued IoC: {ioc29(prime_valued):.4f}")
print(f"Non-prime-valued IoC: {ioc29(non_prime_valued):.4f}")
print()

# Check which GP indices have prime PRIME value (i.e., GP_PRIMES[idx] is in a specific set)
# Actually GP_PRIMES are ALL primes by definition, so this doesn't help

# Check: runes whose POSITION INDEX is a prime vs whose GP VALUE index is a prime
# The "166 and 646" split must come from somewhere specific
# 166 + 646 = 812 ✓
# pi(812) = 141 (1-indexed)
# 0-indexed: positions 2,3,5,...,811 → 141 primes ≤ 811 = 141
# Neither is 166

# Check: maybe it's positions where the RUNE VALUE is prime?
# GP values 0-28, primes among these: 2,3,5,7,11,13,17,19,23
# Count runes with prime GP index
prime_idx_runes = [v for v in p20 if v in {2,3,5,7,11,13,17,19,23}]
print(f"Runes with prime GP index: {len(prime_idx_runes)}")

# 237 is another number from subset_prime_values.txt
# Maybe it's runes whose GP PRIME is itself categorized differently
# subset_prime_values: "237 runes with prime-valued Gematria (only 9 unique: TH,O,C,W,J,P,B,M,D)"
# Those are indices: TH=2, O=3, C=5, W=7, J=11, P=13, B=17, M=19, D=23
# These are exactly the GP indices that are themselves prime numbers!
# Count: TH,O,C,W,J,P,B,M,D → indices 2,3,5,7,11,13,17,19,23
print(f"Runes at prime GP indices (TH,O,C,W,J,P,B,M,D): {len(prime_idx_runes)}")

# So subset_prime_values has 237, matching approach above? Let me recheck:
gp_prime_indices = {2,3,5,7,11,13,17,19,23}  # indices that are prime numbers
prime_val_runes = [v for v in p20 if v in gp_prime_indices]
print(f"Count of prime-valued runes: {len(prime_val_runes)} (expected 237)")

non_prime_val_runes = [v for v in p20 if v not in gp_prime_indices]
print(f"Count of non-prime-valued runes: {len(non_prime_val_runes)} (expected 575)")

# Hmm, 237+575=812 ✓, but none of these give 166+646

# Aha! 166 might be the number of WORDS, not runes!
# And "prime-position" might mean: among the 166 words, select the ones at prime positions
prime_word_positions = [p for p in primes_list if p <= len(words_by_nonrune)]
print(f"\nPrime word positions (out of {len(words_by_nonrune)} words): {len(prime_word_positions)}")
# Select first rune of each prime-positioned word? Or all runes of prime-positioned words?

# Let me read the actual extraction script
print()
print("=" * 60)
print("REARRANGING PRIMES ATTACK")
print("=" * 60)

# ================================================================
# 3. Main attack: interpret "rearranging the prime numbers"
# ================================================================

# Interpretation A: TRANSPOSITION based on prime number sequence
# Arrange 812 runes in a grid, read following a "path" determined by primes

# 812 = 4 × 7 × 29
# Grid 29 × 28: uses 812 cells exactly!
print("\n--- Grid 29×28 transpositions ---")
nrows, ncols = 29, 28
grid = []
idx = 0
for r in range(nrows):
    row = []
    for c in range(ncols):
        if idx < len(p20):
            row.append(p20[idx])
        idx += 1
    grid.append(row)

# Read column by column
col_read = []
for c in range(ncols):
    for r in range(nrows):
        if c < len(grid[r]):
            col_read.append(grid[r][c])
ic_col = ioc29(col_read)
print(f"29×28 col-read: IoC={ic_col:.4f} | {to_latin(col_read[:50])}")

# Read in prime ordering of columns
# Column order determined by primes: sort columns by their associated prime
# First 28 primes: 2,3,5,...,107
first_28_primes = primes_list[:28]
prime_col_order = sorted(range(28), key=lambda c: first_28_primes[c])
prime_col_read = []
for c in prime_col_order:
    for r in range(nrows):
        if c < len(grid[r]):
            prime_col_read.append(grid[r][c])
ic_pcol = ioc29(prime_col_read)
print(f"29×28 prime-col-order read: IoC={ic_pcol:.4f} | {to_latin(prime_col_read[:50])}")

# Also try 28×29 grid
nrows2, ncols2 = 28, 29
grid2 = []
idx = 0
for r in range(nrows2):
    row = []
    for c in range(ncols2):
        if idx < len(p20):
            row.append(p20[idx])
        idx += 1
    grid2.append(row)

col_read2 = []
for c in range(ncols2):
    for r in range(nrows2):
        if c < len(grid2[r]):
            col_read2.append(grid2[r][c])
ic_col2 = ioc29(col_read2)
print(f"28×29 col-read: IoC={ic_col2:.4f} | {to_latin(col_read2[:50])}")

# First 29 primes col order
first_29_primes = primes_list[:29]
prime_col_order2 = sorted(range(29), key=lambda c: first_29_primes[c])
prime_col_read2 = []
for c in prime_col_order2:
    for r in range(nrows2):
        if c < len(grid2[r]):
            prime_col_read2.append(grid2[r][c])
ic_pcol2 = ioc29(prime_col_read2)
print(f"28×29 prime-col-order read: IoC={ic_pcol2:.4f} | {to_latin(prime_col_read2[:50])}")

# Interpretation B: Position-based rearrangement using primes
print("\n--- Prime-sequence position rearrangement ---")

# Read P20[p_i - 1] for i-th prime, then P20[remaining positions]
# Essentially: extract at prime positions, then non-prime positions
# This separates into two streams
prime_stream = [p20[p-1] for p in primes_list if p <= len(p20)]
non_prime_stream = [p20[i] for i in range(len(p20)) if (i+1) not in primes_set]
concat_pn = prime_stream + non_prime_stream
ic_pn = ioc29(concat_pn)
print(f"Prime positions || Non-prime positions: IoC={ic_pn:.4f} (same as original)")
concat_np = non_prime_stream + prime_stream 
print(f"Non-prime || Prime: IoC={ioc29(concat_np):.4f}")

# Interleave differently: prime[0], nonprime[0], prime[1], nonprime[1], ...
interleaved = []
pi, ni = 0, 0
while pi < len(prime_stream) or ni < len(non_prime_stream):
    if pi < len(prime_stream):
        interleaved.append(prime_stream[pi])
        pi += 1
    if ni < len(non_prime_stream):
        interleaved.append(non_prime_stream[ni])
        ni += 1
print(f"Interleaved prime/nonprime: IoC={ioc29(interleaved):.4f}")

# Interpretation C: Substitution where primes are "rearranged"
print("\n--- Prime rearrangement substitution ---")

# What if instead of F=2,U=3,...,EA=109, we use a circular shift?
# "Rearranging" = rotating the prime assignment
for rot in range(29):
    mapping = [(GP_PRIMES[(i + rot) % 29]) for i in range(29)]  # Not useful directly
    # Instead: new_index[i] = (i + rot) % 29 — that's just Caesar
    pass

# What if each rune's value is replaced by the INDEX of its prime in a sorted list?
# That's the identity (they're already sorted)
# But what if sorted differently? Like by prime mod 29?
primes_mod29 = [(GP_PRIMES[i] % 29, i) for i in range(29)]
primes_mod29.sort()
# Mapping: rune i → its rank when primes sorted by (prime mod 29)
mod29_rank = [0] * 29
for rank, (_, orig_idx) in enumerate(primes_mod29):
    mod29_rank[orig_idx] = rank
sub_mod29 = [mod29_rank[v] for v in p20]
ic_mod = ioc29(sub_mod29)
print(f"Substitution by prime-mod-29 rank: IoC={ic_mod:.4f}")

# Interpretation D: Use Deor poem as running key with prime-indexed positions
print("\n--- Deor poem key at prime-indexed positions ---")

# Load Deor poem from existing script
LATIN_TO_VAL = {
    'A': 24, 'B': 17, 'C': 5, 'D': 23, 'E': 18, 'F': 0, 'G': 6, 'H': 8,
    'I': 10, 'J': 11, 'K': 5, 'L': 20, 'M': 19, 'N': 9, 'O': 3, 'P': 13,
    'Q': 5, 'R': 4, 'S': 15, 'T': 16, 'U': 1, 'V': 1, 'W': 7, 'X': 14,
    'Y': 26, 'Z': 15, 'Þ': 2, 'Ð': 2, 'Æ': 25
}

def tokenize_oe(text):
    vals = []
    t = text.upper()
    i = 0
    while i < len(t):
        if t[i] in LATIN_TO_VAL:
            vals.append(LATIN_TO_VAL[t[i]])
            i += 1
        elif t[i] == 'Þ' or t[i] == 'þ':
            vals.append(2)
            i += 1
        elif t[i] == 'Ð' or t[i] == 'ð':
            vals.append(2)
            i += 1
        elif t[i] == 'Æ' or t[i] == 'æ':
            vals.append(25)
            i += 1
        else:
            i += 1
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
print(f"Deor poem: {len(deor_vals)} GP values")

# Test: Deor as running key on full P20
for mode_name, mode_fn in [
    ('SUB', lambda c, k: (c - k) % 29),
    ('ADD', lambda c, k: (c + k) % 29),
    ('BEAU', lambda c, k: (k - c) % 29)
]:
    # Standard running key
    plain = [mode_fn(p20[i], deor_vals[i % len(deor_vals)]) for i in range(len(p20))]
    ic = ioc29(plain)
    if ic > 1.15:
        print(f"  Deor running key {mode_name}: IoC={ic:.4f} | {to_latin(plain[:50])}")

# Test: Deor at prime-valued positions only
# Use Deor[prime_i] as key for P20[i]
for mode_name, mode_fn in [
    ('SUB', lambda c, k: (c - k) % 29),
    ('ADD', lambda c, k: (c + k) % 29),
    ('BEAU', lambda c, k: (k - c) % 29)
]:
    plain = []
    for i in range(len(p20)):
        prime_idx = GP_PRIMES[p20[i]]  # The prime associated with this rune
        key = deor_vals[prime_idx % len(deor_vals)]
        plain.append(mode_fn(p20[i], key))
    ic = ioc29(plain)
    if ic > 1.15:
        print(f"  Deor at prime[rune_val]: {mode_name} IoC={ic:.4f}")
    
    # Also: use Deor[primes[i]] (i-th prime as index into Deor)
    plain2 = []
    for i in range(len(p20)):
        if i < len(primes_list):
            key = deor_vals[primes_list[i] % len(deor_vals)]
        else:
            key = deor_vals[i % len(deor_vals)]
        plain2.append(mode_fn(p20[i], key))
    ic2 = ioc29(plain2)
    if ic2 > 1.15:
        print(f"  Deor at primes[i]: {mode_name} IoC={ic2:.4f}")

print()

# ================================================================
# 4. F-skip totient on P20 specifically (thorough)
# ================================================================
print("=== F-SKIP TOTIENT ON P20 (offsets 0-5000) ===")
all_primes = sieve(60000)
tot_stream = [totient(p) % 29 for p in all_primes[:6000]]

best_fskip = []
for offset in range(5000):
    for mode_name, mode_fn in [('SUB', lambda c, k: (c - k) % 29), 
                                ('ADD', lambda c, k: (c + k) % 29),
                                ('BEAU', lambda c, k: (k - c) % 29)]:
        plain = []
        ki = offset
        for ci in p20:
            if ki >= len(tot_stream):
                break
            plain.append(mode_fn(ci, tot_stream[ki]))
            if plain[-1] != 0:  # F-skip
                ki += 1
        
        if len(plain) == len(p20):
            ic = ioc29(plain)
            if ic > 1.3:
                best_fskip.append((ic, offset, mode_name, to_latin(plain[:60])))

best_fskip.sort(reverse=True)
if best_fskip:
    print(f"Found {len(best_fskip)} hits above IoC 1.3:")
    for ic, off, mode, text in best_fskip[:10]:
        print(f"  offset={off} mode={mode} IoC={ic:.4f} | {text}")
else:
    print("No F-skip totient hits above IoC 1.3")
print()

# ================================================================
# 5. Direct prime stream (not totient) as key
# ================================================================  
print("=== PRIME STREAM (not totient) AS KEY ===")
prime_stream_key = [p % 29 for p in all_primes[:6000]]

best_prime = []
for offset in range(5000):
    for mode_name, mode_fn in [('SUB', lambda c, k: (c - k) % 29),
                                ('ADD', lambda c, k: (c + k) % 29),
                                ('BEAU', lambda c, k: (k - c) % 29)]:
        plain = [mode_fn(p20[i], prime_stream_key[offset + i]) for i in range(len(p20))]
        ic = ioc29(plain)
        if ic > 1.3:
            best_prime.append((ic, offset, mode_name, to_latin(plain[:60])))

best_prime.sort(reverse=True)
if best_prime:
    print(f"Found {len(best_prime)} hits above IoC 1.3:")
    for ic, off, mode, text in best_prime[:10]:
        print(f"  offset={off} mode={mode} IoC={ic:.4f} | {text}")
else:
    print("No prime stream hits above IoC 1.3")
print()

# ================================================================
# 6. Key = primes of primes (prime-indexed primes)
# ================================================================
print("=== PRIME-INDEXED PRIME STREAM ===")
# Use the i-th prime, where i itself is prime
prime_of_prime = [all_primes[p-1] % 29 for p in primes_list if p <= len(all_primes)][:900]

for offset in range(min(200, len(prime_of_prime) - len(p20))):
    for mode_name, mode_fn in [('SUB', lambda c, k: (c - k) % 29),
                                ('ADD', lambda c, k: (c + k) % 29)]:
        plain = [mode_fn(p20[i], prime_of_prime[offset + i]) for i in range(min(len(p20), len(prime_of_prime) - offset))]
        if len(plain) == len(p20):
            ic = ioc29(plain)
            if ic > 1.3:
                print(f"  offset={offset} mode={mode_name} IoC={ic:.4f} | {to_latin(plain[:60])}")

print()

# ================================================================
# 7. GRID TRANSPOSITION with Vigenère combo on 29×28 and 28×29
# ================================================================
print("=== GRID + VIGENÈRE COMBO ===")
# Arrange in 29×28 grid, read columns, then apply Deor key
for nrows, ncols in [(29, 28), (28, 29), (7, 116), (116, 7), (4, 203)]:
    if nrows * ncols != 812:
        if nrows * ncols < 812:
            continue
    
    # Column-first read
    grid = []
    idx = 0
    for r in range(nrows):
        row = []
        for c in range(ncols):
            if idx < len(p20):
                row.append(p20[idx])
            idx += 1
        grid.append(row)
    
    transposed = []
    for c in range(ncols):
        for r in range(nrows):
            if c < len(grid[r]):
                transposed.append(grid[r][c])
    
    # Apply Deor key
    for mode_name, mode_fn in [('SUB', lambda c, k: (c - k) % 29),
                                ('ADD', lambda c, k: (c + k) % 29),
                                ('BEAU', lambda c, k: (k - c) % 29)]:
        plain = [mode_fn(transposed[i], deor_vals[i % len(deor_vals)]) for i in range(len(transposed))]
        ic = ioc29(plain)
        if ic > 1.15:
            print(f"  Grid {nrows}×{ncols} col+{mode_name}(Deor): IoC={ic:.4f}")
            print(f"    {to_latin(plain[:80])}")

# Row-first read (transposed grid = fill cols, read rows)
for nrows, ncols in [(29, 28), (28, 29)]:
    transposed2 = []
    full_cols = len(p20) % ncols if len(p20) % ncols != 0 else ncols
    nrows_actual = math.ceil(len(p20) / ncols)
    idx = 0
    cols_data = []
    for c in range(ncols):
        col_len = nrows_actual if c < full_cols else nrows_actual - 1
        cols_data.append(p20[idx:idx+col_len])
        idx += col_len
    
    for r in range(nrows_actual):
        for c in range(ncols):
            if r < len(cols_data[c]):
                transposed2.append(cols_data[c][r])
    
    for mode_name, mode_fn in [('SUB', lambda c, k: (c - k) % 29),
                                ('ADD', lambda c, k: (c + k) % 29),
                                ('BEAU', lambda c, k: (k - c) % 29)]:
        plain = [mode_fn(transposed2[i], deor_vals[i % len(deor_vals)]) for i in range(len(transposed2))]
        ic = ioc29(plain)
        if ic > 1.15:
            print(f"  Grid {nrows}×{ncols} row+{mode_name}(Deor): IoC={ic:.4f}")
            print(f"    {to_latin(plain[:80])}")

print()
print("=== ATTACK COMPLETE ===")
