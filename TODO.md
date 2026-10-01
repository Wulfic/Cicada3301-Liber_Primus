# TODO — Liber Primus

Plans are written here BEFORE code (AGENTS.md). Newest stage first within a session.

---

## 2026-10-01 — Stage G: organise the repo for clarity (owner request)

**Goal:** someone returning after a break, or new to the repo, can open `MASTER_TRACKER.md` and know exactly
where things stand and what's next; every folder's purpose is obvious from its name and its README.
**Approach:** `git mv` only (history kept); every changed link updated in the same commit; tests run before each commit.
**Rejected:** editing the old tracker body in place. It is ~1,400 lines, mostly invalidated, and correcting
it line by line would never finish. It is archived verbatim with a banner instead.
**Not doing:** no content changes to page files, canonical data, `tools/lpcore`, or archived files (apart from the banner);
no analysis work (D3 waits); no push.
**Blast radius:** paths of reference/data files that only docs link to (nothing in `tools/lpcore` or `tests` reads them; checked
with grep). One deletion: `data/key_search_corpus.txt`, a byte-identical copy (`cmp`) of
`reference/liber_primus_transcript.md`, tracked, so it can be restored from git.

- [ ] G1. `.gitattributes`: LF for text and explicit binaries. Renormalize, check that the diff is empty or EOL-only. Commit.
- [ ] G2. `reference/` → `sources/` (primary Cicada material), `community/` (others' research, tools, images), `findings/` (ours),
      `archive/`. `data/` → `canonical/`, `corpora/` (candidate key texts + wordlist), `outguess/` (+ the 3 hint files),
      `alternate_scans/`, `archive/` (`runes_full.txt` → `archive/legacy_inputs/`). A README in each folder. Links fixed. Commit.
- [ ] G3. `MASTER_TRACKER.md` → `reference/archive/MASTER_TRACKER_2026-04_pre-correction.md` (verbatim + banner). Write a new,
      short tracker: resume-here, status, established facts, refuted claims, open questions, rules, session log. Commit.
- [ ] G4. `README.md` (quick start + layout) and this file trimmed to active work, with done stages collapsed to one line + commit. Commit.

**Rollback:** each step is one commit → `git revert <sha>`.

---

## 2026-10-01 — Stage F: remove material from other projects + first commits ✅

**Owner request:** remove anything not specific to this project (no Ko-fi, no Minecraft), then commit stages A–F.
**Recoverable from:** every deleted item has an identical copy in `../mcMMO-Singleplayer` (checked with `cmp`, or
a line-subset check for the older `.agent/memory` snapshots). The old mcMMO `AGENTS.md` is blob `32ea074` = mcMMO commit `5c52196e4`.

- [x] F1. deleted `.agent/`: mcMMO memory + a 1.1 MB tarball. Undo: `cp -r ../mcMMO-Singleplayer/.agent .agent`
- [x] F2. deleted `.github/FUNDING.yml` (Ko-fi), `.github/workflows/{release,drift-audit}.yml` (mcMMO CI). Kept `sync.yml` (LP upstream sync).
- [x] F3. `AGENTS.md` rewritten for LP. It keeps the owner's general rules and drops the mcMMO band/gradle/audit material.
- [x] F4. `.gitignore` agent block de-mcMMO'd; the save-memory skill (both trees) no longer mentions band branches
- [x] F5. commits on `main`, one per stage group, no AI trailer, not pushed

---

## 2026-09-29 — Stage A: push safety ✅

**Goal:** nothing secret or foreign can reach `github.com/Wulfic/Cicada3301-Liber_Primus` on the next push.
**Blast radius:** none — `.gitignore` edits only.

- [x] A1. `.claude/mcp.vscode-reference.json` holds 3 plaintext bearer tokens (GitHub PAT, mem0, context7) → `.claude/` ignored.
- [x] A2. `.agent/` holds another project's (mcMMO) memory + a 1.1 MB backup tarball → ignored (also AGENTS.md rule R-n).
- [x] A3. `.github/skills/`, `CLAUDE.md`, `.mcp.json`, `.venv*/` ignored (R-n; `.venv_py311/` was 24 MB and unignored).
- [x] A4. Full `git log --all -p` scan for credential patterns → **clean** (nothing ever committed).
- [ ] A5. (owner) Tokens were never pushed, so rotation is optional; consider VS Code `inputs` (`promptString`, `password: true`) instead of hardcoding them in args.

**Rollback:** `git checkout HEAD -- .gitignore`

---

## 2026-09-29 — Stage B: canonical corpus + tested loader + page-file rebuild ✅

**Goal:** one canonical rune source, read by one tested loader, and every `pages/page_XX/runes.txt`
equal to the runes on scan `XX.jpg` in the same folder.

**Finding that forced this:** the page files were misaligned. `page_N/runes.txt` held LP2 page N
while `page_N/images/` holds complete-archive scan N.jpg, and LP1 text was stuffed into pages 57–74.
Verified by eye on scans 59, 66, 68. Tracker "discoveries" built on it are artifacts (see Stage C).

**Approach:** vendor the community master transcription (rtkd/iddqd `liber-primus__transcription--master.txt`,
commit `3089b65`, 2019-06-17). Verified **rune-for-rune identical** to `data/runes_full.txt` for all
57 LP2 rune pages; it additionally has per-scan LP1 pages, the numeric grids, and an empty page for
scan 67 (base-60 only) — which independently confirms the scan mapping found from the images.
**Rejected:** (a) keep `runes_full.txt` as canonical — LP2 only, no scan-67 placeholder, no LP1;
(b) hand-patch individual page files — the corruption is systemic (offset + duplication), patching misses cases.

**Not doing:** no hill-climbing / simulated annealing / GA / any optimiser (owner directive);
not deleting untracked analysis outputs; not touching `.agent/`; no commit or push without the owner's OK.

**Blast radius:** overwrites 75 tracked `pages/page_XX/runes.txt` + 75 `README.md`, all committed and
unmodified at HEAD `9ef4978`. 90 legacy tools read these files; they currently read the WRONG scan's
runes, so this changes their input on purpose. Everything else is additive.

- [x] B1. `data/canonical/liber_primus_master.txt` + `data/canonical/PROVENANCE.md` (URL, commit, sha256)
- [x] B2. `tools/lpcore/corpus.py` — parse master → pages keyed by scan number; lines, words, clause/paragraph/segment/chapter markers; gematria tables
- [x] B3. `tools/lpcore/ciphers.py` — deterministic primitives only: shift, atbash, Vigenère-SUB with interrupter skip, φ(prime) stream
- [x] B4. `tests/test_lpcore.py` — scan-mapping facts from the images; rune totals; **every solved section decrypts to its known plaintext** from canonical data. Run: `python -m unittest discover -s tests -v`
- [x] B5. `tools/rebuild_page_files.py` — dry-run by default, `--write` opt-in, refuses if `pages/` is dirty, logs counts; a test proves the dirty-refusal
- [x] B6. dry-run → read the output → `--write`
- [x] B7. regenerate each page `README.md` from canonical metadata (scan, LP part/page, section, status, rune count)

**Result:** 26 tests green (`python -m unittest discover -s tests -t . -v`). All 9 solved segments reproduce from canonical runes with only 2 documented errata (book typo WIDSOM; upstream translation typo FOLLWING). 150 page files rewritten; re-run reports 0 changes.

**Rollback:** `git checkout 9ef4978 -- pages/` ; new files are untracked → delete `data/canonical/ tools/lpcore/ tests/ tools/rebuild_page_files.py`

---

## 2026-09-29 — Stage C: tracker correction ✅

- [x] C1. `MASTER_TRACKER.md` — prepend "Data integrity correction (2026-09-29)"; list invalidated claims:
      two-time-pad overlaps · P27 == P44[0:234] · LP2 mirrors LP1 · P07/P08 "unsolved polyalphabetic" ·
      P59 reciprocal substitution · 71/83 key-length alternation · "SUB mode confirmed by GPU SA" ·
      P00 key-113 "Old English" · P02 "THE I IS I SAME AS THAT PILGRIM" · P65 decoded grid
- [x] C2. `README.md` status table rewritten against canonical page numbers

**Rollback:** `git diff MASTER_TRACKER.md README.md` then `git checkout HEAD -- <file>` (owner has uncommitted tracker edits — edit, don't rewrite)

---

## 2026-09-29 — Stage D: logic-only analysis (no optimisers) — findings: `reference/lp2_logic_findings_2026-09-29.md`, 35 tests green

**Goal:** facts about the unsolved cipher derived from clean data; every hypothesis test is one
deterministic decryption with a pre-declared pass/fail threshold, logged whether it passes or not.

- [x] D1. per-section statistics on canonical LP2: IoC, doublet rate, rune frequencies, Δ-distribution of consecutive runes
- [x] D2. predicted doublet rate per candidate cipher family, using solved LP plaintext as the plaintext model → which families survive the observed rate
- [~] D3. riddle-derived tests — done: the 3301 square is fully decoded (|3301 − p(F+1)|, Fibonacci F). Open: square-ordinal stream and word-value keys as skip-aware deterministic decodes (see findings §6)
- [x] D4. web check for post-2024 developments → `reference/community_research.md`

---

## 2026-09-29 — Stage E: tidy the file structure (owner request; archive location from the owner's 2026-05-29 tracker note)

**Goal:** `tools/` and `data/` show only trusted, tested material at top level; legacy hill-climb code and outputs are kept, labelled, and out of the way.
**Approach:** moves only — `git mv` for tracked files (history preserved), plain move for untracked; every move recorded in a manifest so it can be reversed mechanically.
**Rejected:** deleting the artifacts (irreversible for the untracked ones, and the owner asked to archive, not delete).
**Not doing:** no content edits to moved files (the owner's uncommitted edits to `tools/advanced_cipher_solver.py` and `data/key_anchors.json` move with them unchanged); not touching reference inputs (Emerson, Deor, wordlist, hints, outguess, alternate_scans, runes_full).
**Blast radius:** paths only. Legacy scripts that build paths relative to `__file__` will need `../..` instead of `..` — documented in `tools/legacy/README.md`.

- [x] E1. `tools/legacy/` ← every legacy `tools/*.py` (all but `__init__.py`, `rebuild_page_files.py`); `tools/legacy/README.md`
- [x] E2. `data/archive/hillclimbers/20260529/` ← tracked hill-climb outputs; `…/untracked/` ← never-committed outputs (git-ignored); `MOVES.txt` manifest; `README.md`
- [x] E3. README.md structure + tracker §0 pointer updated; full test suite green

**Result (2026-10-01):** 301 manifest rows, all verified in place (203 `git mv`, 98 untracked). Two duplicate
rows (`data/p21_30_{analysis,keyword_sweep}.txt` listed again under `untracked/`) were removed. Their real move
is the tracked row above them. Emptied dirs `data/{anchored_results,theory_runs,runeglish,p24_candidates_processed}`
were removed. 35 tests green. Nothing committed yet.
**Gotcha:** legacy scripts resolve the repo root as `Path(__file__).parent.parent`, which is now `tools/`, so they
fail with `FileNotFoundError`. That was left deliberately (see `tools/legacy/README.md`).

**Rollback:** reverse every line of `data/archive/hillclimbers/20260529/MOVES.txt` (`git mv <to> <from>` for tracked, move back for untracked).
