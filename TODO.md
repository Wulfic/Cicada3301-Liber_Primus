# TODO — Liber Primus

The working plan. **Write a plan here before the first edit** (AGENTS.md): goal, approach, rejected
alternatives, what you're *not* doing, blast radius, rollback. When a stage is done, collapse it to one line
under "Done" with its commits. The full text stays in git history. Status and next research steps live in
[`MASTER_TRACKER.md`](MASTER_TRACKER.md) §1, not here.

---

## Active

### AA — keyless sliding-context ciphers (2026-10-12)

**Goal.** One key-free test of every cipher in which each cipher rune is a fixed function of a short window of
plaintext runes and nothing else: no key stream, no position dependence, no ciphertext feedback. Such a cipher sends
equal plaintext windows of n + w runes to equal cipher n-grams wherever they occur, so it keeps the plaintext's
repeat count of long windows, whatever its table. Stage Z did this for aligned blocks and words only.

**Model.** c_i = F(p_{i−a}, …, p_{i+b}) with context width w = a + b, w = 0…12, F any fixed table (not necessarily
injective), followed by the measured anti-doublet rule (a would-be doublet re-drawn uniformly with prob. 0.81, as in
stage Z). Mode "sec": the context restarts at each section start. Mode "cont": segments 7–15 are one stream.
This covers:
- an alphabet chosen by the previous plaintext rune or a 2-rune context (attack catalog row 12, open);
- plaintext autokey with arbitrary tables (any lag ≤ 12, since F may ignore the runes in between);
- any sliding polygraphic transform (a Hill-like map applied at every position, not just to aligned blocks);
- w = 0 is monoalphabetic substitution, already excluded by flatness. It is the known-answer cell.

**Not already excluded because:** C10 and C11 cover additive autokey only, and C18 covers Quagmire autokey only
under random alphabets, not arbitrary tables. C12 selects the alphabet by ciphertext, not plaintext. C16 covers random
tables only. C20 covers aligned blocks and whole words, not sliding windows. Catalog row 12 is open.

**Statistic.** K_n = pairs (i, j) with j − i ≥ n of equal cipher n-grams over all sliding windows (overlapping
windows are left out so the analytic null is exact). Mode "sec": pairs within each section. Mode "cont": pairs over
the 12,956-rune stream. n = 3…7, so 10 statistic cells, each scored once on LP2. Words and spaces are ignored (C1).

**Null (flat).** 1,000 seeded draws of uniform runes in LP2's section sizes with the same anti-doublet rule
(stage Z's null_sections). Per statistic cell: mean μ₀, sd σ₀ (floor 1), max.

**Positive controls, per (mode, w, source).** 200 seeded draws for each of 2 sources, as in stage Z: (E) contiguous
Emerson windows and (L) solved-LP words in random order, cut to LP2's section sizes. Each is enciphered as
c_i = σ_ctx(p_i), ctx = (p_{i−w}, …, p_{i−1}), padded with a 30th symbol before the context start (each section in
"sec", the stream start in "cont"). σ_ctx is a fresh uniform random permutation of Z₂₉ for every distinct context in
every draw. Then the anti-doublet rule is applied within each section. All five K_n are scored on each draw.
A one-sided context is enough: a two-sided window of the same width w gives the same statistic.

**Declared rule** (written before the runner exists and before LP2 is scored):
- Per (n, mode, w): lower = exp(m − 5s) − 1, with m and s the mean and sd of ln(K_n + 1) over a source's draws
  (stage Z's amended bound). **Testable** iff, for both sources, lower > the null's maximum and every draw > the null's
  maximum. **Excluded** iff testable and K_LP2 < lower for both sources.
- Per (mode, w): **excluded** if any n excludes it; otherwise **inconclusive** if any n is testable; otherwise
  **untestable**.
- Per statistic cell (n, mode): **PASS (lead → lp-claim-audit)** iff K_LP2 > null max and (K_LP2 − μ₀)/σ₀ ≥ 6.
- **Run valid** iff every statistic cell with n ≤ 5 has a null mean within 3 s.e. of the analytic
  E[K_n] = (pairs with j − i ≥ n) × P(two windows of n runes are equal) (stage Z's p_equal; the Markov correlation
  between disjoint windows is O(0.03^gap) and ignored). Otherwise every row is VOID.

**Family.** 10 statistic cells scored once, 130 (n, mode, w) exclusion cells, 26 (mode, w) verdicts. A false PASS
needs 6σ above the null maximum. A false exclusion needs a 5σ log-scale miss by both sources.

**Expected** (power check on controls only, 3 draws per source, no LP2): plaintext windows of 10, 12 and 14 runes repeat
about 106–391, 36–126 and 16–51 times in 12,956 runes, against flat 5- and 6-gram nulls near 4 and 0.1. So expect
w = 0 excluded in both modes, w excluded up to about 4–7, and the rest untestable. **Prior, disclosed:** stage Z
found LP2's aligned block repeats at the null level (n = 2–8), so LP2 is expected at the null in all 10 statistic cells.
That gives no PASS, and the new information is the coverage.

**Not doing.** Ciphertext feedback mixed with plaintext context (C12 covers pure ciphertext selection). Keyless tables
that also depend on position (period P). Contexts wider than 12 runes. Random (homophonic) choices. Any cipher with a
stream key on top: a fresh key value per rune destroys repeats, and that is the open space this stage leaves.

**Outputs.** A runner tools/run_stage_aa.py (--quick scores no LP2 runes and writes nothing), TSVs
reference/findings/stage_aa_results.tsv and stage_aa_controls.tsv, a test tests/test_stage_aa.py, findings §25,
and a new constraint C21 if anything is excluded. **Blast radius:** additive only. **Rollback:** git revert.

## Owner items

- [ ] **Tokens in `.claude/mcp.vscode-reference.json`** (GitHub PAT, mem0, context7) are plaintext. They were never
  committed or pushed (full-history scan on 2026-09-29), so rotating them is optional. Consider VS Code `inputs`
  (`promptString`, `password: true`) instead of hardcoding them.

---

## Done

| Date | Stage | Result | Commits |
|---|---|---|---|
| 2026-10-01 | **Z** word and block codebooks | Declared first (`be4a200`, red on the docs test for backticked future paths, fixed in `3015705`). K = pairs of equal units, kept exactly by any word- or block-deterministic table. 72 cells: Zw within sections and across LP2; Zb n = 2–8 at every offset, per section and continuous. 1,000 flat nulls in LP2's word lengths, plus 200 Emerson and 200 shuffled solved-LP controls per cell, with the 0.81 re-draw rule. Amended before LP2 was scored (`5298559`): μ − 5σ became 5σ on ln(K + 1), because `--quick` showed right skew. Valid (null means within 3 s.e. of the exact Markov E[K]). **No pass; LP2 at the null in every cell (\|z\| ≤ 1.38). C20:** 26 excluded (Zw ×2, n = 2–4 all offsets, n = 5 continuous ×5 and sec a = 2), 46 untestable (n ≥ 6, four n = 5 sec offsets). Prediction met → findings §24 | `be4a200` `3015705` `5298559` + this |
| 2026-10-01 | **Y** grid under long byte keys | Declared first (`edd9c53`). The 6 long byte sources on disk (3 `.bin` payloads, hint, `page_00` hex, 256-byte second-onion hex) as running keys on the grid, every cyclic phase, in step, readings R / R-rev / C / C-rev, operations ⊕, g − k, g + k, k − g: 2,865,136 trials. Statistic D = distinct bytes, with an exact null (Stirling numbers); PASS at D ≤ 120 (3.79e-17 per trial). Valid: 24 / 24 plants found at their cell (D 16–64), 0 / 18 negatives, mean D 162.002. **No pass; all 96 cells excluded**, min D 139. Erratum: the declared null minimum "131–136" is about 136–141. k − g duplicates g − k in D (bijection), disclosed → findings §23 | `edd9c53` + this |
| 2026-10-01 | **X** grid structure, key-free | Declared first (`225ff30`). Readings R (printed) and C (column-major, 32 × 8). X1: uniform on all 7 statistics (161 distinct, p 0.92). X2: within-class coincidences C_p, which no per-column σ can change, for p = 1…128 against 100,000 uniform draws and plaintext windows (EN Emerson 9,024, RUNES 2,646, HEX and B64 10,000). No structure (min p 0.0031 vs 10⁻⁵). **Excluded:** every p ≤ 102 (R) / 112–122 (C) for EN, RUNES and HEX; ≤ 22 / 28 for B64. X3: small factors in all 4 integer readings, so not an RSA modulus or prime (R readings factored before the declaration, disclosed). X4: no zlib/gzip/bz2/lzma end-of-stream (raw deflate chance 0.55 %), no signature. Post-run: sympy swapped for a stdlib sieve and Miller–Rabin (X3 rows identical) → findings §22 | `225ff30` + this |
| 2026-10-01 | **W** byte keys as random tabulae, in step | Declared first (`106c634`; that commit was red on `tests/test_docs.py` because it backticked future paths, fixed in `8af4b7e`). Stage S's 5 raw-byte classings (hint, reversed hint, page_17/21/43.bin) × 10 alignments, `alphabets.log_mean_lr`. Per cell, at the exact length: 5 positives and 5 flat negatives (additive, uniform key, keep 0.19), plus an LP2 shuffled-key null per key. Valid: worst negative +0.64. No pass (best +0.84). **Excluded:** continuous and section 15 for all 5, and section 11 for page_21 and page_43 (12 cells). 38 untestable. LP2 rows equal stage S's, as declared. In step only → findings §21 | `106c634` `8af4b7e` `c88b443` + this |
| 2026-10-01 | **C/K rendering** (user report) | Page READMEs rendered solved words with one spelling per rune: CNOW, LICE, BOOC, THINC, ASCED (also UOICE, INSTRUCTIAN, THNGS). Display only: ciphers, detectors, running-key models and keyword spellings all use rune index 5 (C = K = Q), so no result changes. `verify.render_words` takes each word from the translation after `word_matches` confirms the runes spell it, and raises otherwise; segment 2's 13 square cells (no English) stay canonical on a labelled line. Tests: rendered = English word for word, all 19 K kept. 17 page files regenerated. Rejected: a context guess for K; changing `LATIN` | `a003cfd` |
| 2026-10-01 | **V** named keyword Quagmire | Declared first (`8880e3b`); runner and an outputs-only amendment committed before the LP2 run (`7d44b09`). 34 LP keywords → 68 alphabets (K, K⁻¹, id) → 314,432 triples × 6 key families, C13's labelled LLR best over 87, exclude ≤ −10 (false exclusion ≤ e^−10 at any family size). `quagmire.keyed_alphabet` / `log_models` / `best_llr` (brute-force equal; identity reproduces C13). Gates: G1 0 / 300, G2 testable 100 % except hex 99.5 %, letters 13.3 %. **C19:** English ×3 and digits all excluded, hex 314,001, letters A–Z 103,864; best +6.51, no lead. Declared "every testable member excluded" failed (135 hex, 10,197 letters); LP2 sits inside the flat-cipher range → findings §20 | `8880e3b` `7d44b09` + this |
| 2026-10-01 | **U** Quagmire relabelling | Declared first (`4051fe2`). Gates amended before LP2 was scored (`f2ecd72`): the declared G2/G3 had power and calibration swapped, caught by `--quick`; control draws raised to 100,000. `lpcore/quagmire.py` (encoder, C17 interval, exact λ per alphabet draw, vectorised noncentral CDF tested equal to `flatness`). U1 audit: the cipher is the additive one renamed (tested rune for rune). **C17:** iid key doublet rate in [2/29 − Σb², Σb²] under any labels; the deficit needs Σb² > 0.05925. **C18:** G1 within 0.23 %, G3 0 / 20 in all 24 rows; 20 rows excluded (worst P 1.7e-11, no draw reaches λ_max), letters A–Z untestable (power ≤ 2 / 20). C13's letters exclusion now straight alphabets only. Declared Σb² 0.06233 was a rounding slip (0.06232) → findings §19 | `4051fe2` `f2ecd72` + this |
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
