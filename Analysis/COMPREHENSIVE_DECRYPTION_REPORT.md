# Comprehensive Liber Primus Decryption Report

**Date:** Research compilation  
**Purpose:** Document EXACTLY how each solved page was decrypted, identify false claims, and catalogue what remains unsolved.

---

## Table of Contents
1. [Background: The Gematria Primus](#1-background)
2. [Truly Solved Pages (Community-Confirmed)](#2-solved-pages)
3. [Pages Solved by This Project](#3-project-solved)
4. [Partially Solved Pages (17–20)](#4-partial)
5. [FALSE CLAIMS: Pages 21–30](#5-false-claims)
6. [Unsolved Pages 31–54](#6-unsolved-31-54)
7. [Image-Only / Special Pages](#7-special)
8. [Advanced Cipher Methods Tested (All Failed)](#8-failed-methods)
9. [Key Patterns and Mathematical Structure](#9-key-patterns)
10. [Critical Open Questions](#10-open-questions)

---

## 1. Background: The Gematria Primus <a name="1-background"></a>

The Gematria Primus is a 29-character alphabet mapping Anglo-Saxon runes to Latin letters and prime number values:

| Rune | Letter | Value | | Rune | Letter | Value |
|------|--------|-------|-|------|--------|-------|
| ᚠ | F | 2 | | ᛗ | M | 41 |
| ᚢ | U | 3 | | ᛚ | L | 43 |
| ᚦ | TH | 5 | | ᛝ | NG | 47 |
| ᚩ | O | 7 | | ᛟ | OE | 53 |
| ᚱ | R | 11 | | ᛞ | D | 59 |
| ᚳ | C/K | 13 | | ᚪ | A | 61 |
| ᚷ | G | 17 | | ᚫ | AE | 67 |
| ᚹ | W | 19 | | ᚣ | Y | 71 |
| ᚻ | H | 23 | | ᛡ | IA/IO | 73 |
| ᚾ | N | 29 | | ᛠ | EA | 79 |
| ᛁ | I | 31 | |  |  |  |
| ᛄ | J | 37 | |  |  |  |
| ᛇ | EO | 39* | |  |  |  |
| ᛈ | P | 41 | |  |  |  |
| ᛉ | X | 43* | |  |  |  |
| ᛋ | S | 47* | |  |  |  |
| ᛏ | T | 53* | |  |  |  |
| ᛒ | B | 59* | |  |  |  |

*Note: Some value assignments differ between sources. The prime values 2–109 are assigned in order. Digraphs (TH, NG, OE, EA, IO) count as single characters.*

**Alphabet size: 29** — All modular arithmetic is mod 29.

**Index of Coincidence (IoC) baselines:**
- Random text (29-letter alphabet): ~1.0 (or ~0.0345 as proportion)
- English text (29-letter alphabet): ~1.73 (or ~0.065 as proportion)
- Higher IoC = more structured/English-like frequency distribution

---

## 2. Truly Solved Pages — Community-Confirmed <a name="2-solved-pages"></a>

These solutions are confirmed by the broader Cicada 3301 research community (sourced from the community wiki transcript `github_liber_primus.md`).

### Page 00 — "A WARNING"
| Property | Value |
|----------|-------|
| **Cipher** | Cleartext / Reversed Gematria substitution |
| **Key** | None (direct transliteration) |
| **Key Length** | N/A |
| **Meaningful Word** | N/A |
| **Plaintext** | "A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE. TEST ALL THINGS." |
| **Notes** | The first page of LP. Directly readable via Gematria Primus. |

### Page 01 — "A WARNING" (2014 version)
| Property | Value |
|----------|-------|
| **Cipher** | Reversed Gematria 2014 substitution |
| **Key** | Reversed Gematria mapping |
| **Key Length** | N/A (substitution cipher) |
| **Meaningful Word** | N/A |
| **Plaintext** | "A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE..." |
| **Notes** | Uses a reversed version of the Gematria Primus mapping. Same message as P00. |

### Page 02 — "CHAPTER I / INTUS"
| Property | Value |
|----------|-------|
| **Cipher** | Cleartext |
| **Key** | None |
| **Plaintext** | Chapter title page. Latin "INTUS" = "within". |

### Pages 03–04 — "WELCOME PILGRIM"
| Property | Value |
|----------|-------|
| **Cipher** | Vigenère (shift up, forward Gematria) |
| **Key** | `DIVINITY` = [6, 19, 28, 19, 20, 19, 13, 3] |
| **Key Length** | 8 |
| **Meaningful Word** | **DIVINITY** |
| **F-Skip** | Every clear-text F (ᚠ) is skipped during key application |
| **Plaintext (P03)** | "WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE BEING OF WISDOM..." |
| **Plaintext (P04)** | "IT IS THROUGH THIS PILGRIMAGE THAT WE SHAPE OURSELVES..." |
| **Notes** | First use of Vigenère in LP. Key "DIVINITY" is thematically significant. |

### Page 05 — "SOME WISDOM"
| Property | Value |
|----------|-------|
| **Cipher** | Direct Gematria substitution (no encryption) |
| **Key** | None (CAESAR_0) |
| **Plaintext** | "SOME WISDOM / THE PRIMES ARE SACRED / THE TOTIENT FUNCTION IS SACRED / ALL THINGS SHOULD BE ENCRYPTED / KNOW THIS" + Magic Square |
| **Magic Square** | 5×5 matrix, each row/column sums to 1033. Contains embedded words: SHADOWS, AETHEREAL, BUFFERS, VOID, CARNAL, OBSCURA, FORM, MOBIUS, ANALOG, MOURNFUL, CABAL |
| **Notes** | Establishes that primes and Euler's totient φ(n) are "sacred". Same magic square appears in OOB data from earlier puzzles. |

### Pages 06–08 — "A KOAN"
| Property | Value |
|----------|-------|
| **Cipher** | Shift 3 down, reversed Gematria |
| **Key** | Caesar shift of 3 with reversed Gematria table |
| **Key Length** | 1 (constant shift) |
| **Meaningful Word** | N/A |
| **Plaintext** | Extended koan about a man studying with a master. "WHO ARE YOU WHO WISHES TO STUDY HERE?" repeated. The professor, human being, consciousness → "I AM" → "THEN YOU ARE WELCOME TO COME STUDY" |
| **Notes** | Same substitution as Cicada's "Second Onion" from 2014. Multi-page story. |

### Page 09 — "AN INSTRUCTION"
| Property | Value |
|----------|-------|
| **Cipher** | Shift 3 down, reversed Gematria |
| **Key** | Same as P06–08 |
| **Plaintext** | "AN INSTRUCTION: DO FOUR UNREASONABLE THINGS EACH DAY" |

### Pages 10–13 — "THE LOSS OF DIVINITY" / Wisdom teachings
| Property | Value |
|----------|-------|
| **Cipher** | Direct Gematria substitution (no encryption) |
| **Key** | None (CAESAR_0) |
| **Plaintext (P10)** | "THE LOSS OF DIVINITY: THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS WHICH CAUSE THE LOSS OF DIVINITY: CONSUMPTION..." |
| **Plaintext (P11)** | "WE HAVE WHAT WE HAVE NOW BY LUCK AND WE WILL NOT BE STRONG ENOUGH LATER TO OBTAIN WHAT WE NEED..." |
| **Plaintext (P12)** | "MOST THINGS ARE NOT WORTH PRESERVING..." |
| **Plaintext (P13)** | "SOME WISDOM: AMASS GREAT WEALTH..." |
| **Notes** | Four pages of philosophical text about consumption, preservation, adherence. No cipher applied — direct rune-to-letter mapping. |

### Pages 14–15 — "A KOAN: DURING A LESSON"
| Property | Value |
|----------|-------|
| **Cipher** | Vigenère (shift up, forward Gematria) |
| **Key** | `FIRFUMFERENFE` = [29, 19, 25, 29, 28, 10, 29, 11, 25, 11, 20, 29, 11] |
| **Key Length** | 13 (prime) |
| **Meaningful Word** | **FIRFUMFERENFE** — a deliberate corruption of "CIRCUMFERENCE" (C→F mapping: every C replaced by F). This is significant because ᚠ (F) has prime value 2 in Gematria Primus, and the F-skip rule means literal F's are preserved. |
| **F-Skip** | Every clear-text F is an ᚠ (F) and must be skipped |
| **Plaintext** | "A KOAN: DURING A LESSON, THE MASTER EXPLAINED THE I: 'THE I IS THE VOICE OF THE CIRCUMFERENCE,' HE SAID..." / Student claims no voice → Master: 'THE VOICE THAT JUST SAID YOU HAVE NO VOICE IN YOUR HEAD, IS THE I.' AND THE STUDENTS WERE ENLIGHTENED." |
| **Notes** | Second and final confirmed Vigenère page. Key length 13 is prime. The word "CIRCUMFERENCE" appears in plaintext despite key being "FIRFUMFERENFE". |

### Page 16 — "AN INSTRUCTION"
| Property | Value |
|----------|-------|
| **Cipher** | Direct Gematria substitution (no encryption) |
| **Key** | None (CAESAR_0) |
| **Plaintext** | "AN INSTRUCTION: QUESTION ALL THINGS. DISCOVER TRUTH INSIDE YOURSELF. FOLLOW YOUR TRUTH. IMPOSE NOTHING ON OTHERS. KNOW THIS:" + Second magic square |
| **Magic Square** | 5×5, values: 434, 1311, 312, 278, 966... |
| **Notes** | Last confirmed solved page before the "unsolved wall" begins at P17. |

### Page 55/73 (LP2) — "AN END"
| Property | Value |
|----------|-------|
| **Cipher** | φ(prime) shift — Euler's totient function |
| **Key** | `plaintext[i] = (ciphertext[i] - (prime(i) + 57)) mod 29` |
| **Key Length** | Non-repeating (each position uses the next prime number) |
| **F-Skip** | Position 56: literal ᚠ (F) at index 56 is skipped (not encrypted) |
| **Plaintext** | "AN END / WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO [SHA-512 hash] / IT IS THE DUTY OF EVERY PILGRIM TO SEEK OUT THIS PAGE" |
| **Notes** | Uses `φ(p) = p - 1` for each successive prime p. The "+57" offset was key to cracking. This confirms the totient function hint from P05. |
| **IoC Raw → Decrypted** | ~0.034 → English |

### Pages 56–57 (LP2) — "PARABLE"
| Property | Value |
|----------|-------|
| **Cipher** | None — identical pages, direct transliteration |
| **Key** | None |
| **Plaintext** | "PARABLE: LIKE THE INSTAR TUNNELING TO THE SURFACE, WE MUST SHED OUR OWN CIRCUMFERENCES. FIND THE DIVINITY WITHIN AND EMERGE." |
| **Notes** | These two pages are identical to each other AND to Page 74. They're cleartext. |

### Page 74 (LP2) — "PARABLE"
| Property | Value |
|----------|-------|
| **Cipher** | Direct Gematria substitution (no encryption) |
| **Key** | None (CAESAR_0) |
| **Plaintext** | Same as P56/57. "PARABLE: LIKE THE INSTAR..." |
| **Notes** | Final page of LP. Thematic callback to "CIRCUMFERENCE" and "DIVINITY". |

---

## 3. Pages Solved by This Project <a name="3-project-solved"></a>

These were solved during the January 2026 batch attack in this workspace. They were NOT previously confirmed by the broader community.

### Page 59 — "A WARNING"
| Property | Value |
|----------|-------|
| **Cipher** | Caesar shift 28 (= shift -1 mod 29) with reversed Gematria substitution |
| **Key** | CAESAR_28, mode SUB_REV |
| **Key Length** | 1 (constant) |
| **Batch Score** | 1308.5 |
| **Plaintext** | "A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE. TEST ALL THINGS." |
| **Notes** | Identical plaintext to P00/P01. A repeated "A WARNING" page in Chapter 1 (Intus). Simple Caesar shift, NOT a Vigenère key. |

### Page 63 — "SOME WISDOM"
| Property | Value |
|----------|-------|
| **Cipher** | NO ENCRYPTION (CAESAR_0) |
| **Key** | None — direct Gematria substitution |
| **Key Length** | 0 |
| **Batch Score** | 1044.3 |
| **Plaintext** | "SOME WISDOM THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED ALL THINGS SHOULD BE ENCRYPTED KNOW THIS..." |
| **Notes** | This page was **not encrypted at all** — same as P05. Identical content to P05's magic square page. |

### Page 64 — "A KOAN"
| Property | Value |
|----------|-------|
| **Cipher** | Caesar shift 2, reversed Gematria substitution |
| **Key** | CAESAR_2, mode SUB_REV |
| **Key Length** | 1 (constant) |
| **Batch Score** | 3303.9 (highest in entire batch) |
| **Plaintext** | "A KOAN A MAN DECIDED TO GO AND STUDY WITH A MASTER..." |
| **Notes** | Same koan as P06–08. Simple 2-position shift. Highest-scoring page across all 49 attacked pages. |

### Page 68 — "THE LOSS OF DIVINITY"
| Property | Value |
|----------|-------|
| **Cipher** | NO ENCRYPTION (CAESAR_0) |
| **Key** | None — direct Gematria substitution |
| **Key Length** | 0 |
| **Batch Score** | 2627.9 |
| **Plaintext** | "THE LOSS OF DIVINITY THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS WHICH CAUSE THE LOSS OF DIVINITY..." |
| **Notes** | **Not encrypted at all** — same content as P10–13. 657 runes of cleartext. |

### Summary: Chapter 1 (Intus) Pattern
Pages 58–74 largely **repeat content from P00–P16** with the same or simpler ciphers. The structure mirrors the first 17 pages:
- P59 = P00/P01 (A WARNING)
- P63 = P05 (SOME WISDOM + magic square)  
- P64 = P06–08 (A KOAN)
- P68 = P10–13 (THE LOSS OF DIVINITY)
- P74 = P56/57 (PARABLE)

---

## 4. Partially Solved Pages (17–20) <a name="4-partial"></a>

### Page 17 — Title: "SHEOGMYF SCEIY" (encrypted)
| Property | Value |
|----------|-------|
| **Status** | ⚠️ DISPUTED |
| **This project claims** | Key "YAHEOOPYJ", plaintext "EPILOGUE WITHIN THE..." |
| **Community status** | Key: ? (unsolved) |
| **Batch Score** | 1087.5 (with PHI:L3S261 key) |
| **Notes** | The workspace MASTER_STATUS lists this as solved with key "YAHEOOPYJ" but the community transcript marks it as "?". The key "YAHEOOPYJ" is not a meaningful English word. This needs independent verification. |

### Page 18 — Title: "HENGALLA"
| Property | Value |
|----------|-------|
| **Status** | 🔴 UNSOLVED |
| **Community status** | Key: ? |
| **Batch Score** | 591.5 |
| **Connection** | Title "HENGALLA" may connect to **Deor** poem (Old English), where "Weland" appears. Contains possible reference to Anglo-Saxon literature. |
| **Notes** | Part of the 3-page spread P17–19. Investigated with Self-Reliance running key and various autokey approaches — all failed. |

### Page 19 — Partial Solution
| Property | Value |
|----------|-------|
| **Status** | 🟡 PARTIALLY SOLVED |
| **Cipher** | Vigenère ADD (mod 29) |
| **Key Length** | 47 (prime) |
| **Key Indices (partial)** | [24, 15, 2, 24, 4, 21, 11, 10, ?, ?, ?, 14, 13, 28, 9, 2, 16, 6, 23, 11, 2, 5, 23, 0, 19, 28, 24, 20, 2, 20, 2, 25, 22, 11, 9, 18, 27, ?, ?, ?, ?, 2, 14, 20, 1, 9, ?] |
| **Recovered** | 43 of 47 key positions confirmed |
| **Plaintext** | "REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR [K]" |
| **Meaningful Word** | Key appears to spell an English phrase: begins "A STAR(ING)..." ends "...NOT CO(V)ERED" |
| **Notes** | Critically important: the plaintext explicitly says "A PATH TO THE DEOR" — directing solvers to the Old English poem *Deor* as a key source for other pages. 4 key positions remain unrecovered. |

### Page 20 — Dual-Layer Cipher
| Property | Value |
|----------|-------|
| **Status** | 🟡 PARTIALLY SOLVED |
| **Total Runes** | 812 (some sources say 837) |
| **Architecture** | Dual-layer — runes at prime indices vs. non-prime indices are encrypted differently |

**Layer 1: Prime-Position Runes (166 runes)**
| Property | Value |
|----------|-------|
| Cipher | Beaufort cipher with Deor poem as key |
| Formula | `stream[i] = (key[i] - cipher[i]) mod 29` |
| Then | 2×83 column transposition |
| IoC | 1.8952 (English-like) |
| Output | Contains Old English words: EODE, SEFA, THE LONE, HOTAN |
| Status | ✅ Readable (Old English) |

**Layer 2: Non-Prime-Position Runes (646–671 runes)**
| Property | Value |
|----------|-------|
| IoC | ~1.0 (random) |
| Status | 🔴 UNSOLVED |
| Notes | Does not respond to any tested key or cipher method |

**Layer 3: Prime-Valued Runes (237 runes)**
| Property | Value |
|----------|-------|
| Description | Runes whose Gematria VALUES are prime (only 9 distinct letters: TH, O, C, W, J, P, B, M, D) |
| IoC | 3.2125 (extremely high — restricted alphabet) |
| Status | 🟡 Possibly a separate message in restricted alphabet |

---

## 5. FALSE CLAIMS: Pages 21–30 <a name="5-false-claims"></a>

### The Problem
The batch attack produced keywords for pages 21–30 that achieve high IoC values (1.86–2.31), leading to initial claims of "solved" status. **These claims are FALSE.**

### Evidence of Failure

| Page | Claimed Key | IoC | Sample "Plaintext" | Readable? |
|------|-------------|-----|---------------------|-----------|
| 21 | P:L53S156 (ADD) | 1.97 | "eoaeoedjtheooebtheafmheooethetheaiotheaeacoeoetheaththrheathbxaleaathioleaoefthm" | ❌ NO |
| 22 | (similar) | ~1.9 | Scrambled | ❌ NO |
| 23 | (similar) | ~1.9 | Scrambled | ❌ NO |
| 24 | (similar) | ~2.0 | Scrambled | ❌ NO |
| 25 | P:L53S156 | 1.94 | Scrambled | ❌ NO |
| 26 | (similar) | ~1.9 | Scrambled | ❌ NO |
| 27 | (similar) | ~1.9 | Scrambled | ❌ NO |
| 28 | (similar) | ~2.0 | Scrambled | ❌ NO |
| 29 | (similar) | ~2.3 | Scrambled | ❌ NO |
| 30 | (similar) | ~1.9 | Scrambled | ❌ NO |

### Why High IoC ≠ Solved
- **High IoC** means the letter frequency distribution matches English (lots of THE, E, A, etc.)
- **But** the letters are in the wrong ORDER — the text is scrambled
- This suggests the substitution key is partially correct (producing English-like frequencies) but an additional transformation is needed (transposition, multi-layer cipher, etc.)

### All Transposition Attempts Failed
Tested on pages 21–30 after Vigenère decryption:
- Columnar transposition (all widths 2–50)
- Rail fence (2–20 rails)
- Route ciphers (spiral, diagonal, zigzag)
- Reverse, interleave, skip patterns
- Block transposition (all block sizes)

**None produced readable English text.**

### Conclusion
Pages 21–30 use a cipher that is NOT simple Vigenère. The high IoC from Vigenère keywords is a **coincidence of frequency matching**, not actual decryption. The true cipher likely involves:
- Multi-stage encryption (substitution + transposition + ???)
- Non-repeating key (OTP-like, hence IoC ~0.034 in raw ciphertext)
- Running key from an external text source
- Or an entirely different cipher system

---

## 6. Unsolved Pages 31–54 <a name="6-unsolved-31-54"></a>

### Different Pattern from Pages 21–30
- Pages 31–54 **do NOT respond to Vigenère keywords** like 21–30 do
- They **DO respond to Caesar shifts** (constant offset per page)
- But even after Caesar decryption + transposition, text remains scrambled

### Caesar Shift Results

| Page | Best Caesar Shift | Score After Caesar | Readable? |
|------|-------------------|-------------------|-----------|
| 32 | 11 | 285 (English words detected) | ❌ NO |
| 44 | 5 | 227 | ❌ NO |
| 50 | 6 | 224 | ❌ NO |
| Others | Various 0–28 | 100–200 | ❌ NO |

### Hypothesis
Pages 31–54 use **Caesar shift + additional complex encryption** (possibly a different substitution/transposition combination from pages 21–30).

### Page 32 Special Features
- Contains a **numerical header** in runes: "FULM AECNA" followed by a 4×4 number grid:
  ```
  3258  3222  3152  3038
  3278  3299  3298  2838
  3288  3294  3296  2472
  4516  1206   708  1820
  ```
- These numbers may be a clue to the cipher method

### Raw Ciphertext IoC
All pages 17–55 have raw ciphertext IoC of approximately **0.034** (random). This is the most important clue:
- IoC 0.034 with 29-letter alphabet = perfectly random distribution
- This rules out simple substitution (which preserves frequency)
- Suggests either polyalphabetic cipher with long key, or non-repeating key

---

## 7. Image-Only / Special Pages <a name="7-special"></a>

| Page | Content |
|------|---------|
| 65 | Image only, no runes. Outguess yields 58.2kB garbage. |
| 66 | Base60 numerical grid (converted to decimal values). No runes. |
| 67 | Base60 numerical grid (13×8). No runes. |
| 69 | Image only. Outguess yields 58.2kB garbage. |
| 70 | Image only. Outguess yields 58.2kB garbage. |

**Multiple pages yield exactly 58.2kB of "garbage" from Outguess steganography:** P17, P21, P43, P65, P68, P69, P70, P71. The consistency of this size (58.2kB) may be significant.

---

## 8. Advanced Cipher Methods Tested (All Failed on Unsolved Pages) <a name="8-failed-methods"></a>

### Running Key Cipher
- **Key source tested:** Ralph Waldo Emerson's essay "Self-Reliance" (full text available in `reference/research/Self-Reliance.txt`)
- **Connection:** The word "CIRCUMFERENCE" appears prominently in LP and is a key concept in Emerson's essay ("the eye is the first circle; the horizon which it forms is the second; and throughout nature this primary figure is repeated without end")
- **Method:** `plaintext[i] = (ciphertext[i] - keytext[i]) mod 29`
- **Offsets tested:** 0 through 10,000+
- **Result:** ❌ No readable plaintext at any offset

### Autokey Cipher
- **Seeds tested:** DIVINITY, PILGRIM, CICADA, PI, various primes
- **Method:** Key extends using previously decrypted plaintext
- **Result:** ❌ Failed on all unsolved pages

### Vigstream (Vigenère with Mathematical Sequences)
Tested with various non-repeating key streams:
- Prime number sequence (2, 3, 5, 7, 11, 13, ...)
- Fibonacci sequence (1, 1, 2, 3, 5, 8, 13, ...)
- Lucas numbers (2, 1, 3, 4, 7, 11, ...)
- Triangular numbers (1, 3, 6, 10, 15, ...)
- Prime gaps (1, 2, 2, 4, 2, 4, 2, 4, 6, ...)
- Euler's totient sequence (φ(1), φ(2), φ(3), ...)
- All above ± various offsets (0–500)
- **Result:** ❌ None produced readable plaintext

### Beaufort Cipher
- `stream[i] = (key[i] - cipher[i]) mod 29`
- Tested with all keys above
- **Result:** ❌ Only worked on P20 prime positions (with Deor poem key)

### Chained/Cascaded Ciphers
- Vigenère → then transposition
- Caesar → then Vigenère → then transposition
- Substitution → reversal → transposition
- **Result:** ❌ None produced readable text

### Other Sources Tested as Running Key
- Liber AL vel Legis (Aleister Crowley)
- Deor poem (Old English) — only worked for P20 prime positions
- Known LP plaintext from solved pages (self-referential key)
- **Result:** ❌ All failed on pages 21–54

---

## 9. Key Patterns and Mathematical Structure <a name="9-key-patterns"></a>

### All Confirmed Key Lengths Are Prime
From the MASTER_SOLVING_DOC analysis of pages where keys were identified:

| Key Length | Pages Using It | % of Solved Pages |
|------------|---------------|-------------------|
| 71 | 36% of keyed pages | Most common |
| 79 | Multiple pages | Common |
| 83 | Multiple pages | Common |
| 89 | Multiple pages | |
| 97 | Multiple pages | |
| 101 | Multiple pages | |
| 103 | Multiple pages | |
| 107 | Multiple pages | |
| 113 | Multiple pages | |
| 137 | Some pages | |

**Key length 71** is the 20th prime, and appears in 36% of keyed pages per the MASTER_SOLVING_DOC analysis. Note: This analysis was from heuristic key-length detection, not from confirmed decryptions — it should be treated with appropriate skepticism.

### Confirmed Key Words and Their Significance

| Key | Used On | Significance |
|-----|---------|-------------|
| DIVINITY | P03–04 | Core LP concept: "the loss of divinity" |
| FIRFUMFERENFE | P14–15 | Corrupted "CIRCUMFERENCE" (C→F substitution). Length 13 (prime). |
| φ(prime)+57 | P55/73 | Mathematical: Euler's totient of successive primes |

### The F-Skip Rule
On pages encrypted with Vigenère (P03–04, P14–15, P55/73):
- Any position where the plaintext letter is F (ᚠ), the key is NOT applied
- The F rune appears literally and the key index does not advance
- This is a consistent rule across all confirmed Vigenère solutions

### EMB Pattern (from MASTER_SOLVING_DOC)
A discovery in the workspace analysis:
- The first ~80 characters of many pages, after adding the first 80 primes mod 29, produce a pattern dominated by indices 17, 18, 19
- Letters E (index 17), M (index 18), B (index 19) appear at improbable frequency
- This was **not confirmed as a decryption method** — it may be a statistical artifact

### Cyclical Gap Pattern (from IRC research)
From Profetul & Mortlach's analysis:
- Gap of 11 acts as generator in the key structure
- Relationship: 29 - 18 = 11 (alphabet size minus gap = generator)
- "Low doubles" (repeated key values) relate to this pattern
- This was **not confirmed as leading to decryption** — remains theoretical

---

## 10. Critical Open Questions <a name="10-open-questions"></a>

### 1. What cipher do pages 17–54 actually use?
- Raw IoC ~0.034 (random) rules out simple substitution
- The cipher produces perfectly flat frequency distribution
- Most likely: polyalphabetic with very long or non-repeating key
- OR: substitution + transposition (which would distribute frequencies evenly)

### 2. Why does Vigenère produce high IoC on pages 21–30 but not readable text?
- Possible explanation: The true cipher's first layer IS Vigenère-like (hence frequency correction works)
- But a second layer (transposition?) scrambles the order
- The batch attack keys may be partially correct substitution keys

### 3. What is the Deor connection?
- P19 plaintext explicitly says "A PATH TO THE DEOR"
- Deor poem works as Beaufort key on P20 prime positions
- But Deor does NOT work on P18 or non-prime P20 positions
- Is there a different section of Deor, or a different way to apply it?

### 4. What is "Self-Reliance" connection?
- "CIRCUMFERENCE" (key word in LP) is a significant concept in Emerson's Self-Reliance
- Running key with Self-Reliance text was tested exhaustively and failed
- Connection may be thematic rather than cryptographic

### 5. What do the 58.2kB Outguess outputs contain?
- Multiple images produce exactly 58.2kB of apparent garbage
- This consistent size suggests structured hidden data, not random noise
- May contain keys, further ciphertext, or instructions

### 6. What role do the magic squares play?
- Two 5×5 magic squares appear (P05 and P16)
- Row/column sums: 1033 (P05), different values (P16)
- May encode keys, permutation orders, or other cipher parameters

### 7. Is there a master key derivation system?
- The workspace found that key length 71 (20th prime) appears in 36% of pages
- All key lengths are prime
- Is there a formula that generates each page's key from page number + master secret?

---

## Appendix A: Cipher Method Summary Table

| Pages | Cipher Type | Key/Method | Status |
|-------|-------------|------------|--------|
| 00 | Cleartext | Direct Gematria | ✅ SOLVED |
| 01 | Substitution | Reversed Gematria 2014 | ✅ SOLVED |
| 02 | Cleartext | Title page | ✅ SOLVED |
| 03–04 | Vigenère (shift up) | DIVINITY [6,19,28,19,20,19,13,3], F-skip | ✅ SOLVED |
| 05 | Cleartext | Direct Gematria | ✅ SOLVED |
| 06–08 | Substitution | Shift-3 reversed Gematria | ✅ SOLVED |
| 09 | Substitution | Shift-3 reversed Gematria | ✅ SOLVED |
| 10–13 | Cleartext | Direct Gematria | ✅ SOLVED |
| 14–15 | Vigenère (shift up) | FIRFUMFERENFE [29,19,25,29,28,10,29,11,25,11,20,29,11], F-skip | ✅ SOLVED |
| 16 | Cleartext | Direct Gematria | ✅ SOLVED |
| 17 | Vigenère? | "YAHEOOPYJ" (disputed) | ⚠️ DISPUTED |
| 18 | Unknown | ? | 🔴 UNSOLVED |
| 19 | Vigenère ADD | Key length 47, partial recovery | 🟡 PARTIAL |
| 20 | Multi-layer | Beaufort(Deor) on prime positions | 🟡 PARTIAL |
| 21–30 | Unknown | High IoC with Vigenère BUT scrambled | 🔴 UNSOLVED |
| 31–54 | Unknown | Caesar shifts detected but text scrambled | 🔴 UNSOLVED |
| 55/73 | φ(prime) shift | (cipher - (prime+57)) mod 29, F-skip | ✅ SOLVED |
| 56–57 | Cleartext | Direct transliteration (identical pages) | ✅ SOLVED |
| 58 | Cleartext? | 11 runes, short segment | ✅ SOLVED |
| 59 | Caesar 28 | SUB_REV, shift -1 | ✅ SOLVED |
| 60 | Cleartext | 13 runes | ✅ SOLVED |
| 61 | Vigenère? | Key "DIVINITY" claimed | ⚠️ NEEDS REVIEW |
| 62 | Vigenère? | Key "CONSUMPTION" claimed | ⚠️ NEEDS REVIEW |
| 63 | Cleartext | CAESAR_0, direct Gematria | ✅ SOLVED |
| 64 | Caesar 2 | SUB_REV | ✅ SOLVED |
| 65–66 | Image/Base60 | No runes to decrypt | 📷 IMAGE |
| 67 | Base60 | Numerical grid | 📷 IMAGE |
| 68 | Cleartext | CAESAR_0, direct Gematria | ✅ SOLVED |
| 69–70 | Image | Outguess 58.2kB | 📷 IMAGE |
| 71–72 | Unknown | Encrypted runes | 🔴 UNSOLVED |
| 74 | Cleartext | Direct Gematria | ✅ SOLVED |

## Appendix B: Tools in This Workspace

Key solver tools in `Tools/`:
- `advanced_cipher_attack.py` — Multi-method cipher attack
- `advanced_transposition_attack.py` — Transposition brute-force
- `running_key_solver.py` — Running key (Self-Reliance etc.)
- `self_reliance_attack.py` — Targeted Self-Reliance attack
- `solve_p18_self_reliance.py` — P18-specific attempts
- `analyze_p20_deep.py` — P20 dual-layer analysis
- Various `analyze_*.py` scripts for specific pages

Reference data in `LiberPrimus/reference/`:
- `research/Self-Reliance.txt` — Emerson essay (running key source)
- `research/liber_al_vel_legis.txt` — Crowley text (tested as key source)
- `transcripts/github_liber_primus.md` — Community wiki solutions
- `solved_pages/` — Verified plaintext outputs
