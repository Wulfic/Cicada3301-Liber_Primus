---
name: lp-attack
description: "Codebreaking protocol for the unsolved Liber Primus: turn an idea into ONE declared, deterministic hypothesis test with a pre-registered threshold, positive and negative controls, the right lpcore detector, and a recorded result. Use when: proposing a key source, cipher family, anti-doublet mechanism, or decoding of the grid/OutGuess data; planning the next research stage; choosing a statistic; or writing a tools/run_stage_*.py runner. Never use an optimiser."
argument-hint: "The hypothesis (e.g. 'the 2012 P.S. number in two-digit groups is the LP2 key')"
---

# LP Attack: One Declared Test, Run Once, Recorded Either Way

The cipher is OTP-class (tracker §1). A search that "finds" English in it is almost certainly finding the search's
own degrees of freedom. A result only counts if the following hold, in this order:
**the model is written down → the exclusion list doesn't already kill it → the detector has power on a synthetic
control → the threshold is declared → it is run once → the outcome is recorded.**

Load `lp-expert` first if you don't already have the current constraint list in context.

## Hard rules (AGENTS.md, owner directives)

- **No optimisers.** No hill-climbing, simulated annealing, GA, beam search over keys, or "try variants until one
  scores". Their output is not evidence. Enumerating a *declared, finite* family (modes × shifts × alignments)
  is allowed. That makes it a family of hypotheses, and its size enters the false-positive bound.
- **Runes come only through `tools/lpcore/corpus.py`** (`load_corpus().segment_runes(s)`). Never use
  `pages/*/runes.txt`, the transcript, or runes pasted from the web.
- **Every decoder tolerates desync.** About 19 % of would-be doublets leak, and the rest are re-keyed. If the
  re-keying consumes key values, a fixed-sync decode of the right key looks like noise. Use `detect.log_lr`, not
  `fixed_sync_log_lr`, for any key-stream test.

## The protocol

### 1. Write the model as an equation

`c_i = f(p_i, k_j, state)`. Name every part: the key source (exact file, URL or definition), its mapping to
values mod 29, the mode (sub `c−k`, add `c+k`, beaufort `k−c`), the alignment (which segment, which offset),
and the re-key rule. **If you can't write the equation, you have a theme, not a hypothesis.** Examples of themes:
"instar", "the spiral", "Cicada loves primes".

### 2. Check exclusions: stop early if it is dead

Read `attack-catalog.md` (next to this file), the findings §0 constraint register (every C/L number with its
test), then tracker §4 and `lp-expert/lore.md`. If a constraint already
excludes the family, report **which C-number does it and why it applies**, then stop. Watch for disguised
repeats:

- A "progressive" or "polynomial-in-i" key mod 29 is periodic (f(i + 29) ≡ f(i)), so C9 excludes it when the
  key stays in step. Under a drifting re-key rule, C9 only covers periods ≤ 25 (see the catalog's periodicity note).
- A two-layer additive cipher is one additive cipher with key k₁ + k₂. C4, C9, C10 and C13 constrain the *sum*.
  A correct k₁ scored alone fails if k₂ exists. State that limit in the plan rather than claiming exclusion.
- Any key built from English text is excluded under every mapping C10 covers (letters, prime values, φ).
- A transposition before an additive stream changes nothing for `detect.log_lr`: its unigram emissions ignore
  plaintext order.

### 3. Look for a key-independent kill first

Can a statistic of the ciphertext alone falsify the whole family, for *every* key? (C4, C10, C12 and C13 are
of this kind.) That beats testing named keys one at a time, because it covers infinitely many keys at once.
Derive the statistic's predicted value **from the model and the solved plaintext, before looking at LP2**.

### 4. Pick the detector

| Hypothesis shape | Tool (`tools/lpcore/`) | Power note |
|---|---|---|
| Named key stream, additive | `detect.log_lr(cipher, key, q, mode=, shift=, start=)`, `detect.THRESHOLD` = 30 nats | needs ≳ 100 runes in step; seg 10 (9 runes) has no power |
| Key *alphabet* or mapping, no specific source | `stats.cipher_distribution`, `stats.values_distribution`, `stats.unigram_llr` | power is gone for alphabets of about 60 symbols or more (C13: bytes, 00–99, base 60) |
| English-like key, any text | `stats.running_key_distribution` | already C10 |
| Ciphertext feedback or alphabet chosen by c_{i−L} | `stats.transition_chi2`, `stats.lag_combination_chi2` | already C11, C12; flat key on top is **not** covered |
| Periodic or reused key | `stats.lag_scan`, `stats.lag_repeats` | C5, C9 |
| Anti-doublet mechanism | `leak.adjacent_pairs`, `delta_counts`, `phase_test`, `section_chi2`, `dispersion_index`, `skip_next_llr`; `stats.predicted_doublet_rate` | must reproduce L1–L4 and the ≈ 19 % survival from its own definition |
| Byte payloads (grid, OutGuess, hashes) | patterns in `tools/run_stage_n.py`, `tests/test_grid.py` | chance rates **simulated**, never eyeballed |
| Per-position alphabets c = σ_{k_i}(p) | `alphabets.log_mean_lr` (in step); `flatness.random_tabula_p` (key-free, any alignment) | random tabulae with ≤ 153 classes are already C16. The in-step detector needs **flat** synthetic negatives (stage S was void without them). Latin-square tabulae are flat, so flatness cannot see them |

Plaintext model `q`: `detect.unigram(...)` over `keys.solved_plaintext_words(corpus, load_translation())`.
If the hypothesis was inspired by LP2 statistics, build models from held-out solved text (as C14 did).

### 5. Prove power with controls before touching LP2

- **Positive control:** encrypt solved plaintext with the hypothesised key and rule, using
  `keys.encrypt_dodging(plain, key, keep=0.19, seed=…, rekey="next" | "fresh")`, at LP2 section sizes. The
  detector must pass it with margin.
- **Negative control:** the same pipeline on `keys.random_key(n, seed)` and on a wrong but plausible key. It must
  stay below the threshold.
- **If the positive control fails, the hypothesis is "untestable this way".** Record that and stop. Don't loosen
  the threshold until it passes.

### 6. Declare in `TODO.md` before the run

Use the next stage letter. Fields that must be filled:

```markdown
### <Letter> — <name> (YYYY-MM-DD)
**Model:** c_i = …  (source, mapping, modes, alignments, re-key rule)
**Not already excluded because:** … (cite the C-numbers checked)
**Family size N:** modes × shifts × alignments × variants = …  → false-positive bound N·e^−30 (or Bonferroni α/N)
**Pass:** … · **Exclude:** … · **Inconclusive:** … (numbers, written now)
**Expected if true:** … (from the positive control) · **Expected if false:** … (negative control)
**Controls:** positive …, negative …
**Not doing:** … · **Blast radius:** additive only (new runner + TSV + test) · **Rollback:** git revert <commit>
```

### 7. Run once, deterministically

Write `tools/run_stage_<x>.py`, modelled on `tools/run_stage_i.py`. Include `logging`, fixed seeds, a `--quick`
flag, and one TSV row per decode in `reference/findings/stage_<x>_*.tsv`. Write the TSV with `newline="\n"`.
Run it as `python -m tools.run_stage_<x>`. **After you see the result, nothing in the declared family may change.**
A new variant is a new declared hypothesis, and it adds to the family count.

### 8. Record the outcome, whether it passed or failed

- Findings doc: a new numbered section with the declared rule, the result table, controls, and a "Reading".
- Findings §0 register: a row for a new constraint (C or L number), with its test. `tests/test_docs.py` fails if a
  C-number in the tracker has no row, or if any doc cites a test, path or `lpcore` name that does not exist.
- `MASTER_TRACKER.md`: §3.2 for a new constraint, §4.2 for an exclusion, a §7 log row, and §1 if the next
  actions changed.
- `TODO.md`: collapse the stage to one "Done" row with its commits.
- `tests/`: a fast test that pins the headline number and fails if it drifts.
- Every number you cite must be reproduced by that test or by the runner.

## Statistical hygiene

- `log_lr` ≥ T has P ≤ e^−T per hypothesis under the null (Markov, no calibration needed). A family of N decodes
  has a bound of N·e^−T. Keep T = 30 unless the plan says otherwise, and says why.
- χ²-type families get a Bonferroni threshold that is declared before the run (C9 and C11 used about 10⁻⁵).
- **Simulate every chance rate** with a seeded test (gotcha: the PGP-header rate was guessed at 10⁻⁴; it is 0.17 %).
- Never fit and score on the same runes. Never pick the best of K variants and then report it as one test.
- An "almost English" output under ~100 runes means nothing. Score it, don't read it.
- A negative result on a real alignment with a passing positive control is a **result**. Write it up as one.

## Instant-reject list

Free per-position keys, or any key with as many free values as the runes it explains. Crib dragging that yields
"a patterned key fragment" (cribs are untestable without a key model, findings §9). Thresholds set after the run.
Silently dropped variants. Fixed-sync-only decodes. Runes from page files. Numerology without a falsifiable
prediction. "It's close, let me tweak the shift" (that tweak is an optimiser).
