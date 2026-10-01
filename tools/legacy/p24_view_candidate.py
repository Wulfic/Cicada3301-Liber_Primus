#!/usr/bin/env python3
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
PAGES_DIR = BASE / "pages"

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

def load_page_indices(page):
    p = PAGES_DIR / f"page_{page:02d}" / "runes.txt"
    s = p.read_text(encoding='utf-8')
    return [RUNE_TO_IDX[c] for c in s if c in RUNE_TO_IDX]

def indices_to_runeglish(indices):
    return ''.join(IDX_TO_LETTER[i] for i in indices)

def is_prime(n):
    if n < 2: return False
    if n % 2 == 0 and n != 2: return False
    i = 3
    while i * i <= n:
        if n % i == 0: return False
        i += 2
    return True

def columnar_read(indices, width):
    rows = [indices[i:i+width] for i in range(0, len(indices), width)]
    out = []
    for col in range(width):
        for row in rows:
            if col < len(row):
                out.append(row[col])
    return out

def main():
    page = 24
    indices = load_page_indices(page)
    # prime0 stream as before
    prime0 = [indices[i] for i in range(len(indices)) if is_prime(i)]
    width = 14
    shift = 25
    col = columnar_read(prime0, width)
    shifted = [ (c - shift) % 29 for c in col ]
    text = indices_to_runeglish(shifted)
    out = Path('data') / 'p24_candidate_full_width14_shift25.txt'
    out.write_text(text, encoding='utf-8')
    print('Wrote', out)

if __name__ == '__main__':
    main()
