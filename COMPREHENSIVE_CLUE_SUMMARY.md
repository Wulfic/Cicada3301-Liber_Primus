# Comprehensive Clue Summary for Cracking Liber Primus Pages 18-54

*Generated from exhaustive review of all workspace documentation*

---

## Table of Contents
1. [Mathematical Formulas, LFSR Parameters, Cipher Specifications](#1-mathematical-formulas-lfsr-parameters-cipher-specifications)
2. [The 58.2kB Outguess Data](#2-the-582kb-outguess-data)
3. [Missing Telnet Primes & The Gap 71→1229](#3-missing-telnet-primes--the-gap-711229)
4. [Fibonacci, Spirals, and Non-Linear Reading](#4-fibonacci-spirals-and-non-linear-reading)
5. [The Deor Poem Connection](#5-the-deor-poem-connection)
6. [Specific Key Values, Polynomials, LFSR Taps](#6-specific-key-values-polynomials-lfsr-taps)
7. [LFSR over GF(29) — What It Means](#7-lfsr-over-gf29--what-it-means)
8. [IRC, Onion Site, and External Clues](#8-irc-onion-site-and-external-clues)
9. [Page-by-Page Attack Vectors](#9-page-by-page-attack-vectors)
10. [Proven Cipher Methods from Solved Pages](#10-proven-cipher-methods-from-solved-pages)
11. [Community Research Key Findings](#11-community-research-key-findings)
12. [Profetul/IRC Gap-Pattern Hypothesis](#12-profetulirc-gap-pattern-hypothesis)
13. [Raiden's Contest Hex Data](#13-raidens-contest-hex-data)

---

## 1. Mathematical Formulas, LFSR Parameters, Cipher Specifications

### Gematria Primus (29-character alphabet)
**Source:** `LiberPrimus/GEMATRIA_PRIMUS.md`

| Index | Latin | Prime Value |
|-------|-------|-------------|
| 0 | F | 2 |
| 1 | U | 3 |
| 2 | TH | 5 |
| 3 | O | 7 |
| 4 | R | 11 |
| 5 | C/K | 13 |
| 6 | G | 17 |
| 7 | W | 19 |
| 8 | H | 23 |
| 9 | N | 29 |
| 10 | I | 31 |
| 11 | J | 37 |
| 12 | EO | 41 |
| 13 | P | 43 |
| 14 | X | 47 |
| 15 | S | 53 |
| 16 | T | 59 |
| 17 | B | 61 |
| 18 | E | 67 |
| 19 | M | 71 |
| 20 | L | 73 |
| 21 | NG/ING | 79 |
| 22 | OE | 83 |
| 23 | D | 89 |
| 24 | A | 97 |
| 25 | AE | 101 |
| 26 | Y | 103 |
| 27 | IA/IO | 107 |
| 28 | EA | 109 |

### Proven Cipher Formulas

1. **Vigenère SUB (mod 29):**
   ```
   plaintext[i] = (ciphertext[i] - key[i % key_len]) % 29
   ```
   - Used in most solved pages. Key lengths are ALWAYS PRIME.
   - **Source:** `Master_Tracking/MASTER_SOLVING_DOC.md`

2. **φ(prime) Stream Cipher:**
   ```
   plaintext[i] = (ciphertext[i] - (prime[i] - 1)) % 29
   ```
   where `prime[i]` is the i-th prime from a starting offset.
   - **Literal F Rule:** If rune = F (index 0), it passes through UNENCRYPTED and the key counter is NOT incremented.
   - Works on Pages 55, 73.
   - **Source:** `Master_Tracking/MASTER_SOLVING_DOC.md`, `Master_Tracking/KEY_HINTS_FOR_UNSOLVED_PAGES.md`

3. **Beaufort Cipher:**
   ```
   plaintext[i] = (key[i] - ciphertext[i]) % 29
   ```
   - Used for Page 20 prime-position extraction.
   - **Source:** `Analysis/P20_Partial_Solution.md`

4. **Caesar Shift (SUB/ADD):**
   ```
   SUB: plaintext[i] = (ciphertext[i] - shift) % 29
   ADD: plaintext[i] = (ciphertext[i] + shift) % 29
   ```
   - Pages 59 (CAESAR_28 SUB_REV), 64 (CAESAR_2 SUB_REV), 63 & 68 (CAESAR_0 = cleartext).
   - **Source:** `Master_Tracking/BREAKTHROUGH_DISCOVERIES.md`

5. **Community-Proposed Formula for Unsolved Pages:**
   ```
   plaintext[i] = (±G(rune[i]) ± F(i)) % 29
   ```
   where G() is Gematria mapping and F(i) is a running key derived from primes/totient.
   - **Source:** `Analysis/COMMUNITY_RESEARCH_REPORT.md`

### Key Length Evidence
- P18 body: Vigenère SUB, **key length 53** (prime). **Source:** `Master_Tracking/MASTER_SOLVING_DOC.md`
- P19: Vigenère ADD, **key length 47** (prime). **Source:** `Analysis/p19_final_report.md`
- P19 key indices (0-42 confirmed): `[24, 15, 2, 24, 4, 21, 11, 10, 20, 16, 9, 19, 26, 11, 7, 5, 11, 6, 27, 8, 22, 25, 21, 16, 25, 0, 27, 9, 21, 7, 27, 15, 21, 9, 3, 16, 5, 22, 18, 4, 5, 18, 23, 0, 0, 0, 0]`
- P19 key decodes to English: starts "A STARING..." ends "...NOT COVERED"

### LFSR Characteristics (for unsolved pages)
- Frequency analysis shows **extremely uniform rune distribution** (ratio < 2:1 most-to-least frequent).
- This is diagnostic of **LFSR-based stream cipher**, not standard Vigenère.
- **Source:** `Analysis/COMMUNITY_RESEARCH_REPORT.md`

---

## 2. The 58.2kB Outguess Data

### What It Is
PGP-signed hex data blocks embedded via **Outguess steganography** in the JPEG images of Liber Primus pages. Each LP page image file had extractable hidden data.

### Where to Find It
- Community repository: `rtkd/iddqd` on GitHub, folder `lp_outguessed/`, files `00.txt` through `74.txt`.
- **Source:** `Analysis/COMMUNITY_RESEARCH_REPORT.md`

### Which Pages Have Outguess Data
- **Confirmed data:** Pages 00, 01, 02, 03 (PGP-signed hex blocks documented in `Analysis/Reference_Docs/people_liber_primus.md`)
- **Community-identified:** Pages 17, 21, 43, 65, 68-71
- **Page 03 message:** "Let the text guide you. Good luck. 3301" + large hex block (appears to be embedded JPEG data)

### Significance
- The Outguess data from unsolved pages (especially 17, 21, 43) could contain:
  - Encryption keys
  - Hints or instructions
  - Additional ciphertext
- **Pages 65, 68-71** show "garbage" on Outguess extraction — may be encrypted key material.
- The data has NEVER been fully analyzed or used in decryption attempts.

---

## 3. Missing Telnet Primes & The Gap 71→1229

### The Gap
When Cicada's telnet server delivered primes, there was a conspicuous gap: primes jumped from **71 to 1229**, skipping approximately **200 consecutive primes** (73, 79, 83, 89, 97, ..., 1213, 1217, 1223).

### Significance
- These are the **21st prime (73) through approximately the 200th prime (1223)**.
- In Gematria Primus, index 19 = M = prime 71, and index 20 = L = prime 73. The gap starts RIGHT at the boundary of the 29-rune alphabet.
- **Source:** `Analysis/COMMUNITY_RESEARCH_REPORT.md`

### Possible Uses
1. **LFSR polynomial coefficients** — the missing primes could define tap positions for an LFSR
2. **Permutation order** — rearranging text using these primes as indices
3. **Starting points** for stream generation
4. **Key material** — the primes themselves (or their indices, or gaps between them) as encryption key

### Key Numbers
- Gap: 71 → 1229 (primes 20th → ~201st)
- Number of missing primes: ~200
- 71 = M (index 19), 73 = L (index 20) in Gematria
- The gap perfectly spans the "beyond alphabet" prime range

---

## 4. Fibonacci, Spirals, and Non-Linear Reading

### The Onion 7 Grid Discovery
**Source:** `Analysis/COMMUNITY_RESEARCH_REPORT.md`, `Analysis/Reference_Docs/people_2014.md`

A 4×4 number grid was found on the seventh onion site (page 15):

```
When you subtract each number from 3301, the results are ALL PRIMES.
Converting those primes to their ordinal positions gives the FIBONACCI SEQUENCE:
0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987
```

The Fibonacci sequence traces a **SPIRAL PATH** through the grid.

### Key Detail: Möbius Fold
The bottom-left quadrant uses **3301 + X** instead of **3301 - X**, suggesting a **Möbius fold** or sign inversion at the boundary. This implies:
- Non-linear reading order (spiral, not left-to-right)
- Possible bidirectional or self-inverting cipher structure

### Application to LP
- Pages may need to be read in **spiral order**, not linearly
- The Fibonacci sequence could index into text positions
- A "fold" could mean the second half of a page is processed differently (reversed, inverted, etc.)

### P19 Hint
Page 19 plaintext says: **"REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR..."**
- This directly tells us primes define a non-standard reading/processing order
- **Source:** `Analysis/p19_final_report.md`

---

## 5. The Deor Poem Connection

### What It Is
An Old English poem about exile & loss, 7 stanzas, each ending with the refrain:
> "Þæs ofereode, þisses swa mæg" ("That passed away, so may this")

Full text in `Analysis/Reference_Docs/deor_poem.txt`.

### How It's Used
1. **Page 19** hints at Deor ("REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR...")
2. **Page 20 partial solution:** Extract runes at **prime positions** → **Beaufort cipher with Deor** as key → **2×83 column transposition** yields Old English words.
   - Formula: `stream[i] = (Deor[prime_i] - P20[prime_i]) mod 29`
   - Words found: EODE ("went"), SEFA ("heart/mind"), THE LONE, MET, BID, AM, HER, SAY
   - IoC of result: 1.8952

### Deor as Key Material
- The poem can be encoded as Gematria indices for use as a running key
- Both the OLD ENGLISH text and the MODERN ENGLISH translation are candidates
- Strophe structure (7 sections) may correspond to page sections
- **All 951 offsets tested against P20 non-prime stream** → best IoC only 1.27 (failed)
- **Source:** `Analysis/P20_Investigation_Notes.md`, `Analysis/P20_Partial_Solution.md`

### Remaining Questions
- Does Deor apply only to page 20, or to the entire unsolved section?
- Is the key derived from specific CHARACTERS, WORDS, or STRUCTURAL elements of Deor?
- Does "rearranging the primes" mean Fibonacci-indexed positions in Deor?

---

## 6. Specific Key Values, Polynomials, LFSR Taps

### Page 63 Grid Keywords (as Gematria indices)
**Source:** `Master_Tracking/KEY_HINTS_FOR_UNSOLVED_PAGES.md`

| Keyword | Gematria Indices |
|---------|-----------------|
| VOID | [21, 3, 10, 23] |
| AETHEREAL | [24, 18, 2, 8, 18, 4, 18, 24, 20] |
| CARNAL | [5, 24, 4, 9, 24, 20] |
| SHADOWS | [15, 8, 24, 23, 3, 7, 15] |
| MOBIUS | [19, 3, 17, 10, 1, 15] |
| OBSCURA | [3, 17, 15, 5, 1, 4, 24] |
| CABAL | [5, 24, 17, 24, 20] |
| MOURNFUL | [19, 3, 1, 4, 9, 0, 1, 20] |
| ANALOG | [24, 9, 24, 20, 3, 6] |
| FORM | [0, 3, 4, 19] |
| BUFFERS | [17, 1, 0, 0, 18, 4, 15] |
| SUOID | [15, 1, 3, 10, 23] |
| DIVINITY | [23, 10, 21, 10, 9, 10, 16, 26] |
| FIRFUMFERENFE | [0, 10, 4, 0, 1, 19, 0, 18, 4, 18, 9, 0, 18] |
| YAHEOOPYJ | [26, 24, 8, 18, 3, 3, 13, 26, 11] |

### Page 63 Grid Numbers
```
272 138 SHADOWS 131 151
AETHEREAL BUFFERS VOID CARNAL 18
226 OBSCURA FORM 245 MOBIUS
18 ANALOG VOID MOURNFUL AETHEREAL
151 131 CABAL 138 272
```

**Critical:** Number "18" appears **TWICE** — direct reference to Page 18?

### Number Properties
- **Palindromic structure:** Row 1 [272, 138, 131, 151] mirrors Row 5 reversed [151, 131, 138, 272]
- **138272 ÷ 29 = 4768** (exact division!)
- **3301 is the 464th prime; 464 × 29 = 13456**
- Grid is IDENTICAL to the **2014 Magic Square** from the sixth onion server status page
  - Magic number = **1033** (palindrome of 3301)
  - **Source:** `Analysis/Reference_Docs/people_2014.md`

### Cookie Primes
- Palindromic prime pair: **167** and **761**
- Hash values:
  - 167 → `6941f707ff39d259...`
  - 761 → `7bc1e7805ccfa518...`
- **Source:** `Analysis/COMMUNITY_RESEARCH_REPORT.md`

### P.S. Number (131 digits, NEVER USED)
```
104127906589199853598278987395943189564044251069556756437392269523726824238529590817398343903703744757648634152034234993571087136311
```
- May be semiprime, RSA modulus, or key material
- **Source:** `Analysis/COMMUNITY_RESEARCH_REPORT.md`

### Trailing Whitespace Primes
Palindromic prime sequences were embedded in PGP messages as trailing whitespace:
- From the "message.txt.asc" delivered to registered onion services: `2, 3, 5, 7, 11, 13, 17, 23, 29, 31, 37` (OEIS A194954)
- **Source:** `Analysis/Reference_Docs/people_2014.md`

### Music File Duration
- "Interconnectedness" MP3: **277.133 seconds**
- Gematria sum = **772**
- **Source:** `Analysis/Reference_Docs/people_2014.md`

### Rasputin Portrait Numbers
```
Left column: 181, 7, 15, 16, 966, 456, 1071, 351, 626, 7, 204, 434
```
- Left column sums to **1033**
- Right column (implied) sums to **3301**
- **Source:** `Analysis/Reference_Docs/people_2014.md`

### YAHEOOPYJ (Page 17 → Page 18 link)
- Key from last solved page before unsolved section
- Gematria indices: [26, 24, 8, 18, 3, 3, 13, 26, 11]

---

## 7. LFSR over GF(29) — What It Means

### Definition
A **Linear Feedback Shift Register (LFSR)** operating in **Galois Field GF(29)** — arithmetic modulo 29.

### Why GF(29)?
- Gematria Primus has exactly **29 characters** → operations in GF(29) map perfectly to the alphabet
- GF(29) is a prime field, meaning every element (except 0) has a multiplicative inverse
- All 29 elements: {0, 1, 2, ..., 28}

### How LFSR-Based Vigenère Works
1. Define a **feedback polynomial** with coefficients in GF(29)
2. Initialize the register with a **seed** (key)
3. Clock the LFSR to produce a **pseudorandom keystream** of values 0-28
4. Apply Vigenère: `plaintext[i] = (ciphertext[i] - keystream[i]) % 29`

### Key Parameters Needed
- **Polynomial degree** (register length) — could be derived from prime key lengths (47, 53, etc.)
- **Tap positions** — could be the missing telnet primes
- **Seed/initial state** — could be from P63 grid numbers, cookie hashes, or solved-page keywords
- **Feedback coefficients** — the polynomial coefficients in GF(29)

### Evidence for LFSR
- Unsolved pages have near-uniform character frequency (IoC ≈ 0.0345, close to random 1/29 = 0.0345)
- Standard Vigenère with key length < message length would show higher IoC
- Research paper identified: **"Strong Key Mechanism Generated by LFSR based Vigenere Cipher"** (ResearchGate, October 2012)
- **Source:** `Analysis/COMMUNITY_RESEARCH_REPORT.md`

---

## 8. IRC, Onion Site, and External Clues

### IRC Logs (Profetul & Mortlach)
**Source:** `LiberPrimus/reference/research/PFb6eQiD - logs.txt`

Key finding: **Cyclical gap patterns in keys that produce low doubles:**
- Gap of 11 generates low doubles: `0, 11, 22, 4, 15, 26, ...`
- Pattern: `11, -18, 11, 11, -18, 11, X, ...` where `29 - 18 = 11`
- Any ±±... = X pattern works
- Hypothesis: text encoded using a **base cyclic gap pattern** `X1, X2, X3, X4...` where `Xi = K(i+1) - Ki`
- Mortlach tested gap values up to 30

### The 2014 Puzzle Chain (Onion Sites)
**Source:** `Analysis/Reference_Docs/people_2014.md`

1. **Book Ciphers:**
   - Self-Reliance by Emerson (paragraph:sentence:word:letter)
   - Gödel, Escher, Bach by Hofstadter

2. **Magic Squares from OpenPuff steganography:**
   Three magic squares hidden in "Interconnectedness.mp3" via OpenPuff:
   - Password: `33011033` (A only, disable B and C, mp3 > Maximum setting, OpenPuff v4.00)
   - **5×5 square** (sums to 1033): `272 138 341 131 151 / 366 199 130 320 18 / 226 245 91 245 226 / 18 320 130 199 366 / 151 131 341 138 272`
   - **7×7 square** (sums to 1033): `7 375 236 190 27 17 181 / 351 223 14 47 293 98 7 / ...`
   - **5×5 square** (identical to P63 grid): `272 138 341 131 151 / 366 199 130 320 18 / 226 245 91 245 226 / 18 320 130 199 366 / 151 131 341 138 272`

3. **Column Transposition:**
   - Plaintext: "GOOD WORK ULTIMATE TRUTH IS THE ULTIMATE ILLUSION"
   - Period: 14

4. **Seventh Onion (LP2 delivery):**
   - HTML title: `133` (note: 1+3+3 = 7?)
   - Div ID: `331` (3301 without the 0?)
   - Port: `5243`
   - Server: `thttpd/2.25b 29dec2003`
   - 58 page images (0.jpg through 57.jpg)
   - **User-Agent from Cicada:** `Cicada/33.01 CicaDOS 1.033 E Edition` and `Cicada/33.01 Cic/DOS/ 1.033 S Edition`

5. **PGP Message Whitespace Primes:**
   - `2, 3, 5, 7, 11, 13, 17, 23, 29, 31, 37` embedded as + characters

### Gematria Sum Clues
**Source:** `Master_Tracking/KEY_HINTS_FOR_UNSOLVED_PAGES.md`
- "ALL THINGS SHOULD BE ENCRYPTED" = **1237** (emirp — prime that's also prime reversed: 7321)
- "KNOW THIS" = **157** (also an emirp)

---

## 9. Page-by-Page Attack Vectors

### Page 18
- **Status:** UNSOLVED. Body confirmed Vigenère SUB, key length **53** (prime).
- **Links:** YAHEOOPYJ key from P17. Number "18" appears twice in P63 grid.
- **Tested & Failed:** Running key with Self-Reliance (all offsets).
- **Next try:** LFSR with degree 53, P63 keywords as seeds, Outguess data from page_17/18 images.
- **Source:** `Master_Tracking/MASTER_SOLVING_DOC.md`

### Page 19
- **Status:** SOLVED. Vigenère ADD, key length 47.
- **Plaintext hint:** "REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR..."
- **Source:** `Analysis/p19_final_report.md`

### Page 20
- **Status:** PARTIALLY SOLVED.
- **Dual-layer structure:** Runes separated by Gematria VALUE:
  - **Prime-valued runes** (237 runes, letters: TH, O, C, W, J, P, B, M, D) → IoC 3.2125 (restricted alphabet)
  - **Non-prime-valued runes** (575 runes, 20 letters) → IoC 1.4426
- **Prime-position extraction:** 166 runes at prime positions → Beaufort(Deor) + 2×83 transposition → Old English words
- **Non-prime stream with shift -2:** "THE" appears 6× at positions 49, 325, 415, 477, 549, 704
- **Word 17 = "THEY"** in plaintext (positions 96-98)
- **Critical blocker:** Non-prime stream cipher produces random-looking output (IoC ≈ 1.0)
- **ALL of the following FAILED:** Primes sequence key, Deor running key (all 951 offsets), Deor at prime indices, Deor strophes, Autokey w/ P19 hint, Affine w/ prime slopes.
- **Source:** `Analysis/P20_Comprehensive_Analysis.md`, `Analysis/P20_Investigation_Notes.md`, `Analysis/P20_Partial_Solution.md`

### Pages 21-30
- **Status:** High IoC (1.86-2.31) with P63 keywords but TEXT IS SCRAMBLED.
- **Keywords confirmed:** CABAL, DIVINITY, SHADOWS, VOID, OBSCURA, MOBIUS, etc. from P63 grid.
- **The cipher layer is correct** (keywords work) but a **transposition layer** remains unsolved.
- **Action:** Try spiral, Fibonacci-indexed, magic-square-path, and diagonal transpositions.
- **High-score pages:** P25 (1935.0, P:L53S156 ADD), P32 (1903.5, P:L59S222 SUB_REV)
- **Source:** `Master_Tracking/MASTER_STATUS.md`, `Master_Tracking/BREAKTHROUGH_ACTION_PLAN.md`

### Pages 31-54
- **Status:** Respond to Caesar shifts (IoC ≈ 1.0) but TEXT IS SCRAMBLED.
- **Different cipher type** than pages 21-30.
- **Expected pattern:** Another wisdom page (possibly hidden in pages 55-74) contains keywords.
- **Transposition attacks all failed:** Rail fence, columnar, diagonal, every-nth, zigzag.
- **Source:** `Master_Tracking/MASTER_STATUS.md`, `Master_Tracking/CICADA_BREAKTHROUGH_PATTERN.md`

---

## 10. Proven Cipher Methods from Solved Pages

### The Self-Referential Pattern
**Source:** `Master_Tracking/CICADA_BREAKTHROUGH_PATTERN.md`

**Wisdom pages contain literal keywords used as Vigenère keys for content pages:**
- Page 63 keywords → Pages 21-30 keys
- Page 19 Deor hint → Page 20 key
- **Pages 31-54:** Need to find their reference/wisdom page (possibly in pages 55-74)

### Solved Page Summary
**Source:** `LiberPrimus/LP1_INTUS_SOLUTIONS.md`

| Page | Method | Key |
|------|--------|-----|
| 55 | φ(prime) stream | Prime offset |
| 58 | Cleartext | — |
| 59 | CAESAR_28 SUB_REV | — |
| 60 | Cleartext | — |
| 61 | Vigenère | DIVINITY |
| 62 | Vigenère | CONSUMPTION (produces EOTATE — needs review) |
| 63 | Cleartext (CAESAR_0) | — |
| 64 | CAESAR_2 SUB_REV | — |
| 67 | Vigenère | CICADA |
| 68 | Cleartext (CAESAR_0) | — |
| 71 | Cleartext | — |
| 72 | Vigenère | FIRFUMFERENFE |
| 73 | φ(prime) stream + F-skip | Prime offset |
| 74 | Cleartext | — |

### F-Skip Mechanism
When rune = F (index 0, prime value 2), it passes through unencrypted AND the key counter is NOT incremented. This applies to φ(prime) cipher and may apply to unsolved pages.

### VALUE-Based Separation (Page 20)
Runes can be separated by whether their Gematria PRIME VALUE is itself prime-indexed:
- **Prime-valued letters (9):** TH(5), O(7), C(13), W(19), J(37), P(43), B(61), M(71), D(89)
- **Non-prime-valued letters (20):** All others
- This may be a general technique applicable to other pages.

---

## 11. Community Research Key Findings

### Single-Rune Word Attack
**Source:** `Analysis/COMMUNITY_RESEARCH_REPORT.md`

Every single-rune word in the plaintext must be either **I** (index 10) or **A** (index 24). This gives known plaintext-ciphertext pairs wherever single-rune words appear in the ciphertext. For each single-rune cipher word at position i:
```
key[i] = (cipher_rune - 10) % 29  OR  key[i] = (cipher_rune - 24) % 29
```
This produces 2 candidate key values per position — only 2^n combinations for n single-rune words.

### Pages 56-57 Are IDENTICAL When Decrypted
They may need to be combined with other pages or contain layered information.
**Source:** `LiberPrimus/ANALYSIS_REPORT.md`

### Frequency Analysis Proof
The unsolved pages do NOT use standard Vigenère/Caesar. The almost perfectly uniform rune distribution (ratio < 2:1) is characteristic of a **third cipher type** — likely LFSR-based stream cipher.
**Source:** `Analysis/COMMUNITY_RESEARCH_REPORT.md`

### SUOID — Unknown Keyword
Appears in P63 grid. Not a known English/Latin word. Possible anagram, codeword, or key identifier.
- As Gematria indices: [15, 1, 3, 10, 23]
- **Source:** `Master_Tracking/KEY_HINTS_FOR_UNSOLVED_PAGES.md`

---

## 12. Profetul/IRC Gap-Pattern Hypothesis

**Source:** `LiberPrimus/reference/research/PFb6eQiD - logs.txt`

Key insight from community researchers Profetul and Mortlach:
- There are **cyclical patterns in gaps between key elements** that produce low "doubles" (repeated bigrams)
- Gap of **11** is significant: sequence `0, 11, 22, 4, 15, 26, ...` (mod 29)
- Pattern form: `11, -18, 11, 11, -18, 11, X, ...` where **29 - 18 = 11**
- This suggests the cipher key is not random but follows a **structured gap pattern**
- The text may be encoded using a **base cyclic pattern** `X1, X2, X3, ...` where `Xi = K(i+1) - Ki`
- Tested gap values up to 30

### Connection to LFSR
An LFSR produces exactly this kind of structured sequence — the output has cyclical gap patterns determined by the polynomial taps. This IRC finding supports the LFSR hypothesis.

---

## 13. Raiden's Contest Hex Data

**Source:** `LiberPrimus/reference/research/Raiden's Contest.txt`

This file contains a massive block of hex data (252 lines) structured as hash-like 32-character hex blocks followed by longer concatenated hex data. Notable patterns:
- Contains what appears to be JPEG file data (hex headers `ffd8ff` pattern visible in later blocks)
- Address-like prefixes: `000034d:`, `000038e:`, etc. suggesting offset positions
- Some blocks contain anomalous sequences like `000dead:` (offset "DEAD" in hex)
- Contains embedded binary data with JFIF/JPEG markers

This may be:
- An alternative encoding of LP page images
- Additional steganographic content
- Contest material with embedded puzzles

### Mortlach's Gematria Values File
**Source:** `LiberPrimus/reference/research/Liber primus in gematria values by mortlach.txt`

The entire Liber Primus transcribed as Gematria prime values per word. This is a complete machine-readable representation useful for programmatic analysis. Format:
```
{rune_word1, rune_word2, ...}
{{prime_values_word1}, {prime_values_word2}, ...}
```

---

## Priority Attack Plan (Ordered by Likelihood)

### Tier 1 — Highest Probability
1. **Pages 21-30: Spiral/non-linear transposition** after P63 keyword Vigenère
   - Try magic square path (using the 5×5 grid as reading order)
   - Try Fibonacci-indexed positions
   - Try column widths that are prime factors of page length

2. **Page 18: LFSR with degree 53** using P63 grid numbers or YAHEOOPYJ as seed
   - Key length 53 is confirmed
   - Try LFSR polynomial with taps at missing telnet primes

3. **Page 20 non-prime stream: LFSR cipher**
   - Shift -2 produces THE 6× → cipher is close to solution
   - Try varying LFSR parameters around the -2 shift baseline

### Tier 2 — Medium Probability
4. **Outguess data extraction** from page images 17-54
   - Data exists but hasn't been analyzed
   - Could contain keys, hints, or supplementary ciphertext

5. **Single-rune word attack** on all unsolved pages
   - Every 1-rune word = I or A → known plaintext pairs
   - Can constrain key significantly

6. **Gap-pattern LFSR** per Profetul/Mortlach hypothesis
   - Try keys with gap pattern 11 (and -18 alternation) mod 29
   - Test all gap values 1-28

### Tier 3 — Speculative
7. **P.S. Number factorization** — may reveal key structure
8. **Cookie hash pairs** (167/761) as key material
9. **Rasputin numbers** as transposition key (sums to 1033/3301)
10. **OpenPuff re-examination** of other media files

---

## File Index

| Clue Category | Source File |
|---------------|------------|
| Gematria Primus | `LiberPrimus/GEMATRIA_PRIMUS.md` |
| Cipher formulas | `Master_Tracking/MASTER_SOLVING_DOC.md` |
| Page 63 grid & keywords | `Master_Tracking/KEY_HINTS_FOR_UNSOLVED_PAGES.md` |
| Self-referential pattern | `Master_Tracking/CICADA_BREAKTHROUGH_PATTERN.md` |
| Page status & IoC scores | `Master_Tracking/MASTER_STATUS.md` |
| Attack strategies | `Master_Tracking/BREAKTHROUGH_ACTION_PLAN.md` |
| Solved page keys | `LiberPrimus/LP1_INTUS_SOLUTIONS.md` |
| P19 solution & Deor hint | `Analysis/p19_final_report.md` |
| P20 dual-layer analysis | `Analysis/P20_Comprehensive_Analysis.md` |
| P20 failed hypotheses | `Analysis/P20_Investigation_Notes.md` |
| P20 prime-position solution | `Analysis/P20_Partial_Solution.md` |
| Community LFSR research | `Analysis/COMMUNITY_RESEARCH_REPORT.md` |
| 2014 puzzle chain | `Analysis/Reference_Docs/people_2014.md` |
| Outguess data locations | `Analysis/Reference_Docs/people_liber_primus.md` |
| Deor poem text | `Analysis/Reference_Docs/deor_poem.txt` |
| IRC gap-pattern hypothesis | `LiberPrimus/reference/research/PFb6eQiD - logs.txt` |
| Mortlach prime values | `LiberPrimus/reference/research/Liber primus in gematria values by mortlach.txt` |
| Magic squares & OpenPuff | `Analysis/Reference_Docs/people_2014.md` |
| Raiden's contest data | `LiberPrimus/reference/research/Raiden's Contest.txt` |
| Page 28 analysis | `LiberPrimus/reference/research/Page 28, Liber Primus.txt` |
