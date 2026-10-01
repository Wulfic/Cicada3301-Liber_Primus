"""Canonical Liber Primus corpus loader.

Reads `data/canonical/liber_primus_master.txt` (rtkd/iddqd master transcription; provenance in
`data/canonical/PROVENANCE.md`). This is the ONLY supported way to get rune text: the legacy
per-page files were misaligned with their scans until 2026-09-29.

Delimiters: `-` word · `.` clause · `&` paragraph · `$` segment · `§` chapter · `/` line · `%` page.
`/` and `%` do NOT end a word — words run across line and page breaks in the book.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from .gematria import RUNE_INDEX

log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
MASTER_PATH = REPO_ROOT / "data" / "canonical" / "liber_primus_master.txt"

FIRST_LP2_SCAN = 17
SCANS_WITHOUT_RUNES = (0, 2)          # LP1 title pages
EXPECTED_MASTER_PAGES = 73            # 15 LP1 rune pages + 58 LP2 pages
EXPECTED_SEGMENTS = 18

_WORD_BREAKS = "-.&$§"
_IGNORED = "\n\r "


class CorpusError(ValueError):
    """The canonical file does not have the structure this loader was verified against."""


def scan_for_master_page(master_index: int) -> int:
    """Scan number (`pages/page_XX/images/XX.jpg`) of a master page.

    Master page 0 is scan 01 (A WARNING); every later page is scan = index + 2, because scans 00
    and 02 carry no runes. Verified against scans 59, 66 and 68 by eye on 2026-09-29.
    """
    if master_index < 0 or master_index >= EXPECTED_MASTER_PAGES:
        raise CorpusError(f"master page index out of range: {master_index}")
    return 1 if master_index == 0 else master_index + 2


def lp_location(scan: int) -> tuple[str, int]:
    """('LP1', scan) for scans 0–16, ('LP2', scan − 17) for scans 17–74."""
    if not 0 <= scan <= 74:
        raise CorpusError(f"scan out of range: {scan}")
    return ("LP1", scan) if scan < FIRST_LP2_SCAN else ("LP2", scan - FIRST_LP2_SCAN)


@dataclass(frozen=True)
class Word:
    kind: str                 # "rune" or "number"
    text: str                 # raw characters of the word (runes, or digits/letters)
    runes: tuple[int, ...]    # rune indices; empty for number words
    scan: int                 # scan on which the word starts
    segment: int              # `$`-delimited segment, 0–17
    paragraph: int            # global `&` counter
    clause: int               # global `.`/`&`/`$` counter
    rune_offset: int          # global offset of the word's first rune (-1 for numbers)
    line: int                 # global `/` counter at the word's first character


@dataclass
class Page:
    master_index: int
    scan: int
    raw: str                  # page text exactly as in the master, without the `%`

    @property
    def lp_part(self) -> str:
        return lp_location(self.scan)[0]

    @property
    def lp_page(self) -> int:
        return lp_location(self.scan)[1]

    @property
    def runes(self) -> list[int]:
        return [RUNE_INDEX[ch] for ch in self.raw if ch in RUNE_INDEX]


@dataclass
class Corpus:
    pages: list[Page]
    words: list[Word]
    source: Path = field(default=MASTER_PATH)

    def page_by_scan(self, scan: int) -> Page | None:
        return next((p for p in self.pages if p.scan == scan), None)

    def rune_words(self, segment: int | None = None) -> list[Word]:
        return [w for w in self.words if w.kind == "rune" and (segment is None or w.segment == segment)]

    def segment_runes(self, segment: int) -> list[int]:
        return [r for w in self.rune_words(segment) for r in w.runes]

    def all_runes(self) -> list[int]:
        return [r for w in self.rune_words() for r in w.runes]

    def segment_paragraphs(self, segment: int) -> list[list[Word]]:
        """Words of a segment grouped by `&` paragraph, in reading order (numbers included)."""
        groups: dict[int, list[Word]] = {}
        for w in self.words:
            if w.segment == segment:
                groups.setdefault(w.paragraph, []).append(w)
        return [groups[k] for k in sorted(groups)]


def _body(text: str) -> str:
    start = next((i for i, ch in enumerate(text) if ch in RUNE_INDEX), -1)
    if start < 0:
        raise CorpusError("no runes found in master transcription")
    return text[start:].replace("\r", "")


def parse_master(text: str) -> Corpus:
    body = _body(text)
    raw_pages = body.split("%")
    # A trailing chapter mark (`§`) follows the last page separator.
    if raw_pages and raw_pages[-1].strip() in ("", "§"):
        raw_pages = raw_pages[:-1]
    if len(raw_pages) != EXPECTED_MASTER_PAGES:
        log.error("master has %d pages, expected %d", len(raw_pages), EXPECTED_MASTER_PAGES)
        raise CorpusError(f"expected {EXPECTED_MASTER_PAGES} pages, found {len(raw_pages)}")
    pages = [Page(i, scan_for_master_page(i), raw) for i, raw in enumerate(raw_pages)]

    words: list[Word] = []
    page_i = segment = paragraph = clause = line = 0
    buf: list[str] = []
    buf_kind: str | None = None
    buf_scan = buf_offset = buf_line = -1
    rune_offset = 0
    broke_line = False   # a `/` or `%` since the last glyph

    def flush() -> None:
        nonlocal buf, buf_kind
        if buf_kind is not None:
            text_ = "".join(buf)
            runes = tuple(RUNE_INDEX[c] for c in text_) if buf_kind == "rune" else ()
            words.append(Word(buf_kind, text_, runes, buf_scan, segment, paragraph, clause,
                              buf_offset if buf_kind == "rune" else -1, buf_line))
        buf, buf_kind = [], None

    for pos, ch in enumerate(body):
        if ch in RUNE_INDEX or (ch.isascii() and ch.isalnum()):
            kind = "rune" if ch in RUNE_INDEX else "number"
            # Rune words continue across line/page breaks (the book wraps mid-word);
            # numbers never do — grid cells end at the line.
            if buf_kind is not None and (buf_kind != kind or (kind == "number" and broke_line)):
                if not broke_line:
                    log.warning("rune/number adjacency without delimiter at char %d (scan %d)",
                                pos, pages[page_i].scan)
                flush()
            if buf_kind is None:
                buf_kind, buf_scan = kind, pages[min(page_i, len(pages) - 1)].scan
                buf_offset, buf_line = rune_offset, line
            buf.append(ch)
            broke_line = False
            if kind == "rune":
                rune_offset += 1
        elif ch in _WORD_BREAKS:
            flush()
            if ch in ".&$":
                clause += 1
            if ch == "&":
                paragraph += 1
            if ch == "$":
                segment += 1
        elif ch == "%":
            page_i += 1
            broke_line = True
        elif ch == "/":
            line += 1
            broke_line = True
        elif ch in _IGNORED:
            continue
        else:
            log.error("unexpected character %r at char %d", ch, pos)
            raise CorpusError(f"unexpected character {ch!r} at position {pos}")
    flush()

    if segment != EXPECTED_SEGMENTS:
        log.error("found %d segment marks, expected %d", segment, EXPECTED_SEGMENTS)
        raise CorpusError(f"expected {EXPECTED_SEGMENTS} segments, found {segment}")
    return Corpus(pages, words)


def load_corpus(path: Path | None = None) -> Corpus:
    path = path or MASTER_PATH
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        log.exception("cannot read canonical master transcription at %s", path)
        raise
    corpus = parse_master(text)
    corpus.source = path
    log.debug("loaded %d pages, %d words, %d runes from %s",
              len(corpus.pages), len(corpus.words), len(corpus.all_runes()), path)
    return corpus
