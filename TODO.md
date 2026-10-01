# TODO — Liber Primus

The working plan. **Write a plan here before the first edit** (AGENTS.md): goal, approach, rejected
alternatives, what you're *not* doing, blast radius, rollback. When a stage is done, collapse it to one line
under "Done" with its commits. The full text stays in git history. Status and next research steps live in
[`MASTER_TRACKER.md`](MASTER_TRACKER.md) §1, not here.

---

## Active

### U — Latin-square (Quagmire) tabulae: which constraints survive re-labelling (2026-10-01)

**Goal.** MASTER_TRACKER §1 item 1. Quagmire I–IV and keyed mixed alphabets are c_i = π₂(π₁(p_i) + κ_i), with
κ_i = π₃(k_i) the key value after its own relabelling (mode and constant offset are absorbed into π₁ and π₃).
For a fixed key stream this is exactly the additive cipher on x = π₁(p), with its output renamed by π₂. Work out
which of C1–C16 and L1–L5 hold for every π₁, π₂, π₃, then re-derive the label-dependent ones that can be re-derived.

**Model-only facts checked before this declaration** (scratch script; never read LP2):
- With π₁ uniformly random, E|â(f)|² = (29Σq² − 1)/28 at every f ≠ 0, so E[λ] = n·(29Σq² − 1)(29Σb² − 1)/28 for
  **any** key distribution b. Monte Carlo agrees within 0.3 % for six key families (20,000 draws).
- Draws of λ at LP2's length: English runes min 87 / median 294; English prime values 125 / 407; English Latin letters
  120 / 350; decimal digits 187 / 693; hex digits 92 / 296; **uniform letters A–Z 14 / 42**.

**U1. Audit (no LP2 run).** A statistic that depends only on equality patterns of c (doublets, lag repeats, χ²
against flat, transition tables up to relabelling of rows and columns) is unchanged by π₂. A model that uses only the
multiset of q is unchanged by π₁. Classification to be written up: invariant C1, C2, C3, C5–C9, C11, C12, C15,
L2–L5; label-dependent C4, C10, C13, C14, L1 (its "no nudge" reading); C16 holds for its own family, which does not
contain Quagmire. Test: for random π₁, π₂ and a fixed key, the Quagmire cipher and the additive cipher on π₁(p) give
identical doublet counts, lag-1–10 repeats, pooled χ² and the C12 transition χ², while the Δc histogram differs.

**U2. C4 without labels (new C17, theorem plus test; no LP2 run beyond the known 86 / 12,947).** For an iid key with
value distribution b, independent of the plaintext, P(Δκ = e) = (1/29)Σ_f |b̂(f)|² ω^{fe}, which lies in
[2/29 − Σb², Σb²]. So the doublet rate lies in that interval **for any π₁, π₂, π₃ and any plaintext language**.
The observed 0.664 % needs Σb² ≥ 2/29 − 86/12,947 = 0.06233. Test: the interval holds exactly for 1,000 random (b, π)
including point masses; the needed Σb² is pinned; flat, letters A–Z (0.0385), base 60, digit pairs and bytes are
below it. That excludes all of them as rule-free sources of the deficit, under any labels.

**U3. C10 and C13 under random alphabets (new C18, the LP2 run).**
- **Model:** π₁, π₃ uniformly random permutations, either independent (variant I) or tied π₃ = π₁ (variant T,
  Quagmire III-like). π₂ does not affect χ². The key is iid from family b. Families (6): English as runes (LP-English
  q; covers letters), English as prime values mod 29 (φ is a shift of this, so the same family), English as Latin
  letters A–Z, decimal digits, hex digits, uniform letters A–Z.
- **Statistic:** pooled χ² (one set of alphabets for LP2, 28 df) and Σ per-section χ² over sections 7–9 and 11–15
  (fresh alphabets per section, 224 df), as in stage T. For each draw, λ is computed exactly from r = π₁q ⊛ π₃b.
  P = mean over draws of P(χ²_df(λ) ≤ observed). D = 100,000 draws for LP2 and 10,000 per control cipher, seed 3301.
- **Family size N:** 6 families × 2 variants × 2 statistics = 24 rows.
- **Exclude** a row if P ≤ 1e-4 under both the raw χ² and the χ² divided by the dodging factor (the mean χ² / df of
  200 flat-key Quagmire controls at LP2's length, keep 0.19). **Not excluded** otherwise. Family-wise 24 × 1e-4.
- **Gates, run first on synthetic data (word-shuffled solved plaintext, 12,956 runes, keep 0.19, re-key fresh):**
  G1: for variant I, MC mean λ within 3 % of the formula, every family. G2 (power): per family and variant, 20
  ciphers made with that family's key and random alphabets; the row is **testable** only if ≥ 18 / 20 reach
  P ≤ 1e-4, otherwise it is recorded as **untestable this way** whatever LP2 gives. G3: 20 flat-key Quagmire
  ciphers must give P > 1e-4 for every row; any failure makes the run **void**.
- **Expected if the constraints survive:** English (3 representations), digits and hex excluded in all four
  columns; uniform letters A–Z not excluded and probably untestable (median λ 42 vs LP2's λ_max 42.5).
- **Fast vectorised noncentral CDF:** tested equal to `flatness.noncentral_chi2_cdf`.
- **Amendment (before LP2 was scored).** The quick run (gates only, never scores LP2) showed the declared G2 and
  G3 had swapped roles. Ciphers made with a row's own key are the true model, so excluding them is a *false*
  exclusion. Flat-key ciphers look like LP2, so excluding *them* is the power. As written, G3 voids every row that
  has power. Corrected: **G2 (power)**: the exclusion rule (raw and corrected) excludes the row on ≥ 18 / 20
  flat-key ciphers, otherwise the row is untestable. **G3 (calibration)**: it excludes the row on 0 / 20 of the
  row's own ciphers, otherwise the run is void. Also, 10,000 draws cannot resolve P ≈ 1e-4 (the quick run had one
  own-family false exclusion at 2,000), so control rows now use the same 100,000 draws as LP2.
  `family_p` drops draws whose CDF is already below 1e-15. The family, thresholds, statistics and exclusion rule are
  unchanged.

**Not doing:** adversarial alphabets (the minimum of λ over all 29!² pairs is open; we report the prior P and the
smallest λ drawn); named keyword alphabets (a separate stage); C14 and L1 under relabelling; named keys in step
(stage S's decodes were seen, so they cannot be reused). **Rejected:** a key-free test for flat keys. For a fixed key the
cipher is the additive one renamed, and under a flat iid key it is uniform iid whatever π is, so no ciphertext
statistic can see the alphabets.
**Blast radius:** additive. A new `lpcore` module, runner, TSV, tests and docs. **Rollback:** `git revert` the stage commits.

## Owner items

- [ ] **Tokens in `.claude/mcp.vscode-reference.json`** (GitHub PAT, mem0, context7) are plaintext. They were never
  committed or pushed (full-history scan on 2026-09-29), so rotating them is optional. Consider VS Code `inputs`
  (`promptString`, `password: true`) instead of hardcoding them.

---

## Done

| Date | Stage | Result | Commits |
|---|---|---|---|
| 2026-10-01 | **T** flatness of random tabulae | Declared first (`f0c8e39`; that commit was red on `tests/test_docs.py`, since it cited files not yet written). `lpcore/flatness.py`: exact even-df χ² CDFs, the random-σ scale model, boundaries. Gates passed: A within −7.1…−1.5 %, B 0 / 200 at 1e-4 and 7 % at 0.05. **C16:** V_eff ≤ 168 pooled / 174 per section by the declared rule; 153 / 133 after a post-run anti-doublet correction (×0.939, from the additive control), which the findings quote. 15 / 20 stage S classings excluded; raw bytes open. The declared "power" rows were really calibration (0 false exclusions), relabelled. → findings §18 | `f0c8e39` + this |
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
