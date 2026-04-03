#!/usr/bin/env python3
from pathlib import Path
from collections import Counter

BASE = Path(__file__).resolve().parent.parent
PAGES_DIR = BASE / "pages"
DATA_DIR = BASE / "data"

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

def heuristic_process(text):
    # basic GP digraph => approximate English
    rules = [('NG','ING'), ('EO','E'), ('OE','O'), ('AE','A'), ('IO','I'), ('EA','E'), ('C','K'), ('U','V')]
    out = text
    for a,b in rules:
        out = out.replace(a,b)
    out = out.replace('THE',' THE ')
    return ' '.join(out.split())

def parse_top_lines(fname, top_n=6):
    lines = Path(fname).read_text(encoding='utf-8').splitlines()
    entries = []
    for line in lines:
        if line.startswith('width='):
            parts = line.split()
            w = int(parts[0].split('=')[1])
            s = int(parts[1].split('=')[1])
            entries.append((w,s))
            if len(entries) >= top_n:
                break
    return entries

def main():
    page = 24
    indices = load_page_indices(page)
    n = len(indices)
    prime0 = [indices[i] for i in range(n) if is_prime(i)]

    top = parse_top_lines(DATA_DIR / 'p24_prime0_post.txt', top_n=8)
    out_dir = DATA_DIR / 'p24_candidates_processed'
    out_dir.mkdir(exist_ok=True)

    for w, shift in top:
        col = columnar_read(prime0, w)
        shifted = [ (c - shift) % 29 for c in col ]
        text = indices_to_runeglish(shifted)
        proc = heuristic_process(text)
        f = out_dir / f'candidate_w{w}_s{shift}.txt'
        f.write_text(proc, encoding='utf-8')
        print('Wrote', f)

if __name__ == '__main__':
    main()
