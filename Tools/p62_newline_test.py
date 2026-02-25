"""
P62 — Find exact newline positions and test key drift theory.
Theory: key starts at offset 3, newlines absorb key positions → drift to offset 0 by pos 74.
"""
import os
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

with open('LiberPrimus/pages/page_62/runes.txt','r',encoding='utf-8') as f:
    raw = f.read()

# Parse character by character with position tracking
chars = []
rune_idx = 0
newline_positions = []  # Rune index BEFORE each newline
sep_positions = []  # Rune index BEFORE each separator

for c in raw:
    if c in GP:
        chars.append(('R', GP[c], rune_idx))
        rune_idx += 1
    elif c == '\u2022' or c == '•':
        chars.append(('S', -1, rune_idx))
        sep_positions.append(rune_idx)
    elif c == '\n':
        chars.append(('N', -3, rune_idx))
        newline_positions.append(rune_idx)

cipher = [v for t,v,_ in chars if t == 'R']
N = len(cipher)

print(f"P62: {N} runes, {len(sep_positions)} separators, {len(newline_positions)} newlines")
print(f"Newline positions (after rune #): {newline_positions}")
print(f"Separator positions (after rune #): {sep_positions[:30]}")

div_gp = eng_to_gp("DIVINITY")
kl = len(div_gp)
print(f"DIVINITY: {div_gp}")

# Show the raw text structure with line boundaries
print("\n=== RAW TEXT STRUCTURE ===")
line_start = 0
for nl in newline_positions + [N]:
    runes_in_line = [v for t,v,idx in chars if t == 'R' and line_start <= idx < nl]
    seps_in_line = sum(1 for pos in sep_positions if line_start <= pos < nl)
    print(f"  Runes {line_start:3d}-{nl-1:3d}: {len(runes_in_line)} runes, {seps_in_line} separators")
    line_start = nl

# ===== TEST: Newlines advance key, initial offset=3 =====
print("\n" + "="*80)
print("TEST THEORY: start at offset 3, newlines advance key by 1")
print("="*80)

for init_off in range(8):
    key_idx = init_off
    dec = []
    for t, v, idx in chars:
        if t == 'R':
            k = div_gp[key_idx % kl]
            p = (v - k) % MOD
            dec.append(p)
            key_idx += 1
        elif t == 'N':  # Newline advances key
            key_idx += 1
    text = gp_to_lat(dec)
    
    # Score by English word matches
    score = 0
    for w in ['WISDOM','YOU','ARE','BEING','UNTO','YOURSELF','LAW','EACH','INTELLIGENCE','HOLY','ALL','THAT','LIVES','INSTRUCTION','COMMAND','OWN','SELF','FOR','THE','AND','SACRED','WITHIN']:
        score += text.count(w) * len(w)
    
    if score >= 15:
        print(f"  offset={init_off}: score={score:3d} {text[:140]}")

# ===== TEST: Each separator advances key by 1 at specific positions =====
print("\n" + "="*80)
print("TEST: Separators advance key by varying amounts")
print("="*80)

# What if only SOME separators advance the key?
# The key needs to drift by exactly 3 between position 0 and position 74
# (start at offset 3, end at offset 0)
# So 3 "extra advances" needed in the first 74 runes

# Newlines before position 74: 
nls_before_74 = [p for p in newline_positions if p < 74]
print(f"Newlines before pos 74: {nls_before_74}")

seps_before_74 = [p for p in sep_positions if p < 74]
print(f"Separators before pos 74: {seps_before_74}")

# If ONLY newlines advance: we need exactly 3 newlines before pos 74
print(f"Newlines before 74: {len(nls_before_74)} → drift = {len(nls_before_74)}")
# After pos 74: remaining newlines 
nls_after_74 = [p for p in newline_positions if p >= 74]
print(f"Newlines after 74: {len(nls_after_74)} → extra drift = {len(nls_after_74)}")

# ===== BRUTE FORCE: try subsets of {seps ∪ newlines} that give exactly 3 extra advances =====
print("\n" + "="*80)
print("TEST: optimal extra advances per character type")
print("="*80)

# For each possible "extra advance per separator" and "extra advance per newline",
# find the best decryption
for sep_adv in range(4):
    for nl_adv in range(4):
        for init_off in range(8):
            key_idx = init_off
            dec = []
            for t, v, idx in chars:
                if t == 'R':
                    k = div_gp[key_idx % kl]
                    p = (v - k) % MOD
                    dec.append(p)
                    key_idx += 1
                elif t == 'S':
                    key_idx += sep_adv
                elif t == 'N':
                    key_idx += nl_adv
            text = gp_to_lat(dec)
            
            score = 0
            for w in ['WISDOM','YOU','ARE','BEING','UNTO','YOURSELF','LAW','EACH',
                       'INTELLIGENCE','HOLY','ALL','THAT','LIVES','INSTRUCTION','COMMAND',
                       'OWN','SELF','FOR','THE','AND','SACRED','WITHIN','IS']:
                score += text.count(w) * len(w)
            
            if score >= 40:
                print(f"  sep_adv={sep_adv} nl_adv={nl_adv} off={init_off}: score={score:3d} {text[:140]}")

# ===== POSITION-BY-POSITION: find effective key index =====
print("\n" + "="*80)
print("POSITION-BY-POSITION KEY INDEX RECOVERY")
print("="*80)

# Known plaintext (trying to match)
# We know end positions are correct. Let's build the EXACT expected plaintext.
# From offset=0 pos 74 on: ALL THAT LIVES IS HOLY ...
# If start shifts by 3: positions 0-N should decode to known text

# Let me try matching position by position with the expected text
# assuming "WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF 
# EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY AN INSTRUCTION COMMAND 
# YOUR OWN SELF"

# But wait, this is 123 GP values and we have 121 runes.  
# If 3 newlines (or 2 newlines) steal key positions, the plaintext must be shorter
# by the same amount... NO! The cipher has 121 runes = 121 plaintext values.
# The key just advances faster due to newlines.

# So plaintext IS 121 GP values, and the key advances 121 + (number of extra advances) times.

# Let me determine the expected plaintext that's exactly 121 GP values long.

# First try: position-by-position with known crib at end + guessed text at start
# Known at positions 74-90: ALL THAT LIVES IS HOLY (17 GP values)
crib_start = 74
crib = eng_to_gp("ALL THAT LIVES IS HOLY")

# For these crib positions with key_idx = i + init_offset + accumulated_extras,
# we need key_idx % 8 to match DIVINITY alignment.
# We know offset=0 works: key_idx = 74 → 74 % 8 = 2 = DIVINITY[2]

# So with newlines advancing key: total_key_advances_at_pos_74 = 74 + nl_count_before_74
# Must have (74 + nl_count_before_74 + init_off) % 8 = 74 % 8 = 2
# → (nl_count_before_74 + init_off) % 8 = 0
# → init_off = -nl_count_before_74 % 8

print(f"\nNewlines before pos 74: {nls_before_74} count={len(nls_before_74)}")
for nl_adv in range(1, 4):
    total_extra = len(nls_before_74) * nl_adv
    init_off = (-total_extra) % kl
    print(f"  nl_adv={nl_adv}: total_extra={total_extra}, init_off={init_off}")
    
    # Decrypt with this configuration
    key_idx = init_off
    dec = []
    for t, v, idx in chars:
        if t == 'R':
            k = div_gp[key_idx % kl]
            p = (v - k) % MOD
            dec.append(p)
            key_idx += 1
        elif t == 'N':
            key_idx += nl_adv
    text = gp_to_lat(dec)
    
    score = 0
    for w in ['WISDOM','YOU','ARE','BEING','UNTO','YOURSELF','LAW','EACH',
               'INTELLIGENCE','HOLY','ALL','THAT','LIVES','INSTRUCTION','COMMAND',
               'OWN','SELF','FOR','THE','AND','SACRED','WITHIN','IS']:
        score += text.count(w) * len(w)
    
    print(f"    score={score:3d} text={text[:140]}")
    
    # Also verify crib at position 74
    crib_check = [dec[74+j] for j in range(len(crib))]
    crib_match = sum(1 for j in range(len(crib)) if crib_check[j] == crib[j])
    print(f"    Crib match at 74: {crib_match}/{len(crib)}")

# ===== ALSO try separators + newlines combinations =====
print("\n" + "="*80)
print("COMBINED SEPARATOR + NEWLINE EFFECTS")
print("="*80)

# For each configuration, verify the crib at position 74
for sep_adv in range(3):
    for nl_adv in range(4):
        if sep_adv == 0 and nl_adv == 0: continue
        
        # Calculate total extra advances before position 74
        nl_extra = len(nls_before_74) * nl_adv
        sep_extra = len(seps_before_74) * sep_adv
        total_extra = nl_extra + sep_extra
        
        # Need init_off such that (74 + total_extra + init_off) % 8 gives correct alignment
        # Crib works when effective_key_idx % 8 = 74 % 8 = 2 at position 74
        init_off = (2 - (74 + total_extra) % kl) % kl
        
        key_idx = init_off
        dec = []
        for t, v, idx in chars:
            if t == 'R':
                k = div_gp[key_idx % kl]
                p = (v - k) % MOD
                dec.append(p)
                key_idx += 1
            elif t == 'S':
                key_idx += sep_adv
            elif t == 'N':
                key_idx += nl_adv
        text = gp_to_lat(dec)
        
        # Score
        score = 0
        for w in ['WISDOM','YOU','ARE','BEING','UNTO','YOURSELF','LAW','EACH',
                   'INTELLIGENCE','HOLY','ALL','THAT','LIVES','INSTRUCTION','COMMAND',
                   'OWN','SELF','FOR','THE','AND','SACRED','WITHIN','IS']:
            score += text.count(w) * len(w)
        
        # Verify crib
        crib_check = [dec[74+j] for j in range(min(len(crib), N-74))]
        crib_match = sum(1 for j in range(len(crib_check)) if crib_check[j] == crib[j])
        
        if score >= 30 or crib_match == len(crib):
            print(f"  s={sep_adv} n={nl_adv} off={init_off}: score={score:3d} crib={crib_match}/{len(crib)} {text[:140]}")

print("\n=== DONE ===")
