# data/ — inputs

| Folder | What goes here | Read by |
|---|---|---|
| [`canonical/`](canonical/PROVENANCE.md) | ★ **The source of truth.** The master rune transcription (LP1 + LP2), translation, keys, index. Provenance and checksums are in `PROVENANCE.md` | `tools/lpcore/corpus.py` (the only loader) |
| [`corpora/`](corpora/) | Texts for candidate keys and plaintext models: Emerson (`emerson_essays.txt`, `self_reliance.txt`), `deor_poem.txt`, `liber_al_vel_legis.txt`, and an English `wordlist.txt` (370k words) | analysis scripts |
| [`outguess/`](outguess/) | Messages extracted with OutGuess from Cicada images (`page_*.txt` and `.bin`), plus three binary hint files (`folly_hint.txt`, `folly_rev_hint.txt`, `wisdom_hint.txt`; the old tracker says they came from the Cicada ISO `/tmp`) | — |
| [`alternate_scans/`](alternate_scans/) | `enhanced/`: 6 contrast-enhanced scans. `diff/`: 48 difference images between scan versions | — |
| [`archive/`](archive/) | **Not evidence.** `hillclimbers/20260529/`: legacy solver outputs (see its README and `MOVES.txt`). `legacy_inputs/runes_full.txt`: the old LP2-only rune dump, superseded by `canonical/` (they are rune-for-rune identical on all 57 LP2 pages) | — |

Rules:
- New derived output goes in a dated folder under `data/` only if a test or `README` explains what produced it.
  Throwaway output belongs in a scratch directory, not here.
- Never edit `canonical/`. If the transcription is wrong, record the erratum in `tools/lpcore/solved.py`
  (`ERRATA`) with the evidence, the way `WIDSOM` and `FOLLWING` are.
