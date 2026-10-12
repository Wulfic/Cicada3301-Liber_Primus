# Liber Primus — Master Tracker

**Start here** whether you're returning after a break or new to the repo. This page says where things stand
and what to do next. Every claim on it is backed by a test or a linked document. If something here
disagrees with the tests, the tests win, and this page needs fixing.

**Last updated:** 2026-10-12 · **Tests:** 266, all green · **Check it yourself:** `python -m unittest discover -s tests -t . -v`

---

## 1. Resume here

**Where we are (2026-10-12).** The repo was rebuilt on clean data. Before 2026-09-29 the page files did not
match their scans, so most older "discoveries" were artifacts (see §4.3). Now one canonical transcription
(`data/canonical/`) is read by one tested loader (`tools/lpcore`), and every solved section decrypts from it exactly.

The unsolved LP2 cipher is pinned down by twenty-seven constraints (§3.2, C1–C27; each with its test in the
[findings §0 register](reference/findings/lp2_logic_findings_2026-09-29.md#0-constraint-register)). In short: an additive
stream over mod 29, plus an anti-doublet re-keying rule that leaks about 19 % of the time.
- **The key stream** is near-flat mod 29 and aperiodic. Its values come from an alphabet of at least ~30 symbols,
  so not digits, hex or letters. It is not English text, not derived from the primes or the solved text, and not
  chosen by earlier ciphertext.
- **The re-keying replacement** is independent of the key stream (not "skip to the next value"), or the leak is
  hand error.

That is the community's "OTP-class" verdict, with each piece now tested on canonical data. A drift-tolerant
detector (`tools/lpcore/detect.py`, false-positive bound e^−30) tests any named key source. It found none among
the riddle-derived keys (findings §8). The complete base-60 grid spans scans 66–68 and is interpreted as 256 bytes.
Stage M/N test that full payload as a key and under named LP-native keys, modes and alignments (findings §12–§13).
None of those full-grid candidates passes the original thresholds; these are bounded results, not an exclusion
of arbitrary transformations or other grid-derived keys.
The earlier 184-byte runs covered only a prefix. The five numeric-cell updates follow prior community work
credited to Inky in 2021; see [provenance](data/canonical/PROVENANCE.md). Title cribs were closed as untestable (findings §9).
Cicada's published numbers and every OutGuess payload in the repo also fail as keys, from any start phase (findings §16).
A label-free test of per-position alphabets on the long named keys was **void** by its own rule (findings §17).
The flatness of the cipher settles most of that question without a key (C16, findings §18). A secret tabula of
independent random alphabets needs a key with more than ~150 effectively equiprobable values, under any alignment or
desync. So a 26- or 29-row random tabula is out, and so are 15 of stage S's 20 key classings. A Latin-square tabula
(Quagmire-type) is invisible to that test. Stage U (findings §19) shows that a Quagmire cipher is the additive cipher
on relabelled runes. Its alphabets are invisible to any key-free statistic, but the key constraints mostly survive:
no iid key with V_eff ≥ 17 makes the deficit under any alphabets (C17), and under random alphabets the key is still
not English, decimal digits or hex (C18). Only C13's "not letters" is lost: with mixed alphabets a uniform A–Z key is
untestable.
Stage V (findings §20) names the alphabets: 34 LP keywords give 68 keyed alphabets, and all 314,432 triples are
scored with labels (C19). Under every one of them the key is not English or decimal digits, and hex is out for all
but 431. A uniform A–Z key is excluded for a third of the triples; most of the rest cannot be tested from 12,956
runes. No triple fits better than flat.
Stage W (findings §21) re-tests stage S's five long byte keys (the hint, the hint reversed, and the three OutGuess payloads)
as random 256-row tabulae, in step, this time with flat negatives. The run is valid (worst negative +0.64) and nothing
passes. All five are excluded on LP2 continuous (positives ≥ +1,634, LP2 ≈ −900) and on section 15, and two on section 11. The
shorter sections are untestable. Desync is not covered.
Stage X (findings §22) asks what the grid's 256 bytes allow by themselves. They look like uniform random bytes. Under any
per-column byte substitution (so any repeating XOR or add key), English ASCII, rune indices and hex text are excluded
for every period up to 102, and base64 up to 22. Read as a 2,048-bit integer the grid has small factors in every byte
order, so it is not an RSA modulus or a prime. It is not a compressed stream or a known file either. The grid is
OTP-class too: a modern cipher, a hash, random data, or an aperiodic key.
Stage Y (findings §23) runs every long byte source on disk (the three OutGuess payloads, the hint, the `page_00` hex and the
256-byte second-onion hex) as a running key on the grid, from every phase, in 4 readings and 4 operations: 2.87 million
trials. The run is valid (24 / 24 plants found, 0 / 18 negatives) and nothing passes. The lowest distinct-byte count is 139,
at the null's own level, where any text, rune, hex or base64 plaintext would sit at 64 or below. The long on-disk byte
material is now excluded both as an LP2 key and as an in-step running key for the grid. A slipping key is not covered.
Stage Z (findings §24) tests every cipher whose output for a word, or for an aligned block of n runes, depends only on
that unit: a key that restarts at each word, a word codebook, Hill or any polygraphic table. Any such cipher keeps the
plaintext's repeat count, whatever the table. LP2 repeats at the flat-null level in all 72 cells (|z| ≤ 1.38): 25
repeated word pairs within sections, against a null of 20 and at least 3,433 for an English word cipher. Word ciphers
and blocks of n = 2–4 at any offset are excluded (C20), and so is n = 5 in the continuous stream. Blocks of 6 or more
are untestable.
Stage AA (findings §25) extends that to sliding windows: a keyless cipher whose every rune is a fixed function of a short
plaintext window, with any table, keeps the plaintext's repeats of long windows. LP2's sliding 3- to 7-gram repeats sit
at the flat null (|z| ≤ 1.26). Windows of up to 3 runes (context restarting per section) and 2 runes (continuous) are
excluded (C21). That covers a plaintext-selected alphabet from the previous rune and plaintext autokey with any tables
at lag 1. Wider windows are untestable by the declared bound, though every control draw clears the null up to w = 7.
Stage AB (findings §26) asks whether the key starts again at every section, paragraph, clause, written line or page, the
same pad reused per unit. Then units would agree at equal in-unit positions under any alphabets. LP2's agreement counts
are at the flat null for all five unit types, so all five are excluded (C22). That makes the ledger's "keys shared
between sections" test-backed. The line count is the largest deviation (z = 2.98, below the null maximum), and it is
recorded, not interpreted.
Stage AC (findings §27) closes the long-period gap C9 left (C9 stops at 1000). LP2 is read as one stream, and every
lag 11–12,945 is scored for a key shared up to a constant shift or reflection, forwards and backwards. Nothing passes
(best 7.05 and 19.86 nats against null maxima of 10.15 and 20.39). Plain periodic keys are excluded for every period
11–11,781, including 1033, 1729 and 3301 under every relation (C23). No key stretch of ≥ 3,000 runes is reused.
Stage AD (findings §28) asks whether LP2's own ciphertext is the key at a long lag or read backwards. That is an
autokey, which C11 and C12 covered only to lag 1000. Every autokey hypothesis at lags 11–12,863 is excluded, under all
116 shift and reflection variants. No reused ciphertext stretch of ≥ 200 runes keys another (C24).
Stage AE (findings §29) is the label-free twin of C23. A periodic key choosing any alphabets makes runes one period apart
agree as often as the plaintext does. LP2's agreement rate is flat at every lag. Every period 11–4,907 is excluded under
any alphabets, along with 10,030 of the 12,935 lags up to 12,945, including 1033, 1729 and 3301 (C25).
Stage AF (findings §30) closes the last restart variant: the same key at every unit plus a constant per unit (key + page
number). Within-unit differences cancel the constant, and LP2's agreement on them is flat for all five unit types (C26).
Stage AG (findings §31) tests a named-generator family that meets every key constraint without a mapping: constants
written in base 29 (π, e, φ, √2, √3, ln 2, √3301) and base-29 concatenations of the primes, the integers and φ(p).
None is the key, from any start below 1,000 (C27; best real decode −56 nats).

**Next actions, in order** (all low prior; detail in [findings §6–§31](reference/findings/lp2_logic_findings_2026-09-29.md)):

1. **The grid's 256 bytes** are still undeciphered. Simple readings are exhausted (findings §12–§13, §22), and so are
   running keys from the byte material on disk (§23). What is left needs a key for a modern cipher, an RSA modulus, a
   new 2-D reading, or a new byte source, each declared as its own hypothesis.
2. **More named sources** only with a new primary source: OutGuess output from scans the repo does not hold
   (community `lp_outguessed/`), or a named generator (catalog row 22). The material on disk is exhausted (§16), and so
   is the material for wide random tabulae (§21) and for running keys on the grid (§23). A new byte source can go straight
   into `tools/run_stage_w.py`'s design for LP2 and `tools/run_stage_y.py`'s for the grid.
3. **Wider keyless contexts (cheap).** Stage AA's log-scale 5σ bound stops at w = 2 / 1 because of Emerson's right tail,
   but every control draw clears the null up to w = 7 (findings §25). A lower-tail bound with its own declared
   false-exclusion rate would extend C21. It needs a new declaration and a fresh run.
4. **Desync-tolerant tabula tests.** Stage W's detector loses all power at 1 % desync, so a byte-keyed tabula with a
   slipping key is still open. A test needs a model of the slip first. Without one it is a theme, not a hypothesis.

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
are indexed, one row each with its test, in the [findings §0 register](reference/findings/lp2_logic_findings_2026-09-29.md#0-constraint-register).
The evidence is in findings §2 (C1–C7), §7 (C8), §8 (C9), §9 (C10–C11), §10 (C12), §11 (C13), §14 (C14), §15 (C3's test, C15), §18 (C16), §19 (C17–C18), §20 (C19), §24 (C20), §25 (C21), §26 (C22), §27 (C23), §28 (C24), §29 (C25), §30 (C26) and §31 (C27):

- The anti-doublet rule acts on the continuous rune stream and ignores word boundaries (C1).
- There is no plaintext-F passthrough, unlike LP1 (C2). The surviving doublets mark no single plaintext letter (C3):
  26 letters predict the wrong count, and NG, IA and EA the wrong word positions.
- **No homophonic substitution (C15):** with 26 plaintext letters and 29 runes, the flattest possible cipher still
  has χ² ≥ 4,802 (LP2: 26.4).
- **No additive mod-29 cipher with a plaintext-independent key can produce the deficit**, whatever the key text (C4).
- Only lag 1 is affected (C5). One system runs throughout, with no seam between sections (C6). No one-shift-per-word scheme fits (C7).
- **The key is not English text (C10):** from any source, as letters, prime values or φ(prime values), in any mode
  and offset. The key's values must be near-flat mod 29. **No ciphertext autokey (C11)** at lags 2–1000.
- **No ciphertext-selected alphabet (C12):** c_i = σ_{c_{i−L}}(p_i) is excluded for any secret alphabets and
  any L ≤ 1000. This includes keyed autokeys c_i = p_i + f(c_{i−1}).
- **Key alphabet (C13):** not single decimal digits, hex digits, or letters (uniform or English in Latin spelling).
- **Not skip-next (C14):** a "skip to the next key value" rule needs a key repeating adjacent values ~19 % of the
  time, and that would leak English differences into Δc. LLR −21.3. The replacement must be independent of the key stream.
- **No periodic key (C9):** lags 11–1000 are normal. This excludes every period ≤ 1000 under a re-key rule that keeps
  the key in step, and every period ≤ 25 under a drifting one (findings §8). In step it holds for per-position alphabets
  c = σ_{k_i}(p) too, whatever σ is (findings §17). For straight alphabets C23 extends it to period 11,781.
- **Quagmire relabelling (findings §19):** c = π₂(π₁(p) + κ) is the additive cipher renamed, so C1–C3, C5–C9, C11, C12,
  C15 and L2–L5 hold for any alphabets. C4, C10, C13, C14 and L1 use the labels:
  - **C17:** for an iid key, the doublet rate lies in [2/29 − Σb², Σb²] under any π and any plaintext. LP2 needs
    Σb² > 0.05925 (V_eff < 16.9) to explain the deficit without a rule.
  - **C18:** under random alphabets, English keys (runes, prime values, Latin letters), decimal digits and hex still
    leave the cipher too uneven (worst P 1.7 × 10⁻¹¹ over 20 rows). Uniform A–Z letters are untestable this way, so
    C13's letters exclusion holds for straight alphabets only.
  - **C19:** with named keyword alphabets (34 LP keywords, K and K⁻¹ in any role, 314,432 triples, any mode and
    offset), scored with labels: English keys and decimal digits are excluded under every triple, hex under all but
    431, and uniform A–Z under 103,864. No triple scores above +6.51 (lead line +10).
- **No random tabula with few key classes (C16):** if each key value picks an independent random alphabet, the cipher
  marginal is a mixture whose χ² excess is about 10,400 / V_eff. LP2's flatness excludes V_eff ≤ 153 (one tabula) or
  ≤ 133 (one per section), at P ≤ 10⁻⁴ and under any alignment or desync. Latin-square tabulae are not covered (findings §18); see C17–C18.

- **No word or block codebook (C20):** equal plaintext words do not give equal cipher words, and equal aligned blocks
  of 2–4 runes (any offset, restarting per section or not) do not give equal cipher blocks. This excludes a key
  restarting at each word, every word codebook, and Hill or polygraphic tables with n ≤ 4 (n = 5 in the continuous
  stream). Repeats are at the flat level (findings §24).
- **No keyless sliding-context cipher (C21):** c_i = F(p_{i−a}, …, p_{i+b}) with any fixed F and no key keeps the
  plaintext's repeats of (n + w)-rune windows as cipher n-gram repeats. LP2's sliding repeats are flat, which excludes
  w = a + b ≤ 2 with the context restarting per section, and w ≤ 1 in the continuous stream (findings §25).
- **No key restart at any written unit (C22):** the key or alphabet sequence does not start again at each section,
  paragraph, clause, line or page. Same-position agreement between units is at the flat null for all five, under any
  alphabets, with the key in step (findings §26).
- **No long period (C23):** in the continuous stream, no periodic key of period 11–11,781 (plain, or shifting or reflecting
  by a constant each period), including 1033, 1729 and 3301, and no reused key stretch of ≥ 3,000 runes, forwards or
  backwards (straight alphabets, findings §27). This extends C9 past 1000 and across section boundaries.
- **The ciphertext is not its own key (C24):** no autokey c_j = p_j ± f(c_i) or Beaufort, with f a shift or reflection,
  at any lag 11–12,863 in either reading direction, and no reused ciphertext stretch of ≥ 200 runes (findings §28).
  This extends C11 past lag 1000 for straight alphabets.
- **No periodic key under any alphabets (C25):** a periodic key selecting any alphabets (Quagmire, any tabula) is excluded
  for every period 11–4,907 and for 10,030 of the 12,935 lags up to 12,945 in the continuous stream, label-free
  (findings §29). This extends C9 from 1000 to 4,907 and across section boundaries.
- **No shifted restart (C26):** no additive or Beaufort key restarts at each section, paragraph, clause, line or page
  even with a constant added per unit; within-unit differences agree at the flat level (findings §30).
- **Not a base-29 constant (C27):** π, e, φ, √2, √3, ln 2, √3301 in base 29, and the base-29 digit streams of the primes,
  the integers and φ(p), from any start < 1000, drift-tolerant (findings §31).

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
- No homophonic substitution of LP-English (C15, findings §15).
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
- **A "skip to the next key value" anti-doublet rule** (C14, findings §14).
- **The named full-grid byte/rune readings** under the AN END hash, φ(prime), primes, the solved keys as ASCII,
  or the square's cells (456 readings, findings §13). Other keys and transformations remain untested.
- **The scan 66–68 base-60 grid as a key in the tested alignments** (bytes, 5-bit groups, base-60 digits;
  3,132 decodes; findings §12). This does not exclude every use of the grid as a key.
- **Keys made of single decimal digits, hex digits or letters**, in any mode and offset (C13, findings §11). This
  covers π/e digits, the P.S. number, RAND digits, and hash hex read one symbol per rune.
- **Cicada's numbers and OutGuess payloads as additive keys, from any phase** (stage R, findings §16): the
  P.S. number (131 and 132 digits) and the 2014 RSA n as digit pairs or triples; the cookies, AN END hash,
  `page_00` hex, second-onion hex, wisdom/folly hint (both directions) and the three 58,152-byte `.bin` payloads
  as bytes, mod 29 or by rejection. 43,500 drift-tolerant decodes; best on a real section −50.8 vs +30; controls ≥ +169.
- **Per-position alphabets c = σ_{k_i}(p) with any short key in step** (period ≤ 1000: C9, findings §17).
- **Random tabulae keyed by ≤ 153 effective classes, any alignment** (C16, findings §18). Among stage S's long named keys
  this excludes primes mod 29, the solved text's runes and prime values, the hint and the `.bin` payloads mod 29 or by
  rejection, and the four corpora as letters. The raw-byte versions (V_eff ≈ 236–255) and Latin-square tabulae (for these
  keys, beyond C17–C18) remain **open**.
- **Quagmire-type ciphers (mixed alphabets, random) with an English, decimal-digit or hex key** (C18, findings §19), and
  any iid key with V_eff ≥ 17 as the sole cause of the deficit, under any alphabets (C17).
- **Quagmire with alphabets keyed by the 34 declared LP keywords** (C19, findings §20): English and decimal-digit keys
  under all 314,432 triples, hex under all but 431, uniform A–Z under 103,864. The other 210,568 uniform-letter triples
  (mostly untestable from LP2's length), other keywords and other keyed-alphabet constructions remain **open**.
- **Random 256-row tabulae keyed in step by the hint (either direction) or an OutGuess payload's raw bytes**
  (findings §21): on LP2 continuous and section 15 for all five, and section 11 for `page_21.bin` and `page_43.bin`. Other
  sections are untestable at their length, and a desynchronised key remains **open**.
- **The grid as a periodically keyed structured plaintext** (findings §22): any per-column byte substitution with period
  ≤ 102 (row order) or ≤ 112 (column order) over English ASCII, rune indices or hex text, ≤ 22 over base64; at period 1
  that includes any substitution plus any transposition. Not an RSA-2048 modulus or prime in any byte order, not a
  zlib/gzip/bz2/lzma stream, no known file signature. Aperiodic keys and modern ciphers remain **open**.
- **The grid under a running key from the long byte sources on disk** (findings §23): the three OutGuess `.bin` payloads,
  the hint, the `page_00` hex and the second-onion hex, from every cyclic phase, in step, under ⊕, g − k, g + k and k − g,
  in row or column order either way. Excluded for any plaintext with at most 120 distinct bytes (text, runes, hex, decimal,
  base64). A slipping key, sources not on disk and high-entropy plaintexts remain **open**.
- **Word- and block-deterministic ciphers** (C20, findings §24): a key restarting at every word, any word codebook,
  and any fixed substitution of aligned 2–4-rune blocks (Hill, digraphic, polygraphic) at any offset, plus 5-rune
  blocks in the continuous stream. Homophonic codebooks, blocks of 6 or more runes, and blocks restarting at
  lines or pages remain **open**.
- **Keyless sliding-context ciphers** (C21, findings §25): any fixed table of a plaintext window of width w ≤ 2 (per
  section) or w ≤ 1 (continuous). This includes plaintext-selected alphabets from the previous rune and plaintext autokey
  with arbitrary tables at lag 1. Wider windows, a key on top, mixed plaintext and ciphertext context, and
  position-dependent tables remain **open**.
- **A key restarting at every section, paragraph, clause, line or page** (C22, findings §26), under any alphabets, in step.
  Restarts with a per-unit shift, restarts from a unit's end and restarts every k-th unit remain **open**.
- **Periodic keys of period 11–11,781 and reused key stretches of ≥ 3,000 runes** (C23, findings §27), straight alphabets,
  any of the three conventions, forwards or backwards; the periods 1033, 1729 and 3301 under every shift and reflection.
  Shorter reused stretches, mixed alphabets and periods above 11,781 remain **open**.
- **LP2's own ciphertext as the key** (C24, findings §28): every autokey at lags 11–12,863 forwards or backwards, under any
  shift or reflection, and every reused ciphertext stretch of ≥ 200 runes. Mixed alphabets past lag 1000 and nonlinear
  autokeys remain **open**.
- **Periodic keys selecting any alphabets** (C25, findings §29): every period 11–4,907, most up to 10,000, and 1033 / 1729 /
  3301, label-free. The scattered open lags above 4,907 and a drifting key remain **open**.
- **A key restarting per unit with a per-unit shift** (C26, findings §30), additive or Beaufort. Mixed alphabets with a
  shifted key index and shifts changing within a unit remain **open**.
- **Base-29 constants and digit streams** (C27, findings §31): π, e, φ, √2, √3, ln 2, √3301, Copeland–Erdős, Champernowne
  and φ(p) concatenated, from any start < 1000. Other bases, constants and later starts remain **open**.
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
| 2026-10-12 | **Base-29 constants** (TODO AG): exact base-29 digits (`keys.constant_digits`, `keys.concatenated_digits`, verified to 60 decimals) of 7 constants and 3 concatenated streams as running keys, uniform prior over starts < 1000, stage R's drift-tolerant family (8,700 decodes). Controls ≥ +194.9 / ≤ −68.2. **No pass** (best real −56.0). **C27:** all 270 testable cells excluded. `--quick` scored 120 declared decodes before the runner commit (disclosed) | `7c83e52` `5e8c507` + this commit |
| 2026-10-12 | **Shifted restarts** (TODO AF): S_u = pairs of units agreeing on within-unit differences c[t′] − c[t] (gaps 2–300), which cancel any per-unit constant. 5 unit types, 200 nulls, 100 controls per source (additive and Beaufort). Valid (a 20-draw clause offset checked on 150 null-only draws first). No pass; **all five excluded (C26)**, prediction met. C22's line z = 2.98 is not echoed (z 0.61) but this stage cannot resolve a 1 % effect | `e2e305f` `adea288` + this commit |
| 2026-10-12 | **Periodic keys, any alphabets** (TODO AE): exact lag agreement counts k(L) on the continuous stream, L = 11–12,945; PASS by binomial upper tail ≤ 0.01 / 12,935 under LP2's Σf², exclusion by lower tail at p_H = 0.050 ≤ e^−10. Valid (20 nulls no PASS; 100 periodic-tabula controls all PASS, none excluded; lowest control rate 0.0520, a thin margin, disclosed). No pass (best lag 6002, p 3.1e-5). **C25:** every period 11–4,907 excluded, 10,030 of 12,935 lags overall | `434060d` `fb202c8` + this commit |
| 2026-10-12 | **Ciphertext as its own key** (TODO AD): stage AC's scan with the plaintext law (detect's emission) in place of the difference law, 4 relations × 29 shifts, forward and reverse. Valid (null F ≤ 7.18, S ≤ 23.26). No pass (F 5.30, S 23.16). **C24:** every autokey hypothesis at lags 11–12,863 excluded (1,490,948 of them); reused ciphertext stretches ≥ 200 runes found 400 / 400. Erratum: stage AC's and AD's declared family sizes miscounted the lags (12,945 for 12,935); bounds unchanged | `03dad0b` `1b0007a` + this commit |
| 2026-10-12 | **Key reuse at any lag** (TODO AC): LP2 as one stream, a labelled score per pair (difference or sum law of LP-English), 3 relations × 29 shifts. F = whole forward diagonal (periodic key, L = 11–12,945, 1,126,215 hypotheses), S = best segment on every forward and reverse diagonal (a reused stretch). "sumrev" (Beaufort reflection) added before LP2 was scored. Valid (4 full null scans: F ≤ 10.15, S ≤ 20.39). No pass (best F 7.05, S 19.86). **C23:** plain periods 11–11,781 all excluded, 1033 / 1729 / 3301 under every relation; 1,081,691 of 1,086,630 trusted hypotheses at F ≤ −10; reuse ≥ 3,000 runes found 300 / 300. lore.md's "3301 / 1033 ✗ as a period" was wrong before this stage and is now true | `b2f22d9` `a11ec86` + this commit |
| 2026-10-12 | **Key restarts at written units** (TODO AB): K_u = pairs of units agreeing at the same in-unit position, label-free. New `Corpus.rune_units` (rune-level ids, since rune words wrap across lines and pages). 5 cells (9 sections, 15 paragraphs, 168 clauses, 594 lines, 55 pages); 1,000 flat nulls, 200 Emerson and 200 shuffled solved-LP controls each. Valid. No pass; **all five excluded (C22)**, prediction met. Line z = 2.98 is the largest deviation, below the null maximum; recorded, not interpreted | `78f7c37` `a2512ca` + this commit |
| 2026-10-12 | **Keyless sliding-context ciphers** (TODO AA): K_n = separated pairs of equal sliding n-grams, n = 3–7, kept by any c_i = F(plaintext window of width w). 1,000 flat nulls; 200 Emerson and 200 shuffled solved-LP controls per (mode, w = 0–12). Valid (null means match the analytic E[K]). No pass; LP2 at the null in all 10 cells (\|z\| ≤ 1.26). C21: w ≤ 2 (sec) and w ≤ 1 (cont) excluded, 21 widths untestable. A declared expectation failed: it predicted exclusions up to w ≈ 4–7, but Emerson's skew holds the log-scale bound down. Every control draw still clears the null up to w = 7 (an observation only) | `5364609` `eacdc01` + this commit |
| 2026-10-01 | **Word and block codebooks** (TODO Z): K = pairs of equal units. Any word- or block-deterministic table keeps it exactly. 72 cells (words within sections and across LP2; n = 2–8 blocks at every offset, per section and continuous), 1,000 flat nulls, and 2 × 200 positive controls per cell. Valid (null means match the exact Markov-chain E[K]). No pass; LP2 at the null everywhere (\|z\| ≤ 1.38). 26 excluded (words; n = 2–4 at all offsets; n = 5 continuous and one sec offset), 46 untestable. C20. The positive bound was amended to log scale after `--quick` showed skew, before LP2 was scored (disclosed) | `be4a200` `3015705` `5298559` + this commit |
| 2026-10-01 | **Grid under long byte keys** (TODO Y): the 6 long byte sources on disk as running keys on the grid, every cyclic phase, 4 readings × 4 operations, 2,865,136 trials. The statistic is distinct bytes D, with an exact null (Stirling numbers); PASS means D ≤ 120 (1.1e-10 family-wise). Valid: 24 / 24 plants found (D 16–64), 0 / 18 negatives (mean D 162.002). No pass; minimum D 139. Erratum: the declared null minimum "131–136" should have read about 136–141 | `edd9c53` + this commit |
| 2026-10-01 | **Grid structure, key-free** (TODO X): the 256 bytes are consistent with uniform on 7 statistics. Within-class coincidences, which no per-column σ can change, exclude English, rune and hex plaintext under any repeating byte key of period ≤ 102 (row) / ≤ 112 (column), and base64 ≤ 22. Not an RSA modulus or a prime (small factors in all 4 readings; the 2 row readings were factored before the declaration, disclosed). No decompressor or signature fires (chance rates calibrated). No pass | `225ff30` + this commit |
| 2026-10-01 | **Byte keys as random tabulae** (TODO W): stage S's five raw-byte classings re-run in step with controls at each alignment's exact length and flat negatives. Valid (worst negative +0.64; nulls ≤ −876.6); no pass (best +0.84). 12 of 50 cells excluded: continuous and section 15 for all five keys (positives ≥ +125.8, LP2 ≤ −72.7), section 11 for two payloads; 38 untestable. LP2 rows equal stage S's, as declared | `106c634` `8af4b7e` `c88b443` + this commit |
| 2026-10-01 | **C/K rendering** (user report): solved plaintext in the page READMEs read CNOW, LICE, BOOC, because `indices_to_latin` has one spelling per rune (also UOICE, INSTRUCTIAN, THNGS). Display only: every scored path works on rune index 5, where C, K and Q are one value, so no result changes. `verify.render_words` now renders each solved word as the translation's word after `word_matches` confirms it; 17 page files regenerated | `a003cfd` |
| 2026-10-01 | **Named keyword Quagmire** (TODO V): 34 LP keywords → 68 alphabets → 314,432 triples per key family, scored with C13's labelled LLR (exact per member; false exclusion ≤ e^−10 whatever the family size). C19: English (3 forms) and digits excluded under every triple, hex under all but 431, uniform A–Z under 103,864. Gates passed (0 / 300 own-member exclusions). No lead. A declared expectation failed: not every testable member was excluded, and LP2 sits inside the flat-cipher range | `8880e3b` `7d44b09` + this commit |
| 2026-10-01 | **Quagmire relabelling** (TODO U): a Quagmire cipher is the additive one renamed, so key-free statistics cannot see its alphabets. Audit of C1–C16. C17: doublet rate in [2/29 − Σb², Σb²] under any labels; the deficit needs V_eff < 16.9. C18: under random alphabets, English, digit and hex keys stay excluded (20 / 20 rows, worst P 1.7e-11); uniform letters untestable. Declared gate roles were swapped, caught by `--quick` and amended before LP2 was scored | `4051fe2` `f2ecd72` + this commit |
| 2026-10-01 | **Flatness of random tabulae** (TODO T): C16. A random-alphabet mixture over V_eff classes adds ≈ 10,400 / V_eff to χ²; LP2's 26.36 excludes V_eff ≤ 168 / 174 by the declared rule, 153 / 133 after the anti-doublet correction (×0.939). Gates passed (formula within 7.1 %, 0 / 200 false exclusions). 15 of stage S's 20 classings excluded under any alignment; raw bytes and Latin-square tabulae stay open | `f0c8e39` + this commit |
| 2026-10-01 | **Per-position alphabets** (TODO S): label-free DM detector (`alphabets.py`, tested). C9 extended to σ keys. The 200-decode run on long named keys is **void** twice by its declared rule (run 1: tiled control text shared the key period; run 2: random-σ control ciphers are not flat, χ² 355–1,141). LP2 decodes ≤ +0.84, real-data nulls ≤ −489.5, but nothing is excluded. New lead: a flatness constraint | `8c93b22` `2c62782` `3f5b830` + this commit |
| 2026-10-01 | **Full-grid correction:** scans 66–68 supply all 256 cells; five numeric corrections follow Inky's 2021 iddqd update. Prime byte streams continue through all 256 positions. The regenerated 3,132 Stage M and 456 Stage N candidates give no pass; best nontrivial M score −13.75, N 42.6 % printable / +4.63 nats. Payload and stream regressions added; findings §§12–13 supersede the historical prefix results | `4f326e5` (PR #1) |
| 2026-10-01 | **Cicada numbers and OutGuess payloads** (TODO R): 25 sources × 2 mappings, any start phase (`starts=` prior), 43,500 decodes; none passes (best −50.8 on a real section; controls ≥ +169). `fastdetect` (numpy, tested equal). Synthetic check: a label-free coincidence test has power only in step | `2c209dc` `14320cb` |
| 2026-10-01 | **Consolidation** (TODO Q): constraint register (findings §0); C3 now a test (all 29 letters excluded); C15, no homophonic substitution (χ² ≥ 4,802); every §3.2 number pinned; `tests/test_docs.py` checks cited names; errata in C3 (75 → 25) and C7 (2.6 → 2.39 %) | `028ef53` `d8115fd` |
| 2026-10-01 | **Skip-next rule** (TODO O): C14, the re-keying is not "skip to the next key value" (LLR −21.3; held-out models −20/−32) | `0d4d86b` + this commit |
| 2026-10-01 | **Historical grid prefix** (TODO N): the original 184-byte payload gave 72 byte decryptions and 384 rune readings; none passed (best 44 % printable, best log LR −4.8). Superseded by the complete-grid rerun in findings §13 | `14afdff` + this commit |
| 2026-10-01 | **Historical base-60 prefix** (TODO M): scans 66–67 supplied 184 bytes and omitted scan 68. Its 3,132 key tests gave no pass; the power check gave +45…+122. This did not test the complete grid; see corrected findings §12 | `4d66364` + this commit |
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
