#!/usr/bin/env python3
"""Targeted character-prime and columnar tests for Page 24
Saves outputs to data/p24_candidates.txt
"""
from pathlib import Path
from collections import Counter

BASE = Path(__file__).resolve().parent.parent
PAGES_DIR = BASE / "pages"
DATA_DIR = BASE / "data"

# Gematria index mapping (same as other tools)
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

def load_page(page):
    p = PAGES_DIR / f"page_{page:02d}" / "runes.txt"
    if not p.exists():
        raise SystemExit('page file missing')
    return p.read_text(encoding='utf-8')

def extract_indices(content):
    return [RUNE_TO_IDX[c] for c in content if c in RUNE_TO_IDX]

def indices_to_text(indices):
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


def columnar_read(indices, width):
    rows = [indices[i:i+width] for i in range(0, len(indices), width)]
    out = []
    for col in range(width):
        for row in rows:
            if col < len(row):
                out.append(row[col])
    return out


if __name__ == '__main__':
    page = 24
    content = load_page(page)
    indices = extract_indices(content)
    n = len(indices)

    results = []

    # Prime-indexed characters (1-indexed)
    prime_chars_1 = [indices[i-1] for i in range(2, n+1) if is_prime(i)]
    results.append(('prime_chars_1indexed', compute_ioc(prime_chars_1), indices_to_text(prime_chars_1)))

    # Prime-indexed characters (0-indexed)
    prime_chars_0 = [indices[i] for i in range(n) if is_prime(i)]
    results.append(('prime_chars_0indexed', compute_ioc(prime_chars_0), indices_to_text(prime_chars_0)))

    # Non-prime chars
    nonprime_chars = [indices[i] for i in range(n) if not is_prime(i)]
    results.append(('nonprime_chars', compute_ioc(nonprime_chars), indices_to_text(nonprime_chars)))

    # Columnar widths to test
    widths = [5,7,11,13]
    for w in widths:
        col = columnar_read(indices, w)
        results.append((f'columnar_w{w}', compute_ioc(col), indices_to_text(col)))

    # Also test reading primes from the post-key decrypted text candidates if available (skip)

    out_path = DATA_DIR / 'p24_candidates.txt'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f'Page 24 candidate outputs\n')
        f.write('='*60 + '\n')
        for name, ioc, txt in results:
            f.write(f'{name} IoC={ioc:.4f}\n')
            f.write(txt + '\n\n')

    print('Wrote', out_path)
