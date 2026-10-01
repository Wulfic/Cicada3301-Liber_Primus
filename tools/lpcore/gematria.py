"""Gematria Primus: the 29-rune alphabet of the Liber Primus.

Index order is the futhorc order used by every solved section; all cipher arithmetic is mod 29.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

N = 29

RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"

# Canonical transliteration (one spelling per rune).
LATIN: tuple[str, ...] = (
    "F", "U", "TH", "O", "R", "C", "G", "W", "H", "N",
    "I", "J", "EO", "P", "X", "S", "T", "B", "E", "M",
    "L", "NG", "OE", "D", "A", "AE", "Y", "IA", "EA",
)

# Gematria value of each rune: the first 29 primes.
PRIME_VALUES: tuple[int, ...] = (
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
    31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
    73, 79, 83, 89, 97, 101, 103, 107, 109,
)

RUNE_INDEX: dict[str, int] = {r: i for i, r in enumerate(RUNES)}

# Every Latin spelling a rune can stand for in English plaintext. Used only to CHECK a
# decryption against known English, never to generate candidates.
#   U/V share a rune; C/K share a rune; Q is written C+W (LP spells QUESTION as CWESTION);
#   NG may stand for ING; IA may stand for IO; S covers Z (no Z rune).
ALTERNATE_SPELLINGS: dict[str, tuple[int, ...]] = {
    "F": (0,), "U": (1,), "V": (1,), "TH": (2,), "O": (3,), "R": (4,),
    "C": (5,), "K": (5,), "Q": (5,), "G": (6,), "W": (7,), "H": (8,), "N": (9,),
    "I": (10,), "J": (11,), "EO": (12,), "P": (13,), "X": (14,), "S": (15,), "Z": (15,),
    "T": (16,), "B": (17,), "E": (18,), "M": (19,), "L": (20,),
    "NG": (21,), "ING": (21,), "OE": (22,), "D": (23,), "A": (24,), "AE": (25,),
    "Y": (26,), "IA": (27,), "IO": (27,), "EA": (28,),
    "QU": (5, 7),
}

if len(RUNES) != N or len(LATIN) != N or len(PRIME_VALUES) != N:
    raise AssertionError("Gematria tables must all have 29 entries")


def is_rune(ch: str) -> bool:
    return ch in RUNE_INDEX


def runes_to_indices(text: str) -> list[int]:
    """Indices of the runes in `text`, ignoring every non-rune character."""
    return [RUNE_INDEX[ch] for ch in text if ch in RUNE_INDEX]


def indices_to_runes(indices: Iterable[int]) -> str:
    return "".join(RUNES[i % N] for i in indices)


def indices_to_latin(indices: Iterable[int], sep: str = "") -> str:
    return sep.join(LATIN[i % N] for i in indices)


def gematria_sum(indices: Iterable[int]) -> int:
    """Sum of prime values — the 'numbers' the book says are sacred."""
    return sum(PRIME_VALUES[i] for i in indices)


def spellings_of(word: str, max_results: int = 64) -> list[tuple[int, ...]]:
    """All rune-index sequences an English word can be written as (bounded).

    `word` must already be upper-case A–Z. Deterministic enumeration by dynamic programming;
    a word with no valid spelling returns an empty list.
    """
    word = word.upper()
    results: list[tuple[int, ...]] = []

    def walk(pos: int, acc: tuple[int, ...]) -> None:
        if len(results) >= max_results:
            return
        if pos == len(word):
            results.append(acc)
            return
        for length in (3, 2, 1):
            chunk = word[pos:pos + length]
            if len(chunk) == length and chunk in ALTERNATE_SPELLINGS:
                walk(pos + length, acc + ALTERNATE_SPELLINGS[chunk])

    walk(0, ())
    return results


def word_matches(indices: Sequence[int], english_word: str) -> bool:
    """True if the rune word `indices` is a valid spelling of `english_word`.

    Exact: a memoised walk over (position in word, position in runes). Unlike
    `spellings_of` it has no result cap, so it cannot miss a spelling of a long word.
    """
    word = english_word.upper()
    target = tuple(indices)
    memo: dict[tuple[int, int], bool] = {}

    def match(wp: int, tp: int) -> bool:
        key = (wp, tp)
        if key in memo:
            return memo[key]
        if wp == len(word):
            ok = tp == len(target)
        else:
            ok = False
            for length in (1, 2, 3):
                chunk = word[wp:wp + length]
                seq = ALTERNATE_SPELLINGS.get(chunk) if len(chunk) == length else None
                if seq is not None and target[tp:tp + len(seq)] == seq and match(wp + length, tp + len(seq)):
                    ok = True
                    break
        memo[key] = ok
        return ok

    return match(0, 0)
