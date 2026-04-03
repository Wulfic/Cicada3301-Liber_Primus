#!/usr/bin/env python3
"""
Deep analysis of promising pages: P39 (IoC 1.63 with verified key SUB) and P54 (IoC 13.01).
Also re-examine all pages with word-boundary-aware output.
"""
import json, os, sys
from collections import Counter

GP = [
    ('F', 'F', 2),   ('U', 'U', 3),   ('TH', 'TH', 5),  ('O', 'O', 7),
    ('R', 'R', 11),   ('CK', 'CK', 13),  ('G', 'G', 17),  ('W', 'W', 19),
    ('H', 'H', 23),   ('N', 'N', 29),   ('I', 'I', 31),   ('J', 'J', 37),
    ('EO', 'EO', 41),  ('P', 'P', 43),   ('X', 'X', 47),   ('S', 'S', 53),
    ('T', 'T', 59),   ('B', 'B', 61),   ('E', 'E', 67),   ('M', 'M', 71),
    ('L', 'L', 73),   ('NG', 'NG', 79),  ('OE', 'OE', 83),  ('D', 'D', 89),
    ('A', 'A', 97),   ('AE', 'AE', 101), ('Y', 'Y', 103),  ('IA', 'IA', 107),
    ('EA', 'EA', 109),
]

RUNE_CHARS = [
    '\u16A0', '\u16A2', '\u16A6', '\u16A9', '\u16B1', '\u16B3', '\u16B7', '\u16B9',
    '\u16BB', '\u16BE', '\u16C1', '\u16C2', '\u16C7', '\u16C8', '\u16C9', '\u16CB',
    '\u16CF', '\u16D2', '\u16D6', '\u16D7', '\u16DA', '\u16DD', '\u16DF', '\u16DE',
    '\u16AA', '\u16AB', '\u16A3', '\u16E1', '\u16E0',
]

RUNE_TO_IDX = {r: i for i, r in enumerate(RUNE_CHARS)}
IDX_TO_LATIN = [gp[0] for gp in GP]
SEPARATORS = set('.:;\'-')

def load_page_runes(page_num):
    """Load rune data from runeglish file and parse into (rune_indices, words_with_seps)."""
    base = os.path.join(os.path.dirname(__file__), '..', 'data', 'runeglish')
    path = os.path.join(base, f'page_{page_num:02d}_runeglish.txt')
    if not os.path.exists(path):
        return None, None, None
    
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read().strip()
    
    LATIN_TO_IDX = {}
    for i, gp in enumerate(GP):
        LATIN_TO_IDX[gp[0]] = i
    
    rune_indices = []
    words = []       # list of lists of indices
    word_seps = []   # separator after each word
    current_word = []
    
    pos = 0
    while pos < len(text):
        ch = text[pos]
        if ch in '-.\n/' or ch == ' ':
            if current_word:
                words.append(current_word[:])
                word_seps.append(ch if ch in '-.' else ' ')
                current_word = []
            pos += 1
        else:
            matched = False
            if pos + 1 < len(text):
                digraph = text[pos:pos+2].upper()
                if digraph in LATIN_TO_IDX:
                    idx = LATIN_TO_IDX[digraph]
                    rune_indices.append(idx)
                    current_word.append(idx)
                    pos += 2
                    matched = True
            if not matched:
                ch_upper = ch.upper()
                if ch_upper in LATIN_TO_IDX:
                    idx = LATIN_TO_IDX[ch_upper]
                    rune_indices.append(idx)
                    current_word.append(idx)
                pos += 1
    
    if current_word:
        words.append(current_word[:])
        word_seps.append('')
    
    # Compute word start positions
    word_positions = []
    p = 0
    for w in words:
        word_positions.append(p)
        p += len(w)
    
    return rune_indices, words, word_positions

def load_page_runes_from_dir(page_num):
    """Try to load from pages/page_XX/runes.txt (raw rune text)."""
    page_dir = os.path.join(os.path.dirname(__file__), '..', 'pages', f'page_{page_num:02d}')
    rune_file = os.path.join(page_dir, 'runes.txt')
    if not os.path.exists(rune_file):
        return None, None, None
        
    with open(rune_file, 'r', encoding='utf-8') as f:
        text = f.read().strip()
    
    rune_indices = []
    words = []
    current_word = []
    word_positions = []
    
    for ch in text:
        if ch in RUNE_TO_IDX:
            idx = RUNE_TO_IDX[ch]
            if not current_word:
                word_positions.append(len(rune_indices))
            rune_indices.append(idx)
            current_word.append(idx)
        elif ch in SEPARATORS or ch == '\n' or ch == ' ' or ch == '\u2022':
            if current_word:
                words.append(current_word[:])
                current_word = []
    
    if current_word:
        word_positions.append(len(rune_indices) - len(current_word))
        words.append(current_word[:])
    
    return rune_indices, words, word_positions

def compute_ioc(indices):
    if len(indices) < 2:
        return 0.0
    counts = Counter(indices)
    n = len(indices)
    total = sum(c * (c - 1) for c in counts.values())
    return total / (n * (n - 1)) * 29

def decrypt_sub(cipher, key, f_skip=False):
    result = []
    kp = 0
    for c in cipher:
        k = key[kp % len(key)]
        p = (c - k) % 29
        result.append(p)
        if f_skip:
            if p != 0: kp += 1
        else:
            kp += 1
    return result

def decrypt_add(cipher, key, f_skip=False):
    result = []
    kp = 0
    for c in cipher:
        k = key[kp % len(key)]
        p = (c + k) % 29
        result.append(p)
        if f_skip:
            if p != 0: kp += 1
        else:
            kp += 1
    return result

def decrypt_beaufort(cipher, key, f_skip=False):
    result = []
    kp = 0
    for c in cipher:
        k = key[kp % len(key)]
        p = (k - c) % 29
        result.append(p)
        if f_skip:
            if p != 0: kp += 1
        else:
            kp += 1
    return result

def to_text(indices):
    return ''.join(IDX_TO_LATIN[i] for i in indices)

def to_text_with_words(words_plain):
    """Convert word list to text with spaces."""
    return ' '.join(''.join(IDX_TO_LATIN[i] for i in w) for w in words_plain)

def decrypt_words(rune_indices, words, word_positions, key, mode='sub', f_skip=False):
    """Decrypt full rune stream and split back into words."""
    fn = {'sub': decrypt_sub, 'add': decrypt_add, 'beaufort': decrypt_beaufort}[mode]
    plain_all = fn(rune_indices, key, f_skip=f_skip)
    
    plain_words = []
    for i, w in enumerate(words):
        start = word_positions[i]
        end = start + len(w)
        plain_words.append(plain_all[start:end])
    
    return plain_all, plain_words

def main():
    keys_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'verified_keys.json')
    with open(keys_file, 'r') as f:
        verified_keys = json.load(f)
    
    sys.stdout.reconfigure(encoding='utf-8')
    
    # =============================
    # DEEP ANALYSIS: PAGE 39
    # =============================
    print("=" * 80)
    print("DEEP ANALYSIS: PAGE 39 (IoC 1.63 with verified key SUB)")
    print("=" * 80)
    
    for pn in [39]:
        rune_indices, words, word_positions = load_page_runes(pn)
        if rune_indices is None:
            rune_indices, words, word_positions = load_page_runes_from_dir(pn)
        if rune_indices is None:
            print(f"No data for page {pn}")
            continue
        
        key = verified_keys[str(pn)]
        print(f"\nPage {pn}: {len(rune_indices)} runes, {len(words)} words, key len {len(key)}")
        print(f"Key: {key}")
        
        for mode in ['sub', 'add', 'beaufort']:
            for fs in [False, True]:
                plain_all, plain_words = decrypt_words(rune_indices, words, word_positions, key, mode, fs)
                ioc = compute_ioc(plain_all)
                text = to_text_with_words(plain_words)
                
                fs_str = "+FSKIP" if fs else ""
                if ioc > 1.2:
                    print(f"\n  {mode.upper()}{fs_str}: IoC={ioc:.2f}")
                    print(f"  Full text with word boundaries:")
                    print(f"  {text}")
                    
                    # Check single-rune words
                    for i, w in enumerate(words):
                        if len(w) == 1:
                            pv = plain_all[word_positions[i]]
                            print(f"    SRW at word {i}: cipher={w[0]} -> plain={pv} ({IDX_TO_LATIN[pv]})")
    
    # =============================
    # DEEP ANALYSIS: PAGE 54
    # =============================
    print("\n" + "=" * 80)
    print("DEEP ANALYSIS: PAGE 54")
    print("=" * 80)
    
    for pn in [54]:
        rune_indices, words, word_positions = load_page_runes(pn)
        if rune_indices is None:
            rune_indices, words, word_positions = load_page_runes_from_dir(pn)
        if rune_indices is None:
            print(f"No data for page {pn}")
            continue
        
        key = verified_keys[str(pn)]
        print(f"\nPage {pn}: {len(rune_indices)} runes, {len(words)} words, key len {len(key)}")
        print(f"Key: {key}")
        
        for mode in ['sub', 'add', 'beaufort']:
            for fs in [False, True]:
                plain_all, plain_words = decrypt_words(rune_indices, words, word_positions, key, mode, fs)
                ioc = compute_ioc(plain_all)
                text = to_text_with_words(plain_words)
                
                fs_str = "+FSKIP" if fs else ""
                print(f"\n  {mode.upper()}{fs_str}: IoC={ioc:.2f}")
                print(f"  {text}")
                
                for i, w in enumerate(words):
                    if len(w) == 1:
                        pv = plain_all[word_positions[i]]
                        print(f"    SRW at word {i}: cipher={w[0]} -> plain={pv} ({IDX_TO_LATIN[pv]})")
    
    # =============================
    # CHECK: IS P54 KEY TRIVIAL?
    # =============================
    print("\n" + "=" * 80)
    print("KEY ANALYSIS")
    print("=" * 80)
    
    for pn in [39, 54]:
        key = verified_keys[str(pn)]
        print(f"\nPage {pn} key (len {len(key)}): {key}")
        counts = Counter(key)
        print(f"  Value distribution: {dict(sorted(counts.items()))}")
        print(f"  Unique values: {len(counts)}")
        print(f"  Most common: {counts.most_common(5)}")
    
    # =============================
    # CHECK RAW RUNE FREQUENCIES
    # =============================
    print("\n" + "=" * 80)
    print("RAW CIPHER FREQUENCIES (before decryption)")
    print("=" * 80)
    
    for pn in [39, 54]:
        rune_indices, words, word_positions = load_page_runes(pn)
        if rune_indices is None:
            rune_indices, words, word_positions = load_page_runes_from_dir(pn)
        if rune_indices is None:
            continue
        
        counts = Counter(rune_indices)
        ioc = compute_ioc(rune_indices)
        print(f"\nPage {pn}: {len(rune_indices)} runes, raw IoC={ioc:.2f}")
        
        sorted_counts = sorted(counts.items(), key=lambda x: -x[1])
        for idx, cnt in sorted_counts:
            pct = cnt / len(rune_indices) * 100
            print(f"  {IDX_TO_LATIN[idx]:3s} (idx {idx:2d}): {cnt:3d} ({pct:.1f}%)")
    
    # =============================
    # ALL PAGES QUICK SCAN WITH WORD TEXT
    # =============================
    print("\n" + "=" * 80)
    print("ALL PAGES: BEST IoC WITH VERIFIED KEYS")
    print("=" * 80)
    
    results = []
    for pn in range(21, 55):
        rune_indices, words, word_positions = load_page_runes(pn)
        if rune_indices is None:
            rune_indices, words, word_positions = load_page_runes_from_dir(pn)
        if rune_indices is None or str(pn) not in verified_keys:
            continue
        
        key = verified_keys[str(pn)]
        best_ioc = 0
        best_mode = ""
        best_text = ""
        
        for mode in ['sub', 'add', 'beaufort']:
            for fs in [False, True]:
                plain_all, plain_words = decrypt_words(rune_indices, words, word_positions, key, mode, fs)
                ioc = compute_ioc(plain_all)
                if ioc > best_ioc:
                    best_ioc = ioc
                    best_mode = f"{mode.upper()}{'+FS' if fs else ''}"
                    best_text = to_text_with_words(plain_words)
        
        results.append((pn, best_ioc, best_mode, best_text))
    
    results.sort(key=lambda x: -x[1])
    for pn, ioc, mode, text in results:
        print(f"\n  Page {pn:2d} | {mode:12s} | IoC={ioc:.2f}")
        print(f"    {text[:200]}")

if __name__ == '__main__':
    main()
