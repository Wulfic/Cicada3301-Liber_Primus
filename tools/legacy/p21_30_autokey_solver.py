#!/usr/bin/env python3
"""
P21-30 Autokey + Running Key Solver

Tests autokey cipher (keyword seeds, then plaintext/ciphertext feedback)
and Deor/Emerson running key combinations with P63 keywords.
"""

import os, json, math
from collections import Counter

GP_RUNE_TO_IDX = {
    'ᚠ':0, 'ᚢ':1, 'ᚦ':2, 'ᚩ':3, 'ᚱ':4, 'ᚳ':5, 'ᚷ':6, 'ᚹ':7,
    'ᚻ':8, 'ᚾ':9, 'ᛁ':10, 'ᛄ':11, 'ᛇ':12, 'ᛈ':13, 'ᛉ':14, 'ᛋ':15,
    'ᛏ':16, 'ᛒ':17, 'ᛖ':18, 'ᛗ':19, 'ᛚ':20, 'ᛝ':21, 'ᛟ':22, 'ᛞ':23,
    'ᚪ':24, 'ᚫ':25, 'ᚣ':26, 'ᛡ':27, 'ᛠ':28
}

IDX_TO_LATIN = {
    0:'F', 1:'U', 2:'TH', 3:'O', 4:'R', 5:'C', 6:'G', 7:'W',
    8:'H', 9:'N', 10:'I', 11:'J', 12:'EO', 13:'P', 14:'X', 15:'S',
    16:'T', 17:'B', 18:'E', 19:'M', 20:'L', 21:'NG', 22:'OE', 23:'D',
    24:'A', 25:'AE', 26:'Y', 27:'IA', 28:'EA'
}

LATIN_TO_IDX = {}
for k, v in IDX_TO_LATIN.items():
    LATIN_TO_IDX[v] = k

PAGE_CONFIG = {
    21: ('CABAL',    'beaufort', [5, 24, 17, 24, 20]),
    22: ('DIVINITY', 'beaufort', [23, 10, 1, 10, 9, 10, 16, 26]),
    23: ('ENCRYPTION','add',    [18, 9, 5, 4, 26, 13, 16, 10, 3, 9]),
    24: ('OBSCURA',  'beaufort', [3, 17, 15, 5, 1, 4, 24]),
    25: ('CABAL',    'beaufort', [5, 24, 17, 24, 20]),
    26: ('ENCRYPT',  'add',     [18, 9, 5, 4, 26, 13, 16]),
    27: ('SHADOWS',  'add',     [15, 8, 24, 23, 3, 7, 15]),
    28: ('DEOR',     'sub',     [23, 18, 3, 4]),
    29: ('TOTIENT',  'beaufort', [16, 3, 16, 10, 18, 9, 16]),
    30: ('MOURNFUL', 'add',     [19, 3, 1, 4, 9, 0, 1, 20]),
}

# Additional keywords from P63 not assigned to specific pages
ALL_KEYWORDS = {
    'CABAL': [5, 24, 17, 24, 20],
    'DIVINITY': [23, 10, 1, 10, 9, 10, 16, 26],
    'ENCRYPTION': [18, 9, 5, 4, 26, 13, 16, 10, 3, 9],
    'OBSCURA': [3, 17, 15, 5, 1, 4, 24],
    'ENCRYPT': [18, 9, 5, 4, 26, 13, 16],
    'SHADOWS': [15, 8, 24, 23, 3, 7, 15],
    'DEOR': [23, 18, 3, 4],
    'TOTIENT': [16, 3, 16, 10, 18, 9, 16],
    'MOURNFUL': [19, 3, 1, 4, 9, 0, 1, 20],
    'VOID': [1, 3, 10, 23],
    'AETHEREAL': [24, 18, 2, 8, 18, 4, 18, 24, 20],
    'CARNAL': [5, 24, 4, 9, 24, 20],
    'ANALOG': [24, 9, 24, 20, 3, 6],
    'BUFFERS': [17, 1, 0, 0, 18, 4, 15],
    'MOBIUS': [19, 3, 17, 10, 1, 15],
    'FORM': [0, 3, 4, 19],
    'CICADA': [5, 10, 5, 24, 23, 24],
    'CONSUMPTION': [5, 3, 9, 15, 1, 19, 13, 16, 10, 3, 9],
}

def parse_runes(text):
    return [GP_RUNE_TO_IDX[ch] for ch in text if ch in GP_RUNE_TO_IDX]

def text_to_indices(text):
    """Convert Latin text to GP indices."""
    result = []
    text = text.upper()
    i = 0
    while i < len(text):
        # Try two-character digraphs first
        if i + 1 < len(text):
            digraph = text[i:i+2]
            if digraph in LATIN_TO_IDX:
                result.append(LATIN_TO_IDX[digraph])
                i += 2
                continue
        # Single character
        ch = text[i]
        if ch in LATIN_TO_IDX:
            result.append(LATIN_TO_IDX[ch])
        elif ch == 'K':
            result.append(LATIN_TO_IDX['C'])  # K -> C
        elif ch == 'V':
            result.append(LATIN_TO_IDX['U'])  # V -> U
        elif ch == 'Q':
            result.append(LATIN_TO_IDX['C'])  # Q -> C
        elif ch == 'Z':
            result.append(LATIN_TO_IDX['S'])  # Z -> S
        i += 1
    return result

def indices_to_text(indices):
    return ''.join(IDX_TO_LATIN[i] for i in indices)

def compute_ioc(indices):
    if len(indices) < 2:
        return 0
    freq = Counter(indices)
    n = len(indices)
    return 29 * sum(c*(c-1) for c in freq.values()) / (n * (n-1))

def load_english_words(path='data/wordlist.txt'):
    try:
        with open(path) as f:
            return set(w.strip().upper() for w in f if 3 <= len(w.strip()) <= 15)
    except:
        return set()

def load_running_key_text(path):
    """Load a running key source text and convert to GP indices."""
    with open(path, encoding='utf-8') as f:
        text = f.read()
    # Remove non-alphabetic
    clean = ''.join(c for c in text if c.isalpha() or c == ' ')
    return text_to_indices(clean)

def score_text(text, wordlist):
    """Score text by finding English words within it (sliding window)."""
    t = text.upper()
    score = 0
    matched = []
    # Try word boundary version
    words = t.replace('.', ' ').split()
    for w in words:
        if w in wordlist:
            score += len(w) ** 2
            matched.append(w)
        # GP transforms
        for transform in [
            lambda x: x.replace('NG', 'ING'),
            lambda x: x.replace('IA', 'ION'),
            lambda x: x.replace('C', 'K'),
            lambda x: x.replace('U', 'V'),
        ]:
            w2 = transform(w)
            if w2 != w and w2 in wordlist:
                score += len(w2) ** 2
                matched.append(w2)
                break
    return score, matched

# ============================================================================
# CIPHER MODES
# ============================================================================

def autokey_decrypt_plaintext_sub(cipher, seed):
    """Autokey: key = seed || plaintext. SUB mode: p = (c - k) mod 29"""
    n = len(cipher)
    kl = len(seed)
    plain = []
    for i in range(n):
        if i < kl:
            k = seed[i]
        else:
            k = plain[i - kl]
        plain.append((cipher[i] - k) % 29)
    return plain

def autokey_decrypt_plaintext_add(cipher, seed):
    """Autokey: key = seed || plaintext. ADD mode: p = (c + k) mod 29"""
    n = len(cipher)
    kl = len(seed)
    plain = []
    for i in range(n):
        if i < kl:
            k = seed[i]
        else:
            k = plain[i - kl]
        plain.append((cipher[i] + k) % 29)
    return plain

def autokey_decrypt_plaintext_beaufort(cipher, seed):
    """Autokey: key = seed || plaintext. Beaufort: p = (k - c) mod 29"""
    n = len(cipher)
    kl = len(seed)
    plain = []
    for i in range(n):
        if i < kl:
            k = seed[i]
        else:
            k = plain[i - kl]
        plain.append((k - cipher[i]) % 29)
    return plain

def autokey_decrypt_cipher_sub(cipher, seed):
    """Autokey (cipher-feedback): key = seed || ciphertext. SUB: p = (c - k) mod 29"""
    n = len(cipher)
    kl = len(seed)
    plain = []
    for i in range(n):
        if i < kl:
            k = seed[i]
        else:
            k = cipher[i - kl]
        plain.append((cipher[i] - k) % 29)
    return plain

def autokey_decrypt_cipher_add(cipher, seed):
    """Autokey (cipher-feedback): key = seed || ciphertext. ADD: p = (c + k) mod 29"""
    n = len(cipher)
    kl = len(seed)
    plain = []
    for i in range(n):
        if i < kl:
            k = seed[i]
        else:
            k = cipher[i - kl]
        plain.append((cipher[i] + k) % 29)
    return plain

def autokey_decrypt_cipher_beaufort(cipher, seed):
    """Autokey (cipher-feedback): key = seed || ciphertext. Beaufort: p = (k - c) mod 29"""
    n = len(cipher)
    kl = len(seed)
    plain = []
    for i in range(n):
        if i < kl:
            k = seed[i]
        else:
            k = cipher[i - kl]
        plain.append((k - cipher[i]) % 29)
    return plain

def running_key_decrypt(cipher, running_key, offset, mode):
    """Decrypt with a running key at given offset."""
    n = len(cipher)
    rk = running_key[offset:offset+n]
    if len(rk) < n:
        return None
    plain = []
    for i in range(n):
        c = cipher[i]
        k = rk[i]
        if mode == 'sub':
            plain.append((c - k) % 29)
        elif mode == 'add':
            plain.append((c + k) % 29)
        elif mode == 'beaufort':
            plain.append((k - c) % 29)
    return plain


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(base_dir)
    
    wordlist = load_english_words()
    print(f"Loaded {len(wordlist)} English words (3+ chars)")
    
    # Load running key sources
    running_keys = {}
    for name, path in [
        ('deor', 'data/deor_poem.txt'),
        ('self_reliance', 'data/self_reliance.txt'),
    ]:
        if os.path.exists(path):
            running_keys[name] = load_running_key_text(path)
            print(f"Loaded {name}: {len(running_keys[name])} GP indices")
    
    # Track best results per page
    best_results = {}
    
    for page in range(21, 31):
        keyword_name, tracker_mode, keyword_indices = PAGE_CONFIG[page]
        
        rune_path = f'pages/page_{page:02d}/runes.txt'
        if not os.path.exists(rune_path):
            continue
        
        with open(rune_path, encoding='utf-8') as f:
            rune_text = f.read().strip()
        
        cipher = parse_runes(rune_text)
        # Also keep word structure for scoring
        words_raw = []
        current = []
        for ch in rune_text:
            if ch in GP_RUNE_TO_IDX:
                current.append(GP_RUNE_TO_IDX[ch])
            elif ch in '-. ':
                if current:
                    words_raw.append(current)
                    current = []
        if current:
            words_raw.append(current)
        
        print(f"\n{'='*70}")
        print(f"PAGE {page}: {len(cipher)} runes, Keyword={keyword_name}")
        print(f"{'='*70}")
        
        page_results = []
        
        # ========== AUTOKEY TESTS ==========
        autokey_fns = [
            ('autokey_pt_sub', autokey_decrypt_plaintext_sub),
            ('autokey_pt_add', autokey_decrypt_plaintext_add),
            ('autokey_pt_beau', autokey_decrypt_plaintext_beaufort),
            ('autokey_ct_sub', autokey_decrypt_cipher_sub),
            ('autokey_ct_add', autokey_decrypt_cipher_add),
            ('autokey_ct_beau', autokey_decrypt_cipher_beaufort),
        ]
        
        # Test with assigned keyword AND all other keywords
        keywords_to_test = {keyword_name: keyword_indices}
        for kn, ki in ALL_KEYWORDS.items():
            if kn != keyword_name:
                keywords_to_test[kn] = ki
        
        for kw_name, kw_idx in keywords_to_test.items():
            for fn_name, fn in autokey_fns:
                dec = fn(cipher, kw_idx)
                ioc = compute_ioc(dec)
                
                if ioc > 1.3:  # Threshold for interesting results
                    # Reconstruct with word boundaries
                    dec_words = []
                    pos = 0
                    for w in words_raw:
                        dec_words.append(dec[pos:pos+len(w)])
                        pos += len(w)
                    txt = ' '.join(indices_to_text(w) for w in dec_words)
                    sc, mt = score_text(txt, wordlist)
                    label = f"{fn_name}({kw_name})"
                    page_results.append((ioc, sc, label, txt[:200], mt[:10]))
        
        # ========== RUNNING KEY TESTS ==========
        for rk_name, rk_indices in running_keys.items():
            max_offset = len(rk_indices) - len(cipher)
            if max_offset < 0:
                continue
            
            # Coarse sweep
            step = max(1, max_offset // 200)
            for offset in range(0, max_offset, step):
                for mode in ['sub', 'add', 'beaufort']:
                    dec = running_key_decrypt(cipher, rk_indices, offset, mode)
                    if dec is None:
                        continue
                    ioc = compute_ioc(dec)
                    
                    if ioc > 1.3:
                        dec_words = []
                        pos = 0
                        for w in words_raw:
                            dec_words.append(dec[pos:pos+len(w)])
                            pos += len(w)
                        txt = ' '.join(indices_to_text(w) for w in dec_words)
                        sc, mt = score_text(txt, wordlist)
                        label = f"rk_{rk_name}(off={offset},{mode})"
                        page_results.append((ioc, sc, label, txt[:200], mt[:10]))
        
        # ========== COMBINED: KEYWORD VIGENERE + RUNNING KEY ==========
        for kw_name, kw_idx in [(keyword_name, keyword_indices)]:
            for rk_name, rk_indices in running_keys.items():
                max_offset = len(rk_indices) - len(cipher)
                if max_offset < 0:
                    continue
                
                step = max(1, max_offset // 100)
                for offset in range(0, max_offset, step):
                    # Combined key = keyword + running key
                    for kw_mode in ['sub', 'add', 'beaufort']:
                        for rk_mode in ['sub', 'add']:
                            # First apply keyword, then running key
                            combined_key = []
                            for i in range(len(cipher)):
                                kw = kw_idx[i % len(kw_idx)]
                                rk = rk_indices[offset + i] if (offset + i) < len(rk_indices) else 0
                                if rk_mode == 'add':
                                    combined_key.append((kw + rk) % 29)
                                else:
                                    combined_key.append((kw - rk) % 29)
                            
                            dec = []
                            for i in range(len(cipher)):
                                c = cipher[i]
                                k = combined_key[i]
                                if kw_mode == 'sub':
                                    dec.append((c - k) % 29)
                                elif kw_mode == 'add':
                                    dec.append((c + k) % 29)
                                elif kw_mode == 'beaufort':
                                    dec.append((k - c) % 29)
                            
                            ioc = compute_ioc(dec)
                            if ioc > 1.3:
                                dec_words = []
                                pos = 0
                                for w in words_raw:
                                    dec_words.append(dec[pos:pos+len(w)])
                                    pos += len(w)
                                txt = ' '.join(indices_to_text(w) for w in dec_words)
                                sc, mt = score_text(txt, wordlist)
                                label = f"kw({kw_name})+rk_{rk_name}(off={offset},{kw_mode}/{rk_mode})"
                                page_results.append((ioc, sc, label, txt[:200], mt[:10]))
        
        # Sort by IoC, then score
        page_results.sort(key=lambda x: (-x[1], -x[0]))
        
        if page_results:
            print(f"\n  Top results (IoC > 1.3):")
            shown = set()
            count = 0
            for ioc, sc, label, txt, mt in page_results:
                if count >= 15:
                    break
                # Deduplicate similar results
                sig = txt[:50]
                if sig in shown:
                    continue
                shown.add(sig)
                count += 1
                print(f"  IoC={ioc:.4f} Score={sc:4d} [{label}]")
                print(f"    {txt[:150]}")
                if mt:
                    print(f"    Words: {mt}")
        else:
            print(f"  No results with IoC > 1.3")
        
        best_results[page] = page_results[:5] if page_results else []
    
    # Final summary
    print(f"\n\n{'='*70}")
    print("OVERALL BEST RESULTS")
    print(f"{'='*70}")
    all_sorted = []
    for page, results in best_results.items():
        for ioc, sc, label, txt, mt in results:
            all_sorted.append((sc, ioc, page, label, txt, mt))
    all_sorted.sort(reverse=True)
    for sc, ioc, page, label, txt, mt in all_sorted[:20]:
        print(f"  P{page} Score={sc:4d} IoC={ioc:.4f} [{label}]")
        if mt:
            print(f"    Words: {mt}")

if __name__ == '__main__':
    main()
