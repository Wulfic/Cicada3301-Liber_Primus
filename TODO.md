# TODO — Liber Primus

The working plan. **Write a plan here before the first edit** (AGENTS.md): goal, approach, rejected
alternatives, what you're *not* doing, blast radius, rollback. When a stage is done, collapse it to one line
under "Done" with its commits. The full text stays in git history. Status and next research steps live in
[`MASTER_TRACKER.md`](MASTER_TRACKER.md) §1, not here.

---

## Active

### Idea backlog, 2026-11-13: what has not been tried

**Ideas only. Nothing below is declared or run.** Each stage still needs its own declaration (model, family size,
thresholds, controls) committed before its first run. Figures marked "estimate" are for ranking and get replaced by
control measurements then.

- **Goal.** An ordered list of attacks that no constraint (C1–C28, L1–L5), ledger or stage has covered, each concrete
  enough to declare.
- **Revised 2026-11-13 (same day).** The draft named its stages AA–AL, which collided with the finished stages AA–AH
  (findings §25–§32, C21–C28). They are renumbered AI–AT in the same order. The draft was also written against
  C1–C20. Where C21–C28 already cover part of a stage, that stage now says so: AK (offset labels are C22),
  AL (C23 covers in-step periods), AQ (C27 and C28 add sources) and AR (C22 and C23 shrink the moduli).
- **Approach.** Read the tracker, the findings register and the attack catalog. Re-derive one archived claim (the
  payload overlap, stage AI). Look at scans 32, 40 and 50.
- **Not done in this pass.** No LP2 statistic was computed, no code was written, nothing was fetched, nothing is committed.
- **Blast radius.** This file and one pointer line in the tracker. **Rollback:** `git restore TODO.md MASTER_TRACKER.md`.

**How Cicada has worked so far.** These are style priors from the solved material, not constraints.

1. The key is announced in the book before it is used. DIVINITY and CIRCUMFERENCE are plaintext words, and "the primes
   are sacred, the totient function is sacred" comes before AN END's φ(prime) stream. The last announcements we hold are
   "a page that hashes to" (a 512-bit digest) and "shed our own circumferences, find the divinity within".
2. A worked example comes before the real thing. The scan-32 square computes 3301 − p(F + 1) along a spiral, and its
   start cell is printed in red.
3. Outside the book, each stage from 2012 to 2014 hid the next step in an artefact (OutGuess in a JPEG, two files to
   XOR, trailing whitespace), not in harder mathematics. Tier: memory and community. The repo holds no primary source
   for this yet (stage AP).
4. The authors make mistakes (WIDSOM), so nothing may depend on perfect sync.

**What the one anomaly could be.** 86 doublets survive where 447 are expected. Five mechanisms fit L1–L4. M1 and M2 are
in [findings §7](reference/findings/lp2_logic_findings_2026-09-29.md). M3–M5 are new, and each made a prediction nobody
had checked. Stage AJ (findings §34) has since excluded M3 and confined M4 to seams that ignore layout.

| | Mechanism | Predicts | Stage |
|---|---|---|---|
| M1 | A re-key whose replacement equals the original 19 % of the time (C8) | nothing further | — |
| M2 | A hand check that is 81 % reliable | nothing further | — |
| M3 | The rule cannot see some runes. 447 / 29 = 15.4 would-be doublets per rune, so 86 survivors is 5.6 runes' worth | The survivors sit on 5 or 6 rune identities, not 29. Named instance: a script that compared Latin spellings would miss the five runes with two spellings (U/V, C/K, S/Z, NG/ING, IA/IO), which gives 77 | **Excluded by AJ** (L6, findings §34): 32 on the top six, 10 on the five |
| M4 | A perfect rule, then seams. The stream had no doublets at all, and a later step put unrelated runes side by side at 19 % of positions: inserted nulls, a second key layer that changes value there, or a transposition that keeps 81 % of neighbours | The seams are not at word ends (C1), line ends (L2) or a fixed period ≤ 32 (L3). Nulls at the needed rate would also stretch the words (stage AN) | AN. AJ (§34): the survivors ignore word, line, page and clause position |
| M5 | The doublets are deliberate marks, such as key changes, and every accidental one was removed | The text between two marks has structure of its own | AK (§35): no stretch between survivors has its own key of period ≤ 40. Longer or slipping keys open |

**The backlog, in the order I would run it.**

| Stage | What | New sources? | Cost | Why this rank |
|---|---|---|---|---|
| AL | Linear filters: keystreams that obey a recurrence mod 29 | no | 1 session | Key-free and immune to drift. Closes the community's LFSR lead up to order 3 |
| AM | Is any cipher rune tied to one plaintext letter (multiplicative or affine streams) | no | half a session | Key-free, for every multiplier key at once |
| AN | Word shapes: is LP2's segmentation that of its plaintext | no | half a session | Every word-based result assumes it. Tests M4 with nulls |
| AO | Scan overlay: red titles, initials, dots, cuneiform | scans on disk | 1–2 sessions | Data the master drops. Feeds AQ; sub-sections would be new unit labels for AK's test |
| AP | Provenance, missing OutGuess output, signed messages, the ledgers' own lists | network (pre-approved) | 1 session | Stops AQ and AT repeating the ledgers. AI found no depth, so item 2a (reproduce the extraction) comes before item 2 |
| AQ | Named streams on the lag-1 difference, then consumed backwards, then φ(n)-type functions | no | 1 hour of compute each | Catalog row 11 at the one lag that is anomalous |
| AR | The square as a generator: Fibonacci mod M as a prime index | no | 1 hour | The only recipe printed inside LP2. Low prior |
| AS | Grid as an RC4 key on the payloads' shared head; digest census against the AN END hash | no | half a session | Exact tests, so no false positives. Low prior |
| AT | Seeded hash chains and PRNGs (catalog row 22) | after AP | — | Cannot say what it adds until the ledgers' seed lists are read |

#### AL: linear filters

If k_i = a_1·k_{i−1} + … + a_m·k_{i−m} (mod 29), then y_i = c_i − Σ a_j·c_{i−j} is the same filter applied to the
plaintext. It has no key in it, and it is local, so drift does not matter. Scan all 841 filters of order 2 and all
24,389 of order 3. The statistic is χ² of y against flat. Each filter's expected value comes from the solved plaintext
before the run, and filters with too little power are declared untestable.

**Design check (2026-11-14, session ended before the declaration; no LP2 statistic computed).** Figures are from
scratch scripts on Emerson and synthetic streams. The runner's controls must reproduce them before they are cited.
- **The draft's χ² is too weak at order 3.** Noncentrality of y = A(D)p against flat at LP2's length (4-gram DFT of
  Emerson): order 1 433–1,510; order 2 68–1,128, median 175; order 3 12.6–816, median 47. About 80 % of order-3
  filters would be untestable.
- **Replacement statistic.** An exact forward algorithm over the last m key values (29^m states, uniform prior on the
  initial state). At each step the key is the recurrence's next value, or with probability ε a free value that the
  state keeps. That one term absorbs feedback re-keys, glitches and slips. The emission is 29·q(c − k), with q from
  `detect.unigram` over the solved text. At ε = 0 it equals brute-force enumeration of the initial states (checked to
  10 decimals, orders 1–3).
- **ε = 0.03**, the re-key rate C8 implies (0.81 × 3.45 % ≈ 2.8 %). At ε = 0.10 the order-3 null log LR in short
  sections does not reach −10.
- **Anytime thresholds (Ville).** Check the running log LR every 8 runes per section. It fires at +30 and is
  excluded at −10, with the same e^−30 / e^−10 bounds as final-value rules. Design controls, 8 section lengths,
  10 random taps per order:
  - positives fire 240 / 240 per order (feedback re-key; glitch + 1 % slips; feedback + 1 % slips);
  - nulls (Emerson, flat key, anti-doublet) are excluded 160 / 160;
  - the lowest positive dip is −7.7 (order 3, feedback + slips), and the highest null peak is +5.2.
  - Under the null a pass uses 5 / 10 / 16 % of the runes (orders 1 / 2 / 3).
- **Cost.** A full order-3 pass is 1.04 s in numpy (`alpha[src]` gather, row-sum trick, renormalise every 8).
  Throughput tops out at about 5 passes/s on 8 workers because of cache pressure. With sequential exits, the
  47,096 order-3 filter-mode runs take about 30 min. Beaufort is the subtract mode on −c, and add ≡ subtract.
- **Family.** 24,388 tap vectors (28 / 812 / 23,548) × 2 modes × 8 sections (segment 10 untestable). Of the order-3
  vectors, 4,752 have period 12,194 (1,584) or 24,388 (3,168), beyond C23; the next largest period is 6,097. A
  feedback re-key or a slip makes every order aperiodic, so C9 and C23 do not cover those cases.
- **Archived claim.** The 2026-03 "LFSR(2)/(3), 0 candidates" runs used misaligned pages, an exact I/A singleton
  constraint and fixed sync. They are not evidence.
- **Next.** Write the declaration from these figures, then add a new lpcore recurrence module, runner and tests.
  Commit those before LP2 is scored.

Covers: LFSRs mod 29 up to order 3 (the lead in `reference/community/community_research.md` §7a; an order-3 register
can have period 24,388, beyond C23's 11,781), tribonacci-type streams, and polynomial keys of degree below m under a
drifting rule. Not covered: binary LFSRs mapped to runes, which are not linear mod 29. **Overlap:** an order-2
register has period ≤ 840, so C23 already excludes it in step. What this stage adds there is immunity to drift. For
order 3 it adds the periods above 11,781 as well.

#### AM: is any cipher rune tied to one plaintext letter?

**Model.** c_i = a_i·(p_i − x) + y for any multiplier stream a_i ≠ 0: a multiplicative or affine Vigenère. Rune y then
appears exactly where plaintext x does, so y's profile over word positions copies x's.

**Test.** A 29 × class contingency table (first, last, interior, single-rune word; word length; first in clause)
against independence, with each letter's expected profile taken from the solved text. Flat unigrams already limit x to
letters near 1/29. An additive stream with a flat key predicts exact independence, so this also catches any key that
follows word structure.

#### AN: word shapes

Every word-based result (C1, C7, C20, every crib) assumes one cipher rune per plaintext rune with the word breaks kept.
Pinned numbers: LP2 has 12,956 runes in 2,896 words (4.47 per word), and the solved text has 2,901 in 726 (4.00).

**Test.** LP2's word-length and clause-length histograms against each solved section and against Emerson spelled in
runes; the share of single-rune words; repeats of word-length n-grams. A refrain shows up in word lengths without a
key, and the solved koan is the positive control.

**M4 with nulls.** It needs 2ρ/29 = 86/12,947, so ρ = 9.6 % of runes are nulls, which leaves 4.04 real runes per word.
That match is a curiosity until this test says whether 4.47 is ordinary for English in runes. Nulls also predict about
3.1 % repeats at lag 2, against 3.38–3.69 % over lags 2–10 (`test_only_lag_one_is_depleted`).

#### AO: scan overlay

Seen on scans 32, 40 and 50 today, and absent from `data/canonical/liber_primus_master.txt`:
- Section and sub-section titles are in red and end at a red dotted mark. The first rune is a large red initial.
- The square's start cell, 3299, is red.
- Scan 40 has five black dots. Scan 50 has three, unevenly spaced.
- Scan 50 ends with two lines of cuneiform. `reference/community/images/Symbols_page34.png` reads them as 10·7·10·3
  and 50·5·1.
- Scan 32 has a hand-drawn loop between the square and section 11.

**Deliverable.** A tested overlay file: per scan, the red spans as rune offsets, the initials, dot centres in pixels,
numerals and drawings. A script builds it from the JPGs where it can; the rest is entered by eye. Canonical stays
untouched.

**Uses.** Exact title spans (titles are the only cribs with known boundaries); sub-section starts as new unit labels for AK's test (C29 used only the master's units);
dot and cuneiform numbers as named values for AQ; a check on M5 (do the marks line up with survivors?).

#### AP: primary sources

1. `data/outguess/` has no README. Record which image, tool and key produced each file.
2. ~~Fetch the OutGuess output of the other scans~~ **Demoted by stage AI (findings §33).** The payloads are not a
   byte-oriented depth, and look like default-key extraction artefacts. More of them would add extraction runs, not
   messages. Fetch them only if item 2a fails.
2a. **Reproduce the extraction.** Run `outguess -r` with no key on scans 17, 21 and 43 (and check whether those are
   the right images, see item 1). Byte-identical output proves H-raw and closes the payloads as key material. Any
   difference is the first real evidence of an embedded message. Needs an OutGuess build, or a JPEG coefficient reader
   plus OutGuess's iterator in Python, checked against a known stego file.
3. Put Cicada's signed messages in `reference/sources/` with their `gpg --verify` results, so that hints such as "its
   words are the map, their meaning is the road, and their numbers are the direction" stop being memory-tier.
4. Read both ledgers' own lists: the 46 sequences and what "chain form" means, and Dukotah's generators and seeds.

Network access is pre-approved by the owner (2026-11-13).

#### AQ: named streams on the lag-1 difference

Every named-key test so far decoded c itself. Catalog row 11 (an earlier cipher rune plus a stream) is open, and lag 1
is the only lag with an anomaly.

**Model.** c_i − c_{i−1} = p_i ± k_i, and the same for the sum. The "rule" then reads "the keyed value is never 0".

**Families**, each its own declaration, through `detect.log_lr` on the differenced text:
1. stage I's three streams, stage R's 25 sources, and the 22 streams of C27 and C28 (stages AG and AH tested those on
   c itself, not on the difference). `tools/run_stage_ag.py` takes any key-value list unchanged;
2. the same streams consumed backwards from each section's end;
3. further arithmetic functions of the index beyond C28's six, minus whatever AP item 4 shows the ledgers ran.

Do not include the multiplicative chain c_i = c_{i−1} + (p_i − x)·k_i: C3 excludes it.

#### AR: the square as a generator

The square is the only recipe printed inside LP2, and it sits directly above section 11. Its 16 cells stop at F = 987
only because the square is full.

**Model.** k_n = (3301 − p((F_n mod M) + 1)) mod 29, for a short declared list of moduli M, signed and unsigned,
continuous, from any start. A few hundred decodes through `detect.log_lr`. **Overlap:** the key is periodic with the
Pisano period π(M). C23 excludes every in-step period from 11 to 11,781, so only moduli with π(M) > 11,781 are new in
step (π(M) ≤ 6M, so M > 1,963). A key that restarts per section is C22. Smaller moduli and per-section restarts
add only drift tolerance, so declare them as such or drop them.

#### AS: the grid, the payloads' head and the hash

1. The grid is 256 bytes, which is the longest key RC4 accepts. XOR RC4's output (grid in 4 readings, declared drop
   counts) onto the 1,417-byte shared head. Pass if the result has few distinct bytes, by stage Y's statistic.
2. Digest census. SHA-512, Whirlpool, SHA3-512, Keccak-512 and BLAKE2b of every object on disk (75 scans, the
   payloads and their shared parts, the hint files, the grid in 4 readings, the solved text in declared
   serialisations) against the AN END hash. SHA-256, SHA-1 and MD5 against windows of the grid. A pass is an exact
   match, so the family's size costs nothing.

#### AT: seeded generators (catalog row 22)

Hash chains and counters (SHA-512, Whirlpool, SHA-256, MD5), RC4, and Python 2's Mersenne Twister, seeded with the
book's words and numbers, mapped to runes by mod and by rejection. Blocked on AP item 4: Dukotah's ledger already ran
"common KDFs and PRNGs", and without its seed list this stage cannot say what it adds.

**Considered and dropped.**

| Idea | Why it is out |
|---|---|
| A null inserted between two equal cipher runes | It would add about 361 repeats at lag 2. C5 |
| A second layer with one shift per word | It predicts no doublets inside words and about 3.5 % across them. C1 |
| Runes written along a spiral or by columns, then read by rows | Line-end pairs would be at chance, 20 expected. L2 has 4 of 585 |
| A multiplicative chain where a doublet is one plaintext letter | C3, all 29 letters |
| A key built from shuffled decks, so the key never repeats a value | The cipher's doublet rate does not depend on equal key neighbours. C4's formula gives about 3.5 % |
| A running sum of plaintext or ciphertext as the key, or any key updated linearly from the previous rune | c_i − a·c_{i−1} is then a function of two plaintext runes, which C12 sees at lag 1. Now a test: C29 (stage AK, §35) excludes any alphabet chosen by two or three earlier cipher runes |
| The grid as an RSA signature by 7A35090F | Wrong size (findings §22, X3) |
| LP2 as base-29 or base-28 data, a file and not text | Parked. No test proposed, and the word and clause marks would be decoration |
| Section illustrations as method hints (roots, the loop, cuneiform) | Themes until AO turns them into values |

**Detector upgrade, not a hypothesis.** Emissions by position in the word (a single-rune word is A or I) would raise
the power of `detect.log_lr` per rune. Worth doing before AQ and AR.

## Owner items

- [ ] **Tokens in `.claude/mcp.vscode-reference.json`** (GitHub PAT, mem0, context7) are plaintext. They were never
  committed or pushed (full-history scan on 2026-09-29), so rotating them is optional. Consider VS Code `inputs`
  (`promptString`, `password: true`) instead of hardcoding them.

---

## Done

| Date | Stage | Result | Commits |
|---|---|---|---|
| 2026-11-14 | **AK** label coincidences | Declared first (`59c5b56`), replacing the draft's flat null (biased +3.5 % by a shared c_{i−1}) with a simulated one; runner committed before LP2 was scored (`729d34f`). 307 labels: 66 two-rune contexts (lags ≤ 12), the three-rune context, 6 units × own period-L key (L = 1–40). Controls valid (negative max z 3.60; positive z 9.2–471). **Nothing fires** (max z 3.29). 285 excluded, line × 18 not excluded, 21 untestable or empty → **C29**, findings §35 | `59c5b56` `729d34f` + this |
| 2026-11-14 | **AJ** anatomy of the 86 survivors | Declared first (`45bc943`); runner committed before LP2 was scored (`8e31dc6`). 17 statistics against 10⁶ uniform draws of 86 pairs, family α = 10⁻³. Controls valid; T4 (word class, not blind) untestable by its planted control. **Nothing fires** (min p = 0.011). M3 excluded (power 100 / 100 at φ ≥ 0.5), survivors ignore layout, no neighbour or triple signature → **L6**, findings §34 | `45bc943` `8e31dc6` + this |
| 2026-11-13 | **AI** OutGuess payload depth | Backlog renumbered AI–AT, C21–C28 overlaps marked (`2680879`). Declared first (`9d79642`), replacing the draft's uniformity test, which an extraction artefact also fails. Runner committed before the payloads were scored (`2cfaa6d`). 248 controls valid. **RELATED**: bits agree 51.5 % (z ≥ 20) but flat by bit phase (S1 p ≥ 0.37). No byte-oriented depth, so nothing to crib; AP item 2 demoted, 2a added → findings §33 | `9d79642` `2cfaa6d` + this |
| 2026-10-12 | **AH** totient and arithmetic-function keys | Declared first (`17cba27`); runner committed before LP2 was scored (`ce81da6`). 12 keys (φ(n), σ(n), Σφ, prime gaps, φ(φ(n)), n·φ(n); raw and chain), stage AG's family, 10,440 decodes. Controls pass for all 12. **No pass** (best real −47.9). **C28:** all 324 testable cells excluded. Prediction met → findings §32 | `17cba27` `ce81da6` + this |
| 2026-10-12 | **AG** base-29 constants as the key | Declared first (`7c83e52`); digit generators and runner committed before the full run (`5e8c507`; its `--quick` had scored 120 declared decodes, disclosed). 10 sources × 3 modes × 29 shifts × 10 alignments, starts < 1000. Controls pass for all 10. **No pass** (best real −56.0). **C27:** all 270 testable cells excluded; only segment 10 (9 runes) untestable. Prediction met → findings §31 | `7c83e52` `5e8c507` + this |
| 2026-10-12 | **AF** shifted restarts | Declared first (`e2e305f`); runner committed before LP2 was scored (`adea288`). Within-unit difference agreement across units, gaps 2–300, 5 unit types; 200 nulls, 100 controls per source (additive and Beaufort, random per-unit shifts). Valid. **No pass; all 5 excluded (C26)**, prediction met → findings §30 | `e2e305f` `adea288` + this |
| 2026-10-12 | **AE** periodic keys under any alphabets | Declared first (`434060d`); runner committed before LP2 was scored (`fb202c8`, the full suite was run after that commit rather than before it: green, 244). Exact lag agreements over the continuous stream, binomial PASS and exclusion rules. Valid; controls 100 / 100 caught, 0 excluded (lowest rate 0.0520 vs p_H 0.050, disclosed). **No pass. C25:** periods 11–4,907 all excluded, 10,030 / 12,935 lags overall. Declared "exclusions for L ≲ 9,600" met in part: complete only to 4,907, because by-chance high lags leave gaps → findings §29 | `434060d` `fb202c8` + this |
| 2026-10-12 | **AD** ciphertext as its own key | Declared first (`03dad0b`); runner committed before LP2 was scored (`1b0007a`). Plaintext-law score (detect's emission, 0.312 nats per pair), 4 relations × 29 shifts, F per forward diagonal (autokey at lag L), S best segment forward and reverse. Controls: P_max 12,900, M_min 200. Valid. **No pass** (F 5.30, S 23.16 vs null 23.26). **C24:** all 1,490,948 hypotheses at L ≤ 12,863 excluded. Prediction met. Erratum on the declared family sizes of AC and AD (lag count), no bound changes → findings §28 | `03dad0b` `1b0007a` + this |
| 2026-10-12 | **AC** key reuse at any lag | Declared first (`b2f22d9`); "sumrev" (Beaufort reflection of the sum law) added before LP2 was scored and committed with the runner (`a11ec86`). Labelled per-pair score, 3 relations × 29 shifts; F per forward diagonal (periodic key, L = 11–12,945), S best segment per forward and reverse diagonal (reused stretch). Controls: P_max 12,500 (all periodic draws F > −10), M_min 3,000 (300 / 300 found; 2,500 missed 2). Valid (4 null scans, F ≤ 10.15, S ≤ 20.39). **No pass** (F 7.05, S 19.86). **C23:** plain periods 11–11,781 excluded, 1033 / 1729 / 3301 under all 87 relations; 1,081,691 / 1,086,630 hypotheses excluded. Prediction met ("M_min ≈ 2,000–2,500" was one step optimistic) → findings §27 | `b2f22d9` `a11ec86` + this |
| 2026-10-12 | **AB** key restarting at written units | Declared first (`78f7c37`); `Corpus.rune_units` and the runner committed before LP2 was scored (`a2512ca`). Label-free K_u = pairs of units agreeing at the same in-unit position, for 9 sections, 15 paragraphs, 168 clauses, 594 lines and 55 pages. 1,000 flat nulls; 200 Emerson and 200 shuffled solved-LP controls per unit, each with a fresh alphabet per in-unit position shared by all units. Valid (a 50-draw `--quick` line offset of 2.1 s.e. was checked on 400 null-only draws, 0.7 s.e.; runner unchanged). **No pass; all 5 excluded (C22)**, prediction met. Line z = 2.98, below the null maximum: recorded, not interpreted → findings §26 | `78f7c37` `a2512ca` + this |
| 2026-10-12 | **AA** keyless sliding-context ciphers | Declared first (`5364609`); runner committed unchanged before LP2 was scored (`eacdc01`). Any c_i = F(plaintext window of width w), no key, keeps the plaintext's (n + w)-window repeats as cipher n-gram repeats. K_n = separated pairs of equal sliding n-grams, n = 3–7, sec and cont: 10 cells. 1,000 flat nulls; 200 Emerson and 200 shuffled solved-LP controls per (mode, w = 0–12), each with a fresh random permutation per context. Valid (null means within 3 s.e. of analytic for n ≤ 5). **No pass; LP2 at the null in all 10 cells (\|z\| ≤ 1.26). C21:** w ≤ 2 (sec) and w ≤ 1 (cont) excluded, 21 widths untestable. Declared expectation "excluded up to w ≈ 4–7" failed: Emerson's right tail holds the log-scale bound down, although every draw clears the null up to w = 7 (observation only). Verdicts TSV added to the outputs while writing the runner (tabulation only) → findings §25 | `5364609` `eacdc01` + this |
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
