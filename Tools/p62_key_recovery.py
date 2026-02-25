"""
P62 — Precise key recovery using known plaintext + separator advancement.
We know: DIVINITY key, crib matches at end (pos 74+), title is WISDOM.
Goal: Find exact key advancement rule (separators/newlines) that makes the full text work.
"""
import os
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
DIGRAPHS_ORDERED = [('TH',2),('NG',21),('EA',28),('OE',22),('EO',12),('AE',25),('IA',27)]

def eng_to_gp(text):
    result = []
    i = 0; text = text.upper()
    while i < len(text):
        found = False
        for dg, val in DIGRAPHS_ORDERED:
            if text[i:i+len(dg)] == dg:
                result.append(val)
                i += len(dg)
                found = True
                break
        if not found:
            if text[i] in ENG2GP:
                result.append(ENG2GP[text[i]])
            i += 1
    return result

def gp_to_lat(vals):
    return ''.join(LAT[v] for v in vals)

# Read the raw file to get character stream
with open('LiberPrimus/pages/page_62/runes.txt', 'r', encoding='utf-8') as f:
    raw = f.read()

# Build character stream with types
char_stream = []  # list of (type, value_or_None, rune_index_or_None)
rune_idx = 0
cipher = []
for ch in raw:
    if ch in GP:
        char_stream.append(('R', GP[ch], rune_idx))
        cipher.append(GP[ch])
        rune_idx += 1
    elif ch == '\u2022':  # bullet •
        char_stream.append(('S', None, None))
    elif ch == '\n':
        char_stream.append(('N', None, None))
    # ignore other characters

N = len(cipher)
print(f"P62: {N} runes, stream has {len(char_stream)} chars")

# Count separators and newlines before each rune position
sep_before = [0]*N  # cumulative separators before rune i
nl_before = [0]*N   # cumulative newlines before rune i
cum_sep = 0
cum_nl = 0
for item in char_stream:
    if item[0] == 'S':
        cum_sep += 1
    elif item[0] == 'N':
        cum_nl += 1
    elif item[0] == 'R':
        ri = item[2]
        sep_before[ri] = cum_sep
        nl_before[ri] = cum_nl

print(f"Separator counts before each rune position (sample):")
for i in [0, 6, 28, 50, 71, 74, 91, 120]:
    if i < N:
        print(f"  rune[{i:3d}]: {sep_before[i]:2d} seps, {nl_before[i]:2d} newlines (total extra: {sep_before[i]+nl_before[i]})")

# DIVINITY key
DIVINITY = eng_to_gp("DIVINITY")
print(f"\nDIVINITY key: {DIVINITY} = {gp_to_lat(DIVINITY)}")
KL = len(DIVINITY)

# ===== KNOWN PLAINTEXT RECOVERY =====
print("\n" + "="*80)
print("KEY RECOVERY FROM ASSUMED PLAINTEXT")
print("="*80)

# Candidate plaintexts (all match known Cicada text)
candidates = {
    "full_base": "WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY AN INSTRUCTION COMMAND YOUR OWN SELF",
    "no_FOR": "WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY ALL THAT LIVES IS HOLY AN INSTRUCTION COMMAND YOUR OWN SELF",
    "no_AN": "WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY INSTRUCTION COMMAND YOUR OWN SELF",
    "no_FOR_no_AN": "WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY ALL THAT LIVES IS HOLY INSTRUCTION COMMAND YOUR OWN SELF",
    "instructian": "WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY AN INSTRUCTIAN COMMAND YOUR OWN SELF",
    "no_FOR_instructian": "WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY ALL THAT LIVES IS HOLY AN INSTRUCTIAN COMMAND YOUR OWN SELF",
    "selg": "WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY AN INSTRUCTION COMMAND YOUR OWN SELG",
}

for name, text in candidates.items():
    pt = eng_to_gp(text)
    print(f"\n  {name}: {len(pt)} GP values (need {N})")
    if len(pt) != N:
        # Try anyway if close
        if abs(len(pt) - N) > 3:
            continue
    
    # Recover key for SUB mode: cipher = (plain + key) % 29 → key = (cipher - plain) % 29
    # Or if SUB means: plain = (cipher - key) → key = (cipher - plain)
    key_sub = [(cipher[i] - pt[i]) % MOD for i in range(min(len(pt), N))]
    key_add = [(pt[i] - cipher[i]) % MOD for i in range(min(len(pt), N))]
    key_beau = [(pt[i] + cipher[i]) % MOD for i in range(min(len(pt), N))]
    
    for mode, key_vals in [("SUB", key_sub), ("ADD", key_add), ("BEAU", key_beau)]:
        # Check how many match DIVINITY pattern (no extras)
        match_basic = sum(1 for i in range(min(len(key_vals), N)) if key_vals[i] == DIVINITY[i % KL])
        
        # Check if key_vals follow DIVINITY with separator advancement
        for sep_adv in range(4):
            for nl_adv in range(4):
                match = 0
                for i in range(min(len(key_vals), N)):
                    extra = sep_before[i] * sep_adv + nl_before[i] * nl_adv
                    expected_key = DIVINITY[(i + extra) % KL]
                    if key_vals[i] == expected_key:
                        match += 1
                
                if match > 80:  # >66% match
                    print(f"    {mode} sep_adv={sep_adv} nl_adv={nl_adv}: {match}/{min(len(key_vals),N)} DIVINITY matches")
                    # Show first mismatches
                    mismatches = []
                    for i in range(min(len(key_vals), N)):
                        extra = sep_before[i] * sep_adv + nl_before[i] * nl_adv
                        expected_key = DIVINITY[(i + extra) % KL]
                        if key_vals[i] != expected_key:
                            mismatches.append((i, key_vals[i], expected_key, LAT[key_vals[i]], LAT[expected_key]))
                    if mismatches:
                        for pos, got, exp, got_l, exp_l in mismatches[:15]:
                            extra = sep_before[pos] * sep_adv + nl_before[pos] * nl_adv
                            ki = (pos + extra) % KL
                            print(f"      mismatch at rune[{pos:3d}]: key={got_l:3s}({got:2d}) expected DIVINITY[{ki}]={exp_l:3s}({exp:2d})")

# ===== TRY WITH INITIAL OFFSET =====
print("\n" + "="*80)
print("KEY RECOVERY WITH INITIAL OFFSETS")
print("="*80)

for name, text in candidates.items():
    pt = eng_to_gp(text)
    if len(pt) != N:
        continue  # Only exact matches
    
    key_sub = [(cipher[i] - pt[i]) % MOD for i in range(N)]
    
    for init_off in range(KL):
        for sep_adv in range(4):
            for nl_adv in range(4):
                match = 0
                for i in range(N):
                    extra = sep_before[i] * sep_adv + nl_before[i] * nl_adv
                    expected_key = DIVINITY[(i + init_off + extra) % KL]
                    if key_sub[i] == expected_key:
                        match += 1
                
                if match >= 110:  # >90% match
                    pct = match * 100 / N
                    print(f"  {name} SUB init_off={init_off} sep={sep_adv} nl={nl_adv}: {match}/{N} ({pct:.1f}%)")
                    mismatches = []
                    for i in range(N):
                        extra = sep_before[i] * sep_adv + nl_before[i] * nl_adv
                        expected_key = DIVINITY[(i + init_off + extra) % KL]
                        if key_sub[i] != expected_key:
                            mismatches.append((i, key_sub[i], expected_key))
                    if len(mismatches) <= 20:
                        for pos, got, exp in mismatches:
                            extra = sep_before[pos] * sep_adv + nl_before[pos] * nl_adv
                            ki = (pos + init_off + extra) % KL
                            print(f"    mismatch rune[{pos:3d}]: got {LAT[got]}({got}) exp DIVINITY[{ki}]={LAT[exp]}({exp})")

# ===== ALSO TRY: title line uses different offset than body =====
print("\n" + "="*80)
print("SPLIT KEY: TITLE (runes 0-5) + BODY (runes 6-120)")
print("="*80)

# Maybe title has its own key offset and body starts fresh
wisdom_gp = eng_to_gp("WISDOM")
print(f"WISDOM GP: {wisdom_gp}")

# For the title, find what DIVINITY offset produces WISDOM
for off in range(KL):
    dec_title = [(cipher[i] - DIVINITY[(i + off) % KL]) % MOD for i in range(6)]
    text_title = gp_to_lat(dec_title)
    wisdom_match = sum(1 for i in range(6) if dec_title[i] == wisdom_gp[i])
    print(f"  Title offset={off}: {text_title} (WISDOM match: {wisdom_match}/6)")

# Try the body (runes 6+) with different start offsets
body_cipher = cipher[6:]
body_len = N - 6  # 115

# Known text after WISDOM:
body_texts = {
    "base": "YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY AN INSTRUCTION COMMAND YOUR OWN SELF",
    "no_FOR": "YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY ALL THAT LIVES IS HOLY AN INSTRUCTION COMMAND YOUR OWN SELF",
    "no_AN": "YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY INSTRUCTION COMMAND YOUR OWN SELF",
    "no_FOR_no_AN": "YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY ALL THAT LIVES IS HOLY INSTRUCTION COMMAND YOUR OWN SELF",
}

for bt_name, bt_text in body_texts.items():
    bt_gp = eng_to_gp(bt_text)
    if len(bt_gp) != body_len:
        print(f"  Body '{bt_name}': {len(bt_gp)} GP (need {body_len}), skipping exact check")
        continue
    
    body_key = [(body_cipher[i] - bt_gp[i]) % MOD for i in range(body_len)]
    
    for body_off in range(KL):
        for sep_adv in range(4):
            for nl_adv in range(4):
                match = 0
                for i in range(body_len):
                    ri = i + 6  # rune index in full cipher
                    extra = sep_before[ri] * sep_adv + nl_before[ri] * nl_adv
                    expected = DIVINITY[(i + body_off + extra) % KL]
                    if body_key[i] == expected:
                        match += 1
                if match > body_len * 0.85:
                    print(f"  Body '{bt_name}' off={body_off} sep={sep_adv} nl={nl_adv}: {match}/{body_len} ({match*100/body_len:.1f}%)")

# ===== APPROACH 2: Derive key directly, look for ANY pattern =====
print("\n" + "="*80)
print("RAW KEY ANALYSIS (no DIVINITY assumption)")
print("="*80)

# Use known crib positions to anchor, then look at full key pattern
# We know the text is approximately the known Cicada quote
# Let's use "no_FOR" variant first
for variant_name, full_text in candidates.items():
    pt = eng_to_gp(full_text)
    if len(pt) != N:
        continue
    
    key_stream = [(cipher[i] - pt[i]) % MOD for i in range(N)]
    key_text = gp_to_lat(key_stream)
    print(f"\n  Variant '{variant_name}':")
    print(f"  Key stream ({N} values): {key_stream}")
    print(f"  Key as text: {key_text}")
    
    # Check if it's a repeating pattern
    for period in range(1, 20):
        matches = 0
        for i in range(N):
            if key_stream[i] == key_stream[i % period]:
                matches += 1
        if matches > N * 0.9:
            print(f"  Period {period}: {matches}/{N} matches")
    
    # Check if it matches DIVINITY at any offset
    for off in range(KL):
        m = sum(1 for i in range(N) if key_stream[i] == DIVINITY[(i + off) % KL])
        if m > 50:
            print(f"  DIVINITY offset={off}: {m}/{N} matches")

print("\n=== DONE ===")
