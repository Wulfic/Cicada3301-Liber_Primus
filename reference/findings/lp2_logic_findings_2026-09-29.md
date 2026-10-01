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
2. **Key-source riddles not in either community ledger.** Only the new ones are worth
   testing: the scan-32 prime spiral as an ordinal stream; values of the solved text's words
   ("their numbers are the direction", 2016). Each must be one deterministic decryption with
   a pre-declared pass threshold. The skip-aware decode must be exact inference, not an optimiser.
3. **Section titles** are short, structured, and one of them is "A" + 9 runes. Crib ideas must
   state their prediction for the *key* fragment (e.g. "reads as English" for a running key)
   before running.

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
