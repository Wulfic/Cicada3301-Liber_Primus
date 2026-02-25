"""
Brute-force F-skip on P03 with DIVINITY to find which F runes are literal.
Then apply the same technique to ALL other pages.
"""
import os, sys
from collections import Counter
from itertools import product

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

def decrypt_with_fskip_mask(cipher, key, mode, f_positions, skip_mask):
    """Decrypt with specific F-skip pattern.
    skip_mask: bitmask indicating which F positions are literal (1) vs encrypted (0)
    """
    result = []
    ki = 0
    kl = len(key)
    f_set = set()
    for bit_idx, pos in enumerate(f_positions):
        if skip_mask & (1 << bit_idx):
            f_set.add(pos)
    
    for i, c in enumerate(cipher):
        if i in f_set:
            # Literal F: output F, don't advance key
            result.append(0)
        else:
            k = key[ki % kl]
            if mode == 'SUB': p = (c - k) % 29
            elif mode == 'ADD': p = (c + k) % 29
            elif mode == 'BEAU': p = (k - c) % 29
            result.append(p)
            ki += 1
    return result

def score_text(vals):
    """Score based on English trigram frequency"""
    if len(vals) < 5: return 0
    t = text(vals).upper()
    # Common English words
    score = 0
    words_3 = ['THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','HER','WAS',
                'ONE','OUR','OUT','HIS','HAS','ITS','WHO','OWN','SAY','SHE','LET']
    for w in words_3:
        score += t.count(w) * 3
    words_2 = ['OF','TO','IN','IS','IT','AN','OR','IF','NO','SO','BY','AS','AT','WE','BE']
    for w in words_2:
        score += t.count(w) * 2
    words_4 = ['THAT','THIS','WITH','FROM','THEY','HAVE','BEEN','EACH','WILL',
                'YOUR','WHAT','WHEN','THEM','SOME','INTO','THAN','ONLY','SELF',
                'FIND','MAKE','JUST','KNOW']
    for w in words_4:
        score += t.count(w) * 4
    words_5 = ['WHICH','THEIR','ABOUT','BEING','THERE','THOSE','THING','WOULD',
                'SHALL','TRUTH','GREAT','POWER','WORLD','EVERY','AFTER','NEVER',
                'WITHIN','SACRED','WISDOM','MASTER']
    for w in words_5:
        score += t.count(w) * 5
    return score

# ===== BRUTE-FORCE P03 =====
print("=" * 80)
print("BRUTE FORCE: P03 with DIVINITY SUB, testing all F-skip combinations")
print("=" * 80)

p03 = load_page(3)
divinity = keyword_to_gp('DIVINITY')
f_positions = [i for i, c in enumerate(p03) if c == 0]
n_f = len(f_positions)
print(f"P03: {len(p03)} runes, {n_f} F positions: {f_positions}")
print(f"Testing {2**n_f} combinations...")

best_score = 0
best_mask = 0
best_text = ""
best_ioc = 0

for mask in range(2**n_f):
    dec = decrypt_with_fskip_mask(p03, divinity, 'SUB', f_positions, mask)
    score = score_text(dec)
    if score > best_score:
        best_score = score
        best_mask = mask
        best_text = text(dec)
        best_ioc = ioc29(dec)

# Show which F positions are literal
literal_fs = [f_positions[i] for i in range(n_f) if best_mask & (1 << i)]
encrypted_fs = [f_positions[i] for i in range(n_f) if not (best_mask & (1 << i))]
print(f"\nBest score: {best_score}, IoC*29: {best_ioc:.4f}")
print(f"Literal F positions (F-skip): {literal_fs}")
print(f"Encrypted F positions (normal): {encrypted_fs}")
print(f"\nDecrypted text:")
# Pretty print with line breaks every 80 chars
for i in range(0, len(best_text), 80):
    print(f"  {best_text[i:i+80]}")

# Also show top 5 results
print(f"\n--- Top 5 results ---")
results = []
for mask in range(2**n_f):
    dec = decrypt_with_fskip_mask(p03, divinity, 'SUB', f_positions, mask)
    score = score_text(dec)
    if score > best_score - 20:
        results.append((score, mask, ioc29(dec), text(dec)[:80]))
results.sort(reverse=True)
for score, mask, ic, t in results[:5]:
    lits = [f_positions[i] for i in range(n_f) if mask & (1 << i)]
    print(f"  score={score} IoC={ic:.4f} Fskip@{lits}")
    print(f"    {t}")

# ===== NOW APPLY TO P04, P14+P15 =====
print("\n" + "=" * 80)
print("P03+P04 COMBINED with optimal F-skip")
print("=" * 80)

p04 = load_page(4)
if p04:
    combined = p03 + p04
    f_positions_all = [i for i, c in enumerate(combined) if c == 0]
    n_fall = len(f_positions_all)
    print(f"P03+P04: {len(combined)} runes, {n_fall} F positions")
    
    if n_fall <= 20:
        print(f"Testing {2**n_fall} combinations (feasible)...")
        best_s = 0
        best_m = 0
        for mask in range(2**n_fall):
            dec = decrypt_with_fskip_mask(combined, divinity, 'SUB', f_positions_all, mask)
            score = score_text(dec)
            if score > best_s:
                best_s = score
                best_m = mask
        
        dec = decrypt_with_fskip_mask(combined, divinity, 'SUB', f_positions_all, best_m)
        t = text(dec)
        ic = ioc29(dec)
        lits = [f_positions_all[i] for i in range(n_fall) if best_m & (1 << i)]
        print(f"Best: score={best_s}, IoC={ic:.4f}")
        print(f"Literal F: {lits}")
        print(f"\nText:")
        for i in range(0, len(t), 80):
            print(f"  {t[i:i+80]}")
    else:
        print(f"Too many F positions ({n_fall}), using greedy approach...")
        # Greedy: start with no F-skip, toggle each F position and keep if score improves
        mask = 0
        dec = decrypt_with_fskip_mask(combined, divinity, 'SUB', f_positions_all, mask)
        current_score = score_text(dec)
        
        for bit in range(n_fall):
            test_mask = mask | (1 << bit)
            dec = decrypt_with_fskip_mask(combined, divinity, 'SUB', f_positions_all, test_mask)
            new_score = score_text(dec)
            if new_score > current_score:
                mask = test_mask
                current_score = new_score
        
        dec = decrypt_with_fskip_mask(combined, divinity, 'SUB', f_positions_all, mask)
        t = text(dec)
        ic = ioc29(dec)
        lits = [f_positions_all[i] for i in range(n_fall) if mask & (1 << i)]
        print(f"Greedy best: score={current_score}, IoC={ic:.4f}")
        print(f"Literal F: {lits}")
        for i in range(0, len(t), 80):
            print(f"  {t[i:i+80]}")
