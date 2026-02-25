#!/usr/bin/env python3
"""
Targeted attack on P02 and small unsolved pages.
Also tests Gromark cipher, running difference with key, and chain ciphers.
"""

import os, sys
from collections import Counter

# GP mapping with J fix
GP_RUNES = list("ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛞᛟᛡᛠᚪᚫᚣ")
GP_LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','D','OE','A','EA','IA','AE','Y']
GP_RUNE_TO_IDX = {r: i for i, r in enumerate(GP_RUNES)}

def runes_to_indices(text):
    return [GP_RUNE_TO_IDX[ch] for ch in text if ch in GP_RUNE_TO_IDX]

def indices_to_latin(indices):
    return ''.join(GP_LATIN[i] for i in indices)

def load_page(pn):
    path = os.path.join('LiberPrimus', 'pages', f'page_{pn:02d}', 'runes.txt')
    if not os.path.exists(path):
        return None, None
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    return text, runes_to_indices(text)

def ioc29(indices):
    if len(indices) < 2: return 0
    c = Counter(indices)
    n = len(indices)
    return 29 * sum(v*(v-1) for v in c.values()) / (n*(n-1))

ENGLISH_3 = {'THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','HER','WAS','ONE','OUR','OUT','HAS','HIS','HOW','MAN','NEW','NOW','OLD','SEE','TWO','WAY','WHO','BOY','DID','GET','HIM','LET','SAY','SHE','TOO','USE'}
ENGLISH_4 = {'THAT','WITH','HAVE','THIS','WILL','YOUR','FROM','THEY','BEEN','CALL','COME','EACH','FIND','GOOD','INTO','JUST','KNOW','LIKE','LONG','LOOK','MAKE','MANY','MOST','MUCH','MUST','NAME','ONLY','OVER','PART','SAID','SOME','THAN','THEM','THEN','WHEN','WHAT','WORK','YEAR','ALSO','BACK','EVEN','GIVE','HELP','HERE','HIGH','HOME','KEEP','LAST','LIFE','LIVE','SELF','SUCH','TAKE','TELL','VERY','WANT','WENT','WERE','WORD','SHALL','BEING','DEATH','TRUTH','LIGHT','WORLD','THING','FIRST','THESE','THOSE','GREAT','EVERY','STILL','NEVER'}
ENGLISH_5 = {'ABOUT','AFTER','AGAIN','BEING','COULD','EVERY','FIRST','GREAT','THEIR','THERE','THESE','THING','THINK','THOSE','THREE','UNDER','WATER','WHERE','WHICH','WHILE','WORLD','WOULD','SHALL','EARTH','DEATH','LIGHT','TRUTH','FOUND','NEVER','OTHER','TODAY','STILL','SMALL','RIGHT','HOUSE','LARGE','PLACE','YOUNG','MIGHT','NIGHT','ALONG','HEART','CHILD','STAND','GIVEN','POWER','POINT'}
ALL_WORDS = ENGLISH_3 | ENGLISH_4 | ENGLISH_5

def score_text(text):
    """Score by finding English words in the text."""
    found = set()
    for w in ALL_WORDS:
        if w in text:
            found.add(w)
    return len(found), found

os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/..')
OUT = open('p02_targeted_results.txt', 'w', encoding='utf-8')

def log(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', 'replace').decode())
    OUT.write(msg + '\n')
    OUT.flush()

# ===== P02 ANALYSIS =====
raw_text, p02 = load_page(2)
log(f"P02: {len(p02)} runes, IoC*29={ioc29(p02):.4f}")
log(f"Raw text lines:")
for line in raw_text.strip().split('\n'):
    log(f"  {line}")

# Separate by delimiters
words_in_runes = []
current = []
for ch in raw_text:
    if ch in GP_RUNE_TO_IDX:
        current.append(GP_RUNE_TO_IDX[ch])
    elif ch in '-. \n':
        if current:
            words_in_runes.append(current)
            current = []
if current:
    words_in_runes.append(current)

log(f"\nP02 has {len(words_in_runes)} rune-words, lengths: {[len(w) for w in words_in_runes]}")

# ===== Test 1: Direct gematria (Caesar 0) =====
log("\n=== P02 Direct Gematria ===")
text = indices_to_latin(p02)
log(f"  {text}")

# ===== Test 2: All Caesar shifts =====
log("\n=== P02 All Caesar Shifts ===")
for shift in range(29):
    dec = [(v + shift) % 29 for v in p02]
    text = indices_to_latin(dec)
    sc, words = score_text(text)
    if sc >= 3:
        log(f"  shift={shift}: [{sc} words] {text[:120]}")
        log(f"    Words: {sorted(words)}")

# ===== Test 3: Reversed + Caesar =====
log("\n=== P02 Reversed + Caesar ===")
rev = list(reversed(p02))
for shift in range(29):
    dec = [(v + shift) % 29 for v in rev]
    text = indices_to_latin(dec)
    sc, words = score_text(text)
    if sc >= 3:
        log(f"  rev+shift={shift}: [{sc} words] {text[:120]}")

# ===== Test 4: Atbash variants =====
log("\n=== P02 Atbash + Caesar ===")
for shift in range(29):
    dec = [(28 - v + shift) % 29 for v in p02]
    text = indices_to_latin(dec)
    sc, words = score_text(text)
    if sc >= 3:
        log(f"  atbash+{shift}: [{sc} words] {text[:120]}")

# ===== Test 5: Word-level reversal =====
log("\n=== P02 Word-Level Reversal ===")
for shift in range(29):
    # Reverse order of words
    reversed_words = list(reversed(words_in_runes))
    all_indices = []
    for w in reversed_words:
        all_indices.extend(w)
    dec = [(v + shift) % 29 for v in all_indices]
    text = indices_to_latin(dec)
    sc, words = score_text(text)
    if sc >= 3:
        log(f"  word-rev+shift={shift}: [{sc} words] {text[:120]}")

# ===== Test 6: Keyword from P01 =====
log("\n=== P02 Keyword Vigenere ===")
def keyword_to_idx(word):
    indices = []
    i = 0
    w = word.upper()
    while i < len(w):
        if i+2 <= len(w):
            d = w[i:i+2]
            if d == 'TH': indices.append(2); i += 2; continue
            elif d == 'EO': indices.append(12); i += 2; continue
            elif d == 'NG': indices.append(21); i += 2; continue
            elif d == 'OE': indices.append(23); i += 2; continue
            elif d == 'EA': indices.append(25); i += 2; continue
            elif d == 'IA': indices.append(26); i += 2; continue
            elif d == 'AE': indices.append(27); i += 2; continue
        ch = w[i]
        m = {'F':0,'U':1,'O':3,'R':4,'C':5,'G':6,'W':7,'H':8,'N':9,'I':10,'J':11,'P':13,'X':14,'S':15,'T':16,'B':17,'E':18,'M':19,'L':20,'D':22,'A':24,'Y':28}
        if ch in m:
            indices.append(m[ch])
        i += 1
    return indices

keywords_all = ['DIVINITY','CABAL','SHADOWS','AETHEREAL','OBSCURA','MOBIUS','MOURNFUL',
    'VOID','CARNAL','ANALOG','FORM','TOTIENT','PRIMES','WISDOM','ENCRYPT','ENCRYPTION',
    'FIRFUMFERENFE','CICADA','CONSUMPTION','INSTAR','CIRCUMFERENCE','PILGRIM','SACRED',
    'WELCOME','WARNING','KOAN','PARABLE','BELIEVE','QUESTION','INSTRUCTION',
    'YAHEOOPYJ','LIBER','PRIMUS','INTUS']

for kw in keywords_all:
    key = keyword_to_idx(kw)
    if not key: continue
    for mode in ['sub', 'add', 'beau']:
        for offset in range(len(key)):
            shifted = key[offset:] + key[:offset]
            ext = shifted * (len(p02) // len(shifted) + 1)
            if mode == 'sub':
                dec = [(c - k) % 29 for c, k in zip(p02, ext)]
            elif mode == 'add':
                dec = [(c + k) % 29 for c, k in zip(p02, ext)]
            else:
                dec = [(k - c) % 29 for c, k in zip(p02, ext)]
            ic = ioc29(dec)
            text = indices_to_latin(dec)
            sc, words = score_text(text)
            if sc >= 5 or ic > 1.5:
                log(f"  {kw}/{mode}/off={offset}: IoC={ic:.3f}, words={sc}: {text[:100]}")

# ===== Test 7: P02 word lengths as key =====
log("\n=== P02 Rune-Word Analysis ===")
for shift in range(29):
    dec_words = []
    for w in words_in_runes:
        dec_w = [(v + shift) % 29 for v in w]
        dec_words.append(indices_to_latin(dec_w))
    
    matched = 0
    for dw in dec_words:
        if dw in ALL_WORDS:
            matched += 1
    if matched >= 2:
        log(f"  shift={shift}: {matched} word matches: {dec_words}")

# ===== Test 8: P02 as periodic key search =====
log("\n=== P02 Periodic IoC Scan (periods 2-50) ===")
best_periods = []
for period in range(2, min(51, len(p02)//3)):
    cols = [[] for _ in range(period)]
    for i, v in enumerate(p02):
        cols[i % period].append(v)
    avg_ic = sum(ioc29(c) for c in cols if len(c) > 2) / period
    if avg_ic > 1.3:
        best_periods.append((avg_ic, period))
        log(f"  period={period}: col_IoC={avg_ic:.3f}")

if best_periods:
    best_periods.sort(reverse=True)
    log(f"  Top periods: {[(p, round(ic, 3)) for ic, p in best_periods[:5]]}")

# ===== Test 9: Try the page as a title =====
log("\n=== P02 First/Last word analysis ===")
if words_in_runes:
    fw = words_in_runes[0]
    log(f"  First word ({len(fw)} runes):")
    for shift in range(29):
        dec = [(v + shift) % 29 for v in fw]
        text = indices_to_latin(dec)
        log(f"    shift={shift}: {text}")
    
    lw = words_in_runes[-1]
    if len(words_in_runes) > 1:
        log(f"  Last word ({len(lw)} runes):")
        for shift in range(29):
            dec = [(v + shift) % 29 for v in lw]
            text = indices_to_latin(dec)
            log(f"    shift={shift}: {text}")

# ===== SMALL PAGE ATTACKS: P49, P52, P54 =====
log("\n\n" + "="*60)
log("SMALL PAGE ATTACKS: P49, P52, P54")
log("="*60)

for pn in [49, 52, 54]:
    raw, indices = load_page(pn)
    if not indices: continue
    log(f"\n--- P{pn}: {len(indices)} runes ---")
    
    # Full keyword scan with Fskip
    for kw in keywords_all:
        key = keyword_to_idx(kw)
        if not key: continue
        for mode in ['sub', 'add', 'beau']:
            for offset in range(len(key)):
                shifted = key[offset:] + key[:offset]
                # Standard Vigenere
                ext = shifted * (len(indices) // len(shifted) + 1)
                if mode == 'sub':
                    dec = [(c - k) % 29 for c, k in zip(indices, ext)]
                elif mode == 'add':
                    dec = [(c + k) % 29 for c, k in zip(indices, ext)]
                else:
                    dec = [(k - c) % 29 for c, k in zip(indices, ext)]
                ic = ioc29(dec)
                text = indices_to_latin(dec)
                sc, words = score_text(text)
                if sc >= 4 or (ic > 1.6 and len(indices) > 50):
                    log(f"  {kw}/{mode}/off={offset}: IoC={ic:.3f}, words={sc}: {text[:80]}")
                    if words:
                        log(f"    Words: {sorted(words)}")
                
                # F-skip Vigenere
                dec2 = []
                ki = 0
                for c in indices:
                    k = shifted[ki % len(shifted)]
                    if mode == 'sub':
                        p = (c - k) % 29
                    elif mode == 'add':
                        p = (c + k) % 29
                    else:
                        p = (k - c) % 29
                    dec2.append(p)
                    if p != 0:  # F-skip
                        ki += 1
                ic2 = ioc29(dec2)
                text2 = indices_to_latin(dec2)
                sc2, words2 = score_text(text2)
                if sc2 >= 4 or (ic2 > 1.6 and len(indices) > 50):
                    log(f"  FSKIP {kw}/{mode}/off={offset}: IoC={ic2:.3f}, words={sc2}: {text2[:80]}")

# ===== GROMARK CIPHER TEST =====
log("\n\n" + "="*60)
log("GROMARK CIPHER TEST ON SMALL PAGES")
log("="*60)

def gromark_decrypt(cipher, key_seed, alphabet_size=29):
    """Gromark: running key generated from numeric digits of plaintext."""
    result = []
    running_key = list(key_seed)
    for i, c in enumerate(cipher):
        k = running_key[i] if i < len(running_key) else (running_key[-2] + running_key[-1]) % alphabet_size
        p = (c - k) % alphabet_size
        result.append(p)
        running_key.append(p)
    return result

for pn in [2, 49, 52, 54, 22]:
    raw, indices = load_page(pn)
    if not indices or len(indices) < 20: continue
    log(f"\n--- P{pn} Gromark ({len(indices)} runes) ---")
    
    best_sc = 0
    best_result = None
    
    # Try all 2-element seeds
    for s0 in range(29):
        for s1 in range(29):
            dec = gromark_decrypt(indices, [s0, s1])
            text = indices_to_latin(dec)
            sc, words = score_text(text)
            if sc > best_sc:
                best_sc = sc
                best_result = (s0, s1, text[:80], words)
    
    if best_result:
        s0, s1, preview, words = best_result
        log(f"  Best seed=({s0},{s1}): {best_sc} words: {sorted(words)}")
        log(f"    {preview}")

log("\n\n=== TARGETED ATTACK COMPLETE ===")
OUT.close()
