# TODO — Liber Primus

The working plan. **Write a plan here before the first edit** (AGENTS.md): goal, approach, rejected
alternatives, what you're *not* doing, blast radius, rollback. When a stage is done, collapse it to one line
under "Done" with its commits. The full text stays in git history. Status and next research steps live in
[`MASTER_TRACKER.md`](MASTER_TRACKER.md) §1, not here.

---

## Active

### S — per-position alphabets c = σ_{k_i}(p), label-free (2026-10-01)

**Goal.** Tracker §1 item 1 / catalog row 24. Test whether a long named key picks an arbitrary secret alphabet
per position: c_i = σ_{k_i}(p_i), with one unknown permutation σ_v per key class v. This covers mixed-alphabet
tabulae (Quagmire-style, c = σ(τ(p) + k)), a running key with a secret tabula, and the additive case. The
labelled detector (`detect.log_lr`) cannot see any of these except the additive one.

**Model.** Classes v_i = class(K[t + i]) for a named source K read from phase t. Within a class the cipher is
σ_v(plaintext), so it has the plaintext's coincidence rate (s = Σq² = 0.0622) instead of 1/29. The key stays in
step: the re-key rule is a fresh draw (the surviving models in tracker §1; skip-next is C14-excluded). A drifting
rule is out of scope, because a coincidence test has no power under 1 % desync (catalog row 24).

**Detector (new, `tools/lpcore/alphabets.py`).** Per phase, LR(t) = Π_v DM(cipher in class v; α) / 29^−n. DM is a
symmetric Dirichlet-multinomial sequence probability with α = (1 − s)/(29s − 1) = 1.165, chosen so its expected
coincidence rate equals the plaintext's. It is invariant under every σ_v, so it needs no plaintext labels. A
decode is log of the mean of LR(t) over every phase t (a uniform prior, as in stage R). Under an iid-uniform cipher
E[LR(t)] = 1 for each t, so **P(decode ≥ 30) ≤ e^−30 with no calibration**. LP2's doublet deficit only removes
coincidences, so on LP2 the bound is conservative. Counts for all phases come from FFT cross-correlation, tested
equal to a direct per-phase count.

**Not already excluded because:** C2/C4/C10/C13 are marginal arguments about c = p ± k. With arbitrary σ_v the
mixture Σ_v P(v)·σ_v(q) can be flat, so none of them apply. C12 covers alphabets chosen by *ciphertext*, not by a
key. Stages I and R scored these sources only with plaintext labels (additive). **Short sources are already
covered:** a key of period P ≤ 1000 in step gives positions i and i + P the same σ, so the lag-P repeat rate is s
whatever σ is, and C9 sees it. This stage adds a test that C9 flags a σ-periodic synthetic key (periods 500 and
1000). So the cookies, AN END hash, grid, `page_00`, second onion, P.S./RSA groups and word sums (726) are not rerun.

**Family (N = 200 decodes, bound 200·e^−30 ≈ 1.9 × 10⁻¹¹).** 20 key classings × 10 alignments (9 sections, each from
an unknown phase, plus LP2 7–15 continuous from one phase). There are no modes or shifts, because σ absorbs them.
| Source | Read | Classings | # |
|---|---|---|---|
| primes p(n) | linear, phase 0…25,911 | p mod 29 (also φ(p), p ± c, 3301 − p: same partition) | 1 |
| solved plaintext, 2,901 runes | cyclic | rune index; prime value mod 29 | 2 |
| `wisdom_hint.txt`, forward and reversed, 3,368 bytes | cyclic | raw byte; byte mod 29 | 4 |
| `page_17/21/43.bin`, 58,152 bytes | cyclic | raw byte; mod 29; reject (v < 232, then mod 29) | 9 |
| `data/corpora/` emerson, self_reliance, liber_al, deor | cyclic | each distinct letter (`str.isalpha`, upper-cased) is a class | 4 |

**Controls, per key classing, before LP2 is scored.** Positive: the solved plaintext enciphered under that key with a
random σ per class, a random phase and the fresh re-key (keep 0.19), at 729, 1,894 and 12,956 runes, 2 seeds each.
Negative: the same ciphertexts scored against the key shuffled (same class sizes). Real-data null: the shuffled key
scored on LP2 continuous, one per classing (20).

*Amended before any LP2 decode:* the control text is the solved plaintext **reversed**. Started at its first rune, the
plaintext-key controls scored about +210 at 729 runes, because at phase 0 the key equals the text and that one phase
dominated the mean. At the true phase they score about +90, like the letter keys. The detector is unchanged.

**Rules, written now.**
- *Power* at an alignment of n runes: both positive controls at the largest control size ≤ n score ≥ 30. Segment 10
  (9 runes) never has power. Expected from the scratch check: classes mod 29 and letters about +65 at 729 runes and
  +4,000 at 12,956; raw bytes about +11 at 729 (no power), +57 at 1,894 and +1,700 at 12,956.
- *Pass (candidate):* any decode ≥ 30 on a real alignment. It is not a solve. A follow-up stage would have to be
  declared to recover the per-class alphabets.
- *Exclude:* a decode < 30 where there is power.
- *Inconclusive:* a decode < 30 without power. It is recorded as "no power", never as an exclusion.
- *Void:* any negative or real-data-null control ≥ 30. That means the null is broken, and nothing from the run counts.

**Not doing.** Drift; two layers (σ then an additive stream); rune transliterations of the corpora (no transliterator
exists, and building one is its own stage); sources not on disk. **Blast radius:** additive only (new module, runner,
TSVs, tests, docs). **Rollback:** `git revert` the stage commits.

**Run 1 (after `8c93b22`): VOID by the rule above.** Four negative controls scored +904 … +1,104, all on
plaintext-derived keys at 12,956 runes. The cause is in the control, not the detector. The control text was the
2,901-rune plaintext tiled, and those keys are read cyclically with the same period 2,901. So the control cipher
repeated itself at lag 2,901 (96.8 % of positions), and any classing of period 2,901 caught that, a shuffled key
included. LP2 at lag 2,901 is normal (328 / 10,055 = 3.3 %). The 20 real-data nulls were all ≤ −489. No decode
reached 30. The outputs of run 1 are committed as the record.

**Run 2, declared now (S′).** One change, to the controls only: the control text is the solved plaintext's *words*,
concatenated in a fresh seeded random order each time the list is used up. That text has no period. The family, the
detector, α, the sizes, seeds and every rule above are unchanged. *Not blind:* run 1's LP2 decodes have been seen
(all < 1 nat). They are deterministic, so run 2 must reproduce them exactly. The test will assert that, and the
controls can then only decide where there is power, by the rule already written.

## Owner items

- [ ] **Tokens in `.claude/mcp.vscode-reference.json`** (GitHub PAT, mem0, context7) are plaintext. They were never
  committed or pushed (full-history scan on 2026-09-29), so rotating them is optional. Consider VS Code `inputs`
  (`promptString`, `password: true`) instead of hardcoding them.

---

## Done

| Date | Stage | Result | Commits |
|---|---|---|---|
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
