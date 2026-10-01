<a href="https://www.youtube.com/watch?v=I2O7blSSzpI">
<img src="https://github.com/cijhho123/cicada3301/blob/main/2012/additional%20media/images/cicada%20(from%20the%20website).jpg" alt="cicada3301">
</a>

# What is Cicada 3301?

Cicada 3301 is an organization that posted three rounds of cryptographic puzzles (2012, 2013, 2014) to recruit codebreakers. The third puzzle — centred on the **Liber Primus**, a 75-page runic manuscript — remains partially unsolved. See [Lemmino's overview](https://www.youtube.com/watch?v=I2O7blSSzpI) or [Nox Populi's deep dive](https://www.youtube.com/watch?v=l0z03ntMJio) for background.

# This Repository

Active research workspace for decrypting the Liber Primus. All progress, keys, failed approaches, and next steps are tracked in a single document:

> **[MASTER_TRACKER.md](MASTER_TRACKER.md)** — the sole source of truth. Start here.

---

## Repository Structure

```
├── MASTER_TRACKER.md          # All progress, keys, methods, status
├── README.md
│
├── pages/                     # The manuscript — 75 page directories
│   └── page_XX/
│       ├── runes.txt          # Raw rune ciphertext
│       ├── README.md          # Per-page status & notes
│       └── images/            # Page scans & enhanced images
│
├── data/                      # Corpus, keys, derived data
│   ├── canonical/             # ★ canonical rune text + translation (source of truth, see PROVENANCE.md)
│   ├── gematria_primus.md     # 29-char runic alphabet & values
│   ├── runes_full.txt         # Concatenated runes (all pages)
│   ├── self_reliance.txt      # Emerson — referenced in solved text
│   ├── emerson_essays.txt     # Full Emerson corpus
│   ├── deor_poem.txt          # Old English poem (Deor)
│   ├── wordlist.txt           # English dictionary for scoring
│   ├── key_search_corpus.txt  # Combined key-search corpus
│   ├── folly_hint.txt         # Outguess hint (folly)
│   ├── folly_rev_hint.txt     # Outguess hint (folly reversed)
│   ├── wisdom_hint.txt        # Outguess hint (wisdom)
│   ├── outguess/              # 5 outguess-extracted messages
│   └── archive/hillclimbers/  # LEGACY hill-climb outputs on misaligned data — not evidence (see its README)
│
├── reference/                 # Community research & external docs
│   ├── community_research.md  # Wiki/Reddit/GitHub findings
│   ├── liber_primus_transcript.md  # Full LP transcript
│   ├── people_2014.md         # Known 2014 participants
│   ├── LiberPrimus.pdf        # Original LP scan (55 MB)
│   ├── cicada_pgp_key.asc     # 3301 PGP public key
│   ├── cicada_puzzle_paper.pdf # Academic paper on the puzzle
│   ├── solved_pages.docx      # Community compiled solutions
│   ├── RuneSolver.py          # Community rune solver tool
│   └── ...                    # IRC logs, cuneiform ref, images, etc.
│
├── tests/                     # unittest suite: python -m unittest discover -s tests -t . -v
│
└── tools/                     # Python scripts
    ├── lpcore/                # ★ tested core: corpus loader, gematria, deterministic ciphers, verifier
    ├── rebuild_page_files.py  # regenerates pages/page_XX/{runes.txt,README.md} (dry-run default)
    └── legacy/                # 107 pre-2026-09-29 scripts, untested, read misaligned data (see its README)
```

## Liber Primus Status

Page folders are keyed by **scan number**: `pages/page_XX/` holds `images/XX.jpg` and the runes on that scan.
Status is **asserted by tests** (`python -m unittest discover -s tests -t . -v`), not claimed.

| Scans (`page_XX`) | Book | Content | Status |
|---|---|---|---|
| 00, 02 | LP1 | title pages | no runes |
| 01, 03–16 | LP1 | A WARNING · WELCOME · SOME WISDOM · A KOAN · AN INSTRUCTION · THE LOSS OF DIVINITY · A KOAN · AN INSTRUCTION | ✅ solved (all reproduced from canonical runes) |
| 17–66, 68–72 | LP2 p0–55 | 9 sections, 12,956 runes | 🔴 **unsolved** |
| 67 | LP2 p50 | base-60 grid | no runes |
| 73 | LP2 p56 | AN END (φ(prime) stream) | ✅ solved |
| 74 | LP2 p57 | PARABLE (plaintext) | ✅ solved |

> **2026-09-29 correction:** before this date the page files did not match their scans (`page_N` held LP2 page N),
> and many "discoveries" in older notes were artifacts of that or of hill-climbing. See **§0 of MASTER_TRACKER.md**.
> Canonical text: [`data/canonical/`](data/canonical/PROVENANCE.md) · tested core: [`tools/lpcore/`](tools/lpcore/__init__.py).

---

## Credits & Links

Credit to the Cicada solvers community and the 3301 organization.

- [Uncovering Cicada Wiki](https://uncovering-cicada.fandom.com/wiki/Uncovering_Cicada_Wiki)
- [Cicada Solvers Discord](https://discord.com/invite/eMmeaA9)
- [#cicadasolvers on IRC](https://webchat.freenode.net/#cicadasolvers)
