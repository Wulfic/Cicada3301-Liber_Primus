#!/usr/bin/env python3
"""
P43 + P00 Analysis — IoC 2.0632 (Highest signal in any unsolved page)
=====================================================================
The Master Tracker notes that using P00 runes as Vigenère ADD key on P43
produces IoC 2.0632 — HIGHER than English (~1.73).

This script:
1. Tests P00 as key for P43 (ADD, SUB, Beaufort, XOR)
2. Tests P43 as key for P00
3. Analyzes the decrypted output for words
4. Tries second-layer transformations
5. Tests P00 as key for ALL unsolved pages
"""

import os
import sys
import json
from pathlib import Path
from collections import Counter
from itertools import combinations

BASE = Path(__file__).resolve().parent.parent
PAGES_DIR = BASE / "pages"
DATA_DIR = BASE / "data"

# === Gematria Primus ===
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

# GP prime values
GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]

# Common English words (Runeglish form)
COMMON_WORDS = {
    'THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','HER','WAS','ONE','OUR',
    'OUT','HAD','HAS','HIS','HOW','ITS','MAY','NEW','NOW','OLD','SEE','WAY','WHO',
    'THIS','THAT','WITH','HAVE','FROM','THEY','BEEN','SAID','EACH','WILL','INTO',
    'THAN','THEM','THEN','WHAT','WHEN','MAKE','LIKE','LONG','LOOK','MANY','SOME',
    'TIME','YOUR','KNOW','JUST','COME','MADE','FIND','BACK','ONLY','SELF','BEING',
    'TRUTH','WITHIN','SACRED','WISDOM','FOLLOW','INSTRUCTION','DIVINITY',
    'CIRCUMFERENCE','CONSUMPTION','BELIEVE','NOTHING','BOOK','EXCEPT','TRUE',
    'TEST','KNOWLEDGE','EXPERIENCE','DEATH','EDIT','CHANGE','MESSAGE','CONTAINED',
    'EITHER','WORDS','NUMBERS','THINGS','SHOULD','ENCRYPTED','PRIMES','TOTIENT',
    'PILGRIM','JOURNEY','TOWARD','END','EASY','TRIP','THOSE','NECESSARY',
    'ALONG','STRUGGLE','SUFFERING','INNOCENCE','ILLUSIONS','CERTAINTY','REALITY',
    'ULTIMATELY','DISCOVER','THROUGH','PILGRIMAGE','SHAPE','OURSELVES','REALITIES',
    'DEEP','ARRIVE','OUTSIDE','INSTAR','GOING','EMERGE','HOLY','INTELLIGENCE',
    'COMMAND','OWN','SHADOWS','VOID','CARNAL','OBSCURA','FORM','MOBIUS','ANALOG',
    'MOURNFUL','CABAL','AETHEREAL','BUFFERS',
    'A','I','OF','TO','IN','IS','IT','AN','AS','AT','BE','BY','DO','GO','IF',
    'ME','MY','NO','ON','OR','SO','UP','WE',
    # GP-specific forms
    'EUERY','NEUER','DISCOUER','ABOUE','CWESTION','THNGS','CNOW',
}

# Cicada-specific word patterns
CICADA_BIGRAMS = {
    'TH': 8, 'HE': 7, 'IN': 6, 'AN': 6, 'ER': 5, 'ND': 5, 'ON': 5, 'EN': 5,
    'AT': 5, 'RE': 5, 'ED': 4, 'ES': 4, 'OU': 4, 'TO': 4, 'HA': 4, 'IS': 4,
    'IT': 4, 'AL': 4, 'ST': 4, 'NG': 4, 'OR': 3, 'AR': 3, 'TE': 3, 'SE': 3,
    'OF': 3, 'LE': 3, 'SA': 3, 'EA': 3, 'OE': 3, 'IO': 3,
}

def load_runes(page_num):
    """Load rune file and return rune indices (letter-only)."""
    rune_file = PAGES_DIR / f"page_{page_num:02d}" / "runes.txt"
    if not rune_file.exists():
        return None, None
    with open(rune_file, 'r', encoding='utf-8') as f:
        content = f.read()
    indices = [RUNE_TO_IDX[ch] for ch in content if ch in RUNE_TO_IDX]
    return indices, content

def load_runes_with_structure(page_num):
    """Load runes preserving word boundaries."""
    rune_file = PAGES_DIR / f"page_{page_num:02d}" / "runes.txt"
    if not rune_file.exists():
        return None
    with open(rune_file, 'r', encoding='utf-8') as f:
        content = f.read()
    return content

def decrypt(cipher, key, mode='add'):
    """Decrypt cipher with key using given mode."""
    result = []
    klen = len(key)
    for i, c in enumerate(cipher):
        k = key[i % klen]
        if mode == 'add':
            result.append((c + k) % 29)
        elif mode == 'sub':
            result.append((c - k) % 29)
        elif mode == 'beaufort':
            result.append((k - c) % 29)
        elif mode == 'xor':
            # XOR in mod 29 is not standard, but try additive inverse
            result.append((c ^ k) % 29)
    return result

def to_runeglish(indices):
    """Convert GP indices to runeglish string."""
    return ''.join(IDX_TO_LETTER[i] for i in indices)

def to_runeglish_with_structure(content, key_indices, mode='add'):
    """Decrypt preserving structure (hyphens, periods, etc.)."""
    key_pos = 0
    klen = len(key_indices)
    output = []
    words = []
    current_word = []
    
    for ch in content:
        if ch in RUNE_TO_IDX:
            c = RUNE_TO_IDX[ch]
            k = key_indices[key_pos % klen]
            if mode == 'add':
                p = (c + k) % 29
            elif mode == 'sub':
                p = (c - k) % 29
            elif mode == 'beaufort':
                p = (k - c) % 29
            else:
                p = c
            output.append(IDX_TO_LETTER[p])
            current_word.append(IDX_TO_LETTER[p])
            key_pos += 1
        elif ch == '-':
            if current_word:
                words.append(''.join(current_word))
                current_word = []
            output.append(' ')
        elif ch == '.':
            if current_word:
                words.append(''.join(current_word))
                current_word = []
            output.append('. ')
        elif ch in '&$/%':
            if current_word:
                words.append(''.join(current_word))
                current_word = []
            output.append(f' {ch} ')
        elif ch in '\n\r':
            pass
    
    if current_word:
        words.append(''.join(current_word))
    
    return ''.join(output), words

def compute_ioc(indices):
    """Compute Index of Coincidence normalized to 29-letter alphabet."""
    n = len(indices)
    if n < 2:
        return 0
    counts = Counter(indices)
    numerator = sum(c * (c - 1) for c in counts.values())
    denominator = n * (n - 1)
    return 29 * numerator / denominator if denominator > 0 else 0

def score_english(text, words):
    """Score text for English-likeness."""
    score = 0
    
    # Word matching
    for w in words:
        wu = w.upper()
        if wu in COMMON_WORDS:
            score += len(wu) * 10
        # GP variants
        elif wu.replace('C', 'K') in COMMON_WORDS:
            score += len(wu) * 8
        elif wu.replace('U', 'V') in COMMON_WORDS:
            score += len(wu) * 8
        else:
            # Check 3+ letter matches
            if len(wu) >= 3:
                score -= 2
    
    # Bigram scoring on full text
    flat = text.replace(' ', '').replace('.', '')
    for i in range(len(flat) - 1):
        bi = flat[i:i+2]
        if bi in CICADA_BIGRAMS:
            score += CICADA_BIGRAMS[bi]
    
    return score

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i+2) == 0: return False
        i += 6
    return True

def analyze_page_pair(cipher_page, key_page, cipher_num, key_num):
    """Analyze using key_page's runes as key for cipher_page."""
    results = []
    
    cipher_idx, cipher_raw = load_runes(cipher_page)
    key_idx, _ = load_runes(key_page)
    cipher_content = load_runes_with_structure(cipher_page)
    
    if cipher_idx is None or key_idx is None:
        return results
    
    for mode in ['add', 'sub', 'beaufort']:
        plain = decrypt(cipher_idx, key_idx, mode)
        ioc = compute_ioc(plain)
        text, words = to_runeglish_with_structure(cipher_content, key_idx, mode)
        score = score_english(text, words)
        
        results.append({
            'cipher_page': cipher_num,
            'key_page': key_num,
            'mode': mode,
            'ioc': ioc,
            'score': score,
            'text': text[:300],
            'words': words[:50],
            'plain_indices': plain,
        })
    
    return results

def test_p43_p00():
    """Primary test: P43 with P00 as key."""
    print("=" * 80)
    print("P43 + P00 ANALYSIS (Highest IoC signal: 2.0632)")
    print("=" * 80)
    
    # P43 cipher with P00 as key
    results = analyze_page_pair(43, 0, 43, 0)
    for r in sorted(results, key=lambda x: -x['ioc']):
        print(f"\n--- P{r['cipher_page']:02d} cipher, P{r['key_page']:02d} key, mode={r['mode']} ---")
        print(f"IoC: {r['ioc']:.4f} | Score: {r['score']}")
        print(f"Text: {r['text']}")
        print(f"Words (first 20): {r['words'][:20]}")
    
    # Also test reverse: P00 with P43 as key
    print("\n" + "=" * 80)
    print("P00 cipher, P43 as key (reverse)")
    print("=" * 80)
    
    results2 = analyze_page_pair(0, 43, 0, 43)
    for r in sorted(results2, key=lambda x: -x['ioc']):
        print(f"\n--- P{r['cipher_page']:02d} cipher, P{r['key_page']:02d} key, mode={r['mode']} ---")
        print(f"IoC: {r['ioc']:.4f} | Score: {r['score']}")
        print(f"Text: {r['text']}")
        print(f"Words (first 20): {r['words'][:20]}")
    
    return results + results2

def test_p00_as_key_all_unsolved():
    """Test P00 as a running key for all unsolved pages."""
    print("\n" + "=" * 80)
    print("P00 AS KEY FOR ALL UNSOLVED PAGES")
    print("=" * 80)
    
    p00_idx, _ = load_runes(0)
    if p00_idx is None:
        print("ERROR: Could not load P00")
        return
    
    unsolved = list(range(21, 55))  # P21-54
    best_results = []
    
    for pg in unsolved:
        cipher_idx, _ = load_runes(pg)
        cipher_content = load_runes_with_structure(pg)
        if cipher_idx is None:
            continue
        
        best_ioc = 0
        best_mode = None
        best_text = ""
        best_words = []
        
        for mode in ['add', 'sub', 'beaufort']:
            plain = decrypt(cipher_idx, p00_idx, mode)
            ioc = compute_ioc(plain)
            text, words = to_runeglish_with_structure(cipher_content, p00_idx, mode)
            score = score_english(text, words)
            
            if ioc > best_ioc:
                best_ioc = ioc
                best_mode = mode
                best_text = text[:200]
                best_words = words[:20]
                best_score = score
        
        best_results.append({
            'page': pg,
            'ioc': best_ioc,
            'mode': best_mode,
            'score': best_score,
            'text': best_text,
        })
    
    # Sort by IoC
    best_results.sort(key=lambda x: -x['ioc'])
    
    print(f"\n{'Page':>4} | {'Mode':>8} | {'IoC':>7} | {'Score':>6} | Text Preview")
    print("-" * 80)
    for r in best_results[:15]:
        print(f"P{r['page']:02d}  | {r['mode']:>8} | {r['ioc']:.4f} | {r['score']:>6} | {r['text'][:60]}")

def test_1331_triangle():
    """Test 1331 Triangle: P00, P48, P54 (distance sum 1331 from P57/Parable)."""
    print("\n" + "=" * 80)
    print("1331 TRIANGLE (P00, P48, P54) — Parable Key Tests")
    print("=" * 80)
    
    # Load Parable (P57) text as key
    p57_idx, _ = load_runes(57)
    if p57_idx is None:
        # Try P56 (same content)
        p57_idx, _ = load_runes(56)
    
    triangle_pages = [0, 48, 54]
    
    for pg in triangle_pages:
        cipher_idx, _ = load_runes(pg)
        cipher_content = load_runes_with_structure(pg)
        if cipher_idx is None or p57_idx is None:
            continue
        
        print(f"\n--- P{pg:02d} with Parable key ---")
        for mode in ['add', 'sub', 'beaufort']:
            plain = decrypt(cipher_idx, p57_idx, mode)
            ioc = compute_ioc(plain)
            text, words = to_runeglish_with_structure(cipher_content, p57_idx, mode)
            score = score_english(text, words)
            print(f"  {mode:>8}: IoC={ioc:.4f} Score={score:>5} | {text[:80]}")

def test_cross_page_keys():
    """Test various pages as keys for each other."""
    print("\n" + "=" * 80)
    print("CROSS-PAGE KEY TESTS (Unsolved × Unsolved)")
    print("=" * 80)
    
    # Test interesting pairs from tracker hypotheses
    test_pairs = [
        (43, 0), (0, 43),  # P43+P00 (IoC 2.0632)
        (48, 0), (0, 48),  # 1331 triangle
        (54, 0), (0, 54),  # 1331 triangle
        (48, 54), (54, 48), # Within triangle
        (27, 44),  # P27 = P44 first 234 runes (duplicate)
    ]
    
    results = []
    for cipher_pg, key_pg in test_pairs:
        r = analyze_page_pair(cipher_pg, key_pg, cipher_pg, key_pg)
        for res in r:
            results.append(res)
    
    # Sort by IoC
    results.sort(key=lambda x: -x['ioc'])
    
    print(f"\n{'Cipher':>6} | {'Key':>4} | {'Mode':>8} | {'IoC':>7} | {'Score':>6} | Text Preview")
    print("-" * 90)
    for r in results[:20]:
        print(f"P{r['cipher_page']:02d}    | P{r['key_page']:02d} | {r['mode']:>8} | {r['ioc']:.4f} | {r['score']:>6} | {r['text'][:50]}")

def test_verified_keys():
    """Load verified_keys.json and analyze the key patterns for unsolved pages."""
    print("\n" + "=" * 80)
    print("VERIFIED KEYS ANALYSIS")
    print("=" * 80)
    
    vk_path = DATA_DIR / "verified_keys.json"
    if not vk_path.exists():
        print("verified_keys.json not found")
        return
    
    with open(vk_path, 'r') as f:
        vk = json.load(f)
    
    # Analyze key lengths and patterns
    for pg_str in sorted(vk.keys(), key=int):
        pg = int(pg_str)
        if 21 <= pg <= 54:
            key = vk[pg_str]
            klen = len(key)
            
            # Try applying this key
            cipher_idx, _ = load_runes(pg)
            cipher_content = load_runes_with_structure(pg)
            if cipher_idx is None:
                continue
            
            # Decrypt with verified key (SUB mode - most common)
            plain_sub = [(c - k) % 29 for c, k in zip(cipher_idx, key * (len(cipher_idx) // klen + 1))]
            ioc_sub = compute_ioc(plain_sub)
            
            # Also try ADD
            plain_add = [(c + k) % 29 for c, k in zip(cipher_idx, key * (len(cipher_idx) // klen + 1))]
            ioc_add = compute_ioc(plain_add)
            
            best_ioc = max(ioc_sub, ioc_add)
            best_mode = 'sub' if ioc_sub >= ioc_add else 'add'
            best_plain = plain_sub if ioc_sub >= ioc_add else plain_add
            
            text = to_runeglish(best_plain[:60])
            print(f"P{pg:02d}: keylen={klen:>3}, best_mode={best_mode}, IoC={best_ioc:.4f} | {text[:80]}")

def main():
    print("LIBER PRIMUS — Comprehensive Unsolved Page Analysis")
    print("=" * 80)
    
    # Priority 1: P43+P00
    all_results = test_p43_p00()
    
    # Priority 2: P00 as key for all unsolved
    test_p00_as_key_all_unsolved()
    
    # Priority 3: 1331 Triangle
    test_1331_triangle()
    
    # Priority 4: Cross-page keys
    test_cross_page_keys()
    
    # Priority 5: Verified keys analysis
    test_verified_keys()
    
    # Summary of highest IoC results
    print("\n" + "=" * 80)
    print("TOP RESULTS SUMMARY")
    print("=" * 80)
    all_results.sort(key=lambda x: -x['ioc'])
    for r in all_results[:10]:
        print(f"P{r['cipher_page']:02d}×P{r['key_page']:02d} {r['mode']:>8}: IoC={r['ioc']:.4f} Score={r['score']}")
        # Print word-by-word analysis for top results
        if r['ioc'] > 1.5:
            print(f"  Words: {' | '.join(r['words'][:30])}")
            # Check which words match English
            eng_matches = [w for w in r['words'] if w.upper() in COMMON_WORDS or 
                          w.upper().replace('C','K') in COMMON_WORDS or
                          w.upper().replace('U','V') in COMMON_WORDS]
            print(f"  English matches: {eng_matches}")

if __name__ == '__main__':
    main()
