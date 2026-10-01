# Liber Primus — Master Tracker

**Start here** whether you're returning after a break or new to the repo. This page says where things stand
and what to do next. Every claim on it is backed by a test or a linked document. If something here
disagrees with the tests, the tests win, and this page needs fixing.

**Last updated:** 2026-10-01 · **Tests:** 80, all green · **Check it yourself:** `python -m unittest discover -s tests -t . -v`

---

## 1. Resume here

**Where we are (2026-10-01).** The repo was rebuilt on clean data. Before 2026-09-29 the page files did not
match their scans, so most older "discoveries" were artifacts (see §4.3). Now one canonical transcription
(`data/canonical/`) is read by one tested loader (`tools/lpcore`). Every solved section decrypts from it
exactly. The unsolved LP2 cipher has a key-independent fingerprint (§3.2). The repo was reorganised by trust level.
The doublet leak has been characterised: the 86 survivors are random at a constant ≈ 19 %, and the key-switch
scheme is refuted (§3.2 "The leak", findings §7). A drift-tolerant key detector now exists (`tools/lpcore/detect.py`,
exact forward algorithm, false-positive bound e^−30 per test). It found none of the riddle-derived keys, and
periodic keys are excluded (C9, findings §8). The key is not English text from any source, and the cipher is not
an autokey on its ciphertext (C10, C11, findings §9). No earlier cipher rune chooses the alphabet, for any secret
alphabets (C12, findings §10). The key's values are not decimal digits, hex digits or letters (C13, findings §11). The base-60 grid on scans
66–67 is a 184-byte stream, and it is not the key (findings §12). So the key stream is random-like numbers, which is why
title cribs were closed as untestable.

**Next actions, in order** (detail in [findings §6](reference/findings/lp2_logic_findings_2026-09-29.md)):

1. **Named key sources with wide alphabets.** C1–C13 leave a near-flat, aperiodic key whose values span at least
   ~30 symbols: bytes, digit pairs, base 60, or numbers mod 29. Only a named source can be tested, scored with
   `detect.log_lr`. Done: the scan 66–67 grid (§12). Still untested: two-digit groupings of Cicada numbers
   (the P.S. number, the 2013–2014 numbers), and OutGuess payloads re-run with drift (the ledger used fixed sync).
   Declare each before running.
3. **What are the grid's 184 bytes?** They are random-like (6.91 bits per byte). Testing whether they decrypt
   under LP-native ideas (the totient stream, DIVINITY-style keys, XOR with the hash on AN END) is cheap and new.
2. **Any new key source goes through `detect.log_lr`.** Add it to `tools/run_stage_i.py` style: declared first,
   every mode and shift recorded, pass at 30 nats.

**Before you start anything:** read §4 (ruled out) and §6 (rules of evidence). Plans go in [`TODO.md`](TODO.md).

---

## 2. Status by scan

Page folders are keyed by **scan number**: `pages/page_XX/` holds `images/XX.jpg` and the runes on that scan.

| Scans | Book | Content | Status |
|---|---|---|---|
| 00, 02 | LP1 | title pages | no runes |
| 01, 03–16 | LP1 | A WARNING · WELCOME/WISDOM · SOME WISDOM (square 1033) · A KOAN · AN INSTRUCTION · THE LOSS OF DIVINITY · A KOAN (the I) · AN INSTRUCTION (square 3301) | ✅ solved, test-verified |
| 17–66, 68–72 | LP2 p0–55 | 9 sections (§3.2), **12,956 runes** | 🔴 **unsolved** |
| 67 | LP2 p50 | base-60 grid only | no runes |
| 73 | LP2 p56 | AN END | ✅ solved, test-verified |
| 74 | LP2 p57 | PARABLE | ✅ solved, test-verified |

---

## 3. Established facts (test-backed)

### 3.1 How the solved sections decrypt

Source of truth: [`tools/lpcore/solved.py`](tools/lpcore/solved.py), asserted by `tests/test_lpcore.py`.
Indices are Gematria Primus positions 0–28 (ᚠ = 0).

| Seg | Title | Method |
|---|---|---|
| 0 | A WARNING | reversed gematria (atbash): p = 28 − c |
| 1 | WELCOME / WISDOM | Vigenère p = c − k, key **DIVINITY**, continuous through all 515 runes; plaintext F left unenciphered |
| 2 | SOME WISDOM (square, sum 1033) | plaintext |
| 3 | A KOAN / AN INSTRUCTION | atbash then +3: p = (28 − c + 3) mod 29 |
| 4 | THE LOSS OF DIVINITY | plaintext |
| 5 | A KOAN (the I) | Vigenère, key **FIRFUMFERENFE** (CIRCUMFERENCE with C→F), continuous with no resets at quotes; F unenciphered |
| 6 | AN INSTRUCTION (square, sum 3301) | plaintext |
| 16 | AN END | p = c − φ(pₙ) over primes 2, 3, 5, …; plaintext F unenciphered and consumes no prime |
| 17 | PARABLE | plaintext |

Errata, each with its evidence in `solved.py`: **WIDSOM** is the book's own typo and survives decryption.
**FOLLWING** is a typo in the upstream translation; the runes say FOLLOWING.

### 3.2 The unsolved cipher: fingerprint and constraints

| Seg | Scans | Runes | Doublets | Rate | Opening runes (title) |
|---|---|---|---|---|---|
| 7 | 17–19 | 729 | 4 | 0.55 % | ᛋᚻᛖᚩᚷᛗᛡᚠ ᛋᚣᛖᛝᚳ |
| 8 | 20–24 | 1,145 | 6 | 0.52 % | ᛚᛄ ᛇᚻᛝᚳᚦᛏᚫᛄᛏᛉᚻ ᛏᚢᛟ |
| 9 | 25–31 | 1,729 | 9 | 0.52 % | ᛉᛁᛉᛗ ᚢᛉᛗᚳᚦᛈᚩᛒ |
| 10 | 32 | 9 | 0 | — | ᚠᚢᛚᛗ ᚪᛠᚣᛟᚪ + the 4×4 square |
| 11 | 32–39 | 1,894 | 10 | 0.53 % | ᛚᚢᛝᚾ ᚳᚢ ᛒᚾᛏᚠᛝ |
| 12 | 40–43 | 1,021 | 11 | 1.08 % | ᚢᚪ ᚹᛝᚷᛉᛞᚷ ᛁᛒᛁ ᛇᛏᛒᛁᚣ |
| 13 | 44–50 | 1,524 | 13 | 0.85 % | ᛗᛈᚣ ᛚᛋᚩᚪᚫᚻᛚᛖᛇᛁᛗᛚ ᛚᛋᚳᛈ |
| 14 | 50–56 | 1,589 | 12 | 0.76 % | ᛝᚦᛇ ᛁᚠᚳᛟᛇ |
| 15 | 57–72 | 3,316 | 21 | 0.63 % | ᚠᚾᛗ ᚣᚷᛞᚫᚻ |
| **all** | | **12,956** | **86** | **0.66 %** vs 3.45 % expected (z = −17) | |

Everything else is flat: IoC, rune frequencies, and repeats at lags 2–10. The constraints derived from that
are C1–C7 in [findings §2](reference/findings/lp2_logic_findings_2026-09-29.md) (C8 is in §7, C9 in §8, C10–C11 in §9, C12 in §10, C13 in §11):

- The anti-doublet rule acts on the continuous rune stream and ignores word boundaries (C1).
- There is no plaintext-F passthrough, unlike LP1 (C2). The surviving doublets mark no single plaintext letter (C3).
- **No additive mod-29 cipher with a plaintext-independent key can produce the deficit**, whatever the key text (C4).
- Only lag 1 is affected (C5). One system runs throughout, with no seam between sections (C6). No one-shift-per-word scheme fits (C7).
- **The key is not English text (C10):** from any source, as letters, prime values or φ(prime values), in any mode
  and offset. The key's values must be near-flat mod 29. **No ciphertext autokey (C11)** at lags 2–1000.
- **No ciphertext-selected alphabet (C12):** c_i = σ_{c_{i−L}}(p_i) is excluded for any secret alphabets and
  any L ≤ 1000. This includes keyed autokeys c_i = p_i + f(c_{i−1}).
- **Key alphabet (C13):** not single decimal digits, hex digits, or letters (uniform or English in Latin spelling).
- **No periodic key (C9):** lags 11–1000 are normal. This excludes every period ≤ 1000 under a re-key rule that keeps
  the key in step, and every period ≤ 25 under a drifting one (findings §8).

**Reading:** a rule applied at the output of a non-periodic additive stream. It is not a property of the key
text, of word structure, or of any plaintext letter.

**The leak (findings §7, `tests/test_leak.py`).** The 86 survivors look like independent random events at one
constant rate, about 19 % of would-be doublets. That rate holds across lines and pages (L2), periods (L3), and
sections and windows (L4). The suppressed doublets are spread evenly over all other differences (L1).
**C8:** a rule that re-keys a would-be doublet keeps it exactly when the replacement key value equals the original.
So a re-keying rule needs agreement at ≈ 19 % of those positions (independent keys give 3.4 %). A check
applied by hand with ≈ 81 % reliability also fits. These data cannot tell the two apart.

### 3.3 The number squares are all decoded

- **LP2 scan 32 (4×4):** every cell is |3301 − p(F+1)| for Fibonacci F = 0…987, read as a spiral out from the centre.
  The bottom row is included: 1206 → p(611) = 4507, 4516 → p(988) = 7817. Test: `test_square_on_scan_32_is_fully_explained`.
- **LP1 scan 05:** magic sum 1033. Word cells are worth their gematria sums (SHADOWS = CABAL = 341). Test: `test_scan05_square_parses_into_a_magic_square`.
- **LP1 scan 16:** magic sum 3301, with 809 at the centre.

---

## 4. Ruled out — don't repeat these

### 4.1 By the 2026 community ledgers (details in [`community_research.md`](reference/community/community_research.md))

Leo-Y-Zhang/LiberPrimusAnalysis and Dukotah/cicada3301 exclude: periodic keys with or without an F-interrupter ·
46 integer sequences, raw and chained · autokey · prime-value feedback · ~200 public key texts · running keys
from Cicada texts · keys shared between sections · digraphic ciphers · common KDFs/PRNGs · Bitcoin, NIST Beacon,
RANDOM.ORG and RAND archives (~14.5 billion offsets). Both conclude "OTP-class" plus a soft anti-doublet rule.

### 4.2 By our own tests

- No plaintext-F passthrough (C2).
- No doublet↔plaintext-letter link; this refutes the chain-multiplicative family c = c₋₁ + (p − x)·k (C3).
- No additive cipher with a plaintext-independent key, including English running keys, primes and φ(prime) (C4).
- No per-word shift scheme (C7).
- The community **key-switch** scheme ([`Algorithm.png`](reference/community/images/Algorithm.png)) leaves 6–10 doublets
  per ~2,900 runes, which scales to λ ≈ 27–45 against the 86 observed (P ≤ 3 × 10⁻⁸). Its literal code gives 0.35 %,
  not the 0.69 % the picture claims (L5, findings §7).
- A per-line check, a "nudge" rule (c ± 1), and a periodic gap in checking are all excluded (L1–L3).
- **Riddle-derived keys (stage I, findings §8):** primes p(n) in every mode and constant shift (so also φ(p), p ± 1 and
  3301 − p), the solved text's word sums, and its rune values, each per section and continuous. That is 2,610
  drift-tolerant decodes, with the best on a real section at −65 nats against a pass mark of +30. The scan-32 square's
  numbers do not decode the segment 10 title (0 of 30).
- **Any English running key, plaintext autokey at any lag, ciphertext autokey at lags 2–1000** (C10, C11; findings §9).
  Section-title cribs are closed as untestable without a key model.
- **Ciphertext-selected alphabets** c_i = σ_{c_{i−L}}(p_i), any σ, L ≤ 1000 (C12, findings §10).
- **The scan 66–67 base-60 grid as a key** (bytes, 5-bit groups, base-60 digits; 3,132 decodes; findings §12).
- **Keys made of single decimal digits, hex digits or letters**, in any mode and offset (C13, findings §11). This
  covers π/e digits, the P.S. number, RAND digits, and hash hex read one symbol per rune.
- The "Echo446Ghq full solution" is debunked ([analysis](reference/community/echo446ghq_analysis.md)).

### 4.3 Invalid claims from before 2026-09-29

Section numbers refer to the [archived tracker](reference/archive/MASTER_TRACKER_pre-2026-09-29.md).
Its *negative* results on LP2 text may still hold, since the old page files did contain LP2 text, just under the
wrong scan numbers. But none of them was test-backed, and the community ledgers (§4.1) cover them more rigorously.

| Claim | Why it is invalid |
|---|---|
| §8.10 "two-time-pad" overlaps (3,718 positions) | Text was duplicated across the old page files. Canonical LP2 has no such repeats |
| "P27 == P44[0:234]" | Old `page_27` was the first page of the section that old `page_44` held whole |
| §8.2 "LP2 mirrors LP1" | LP1 text had been copied into old pages 57–74 |
| P07/P08 "unsolved polyalphabetic" | Scans 07/08 are the solved KOAN (atbash + 3) |
| P59 "reciprocal substitution"; P61–64, 67–68, 71–72 "solved" | LP1 text in the wrong slots. Those scans are unsolved LP2 |
| P65 "decoded 11×11 grid" | Scan 65 is an ordinary unsolved rune page |
| §8.3a 71/83 key-length alternation; `verified_keys.json` | Hill-climb output on misaligned data |
| §8.11 "SUB mode confirmed" by GPU SA; "7 perfect cribs" | A free key per position can fit any crib |
| P00 "key length 113 → Old English" | A 113-long key on 262 runes can produce anything |
| P02 "THE I IS I SAME AS THAT PILGRIM", key-43 anchors | The anchors were fitted, not found |
| P14 "key resets at each quote" | False: FIRFUMFERENFE runs continuously (tested) |
| "P21–30 high IoC with P63 keywords" | Retracted in Session 7, and built on the wrong pages |

---

## 5. Open questions

The ordered list is in §1. These questions are also open and cheap to state:

- Answered 2026-10-01 (findings §7): the survivors do not cluster in position (L3, L4). Segment 12's 1.08 % is noise
  (χ² across all sections p = 0.72).
- Section sizes 729 = 9³ and 1729 = 9³ + 10³; 1021 is prime; 3316 = 4 × 829. These are curiosities, not evidence.

---

## 6. Rules of evidence

1. Runes come only from `data/canonical/`, through `tools/lpcore`. Never from `pages/*/runes.txt` by hand, and never from the transcript.
2. **No optimisers.** No hill-climbing, SA, GA or GPU search (owner directive). Their output is not evidence.
3. A hypothesis test is **one deterministic decode with a threshold declared before the run**. Record it whether it passes or fails.
4. Key tests must handle skips. About 3 % desync (interrupters) defeats a naive decode.
5. A new fact enters §3 only with a test, and a new exclusion enters §4 only with a test or a cited ledger.

---

## 7. Session log (newest first)

| Date | What happened | Commits |
|---|---|---|
| 2026-10-01 | **Base-60 grid** (TODO M): scans 66–67 parse as 184 bytes. As a key (3 readings × 3 modes × 29 shifts × 12 alignments) nothing passes; the power check gives +45…+122 | `4d66364` + this commit |
| 2026-10-01 | **Key alphabets** (TODO L): C13, the key is not decimal digits (−214), hex (−19.5) or letters (−14.3; English Latin −122); bytes, digit pairs and base 60 are untestable this way | `0c59200` + this commit |
| 2026-10-01 | **Ciphertext-selected alphabets** (TODO K): C12, no lag 1–1000 transition table carries plaintext structure, for any secret alphabets | `55c78b1` + this commit |
| 2026-10-01 | **Key statistics** (TODO J): C10, no English running key from any text (LLR −255 to −333; still excluded at 25 % English-like); C11, no ciphertext autokey at lags 2–1000. Title cribs closed as untestable | `b1fa1bb` + this commit |
| 2026-10-01 | **Key-source riddles** (TODO I): drift-tolerant detector, C9 (no periodic key), 2,610 candidate decodes all fail, segment 10 title not decoded. AN END control failed by length (29.6 < 30), recorded | `8641c50` `3720710` |
| 2026-10-01 | **Doublet leak characterised** (TODO H): L1–L5 and C8, `tools/lpcore/leak.py`, 13 tests. Key-switch refuted; C6 promoted to a test | `d66cbb2` |
| 2026-10-01 | Repo organised by trust level. This tracker rewritten; the old one archived. Material from another project removed. `.gitattributes` added | `f5ca9a1` … this commit |
| 2026-09-29 | **Data-integrity correction.** Canonical corpus, `tools/lpcore` and 35 tests; 150 page files rebuilt; legacy tools and outputs archived; logic-only findings C1–C7; scan-32 square decoded | `f038274`, `50889e8`, `a85c106` |
| 2026-02 → 2026-05 | Sessions 1–21 on the misaligned page files, much of it hill-climbing. Archived: [old tracker](reference/archive/MASTER_TRACKER_pre-2026-09-29.md) | — |

Full plans, rollbacks and per-stage detail are in [`TODO.md`](TODO.md) and the git history.

---

## 8. Where things are

See the layout in [`README.md`](README.md). In short: `data/canonical/` is the truth · `tools/lpcore/` is the tested code ·
`tests/` is the proof · `reference/findings/` holds our results · `reference/community/` holds others' (unverified) ·
`tools/legacy/`, `data/archive/` and `reference/archive/` are history, not evidence.
