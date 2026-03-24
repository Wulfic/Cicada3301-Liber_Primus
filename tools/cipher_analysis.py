#!/usr/bin/env python3
"""
Comprehensive cipher analysis for Pages 21-54 of Liber Primus
=============================================================
Tests multiple cipher hypotheses including:
1. Keywords with gematria PRIME VALUES (not positional indices)
2. Autokey cipher variations
3. Cross-page key relationships (P00, P43, etc.)
4. Running key with solved page plaintext
5. P63 magic square numbers as key material
6. LFSR-based approaches
"""

import json
import os
import sys
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
PAGES_DIR = BASE / "pages"
DATA_DIR = BASE / "data"

# === Gematria Primus ===
RUNE_TO_IDX = {
    '\u16A0': 0,  '\u16A2': 1,  '\u16A6': 2,  '\u16A9': 3,  '\u16B1': 4,
    '\u16B3': 5,  '\u16B7': 6,  '\u16B9': 7,  '\u16BB': 8,  '\u16BE': 9,
    '\u16C1': 10, '\u16C4': 11, '\u16C7': 12, '\u16C8': 13, '\u16C9': 14,
    '\u16CB': 15, '\u16CF': 16, '\u16D2': 17, '\u16D6': 18, '\u16D7': 19,
    '\u16DA': 20, '\u16DD': 21, '\u16DF': 22, '\u16DE': 23, '\u16AA': 24,
    '\u16AB': 25, '\u16A3': 26, '\u16E1': 27, '\u16E0': 28,
}
IDX_TO_LETTER = [
    'F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S',
    'T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA'
]
# GP prime values
GP_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109]

def load_runes(page_num):
    p = PAGES_DIR / f"page_{page_num:02d}" / "runes.txt"
    if not p.exists():
        return None
    with open(p, 'r', encoding='utf-8') as f:
        return f.read()

def extract_indices(content):
    return [RUNE_TO_IDX[c] for c in content if c in RUNE_TO_IDX]

def compute_ioc(indices):
    n = len(indices)
    if n < 2:
        return 0
    counts = Counter(indices)
    return 29 * sum(c*(c-1) for c in counts.values()) / (n*(n-1))

def decrypt(cipher, key, mode='sub'):
    klen = len(key)
    result = []
    for i, c in enumerate(cipher):
        k = key[i % klen]
        if mode == 'sub':
            result.append((c - k) % 29)
        elif mode == 'add':
            result.append((c + k) % 29)
        elif mode == 'beaufort':
            result.append((k - c) % 29)
    return result

def to_runeglish(indices):
    return ''.join(IDX_TO_LETTER[i] for i in indices)

def keyword_to_indices(kw):
    """Convert keyword to GP index array."""
    rev = {}
    for i, l in enumerate(IDX_TO_LETTER):
        rev[l] = i
    result = []
    s = kw.upper()
    i = 0
    while i < len(s):
        matched = False
        for length in [3, 2]:
            if i + length <= len(s):
                chunk = s[i:i+length]
                if chunk in rev:
                    result.append(rev[chunk])
                    i += length
                    matched = True
                    break
        if not matched:
            ch = s[i]
            if ch == 'K': ch = 'C'
            if ch == 'V': ch = 'U'
            if ch in rev:
                result.append(rev[ch])
            i += 1
    return result

def keyword_to_prime_values(kw):
    """Convert keyword to GP prime values mod 29."""
    indices = keyword_to_indices(kw)
    return [GP_PRIMES[i] % 29 for i in indices]

# Common English word scoring  
COMMON_3GRAMS = {
    'THE': 100, 'AND': 80, 'FOR': 60, 'ARE': 55, 'BUT': 50,
    'NOT': 50, 'YOU': 45, 'ALL': 45, 'CAN': 40, 'HER': 40,
    'WAS': 40, 'ONE': 35, 'OUR': 35, 'OUT': 35, 'HAD': 30,
    'HAS': 30, 'HIS': 30, 'HOW': 25, 'ITS': 25, 'MAY': 25,
    'NEW': 25, 'NOW': 25, 'OLD': 25, 'SEE': 25, 'WAY': 25,
    'WHO': 25, 'DID': 20, 'GOT': 20, 'LET': 20, 'SAY': 20,
    'SHE': 20, 'TOO': 20, 'USE': 20, 'ING': 60, 'ION': 50,
    'ENT': 40, 'TIO': 40, 'ERE': 30, 'HIN': 30, 'ITH': 30,
}

def english_score(indices):
    """Score text for English-likeness using trigrams."""
    text = to_runeglish(indices)
    score = 0
    for i in range(len(text) - 2):
        tri = text[i:i+3]
        if tri in COMMON_3GRAMS:
            score += COMMON_3GRAMS[tri]
    return score

def english_score_words(content_with_seps, plain_indices):
    """Score based on word recognition."""
    common = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 
              'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'HAS', 'HIS', 'HOW',
              'ITS', 'MAY', 'NEW', 'NOW', 'OLD', 'SEE', 'WAY', 'WHO', 'DID',
              'THIS', 'THAT', 'WITH', 'HAVE', 'FROM', 'THEY', 'BEEN', 'SAID',
              'EACH', 'WILL', 'INTO', 'THAN', 'THEM', 'THEN', 'WHAT', 'WHEN',
              'MAKE', 'LIKE', 'LONG', 'LOOK', 'MANY', 'SOME', 'TIME', 'VERY',
              'YOUR', 'KNOW', 'JUST', 'COME', 'MADE', 'FIND', 'BACK', 'ONLY',
              'SELF', 'AN', 'TO', 'IN', 'IS', 'IT', 'AT', 'BE', 'BY', 'DO',
              'GO', 'IF', 'ME', 'MY', 'NO', 'ON', 'OR', 'SO', 'UP', 'WE',
              'OF', 'A', 'I', 'BEING', 'TRUTH', 'WITHIN', 'SACRED', 'WISDOM',
              'FOLLOW', 'INSTRUCTION', 'PILGRIMAGE', 'DIVINITY', 'INSTAR',
              'CIRCUMFERENCE', 'CONSUMPTION', 'PARABLE', 'KOAN', 'WARNING',
              'BELIEVE', 'NOTHING', 'BOOK', 'EXCEPT', 'DISCOVER', 'DEATH',
              'SUFFERING', 'STRUGGLE', 'INTELLIGENCE', 'HOLY'}
    
    # Extract words by splitting on non-rune chars
    ki = 0
    words = []
    cur = []
    for ch in content_with_seps:
        if ch in RUNE_TO_IDX:
            if ki < len(plain_indices):
                cur.append(plain_indices[ki])
                ki += 1
        elif ch in '-. \n':
            if cur:
                words.append(cur[:])
                cur = []
    if cur:
        words.append(cur[:])
    
    score = 0
    for w in words:
        rg = to_runeglish(w).upper()
        if rg in common:
            score += len(rg) * 15
        # GP substitution variants
        elif rg.replace('C', 'K') in common:
            score += len(rg) * 12
        elif rg.replace('U', 'V') in common:
            score += len(rg) * 12
    return score

# ===== TEST APPROACHES =====

def test_approach_results(page_num, cipher, content, results):
    """Collect and sort all test results."""
    results.sort(key=lambda x: (-x[1], -x[2]))  # Sort by IoC desc, then score desc
    
    print(f"\n{'='*70}")
    print(f"PAGE {page_num} - {len(cipher)} runes - Raw IoC: {compute_ioc(cipher):.4f}")
    print(f"{'='*70}")
    
    for name, ioc, escore, text_preview in results[:15]:
        print(f"  [{ioc:.4f}] [{escore:4d}] {name}: {text_preview[:80]}")
    
    return results

def analyze_page(page_num):
    content = load_runes(page_num)
    if not content:
        return []
    cipher = extract_indices(content)
    n = len(cipher)
    results = []
    
    # P63 keywords
    keywords = {
        'CABAL': [5, 24, 17, 24, 20],
        'DIVINITY': [23, 10, 1, 10, 9, 10, 16, 26],
        'SHADOWS': [15, 8, 24, 23, 3, 7, 15],
        'OBSCURA': [3, 17, 15, 5, 1, 4, 24],
        'MOURNFUL': [19, 3, 1, 4, 9, 0, 1, 20],
        'ENCRYPT': keyword_to_indices('ENCRYPT'),
        'ENCRYPTION': keyword_to_indices('ENCRYPTION'),
        'TOTIENT': keyword_to_indices('TOTIENT'),
        'DEOR': keyword_to_indices('DEOR'),
        'VOID': keyword_to_indices('VOID'),
        'AETHEREAL': keyword_to_indices('AETHEREAL'),
        'CARNAL': keyword_to_indices('CARNAL'),
        'ANALOG': keyword_to_indices('ANALOG'),
        'BUFFERS': keyword_to_indices('BUFFERS'),
        'MOBIUS': keyword_to_indices('MOBIUS'),
        'FORM': keyword_to_indices('FORM'),
        'CICADA': keyword_to_indices('CICADA'),
    }
    
    modes = ['sub', 'add', 'beaufort']
    
    # === Approach 1: Standard keyword Vigenere ===
    for kw_name, kw_idx in keywords.items():
        for mode in modes:
            plain = decrypt(cipher, kw_idx, mode)
            ioc = compute_ioc(plain)
            es = english_score(plain)
            ws = english_score_words(content, plain)
            text = to_runeglish(plain)
            results.append((f"Vig({kw_name},{mode})", ioc, es + ws, text[:200]))
    
    # === Approach 2: Keyword with GP PRIME VALUES mod 29 ===
    for kw_name, kw_idx in keywords.items():
        prime_key = [GP_PRIMES[i] % 29 for i in kw_idx]
        for mode in modes:
            plain = decrypt(cipher, prime_key, mode)
            ioc = compute_ioc(plain)
            es = english_score(plain)
            text = to_runeglish(plain)
            results.append((f"PrimeVal({kw_name},{mode})", ioc, es, text[:200]))
    
    # === Approach 3: Autokey cipher ===
    for kw_name, kw_idx in keywords.items():
        for mode in ['sub', 'add']:
            # Autokey: key = keyword + plaintext
            plain = []
            key_stream = list(kw_idx)
            for i, c in enumerate(cipher):
                if i < len(key_stream):
                    k = key_stream[i]
                else:
                    k = plain[i - len(kw_idx)]
                if mode == 'sub':
                    p = (c - k) % 29
                else:
                    p = (c + k) % 29
                plain.append(p)
                if i >= len(key_stream) - 1:
                    key_stream.append(p)  # extend for autokey
            ioc = compute_ioc(plain)
            es = english_score(plain)
            text = to_runeglish(plain)
            results.append((f"Autokey({kw_name},{mode})", ioc, es, text[:200]))
    
    # === Approach 4: Caesar shifts (0-28) ===
    for shift in range(29):
        plain = [(c - shift) % 29 for c in cipher]
        ioc = compute_ioc(plain)
        es = english_score(plain)
        text = to_runeglish(plain)
        if ioc > 1.3 or es > 50:
            results.append((f"Caesar({shift})", ioc, es, text[:200]))
    
    # === Approach 5: Multiplicative cipher ===
    for a in range(1, 29):
        # Check if a has inverse mod 29
        try:
            a_inv = pow(a, -1, 29)
        except:
            continue
        plain = [(a_inv * c) % 29 for c in cipher]
        ioc = compute_ioc(plain)
        es = english_score(plain)
        if ioc > 1.3:
            text = to_runeglish(plain)
            results.append((f"Mult(a={a})", ioc, es, text[:200]))
    
    # === Approach 6: Affine cipher ===
    for a in [3, 5, 7, 11, 13, 17, 19, 23]:
        a_inv = pow(a, -1, 29)
        for b in range(29):
            plain = [(a_inv * (c - b)) % 29 for c in cipher]
            ioc = compute_ioc(plain)
            if ioc > 1.5:
                es = english_score(plain)
                text = to_runeglish(plain)
                results.append((f"Affine(a={a},b={b})", ioc, es, text[:200]))
    
    # === Approach 7: Cross-page keys ===
    # Use other pages' runes as running key
    for key_page in [0, 56, 57]:  # P00 (title), P56 (parable), P57 (parable)
        key_content = load_runes(key_page)
        if key_content:
            key_indices = extract_indices(key_content)
            if len(key_indices) >= n:
                for mode in modes:
                    plain = decrypt(cipher, key_indices[:n], mode)
                    ioc = compute_ioc(plain)
                    es = english_score(plain)
                    text = to_runeglish(plain)
                    results.append((f"PageKey(P{key_page},{mode})", ioc, es, text[:200]))
            # Also try repeating shorter key pages
            elif len(key_indices) > 0:
                rep_key = (key_indices * (n // len(key_indices) + 1))[:n]
                for mode in modes:
                    plain = decrypt(cipher, rep_key, mode)
                    ioc = compute_ioc(plain)
                    es = english_score(plain)
                    text = to_runeglish(plain)
                    results.append((f"PageKey(P{key_page}rep,{mode})", ioc, es, text[:200]))
    
    # === Approach 8: Totient stream (phi(prime)) ===
    def primes_list(count):
        primes = []
        n = 2
        while len(primes) < count:
            if all(n % p != 0 for p in primes):
                primes.append(n)
            n += 1
        return primes
    
    primes = primes_list(n + 10)
    totient_key = [(p - 1) % 29 for p in primes[:n]]
    for mode in modes:
        plain = decrypt(cipher, totient_key, mode)
        ioc = compute_ioc(plain)
        es = english_score(plain)
        text = to_runeglish(plain)
        results.append((f"Totient_stream({mode})", ioc, es, text[:200]))
    
    # === Approach 9: P63 grid NUMBERS as key ===
    grid_numbers = [272, 138, 131, 151, 226, 245, 18]
    grid_key = [x % 29 for x in grid_numbers]
    for mode in modes:
        plain = decrypt(cipher, grid_key, mode)
        ioc = compute_ioc(plain)
        es = english_score(plain)
        text = to_runeglish(plain)
        results.append((f"GridNums({mode})", ioc, es, text[:200]))
    
    # Also try: 1033 (magic constant), 3301 
    for const, name in [(1033, 'MagicConst'), (3301, '3301'), (29, 'AlphaSize')]:
        key = [const % 29]
        plain = decrypt(cipher, key, 'sub')
        ioc = compute_ioc(plain)
        es = english_score(plain)
        if ioc > 1.0:
            text = to_runeglish(plain)
            results.append((f"{name}_caesar", ioc, es, text[:200]))
    
    # === Approach 10: Running key with Emerson's Self-Reliance ===
    sr_path = DATA_DIR / "self_reliance.txt"
    if sr_path.exists():
        with open(sr_path, 'r', encoding='utf-8', errors='ignore') as f:
            sr_text = f.read().upper()
        sr_indices = []
        rev = {}
        for i, l in enumerate(IDX_TO_LETTER):
            rev[l] = i
        for ch in sr_text:
            if ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                if ch == 'K': ch = 'C'
                if ch == 'V': ch = 'U'
                if ch == 'Q': ch = 'C'
                if ch == 'Z': ch = 'S'
                if ch in rev:
                    sr_indices.append(rev[ch])
        
        # Try 10 different offsets
        for offset in [0, 100, 500, 1000, 2000, 5000, 10000]:
            if offset + n <= len(sr_indices):
                key = sr_indices[offset:offset+n]
                for mode in ['sub', 'add']:
                    plain = decrypt(cipher, key, mode)
                    ioc = compute_ioc(plain)
                    es = english_score(plain)
                    if ioc > 1.2 or es > 30:
                        text = to_runeglish(plain)
                        results.append((f"SelfRel(off={offset},{mode})", ioc, es, text[:200]))
    
    # === Approach 11: Deor poem as running key ===
    deor_path = DATA_DIR / "deor_poem.txt"
    if deor_path.exists():
        with open(deor_path, 'r', encoding='utf-8', errors='ignore') as f:
            deor_text = f.read().upper()
        deor_indices = []
        rev = {}
        for i, l in enumerate(IDX_TO_LETTER):
            rev[l] = i
        for ch in deor_text:
            if ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                if ch == 'K': ch = 'C'
                if ch == 'V': ch = 'U'
                if ch == 'Q': ch = 'C'
                if ch == 'Z': ch = 'S'
                if ch in rev:
                    deor_indices.append(rev[ch])
        
        for offset in range(0, min(len(deor_indices) - n, 200)):
            if offset + n <= len(deor_indices):
                key = deor_indices[offset:offset+n]
                for mode in ['sub', 'beaufort']:
                    plain = decrypt(cipher, key, mode)
                    ioc = compute_ioc(plain)
                    es = english_score(plain)
                    if ioc > 1.4 or es > 50:
                        text = to_runeglish(plain)
                        results.append((f"Deor(off={offset},{mode})", ioc, es, text[:200]))
    
    # === Approach 12: Liber AL vel Legis as running key ===
    la_path = BASE / "reference" / "liber_al_vel_legis.txt"
    if la_path.exists():
        with open(la_path, 'r', encoding='utf-8', errors='ignore') as f:
            la_text = f.read().upper()
        la_indices = []
        rev = {}
        for i, l in enumerate(IDX_TO_LETTER):
            rev[l] = i
        for ch in la_text:
            if ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                if ch == 'K': ch = 'C'
                if ch == 'V': ch = 'U'
                if ch == 'Q': ch = 'C'
                if ch == 'Z': ch = 'S'
                if ch in rev:
                    la_indices.append(rev[ch])
        
        # Try several offsets
        for offset in range(0, min(len(la_indices) - n, 5000), 100):
            if offset + n <= len(la_indices):
                key = la_indices[offset:offset+n]
                for mode in ['sub', 'beaufort']:
                    plain = decrypt(cipher, key, mode)
                    ioc = compute_ioc(plain)
                    es = english_score(plain)
                    if ioc > 1.4 or es > 50:
                        text = to_runeglish(plain)
                        results.append((f"LiberAL(off={offset},{mode})", ioc, es, text[:200]))
    
    return test_approach_results(page_num, cipher, content, results)

def main():
    # Test pages 21-30 first (highest priority)
    for page in range(21, 31):
        results = analyze_page(page)
        if results:
            best = results[0]
            print(f"\n  ** BEST for P{page}: {best[0]} IoC={best[1]:.4f} score={best[2]}")
    
    print(f"\n{'='*70}")
    print("Testing P43 + P00 cross-key relationship")
    print(f"{'='*70}")
    
    # Special: P43 + P00 
    p43_content = load_runes(43)
    p00_content = load_runes(0)
    if p43_content and p00_content:
        p43_cipher = extract_indices(p43_content)
        p00_cipher = extract_indices(p00_content)
        
        # P43 decrypted with P00 as key (ADD)
        p00_key = (p00_cipher * (len(p43_cipher) // len(p00_cipher) + 1))[:len(p43_cipher)]
        for mode in ['sub', 'add', 'beaufort']:
            plain = decrypt(p43_cipher, p00_key, mode)
            ioc = compute_ioc(plain)
            es = english_score(plain)
            text = to_runeglish(plain)
            print(f"  P43 w/P00 key ({mode}): IoC={ioc:.4f} score={es} text={text[:100]}")
        
        # P00 decrypted with P43 as key
        p43_key = (p43_cipher * (len(p00_cipher) // len(p43_cipher) + 1))[:len(p00_cipher)]
        for mode in ['sub', 'add', 'beaufort']:
            plain = decrypt(p00_cipher, p43_key, mode)
            ioc = compute_ioc(plain)
            es = english_score(plain)
            text = to_runeglish(plain)
            print(f"  P00 w/P43 key ({mode}): IoC={ioc:.4f} score={es} text={text[:100]}")

if __name__ == "__main__":
    main()
