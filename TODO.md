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

- **Goal.** An ordered list of attacks that no constraint (C1–C20, L1–L5), ledger or stage has covered, each concrete
  enough to declare.
- **Approach.** Read the tracker, the findings register and the attack catalog. Re-derive one archived claim (the
  payload overlap, stage AA). Look at scans 32, 40 and 50.
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
   for this yet (stage AH).
4. The authors make mistakes (WIDSOM), so nothing may depend on perfect sync.

**What the one anomaly could be.** 86 doublets survive where 447 are expected. Five mechanisms fit L1–L4. M1 and M2 are
in [findings §7](reference/findings/lp2_logic_findings_2026-09-29.md). M3–M5 are new, and each makes a prediction nobody
has checked.

| | Mechanism | Predicts | Stage |
|---|---|---|---|
| M1 | A re-key whose replacement equals the original 19 % of the time (C8) | nothing further | — |
| M2 | A hand check that is 81 % reliable | nothing further | — |
| M3 | The rule cannot see some runes. 447 / 29 = 15.4 would-be doublets per rune, so 86 survivors is 5.6 runes' worth | The survivors sit on 5 or 6 rune identities, not 29. Named instance: a script that compared Latin spellings would miss the five runes with two spellings (U/V, C/K, S/Z, NG/ING, IA/IO), which gives 77 | AB |
| M4 | A perfect rule, then seams. The stream had no doublets at all, and a later step put unrelated runes side by side at 19 % of positions: inserted nulls, a second key layer that changes value there, or a transposition that keeps 81 % of neighbours | The seams are not at word ends (C1), line ends (L2) or a fixed period ≤ 32 (L3). Nulls at the needed rate would also stretch the words (stage AF) | AB, AF |
| M5 | The doublets are deliberate marks, such as key changes, and every accidental one was removed | The text between two marks has structure of its own | AC |

**The backlog, in the order I would run it.**

| Stage | What | New sources? | Cost | Why this rank |
|---|---|---|---|---|
| AA | The three OutGuess payloads are aligned byte for byte: XOR them | no | 1 hour | The only unexplained exact structure on disk. Key-free. Could give a three-message depth |
| AB | Anatomy of the 86 survivors: which runes, where in the word and line | no | 1 session | Separates M3 and M4 from M1 and M2 |
| AC | Label coincidences: alphabets fixed by two or three earlier runes, by offset in a line, page or clause, or by unit | no | 1 session | Key-free, and closes catalog row 12 and every key restart except per word |
| AD | Linear filters: keystreams that obey a recurrence mod 29 | no | 1 session | Key-free and immune to drift. Closes the community's LFSR lead up to order 3 |
| AE | Is any cipher rune tied to one plaintext letter (multiplicative or affine streams) | no | half a session | Key-free, for every multiplier key at once |
| AF | Word shapes: is LP2's segmentation that of its plaintext | no | half a session | Every word-based result assumes it. Tests M4 with nulls |
| AG | Scan overlay: red titles, initials, dots, cuneiform | scans on disk | 1–2 sessions | Data the master drops. Feeds AC and AI |
| AH | Provenance, missing OutGuess output, signed messages, the ledgers' own lists | network, owner's OK | 1 session | Stops AI and AL repeating the ledgers. Worth more if AA finds depth |
| AI | Named streams on the lag-1 difference, then consumed backwards, then φ(n)-type functions | no | 1 hour of compute each | Catalog row 11 at the one lag that is anomalous |
| AJ | The square as a generator: Fibonacci mod M as a prime index | no | 1 hour | The only recipe printed inside LP2. Low prior |
| AK | Grid as an RC4 key on the payloads' shared head; digest census against the AN END hash | no | half a session | Exact tests, so no false positives. Low prior |
| AL | Seeded hash chains and PRNGs (catalog row 22) | after AH | — | Cannot say what it adds until the ledgers' seed lists are read |

#### AA: the three OutGuess payloads are aligned byte for byte

**Fact** (re-derived today; AA's first commit pins it with a test). `data/outguess/page_17.bin`, `page_21.bin` and
`page_43.bin` are 58,152 bytes each. 17↔21 and 17↔43 agree on the first 1,417 and the last 1,953 bytes. 21↔43 agree on
the first 2,004 and the last 2,228. (`cmp` reports the first difference at bytes 1,418 and 2,005.) The archived tracker
recorded this in its §9.1. No current doc does, and stages R, W and Y treated the files as three unrelated keys.

**What that already implies.** The agreement starts and stops inside 8- and 16-byte blocks: 2,004 ≡ 4 mod 8 and mod 16,
and the 21↔43 difference ends at offset 55,923 ≡ 3 mod 8. Under ECB a changed block changes each byte with probability
255/256, so four agreeing bytes inside a changed block have chance 256⁻⁴ ≈ 2 × 10⁻¹⁰, at each end. CBC cannot
re-converge at all. So the files are related position by position. Two readings are left:

- **H-stream:** one keystream was XORed onto three messages that share a head and a tail (a stream cipher, counter
  mode, or a reused pad).
- **H-raw:** three high-entropy objects that share bytes, for example an extraction artefact of images built on one
  template.

**Test.** Under H-stream, P_a ⊕ P_b = M_a ⊕ M_b with no key. Over the bytes where a pair differs:
1. distinct values and χ² of the XOR against uniform (stage Y's distinct-byte statistic has an exact null);
2. the count and length of zero runs inside the middle, against Binomial(n, 1/256);
3. the same for the three-way XOR.

Text, hex, base64, bitmaps and any format with fixed fields fail uniformity by a wide margin. Controls: two texts under
one random pad must be flagged, and two independent random strings must not.

**If structured:** a three-message depth on about 54,000 bytes, and the next stage declares cribs. **If uniform:** each
file is head + independent noise + tail, payload work drops down this list, and tracker next-action 2 loses most of
its value.

#### AB: anatomy of the 86 survivors

Stage H asked where and when the survivors fall. Nobody has asked which runes they are. Tests on `leak.adjacent_pairs`:

1. Identity of the doubled rune: 29 cells with expectation 2.97, exact tail by simulation. M3 predicts 5 or 6 cells near 15.
2. The named M3 instance: every survivor on ᚢ ᚳ ᛋ ᛝ ᛡ.
3. Position: index in the word from each end, lengths of the words involved, column in the line from each end, line
   on the page, place in the clause.
4. Neighbours: the rune before and after each survivor against flat, and triples.

About 10 tests, Bonferroni. A hit names the mechanism. A clean miss removes M3 and narrows M4 to seams that ignore layout.

#### AC: label coincidences

**Statistic.** K_u = the number of pairs of positions that share a label u and hold the same rune. If the alphabet at
position i is any function of u(i), each label class is a monoalphabetic sample, and K_u sits near 1.79 × flat (C12's
figure) whatever the function or the tables. Stage Z used this for words and blocks. C12 is the case u = one earlier rune.

**Labels not yet tried:**
- **Two or three earlier cipher runes:** (c_{i−a}, c_{i−b}) for 1 ≤ a < b ≤ 12, and (c_{i−1}, c_{i−2}, c_{i−3}).
  Findings §10 left these open as "too sparse for χ²", but pair counts are not sparse: 841 contexts give about 88,000
  pairs (estimate: 40 σ for two runes, 9 σ for three). This covers c_i = p_i + f(c_{i−1}, c_{i−2}) for any f, including
  a Fibonacci-lag autokey.
- **Offset from the start or end of a line, page, clause or paragraph.** This covers a key that restarts there (C20
  covers words only, the ledger covers sections) and any alphabet chosen by column.
- **Unit membership:** the same clause, paragraph or page, or the same stretch between two survivors (M5), alone and
  crossed with i mod L for L = 2…40. This covers units that each have their own short key, which smears across lags
  and escapes C9.

**Null:** flat, with exact mean and variance. **Positive controls:** `keys.encrypt_dodging` variants at LP2's sizes.
**Limits:** a flat stream on top hides everything, and offset labels lose power when a re-key consumes key, so they
are good for short units only.

#### AD: linear filters

If k_i = a_1·k_{i−1} + … + a_m·k_{i−m} (mod 29), then y_i = c_i − Σ a_j·c_{i−j} is the same filter applied to the
plaintext. It has no key in it, and it is local, so drift does not matter. Scan all 841 filters of order 2 and all
24,389 of order 3. The statistic is χ² of y against flat. Each filter's expected value comes from the solved plaintext
before the run, and filters with too little power are declared untestable.

Covers: LFSRs mod 29 up to order 3 (the lead in `reference/community/community_research.md` §7a; an order-3 register
can have period 24,388, beyond C9's reach), tribonacci-type streams, and polynomial keys of degree below m under a
drifting rule, where the catalog's periodicity note leaves periods 26–1000 open. Not covered: binary LFSRs mapped to
runes, which are not linear mod 29.

#### AE: is any cipher rune tied to one plaintext letter?

**Model.** c_i = a_i·(p_i − x) + y for any multiplier stream a_i ≠ 0: a multiplicative or affine Vigenère. Rune y then
appears exactly where plaintext x does, so y's profile over word positions copies x's.

**Test.** A 29 × class contingency table (first, last, interior, single-rune word; word length; first in clause)
against independence, with each letter's expected profile taken from the solved text. Flat unigrams already limit x to
letters near 1/29. An additive stream with a flat key predicts exact independence, so this also catches any key that
follows word structure.

#### AF: word shapes

Every word-based result (C1, C7, C20, every crib) assumes one cipher rune per plaintext rune with the word breaks kept.
Pinned numbers: LP2 has 12,956 runes in 2,896 words (4.47 per word), and the solved text has 2,901 in 726 (4.00).

**Test.** LP2's word-length and clause-length histograms against each solved section and against Emerson spelled in
runes; the share of single-rune words; repeats of word-length n-grams. A refrain shows up in word lengths without a
key, and the solved koan is the positive control.

**M4 with nulls.** It needs 2ρ/29 = 86/12,947, so ρ = 9.6 % of runes are nulls, which leaves 4.04 real runes per word.
That match is a curiosity until this test says whether 4.47 is ordinary for English in runes. Nulls also predict about
3.1 % repeats at lag 2, against 3.38–3.69 % over lags 2–10 (`test_only_lag_one_is_depleted`).

#### AG: scan overlay

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

**Uses.** Exact title spans (titles are the only cribs with known boundaries); sub-section starts as labels for AC;
dot and cuneiform numbers as named values for AI; a check on M5 (do the marks line up with survivors?).

#### AH: primary sources

1. `data/outguess/` has no README. Record which image, tool and key produced each file.
2. Fetch the OutGuess output of the other scans (the community lists 65 and 68–71; rtkd/iddqd `lp_outguessed/`). This
   is worth doing only if AA finds depth, where each further payload is a further message.
3. Put Cicada's signed messages in `reference/sources/` with their `gpg --verify` results, so that hints such as "its
   words are the map, their meaning is the road, and their numbers are the direction" stop being memory-tier.
4. Read both ledgers' own lists: the 46 sequences and what "chain form" means, and Dukotah's generators and seeds.

Needs network access and the owner's OK.

#### AI: named streams on the lag-1 difference

Every named-key test so far decoded c itself. Catalog row 11 (an earlier cipher rune plus a stream) is open, and lag 1
is the only lag with an anomaly.

**Model.** c_i − c_{i−1} = p_i ± k_i, and the same for the sum. The "rule" then reads "the keyed value is never 0".

**Families**, each its own declaration, through `detect.log_lr` on the differenced text:
1. stage I's three streams and stage R's 25 sources;
2. the same streams consumed backwards from each section's end;
3. arithmetic functions of the index (φ(n) and relatives) from any start, minus whatever AH item 4 shows the ledgers ran.

Do not include the multiplicative chain c_i = c_{i−1} + (p_i − x)·k_i: C3 excludes it.

#### AJ: the square as a generator

The square is the only recipe printed inside LP2, and it sits directly above section 11. Its 16 cells stop at F = 987
only because the square is full.

**Model.** k_n = (3301 − p((F_n mod M) + 1)) mod 29, for a short declared list of moduli M whose Pisano period exceeds
1,000 (C9 covers the rest), signed and unsigned, per section and continuous, from any start. A few hundred decodes
through `detect.log_lr`.

#### AK: the grid, the payloads' head and the hash

1. The grid is 256 bytes, which is the longest key RC4 accepts. XOR RC4's output (grid in 4 readings, declared drop
   counts) onto the 1,417-byte shared head. Pass if the result has few distinct bytes, by stage Y's statistic.
2. Digest census. SHA-512, Whirlpool, SHA3-512, Keccak-512 and BLAKE2b of every object on disk (75 scans, the
   payloads and their shared parts, the hint files, the grid in 4 readings, the solved text in declared
   serialisations) against the AN END hash. SHA-256, SHA-1 and MD5 against windows of the grid. A pass is an exact
   match, so the family's size costs nothing.

#### AL: seeded generators (catalog row 22)

Hash chains and counters (SHA-512, Whirlpool, SHA-256, MD5), RC4, and Python 2's Mersenne Twister, seeded with the
book's words and numbers, mapped to runes by mod and by rejection. Blocked on AH item 4: Dukotah's ledger already ran
"common KDFs and PRNGs", and without its seed list this stage cannot say what it adds.

**Considered and dropped.**

| Idea | Why it is out |
|---|---|
| A null inserted between two equal cipher runes | It would add about 361 repeats at lag 2. C5 |
| A second layer with one shift per word | It predicts no doublets inside words and about 3.5 % across them. C1 |
| Runes written along a spiral or by columns, then read by rows | Line-end pairs would be at chance, 20 expected. L2 has 4 of 585 |
| A multiplicative chain where a doublet is one plaintext letter | C3, all 29 letters |
| A key built from shuffled decks, so the key never repeats a value | The cipher's doublet rate does not depend on equal key neighbours. C4's formula gives about 3.5 % |
| A running sum of plaintext or ciphertext as the key, or any key updated linearly from the previous rune | c_i − a·c_{i−1} is then a function of two plaintext runes, which C12 sees at lag 1. This is an argument, not a test; AC's two-rune label makes it one |
| The grid as an RSA signature by 7A35090F | Wrong size (findings §22, X3) |
| LP2 as base-29 or base-28 data, a file and not text | Parked. No test proposed, and the word and clause marks would be decoration |
| Section illustrations as method hints (roots, the loop, cuneiform) | Themes until AG turns them into values |

**Detector upgrade, not a hypothesis.** Emissions by position in the word (a single-rune word is A or I) would raise
the power of `detect.log_lr` per rune. Worth doing before AI and AJ.

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
