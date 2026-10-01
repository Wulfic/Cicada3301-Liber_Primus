# Archived hill-climb outputs — 2026-05-29 runs

These are the outputs of the legacy solvers (`tools/legacy/`), moved here unchanged on 2026-09-29
(Stage E in `TODO.md`). The archive location follows the owner's 2026-05-29 tracker note.

**Don't use them as evidence.** They were computed on the misaligned page files: `page_N/runes.txt`
held LP2 page N instead of the runes on scan N.jpg. Most of them also came from optimisers
(hill-climbing, SA, GPU search), which the project no longer accepts as evidence. The
"verified keys", "confirmed cribs" and "anchors" in here are those artifacts.

## Layout

| Path | Contents | In git? |
|---|---|---|
| `./` (top level) | outputs that were committed before 2026-09-29 | yes, moved with `git mv` so history is kept |
| `untracked/` | outputs that were never committed (`anchored_results/`, `theory_runs/`, `p21_*` sweeps, three stray files from the repo root under `repo_root/`) | **no**, git-ignored and local to this working copy |

## Undo

`MOVES.txt` lists every move, one per line: `T|U <TAB> from <TAB> to`.

- `T` rows: `git mv <to> <from>`
- `U` rows: move `<to>` back to `<from>`
