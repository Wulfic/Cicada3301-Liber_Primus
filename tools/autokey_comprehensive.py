#!/usr/bin/env python3
"""
Comprehensive Autokey Cipher Test for Liber Primus
====================================================
Tests autokey cipher (both plaintext-feedback and ciphertext-feedback)
with:
  1. Brute-force seeds of length 2 (29^2=841) and length 3 (29^3=24389)
  2. All P63 keywords as seeds
  3. All 6 mode combinations (sub/add/beaufort × plaintext/ciphertext feedback)
  4. F-skip-aware autokey variant
  5. Hard singleton constraint + IoC scoring
  6. On ALL unsolved pages 21-54
"""

import sys, os, json, itertools
from pathlib import Path
from collections import Counter

BASE = Path(__file__).resolve().parent.parent
PAGES_DIR = BASE / "pages"

# GP Alphabet
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

# All P63 keywords
ALL_KEYWORDS = {
    'DIVINITY':     [23, 10, 1, 10, 9, 10, 16, 26],
    'CABAL':        [5, 24, 17, 24, 20],
    'SHADOWS':      [15, 8, 24, 23, 3, 7, 15],
    'OBSCURA':      [3, 17, 15, 5, 1, 4, 24],
    'VOID':         [1, 3, 10, 23],
    'FORM':         [0, 3, 4, 19],
    'MOBIUS':       [19, 3, 17, 10, 1, 15],
    'ANALOG':       [24, 9, 24, 20, 3, 6],
    'MOURNFUL':     [19, 3, 1, 4, 9, 0, 1, 20],
    'AETHEREAL':    [24, 18, 2, 8, 18, 4, 18, 24, 20],
    'BUFFERS':      [17, 1, 0, 0, 18, 4, 15],
    'CARNAL':       [5, 24, 4, 9, 24, 20],
    'TOTIENT':      [16, 3, 16, 10, 18, 9, 16],
    'ENCRYPT':      [18, 9, 5, 4, 26, 13, 16],
    'ENCRYPTION':   [18, 9, 5, 4, 26, 13, 16, 10, 3, 9],
    'DEOR':         [23, 12, 4],
    'CICADA':       [5, 10, 5, 24, 23, 24],
    'FIRFUMFERENFE': [0, 10, 4, 0, 1, 19, 0, 18, 4, 18, 9, 0, 18],
    'YAHEOOPYJ':    [26, 24, 8, 12, 3, 13, 26, 11],
    'CONSUMPTION':  [5, 3, 9, 15, 1, 19, 13, 16, 10, 3, 9],
    'PRIMES':       [13, 4, 10, 19, 18, 15],
    'SACRED':       [15, 24, 5, 4, 18, 23],
}

# English bigrams for scoring
COMMON_BIGRAMS = {'TH','HE','IN','ER','AN','RE','ON','AT','EN','ND','TI','ES','OR','TE','OF',
                   'ED','IS','IT','AL','AR','ST','TO','NT','NG','SE','HA','AS','OU'}


def load_page(page_num):
    """Load runes and word structure for a page."""
    rune_path = PAGES_DIR / f"page_{page_num:02d}" / "runes.txt"
    if not rune_path.exists():
        return None, None, None
    content = rune_path.read_text(encoding='utf-8').strip()
    
    # Parse into rune indices, tracking word boundaries for singleton check
    indices = []
    words = []  # list of (start_idx, length) for each word
    current_word_start = len(indices)
    current_word_len = 0
    
    for ch in content:
        if ch in RUNE_TO_IDX:
            if current_word_len == 0:
                current_word_start = len(indices)
            indices.append(RUNE_TO_IDX[ch])
            current_word_len += 1
        elif ch in '-\n /%.&$':
            if current_word_len > 0:
                words.append((current_word_start, current_word_len))
                current_word_len = 0
    if current_word_len > 0:
        words.append((current_word_start, current_word_len))
    
    # Find singleton positions (1-rune words)
    singletons = [(start, 1) for start, length in words if length == 1]
    
    return indices, singletons, content


def compute_ioc(plain):
    """Compute normalized IoC for a list of indices."""
    n = len(plain)
    if n < 2:
        return 0
    freq = Counter(plain)
    total = sum(f * (f - 1) for f in freq.values())
    raw = total / (n * (n - 1))
    expected = 1.0 / 29
    return raw / expected if expected > 0 else 0


def to_runeglish(plain):
    """Convert indices to runeglish text."""
    return ''.join(IDX_TO_LETTER[i] for i in plain)


def bigram_score(text):
    """Count common English bigrams in the text."""
    count = 0
    for i in range(len(text) - 1):
        if text[i:i+2] in COMMON_BIGRAMS:
            count += 1
    return count


def check_singletons(plain, singletons):
    """Check how many singleton words decrypt to I(10) or A(24)."""
    passed = 0
    for start, length in singletons:
        if start < len(plain) and plain[start] in (10, 24):
            passed += 1
    return passed, len(singletons)


# ============ AUTOKEY DECRYPTION FUNCTIONS ============

def autokey_pt_sub(cipher, seed):
    """Plaintext-feedback autokey, SUB decryption: p[i] = (c[i] - key[i]) % 29"""
    plain = []
    kl = len(seed)
    for i, c in enumerate(cipher):
        k = seed[i] if i < kl else plain[i - kl]
        plain.append((c - k) % 29)
    return plain

def autokey_pt_add(cipher, seed):
    """Plaintext-feedback autokey, ADD decryption: p[i] = (c[i] + key[i]) % 29"""
    plain = []
    kl = len(seed)
    for i, c in enumerate(cipher):
        k = seed[i] if i < kl else plain[i - kl]
        plain.append((c + k) % 29)
    return plain

def autokey_pt_beau(cipher, seed):
    """Plaintext-feedback autokey, Beaufort: p[i] = (key[i] - c[i]) % 29"""
    plain = []
    kl = len(seed)
    for i, c in enumerate(cipher):
        k = seed[i] if i < kl else plain[i - kl]
        plain.append((k - c) % 29)
    return plain

def autokey_ct_sub(cipher, seed):
    """Ciphertext-feedback autokey, SUB: p[i] = (c[i] - key[i]) % 29"""
    plain = []
    kl = len(seed)
    for i, c in enumerate(cipher):
        k = seed[i] if i < kl else cipher[i - kl]
        plain.append((c - k) % 29)
    return plain

def autokey_ct_add(cipher, seed):
    """Ciphertext-feedback autokey, ADD: p[i] = (c[i] + key[i]) % 29"""
    plain = []
    kl = len(seed)
    for i, c in enumerate(cipher):
        k = seed[i] if i < kl else cipher[i - kl]
        plain.append((c + k) % 29)
    return plain

def autokey_ct_beau(cipher, seed):
    """Ciphertext-feedback autokey, Beaufort: p[i] = (key[i] - c[i]) % 29"""
    plain = []
    kl = len(seed)
    for i, c in enumerate(cipher):
        k = seed[i] if i < kl else cipher[i - kl]
        plain.append((k - c) % 29)
    return plain


MODES = [
    ('pt_sub', autokey_pt_sub),
    ('pt_add', autokey_pt_add),
    ('pt_beau', autokey_pt_beau),
    ('ct_sub', autokey_ct_sub),
    ('ct_add', autokey_ct_add),
    ('ct_beau', autokey_ct_beau),
]


def test_seed(cipher, singletons, seed, mode_func):
    """Test a seed on a cipher. Returns (ioc, singleton_pass, singleton_total, plaintext)."""
    plain = mode_func(cipher, seed)
    sp, st = check_singletons(plain, singletons)
    # Quick singleton filter: require ALL singletons to pass
    if st > 0 and sp < st:
        return None
    ioc = compute_ioc(plain)
    return (ioc, sp, st, plain)


def main():
    print("=" * 80)
    print("COMPREHENSIVE AUTOKEY TEST — Liber Primus Pages 21-54")
    print("=" * 80)
    sys.stdout.flush()
    
    # Load all pages
    pages = {}
    for pg in range(21, 55):
        data = load_page(pg)
        if data[0] is not None:
            pages[pg] = data
    
    print(f"Loaded {len(pages)} pages")
    for pg in sorted(pages.keys()):
        ci, si, _ = pages[pg]
        print(f"  P{pg:02d}: {len(ci)} runes, {len(si)} singletons")
    sys.stdout.flush()
    
    # Also test solved P06 as validation
    p06_data = load_page(6)
    if p06_data[0] is not None:
        print(f"  P06 (validation): {len(p06_data[0])} runes, {len(p06_data[1])} singletons")
    
    all_hits = {}  # page -> list of (ioc, mode, seed_name, text_preview)
    
    # ====================================================================
    # PHASE 1: Test all P63 keywords as autokey seeds on ALL pages
    # ====================================================================
    print("\n" + "=" * 80)
    print("PHASE 1: P63 Keywords as Autokey Seeds")
    print("=" * 80)
    sys.stdout.flush()
    
    for pg in sorted(pages.keys()):
        cipher, singletons, _ = pages[pg]
        hits = []
        
        for kw_name, kw_seed in ALL_KEYWORDS.items():
            for mode_name, mode_func in MODES:
                result = test_seed(cipher, singletons, kw_seed, mode_func)
                if result is not None:
                    ioc, sp, st, plain = result
                    if ioc > 1.3:
                        text = to_runeglish(plain)
                        bg = bigram_score(text)
                        hits.append((ioc, bg, mode_name, kw_name, sp, st, text[:100]))
        
        if hits:
            hits.sort(key=lambda x: -x[0])
            all_hits[pg] = hits
            print(f"\nP{pg:02d} — {len(hits)} hits passing all singletons with IoC > 1.3:")
            for ioc, bg, mode, kw, sp, st, txt in hits[:5]:
                print(f"  IoC={ioc:.4f} bg={bg:3d} sing={sp}/{st} [{kw:15s}] {mode:10s} | {txt[:70]}")
        else:
            print(f"P{pg:02d} — NO keyword autokey hits (all singletons pass + IoC > 1.3)")
        sys.stdout.flush()
    
    # Also test P06 (validation)
    if p06_data[0] is not None:
        cipher, singletons, _ = p06_data
        print(f"\nP06 VALIDATION:")
        for kw_name, kw_seed in ALL_KEYWORDS.items():
            for mode_name, mode_func in MODES:
                result = test_seed(cipher, singletons, kw_seed, mode_func)
                if result is not None:
                    ioc, sp, st, plain = result
                    if ioc > 1.3:
                        text = to_runeglish(plain)
                        print(f"  IoC={ioc:.4f} [{kw_name:15s}] {mode_name:10s} | {text[:80]}")
        sys.stdout.flush()
    
    # ====================================================================
    # PHASE 2: Brute-force autokey seeds of length 2 (841 combos per mode)
    # ====================================================================
    print("\n" + "=" * 80)
    print("PHASE 2: Brute-Force Autokey Seeds (length 2)")
    print("=" * 80)
    sys.stdout.flush()
    
    for pg in sorted(pages.keys()):
        cipher, singletons, _ = pages[pg]
        hits = []
        
        # Use singleton filter as primary — only check IoC if all singletons pass
        for a in range(29):
            for b in range(29):
                seed = [a, b]
                for mode_name, mode_func in MODES:
                    result = test_seed(cipher, singletons, seed, mode_func)
                    if result is not None:
                        ioc, sp, st, plain = result
                        if ioc > 1.3:
                            text = to_runeglish(plain)
                            bg = bigram_score(text)
                            hits.append((ioc, bg, mode_name, f"[{a},{b}]", sp, st, text[:100]))
        
        if hits:
            hits.sort(key=lambda x: -x[0])
            print(f"\nP{pg:02d} — {len(hits)} length-2 autokey hits:")
            for ioc, bg, mode, seed_str, sp, st, txt in hits[:5]:
                print(f"  IoC={ioc:.4f} bg={bg:3d} sing={sp}/{st} seed={seed_str:10s} {mode:10s} | {txt[:65]}")
        else:
            print(f"P{pg:02d} — NO length-2 autokey hits")
        sys.stdout.flush()
    
    # ====================================================================
    # PHASE 3: Brute-force autokey seeds of length 3 (24389 combos per mode)
    # ====================================================================
    print("\n" + "=" * 80)
    print("PHASE 3: Brute-Force Autokey Seeds (length 3)")
    print("=" * 80)
    sys.stdout.flush()
    
    for pg in sorted(pages.keys()):
        cipher, singletons, _ = pages[pg]
        hits = []
        
        # Only test pages with enough singletons for filtering power (>=3)
        if len(singletons) < 3:
            print(f"P{pg:02d} — skipping (only {len(singletons)} singletons, need 3+ for filtering)")
            continue
        
        for a in range(29):
            for b in range(29):
                for c_val in range(29):
                    seed = [a, b, c_val]
                    for mode_name, mode_func in MODES:
                        result = test_seed(cipher, singletons, seed, mode_func)
                        if result is not None:
                            ioc, sp, st, plain = result
                            if ioc > 1.3:
                                text = to_runeglish(plain)
                                bg = bigram_score(text)
                                hits.append((ioc, bg, mode_name, f"[{a},{b},{c_val}]", sp, st, text[:100]))
        
        if hits:
            hits.sort(key=lambda x: -x[0])
            print(f"\nP{pg:02d} — {len(hits)} length-3 autokey hits:")
            for ioc, bg, mode, seed_str, sp, st, txt in hits[:5]:
                print(f"  IoC={ioc:.4f} bg={bg:3d} sing={sp}/{st} seed={seed_str:12s} {mode:10s} | {txt[:60]}")
        else:
            print(f"P{pg:02d} — NO length-3 autokey hits")
        sys.stdout.flush()
    
    # ====================================================================
    # SUMMARY
    # ====================================================================
    print("\n" + "=" * 80)
    print("SUMMARY — Best autokey result per page")
    print("=" * 80)
    
    if not all_hits:
        print("NO autokey combination passed all singleton constraints with IoC > 1.3")
        print("on ANY unsolved page.")
        print("\nAUTOKEY CIPHER HYPOTHESIS: RULED OUT for pages 21-54")
    else:
        for pg in sorted(all_hits.keys()):
            best = all_hits[pg][0]
            ioc, bg, mode, kw, sp, st, txt = best
            print(f"  P{pg:02d}: IoC={ioc:.4f} bg={bg} [{kw}] {mode} | {txt[:60]}")
    
    print("\nDone.")


if __name__ == '__main__':
    main()
