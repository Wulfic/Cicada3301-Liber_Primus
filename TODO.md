# TODO — Liber Primus

The working plan. **Write a plan here before the first edit** (AGENTS.md): goal, approach, rejected
alternatives, what you're *not* doing, blast radius, rollback. When a stage is done, collapse it to one line
under "Done" with its commits. The full text stays in git history. Status and next research steps live in
[`MASTER_TRACKER.md`](MASTER_TRACKER.md) §1, not here.

---

## Active

### K — ciphertext-selected alphabets (started 2026-10-01)

**Goal.** Tracker §1 item 1. C11 excludes c_i = p_i ± c_{i−L}. Generalise it to every cipher in which an earlier
cipher rune chooses the alphabet: c_i = σ_{c_{i−L}}(p_i) for any 29 secret permutations σ_x. This includes keyed
autokeys with a secret table, c_i = p_i + f(c_{i−1}), and affine chains.

**Why it is testable without a key.** In the lag-L transition table, row x is P(c_i = y | c_{i−L} = x) =
q(σ_x⁻¹(y)), a permutation of English. Its IoC is IoC(q) ≈ 1.79 whatever σ is. Under the null every row is flat.

**Test (C12).**
- For L = 1…1000: count (c_{i−L}, c_i) pairs within sections. Drop the diagonal cells (y = x), because the
  doublet rule acts there at L = 1; drop them at every lag for consistency.
- Expected count E_xy = R_x · f_y / (1 − f_x), where R_x is the row's off-diagonal total and f the pooled
  frequencies. Statistic: Pearson χ² over the 29 × 28 cells, df = 29 × 27 = 783. p from the Wilson–Hilferty
  approximation.
- **Declared rule:** a lag is flagged if p < 0.01 / 1000. Prediction: nothing is flagged.
- **Calibration (negative control):** random i.i.d. streams of LP2's section sizes give about 1 % of lags with
  p < 0.01 (allowed 0–3 %), and none flagged.
- **Positive control:** a synthetic c_i = σ_{c_{i−L}}(p_i) with seeded random σ tables, at L = 1 and L = 500
  (solved plaintext, LP2-sized), must be flagged.
- If nothing is flagged: C12 subsumes C11, and it also covers the lag-1 sum, which neither L1 nor C11 tested.

**What it does NOT exclude (state it in the doc).** The same construction with a flat stream key on top,
c_i = σ_{c_{i−L}}(p_i + k_i): its rows are flat. Alphabets chosen by plaintext runes (a mixture, and weaker).
Contexts of two or more runes (841 rows of about 15 entries each are too sparse for χ²).

**Rejected.** An order-2 coincidence statistic: it needs a variance formula checked by simulation, and it is
low priority. Deferred, not done.

**Blast radius.** `tools/lpcore/stats.py` (one function), `tests/test_keyspace.py`, docs. **Rollback:** `git revert`.

## Owner items

- [ ] **Tokens in `.claude/mcp.vscode-reference.json`** (GitHub PAT, mem0, context7) are plaintext. They were never
  committed or pushed (full-history scan on 2026-09-29), so rotating them is optional. Consider VS Code `inputs`
  (`promptString`, `password: true`) instead of hardcoding them.

---

## Done

| Date | Stage | Result | Commits |
|---|---|---|---|
| 2026-10-01 | **J** key statistics | Rules declared first. C10: no English running key from any text, in 3 mappings × 3 modes × 29 offsets (LLR −255…−333; still excluded at λ = 0.25). C11: no ciphertext autokey at lags 2–1000 (best p 5.6e-4 vs 5e-6). Title cribs closed as untestable. → findings §9, `tests/test_keyspace.py` | `b1fa1bb` + this |
| 2026-10-01 | **I** key-source riddles | Plan, thresholds and candidate list declared first. Drift-tolerant detector (`detect.py`, forward algorithm, bound e^−30). Controls pass except AN END (85 runes, 29.6 < 30: too short, recorded). C9: no periodic key (lags 11–1000). 2,610 decodes of primes / word sums / plaintext values all fail (best −65 nats on a real section). Segment 10 title not decoded by the square. → findings §8. `tools/run_stage_i.py`, `tests/test_detect.py` | `8641c50` `3720710` |
| 2026-10-01 | **H** characterise the doublet leak | Predictions L1–L5 declared here, then run. Survivors are random at a constant ≈ 19 % (no nudge, no per-line check, no period, no clustering; C6 now a test). Key-switch refuted. New exact constraint C8 → findings §7. `tools/lpcore/leak.py`, `tests/test_leak.py` | `d66cbb2` |
| 2026-10-01 | **G** organise for clarity | `.gitattributes` (LF). `reference/` split into findings/sources/community/archive; `data/` split into canonical/corpora/outguess/archive, each with a README. Duplicate `key_search_corpus.txt` removed. Tracker rewritten as resume-here; old one archived verbatim. README rewritten | `d008cb2` `fe7588b` `8b143c1` + this |
| 2026-10-01 | **F** remove other-project material | `.agent/` (mcMMO memory), Ko-fi `FUNDING.yml`, mcMMO workflows deleted (identical copies in `../mcMMO-Singleplayer`). AGENTS.md rewritten for LP | `f5ca9a1` |
| 2026-09-29 | **E** archive legacy | 107 scripts → `tools/legacy/`; outputs → `data/archive/hillclimbers/20260529/` (`MOVES.txt` lists all 301 moves for reversal) | `50889e8` |
| 2026-09-29 | **D** logic-only analysis | Constraints C1–C7, scan-32 square decoded, 2026 web check → `reference/findings/`, `reference/community/community_research.md` | `f038274` `a85c106` |
| 2026-09-29 | **C** tracker correction | Invalid claims identified (now MASTER_TRACKER §4.3) | `a85c106` |
| 2026-09-29 | **B** canonical corpus | rtkd/iddqd master vendored; `tools/lpcore` + tests; 150 page files rebuilt from it | `f038274` |
| 2026-09-29 | **A** push safety | Tokens and foreign material git-ignored. History scanned: no secret ever committed | `f5ca9a1` |

Rollback for any stage: `git revert <commit>`. Untracked archive moves are reversed with `MOVES.txt`.
