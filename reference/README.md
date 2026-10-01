# reference/ — reading material

Nothing in here is loaded by code. For runes, use `data/canonical/` through `tools/lpcore`.

| Folder | What goes here | Trust |
|---|---|---|
| [`findings/`](findings/) | **Our own results.** Each number in a finding is reproduced by a test or a named script | High, as far as the tests go |
| [`sources/`](sources/) | Primary Cicada material and transcriptions of it | Primary, but see the transcript note below |
| [`community/`](community/) | Other people's research, tools, notes and images | Unverified until we reproduce it |
| [`archive/`](archive/) | Superseded documents of ours, kept verbatim for history | **Not evidence**. Built on misaligned data before 2026-09-29 |

## findings/

| File | Contents |
|---|---|
| `lp2_logic_findings_2026-09-29.md` | Key-independent constraints C1–C7 on the unsolved LP2 cipher, the scan-32 square decoded, open items (§6) |

## sources/

| File | Contents |
|---|---|
| `LiberPrimus.pdf` | The complete scan set as one PDF (55 MB). The per-scan JPGs are in `pages/page_XX/images/` |
| `liber_primus_transcript.md` | Wiki transcript with English for solved parts. It groups several scans per block, so **don't use it for per-page work** |
| `page28_transcript.txt` | Latin transliteration of one LP2 page (which scan has not been verified) |
| `gematria_primus.md` | The 29-rune alphabet with values. The tested copy is `tools/lpcore/gematria.py` |
| `cicada_pgp_key.asc` | 3301's PGP public key, for verifying signed messages |

## community/

| File | Contents |
|---|---|
| `community_research.md` | State of the art in 2026: community ledgers, what has been excluded, our web checks |
| `echo446ghq_analysis.md` | Review of a claimed full solution (Echo446Ghq). **Debunked** |
| `people_2014.md` | Known 2014 participants |
| `irc_logs.txt` | IRC excerpt (Profetul/mortlach) on key-gap patterns that produce few doublets |
| `mortlach_gematria.txt` | mortlach's LP2 words as prime-value lists (Mathematica format) |
| `3301_guitar_tones.txt` | Guitar-tone hint text ("-Jens"). Provenance unverified |
| `raidens_contest.txt` | Hex hashes from Raiden's contest. A community puzzle, not Cicada |
| `RuneSolver.py` | Community rune-solving tool, untested here |
| `solved_pages.docx`, `ideas_suggestions.docx` | Community-compiled solutions and idea list |
| `cicada_puzzle_paper.pdf` | Academic paper on the puzzles |
| `cuneiform.pdf` | Cuneiform numeral reference (LP2 uses base-60 cuneiform) |
| `images/2_grams.png` | 2-gram count table for LP2 pages 0–55 (12,956 runes). It shows the doublet deficit on the diagonal |
| `images/Algorithm.png` | A community "key switch" proposal: change keys whenever the next cipher rune would repeat. **A candidate mechanism for the doublet rule** (findings §6.1) |
| `images/Symbols_page34.png` | Cuneiform reading 10·7·10·3 / 50·5·1 in base 60. Neither total is prime |
| `images/Screenshot_from_2016-01-15_02-52-43.png` | Output of a word-pattern lookup tool |
