# TODO — Liber Primus

The working plan. **Write a plan here before the first edit** (AGENTS.md): goal, approach, rejected
alternatives, what you're *not* doing, blast radius, rollback. When a stage is done, collapse it to one line
under "Done" with its commits. The full text stays in git history. Status and next research steps live in
[`MASTER_TRACKER.md`](MASTER_TRACKER.md) §1, not here.

---

## Active

### L — what values can the key take? (started 2026-10-01)

**Goal.** Tracker §1 item 1. Generalise C10 from "English text" to any key *alphabet*. When the key's values come
from a small set, the cipher distribution r = q ⊛ k is uneven in every mode and offset, and drift does not change
it. Testing the marginal excludes whole classes of digit, hex and letter keys without decoding any.

**Prediction (model only, before LP2): expected LLR on 12,956 runes if the alphabet were the key's.**
Decimal digits 0–9: +240. Hex 0–15: +41. Uniform letters A–Z: +25. Base-60: +3. Two-digit groups 00–99: +1.1.
Bytes: +0.3. Three-digit groups: 0.0. Also tested: **English text written as Latin letters**, A–Z → 0–25, with
A–Z frequencies from the solved translation. C10 covered English only in rune form.

**Declared rules.**
- Statistic: as C10, LLR = Σ O_c log(29 r_c), the most favourable of 29 offsets in each of 3 modes. Offsets also
  cover A = 0 against A = 1, and digit keys + constant.
- **Excluded** if every mode's best LLR ≤ −10.
- **Untestable** (recorded, not excluded) if the predicted LLR is below 20: base-60, 00–99, bytes, 000–999.
- **Positive controls:** LP2-sized synthetic ciphers (solved plaintext, repeated) with random keys from each
  testable alphabet, and with Emerson as Latin letters, must give LLR ≥ +10 with their own model.

**Consequence if excluded.** No key made of single decimal digits (π, e, the 2012 P.S. number, RAND digits, the
decimal digits of a hash), single hex digits (SHA hashes, OutGuess hex), or letters (uniform, or English).

**Not doing.** No new decodes. Wider alphabets with no power are recorded as untestable this way.

**Blast radius.** `tools/lpcore/stats.py` (refactor `running_key_distribution` over a new `cipher_distribution`),
`tests/test_keyspace.py`, docs. **Rollback:** `git revert`.

## Owner items

- [ ] **Tokens in `.claude/mcp.vscode-reference.json`** (GitHub PAT, mem0, context7) are plaintext. They were never
  committed or pushed (full-history scan on 2026-09-29), so rotating them is optional. Consider VS Code `inputs`
  (`promptString`, `password: true`) instead of hardcoding them.

---

## Done

| Date | Stage | Result | Commits |
|---|---|---|---|
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
