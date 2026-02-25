#!/usr/bin/env python3
"""
Fresh comprehensive attack on unsolved Liber Primus pages.
Session 3 - Feb 25, 2026
Focuses on genuinely untested cipher methods with J-fixed GP mapping.
"""

import os, sys, math, json
from collections import Counter
from itertools import product

# ===== GP MAPPING WITH J FIX =====
GP_RUNES = list("ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛞᛟᛡᛠᚪᚫᚣ")
GP_LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','D','OE','A','EA','IA','AE','Y']
GP_RUNE_TO_IDX = {r: i for i, r in enumerate(GP_RUNES)}

def runes_to_indices(rune_text):
    """Convert rune string to list of GP indices, skipping separators."""
    indices = []
    for ch in rune_text:
        if ch in GP_RUNE_TO_IDX:
            indices.append(GP_RUNE_TO_IDX[ch])
    return indices

def indices_to_latin(indices):
    """Convert GP indices to Latin text."""
    return ''.join(GP_LATIN[i] for i in indices)

def load_page(page_num):
    """Load a page's rune text and return indices."""
    path = os.path.join('LiberPrimus', 'pages', f'page_{page_num:02d}', 'runes.txt')
    if not os.path.exists(path):
        return None, None
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    indices = runes_to_indices(text)
    return text, indices

def ioc_29(indices):
    """Index of coincidence * 29."""
    if len(indices) < 2:
        return 0
    counts = Counter(indices)
    n = len(indices)
    total = sum(c * (c - 1) for c in counts.values())
    return 29 * total / (n * (n - 1))

# ===== ENGLISH SCORING =====
COMMON_WORDS = {'THE','AND','OF','TO','IN','IS','IT','THAT','FOR','WAS','ON','ARE','AS','WITH',
    'HIS','THEY','BE','AT','ONE','HAVE','THIS','FROM','OR','HAD','BY','NOT','BUT','SOME',
    'WHAT','THERE','WE','CAN','OUT','OTHER','WERE','ALL','YOUR','WHEN','UP','USE','HOW',
    'EACH','WHICH','THEIR','IF','DO','WILL','AN','ABOUT','MANY','THEN','SO','HER','WOULD',
    'MAKE','HIM','INTO','HAS','TWO','MORE','NO','WAY','COULD','MY','THAN','BEEN','WHO',
    'ITS','NOW','DID','GET','COME','MADE','MAY','AFTER','ALSO','MUST','SAID','FIND','YOU',
    'WITHIN','THROUGH','SELF','BEING','UNTO','HOLY','SACRED','WISDOM','TRUTH','PATH',
    'DIVINITY','INSTRUCTION','WARNING','BELIEVE','NOTHING','KNOW','QUESTION','COMMAND',
    'PILGRIM','JOURNEY','END','SHALL','THESE','THOSE','BEFORE','UPON','WHY','BETWEEN',
    'ONLY','BECAUSE','DOES','MOST','SUCH','OUR','OVER','JUST','LIKE','EVERY','GREAT',
    'THINGS','SHOULD','WORLD','LIFE','STILL','GOOD','GIVE','MAN','FIRST','EVEN','NEW',
    'BECAUSE','TAKE','PEOPLE','VERY','LONG','OWN','JUST','OLD','THINK','TELL','HELP',
    'ASK','AWAY','HAND','HIGH','KEEP','LAST','LET','MIGHT','NAME','NEVER','NEXT','SAME',
    'ANOTHER','BEGAN','WHILE','OFTEN','RUN','SMALL','PART','NEED','HOUSE','UNDER',
    'WORD','WORK','YEAR','BACK','MUCH','GO','RIGHT','LOOK','SHE','HE','WHERE','HERE',
    'LOSS','DEATH','BORN','EARTH','LIGHT','DARK','SPIRIT','SOUL','MIND','BODY','EYE',
    'SEE','HEAR','SPEAK','VOICE','MASTER','STUDENT','KOAN','PARABLE','INSTAR'}

def english_score(text):
    """Score text for English-ness using word matching."""
    words = text.replace('-',' ').replace('.',' ').split()
    score = 0
    for w in words:
        if w in COMMON_WORDS:
            score += len(w) * 3
        elif len(w) >= 3:
            # Partial: check if common words appear as substrings
            for cw in COMMON_WORDS:
                if len(cw) >= 3 and cw in text:
                    score += 1
                    break
    return score

def english_word_count(text):
    """Count English words found in text."""
    found = set()
    for w in COMMON_WORDS:
        if len(w) >= 3 and w in text:
            found.add(w)
    return found

# ===== CIPHER IMPLEMENTATIONS =====

def vigenere_sub(cipher, key):
    return [(c - k) % 29 for c, k in zip(cipher, key * (len(cipher) // len(key) + 1))]

def vigenere_add(cipher, key):
    return [(c + k) % 29 for c, k in zip(cipher, key * (len(cipher) // len(key) + 1))]

def beaufort(cipher, key):
    return [(k - c) % 29 for c, k in zip(cipher, key * (len(cipher) // len(key) + 1))]

def caesar(cipher, shift):
    return [(c + shift) % 29 for c in cipher]

def affine_decrypt(cipher, a, b):
    """Affine cipher: E(x) = ax+b mod 29, D(y) = a_inv*(y-b) mod 29"""
    a_inv = pow(a, -1, 29)
    return [(a_inv * (c - b)) % 29 for c in cipher]

def multiplicative_decrypt(cipher, a):
    """Multiplicative cipher: E(x) = ax mod 29"""
    a_inv = pow(a, -1, 29)
    return [(a_inv * c) % 29 for c in cipher]

def porta_decrypt(cipher, key):
    """Porta cipher adapted for mod 29 alphabet."""
    result = []
    klen = len(key)
    for i, c in enumerate(cipher):
        k = key[i % klen]
        half = 29 // 2  # 14
        shift = k // 2
        if c < half:
            p = (c - shift) % half + half
        else:
            p = (c - half + shift) % half
        result.append(p)
    return result

def autokey_decrypt_beaufort(cipher, primer):
    """Beaufort autokey: key = primer + plaintext"""
    result = []
    key_stream = list(primer)
    for i, c in enumerate(cipher):
        k = key_stream[i] if i < len(key_stream) else result[i - len(primer)]
        p = (k - c) % 29
        result.append(p)
        if i >= len(key_stream) - 1 and len(key_stream) <= i + 1:
            key_stream.append(p)
    return result

def autokey_decrypt_sub(cipher, primer):
    """Vigenere autokey SUB: key = primer + plaintext"""
    result = []
    key_stream = list(primer)
    for i, c in enumerate(cipher):
        if i < len(key_stream):
            k = key_stream[i]
        else:
            k = result[i - len(primer)]
        p = (c - k) % 29
        result.append(p)
    return result

def autokey_decrypt_add(cipher, primer):
    """Vigenere autokey ADD: key = primer + plaintext"""
    result = []
    key_stream = list(primer)
    for i, c in enumerate(cipher):
        if i < len(key_stream):
            k = key_stream[i]
        else:
            k = result[i - len(primer)]
        p = (c + k) % 29
        result.append(p)
    return result

def cumulative_decrypt(cipher, mode='sub'):
    """Running cumulative cipher: each ciphertext depends on previous."""
    result = [cipher[0]]
    for i in range(1, len(cipher)):
        if mode == 'sub':
            result.append((cipher[i] - cipher[i-1]) % 29)
        elif mode == 'add':
            result.append((cipher[i] + cipher[i-1]) % 29)
        elif mode == 'xor':
            result.append(cipher[i] ^ cipher[i-1])
    return result

def running_sum_decrypt(cipher):
    """Decrypt assuming cipher[i] = (plain[i] + sum(plain[0..i-1])) mod 29"""
    result = [cipher[0]]
    running = cipher[0]
    for i in range(1, len(cipher)):
        p = (cipher[i] - running) % 29
        result.append(p)
        running = (running + p) % 29
    return result

def fskip_vigenere(cipher, key, mode='sub', skip_val=0):
    """Vigenere with F-skip: when plaintext = skip_val, key doesn't advance."""
    result = []
    ki = 0
    klen = len(key)
    for c in cipher:
        k = key[ki % klen]
        if mode == 'sub':
            p = (c - k) % 29
        elif mode == 'add':
            p = (c + k) % 29
        else:  # beaufort
            p = (k - c) % 29
        result.append(p)
        if p != skip_val:
            ki += 1
    return result

def totient_decrypt(cipher, offset=0, mode='sub'):
    """Totient stream cipher as used on P55/P73."""
    def nth_prime(n):
        primes = []
        candidate = 2
        while len(primes) <= n:
            if all(candidate % p != 0 for p in primes):
                primes.append(candidate)
            candidate += 1
        return primes[n]
    
    result = []
    ki = offset
    for c in cipher:
        p_val = nth_prime(ki)
        tot = p_val - 1  # phi(prime) = prime - 1
        k = tot % 29
        if mode == 'sub':
            p = (c - k) % 29
        elif mode == 'add':
            p = (c + k) % 29
        else:
            p = (k - c) % 29
        result.append(p)
        if p != 0:  # F-skip
            ki += 1
    return result

# ===== KEYWORD ENCODING =====
def keyword_to_indices(word):
    """Convert a keyword string to GP indices."""
    indices = []
    i = 0
    word = word.upper()
    while i < len(word):
        # Check digraphs first
        if i + 2 <= len(word):
            digraph = word[i:i+2]
            if digraph == 'TH':
                indices.append(2); i += 2; continue
            elif digraph == 'EO':
                indices.append(12); i += 2; continue
            elif digraph == 'NG':
                indices.append(21); i += 2; continue
            elif digraph == 'OE':
                indices.append(23); i += 2; continue
            elif digraph == 'EA':
                indices.append(25); i += 2; continue
            elif digraph == 'IA':
                indices.append(26); i += 2; continue
            elif digraph == 'AE':
                indices.append(27); i += 2; continue
        if i + 1 <= len(word):
            ch = word[i]
            mapping = {'F':0,'U':1,'O':3,'R':4,'C':5,'G':6,'W':7,'H':8,'N':9,
                       'I':10,'J':11,'P':13,'X':14,'S':15,'T':16,'B':17,'E':18,
                       'M':19,'L':20,'D':22,'A':24,'Y':28}
            if ch in mapping:
                indices.append(mapping[ch])
            i += 1
    return indices

# ===== MAIN ANALYSIS =====

RESULTS_FILE = 'session3_results.txt'

def log(msg):
    print(msg)
    with open(RESULTS_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

def main():
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        f.write("=== SESSION 3 FRESH ATTACK - Feb 25, 2026 ===\n\n")
    
    # Load all unsolved pages
    unsolved = {}
    for pn in list(range(2, 3)) + list(range(18, 55)):
        text, indices = load_page(pn)
        if indices and len(indices) > 5:
            unsolved[pn] = indices
            log(f"P{pn:02d}: {len(indices)} runes, IoC*29={ioc_29(indices):.4f}")
    
    log(f"\nLoaded {len(unsolved)} unsolved pages\n")
    
    # ===== PHASE 1: AFFINE CIPHER =====
    log("=" * 60)
    log("PHASE 1: AFFINE CIPHER (ax+b mod 29)")
    log("=" * 60)
    
    # a must be coprime to 29. Since 29 is prime, all a in 1..28 work.
    best_affine = {}
    for pn, cipher in unsolved.items():
        best_score = 0
        best_params = None
        for a in range(1, 29):
            for b in range(29):
                dec = affine_decrypt(cipher, a, b)
                ic = ioc_29(dec)
                if ic > 1.5 and len(cipher) > 30:
                    text = indices_to_latin(dec)
                    words = english_word_count(text)
                    if len(words) > best_score:
                        best_score = len(words)
                        best_params = (a, b, ic, text[:80], words)
        if best_params and best_score >= 3:
            a, b, ic, preview, words = best_params
            log(f"  P{pn:02d}: a={a}, b={b}, IoC={ic:.3f}, words={best_score}: {sorted(words)[:10]}")
            log(f"    Preview: {preview}")
            best_affine[pn] = best_params
    
    if not best_affine:
        log("  No significant affine results.")
    
    # ===== PHASE 2: PORTA CIPHER WITH KEYWORDS =====
    log("\n" + "=" * 60)
    log("PHASE 2: PORTA CIPHER WITH KNOWN KEYWORDS")
    log("=" * 60)
    
    keywords = {
        'DIVINITY': keyword_to_indices('DIVINITY'),
        'CABAL': keyword_to_indices('CABAL'),
        'SHADOWS': keyword_to_indices('SHADOWS'),
        'AETHEREAL': keyword_to_indices('AETHEREAL'),
        'OBSCURA': keyword_to_indices('OBSCURA'),
        'MOBIUS': keyword_to_indices('MOBIUS'),
        'MOURNFUL': keyword_to_indices('MOURNFUL'),
        'VOID': keyword_to_indices('VOID'),
        'CARNAL': keyword_to_indices('CARNAL'),
        'ANALOG': keyword_to_indices('ANALOG'),
        'FORM': keyword_to_indices('FORM'),
        'TOTIENT': keyword_to_indices('TOTIENT'),
        'PRIMES': keyword_to_indices('PRIMES'),
        'WISDOM': keyword_to_indices('WISDOM'),
        'ENCRYPT': keyword_to_indices('ENCRYPT'),
        'ENCRYPTION': keyword_to_indices('ENCRYPTION'),
        'FIRFUMFERENFE': keyword_to_indices('FIRFUMFERENFE'),
        'CICADA': keyword_to_indices('CICADA'),
        'CONSUMPTION': keyword_to_indices('CONSUMPTION'),
        'INSTAR': keyword_to_indices('INSTAR'),
        'CIRCUMFERENCE': keyword_to_indices('CIRCUMFERENCE'),
        'PILGRIM': keyword_to_indices('PILGRIM'),
        'SACRED': keyword_to_indices('SACRED'),
    }
    
    for kw_name, key in keywords.items():
        if not key:
            continue
        for pn, cipher in unsolved.items():
            dec = porta_decrypt(cipher, key)
            ic = ioc_29(dec)
            if ic > 1.5 and len(cipher) > 30:
                text = indices_to_latin(dec)
                words = english_word_count(text)
                if len(words) >= 3:
                    log(f"  P{pn:02d} + PORTA({kw_name}): IoC={ic:.3f}, words={len(words)}: {sorted(words)[:8]}")
                    log(f"    {text[:80]}")

    # ===== PHASE 3: CUMULATIVE/RUNNING CIPHERS =====
    log("\n" + "=" * 60)
    log("PHASE 3: CUMULATIVE/RUNNING CIPHERS")
    log("=" * 60)
    
    for pn, cipher in unsolved.items():
        for mode_name, func in [
            ('diff_sub', lambda c: cumulative_decrypt(c, 'sub')),
            ('diff_add', lambda c: cumulative_decrypt(c, 'add')),
            ('running_sum', running_sum_decrypt),
            ('double_diff', lambda c: cumulative_decrypt(cumulative_decrypt(c, 'sub'), 'sub')),
        ]:
            dec = func(cipher)
            dec_mod = [x % 29 for x in dec]
            ic = ioc_29(dec_mod)
            if ic > 1.4 and len(cipher) > 30:
                text = indices_to_latin(dec_mod)
                words = english_word_count(text)
                if len(words) >= 3:
                    log(f"  P{pn:02d} {mode_name}: IoC={ic:.3f}, words={len(words)}: {sorted(words)[:8]}")
                    log(f"    {text[:80]}")
    
    # Also try with Caesar pre-shift
    for pn, cipher in unsolved.items():
        for shift in range(29):
            shifted = caesar(cipher, shift)
            dec = cumulative_decrypt(shifted, 'sub')
            dec_mod = [x % 29 for x in dec]
            ic = ioc_29(dec_mod)
            if ic > 1.6 and len(cipher) > 30:
                text = indices_to_latin(dec_mod)
                words = english_word_count(text)
                if len(words) >= 4:
                    log(f"  P{pn:02d} Caesar({shift})+diff: IoC={ic:.3f}, words={len(words)}")
                    log(f"    {text[:80]}")
    
    # ===== PHASE 4: AUTOKEY WITH ALL KEYWORDS =====
    log("\n" + "=" * 60)
    log("PHASE 4: AUTOKEY CIPHER (Beaufort/Sub/Add) WITH KEYWORDS")
    log("=" * 60)
    
    for kw_name, key in keywords.items():
        if not key:
            continue
        for pn, cipher in unsolved.items():
            if len(cipher) < 20:
                continue
            for mode_name, func in [
                ('autokey_beaufort', lambda c, k: autokey_decrypt_beaufort(c, k)),
                ('autokey_sub', lambda c, k: autokey_decrypt_sub(c, k)),
                ('autokey_add', lambda c, k: autokey_decrypt_add(c, k)),
            ]:
                try:
                    dec = func(cipher, key)
                    ic = ioc_29(dec)
                    if ic > 1.5 and len(cipher) > 30:
                        text = indices_to_latin(dec)
                        words = english_word_count(text)
                        if len(words) >= 4:
                            log(f"  P{pn:02d} {kw_name}/{mode_name}: IoC={ic:.3f}, words={len(words)}")
                            log(f"    {text[:100]}")
                except:
                    pass
    
    # ===== PHASE 5: F-SKIP VIGENERE ON ALL UNSOLVED =====
    log("\n" + "=" * 60)
    log("PHASE 5: F-SKIP VIGENERE (all keywords, offsets 0-7, skip vals 0-3)")
    log("=" * 60)
    
    for kw_name, key in keywords.items():
        if not key:
            continue
        for pn, cipher in unsolved.items():
            if len(cipher) < 20:
                continue
            for offset in range(min(len(key), 8)):
                shifted_key = key[offset:] + key[:offset]
                for skip_val in range(4):  # F=0, U=1, TH=2, O=3
                    for mode in ['sub', 'add', 'beaufort']:
                        dec = fskip_vigenere(cipher, shifted_key, mode, skip_val)
                        ic = ioc_29(dec)
                        if ic > 1.5 and len(cipher) > 30:
                            text = indices_to_latin(dec)
                            words = english_word_count(text)
                            if len(words) >= 5:
                                log(f"  P{pn:02d} FSKIP {kw_name}/{mode}/off={offset}/skip={skip_val}: IoC={ic:.3f}, words={len(words)}")
                                log(f"    {text[:100]}")
    
    # ===== PHASE 6: MULTIPLICATIVE CIPHER =====
    log("\n" + "=" * 60)
    log("PHASE 6: MULTIPLICATIVE CIPHER (ax mod 29)")
    log("=" * 60)
    
    for pn, cipher in unsolved.items():
        for a in range(1, 29):
            dec = multiplicative_decrypt(cipher, a)
            ic = ioc_29(dec)
            if ic > 1.5 and len(cipher) > 30:
                text = indices_to_latin(dec)
                words = english_word_count(text)
                if len(words) >= 3:
                    log(f"  P{pn:02d} mult a={a}: IoC={ic:.3f}, words={len(words)}: {sorted(words)[:8]}")
    
    # ===== PHASE 7: BOUSTROPHEDON AND SPIRAL READING =====
    log("\n" + "=" * 60)
    log("PHASE 7: ALTERNATIVE READING ORDERS")
    log("=" * 60)
    
    for pn, cipher in unsolved.items():
        n = len(cipher)
        
        # Boustrophedon (serpentine) with various widths
        for width in [5, 7, 11, 13, 17, 19, 23, 29]:
            if width >= n:
                continue
            rows = []
            for i in range(0, n, width):
                row = cipher[i:i+width]
                rows.append(row)
            # Reverse every other row
            reordered = []
            for ri, row in enumerate(rows):
                if ri % 2 == 1:
                    reordered.extend(reversed(row))
                else:
                    reordered.extend(row)
            
            ic = ioc_29(reordered)
            # Try Caesar on reordered
            for shift in range(29):
                dec = caesar(reordered, shift)
                text = indices_to_latin(dec)
                words = english_word_count(text)
                if len(words) >= 5:
                    log(f"  P{pn:02d} boustrophedon w={width} shift={shift}: words={len(words)}: {sorted(words)[:8]}")
                    log(f"    {text[:100]}")
        
        # Columnar reading
        for width in [5, 7, 11, 13, 17, 19, 23, 29]:
            if width >= n:
                continue
            cols = [[] for _ in range(width)]
            for i, v in enumerate(cipher):
                cols[i % width].append(v)
            reordered = []
            for col in cols:
                reordered.extend(col)
            
            for shift in range(29):
                dec = caesar(reordered, shift)
                text = indices_to_latin(dec)
                words = english_word_count(text)
                if len(words) >= 5:
                    log(f"  P{pn:02d} columnar w={width} shift={shift}: words={len(words)}: {sorted(words)[:8]}")
                    log(f"    {text[:100]}")
    
    # ===== PHASE 8: CROSS-PAGE KEYING =====
    log("\n" + "=" * 60)
    log("PHASE 8: CROSS-PAGE KEYING (page N keys page N+1)")
    log("=" * 60)
    
    # Load solved pages' plaintext indices
    solved_indices = {}
    for pn in range(0, 75):
        text, indices = load_page(pn)
        if indices and len(indices) > 5:
            # For solved pages, try to load decoded.txt
            dec_path = os.path.join('LiberPrimus', 'pages', f'page_{pn:02d}', 'decoded.txt')
            if os.path.exists(dec_path):
                with open(dec_path, 'r', encoding='utf-8') as f:
                    dec_text = f.read().strip().upper()
                dec_indices = []
                j = 0
                while j < len(dec_text):
                    found = False
                    if j + 2 <= len(dec_text):
                        digraph = dec_text[j:j+2]
                        for idx, lat in enumerate(GP_LATIN):
                            if lat == digraph and len(lat) == 2:
                                dec_indices.append(idx)
                                j += 2
                                found = True
                                break
                    if not found:
                        ch = dec_text[j]
                        for idx, lat in enumerate(GP_LATIN):
                            if lat == ch and len(lat) == 1:
                                dec_indices.append(idx)
                                found = True
                                break
                        j += 1
                if dec_indices:
                    solved_indices[pn] = dec_indices
    
    # Try using adjacent solved page as running key
    for pn, cipher in unsolved.items():
        # Check pages nearby
        for key_pn in [pn - 1, pn + 1, pn - 2, pn + 2]:
            if key_pn in solved_indices:
                key = solved_indices[key_pn]
                if len(key) < 10:
                    continue
                for mode in ['sub', 'add', 'beaufort']:
                    extended_key = key * (len(cipher) // len(key) + 1)
                    if mode == 'sub':
                        dec = [(c - k) % 29 for c, k in zip(cipher, extended_key)]
                    elif mode == 'add':
                        dec = [(c + k) % 29 for c, k in zip(cipher, extended_key)]
                    else:
                        dec = [(k - c) % 29 for c, k in zip(cipher, extended_key)]
                    ic = ioc_29(dec)
                    if ic > 1.4:
                        text = indices_to_latin(dec)
                        words = english_word_count(text)
                        if len(words) >= 4:
                            log(f"  P{pn:02d} keyed by P{key_pn:02d}/{mode}: IoC={ic:.3f}, words={len(words)}")
                            log(f"    {text[:100]}")
    
    # ===== PHASE 9: P02 FOCUSED ATTACK =====
    log("\n" + "=" * 60)
    log("PHASE 9: P02 FOCUSED ATTACK")
    log("=" * 60)
    
    if 2 in unsolved:
        cipher = unsolved[2]
        log(f"  P02: {len(cipher)} runes")
        
        # Try all simple methods
        for shift in range(29):
            dec = caesar(cipher, shift)
            text = indices_to_latin(dec)
            words = english_word_count(text)
            if len(words) >= 2:
                log(f"  Caesar {shift}: IoC={ioc_29(dec):.3f}, words={len(words)}: {text[:80]}")
        
        # Reverse + Caesar
        rev = list(reversed(cipher))
        for shift in range(29):
            dec = caesar(rev, shift)
            text = indices_to_latin(dec)
            words = english_word_count(text)
            if len(words) >= 2:
                log(f"  Rev+Caesar {shift}: IoC={ioc_29(dec):.3f}, words={len(words)}: {text[:80]}")
        
        # Atbash
        dec = [(28 - c) % 29 for c in cipher]
        text = indices_to_latin(dec)
        log(f"  Atbash: {text[:80]}")
        
        # Atbash + Caesar
        for shift in range(29):
            dec2 = caesar(dec, shift)
            text2 = indices_to_latin(dec2)
            words = english_word_count(text2)
            if len(words) >= 2:
                log(f"  Atbash+Caesar {shift}: words={len(words)}: {text2[:80]}")
        
        # Try all keywords
        for kw_name, key in keywords.items():
            if not key:
                continue
            for mode_name, func in [('sub', vigenere_sub), ('add', vigenere_add), ('beau', beaufort)]:
                dec = func(cipher, key)
                ic = ioc_29(dec)
                text = indices_to_latin(dec)
                words = english_word_count(text)
                if len(words) >= 2:
                    log(f"  P02 {kw_name}/{mode_name}: IoC={ic:.3f}, words={len(words)}: {text[:80]}")
    
    # ===== PHASE 10: TOTIENT WITH EXTENDED OFFSETS =====
    log("\n" + "=" * 60)
    log("PHASE 10: TOTIENT CIPHER (offsets 0-2000) ON SMALLEST PAGES")
    log("=" * 60)
    
    # Focus on smallest unsolved pages
    small_pages = sorted([(len(v), pn, v) for pn, v in unsolved.items()])[:8]
    
    for length, pn, cipher in small_pages:
        log(f"\n  Testing P{pn:02d} ({length} runes)...")
        best_ic = 0
        best_params = None
        for offset in range(2000):
            for mode in ['sub', 'add', 'beaufort']:
                try:
                    dec = totient_decrypt(cipher, offset, mode)
                    ic = ioc_29(dec)
                    if ic > best_ic:
                        best_ic = ic
                        best_params = (offset, mode, ic, dec)
                except:
                    pass
        if best_params:
            offset, mode, ic, dec = best_params
            text = indices_to_latin(dec)
            words = english_word_count(text)
            log(f"  P{pn:02d} best totient: offset={offset}, mode={mode}, IoC={ic:.3f}, words={len(words)}")
            log(f"    {text[:100]}")
    
    log("\n\n=== SESSION 3 COMPLETE ===")

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/..')
    main()
