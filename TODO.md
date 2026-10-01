# TODO — Liber Primus

The working plan. **Write a plan here before the first edit** (AGENTS.md): goal, approach, rejected
alternatives, what you're *not* doing, blast radius, rollback. When a stage is done, collapse it to one line
under "Done" with its commits. The full text stays in git history. Status and next research steps live in
[`MASTER_TRACKER.md`](MASTER_TRACKER.md) §1, not here.

---

## Active

### Q — consolidate the evidence base (2026-10-01)

**Goal.** Every number in tracker §3 and findings §2 is pinned by a test. C3 moves from a one-off script to a
test. One constraint register maps each C/L number to its statement, its observed value against its threshold,
and its test. A test keeps the docs honest: every test name, path and `lpcore` name a doc cites must exist.

**Audit (read-only, done before this plan).** Everything in C1–C7 reproduces from canonical data, but these are
unpinned: z = −17.36; the unigram χ² = 26.36 (C2); per-section doublets and z −4.15…−8.88 (C6); early vs late
p = 0.099; C4's rates 3.60 / 3.20 / 3.20 / 3.45 % (the test only checks > 3 %); the plaintext letter counts used by
the skills (AE = EO = OE = 0, J 3, X 5, IA 16, EA 18, F 44). C3 has no test at all (findings §5 says so).

**Steps.**
1. Pin the numbers above in `tests/test_stats.py`.
2. **C3 as a declared test** (not blind: the one-off result "≤ −0.3 for all 29 letters" was seen in 2026-09).
   Model M_x: c_i = c_{i−1} + (p_i − x)·k_i with k_i ≠ 0, so a doublet at i ⇔ p_i = x, with no leak. Word
   boundaries are taken as the plaintext's (as in C1, C7). Two predictions per letter x, from the 2,901 solved
   plaintext runes:
   - *Count:* the doublet count is Poisson(f_x · 12,947). Excluded if the two-sided tail p < 10⁻⁶.
   - *Position:* the class of each doublet's second rune in its word (initial / medial / final / sole). LLR_x =
     Σ over the 86 doublets of log[P̂(x | class) / f_x], with P̂(x | class) = (n_x,class + 10·f_x) / (n_class + 10).
     Excluded if LLR_x ≤ −10.
   - x is excluded if either rule fires. Letters absent from the plaintext (f_x = 0) predict 0 doublets.
   - **Verdict:** C3 holds if all 29 are excluded. Otherwise record which letters survive, and C3 is weakened
     to the rest.
3. **Homophonic substitution** (catalog #19, currently "arg"). A homophonic map sends each plaintext letter to
   its own set of cipher runes. With 26 letters used and 29 runes, only 3 are spare. The exact lower bound on
   LP2's unigram χ² over every allocation (each letter gets ≥ 1 rune, 3 spares, split evenly, which is optimal by
   convexity) is computed by enumerating all C(28, 3) = 3,276 allocations. **Excluded if the minimum χ² ≥ 200**
   (observed 26.4 on 28 df). Predicted before running: thousands, from J and X alone.
4. **Constraint register** as findings §0: ID, one-line statement, observed vs threshold, test. Tracker §3.2
   links to it.
5. **`tests/test_docs.py`.** In tracked docs, every backticked `test_*` name exists in `tests/`; every cited
   repo path exists; every `stats.` / `detect.` / `leak.` / `keys.` … name resolves. Every C-number in tracker
   §3.2 has a register row. Positive control: a doc string with a bogus name must fail the checker.
6. Fix stale pointers: AGENTS.md ("§2 constraints C1–C7, §6 open items"), findings §5 and §6. Skills (local
   only): cite the register, record C3 and homophonic status.

**Rejected.** A new standalone "facts" doc: a third copy of the constraint list would drift. The register lives
in the findings doc, and the tracker links to it. Re-deriving the P.S. number's provenance: it needs primary
sources that are not in the repo.
**Not doing.** No new key-source tests. No change to any existing verdict or threshold.
**Blast radius.** Tests, docs, and one or two pure functions in `stats.py`/`leak.py`. **Rollback:** `git revert`.

## Owner items

- [ ] **Tokens in `.claude/mcp.vscode-reference.json`** (GitHub PAT, mem0, context7) are plaintext. They were never
  committed or pushed (full-history scan on 2026-09-29), so rotating them is optional. Consider VS Code `inputs`
  (`promptString`, `password: true`) instead of hardcoding them.

---

## Done

| Date | Stage | Result | Commits |
|---|---|---|---|
| 2026-10-01 | **P** agent skills | Local only (`.claude/` and `CLAUDE.md` are gitignored). New skills `lp-expert` (+ `lore.md`), `lp-attack` (+ `attack-catalog.md`), `lp-claim-audit`; repo overrides in 7 generic skills; `CLAUDE.md` index. All 23 cited `lpcore` names resolve; suite green. No research result changed | — (no tracked files besides this row) |
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
