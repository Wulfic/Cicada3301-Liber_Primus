"""How every solved section of the Liber Primus decrypts — the single source of truth.

Each entry is asserted by tests/test_lpcore.py to reproduce the published English exactly from
canonical runes, so nothing here is a guess.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import ciphers
from .corpus import Corpus
from .gematria import runes_to_indices
from .verify import AlignmentError, english_words, interrupter_positions, split_like

DIVINITY = tuple(runes_to_indices("ᛞᛁᚢᛁᚾᛁᛏᚣ"))            # 23,10,1,10,9,10,16,26
FIRFUMFERENFE = tuple(runes_to_indices("ᚠᛁᚱᚠᚢᛗᚠᛖᚱᛖᚾᚠᛖ"))   # CIRCUMFERENCE with every C written F

SEGMENT_TITLES: dict[int, str] = {
    0: "A WARNING",
    1: "WELCOME / WISDOM",
    2: "SOME WISDOM / KNOW THIS (magic square, sum 1033)",
    3: "A KOAN / AN INSTRUCTION",
    4: "THE LOSS OF DIVINITY / SOME WISDOM / AN INSTRUCTION",
    5: "A KOAN (the I is the voice of the circumference)",
    6: "AN INSTRUCTION / KNOW THIS (magic square, sum 3301)",
    7: "unsolved — 'crosses/signs' (ᛋᚻᛖᚩᚷᛗᛡᚠ ᛋᚣᛖᛝᚳ)",
    8: "unsolved — 'sprouts' (ᛚᛄ ᛇᚻᛝᚳᚦᛏᚫᛄᛏᛉᚻ ᛏᚢᛟ)",
    9: "unsolved — 'roots' (ᛉᛁᛉᛗ ᚢᛉᛗᚳᚦᛈᚩᛒ)",
    10: "unsolved — ᚠᚢᛚᛗ ᚪᛠᚣᛟᚪ + 4×4 number square",
    11: "unsolved — 'moebius' (ᛚᚢᛝᚾ ᚳᚢ ᛒᚾᛏᚠᛝ)",
    12: "unsolved — 'dots/mayfly' (ᚢᚪ ᚹᛝᚷᛉᛞᚷ ᛁᛒᛁ ᛇᛏᛒᛁᚣ)",
    13: "unsolved — 'wing' (ᛗᛈᚣ ᛚᛋᚩᚪᚫᚻᛚᛖᛇᛁᛗᛚ ᛚᛋᚳᛈ)",
    14: "unsolved — 'cuneiform' (ᛝᚦᛇ ᛁᚠᚳᛟᛇ)",
    15: "unsolved — 'plants' (ᚠᚾᛗ ᚣᚷᛞᚫᚻ)",
    16: "AN END",
    17: "PARABLE",
}

# Verified corrections to the published English, keyed by (segment, word index).
ERRATA: dict[tuple[int, int], str] = {
    # The BOOK's own plaintext typo: the runes decrypt to W-I-D-S-O-M. Swapping two cipher runes
    # cannot yield a clean S/D swap unless the two key letters there are equal, and DIVINITY has
    # no equal adjacent letters — so the typo existed before encryption.
    (1, 95): "WIDSOM",
    # The upstream TRANSLATION's typo: the runes are F-O-L-L-O-W-ᛝ = FOLLOWING (ING rune).
    # ("BELEIVE" in the same clause IS in the runes and needs no correction.)
    (4, 24): "FOLLOWING",
}


@dataclass(frozen=True)
class SolvedSection:
    segment: int
    group: str                 # translation group in data/canonical/liber_primus_translation.txt
    paragraphs: tuple[int, ...]
    method: tuple              # ("plain",) | ("invert",) | ("invert_shift", k) | ("vigenere", key) | ("totient",)
    trailing_square: bool      # rune words after the English (magic-square cells) are expected
    description: str


SOLVED_SECTIONS: tuple[SolvedSection, ...] = (
    SolvedSection(0, "0.0", (0,), ("invert",), False, "reversed gematria (atbash): p = 28 − c"),
    SolvedSection(1, "0.1", (0, 1), ("vigenere", DIVINITY), False,
                  "Vigenère p = c − k, key DIVINITY, continuous over the whole segment; plaintext F left unenciphered"),
    SolvedSection(2, "0.1", (2, 3), ("plain",), True, "plaintext"),
    SolvedSection(3, "0.2", (0, 1), ("invert_shift", 3), False, "reversed gematria then +3: p = (28 − c + 3) mod 29"),
    SolvedSection(4, "0.3", (0, 1, 2), ("plain",), False, "plaintext"),
    SolvedSection(5, "0.4", (0,), ("vigenere", FIRFUMFERENFE), False,
                  "Vigenère p = c − k, key FIRFUMFERENFE, continuous (no resets); plaintext F left unenciphered"),
    SolvedSection(6, "0.4", (1, 2), ("plain",), True, "plaintext"),
    SolvedSection(16, "0.13", (0,), ("totient",), False,
                  "p = c − φ(pₙ) over primes 2,3,5,…; plaintext F left unenciphered (does not consume a prime)"),
    SolvedSection(17, "0.14", (0,), ("plain",), False, "plaintext"),
)

SOLVED_BY_SEGMENT = {s.segment: s for s in SOLVED_SECTIONS}


def expected_english(section: SolvedSection, translation: dict[str, list[list[str]]]) -> list[str]:
    english = [w for p in section.paragraphs for clause in translation[section.group][p] for w in english_words(clause)]
    for (seg, idx), word in ERRATA.items():
        if seg == section.segment:
            english[idx] = word
    return english


def decrypt_section(
    corpus: Corpus,
    translation: dict[str, list[list[str]]],
    section: SolvedSection,
    method: tuple | None = None,
) -> tuple[list[tuple[int, ...]], list[str]]:
    """(plaintext words for EVERY rune word of the segment, expected English words).

    Interrupters (plaintext F) are located from the expected English only. `method` overrides the
    section's own method — tests use that to prove a wrong key is detected.
    """
    method = method or section.method
    english = expected_english(section, translation)
    cipher_words = [w.runes for w in corpus.rune_words(section.segment)]
    if section.trailing_square:
        if len(cipher_words) < len(english):
            raise AlignmentError(f"segment {section.segment}: fewer rune words than English words")
        compared = cipher_words[:len(english)]
    else:
        compared = cipher_words
    stream = [r for cw in cipher_words for r in cw]
    kind = method[0]
    if kind == "plain":
        plain = list(stream)
    elif kind == "invert":
        plain = ciphers.invert(stream)
    elif kind == "invert_shift":
        plain = ciphers.invert_shift(stream, method[1])
    elif kind in ("vigenere", "totient"):
        skip = interrupter_positions(compared, english)
        keystream = ciphers.repeating_key(method[1]) if kind == "vigenere" else ciphers.totient_prime_stream()
        plain = ciphers.apply_stream(stream, keystream, mode="sub", skip=skip)
    else:
        raise ValueError(f"unknown method {method!r}")
    return split_like(plain, cipher_words), english
