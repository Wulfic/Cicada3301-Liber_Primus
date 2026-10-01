# tools/legacy — archived, untrusted

These 107 scripts are the pre-2026-09-29 toolset, moved here unchanged in Stage E (see `TODO.md`).
Nothing in this folder is tested, and nothing in it should be cited as evidence.

## Why they are archived

- **They read misaligned data.** Until 2026-09-29, `pages/page_N/runes.txt` held LP2 page N while
  `pages/page_N/images/` held scan N.jpg, and LP1 text sat in pages 57–74. Every result these
  scripts produced from page files came from the wrong scan. The "discoveries" that depended on
  that are listed in `MASTER_TRACKER.md` §4.3.
- **Most of them are optimisers** (hill-climbing, simulated annealing, GPU search). Project
  policy is that hypothesis tests must be deterministic, with one decode and a threshold declared
  before the run. Optimiser output isn't accepted as evidence.

## Use instead

| Need | Trusted replacement |
|---|---|
| Runes for a page/scan | `tools.lpcore.corpus` (reads `data/canonical/liber_primus_master.txt`) |
| Gematria tables | `tools.lpcore.gematria` |
| Shift / atbash / Vigenère with skips / φ(prime) stream | `tools.lpcore.ciphers` |
| Solved-section checks | `tools.lpcore.solved`, `tools.lpcore.verify` |
| IoC, doublet rate, Δ statistics | `tools.lpcore.stats` |

Tests: `python -m unittest discover -s tests -t . -v`

## If you do run one

The scripts locate the repo as `Path(__file__).parent.parent` (64 of them), which now
resolves to `tools/` rather than the repo root, so most will fail with `FileNotFoundError`.
That is deliberate: a loud failure is better than quietly reading the wrong file. Their old
output files are in `data/archive/hillclimbers/20260529/` and are no longer at the paths the
scripts expect.

To revive one, copy it out, point it at `tools.lpcore` for its input, and add a test.
Don't edit it in place.

Every move is recorded in `data/archive/hillclimbers/20260529/MOVES.txt`.
