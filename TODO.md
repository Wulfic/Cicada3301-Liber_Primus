# TODO — Liber Primus

The working plan. **Write a plan here before the first edit** (AGENTS.md): goal, approach, rejected
alternatives, what you're *not* doing, blast radius, rollback. When a stage is done, collapse it to one line
under "Done" with its commits. The full text stays in git history. Status and next research steps live in
[`MASTER_TRACKER.md`](MASTER_TRACKER.md) §1, not here.

---

## Active

### R — Cicada's own numbers and OutGuess payloads as wide-alphabet keys (2026-10-01)

Tracker §1, item 1. Declared before any LP2 decode. The only runs so far were synthetic power checks, on solved
plaintext encrypted with these keys.

**Model:** c_i = p_i ± k_j (sub `c−k`, add `c+k`, beaufort `k−c`), plus a constant shift s ∈ 0…28. The key k is one
of the sources below, **read cyclically from an unknown start phase**. Drift follows `detect.log_lr`: ρ = 0.02
stall and skip, ε = 0.1. The unknown phase is handled exactly, not searched: the forward pass starts with a uniform
prior over all P phases (new `starts=` argument to `detect.log_lr`). The mixture's E[LR] = 1 under the null, so
the e^−30 bound per decode still holds, and the cost is log P ≤ 11 nats of power.

**Sources** (key values mod 29; each under two **mappings**, `mod` = v mod 29 and `reject` = drop v ≥ 29·⌊V/29⌋,
then mod 29, which is how a careful pad generator makes uniform values):
- Digit groups (V = 100 for pairs, 1000 for triples): pairs at phase 0 and 1, triples at phase 0, 1 and 2, of
  - the 2012 P.S. number, 131 digits (`community_research.md` §2b; `echo446ghq_analysis.md` agrees);
  - its 132-digit variant (the archived tracker §9.5 appends a `1`; provenance unresolved, so both are run);
  - the 2014 RSA modulus n, 130 digits (`people_2014.md`, outguess of 1033.jpg).
  That is 15 digit keys.
- Bytes (V = 256): the onion cookies 167 and 761 (32 bytes each, `community_research.md` §2c); the AN END hash
  (`keys.an_end_hash`, 64 bytes); the signed hex in `data/outguess/page_00.txt` (991 bytes); the 2014 second-onion
  hex (256 bytes, `people_2014.md`); the wisdom/folly hint (3,368 bytes; `wisdom_hint` = `folly_hint`), forward and
  reversed (= `folly_rev_hint`); and `page_17.bin`, `page_21.bin`, `page_43.bin` (58,152 bytes each). That is 10 byte keys.
- Excluded from the family: `page_08.txt` (English, so C10), and hex read one digit per rune (C13).

**Alignments:** each of the 9 unsolved sections, and LP2 continuous (7–15). That is 10.
**Not already excluded because:** C9 excludes these short keys only as in-step periods ≤ 1000. Under drift it covers
only periods ≤ 25, and the long payloads (3,368 and 58,152) are outside it. C13 covers single digits, hex and
letters, not pairs, triples or bytes (untestable by marginals). The ledger ran OutGuess payloads in fixed sync only.
**Family size N:** 25 keys × 2 mappings × 3 modes × 29 shifts × 10 alignments = **43,500** → false-positive bound
43,500 · e^−30 ≈ 4.1 × 10⁻⁹.
**Pass:** any decode with log LR ≥ 30. A pass is then audited (`lp-claim-audit`) before it is called anything.
**Exclude:** every decode < 30, with all positive controls ≥ 30. **Inconclusive:** any positive control < 30. That
source is then recorded as "untestable this way".
**Controls (run first, in the same runner):** positive: solved plaintext at 729 and 3,316 runes, encrypted by
`keys.encrypt_dodging` (keep 0.19, rekey `fresh` and `next`) from a random phase of each key and mapping, scored
in sub mode at the true shift. Each must be ≥ 30. Synthetic checks gave +216…+338 at 729–1,021 runes. Negative:
the same pipeline on a `keys.random_key` of each key's length, which must stay < 30.
**Expected if true:** ≥ +200 on the true alignment. **Expected if false:** about −1 nat per rune, so −90 … −1,600.
**Not doing:** other mappings (base conversions, factorisations, hashes of these numbers); the wrapper/middle split
of the `.bin` files (the phase mixture already covers every offset); onion addresses as text (English-like, C10).
**Blast radius:** additive. A `starts=` keyword in `detect.log_lr` (default unchanged), `tools/run_stage_r.py`,
`reference/findings/stage_r_candidates.tsv`, and tests. **Rollback:** `git revert <commit>`.

## Owner items

- [ ] **Tokens in `.claude/mcp.vscode-reference.json`** (GitHub PAT, mem0, context7) are plaintext. They were never
  committed or pushed (full-history scan on 2026-09-29), so rotating them is optional. Consider VS Code `inputs`
  (`promptString`, `password: true`) instead of hardcoding them.

---

## Done

| Date | Stage | Result | Commits |
|---|---|---|---|
| 2026-10-01 | **Q** consolidation | Declared first (`028ef53`). Register of every C/L number with its test (findings §0). C3 now a test: all 29 letters excluded (23 + AE/EO/OE by count, NG/IA/EA by position). C15: no homophonic substitution, least χ² 4,802 ≥ 200 (enumeration also allows unused runes, which can only lower the bound). §3.2 numbers pinned; `tests/test_docs.py` checks cited tests, paths, names, links. Errata: C3 "75" → 25.2, C7 "2.6 %" → 2.39 %. → findings §15 | `028ef53` + this |
| 2026-10-01 | **P** agent skills | Now tracked: `CLAUDE.md` and the 10 enabled skills under `.claude/skills/` (tokens and local settings stay ignored). New skills `lp-expert` (+ `lore.md`), `lp-attack` (+ `attack-catalog.md`), `lp-claim-audit`; repo overrides in 7 generic skills; `CLAUDE.md` index. All 23 cited `lpcore` names resolve; suite green. No research result changed | — (no tracked files besides this row) |
| 2026-10-01 | **O** skip-next rule | Declared first (directional statistic new; L1 χ² already seen). C14: LLR −21.3 ≤ −10, skip-next excluded; robust to held-out Δp models (−20/−32). → findings §14 | `0d4d86b` + this |
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
