#!/usr/bin/env python3
"""
Advanced Cipher Solver for Liber Primus Pages 21-54
=====================================================
Tests cipher models beyond simple Vigenère:
1. Autokey cipher (plaintext-feedback) with P63 keywords as seeds
2. Running key using Liber AL vel Legis
3. Running key using solved LP page plaintexts
4. Beaufort autokey
5. Vigenère with F-skip using P63 keywords
6. Gromark/progressive key
7. Two-square / Playfair variants adapted to mod-29
8. LFSR with keyword-derived taps
"""

import os
import sys
import json
import math
from pathlib import Path
from collections import Counter

BASE = Path(__file__).resolve().parent.parent
PAGES_DIR = BASE / "pages"
DATA_DIR = BASE / "data"
REF_DIR = BASE / "reference"

# === GP Alphabet ===
RUNE_TO_IDX = {
    'ᚠ': 0, 'ᚢ': 1, 'ᚦ': 2, 'ᚩ': 3, 'ᚱ': 4, 'ᚳ': 5, 'ᚷ': 6, 'ᚹ': 7,
    'ᚻ': 8, 'ᚾ': 9, 'ᛁ': 10, 'ᛄ': 11, 'ᛇ': 12, 'ᛈ': 13, 'ᛉ': 14, 'ᛋ': 15,
    'ᛏ': 16, 'ᛒ': 17, 'ᛖ': 18, 'ᛗ': 19, 'ᛚ': 20, 'ᛝ': 21, 'ᛟ': 22, 'ᛞ': 23,
    'ᚪ': 24, 'ᚫ': 25, 'ᚣ': 26, 'ᛡ': 27, 'ᛠ': 28,
}
IDX_TO_LETTER = [
    'F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S',
    'T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA'
]

GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]

# Page keywords (from P63 grid)
PAGE_KEYWORDS = {
    21: ('CABAL',      [5, 24, 17, 24, 20]),
    22: ('DIVINITY',   [23, 10, 1, 10, 9, 10, 16, 26]),
    23: ('ENCRYPTION', [18, 9, 5, 4, 26, 13, 16, 10, 3, 9]),
    24: ('OBSCURA',    [3, 17, 15, 5, 1, 4, 24]),
    25: ('CABAL',      [5, 24, 17, 24, 20]),
    26: ('ENCRYPT',    [18, 9, 5, 4, 26, 13, 16]),
    27: ('SHADOWS',    [15, 8, 24, 23, 3, 7, 15]),
    28: ('DEOR',       [23, 18, 3, 4]),
    29: ('TOTIENT',    [16, 3, 16, 10, 18, 9, 16]),
    30: ('MOURNFUL',   [19, 3, 1, 4, 9, 0, 1, 20]),
}

# Common English words for scoring
COMMON_3PLUS = {'THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','HER','WAS','ONE',
    'OUR','OUT','HAD','HAS','HIS','HOW','ITS','MAY','NEW','NOW','OLD','SEE','WAY','WHO',
    'THIS','THAT','WITH','HAVE','FROM','THEY','BEEN','SAID','EACH','WILL','INTO','THAN',
    'THEM','THEN','WHAT','WHEN','MAKE','LIKE','LONG','LOOK','MANY','SOME','TIME','YOUR',
    'KNOW','JUST','COME','MADE','FIND','ONLY','SELF','BEING','TRUTH','WITHIN','SACRED',
    'WISDOM','FOLLOW','BELIEVE','NOTHING','BOOK','THINGS','SHOULD','PRIMES','TOTIENT',
    'PILGRIM','JOURNEY','TOWARD','THROUGH','DISCOVER','EMERGE','HOLY','INTELLIGENCE',
    'COMMAND','OWN','INSTRUCTION','KOAN','DIVINITY','CIRCUMFERENCE','CONSUMPTION',
    'PRESERVATION','ADHERENCE','ENCRYPTED','QUESTION','DEATH','EXPERIENCE','TEST',
    'KNOWLEDGE','PARABLE','INSTAR','CERTAINTY','ILLUSIONS','INNOCENCE','SUFFERING',
    'STRUGGLE','REALITY','REALITIES','SHAPE','PILGRIMAGE','ARRIVE','OUTSIDE','DEEP',
    'SHADOWS','VOID','CARNAL','OBSCURA','FORM','WELCOME','WARNING','END',
    # GP-specific forms
    'EUERY','NEUER','DISCOUER','ABOUE','CWESTION','THNGS','CNOW','BENG','LICE',
    'SEEC','BOOC','GONG','SUFFERNG',
}

def load_runes(page_num):
    rune_file = PAGES_DIR / f"page_{page_num:02d}" / "runes.txt"
    if not rune_file.exists():
        return None, None
    with open(rune_file, 'r', encoding='utf-8') as f:
        content = f.read()
    indices = [RUNE_TO_IDX[ch] for ch in content if ch in RUNE_TO_IDX]
    return indices, content

def text_to_gp_indices(text):
    """Convert English text to GP index array (best effort)."""
    LETTER_MAP = {}
    for i, l in enumerate(IDX_TO_LETTER):
        LETTER_MAP[l] = i
    
    result = []
    text = text.upper()
    i = 0
    while i < len(text):
        matched = False
        # Try 2-char digraphs first
        if i + 2 <= len(text):
            chunk = text[i:i+2]
            if chunk in LETTER_MAP:
                result.append(LETTER_MAP[chunk])
                i += 2
                matched = True
        if not matched and i + 3 <= len(text):
            chunk = text[i:i+3]
            if chunk == 'ING':
                result.append(LETTER_MAP['NG'])
                i += 3
                matched = True
        if not matched:
            ch = text[i]
            if ch == 'K': ch = 'C'
            if ch == 'V': ch = 'U'
            if ch == 'Q': ch = 'C'
            if ch in LETTER_MAP:
                result.append(LETTER_MAP[ch])
                i += 1
                matched = True
            else:
                i += 1  # Skip non-GP characters
    return result

def compute_ioc(indices):
    n = len(indices)
    if n < 2: return 0
    counts = Counter(indices)
    num = sum(c*(c-1) for c in counts.values())
    den = n*(n-1)
    return 29 * num / den if den > 0 else 0

def to_runeglish(indices):
    return ''.join(IDX_TO_LETTER[i] for i in indices)

def score_text(runeglish):
    """Quick score: count word matches in text split by likely word boundaries."""
    # Heuristic: check for common 3+ letter words as substrings
    score = 0
    text = runeglish.upper()
    
    for word in COMMON_3PLUS:
        count = text.count(word)
        if count > 0:
            score += count * len(word) * len(word)  # Weight longer words more
    
    return score

def score_with_structure(content, plain_indices, mode_key_func):
    """Score using word boundaries from the original rune text."""
    words = []
    current = []
    key_pos = 0
    
    for ch in content:
        if ch in RUNE_TO_IDX:
            if key_pos < len(plain_indices):
                current.append(IDX_TO_LETTER[plain_indices[key_pos]])
            key_pos += 1
        elif ch == '-':
            if current:
                words.append(''.join(current))
                current = []
        elif ch == '.':
            if current:
                words.append(''.join(current))
                current = []
    if current:
        words.append(''.join(current))
    
    score = 0
    matched = 0
    for w in words:
        wu = w.upper()
        if wu in COMMON_3PLUS:
            score += len(wu) * 10
            matched += 1
        elif wu.replace('C', 'K') in COMMON_3PLUS:
            score += len(wu) * 8
            matched += 1
        elif wu.replace('U', 'V') in COMMON_3PLUS:
            score += len(wu) * 8
            matched += 1
    
    return score, matched, len(words), words

# ========== CIPHER METHODS ==========

def autokey_decrypt_sub(cipher, seed):
    """Autokey cipher: key = seed + plaintext."""
    plain = []
    key = list(seed)
    for i, c in enumerate(cipher):
        k = key[i] if i < len(key) else plain[i - len(seed)]
        p = (c - k) % 29
        plain.append(p)
    return plain

def autokey_decrypt_add(cipher, seed):
    """Autokey ADD: plain[i] = (cipher[i] + key[i]) % 29, key = seed + plaintext."""
    plain = []
    key = list(seed)
    for i, c in enumerate(cipher):
        k = key[i] if i < len(key) else plain[i - len(seed)]
        p = (c + k) % 29
        plain.append(p)
    return plain

def autokey_decrypt_beaufort(cipher, seed):
    """Autokey Beaufort: plain[i] = (key[i] - cipher[i]) % 29."""
    plain = []
    key = list(seed)
    for i, c in enumerate(cipher):
        k = key[i] if i < len(key) else plain[i - len(seed)]
        p = (k - c) % 29
        plain.append(p)
    return plain

def autokey_decrypt_cipher_feedback(cipher, seed, mode='sub'):
    """Cipher-feedback autokey: key = seed + ciphertext (not plaintext)."""
    plain = []
    key = list(seed)
    for i, c in enumerate(cipher):
        k = key[i] if i < len(key) else cipher[i - len(seed)]
        if mode == 'sub':
            p = (c - k) % 29
        elif mode == 'add':
            p = (c + k) % 29
        elif mode == 'beaufort':
            p = (k - c) % 29
        plain.append(p)
    return plain

def running_key_decrypt(cipher, key_stream, mode='sub'):
    """Running key: use external text as one-time key."""
    plain = []
    for i, c in enumerate(cipher):
        if i >= len(key_stream):
            break
        k = key_stream[i]
        if mode == 'sub':
            p = (c - k) % 29
        elif mode == 'add':
            p = (c + k) % 29
        elif mode == 'beaufort':
            p = (k - c) % 29
        plain.append(p)
    return plain

def vigenere_fskip(cipher_content, key_indices, mode='sub'):
    """Vigenère with F-skip: literal F (index 0) in cipher skips key advancement."""
    plain = []
    key_pos = 0
    klen = len(key_indices)
    
    for ch in cipher_content:
        if ch not in RUNE_TO_IDX:
            continue
        c = RUNE_TO_IDX[ch]
        
        if c == 0:  # F rune
            # Check if this is a literal F (key not applied)
            plain.append(0)  # Output F
            # Key does NOT advance
        else:
            k = key_indices[key_pos % klen]
            if mode == 'sub':
                p = (c - k) % 29
            elif mode == 'add':
                p = (c + k) % 29
            elif mode == 'beaufort':
                p = (k - c) % 29
            plain.append(p)
            key_pos += 1
    
    return plain

def progressive_key(cipher, seed, step=1):
    """Progressive/Gromark: key[i] = (seed[i%len(seed)] + i*step) % 29."""
    plain = []
    slen = len(seed)
    for i, c in enumerate(cipher):
        k = (seed[i % slen] + i * step) % 29
        p = (c - k) % 29
        plain.append(p)
    return plain

def lfsr_key_stream(seed, taps, length, mod=29):
    """Generate LFSR key stream over GF(mod)."""
    register = list(seed)
    stream = []
    for _ in range(length):
        stream.append(register[0])
        # Feedback: sum of tapped positions
        feedback = sum(register[t] for t in taps) % mod
        register.pop(0)
        register.append(feedback)
    return stream

# ========== RUNNING KEY SOURCES ==========

def load_liber_al():
    """Load Liber AL vel Legis and convert to GP indices."""
    path = REF_DIR / "liber_al_vel_legis.txt"
    if not path.exists():
        return []
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    return text_to_gp_indices(text)

def load_solved_plaintext():
    """Concatenate all solved page plaintexts as GP indices."""
    # Use the known plaintext from Master Tracker
    known_texts = [
        # P01
        "A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE TEST THE KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH DO NOT EDIT OR CHANGE THIS BOOK OR THE MESSAGE CONTAINED WITHIN EITHER THE WORDS OR THEIR NUMBERS FOR ALL IS SACRED",
        # P03-04
        "WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS IT IS NOT AN EASY TRIP BUT FOR THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE ALONG THE WAY YOU WILL FIND AN END TO ALL STRUGGLE AND SUFFERING YOUR INNOCENCE YOUR ILLUSIONS YOUR CERTAINTY AND YOUR REALITY ULTIMATELY YOU WILL DISCOVER AN END TO SELF IT IS THROUGH THIS PILGRIMAGE THAT WE SHAPE OURSELVES AND OUR REALITIES JOURNEY DEEP WITHIN AND YOU WILL ARRIVE OUTSIDE LIKE THE INSTAR IT IS ONLY THROUGH GOING WITHIN THAT WE MAY EMERGE WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY AN INSTRUCTION COMMAND YOUR OWN SELF",
        # P05
        "SOME WISDOM THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED ALL THINGS SHOULD BE ENCRYPTED KNOW THIS",
        # P06-08
        "A KOAN A MAN DECIDED TO GO AND STUDY WITH A MASTER HE WENT TO THE DOOR OF THE MASTER AND ASKED TO BE ACCEPTED AS A STUDENT THE MASTER SAID HOW CAN I TEACH YOU IF YOUR HEAD IS ALREADY FULL OF KNOWLEDGE WHAT DO YOU KNOW THE STUDENT DECIDED TO SHOW HIS INTELLIGENCE AND BEGAN TO TALK ABOUT ALL OF THE THINGS HE HAD LEARNED ABOUT LOGIC AND PHILOSOPHY AND MATHEMATICS AND ALL OF THE BOOKS HE HAD READ THE MASTER INVITED HIM INSIDE FOR TEA AS THE MASTER BEGAN TO POUR THE CUP OF TEA HE DID NOT STOP WHEN THE CUP WAS FULL BUT INSTEAD CONTINUED TO POUR THE STUDENT SHOUTED STOP THE CUP IS FULL IT CANNOT HOLD ANY MORE TO WHICH THE MASTER REPLIED RETURN TO ME WHEN YOUR CUP IS EMPTY SOME WISDOM A MAN IS ONLY AS FAITHFUL AS HIS OPTIONS AN INSTRUCTION STUDY THE WORD GO AND LISTEN FOR THE WORD COME",
        # P09
        "AN INSTRUCTION DO FOUR UNREASONABLE THINGS EACH DAY",
        # P10-13
        "THE LOSS OF DIVINITY THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS WHICH CAUSE THE LOSS OF DIVINITY CONSUMPTION THERE IS NO THING IN CREATION WHICH LACKS BEAUTY AND VALUE ALL THINGS POSSESS DIVINITY AND THIS DIVINITY MUST BE KNOWN NOT CONSUMED EVERYTHING IS SACRED ALL IS SACRED SOME WISDOM AMASS GREAT WEALTH NEVER BECOME ATTACHED TO WHAT YOU OWN BE PREPARED TO DESTROY ALL THAT YOU OWN",
        # P14-15
        "A KOAN DURING A LESSON THE MASTER EXPLAINED THE I THE I IS A PART OF YOU THAT BELIEVES IT IS IN CONTROL YOUR I IS THE VOICE IN YOUR HEAD THAT IS IN CONTROL",
        # P17
        "EPILOGUE WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO",
    ]
    
    combined = ' '.join(known_texts)
    return text_to_gp_indices(combined)

def load_self_reliance():
    """Load Emerson's Self-Reliance essay."""
    path = DATA_DIR / "self_reliance.txt"
    if not path.exists():
        return []
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    return text_to_gp_indices(text)

def load_deor():
    """Load Deor poem."""
    path = DATA_DIR / "deor_poem.txt"
    if not path.exists():
        return []
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    return text_to_gp_indices(text)

# ========== MAIN SOLVER ==========

def test_page(page_num, running_keys, verbose=True):
    """Test all cipher methods on a page."""
    cipher, content = load_runes(page_num)
    if cipher is None:
        return None
    
    results = []
    
    kw_name = None
    kw_idx = None
    if page_num in PAGE_KEYWORDS:
        kw_name, kw_idx = PAGE_KEYWORDS[page_num]
    
    # ===== 1. Autokey with keyword seed =====
    if kw_idx:
        for mode_name, func in [('autokey_sub', autokey_decrypt_sub), 
                                  ('autokey_add', autokey_decrypt_add),
                                  ('autokey_beaufort', autokey_decrypt_beaufort)]:
            plain = func(cipher, kw_idx)
            ioc = compute_ioc(plain)
            text = to_runeglish(plain)
            sc = score_text(text)
            sc2, matched, total, words = score_with_structure(content, plain, None)
            results.append((f'{mode_name}({kw_name})', ioc, sc + sc2, matched, total, text[:150], words[:15]))
    
    # ===== 2. Cipher-feedback autokey =====
    if kw_idx:
        for mode in ['sub', 'add', 'beaufort']:
            plain = autokey_decrypt_cipher_feedback(cipher, kw_idx, mode)
            ioc = compute_ioc(plain)
            text = to_runeglish(plain)
            sc = score_text(text)
            sc2, matched, total, words = score_with_structure(content, plain, None)
            results.append((f'cf_autokey_{mode}({kw_name})', ioc, sc + sc2, matched, total, text[:150], words[:15]))
    
    # ===== 3. Vigenère with F-skip =====
    if kw_idx:
        for mode in ['sub', 'add', 'beaufort']:
            plain = vigenere_fskip(content, kw_idx, mode)
            ioc = compute_ioc(plain)
            text = to_runeglish(plain)
            sc = score_text(text)
            results.append((f'fskip_{mode}({kw_name})', ioc, sc, 0, 0, text[:150], []))
    
    # ===== 4. Progressive key =====
    if kw_idx:
        for step in [1, 2, 3, 5, 7, 11, 13, -1, -2]:
            plain = progressive_key(cipher, kw_idx, step)
            ioc = compute_ioc(plain)
            text = to_runeglish(plain)
            sc = score_text(text)
            results.append((f'progressive_s{step}({kw_name})', ioc, sc, 0, 0, text[:150], []))
    
    # ===== 5. Running keys with various sources =====
    for rk_name, rk_indices in running_keys.items():
        if len(rk_indices) < len(cipher):
            continue
        
        # Test multiple offsets
        best_offset = -1
        best_ioc = 0
        best_mode = None
        best_text = ""
        best_score = 0
        best_words = []
        
        # Coarse scan: every 100th offset
        for offset in range(0, len(rk_indices) - len(cipher), 100):
            key_segment = rk_indices[offset:offset+len(cipher)]
            for mode in ['sub', 'add', 'beaufort']:
                plain = running_key_decrypt(cipher, key_segment, mode)
                ioc = compute_ioc(plain)
                if ioc > best_ioc:
                    best_ioc = ioc
                    best_offset = offset
                    best_mode = mode
        
        # Refine around best offset
        if best_offset >= 0:
            for offset in range(max(0, best_offset - 100), min(len(rk_indices) - len(cipher), best_offset + 100)):
                key_segment = rk_indices[offset:offset+len(cipher)]
                plain = running_key_decrypt(cipher, key_segment, best_mode)
                ioc = compute_ioc(plain)
                if ioc > best_ioc:
                    best_ioc = ioc
                    best_offset = offset
            
            # Get text for best result
            key_segment = rk_indices[best_offset:best_offset+len(cipher)]
            plain = running_key_decrypt(cipher, key_segment, best_mode)
            text = to_runeglish(plain)
            sc = score_text(text)
            sc2, matched, total, words = score_with_structure(content, plain, None)
            results.append((f'runkey_{rk_name}_off{best_offset}_{best_mode}', best_ioc, sc + sc2, matched, total, text[:150], words[:15]))
    
    # ===== 6. LFSR key streams =====
    if kw_idx:
        for degree in [4, 5, 6, 7, 8]:
            seed = (kw_idx * ((degree // len(kw_idx)) + 1))[:degree]
            # Try different tap configurations
            for taps in [[1, degree-1], [1, 2], [2, degree-1], list(range(1, degree))]:
                valid_taps = [t for t in taps if t < degree]
                if not valid_taps:
                    continue
                ks = lfsr_key_stream(seed, valid_taps, len(cipher))
                for mode in ['sub', 'beaufort']:
                    plain = running_key_decrypt(cipher, ks, mode)
                    ioc = compute_ioc(plain)
                    if ioc > 1.2:  # Only report promising results
                        text = to_runeglish(plain)
                        sc = score_text(text)
                        results.append((f'lfsr_d{degree}_t{valid_taps}_{mode}', ioc, sc, 0, 0, text[:150], []))
    
    # ===== 7. Autokey with ALL P63 keywords as seeds =====
    all_keywords = {
        'DIVINITY': [23, 10, 1, 10, 9, 10, 16, 26],
        'CABAL': [5, 24, 17, 24, 20],
        'SHADOWS': [15, 8, 24, 23, 3, 7, 15],
        'OBSCURA': [3, 17, 15, 5, 1, 4, 24],
        'VOID': [1, 3, 10, 23],
        'FORM': [0, 3, 4, 19],
        'MOBIUS': [19, 3, 17, 10, 1, 15],
        'ANALOG': [24, 9, 24, 20, 3, 6],
        'MOURNFUL': [19, 3, 1, 4, 9, 0, 1, 20],
        'AETHEREAL': [24, 18, 2, 8, 18, 4, 18, 24, 20],
        'BUFFERS': [17, 1, 0, 0, 18, 4, 15],
        'CARNAL': [5, 24, 4, 9, 24, 20],
        'TOTIENT': [16, 3, 16, 10, 18, 9, 16],
        'ENCRYPT': [18, 9, 5, 4, 26, 13, 16],
        'DEOR': [23, 18, 3, 4],
        'CICADA': [5, 10, 5, 24, 23, 24],
    }
    
    for ak_name, ak_seed in all_keywords.items():
        if kw_name and ak_name == kw_name:
            continue  # Already tested above
        for mode_name, func in [('autosub', autokey_decrypt_sub), 
                                  ('autobeau', autokey_decrypt_beaufort)]:
            plain = func(cipher, ak_seed)
            ioc = compute_ioc(plain)
            if ioc > 1.2:  # Only report promising
                text = to_runeglish(plain)
                sc = score_text(text)
                sc2, matched, total, words = score_with_structure(content, plain, None)
                results.append((f'{mode_name}({ak_name})', ioc, sc + sc2, matched, total, text[:150], words[:15]))
    
    # Sort by combined score (IoC * 100 + word_score)
    results.sort(key=lambda x: -(x[2] + x[1] * 50))
    
    if verbose:
        print(f"\n{'='*80}")
        print(f"PAGE {page_num:02d} — {len(cipher)} runes")
        if kw_name:
            print(f"P63 Keyword: {kw_name}")
        print(f"{'='*80}")
        print(f"{'Method':<45} {'IoC':>7} {'Score':>7} {'Match':>5}/{'':<5} | Text Preview")
        print("-" * 130)
        for method, ioc, score, matched, total, text, words in results[:20]:
            print(f"{method:<45} {ioc:>7.4f} {score:>7} {matched:>5}/{total:<5} | {text[:65]}")
            if matched > 0:
                eng_words = [w for w in words if w.upper() in COMMON_3PLUS or 
                            w.upper().replace('C','K') in COMMON_3PLUS or
                            w.upper().replace('U','V') in COMMON_3PLUS]
                if eng_words:
                    print(f"{'':45} {'':>7} {'':>7} {'':>5} {'':>5} | MATCHES: {eng_words[:10]}")
    
    return results

def main():
    print("LIBER PRIMUS — Advanced Cipher Analysis")
    print("=" * 80)
    
    # Load running key sources
    print("Loading running key sources...")
    running_keys = {}
    
    liber_al = load_liber_al()
    if liber_al:
        running_keys['LiberAL'] = liber_al
        print(f"  Liber AL: {len(liber_al)} GP indices")
    
    solved_pt = load_solved_plaintext()
    if solved_pt:
        running_keys['SolvedLP'] = solved_pt
        print(f"  Solved LP: {len(solved_pt)} GP indices")
    
    self_rel = load_self_reliance()
    if self_rel:
        running_keys['SelfReliance'] = self_rel  
        print(f"  Self-Reliance: {len(self_rel)} GP indices")
    
    deor = load_deor()
    if deor:
        running_keys['Deor'] = deor
        print(f"  Deor: {len(deor)} GP indices")
    
    # Test pages 21-54
    all_results = {}
    
    # Focus on key pages first
    priority_pages = [21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 43, 44, 49, 54]
    
    for pg in priority_pages:
        results = test_page(pg, running_keys)
        if results:
            all_results[pg] = results
    
    # Summary
    print("\n" + "=" * 80)
    print("BEST RESULTS PER PAGE")
    print("=" * 80)
    for pg in sorted(all_results.keys()):
        if all_results[pg]:
            best = all_results[pg][0]
            method, ioc, score, matched, total, text, words = best
            eng = [w for w in words if w.upper() in COMMON_3PLUS]
            print(f"P{pg:02d}: {method:<40} IoC={ioc:.4f} Score={score:>6} Match={matched}/{total}")
            if eng:
                print(f"  → English words: {eng[:10]}")

if __name__ == '__main__':
    main()
