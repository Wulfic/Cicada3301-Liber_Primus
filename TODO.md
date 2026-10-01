# TODO — Liber Primus

The working plan. **Write a plan here before the first edit** (AGENTS.md): goal, approach, rejected
alternatives, what you're *not* doing, blast radius, rollback. When a stage is done, collapse it to one line
under "Done" with its commits. The full text stays in git history. Status and next research steps live in
[`MASTER_TRACKER.md`](MASTER_TRACKER.md) §1, not here.

---

## Active

### T — flatness constraint on per-position alphabets (2026-10-01)

**Goal:** turn findings §17's "what this suggests" into a declared, key-independent constraint (tracker §1 item 1).

**Model:** c_i = σ_{k_i}(p_i). The key takes V values with weights w_v. The σ_v are **independent uniformly random**
permutations (a secret tabula with unstructured rows). The re-key rule is any rule that redraws a class from the same
weights. The cipher marginal is P(c) = Σ_v w_v q(σ_v⁻¹(c)), and its noncentrality is λ = n·29·Σ_c (P(c) − 1/29)².
Over random σ, E[λ] = λ̄ = n·(29·Σq² − 1)·Σw². By permutation symmetry the deviation is isotropic in the 28-dim
sum-zero space, so (CLT over classes) the observed χ² ≈ (1 + λ̄/28)·χ²₂₈. The CDF for even df is exact:
F_{2m}(x) = 1 − e^{−x/2} Σ_{j<m} (x/2)^j / j!. Only the weights matter, **not the alignment**, so the bound holds under any
desync or drift. q is the 2,901-rune solved plaintext (Σq² = 0.0622).

**Not already excluded because:** C9 and §17 cover σ keys only in step with period ≤ 1000. C12 covers σ chosen by
ciphertext. C15 covers homophonic substitution. C4, C10 and C13 concern additive keys. Stage S (named long keys) was void.

**Statistics (two, declared now):**
1. *Pooled* (one tabula for all of LP2): χ² of the 12,956 unsolved runes vs flat, already known to be 26.36 (C2 test).
   P_T(V_eff) = F₂₈(26.36 / (1 + λ̄/28)), with n = 12,956 and V_eff = 1/Σw².
2. *Per section* (a fresh tabula per section, same V_eff): S = Σ χ²_s over sections 7–9 and 11–15 (seg 10 has 9 runes,
   so it is left out; df 224). Null: Σ_s (1 + λ̄_s/28)·χ²₂₈, P by seeded Monte Carlo with 2·10⁶ draws. **The LP2 value
   of S has not been computed yet.**

**Exclude:** a model (V_eff, statistic) is excluded if P ≤ 1e-4 (the same order as C14's e^−10). Report V*, the largest
V_eff excluded, for each statistic. Apply the pooled rule to the stage S key classings' empirical weights (primes mod 29,
plaintext runes, hint, `.bin` raw and mod 29, four corpora as letters).

**Validity gates, run on synthetic ciphers before the LP2 per-section value is computed.** If either gate fails, the
stage is VOID and nothing is excluded:
- A (formula): word-shuffled solved plaintext, 12,956 runes, iid uniform keys over V ∈ {29, 256, 1024}, random σ,
  `encrypt_alphabets` with keep = 0.19, 200 ciphers per V. The mean χ² must be within 15 % of 28 + λ̄.
- B (no false exclusion): the same set-up at V = 1024. The pooled P under the true V must be ≤ 1e-4 for 0 of 200
  ciphers, and ≤ 0.05 for at most 10 % of them.
- Power (reported, not a gate): the fraction of V = 29 ciphers excluded, and of ciphers at V*/2.
- Structural control (reported): additive σ_v(p) = p + v with a uniform key. Its χ² stays near 28, which shows that
  Latin-square tabulae are outside this test.

**Expected if true** (LP2 = random tabula with few classes): χ² in the hundreds. **Expected if false:** the boundary
V* lands near a few hundred classes (rough estimate ~200–300 before computing), which excludes every ≤ 29-class key.

**Not doing:** structured σ families. A Latin-square tabula (Vigenère, Quagmire, affine with flat shifts) under a
near-flat key gives an exactly flat mixture, so this test cannot see it, and the doc will say so. No keyed decodes.
No change to the plaintext model after the run (the scaling with Σq² is reported, not gated).
**Blast radius:** additive only: `tools/lpcore/flatness.py`, `tools/run_stage_t.py`, `tests/test_flatness.py`, a TSV,
and docs. **Rollback:** `git revert <commit>`.

## Owner items

- [ ] **Tokens in `.claude/mcp.vscode-reference.json`** (GitHub PAT, mem0, context7) are plaintext. They were never
  committed or pushed (full-history scan on 2026-09-29), so rotating them is optional. Consider VS Code `inputs`
  (`promptString`, `password: true`) instead of hardcoding them.

---

## Done

| Date | Stage | Result | Commits |
|---|---|---|---|
| 2026-10-01 | **Contributors** policy | Owner request: wulfic is the main contributor; a merged PR makes its author a contributor. `CONTRIBUTORS.md` (PR #1 author listed, upstream credited separately), `tools/add_contributor.py` (dry-run unless `--write`; rejects invalid logins, skips maintainer and bots, one row per login), `.github/workflows/contributors.yml` (`pull_request_target` merged into main, PR code never checked out), `tests/test_contributors.py` | this |
| 2026-10-01 | **S** per-position alphabets, label-free | Declared first (`8c93b22`). DM detector `lpcore/alphabets.py` (exact mean-1 null, FFT = direct counts, in-step power, no power at 1 % desync). C9 shown to flag σ-periodic keys (P 500, 1000). The 20 classings × 10 alignments run is **VOID twice** by the declared rule. Run 1: the tiled 2,901-rune control text shared the plaintext keys' period (negatives +904…+1,104). Run 2, word-shuffled text: Liber AL negative +53.5, because random-σ control ciphers are not flat (χ² 1,141 / 355.6 vs LP2 26.4). Real nulls ≤ −489.5; LP2 decodes ≤ +0.84, identical across runs. Nothing excluded. Stopped after two failed fixes (attempt budget) → findings §17 | `8c93b22` `2c62782` `3f5b830` + this |
| 2026-10-01 | **PR #1** full grid | External PR (certified-retart) reviewed and merged: scan 68's 72 cells restored (256-byte grid), five cells per iddqd `f804b85` (checked against the upstream diff and scans 66–68; one I/l call is convention). Suite green on the PR branch; stage M/N TSVs regenerate byte-identical. Merged into local main with stage R/S | `4f326e5` `66c67a3` |
| 2026-10-01 | **R** Cicada numbers, OutGuess payloads | Declared first (`2c209dc`). 25 sources × 2 mappings (mod, rejection) × 3 modes × 29 shifts × 10 alignments = 43,500 drift-tolerant decodes, every start phase under a uniform prior (`detect.log_lr(starts=)`). None passes: best on a real section −50.8 vs +30; controls 200/200 ≥ +169.1. First run killed at the 2 h background limit, so `lpcore/fastdetect.py` (numpy, tested equal) was added and the unchanged family re-run. → findings §16 | `2c209dc` + this |
| 2026-10-01 | **Q** consolidation | Declared first (`028ef53`). Register of every C/L number with its test (findings §0). C3 now a test: all 29 letters excluded (23 + AE/EO/OE by count, NG/IA/EA by position). C15: no homophonic substitution, least χ² 4,802 ≥ 200 (enumeration also allows unused runes, which can only lower the bound). §3.2 numbers pinned; `tests/test_docs.py` checks cited tests, paths, names, links. Errata: C3 "75" → 25.2, C7 "2.6 %" → 2.39 %. → findings §15 | `028ef53` + this |
| 2026-10-01 | **P** agent skills | Now tracked: `CLAUDE.md` and the 10 enabled skills under `.claude/skills/` (tokens and local settings stay ignored). New skills `lp-expert` (+ `lore.md`), `lp-attack` (+ `attack-catalog.md`), `lp-claim-audit`; repo overrides in 7 generic skills; `CLAUDE.md` index. All 23 cited `lpcore` names resolve; suite green. No research result changed | — (no tracked files besides this row) |
| 2026-10-01 | **O** skip-next rule | Declared first (directional statistic new; L1 χ² already seen). C14: LLR −21.3 ≤ −10, skip-next excluded; robust to held-out Δp models (−20/−32). → findings §14 | `0d4d86b` + this |
| 2026-10-01 | **N** historical grid prefix | Declared first (PGP rule amended before the run). The original 184-byte prefix gave 72 byte decryptions + 384 rune readings: none passed (best 44 % printable; best log LR −4.8). Superseded by the full-grid rerun. → findings §13, `tools/run_stage_n.py`, `tests/test_grid.py` | `14afdff` + this |
| 2026-10-01 | **M** historical base-60 prefix | Declared first. Scans 66–67 supplied 184 bytes and omitted scan 68. Its 3,132 key tests gave no pass (best −5.5 on a real alignment; power check +45…+122). Superseded by the full-grid rerun. → findings §12, `tools/run_stage_m.py` | `4d66364` + this |
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
