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

def load_page(page):
    p = PAGES_DIR / f"page_{page:02d}" / "runes.txt"
    return p.read_text(encoding='utf-8')

def extract_indices(content):
    return [RUNE_TO_IDX[c] for c in content if c in RUNE_TO_IDX]

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

def compute_ioc(indices):
    n = len(indices)
    if n < 2: return 0.0
    counts = Counter(indices)
    return 29 * sum(c*(c-1) for c in counts.values()) / (n*(n-1))

def score_trigrams(runeglish):
    s = runeglish.upper()
    score = 0
    for i in range(len(s)-2):
        tri = s[i:i+3]
        if tri in COMMON_3GRAMS:
            score += COMMON_3GRAMS[tri]
    return score

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
    content = load_page(page)
    indices = extract_indices(content)
    n = len(indices)

    prime0 = [indices[i] for i in range(n) if is_prime(i)]
    results = []
    for w in range(2, 15):
        col = columnar_read(prime0, w)
        for shift in range(29):
            shifted = [ (c - shift) % 29 for c in col ]
            text = indices_to_runeglish(shifted)
            tri_score = score_trigrams(text)
            ioc = compute_ioc(shifted)
            results.append((w, shift, ioc, tri_score, text[:200]))

    results.sort(key=lambda x: (-x[3], -x[2]))
    out = Path(DATA_DIR) / 'p24_prime0_post.txt'
    with open(out, 'w', encoding='utf-8') as f:
        for w, shift, ioc, tri, txt in results[:40]:
            f.write(f'width={w} shift={shift} IoC={ioc:.4f} tri={tri}\n')
            f.write(txt + '\n\n')
    print('Wrote', out)

if __name__ == '__main__':
    main()
