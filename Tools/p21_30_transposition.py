#!/usr/bin/env python3
"""
Pages 21-30: Keyword-based transposition + Vigenère.
Hypothesis: cipher = Vigenère(transpose(plaintext, keyword), keyword)
Also: combined pages after Vigenère + single transposition.
"""
import sys, os, math
sys.stdout.reconfigure(encoding='utf-8')

GP = {'\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
      '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
      '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
      '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
      '\u16A3':26,'\u16E1':27,'\u16E0':28}
IDX2LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,'K':5,'L':20,
          'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}

COMMON_WORDS = ['THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','THIS','WILL','YOUR','FROM',
                'THAT','WITH','HAVE','BEEN','SOME','THEM','THAN','EACH','LIKE','INTO','JUST',
                'KNOW','BEING','WITHIN','SACRED','WISDOM','INSTRUCTION','WELCOME','PILGRIM',
                'DIVINITY','TRUTH','MIND','REALITY','SELF','THINGS','THERE','WHAT','NEVER',
                'ONLY','MUST','SHALL','UNTO','EVERY','GREAT','JOURNEY','TOWARD','THROUGH']

def keyword_to_gp(keyword):
    result = []
    i = 0
    kw = keyword.upper()
    while i < len(kw):
        if i+1 < len(kw):
            di = kw[i:i+2]
            if di in ('TH','NG','EO','OE','EA','AE','IA'):
                result.append({'TH':2,'NG':21,'EO':12,'OE':22,'EA':28,'AE':25,'IA':27}[di])
                i += 2
                continue
        if kw[i] in ENG2GP:
            result.append(ENG2GP[kw[i]])
        i += 1
    return result

def load_runes(page):
    with open(f'LiberPrimus/pages/page_{page:02d}/runes.txt','r',encoding='utf-8') as f:
        return [GP[c] for c in f.read() if c in GP]

def to_runeglish(indices):
    return ''.join(IDX2LAT[i] for i in indices)

def score_text(text):
    score = 0
    for word in COMMON_WORDS:
        if word in text:
            score += len(word) * 4
    return score

def vigenere_beau(c, k): return [(k[i%len(k)]-c[i])%29 for i in range(len(c))]
def vigenere_sub(c, k): return [(c[i]-k[i%len(k)])%29 for i in range(len(c))]
def vigenere_add(c, k): return [(c[i]+k[i%len(k)])%29 for i in range(len(c))]

MODES = {'sub':vigenere_sub,'add':vigenere_add,'beau':vigenere_beau}

def keyword_order(kw_gp):
    return [i for i,_ in sorted(enumerate(kw_gp), key=lambda x:x[1])]

def columnar_decrypt(data, key_order):
    ncols = len(key_order)
    nrows = math.ceil(len(data)/ncols)
    pad = nrows*ncols - len(data)
    col_lens = [nrows]*ncols
    for i in range(pad):
        col_lens[key_order[ncols-1-i]] -= 1
    cols = [[]]*ncols
    pos = 0
    for ci in key_order:
        cols[ci] = data[pos:pos+col_lens[ci]]
        pos += col_lens[ci]
    result = []
    for r in range(nrows):
        for c in range(ncols):
            if r < len(cols[c]):
                result.append(cols[c][r])
    return result

def rail_fence_decrypt(data, rails):
    if rails < 2 or rails >= len(data): return data
    n = len(data)
    cycle = 2*(rails-1)
    pattern = [min(i%cycle, cycle-i%cycle) for i in range(n)]
    rl = [0]*rails
    for r in pattern: rl[r] += 1
    rd = [[]]*rails
    idx = 0
    for r in range(rails):
        rd[r] = list(data[idx:idx+rl[r]])
        idx += rl[r]
    rp = [0]*rails
    result = []
    for r in pattern:
        result.append(rd[r][rp[r]])
        rp[r] += 1
    return result

PAGE_KEYS = {
    21:('CABAL','beau'), 22:('DIVINITY','beau'), 23:('ENCRYPTION','add'),
    24:('OBSCURA','beau'), 26:('ENCRYPT','add'), 27:('SHADOWS','add'),
    28:('DEOR','sub'), 29:('TOTIENT','beau'), 30:('MOURNFUL','add'),
}
ALL_KW = ['CABAL','DIVINITY','ENCRYPTION','OBSCURA','ENCRYPT','SHADOWS','DEOR','TOTIENT',
          'MOURNFUL','PILGRIM','WISDOM','SACRED','PRIMUS','LIBER','KOAN','VOID',
          'CIRCUMFERENCE','FIRFUMFERENFE','CONSUMPTION','PRESERVATION','ADHERENCE','MOBIUS']

print("="*70)
print("TEST 1: KEYWORD AS VIGENÈRE + COLUMNAR TRANSPOSITION KEY")
print("="*70)

for page in sorted(PAGE_KEYS.keys()):
    cipher = load_runes(page)
    best = (0,'','')
    
    for kw in ALL_KW:
        key = keyword_to_gp(kw)
        if not key: continue
        ko = keyword_order(key)
        
        for mode_name, mode_fn in MODES.items():
            # Vigenère then columnar decrypt
            vig = mode_fn(cipher, key)
            untrans = columnar_decrypt(vig, ko)
            text = to_runeglish(untrans)
            sc = score_text(text)
            if sc > best[0]:
                best = (sc, f'{kw}_{mode_name}_col', text)
            
            # For same keyword: try columnar widths 2-50
            for w in range(2, min(50, len(cipher)//2)):
                untrans_w = columnar_decrypt(vig, list(range(w)))
                text_w = to_runeglish(untrans_w)
                sc_w = score_text(text_w)
                if sc_w > best[0]:
                    best = (sc_w, f'{kw}_{mode_name}_colw{w}', text_w)
            
            # Rail fence
            for rails in range(2, 20):
                untrans_rf = rail_fence_decrypt(vig, rails)
                text_rf = to_runeglish(untrans_rf)
                sc_rf = score_text(text_rf)
                if sc_rf > best[0]:
                    best = (sc_rf, f'{kw}_{mode_name}_rf{rails}', text_rf)
    
    # Cross-keyword: Vigenère with primary key, transposition with different key
    primary_kw, primary_mode = PAGE_KEYS[page]
    primary_key = keyword_to_gp(primary_kw)
    vig = MODES[primary_mode](cipher, primary_key)
    
    for trans_kw in ALL_KW:
        trans_key = keyword_to_gp(trans_kw)
        if not trans_key: continue
        trans_order = keyword_order(trans_key)
        untrans = columnar_decrypt(vig, trans_order)
        text = to_runeglish(untrans)
        sc = score_text(text)
        if sc > best[0]:
            best = (sc, f'{primary_kw}_{primary_mode}+{trans_kw}_col', text)
    
    print(f"P{page:02d}: score={best[0]:>4d} | {best[1]}")
    if best[0] > 100:
        print(f"  {best[2][:120]}")

# ===== TEST 2: Reversed/interleaved reading + Vigenère =====
print(f"\n{'='*70}")
print("TEST 2: ALTERNATIVE READ ORDERS + VIGENÈRE")
print(f"{'='*70}")

for page in sorted(PAGE_KEYS.keys()):
    cipher = load_runes(page)
    best = (0,'','')
    kw_name, mode_name = PAGE_KEYS[page]
    key = keyword_to_gp(kw_name)
    mode_fn = MODES[mode_name]
    
    # Reversed
    plain = mode_fn(list(reversed(cipher)), key)
    text = to_runeglish(plain)
    sc = score_text(text)
    if sc > best[0]: best = (sc, 'reversed', text)
    
    # Even/odd interleave
    evens = cipher[::2]
    odds = cipher[1::2]
    for reorder in [evens+odds, odds+evens]:
        plain = mode_fn(reorder, key)
        text = to_runeglish(plain)
        sc = score_text(text)
        if sc > best[0]: best = (sc, 'evod_interleave', text)
    
    # Skip-n patterns
    for skip in [3, 5, 7, 11, 13]:
        reordered = []
        for start in range(skip):
            reordered.extend(cipher[start::skip])
        plain = mode_fn(reordered, key)
        text = to_runeglish(plain)
        sc = score_text(text)
        if sc > best[0]: best = (sc, f'skip{skip}', text)
    
    print(f"P{page:02d}: score={best[0]:>4d} | {kw_name}_{mode_name}+{best[1]}")

# ===== TEST 3: Combined all pages then transposition =====
print(f"\n{'='*70}")
print("TEST 3: COMBINED PAGES AFTER VIGENÈRE + TRANSPOSITION")
print(f"{'='*70}")

combined = []
for page in sorted(PAGE_KEYS.keys()):
    cipher = load_runes(page)
    kw_name, mode_name = PAGE_KEYS[page]
    key = keyword_to_gp(kw_name)
    decrypted = MODES[mode_name](cipher, key)
    combined.extend(decrypted)

print(f"Combined: {len(combined)} runes")
base_text = to_runeglish(combined)
base_score = score_text(base_text)
print(f"Base score: {base_score}")

best_comb = (base_score, 'none', base_text)
for w in range(2, 60):
    u = columnar_decrypt(combined, list(range(w)))
    t = to_runeglish(u)
    s = score_text(t)
    if s > best_comb[0]: best_comb = (s, f'col_w{w}', t)

for rails in range(2, 30):
    u = rail_fence_decrypt(combined, rails)
    t = to_runeglish(u)
    s = score_text(t)
    if s > best_comb[0]: best_comb = (s, f'rf_{rails}', t)

# Keyword columnar on combined
for kw in ALL_KW:
    key = keyword_to_gp(kw)
    if not key: continue
    ko = keyword_order(key)
    u = columnar_decrypt(combined, ko)
    t = to_runeglish(u)
    s = score_text(t)
    if s > best_comb[0]: best_comb = (s, f'col_{kw}', t)

print(f"\nBest: score={best_comb[0]} | {best_comb[1]}")
print(f"  {best_comb[2][:200]}")

# ===== TEST 4: Different page order in combination =====
print(f"\n{'='*70}")
print("TEST 4: REVERSE PAGE ORDER + VIGENÈRE + TRANSPOSITION")
print(f"{'='*70}")

combined_rev_pages = []
for page in reversed(sorted(PAGE_KEYS.keys())):
    cipher = load_runes(page)
    kw_name, mode_name = PAGE_KEYS[page]
    key = keyword_to_gp(kw_name)
    decrypted = MODES[mode_name](cipher, key)
    combined_rev_pages.extend(decrypted)

rev_text = to_runeglish(combined_rev_pages)
rev_score = score_text(rev_text)
print(f"Reversed page order score: {rev_score}")
print(f"  {rev_text[:200]}")

print("\nDone.")
