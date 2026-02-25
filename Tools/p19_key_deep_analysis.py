"""
Deep analysis of P19 key vs LP1_FWD offset 561 — 12/43 zero-diffs.
Also: exhaustive search for the P19 key source using broader methods.
"""
import os, sys
from collections import Counter

os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

# === GP Mapping ===
GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,'K':5,'L':20,'M':19,
           'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':14}

def tokenize_english(text):
    text = text.upper().replace(' ', '').replace('\n', '')
    for ch in '.,;:!?\'"()[]{}–—-0123456789':
        text = text.replace(ch, '')
    values = []
    i = 0
    while i < len(text):
        if i + 2 < len(text) and text[i:i+3] == 'ING':
            values.append(10); values.append(21); i += 3
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

def to_english(gp_values):
    return ''.join(LATIN[v] for v in gp_values)

# P19 key (43 values, ADD mode)
P19_KEY = [24, 15, 2, 24, 4, 21, 11, 10, 20, 16, 9, 19, 26, 11, 7, 5, 11, 6, 27, 8, 22, 25, 21, 16, 25, 0, 27, 9, 21, 7, 27, 15, 21, 9, 3, 16, 5, 22, 18, 4, 5, 18, 23]

# Build full LP1 token stream
LP_SOLVED = {
    'P00': "LIBER PRIMUS",
    'P01': "A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE TEST THE KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH DO NOT EDIT OR CHANGE THIS BOOK OR THE MESSAGE CONTAINED WITHIN EITHER THE WORDS OR THEIR NUMBERS FOR ALL IS SACRED",
    'P02': "CHAPTER I INTUS",
    'P03': "WELCOME WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS IT IS NOT AN EASY TRIP BUT FOR THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE ALONG THE WAY YOU WILL FIND AN END TO ALL STRUGGLE AND SUFFERING YOUR INNOCENCE YOUR ILLUSIONS YOUR CERTAINTY AND YOUR REALITY ULTIMATELY YOU WILL DISCOVER AN END TO SELF",
    'P04': "IT IS THROUGH THIS PILGRIMAGE THAT WE SHAPE OURSELVES AND OUR REALITIES JOURNEY DEEP WITHIN AND YOU WILL ARRIVE OUTSIDE LIKE THE INSTAR IT IS ONLY THROUGH GOING WITHIN THAT WE MAY EMERGE WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY AN INSTRUCTION COMMAND YOUR OWN SELF",
    'P05': "SOME WISDOM THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED ALL THINGS SHOULD BE ENCRYPTED",
    'P06_09': "A KOAN A MAN DECIDED TO GO AND STUDY WITH A MASTER HE WENT TO THE DOOR OF THE MASTER WHO ARE YOU WHO WISHES TO STUDY HERE ASKED THE MASTER THE STUDENT TOLD THE MASTER HIS NAME THAT IS NOT WHAT YOU ARE THAT IS ONLY WHAT YOU ARE CALLED WHO ARE YOU WHO WISHES TO STUDY HERE HE ASKED AGAIN THE MAN THOUGHT FOR A MOMENT AND REPLIED I AM A PROFESSOR THAT IS WHAT YOU DO NOT WHAT YOU ARE REPLIED THE MASTER WHO ARE YOU WHO WISHES TO STUDY HERE CONFUSED THE MAN THOUGHT SOME MORE FINALLY HE ANSWERED I AM A HUMAN BEING THAT IS ONLY YOUR SPECIES NOT WHO YOU ARE WHO ARE YOU WHO WISHES TO STUDY HERE ASKED THE MASTER AGAIN AFTER A MOMENT OF THOUGHT THE PROFESSOR REPLIED I AM A CONSCIOUSNESS INHABITING AN ARBITRARY BODY THAT IS MERELY WHAT YOU ARE NOT WHO YOU ARE WHO ARE YOU WHO WISHES TO STUDY HERE THE MAN WAS GETTING IRRITATED I AM HE STARTED BUT HE COULD NOT THINK OF ANYTHING ELSE TO SAY SO HE TRAILED OFF AFTER A LONG PAUSE THE MASTER REPLIED THEN YOU ARE WELCOME TO COME STUDY AN INSTRUCTION DO FOUR UNREASONABLE THINGS EACH DAY",
    'P10_13': "THE LOSS OF DIVINITY THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS WHICH CAUSE THE LOSS OF DIVINITY CONSUMPTION WE CONSUME TOO MUCH BECAUSE WE BELIEVE THE FOLLOWING TWO ERRORS WITHIN THE DECEPTION WE DO NOT HAVE ENOUGH OR THERE IS NOT ENOUGH WE HAVE WHAT WE HAVE NOW BY LUCK AND WE WILL NOT BE STRONG ENOUGH LATER TO OBTAIN WHAT WE NEED MOST THINGS ARE NOT WORTH CONSUMING PRESERVATION WE PRESERVE THINGS BECAUSE WE BELIEVE WE ARE WEAK IF WE LOSE THEM WE WILL NOT BE STRONG ENOUGH TO GAIN THEM AGAIN THIS IS THE DECEPTION MOST THINGS ARE NOT WORTH PRESERVING ADHERENCE WE FOLLOW DOGMA SO THAT WE CAN BELONG AND BE RIGHT OR WE FOLLOW REASON SO WE CAN BELONG AND BE RIGHT THERE IS NOTHING TO BE RIGHT ABOUT TO BELONG IS DEATH IT IS THE BEHAVIORS OF CONSUMPTION PRESERVATION AND ADHERENCE THAT HAVE US LOSE OUR PRIMALITY AND THUS OUR DIVINITY SOME WISDOM AMASS GREAT WEALTH NEVER BECOME ATTACHED TO WHAT YOU OWN BE PREPARED TO DESTROY ALL THAT YOU OWN AN INSTRUCTION PROGRAM YOUR MIND PROGRAM REALITY",
    'P14_15': "A KOAN DURING A LESSON THE MASTER EXPLAINED THE I THE I IS THE VOICE OF THE CIRCUMFERENCE HE SAID WHEN ASKED BY A STUDENT TO EXPLAIN WHAT THAT MEANT THE MASTER SAID IT IS A VOICE INSIDE YOUR HEAD I DONT HAVE A VOICE IN MY HEAD THOUGHT THE STUDENT AND HE RAISED HIS HAND TO TELL THE MASTER THE MASTER STOPPED THE STUDENT AND SAID THE VOICE THAT JUST SAID YOU HAVE NO VOICE IN YOUR HEAD IS THE I AND THE STUDENTS WERE ENLIGHTENED",
    'P16': "AN INSTRUCTION QUESTION ALL THINGS DISCOVER TRUTH INSIDE YOURSELF FOLLOW YOUR TRUTH IMPOSE NOTHING ON OTHERS",
}

# Build LP1 tokens with per-character tracking
all_text = ""
page_boundaries = []
for name in ['P00', 'P01', 'P02', 'P03', 'P04', 'P05', 'P06_09', 'P10_13', 'P14_15', 'P16']:
    start_idx = len(all_text.replace(' ', ''))
    text = LP_SOLVED[name]
    all_text += text + " "
    end_idx = len(all_text.replace(' ', ''))
    page_boundaries.append((name, start_idx, end_idx))

lp1_tokens = tokenize_english(all_text)
print(f"LP1 total tokens: {len(lp1_tokens)}")
print(f"\nPage boundaries (in token positions):")
for name, s, e in page_boundaries:
    print(f"  {name}: chars {s}-{e}")

# === Analyze offset 561 ===
print("\n" + "="*80)
print("ANALYSIS: LP1_FWD offset=561, 12/43 zero-diffs")
print("="*80)

offset = 561
text_slice = lp1_tokens[offset:offset+43]
diff = [(P19_KEY[i] - text_slice[i]) % 29 for i in range(43)]

print(f"\nKey:  {P19_KEY}")
print(f"Text: {list(text_slice)}")
print(f"Diff: {diff}")
print(f"Key as runeglish:  {to_english(P19_KEY)}")
print(f"Text as runeglish: {to_english(text_slice)}")
print(f"Diff as runeglish: {to_english(diff)}")

# Which positions match?
match_positions = [i for i in range(43) if diff[i] == 0]
print(f"\nZero-diff positions: {match_positions}")
print(f"  Key chars at matches: {[LATIN[P19_KEY[i]] for i in match_positions]}")

# What text does offset 561 correspond to?
# Need to find which page
for name, s, e in page_boundaries:
    if s <= 561 < e:
        print(f"\nOffset 561 falls in {name} (chars {s}-{e})")
        print(f"  Position within page: {561 - s}")
        break

# Build the original English text character by character to map
print("\n--- Surrounding original text at offset 561 ---")
clean_text = ""
for name in ['P00', 'P01', 'P02', 'P03', 'P04', 'P05', 'P06_09', 'P10_13', 'P14_15', 'P16']:
    clean_text += LP_SOLVED[name]
# Map to tokens to find where offset 561 falls in the original text
# This is approximate since digraphs merge chars
print(f"Approximate text near token 561: ...{clean_text[500:600]}...")

# === Now exhaustively check ALL offsets with all ops ===
print("\n" + "="*80)
print("EXHAUSTIVE: Check if diff pattern has structure at any offset")
print("="*80)

# For each offset, compute (key - text) mod 29 and check if 
# the non-zero diffs have any hidden structure

def check_structure(diff):
    """Check various structural patterns in the difference vector"""
    results = []
    
    # Constant?
    if len(set(diff)) == 1:
        results.append(f"CONSTANT: {diff[0]}")
    
    # Periodic?
    for p in range(2, 22):
        is_periodic = True
        for i in range(p, len(diff)):
            if diff[i] != diff[i % p]:
                is_periodic = False
                break
        if is_periodic:
            results.append(f"PERIOD-{p}: {diff[:p]}")
    
    # Linear (a*i + b) mod 29?
    for a in range(29):
        for b in range(29):
            if all(diff[i] == (a*i + b) % 29 for i in range(len(diff))):
                results.append(f"LINEAR: ({a}*i + {b}) mod 29")
    
    # Quadratic (a*i^2 + b*i + c) mod 29?
    for a in range(29):
        for b in range(29):
            c = diff[0]
            if all(diff[i] == (a*i*i + b*i + c) % 29 for i in range(len(diff))):
                results.append(f"QUADRATIC: ({a}*i^2 + {b}*i + {c}) mod 29")
    
    return results

# Check the top offsets more deeply
print("\nTop 10 offsets by zero-diff count:")
offset_scores = []
for offset in range(len(lp1_tokens) - 42):
    text_slice = lp1_tokens[offset:offset+43]
    diff = [(P19_KEY[i] - text_slice[i]) % 29 for i in range(43)]
    zeros = diff.count(0)
    offset_scores.append((zeros, offset, diff))

offset_scores.sort(key=lambda x: -x[0])

for zeros, off, diff in offset_scores[:10]:
    print(f"\n  Offset {off}: {zeros}/43 zero-diffs")
    print(f"    Diff: {diff}")
    # Check non-zero positions for structure
    nz_positions = [(i, diff[i]) for i in range(43) if diff[i] != 0]
    nz_vals = [diff[i] for i in range(43) if diff[i] != 0]
    print(f"    Non-zero values: {nz_vals}")
    structs = check_structure(diff)
    if structs:
        for s in structs:
            print(f"    *** STRUCTURE FOUND: {s} ***")
    
    # Check if non-zero diffs form a word
    nz_text = to_english(nz_vals)
    print(f"    Non-zero as text: {nz_text}")

# === Check if P19 key matches CIPHERTEXT of other pages (not plaintext) ===
print("\n" + "="*80)
print("P19 KEY vs CIPHERTEXT of other pages")
print("="*80)

def load_page(pg):
    for p in [f'LiberPrimus/pages/page_{pg:02d}/runes.txt', f'LiberPrimus/pages/page_{pg}/runes.txt']:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                raw = f.read()
                return [GP[c] for c in raw if c in GP]
    return None

for pg in list(range(0, 75)):
    cipher = load_page(pg)
    if cipher is None or len(cipher) < 43:
        continue
    
    # Check if P19 key appears as a substring of this page's ciphertext
    for offset in range(len(cipher) - 42):
        matches = sum(1 for i in range(43) if cipher[offset+i] == P19_KEY[i])
        if matches >= 10:
            print(f"  P{pg:02d} offset {offset}: {matches}/43 matches with P19 key")

# === Check P19 key vs prime-modified ciphertext of solved pages ===
print("\n" + "="*80)
print("P19 KEY vs PRIMES applied to LP1 tokens")
print("="*80)

def sieve_primes(n):
    is_prime = [True] * (n+1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5)+1):
        if is_prime[i]:
            for j in range(i*i, n+1, i):
                is_prime[j] = False
    return [i for i in range(2, n+1) if is_prime[i]]

PRIMES = sieve_primes(10000)

# Test: key[i] = (lp1_tokens[off+i] + prime[i]) % 29  etc.
for mode_name, op in [('TEXT+PRIME', lambda t,p: (t+p)%29), ('TEXT-PRIME', lambda t,p: (t-p)%29), ('PRIME-TEXT', lambda t,p: (p-t)%29)]:
    best_m, best_o = 0, 0
    for offset in range(len(lp1_tokens) - 42):
        candidate = [op(lp1_tokens[offset+i], PRIMES[i] % 29) for i in range(43)]
        matches = sum(1 for i in range(43) if candidate[i] == P19_KEY[i])
        if matches > best_m:
            best_m = matches
            best_o = offset
    print(f"  {mode_name}: best offset={best_o}, {best_m}/43 matches")

# Test: key[i] = (lp1_tokens[off+i] + euler_totient(prime[i])) % 29
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

for mode_name, op in [('TEXT+TOT', lambda t,i: (t+euler_totient(PRIMES[i]))%29), ('TEXT-TOT', lambda t,i: (t-euler_totient(PRIMES[i]))%29)]:
    best_m, best_o = 0, 0
    for offset in range(len(lp1_tokens) - 42):
        candidate = [op(lp1_tokens[offset+i], i) for i in range(43)]
        matches = sum(1 for i in range(43) if candidate[i] == P19_KEY[i])
        if matches > best_m:
            best_m = matches
            best_o = offset
    print(f"  {mode_name}: best offset={best_o}, {best_m}/43 matches")

# === KEY AS AUTOKEY with LP1 as seed ===
print("\n" + "="*80)
print("P19 KEY: AUTOKEY CHECK (key[i] = previous plaintext/cipher value?)")
print("="*80)
# P19 known plaintext: REARRANGINGTHEPRIMESNUMBERSWILLSHOWAPATHTOTHEDEOR
p19_plain = tokenize_english("REARRANGINGTHEPRIMESNUMBERSWILLSHOWAPATHTOTHEDEOR")
p19_cipher = load_page(19)
nk = len(P19_KEY)
np19 = min(nk, len(p19_plain))

print(f"P19 plaintext ({len(p19_plain)}): {p19_plain[:nk]}")
print(f"P19 cipher ({len(p19_cipher)}):    {list(p19_cipher[:nk])}")
print(f"P19 key ({nk}):       {P19_KEY}")

# Check if key[i] = plaintext[i-lag] (autokey with plaintext)
for lag in range(1, 10):
    matches = sum(1 for i in range(lag, np19) if P19_KEY[i] == p19_plain[i-lag])
    if matches > 3:
        print(f"  Key[i] == plain[i-{lag}]: {matches}/{np19-lag} matches")

# Check if key[i] = cipher[i-lag] (autokey with ciphertext)
for lag in range(1, 10):
    matches = sum(1 for i in range(lag, nk) if P19_KEY[i] == p19_cipher[i-lag])
    if matches > 3:
        print(f"  Key[i] == cipher[i-{lag}]: {matches}/{nk-lag} matches")

# Check if key[i] = key[i-lag] + something (recurrence)
for lag in range(1, 10):
    diffs = [(P19_KEY[i] - P19_KEY[i-lag]) % 29 for i in range(lag, nk)]
    unique_diffs = len(set(diffs))
    if unique_diffs <= 5:
        print(f"  Key[i] - key[i-{lag}] mod 29: only {unique_diffs} unique values: {set(diffs)}")
    # Check if diffs match plaintext
    matches = sum(1 for i in range(lag, np19) if diffs[i-lag] == p19_plain[i])
    if matches > 3:
        print(f"  (Key[i]-key[i-{lag}]) == plain[i]: {matches}/{np19-lag}")


# === WHAT ABOUT: Each page uses its OWN ciphertext as running key for the NEXT page? ===
print("\n" + "="*80)
print("CIPHER CHAINING: Does page N's ciphertext serve as key for page N+1?")
print("="*80)

def ioc(values, alphabet_size=29):
    n = len(values)
    if n < 2: return 0
    counts = Counter(values)
    return sum(c*(c-1) for c in counts.values()) / (n*(n-1)) * alphabet_size

unsolved_pages = list(range(18, 55))
for pg in unsolved_pages:
    cipher = load_page(pg)
    if cipher is None:
        continue
    
    # Try previous page's ciphertext as key  
    for prev_pg in [pg-1, pg-2, pg+1]:
        prev_cipher = load_page(prev_pg)
        if prev_cipher is None:
            continue
        
        n = min(len(cipher), len(prev_cipher))
        if n < 50:
            continue
        
        for mode_name, op in [('SUB', lambda c,k: (c-k)%29), ('ADD', lambda c,k: (c+k)%29), ('BEAU', lambda c,k: (k-c)%29)]:
            plain = [op(cipher[i], prev_cipher[i]) for i in range(n)]
            ic = ioc(plain)
            if ic > 1.30:
                text = to_english(plain[:50])
                print(f"  P{pg} key=P{prev_pg} {mode_name}: IoC={ic:.4f} | {text}")

# Also try solved plaintext of known pages as key for their neighbors
print("\n--- Known plaintext as key for adjacent unsolved pages ---")
solved_gp = {}
for name, text in LP_SOLVED.items():
    solved_gp[name] = tokenize_english(text)

# P16 plaintext as key for P17
p16_gp = solved_gp['P16']
p17 = load_page(17)
if p17:
    n = min(len(p16_gp), len(p17))
    for mode_name, op in [('SUB', lambda c,k: (c-k)%29), ('ADD', lambda c,k: (c+k)%29), ('BEAU', lambda c,k: (k-c)%29)]:
        plain = [op(p17[i], p16_gp[i % len(p16_gp)]) for i in range(len(p17))]
        ic = ioc(plain)
        print(f"  P17 key=P16_plain(cycled) {mode_name}: IoC={ic:.4f}")

# P05 plaintext as key for P17 (since P05 mentions primes)
p05_gp = solved_gp['P05']
if p17:
    n = min(len(p05_gp), len(p17))
    for mode_name, op in [('SUB', lambda c,k: (c-k)%29), ('ADD', lambda c,k: (c+k)%29), ('BEAU', lambda c,k: (k-c)%29)]:
        plain = [op(p17[i], p05_gp[i % len(p05_gp)]) for i in range(len(p17))]
        ic = ioc(plain)
        print(f"  P17 key=P05_plain(cycled) {mode_name}: IoC={ic:.4f}")

print("\nDone.")
