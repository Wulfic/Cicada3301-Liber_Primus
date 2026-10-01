# TODO — Liber Primus

The working plan. **Write a plan here before the first edit** (AGENTS.md): goal, approach, rejected
alternatives, what you're *not* doing, blast radius, rollback. When a stage is done, collapse it to one line
under "Done" with its commits. The full text stays in git history. Status and next research steps live in
[`MASTER_TRACKER.md`](MASTER_TRACKER.md) §1, not here.

---

## Active

### O — is the anti-doublet rule "skip to the next key value"? (started 2026-10-01)

**Goal.** Tell the re-keying mechanisms of C8 apart. Under a skip-next rule, a would-be doublet survives only when
k_{j+1} = k_j. The 19 % survival rate then forces the key to repeat adjacent values about 19 % of the time. But
then, at ordinary positions, Δc = Δp in 19 % of cases. English bigram differences leak into the Δc histogram
(bins 1–28), which L1 measured as flat (max |z| 2.58, χ² 41.2 on 27 df).

**Power, computed from the model before this plan:** the expected χ² excess is +47 at a 19 % key repeat, +8 at 10 %.
A directional likelihood ratio has about ±23 nats expectation and an sd of about 7.

**Test (C14).**
- H1: Δc bins 1–28 ∝ P1(e) = 0.19·P(Δp = e) + 0.81/28 · (1 − P(Δp = e)), with P(Δp) from the solved plaintext.
  H0: flat.
- LLR = Σ_e O_e · log(P1(e) / (1/28)) over the 28 bins, each renormalised.
- **Declared rule:** H1 is excluded if LLR ≤ −10; H1 is supported if LLR ≥ +10; otherwise undecided.
- **Not blind on the data:** L1's undirected χ² was already seen. The directional statistic and its rule are
  fixed here before it is computed.
- **Controls:** an LP2-sized synthetic under a skip-next rule with a key that repeats adjacent values 19 % of the
  time must give ≥ +10. A synthetic under a fresh re-key with a flat random key must give ≤ −10.

**Consequence if excluded.** C8's re-keying must use a replacement independent of the next key value (a "fresh"
draw, or a second key), or the leak is human error. Skip-next is gone.

**Blast radius.** `tools/lpcore/leak.py` (one function), `tests/test_leak.py`, docs. **Rollback:** `git revert`.

## Owner items

- [ ] **Tokens in `.claude/mcp.vscode-reference.json`** (GitHub PAT, mem0, context7) are plaintext. They were never
  committed or pushed (full-history scan on 2026-09-29), so rotating them is optional. Consider VS Code `inputs`
  (`promptString`, `password: true`) instead of hardcoding them.

---

## Done

| Date | Stage | Result | Commits |
|---|---|---|---|
| 2026-10-01 | **N** grid bytes | Declared first (PGP rule amended before the run). 72 byte decryptions + 384 rune readings under LP-native keys: none passes (best 44 % printable; best log LR −4.8). → findings §13, `tools/run_stage_n.py`, `tests/test_grid.py` | `14afdff` + this |
| 2026-10-01 | **M** base-60 grid | Declared first. Scans 66–67 = 184 bytes (60a + b ≤ 255). Bytes / 5-bit / digits as a key: 3,132 decodes, none passes (best −5.5 on a real alignment; power check +45…+122). → findings §12, `tools/run_stage_m.py` | `4d66364` + this |
| 2026-10-01 | **L** key alphabets | Rules and predictions declared first. C13: no decimal-digit (−214), hex (−19.5), letter (−14.3) or English-Latin (−122) key, best of 87 mode/offsets; controls +24…+251. Bytes, 00–99, base 60 untestable this way. → findings §11 | `0c59200` + this |
| 2026-10-01 | **K** ciphertext-selected alphabets | Rule declared first. C12: off-diagonal lag-L transition χ² flat for L = 1–1000 (best p 3.9e-3 vs 1e-5); calibration conservative; controls χ² 7.6k–14k. Subsumes C11. → findings §10 | `55c78b1` + this |
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
