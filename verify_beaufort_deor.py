#!/usr/bin/env python3
"""
CRITICAL VERIFICATION: Test Beaufort(Deor) on prime positions for ALL unsolved pages.
Uses the CORRECT GP mapping (positions 22-28 fixed).
Also tests with the OLD WRONG mapping to see if the IoC=1.89 claim depends on it.
"""
import os, sys, io, math
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

# ============ CORRECT GP MAPPING ============
GP_CORRECT = {
    '\u16A0':0,  # ᚠ F
    '\u16A2':1,  # ᚢ U
    '\u16A6':2,  # ᚦ TH
    '\u16A9':3,  # ᚩ O
    '\u16B1':4,  # ᚱ R
    '\u16B3':5,  # ᚳ C
    '\u16B7':6,  # ᚷ G
    '\u16B9':7,  # ᚹ W
    '\u16BB':8,  # ᚻ H
    '\u16BE':9,  # ᚾ N
    '\u16C1':10, # ᛁ I
    '\u16C2':11, # ᛂ J (variant)
    '\u16C4':11, # ᛄ J
    '\u16C7':12, # ᛇ EO
    '\u16C8':13, # ᛈ P
    '\u16C9':14, # ᛉ X
    '\u16CB':15, # ᛋ S
    '\u16CF':16, # ᛏ T
    '\u16D2':17, # ᛒ B
    '\u16D6':18, # ᛖ E
    '\u16D7':19, # ᛗ M
    '\u16DA':20, # ᛚ L
    '\u16DD':21, # ᛝ NG
    '\u16DF':22, # ᛟ OE
    '\u16DE':23, # ᛞ D
    '\u16AA':24, # ᚪ A
    '\u16AB':25, # ᚫ AE
    '\u16A3':26, # ᚣ Y
    '\u16E1':27, # ᛡ IA
    '\u16E0':28, # ᛠ EA
}

# OLD WRONG MAPPING (positions 22-28 differ)
GP_WRONG = dict(GP_CORRECT)
# In the wrong mapping: ᛞ=22, ᛟ=23, ᛡ=26, ᛠ=27, ᚣ=28
GP_WRONG['\u16DE'] = 22  # ᛞ was wrongly at 22
GP_WRONG['\u16DF'] = 23  # ᛟ was wrongly at 23
GP_WRONG['\u16E1'] = 26  # ᛡ was wrongly at 26
GP_WRONG['\u16E0'] = 27  # ᛠ was wrongly at 27
GP_WRONG['\u16A3'] = 28  # ᚣ was wrongly at 28

LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
         'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

# ============ HELPER FUNCTIONS ============
def ioc(values, alphabet_size=29):
    n = len(values)
    if n < 2: return 0
    counts = Counter(values)
    return sum(c*(c-1) for c in counts.values()) / (n*(n-1)) * alphabet_size

def to_latin(vals):
    return ''.join(LATIN[v] for v in vals)

def sieve_primes(n):
    is_prime = [True] * (n+1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5)+1):
        if is_prime[i]:
            for j in range(i*i, n+1, i):
                is_prime[j] = False
    return set(i for i in range(2, n+1) if is_prime[i])

def load_page(pg, gp_map):
    for p in [f'LiberPrimus/pages/page_{pg:02d}/runes.txt', f'LiberPrimus/pages/page_{pg}/runes.txt']:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                raw = f.read()
            return [gp_map[c] for c in raw if c in gp_map]
    return None

# ============ DEOR TOKENIZER (from verify_p20_independent.py - TRUSTED) ============
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,'K':5,'L':20,'M':19,
           'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':14}

def tokenize_oe_text(text):
    """Convert Old English text to GP values, handling digraphs and special chars."""
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
            if digraph == 'TH':
                values.append(2); i += 2
            elif digraph == 'NG':
                values.append(21); i += 2
            elif digraph == 'OE':
                values.append(22); i += 2
            elif digraph == 'AE':
                values.append(25); i += 2
            elif digraph in ('IA', 'IO'):
                values.append(27); i += 2
            elif digraph == 'EA':
                values.append(28); i += 2
            elif digraph == 'EO':
                values.append(12); i += 2
            elif text[i] in ENG2GP:
                values.append(ENG2GP[text[i]]); i += 1
            else:
                i += 1
        elif text[i] in ENG2GP:
            values.append(ENG2GP[text[i]]); i += 1
        else:
            i += 1
    return values

# Also try simple (no-digraph) conversion
def tokenize_oe_simple(text):
    """Convert each character individually, no digraph detection."""
    text = text.upper().replace(' ', '').replace('\n', '')
    for ch in '.,;:!?\'"()[]{}–—-0123456789':
        text = text.replace(ch, '')
    values = []
    for c in text:
        if c == 'Þ' or c == 'Ð':
            values.append(2)
        elif c == 'Æ':
            values.append(25)
        elif c in ENG2GP:
            values.append(ENG2GP[c])
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

# ============ MAIN ============
print("=" * 80)
print("VERIFICATION: Beaufort(Deor) on prime positions")
print("Testing with CORRECT and WRONG GP mappings")
print("=" * 80)

# Tokenize Deor both ways
deor_digraph = tokenize_oe_text(DEOR_OE)
deor_simple = tokenize_oe_simple(DEOR_OE)
print(f"Deor (digraph tokenizer): {len(deor_digraph)} tokens")
print(f"Deor (simple tokenizer): {len(deor_simple)} tokens")
print(f"Deor digraph first 30: {deor_digraph[:30]}")
print(f"Deor simple first 30: {deor_simple[:30]}")
print(f"Deor digraph as text: {to_latin(deor_digraph[:30])}")
print(f"Deor simple as text: {to_latin(deor_simple[:30])}")

# Pre-generate large prime set
ALL_PRIMES = sieve_primes(3500)

unsolved_pages = list(range(17, 55))

print(f"\n{'='*80}")
print("SECTION 1: P20 Verification (testing all combinations)")
print(f"{'='*80}")

for gp_label, gp_map in [("CORRECT", GP_CORRECT), ("WRONG", GP_WRONG)]:
    p20 = load_page(20, gp_map)
    if not p20:
        print(f"  ERROR: Could not load P20 with {gp_label} mapping")
        continue
    
    for deor_label, deor in [("digraph", deor_digraph), ("simple", deor_simple)]:
        max_idx = min(len(p20), len(deor))
        prime_pos = sorted([i for i in range(max_idx) if i in ALL_PRIMES])
        
        # Beaufort: (key - cipher) mod 29
        beau = [(deor[p] - p20[p]) % 29 for p in prime_pos]
        # Vigenere SUB: (cipher - key) mod 29
        sub = [(p20[p] - deor[p]) % 29 for p in prime_pos]
        # Vigenere ADD: (cipher + key) mod 29
        add = [(p20[p] + deor[p]) % 29 for p in prime_pos]
        
        print(f"\n  GP={gp_label}, Deor={deor_label}, #primes={len(prime_pos)}")
        print(f"    BEAU IoC={ioc(beau):.4f}  text: {to_latin(beau)[:60]}")
        print(f"    SUB  IoC={ioc(sub):.4f}  text: {to_latin(sub)[:60]}")
        print(f"    ADD  IoC={ioc(add):.4f}  text: {to_latin(add)[:60]}")
        
        # Also try sequential Deor (deor[0], deor[1], ...) instead of positional (deor[prime_pos])
        beau_seq = [(deor[i % len(deor)] - p20[prime_pos[i]]) % 29 for i in range(len(prime_pos))]
        sub_seq = [(p20[prime_pos[i]] - deor[i % len(deor)]) % 29 for i in range(len(prime_pos))]
        add_seq = [(p20[prime_pos[i]] + deor[i % len(deor)]) % 29 for i in range(len(prime_pos))]
        
        print(f"    BEAU_SEQ IoC={ioc(beau_seq):.4f}  text: {to_latin(beau_seq)[:60]}")
        print(f"    SUB_SEQ  IoC={ioc(sub_seq):.4f}  text: {to_latin(sub_seq)[:60]}")
        print(f"    ADD_SEQ  IoC={ioc(add_seq):.4f}  text: {to_latin(add_seq)[:60]}")

# Also check: raw IoC of P20 prime-position runes vs non-prime
print(f"\n{'='*80}")
print("SECTION 2: Raw IoC at prime vs non-prime positions")
print(f"{'='*80}")

for pg in unsolved_pages:
    p = load_page(pg, GP_CORRECT)
    if not p: continue
    n = len(p)
    prime_pos = sorted([i for i in range(n) if i in ALL_PRIMES])
    non_prime_pos = sorted([i for i in range(n) if i not in ALL_PRIMES])
    
    prime_vals = [p[i] for i in prime_pos]
    non_prime_vals = [p[i] for i in non_prime_pos]
    
    ioc_all = ioc(p)
    ioc_p = ioc(prime_vals)
    ioc_np = ioc(non_prime_vals)
    
    if abs(ioc_p - ioc_all) > 0.15 or abs(ioc_np - ioc_all) > 0.15:
        flag = " <-- NOTABLE"
    else:
        flag = ""
    
    print(f"  P{pg:02d} ({n:4d}): all={ioc_all:.3f}  prime({len(prime_pos):3d})={ioc_p:.3f}  non-prime({len(non_prime_pos):3d})={ioc_np:.3f}{flag}")

print(f"\n{'='*80}")
print("SECTION 3: Beaufort(Deor) at prime positions on ALL unsolved pages")
print(f"{'='*80}")

for pg in unsolved_pages:
    p = load_page(pg, GP_CORRECT)
    if not p: continue
    n = len(p)
    max_idx = min(n, len(deor_digraph))
    prime_pos = sorted([i for i in range(max_idx) if i in ALL_PRIMES])
    
    if len(prime_pos) < 5:
        continue
    
    # Beaufort positional
    beau_pos = [(deor_digraph[pp] - p[pp]) % 29 for pp in prime_pos]
    sub_pos = [(p[pp] - deor_digraph[pp]) % 29 for pp in prime_pos]
    
    # Beaufort sequential
    beau_seq = [(deor_digraph[i % len(deor_digraph)] - p[prime_pos[i]]) % 29 for i in range(len(prime_pos))]
    sub_seq = [(p[prime_pos[i]] - deor_digraph[i % len(deor_digraph)]) % 29 for i in range(len(prime_pos))]
    
    results = [
        ("BEAU_POS", ioc(beau_pos), beau_pos),
        ("SUB_POS", ioc(sub_pos), sub_pos),
        ("BEAU_SEQ", ioc(beau_seq), beau_seq),
        ("SUB_SEQ", ioc(sub_seq), sub_seq),
    ]
    
    best = max(results, key=lambda x: x[1])
    
    if best[1] > 1.15:
        print(f"  P{pg:02d} ({len(prime_pos):3d} primes): {best[0]} IoC={best[1]:.4f}  text: {to_latin(best[2])[:60]}")
        # Show all modes if best is notable
        if best[1] > 1.3:
            for label, ic, stream in results:
                print(f"       {label}: IoC={ic:.4f}  {to_latin(stream)[:60]}")
    else:
        print(f"  P{pg:02d} ({len(prime_pos):3d} primes): best={best[0]} IoC={best[1]:.4f}")

print(f"\n{'='*80}")
print("SECTION 4: Also test NON-prime positions with Deor")
print(f"{'='*80}")

for pg in unsolved_pages:
    p = load_page(pg, GP_CORRECT)
    if not p: continue
    n = len(p)
    non_prime_pos = sorted([i for i in range(n) if i not in ALL_PRIMES])
    
    if len(non_prime_pos) < 10:
        continue
    
    # Sequential Deor key on non-prime positions  
    for mode, label in [('beau', 'BEAU'), ('sub', 'SUB'), ('add', 'ADD')]:
        stream = []
        for idx, npp in enumerate(non_prime_pos):
            dk = deor_digraph[idx % len(deor_digraph)]
            cv = p[npp]
            if mode == 'beau':
                stream.append((dk - cv) % 29)
            elif mode == 'sub':
                stream.append((cv - dk) % 29)
            else:
                stream.append((cv + dk) % 29)
        ic = ioc(stream)
        if ic > 1.15:
            print(f"  P{pg:02d} non-prime ({len(non_prime_pos):3d}): {label}_SEQ IoC={ic:.4f}  {to_latin(stream)[:60]}")

print(f"\n{'='*80}")
print("SECTION 5: Test with WRONG mapping on P20 to reproduce old IoC=1.89")
print(f"{'='*80}")

p20_wrong = load_page(20, GP_WRONG)
p20_correct = load_page(20, GP_CORRECT)

if p20_wrong and p20_correct:
    # Count differences
    diffs = sum(1 for a, b in zip(p20_wrong, p20_correct) if a != b)
    print(f"P20 rune count: {len(p20_correct)}")
    print(f"Differences between WRONG and CORRECT mapping: {diffs}/{len(p20_correct)}")
    
    # Show which runes are affected
    affected_runes = set()
    for i, (w, c) in enumerate(zip(p20_wrong, p20_correct)):
        if w != c:
            affected_runes.add((w, c))
    print(f"Affected value pairs (wrong→correct): {affected_runes}")

print(f"\n{'='*80}")
print("SECTION 6: Beaufort with Deor refrain only")
print(f"{'='*80}")

# The Deor poem has a repeating refrain: "Þæs ofereode, þisses swa mæg"
REFRAIN_OE = "Þæs ofereode, þisses swa mæg"
refrain_tokens = tokenize_oe_text(REFRAIN_OE)
print(f"Refrain tokens: {refrain_tokens}")
print(f"Refrain text: {to_latin(refrain_tokens)}")
print(f"Refrain length: {len(refrain_tokens)}")

for pg in unsolved_pages:
    p = load_page(pg, GP_CORRECT)
    if not p: continue
    
    # Use refrain as repeating key (Vigenère/Beaufort)
    rlen = len(refrain_tokens)
    for mode, label in [('beau', 'BEAU'), ('sub', 'SUB'), ('add', 'ADD')]:
        stream = []
        ki = 0
        for ci in range(len(p)):
            cv = p[ci]
            if cv == 0:  # F-skip
                stream.append(0)
                continue
            dk = refrain_tokens[ki % rlen]
            if mode == 'beau':
                stream.append((dk - cv) % 29)
            elif mode == 'sub':
                stream.append((cv - dk) % 29)
            else:
                stream.append((cv + dk) % 29)
            ki += 1
        ic = ioc(stream)
        if ic > 1.25:
            print(f"  P{pg:02d} REFRAIN {label} (F-skip): IoC={ic:.4f}  {to_latin(stream)[:60]}")
    
    # Without F-skip
    for mode, label in [('beau', 'BEAU'), ('sub', 'SUB'), ('add', 'ADD')]:
        stream = [(refrain_tokens[i % rlen] - p[i]) % 29 if mode == 'beau' 
                   else (p[i] - refrain_tokens[i % rlen]) % 29 if mode == 'sub'
                   else (p[i] + refrain_tokens[i % rlen]) % 29 
                   for i in range(len(p))]
        ic = ioc(stream)
        if ic > 1.25:
            print(f"  P{pg:02d} REFRAIN {label} (no-skip): IoC={ic:.4f}  {to_latin(stream)[:60]}")

print(f"\n{'='*80}")
print("SECTION 7: Prime-VALUED rune separation (P20 Method 2)")
print(f"{'='*80}")

PRIME_GP_VALUES = {2, 3, 5, 7, 11, 13, 17, 19, 23}

for pg in [17, 18, 19, 20, 25, 32, 40, 44, 50]:
    p = load_page(pg, GP_CORRECT)
    if not p: continue
    
    prime_valued = [v for v in p if v in PRIME_GP_VALUES]
    non_prime_valued = [v for v in p if v not in PRIME_GP_VALUES]
    
    ic_pv = ioc(prime_valued)
    ic_npv = ioc(non_prime_valued)
    
    print(f"  P{pg:02d}: prime-valued={len(prime_valued)}(IoC={ic_pv:.3f}) non-prime-valued={len(non_prime_valued)}(IoC={ic_npv:.3f})")
    
    # Caesar shifts on non-prime-valued stream
    best_shift = max(range(29), key=lambda s: ioc([(v+s)%29 for v in non_prime_valued]))
    shifted = [(v+best_shift)%29 for v in non_prime_valued]
    print(f"         non-prime best shift={best_shift}: IoC={ioc(shifted):.3f}  {to_latin(shifted)[:60]}")

print(f"\n{'='*80}")
print("SECTION 8: Verify P20 decoded stream word quality")
print(f"{'='*80}")

# Get the CORRECT P20 prime-position Beaufort stream
p20c = load_page(20, GP_CORRECT)
max_idx = min(len(p20c), len(deor_digraph))
prime_pos = sorted([i for i in range(max_idx) if i in ALL_PRIMES])

beau_stream = [(deor_digraph[p] - p20c[p]) % 29 for p in prime_pos]
sub_stream = [(p20c[p] - deor_digraph[p]) % 29 for p in prime_pos]

print(f"P20 CORRECT BEAU_POS ({len(beau_stream)} runes): IoC={ioc(beau_stream):.4f}")
print(f"  Full text: {to_latin(beau_stream)}")
print(f"\nP20 CORRECT SUB_POS ({len(sub_stream)} runes): IoC={ioc(sub_stream):.4f}")
print(f"  Full text: {to_latin(sub_stream)}")

# Sequential key version
beau_seq = [(deor_digraph[i % len(deor_digraph)] - p20c[prime_pos[i]]) % 29 for i in range(len(prime_pos))]
sub_seq = [(p20c[prime_pos[i]] - deor_digraph[i % len(deor_digraph)]) % 29 for i in range(len(prime_pos))]

print(f"\nP20 CORRECT BEAU_SEQ ({len(beau_seq)} runes): IoC={ioc(beau_seq):.4f}")
print(f"  Full text: {to_latin(beau_seq)}")
print(f"\nP20 CORRECT SUB_SEQ ({len(sub_seq)} runes): IoC={ioc(sub_seq):.4f}")
print(f"  Full text: {to_latin(sub_seq)}")

# Now do 2x83 transposition on any stream with IoC > 1.3
for label, stream in [("BEAU_POS", beau_stream), ("SUB_POS", sub_stream), 
                       ("BEAU_SEQ", beau_seq), ("SUB_SEQ", sub_seq)]:
    ic = ioc(stream)
    n = len(stream)
    if ic > 1.3 and n > 10:
        # Try various column transpositions
        for cols in range(2, min(n//2 + 1, 100)):
            if n % cols != 0: continue
            rows = n // cols
            transposed = [0] * n
            for i in range(n):
                src_row = i // cols
                src_col = i % cols
                new_idx = src_col * rows + src_row
                if new_idx < n:
                    transposed[new_idx] = stream[i]
            ic_t = ioc(transposed)
            if ic_t > ic + 0.1:
                print(f"  {label} cols={cols}: IoC {ic:.3f} → {ic_t:.3f}  {to_latin(transposed)[:60]}")

print("\nDONE")
