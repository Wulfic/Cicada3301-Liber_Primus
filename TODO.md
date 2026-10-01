# TODO — Liber Primus

The working plan. **Write a plan here before the first edit** (AGENTS.md): goal, approach, rejected
alternatives, what you're *not* doing, blast radius, rollback. When a stage is done, collapse it to one line
under "Done" with its commits. The full text stays in git history. Status and next research steps live in
[`MASTER_TRACKER.md`](MASTER_TRACKER.md) §1, not here.

---

## Active

### V — Quagmire with named keyword alphabets, labelled (2026-10-01)

**Goal.** MASTER_TRACKER §1 item 1. Stage U treated the alphabets of c = π₂(π₁(p) + π₃(k)) as random, and a uniform
A–Z key was untestable there. Here every alphabet is **named**, from a declared list of LP keywords. Naming π₂ gives
back the labels, so C13's own statistic (labelled unigram LLR against flat, best over mode × offset) applies exactly
to each member. It is stronger than the label-free χ²: on flat data E[LLR] ≈ −λ/2 with sd ≈ √λ.

**Model:** c_i = π₂(s·π₁(p_i) + t·π₃(k_i) + a), with k_i iid from family b and independent of the plaintext. Mode
sub is (s, t) = (+, +), add is (+, −), beaufort is (−, +), as in `stats.cipher_distribution`. a ∈ Z₂₉ is the constant
offset. Would-be doublets are re-keyed with a fresh value and leak 19 % of the time (`quagmire.encrypt`).
- **Keywords (declared, 34):** the solved keys DIVINITY and FIRFUMFERENFE (literal runes, `solved.py`), and
  CIRCUMFERENCE. The solved section titles: A WARNING, WELCOME, WISDOM, SOME WISDOM, KNOW THIS, A KOAN, AN
  INSTRUCTION, THE LOSS OF DIVINITY, AN END, PARABLE. Every distinct word of the PARABLE plaintext: LIKE, THE,
  INSTAR, TUNNELING, TO, SURFACE, WE, MUST, SHED, OUR, OWN, CIRCUMFERENCES, FIND, (DIVINITY), WITHIN, AND, EMERGE.
  And LIBER PRIMUS, PRIMUS, CICADA, PRIMES, TOTIENT. Multi-word keywords are written without spaces. A word becomes
  runes by `gematria.spellings_of(word)[0]`, the greedy longest-match spelling (THE → ᚦᛖ).
- **Alphabets A:** the identity, plus each keyword's keyed alphabet K (its distinct runes in order, then the rest in
  Gematria order) and its inverse K⁻¹ (Quagmire places letters by position, so both roles occur). Duplicate
  permutations are collapsed. Prototype count: 68.
- **Family:** every triple (π₁, π₂, π₃) ∈ A³ (Quagmire I–IV are subsets), so 314,432 members per key family. Each
  member's free parameters are mode × offset (87), as in C13.
- **Key families b (stage U's six):** English as runes, English as prime values mod 29, English as Latin A–Z,
  decimal digits, hex digits, uniform letters A–Z. Values are 0…V−1 before π₃, as in stages L and U.
- **Statistic:** best over 87 of `stats.unigram_llr` on the pooled LP2 counts (segments 7–15, 12,956 runes), with
  model r = π₂(π₁q ⊛ π₃b) and q = `detect.unigram` of the solved plaintext (C13's q).
- **Exclude** a member if its best LLR ≤ −10 (C13's line). **Not excluded** otherwise. **Lead** if ≥ +10: that is
  only a marginal fit, so it would need its own declared key test.
- **Error bound.** For the true member, P(LLR at its true mode and offset ≤ −10) ≤ e^−10 (Markov on the reverse
  ratio), and the best over 87 can only be higher. At most one member is true, so the chance of excluding it is
  ≤ e^−10 ≈ 4.5 × 10⁻⁵ whatever the family size. G1 checks this holds under dodging.
- **G1 calibration (void rule):** 300 synthetic ciphers (50 per key family) at 12,956 runes, from word-shuffled
  solved plaintext, keep 0.19. Each uses a seeded random member, mode and offset. If any is excluded by its own
  member, the run is **VOID**.
- **G2 power, per member:** 20 flat-key synthetic ciphers (keep 0.19). A member is **testable** if the rule excludes
  it on ≥ 18 / 20; otherwise it is recorded as **untestable** whatever LP2 gives.
- **Model-only facts seen before this declaration** (scratch script; synthetic only, LP2 never read): the vectorised
  LLR equals `stats.cipher_distribution` + `unigram_llr` on the identity triple (9.966042797 both). The share of
  members testable is 100 % for English (3 forms) and digits, 99.3 % for hex, and **10.6 % for uniform letters
  A–Z** (median flat best −9.6). The worst own-member score in 120 synthetic ciphers was +9.2 (letters A–Z).
- **Expected if the constraints extend:** every testable member excluded in all six families, so English, digits
  and hex are out under every named keyword alphabet. For letters A–Z, about 1 in 10 members excluded and the rest
  untestable. The identity triple must reproduce C13's −14.3 (letters A–Z), −19.5 (hex) and −214.3 (digits).
- **Outputs (to be written):** a stage V runner (`--quick`: gates only, never scores LP2), a stage V results TSV
  (gate rows, per-family counts, and every member not excluded), new `quagmire` helpers (keyed alphabets,
  vectorised best LLR), and a keyword-alphabets test module.
- **Amendment to the outputs only (before LP2 was scored).** About 90 % of the letters A–Z members are untestable,
  so "a row for every member not excluded" could mean ~10⁵ rows. Member rows are now written for every *testable*
  member not excluded and for every lead. Untestable members that are not excluded are counted per family. The
  runner is deterministic, so the full per-member table is reproducible. Family, statistic, thresholds and gates
  are unchanged. The `--quick` run (5 ciphers; never scores LP2) passed G1 and G2 before this commit.

**Not doing:** other keyed-alphabet constructions (continuing after the keyword's last letter, columnar-mixed),
26-letter Latin keyword alphabets, per-section alphabets, keys with dependent values, named key streams in step,
adversarial alphabets. **Rejected:** the label-free flatness χ² per (π₁, π₃). It ignores π₂, so it covers more
ciphers, but it has less power, and the family here names π₂ anyway.
**Blast radius:** additive. New helpers, runner, TSV, tests and docs. **Rollback:** `git revert` the stage commits.

## Owner items

- [ ] **Tokens in `.claude/mcp.vscode-reference.json`** (GitHub PAT, mem0, context7) are plaintext. They were never
  committed or pushed (full-history scan on 2026-09-29), so rotating them is optional. Consider VS Code `inputs`
  (`promptString`, `password: true`) instead of hardcoding them.

---

## Done

| Date | Stage | Result | Commits |
|---|---|---|---|
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
