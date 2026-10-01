# LP2 — logic-only findings, 2026-09-29

No hill-climbing, no optimisers. Current numbers are reproduced by the cited tests or named runners
from canonical data (`data/canonical/`). Run the full suite with `python -m unittest discover -s tests -t . -v`.
Explicitly labelled historical-prefix results in §§12–13 describe the earlier commits, rather than the
current full-grid input.

## 0. Constraint register

One row per constraint, with the test that pins it. **This is the index. The sections below hold the evidence.**
`tests/test_docs.py` fails if a C-number in the tracker has no row here, or if a test named here does not exist.

| # | Constraint on the LP2 cipher | Observed vs declared line | Test | § |
|---|---|---|---|---|
| C1 | The anti-doublet rule ignores word boundaries | within-word 0.63 %, across 0.80 %, vs 3.45 % | `test_suppression_ignores_word_boundaries` | 2 |
| C2 | No plaintext-F passthrough; unigrams flat | ᚠ 458 vs 447 (passthrough adds ≈ 190); χ² 26.4 on 28 df | `test_no_plaintext_f_passthrough`, `test_unigrams_are_flat` | 2 |
| C3 | The survivors mark no plaintext letter | 26 letters by count (p < 10⁻⁶); NG, IA, EA by position, LLR −106 / −149 / −68 ≤ −10 | `test_every_letter_is_excluded` | 2, 15 |
| C4 | No additive cipher with a plaintext-independent key makes the deficit | predicted 3.20–3.60 % vs 0.66 % | `test_additive_ciphers_cannot_produce_the_deficit` | 2 |
| C5 | Only lag 1 is affected | lags 2–10: 3.38–3.69 % | `test_only_lag_one_is_depleted` | 2 |
| C6 | One system, no seam between sections | χ² 5.33 on 8 df, p = 0.72; early vs late p = 0.099 | `test_l4_survivors_are_homogeneous_and_unclustered`, `test_early_and_late_sections_do_not_differ` | 2, 7 |
| C7 | No one-shift-per-word scheme | predicted 2.39 % within words vs 0.63 % (z = −11.6) | `test_per_word_shift_is_excluded` | 2 |
| C8 | A re-key leaks exactly where the replacement equals the original | algebraic identity (p + k′ = c₋₁ ⇔ k′ = k) | `test_key_switch_mechanics` (the k′ = k + 1 case) | 7 |
| C9 | No periodic key, additive or per-position alphabets σ_{k_i} (in step) | lags 11–1000: best p = 3.4 × 10⁻⁴ vs 1.0 × 10⁻⁵ | `test_no_period_in_the_unsolved_text`, `test_sigma_periodic_keys_are_flagged_at_their_period` | 8, 17 |
| C10 | The key is not English text (letters, prime values, φ) | LLR −255 … −333 ≤ −10 | `test_no_english_running_key` | 9 |
| C11 | No ciphertext autokey, lags 2–1000 | best p = 5.6 × 10⁻⁴ vs 5.0 × 10⁻⁶ | `test_no_ciphertext_autokey` | 9 |
| C12 | No alphabet chosen by c_{i−L}, L ≤ 1000 | best p = 3.9 × 10⁻³ vs 10⁻⁵ | `test_no_ciphertext_selected_alphabet` | 10 |
| C13 | The key is not single digits, hex digits or letters | LLR −214 / −19.5 / −14.3 / −122 ≤ −10 | `test_small_key_alphabets_are_excluded` | 11 |
| C14 | The re-keying is not "skip to the next key value" | LLR −21.3 ≤ −10 | `test_skip_next_is_excluded` | 14 |
| C15 | No homophonic substitution (without a stream on top) | least possible χ² 4,802 ≥ 200, vs 26.4 observed | `test_homophonic_substitution_is_excluded` | 15 |

**The leak** (how the 86 survivors are spread, §7):

| # | Finding | Observed vs line | Test |
|---|---|---|---|
| L1 | Suppressed doublets spread evenly over Δc = 1–28 (no nudge) | max \|z\| 2.58 < 3.5 | `test_l1_suppressed_doublets_spread_evenly` |
| L2 | The rule spans line and page breaks | line-break 4 / 585 vs within-line 0.66 %, p = 0.54 | `test_l2_rule_spans_line_and_page_breaks` |
| L3 | Survivors fall on no period, m = 2–32 | best p = 0.036 vs 1.6 × 10⁻⁴ | `test_l3_no_period_in_survivor_positions` |
| L4 | Survivors are homogeneous and unclustered | dispersion 1.02 | `test_l4_survivors_are_homogeneous_and_unclustered` |
| L5 | The community key-switch leaves too few doublets | λ = 27 / 45 vs 86; P ≤ 3 × 10⁻⁸ | `test_l5_key_switch_cannot_leave_86_doublets` |

**Named key families scored and failed** (each a declared, recorded family):

| Family | Decodes | Best vs pass | Test |
|---|---|---|---|
| Primes, word sums, plaintext values (stage I) | 2,610 | −65 vs +30 nats | `test_recorded_family_is_complete_and_fails` |
| The square's numbers on the segment 10 title | 30 | 0 English | `test_segment_10_title_is_not_decoded_by_the_square` |
| The complete base-60 grid as a key in the tested alignments (stage M) | 3,132 | −13.75 excluding the short title vs +30 | `test_recorded_family_fails` |
| The complete grid under the named byte/rune readings (stage N) | 456 | 42.6 % printable vs 90 %; +4.63 vs +30 | `test_recorded_verdict` |
| Cicada's numbers and OutGuess payloads, any phase (stage R) | 43,500 | −50.8 vs +30 | `test_recorded_family_is_complete_and_fails` |
| Long named keys as per-position alphabets, label-free (stage S) | 200 | **void**: excludes nothing (§17) | `test_run_2_is_void` |

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
| C2 | **LP2 does not use LP1's "plaintext F unenciphered" convention**, or its plaintext is almost free of F. | ᚠ occurs 458 times vs 447 expected (flat; χ² = 26.4 on 28 df). F-passthrough would add roughly the plaintext F-rate, about 1.5 % of 12,956 ≈ 190 extra ᚠ. | `test_no_plaintext_f_passthrough`, `test_unigrams_are_flat` |
| C3 | **The surviving doublets do not mark any single plaintext letter.** This refutes the chain-multiplicative family c = c₋₁ + (p − x)·k over Z₂₉\*. | Under x = F, OF and IF would put about 25 doublets at the end of 2-rune words; 1 is observed. 26 letters predict the wrong count; NG, IA and EA predict the wrong word positions. EA's 0.62 % frequency matching 0.66 % is a coincidence. Declared test and numbers: §15 | `test_every_letter_is_excluded`, `test_f_would_end_two_rune_words` |
| C4 | **No additive mod-29 cipher with a plaintext-independent key can produce the deficit**, whatever the key text. | Predicted rate Σ P(Δp=d)·P(Δk=−d) with LP-English as the model: English running key / long-lag autokey 3.60 %; φ(prime) 3.20 %; prime values 3.20 %; any flat key 3.45 %. Observed: 0.66 %. | `test_additive_ciphers_cannot_produce_the_deficit` |
| C5 | **Only lag 1 is affected.** Repeats at lags 2–10 are normal. | 3.38–3.69 % at every lag from 2 to 10 | `test_only_lag_one_is_depleted` |
| C6 | **One system throughout, with no seam.** Every unsolved section shows the deficit. | z from −4.1 to −8.9 per section; early (0.53 %) vs late (0.77 %) sections are not significantly different (p ≈ 0.10). All 9 sections: χ² = 5.33, df 8, p = 0.72 (§7 L4) | `test_l4_survivors_are_homogeneous_and_unclustered` |
| C7 | **Any scheme that uses one shift per word is excluded.** | A per-word shift preserves plaintext bigram differences inside words, so the within-word doublet rate would be LP-English's own: 52 / 2,175 = 2.39 %. Observed: 0.63 % (z = −11.6). | `test_per_word_shift_is_excluded` |

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

*Closed 2026-10-01.* C3 was a one-off script. It is now a declared test (§15), and every row in §2 has a test.

## 6. What is still open — suggested next logic steps

*Historical: these were the next steps on 2026-09-29. The current open list is `MASTER_TRACKER.md` §1.*


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

## 11. What values the key can take (2026-10-01, TODO stage L)

Rules declared in `TODO.md` before the run. Functions: `stats.cipher_distribution`, `stats.values_distribution`.
Tests: `tests/test_keyspace.py`.

**C13.** C10 generalised from "English text" to any small key alphabet. If the key's values come from a small set,
the cipher distribution r = q ⊛ k is uneven in every mode and offset, and no amount of drift or skipping changes
that. The statistic is C10's, the best LLR over 3 modes × 29 offsets; offsets also cover A = 0 against A = 1 and
digit + constant. The expected LLR if true was computed from the model before the run.

| Key values | Expected if true | LP2 (best of 87) | Control | Verdict |
|---|---|---|---|---|
| decimal digits 0–9 | +240 | **−214.3** | +251 | excluded |
| hex digits 0–15 | +41 | **−19.5** | +45 | excluded |
| letters A–Z, uniform | +25 | **−14.3** | +24 | excluded |
| English text as Latin letters A–Z | — | **−121.7** | +141 (Emerson) | excluded |
| base-60 digits, two-digit groups 00–99, bytes, 000–999 | +3 … 0 | — | — | **untestable this way** (no power) |

Consequences: the key is not a stream of single decimal digits. That covers π, e, the 2012 P.S. number, RAND
digits, and any number written out in decimal, read one digit per rune, in any mode and offset. It is not single
hex digits (a SHA hash, OutGuess hex), and not letters, whether uniform or English in Latin spelling. Wider
alphabets (bytes, digit pairs, base 60) leave too little trace in the marginal. Those need a named source and
`detect.log_lr`.

## 12. The complete base-60 grid as a key (2026-10-01, TODO stage M, corrected)

The original plan and thresholds were declared in `TODO.md`; the correction plan restores the complete input
without adding a cipher family. Parser: `keys.grid_bytes` and siblings. Run: `python -m tools.run_stage_m`,
rows in [`stage_m_candidates.tsv`](stage_m_candidates.tsv). Tests: `tests/test_detect.py` (`TestStageMGrid`)
and `tests/test_grid_extraction.py`.

**Input correction.** The original extractor selected only scans 66 and 67, yielding a 184-byte prefix and
omitting the final 72 cells on scan 68. The complete grid spans **LP2 pages 49–51 / scans 66–68**, with
80 + 104 + 72 = **256 cells**. Five numeric cells now follow the prior community corrections credited to Inky
in [iddqd commit f804b85, 2021-05-09](https://github.com/cicada-solvers/iddqd/commit/f804b85e9e6fe6287c7cab054335af07ed420728).
The 2019 punctuation and all rune text are preserved. Some `I`/`l` strokes are ambiguous; the cell choices follow
that documented community convention. See [canonical provenance](../../data/canonical/PROVENANCE.md) for the
exact overlay, attribution and source checksums.

**Tested byte interpretation.** Tokens use base 60 (0-9 A-Z a-x), interpreted as `60*a+b`. The first character
is never above 4, and for 4 the second is at most F, so the values lie in 0–255. This convention yields a
256-byte payload starting cb e7 a7 ba, with 161 distinct values and entropy 7.16965 bits per byte.
Its SHA-256 is `3b9b07d9a26e6d55c432d94d2661fdff3c2b348daed06821f2bdb23184a4b290`.
The first grid cell follows rune 2,474 of section 15's 3,316; these offsets do not change.
`test_all_three_pages_and_current_payload` pins the counts, checksum and byte properties. The byte reading is
a tested convention, not an authenticated statement of Cicada's intent.

**Full-grid key tests: none passes.** The three readings, all mod 29, are bytes (256 values), 5-bit groups
MSB first (409, with the final three bits dropped), and single base-60 digits (512). Each runs in 3 modes ×
29 shifts × 12 alignments: the 9 section starts, LP2 continuous, the runes right after the grid, and the runes
ending where the grid begins. That is 3,132 decodes under the original pass threshold of +30 nats. The detector's
uniform-null false-positive bound for this family is 3,132 × e⁻³⁰ ≈ 3 × 10⁻¹⁰.

| Key | Power control | Best excluding section 10 |
|---|---|---|
| bytes | +88.33 | −13.75 (section 8, Beaufort, shift 9) |
| 5-bit groups | +134.55 | −28.20 (section 7, Beaufort, shift 9) |
| base-60 digits | +167.15 | −47.26 (section 13, add, shift 13) |

Power controls use the exact construction in `test_power_check`: solved plaintext beginning at rune 700,
`n=int(len(key)/1.1)`, skip-next encryption with `keep=0.19` and seed 700. Each exceeds the declared threshold.
The best score anywhere is +4.83 on the 9-rune section 10, whose short title gives little power.

**Historical prefix results.** The original 184-byte / 294-group / 368-digit run also tested 3,132 candidates.
Its best score excluding section 10 was −5.5 (bytes, section 15), and its power checks were +45…+122.
Those results applied only to the older-transcription prefix; they did not test the complete grid. The current
TSV and assertions are regenerated for the complete, updated payload. The historical construction is
`tools/run_stage_m.py` at the pre-correction baseline `a7ab786`.

**Scope.** These results concern the named readings, modes, shifts, alignments and drift detector. They do not
exclude other offsets, transformations, plaintext models or uses of the grid as a key. This stage does not
attempt to decipher the grid itself.

## 13. The complete grid under named LP-native keys (2026-10-01, TODO stage N, corrected)

The original thresholds remain unchanged. Run: `python -m tools.run_stage_n`, rows in
[`stage_n_results.tsv`](stage_n_results.tsv). Tests: `tests/test_grid.py` and `tests/test_grid_extraction.py`.
The input is the complete 256-byte payload documented in §12.

**Byte readings: 72 decryptions, none passes.** Operations are XOR, b − k and b + k mod 256, with the grid read
forward and reversed. Keys are the AN END hash (64 bytes, canonical scan 73) and its reverse; φ(prime) mod 256
and primes mod 256; DIVINITY, FIRFUMFERENFE and CIRCUMFERENCE as ASCII in upper and lower case; "3301";
and the scan-32 square cells mod 256. The hash, ASCII and square keys repeat. The prime streams now continue
through all 256 positions: the original fixed 200-prime list would have wrapped prematurely on the full grid.
A regression checks the actual prime contents, not just their lengths.

A pass needs ≥ 90 % printable ASCII or a recognized file signature. The best output is **42.6 % printable**,
and no output matches a signature. All 36 named key/operation combinations recover their planted 256-byte
ASCII text exactly in `test_positive_controls_bytes`.

**Rune readings: 384 decodes, none passes.** The grid is read as bytes mod 29 and base-60 digits mod 29, each
forward and reversed. Keys are a constant (3 modes × 29 shifts, covering Caesar and atbash variants), φ(prime),
DIVINITY and FIRFUMFERENFE. The best log LR is **+4.63**, below the pass mark of +30. A 256-rune planted
plaintext under the right φ key scores +106.28 in `test_positive_control_runes`.

**Signature calibration.** The OpenPGP header-and-length check does not validate packet contents. In the
deterministic calibration in `test_pgp_header_check` (seed 1), it passes **4 of 20,000 random 256-byte blocks**,
an empirical rate of 0.020 %, or about 0.014 expected hits over 72 readings. No grid reading passes that check.

**Historical prefix results.** The original 184-byte run gave 44.0 % best printable output and −4.8 best rune
log LR; no candidate passed. Its separate 184-byte OpenPGP calibration gave 33 / 20,000 hits (0.165 %).
These describe the old prefix and must not be treated as full-grid results. The historical construction is
`tools/run_stage_n.py` and `tests/test_grid.py` at the pre-correction baseline `a7ab786`.

**Scope.** No candidate in this finite set of byte/rune readings passes the declared criteria. This does not
exclude other keys, key offsets, transformations, ciphers, plaintext distributions or layers, and it yields
neither a plaintext nor a proof of the grid's intended purpose.

## 14. The re-keying is not "skip to the next key value" (2026-10-01, TODO stage O)

Rule declared in `TODO.md` before the run. Function: `leak.skip_next_llr`. Tests: `tests/test_leak.py` (`TestC14SkipNext`).

**Argument.** By C8, a skip-next rule keeps a would-be doublet only when k_{j+1} = k_j. A 19 % survival rate then
means the key repeats adjacent values about 19 % of the time. At those ordinary positions Δc = Δp, so the Δc
histogram over bins 1–28 becomes P1(e) ∝ 0.19 · P(Δp = e) + 0.81/28 · (1 − P(Δp = e)). That carries the shape
of English bigram differences. The flat alternative is that the replacement is independent of the next key
value. Power, computed before the plan: expected χ² excess +47, directional LLR about ±23.

**C14 result: LLR(H1 : flat) = −21.3**, against the declared exclusion line of −10. *Not blind on the data:* L1's
undirected χ² (41.2 on 27 df) had been seen, but not this directional statistic.

| Check | LLR |
|---|---|
| LP2, Δp model from all solved plaintext | **−21.3** |
| LP2, Δp model from disjoint halves of the solved text | −31.7 / −20.0 |
| Control: skip-next, key repeating 19 %, LP2-sized (in-sample model) | +34.8 / +39.7 / +34.0 |
| Control: same, out-of-sample model | +11.0 / +7.2 / +10.6 / +29.0 (weaker, never negative) |
| Control: fresh re-key, flat key | −13.1 / −28.0 / −31.6 |

A by-product: a skip-next rule with a 19 %-repeating key reproduces LP2's doublet rate *by itself*
(0.70–0.76 %, with no "keep" probability). That makes it an attractive mechanism, but the Δc histogram rules
it out.

**Consequence.** If the deficit comes from re-keying, the replacement value is independent of the next key value:
a fresh draw, a second key, or a value from some other source. The other reading still stands: a check applied by
hand that misses about 1 doublet in 5.

## 15. Consolidation: C3 as a test, homophonic substitution, and two errata (2026-10-01, TODO stage Q)

Rules declared in `TODO.md` before the run. Functions: `leak.doublet_classes`, `leak.marker_letter_llr`,
`leak.poisson_cdf`, `stats.homophonic_min_chi2`. Tests: `tests/test_leak.py` (`TestC3MarkerLetter`) and
`tests/test_stats.py` (`TestHomophonic`, and the fingerprint numbers of tracker §3.2 that had no test before).

**C3, re-derived** (not blind: the 2026-09 one-off result had been seen). Under M_x, c_i = c_{i−1} + (p_i − x)·k_i
with k_i ≠ 0, a doublet sits exactly where p_i = x, with no leak. So the 86 doublets would be x's count, at x's
places in words. Rules: x is excluded if the count is off (two-sided Poisson p < 10⁻⁶, rate from the 2,901 solved
plaintext runes) or if the doublets' word positions (initial 23, medial 44, final 19, sole 0) are not x's
(LLR ≤ −10, with P(x | class) shrunk toward f_x by 10 pseudo-counts).

| Letters | Rule that excludes them | Value |
|---|---|---|
| AE, EO, OE | count | never in the plaintext, so M_x predicts 0 doublets |
| 23 others | count | p ≤ 1.5 × 10⁻¹⁰ (B, the closest) |
| NG (λ = 138), IA (71), EA (80) | position | LLR −106.4, −149.4, −67.7 |

Power: on the solved text enciphered under M_x itself, NG, IA and EA each score ≥ +10. On 86 random positions of
the same text they score ≤ −10. **C3 holds for all 29 letters.**

**C15: no homophonic substitution.** A homophonic cipher gives each plaintext letter its own set of cipher runes.
The solved plaintext uses 26 letters, so only 3 of the 29 runes are spare. The least χ² of the expected counts
against flat, over every way to hand out the spares (all 3,654, including leaving runes unused), is **4,802**. The
best case gives E three runes and O two. Rare letters decide it: J (3 of 2,901) and X (5) would each own a rune
that LP2 uses about 447 times. With letter rates padded by +1 it is still about 4,710. LP2's observed χ² is 26.4. The
declared line was 200. This covers homophonic substitution alone; with a flat stream added on top, the stream
decides (catalog row 3).

**Errata, both in §2 and both corrected there.** Neither changes a verdict.
- C3 said x = F predicts "about 75" doublets at the end of 2-rune words. That does not reproduce: LP2's 448 two-rune
  words × 10 / 178 (the share of solved 2-rune words that end in F) gives **25.2**. Observed: 1.
- C7 said a per-word shift leaves "2.6 %" doublets inside words. The solved plaintext gives **52 / 2,175 = 2.39 %**.
  Against LP2's 63 / 10,060 that is z = −11.6.

## 16. Cicada's own numbers and OutGuess payloads are not the key, from any phase (2026-10-01, TODO stage R)

Declared in `TODO.md` and committed (`2c209dc`) before any LP2 decode. Run: `python -m tools.run_stage_r` (about
1 hour on 16 cores), rows in [`stage_r_candidates.tsv`](stage_r_candidates.tsv), controls in
[`stage_r_controls.tsv`](stage_r_controls.tsv). Tests: `tests/test_detect.py` (`TestStageRCicadaNumbers`, and
`test_fast_detector_equals_the_reference`).

**What is new.** Each source is read **cyclically from an unknown phase**, and the phase is not searched.
`detect.log_lr(starts=…)` puts a uniform prior on every start, so one decode is the mean LR over all phases. It
keeps the e^−30 bound per decode and costs at most log 58,152 ≈ 11 nats of power. This covers short sources used
as a repeating key under drift (C9 reaches only periods ≤ 25 there) and long payloads read from any offset. The
ledger ran OutGuess payloads in fixed sync only. `tools/lpcore/fastdetect.py` is a numpy version of the same
forward pass, about 5× faster, and is tested equal to `detect.log_lr`.

**Family.** 25 sources × 2 mappings (`mod` = v mod 29; `reject` = drop v ≥ 29·⌊V/29⌋ first, as a careful pad
generator would) × 3 modes × 29 shifts × 10 alignments (9 sections, LP2 continuous) = **43,500 decodes**, with a
false-positive bound of 4.1 × 10⁻⁹.

| Source | Values | Provenance (tier) |
|---|---|---|
| 2012 P.S. number, digit pairs (2 phases) and triples (3 phases) | 131 digits → 43–65 | `community_research.md` §2b (community) |
| The same with a trailing `1` (132 digits) | 43–66 | archived tracker §9.5; unresolved, so both ran |
| 2014 RSA modulus n, pairs and triples | 130 digits → 42–65 | `people_2014.md`, OutGuess of 1033.jpg (community) |
| Onion cookies 167 and 761 | 32 bytes each | `community_research.md` §2c (community) |
| AN END hash | 64 bytes | `keys.an_end_hash` (canonical) |
| `page_00.txt` signed hex | 991 bytes | `data/outguess/` |
| 2014 second-onion hex ("Patience is a virtue") | 256 bytes | `people_2014.md` (community) |
| Wisdom/folly hint, forward and reversed | 3,368 bytes | `data/outguess/`; `wisdom_hint` = `folly_hint`, and `folly_rev_hint` is its exact reverse |
| `page_17.bin`, `page_21.bin`, `page_43.bin` | 58,152 bytes each | `data/outguess/` |

Some 132-digit variants equal their 131-digit ones, because the extra digit never enters a group. They were run
anyway as declared, which only makes the bound more conservative.

**Result: nothing passes.**

| Check | Value |
|---|---|
| Positive controls (solved text enciphered by each key, keep 0.19, fresh and next re-key, 729 and 3,316 runes) | 200 of 200 ≥ 30; least **+169.1** |
| Negative controls (same ciphertext, random key of the same length) | 200 of 200 < 30; greatest −60.9 |
| Best decode on a real section | **−50.8** (`page_17.bin` mod, section 7, beaufort, shift 18) |
| Best decode on LP2 continuous | −1,479.7 |
| Best decode overall | +2.4, on the 9-rune section 10 (no power) |

Every source's best on a real section lies between −50.8 and −77.2.

**Reading.** None of the payloads on disk, and none of Cicada's published numbers in pair, triple or byte form,
is an additive LP2 key. That holds under any mode, shift or start phase, with drift, and per section or
continuous. This closes tracker §1 item 1 for the material in the repo. Not covered: other mappings of these
numbers (base conversion, factors, hashes), OutGuess output from scans the repo does not hold (community
`lp_outguessed/`), and any non-additive use (the label-free detector in tracker §1).

## 17. Per-position alphabets c = σ_{k_i}(p): the label-free test is void (2026-10-01, TODO stage S)

Declared in `TODO.md` and committed (`8c93b22`) before any LP2 decode. Detector: `tools/lpcore/alphabets.py`. Run:
`python -m tools.run_stage_s` (about 10 minutes on 8 workers), rows in [`stage_s_candidates.tsv`](stage_s_candidates.tsv)
and [`stage_s_controls.tsv`](stage_s_controls.tsv). Tests: `tests/test_alphabets.py`.

**The question.** Suppose each key value v picks its own secret alphabet σ_v, so c_i = σ_{k_i}(p_i). That covers
mixed-alphabet tabulae, a running key with a secret tabula, and the additive case. The labelled detector cannot see
it, because it scores plaintext letters. Inside one key class, though, the cipher repeats as often as the plaintext
does (Σq² = 0.0622 instead of 1/29), whatever σ_v is.

**The detector works.** Per key phase, the score is a Dirichlet-multinomial likelihood ratio against a uniform
cipher, with α = 1.165 matched to the plaintext's coincidence rate (`alphabets.dm_alpha`). Its mean over every
phase keeps the e^−30 bound. Tests pin four properties:
- an exact mean LR of 1 under a uniform cipher (`test_mean_lr_under_a_uniform_cipher_is_one`);
- FFT counts equal to direct counts (`test_fft_counts_equal_direct_counts`);
- power in step at 729 runes, finding the true phase (`test_mod_29_classes_at_729_runes`);
- no power at 1 % desync (`test_one_percent_desync_kills_the_signal`).

**What holds (C9, extended).** A σ key of period P that stays in step gives positions i and i + P the same alphabet.
So the lag-P repeat rate is Σq² whatever σ is, and C9's scan sees it. A synthetic check at periods 500 and 1000 is
flagged below the Bonferroni line (`test_sigma_periodic_keys_are_flagged_at_their_period`). With C9 on LP2, that
excludes **every per-position-alphabet cipher whose key has period ≤ 1000 and stays in step**. That covers the
short named sources (the cookies, the AN END hash, the 256-byte grid, `page_00`, the second onion, the P.S. and RSA
digit groups, the solved text's word sums) under any σ.

**What does not hold: the run on the long named keys is void.** The family was 20 key classings × 10 alignments: the
primes mod 29, the solved plaintext, the hint, the three `.bin` payloads and four English corpora as letter classes.
It ran twice, and both runs are void by the rule declared first (a negative control at or above 30 voids the run).
| Run | Void because | Real-data nulls (shuffled key on LP2) | LP2 decodes |
|---|---|---|---|
| 1 | 4 negative controls at +904 … +1,104. The control text (the 2,901-rune plaintext, tiled) and the plaintext keys share period 2,901, so the control cipher repeats at that lag 96.8 % of the time. LP2 at lag 2,901: 328 / 10,055 | all ≤ −489.5 | best +0.84 |
| 2 | 1 negative control at +53.5 (Liber AL letters, 12,956 runes) | all ≤ −489.5 | identical to run 1, byte for byte |

**Diagnosis of run 2.** A cipher made with random σ_v over a few dozen key classes is **not flat**. The control
ciphers have χ² = 1,141 (Liber AL letters) and 355.6 (`page_17.bin` mod 29) on 28 df, where LP2 has 26.4 (C2). A DM
score against a uniform cipher rewards any lumping of an uneven cipher, so the synthetic "negative" controls were
never nulls. On the real, flat ciphertext the null behaves: every shuffled key scores ≤ −489.5. No LP2 decode reached
30 (best +0.84). Under the declared rules, though, the run **excludes nothing**. The decodes were seen before the
controls were fixed, so they can't be promoted to a result now.

**What this suggests (not yet a result).** The same uneven marginal that broke the controls is a key-independent
handle. Random σ_v over V roughly equal classes gives an expected χ² excess of about n·(29·Σq² − 1)/V ≈ 10,400 / V
at LP2's length. For LP2's χ² of 26.4 that needs hundreds of effective classes, unless the σ_v are structured so that
their mixture is flat (additive and Quagmire alphabets are, under a flat key). That is a constraint, written as a
prediction. It needs its own declared stage before it can enter the register.

