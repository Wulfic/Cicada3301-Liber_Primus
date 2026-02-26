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
│   ├── gematria_primus.md     # 29-char runic alphabet & values
│   ├── verified_keys.json     # Hill-climbed keys (71/83 alternation pattern)
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
│   └── runeglish/             # 68 runeglish transliterations
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
└── tools/                     # Python scripts
    ├── batch_solver.py        # Multi-page batch attack
    ├── generate_runeglish.py  # Rune → runeglish transliteration
    ├── populate_runes.py      # Extract runes from page images
    ├── solve_p61_p62.py       # F-skip breakthrough solver
    └── translate_runes.py     # Rune ↔ English translation
```

## Liber Primus Status

| Category | Pages | Count | Notes |
|----------|-------|-------|-------|
| ✅ **Solved** | 01, 03–17, 55–58, 59–64, 67–68, 71–74 | 32 | Confirmed readable English / Old English plaintext |
| ⚠️ **Partial** | 00, 02, 18, 19 | 4 | P00: Old English; P02: key 43, fragments; P18/P19: key partially recovered |
| 🟡 **Partial** | 20 | 1 | 166 prime-index runes decoded; 646 non-prime runes still scrambled |
| 🔴 **High IoC** | 21–30 | 10 | P63 keywords applied → IoC 1.86–2.31, but text unreadable (transposition layer remains) |
| 🔴 **Caesar layer** | 31–54 | 24 | Caesar shifts identified, IoC ~1.0, additional cipher layer unsolved |
| 📄 **Image / Special** | 65–66, 69–70 | 4 | No standard rune ciphertext; P65 has a grid (11 × 11) |

> **Note:** Many per-page READMEs contain incorrect "SOLVED" labels from hill-climbing that produced gibberish. Always trust MASTER_TRACKER.md over individual page READMEs.

---

## Credits & Links

Credit to the Cicada solvers community and the 3301 organization.

- [Uncovering Cicada Wiki](https://uncovering-cicada.fandom.com/wiki/Uncovering_Cicada_Wiki)
- [Cicada Solvers Discord](https://discord.com/invite/eMmeaA9)
- [#cicadasolvers on IRC](https://webchat.freenode.net/#cicadasolvers)
