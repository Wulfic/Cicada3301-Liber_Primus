"""
P03+P04 combined brute force with DIVINITY.
Use known P03 optimal mask, brute-force only P04 F positions.
Also test ALL modes (SUB/ADD/BEAU) and refine.
"""
import os
from collections import Counter

RUNE_TO_INDEX = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,'\u16C7':12,'\u16C8':13,'\u16C9':14,
    '\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,'\u16D7':19,'\u16DA':20,'\u16DD':21,
    '\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,'\u16A3':26,'\u16E1':27,'\u16E0':28
}
GP = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
      'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
BASE = r"c:\Users\tyler\Repos\Cicada3301\LiberPrimus\pages"

def load_page(pn):
    path = os.path.join(BASE, f"page_{pn:02d}", "runes.txt")
    if not os.path.exists(path): return []
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    rune_text = ''.join(line for line in lines if not (line.strip() and line.strip()[0].isascii() and line.strip()[0].isalpha()))
    return [RUNE_TO_INDEX[c] for c in rune_text if c in RUNE_TO_INDEX]

def keyword_to_gp(word):
    result = []; i = 0; word = word.upper()
    while i < len(word):
        if i+1 < len(word):
            di = word[i:i+2]
            dmap = {'TH':2,'EO':12,'NG':21,'OE':22,'AE':25,'IA':27,'IO':27,'EA':28}
            if di in dmap: result.append(dmap[di]); i += 2; continue
        smap = {'F':0,'U':1,'V':1,'O':3,'R':4,'C':5,'K':5,'G':6,'W':7,'H':8,'N':9,
                'I':10,'J':11,'P':13,'X':14,'S':15,'Z':15,'T':16,'B':17,'E':18,'M':19,
                'L':20,'D':23,'A':24,'Y':26}
        if word[i] in smap: result.append(smap[word[i]])
        i += 1
    return result

def ioc29(vals):
    if len(vals) < 2: return 0
    ct = Counter(vals); n = len(vals)
    return 29 * sum(c*(c-1) for c in ct.values()) / (n*(n-1))

def text(vals): return ''.join(GP[v] for v in vals)

def decrypt_fskip_set(cipher, key, mode, skip_positions):
    """skip_positions: set of indices where the cipher F is literal"""
    result = []; ki = 0; kl = len(key)
    for i, c in enumerate(cipher):
        if i in skip_positions:
            result.append(0); continue
        k = key[ki % kl]
        if mode == 'SUB': p = (c - k) % 29
        elif mode == 'ADD': p = (c + k) % 29
        elif mode == 'BEAU': p = (k - c) % 29
        result.append(p)
        ki += 1
    return result

def score_text(vals):
    t = text(vals).upper()
    score = 0
    for w in ['THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','HER','WAS',
              'ONE','OUR','OUT','HIS','HAS','ITS','WHO','OWN','SAY','SHE','LET']:
        score += t.count(w) * 3
    for w in ['OF','TO','IN','IS','IT','AN','OR','IF','NO','SO','BY','AS','AT','WE','BE']:
        score += t.count(w) * 2
    for w in ['THAT','THIS','WITH','FROM','THEY','HAVE','BEEN','EACH','WILL',
              'YOUR','WHAT','WHEN','THEM','SOME','INTO','THAN','ONLY','SELF',
              'FIND','MAKE','JUST','KNOW']:
        score += t.count(w) * 4
    for w in ['WHICH','THEIR','ABOUT','BEING','THERE','THOSE','THING','WOULD',
              'SHALL','TRUTH','GREAT','POWER','WORLD','EVERY','AFTER','NEVER',
              'WITHIN','SACRED','WISDOM','MASTER','WELCOME','PILGRIM','JOURNEY',
              'REALITY','INNOCENCE','ILLUSION','SUFFERING','STRUGGLE','DISCOVER',
              'EMERGE','INSTAR','NECESSARY','ULTIMATELY','PILGRIMAGE']:
        score += t.count(w) * 6
    return score

# ===== KNOWN P03 RESULT =====
p03 = load_page(3)
p04 = load_page(4)
divinity = keyword_to_gp('DIVINITY')
print(f"DIVINITY key: {divinity}")

# P03 F positions
p03_f = [i for i, c in enumerate(p03) if c == 0]
# Best mask from brute force: positions 48, 74, 84, 132, 159, 160, 250 are literal
p03_literal = {48, 74, 84, 132, 159, 160, 250}

# Verify P03 alone
dec = decrypt_fskip_set(p03, divinity, 'SUB', p03_literal)
print(f"\n=== P03 ALONE (verified) ===")
print(f"IoC: {ioc29(dec):.4f}, Score: {score_text(dec)}")
t = text(dec)
# Insert spaces for readability
print(f"\nRaw: {t}")

# ===== P03+P04 COMBINED =====
print(f"\n{'='*80}")
print(f"P03+P04 COMBINED -- key continues through")
print(f"{'='*80}")

combined = p03 + p04
# P04 starts at index len(p03) in combined array
p04_start = len(p03)
p04_f = [i for i, c in enumerate(combined) if c == 0 and i >= p04_start]
p04_n = len(p04_f)
print(f"P04 has {p04_n} F positions within combined: {p04_f}")
print(f"P04 alone has {len(p04)} runes")

# For combined, P03 skip positions stay the same since indices are the same
combined_p03_skip = p03_literal.copy()

best_score = 0
best_p04_mask = 0
for mask in range(2**p04_n):
    skip_set = combined_p03_skip.copy()
    for bit_idx, pos in enumerate(p04_f):
        if mask & (1 << bit_idx):
            skip_set.add(pos)
    dec = decrypt_fskip_set(combined, divinity, 'SUB', skip_set)
    s = score_text(dec)
    if s > best_score:
        best_score = s
        best_p04_mask = mask

# Reconstruct best
best_skip = combined_p03_skip.copy()
for bit_idx, pos in enumerate(p04_f):
    if best_p04_mask & (1 << bit_idx):
        best_skip.add(pos)

dec = decrypt_fskip_set(combined, divinity, 'SUB', best_skip)
t = text(dec)
ic = ioc29(dec)
p04_lits = [p04_f[i] for i in range(p04_n) if best_p04_mask & (1 << i)]
print(f"\nBest: IoC={ic:.4f}, Score={best_score}")
print(f"P04 literal F positions: {p04_lits}")
print(f"\nFull decrypted text:")
for i in range(0, len(t), 80):
    print(f"  {t[i:i+80]}")

# Show P03 and P04 portions separately
t_p03 = text(dec[:len(p03)])
t_p04 = text(dec[len(p03):])
print(f"\n--- P03 portion ({len(p03)} runes) ---")
print(f"  {t_p03}")
print(f"\n--- P04 portion ({len(p04)} runes) ---")
print(f"  {t_p04}")

# ===== ALSO TRY P04 SEPARATELY (key starting from position 0) =====
print(f"\n{'='*80}")
print(f"P04 ALONE with DIVINITY (fresh key)")
print(f"{'='*80}")
p04_alone_f = [i for i, c in enumerate(p04) if c == 0]
p04_alone_n = len(p04_alone_f)
print(f"P04: {len(p04)} runes, {p04_alone_n} F positions: {p04_alone_f}")
for mode in ['SUB', 'ADD', 'BEAU']:
    best_s = 0; best_m = 0
    for mask in range(2**p04_alone_n):
        skip = set()
        for bi, pos in enumerate(p04_alone_f):
            if mask & (1 << bi): skip.add(pos)
        dec = decrypt_fskip_set(p04, divinity, mode, skip)
        s = score_text(dec)
        if s > best_s: best_s = s; best_m = mask
    
    skip = set()
    for bi, pos in enumerate(p04_alone_f):
        if best_m & (1 << bi): skip.add(pos)
    dec = decrypt_fskip_set(p04, divinity, mode, skip)
    t = text(dec)
    print(f"  {mode}: score={best_s} IoC={ioc29(dec):.4f} -- {t[:100]}")

# ===== ALSO TRY DIFFERENT KEYWORDS ON P04 =====
print(f"\n{'='*80}")
print(f"P04 ALONE with various keywords")
print(f"{'='*80}")
keywords = ['DIVINITY','FIRFUMFERENFE','PILGRIM','WELCOME','TRUTH','SACRED',
            'WISDOM','INSTAR','EMERGE','REALITY','CICADA']
for kw in keywords:
    key = keyword_to_gp(kw)
    if not key: continue
    for mode in ['SUB']:
        best_s = 0; best_m = 0
        for mask in range(2**p04_alone_n):
            skip = set()
            for bi, pos in enumerate(p04_alone_f):
                if mask & (1 << bi): skip.add(pos)
            dec = decrypt_fskip_set(p04, key, mode, skip)
            s = score_text(dec)
            if s > best_s: best_s = s; best_m = mask
        
        skip = set()
        for bi, pos in enumerate(p04_alone_f):
            if best_m & (1 << bi): skip.add(pos)
        dec = decrypt_fskip_set(p04, key, mode, skip)
        t = text(dec)
        ic = ioc29(dec)
        if best_s > 10 or ic > 1.3:
            print(f"  {kw} {mode}: score={best_s} IoC={ic:.4f} -- {t[:100]}")

# ===== NOW TEST P14+P15 =====
print(f"\n{'='*80}")
print(f"P14 + P15 with FIRFUMFERENFE F-skip")
print(f"{'='*80}")
p14 = load_page(14)
p15 = load_page(15)
firfum = keyword_to_gp('FIRFUMFERENFE')
print(f"FIRFUMFERENFE key: {firfum}")

for pname, cipher in [("P14", p14), ("P15", p15), ("P14+P15", p14+p15)]:
    fps = [i for i, c in enumerate(cipher) if c == 0]
    n = len(fps)
    print(f"\n{pname}: {len(cipher)} runes, {n} F positions")
    if n > 20:
        print(f"  Too many F positions ({n}) for exhaustive. Using greedy+random...")
        # Multi-pass greedy
        import random
        best_s = 0; best_skip = set()
        for trial in range(100):
            if trial == 0:
                mask = 0
            else:
                mask = random.randint(0, 2**n - 1)
            skip = set()
            for bi, pos in enumerate(fps):
                if mask & (1 << bi): skip.add(pos)
            dec = decrypt_fskip_set(cipher, firfum, 'SUB', skip)
            s = score_text(dec)
            # Then greedy optimize
            for bi in range(n):
                pos = fps[bi]
                # Toggle
                if pos in skip: skip.discard(pos)
                else: skip.add(pos)
                dec = decrypt_fskip_set(cipher, firfum, 'SUB', skip)
                ns = score_text(dec)
                if ns > s:
                    s = ns
                else:
                    if fps[bi] in skip: skip.discard(pos)
                    else: skip.add(pos)
            if s > best_s:
                best_s = s; best_skip = skip.copy()
        
        dec = decrypt_fskip_set(cipher, firfum, 'SUB', best_skip)
        t = text(dec)
        ic = ioc29(dec)
        print(f"  Best: score={best_s}, IoC={ic:.4f}")
        print(f"  {t[:200]}")
    else:
        for mode in ['SUB', 'BEAU']:
            best_s = 0; best_m = 0
            for mask in range(2**n):
                skip = set()
                for bi, pos in enumerate(fps):
                    if mask & (1 << bi): skip.add(pos)
                dec = decrypt_fskip_set(cipher, firfum, mode, skip)
                s = score_text(dec)
                if s > best_s: best_s = s; best_m = mask
            
            skip = set()
            for bi, pos in enumerate(fps):
                if best_m & (1 << bi): skip.add(pos)
            dec = decrypt_fskip_set(cipher, firfum, mode, skip)
            t = text(dec)
            ic = ioc29(dec)
            lits = [fps[i] for i in range(n) if best_m & (1 << i)]
            if best_s > 10 or ic > 1.3:
                print(f"  {mode}: score={best_s} IoC={ic:.4f} skip@{lits}")
                print(f"    {t[:200]}")
