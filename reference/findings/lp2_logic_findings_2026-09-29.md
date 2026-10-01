# LP2 — logic-only findings, 2026-09-29

No hill-climbing, no optimisers. Every number below is reproduced by the test suite
(`python -m unittest discover -s tests -t . -v`) from canonical data (`data/canonical/`).

## 1. State of the art (web check, September 2026)

Nobody has solved the unsolved LP2 pages. Two public 2026 analyses matter:

- **[Leo-Y-Zhang/LiberPrimusAnalysis](https://github.com/Leo-Y-Zhang/LiberPrimusAnalysis).**
  The 12,956 unsolved runes are "statistically flat at every order except one": 86 adjacent
  identical runes against 447 expected (0.66 % vs 3.45 %, z = −17). Its exclusion ledger, where
  every negative result has a positive control, rules out: periodic keys with or without an
  F-interrupter; 46 integer sequences in raw and chain form; autokeys; prime-value feedback;
  running keys from Cicada texts; keys shared between sections; digraphic ciphers.
  It proposes a doublet-dodging rule that is "soft" (keeps a would-be doublet about 1 time in 5).
- **[Dukotah/cicada3301](https://github.com/Dukotah/cicada3301).** Verdict "OTP-class, not
  unsolvable". Ruled out: autokey; about 200 public key texts; common KDFs and PRNGs;
  Bitcoin, the NIST Beacon, RANDOM.ORG and RAND archives (about 14.5 billion offsets).
  Still open: short-seed derived keystreams; a pad that is public but unswept.
- Background: [Uncovering Cicada — unsolved pages](https://uncovering-cicada.fandom.com/wiki/Liber_Primus_Unsolved_Pages),
  [DEF CON 31 talk](https://media.defcon.org/DEF%20CON%2031/DEF%20CON%2031%20presentations/Taiiwo%20Artorias%20Puck%20TheClockworkBird%20-%20Cracking%20Cicada%203301%20The%20Future%20of%20Collaborative%20Puzzle-Solving.pdf).

Our canonical data independently reproduces their headline numbers exactly: 12,956 unsolved
runes, and 86 doublets in 12,947 adjacent pairs.

## 2. Key-independent constraints established here

Each result needs no key and no search. Each has a named regression test.

| # | Finding | Evidence | Test |
|---|---|---|---|
| C1 | **The anti-doublet rule ignores word boundaries.** It acts on the continuous rune stream, the same way the solved-section keys run through word breaks. | within-word 63/10,060 = 0.63 %; across-word 23/2,887 = 0.80 %; both far below 3.45 % | `test_suppression_ignores_word_boundaries` |
| C2 | **LP2 does not use LP1's "plaintext F unenciphered" convention**, or its plaintext is almost free of F. | ᚠ occurs 458 times vs 447 expected (flat; χ² = 26.4 on 28 df). F-passthrough would add roughly the plaintext F-rate, about 1.5 % of 12,956 ≈ 190 extra ᚠ. | `test_no_plaintext_f_passthrough` |
| C3 | **The surviving doublets do not mark any single plaintext letter.** This refutes the chain-multiplicative family c = c₋₁ + (p − x)·k over Z₂₉\*. | F predicts about 75 doublets at the end of 2-rune words (OF, IF); we observe 1. A positional log-likelihood against random placement is ≤ −0.3 for all 29 letters. EA's 0.62 % frequency matching 0.66 % is a coincidence. | analysis script (§5) |
| C4 | **No additive mod-29 cipher with a plaintext-independent key can produce the deficit**, whatever the key text. | Predicted rate Σ P(Δp=d)·P(Δk=−d) with LP-English as the model: English running key / long-lag autokey 3.60 %; φ(prime) 3.20 %; prime values 3.20 %; any flat key 3.45 %. Observed: 0.66 %. | `test_additive_ciphers_cannot_produce_the_deficit` |
| C5 | **Only lag 1 is affected.** Repeats at lags 2–10 are normal. | 3.38–3.69 % at every lag from 2 to 10 | `test_only_lag_one_is_depleted` |
| C6 | **One system throughout, with no seam.** Every unsolved section shows the deficit. | z from −4.1 to −8.9 per section; early (0.53 %) vs late (0.77 %) sections are not significantly different (p ≈ 0.10). All 9 sections: χ² = 5.33, df 8, p = 0.72 (§7 L4) | `test_l4_survivors_are_homogeneous_and_unclustered` |
| C7 | **Any scheme that uses one shift per word is excluded.** | A per-word shift preserves plaintext bigram differences inside words (2.6 % doublets for LP-English). Observed within-word rate: 0.63 %. | follows from C1 |

Reading of C1–C7: the deficit comes from a rule applied at the output of a non-periodic
additive stream. It is not a property of any key text, of word structure, or of a particular
plaintext letter. That agrees with both community analyses, now derived from the book's own
plaintext statistics.

## 3. The LP2 4×4 square (scan 32, segment 10) is fully decoded

```
3258 3222 3152 3038
3278 3299 3298 2838
3288 3294 3296 2472
4516 1206  708 1820
```

Read as a spiral out from the centre (3299 → 3298 → 3296 → 3294 → 3288 → 3278 → 3258 → …),
every cell is **|3301 − p(F+1)|**, where p(n) is the n-th prime and F runs over the distinct
Fibonacci numbers 0, 1, 2, 3, 5, 8, …, 987. The ordinals are 1, 2, 3, 4, 6, 9, 14, 22, 35, 56,
90, 145, 234, 378, 611, 988. The last two cells are the only ones where the prime exceeds 3301:
3301 + 1206 = 4507 = p(611) and 3301 + 4516 = 7817 = p(988). That explains the bottom row, which
the old tracker's "3301 − x gives primes" rule could not. Test: `test_square_on_scan_32_is_fully_explained`.

The other squares in the book are also decoded:
- LP1 scan 05: magic sum **1033**. Some cells are words, and their gematria sum is the cell
  value (SHADOWS = CABAL = 341, AETHEREAL = 366, …). Test: `test_scan05_square_parses_into_a_magic_square`.
- LP1 scan 16: magic sum **3301**, with 809 at the centre. 1033 reversed is 3301.

## 4. Other facts pinned by the tests

- Every solved section reproduces exactly from canonical runes, with two errata. **WIDSOM** is a
  typo in the book's own plaintext; it survives decryption, and a transcription swap could not
  produce it. **FOLLWING** is a typo in the upstream translation (the runes say FOLLOWING, using ᛝ).
- The DIVINITY key runs continuously through all 515 runes of WELCOME/WISDOM.
  FIRFUMFERENFE runs continuously through the 319-rune koan: no resets at quotes.
- Unsolved section sizes: 729, 1145, 1729, 9, 1894, 1021, 1524, 1589, 3316 runes.
  Curiosities, not evidence: 729 = 9³ and 1729 = 9³ + 10³ (the taxicab number); 1021 is prime;
  3316 = 4 × 829, and 829 is one of the square's primes.

## 5. Reproducing the analysis-script row (C3)

C3 was computed in a one-off session script (C6 is now a test, §7 L4). The inputs are all available from
`tools.lpcore`: `corpus.rune_words(seg)` for word positions, and `stats.lag_repeats` for
per-section rates. Promote it to a test before building on them.

## 6. What is still open — suggested next logic steps

1. ~~**Characterise the leak.**~~ **Done 2026-10-01, see §7.** Nothing separates the survivors.
   The key-switch scheme is refuted. C8 states what any re-keying rule must satisfy.
2. ~~**Key-source riddles not in either community ledger.**~~ **Done 2026-10-01, see §8.** The prime family,
   word sums and plaintext values all fail under a drift-tolerant detector. Periodic keys are excluded (C9). The
   square does not decode the segment 10 title.
3. ~~**Section titles.**~~ **Closed 2026-10-01, see §9.** A crib is falsifiable only under a key model, and the
   "reads as English" model is excluded on the whole text by C10.

## 7. The doublet leak, characterised (2026-10-01, TODO stage H)

The predictions and verdict rules were written in `TODO.md` before the run. Module: `tools/lpcore/leak.py`.
Tests: `tests/test_leak.py`. Each statistic also has a positive control, a synthetic stream with the effect
built in, and the test checks that the statistic detects it.

| # | Question | Observed | Verdict |
|---|---|---|---|
| L1 | Where did the ≈ 361 suppressed doublets go? | Δc bins d = 1..28 range 404–510. The largest deviation is \|z\| = 2.58 (d = 17, *low*). Threshold 3.5 | **Spread evenly.** No "nudge" rule (c ± 1 or similar) |
| L2 | Is the rule checked only within a written line? | within a line 82 / 12,362 (0.66 %); across a line break 4 / 585 (0.68 %); across a page break 0 / 48 | **The rule spans line and page breaks.** One-sided p = 0.54 |
| L3 | Do survivors fall on a period (m = 2..32, two indexings)? | Best union-bound p = 0.036 (m = 27 along the stream). Bonferroni threshold 1.6 × 10⁻⁴ | **No period** |
| L4 | Are survivors clustered or section-dependent? | Across sections χ² = 5.33, df 8, p = 0.72 (C6, now a test). Index of dispersion in 500-pair windows = 1.02 | **Homogeneous and unclustered** |
| L5 | The community key-switch ([`Algorithm.png`](../community/images/Algorithm.png)) on 2,901 runes of LP1 plaintext | DIVINITY / CIRCUMFERENCES: idealised 6 / 2,900 (0.21 %), the picture's literal code 10 / 2,898 (0.35 %, not the 0.69 % it claims). Scaled to 12,947 pairs: λ = 27 and 45; P(X ≥ 86) = 9 × 10⁻²⁰ and 3 × 10⁻⁸ | **Refuted** as declared (threshold 10⁻⁶) |

The second declared key pair, φ(prime) / prime values, turned out to be degenerate: φ(p) = p − 1, so key 2 is
always key 1 + 1 and no switched rune can repeat (0 survivors). This does not change the verdict. It is a
special case of C8 below.

**C8 (exact, no key needed): a re-keying rule leaks exactly where the replacement key equals the original.**
Suppose a would-be doublet p + k = c₋₁ is re-encrypted with a replacement key value k′. Then p + k′ = c₋₁
holds if and only if k′ ≡ k. So any "on a would-be doublet, use another key value" mechanism (a second key,
skipping to the next key value, a re-draw) keeps 19 % of would-be doublets only if its replacement value
equals the original at ≈ 19 % of those positions. For independent keys the figure is 1 / 29 ≈ 3.4 %.
For a "skip to the next key value" rule, 19 % is the key stream's own lag-1 repeat rate.

**Reading.** The survivors look like independent random events at one constant rate. That rate holds across
lines, pages, sections and phases, and the missing doublets are spread evenly over every other difference.
This fits a re-keying rule (L1) whose replacement agrees with the original about 19 % of the time (C8).
It also fits a check applied by hand with ≈ 81 % reliability. These data cannot tell the two apart.
Any proposed mechanism must reproduce L1–L4 and the 19 % figure from its own definition, without fitting.

## 8. Key-source riddles with a drift-tolerant detector (2026-10-01, TODO stage I)

Predictions, thresholds and the candidate list were written in `TODO.md` before the run. Module:
`tools/lpcore/detect.py`. Candidates: `tools/lpcore/keys.py`. Run: `python -m tools.run_stage_i`, which writes
every decode to [`stage_i_candidates.tsv`](stage_i_candidates.tsv). Tests: `tests/test_detect.py`.

**The detector.** C8 says a would-be doublet is re-keyed. If that consumes key values, the key drifts out of step
with the cipher about every 36 runes, and a fixed-sync decode of the right key looks like noise. `detect.log_lr`
sums over every drift path with the forward algorithm. At each rune the key index moves +1, +2 (a skipped value)
or 0 (a stall or interrupter), with ρ = 0.02 each for the last two. The emission ratio against uniform noise is
r = 0.9 · 29 · q(p) + 0.1, where q is the unigram of the solved plaintext. Under a uniform null E[r] = 1, so
E[LR] = 1 and **P(log LR ≥ 30) ≤ e^−30 ≈ 10^−13 per hypothesis, with no calibration**. Unigram emissions are
blind to plaintext order, so a transposition before encryption would not hide the key.

| Control (declared) | Observed | |
|---|---|---|
| Seg 1, DIVINITY (515 runes; q built without seg 1) | **+142** nats; fixed sync −104 (F interrupters desync it) | pass |
| Seg 5, FIRFUMFERENFE (319 runes) | +119 | pass |
| Seg 16, φ(prime) (AN END, 85 runes) | **29.6 < 30** | **failed by length.** The detector needs ≳ 100 runes in step; every LP2 section except seg 10 has ≥ 729 |
| Synthetic: solved plaintext under φ(prime), skip-next anti-doublet rule, 19 % leak | +892; fixed sync negative; 0.52 % doublets (LP2: 0.66 %) | pass |
| Wrong key (DIVINITY on seg 5); 180 random keys on LP2 sections | all < 30 (random keys ≈ −0.13 nats per rune) | pass |

**C9 (key-independent): no periodic key.** Repeat rates at lags 11–1000 inside sections are all normal. The best
is lag 717 (304 / 7,211, p = 3.4 × 10⁻⁴); the declared Bonferroni threshold was 1.0 × 10⁻⁵. Power, measured on
synthetic text of LP2's size: under a re-key rule that keeps the key in step, every period from 16 to 1000 is
detected (p ≤ 10⁻²⁰). Under a drifting skip-next rule only periods ≤ 25 are. With C5 (lags 2–10), this excludes
every periodic key of period ≤ 1000 under an in-step rule, and of period ≤ 25 under a drifting one. That includes
the scan-32 square's 16 values and Fibonacci or Lucas numbers mod 29 (Pisano period 14).

**The candidate family: 2,610 decodes, none passes.** Each key ran in 3 modes (sub, add, beaufort) × 29 constant
shifts × 10 alignments (each of 9 sections from its first rune, and continuous through LP2). The family's
false-positive bound is 2,610 · e^−30 ≈ 2 × 10⁻¹⁰.

| Key | Definition | Covers | Best log LR on a real section | Median |
|---|---|---|---|---|
| K-A | primes p(n), 25,912 terms | p ± c, φ(p) (AN END's stream continued), 3301 − p(n) | −69.5 | −194 |
| K-C | gematria sum of each solved-plaintext word, book order (726 terms) | "their numbers are the direction" | −65.5 | −97 |
| K-D | prime value of each solved-plaintext rune (2,901 terms) | the solved text as a running key | −77.4 | −215 |

The only scores above 0 come from segment 10, whose 9 runes carry no power (the best is +4.1). A right key would
score hundreds of nats on any LP2 section. K-C covers only the first 726 runes of each alignment.

**The segment 10 title is not the square's key at work.** Its 9 runes (F-U-L-M A-EA-Y-OE-A) were decoded with the
square's own numbers, read outward and inward along the spiral, in 3 modes: the cell values, p(F+1), p(F+1) − 1,
the ordinals F+1, and F itself. That is 30 decodes, and none gives two English words. The check accepts WISE WORDS
enciphered the same way. Chance rate, measured first: 0 of 20,000 random keys pass.

**Reading.** Prime-based streams, with or without drift and in every mode and shift, are not the LP2 key. Nor are
the solved text's word sums or rune values. Periodic keys are gone. What is left are long, aperiodic keys from
a source nobody has named, or a non-additive cipher.

## 9. What the key's own statistics must be (2026-10-01, TODO stage J)

Rules declared in `TODO.md` before the run. Functions: `stats.running_key_distribution`, `stats.unigram_llr`,
`stats.lag_combination_chi2`. Tests: `tests/test_keyspace.py`. Neither result needs a key.

**C10: the key is not English text, from any source.** Let c = p + k (sub), p − k (add) or k − p (beaufort), with p
and k both English. Then c's rune distribution is the convolution or correlation r of two English unigrams, and r
is not flat. Before looking at LP2 the prediction was IoC(r) = 1.054 for key letters used as values, and 1.042
for key letters mapped to their prime values or φ of those, mod 29. That is a χ² excess of about 550–700 on
12,956 runes, against the observed χ² of 26.4 on 28 df (C2). The test is LLR = Σ_c O_c · log(29 r_c), taking the
most favourable of the 29 constant key offsets. The hypothesis is excluded at LLR ≤ −10.

| Key letters as | λ = 1 (English key) | λ = 0.5 | λ = 0.25 (only a quarter English-like) |
|---|---|---|---|
| letters (values 0–28) | −333 / −287 / −287 | −75 / −68 / −68 | −15.7 / −14.4 / −14.4 |
| prime values mod 29 | −255 / −273 / −268 | −121 / −124 / −121 | −83 / −80 / −79 |
| φ(prime values) mod 29 | −255 / −273 / −268 | −121 / −124 / −121 | −83 / −80 / −79 |

Columns give sub / add / beaufort. The key distribution in each column is λ·English + (1 − λ)·uniform. **All
27 are excluded.** Positive controls: on 2,901 runes, the solved text enciphered with itself as a running key
scores +70 (+74 with prime values); a random key scores −62. A true English running key would score about +300
on LP2. Prime values mod 29 are not a permutation (31 ≡ 2, and so on), so a key made of prime values is uneven
*whatever the text*; that is why those rows stay negative even at λ = 0.25.

Consequences:
- No running key from any English text, public or not, in these three mappings. This covers Dukotah's
  "public but unswept pad" item whenever the pad is English text.
- No plaintext autokey at any lag, since its key is the plaintext itself.
- The key stream's values mod 29 must be close to flat: random-like numbers, not text.

**C11: no autokey on the ciphertext, at any lag 2–1000.** Under c_i = p_i ± c_{i−L}, the lag-L difference or sum
of the ciphertext *is* the plaintext, so its histogram would be English. Across 1,998 tests (lags 2–1000 ×
difference and sum), none is flagged. The best is lag 880, difference, χ² = 58.9 on 28 df, p = 5.6 × 10⁻⁴,
against the declared threshold of 5.0 × 10⁻⁶. Positive controls (an autokey at L = 7 and L = 500, both signs)
give χ² ≈ 7,000–10,000. The Leo-Y-Zhang ledger covered lags 1–60; L1 already covers the lag-1 difference.

**Title cribs are closed as untestable.** Against a key with no model, any crib yields *some* key fragment, so a
crib alone cannot fail. The only declared model for a fragment was "it reads as English", and C10 tests that on
all 12,956 runes at once, with far more power than a 10-rune title. A crib becomes testable again only together
with a concrete key-source hypothesis, and then `detect.log_lr` scores the whole section anyway.

## 10. No ciphertext rune chooses the alphabet (2026-10-01, TODO stage K)

Rule declared in `TODO.md` before the run. Function: `stats.transition_chi2`. Tests: `tests/test_keyspace.py`.

**C12.** Suppose an earlier cipher rune picks the alphabet: c_i = σ_{c_{i−L}}(p_i) for any 29 secret permutations.
This family includes keyed autokeys with a secret table, c_i = p_i + f(c_{i−1}), and affine chains. Then row x of
the lag-L transition table is a permutation of the plaintext distribution, with IoC ≈ 1.79 whatever σ is. The
test is Pearson χ² over the off-diagonal cells (the diagonal is where the doublet rule acts), against
E_xy = R_x · f_y / (1 − f_x), with df = 783 and the p-value from Wilson–Hilferty.

| | Observed |
|---|---|
| LP2, lags 1–1000 | **0 flagged.** The best is lag 142, p = 3.9 × 10⁻³, against the declared threshold of 10⁻⁵. At lag 1 off the diagonal: χ² = 785.5 on 783 df |
| Calibration: random streams of LP2's section sizes | 0.1–0.2 % of lags at p < 0.01 (nominal 1 %): the test is slightly conservative. None flagged |
| Positive control: random σ tables, solved plaintext, LP2-sized | χ² = 14,445 (L = 1) and 7,592 (L = 500) |

C12 subsumes C11 and covers the lag-1 sum, which L1 and C11 did not test.

**Not covered:** the same construction with a flat stream key added on top, c_i = σ_{c_{i−L}}(p_i + k_i), whose rows
are flat. Also not covered: alphabets chosen by *plaintext* runes, and contexts of two or more runes. A
two-rune context gives 841 rows of about 15 entries each, too sparse for χ².

**Where this leaves the cipher (C1–C12).** On top of whatever does the anti-doublet re-keying, there is a key
stream whose values are near-flat mod 29. It is not periodic, not English text, not derived from the primes or
the solved text, and not a function of the ciphertext alone. That is the "OTP-class" verdict of both community
ledgers, now with each piece tested on canonical data. Only a named key source can go further, and
`detect.log_lr` is the tool for testing one.
