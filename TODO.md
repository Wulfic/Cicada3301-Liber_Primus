# TODO — Liber Primus

The working plan. **Write a plan here before the first edit** (AGENTS.md): goal, approach, rejected
alternatives, what you're *not* doing, blast radius, rollback. When a stage is done, collapse it to one line
under "Done" with its commits. The full text stays in git history. Status and next research steps live in
[`MASTER_TRACKER.md`](MASTER_TRACKER.md) §1, not here.

---

## Active

### X — key-free structure of the grid's 256 bytes (2026-10-01)

**Goal:** tracker §1 item 1. Stages M/N tried named keys on the grid. This stage asks what the bytes themselves allow,
for every key at once, as stage T did for LP2.

**Readings.** R = the 256 bytes in printed order (`keys.grid_bytes`). C = column-major: the grid is 32 rows × 8 cells
(scans 66/67/68 give 10/13/9 rows), read down column 0, then column 1, and so on. Reversal adds nothing to X1 and X2
(it maps the residue classes mod p onto each other), so it enters only X3 and X4.

**X1 — uniformity (a description, not an exclusion).** Seven statistics: distinct values, χ² over 256 bins, ones among
2,048 bits, high-nibble χ², low-nibble χ², and adjacent equal bytes in R and in C. Each gets a two-sided Monte Carlo p
from 100,000 iid uniform 256-byte blocks (seed 3301). **Non-uniform** if any p < 0.01 / 7. Distinct values (161) were
already published in findings §12, so (a) reproduces a known number.

**X2 — periodic byte substitution (the key-free kill).**
**Model:** in reading O ∈ {R, C}, c_i = σ_{i mod p}(m_i) for a period p ∈ 1…128, where σ_0…σ_{p−1} are *any* byte
bijections. That covers repeating-key XOR, b + k and b − k mod 256 under every key of length p, any per-column
substitution, and (p = 1) any monoalphabetic substitution combined with any transposition. The plaintext m comes from
class K.
**Statistic:** C_p(O) = Σ over columns, Σ over byte values, of (n choose 2), the coincident pairs within the residue classes
mod p. σ cannot change it, so a control is a plaintext window with no key.
**Classes K and controls** (256-byte windows): EN = raw bytes of data/corpora/emerson_essays.txt, windows at every
multiple of 64. RUNES = rune indices (bytes 0–28) of the solved plaintext (`keys.solved_plaintext_words`), windows at
every offset. HEX = random lowercase hex text, 10,000 seeded blocks. B64 = random base64 text, 10,000 seeded blocks.
Decimal and base-60 text are not run: their coincidence rates (1/10, 1/60) lie between HEX's and B64's.
**Rules, per cell (O, p, K):**
- **Structure (PASS)** for (O, p): C_p(O) exceeds all 100,000 uniform null draws. That is an empirical p < 10⁻⁵ per
  cell, and the 256 cells bound the family-wise rate at 2.6 × 10⁻³.
- **Excluded** (O, p, K): C_p(O) < the 0.1 % quantile of K's controls at that (O, p). The false-exclusion rate for the
  true (p, K) is ≤ 10⁻³.
- **Not excluded** otherwise. This is expected where K's controls overlap the uniform null: large p for every class,
  and most p for B64.
**Expected if true:** C_p ≈ P_p · κ_K, where P_p is the number of within-column pairs. κ is about 0.06 for EN and
1/16 for HEX, so at p = 64 that is ≈ 24 pairs against ≈ 1.5. **Expected if false (uniform bytes):** C_p ≈ P_p / 256.

**X3 — the grid as a 2,048-bit integer.** Four integers: R and C, each big-endian and little-endian. An RSA-2048
modulus must be odd, have exactly 2,048 bits and no prime factor below 10⁶. **Excluded as a modulus** if any reading
fails one of those; a Miller–Rabin primality result is also reported per reading. *Disclosure:* the two R readings were
factored before this declaration (big-endian: even, ÷ 3, 7, 13, 29, 179; little-endian: ÷ 3, 7, 11). That is
arithmetic, not a thresholded statistic, but it is recorded as observed, not predicted. The C readings are unseen.
Cicada's key 7A35090F is RSA-4096 (`reference/sources/cicada_pgp_key.asc`), so 256 bytes cannot be a raw signature by it.

**X4 — compression streams and file signatures.** Five decoders (zlib raw deflate, zlib, gzip, bz2, lzma FORMAT_AUTO),
each on four readings (R, R reversed, C, C reversed), for 20 decodes. Event E: the decoder reaches end-of-stream
without error. E's chance rate per decoder is calibrated on 100,000 seeded uniform blocks. **PASS:** E on a reading
whose decoder's calibrated rate × 20 ≤ 0.01. **Inconclusive:** E where the rate is higher (the output is recorded).
**Excluded:** no E. Stage N's signature list is also applied to the four unkeyed readings (stage N only checked keyed
outputs).

**Not already excluded because:** §12 and §13 tested named keys only. No C-number concerns the grid's own structure.
**Not doing:** keyed modern ciphers (AES and the like: untestable without a key), RSA ciphertext (needs n), aperiodic or
running keys over bytes, p > 128, and other 2-D readings (diagonals, spirals, boustrophedon). Each of those would be a
new declared hypothesis.
**Blast radius:** additive only. A new runner (tools/run_stage_x.py), result TSVs in reference/findings/, a test
(tests/test_stage_x.py), and docs. **Rollback:** git revert the stage commits.

## Owner items

- [ ] **Tokens in `.claude/mcp.vscode-reference.json`** (GitHub PAT, mem0, context7) are plaintext. They were never
  committed or pushed (full-history scan on 2026-09-29), so rotating them is optional. Consider VS Code `inputs`
  (`promptString`, `password: true`) instead of hardcoding them.

---

## Done

| Date | Stage | Result | Commits |
|---|---|---|---|
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
