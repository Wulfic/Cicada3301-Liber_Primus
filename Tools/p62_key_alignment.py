"""
P62 KEY ALIGNMENT — DIVINITY key with shifting offset
The text is known: WISDOM + AN INSTRUCTION sections
The key alignment shifts because separators consume key positions.
Let's reverse-engineer the exact alignment.
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

# Load P62 raw text with separators
with open('LiberPrimus/pages/page_62/runes.txt','r',encoding='utf-8') as f:
    raw = f.read()

# Show all characters
print("=== RAW TEXT ANALYSIS ===")
all_chars = []
for c in raw:
    if c in GP:
        all_chars.append(('R', GP[c], c))  # Rune
    elif c == '\u2022' or c == '•':
        all_chars.append(('S', -1, c))  # Separator (bullet)
    elif c == '-':
        all_chars.append(('D', -2, c))  # Dash
    elif c == '\n':
        all_chars.append(('N', -3, c))  # Newline
    elif c == '.':
        all_chars.append(('P', -4, c))  # Period
    else:
        all_chars.append(('?', ord(c), c))

print(f"Total characters: {len(all_chars)}")
char_types = Counter(t for t,_,_ in all_chars)
print(f"Character types: {dict(char_types)}")

# Show separator positions
sep_positions = []
rune_idx = 0
for i, (t, v, c) in enumerate(all_chars):
    if t == 'S' or t == 'D' or t == 'P':
        sep_positions.append((rune_idx, t))
    elif t == 'R':
        rune_idx += 1

print(f"\nSeparator positions (by rune index before them):")
for pos, typ in sep_positions:
    print(f"  After rune {pos}: type={typ}")

# Extract cipher runes only
cipher = [v for t,v,c in all_chars if t == 'R']
N = len(cipher)
print(f"\nCipher length: {N}")

# DIVINITY key
div_gp = eng_to_gp("DIVINITY")
print(f"DIVINITY: {div_gp} ({gp_to_lat(div_gp)})")
kl = len(div_gp)

# ===== KNOWN PLAINTEXT ALIGNMENT =====
print("\n" + "="*80)
print("KNOWN PLAINTEXT ALIGNMENT")
print("="*80)

# The known text from Cicada - Page 62 is a "WISDOM" section
known_candidates = [
    "WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY AN INSTRUCTION COMMAND YOUR OWN SELF",
    "WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY",
    "AN INSTRUCTION COMMAND YOUR OWN SELF",
    # Without spaces
]

for cand in known_candidates:
    gp = eng_to_gp(cand)
    if len(gp) != N:
        print(f"\n'{cand[:50]}...' → {len(gp)} GP values (need {N})")
    else:
        print(f"\n'{cand[:50]}...' → {len(gp)} GP values = EXACT MATCH!")

# Let's try the most likely: the full text
# First, figure out what the text should be
# From the offset analysis:
# offset=3: "WISDOM YOU ARE A BEING UNTO YOURSELF" (positions ~0-35)
# offset=2: "YOU ARE A LAW UNTO YOURSELF" (positions ~36-62)
# offset=1: "EACH INTELLIGENCE IS HOLY" (positions ~63-90)
# offset=0: "ALL THAT LIVES IS HOLY AN INSTRUCTION COMMAND YOUR OWN SELF" (positions ~91-120)

# Build the full expected plaintext
full_text = "WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY AN INSTRUCTION COMMAND YOUR OWN SELF"
full_gp = eng_to_gp(full_text)
print(f"\nFull expected: {len(full_gp)} GP values (need {N})")
print(f"Full text LAT: {gp_to_lat(full_gp)}")

# Try with different texts to match length 121
texts_to_try = [
    "WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY AN INSTRUCTION COMMAND YOUR OWN SELF",
    "A WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY AN INSTRUCTION COMMAND YOUR OWN SELF",
    "WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY AN INSTRUCTION COMMAND YOUR OWN SELF SOME",
]

for txt in texts_to_try:
    gp = eng_to_gp(txt)
    print(f"  '{txt[:30]}...' → {len(gp)} GP values")

# ===== POSITION-BY-POSITION KEY RECOVERY =====
print("\n" + "="*80)
print("POSITION-BY-POSITION KEY RECOVERY")
print("="*80)

# For the best candidate, recover key at each position
candidate = "WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY AN INSTRUCTION COMMAND YOUR OWN SELF"
cand_gp = eng_to_gp(candidate)

if len(cand_gp) > N:
    print(f"Candidate too long ({len(cand_gp)} > {N}), trying truncated versions")
    # Try different truncation points
    words = candidate.split()
    for end in range(len(words), 5, -1):
        sub = ' '.join(words[:end])
        sub_gp = eng_to_gp(sub)
        if len(sub_gp) <= N:
            print(f"  '{sub}' → {len(sub_gp)} GP values")
            if len(sub_gp) == N:
                print(f"  *** EXACT MATCH! ***")
                cand_gp = sub_gp
                break
    else:
        cand_gp = cand_gp[:N]  # Force truncate

if len(cand_gp) < N:
    print(f"Candidate too short ({len(cand_gp)} < {N})")
    # Need to find the right plaintext
else:
    # Recover key for each position (SUB mode: p = (c - k) % 29 → k = (c - p) % 29)
    key_recovered = [(cipher[i] - cand_gp[i]) % MOD for i in range(len(cand_gp))]
    print(f"Recovered key: {key_recovered}")
    print(f"Recovered key LAT: {gp_to_lat(key_recovered)}")
    
    # Check if key follows DIVINITY pattern
    for i in range(len(key_recovered)):
        expected_div_idx = i % kl
        expected_key = div_gp[expected_div_idx]
        actual_key = key_recovered[i]
        match = "✓" if actual_key == expected_key else "✗"
        if match == "✗":
            print(f"  pos {i:3d}: key={actual_key:2d} ({LAT[actual_key]:3s}) expected={expected_key:2d} ({LAT[expected_key]:3s}) {match}")

# ===== TRY KEY WITH SEPARATOR OFFSET =====
print("\n" + "="*80)
print("KEY WITH SEPARATOR OFFSET HYPOTHESIS")
print("="*80)

# Hypothesis: the key position increments for EVERY character in original text,
# including separators. So key_idx = rune_position + number_of_separators_before_this_rune

# Rebuild with character-level tracking
key_idx = 0
dec_with_sep = []
rune_pos = 0

for t, v, c in all_chars:
    if t == 'R':
        k = div_gp[key_idx % kl]
        p = (v - k) % MOD
        dec_with_sep.append(p)
        rune_pos += 1
        key_idx += 1
    elif t in ('S', 'D', 'P'):
        key_idx += 1  # Separator consumes a key position
    elif t == 'N':
        pass  # Newlines don't consume key positions

text = gp_to_lat(dec_with_sep)
print(f"Sep-offset SUB (newlines skip): {text}")

# Try newlines also consuming key positions
key_idx = 0
dec_with_sep2 = []
for t, v, c in all_chars:
    if t == 'R':
        k = div_gp[key_idx % kl]
        p = (v - k) % MOD
        dec_with_sep2.append(p)
    key_idx += 1  # ALL characters consume key positions

text2 = gp_to_lat(dec_with_sep2)
print(f"Sep-offset SUB (all chars): {text2}")

# Try with ADD mode
key_idx = 0
dec_with_sep3 = []
for t, v, c in all_chars:
    if t == 'R':
        k = div_gp[key_idx % kl]
        p = (v + k) % MOD
        dec_with_sep3.append(p)
        key_idx += 1
    elif t in ('S', 'D', 'P'):
        key_idx += 1

text3 = gp_to_lat(dec_with_sep3)
print(f"Sep-offset ADD (newlines skip): {text3}")

# Try BEAU mode  
key_idx = 0
dec_with_sep4 = []
for t, v, c in all_chars:
    if t == 'R':
        k = div_gp[key_idx % kl]
        p = (k - v) % MOD
        dec_with_sep4.append(p)
        key_idx += 1
    elif t in ('S', 'D', 'P'):
        key_idx += 1

text4 = gp_to_lat(dec_with_sep4)
print(f"Sep-offset BEAU (newlines skip): {text4}")

# ===== TRY DIFFERENT SEPARATOR HANDLING =====
print("\n" + "="*80)
print("DIFFERENT SEPARATOR HANDLING VARIANTS")
print("="*80)

# What types of separators exist?
for skip_type in ['S', 'SD', 'SDP', 'SDPN', 'N', 'SN']:
    for mode in ['SUB', 'ADD', 'BEAU']:
        key_idx = 0
        dec = []
        for t, v, c in all_chars:
            if t == 'R':
                k = div_gp[key_idx % kl]
                if mode == 'SUB': p = (v - k) % MOD
                elif mode == 'ADD': p = (v + k) % MOD
                elif mode == 'BEAU': p = (k - v) % MOD
                dec.append(p)
                key_idx += 1
            elif t in skip_type:
                key_idx += 1  # This separator type consumes a key position
        
        text = gp_to_lat(dec)
        # Count English word hits
        hits = 0
        for w in ['WISDOM','THE','AND','THAT','WITH','FOR','ALL','ARE','YOU','NOT','BUT','THIS','BEING','WITHIN','HOLY','LIVES','EACH','INTELLIGENCE','UNTO','YOURSELF','LAW','INSTRUCTION','COMMAND','OWN','SELF']:
            hits += text.count(w)
        
        if hits >= 6:
            print(f"  skip={skip_type:5s} {mode:4s}: [{hits:2d} hits] {text[:120]}")

# ===== BRUTE FORCE: find which chars to skip =====
print("\n" + "="*80)
print("DIRECT POSITION-BY-POSITION DIVINITY ALIGNMENT")
print("="*80)

# For each cipher position, try all 8 DIVINITY values
# Find the one that produces a plausible plaintext character
# This reveals the effective key offset at each position

for mode in ['SUB']:
    print(f"\n--- {mode} ---")
    for start_off in range(8):
        dec = []
        for i in range(N):
            k = div_gp[(i + start_off) % kl]
            if mode == 'SUB': p = (cipher[i] - k) % MOD
            elif mode == 'ADD': p = (cipher[i] + k) % MOD
            elif mode == 'BEAU': p = (k - cipher[i]) % MOD
            dec.append(p)
        
        text = gp_to_lat(dec)
        # Find all English word occurrences with positions
        for w in ['WISDOM','BEING','UNTO','YOURSELF','INTELLIGENCE','HOLY','LIVES','INSTRUCTION','COMMAND','LAW']:
            idx = text.find(w)
            while idx >= 0:
                print(f"  off={start_off}: '{w}' found at LAT pos {idx}")
                idx = text.find(w, idx+1)

print("\n=== DONE ===")
