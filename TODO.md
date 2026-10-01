# TODO — Liber Primus

The working plan. **Write a plan here before the first edit** (AGENTS.md): goal, approach, rejected
alternatives, what you're *not* doing, blast radius, rollback. When a stage is done, collapse it to one line
under "Done" with its commits. The full text stays in git history. Status and next research steps live in
[`MASTER_TRACKER.md`](MASTER_TRACKER.md) §1, not here.

---

## Active

### H — characterise the doublet leak (MASTER_TRACKER §1 item 1)

**Goal.** 86 of ~447 would-be doublets survive (≈ 19 %). Find what separates the survivors, and test the
community key-switch scheme ([`Algorithm.png`](reference/community/images/Algorithm.png)) as the mechanism.

**Approach.** New module `tools/lpcore/leak.py` and new tests in `tests/test_leak.py`. Only deterministic counts on canonical
data. Pairs never cross a segment boundary (as in `stats.lag_repeats`). The "LP2 stream" is the 9 unsolved segments.
Predictions and pass/fail thresholds are declared here **before** the run:

| # | Test | Prediction (declared before the run) | Verdict rule |
|---|---|---|---|
| L1 | Where did the ≈ 361 suppressed doublets go? Histogram of Δc = c[i+1] − c[i] mod 29, d = 1..28 | Retry with a fresh key → spread evenly, ≈ 459 per bin. A "nudge" rule (c ± 1) → one or two bins inflated by ≈ 180–361 | "Nudge" if any bin has z ≥ 3.5 against the even-spread expectation; otherwise "spread evenly" |
| L2 | Survivor rate on pairs that straddle a line break vs pairs within a line | Rule checked only within a written line → straddling pairs show ≈ 3.45 %. Global rule → ≈ 0.66 % on both | "Per-line rule" if straddling rate ≥ 2.5 % **and** one-sided binomial p < 0.01 against the within-line rate. Page breaks reported only (≈ 55 pairs, too few to decide) |
| L3 | Periodicity: survivor count by phase (position mod m), m = 2..32, phase taken within the segment and along the continuous LP2 stream | "Every m-th pair unchecked" → all survivors in one phase. Hand error → no period | Significant if the union-bound p (m · P[Binom(n, 1/m) ≥ max cell]) < 0.01 / 62 (Bonferroni over 31 m × 2 indexings) |
| L4 | Clustering and homogeneity: survivor counts per section (promotes C6 to a test) and the index of dispersion in windows of 500 pairs | Random leak → per-section χ² p > 0.01 and dispersion ≈ 1 | "Inhomogeneous" if χ² p < 0.01 or the dispersion falls outside [0.5, 2.0] |
| L5 | Key-switch. (a) Idealised: when key 1 would repeat the last *emitted* rune, use key 2 for this rune and keep the result even if it also repeats. (b) The picture's literal code (it compares key-1 values and switches the *earlier* rune). Both are encrypted over the solved LP1 plaintext and key pairs {DIVINITY, CIRCUMFERENCES}, {φ(prime), prime values} | (a) survival ≈ 1/29, so ≈ 15 doublets expected per 12,947 pairs. (b) about 2/841 ≈ 0.24 %, not the 0.69 % claimed in the picture | Key-switch is **refuted** as the mechanism if every simulated rate gives Poisson P(X ≥ 86 \| 12,947 pairs) < 10⁻⁶ |

**Rejected.** Fitting a survival probability or a second key to make the count match: that is an optimiser.
Simulating with random keys from an unseeded PRNG: not reproducible. Deterministic key streams are used instead.

**Not doing.** Any decryption attempt. Changes to `corpus.py` or other core modules. Rune positions per line are derived
inside `leak.py` from `Page.raw`, and a test checks they agree with `Corpus.all_runes()`.

**Blast radius.** Two new files and edits to the docs (findings §7, tracker §1/§3/§4). **Rollback:** `git revert` the commit.

**Result (2026-10-01).** Run as declared; all verdicts in findings §7. L1 spread evenly (max |z| 2.58). L2 not per-line
(0.68 % vs 0.66 %). L3 no period (best p 0.036). L4 homogeneous (χ² p 0.72, dispersion 1.02). L5 refuted
(λ 27 and 45; P ≤ 3 × 10⁻⁸). The φ(prime)/primes pair was degenerate (key 2 = key 1 + 1), which gives 0 survivors.

## Owner items

- [ ] **Tokens in `.claude/mcp.vscode-reference.json`** (GitHub PAT, mem0, context7) are plaintext. They were never
  committed or pushed (full-history scan on 2026-09-29), so rotating them is optional. Consider VS Code `inputs`
  (`promptString`, `password: true`) instead of hardcoding them.

---

## Done

| Date | Stage | Result | Commits |
|---|---|---|---|
| 2026-10-01 | **H** characterise the doublet leak | Predictions L1–L5 declared here, then run. Survivors are random at a constant ≈ 19 % (no nudge, no per-line check, no period, no clustering; C6 now a test). Key-switch refuted. New exact constraint C8 → findings §7. `tools/lpcore/leak.py`, `tests/test_leak.py` | this commit |
| 2026-10-01 | **G** organise for clarity | `.gitattributes` (LF). `reference/` split into findings/sources/community/archive; `data/` split into canonical/corpora/outguess/archive, each with a README. Duplicate `key_search_corpus.txt` removed. Tracker rewritten as resume-here; old one archived verbatim. README rewritten | `d008cb2` `fe7588b` `8b143c1` + this |
| 2026-10-01 | **F** remove other-project material | `.agent/` (mcMMO memory), Ko-fi `FUNDING.yml`, mcMMO workflows deleted (identical copies in `../mcMMO-Singleplayer`). AGENTS.md rewritten for LP | `f5ca9a1` |
| 2026-09-29 | **E** archive legacy | 107 scripts → `tools/legacy/`; outputs → `data/archive/hillclimbers/20260529/` (`MOVES.txt` lists all 301 moves for reversal) | `50889e8` |
| 2026-09-29 | **D** logic-only analysis | Constraints C1–C7, scan-32 square decoded, 2026 web check → `reference/findings/`, `reference/community/community_research.md` | `f038274` `a85c106` |
| 2026-09-29 | **C** tracker correction | Invalid claims identified (now MASTER_TRACKER §4.3) | `a85c106` |
| 2026-09-29 | **B** canonical corpus | rtkd/iddqd master vendored; `tools/lpcore` + tests; 150 page files rebuilt from it | `f038274` |
| 2026-09-29 | **A** push safety | Tokens and foreign material git-ignored. History scanned: no secret ever committed | `f5ca9a1` |

Rollback for any stage: `git revert <commit>`. Untracked archive moves are reversed with `MOVES.txt`.
