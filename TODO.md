# TODO — Liber Primus

The working plan. **Write a plan here before the first edit** (AGENTS.md): goal, approach, rejected
alternatives, what you're *not* doing, blast radius, rollback. When a stage is done, collapse it to one line
under "Done" with its commits. The full text stays in git history. Status and next research steps live in
[`MASTER_TRACKER.md`](MASTER_TRACKER.md) §1, not here.

---

## Active

### N — do the grid's 184 bytes decrypt under LP-native keys? (started 2026-10-01)

**Goal.** Tracker §1 item 3. The grid bytes are random-like (6.91 bits per byte; 18 % prime, 49 % even, 52 % with
the high bit set). Test a short, declared list of LP-native decryptions. No search.

**Declared pass rule.** An output passes if any of these holds:
- (a) ≥ 90 % of its bytes are printable ASCII (0x20–0x7E, tab, CR, LF). For random bytes P ≈ 0.38 per byte, so
  the chance is below 10⁻⁵⁰, and multiplicity does not matter.
- (b) It starts with a known file signature: PNG, JPEG, GIF, gzip, zip, bzip2, PDF, ELF, or OpenPGP armour or packet tags.
  *Amended before the first run:* a bare OpenPGP tag byte matches 8 of 256 values (3 % per decode, about 4 false
  passes in 144). An OpenPGP packet now counts only if its header is well formed (old or new format) and its stated
  body length equals the bytes that follow.
- (c) For a rune reading, `detect.log_lr` ≥ 30.

**Byte operations.** XOR, b − k and b + k mod 256. Grid read forward and reversed. Each key:
- **H:** the AN END hash bytes (64, canonical page 73), repeated; also H reversed.
- **T:** the φ(prime) stream mod 256 (AN END's key) and the primes mod 256.
- **W:** the ASCII words DIVINITY, FIRFUMFERENFE, CIRCUMFERENCE and 3301, upper and lower case, repeated.
- **S:** the scan-32 square cells mod 256, in spiral order, repeated.

**Rune readings.** Bytes mod 29 and base-60 digits mod 29, read as LP ciphertext and scored by `detect.log_lr` under:
a constant key (3 modes × 29 shifts, which includes Caesar, atbash and atbash + 3); the φ(prime) key; DIVINITY; and
FIRFUMFERENFE.

**Positive controls.** ASCII text encrypted with each byte operation and key must pass (a) after decryption.
LP plaintext in runes, encrypted as bytes with the φ key, must pass (c).

**Prediction.** Nothing passes.

**Not doing.** Unlisted keys, any optimiser, guessing at multi-layer schemes.

**Blast radius.** `tools/lpcore/keys.py` (hash parser), `tools/run_stage_n.py`, tests, docs.
**Rollback:** `git revert`.

## Owner items

- [ ] **Tokens in `.claude/mcp.vscode-reference.json`** (GitHub PAT, mem0, context7) are plaintext. They were never
  committed or pushed (full-history scan on 2026-09-29), so rotating them is optional. Consider VS Code `inputs`
  (`promptString`, `password: true`) instead of hardcoding them.

---

## Done

| Date | Stage | Result | Commits |
|---|---|---|---|
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
