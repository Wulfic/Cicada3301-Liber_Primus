#!/usr/bin/env python3
"""
Quick investigation: How does P20 get 166 "prime-position" runes?
Test different counting methods.
"""
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

RUNE_TO_IDX = {
    '\u16A0': 0, '\u16A2': 1, '\u16A6': 2, '\u16A9': 3, '\u16B1': 4,
    '\u16B3': 5, '\u16B7': 6, '\u16B9': 7, '\u16BB': 8, '\u16BE': 9,
    '\u16C1': 10, '\u16C4': 11, '\u16C7': 12, '\u16C8': 13, '\u16C9': 14,
    '\u16CB': 15, '\u16CF': 16, '\u16D2': 17, '\u16D6': 18, '\u16D7': 19,
    '\u16DA': 20, '\u16DD': 21, '\u16DF': 22, '\u16DE': 23, '\u16AA': 24,
    '\u16AB': 25, '\u16A3': 26, '\u16E1': 27, '\u16E0': 28,
}

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i*i <= n:
        if n%i == 0 or n%(i+2) == 0: return False
        i += 6
    return True

with open(BASE / 'pages' / 'page_20' / 'runes.txt', 'r', encoding='utf-8') as f:
    raw = f.read()

# Method 1: 0-indexed rune-only positions
runes_only = [(i, RUNE_TO_IDX[ch]) for i, (pos, ch) in enumerate(
    [(j, c) for j, c in enumerate(raw) if c in RUNE_TO_IDX]
)]
n1 = len(runes_only)
primes1 = sum(1 for i in range(n1) if is_prime(i))
print(f"Method 1 (0-indexed rune positions): {n1} total, {primes1} prime, {n1-primes1} non-prime")

# Method 2: 1-indexed rune-only positions
primes2 = sum(1 for i in range(1, n1+1) if is_prime(i))
print(f"Method 2 (1-indexed rune positions): {n1} total, {primes2} prime, {n1-primes2} non-prime")

# Method 3: Count ALL characters (including separators), 0-indexed
total_chars = len(raw.strip())
rune_at_prime_char = []
for ci, ch in enumerate(raw.strip()):
    if ch in RUNE_TO_IDX and is_prime(ci):
        rune_at_prime_char.append((ci, RUNE_TO_IDX[ch]))
print(f"Method 3 (0-indexed char positions, include separators): {total_chars} chars, {len(rune_at_prime_char)} runes at prime char positions")

# Method 4: 1-indexed character positions
rune_at_prime_char_1 = []
for ci, ch in enumerate(raw.strip()):
    if ch in RUNE_TO_IDX and is_prime(ci + 1):
        rune_at_prime_char_1.append((ci, RUNE_TO_IDX[ch]))
print(f"Method 4 (1-indexed char positions): {total_chars} chars, {len(rune_at_prime_char_1)} runes at prime char positions")

# Method 5: Character positions but \n counts as nothing
no_newline = raw.strip().replace('\n', '')
rune_at_prime_nonl = []
for ci, ch in enumerate(no_newline):
    if ch in RUNE_TO_IDX and is_prime(ci):
        rune_at_prime_nonl.append((ci, RUNE_TO_IDX[ch]))
total_no_nl = len(no_newline)
print(f"Method 5 (0-indexed all chars except newline): {total_no_nl} chars, {len(rune_at_prime_nonl)} runes at prime positions")

rune_at_prime_nonl_1 = []
for ci, ch in enumerate(no_newline):
    if ch in RUNE_TO_IDX and is_prime(ci + 1):
        rune_at_prime_nonl_1.append((ci, RUNE_TO_IDX[ch]))
print(f"Method 6 (1-indexed all chars except newline): {total_no_nl} chars, {len(rune_at_prime_nonl_1)} runes at prime positions")

# Also check what separators are
seps = set()
for ch in raw:
    if ch not in RUNE_TO_IDX and ch.strip():
        seps.add((ch, hex(ord(ch))))
print(f"\nSeparator characters: {seps}")

# How many runes vs separators?
rune_count = sum(1 for ch in raw if ch in RUNE_TO_IDX)
sep_count = sum(1 for ch in raw.strip() if ch not in RUNE_TO_IDX and ch not in '\n\r')
print(f"Runes: {rune_count}, Separators/other: {sep_count}")
print(f"Total chars (no newline): {len(raw.strip().replace(chr(10),'').replace(chr(13),''))}")
