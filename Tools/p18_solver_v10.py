"""
P18 SOLVER v10 - Verify SOLUTION.md candidate & non-repeating key analysis

SOLUTION.md claims the FIRST 53 runes decrypt to:
"BEING OF ALL I WILL ASC THE OATH IS SWORN TO THE ONE WITHIN THE ABOVE THE WAY"

Key insight: The key length equals the plaintext length (53), and the key 
DOESN'T REPEAT for the rest of the page. This means:
1. The repeating-key assumption was WRONG
2. The 34 "confirmed" values from previous solvers may be artifacts
3. We need to find the full 260-rune key, not just a 53-rune repeating key

Strategy:
- Verify the first-53 candidate
- Derive the first-period key
- Test if subsequent key values follow a pattern (autokey, LFSR, progressive, etc.)
"""
import os, sys
from collections import Counter

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,'K':5,'L':20,
          'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}
DIGRAPHS = {'TH':2,'NG':21,'EO':12,'OE':22,'EA':28,'AE':25,'IA':27}
MOD = 29

os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

def load_page(pg):
    with open(f'LiberPrimus/pages/page_{pg:02d}/runes.txt','r',encoding='utf-8') as f:
        raw = f.read()
    runes = [GP[c] for c in raw if c in GP]
    # Also get word boundaries
    words, current, start, pos = [], [], 0, 0
    for c in raw:
        if c in GP:
            if not current: start = pos
            current.append(GP[c]); pos += 1
        elif current:
            words.append((start, list(current))); current = []
    if current: words.append((start, list(current)))
    return runes, words, raw

def text_to_gp(text):
    """Convert English text to GP values. Handles digraphs."""
    result = []
    i = 0
    text = text.upper()
    while i < len(text):
        if text[i] == ' ' or text[i] == '\n':
            i += 1
            continue
        # Try digraph first
        if i + 1 < len(text):
            di = text[i:i+2]
            if di in DIGRAPHS:
                result.append(DIGRAPHS[di])
                i += 2
                continue
        # Single character
        if text[i] in ENG2GP:
            result.append(ENG2GP[text[i]])
        else:
            print(f"  WARNING: unknown char '{text[i]}'")
            result.append(0)
        i += 1
    return result

cipher, words, raw = load_page(18)
N = len(cipher)
print(f"P18: {N} runes, {len(words)} words")

# =======================================================================
# Phase 1: Verify SOLUTION.md candidate for first 53 runes
# =======================================================================
print(f"\n{'='*80}")
print(f"Phase 1: Verify SOLUTION.md candidate")
print(f"{'='*80}")

# The claimed plaintext
candidate = "BEING OF ALL I WILL ASC THE OATH IS SWORN TO THE ONE WITHIN THE ABOVE THE WAY"
# Note: in Cicada runes, V->U (or F), K->C
# ABOVE -> A,B,O,V(=U or F),E  Let's try both

# Version with V=U: ABOUE
plain_v1 = text_to_gp("BEING OF ALL I WILL ASC THE OATH IS SWORN TO THE ONE WITHIN THE ABOUE THE WAY")
# Version with V=F: ABOFE  
plain_v2 = text_to_gp("BEING OF ALL I WILL ASC THE OATH IS SWORN TO THE ONE WITHIN THE ABOFE THE WAY")
# Version as-is (V->U by default mapping)
plain_v3 = text_to_gp(candidate)

for desc, plain in [("V=U (ABOUE)", plain_v1), ("V=F (ABOFE)", plain_v2), ("Default V=U", plain_v3)]:
    print(f"\n  Candidate ({desc}): {len(plain)} runes")
    if len(plain) != 53:
        print(f"    Length mismatch! Expected 53, got {len(plain)}")
        # Show the breakdown
        for word in candidate.split():
            gp = text_to_gp(word)
            print(f"    '{word}' -> {gp} ({len(gp)} runes: {''.join(LAT[v] for v in gp)})")
        continue
    
    # Derive key for first 53 positions: key[i] = (cipher[i] - plain[i]) % 29
    key_first53 = [(cipher[i] - plain[i]) % MOD for i in range(53)]
    print(f"    Key: {key_first53}")
    print(f"    Key (LAT): {''.join(LAT[v] for v in key_first53)}")
    
    # Check the SOLUTION.md key
    solution_key = [11, 6, 1, 20, 25, 20, 9, 15, 24, 26, 25, 7, 19, 8, 10, 24, 18, 9, 0, 16, 9, 4, 14, 22, 13, 13, 3, 28, 5, 21, 24, 19, 5, 1, 27, 14, 6, 17, 24, 24, 22, 8, 23, 6, 22, 19, 2, 11, 3, 19, 25, 15, 24]
    print(f"    SOLUTION.md key: {solution_key}")
    matches = sum(1 for a, b in zip(key_first53, solution_key) if a == b)
    print(f"    Matches with SOLUTION.md key: {matches}/53")

# Also check: what does the SOLUTION.md key actually decrypt the first 53 to?
solution_key = [11, 6, 1, 20, 25, 20, 9, 15, 24, 26, 25, 7, 19, 8, 10, 24, 18, 9, 0, 16, 9, 4, 14, 22, 13, 13, 3, 28, 5, 21, 24, 19, 5, 1, 27, 14, 6, 17, 24, 24, 22, 8, 23, 6, 22, 19, 2, 11, 3, 19, 25, 15, 24]
if len(solution_key) == 53:
    dec_first53 = [(cipher[i] - solution_key[i]) % MOD for i in range(53)]
    text_first53 = ''.join(LAT[v] for v in dec_first53)
    print(f"\n  SOLUTION.md key decrypts first 53 runes to:")
    print(f"    {text_first53}")
    # Show word by word
    words_text = []
    for start, wrunes in words:
        if start + len(wrunes) > 53: break
        vals = [(cipher[start+j] - solution_key[start+j]) % MOD for j in range(len(wrunes))]
        words_text.append(''.join(LAT[v] for v in vals))
    print(f"    Words: {' '.join(words_text)}")

# =======================================================================
# Phase 2: Use the verified key and analyze remaining positions
# =======================================================================
print(f"\n{'='*80}")
print(f"Phase 2: Key continuation analysis")
print(f"{'='*80}")

# Use the SOLUTION.md key for the first 53 runes
first_key = solution_key

# Now check what happens if we repeat this key
dec_repeat = [(cipher[i] - first_key[i % 53]) % MOD for i in range(N)]
text_repeat = ''.join(LAT[v] for v in dec_repeat)

# Word analysis
WORDLIST = set()
try:
    with open('Tools/english_words.txt', 'r') as f:
        for line in f:
            w = line.strip().upper()
            if len(w) >= 1: WORDLIST.add(w)
except:
    WORDLIST = set('A I AM AN AS AT BE BY DO GO HE IF IN IS IT ME MY NO OF OH OK ON OR SO TO UP US WE THE AND FOR ARE BUT NOT YOU ALL CAN HER WAS ONE OUR OUT HAD HAS HIS HOW ITS MAY NEW NOW OLD SEE WAY WHO BOY DID GET HAS HIM LET PUT SAY SHE TOO USE DAD MOM THAT WITH HAVE THIS WILL YOUR FROM THEY BEEN CALL CAME COME EACH FIND GIVE GOOD GREAT HERE JUST KNOW LIKE LONG LOOK MAKE MANY MOST NAME OVER PART SOME THEM THEN WHAT WHEN WILL WITH WORK YEAR ABOUT AFTER BEING COULD EVERY FIRST GREAT HOUSE LARGE MIGHT NEVER OTHER RIGHT SHALL SMALL SOUND STILL THEIR THERE THESE THINK THREE WHERE WHICH WORLD WOULD WRITE YOUNG BEFORE CHANGE DIFFER FOLLOW NUMBER SHOULD THOUGHT THROUGH'.split())

SMALL_WORDS = set('A I AM AN AS AT BE BY DO GO HE IF IN IS IT ME MY NO OF OH OK ON OR SO TO UP US WE THE AND FOR ARE BUT NOT YOU ALL CAN HER WAS ONE OUR OUT HAD HAS HIS HOW ITS MAY NOW OLD SEE WAY WHO DID GET HIM HIS LET PUT SAY SHE TOO USE THAT WITH HAVE THIS WILL YOUR FROM THEY BEEN EACH FIND SOME THEM THEN WHAT WHEN WITH WILL'.split())

print(f"\n  Repeating key (period 53) - Words:")
n_match = 0
for wi, (start, wrunes) in enumerate(words):
    vals = dec_repeat[start:start+len(wrunes)]
    txt = ''.join(LAT[v] for v in vals)
    is_match = txt.upper() in WORDLIST or txt.upper() in SMALL_WORDS
    marker = "Y" if is_match else " "
    if is_match: n_match += 1
    period = start // 53
    print(f"  {marker} w{wi:2d} (pos {start:3d}, P{period}): '{txt}'")
print(f"  Total matches: {n_match}/{len(words)}")

# =======================================================================
# Phase 3: What key values would make the REST of the page English?
# =======================================================================
print(f"\n{'='*80}")
print(f"Phase 3: Full key stream analysis")
print(f"{'='*80}")

# If this is a non-repeating key, what would the FULL key stream be
# that makes the entire page English?
# For each position i >= 53, key[i] is unknown.
# Let's try several models:

# Model A: Autokey (plaintext feedback)
# key[i] = plain[i-53] for i >= 53
print("\n--- Model A: Autokey SUB (plaintext feedback, period 53) ---")
dec_autokey = [0] * N
for i in range(N):
    if i < 53:
        dec_autokey[i] = (cipher[i] - first_key[i]) % MOD
    else:
        # key[i] = dec[i-53]
        dec_autokey[i] = (cipher[i] - dec_autokey[i-53]) % MOD

text_ak = ''.join(LAT[v] for v in dec_autokey)
counts = Counter(dec_autokey[53:])
ioc_ak = sum(c*(c-1) for c in counts.values()) / (len(dec_autokey[53:])*(len(dec_autokey[53:])-1)) * MOD if len(dec_autokey[53:]) > 1 else 0
print(f"  IoC*29 (pos 53+): {ioc_ak:.3f}")
print(f"  Words (pos 53+):")
n_match = 0
for wi, (start, wrunes) in enumerate(words):
    if start < 53: continue
    vals = dec_autokey[start:start+len(wrunes)]
    txt = ''.join(LAT[v] for v in vals)
    is_match = txt.upper() in WORDLIST or txt.upper() in SMALL_WORDS
    marker = "Y" if is_match else " "
    if is_match: n_match += 1
    print(f"  {marker} w{wi:2d} (pos {start:3d}): '{txt}'")
print(f"  Matches (pos 53+): {n_match}")

# Model B: Cipher feedback
# key[i] = cipher[i-53] for i >= 53
print("\n--- Model B: Cipher feedback ---")
dec_cfb = [0] * N
for i in range(N):
    if i < 53:
        dec_cfb[i] = (cipher[i] - first_key[i]) % MOD
    else:
        dec_cfb[i] = (cipher[i] - cipher[i-53]) % MOD

text_cfb = ''.join(LAT[v] for v in dec_cfb)
counts = Counter(dec_cfb[53:])
ioc_cfb = sum(c*(c-1) for c in counts.values()) / (len(dec_cfb[53:])*(len(dec_cfb[53:])-1)) * MOD if len(dec_cfb[53:]) > 1 else 0
print(f"  IoC*29 (pos 53+): {ioc_cfb:.3f}")
n_match = 0
for wi, (start, wrunes) in enumerate(words):
    if start < 53: continue
    vals = dec_cfb[start:start+len(wrunes)]
    txt = ''.join(LAT[v] for v in vals)
    is_match = txt.upper() in WORDLIST or txt.upper() in SMALL_WORDS
    marker = "Y" if is_match else " "
    if is_match: n_match += 1
    print(f"  {marker} w{wi:2d} (pos {start:3d}): '{txt}'")
print(f"  Matches (pos 53+): {n_match}")

# Model C: Key addition (progressive)
# key[i] = (first_key[i%53] + delta * (i // 53)) % 29
print("\n--- Model C: Progressive key (delta shift per period) ---")
for delta in range(1, 29):
    dec_prog = [(cipher[i] - (first_key[i%53] + delta * (i//53)) % MOD) % MOD for i in range(N)]
    n_match = 0
    for wi, (start, wrunes) in enumerate(words):
        if start < 53: continue
        vals = dec_prog[start:start+len(wrunes)]
        txt = ''.join(LAT[v] for v in vals).upper()
        if txt in WORDLIST or txt in SMALL_WORDS: n_match += 1
    if n_match >= 3:
        print(f"  Delta {delta}: {n_match} word matches (pos 53+)")

# Model D: Key multiplication (progressive)
# key[i] = first_key[i%53] * mult^(i//53) % 29
print("\n--- Model D: Multiplicative progressive key ---")
for mult in range(2, 29):
    dec_mult = [0] * N
    for i in range(N):
        period = i // 53
        key_val = (first_key[i%53] * pow(mult, period, MOD)) % MOD
        dec_mult[i] = (cipher[i] - key_val) % MOD
    n_match = 0
    for wi, (start, wrunes) in enumerate(words):
        if start < 53: continue
        vals = dec_mult[start:start+len(wrunes)]
        txt = ''.join(LAT[v] for v in vals).upper()
        if txt in WORDLIST or txt in SMALL_WORDS: n_match += 1
    if n_match >= 3:
        print(f"  Mult {mult}: {n_match} word matches (pos 53+)")

# Model E: LFSR on the full key stream (not period-53)
# Check if the first 53 key values follow an LFSR of low degree
print("\n--- Model E: LFSR check on first-period key ---")
def lfsr_check(seq, degree):
    """Check if sequence follows linear recurrence of given degree."""
    if len(seq) < 2 * degree:
        return None
    # Build system
    matrix = []
    rhs = []
    for i in range(degree, len(seq)):
        row = [seq[i-d-1] for d in range(degree)]
        matrix.append(row)
        rhs.append(seq[i])
    
    # Solve first 'degree' equations
    if len(matrix) < degree:
        return None
    
    # Gaussian elimination over GF(29)
    n = degree
    aug = [list(matrix[i][:n]) + [rhs[i]] for i in range(n)]
    
    for col in range(n):
        # Find pivot
        pivot = None
        for r in range(col, n):
            if aug[r][col] % MOD != 0:
                pivot = r
                break
        if pivot is None:
            return None
        aug[col], aug[pivot] = aug[pivot], aug[col]
        
        inv = pow(aug[col][col], -1, MOD)
        aug[col] = [(v * inv) % MOD for v in aug[col]]
        
        for r in range(n):
            if r != col and aug[r][col] != 0:
                factor = aug[r][col]
                aug[r] = [(aug[r][j] - factor * aug[col][j]) % MOD for j in range(n + 1)]
    
    coeffs = [aug[i][n] % MOD for i in range(n)]
    
    # Verify against ALL data
    n_ok = 0
    for i in range(degree, len(seq)):
        predicted = sum(coeffs[d] * seq[i-d-1] for d in range(degree)) % MOD
        if predicted == seq[i]:
            n_ok += 1
    
    n_total = len(seq) - degree
    return coeffs, n_ok, n_total

for deg in range(1, 26):
    result = lfsr_check(first_key, deg)
    if result:
        coeffs, n_ok, n_total = result
        if n_ok == n_total:
            print(f"  Degree {deg}: PERFECT FIT ({n_ok}/{n_total})! Coeffs: {coeffs}")
            # Generate extended key
            ext_key = list(first_key)
            for i in range(53, N):
                val = sum(coeffs[d] * ext_key[i-d-1] for d in range(deg)) % MOD
                ext_key.append(val)
            # Decrypt with extended key
            dec_lfsr = [(cipher[i] - ext_key[i]) % MOD for i in range(N)]
            n_match = 0
            for wi, (start, wrunes) in enumerate(words):
                if start < 53: continue
                vals = dec_lfsr[start:start+len(wrunes)]
                txt = ''.join(LAT[v] for v in vals).upper()
                if txt in WORDLIST or txt in SMALL_WORDS: n_match += 1
            print(f"    Extended LFSR key -> {n_match} word matches (pos 53+)")
            if n_match >= 5:
                print(f"    PROMISING! Full decryption:")
                for wi, (start, wrunes) in enumerate(words):
                    vals = dec_lfsr[start:start+len(wrunes)]
                    txt = ''.join(LAT[v] for v in vals)
                    print(f"      w{wi}: '{txt}'")
        elif n_ok > n_total * 0.9:
            print(f"  Degree {deg}: {n_ok}/{n_total} correct")

# =======================================================================
# Phase 4: Beaufort and ADD alternatives for first 53
# =======================================================================
print(f"\n{'='*80}")
print(f"Phase 4: Alternative cipher modes for first 53 runes")
print(f"{'='*80}")

# Maybe the cipher isn't SUB but Beaufort or ADD
# Beaufort: plain = (key - cipher) % 29
# ADD: plain = (cipher + key) % 29

# For Beaufort: key[i] = (plain[i] + cipher[i]) % 29
# For ADD: key[i] = (plain[i] - cipher[i]) % 29

# Use the SOLUTION.md plaintext
plain_53 = text_to_gp("BEING OF ALL I WILL ASC THE OATH IS SWORN TO THE ONE WITHIN THE ABOUE THE WAY")
if len(plain_53) == 53:
    print(f"\n  Candidate plaintext: {len(plain_53)} runes")
    
    # SUB key: key = (cipher - plain) % 29
    key_sub = [(cipher[i] - plain_53[i]) % MOD for i in range(53)]
    # Beaufort key: key = (plain + cipher) % 29
    key_beau = [(plain_53[i] + cipher[i]) % MOD for i in range(53)]
    # ADD key: key = (plain - cipher) % 29
    key_add = [(plain_53[i] - cipher[i]) % MOD for i in range(53)]
    
    print(f"\n  SUB key: {key_sub}")
    print(f"  Beaufort key: {key_beau}")
    print(f"  ADD key: {key_add}")
    
    # Check LFSR for each key variant
    for mode, key_variant in [("SUB", key_sub), ("Beaufort", key_beau), ("ADD", key_add)]:
        for deg in range(1, 26):
            result = lfsr_check(key_variant, deg)
            if result:
                coeffs, n_ok, n_total = result
                if n_ok == n_total:
                    print(f"\n  {mode} key fits LFSR degree {deg} PERFECTLY!")
                    print(f"    Coeffs: {coeffs}")
                    # Extend and decrypt
                    ext_key = list(key_variant)
                    for i in range(53, N):
                        val = sum(coeffs[d] * ext_key[i-d-1] for d in range(deg)) % MOD
                        ext_key.append(val)
                    
                    if mode == "SUB":
                        dec = [(cipher[i] - ext_key[i]) % MOD for i in range(N)]
                    elif mode == "Beaufort":
                        dec = [(ext_key[i] - cipher[i]) % MOD for i in range(N)]
                    else:
                        dec = [(cipher[i] + ext_key[i]) % MOD for i in range(N)]
                    
                    n_match = 0
                    for wi, (start, wrunes) in enumerate(words):
                        if start < 53: continue
                        vals = dec[start:start+len(wrunes)]
                        txt = ''.join(LAT[v] for v in vals).upper()
                        if txt in WORDLIST or txt in SMALL_WORDS: n_match += 1
                    
                    if n_match >= 3:
                        text_full = ''.join(LAT[v] for v in dec)
                        print(f"    Word matches (pos 53+): {n_match}")
                        print(f"    Full text: {text_full[:300]}")

# Also try with ABOFE variant
plain_53b = text_to_gp("BEING OF ALL I WILL ASC THE OATH IS SWORN TO THE ONE WITHIN THE ABOFE THE WAY")
if len(plain_53b) == 53:
    key_sub_b = [(cipher[i] - plain_53b[i]) % MOD for i in range(53)]
    print(f"\n  ABOFE variant SUB key: {key_sub_b}")
    diff_positions = [i for i in range(53) if key_sub_b[i] != key_sub[i]]
    print(f"  Differs from ABOUE at positions: {diff_positions}")
    
    for mode, key_variant in [("SUB-ABOFE", key_sub_b)]:
        for deg in range(1, 26):
            result = lfsr_check(key_variant, deg)
            if result:
                coeffs, n_ok, n_total = result
                if n_ok == n_total:
                    print(f"\n  {mode} key fits LFSR degree {deg} PERFECTLY!")
                    ext_key = list(key_variant)
                    for i in range(53, N):
                        val = sum(coeffs[d] * ext_key[i-d-1] for d in range(deg)) % MOD
                        ext_key.append(val)
                    dec = [(cipher[i] - ext_key[i]) % MOD for i in range(N)]
                    n_match = 0
                    for wi, (start, wrunes) in enumerate(words):
                        if start < 53: continue
                        vals = dec[start:start+len(wrunes)]
                        txt = ''.join(LAT[v] for v in vals).upper()
                        if txt in WORDLIST or txt in SMALL_WORDS: n_match += 1
                    if n_match >= 2:
                        print(f"    Word matches (pos 53+): {n_match}")

# =======================================================================
# Phase 5: Try various other first-53 candidates and check LFSR
# =======================================================================
print(f"\n{'='*80}")
print(f"Phase 5: Alternative plaintext candidates for first 53 runes")  
print(f"{'='*80}")

# What if the first 53 aren't "BEING OF ALL..."?
# Let's check IoC again more carefully
print("\n  IoC analysis revisited:")
for kl in [1, 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 130, 260]:
    if kl > N: break
    cols = [[] for _ in range(kl)]
    for i in range(N): cols[i%kl].append(cipher[i])
    iocs = []
    for col in cols:
        if len(col) < 2: continue
        freq = Counter(col)
        ioc = sum(c*(c-1) for c in freq.values()) / (len(col)*(len(col)-1)) * MOD
        iocs.append(ioc)
    avg_ioc = sum(iocs)/len(iocs) if iocs else 0
    min_vals = min(len(col) for col in cols)
    max_vals = max(len(col) for col in cols)
    print(f"  kl={kl:3d}: IoC*29={avg_ioc:.3f} (vals/col: {min_vals}-{max_vals})")

print(f"\n=== DONE ===")
