# TODO — Liber Primus

The working plan. **Write a plan here before the first edit** (AGENTS.md): goal, approach, rejected
alternatives, what you're *not* doing, blast radius, rollback. When a stage is done, collapse it to one line
under "Done" with its commits. The full text stays in git history. Status and next research steps live in
[`MASTER_TRACKER.md`](MASTER_TRACKER.md) §1, not here.

---

## Active

### I — key-source riddles, tested with a drift-tolerant detector (started 2026-10-01)

**Goal.** Run tracker §1 item 1 (findings §6.2): test the riddle-derived key sources that neither community
ledger covers. Each is a deterministic decode with a threshold declared here before the run.

**Why a new detector.** The anti-doublet rule re-keys about 2.8 % of positions (C8). If the rule consumes key
values, the key drifts out of step with the cipher. A naive decode then loses sync within about 36 runes, so a
right key can look wrong. The Leo-Y-Zhang ledger decodes sequences with fixed sync, F-interrupts at most.

**Approach.**
1. `tools/lpcore/detect.py`: a forward algorithm (an exact sum, not a max) over the key index j used at each cipher
   position. Each step moves j by +1 (prob. 1 − 2ρ), +2 (a skipped key value, ρ) or 0 (a stalled key, e.g. an
   interrupter, ρ), with ρ = 0.02. The emission ratio is r = (1 − ε)·29·q(p) + ε, with ε = 0.1, where q is the LP
   plaintext unigram (from the solved sections, add-one smoothed) and p is the decoded rune. The output is
   log LR = log Σ_paths Π r. Pruning states below 1e-12 of the maximum only drops positive terms.
   - **Why unigram:** it is blind to a transposition of the plaintext, so it still detects the right key if the
     plaintext was scrambled before encryption.
   - **Null bound (exact, no calibration):** if the decode is uniform and i.i.d., E[r] = 1 at every step, so
     E[LR] = 1. Markov's inequality then gives P(log LR ≥ T) ≤ e^−T per hypothesis, and pruning only lowers LR.
2. **Declared threshold: T = 30 nats** on any one decode. For a family of M hypotheses the false-positive bound is
   M·e^−30 (≈ 10^−9 for M = 10^4).
3. **Controls, which must pass before the candidates run:**
   - (+) segment 1 with DIVINITY, segment 5 with FIRFUMFERENFE, segment 16 with φ(prime): log LR ≥ T, including with
     q built without that segment.
   - (+) synthetic: LP plaintext encrypted with φ(prime) under the rule "on a would-be doublet use the next key
     value, keep the doublet 19 % of the time". The right key gives log LR ≥ T and a naive fixed-sync decode does not.
   - (−) 20 seeded random keys on every LP2 section give log LR < T. A wrong solved key (DIVINITY on segment 5) gives
     log LR < T.
4. **C9, key-independent (periodic keys).** Measure lag-m repeat rates for m = 11…1000 within sections. A period-m
   key without drift raises lag m from 3.45 % to about 6 %. Prediction: no lag exceeds the Bonferroni threshold
   (one-sided p < 0.01 / 990). A positive control (a period-16 key with the drifting rule) must be detected.
   If C9 holds, it also excludes every periodic source: the square's 16 values, Fibonacci/Lucas mod 29 (Pisano
   period 14), and short keywords.
5. **Candidate family (declared now; every result recorded).** Each runs in modes sub / add / beaufort, with
   constant shifts a = 0…28, either restarting at each section or continuous through LP2:
   - **K-A primes p(n).** With the shift, this also covers p ± 1, φ(p) = p − 1 (AN END's stream, continued) and
     3301 − p(n) (3301 ≡ 24 mod 29). It is a re-test of ledger items, now drift-aware.
   - **K-C word sums:** the gematria sums of solved-plaintext words in book order, one per cipher rune ("their
     numbers are the direction").
   - **K-D plaintext values:** the prime values of solved-plaintext runes in order (Cicada running key, now drift-aware).
   - **The scan-32 ordinals / Fibonacci-indexed primes** cannot define more than 16 terms (p(F+1) for F > 10⁶ is
     out of reach). As a key they are periodic, so C9 covers them.
   - **Prediction:** all candidates give log LR < 30 (expected: none is the key). PASS means log LR ≥ 30 on any section.
6. **Segment 10 title (9 runes, ᚠᚢᛚᛗ ᚪᛠᚣᛟᚪ), next to the square.** Decode it with the square's own numbers mod 29
   (cell values; primes; ordinals), read inward and outward along the spiral, in 3 modes. PASS = both words decode
   to entries of an English vocabulary V (solved LP plaintext + Emerson + Liber AL words). Before the verdict,
   measure the chance rate of the same check over all 29 × 3 constant keys.

**Rejected.** Viterbi or maximised alignment: it overfits, and its null is unknown. Bigram emissions: stronger,
but they break the transposition blindness and complicate the bound; revisit only if unigram power is too low.
numpy: README promises stdlib only.

**Not doing.** No optimiser. No free-key or crib fitting. No new key texts beyond this list.

**Blast radius.** New files only: `tools/lpcore/detect.py`, `tools/lpcore/keys.py`, `tests/test_detect.py`,
`tools/run_stage_i.py`. Docs: findings §8, tracker. **Rollback:** `git revert`.

## Owner items

- [ ] **Tokens in `.claude/mcp.vscode-reference.json`** (GitHub PAT, mem0, context7) are plaintext. They were never
  committed or pushed (full-history scan on 2026-09-29), so rotating them is optional. Consider VS Code `inputs`
  (`promptString`, `password: true`) instead of hardcoding them.

---

## Done

| Date | Stage | Result | Commits |
|---|---|---|---|
| 2026-10-01 | **H** characterise the doublet leak | Predictions L1–L5 declared here, then run. Survivors are random at a constant ≈ 19 % (no nudge, no per-line check, no period, no clustering; C6 now a test). Key-switch refuted. New exact constraint C8 → findings §7. `tools/lpcore/leak.py`, `tests/test_leak.py` | `d66cbb2` |
| 2026-10-01 | **G** organise for clarity | `.gitattributes` (LF). `reference/` split into findings/sources/community/archive; `data/` split into canonical/corpora/outguess/archive, each with a README. Duplicate `key_search_corpus.txt` removed. Tracker rewritten as resume-here; old one archived verbatim. README rewritten | `d008cb2` `fe7588b` `8b143c1` + this |
| 2026-10-01 | **F** remove other-project material | `.agent/` (mcMMO memory), Ko-fi `FUNDING.yml`, mcMMO workflows deleted (identical copies in `../mcMMO-Singleplayer`). AGENTS.md rewritten for LP | `f5ca9a1` |
| 2026-09-29 | **E** archive legacy | 107 scripts → `tools/legacy/`; outputs → `data/archive/hillclimbers/20260529/` (`MOVES.txt` lists all 301 moves for reversal) | `50889e8` |
| 2026-09-29 | **D** logic-only analysis | Constraints C1–C7, scan-32 square decoded, 2026 web check → `reference/findings/`, `reference/community/community_research.md` | `f038274` `a85c106` |
| 2026-09-29 | **C** tracker correction | Invalid claims identified (now MASTER_TRACKER §4.3) | `a85c106` |
| 2026-09-29 | **B** canonical corpus | rtkd/iddqd master vendored; `tools/lpcore` + tests; 150 page files rebuilt from it | `f038274` |
| 2026-09-29 | **A** push safety | Tokens and foreign material git-ignored. History scanned: no secret ever committed | `f5ca9a1` |

Rollback for any stage: `git revert <commit>`. Untracked archive moves are reversed with `MOVES.txt`.
