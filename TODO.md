# TODO — Liber Primus

The working plan. **Write a plan here before the first edit** (AGENTS.md): goal, approach, rejected
alternatives, what you're *not* doing, blast radius, rollback. When a stage is done, collapse it to one line
under "Done" with its commits. The full text stays in git history. Status and next research steps live in
[`MASTER_TRACKER.md`](MASTER_TRACKER.md) §1, not here.

---

## Active

### J — what the key's own statistics must be (started 2026-10-01)

**Goal.** Tracker §1 item 1 (title cribs), approached from the key side. A crib against an OTP-class key always
yields *some* key fragment. It is falsifiable only under a key model, and the natural model ("the key is English
text, so the fragment reads as English") can be tested on all 12,956 runes at once without any crib.

**Approach. Two key-independent tests, each with positive controls.**
1. **C10: no English running key, from any text.** If c = p ± k with p and k both English, then c's unigram
   distribution is r = q ⊛ q_k (a convolution or correlation), and that is not flat. Predicted before looking at
   LP2 counts, with q = the solved-plaintext unigram: IoC(r) = 1.054 for the identity mapping and 1.042 when key
   letters map to prime values or φ(prime values) mod 29, in every sign. That is a predicted χ² excess of about
   550–700 over n = 12,956 runes. (C2 already measured the observed χ² at 26.4 on 28 df, so this is not blind on
   the data, only on the model.)
   - **Statistic:** LLR = Σ_c O_c · log(29 r_c), log-likelihood of the H_RK model against a flat one.
   - **Declared rule:** H_RK is excluded if LLR ≤ −10 nats.
   - **Robustness:** the key distribution is also diluted toward uniform, k_λ = λ q + (1 − λ) u for λ ∈ {1, 0.5,
     0.25}, and each λ is reported. A positive control (a synthetic running-key cipher, solved plaintext + LP1 text
     as key) must give LLR ≥ +10.
   - **Consequence if excluded:** plaintext autokey at any lag goes too (its key is the plaintext itself).
   - *Amended during implementation, before the LP2 run:* the LLR is not invariant to the mode's sign or to a
     constant key offset, so every mode is run separately and the hypothesis takes the most favourable of the 29
     offsets (the conservative direction for an exclusion).
2. **C11: no lag-L autokey on the ciphertext (L = 2…1000).** Under c_i = p_i ± c_{i−L}, the lag-L difference
   (or sum) of the ciphertext *is* the plaintext, so its 29-bin histogram is English, not flat. Statistic: χ² of
   (c_{i+L} − c_i) and of (c_{i+L} + c_i) mod 29 within sections, against the expectation from the observed
   frequencies. **Declared rule:** a lag is flagged if p < 0.01 / 1998. Prediction: nothing is flagged.
   Positive control: synthetic autokey at L = 7 and L = 500 must be flagged.
3. **Title cribs.** If C10 holds, record why cribs cannot be tested against an unmodelled key, and close the item.

**Rejected.** Cribbing titles against free keys: unfalsifiable. Brute-forcing mappings σ over 29! permutations:
that's search. Only three natural mappings are declared.

**Not doing.** No new key texts, no optimiser.

**Blast radius.** `tools/lpcore/stats.py` (new functions), `tests/test_keyspace.py`, docs. **Rollback:** `git revert`.

## Owner items

- [ ] **Tokens in `.claude/mcp.vscode-reference.json`** (GitHub PAT, mem0, context7) are plaintext. They were never
  committed or pushed (full-history scan on 2026-09-29), so rotating them is optional. Consider VS Code `inputs`
  (`promptString`, `password: true`) instead of hardcoding them.

---

## Done

| Date | Stage | Result | Commits |
|---|---|---|---|
| 2026-10-01 | **I** key-source riddles | Plan, thresholds and candidate list declared first. Drift-tolerant detector (`detect.py`, forward algorithm, bound e^−30). Controls pass except AN END (85 runes, 29.6 < 30: too short, recorded). C9: no periodic key (lags 11–1000). 2,610 decodes of primes / word sums / plaintext values all fail (best −65 nats on a real section). Segment 10 title not decoded by the square. → findings §8. `tools/run_stage_i.py`, `tests/test_detect.py` | `8641c50` + this |
| 2026-10-01 | **H** characterise the doublet leak | Predictions L1–L5 declared here, then run. Survivors are random at a constant ≈ 19 % (no nudge, no per-line check, no period, no clustering; C6 now a test). Key-switch refuted. New exact constraint C8 → findings §7. `tools/lpcore/leak.py`, `tests/test_leak.py` | `d66cbb2` |
| 2026-10-01 | **G** organise for clarity | `.gitattributes` (LF). `reference/` split into findings/sources/community/archive; `data/` split into canonical/corpora/outguess/archive, each with a README. Duplicate `key_search_corpus.txt` removed. Tracker rewritten as resume-here; old one archived verbatim. README rewritten | `d008cb2` `fe7588b` `8b143c1` + this |
| 2026-10-01 | **F** remove other-project material | `.agent/` (mcMMO memory), Ko-fi `FUNDING.yml`, mcMMO workflows deleted (identical copies in `../mcMMO-Singleplayer`). AGENTS.md rewritten for LP | `f5ca9a1` |
| 2026-09-29 | **E** archive legacy | 107 scripts → `tools/legacy/`; outputs → `data/archive/hillclimbers/20260529/` (`MOVES.txt` lists all 301 moves for reversal) | `50889e8` |
| 2026-09-29 | **D** logic-only analysis | Constraints C1–C7, scan-32 square decoded, 2026 web check → `reference/findings/`, `reference/community/community_research.md` | `f038274` `a85c106` |
| 2026-09-29 | **C** tracker correction | Invalid claims identified (now MASTER_TRACKER §4.3) | `a85c106` |
| 2026-09-29 | **B** canonical corpus | rtkd/iddqd master vendored; `tools/lpcore` + tests; 150 page files rebuilt from it | `f038274` |
| 2026-09-29 | **A** push safety | Tokens and foreign material git-ignored. History scanned: no secret ever committed | `f5ca9a1` |

Rollback for any stage: `git revert <commit>`. Untracked archive moves are reversed with `MOVES.txt`.
