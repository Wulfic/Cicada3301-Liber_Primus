# Canonical Liber Primus data — provenance

**This directory is the single source of truth for rune text.** Everything else in the repo
(`pages/page_XX/runes.txt`, `data/archive/legacy_inputs/runes_full.txt`, the transcript in `reference/sources/`) is either
generated from these files or a legacy copy. Load text through `tools/lpcore/corpus.py`.

| File | Source | Upstream commit | sha256 |
|---|---|---|---|
| `liber_primus_master.txt` | rtkd/iddqd master with the five numeric-grid corrections from cicada-solvers/iddqd | `3089b656` (2019-06-17) + numeric overlay from `f804b85` (2021-05-09) | `df7eaaa0c92243946803a7a90a7bfdcb36c0eba73f964f3a093c238ab01a5746` |
| `liber_primus_translation.txt` | rtkd/iddqd `liber-primus__translation/liber-primus__translation.txt` | master @ 2023-08-15 | `adce48cfea746fd5add5071c85a34a998a546ca94c009bcd796cd3e699cc1c47` |
| `liber_primus_index.txt` | rtkd/iddqd `liber-primus__index/liber-primus__index.txt` | master @ 2023-08-15 | `a3b62f17d7a9281829e85eaed13d5541b6c1be70b1683fad2701d1f53a954ebf` |
| `liber_primus_keys.txt` | rtkd/iddqd `liber-primus__keys/liber-primus__keys.txt` | master @ 2023-08-15 | `ff1106e69d2136381c0ac166a0836c64a6d64078bce4be33436c2198af758ac3` |

Upstream: <https://github.com/rtkd/iddqd> (community transcription; no license file upstream).
Downloaded 2026-09-29.

## Numeric-grid correction (2026-10-01)

The base transcription is retained, with exactly five numeric cells updated to follow
[cicada-solvers/iddqd commit f804b85](https://github.com/cicada-solvers/iddqd/commit/f804b85e9e6fe6287c7cab054335af07ed420728).
That 2021 commit credits **Inky** and links to
[the original Discord message](https://discord.com/channels/572330844056715284/585524644740857882/840142864830824479).
These are prior community corrections. The update preserves the 2019 punctuation, rune text and word positions;
it does not replace the entire master with the newer transcription. The unmodified 2019 file's SHA-256 was
`e21743ccd9a07f3845d52a329c61b9fa69e9ca6a44ee3ba0db8f28a0d7065004`.

Rows and columns below are one-based within the grid on each LP2 page; byte offsets are zero-based
within the complete grid's reading-order payload.

| LP2 page | Scan | Row | Column | Old token | Updated token | Byte offset |
|---|---:|---:|---:|---|---|---:|
| 49 | 66 | 6 | 6 | `1L` | `1l` | 45 |
| 49 | 66 | 7 | 3 | `0L` | `0l` | 50 |
| 50 | 67 | 11 | 6 | `0l` | `0I` | 165 |
| 50 | 67 | 12 | 5 | `2s` | `2S` | 172 |
| 51 | 68 | 8 | 7 | `3i` | `3I` | 246 |

The original images contain ambiguous unadorned `I`/`l` strokes. These cell choices follow the documented
community convention, rather than claiming that every case distinction is uniquely recoverable from the image.

The grid spans LP2 pages 49–51 (scans 66–68): 80 + 104 + 72 = **256 cells**. With alphabet
`0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx` and each cell interpreted as `60*a+b`,
the updated byte payload has SHA-256 `3b9b07d9a26e6d55c432d94d2661fdff3c2b348daed06821f2bdb23184a4b290`.
This is the tested byte interpretation, not an authenticated statement of Cicada's intent.
`tests/test_grid_extraction.py` pins the scan counts, payload checksum and five corrections.

## Delimiters (from the file header)

`-` word · `.` clause · `&` paragraph · `$` segment · `§` chapter · `/` line · `%` page

## Verification performed before adoption (2026-09-29)

- **Rune-for-rune identical** to the repo's older `data/archive/legacy_inputs/runes_full.txt` on all 57 LP2 rune pages.
  The only differences are ~6 `.`↔`-` separator choices, a few `&`/`$` placements, and the numeric
  grids (4×4 square on LP2 p15, base-60 blocks), which the master includes and `runes_full.txt` omits.
- The master keeps a **page with no runes for scan 67** (LP2 page 50, containing 104 base-60 grid cells).
  This was independently confirmed by viewing scans 59, 66 and 68.

## Page → scan mapping (split on `%`, text starting at the first rune)

| Master pages | Scans (`pages/page_XX/images/XX.jpg`) | Content |
|---|---|---|
| 0 | 01 | LP1 — A WARNING |
| 1–14 | 03–16 | LP1 — solved sections |
| 15–72 | 17–74 | LP2 pages 0–57 (scan = 17 + LP2 page) |
| — | 00, 02 | no runes (title pages) |

Scan 67 (LP2 page 50) is present with numeric grid cells and no runes.

## Segments (`$`) — 18 total, matching the upstream keys file 0.0–0.17

| Seg | Runes | Content | Status |
|---|---|---|---|
| 0 | 184 | A WARNING | solved — inverted gematria |
| 1 | 515 | WELCOME / WISDOM | solved — Vigenère DIVINITY, plaintext F unenciphered |
| 2 | 157 | SOME WISDOM / KNOW THIS | plaintext |
| 3 | 778 | A KOAN / AN INSTRUCTION | solved — inverted gematria + shift 3 |
| 4 | 755 | THE LOSS OF DIVINITY / SOME WISDOM / AN INSTRUCTION | plaintext |
| 5 | 319 | A KOAN (the I) | solved — Vigenère FIRFUMFERENFE, plaintext F unenciphered |
| 6 | 89 | AN INSTRUCTION / KNOW THIS | plaintext |
| 7–15 | 12,956 | LP2 unsolved: crosses, sprouts, roots, `ᚠᚢᛚᛗ ᚪᛠᚣᛟᚪ`+square, moebius, mayfly, wing, cuneiform, plants | **unsolved** |
| 16 | 85 | AN END | solved — φ(prime) stream, plaintext F unenciphered |
| 17 | 95 | PARABLE | plaintext |

Every "solved" row is asserted by `tests/test_lpcore.py`: the canonical runes must decrypt to
`liber_primus_translation.txt`. The numbers here are what the tests check, not a claim.
