# LIBER PRIMUS — MASTER TRACKER
## Cicada 3301 (2014) — Comprehensive Solving Record

**Last Updated:** Feb 26, 2026  
**Purpose:** Single source of truth. ALL findings, methods tried, and status consolidated here.  
**Rule:** Check this document BEFORE starting any new attack to avoid repeating work.  
**Note:** Repository reorganized Feb 2026. Old directories (LiberPrimus/, Analysis/, Assets/, Tools/) replaced by pages/, data/, reference/, tools/. See §12 for current file index.

---

## TABLE OF CONTENTS

1. [Page Status Overview](#1-page-status-overview)
2. [Solved Pages & Plaintexts](#2-solved-pages--plaintexts)
3. [Partially Solved Pages](#3-partially-solved-pages)
4. [Unsolved Pages — Current State](#4-unsolved-pages--current-state)
5. [Gematria Primus Reference](#5-gematria-primus-reference)
6. [Proven Cipher Methods](#6-proven-cipher-methods)
7. [All Known Keys & Keywords](#7-all-known-keys--keywords)
8. [Structural Discoveries](#8-structural-discoveries)
9. [External Clues & Reference Data](#9-external-clues--reference-data)
10. [Failed Approaches (DO NOT REPEAT)](#10-failed-approaches-do-not-repeat)
11. [Active Hypotheses & Next Steps](#11-active-hypotheses--next-steps)
12. [File Index](#12-file-index)

---

## 1. PAGE STATUS OVERVIEW

| Category | Pages | Count | Notes |
|----------|-------|-------|-------|
| ✅ **SOLVED** | 01, 03–17, 55–58, 59–64, 67–68, 71–74 | 32 | Confirmed readable English/Old English plaintext |
| ⚠️ **PARTIAL** | 00, 02, 18, 19 | 4 | P00: Old English (needs translation); P02: key 43, fragments; P18/P19: key partially recovered |
| 🟡 **PARTIAL** | 20 | 1 | 166-rune prime-stream decoded (Old English); 646 non-prime runes scrambled |
| 🔴 **HIGH IoC, SCRAMBLED** | 21–30 | 10 | P63 keywords → IoC 1.86–2.31, but text unreadable |
| 🔴 **CAESAR, SCRAMBLED** | 31–54 | 24 | Caesar shifts identified, IoC ~1.0, text unreadable |
| 📄 **IMAGE/SPECIAL** | 65–66, 69–70 | 4 | No rune ciphertext; P65-66 may contain alphanumeric grid data |

> **⚠️ CRITICAL:** High IoC ≠ Solved. Pages 21-54 have correct letter frequency but text remains scrambled after all standard transposition methods.
> 
> **⚠️ NOTE:** Many page READMEs have WRONG status labels (e.g., P21-54 READMEs say "SOLVED" but are actually UNSOLVED — hill climbing produced runeglish gibberish, not English). Always trust THIS document over individual page READMEs.

---

## 2. SOLVED PAGES & PLAINTEXTS

### LP1 (Pages 00–17)

| Page | Method | Key | Plaintext |
|------|--------|-----|-----------|
| 00 | SUB mod 29, Key Length 113 | 113-element key (see below §3) | Old English (Runeglish) — NOT modern English. 262 runes. Known words: FLETH (dwelling/floor), HATHEN (heathen), THEON (thrive), DOETH (dœþ), GOETH (gœþ), EARTH (eaþþ). TH freq=28.2% (73×), THE trigram=47×. **Needs second-layer translation.** |
| 01 | Reversed Gematria | — | `A WARNING / BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE / TEST THE KNOWLEDGE / FIND YOUR TRUTH / EXPERIENCE YOUR DEATH / DO NOT EDIT OR CHANGE THIS BOOK OR THE MESSAGE CONTAINED WITHIN / EITHER THE WORDS OR THEIR NUMBERS / FOR ALL IS SACRED` |
| 02 | See Section 3 | Key Length 43 | **PARTIAL** — moved to Partially Solved |
| 03 | Vigenère SUB + F-skip | DIVINITY | `WELCOME / WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS / IT IS NOT AN EASY TRIP BUT FOR THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE / ALONG THE WAY YOU WILL FIND AN END TO ALL STRUGGLE AND SUFFERING YOUR INNOCENCE YOUR ILLUSIONS YOUR CERTAINTY AND YOUR REALITY / ULTIMATELY YOU WILL DISCOVER AN END TO SELF` |
| 04 | Vigenère SUB + F-skip | DIVINITY (cont.) | `IT IS THROUGH THIS PILGRIMAGE THAT WE SHAPE OURSELVES AND OUR REALITIES / JOURNEY DEEP WITHIN AND YOU WILL ARRIVE OUTSIDE / LIKE THE INSTAR IT IS ONLY THROUGH GOING WITHIN THAT WE MAY EMERGE / WISDOM / YOU ARE A BEING UNTO YOURSELF / YOU ARE A LAW UNTO YOURSELF / EACH INTELLIGENCE IS HOLY / FOR ALL THAT LIVES IS HOLY / AN INSTRUCTION COMMAND YOUR OWN SELF` |
| 05 | Cleartext (Direct Gematria) | — | `SOME WISDOM / THE PRIMES ARE SACRED / THE TOTIENT FUNCTION IS SACRED / ALL THINGS SHOULD BE ENCRYPTED / KNOW THIS / [5×5 Magic Square with keywords: SHADOWS, AETHEREAL, BUFFERS, VOID, CARNAL, OBSCURA, FORM, MOBIUS, ANALOG, MOURNFUL, CABAL + numbers 272,138,131,151,226,245,18]` |
| 06–08 | Shift 3 + Reversed Gematria | — | `A KOAN / A MAN DECIDED TO GO AND STUDY WITH A MASTER...` (full koan about identity — "Who are you who wishes to study here?") |
| 09 | Shift 3 + Reversed Gematria | — | `AN INSTRUCTION / DO FOUR UNREASONABLE THINGS EACH DAY` |
| 10–13 | Cleartext (Direct Gematria) | — | `THE LOSS OF DIVINITY / THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS WHICH CAUSE THE LOSS OF DIVINITY / CONSUMPTION...PRESERVATION...ADHERENCE... / SOME WISDOM AMASS GREAT WEALTH NEVER BECOME ATTACHED TO WHAT YOU OWN BE PREPARED TO DESTROY ALL THAT YOU OWN / AN INSTRUCTION PROGRAM YOUR MIND PROGRAM REALITY` |
| 14–15 | Vigenère + F-skip | FIRFUMFERENFE | `A KOAN / DURING A LESSON THE MASTER EXPLAINED THE I...` (koan about the voice in your head) |
| 16 | Cleartext (Direct Gematria) | — | `AN INSTRUCTION / QUESTION ALL THINGS / DISCOVER TRUTH INSIDE YOURSELF / FOLLOW YOUR TRUTH / IMPOSE NOTHING ON OTHERS / KNOW THIS / [5×5 Magic Square]` |
| 17 | Vigenère | YAHEOOPYJ | `EPILOGUE / WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO [SHA-512 hash] / IT IS THE DUTY OF EVERY PILGRIM TO SEEK OUT THIS PAGE` |

### LP2 (Pages 55–74)

| Page | Method | Key | Plaintext |
|------|--------|-----|-----------|
| 55 | φ(prime) stream + F-skip | Prime offset | `AN END / WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO [hash] / IT IS THE DUTY OF EUERY PILGRIM TO SEEK OUT THIS PAGE` (85 runes. Literal F at position 56 = word "OF". SEEC=SEEK, C subs for K.) |
| 56 | Prime shift | — | `PARABLE / LIKE THE INSTAR TUNNELING TO THE SURFACE / WE MUST SHED OUR OWN CIRCUMFERENCES / FIND THE DIVINITY WITHIN AND EMERGE` |
| 57 | Cleartext | — | Same as P56 (identical) |
| 58 | Cleartext | — | `LIBER PRIMUS` (11 chars — LP2 title page) |
| 59 | Reciprocal Substitution (Monoalphabetic) | Full cipher table (see P59 SOLUTION.md) | Same as P01 — `A WARNING / BELIEVE NOTHING FROM THIS BOOK...` NOTE: NOT simple Caesar — uses a specific letter-by-letter substitution table (R↔A, NG↔W, J↔B, I↔E, H↔L, E↔I, IA↔V, AE↔O, D↔K, OE↔G, C↔D, EO↔T, N↔M, P↔S, S↔P, X↔X, EA↔F, Y↔TH, TH↔Y) |
| 60 | Cleartext | — | `CHAPTER I INTUS` (LP2 chapter title) |
| 61 | Vigenère SUB + F-skip | DIVINITY (offset 0) | 394 runes. Composite of P03-04 content. Standard DIVINITY + F-skip. All 16 F positions in cipher: {5,14,47,48,74,84,132,144,152,159,160,165,219,250,317,331}. F-mask binary `0010011001111000`. 7 literal F at {48,74,84,132,159,160,250}. Exhaustive search over 524,288 combos (score 298). GP: ILLUSIIANS→ILLUSIONS, LICE→LIKE, GONG→GOING, THNGS→THINGS, SUFFERNG→SUFFERING. |
| 62 | Vigenère SUB + F-skip | DIVINITY (offset 3) | `WISDOM / YOU ARE A BEING UNTO YOURSELF / YOU ARE A LAW UNTO YOURSELF / EACH INTELLIGENCE IS HOLY / FOR ALL THAT LIVES IS HOLY / AN INSTRUCTION / COMMAND YOUR OWN SELF` (121 runes). All 9 F positions: {4,27,29,49,71,76,105,111,120}. F-mask binary `010110001`. 4 literal F at {27,49,71,120}. 12,288 combos tested (score 291). GP: WIDSOM→WISDOM, INSTRUCTIAN→INSTRUCTION, BENG→BEING. |
| 63 | Cleartext (Caesar 0) | — | Same as P05 — `SOME WISDOM / THE PRIMES ARE SACRED...` + Magic Square grid |
| 64 | Caesar 2, SUB_REV | — | Same as P06-08 — full koan about identity. Score 3303.9 (highest batch score). |
| 67 | Shift 3 + Reversed Gematria | — | Same as P09 — `AN INSTRUCTION / DO FOUR UNREASONABLE THINGS EACH DAY` (38 runes, identical to P09). Formula: `plain[i] = (28 - (cipher[i] - 3)) % 29`. **Also contains SHA-512 hash:** `36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a8425893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4` |
| 68 | Cleartext (Caesar 0) | — | Same as P10-13 — `THE LOSS OF DIVINITY...` (657 chars, largest cleartext page) |
| 71 | Cleartext | — | `SOME WISDOM AMASS GREAT WEALTH NEUER BECOME ATTACHED TO WHAT YOU OWN BE PREPARED TO DESTROY ALL THAT YOU OWN` (89 chars) |
| 72 | Vigenère | FIRFUMFERENFE | `A KOAN` (5 chars only — title/header) |
| 73 | φ(prime) stream + F-skip | Prime offset | Same as P55 — `AN END...` |
| 74 | Cleartext | — | `PARABLE / LIKE THE INSTAR...` + `AN INSTRUCTION / CWESTION ALL THNGS / DISCOUER TRUTH INSIDE YOURSELF / FOLLOW YOUR TRUTH / IMPOSE NOTHNG ON OTHERS / CNOW THIS` (instruction text appears TWICE consecutively in raw output, then ends with IMPOSE... section. P74 has MORE content than P56.) |

### Key Observation: LP2 mirrors LP1
Pages 58–74 substantially repeat pages 00–17 content using different (often simpler) ciphers.
| LP2 Page | Mirrors LP1 Page(s) | Method Change |
|----------|---------------------|---------------|
| 58 | 00 | Both are title pages |
| 59 | 01 | Reciprocal Substitution (vs Reversed Gematria) |
| 60 | 02 | Both are chapter titles ("CHAPTER I INTUS") |
| 61 | 03-04 | Same key DIVINITY, but multi-offset composite |
| 62 | 04 (end) | Same key DIVINITY offset 3 + F-skip |
| 63 | 05 | Both cleartext (magic square) |
| 64 | 06-08 | Caesar 2 SUB_REV (vs Shift 3 + RevGem) |
| 67 | 09 | Identical 38 runes, same cipher method |
| 68 | 10-13 | Both cleartext |
| 71 | 13 (end) | Both cleartext wisdom |
| 72 | 14-15 | Same key FIRFUMFERENFE, but only 5 chars |
| 73 | 55→17 | Both φ(prime) + F-skip |
| 74 | 56+16 | Cleartext parable + instruction (P74 has MORE content) |

---

## 3. PARTIALLY SOLVED PAGES

### Page 00 — SUB mod 29, Key Length 113
- **Status:** Decrypted to Old English (Runeglish), NOT modern English
- **Rune Count:** 262
- **Key Length:** 113 (30th prime) — IoC analysis ranked key length 92 HIGHEST (IoC 0.0764), then 83 (IoC 0.0563), then 113 (IoC 0.0472). The 113 key was selected based on other criteria.
- **Best PRIME key length IoC ranking:** 83 (0.0563), 113 (0.0472), 101 (0.0462), 97 (0.0447), 73 (0.0434), 79 (0.0422), 41 (0.0420), 89 (0.0412), 107 (0.0405), 17 (0.0391)
- **Alternative key length 59 result:** Score 469, key `[26, 20, 27, 14, 17, 28, 9, 10, 27, 24, 0, 5, 18, 15, 18, 7, 9, 4, 14, 20, 12, 20, 0, 18, 0, 6, 27, 4, 23, 21, 5, 10, 21, 6, 4, 21, 13, 19, 28, 20, 9, 24, 27, 19, 23, 15, 6, 4, 6, 25, 26, 17, 26, 0, 11, 11, 27, 17, 11]` — fragments like "THEOAD", "THEAMA", "THECA" but lower quality than key-113
- **Operation:** SUB mod 29 (100% reversible)
- **English Score:** 837
- **Output:** Old English with identifiable words: FLETH (dwelling/floor), HATHEN (heathen), THEON (thrive), DOETH (dœþ), GOETH (gœþ), EARTH (eaþþ), EAGOE (eage=eye?), ESTHES (is þes=is this?), HTHEO (heo=she? / hleo=shelter?)
- **Draft gloss:** "At that time is this... through... that she dwelling earth... heathen..."
- **TH Statistics:** 28.2% frequency (73×), 5× higher than normal English; THE trigram = 47×
- **Complete Key:** `[19, 6, 23, 16, 10, 22, 9, 27, 26, 11, 16, 3, 19, 0, 12, 7, 23, 17, 7, 1, 1, 5, 28, 7, 20, 21, 15, 1, 17, 20, 23, 8, 22, 9, 20, 16, 7, 8, 13, 22, 15, 10, 2, 11, 22, 22, 4, 9, 19, 24, 1, 8, 12, 18, 21, 11, 21, 22, 21, 12, 7, 6, 13, 1, 14, 12, 26, 11, 11, 5, 27, 21, 25, 8, 22, 15, 20, 4, 20, 4, 19, 26, 0, 19, 1, 6, 2, 3, 22, 26, 24, 1, 19, 22, 12, 0, 21, 18, 20, 5, 17, 4, 24, 10, 19, 14, 19, 7, 12, 12, 14, 16, 2]`
- **Next step:** Old English → Modern English translation; check if second cipher layer exists

### Page 02 — Vigenère, Key Length 43 (or 83)
- **Status:** Partial fragments recovered via crib dragging
- **Rune Count:** ~230
- **Confirmed Key Length:** 43 (14th prime) via crib dragging; IoC analysis also ranks **83** as top candidate (IoC 0.0723)
- **Key:** `[23, 9, 14, 21, 14, 18, 26, 25, 4, 19, 22, 4, 26, 9, 1, 18, 9, 15, 20, 1, 6, 21, 20, 25, 21, 11, 16, 22, 15, 16, 16, 0, 0, 2, 15, 4, 2, 0, 9, 22, 26, 22, 15]`
- **Fragments found:** `SAME AS THAT`, `THE OTHER`, `WITH A`, `THE SONG`
- **Raw output:** `EAI-T.TTH-EASAMEAS-THAT-LEATHIOCG-...`
- **Next step:** Continue crib dragging to refine remaining key positions

### Page 18 — Vigenère SUB, Key Length 53
- **Status:** Full 53-element key recovered (one-time pad — key length = message length)
- **Rune Count:** ~170 total, key length 53 (16th prime)
- **Confirmed Key Length:** 53 (prime)
- **Fragment:** `BEING OF ALL I WILL ASC THE OATH IS SWORN TO THE ONE WITHIN THE ABOVE THE WAY`
- **Full Key (53 indices):** `[11, 6, 1, 20, 25, 20, 9, 15, 24, 26, 25, 7, 19, 8, 10, 24, 18, 9, 0, 16, 9, 4, 14, 22, 13, 13, 3, 28, 5, 21, 24, 19, 5, 1, 27, 14, 6, 17, 24, 24, 22, 8, 23, 6, 22, 19, 2, 11, 3, 19, 25, 15, 24]`
- **Key as letters:** `JGULAELNSAYAEWMHIAENFTNRXOEPPOEACNGAMCUIAXGBAAOEHDGOEMTHJOMAESA`
- **GP notes:** "ASC" = "ASK" (K→C), "ABOFE" = "ABOVE" (V→F/U)
- **Connection:** P17 key YAHEOOPYJ links to P18 title (shifted by 7)

### Page 19 — Vigenère ADD, Key Length 47
- **Status:** Mostly solved
- **Confirmed Key Length:** 47 (prime)
- **P19 key indices (0-46):** `[24, 15, 2, 24, 4, 21, 11, 10, 20, 16, 9, 19, 26, 11, 7, 5, 11, 6, 27, 8, 22, 25, 21, 16, 25, 0, 27, 9, 21, 7, 27, 15, 21, 9, 3, 16, 5, 22, 18, 4, 5, 18, 23, 28, 28, 28, 28]`
- **Key decodes to:** starts "A STARING JILT N MY..." ends "...WISHING NOT COERCED"
- **Note:** Last 4 indices = `[28, 28, 28, 28]` (EA rune) — may indicate key padding or alignment artifact
- **Plaintext hint:** `REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR K`
- **Significance:** Points to Page 20's decryption method

### Page 20 — Dual-Layer Cipher (Partial)
- **Prime-position stream (166 runes):** Beaufort(Deor) + 2×83 transpose → Old English words
  - Words found: EODE ("went"), SEFA ("heart"), THE LONE, MET, BID, AM, HER, SAY
  - IoC: 1.8952
- **Non-prime stream (646 runes):** UNSOLVED
  - Caesar shift 16 → IoC 2.0135 (best result, still scrambled)
  - Vigenère SUB with 166-stream key → IoC 1.9992
  - All transposition methods failed
- **Value-based separation:** Rune VALUES (prime vs non-prime gematria values) separate two streams
  - Prime-valued letters: TH, O, C, W, J, P, B, M, D
  - Non-prime with shift -2: "THE" appears 6× at positions 49, 325, 415, 477, 549, 704

---

## 4. UNSOLVED PAGES — CURRENT STATE

### Pages 21–30: High IoC with Page 63 Keywords

Letters are correct, order is wrong. Keyword + mode confirmed:

| Page | Keyword | Mode | IoC |
|------|---------|------|-----|
| 21 | CABAL | Beaufort | 1.9728 |
| 22 | DIVINITY | Beaufort | 1.8671 |
| 23 | ENCRYPTION | ADD | 2.0044 |
| 24 | OBSCURA | Beaufort | 2.0622 |
| 25 | CABAL | Beaufort | 1.8920 |
| 26 | ENCRYPT | ADD | 1.9844 |
| 27 | SHADOWS | ADD | 2.1043 |
| 28 | DEOR | SUB | 2.0678 |
| 29 | TOTIENT | Beaufort | 2.1184 |
| 30 | MOURNFUL | ADD | 1.9756 |

**Remaining problem:** An additional transformation layer (transposition, word-level rearrangement, or multi-stage) is needed beyond keyword decryption.

### Pages 31–54: Caesar Shift Identified

Each page has a different optimal Caesar shift. After Caesar, IoC ≈ 1.0, text scrambled.

| Page | Caesar Shift | English Score |
|------|-------------|---------------|
| 32 | 11 | 285 (best) |
| 44 | 5 | 227 |
| 50 | 6 | 224 |
| 40 | 0 (cleartext?) | 163 |

**Remaining problem:** Different cipher type than pages 21–30. Standard keyword Vigenère does NOT work. May need a different "wisdom page" with keys for this block.

**Notable:** P27 ciphertext = P44 first 234 runes (duplicate/subset relationship).

### Pages 62, 65–67, 69–72
- **P65–66, P69–70:** Image-only / no standard rune ciphertext. P65 has a **decoded_grid.txt** (121 chars = 11²) containing runeglish output: `LFNTDSAESBBRAWIOEAEEAEAIONTHLNGNUSISJNGNGHOEWPMDIAENGIONBDTHOGTNJBOEFDIOIEHLTHIEONIBNXDWIORJRUJHXGICLAHRMJLCLNIODHOEYJBMUNGEOBEC`. Reportedly decoded via "Grid lookup on Pages 0-4 runic text" (unverified). P66/P69/P70 remain unanalyzed.

### Structural Markers in Pages 21–54
- **`& $` at end of pages:** 22, 26, 32, 39, 54 — likely mark section/chapter endings
- **`&` mid-text:** 33, 38, 39 — delineate sub-sections within a page
- **Numbered sections (`1-` through `5-`):** Span pages 36-38, crossing page boundaries
- **Short pages (potential special significance):** P49 (66 runes), P54 (73), P50 (92), P32 (121), P22 (131)
- **P27 ciphertext = P44 first 234 runes:** Confirmed duplicate/subset relationship

---

## 5. GEMATRIA PRIMUS REFERENCE

| Index | Latin | Rune | Prime Value |
|-------|-------|------|-------------|
| 0 | F | ᚠ | 2 |
| 1 | U/V | ᚢ | 3 |
| 2 | TH | ᚦ | 5 |
| 3 | O | ᚩ | 7 |
| 4 | R | ᚱ | 11 |
| 5 | C/K | ᚳ | 13 |
| 6 | G | ᚷ | 17 |
| 7 | W | ᚹ | 19 |
| 8 | H | ᚻ | 23 |
| 9 | N | ᚾ | 29 |
| 10 | I | ᛁ | 31 |
| 11 | J | ᛄ | 37 |
| 12 | EO | ᛇ | 41 |
| 13 | P | ᛈ | 43 |
| 14 | X | ᛉ | 47 |
| 15 | S | ᛋ | 53 |
| 16 | T | ᛏ | 59 |
| 17 | B | ᛒ | 61 |
| 18 | E | ᛖ | 67 |
| 19 | M | ᛗ | 71 |
| 20 | L | ᛚ | 73 |
| 21 | NG/ING | ᛝ | 79 |
| 22 | OE | ᛟ | 83 |
| 23 | D | ᛞ | 89 |
| 24 | A | ᚪ | 97 |
| 25 | AE | ᚫ | 101 |
| 26 | Y | ᚣ | 103 |
| 27 | IA/IO | ᛡ | 107 |
| 28 | EA | ᛠ | 109 |

**29-character alphabet.** All operations mod 29.  
**U/V merger:** Both map to ᚢ — so "EVERY" → "EUERY".

### Punctuation & Formatting Characters
| Symbol | Meaning |
|--------|---------|
| `-` | Word separator (space) |
| `.` | Sentence end (period) |
| `/` | Line break |
| `%` | Page separator |
| `&` | Section marker |
| `$` | Chapter marker |

**Important:** `-` and `.` are NOT encrypted in unsolved pages — word boundaries and sentence structure are preserved.

---

## 6. PROVEN CIPHER METHODS

### 6.1 Vigenère SUB (mod 29)
```
plaintext[i] = (ciphertext[i] - key[i % key_len]) % 29
```
- Key lengths are ALWAYS PRIME (43, 47, 53, 83...)
- Used on most LP1 pages

### 6.2 Vigenère ADD (mod 29)
```
plaintext[i] = (ciphertext[i] + key[i % key_len]) % 29
```
- Used on P23, P26, P27, P30 (Pages 21-30 block)

### 6.3 Beaufort Cipher
```
plaintext[i] = (key[i % key_len] - ciphertext[i]) % 29
```
- Used for P20 prime-position extraction, P21, P22, P24, P25, P29

### 6.4 φ(prime) Stream Cipher
```
plaintext[i] = (ciphertext[i] - (prime[i] - 1)) % 29
```
- Works on Pages 55, 73
- **Literal F Rule:** If rune = ᚠ AND expected plaintext = F, output F directly, do NOT increment key counter

### 6.5 Caesar Shift
```
SUB: plaintext[i] = (ciphertext[i] - shift) % 29
ADD: plaintext[i] = (ciphertext[i] + shift) % 29
SUB_REV: reverse rune order, then SUB
```
- P59: Reciprocal Substitution (monoalphabetic, NOT Caesar — see full table in P59/SOLUTION.md)
- P64: Caesar 2 SUB_REV

### 6.6 Reciprocal Substitution (Monoalphabetic)
Used on P59. Each rune maps to a fixed different rune. Key pairs:
```
R↔A, NG↔W, M↔N, J↔B, I↔E, H↔L, E↔I, IA↔V, AE↔O,
D↔K, OE↔G, C↔D, EO↔T, N↔M, P↔S, S↔P, X↔X, EA↔F, Y↔TH, TH↔Y
```
Some pairs are reciprocal (R→A but also A→R), making this a self-inverse cipher.

### 6.7 GP Digraph Absorption Rules (Critical for Scoring)
When decoding Runeglish → English, these digraph rules apply:
- **NG absorbs adjacent I**: GONG→GOING, BENG→BEING, SUFFERNG→SUFFERING
- **IA replaces ION**: INSTRUCTIAN→INSTRUCTION, ILLUSIIANS→ILLUSIONS
- **K→C substitution**: LICE→LIKE, BOOC→BOOK, CNOW→KNOW, SEEC→SEEK
- **U/V merger**: EUERY→EVERY, NEUER→NEVER, DISCOUER→DISCOVER
- **TH is single rune**: Always index 2 (ᚦ)

### 6.8 F-Skip Rule (Critical)
When plaintext is F (index 0), the cipher outputs literal ᚠ WITHOUT encryption, and the key counter does NOT advance. Applies to Vigenère and φ(prime) ciphers.

---

## 7. ALL KNOWN KEYS & KEYWORDS

### Verified Working Keys

| Key | Pages Used | Gematria Indices |
|-----|-----------|-----------------|
| DIVINITY | 03, 04, 61 | [23, 10, 1, 10, 9, 10, 16, 26] |
| FIRFUMFERENFE | 14, 15, 72 | [0, 10, 4, 0, 1, 19, 0, 18, 4, 18, 9, 0, 18] |
| YAHEOOPYJ | 17 | [26, 24, 8, 18, 3, 3, 13, 26, 11] |
| CICADA | — | [5, 10, 5, 24, 23, 24] |
| CONSUMPTION | — | — |
| CABAL | 21, 25 | [5, 24, 17, 24, 20] |
| DIVINITY | 22 | See above |
| ENCRYPTION | 23 | — |
| OBSCURA | 24 | [3, 17, 15, 5, 1, 4, 24] |
| ENCRYPT | 26 | — |
| SHADOWS | 27 | [15, 8, 24, 23, 3, 7, 15] |
| DEOR | 28 | — |
| TOTIENT | 29 | — |
| MOURNFUL | 30 | [19, 3, 1, 4, 9, 0, 1, 20] |

### Page 63 Grid Keywords (Complete)

| Keyword | Gematria Indices | Used As Key? |
|---------|-----------------|--------------|
| VOID | [1, 3, 10, 23] | Not yet |
| AETHEREAL | [24, 18, 2, 8, 18, 4, 18, 24, 20] | Not yet |
| CARNAL | [5, 24, 4, 9, 24, 20] | Not yet |
| ANALOG | [24, 9, 24, 20, 3, 6] | Not yet |
| BUFFERS | [17, 1, 0, 0, 18, 4, 15] | Not yet |
| MOBIUS | [19, 3, 17, 10, 1, 15] | Not yet |
| FORM | [0, 3, 4, 19] | Not yet |
| SUOID | [15, 1, 3, 10, 23] | Not yet — UNKNOWN WORD |

### Page 63 Grid Numbers
```
272   138   SHADOWS   131   151
AETHEREAL   BUFFERS   VOID   CARNAL   18
226   OBSCURA   FORM   245   MOBIUS
18   ANALOG   VOID   MOURNFUL   AETHEREAL
151   131   CABAL   138   272
```
Numeric form (using SHADOWS=341, VOID=130, etc.):
```
272  138  341  131  151    → Sum: 1033
366  199  130  320   18    → Sum: 1033
226  245   91  245  226    → Sum: 1033
 18  320  130  199  366    → Sum: 1033
151  131  341  138  272    → Sum: 1033
```
**Magic constant = 1033** (palindrome of 3301)

---

## 8. STRUCTURAL DISCOVERIES

### 8.1 Self-Referential Puzzle Design
- **Wisdom pages contain literal keywords** used as Vigenère keys for content pages
- P19 plaintext → hints at P20 solution (prime extraction + Deor)
- P63 keywords → unlock P21-30
- **Expected:** Another wisdom/reference page unlocks P31-54

### 8.2 LP2 Mirrors LP1
Pages 58–74 substantially repeat pages 00–17 content with different (simpler) ciphers.

### 8.3 Key Lengths Are Always Prime
Every confirmed Vigenère key length is prime: 8 (DIVINITY), 13 (FIRFUMFERENFE), 9 (YAHEOOPYJ), 53 (P18), 47 (P19).

### 8.3a Verified Key Length Pattern: 71/83 Alternation
`Tools/verified_keys.json` contains keys for pages 1–55. Key lengths follow a **strict period-4 pattern**:
- **Length 71** (20th prime): Pages 1, 5, 9, 13, 17, 21, 25, 29, 33, 37, 41, 45, 49, 53 — i.e. `(page_num - 1) % 4 == 0`
- **Length 83** (23rd prime): All other pages (2–4, 6–8, 10–12, 14–16, 18–20, 22–24, 26–28, 30–32, 34–36, 38–40, 42–44, 46–48, 50–52, 54–55)

**Note:** These keys cover UNSOLVED pages too (P21–54), so the keys for unsolved pages are hill-climbed best-guesses, NOT confirmed solutions. However, the regular alternation pattern is a strong structural clue.

**Previous §8.3a said** hill climbing converges on key length 83 for P19/P21/P28/P43 — this is partially incorrect. P21's README shows key length **71**, not 83. The pattern is that every 4th page uses 71, others use 83.

### 8.4 Single-Rune Word Constraint
Every single-rune word in plaintext must be I (index 10) or A (index 24). This constrains keystream values at those positions:
```
key[i] = (cipher_rune - 10) % 29  OR  key[i] = (cipher_rune - 24) % 29
```

### 8.5 Fibonacci Spiral Reading Order
From the seventh onion site 4×4 grid: subtracting each number from 3301 yields primes whose ordinal positions form the Fibonacci sequence. The Fibonacci sequence traces a spiral path through the grid. Pages may need spiral/non-linear reading order.

### 8.6 Gematria Value Sums from Solved Pages
- "ALL THINGS SHOULD BE ENCRYPTED" = 1237 (emirp — 7321 is also prime)
- "KNOW THIS" = 157 (emirp)
- P01 line sums are all prime: 757, 1009, 691, 353, 769, 911, 1051, 859, 677

### 8.7 P11-P12 Key Overlap (Running Key Evidence)
Both pages use Vigenère SUB with **key length 83** (23rd prime).
- P11 key positions [47:82] exactly match P12 key positions [48:83] (35 overlapping values)
- The offset of 1 suggests a **continuous running key** that advances by 1 position per page
- The shared tail is: `8, 11, 19, 11, 28, 26, 0, 16, 21, 24, 1, 10, 8, 24, 2, 6, 21, 6, 12, 12, 2, 25, 27, 0, 12, 18, 2, 8, 28, 0, 18, 27, 10, 3, 9`
- **Hypothesis:** A single master key stream is used across multiple pages, with each page selecting its 83-character window from the stream

### 8.8 Structural Markers in Pages 21–54
- **Separator `& $`** at end of pages: 22, 26, 32, 39, 54 — marks section/chapter endings
- **Separator `&`** mid-text in pages: 33, 38, 39 — sub-section delineation
- **Numbered sections** (`1-` through `5-`) span pages 36-38 continuously across page boundaries
- **Short pages** may be special: P49 (66), P54 (73), P50 (92), P32 (121), P22 (131) runes

### 8.9 Page Analysis Cross-References

#### P43 + P00 → IoC 2.0632 (HIGHEST UNSOLVED IoC)
- Using Page 0 runes as Vigenère key (addition mod 29) produces IoC = 2.0632
- This is HIGHER than English IoC (~1.73) — extremely anomalous
- P43 is very short — high IoC may be amplified by short length
- **Needs word-level analysis of the output**

#### 1331 Triangle (P00, P48, P54)
- Pages 0, 48, and 54 all have **distance sum = 1331 from the Parable (P57)**
- 1331 = 11³ (eleven cubed — significant in Cicada numerology)
- Keys derived from (P00 − Parable) and (P48 − Parable) are NOT identical
- Page number differences: 48-0=48, 54-0=54, 54-48=6, 57-48=9 → **3, 6, 9 pattern**
- Suggests these three pages share an encryption framework with Parable as common component

#### 95-Element Master Key
A 95-element key has been tested across pages 27-52. Best results:
```
[11, 24, 17, 28, 10, 11, 25, 19, 9, 22, 5, 11, 3, 20, 27, 9, 3, 21, 20, 5,
 20, 22, 18, 18, 24, 16, 23, 2, 23, 24, 10, 5, 28, 19, 15, 19, 0, 25, 27,
 17, 2, 14, 10, 15, 8, 22, 8, 8, 27, 14, 2, 2, 19, 0, 18, 14, 28, 2, 11, 14,
 5, 3, 19, 8, 16, 11, 9, 5, 1, 21, 9, 9, 9, 5, 0, 19, 25, 28, 7, 14, 14, 7,
 14, 3, 26, 18, 24, 23, 19, 8, 4, 9, 16, 7, 23]
```
- Each page requires a **different offset** into this key
- Best offsets per page do NOT follow a simple formula `f(page_number)`
- **P30:** Cols=8, XOR offset=66 → Score 303 (highest for any unsolved page)
- **P28:** Partial key (24 chars) → Score 234 (closest to solved among unsolved pages)
- **P52:** Offset 72 finds THE, AND, ARE at positions 3, 32, 39 (263 runes, prime length)
- **P27:** Double-layer (Master Key + Parable shift 25) → Score 51; 25 = page 27 − 2 (hypothesis: `parable_shift = page_num − 2`, but didn't generalize)

#### Global IoC Finding
Pages 17–55 have IoC ≈ 0.034 — **indistinguishable from random** (expected 0.0345 for uniform). This rules out simple Vigenère with short keys and strongly suggests:
- Non-repeating key cipher (OTP, running key, or autokey)
- OR multi-layer encryption
- OR LFSR-based stream cipher

---

## 9. EXTERNAL CLUES & REFERENCE DATA

### 9.1 Outguess Steganography
PGP-signed hex data extracted from LP page images. Files in repo: outguess_00.txt, outguess_08.txt, outguess_17.txt, outguess_21.txt, outguess_43.txt. Community source: `rtkd/iddqd` GitHub repo (folder `lp_outguessed/`, files `00.txt`–`74.txt`).

- **P00:** Large PGP-signed hex block (68 lines of 60-char hex, signed with GnuPG v1.4.11)
- **P03 message:** "Let the text guide you. Good luck. 3301" + embedded JPEG data
- **P08:** Bigram grid hint — "For those who have fallen behind:" followed by:
  ```
  TL BE IE OV UT HT RE ID TS EO ST PO SO YR
  SL BT II IY T4 DG UQ IM NU 44 2I 15 33 9M
  ```
  Second row includes numbers (T4, 44, 2I, 15, 33, 9M). Signed "Good luck. 3301". **NEVER DECODED.**
- **P10–13:** PGP-signed instructions to create Tor hidden services and post magic squares
- **P17, P21, P43:** 58,152 bytes each of encrypted binary (shared 1,417-byte GPG header, NOT valid OpenPGP packets). Likely GPG-encrypted with Cicada's private key. **NEVER DECRYPTED.**
- **P65, P68–71:** Show "garbage" on extraction — may be encrypted key material
- Full outguess data for ALL pages available at `github.com/rtkd/iddqd/lp_outguessed/`

### 9.2 Telnet Gap: Primes 71→1229
Cicada's telnet server skipped ~200 primes (73 through 1223, primes 21st–~200th). Gap starts exactly at the boundary of the 29-rune alphabet (index 20=L=73). Could define LFSR taps, permutation order, or key material.

### 9.3 Self-Reliance (Emerson)
Referenced in solved pages ("shed our circumferences"). Full text in `self_reliance.txt`. Tested as running key — **FAILED** on P18 body.

### 9.4 Deor Poem (Old English)
7 stanzas, refrain: "Þæs ofereode, þisses swa mæg." Used as Beaufort key for P20 prime extraction. Full text in `Analysis/Reference_Docs/deor_poem.txt`.

### 9.5 P.S. Number (131 digits, NEVER USED)
```
104127906589199853598278987395943189564044251069556756437392269523726824238529590817398343903703744757648634152034234993571087136311
```

### 9.6 Cookie Primes
Palindromic pair: 167 and 761.
- `167=6941f707ff39d259ff71657a79cb6b54c184d2f0455810109c1a960860bde0e6`
- `761=7bc1e7805ccfa518920f0d94fc4e8f7dbd83287a03b337b89109cd2287befae5`

### 9.7 OpenPuff / Interconnectedness MP3
Magic squares hidden in "Interconnectedness.mp3" via OpenPuff (password: 33011033, A only, disable B and C, mp3 > Maximum, OpenPuff v4.00). Yields:
- **5×5 square** (identical to P63 grid, sums to 1033)
- **7×7 square** (also sums to 1033): `7 375 236 190 27 17 181 / 351 223 14 47 293 98 7 / ...`
- MP3 duration: **277.133 seconds**, Gematria sum = 772

### 9.8 IRC Gap-Pattern Hypothesis (Profetul/Mortlach)
Cyclical gap patterns in key elements: gap of 11 generates low doubles (`0, 11, 22, 4, 15, 26...`). Pattern: `11, -18, 11, 11, -18...` where 29-18=11. Supports LFSR hypothesis.

### 9.9 LFSR over GF(29)
The nearly uniform rune distribution in unsolved pages (ratio < 2:1) suggests LFSR-based stream cipher, not standard Vigenère. Parameters needed: polynomial degree, tap positions, seed, feedback coefficients.
- Reference paper: "Strong Key Mechanism Generated by LFSR based Vigenere Cipher" (ResearchGate, October 2012)
- An LFSR in GF(29) uses 29-valued register elements with feedback polynomial mod 29
- Every non-zero element has a multiplicative inverse in GF(29)

### 9.10 Trailing Whitespace Prime Sequences
Cicada embedded prime sequences in PGP message trailing whitespace:
- **vjuNp.jpg (2012):** `0, 2, 3, 5, 7, 11, 13, (1,1,2), 11, 0, 7, 0, 5, 0, 3, 2` — palindromic
- **message.txt.asc (2014):** `2, 3, 5, 7, 11, 13, 17, 23, 29, 31, 37` — first 11 primes (OEIS A194954)
- **Planned Parenthood (2015):** `5, 3, 2, 5, 7`

### 9.11 2014 Puzzle Chain (Onion Sites)
- **Book Ciphers used:** Self-Reliance by Emerson (paragraph:sentence:word:letter), Gödel Escher Bach by Hofstadter
- **Column Transposition plaintext:** "GOOD WORK ULTIMATE TRUTH IS THE ULTIMATE ILLUSION" (period 14)
- **Seventh Onion (LP2 delivery):** HTML title `133`, Div ID `331`, Port `5243`, Server `thttpd/2.25b 29dec2003`
- **User-Agents:** `Cicada/33.01 CicaDOS 1.033 E Edition` and `Cicada/33.01 Cic/DOS/ 1.033 S Edition`

### 9.12 Rasputin Portrait Numbers
```
Left column: 181, 7, 15, 16, 966, 456, 1071, 351, 626, 7, 204, 434 → Sum: 1033
Right column (implied) → Sum: 3301
```

### 9.13 Page 16 Magic Square (Distinct from P63)
```
434   1311   312   278   966
204    812   934   280  1071
626    620   809   620   626
1071   280   934   812   204
966    278   312  1311   434
```
This is a DIFFERENT grid from P05/P63. Both grids have palindromic structure.

### 9.14 Raiden's Contest Hex Data
File `LiberPrimus/reference/research/Raiden's Contest.txt` contains a massive hex block (252 lines) with embedded JPEG data (ffd8ff markers). May contain steganographic content or alternative LP page encodings. Includes anomalous offset `000dead:` (hex DEAD).

### 9.15 Mortlach's Gematria Values
File `LiberPrimus/reference/research/Liber primus in gematria values by mortlach.txt` has the entire LP transcribed as Gematria prime values per word — machine-readable format for programmatic analysis.

### 9.16 3301.txt (Guitar Fret Tones)
File `LiberPrimus/reference/research/3301.txt` contains:
```
0421812877725
May you find this
Here's a hint
http://www.youtube.com/watch?v=4xys0D9LNC8&feature=youtu.be&t=50s
The following tones are:
1st string 3rd fret / 1st string 1st fret / 2nd string 3rd fret /
2nd string 1st fret / 2nd string(0) / 2nd string 1st fret
Good luck -Jens
```
Number `0421812877725` and guitar tones (G, F, Bb, Ab, Gb, Ab on standard tuning) are unanalyzed. Likely from 2012/2013 puzzle chain, not directly LP.

### 9.17 IRC Research Details (Profetul/Mortlach)
Gist: `https://gist.github.com/Profetul/bd8ad9cb16c81302382526ea2e4f6e67`
Key insight: "blocks of the same size as a section" — testing gap values up to 30 for cyclical key patterns.

### 9.18 Parable → FIRFUMFERENFE Connection
Page 57 Parable contains "CIRCUMFERENCE" — this word also appears in Onion 6 pages (107, 167). The Vigenère key FIRFUMFERENFE is a runic spelling of CIRCUMFERENCE (C→F phonetic substitution). Confirms Parable functioned as a hint for the key.

---

## 10. FAILED APPROACHES (DO NOT REPEAT)

### Pages 21–30 (After Keyword Decryption)
| Method | Result |
|--------|--------|
| ❌ Rail fence (zigzag) — 2,3,4,5,7,11 rails | Scrambled |
| ❌ Columnar transposition — widths 11,13,17,19,23,29,31,37,41,43,47,53 | Scrambled |
| ❌ Diagonal reading (multiple widths) | Scrambled |
| ❌ Boustrophedon (reverse every other row) | Scrambled |
| ❌ Every-Nth character extraction | Scrambled |
| ❌ Multi-pass Vigenère (double encryption with all keywords) | No improvement |

### Pages 31–54
| Method | Result |
|--------|--------|
| ❌ All Page 63 keywords as Vigenère keys | No high IoC matches |
| ❌ Columnar transposition (forward + reverse) | Scrambled |
| ❌ Diagonal transposition (multiple widths) | Scrambled |
| ❌ Every-Nth character extraction | Scrambled |
| ❌ Caesar + transposition combined | Scrambled |

### Page 18
| Method | Result |
|--------|--------|
| ❌ Running key with Self-Reliance (all offsets) | No solve |
| ❌ LFSR with degree 53 | No solve |
| ❌ P63 keywords as keys | No solve |
| ❌ Autokey with P17 plaintext | No solve |
| ❌ Simulated annealing (SA) | Partial — 34/53 key positions found |
| ❌ Hill cipher 2×2, 3×3 exhaustive | Best IoC ~1.12 |

### Page 20 Non-Prime Stream (646 runes)
| Method | Result |
|--------|--------|
| ❌ Primes sequence as key | No readable text |
| ❌ Deor running key (all 951 offsets) | Best IoC 1.27 |
| ❌ Deor at prime indices | No solve |
| ❌ Deor strophes | No solve |
| ❌ Autokey with P19 hint text | No solve |
| ❌ Affine with prime slopes | No solve |
| ❌ All transposition methods (zigzag, diagonal, columnar) | Scrambled |

### General (All Unsolved Pages 18-54)
| Method | Result |
|--------|--------|
| ❌ Alberti progressive cipher | 0 hits |
| ❌ Bifid/Trifid fractionation | 0 hits |
| ❌ Math constants (π, e, √2, φ) as keystreams | No results |
| ❌ Concatenated pages as single stream | No results |
| ❌ Variable skip-value totient | 0 hits |
| ❌ Multiplicative / Gromark ciphers | No breakthrough |
| ❌ Hill cipher (2×2, 3×3 matrix) | Best IoC ~1.12 |
| ❌ Global stream (inter-page) cipher | No results |
| ❌ XOR-based ciphers (all keywords, affine, random) | Best ~1600 (P32, gibberish) |
| ❌ Porta cipher + CICADA/DESTINY keys | High scores but gibberish (P25=4970, P32=5666, P44=4519) |
| ❌ GPU batch attack (2900 keys × all modes) | No readable English on any unsolved page |
| ❌ Affine ciphers (a=3..28, b=0..28) | Best ~926 (P18), all gibberish |

### Page 00 (After Key Length 113 Decryption)
| Method | Result |
|--------|--------|
| ❌ Vigenère with 15+ known keys (DIVINITY, TRUTH, etc.) | All gibberish |
| ❌ Caesar shifts (all 29) | No improvement |
| ❌ Atbash + all shift variants (0-28) | Best score 303 (Atbash+Shift 9), then Atbash alone 246 |
| ❌ Caesar(5): 226, Caesar(6): 226, Caesar(7): 216 | No solve |
| ❌ Vigenere(DIVINITY): 208, Vigenere(TRUTH): 188, Vigenere(DEATH): 181 | No solve |
| ❌ Vigenere(CICADA): 142, Vigenere(PARABLE): 139, Vigenere(SELF): 132 | No solve |
| ❌ Vigenere(INSTAR): 110, Vigenere(WELCOME): 92, Vigenere(LIBER): 88 | No solve |
| ❌ Prime+1 shift: 142, Prime+56 shift: 87 | No solve |
| ❌ Community-proven methods (60+ combinations scored) | Best = Atbash+Shift(9) at 303 |
| ℹ️ IoC = 0.0343 (random-like) | Suggests non-repeating key or OTP |

### Pages 27-52 (95-Element Master Key)
| Method | Result |
|--------|--------|
| ❌ Master Key at all 95 offsets per page | Best: P30 offset 66 (score 303) |
| ❌ Columnar transposition + XOR (all combos) | Fragments only |
| ❌ Double-layer (Master Key + Parable key) | P27 best shift 25 (score 51) |
| ❌ Offset formula: `(page × k) mod 95` | No universal formula found |
| ❌ P28 full Master Key (score 195) | Partial matches only |
| ❌ P28 partial key 24 chars (score 234) | Better but not solved |

---

## 11. ACTIVE HYPOTHESES & NEXT STEPS

### Priority 1: Word-Level Anagram (Pages 21–30) ⭐⭐⭐⭐⭐
Letters are correct but order is wrong. P19 says "REARRANGING" explicitly.
- Extract words using rune hyphens as boundaries
- Reconstruct sentences using word frequency / n-gram statistics
- Try magic square path as reading/rearranging order

### Priority 2: P43 + P00 Key Relationship ⭐⭐⭐⭐⭐
P00 runes as Vigenère ADD key → IoC 2.0632 (highest signal in any unsolved page).
- Perform word-level analysis of the decrypted output
- Try reverse: P43 as key for P00's second layer
- Test P00 as key for other short unsolved pages

### Priority 3: 1331 Triangle (P00, P48, P54) ⭐⭐⭐⭐
All three pages have distance sum 1331 (= 11³) from Parable (P57).
- Investigate shared encryption framework
- Use Parable as second-layer key with page-specific offsets
- Explore the 3-6-9 pattern in page number differences

### Priority 4: Running Key Chain (P11-P12 evidence) ⭐⭐⭐⭐
P11[47:82] = P12[48:83] — 35-element overlap with 1-position shift.
- **Blocker:** Requires understanding the master key stream source
- Test if P10 and P13 keys follow the same pattern
- If continuous key: could predict key for unsolved pages

### Priority 5: Find Wisdom Page for Pages 31–54 ⭐⭐⭐⭐
The self-referential pattern (P63→P21-30) predicts another reference page for this block.
- Scan P55-74 for pages with grid structures, keyword lists, or unusual patterns
- Check if any solved page content contains hidden keys for P31-54
- P74's instruction section is LONGER than P56 — may contain additional clues

### Priority 6: 95-Element Master Key + Offset ⭐⭐⭐
Each page needs a different offset. Best results: P30 (score 303), P28 (score 234).
- Derive offsets from page properties (rune count, prime index, structural position)
- Focus on P28 (closest to solved) to crack the offset formula
- Test if offsets follow Fibonacci, prime, or GP-index sequence

### Priority 7: Outguess Data Analysis ⭐⭐⭐
P17, P21, P43 contain PGP-signed hex data never fully analyzed.
- Extract and analyze for keys, hints, or additional ciphertext
- P67 SHA-512 hash may point to a deep web page with additional information

### Priority 8: LFSR Stream Cipher ⭐⭐⭐
Near-uniform frequency in P31-54 suggests LFSR, not standard Vigenère.
- Try LFSR with polynomial degree from key lengths (47, 53)
- Use telnet gap primes as tap positions
- Use P63 grid numbers or keywords as seed

### Priority 9: Page 00 Second Layer ⭐⭐
Old English output confirmed (FLETH, HATHEN, THEON). Needs:
- Full Old English → Modern English translation
- Check if a second cipher transforms OE to ME
- Compare structure to Deor poem or other OE texts

---

## 12. FILE INDEX

> Paths below reflect the **reorganized** repo layout (Feb 2026).

### Root
| File | Purpose |
|------|---------|
| MASTER_TRACKER.md | **THIS FILE** — single source of truth |
| README.md | Project overview & repo structure |

### pages/
| Path | Purpose |
|------|---------|
| pages/page_XX/runes.txt | Per-page rune ciphertext (**essential**) |
| pages/page_XX/images/*.jpg | Original LP page scans & enhanced images (**essential**) |
| pages/page_XX/README.md | Per-page status (**WARNING: P21-54 labels are WRONG — trust THIS tracker**) |

### data/
| File | Purpose |
|------|---------|
| data/gematria_primus.md | 29-char runic alphabet, GP values, Python dicts, Unicode codepoints |
| data/verified_keys.json | **71/83 alternating key arrays for pages 1–55** (see §8.3a) |
| data/runes_full.txt | Concatenated runes, all pages (43 KB) |
| data/emerson_essays.txt | Emerson essays — running key source (564 KB) |
| data/self_reliance.txt | Self-Reliance essay (57 KB) |
| data/deor_poem.txt | Old English Deor poem (key for P19/P20) |
| data/wordlist.txt | 370K English words for scoring (4 MB) |
| data/key_search_corpus.txt | Community transcription with outguess data (137 KB) |
| data/folly_hint.txt, folly_rev_hint.txt, wisdom_hint.txt | Binary-encoded hints (from Cicada ISO /tmp) |
| data/outguess/ | 5 outguess-extracted messages (P00 PGP hex, P08 bigram grid, P17/P21/P43 binary payloads) |
| data/runeglish/ | 68 rune→Latin transliterations per page |

### reference/
| File | Purpose |
|------|---------|
| reference/community_research.md | Wiki/Reddit/GitHub findings summary |
| reference/liber_primus_transcript.md | Full LP community transcript (135 KB) |
| reference/people_2014.md | Known 2014 puzzle participants |
| reference/LiberPrimus.pdf | Original LP scan (55 MB) |
| reference/cicada_pgp_key.asc | 3301 PGP public key |
| reference/cicada_puzzle_paper.pdf | Academic paper on the puzzle (1.5 MB) |
| reference/solved_pages.docx | Community compiled solutions |
| reference/RuneSolver.py | Community rune solver tool (90 KB) |
| reference/mortlach_gematria.txt | Gematria values by Mortlach |
| reference/irc_logs.txt | IRC solver channel logs |
| reference/raidens_contest.txt | Raiden's Contest hex data |
| reference/liber_al_vel_legis.txt | Liber AL vel Legis text |
| reference/3301_guitar_tones.txt | Guitar fret → tone mapping from 3301.txt |

### tools/
| File | Purpose |
|------|---------|
| tools/batch_solver.py | General batch solving framework |
| tools/translate_runes.py | Rune translation utility |
| tools/generate_runeglish.py | Runeglish generation utility |
| tools/populate_runes.py | Rune file population utility |
| tools/solve_p61_p62.py | Canonical P61/P62 F-skip solver — confirmed solution |

---

*"BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE" — Page 01*
