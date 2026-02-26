#!/usr/bin/env python3
"""
Novel attack approaches with CORRECT GP mapping:
1. Running key cipher using solved page plaintexts
2. Sequential page chain (each page's plaintext = next page's key)
3. Verify totient/φ(prime) cipher on P55/P56/P57
4. Page-number based algorithmic keys
5. GP prime-value operations (multiply, divide, XOR of prime values)
6. Autokey cipher variants
"""

import os, sys, io
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ====================== CORRECT GP MAPPING ======================
GP_RUNES = list("ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛂᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ")
GP_LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
            'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]

GP_RUNE_TO_IDX = {r: i for i, r in enumerate(GP_RUNES)}
GP_RUNE_TO_IDX['\u16C4'] = 11  # ᛄ alias

LETTER_TO_IDX = {}
for i, lt in enumerate(GP_LATIN):
    LETTER_TO_IDX[lt] = i
for i, lt in enumerate(GP_LATIN):
    if len(lt) == 1:
        LETTER_TO_IDX[lt] = i
LETTER_TO_IDX['V'] = 1; LETTER_TO_IDX['K'] = 5; LETTER_TO_IDX['Z'] = 15; LETTER_TO_IDX['Q'] = 5

def runes_to_indices(text):
    return [GP_RUNE_TO_IDX[ch] for ch in text if ch in GP_RUNE_TO_IDX]

def indices_to_latin(indices):
    return ''.join(GP_LATIN[i] for i in indices)

def text_to_indices(text):
    """Convert English text to GP index array."""
    indices = []
    i = 0
    t = text.upper().replace(' ', '')
    while i < len(t):
        if i + 2 <= len(t):
            d = t[i:i+2]
            if d in LETTER_TO_IDX:
                indices.append(LETTER_TO_IDX[d])
                i += 2
                continue
        ch = t[i]
        if ch in LETTER_TO_IDX:
            indices.append(LETTER_TO_IDX[ch])
        i += 1
    return indices

def ioc29(indices):
    if len(indices) < 2: return 0
    c = Counter(indices)
    n = len(indices)
    return 29 * sum(v*(v-1) for v in c.values()) / (n*(n-1))

def load_page(pn):
    path = os.path.join('LiberPrimus', 'pages', f'page_{pn:02d}', 'runes.txt')
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return runes_to_indices(f.read())

# English word scoring
COMMON_WORDS = set(['THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','HER','WAS','ONE','OUR',
    'OUT','HAS','HIS','HOW','ITS','MAY','NEW','NOW','OLD','SEE','WAY','WHO','BOY','DID',
    'GET','HIM','LET','SAY','SHE','TOO','USE','DAD','MOM','MAN','DAY','HAD','HAS',
    'THAT','THIS','WITH','HAVE','FROM','THEY','BEEN','SAID','EACH','WHICH','THEIR',
    'WILL','OTHER','ABOUT','INTO','THAN','THEM','THEN','WHEN','SOME','WHAT','WERE',
    'THERE','THOSE','BEING','WOULD','COULD','SHOULD','THESE','AFTER','BEFORE','WITHIN',
    'THROUGH','BETWEEN','WITHOUT','DURING','AGAINST','UPON','UNTO','YOUR','SELF','TRUTH',
    'KNOW','FIND','WISDOM','SACRED','PRIME','PRIMES','TOTIENT','EMERGE','SHED','BODY',
    'MIND','SOUL','DEATH','LIFE','PATH','LOSS','THAT','MOST','JUST','LIKE','MAKE',
    'OVER','SUCH','TAKE','THAN','VERY','COME','MADE','MANY','ONLY','ALSO','BACK',
    'EVEN','GIVE','MORE','MOST','MUST','NAME','NEED','NEXT','OF'])

def score_text(text):
    """Score GP latin text for English-likeness."""
    score = 0
    for w in COMMON_WORDS:
        if w in text:
            score += len(w) * len(w)
    return score

os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/..')

# ====================== SOLVED PLAINTEXTS ======================
SOLVED_TEXTS = {
    'P01_WARNING': "A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE TEST THE KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH DO NOT EDIT OR CHANGE THIS BOOK OR THE MESSAGE CONTAINED WITHIN EITHER THE WORDS OR THEIR NUMBERS FOR ALL IS SACRED",
    'P03_WELCOME': "WELCOME WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS IT IS NOT AN EASY TRIP BUT FOR THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE ALONG THE WAY YOU WILL FIND AN END TO ALL STRUGGLE AND SUFFERING YOUR INNOCENCE YOUR ILLUSIONS YOUR CERTAINTY AND YOUR REALITY ULTIMATELY YOU WILL DISCOVER AN END TO SELF",
    'P04_SHAPE': "IT IS THROUGH THIS PILGRIMAGE THAT WE SHAPE OURSELVES AND OUR REALITIES JOURNEY DEEP WITHIN AND YOU WILL ARRIVE OUTSIDE LIKE THE INSTAR IT IS ONLY THROUGH GOING WITHIN THAT WE MAY EMERGE WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY AN INSTRUCTION COMMAND YOUR OWN SELF",
    'P05_WISDOM': "SOME WISDOM THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED ALL THINGS SHOULD BE ENCRYPTED KNOW THIS",
    'P06_KOAN': "A KOAN A MAN DECIDED TO GO AND STUDY WITH A MASTER HE WENT TO THE DOOR OF THE MASTER WHO ARE YOU WHO WISHES TO STUDY HERE ASKED THE MASTER THE STUDENT TOLD THE MASTER HIS NAME THAT IS NOT WHAT YOU ARE THAT IS ONLY WHAT YOU ARE CALLED WHO ARE YOU WHO WISHES TO STUDY HERE HE ASKED AGAIN THE MAN THOUGHT FOR A MOMENT AND REPLIED I AM A PROFESSOR THAT IS WHAT YOU DO NOT WHAT YOU ARE REPLIED THE MASTER WHO ARE YOU WHO WISHES TO STUDY HERE CONFUSED THE MAN THOUGHT SOME MORE FINALLY HE ANSWERED I AM A HUMAN BEING THAT IS ONLY YOUR SPECIES NOT WHO YOU ARE WHO ARE YOU WHO WISHES TO STUDY HERE ASKED THE MASTER AGAIN AFTER A MOMENT OF THOUGHT THE PROFESSOR REPLIED I AM A CONSCIOUSNESS INHABITING AN ARBITRARY BODY THAT IS MERELY WHAT YOU ARE NOT WHO YOU ARE WHO ARE YOU WHO WISHES TO STUDY HERE THE MAN WAS GETTING IRRITATED I AM HE STARTED BUT HE COULD NOT THINK OF ANYTHING ELSE TO SAY SO HE TRAILED OFF AFTER A LONG PAUSE THE MASTER REPLIED THEN YOU ARE WELCOME TO COME STUDY AN INSTRUCTION DO FOUR UNREASONABLE THINGS EACH DAY",
    'P10_LOSS': "THE LOSS OF DIVINITY THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS WHICH CAUSE THE LOSS OF DIVINITY CONSUMPTION WE CONSUME TOO MUCH BECAUSE WE BELIEVE THE FOLLOWING TWO ERRORS WITHIN THE DECEPTION WE DO NOT HAVE ENOUGH OR THERE IS NOT ENOUGH WE HAVE WHAT WE HAVE NOW BY LUCK AND WE WILL NOT BE STRONG ENOUGH LATER TO OBTAIN WHAT WE NEED MOST THINGS ARE NOT WORTH CONSUMING PRESERVATION WE PRESERVE THINGS BECAUSE WE BELIEVE WE ARE WEAK IF WE LOSE THEM WE WILL NOT BE STRONG ENOUGH TO GAIN THEM AGAIN THIS IS THE DECEPTION MOST THINGS ARE NOT WORTH PRESERVING ADHERENCE WE FOLLOW DOGMA SO THAT WE CAN BELONG AND BE RIGHT OR WE FOLLOW REASON SO WE CAN BELONG AND BE RIGHT THERE IS NOTHING TO BE RIGHT ABOUT TO BELONG IS DEATH IT IS THE BEHAVIORS OF CONSUMPTION PRESERVATION AND ADHERENCE THAT HAVE US LOSE OUR PRIMALITY AND THUS OUR DIVINITY SOME WISDOM AMASS GREAT WEALTH NEVER BECOME ATTACHED TO WHAT YOU OWN BE PREPARED TO DESTROY ALL THAT YOU OWN AN INSTRUCTION PROGRAM YOUR MIND PROGRAM REALITY",
    'P14_KOAN2': "A KOAN DURING A LESSON THE MASTER EXPLAINED THE I THE I IS THE VOICE OF THE CIRCUMFERENCE HE SAID WHEN ASKED BY A STUDENT TO EXPLAIN WHAT THAT MEANT THE MASTER SAID IT IS A VOICE INSIDE YOUR HEAD I DONT HAVE A VOICE IN MY HEAD THOUGHT THE STUDENT AND HE RAISED HIS HAND TO TELL THE MASTER THE MASTER STOPPED THE STUDENT AND SAID THE VOICE THAT JUST SAID YOU HAVE NO VOICE IN YOUR HEAD IS THE I AND THE STUDENTS WERE ENLIGHTENED",
    'P16_INSTRUCTION': "AN INSTRUCTION QUESTION ALL THINGS DISCOVER TRUTH INSIDE YOURSELF FOLLOW YOUR TRUTH IMPOSE NOTHING ON OTHERS KNOW THIS",
    'P55_END': "AN END WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO IT IS THE DUTY OF EVERY PILGRIM TO SEEK OUT THIS PAGE",
    'P56_PARABLE': "PARABLE LIKE THE INSTAR TUNNELING TO THE SURFACE WE MUST SHED OUR OWN CIRCUMFERENCES FIND THE DIVINITY WITHIN AND EMERGE",
    'P74_INST': "AN INSTRUCTION QUESTION ALL THINGS DISCOVER TRUTH INSIDE YOURSELF FOLLOW YOUR TRUTH IMPOSE NOTHING ON OTHERS KNOW THIS",
}

# Convert all to GP indices
SOLVED_INDICES = {}
for name, text in SOLVED_TEXTS.items():
    SOLVED_INDICES[name] = text_to_indices(text)

print("=" * 80)
print("SOLVED PLAINTEXT LENGTHS (in GP indices):")
print("=" * 80)
for name, idx in SOLVED_INDICES.items():
    print(f"  {name:20s}: {len(idx)} GP indices")

# ====================== ATTACK 1: RUNNING KEY WITH SOLVED PLAINTEXTS ======================
print("\n" + "=" * 80)
print("ATTACK 1: RUNNING KEY CIPHER (solved plaintext as key)")
print("=" * 80)

hits = []
for pn in range(18, 55):
    cipher = load_page(pn)
    if not cipher or len(cipher) < 20:
        continue
    
    for src_name, key_indices in SOLVED_INDICES.items():
        if len(key_indices) < len(cipher):
            continue  # Key must be at least as long as ciphertext
        
        for mode in ['sub', 'add', 'beaufort']:
            for offset in range(0, min(50, len(key_indices) - len(cipher) + 1), 1):
                key = key_indices[offset:offset+len(cipher)]
                
                if mode == 'sub':
                    dec = [(cipher[i] - key[i]) % 29 for i in range(len(cipher))]
                elif mode == 'add':
                    dec = [(cipher[i] + key[i]) % 29 for i in range(len(cipher))]
                else:
                    dec = [(key[i] - cipher[i]) % 29 for i in range(len(cipher))]
                
                ic = ioc29(dec)
                if ic > 1.3:
                    text = indices_to_latin(dec)[:60]
                    sc = score_text(text)
                    hits.append((ic, sc, pn, src_name, mode, offset, text))

hits.sort(key=lambda x: (-x[0], -x[1]))
if hits:
    print(f"\nFound {len(hits)} results with IoC > 1.3:")
    for ic, sc, pn, src, mode, off, text in hits[:30]:
        print(f"  P{pn:02d} key={src:20s}/{mode:8s} off={off:3d}: IoC={ic:.4f} score={sc:3d}  {text}")
else:
    print("\n  *** NO RUNNING KEY RESULTS WITH IoC > 1.3 ***")

# ====================== ATTACK 2: AUTOKEY CIPHER ======================
print("\n" + "=" * 80)
print("ATTACK 2: AUTOKEY CIPHER (ciphertext/plaintext feeds back as key)")
print("=" * 80)

def autokey_decrypt(cipher, seed_key, mode='pt_autokey'):
    """
    Autokey cipher where:
    - pt_autokey: key = seed || plaintext  (plaintext autokey)
    - ct_autokey: key = seed || ciphertext (ciphertext autokey)
    """
    dec = []
    key_stream = list(seed_key)
    
    for i in range(len(cipher)):
        k = key_stream[i] if i < len(key_stream) else 0
        
        p = (cipher[i] - k) % 29  # SUB mode
        dec.append(p)
        
        if mode == 'pt_autokey':
            key_stream.append(p)
        else:  # ct_autokey
            key_stream.append(cipher[i])
    
    return dec

# Test autokey with various seed keys
autokey_hits = []
SEED_KEYS = {
    'DIVINITY': [23, 10, 1, 10, 9, 10, 16, 26],
    'CABAL': [5, 24, 17, 24, 20],
    'SHADOWS': [15, 8, 24, 23, 3, 7, 15],
    'TOTIENT': [16, 3, 16, 10, 18, 9, 16],
    'PRIMES': [13, 4, 10, 19, 18, 15],
    'SACRED': [15, 24, 5, 4, 18, 23],
    'ENCRYPT': [18, 9, 5, 4, 26, 13, 16],
    'DEOR': [23, 18, 3, 4],
    'WISDOM': [7, 10, 15, 23, 3, 19],
    'INSTAR': [10, 9, 15, 16, 24, 4],
    'INTUS': [10, 9, 16, 1, 15],
    'PILGRIM': [13, 10, 20, 6, 4, 10, 19],
    'EMERGENCE': [18, 19, 18, 4, 6, 18, 9, 5, 18],
    'CIRCUMFERENCE': [5, 10, 4, 5, 1, 19, 0, 18, 4, 18, 9, 5, 18],
    'FIRFUMFERENFE': [0, 10, 4, 0, 1, 19, 0, 18, 4, 18, 9, 0, 18],
}

for pn in range(18, 55):
    cipher = load_page(pn)
    if not cipher or len(cipher) < 20:
        continue
    
    for kw_name, seed in SEED_KEYS.items():
        for ak_mode in ['pt_autokey', 'ct_autokey']:
            # SUB autokey
            dec = autokey_decrypt(cipher, seed, ak_mode)
            ic = ioc29(dec)
            if ic > 1.3:
                text = indices_to_latin(dec)[:60]
                autokey_hits.append((ic, pn, kw_name, ak_mode, 'sub', text))
            
            # ADD autokey
            dec_add = []
            key_stream = list(seed)
            for i in range(len(cipher)):
                k = key_stream[i] if i < len(key_stream) else 0
                p = (cipher[i] + k) % 29
                dec_add.append(p)
                if ak_mode == 'pt_autokey':
                    key_stream.append(p)
                else:
                    key_stream.append(cipher[i])
            ic = ioc29(dec_add)
            if ic > 1.3:
                text = indices_to_latin(dec_add)[:60]
                autokey_hits.append((ic, pn, kw_name, ak_mode, 'add', text))
            
            # BEAUFORT autokey
            dec_beau = []
            key_stream = list(seed)
            for i in range(len(cipher)):
                k = key_stream[i] if i < len(key_stream) else 0
                p = (k - cipher[i]) % 29
                dec_beau.append(p)
                if ak_mode == 'pt_autokey':
                    key_stream.append(p)
                else:
                    key_stream.append(cipher[i])
            ic = ioc29(dec_beau)
            if ic > 1.3:
                text = indices_to_latin(dec_beau)[:60]
                autokey_hits.append((ic, pn, kw_name, ak_mode, 'beau', text))

autokey_hits.sort(reverse=True)
if autokey_hits:
    print(f"\nFound {len(autokey_hits)} autokey results with IoC > 1.3:")
    for ic, pn, kw, ak, cipher_mode, text in autokey_hits[:30]:
        print(f"  P{pn:02d} {kw:16s} {ak:12s}/{cipher_mode}: IoC={ic:.4f}  {text}")
else:
    print("\n  *** NO AUTOKEY RESULTS WITH IoC > 1.3 ***")

# ====================== ATTACK 3: TOTIENT CIPHER VERIFICATION ======================
print("\n" + "=" * 80)
print("ATTACK 3: VERIFY TOTIENT CIPHER ON P55/P56 (known solutions)")
print("=" * 80)

def gen_primes(n):
    primes = []
    c = 2
    while len(primes) < n:
        ok = True
        for p in primes:
            if p*p > c: break
            if c % p == 0: ok = False; break
        if ok: primes.append(c)
        c += 1
    return primes

primes = gen_primes(5000)

# P56 is known to use: plaintext = (cipher - (prime_i - 1)) % 29
for pn in [55, 56, 57]:
    cipher = load_page(pn)
    if not cipher:
        print(f"\n  P{pn}: NO DATA")
        continue
    
    print(f"\nP{pn}: {len(cipher)} runes")
    
    for start in range(10):
        for mode_name, op in [('sub_pm1', lambda c,p: (c - (p-1)) % 29),
                               ('add_pm1', lambda c,p: (c + (p-1)) % 29),
                               ('sub_phi', lambda c,p: (c - ((p-1) % 29)) % 29),
                               ('add_phi', lambda c,p: (c + ((p-1) % 29)) % 29)]:
            # Standard totient
            dec = [op(cipher[i], primes[start+i]) for i in range(len(cipher))]
            ic = ioc29(dec)
            text = indices_to_latin(dec)[:80]
            if ic > 1.3 or (pn in [55,56] and start < 3):
                print(f"  {mode_name} start={start}: IoC={ic:.4f}  {text}")
            
            # F-skip variant
            dec_fs = []
            k = start
            for c in cipher:
                if c == 0:
                    dec_fs.append(0)
                else:
                    dec_fs.append(op(c, primes[k]))
                    k += 1
            ic_fs = ioc29(dec_fs)
            text_fs = indices_to_latin(dec_fs)[:80]
            if ic_fs > 1.3:
                print(f"  {mode_name}_fskip start={start}: IoC={ic_fs:.4f}  {text_fs}")

# ====================== ATTACK 4: PAGE-NUMBER ALGORITHMIC KEYS ======================
print("\n" + "=" * 80)
print("ATTACK 4: PAGE-NUMBER BASED KEYS")
print("=" * 80)

algo_hits = []
for pn in range(18, 55):
    cipher = load_page(pn)
    if not cipher or len(cipher) < 20:
        continue
    n = len(cipher)
    
    # Key = page number repeated
    for key_val in [pn, pn % 29, (29 - pn) % 29, pn * 2 % 29, pn * 3 % 29]:
        for mode in ['sub', 'add']:
            if mode == 'sub':
                dec = [(c - key_val) % 29 for c in cipher]
            else:
                dec = [(c + key_val) % 29 for c in cipher]
            ic = ioc29(dec)
            if ic > 1.3:
                text = indices_to_latin(dec)[:60]
                algo_hits.append((ic, pn, f'const_{key_val}', mode, text))
    
    # Key = fibonacci sequence mod 29
    fib = [1, 1]
    for i in range(n): fib.append(fib[-1] + fib[-2])
    for offset in range(5):
        for mode in ['sub', 'add']:
            if mode == 'sub':
                dec = [(cipher[i] - fib[offset+i] % 29) % 29 for i in range(n)]
            else:
                dec = [(cipher[i] + fib[offset+i] % 29) % 29 for i in range(n)]
            ic = ioc29(dec)
            if ic > 1.3:
                text = indices_to_latin(dec)[:60]
                algo_hits.append((ic, pn, f'fib_off{offset}', mode, text))
    
    # Key = triangular numbers mod 29
    for mode in ['sub', 'add']:
        tri = [i*(i+1)//2 % 29 for i in range(n)]
        if mode == 'sub':
            dec = [(cipher[i] - tri[i]) % 29 for i in range(n)]
        else:
            dec = [(cipher[i] + tri[i]) % 29 for i in range(n)]
        ic = ioc29(dec)
        if ic > 1.3:
            text = indices_to_latin(dec)[:60]
            algo_hits.append((ic, pn, 'triangular', mode, text))
    
    # Key = i^2 mod 29 (quadratic)
    for mode in ['sub', 'add']:
        quad = [i*i % 29 for i in range(n)]
        if mode == 'sub':
            dec = [(cipher[i] - quad[i]) % 29 for i in range(n)]
        else:
            dec = [(cipher[i] + quad[i]) % 29 for i in range(n)]
        ic = ioc29(dec)
        if ic > 1.3:
            text = indices_to_latin(dec)[:60]
            algo_hits.append((ic, pn, 'quadratic', mode, text))

if algo_hits:
    algo_hits.sort(reverse=True)
    print(f"\nFound {len(algo_hits)} algorithmic key results with IoC > 1.3:")
    for ic, pn, desc, mode, text in algo_hits[:20]:
        print(f"  P{pn:02d} {desc:16s}/{mode}: IoC={ic:.4f}  {text}")
else:
    print("\n  *** NO ALGORITHMIC KEY RESULTS ***")

# ====================== ATTACK 5: GP PRIME VALUE OPERATIONS ======================
print("\n" + "=" * 80)
print("ATTACK 5: PRIME VALUE DOMAIN OPERATIONS")
print("=" * 80)

# What if operations happen in the PRIME domain?
# cipher_prime_value OP key_value → plaintext_prime_value
prime_hits = []
IDX_TO_PRIME = {i: GP_PRIMES[i] for i in range(29)}
PRIME_TO_IDX = {p: i for i, p in enumerate(GP_PRIMES)}

for pn in [18, 19, 20, 21, 49, 54]:  # Test on subset first
    cipher = load_page(pn)
    if not cipher or len(cipher) < 20:
        continue
    n = len(cipher)
    
    # Convert cipher to prime values
    cipher_primes = [GP_PRIMES[c] for c in cipher]
    
    # For each keyword, try: prime_result = (cipher_prime * key_prime) mod some_modulus
    for kw_name, key in SEED_KEYS.items():
        key_ext = (key * (n // len(key) + 1))[:n]
        key_primes = [GP_PRIMES[k] for k in key_ext]
        
        # XOR of prime values mod 29
        dec_xor = [(cipher_primes[i] ^ key_primes[i]) % 29 for i in range(n)]
        ic = ioc29(dec_xor)
        if ic > 1.3:
            text = indices_to_latin(dec_xor)[:60]
            prime_hits.append((ic, pn, kw_name, 'prime_xor', text))
        
        # Multiply prime values mod 29*prime(29)=29*109=3161
        for modulus in [29, 109, 113, 127, 131, 137, 139]:
            dec_mul = [(cipher_primes[i] * key_primes[i]) % modulus % 29 for i in range(n)]
            ic = ioc29(dec_mul)
            if ic > 1.3:
                text = indices_to_latin(dec_mul)[:60]
                prime_hits.append((ic, pn, kw_name, f'prime_mul_mod{modulus}', text))

if prime_hits:
    prime_hits.sort(reverse=True)
    print(f"\nFound {len(prime_hits)} prime domain results with IoC > 1.3:")
    for ic, pn, kw, op, text in prime_hits[:20]:
        print(f"  P{pn:02d} {kw:16s} {op:20s}: IoC={ic:.4f}  {text}")
else:
    print("\n  *** NO PRIME DOMAIN RESULTS ***")

# ====================== ATTACK 6: SINGLE-RUNE WORD CONSTRAINT ======================
print("\n" + "=" * 80)
print("ATTACK 6: SINGLE-RUNE WORD ANALYSIS")
print("=" * 80)
print("Every single-rune word must be I(10) or A(24) in plaintext.")
print("This gives known plaintext-ciphertext pairs at those positions.\n")

for pn in range(18, 55):
    path = os.path.join('LiberPrimus', 'pages', f'page_{pn:02d}', 'runes.txt')
    if not os.path.exists(path):
        continue
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    
    # Find word boundaries
    words = []
    current_word = []
    pos = 0
    for ch in raw:
        if ch in GP_RUNE_TO_IDX:
            current_word.append((pos, GP_RUNE_TO_IDX[ch]))
            pos += 1
        elif ch in ('•', ' ', '\n', '\r', '\t') and current_word:
            words.append(current_word)
            current_word = []
        # Skip non-rune, non-separator characters
    if current_word:
        words.append(current_word)
    
    # Find single-rune words
    single_rune_words = [(w[0][0], w[0][1]) for w in words if len(w) == 1]
    
    if single_rune_words:
        print(f"P{pn:02d}: {len(single_rune_words)} single-rune words at positions:")
        for pos, cipher_val in single_rune_words:
            # If plaintext = I (10): key[pos] = (cipher - 10) % 29 (SUB mode)
            #                          key[pos] = (10 - cipher) % 29 (BEAU mode)
            # If plaintext = A (24): key[pos] = (cipher - 24) % 29 (SUB mode)
            key_if_I_sub = (cipher_val - 10) % 29
            key_if_A_sub = (cipher_val - 24) % 29
            key_if_I_add = (10 - cipher_val) % 29
            key_if_A_add = (24 - cipher_val) % 29
            print(f"    pos={pos:4d} cipher={cipher_val:2d}({GP_LATIN[cipher_val]:3s})"
                  f"  →SUB: key={key_if_I_sub:2d}(if I) or {key_if_A_sub:2d}(if A)"
                  f"  →ADD: key={key_if_I_add:2d}(if I) or {key_if_A_add:2d}(if A)")

# ====================== ATTACK 7: BRUTE FORCE SMALL PAGES ======================
print("\n" + "=" * 80)
print("ATTACK 7: HILL-CLIMBING ON P49 (66 runes) AND P54 (76 runes)")
print("=" * 80)

import random
random.seed(42)

# English trigram frequencies from known solved GP text
# Build frequency model from solved texts
all_solved_text = ' '.join(SOLVED_TEXTS.values())
solved_idx = text_to_indices(all_solved_text)
trigram_freq = Counter()
for i in range(len(solved_idx) - 2):
    trigram_freq[(solved_idx[i], solved_idx[i+1], solved_idx[i+2])] += 1

def score_trigrams(indices):
    score = 0
    for i in range(len(indices) - 2):
        t = (indices[i], indices[i+1], indices[i+2])
        if t in trigram_freq:
            score += trigram_freq[t]
    return score

for pn in [49, 54]:
    cipher = load_page(pn)
    if not cipher:
        continue
    
    print(f"\nP{pn}: {len(cipher)} runes — brute-force Caesar + hill-climbing simple substitution")
    
    # Caesar shifts (all 29)
    best_caesar = (0, 0, '')
    for shift in range(29):
        dec = [(c + shift) % 29 for c in cipher]
        sc = score_trigrams(dec)
        if sc > best_caesar[0]:
            best_caesar = (sc, shift, indices_to_latin(dec))
    
    sc, shift, text = best_caesar
    print(f"  Best Caesar: shift={shift} score={sc} IoC={ioc29([(c+shift)%29 for c in cipher]):.4f}")
    print(f"  Text: {text[:80]}")
    
    # Affine cipher: p = (a*c + b) % 29
    best_affine = (0, 0, 0, '')
    for a in range(1, 29):
        # Check if a is coprime to 29 (29 is prime, so all 1-28 work)
        for b in range(29):
            dec = [(a * c + b) % 29 for c in cipher]
            sc = score_trigrams(dec)
            if sc > best_affine[0]:
                best_affine = (sc, a, b, indices_to_latin(dec))
    
    sc, a, b, text = best_affine
    print(f"  Best Affine: a={a} b={b} score={sc}")
    print(f"  Text: {text[:80]}")

print("\n=== NOVEL ATTACKS COMPLETE ===")
