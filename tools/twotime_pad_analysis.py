#!/usr/bin/env python3
"""
Two-Time Pad Detection & Running Key Analysis for Liber Primus
================================================================
If two pages share the same key stream, then C1 - C2 = P1 - P2,
which will have IoC significantly above 1.0 (since both P1 and P2
are English text).

Also tests:
1. Pairwise ciphertext differences (two-time pad detection)
2. Solved LP plaintext as running key for unsolved pages 
3. LP2 solved plaintext as running key for unsolved pages
4. Key stream extraction from P27=P44[0:234] relationship
"""

import sys, json
from pathlib import Path
from collections import Counter

BASE = Path(__file__).resolve().parent.parent
PAGES_DIR = BASE / "pages"
DATA_DIR = BASE / "data"
REF_DIR = BASE / "reference"

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

# Solved page plaintexts (GP indices from known solutions)
# We'll load these from runeglish or compute from known keys

def load_runes(page_num):
    """Load rune indices from a page."""
    rune_path = PAGES_DIR / f"page_{page_num:02d}" / "runes.txt"
    if not rune_path.exists():
        return None, None
    content = rune_path.read_text(encoding='utf-8').strip()
    indices = [RUNE_TO_IDX[ch] for ch in content if ch in RUNE_TO_IDX]
    return indices, content


def compute_ioc(vals):
    if len(vals) < 2:
        return 0
    freq = Counter(vals)
    n = len(vals)
    total = sum(f * (f - 1) for f in freq.values())
    raw = total / (n * (n - 1))
    return raw / (1.0 / 29)


def to_runeglish(indices):
    return ''.join(IDX_TO_LETTER[i] for i in indices)


def diff_streams(a, b, mode='sub'):
    """Compute pairwise difference/sum of two streams."""
    n = min(len(a), len(b))
    if mode == 'sub':
        return [(a[i] - b[i]) % 29 for i in range(n)]
    elif mode == 'add':
        return [(a[i] + b[i]) % 29 for i in range(n)]
    elif mode == 'beaufort':
        return [(b[i] - a[i]) % 29 for i in range(n)]


def get_word_boundaries(content):
    """Get word structure from rune content."""
    words = []
    current_len = 0
    current_start = 0
    idx = 0
    for ch in content:
        if ch in RUNE_TO_IDX:
            if current_len == 0:
                current_start = idx
            current_len += 1
            idx += 1
        elif ch in '-\n /%.&$':
            if current_len > 0:
                words.append((current_start, current_len))
                current_len = 0
    if current_len > 0:
        words.append((current_start, current_len))
    return words


def check_singletons(plain, words):
    passed = 0
    total = 0
    for start, length in words:
        if length == 1:
            total += 1
            if start < len(plain) and plain[start] in (10, 24):
                passed += 1
    return passed, total


# Common English bigrams for scoring
COMMON_BIGRAMS = {'TH','HE','IN','ER','AN','RE','ON','AT','EN','ND','TI','ES','OR','TE',
                   'ED','IS','IT','AL','AR','ST','TO','NT','NG','SE','HA','AS','OU','OF'}

def bigram_score(text):
    count = 0
    for i in range(len(text) - 1):
        if text[i:i+2] in COMMON_BIGRAMS:
            count += 1
    return count


def main():
    print("=" * 80)
    print("TWO-TIME PAD DETECTION & RUNNING KEY ANALYSIS")
    print("=" * 80)
    sys.stdout.flush()
    
    # Load all pages
    all_pages = {}
    all_content = {}
    for pg in range(21, 55):
        data = load_runes(pg)
        if data[0] is not None:
            all_pages[pg] = data[0]
            all_content[pg] = data[1]
    
    print(f"Loaded {len(all_pages)} unsolved pages\n")
    
    # ================================================================
    # PART 1: TWO-TIME PAD DETECTION
    # ================================================================
    print("=" * 80)
    print("PART 1: Two-Time Pad Detection (Pairwise Ciphertext Differences)")
    print("=" * 80)
    print("Testing all pairs of unsolved pages. If two pages share a key stream,")
    print("their difference will have IoC >> 1.0\n")
    sys.stdout.flush()
    
    page_nums = sorted(all_pages.keys())
    high_ioc_pairs = []
    
    for i, pg1 in enumerate(page_nums):
        for pg2 in page_nums[i+1:]:
            c1 = all_pages[pg1]
            c2 = all_pages[pg2]
            n = min(len(c1), len(c2))
            if n < 50:
                continue
            
            for mode in ['sub', 'add']:
                d = diff_streams(c1[:n], c2[:n], mode)
                ioc = compute_ioc(d)
                
                if ioc > 1.15:
                    text = to_runeglish(d)
                    bg = bigram_score(text)
                    high_ioc_pairs.append((ioc, bg, pg1, pg2, mode, n, text[:80]))
    
    high_ioc_pairs.sort(key=lambda x: -x[0])
    
    if high_ioc_pairs:
        print(f"Found {len(high_ioc_pairs)} pairs with IoC > 1.15:")
        for ioc, bg, p1, p2, mode, n, txt in high_ioc_pairs[:30]:
            print(f"  P{p1:02d} - P{p2:02d} ({mode:4s}, {n:4d} runes): IoC={ioc:.4f} bg={bg:3d} | {txt[:60]}")
    else:
        print("NO pairs found with IoC > 1.15")
        print("This means NO two unsolved pages share the same key stream.")
    
    sys.stdout.flush()
    
    # ================================================================
    # PART 2: RUNNING KEY WITH SOLVED LP1 PLAINTEXTS
    # ================================================================
    print("\n" + "=" * 80)
    print("PART 2: Solved LP Plaintext as Running Key")
    print("=" * 80)
    sys.stdout.flush()
    
    # Load solved page runeglish and convert to GP indices
    solved_pages_text = {}
    solved_order = [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
                    55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 67, 68, 71, 72, 73, 74]
    
    # We'll use runeglish files if available, otherwise raw runes directly
    runeglish_dir = DATA_DIR / "runeglish"
    
    # Build a master solved-plaintext stream from solved pages
    # Since we know the plaintext of solved pages, we can convert to GP indices
    # But we need the PLAINTEXT indices, not the CIPHERTEXT indices
    # For now, let's try using CIPHERTEXT of solved pages as running key
    # (since ciphertext of cleartext pages IS the plaintext)
    
    # Actually, for cleartext pages, cipher = plain
    # For Vigenère pages, we'd need to decrypt first
    # Let's focus on cleartext pages as a clean source:
    cleartext_pages = [5, 10, 11, 12, 13, 16, 57, 58, 60, 63, 68, 71, 74]
    
    master_stream = []
    for pg in cleartext_pages:
        runes, _ = load_runes(pg)
        if runes:
            master_stream.extend(runes)
    
    print(f"Master solved-plaintext stream: {len(master_stream)} GP values from cleartext pages")
    print(f"  Sources: {cleartext_pages}")
    
    if len(master_stream) >= 50:
        print("\nTesting as running key (offset 0) on all unsolved pages:\n")
        
        for pg in sorted(all_pages.keys()):
            cipher = all_pages[pg]
            content = all_content[pg]
            words = get_word_boundaries(content)
            
            best_ioc = 0
            best_result = None
            
            # Test multiple offsets
            max_offset = max(0, len(master_stream) - len(cipher))
            step = max(1, max_offset // 100)
            
            for offset in range(0, max_offset + 1, step):
                key_seg = master_stream[offset:offset + len(cipher)]
                if len(key_seg) < len(cipher):
                    break
                    
                for mode in ['sub', 'add', 'beaufort']:
                    plain = diff_streams(cipher, key_seg, mode)
                    ioc = compute_ioc(plain)
                    
                    if ioc > best_ioc:
                        sp, st = check_singletons(plain, words)
                        text = to_runeglish(plain)
                        bg = bigram_score(text)
                        best_ioc = ioc
                        best_result = (ioc, bg, sp, st, mode, offset, text[:80])
            
            if best_result:
                ioc, bg, sp, st, mode, off, txt = best_result
                flag = " ***" if ioc > 1.3 else ""
                print(f"  P{pg:02d}: IoC={ioc:.4f} bg={bg:3d} sing={sp}/{st} {mode:8s} off={off:4d} | {txt[:55]}{flag}")
    
    sys.stdout.flush()
    
    # ================================================================
    # PART 3: ALL RUNE PAGES AS RUNNING KEY SOURCE
    # ================================================================
    print("\n" + "=" * 80)
    print("PART 3: Full LP Rune Stream as Running Key")
    print("=" * 80)
    sys.stdout.flush()
    
    # Load runes_full.txt as a complete running key source
    runes_full_path = DATA_DIR / "runes_full.txt"
    full_stream = []
    if runes_full_path.exists():
        raw = runes_full_path.read_text(encoding='utf-8')
        full_stream = [RUNE_TO_IDX[ch] for ch in raw if ch in RUNE_TO_IDX]
        print(f"Full LP rune stream: {len(full_stream)} runes")
    
    if len(full_stream) >= 1000:
        print("\nTesting full LP rune stream as running key with various offsets:\n")
        
        for pg in sorted(all_pages.keys()):
            cipher = all_pages[pg]
            content = all_content[pg]
            words = get_word_boundaries(content)
            
            best_ioc = 0
            best_result = None
            
            max_offset = len(full_stream) - len(cipher)
            # Coarse scan
            for offset in range(0, max_offset, 50):
                key_seg = full_stream[offset:offset + len(cipher)]
                
                for mode in ['sub', 'add', 'beaufort']:
                    plain = diff_streams(cipher, key_seg, mode)
                    ioc = compute_ioc(plain)
                    
                    if ioc > best_ioc:
                        sp, st = check_singletons(plain, words)
                        text = to_runeglish(plain)
                        bg = bigram_score(text)
                        best_ioc = ioc
                        best_result = (ioc, bg, sp, st, mode, offset, text[:80])
            
            if best_result:
                ioc, bg, sp, st, mode, off, txt = best_result
                flag = " ***" if ioc > 1.3 else ""
                print(f"  P{pg:02d}: IoC={ioc:.4f} bg={bg:3d} sing={sp}/{st} {mode:8s} off={off:5d} | {txt[:50]}{flag}")
    
    sys.stdout.flush()
    
    # ================================================================
    # PART 4: REFERENCE TEXT RUNNING KEYS (Emerson, Liber AL)
    # ================================================================
    print("\n" + "=" * 80)
    print("PART 4: External Reference Texts as Running Keys")
    print("=" * 80)
    sys.stdout.flush()
    
    ref_texts = {}
    
    # Emerson essays
    emerson_path = DATA_DIR / "emerson_essays.txt"
    if emerson_path.exists():
        raw = emerson_path.read_text(encoding='utf-8')
        # Convert to GP indices: A=24, B=17, C=5, D=23, E=18, ...
        LETTER_TO_GP = {
            'A': 24, 'B': 17, 'C': 5, 'D': 23, 'E': 18, 'F': 0, 'G': 6,
            'H': 8, 'I': 10, 'J': 11, 'K': 5, 'L': 20, 'M': 19, 'N': 9,
            'O': 3, 'P': 13, 'Q': 5, 'R': 4, 'S': 15, 'T': 16, 'U': 1,
            'V': 1, 'W': 7, 'X': 14, 'Y': 26, 'Z': 15,
        }
        em_indices = [LETTER_TO_GP[c.upper()] for c in raw if c.upper() in LETTER_TO_GP]
        ref_texts['Emerson'] = em_indices
        print(f"  Emerson: {len(em_indices)} GP values")
    
    # Liber AL
    liber_al_path = REF_DIR / "liber_al_vel_legis.txt"
    if liber_al_path.exists():
        raw = liber_al_path.read_text(encoding='utf-8')
        LETTER_TO_GP = {
            'A': 24, 'B': 17, 'C': 5, 'D': 23, 'E': 18, 'F': 0, 'G': 6,
            'H': 8, 'I': 10, 'J': 11, 'K': 5, 'L': 20, 'M': 19, 'N': 9,
            'O': 3, 'P': 13, 'Q': 5, 'R': 4, 'S': 15, 'T': 16, 'U': 1,
            'V': 1, 'W': 7, 'X': 14, 'Y': 26, 'Z': 15,
        }
        la_indices = [LETTER_TO_GP[c.upper()] for c in raw if c.upper() in LETTER_TO_GP]
        ref_texts['LiberAL'] = la_indices
        print(f"  Liber AL: {len(la_indices)} GP values")
    
    # Self-Reliance
    sr_path = DATA_DIR / "self_reliance.txt"
    if sr_path.exists():
        raw = sr_path.read_text(encoding='utf-8')
        LETTER_TO_GP = {
            'A': 24, 'B': 17, 'C': 5, 'D': 23, 'E': 18, 'F': 0, 'G': 6,
            'H': 8, 'I': 10, 'J': 11, 'K': 5, 'L': 20, 'M': 19, 'N': 9,
            'O': 3, 'P': 13, 'Q': 5, 'R': 4, 'S': 15, 'T': 16, 'U': 1,
            'V': 1, 'W': 7, 'X': 14, 'Y': 26, 'Z': 15,
        }
        sr_indices = [LETTER_TO_GP[c.upper()] for c in raw if c.upper() in LETTER_TO_GP]
        ref_texts['SelfReliance'] = sr_indices
        print(f"  Self-Reliance: {len(sr_indices)} GP values")
    
    # Deor poem
    deor_path = DATA_DIR / "deor_poem.txt"
    if deor_path.exists():
        raw = deor_path.read_text(encoding='utf-8')
        LETTER_TO_GP = {
            'A': 24, 'B': 17, 'C': 5, 'D': 23, 'E': 18, 'F': 0, 'G': 6,
            'H': 8, 'I': 10, 'J': 11, 'K': 5, 'L': 20, 'M': 19, 'N': 9,
            'O': 3, 'P': 13, 'Q': 5, 'R': 4, 'S': 15, 'T': 16, 'U': 1,
            'V': 1, 'W': 7, 'X': 14, 'Y': 26, 'Z': 15,
        }
        dr_indices = [LETTER_TO_GP[c.upper()] for c in raw if c.upper() in LETTER_TO_GP]
        ref_texts['Deor'] = dr_indices
        print(f"  Deor: {len(dr_indices)} GP values")
    
    for ref_name, ref_indices in ref_texts.items():
        print(f"\n--- {ref_name} as running key ---")
        
        # Test P28 specifically (most singletons among unsolved, good test case)
        test_pages = [28, 53, 21, 24, 29, 30, 39, 34, 51]
        
        for pg in test_pages:
            if pg not in all_pages:
                continue
            cipher = all_pages[pg]
            content = all_content[pg]
            words = get_word_boundaries(content)
            
            best_ioc = 0
            best_result = None
            
            max_off = len(ref_indices) - len(cipher)
            if max_off < 0:
                continue
            
            # Finer scan for shorter texts
            step = max(1, max_off // 500)
            
            for offset in range(0, max_off + 1, step):
                key_seg = ref_indices[offset:offset + len(cipher)]
                
                for mode in ['sub', 'add', 'beaufort']:
                    plain = diff_streams(cipher, key_seg, mode)
                    sp, st = check_singletons(plain, words)
                    
                    # Singleton filter
                    if st > 2 and sp < st * 0.5:
                        continue
                    
                    ioc = compute_ioc(plain)
                    if ioc > best_ioc:
                        text = to_runeglish(plain)
                        bg = bigram_score(text)
                        best_ioc = ioc
                        best_result = (ioc, bg, sp, st, mode, offset, text[:80])
            
            if best_result:
                ioc, bg, sp, st, mode, off, txt = best_result
                flag = " ***" if ioc > 1.3 else ""
                print(f"  P{pg:02d}: IoC={ioc:.4f} bg={bg:3d} sing={sp}/{st} {mode:8s} off={off:5d} | {txt[:55]}{flag}")
    
    sys.stdout.flush()
    
    # ================================================================
    # PART 5: P27 = P44[0:234] ANALYSIS
    # ================================================================
    print("\n" + "=" * 80)
    print("PART 5: P27 = P44[0:234] Constraint Analysis")
    print("=" * 80)
    sys.stdout.flush()
    
    if 27 in all_pages and 44 in all_pages:
        c27 = all_pages[27]
        c44 = all_pages[44]
        
        # Verify the overlap
        match_count = sum(1 for i in range(min(len(c27), len(c44))) if c27[i] == c44[i])
        print(f"P27 length: {len(c27)}, P44 length: {len(c44)}")
        print(f"Match in first {len(c27)} positions: {match_count}/{len(c27)} ({100*match_count/len(c27):.1f}%)")
        
        if match_count == len(c27):
            print("CONFIRMED: P27 is an exact prefix of P44")
            print("\nP44 unique tail (positions 234+):")
            tail = c44[len(c27):]
            print(f"  {len(tail)} additional runes")
            tail_text = to_runeglish(tail)
            print(f"  IoC of tail: {compute_ioc(tail):.4f}")
            print(f"  IoC of P27/P44 shared prefix: {compute_ioc(c27):.4f}")
            print(f"  IoC of full P44: {compute_ioc(c44):.4f}")
            
            # Check if the tail has different statistical properties
            freq_prefix = Counter(c27)
            freq_tail = Counter(tail)
            print(f"\n  Most common in prefix: {freq_prefix.most_common(5)}")
            print(f"  Most common in tail: {freq_tail.most_common(5)}")
        else:
            print(f"WARNING: P27 is NOT an exact prefix of P44 (only {match_count} matches)")
            # Find where they diverge
            for i in range(min(len(c27), len(c44))):
                if c27[i] != c44[i]:
                    print(f"  First divergence at position {i}: P27={c27[i]}, P44={c44[i]}")
                    break
    
    print("\nDone.")


if __name__ == '__main__':
    main()
