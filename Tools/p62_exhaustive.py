"""
P62 EXHAUSTIVE — find exact separator handling + DIVINITY alignment
"""
import os
from collections import Counter
from itertools import combinations

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
MOD = 29
os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
          'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
          'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}
DIGRAPHS = {'TH':2,'NG':21,'EO':12,'OE':22,'EA':28,'AE':25,'IA':27}

def eng_to_gp(text):
    result = []
    i = 0; text = text.upper()
    while i < len(text):
        if i+1 < len(text) and text[i:i+2] in DIGRAPHS:
            result.append(DIGRAPHS[text[i:i+2]])
            i += 2
        elif text[i] in ENG2GP:
            result.append(ENG2GP[text[i]])
            i += 1
        else:
            i += 1
    return result

def gp_to_lat(vals):
    return ''.join(LAT[v] for v in vals)

# Load P62 raw text
with open('LiberPrimus/pages/page_62/runes.txt','r',encoding='utf-8') as f:
    raw = f.read()

# Parse into character stream
chars = []
for c in raw:
    if c in GP:
        chars.append(('R', GP[c]))
    elif c == '\u2022' or c == '•':
        chars.append(('S', -1))
    elif c == '\n':
        chars.append(('N', -3))

cipher = [v for t,v in chars if t == 'R']
N = len(cipher)

# DIVINITY key
div_gp = eng_to_gp("DIVINITY")  # [23, 10, 1, 10, 9, 10, 16, 26]
kl = len(div_gp)
print(f"DIVINITY: {div_gp}")
print(f"Cipher: {N} runes")

# English word list for scoring
ENGLISH_WORDS = [
    'WISDOM','YOU','ARE','BEING','UNTO','YOURSELF','LAW',
    'EACH','INTELLIGENCE','HOLY','FOR','ALL','THAT','LIVES',
    'INSTRUCTION','COMMAND','YOUR','OWN','SELF','THE','AND',
    'WITH','WITHIN','NOT','BUT','THIS','WHICH','HAVE','FROM',
    'SACRED','DIVINITY','TRUTH','PRIMES','PILGRIM','END'
]

def score_text(text):
    s = 0
    for w in ENGLISH_WORDS:
        c = text.count(w)
        s += c * len(w)  # Weight by word length
    return s

# ===== EXHAUSTIVE: all skip combos + all offsets + all modes =====
print("\n" + "="*80)
print("EXHAUSTIVE SEPARATOR + OFFSET + MODE SEARCH")
print("="*80)

# Character types that might consume key positions: S (bullet), N (newline)
skip_configs = [
    ('none', ''),
    ('bullets', 'S'),
    ('newlines', 'N'),
    ('both', 'SN'),
]

best_results = []

for skip_name, skip_types in skip_configs:
    for start_off in range(kl):
        for mode in ['SUB', 'ADD', 'BEAU']:
            key_idx = start_off
            dec = []
            for t, v in chars:
                if t == 'R':
                    k = div_gp[key_idx % kl]
                    if mode == 'SUB': p = (v - k) % MOD
                    elif mode == 'ADD': p = (v + k) % MOD
                    elif mode == 'BEAU': p = (k - v) % MOD
                    dec.append(p)
                    key_idx += 1
                elif t in skip_types:
                    key_idx += 1
            
            text = gp_to_lat(dec)
            sc = score_text(text)
            if sc >= 20:
                best_results.append((sc, skip_name, start_off, mode, text))

best_results.sort(reverse=True)
print("\nTop results:")
for sc, skip_name, off, mode, text in best_results[:20]:
    print(f"  score={sc:3d} skip={skip_name:8s} off={off} {mode:4s}: {text[:120]}")

# ===== POSITION-BY-POSITION CRIB DRAG =====
print("\n" + "="*80)
print("CRIB DRAG — Find which DIVINITY position decrypts each rune correctly")
print("="*80)

# For each mode, for each rune position, find which of the 8 DIVINITY 
# key values produces a "plausible" English GP value
# English-common GP values: 0(F), 2(TH), 3(O), 4(R), 5(C), 8(H), 9(N), 
# 10(I), 15(S), 16(T), 18(E), 20(L), 24(A)
COMMON = {0,2,3,4,5,8,9,10,15,16,18,20,24}

for mode in ['SUB']:
    print(f"\n--- {mode} ---")
    # For each position, which key indices produce common values?
    for i in range(N):
        matches = []
        for ki in range(kl):
            k = div_gp[ki]
            if mode == 'SUB': p = (cipher[i] - k) % MOD
            elif mode == 'ADD': p = (cipher[i] + k) % MOD
            elif mode == 'BEAU': p = (k - cipher[i]) % MOD
            if p in COMMON:
                matches.append((ki, p, LAT[p]))
        if len(matches) == 1:
            ki, p, lat = matches[0]
            # Only one DIVINITY key value produces a common GP letter
            pass  # Will analyze pattern below

    # Build the effective key index at each position
    # Try to find a consistent pattern
    # For the known-text approach: if we know the plaintext, we can recover
    # the EXACT key index at each position
    
    # Use the end of the text where we KNOW the plaintext
    # offset=0: positions 74-120 = "ALLTHATLIUESISHOLYANINSTRUCTIANCOMMANDYOUROWNSELG"
    # But some chars are wrong (SELG not SELF, INSTRUCTIAN not INSTRUCTION)
    
    # Let's try: the TEXT is right but there are encoding ambiguities
    # INSTRUCTIAN → the IA is GP 27, but INSTRUCTION → I(10) O(3) N(9) 
    # In the decrypted stream, we got GP 27 (IA). That means:
    # cipher[I] - div_gp[ki] = 27 (mod 29) for that position
    
    # Actually, let me just look at what key index would make EACH position
    # produce the expected plaintext
    
    # Expected plaintext (end segment, offset=0 SUB starting from the known "ALL"):
    # Working backwards from cipher position 120:
    # Let's assume SELF not SELG at the end: S(15) E(18) L(20) F(0)
    # cipher[117..120] - key = [15, 18, 20, 0] mod 29
    # cipher[117..120] = ?
    print("\nCipher values at end:")
    for i in range(N-20, N):
        for ki in range(kl):
            k = div_gp[ki]
            p = (cipher[i] - k) % MOD
            print(f"  ci[{i:3d}]={cipher[i]:2d} ki={ki}({LAT[div_gp[ki]]:3s}) → {LAT[p]:3s}({p:2d})", end="")
        print()

# ===== SMARTER: assume we know plaintext, find key shift pattern =====
print("\n" + "="*80)
print("ASSUME PLAINTEXT + FIND KEY PATTERN")
print("="*80)

# The plaintext from offset=0 SUB at end is mostly correct
# Let me try to match the FULL known text to the cipher
# and find the key index at each position

# Expected plaintext (best guess)
# From fragments: "WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY AN INSTRUCTION COMMAND YOUR OWN SELF"

# But INSTRUCTION has 11 GP values and INSTRUCTIAN has 10
# And the total is 123 vs 121 needed

# What if we use INSTRUCTIAN (with IA digraph) = 10 values?
# That gives 122 GP values. Still 1 too many.
# Also SELG vs SELF...

# Let me try a different approach: what if the text doesn't have "FOR"?
# "EACH INTELLIGENCE IS HOLY ALL THAT LIVES IS HOLY" 
# Without "FOR": 123 - 3 = 120. One short.

# What if we add a letter? Like "A WISDOM"?
# "A WISDOM YOU ARE..." adds A(24) = 1 GP. 123 + 1 = 124. Too many.

# Hmm. Let me try: what if "YOURSELF" is "YOURSELFE" (with final E)?
# No, that's 9 values instead of 8.

# Let me instead try EVERY possible known-text alignment against the cipher,
# using SUB mode, and find the total key shift (sum of separator-induced offsets)

# candidate plaintexts of length 121:
candidates = []

# Try remove words to get to 121
base = "WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY AN INSTRUCTION COMMAND YOUR OWN SELF"
base_gp = eng_to_gp(base)
print(f"Base text: {len(base_gp)} GP values")

# Try variants
variants = [
    ("base_minus_FOR", "WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY ALL THAT LIVES IS HOLY AN INSTRUCTION COMMAND YOUR OWN SELF"),
    ("base_minus_AN", "WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY INSTRUCTION COMMAND YOUR OWN SELF"),
    ("SELVE", "WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY AN INSTRUCTION COMMAND YOUR OWN SELVE"),
    ("no_A1", "WISDOM YOU ARE BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY AN INSTRUCTION COMMAND YOUR OWN SELF"),
    ("no_A2", "WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY AN INSTRUCTION COMMAND YOUR OWN SELF"),
    # What about SOME instead of AN?
    ("SOME", "WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY SOME INSTRUCTION COMMAND YOUR OWN SELF"),
    # What about extending with more text?
    ("SELF_extended", "WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY AN INSTRUCTION COMMAND YOUR OWN SELF SOME"),
    # Without final SELF → SELVE = 5 GP → 123-4+5=124
    # Hmm, try without "IS" somewhere
    ("no_IS2", "WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES HOLY AN INSTRUCTION COMMAND YOUR OWN SELF"),
]

for name, txt in variants:
    gp = eng_to_gp(txt)
    ln = len(gp)
    print(f"  {name:20s}: {ln} GP values {'*** MATCH ***' if ln == 121 else ''}")
    if ln == 121:
        # Recover key pattern
        key_recovered = [(cipher[i] - gp[i]) % MOD for i in range(121)]
        
        # Check if key follows DIVINITY with shifting
        # For each position, find which DIVINITY index it maps to
        div_indices = []
        for i in range(121):
            matched = False
            for ki in range(kl):
                if key_recovered[i] == div_gp[ki]:
                    div_indices.append(ki)
                    matched = True
                    break
            if not matched:
                div_indices.append(-1)
        
        match_count = sum(1 for di in div_indices if di >= 0)
        print(f"    DIVINITY match: {match_count}/121 ({match_count/121*100:.1f}%)")
        
        # Show the pattern
        if match_count > 50:
            print(f"    Pattern: {div_indices[:40]}")
            # Check if indices are sequential mod 8
            sequential = True
            for i in range(1, 121):
                if div_indices[i] >= 0 and div_indices[i-1] >= 0:
                    if div_indices[i] != (div_indices[i-1] + 1) % kl:
                        sequential = False
                        break
            if sequential:
                print(f"    KEY IS SEQUENTIAL! Starting at DIVINITY[{div_indices[0]}]")
            
        # Even if no exact match, check what percentage if we allow offset
        for test_off in range(kl):
            matches = sum(1 for i in range(121) if key_recovered[i] == div_gp[(i+test_off)%kl])
            if matches > 80:
                print(f"    With offset={test_off}: {matches}/121 match")

# ===== RAW CRIB AT KNOWN POSITIONS =====
print("\n" + "="*80)
print("RAW CRIB: 'ALLTHATLIUESISHOLY' at cipher end, find key")
print("="*80)

# We KNOW (from offset=0 SUB) the end is approximately "ALL THAT LIVES IS HOLY..."
# Let me try the known ending with EXACT GP values
# ALL THAT LIVES IS HOLY = A(24) L(20) L(20) TH(2) A(24) T(16) L(20) I(10) V(1) E(18) S(15) I(10) S(15) H(8) O(3) L(20) Y(26) = 17 values
crib = eng_to_gp("ALL THAT LIVES IS HOLY")
print(f"Crib length: {len(crib)} GP values")

# Try at each cipher position
for start_pos in range(N - len(crib) + 1):
    key_vals = [(cipher[start_pos + j] - crib[j]) % MOD for j in range(len(crib))]
    # Check if all key values are from DIVINITY set
    div_set = set(div_gp)
    all_div = all(k in div_set for k in key_vals)
    # Check if key values follow sequential DIVINITY pattern
    for test_off in range(kl):
        match = all(key_vals[j] == div_gp[(start_pos + j + test_off) % kl] for j in range(len(crib)))
        if match:
            print(f"  crib at pos {start_pos}, offset={test_off}: EXACT SEQUENTIAL MATCH!")
            # Now extend: try to decode the full text with this offset
            total_key_advance = (start_pos + test_off)
            dec_full = []
            for i in range(N):
                k = div_gp[(i + test_off) % kl]
                p = (cipher[i] - k) % MOD
                dec_full.append(p)
            text = gp_to_lat(dec_full)
            print(f"    Full text: {text[:120]}")

    # Also check with separator-based key advancement  
    # (key advances by 1 extra for each separator)
    
# Try a more flexible approach: 
# For each starting key index, check how much of "ALLTHATLIVESISHOLY" matches
for test_off in range(kl):
    for end_offset in range(-5, 6):  # Try placing crib at different positions from end
        start_pos = N - len(crib) + end_offset
        if start_pos < 0 or start_pos + len(crib) > N: continue
        matches = sum(1 for j in range(len(crib)) if (cipher[start_pos+j] - div_gp[(start_pos+j+test_off)%kl])%MOD == crib[j])
        if matches >= 14:  # Most of the crib matches
            dec = [(cipher[start_pos+j] - div_gp[(start_pos+j+test_off)%kl])%MOD for j in range(len(crib))]
            text = gp_to_lat(dec)
            print(f"  pos={start_pos} off={test_off}: {matches}/{len(crib)} matches → {text}")

print("\n=== DONE ===")
