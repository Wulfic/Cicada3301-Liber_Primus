"""Check a decryption against known English, word by word.

Used by the tests (solved sections must reproduce the published translation exactly) and by any
future crib check. It never proposes plaintext — it only answers "does this rune word spell this
English word?".
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path

from .corpus import REPO_ROOT
from .gematria import ALTERNATE_SPELLINGS, indices_to_latin, word_matches

log = logging.getLogger(__name__)

TRANSLATION_PATH = REPO_ROOT / "data" / "canonical" / "liber_primus_translation.txt"
F = 0

_CLAUSE_LINE = re.compile(r"^(\d+)\.(\d+)\.(\d+)\.(\d+)\s+(.*)$")


def load_translation(path: Path | None = None) -> dict[str, list[list[str]]]:
    """{"0.1": [paragraph0_clauses, paragraph1_clauses, ...]} from the iddqd translation file."""
    path = path or TRANSLATION_PATH
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        log.exception("cannot read translation file %s", path)
        raise
    groups: dict[str, dict[int, list[str]]] = {}
    for line in lines:
        m = _CLAUSE_LINE.match(line.strip())
        if m:
            group = f"{m.group(1)}.{m.group(2)}"
            groups.setdefault(group, {}).setdefault(int(m.group(3)), []).append(m.group(5).strip())
    return {g: [paras[k] for k in sorted(paras)] for g, paras in groups.items()}


def english_words(text: str) -> list[str]:
    """Upper-case letter words; apostrophes dropped (DON'T → DONT), digits dropped (list numbering)."""
    cleaned = text.upper().replace("'", "").replace("’", "")
    return [w for w in re.split(r"[^A-Z0-9]+", cleaned) if w and not w.isdigit()]


def spellings_of_length(word: str, length: int) -> list[tuple[int, ...]]:
    """Every spelling of `word` that is exactly `length` runes long."""
    word = word.upper()
    out: list[tuple[int, ...]] = []

    def walk(wp: int, acc: tuple[int, ...]) -> None:
        if len(acc) > length:
            return
        if wp == len(word):
            if len(acc) == length:
                out.append(acc)
            return
        for size in (1, 2, 3):
            chunk = word[wp:wp + size]
            if len(chunk) == size and chunk in ALTERNATE_SPELLINGS:
                walk(wp + size, acc + ALTERNATE_SPELLINGS[chunk])

    walk(0, ())
    return out


class AlignmentError(ValueError):
    pass


def interrupter_positions(cipher_words: list[tuple[int, ...]], english: list[str]) -> set[int]:
    """Stream positions that hold a plaintext F (the book leaves plaintext F unenciphered).

    Derived only from the known English: a position is an interrupter iff the English word's
    spelling at that length puts F there and the cipher rune there is ᚠ. Raises if the spellings
    of one word disagree about where F is (ambiguous) or the word counts differ.
    """
    if len(cipher_words) != len(english):
        raise AlignmentError(f"{len(cipher_words)} cipher words vs {len(english)} English words")
    positions: set[int] = set()
    offset = 0
    for cw, ew in zip(cipher_words, english):
        spellings = spellings_of_length(ew, len(cw))
        if not spellings:
            raise AlignmentError(f"English word {ew!r} has no {len(cw)}-rune spelling (cipher offset {offset})")
        f_sets = {frozenset(i for i, t in enumerate(s) if t == F) for s in spellings}
        if len(f_sets) != 1:
            raise AlignmentError(f"ambiguous F positions for {ew!r} at offset {offset}")
        for i in next(iter(f_sets)):
            if cw[i] == F:
                positions.add(offset + i)
        offset += len(cw)
    return positions


@dataclass(frozen=True)
class Mismatch:
    word_index: int
    expected: str
    got: str


def compare_words(plain_words: list[tuple[int, ...]], english: list[str]) -> list[Mismatch]:
    if len(plain_words) != len(english):
        raise AlignmentError(f"{len(plain_words)} plaintext words vs {len(english)} English words")
    return [
        Mismatch(i, ew, indices_to_latin(pw))
        for i, (pw, ew) in enumerate(zip(plain_words, english))
        if not word_matches(pw, ew)
    ]


def render_words(plain_words: list[tuple[int, ...]], english: list[str]) -> list[str]:
    """Latin rendering of solved rune words: the translation's own word wherever one exists.

    A rune can stand for several letters (ᚳ = C/K/Q, ᚢ = U/V, ᛡ = IA/IO, ᛝ = NG/ING), so the one-spelling
    `indices_to_latin` turns KNOW into CNOW. Only the English can choose, so each rune word is rendered as its
    English word after `word_matches` confirms the runes spell it. Words past the end of `english` (square cells)
    fall back to `indices_to_latin`. Raises AlignmentError if a rune word does not spell its English word.
    """
    if len(english) > len(plain_words):
        raise AlignmentError(f"{len(english)} English words for {len(plain_words)} rune words")
    out = []
    for i, pw in enumerate(plain_words):
        if i >= len(english):
            out.append(indices_to_latin(pw))
        elif word_matches(pw, english[i]):
            out.append(english[i])
        else:
            raise AlignmentError(f"rune word {i} ({indices_to_latin(pw)}) does not spell {english[i]!r}")
    return out


def split_like(stream: list[int], words: list[tuple[int, ...]]) -> list[tuple[int, ...]]:
    """Cut a flat stream back into words with the same lengths as `words`."""
    out, pos = [], 0
    for w in words:
        out.append(tuple(stream[pos:pos + len(w)]))
        pos += len(w)
    if pos != len(stream):
        raise AlignmentError(f"stream length {len(stream)} != total word length {pos}")
    return out
