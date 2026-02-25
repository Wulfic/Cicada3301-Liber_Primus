#!/usr/bin/env python3
"""
Phase 2 Attack for Liber Primus Unsolved Pages
================================================
Tests approaches NOT yet tried with correct GP mapping:
1. Ciphertext-autokey (d-step differencing) for d=1..100
2. Plaintext-autokey for seed lengths 1-3 (29, 841, 24389 seeds)
3. Self-Reliance (Emerson) as running key
4. Large offset totient (0-15000)
5. Continuous stream hypothesis (all pages as one stream)
6. Bigram/trigram IoC analysis (detect Hill cipher)
7. Higher-order LFSR GF(29) with order 3-6
"""

import os, sys, math, itertools
from collections import Counter

# ============================================================
# Gematria Primus (CORRECT mapping from advanced_cipher_attack.py)
# ============================================================
RUNE_TO_INDEX = {
    '\u16A0':0, '\u16A2':1, '\u16A6':2, '\u16A9':3, '\u16B1':4,
    '\u16B3':5, '\u16B7':6, '\u16B9':7, '\u16BB':8, '\u16BE':9,
    '\u16C1':10, '\u16C2':11, '\u16C4':11, '\u16C7':12, '\u16C8':13,
    '\u16C9':14, '\u16CB':15, '\u16CF':16, '\u16D2':17, '\u16D6':18,
    '\u16D7':19, '\u16DA':20, '\u16DD':21, '\u16DF':22, '\u16DE':23,
    '\u16AA':24, '\u16AB':25, '\u16A3':26, '\u16E1':27, '\u16E0':28
}

INDEX_TO_LATIN = {
    0:'F', 1:'U', 2:'TH', 3:'O', 4:'R', 5:'C', 6:'G', 7:'W',
    8:'H', 9:'N', 10:'I', 11:'J', 12:'EO', 13:'P', 14:'X',
    15:'S', 16:'T', 17:'B', 18:'E', 19:'M', 20:'L', 21:'NG',
    22:'OE', 23:'D', 24:'A', 25:'AE', 26:'Y', 27:'IA', 28:'EA'
}

LATIN_TO_INDEX = {}
for idx, lat in INDEX_TO_LATIN.items():
    LATIN_TO_INDEX[lat] = idx

def indices_to_text(indices):
    return ''.join(INDEX_TO_LATIN.get(i, '?') for i in indices)

def load_page_runes(page_num):
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rune_path = os.path.join(base, 'LiberPrimus', 'pages', f'page_{page_num:02d}', 'runes.txt')
    if not os.path.exists(rune_path):
        return []
    raw = open(rune_path, 'r', encoding='utf-8').read()
    return [RUNE_TO_INDEX[c] for c in raw if c in RUNE_TO_INDEX]

def load_page_raw(page_num):
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rune_path = os.path.join(base, 'LiberPrimus', 'pages', f'page_{page_num:02d}', 'runes.txt')
    if not os.path.exists(rune_path):
        return ""
    return open(rune_path, 'r', encoding='utf-8').read()

def calculate_ioc(indices):
    if len(indices) <= 1:
        return 0
    freq = [0]*29
    for i in indices:
        freq[i] += 1
    n = len(indices)
    return sum(f*(f-1) for f in freq) / (n*(n-1)) * 29

def bigram_ioc(indices):
    """Calculate bigram IoC (29^2 = 841 possible bigrams)"""
    if len(indices) <= 3:
        return 0
    bigrams = [(indices[i], indices[i+1]) for i in range(len(indices)-1)]
    freq = Counter(bigrams)
    n = len(bigrams)
    return sum(f*(f-1) for f in freq.values()) / (n*(n-1)) * 841

def trigram_ioc(indices):
    """Calculate trigram IoC (29^3 = 24389 possible trigrams)"""
    if len(indices) <= 5:
        return 0
    trigrams = [(indices[i], indices[i+1], indices[i+2]) for i in range(len(indices)-2)]
    freq = Counter(trigrams)
    n = len(trigrams)
    if n <= 1:
        return 0
    return sum(f*(f-1) for f in freq.values()) / (n*(n-1)) * 24389

def score_english(text):
    text_upper = text.upper()
    common = ['THE','AND','THAT','HAVE','FOR','NOT','WITH','YOU','THIS','BUT',
              'HIS','FROM','THEY','BEEN','WILL','EACH','WHICH','THEIR',
              'WOULD','MAKE','LIKE','TIME','JUST','KNOW','WHO','ARE','WAS',
              'ONE','ALL','HAD','HAS','WHEN','CAN','THERE','WHAT','SOME',
              'DIVINITY','TRUTH','WISDOM','SACRED','PRIMES','TOTIENT',
              'SPIRIT','SOUL','DEATH','FAITH','PATH','BEING','THINGS','WORLD',
              'WITHIN','SEEK','FIND','DEEP','INSTAR','EMERGE','SELF','NATURE']
    score = sum(text_upper.count(w) * len(w) * 2 for w in common)
    trigrams = ['THE','AND','ING','ENT','ION','HER','FOR','THA','NTH','INT',
                'ERE','TIO','VER','EST','ALL','ATE','OUS','ITH','HIS','TER']
    score += sum(text_upper.count(t) * 3 for t in trigrams)
    return score

def sieve_primes(limit):
    is_p = [True]*(limit+1)
    is_p[0] = is_p[1] = False
    for i in range(2, int(limit**0.5)+1):
        if is_p[i]:
            for j in range(i*i, limit+1, i):
                is_p[j] = False
    return [i for i in range(2, limit+1) if is_p[i]]

def euler_totient(n):
    result = n
    p = 2
    temp = n
    while p*p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result

def text_to_gp_indices(text):
    """Convert English text to GP indices for running key"""
    text = text.upper()
    indices = []
    i = 0
    while i < len(text):
        if i < len(text) - 2:
            tri = text[i:i+3]
            if tri == 'ING':
                indices.append(LATIN_TO_INDEX.get('NG', 21))
                i += 3
                continue
        if i < len(text) - 1:
            two = text[i:i+2]
            if two in LATIN_TO_INDEX:
                indices.append(LATIN_TO_INDEX[two])
                i += 2
                continue
        one = text[i]
        if one in LATIN_TO_INDEX:
            indices.append(LATIN_TO_INDEX[one])
        i += 1
    return indices

UNSOLVED_PAGES = list(range(17, 55))
FOCUS_PAGES = [17, 19, 20, 21, 22, 23, 24, 25, 32, 40, 44, 50]

print("="*80)
print("PHASE 2 ATTACK - LIBER PRIMUS")
print("="*80)

# Load all unsolved pages
page_data = {}
for p in UNSOLVED_PAGES:
    data = load_page_runes(p)
    if data:
        page_data[p] = data
        
print(f"\nLoaded {len(page_data)} unsolved pages")
for p in sorted(page_data.keys()):
    print(f"  P{p:02d}: {len(page_data[p])} runes, IoC={calculate_ioc(page_data[p]):.4f}")

# ============================================================
# SECTION 1: BIGRAM/TRIGRAM IoC ANALYSIS
# Detect if Hill cipher (elevated bigram IoC with flat monogram IoC)
# ============================================================
print("\n" + "="*80)
print("SECTION 1: BIGRAM/TRIGRAM IoC ANALYSIS")
print("="*80)
print("If bigram IoC >> 1.0 while monogram IoC ≈ 1.0, suggests Hill cipher")
print(f"{'Page':>6} {'#Runes':>7} {'Mono IoC':>10} {'Bigram IoC':>12} {'Trigram IoC':>13}")
for p in sorted(page_data.keys()):
    d = page_data[p]
    if len(d) < 20:
        continue
    mi = calculate_ioc(d)
    bi = bigram_ioc(d) if len(d) >= 50 else 0
    ti = trigram_ioc(d) if len(d) >= 100 else 0
    flag = " *** ELEVATED" if bi > 1.3 else ""
    print(f"  P{p:02d}  {len(d):>7}  {mi:>10.4f}  {bi:>12.4f}  {ti:>13.4f}{flag}")

# ============================================================
# SECTION 2: CIPHERTEXT-AUTOKEY (d-step differencing)
# ============================================================
print("\n" + "="*80)
print("SECTION 2: CIPHERTEXT-AUTOKEY (d-step differencing)")
print("="*80)
print("Testing P[i] = (C[i] - C[i-d]) mod 29 for d=1..100")
print("Equivalent to ciphertext-autokey with seed length d")

best_autokey = []
for p in sorted(page_data.keys()):
    C = page_data[p]
    if len(C) < 50:
        continue
    page_best_ioc = 0
    page_best_d = 0
    for d in range(1, min(101, len(C))):
        # Compute d-step difference
        diff = [(C[i] - C[i-d]) % 29 for i in range(d, len(C))]
        ioc = calculate_ioc(diff)
        if ioc > page_best_ioc:
            page_best_ioc = ioc
            page_best_d = d
    
    if page_best_ioc > 1.2:
        best_autokey.append((p, page_best_d, page_best_ioc))
        
    if page_best_ioc > 1.15:
        # Also try ADD mode
        diff_add = [(C[i] + C[i-page_best_d]) % 29 for i in range(page_best_d, len(C))]
        ioc_add = calculate_ioc(diff_add)
        print(f"  P{p:02d} d={page_best_d:>3}: SUB IoC={page_best_ioc:.4f}, ADD IoC={ioc_add:.4f}")

if not best_autokey:
    print("  No pages with ciphertext-autokey IoC > 1.2")
else:
    print(f"\n  Best hits (IoC > 1.2):")
    for p, d, ioc in sorted(best_autokey, key=lambda x: -x[2]):
        # Decrypt with the best d, try all seed values
        C = page_data[p]
        diff = [(C[i] - C[i-d]) % 29 for i in range(d, len(C))]
        txt = indices_to_text(diff[:100])
        print(f"    P{p:02d} d={d}: IoC={ioc:.4f} -> {txt[:80]}...")

# Try all 3 modes more carefully for best hits
for p, d, ioc in best_autokey:
    if ioc > 1.4:
        C = page_data[p]
        print(f"\n  *** Promising: P{p:02d} d={d} IoC={ioc:.4f}")
        for mode_name, mode_fn in [("SUB", lambda c,k: (c-k)%29), 
                                     ("ADD", lambda c,k: (c+k)%29),
                                     ("BEAU", lambda c,k: (k-c)%29)]:
            diff = [mode_fn(C[i], C[i-d]) for i in range(d, len(C))]
            txt = indices_to_text(diff[:120])
            sc = score_english(txt)
            print(f"    {mode_name}: score={sc:>4} {txt[:100]}...")

# ============================================================
# SECTION 3: PLAINTEXT-AUTOKEY 
# ============================================================
print("\n" + "="*80)
print("SECTION 3: PLAINTEXT-AUTOKEY (seed lengths 1-3)")
print("="*80)

best_pt_autokey = []
for p in FOCUS_PAGES:
    if p not in page_data:
        continue
    C = page_data[p]
    if len(C) < 50:
        continue
    
    for seed_len in [1, 2]:
        if seed_len == 1:
            seed_range = range(29)
        else:
            seed_range = itertools.product(range(29), repeat=2)
        
        for seed_val in seed_range:
            if seed_len == 1:
                seed = [seed_val]
            else:
                seed = list(seed_val)
            
            for mode_name, mode_fn in [("SUB", lambda c,k: (c-k)%29),
                                        ("ADD", lambda c,k: (c+k)%29),
                                        ("BEAU", lambda c,k: (k-c)%29)]:
                # Decrypt with plaintext-autokey
                plain = []
                for i in range(len(C)):
                    if i < seed_len:
                        key_val = seed[i]
                    else:
                        key_val = plain[i - seed_len]
                    plain.append(mode_fn(C[i], key_val))
                
                ioc = calculate_ioc(plain)
                if ioc > 1.45:
                    txt = indices_to_text(plain[:80])
                    sc = score_english(txt)
                    best_pt_autokey.append((p, seed_len, seed, mode_name, ioc, sc, txt))

if best_pt_autokey:
    best_pt_autokey.sort(key=lambda x: -x[4])
    print(f"  Found {len(best_pt_autokey)} hits with IoC > 1.45:")
    for p, sl, seed, mode, ioc, sc, txt in best_pt_autokey[:30]:
        print(f"    P{p:02d} seed_len={sl} seed={seed} {mode}: IoC={ioc:.4f} score={sc:>4} -> {txt[:70]}...")
else:
    print("  No plaintext-autokey hits with IoC > 1.45 for seed lengths 1-2")

# ============================================================
# SECTION 4: SELF-RELIANCE AS RUNNING KEY
# ============================================================
print("\n" + "="*80)
print("SECTION 4: SELF-RELIANCE AS RUNNING KEY")
print("="*80)

# Extract Self-Reliance text - try loading from file first
self_reliance_text = ""
sr_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'emerson_self_reliance.txt')
if os.path.exists(sr_path):
    self_reliance_text = open(sr_path, 'r', encoding='utf-8').read()
    
if not self_reliance_text:
    # Use a truncated version of Self-Reliance opening
    self_reliance_text = """I read the other day some verses written by an eminent painter which were
original and not conventional. The soul always hears an admonition in such lines,
let the subject be what it may. The sentiment they instill is of more value than
any thought they may contain. To believe your own thought, to believe that what
is true for you in your private heart is true for all men, that is genius.
Speak your latent conviction, and it shall be the universal sense; for the inmost
in due time becomes the outmost, and our first thought is rendered back to us by
the trumpets of the Last Judgment. Familiar as the voice of the mind is to each,
the highest merit we ascribe to Moses, Plato, and Milton is, that they set at
naught books and traditions, and spoke not what men, but what they thought.
A man should learn to detect and watch that gleam of light which flashes across
his mind from within, more than the luster of the firmament of bards and sages.
Yet he dismisses without notice his thought, because it is his. In every work of
genius we recognize our own rejected thoughts: they come back to us with a certain
alienated majesty. Trust thyself: every heart vibrates to that iron string.
Accept the place the divine providence has found for you, the society of your
contemporaries, the connection of events. Great men have always done so.
There is a time in every mans education when he arrives at the conviction that
envy is ignorance; that imitation is suicide; that he must take himself for
better, for worse, as his portion; that though the wide universe is full of good,
no kernel of nourishing corn can come to him but through his toil bestowed on
that plot of ground which is given to him to till. The power which resides in him
is new in nature, and none but he knows what that is which he can do, nor does he
know until he has tried. Whoso would be a man must be a nonconformist. He who
would gather immortal palms must not be hindered by the name of goodness, but must
explore if it be goodness. Nothing is at last sacred but the integrity of your own
mind. What I must do is all that concerns me, not what the people think. This rule
equally arduous in actual and in intellectual life may serve for the whole distinction
between greatness and meanness. It is easy in the world to live after the worlds
opinion; it is easy in solitude to live after our own; but the great man is he who
in the midst of the crowd keeps with perfect sweetness the independence of solitude.
A foolish consistency is the hobgoblin of little minds, adored by little statesmen
and philosophers and divines. With consistency a great soul has simply nothing to do.
He may as well concern himself with his shadow on the wall. Speak what you think now
in hard words, and to-morrow speak what to-morrow thinks in hard words again, though
it contradict every thing you said to-day. Life only avails, not the having lived.
Power ceases in the instant of repose; it resides in the moment of transition from
a past to a new state, in the shooting of the gulf, in the darting to an aim.
Insist on yourself; never imitate. Your own gift you can present every moment with
the cumulative force of a whole lifes cultivation. Society never advances. It recedes
as fast on one side as it gains on the other. And so the reliance on Property,
including the reliance on governments which protect it, is the want of self-reliance.
Nothing can bring you peace but yourself. Nothing can bring you peace but the
triumph of principles."""

sr_indices = text_to_gp_indices(self_reliance_text)
print(f"Self-Reliance key: {len(sr_indices)} GP indices")

# Try Self-Reliance at various offsets as running key
best_sr = []
for p in sorted(page_data.keys()):
    C = page_data[p]
    if len(C) < 30:
        continue
    
    for offset in range(0, max(1, len(sr_indices) - len(C)), 50):
        key = sr_indices[offset:offset+len(C)]
        if len(key) < len(C):
            break
        
        for mode_name, mode_fn in [("SUB", lambda c,k: (c-k)%29),
                                    ("ADD", lambda c,k: (c+k)%29),
                                    ("BEAU", lambda c,k: (k-c)%29)]:
            plain = [mode_fn(C[i], key[i]) for i in range(len(C))]
            ioc = calculate_ioc(plain)
            if ioc > 1.4:
                txt = indices_to_text(plain[:80])
                sc = score_english(txt)
                best_sr.append((p, offset, mode_name, ioc, sc, txt))

if best_sr:
    best_sr.sort(key=lambda x: -x[4])
    print(f"  Found {len(best_sr)} hits with IoC > 1.4:")
    for p, off, mode, ioc, sc, txt in best_sr[:20]:
        print(f"    P{p:02d} off={off:>4} {mode}: IoC={ioc:.4f} score={sc:>4} -> {txt[:70]}...")
else:
    print("  No Self-Reliance running key hits with IoC > 1.4")

# ============================================================
# SECTION 5: LARGE OFFSET TOTIENT
# ============================================================
print("\n" + "="*80)
print("SECTION 5: LARGE OFFSET TOTIENT (offsets 0-15000)")
print("="*80)
print("Testing phi(prime[i+offset]) as keystream on focus pages")

primes = sieve_primes(200000)  # Need enough primes

# Pre-compute totient values
phi_cache = {}
def get_phi(n):
    if n not in phi_cache:
        phi_cache[n] = euler_totient(n)
    return phi_cache[n]

best_totient = []
test_pages = [20, 32, 25, 50, 44, 40, 17, 19, 22]  # Largest/most important first
for p in test_pages:
    if p not in page_data:
        continue
    C = page_data[p]
    if len(C) < 50:
        continue
    
    print(f"  Testing P{p:02d} ({len(C)} runes)...", end=" ", flush=True)
    page_best = (0, 0)
    
    for offset in range(0, 15001, 1):
        if offset + len(C) >= len(primes):
            break
        
        # Compute phi(prime[i+offset]) % 29 keystream
        key = [get_phi(primes[offset + i]) % 29 for i in range(len(C))]
        
        for mode_name, mode_fn in [("SUB", lambda c,k: (c-k)%29),
                                    ("BEAU", lambda c,k: (k-c)%29)]:
            plain = [mode_fn(C[i], key[i]) for i in range(len(C))]
            ioc = calculate_ioc(plain)
            if ioc > page_best[1]:
                page_best = (offset, ioc)
            if ioc > 1.45:
                txt = indices_to_text(plain[:80])
                sc = score_english(txt)
                best_totient.append((p, offset, mode_name, ioc, sc, txt))
    
    print(f"best IoC={page_best[1]:.4f} at offset={page_best[0]}")

if best_totient:
    best_totient.sort(key=lambda x: -x[4])
    print(f"\n  Found {len(best_totient)} hits with IoC > 1.45:")
    for p, off, mode, ioc, sc, txt in best_totient[:20]:
        print(f"    P{p:02d} off={off:>5} {mode}: IoC={ioc:.4f} score={sc:>4} -> {txt[:70]}...")
else:
    print("  No totient hits with IoC > 1.45 in range 0-15000")

# ============================================================
# SECTION 6: CONTINUOUS STREAM HYPOTHESIS
# ============================================================
print("\n" + "="*80)
print("SECTION 6: CONTINUOUS STREAM HYPOTHESIS")
print("="*80)
print("Concatenate pages as continuous stream, apply totient with cumulative index")

# Load ALL pages 0-54 and compute cumulative rune counts
all_page_runes = {}
cumulative = {}
total = 0
for p in range(0, 55):
    runes = load_page_runes(p)
    all_page_runes[p] = runes
    cumulative[p] = total
    total += len(runes)
    if runes:
        print(f"  P{p:02d}: {len(runes):>5} runes, cumulative start: {cumulative[p]}")

print(f"  Total runes P00-P54: {total}")

# Now try totient stream starting from offset 0 through the whole corpus
# For unsolved pages (17-54), check if treating them as part of one stream helps
print(f"\n  Testing totient stream where each page's prime index = cumulative position...")

for p in [17, 18, 19, 20, 21, 22]:
    if p not in page_data:
        continue
    C = page_data[p]
    offset = cumulative[p]
    if offset + len(C) >= len(primes):
        continue
    
    key = [get_phi(primes[offset + i]) % 29 for i in range(len(C))]
    for mname in ["SUB", "BEAU"]:
        if mname == "SUB":
            plain = [(C[i] - key[i]) % 29 for i in range(len(C))]
        else:
            plain = [(key[i] - C[i]) % 29 for i in range(len(C))]
        ioc = calculate_ioc(plain)
        txt = indices_to_text(plain[:60])
        sc = score_english(txt)
        flag = " ***" if ioc > 1.4 else ""
        print(f"    P{p:02d} cum_offset={offset:>5} {mname}: IoC={ioc:.4f} score={sc:>3}{flag} -> {txt[:50]}...")

# Also try prime_direct (prime[i+offset] mod 29) as keystream
print(f"\n  Testing prime_direct stream (prime[i+cum_offset] mod 29)...")
for p in [17, 18, 19, 20, 21, 22, 25, 32]:
    if p not in page_data:
        continue
    C = page_data[p]
    offset = cumulative[p]
    if offset + len(C) >= len(primes):
        continue
    
    key = [primes[offset + i] % 29 for i in range(len(C))]
    for mname in ["SUB", "BEAU"]:
        if mname == "SUB":
            plain = [(C[i] - key[i]) % 29 for i in range(len(C))]
        else:
            plain = [(key[i] - C[i]) % 29 for i in range(len(C))]
        ioc = calculate_ioc(plain)
        if ioc > 1.15:
            txt = indices_to_text(plain[:60])
            print(f"    P{p:02d} cum_offset={offset:>5} {mname}: IoC={ioc:.4f} -> {txt[:50]}...")

# ============================================================
# SECTION 7: HIGHER-ORDER LFSR GF(29) 
# ============================================================
print("\n" + "="*80)
print("SECTION 7: HIGHER-ORDER LFSR - IoC SCREENING")
print("="*80)
print("For d-step autokey, if IoC was elevated, try LFSR interpretation")

# The ciphertext-autokey d-step test already tells us if LFSR of that order 
# would help. If d-step differencing doesn't elevate IoC, then LFSR of that
# order won't help either with a simple substitution.

# A better approach: if the cipher is LFSR_key XOR plaintext (mod 29),
# then we need to find LFSR params that produce the keystream.
# But first, check if ANY linear recurrence exists in the ciphertext.

# For small pages, try order-3 LFSR with brute force on coefficients
print("Testing LFSR order-3 on focus pages with known-plaintext cribs...")

def try_lfsr_order3(C, known_prefix_indices):
    """Try all LFSR(3) params: K[i] = (a*K[i-1] + b*K[i-2] + c*K[i-3]) mod 29
       Recover key from known plaintext, check if it follows LFSR(3)"""
    n = len(known_prefix_indices)
    if n < 6:
        return []
    
    # Recover key assuming SUB: K[i] = (C[i] - P[i]) mod 29
    key = [(C[i] - known_prefix_indices[i]) % 29 for i in range(n)]
    
    results = []
    # Check if key follows LFSR(3): key[i] = (a*key[i-1]+b*key[i-2]+c*key[i-3]) mod 29
    for a in range(29):
        for b in range(29):
            for c in range(29):
                ok = True
                for i in range(3, n):
                    expected = (a*key[i-1] + b*key[i-2] + c*key[i-3]) % 29
                    if expected != key[i]:
                        ok = False
                        break
                if ok and (a != 0 or b != 0 or c != 0):
                    results.append((a, b, c))
    return results

# Try with "THE INSTAR" prefix on P49
the_instar = text_to_gp_indices("THEINSTAR")
print(f"  'THE INSTAR' = {the_instar} ({len(the_instar)} indices)")

for p in [49, 47, 48, 42, 20, 17]:
    if p not in page_data:
        continue
    C = page_data[p]
    
    # Try various known prefixes
    prefixes = {
        "THEINSTAR": text_to_gp_indices("THEINSTAR"),
        "THEPRIMES": text_to_gp_indices("THEPRIMES"),
        "SOMEWISDOM": text_to_gp_indices("SOMEWISDOM"),
        "ANINSTRUCTION": text_to_gp_indices("ANINSTRUCTION"),
        "WARNING": text_to_gp_indices("WARNING"),
    }
    
    for prefix_name, prefix_idx in prefixes.items():
        if len(prefix_idx) < 6:
            continue
        results = try_lfsr_order3(C, prefix_idx)
        if results:
            print(f"    P{p:02d} prefix='{prefix_name}': LFSR(3) matches: {results[:5]}")
            # Extend key and decrypt  
            for a, b, c in results[:3]:
                key = [(C[i] - prefix_idx[i]) % 29 for i in range(len(prefix_idx))]
                for i in range(len(key), len(C)):
                    key.append((a*key[i-1] + b*key[i-2] + c*key[i-3]) % 29)
                plain = [(C[i] - key[i]) % 29 for i in range(len(C))]
                ioc = calculate_ioc(plain)
                txt = indices_to_text(plain[:80])
                sc = score_english(txt)
                print(f"      a={a},b={b},c={c}: IoC={ioc:.4f} score={sc:>4} -> {txt[:60]}...")

# ============================================================
# SECTION 8: NOVEL KEY DERIVATION - PAGE NUMBER OFFSET
# ============================================================
print("\n" + "="*80)
print("SECTION 8: PAGE-SPECIFIC PRIME OFFSETS")
print("="*80)
print("What if each page's totient offset = page_number * some_constant?")

multiples_to_try = [1, 7, 11, 13, 17, 23, 29, 31, 37, 41, 43, 47, 53, 59, 
                    71, 73, 89, 97, 101, 127, 131, 167, 173, 233, 283, 317, 
                    761, 1033, 3301]

best_page_offset = []
for mult in multiples_to_try:
    for p in FOCUS_PAGES:
        if p not in page_data:
            continue
        C = page_data[p]
        offset = (p * mult) % len(primes)
        if offset + len(C) >= len(primes):
            continue
        
        key = [get_phi(primes[offset + i]) % 29 for i in range(len(C))]
        for mname in ["SUB", "BEAU"]:
            if mname == "SUB":
                plain = [(C[i] - key[i]) % 29 for i in range(len(C))]
            else:
                plain = [(key[i] - C[i]) % 29 for i in range(len(C))]
            ioc = calculate_ioc(plain)
            if ioc > 1.45:
                txt = indices_to_text(plain[:60])
                sc = score_english(txt)
                best_page_offset.append((p, mult, offset, mname, ioc, sc))

if best_page_offset:
    best_page_offset.sort(key=lambda x: -x[4])
    print(f"  Found {len(best_page_offset)} hits with IoC > 1.45:")
    for p, mult, off, mode, ioc, sc in best_page_offset[:20]:
        print(f"    P{p:02d} mult={mult:>4} offset={off:>6} {mode}: IoC={ioc:.4f} score={sc:>4}")
else:
    print("  No page-specific offset hits with IoC > 1.45")

# Also try prime_direct (prime value mod 29, not totient)
print(f"\n  Same with prime_direct (prime[i+offset] mod 29)...")
best_pd_offset = []
for mult in multiples_to_try:
    for p in FOCUS_PAGES:
        if p not in page_data:
            continue
        C = page_data[p]
        offset = (p * mult) % len(primes)
        if offset + len(C) >= len(primes):
            continue
        
        key = [primes[offset + i] % 29 for i in range(len(C))]
        for mname in ["SUB", "BEAU"]:
            if mname == "SUB":
                plain = [(C[i] - key[i]) % 29 for i in range(len(C))]
            else:
                plain = [(key[i] - C[i]) % 29 for i in range(len(C))]
            ioc = calculate_ioc(plain)
            if ioc > 1.45:
                txt = indices_to_text(plain[:60])
                sc = score_english(txt)
                best_pd_offset.append((p, mult, offset, mname, ioc, sc))

if best_pd_offset:
    best_pd_offset.sort(key=lambda x: -x[4])
    for p, mult, off, mode, ioc, sc in best_pd_offset[:10]:
        print(f"    P{p:02d} mult={mult:>4} offset={off:>6} {mode}: IoC={ioc:.4f} score={sc:>4}")
else:
    print("  No prime_direct page-offset hits either")

# ============================================================
# SECTION 9: FIBONACCI-INDEXED PRIMES
# ============================================================
print("\n" + "="*80)
print("SECTION 9: FIBONACCI-INDEXED PRIMES AS KEYSTREAM")
print("="*80)
print("'Rearranging the primes' = using Fibonacci ordering?")

# Generate Fibonacci sequence
fib = [1, 1]
while fib[-1] < 200000:
    fib.append(fib[-1] + fib[-2])

# Key = prime[fib[i]] mod 29 or phi(prime[fib[i]]) mod 29
fib_prime_key = []
fib_totient_key = []
for i in range(len(fib)):
    if fib[i] < len(primes):
        fib_prime_key.append(primes[fib[i]] % 29)
        fib_totient_key.append(get_phi(primes[fib[i]]) % 29)

print(f"  Fibonacci-indexed prime key: {len(fib_prime_key)} values")

for p in FOCUS_PAGES:
    if p not in page_data:
        continue
    C = page_data[p]
    if len(C) > len(fib_prime_key):
        continue
    
    for key_name, key in [("fib_prime", fib_prime_key), ("fib_totient", fib_totient_key)]:
        for mname in ["SUB", "BEAU"]:
            if mname == "SUB":
                plain = [(C[i] - key[i]) % 29 for i in range(len(C))]
            else:
                plain = [(key[i] - C[i]) % 29 for i in range(len(C))]
            ioc = calculate_ioc(plain)
            if ioc > 1.3:
                txt = indices_to_text(plain[:60])
                sc = score_english(txt)
                print(f"    P{p:02d} {key_name} {mname}: IoC={ioc:.4f} score={sc:>3} -> {txt[:50]}...")

# ============================================================
# SECTION 10: OUTGUESS DATA ANALYSIS
# ============================================================
print("\n" + "="*80)
print("SECTION 10: OUTGUESS DATA KEY EXTRACTION")
print("="*80)

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for fname in ['outguess_00.txt', 'outguess_08.txt', 'outguess_17.txt', 'outguess_21.txt', 'outguess_43.txt']:
    fpath = os.path.join(base_dir, fname)
    if os.path.exists(fpath):
        data = open(fpath, 'rb').read()
        print(f"\n  {fname}: {len(data)} bytes")
        
        # Check for ASCII content
        try:
            text = data.decode('utf-8', errors='replace')
            # Look for any readable text
            ascii_chars = sum(1 for c in text if 32 <= ord(c) <= 126)
            print(f"    ASCII chars: {ascii_chars}/{len(text)} ({100*ascii_chars/len(text):.1f}%)")
            if ascii_chars > len(text) * 0.5:
                print(f"    First 200 chars: {text[:200]}")
        except:
            pass
        
        # Check for rune content
        rune_chars = sum(1 for c in data.decode('utf-8', errors='replace') if c in RUNE_TO_INDEX)
        if rune_chars > 0:
            print(f"    Rune chars found: {rune_chars}")
        
        # Check byte frequency distribution
        freq = Counter(data)
        # If evenly distributed, likely encrypted/random
        # If concentrated, likely has structure
        unique_bytes = len(freq)
        max_freq = max(freq.values())
        min_freq = min(freq.values()) if freq else 0
        print(f"    Unique bytes: {unique_bytes}/256, max_freq={max_freq}, min_freq={min_freq}")
        
        # Try treating bytes as key stream (mod 29)
        if fname == 'outguess_17.txt':
            byte_key = [b % 29 for b in data[:2000]]
            # Try as key for page 17
            if 17 in page_data:
                C = page_data[17]
                key = byte_key[:len(C)]
                if len(key) == len(C):
                    for mname in ["SUB", "BEAU"]:
                        if mname == "SUB":
                            plain = [(C[i] - key[i]) % 29 for i in range(len(C))]
                        else:
                            plain = [(key[i] - C[i]) % 29 for i in range(len(C))]
                        ioc = calculate_ioc(plain)
                        if ioc > 1.15:
                            txt = indices_to_text(plain[:60])
                            print(f"    As key for P17 {mname}: IoC={ioc:.4f} -> {txt[:50]}...")

print("\n" + "="*80)
print("PHASE 2 ATTACK COMPLETE")
print("="*80)
