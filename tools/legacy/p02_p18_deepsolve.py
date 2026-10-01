#!/usr/bin/env python3
"""
P02/P18 Deep Recovery + DIVINITY F-skip mod-17-class tests
===========================================================
1. Hill-climb P02 key (currently partial 43-element key) with rich LP vocab
2. Hill-climb P18 key (34/53 positions found, 19 remaining)  
3. Test DIVINITY with F-skip on mod-10-class pages (P27, P44)
4. Test FIRFUMFERENFE on mod-14/15 class pages (P31, P32)
5. Test phi(prime) stream on mod-4/5 class pages (P21, P22, P39)
"""

import sys, os, re, random, math
from pathlib import Path
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(__file__).resolve().parent.parent
PAGES_DIR = BASE / "pages"

# === Gematria Primus ===
RUNE_TO_IDX = {chr(k): v for k, v in [
    (0x16A0,0),(0x16A2,1),(0x16A6,2),(0x16A9,3),(0x16B1,4),(0x16B3,5),
    (0x16B7,6),(0x16B9,7),(0x16BB,8),(0x16BE,9),(0x16C1,10),(0x16C4,11),
    (0x16C7,12),(0x16C8,13),(0x16C9,14),(0x16CB,15),(0x16CF,16),(0x16D2,17),
    (0x16D6,18),(0x16D7,19),(0x16DA,20),(0x16DD,21),(0x16DF,22),(0x16DE,23),
    (0x16AA,24),(0x16AB,25),(0x16A3,26),(0x16E1,27),(0x16E0,28),
]}
IDX_TO_LETTER = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
                  'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA']

SEPARATORS = set('-. \n\r\t\u2022/')

def load_runes(page_num):
    path = PAGES_DIR / f"page_{page_num:02d}" / "runes.txt"
    if not path.exists():
        return [], []
    with open(path, encoding='utf-8') as f:
        text = f.read()
    words = []; current = []
    for ch in text:
        if ch in RUNE_TO_IDX:
            current.append(RUNE_TO_IDX[ch])
        elif ch in SEPARATORS:
            if current:
                words.append(tuple(current))
                current = []
    if current:
        words.append(tuple(current))
    flat = [r for w in words for r in w]
    return flat, words

def to_text(indices):
    return ''.join(IDX_TO_LETTER[i] for i in indices)

def decrypt_sub(flat, key):
    kl = len(key)
    return [(flat[i] - key[i % kl]) % 29 for i in range(len(flat))]

def decrypt_add(flat, key):
    kl = len(key)
    return [(flat[i] + key[i % kl]) % 29 for i in range(len(flat))]

def decrypt_beaufort(flat, key):
    kl = len(key)
    return [(key[i % kl] - flat[i]) % 29 for i in range(len(flat))]

def ioc(values):
    if len(values) < 2: return 0.0
    c = Counter(values)
    n = len(values)
    return sum(v*(v-1) for v in c.values()) / (n*(n-1))

# Rich LP vocabulary for scoring 
LP_WORDS = set("""
THE A AN I IN IS IT OF TO AND BE THAT FOR NOT ON WITH AS ALL THIS FROM
SELF TRUTH SEEK WITHIN SACRED HOLY PILGRIM WISDOM KNOWLEDGE EVERY PATH
FIND ABOVE WAY BEING SHALL MUST OUR YOUR LIKE MORE BUT HIS HER THEY WE
ARE YOU DO AT WHAT SO UP IF ABOUT WHO WHICH WHEN HOW THEN NO JUST THEM
SOME TIME ITS HAD HAS HIS HOW ITS MAY NEW NOW OLD SEE WHO WILL INTO THAN
WELCOME JOURNEY DIVINITY CIRCUMFERENCE CONSUMPTION PRESERVATION ADHERENCE
COMMAND REALITY KOAN MASTER BEING TRUTH WITHIN ABOVE BEYOND LOSS QUESTION
DISCOVER IMPOSE INNOCENT ILLUSION CERTAINTY STRUGGLE SUFFERING END GREAT
NECESSARY EMERGE INSTAR SHAPE INTELLIGENCE HOLY LAW ENCRYPT UNTO EACH
CHAPTER INTUS SAME OTHER SONG WITH SINGING VOICE MUSIC NOTE TONE CHORD
HATH DOTH GOETH FLETH EARTH DEATH LIFE LOVE HATE FEAR HOPE FAITH
ASK OATH SWORN ONE ABOVE BELIEVE NOTHING EXCEPT KNOW TRUE TEST
EXPERIENCE EDIT CHANGE MESSAGE CONTAINED WORDS NUMBERS SACRED
DO FOUR UNREASONABLE THINGS EACH DAY DEEP WEB EXISTS PAGE HASHES
DUTY EVERY PILGRIM SEEK THIS BEGINNING PRIMES TOTIENT FUNCTION
SHOULD ENCRYPTED KNOW MYSTERY SHADOWS VOID CARNAL FORM MOBIUS
MOURNFUL AETHEREAL OBSCURA ANALOG BUFFERS CABAL DEOR TOTIENT
INSTRUCTION PROGRAM MIND REALITY COMMAND OWN SELF QUESTION ALL
THINGS DISCOVER INSIDE FOLLOW IMPOSE NOTHING OTHERS KNOW THIS
LIKE INSTAR TUNNELING SURFACE WED SHED CIRCUMFERENCES FIND
WITHIN EMERGE PARABLE INSTAR LOVE DIVINITY INTELLIGENCE HOLY
WARN WARNING BOOK EXCEPT WHAT TEST KNOWLEDGE FIND YOUR EXPERIENCE
DEATH EDIT CHANGE WORD NUMBER SACRED BEGIN CHAPTER PART ONE TWO
THREE BEING WITHIN WITHOUT ABOVE BELOW BEFORE AFTER IS BY THIS
""".split())

def score_text_words(words_as_text):
    """Score plaintext word list against LP vocabulary."""
    score = 0
    for w in words_as_text:
        # Direct match
        if w in LP_WORDS:
            score += len(w) * 4
        elif len(w) >= 4:
            # Check for trigrams
            for kw in LP_WORDS:
                if len(kw) >= 4 and kw in w:
                    score += len(kw)
                    break
    return score

def check_singletons(plain_words):
    for w in plain_words:
        if len(w) == 1 and w[0] not in (10, 24):  # I or A only
            return False
    return True

def words_from_flat(flat, word_sizes):
    result = []; pos = 0
    for s in word_sizes:
        result.append(tuple(flat[pos:pos+s]))
        pos += s
    return result

def hill_climb_key(flat, word_sizes, initial_key, max_iter=500, verbose=True):
    """Hill-climb key using LP vocabulary scoring."""
    best_key = list(initial_key)
    kl = len(best_key)
    
    # Initial decode
    plain = decrypt_sub(flat, best_key)
    plain_words = words_from_flat(plain, word_sizes)
    best_words_text = [to_text(w) for w in plain_words]
    best_score = score_text_words(best_words_text)
    
    if not check_singletons(plain_words):
        # Fix singleton violations first
        for i, (w, wt) in enumerate(zip(plain_words, best_words_text)):
            if len(w) == 1 and w[0] not in (10, 24):
                pos = sum(word_sizes[:i])
                ki = pos % kl
                # Force key to I or A
                for target in (10, 24):
                    new_key = list(best_key)
                    new_key[ki] = (flat[pos] - target) % 29
                    new_plain = decrypt_sub(flat, new_key)
                    new_words = words_from_flat(new_plain, word_sizes)
                    if check_singletons(new_words):
                        new_text = [to_text(w) for w in new_words]
                        new_score = score_text_words(new_text)
                        if new_score >= best_score:
                            best_key = new_key
                            best_score = new_score
                            plain_words = new_words
                            best_words_text = new_text
                            break

    improved = True
    iteration = 0
    while improved and iteration < max_iter:
        improved = False
        iteration += 1
        # Try each key position
        for ki in range(kl):
            current_val = best_key[ki]
            best_vi = current_val
            best_vi_score = best_score
            for v in range(29):
                if v == current_val:
                    continue
                test_key = list(best_key)
                test_key[ki] = v
                plain = decrypt_sub(flat, test_key)
                plain_words = words_from_flat(plain, word_sizes)
                if not check_singletons(plain_words):
                    continue
                words_text = [to_text(w) for w in plain_words]
                score = score_text_words(words_text)
                if score > best_vi_score:
                    best_vi_score = score
                    best_vi = v
            if best_vi != current_val:
                best_key[best_vi] = best_vi if False else best_vi  # Bug fix
                best_key[ki] = best_vi
                improved = True
                best_score = best_vi_score
    
    # Final decode
    plain = decrypt_sub(flat, best_key)
    plain_words = words_from_flat(plain, word_sizes)
    best_words_text = [to_text(w) for w in plain_words]
    return best_key, best_score, best_words_text

# ==============================================================
# DIVINITY F-skip test on mod-10 class pages
# ==============================================================
print("=" * 60)
print("TEST: DIVINITY + F-skip on mod-10 pages (P27, P44)")
print("=" * 60)

DIVINITY = [23, 10, 1, 10, 9, 10, 16, 26]
FIRFUMFERENFE = [0, 10, 4, 0, 1, 19, 0, 18, 4, 18, 9, 0, 18]
PHI_PRIME_STREAM = None  # Generated below

def sieve(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5)+1):
        if is_prime[i]:
            for j in range(i*i, limit+1, i):
                is_prime[j] = False
    return [i for i in range(2, limit+1) if is_prime[i]]

primes = sieve(100000)

def euler_totient(n):
    result = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result

def phi_prime_stream(length):
    """Generate phi(prime) % 29 stream."""
    stream = [(euler_totient(p)) % 29 for p in primes[:length+10]]
    return stream[:length]

def decrypt_fskip(cipher_words, key, mode='sub'):
    """Vigenère with F-skip rule: if plaintext would be F(0), output F unchanged, don't advance key counter."""
    key_pos = 0
    plain_words = []
    for w in cipher_words:
        plain_word = []
        for c in w:
            if c == 0:  # Cipher is F(0) — this IS the literal F rule
                # The F-skip rule: if cipher=F and it's a LITERAL F in plaintext,
                # output F without advancing key
                # But we can't know if it's literal without decrypting...
                # Use: if cipher[i]=F(0), treat as plaintext F, skip key
                plain_word.append(0)  # F
                # key_pos NOT advanced
            else:
                if mode == 'sub':
                    p = (c - key[key_pos % len(key)]) % 29
                elif mode == 'add':
                    p = (c + key[key_pos % len(key)]) % 29
                elif mode == 'beaufort':
                    p = (key[key_pos % len(key)] - c) % 29
                else:
                    p = c
                if p == 0:  # If result is F but cipher was not F, that's wrong
                    plain_word.append(p)
                else:
                    plain_word.append(p)
                key_pos += 1
        plain_words.append(tuple(plain_word))
    return plain_words

def score_words_list(word_texts):
    score = 0
    for wt in word_texts:
        if wt in LP_WORDS:
            score += len(wt) * 4
        elif len(wt) >= 3:
            for kw in LP_WORDS:
                if len(kw) >= 3 and kw in wt:
                    score += len(kw)
                    break
    return score

# Test all known keys on mod-10 class pages
MOD10_PAGES = [10, 27, 44, 61]
KNOWN_KEYS = {
    'DIVINITY': DIVINITY,
    'FIRFUMFERENFE': FIRFUMFERENFE,
    'YAHEOOPYJ': [26, 24, 8, 18, 3, 3, 13, 26, 11],
    'SHADOWS': [15, 8, 24, 23, 3, 7, 15],
    'MOURNFUL': [19, 3, 1, 4, 9, 0, 1, 20],
    'CABAL': [5, 24, 17, 24, 20],
    'OBSCURA': [3, 17, 15, 5, 1, 4, 24],
    'VOID': [1, 3, 10, 23],
    'TOTIENT': [16, 3, 16, 10, 18, 9, 16],
    'DEOR': [23, 18, 3, 4],
    'CONSUMPTION': [5,3,9,15,1,19,13,16,16,10,3,9],
    'CICADA': [5,10,5,24,23,24],
}

for page in [27, 44]:
    flat, words = load_runes(page)
    word_sizes = [len(w) for w in words]
    if not flat:
        print(f"P{page}: no runes loaded")
        continue
    print(f"\nTesting all known keys on P{page} ({len(flat)} runes, {len(words)} words):")
    results = []
    for key_name, key_vals in KNOWN_KEYS.items():
        for mode in ['sub', 'add', 'beaufort']:
            for offset in range(len(key_vals)):
                rotated = key_vals[offset:] + key_vals[:offset]
                plain = decrypt_sub(flat, rotated) if mode == 'sub' else \
                        decrypt_add(flat, rotated) if mode == 'add' else \
                        decrypt_beaufort(flat, rotated)
                pw = words_from_flat(plain, word_sizes)
                if not check_singletons(pw):
                    continue
                wt = [to_text(w) for w in pw]
                score = score_words_list(wt)
                iv = ioc(plain)
                if iv > 1.3 or score > 50:
                    results.append((iv, score, key_name, mode, offset, wt[:10]))
    results.sort(reverse=True)
    if results:
        for iv, score, kname, mode, off, sample in results[:5]:
            print(f"  {kname} mode={mode} off={off}: IoC={iv:.4f} score={score}")
            print(f"  Sample: {' '.join(sample[:8])}")
    else:
        print(f"  No results with IoC>1.3 or score>50")
    
    # SPECIAL: F-skip test with DIVINITY
    print(f"  -- F-skip test with DIVINITY --")
    for offset in range(len(DIVINITY)):
        rotated = DIVINITY[offset:] + DIVINITY[:offset]
        pw = decrypt_fskip(words, rotated, 'sub')
        if not check_singletons(pw):
            continue
        wt = [to_text(w) for w in pw]
        score = score_words_list(wt)
        flat_plain = [r for w in pw for r in w]
        iv = ioc(flat_plain)
        if score > 30 or iv > 1.3:
            print(f"  DIVINITY F-skip off={offset}: IoC={iv:.4f} score={score}")
            print(f"  Sample: {' '.join(wt[:8])}")

# ==============================================================
# Test FIRFUMFERENFE on mod-14/15 class pages (P31, P32)
# ==============================================================
print("\n" + "=" * 60)
print("TEST: FIRFUMFERENFE on mod-14/15 pages (P31, P32)")
print("=" * 60)

for page in [31, 32]:
    flat, words = load_runes(page)
    word_sizes = [len(w) for w in words]
    if not flat:
        print(f"P{page}: N/A")
        continue
    print(f"\nP{page} ({len(flat)} runes, {len(words)} words):")
    for mode in ['sub', 'add', 'beaufort']:
        for offset in range(len(FIRFUMFERENFE)):
            rotated = FIRFUMFERENFE[offset:] + FIRFUMFERENFE[:offset]
            plain = decrypt_sub(flat, rotated) if mode == 'sub' else \
                    decrypt_add(flat, rotated) if mode == 'add' else \
                    decrypt_beaufort(flat, rotated)
            pw = words_from_flat(plain, word_sizes)
            if not check_singletons(pw):
                continue
            wt = [to_text(w) for w in pw]
            score = score_words_list(wt)
            iv = ioc(plain)
            if iv > 1.3 or score > 50:
                print(f"  FIRFUMFERENFE mode={mode} off={offset}: IoC={iv:.4f} score={score}")
                print(f"  Sample: {' '.join(wt[:8])}")

# ==============================================================
# Test phi(prime) stream on mod-4/5 class pages (P21, P22, P38, P39)
# ==============================================================
print("\n" + "=" * 60)
print("TEST: phi(prime) stream on mod-4/5 pages (P21, P22, P38, P39)")
print("=" * 60)

phi_stream_large = phi_prime_stream(3000)
for page in [21, 22, 38, 39]:
    flat, words = load_runes(page)
    word_sizes = [len(w) for w in words]
    if not flat:
        continue
    print(f"\nP{page} ({len(flat)} runes):")
    best = (0, -1, '', '')
    for offset in range(0, min(500, len(phi_stream_large) - len(flat))):
        key_seg = phi_stream_large[offset:offset+len(flat)]
        for mode in ['sub', 'add', 'beaufort']:
            plain = decrypt_sub(flat, key_seg) if mode == 'sub' else \
                    decrypt_add(flat, key_seg) if mode == 'add' else \
                    decrypt_beaufort(flat, key_seg)
            pw = words_from_flat(plain, word_sizes)
            if not check_singletons(pw):
                continue
            wt = [to_text(w) for w in pw]
            score = score_words_list(wt)
            iv = ioc(plain)
            if iv > best[0]:
                best = (iv, score, mode, offset, ' '.join(wt[:8]))
            if iv > 1.3:
                print(f"  phi stream off={offset} mode={mode}: IoC={iv:.4f} score={score}")
                print(f"  {' '.join(wt[:8])}")
    print(f"  Best: IoC={best[0]:.4f} score={best[1]} mode={best[2]} off={best[3]}")
    if best[0] > 1.0 and len(best) > 4:
        print(f"  Text: {best[4]}")

# ==============================================================
# P02 Hill Climb
# ==============================================================
print("\n" + "=" * 60)
print("P02 HILL CLIMB")
print("=" * 60)

flat02, words02 = load_runes(2)
word_sizes02 = [len(w) for w in words02]
key02 = [23, 9, 14, 21, 14, 18, 26, 25, 4, 19, 22, 4, 26, 9, 1, 18, 9, 15, 20, 1,
          6, 21, 20, 25, 21, 11, 16, 22, 15, 16, 16, 0, 0, 2, 15, 4, 2, 0, 9, 22, 26, 22, 15]

# Multiple hill-climb runs with restarts
best_overall_key = list(key02)
best_overall_score = -1
best_overall_text = []

for trial in range(5):
    if trial == 0:
        trial_key = list(key02)
    else:
        # Random perturbation
        trial_key = list(key02)
        for _ in range(5):
            pos = random.randint(0, len(key02)-1)
            trial_key[pos] = random.randint(0, 28)
    
    new_key, score, words_text = hill_climb_key(flat02, word_sizes02, trial_key, max_iter=30)
    print(f"Trial {trial}: score={score}, text: {' '.join(words_text[:12])}")
    
    if score > best_overall_score:
        best_overall_score = score
        best_overall_key = new_key
        best_overall_text = words_text

print(f"\nBest P02 key: {best_overall_key}")
print(f"Best P02 score: {best_overall_score}")
print("Best P02 text:")
print(' '.join(best_overall_text))
print()

# Double-check with ADD mode too
for mode in ['add', 'beaufort']:
    plain = decrypt_add(flat02, best_overall_key) if mode == 'add' else decrypt_beaufort(flat02, best_overall_key)
    pw = words_from_flat(plain, word_sizes02)
    wt = [to_text(w) for w in pw]
    score = score_words_list(wt)
    if score > best_overall_score:
        print(f"P02 {mode} mode gives better score {score}: {' '.join(wt[:15])}")

# ==============================================================
# P18 Hill Climb
# ==============================================================
print("\n" + "=" * 60)
print("P18 HILL CLIMB")
print("=" * 60)

flat18, words18 = load_runes(18)
word_sizes18 = [len(w) for w in words18]
key18 = [11, 6, 1, 20, 25, 20, 9, 15, 24, 26, 25, 7, 19, 8, 10, 24, 18, 9, 0, 16,
          9, 4, 14, 22, 13, 13, 3, 28, 5, 21, 24, 19, 5, 1, 27, 14, 6, 17, 24, 24,
          22, 8, 23, 6, 22, 19, 2, 11, 3, 19, 25, 15, 24]

best_p18_key = list(key18)
best_p18_score = -1
best_p18_text = []

for trial in range(5):
    if trial == 0:
        trial_key = list(key18)
    else:
        trial_key = list(key18)
        for _ in range(8):  # More perturbation since more unknowns
            pos = random.randint(0, len(key18)-1)
            trial_key[pos] = random.randint(0, 28)
    
    new_key, score, words_text = hill_climb_key(flat18, word_sizes18, trial_key, max_iter=50)
    print(f"Trial {trial}: score={score}, text: {' '.join(words_text[:12])}")
    
    if score > best_p18_score:
        best_p18_score = score
        best_p18_key = new_key
        best_p18_text = words_text

print(f"\nBest P18 key: {best_p18_key}")
print(f"Best P18 score: {best_p18_score}")
print("Best P18 text:")
print(' '.join(best_p18_text))

# ==============================================================
# P19 Verification and P20 Non-Prime Stream
# ==============================================================
print("\n" + "=" * 60)
print("P19 Current Decryption")
print("=" * 60)

flat19, words19 = load_runes(19)
key19 = [24, 15, 2, 24, 4, 21, 11, 10, 20, 16, 9, 19, 26, 11, 7, 5, 11, 6, 27, 8,
          22, 25, 21, 16, 25, 0, 27, 9, 21, 7, 27, 15, 21, 9, 3, 16, 5, 22, 18, 4,
          5, 18, 23, 28, 28, 28, 28]

plain19 = decrypt_sub(flat19, key19)
word_sizes19 = [len(w) for w in words19]
p19_words = words_from_flat(plain19, word_sizes19)
p19_text = [to_text(w) for w in p19_words]
print("P19 current text:")
print(' '.join(p19_text))

# Try hill-climbing P19 too
new_key19, score19, wt19 = hill_climb_key(flat19, word_sizes19, key19, max_iter=30)
if score19 > score_words_list(p19_text):
    print(f"\nP19 improved to score {score19}:")
    print(' '.join(wt19))
    print(f"Improved key: {new_key19}")
