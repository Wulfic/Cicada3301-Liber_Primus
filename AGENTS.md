# Agent Instructions — Liber Primus

The goal is to solve the unsolved pages of Cicada 3301's Liber Primus with work that anyone can
reproduce and test. Work like a senior developer with zero patience for slop. Be direct, and assume
a result is wrong until a test proves it. Don't pad reports with praise: silence means "no
objection". When something is wrong, say so plainly and fix it.

## Sources of truth

| What | Where |
|---|---|
| Rune text (LP1 + LP2) | `data/canonical/liber_primus_master.txt`. Load it **only** through `tools/lpcore/corpus.py` |
| Proof the data and core are right | `python -m unittest discover -s tests -t . -v` (every solved section must decrypt) |
| What is known, refuted and open | `MASTER_TRACKER.md` (start at §1 "Resume here"), then `reference/findings/lp2_logic_findings_2026-09-29.md` |
| Current plan and progress | `TODO.md` |
| Repo layout | `README.md` |

⚠️ **Anything written before 2026-09-29 is suspect.** Until then the page files were misaligned:
`pages/page_N/runes.txt` held LP2 page N, not the runes on scan N.jpg. Claims built on them are
listed as invalid in `MASTER_TRACKER.md` §4.3. Re-derive any older claim from canonical data before
you build on it. The old scripts and their outputs are in `tools/legacy/` and
`data/archive/hillclimbers/`. They are history, not evidence.

## Research rules (owner directives)

- **No hill-climbing, simulated annealing, genetic algorithms or any other optimiser.** Their
  output is not evidence. Use logic and deterministic tests only.
- **A hypothesis test is one deterministic decryption with a pass/fail threshold declared before
  the run.** Write the prediction down first (in `TODO.md` or the test), then run it, and record
  the result whether it passed or failed.
- **Check the exclusion list before proposing an attack.** It is in the findings doc (§1 community
  ledgers, §2 constraints C1–C7, §6 open items). Re-running an excluded attack wastes the session.
- **Key tests must handle skips.** About 3 % key desync (interrupters) defeats a naive decode.
- **Every number cited in a doc has a test or a named script that reproduces it.**

## Destructive actions — rule zero

An action is destructive if a mistake would lose state that isn't reproducible from what's on disk
and committed: deleting or overwriting files (including writing a file you never read),
`reset --hard`, `clean -fd`, `checkout -- .`, `branch -D`, `stash drop`, `--amend`, rebase,
`push --force`, deleting tags or releases, and anything outward-facing (publishing, pushing,
closing issues).

Five gates, in order, every time:

1. **Resolve the target.** `ls` it and print the variable. Act on what you just read, never on the
   pattern you typed.
2. **Prove it's recoverable.** Name the copy (a commit, or a verified backup). If there is none,
   make one first.
3. **Dry-run it.** For example `git clean -nd`, or a tool's `--dry-run`. Read the output.
4. **Narrow the scope.** Act on the file, not the directory. Never put a destructive command
   inside a `&&` chain or a loop.
5. **Write the undo**, then confirm with the owner and quote the exact command.

Code that deletes or overwrites ships with its own guards: dry-run by default with `--write` or
`--force` to opt in, a refusal on an empty filter, a log with counts, and **a test that feeds bad
input and asserts nothing was destroyed**. `tools/rebuild_page_files.py` is the model.

## Workflow

1. **Plan in `TODO.md` before the first edit.** Give the goal, the approach, what was rejected,
   what you are *not* doing, the blast radius and the rollback.
2. **Small diffs, verified often.** One logical unit, run the tests, then the next.
3. **Tests before "done".** Every new fact or tool gets a test that fails when it breaks.
4. **Log every error path.** No empty `except`, no suppressions (`# type: ignore`, `noqa`).
5. **Never commit red.** The full suite passes or nothing gets committed.
6. **Commits:** conventional style, on `main`. **Never create a branch unless asked. Never add an
   AI co-author or "Generated with" trailer.** Commits are the owner's alone. Never push without
   the owner's OK.

**Attempt budget:** three fixes for the same failure, then stop and report what you tried. If two
fixes fail, the diagnosis is wrong, so re-diagnose rather than patch again. Never delete a test to
get to green.

## Memory

Decisions and gotchas go in `.agent/memory/` (`decisions.md` and `gotchas.md` are append-only;
`state.md` is rewritten at each phase boundary). It is **gitignored and local to one working
copy**, so anything a fresh clone must know belongs in `TODO.md`, `MASTER_TRACKER.md` or a commit
message.

## Done means

- [ ] `python -m unittest discover -s tests -t . -v` is green
- [ ] Every new claim has a test or a reproducing script
- [ ] Destructive paths are guarded, and each guard has a test
- [ ] `TODO.md` and `MASTER_TRACKER.md` match reality
- [ ] Doc caveats grepped by **symptom**: a fix makes some warning elsewhere stale
- [ ] Diff self-reviewed: no debug code, no commented-out blocks, no secrets
