# Gematria Primus - The Cipher Alphabet

The Gematria Primus is the 29-character alphabet used throughout the Liber Primus. Each character is assigned both an index (0-28) and a prime number value.

---

## Complete Alphabet Table

| Index | Rune | Latin Letter(s) | Prime Value | Unicode |
|-------|------|-----------------|-------------|---------|
| 0 | ᚠ | F | 2 | U+16A0 |
| 1 | ᚢ | U | 3 | U+16A2 |
| 2 | ᚦ | TH | 5 | U+16A6 |
| 3 | ᚩ | O | 7 | U+16A9 |
| 4 | ᚱ | R | 11 | U+16B1 |
| 5 | ᚳ | C/K | 13 | U+16B3 |
| 6 | ᚷ | G | 17 | U+16B7 |
| 7 | ᚹ | W | 19 | U+16B9 |
| 8 | ᚻ | H | 23 | U+16BB |
| 9 | ᚾ | N | 29 | U+16BE |
| 10 | ᛁ | I | 31 | U+16C1 |
| 11 | ᛂ | J | 37 | U+16C2 |
| 12 | ᛇ | EO | 41 | U+16C7 |
| 13 | ᛈ | P | 43 | U+16C8 |
| 14 | ᛉ | X | 47 | U+16C9 |
| 15 | ᛋ | S | 53 | U+16CB |
| 16 | ᛏ | T | 59 | U+16CF |
| 17 | ᛒ | B | 61 | U+16D2 |
| 18 | ᛖ | E | 67 | U+16D6 |
| 19 | ᛗ | M | 71 | U+16D7 |
| 20 | ᛚ | L | 73 | U+16DA |
| 21 | ᛝ | NG/ING | 79 | U+16DD |
| 22 | ᛟ | OE | 83 | U+16DF |
| 23 | ᛞ | D | 89 | U+16DE |
| 24 | ᚪ | A | 97 | U+16AA |
| 25 | ᚫ | AE | 101 | U+16AB |
| 26 | ᚣ | Y | 103 | U+16A3 |
| 27 | ᛡ | IA/IO | 107 | U+16E1 |
| 28 | ᛠ | EA | 109 | U+16E0 |

---

## Digraph Characters

Several runes represent two-letter combinations:

| Rune | Digraph | Example Words |
|------|---------|---------------|
| ᚦ | TH | THE, THAT, THINK |
| ᛇ | EO | PEOPLE, THEORY |
| ᛝ | NG/ING | THING, BEING, RING |
| ᛟ | OE | PHOENIX, POEM |
| ᚫ | AE | AESTHETIC, CAESAR |
| ᛡ | IA/IO | RATIO, MEDIA |
| ᛠ | EA | IDEA, REAL, EACH |

---

## Punctuation & Formatting

| Symbol | Meaning | Usage |
|--------|---------|-------|
| `-` | Word separator | Between words (replaces space) |
| `.` | Sentence end | Period/full stop |
| `/` | Line break | New line within page |
| `%` | Page separator | End of page |
| `&` | Section marker | Section division |
| `$` | Chapter marker | Chapter division |

---

## Prime Number Significance

The prime values follow the sequence of prime numbers:
- 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109

This suggests potential gematria-based calculations where text can be converted to numerical values by summing the prime values of constituent runes.

---

## Quick Reference (Index → Rune)

```
 0=ᚠ  1=ᚢ  2=ᚦ  3=ᚩ  4=ᚱ  5=ᚳ  6=ᚷ  7=ᚹ  8=ᚻ  9=ᚾ
10=ᛁ 11=ᛂ 12=ᛇ 13=ᛈ 14=ᛉ 15=ᛋ 16=ᛏ 17=ᛒ 18=ᛖ 19=ᛗ
20=ᛚ 21=ᛝ 22=ᛟ 23=ᛞ 24=ᚪ 25=ᚫ 26=ᚣ 27=ᛡ 28=ᛠ
```

---

## Python Dictionary

```python
GEMATRIA = {
    'ᚠ': (0, 'F', 2),    'ᚢ': (1, 'U', 3),    'ᚦ': (2, 'TH', 5),
    'ᚩ': (3, 'O', 7),    'ᚱ': (4, 'R', 11),   'ᚳ': (5, 'C', 13),
    'ᚷ': (6, 'G', 17),   'ᚹ': (7, 'W', 19),   'ᚻ': (8, 'H', 23),
    'ᚾ': (9, 'N', 29),   'ᛁ': (10, 'I', 31),  'ᛂ': (11, 'J', 37),
    'ᛇ': (12, 'EO', 41), 'ᛈ': (13, 'P', 43),  'ᛉ': (14, 'X', 47),
    'ᛋ': (15, 'S', 53),  'ᛏ': (16, 'T', 59),  'ᛒ': (17, 'B', 61),
    'ᛖ': (18, 'E', 67),  'ᛗ': (19, 'M', 71),  'ᛚ': (20, 'L', 73),
    'ᛝ': (21, 'NG', 79), 'ᛟ': (22, 'OE', 83), 'ᛞ': (23, 'D', 89),
    'ᚪ': (24, 'A', 97),  'ᚫ': (25, 'AE', 101),'ᚣ': (26, 'Y', 103),
    'ᛡ': (27, 'IA', 107),'ᛠ': (28, 'EA', 109)
}

# Reverse lookup: index to rune
INDEX_TO_RUNE = {v[0]: k for k, v in GEMATRIA.items()}

# Rune to index
RUNE_TO_INDEX = {k: v[0] for k, v in GEMATRIA.items()}
```

---

## Frequency Analysis (Expected English)

For frequency-based attacks, the expected most common letters in English text:

| Rank | Letter | Expected % | Gematria Index |
|------|--------|------------|----------------|
| 1 | E | 12.7% | 18 (ᛖ) |
| 2 | T | 9.1% | 16 (ᛏ) |
| 3 | A | 8.2% | 24 (ᚪ) |
| 4 | O | 7.5% | 3 (ᚩ) |
| 5 | I | 7.0% | 10 (ᛁ) |
| 6 | N | 6.7% | 9 (ᚾ) |
| 7 | S | 6.3% | 15 (ᛋ) |
| 8 | H | 6.1% | 8 (ᚻ) |
| 9 | R | 6.0% | 4 (ᚱ) |
| 10 | TH | ~3.5% | 2 (ᚦ) |

Note: The digraphs (TH, NG, EA, etc.) complicate standard frequency analysis.
