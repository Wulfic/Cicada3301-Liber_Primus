"""
Decode P14 and P15 with FIRFUMFERENFE key + F-skip rule.
P14 uses bullet separator, P15 uses dash/dot separator.
"""
import os, sys

RUNE_TO_IDX = {
    'ᚠ': 0,  'ᚢ': 1,  'ᚦ': 2,  'ᚩ': 3,  'ᚱ': 4,  'ᚳ': 5,  'ᚷ': 6,  'ᚹ': 7,
    'ᚻ': 8,  'ᚾ': 9,  'ᛁ': 10, 'ᛄ': 11, 'ᛇ': 12, 'ᛈ': 13, 'ᛉ': 14, 'ᛋ': 15,
    'ᛏ': 16, 'ᛒ': 17, 'ᛖ': 18, 'ᛗ': 19, 'ᛚ': 20, 'ᛝ': 21, 'ᛟ': 22, 'ᛞ': 23,
    'ᚪ': 24, 'ᚫ': 25, 'ᚣ': 26, 'ᛡ': 27, 'ᛠ': 28,
}
IDX_TO_LATIN = [
    'F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S',
    'T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA',
]
N = 29

# FIRFUMFERENFE
KEY_LATIN = 'FIRFUMFERENFE'
LATIN_TO_GP_MONO = {
    'F':0,'I':10,'R':4,'U':1,'M':19,'E':18,'N':9,
    'A':24,'S':15,'T':16,'H':8,'W':7,'G':6,'B':17,'L':20,'D':23,'O':3,
    'Y':26,'C':5,'K':5,'P':13,'V':1,'X':14,'J':11,
}
KEY = [LATIN_TO_GP_MONO[c] for c in KEY_LATIN]
print(f"Key: {KEY_LATIN} = {KEY}")

def decode_rune_page(path, separator_chars, mode='sub'):
    """Decode a page with given separators."""
    raw = open(path, encoding='utf-8').read()
    
    # Build sequence: list of (is_separator, char_or_rune_idx)
    words_raw = []
    cur_word = []
    
    for ch in raw:
        if ch in RUNE_TO_IDX:
            cur_word.append(RUNE_TO_IDX[ch])
        elif ch in separator_chars or ch == '\n':
            if cur_word:
                words_raw.append(cur_word[:])
                cur_word = []
        # else: skip other chars (quotes, comments, etc.)
    if cur_word:
        words_raw.append(cur_word[:])
    
    # Decode with corrected F-skip:
    # F-skip ONLY when cipher=ᚠ(0) AND key[ki%len]=F(0).
    # In that case: output F, do NOT advance ki.
    # If cipher=ᚠ(0) but key is NOT F, decode normally.
    ki = 0
    decoded_words = []
    for word in words_raw:
        plain_word = []
        for c in word:
            kv = KEY[ki % len(KEY)]
            if c == 0 and kv == 0:  # true F-skip
                plain_word.append(0)  # F, don't advance ki
            else:
                if mode == 'sub':
                    p = (c - kv) % N
                elif mode == 'add':
                    p = (c + kv) % N
                elif mode == 'beau':
                    p = (kv - c) % N
                plain_word.append(p)
                ki += 1
        decoded_words.append(plain_word)
    
    return decoded_words, words_raw

def gp_to_text(gp_list):
    return ''.join(IDX_TO_LATIN[i] for i in gp_list)

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# P14: bullet separator
print("\n=== P14 DECODE (sub mode, • separator) ===")
path14 = os.path.join(base, 'pages', 'page_14', 'runes.txt')
dec14, raw14 = decode_rune_page(path14, '•"\'', mode='sub')
print("Word by word:")
for i, (w, r) in enumerate(zip(dec14, raw14)):
    if r:  # Skip empty
        print(f"  {gp_to_text(w)}", end=' ')
print()
print("\nFull:")
print(' '.join(gp_to_text(w) for w in dec14 if w))
print()

# Try add mode too
print("=== P14 DECODE (add mode) ===")
dec14a, _ = decode_rune_page(path14, '•"\'', mode='add')
print(' '.join(gp_to_text(w) for w in dec14a if w))

print("\n=== P14 DECODE (beaufort mode) ===")
dec14b, _ = decode_rune_page(path14, '•"\'', mode='beau')
print(' '.join(gp_to_text(w) for w in dec14b if w))

# P15: uses - and . separators
print("\n=== P15 DECODE (sub mode, -. separator) ===")
path15 = os.path.join(base, 'pages', 'page_15', 'runes.txt')
dec15, raw15 = decode_rune_page(path15, '-./&$', mode='sub')
print(' '.join(gp_to_text(w) for w in dec15 if w))

print("\n=== P15 DECODE (add mode, -. separator) ===")
dec15a, _ = decode_rune_page(path15, '-./&$', mode='add')
print(' '.join(gp_to_text(w) for w in dec15a if w))

print("\n=== P15 DECODE (beaufort mode, -. separator) ===")
dec15b, _ = decode_rune_page(path15, '-./&$', mode='beau')
print(' '.join(gp_to_text(w) for w in dec15b if w))
