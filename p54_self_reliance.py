#!/usr/bin/env python3
"""
P54 Running-Key Cipher attack using Emerson's Self-Reliance as key source.

The P54 README notes:
- IoC ≈ 0.034 (1/29 = random) → NOT periodic Vigenère
- "Running Key Suspected"
- "Self-Reliance as key source"

This script fetches Self-Reliance text, converts to GP rune values,
and tries every offset with SUB/ADD/BEAU modes.
"""

import sys, os, functools, re, urllib.request

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
print = functools.partial(print, flush=True)

# ── Gematria Primus (CORRECT mapping verified by P55/P73) ──
GP_RUNES = 'ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
GP_NAMES = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
N = 29

# English text → GP values (greedy digraph matching, left-to-right)
# Digraphs: TH, NG, EA, OE, AE, IA, EO
# Single: F, U, O, R, C, G, W, H, N, I, J, P, X, S, T, B, E, M, L, D, A, Y
DIGRAPHS = {'TH':2, 'NG':21, 'EA':28, 'OE':22, 'AE':25, 'IA':27, 'EO':12}
SINGLES = {'F':0, 'U':1, 'O':3, 'R':4, 'C':5, 'G':6, 'W':7, 'H':8, 'N':9, 
           'I':10, 'J':11, 'P':13, 'X':14, 'S':15, 'T':16, 'B':17, 'E':18, 
           'M':19, 'L':20, 'D':23, 'A':24, 'Y':26}

def text_to_gp(text):
    """Convert English text to GP values, greedy digraph matching."""
    text = text.upper()
    vals = []
    i = 0
    while i < len(text):
        if i + 1 < len(text):
            di = text[i:i+2]
            if di in DIGRAPHS:
                vals.append(DIGRAPHS[di])
                i += 2
                continue
        ch = text[i]
        if ch in SINGLES:
            vals.append(SINGLES[ch])
            i += 1
        else:
            # Skip non-alphabetic characters
            i += 1
    return vals

# ── P54 cipher values ──
CIPHER = [21, 25, 19, 10, 7, 15, 17, 14, 19, 15, 12, 6, 23, 2, 25, 0, 27, 24, 17, 5, 1, 7, 4, 17, 28, 0, 14, 10, 19, 1, 5, 13, 8, 21, 20, 12, 19, 15, 23, 27, 13, 0, 17, 8, 12, 5, 12, 18, 28, 18, 10, 6, 14, 6, 15, 18, 15, 12, 2, 2, 18, 15, 2, 22, 5, 28, 10, 19, 5, 14, 23, 11, 1, 17, 18, 10]
WORD_LENS = [1, 4, 2, 2, 6, 6, 2, 1, 12, 6, 4, 2, 7, 7, 2, 4, 2, 3, 3]

# ── Load dictionary ──
print("Loading dictionary...")
with open('wordlist.txt', 'r') as f:
    ALL_WORDS = set(w.strip().upper() for w in f if w.strip())
print(f"  Dictionary: {len(ALL_WORDS)} words")

# Also build a GP-word set for quick lookup
def gp_to_text(vals):
    """Convert GP values back to text (using canonical names)."""
    return ''.join(GP_NAMES[v] for v in vals)

def extract_words(plaintext_vals):
    """Split plaintext GP values into words using WORD_LENS."""
    words = []
    pos = 0
    for wl in WORD_LENS:
        word_vals = plaintext_vals[pos:pos+wl]
        words.append(gp_to_text(word_vals))
        pos += wl
    return words

def count_word_matches(words):
    """Count how many words are in the dictionary."""
    count = 0
    matched = []
    for i, w in enumerate(words):
        if w in ALL_WORDS:
            count += 1
            matched.append(f"W{i}={w}")
    return count, matched

def decrypt(cipher, key_vals, mode):
    """Decrypt cipher with key using specified mode."""
    plain = []
    for i in range(len(cipher)):
        c = cipher[i]
        k = key_vals[i]
        if mode == 'SUB':
            p = (c - k) % N
        elif mode == 'ADD':
            p = (c + k) % N
        elif mode == 'BEAU':
            p = (k - c) % N
        plain.append(p)
    return plain

# ── Fetch Self-Reliance text ──
print("\nLoading Self-Reliance text...")

# Try to read from local cache first
SR_CACHE = 'self_reliance.txt'
if os.path.exists(SR_CACHE):
    with open(SR_CACHE, 'r', encoding='utf-8') as f:
        sr_text = f.read()
    print(f"  Loaded from cache: {len(sr_text)} chars")
else:
    # Fetch from Project Gutenberg
    url = 'https://www.gutenberg.org/cache/epub/16643/pg16643.txt'
    print(f"  Fetching from {url}...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        full_text = resp.read().decode('utf-8', errors='replace')
    
    # Extract Self-Reliance essay
    # Find the start: "SELF-RELIANCE" followed by the epigraph
    sr_start = full_text.find('SELF-RELIANCE')
    if sr_start == -1:
        sr_start = full_text.find('SELF RELIANCE')
    if sr_start == -1:
        print("ERROR: Could not find Self-Reliance in text!")
        sys.exit(1)
    
    # Find the next essay (FRIENDSHIP)
    sr_end = full_text.find('\nFRIENDSHIP', sr_start + 100)
    if sr_end == -1:
        sr_end = full_text.find('\nHEROISM', sr_start + 100)
    if sr_end == -1:
        sr_end = sr_start + 100000  # Take a large chunk
    
    sr_text = full_text[sr_start:sr_end]
    
    # Save cache
    with open(SR_CACHE, 'w', encoding='utf-8') as f:
        f.write(sr_text)
    print(f"  Extracted: {len(sr_text)} chars, saved to {SR_CACHE}")

# Also try the pure essay text (without footnotes and epigraph variants)
# Find where the actual essay prose begins
prose_start = sr_text.find('I read the other day')
if prose_start == -1:
    prose_start = 0
    print("  WARNING: Could not find essay prose start")

# Convert full SR text to GP
sr_gp_full = text_to_gp(sr_text)
print(f"  Full Self-Reliance GP values: {len(sr_gp_full)}")

# Convert prose-only to GP
sr_gp_prose = text_to_gp(sr_text[prose_start:])
print(f"  Prose-only GP values: {len(sr_gp_prose)}")

# Also try just the epigraph/motto
epigraph_end = prose_start if prose_start > 0 else 500
sr_gp_epigraph = text_to_gp(sr_text[:epigraph_end])
print(f"  Epigraph GP values: {len(sr_gp_epigraph)}")

# Show first few GP values for verification
print(f"\n  First 20 GP values (full): {sr_gp_full[:20]}")
print(f"  = {gp_to_text(sr_gp_full[:20])}")
print(f"\n  First 20 GP values (prose): {sr_gp_prose[:20]}")
print(f"  = {gp_to_text(sr_gp_prose[:20])}")

# ── Run running-key attack ──
print("\n" + "="*80)
print("RUNNING-KEY ATTACK: SELF-RELIANCE")
print("="*80)

# Save results to file
outf = open('p54_sr_results.txt', 'w', encoding='utf-8')

best_overall = 0
best_results = []

for label, key_gp in [("SR_FULL", sr_gp_full), ("SR_PROSE", sr_gp_prose)]:
    max_offset = len(key_gp) - len(CIPHER)
    if max_offset < 0:
        print(f"\n{label}: Key too short ({len(key_gp)} < {len(CIPHER)})")
        continue
    
    print(f"\n--- {label}: {len(key_gp)} GP values, testing {max_offset+1} offsets ---")
    outf.write(f"\n--- {label}: {len(key_gp)} GP values, testing {max_offset+1} offsets ---\n")
    
    section_best = 0
    section_results = []
    
    for offset in range(max_offset + 1):
        key_slice = key_gp[offset:offset + len(CIPHER)]
        
        for mode in ['SUB', 'ADD', 'BEAU']:
            plain = decrypt(CIPHER, key_slice, mode)
            words = extract_words(plain)
            matches, matched_list = count_word_matches(words)
            
            if matches >= 12:
                text = ' '.join(words)
                line = f"  {label} off={offset} {mode}: {matches}/19 matches"
                print(line)
                print(f"    Text: {text}")
                print(f"    Matches: {', '.join(matched_list)}")
                outf.write(line + "\n")
                outf.write(f"    Text: {text}\n")
                outf.write(f"    Matches: {', '.join(matched_list)}\n")
                
            if matches > section_best:
                section_best = matches
                section_results = [(offset, mode, matches, words, matched_list)]
            elif matches == section_best and matches >= 10:
                section_results.append((offset, mode, matches, words, matched_list))
    
    print(f"\n  {label} BEST: {section_best}/19 matches")
    outf.write(f"\n  {label} BEST: {section_best}/19 matches\n")
    
    if section_best > best_overall:
        best_overall = section_best
        best_results = section_results
    
    # Show top results (best and near-best)
    if section_best >= 10:
        print(f"  Top results for {label}:")
        outf.write(f"  Top results for {label}:\n")
        for off, mode, matches, words, ml in section_results[:10]:
            text = ' '.join(words)
            line = f"    off={off} {mode}: {matches}/19 → {text}"
            print(line)
            print(f"      Matches: {', '.join(ml)}")
            outf.write(line + "\n")
            outf.write(f"      Matches: {', '.join(ml)}\n")

# ── Also try with letters-only conversion (no digraphs) ──
print("\n" + "="*80)
print("ALTERNATE: SINGLE-LETTER ONLY CONVERSION (no digraphs)")
print("="*80)

# Map each letter individually (A=24, B=17, C=5, D=23, E=18, F=0, G=6, H=8, I=10, J=11, etc.)
def text_to_gp_singles(text):
    """Convert English text to GP values, single letters only (no digraph matching)."""
    text = text.upper()
    return [SINGLES[ch] for ch in text if ch in SINGLES]

sr_singles_full = text_to_gp_singles(sr_text)
sr_singles_prose = text_to_gp_singles(sr_text[prose_start:])

for label, key_gp in [("SINGLES_FULL", sr_singles_full), ("SINGLES_PROSE", sr_singles_prose)]:
    max_offset = len(key_gp) - len(CIPHER)
    if max_offset < 0:
        continue
    
    print(f"\n--- {label}: {len(key_gp)} GP values, testing {max_offset+1} offsets ---")
    outf.write(f"\n--- {label}: {len(key_gp)} GP values, testing {max_offset+1} offsets ---\n")
    
    section_best = 0
    
    for offset in range(max_offset + 1):
        key_slice = key_gp[offset:offset + len(CIPHER)]
        
        for mode in ['SUB', 'ADD', 'BEAU']:
            plain = decrypt(CIPHER, key_slice, mode)
            words = extract_words(plain)
            matches, matched_list = count_word_matches(words)
            
            if matches >= 12:
                text = ' '.join(words)
                line = f"  {label} off={offset} {mode}: {matches}/19"
                print(line)
                print(f"    Text: {text}")
                print(f"    Matches: {', '.join(matched_list)}")
                outf.write(line + "\n")
                outf.write(f"    Text: {text}\n")
                outf.write(f"    Matches: {', '.join(matched_list)}\n")
            
            if matches > section_best:
                section_best = matches
    
    print(f"\n  {label} BEST: {section_best}/19 matches")
    outf.write(f"\n  {label} BEST: {section_best}/19 matches\n")

# ── Also try F-skip variant: skip F(0) positions in ciphertext ──
print("\n" + "="*80)
print("F-SKIP VARIANT: Remove F(0) runes at positions 15,25,41")
print("="*80)

F_POSITIONS = [15, 25, 41]
CIPHER_FSKIP = [CIPHER[i] for i in range(len(CIPHER)) if i not in F_POSITIONS]
# Recalculate word lengths after removing F positions
# Original word boundaries: cumsum of WORD_LENS
# pos 0: w0(1), pos 1: w1(4), pos 5: w2(2), pos 7: w3(2), pos 9: w4(6), pos 15: w5(6), pos 21: w6(2), pos 23: w7(1), pos 24: w8(12), pos 36: w9(6), pos 42: w10(4), pos 46: w11(2), pos 48: w12(7), pos 55: w13(7), pos 62: w14(2), pos 64: w15(4), pos 68: w16(2), pos 70: w17(3), pos 73: w18(3)
# F at pos 15 (start of w5), pos 25 (in w8, offset 1), pos 41 (in w9, offset 5)
# After F-skip:
# w0: 1, w1: 4, w2: 2, w3: 2, w4: 6, w5: 5(-1), w6: 2, w7: 1, w8: 11(-1), w9: 5(-1), w10: 4, w11: 2, w12: 7, w13: 7, w14: 2, w15: 4, w16: 2, w17: 3, w18: 3
FSKIP_WORD_LENS = [1, 4, 2, 2, 6, 5, 2, 1, 11, 5, 4, 2, 7, 7, 2, 4, 2, 3, 3]
print(f"  F-skip cipher: {len(CIPHER_FSKIP)} values")
print(f"  F-skip word lens sum: {sum(FSKIP_WORD_LENS)}")

def extract_words_fskip(plaintext_vals):
    words = []
    pos = 0
    for wl in FSKIP_WORD_LENS:
        word_vals = plaintext_vals[pos:pos+wl]
        words.append(gp_to_text(word_vals))
        pos += wl
    return words

for label, key_gp in [("FSKIP_SR_FULL", sr_gp_full), ("FSKIP_SR_PROSE", sr_gp_prose)]:
    max_offset = len(key_gp) - len(CIPHER_FSKIP)
    if max_offset < 0:
        continue
    
    print(f"\n--- {label}: testing {max_offset+1} offsets ---")
    outf.write(f"\n--- {label}: testing {max_offset+1} offsets ---\n")
    
    section_best = 0
    
    for offset in range(max_offset + 1):
        key_slice = key_gp[offset:offset + len(CIPHER_FSKIP)]
        
        for mode in ['SUB', 'ADD', 'BEAU']:
            plain = decrypt(CIPHER_FSKIP, key_slice, mode)
            words = extract_words_fskip(plain)
            matches, matched_list = count_word_matches(words)
            
            if matches >= 12:
                text = ' '.join(words)
                line = f"  {label} off={offset} {mode}: {matches}/19"
                print(line)
                print(f"    Text: {text}")
                print(f"    Matches: {', '.join(matched_list)}")
                outf.write(line + "\n")
                outf.write(f"    Text: {text}\n")
                outf.write(f"    Matches: {', '.join(matched_list)}\n")
            
            if matches > section_best:
                section_best = matches
    
    print(f"\n  {label} BEST: {section_best}/19 matches")
    outf.write(f"\n  {label} BEST: {section_best}/19 matches\n")

# ── Also try: apply GP conversion to Self-Reliance but treating 
#    common contractions and archaic spellings ──
# And try: the key might be from OTHER Emerson essays in the same book

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Best overall: {best_overall}/19 matches")
if best_results:
    for off, mode, matches, words, ml in best_results[:5]:
        text = ' '.join(words)
        print(f"  off={off} {mode}: {text}")
        print(f"    Matches: {', '.join(ml)}")

outf.write(f"\nBest overall: {best_overall}/19 matches\n")
outf.close()
print("\nResults saved to p54_sr_results.txt")
print("DONE")
