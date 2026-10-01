<a href="https://www.youtube.com/watch?v=I2O7blSSzpI">
<img src="https://github.com/cijhho123/cicada3301/blob/main/2012/additional%20media/images/cicada%20(from%20the%20website).jpg" alt="cicada3301">
</a>

# What is Cicada 3301?

Cicada 3301 is an organization that posted three rounds of cryptographic puzzles (2012, 2013, 2014) to recruit codebreakers. The third puzzle centres on the **Liber Primus**, a 75-page runic manuscript, and it remains partially unsolved. See [Lemmino's overview](https://www.youtube.com/watch?v=I2O7blSSzpI) or [Nox Populi's deep dive](https://www.youtube.com/watch?v=l0z03ntMJio) for background.

# This repository

A research workspace for the unsolved pages of the Liber Primus, built on logic and reproducible tests rather than search.

> **Start at [MASTER_TRACKER.md](MASTER_TRACKER.md).** It says where the work stands, what is proven, what is ruled out, and what to do next.

| Scans (`pages/page_XX`) | Book | Status |
|---|---|---|
| 01, 03–16 | LP1 | ✅ solved: every section reproduced from canonical runes by the tests |
| 17–66, 68–72 | LP2 p0–55 | 🔴 **unsolved**: 9 sections, 12,956 runes |
| 73, 74 | LP2 p56–57 | ✅ solved (AN END, PARABLE) |
| 00, 02, 67 | — | no runes (title pages, base-60 grid) |

## Quick start

Python 3.11 or newer, standard library only.

```
python -m unittest discover -s tests -t . -v      # proves the data and the core are right (73 tests)
```

```python
from tools.lpcore.corpus import load_corpus
from tools.lpcore.gematria import indices_to_latin

corpus = load_corpus()                     # canonical LP1 + LP2, keyed by scan number
runes = corpus.segment_runes(7)            # first unsolved section, as Gematria Primus indices 0–28
print(len(runes), indices_to_latin(runes[:20], sep=" "))
```

## Repository layout

Folders are grouped by **how far you can trust them**. ★ = source of truth.

```
MASTER_TRACKER.md          ★ status, facts, exclusions, next steps; start here
TODO.md                    current plan (written before any code) and stage history
AGENTS.md                  working rules for anyone, human or AI, changing this repo

pages/page_XX/             one folder per scan, 00–74
  images/                  the scan(s)
  runes.txt, README.md     generated from canonical data by tools/rebuild_page_files.py; don't hand-edit

data/                      inputs; see data/README.md
  canonical/               ★ master rune transcription, translation, keys + PROVENANCE.md
  corpora/                 candidate key texts (Emerson, Deor, Liber AL) and an English wordlist
  outguess/                OutGuess-extracted messages and binary hints
  alternate_scans/         enhanced and difference images
  archive/                 history, not evidence: legacy solver outputs, superseded inputs

tools/
  lpcore/                  ★ tested core: corpus loader, gematria, deterministic ciphers, verifier, statistics
  rebuild_page_files.py    regenerates pages/*/runes.txt + README.md (dry-run unless --write)
  run_stage_i.py           reproduces the stage-I key-source run (findings §8); writes one TSV of results
  legacy/                  107 pre-2026-09-29 scripts, untested and built on misaligned data; history only

tests/                     ★ the proof: python -m unittest discover -s tests -t . -v

reference/                 reading material; see reference/README.md
  findings/                our results, each backed by a test
  sources/                 primary Cicada material (the full PDF, transcript, PGP key, gematria table)
  community/               other people's research and tools, unverified until reproduced
  archive/                 superseded docs of ours, e.g. the pre-2026-09-29 tracker
```

> **Why "history, not evidence"?** Until 2026-09-29 the page files did not match their scans, and much of the
> older work was hill-climbing. The claims that turned out to be artifacts are listed in
> [MASTER_TRACKER.md §4.3](MASTER_TRACKER.md#43-invalid-claims-from-before-2026-09-29).

---

## Credits & Links

Credit to the Cicada solvers community and the 3301 organization.

- [Uncovering Cicada Wiki](https://uncovering-cicada.fandom.com/wiki/Uncovering_Cicada_Wiki)
- [Cicada Solvers Discord](https://discord.com/invite/eMmeaA9)
- [#cicadasolvers on IRC](https://webchat.freenode.net/#cicadasolvers)
