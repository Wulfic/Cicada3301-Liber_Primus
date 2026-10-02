# TODO — Liber Primus

The working plan. **Write a plan here before the first edit** (AGENTS.md): goal, approach, rejected
alternatives, what you're *not* doing, blast radius, rollback. When a stage is done, collapse it to one line
under "Done" with its commits. The full text stays in git history. Status and next research steps live in
[`MASTER_TRACKER.md`](MASTER_TRACKER.md) §1, not here.

---

## Active

### Z — deterministic local encryption: word and block codebooks (2026-10-01)

**Goal.** One key-free test of every cipher in which the ciphertext of a local plaintext unit depends only on that
unit. Any such cipher maps equal units to equal cipher units, so it keeps the plaintext's repeat count exactly,
whatever the table. Two families:
- **Word-deterministic (Zw):** cipher word = T(plaintext word) for a fixed injective T. This covers a key that restarts
  at every word (c_j = p_j + k_j, j = position in the word, any k), word-length-dependent keys, any per-word
  transposition plus substitution, and a word codebook. A key that restarts at each word is not periodic in the global
  position, so C9 does not cover it. C7 (one shift per word) is a stream, not this.
- **Block-deterministic (Zb, ECB):** aligned n-rune blocks map through a fixed bijection of Z₂₉ⁿ. This covers Hill
  n ≥ 2 (catalog row 18, open), any polygraphic codebook, and digraphic n = 2 (ledger only, never run here).

**Model.** Zw: c_word = T(p_word). Zb: c[a + n·t … a + n·t + n − 1] = B(p[same]), n = 2…8. Either is followed by the
measured anti-doublet rule: a would-be doublet in the continuous stream is re-drawn uniformly with prob. 0.81 (C8, keep 0.19).

**Not already excluded because:** C1–C19 test additive streams, tabulae keyed per position, or ciphertext feedback.
A word-restart key is not a global period (C9), and a fixed block table is no stream (C4, C10, C13). C15 (homophonic)
is n = 1 only. Catalog row 18 is open; row 17 rests on the ledger.

**Statistic.** K = number of pairs of equal units (words of ≥ 2 runes for Zw; aligned n-blocks for Zb). Words come
from the corpus's word divisions (numbers ignored). The cells are:
- Zw-sec: pairs within each section. Zw-all: pairs across all of LP2 (2 cells).
- Zb, mode "sec": blocks aligned at offset a from each section start, pairs within each section. Mode "cont": the 12,956
  runes as one stream, offset a, pairs over the whole stream. n = 2…8, a = 0…n−1, both modes: 70 cells.
- **Family 72 cells.**

**Null (flat).** 1,000 seeded draws: uniform iid runes in LP2's exact section and word lengths (all of segments 7–15),
with the same anti-doublet rule (continuous within a section). Per cell: mean μ₀, sd σ₀ (floor 1), max.

**Positive controls (power), per cell.** 200 seeded draws for each of 2 sources:
(E) contiguous Emerson-essays windows and (L) solved-LP plaintext words in random order. Each is cut to LP2's section
rune counts, enciphered with a fresh random injective table at that cell's unit and alignment, then given the
anti-doublet rule. Per cell and source: μ_pos, σ_pos.

**Declared rule** (written before LP2 is scored):
- **Testable** iff, for both sources, μ_pos − 5σ_pos > the null's maximum.
- **Excluded** iff testable and K_LP2 < μ_pos − 5σ_pos for both sources.
- **PASS (lead → `lp-claim-audit`)** iff K_LP2 > null max and (K_LP2 − μ₀)/σ₀ ≥ 6. Bonferroni: 72 cells, normal tail
  about 1e-9 each.
- Otherwise **inconclusive**.
- **Run valid** iff in every cell the 1,000 nulls have mean within 3 s.e. of the analytic E[K]. For Zb that is
  C(B, 2) · Σ P(block)² computed from the null's own marginal; it is only checked for n ≤ 4, where the mean is ≥ 1.
  The run is void if any n ≤ 4 cell fails.

**Expected if true** (English-only power check, 30 draws, no LP2): Zw ≈ 8,600–10,300 pairs against a flat ≈ 62; Zb n = 2:
≈ 19,600 against 3,846; n = 3: ≈ 1,400 against 60; n = 4: ≈ 215 against 1.3; n = 5: ≈ 62 against 0.03. **Expected if
false:** K_LP2 inside the null. **Prediction:** LP2 is OTP-class, so every testable cell is excluded; Zw and n = 2–4 are
testable, and n ≥ 6 is not.

**Not doing:** a codebook with homophones (several cipher strings per unit chosen at random), blocks that restart at
lines, pages or paragraphs, word-deterministic ciphers with a stream on top (that is the additive family), and
n > 8. Words of 1 rune are left out of Zw, since chance collisions swamp them.
**Blast radius:** additive only (new runner tools/run_stage_z.py, two TSVs, tests/test_stage_z.py, docs; not yet written).
**Rollback:** `git revert <commit>`.

## Owner items

- [ ] **Tokens in `.claude/mcp.vscode-reference.json`** (GitHub PAT, mem0, context7) are plaintext. They were never
  committed or pushed (full-history scan on 2026-09-29), so rotating them is optional. Consider VS Code `inputs`
  (`promptString`, `password: true`) instead of hardcoding them.

---

## Done

| Date | Stage | Result | Commits |
|---|---|---|---|
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
