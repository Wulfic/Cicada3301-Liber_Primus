# Canonical Liber Primus data — provenance

**This directory is the single source of truth for rune text.** Everything else in the repo
(`pages/page_XX/runes.txt`, `data/archive/legacy_inputs/runes_full.txt`, the transcript in `reference/sources/`) is either
generated from these files or a legacy copy. Load text through `tools/lpcore/corpus.py`.

| File | Source | Upstream commit | sha256 |
|---|---|---|---|
| `liber_primus_master.txt` | rtkd/iddqd `liber-primus__transcription--master/liber-primus__transcription--master.txt` | `3089b656` (2019-06-17, "Fix segment offsets and transcription errors") | `e21743ccd9a07f3845d52a329c61b9fa69e9ca6a44ee3ba0db8f28a0d7065004` |
| `liber_primus_translation.txt` | rtkd/iddqd `liber-primus__translation/liber-primus__translation.txt` | master @ 2023-08-15 | `adce48cfea746fd5add5071c85a34a998a546ca94c009bcd796cd3e699cc1c47` |
| `liber_primus_index.txt` | rtkd/iddqd `liber-primus__index/liber-primus__index.txt` | master @ 2023-08-15 | `a3b62f17d7a9281829e85eaed13d5541b6c1be70b1683fad2701d1f53a954ebf` |
| `liber_primus_keys.txt` | rtkd/iddqd `liber-primus__keys/liber-primus__keys.txt` | master @ 2023-08-15 | `ff1106e69d2136381c0ac166a0836c64a6d64078bce4be33436c2198af758ac3` |

Upstream: <https://github.com/rtkd/iddqd> (community transcription; no license file upstream).
Downloaded 2026-09-29.

## Delimiters (from the file header)

`-` word · `.` clause · `&` paragraph · `$` segment · `§` chapter · `/` line · `%` page

## Verification performed before adoption (2026-09-29)

- **Rune-for-rune identical** to the repo's older `data/archive/legacy_inputs/runes_full.txt` on all 57 LP2 rune pages.
  The only differences are ~6 `.`↔`-` separator choices, a few `&`/`$` placements, and the numeric
  grids (4×4 square on LP2 p15, base-60 blocks), which the master includes and `runes_full.txt` omits.
- The master keeps an **empty page for scan 67** (LP2 page 50, base-60 grid only).
  This was independently confirmed by viewing scans 59, 66 and 68.

## Page → scan mapping (split on `%`, text starting at the first rune)

| Master pages | Scans (`pages/page_XX/images/XX.jpg`) | Content |
|---|---|---|
| 0 | 01 | LP1 — A WARNING |
| 1–14 | 03–16 | LP1 — solved sections |
| 15–72 | 17–74 | LP2 pages 0–57 (scan = 17 + LP2 page) |
| — | 00, 02 | no runes (title pages) |

Scan 67 (LP2 page 50) is present as an empty page.

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
