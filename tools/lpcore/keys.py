"""Candidate key streams for stage I, and a reference encryptor with an anti-doublet rule (for controls).

Every stream is fully determined by its definition; nothing is fitted. A constant shift and the mode are applied
by `detect.log_lr`, so `primes` also stands for p ± 1, φ(p) = p − 1 and 3301 − p (3301 ≡ 24 mod 29).
"""

from __future__ import annotations

import random
import string
from collections.abc import Sequence
from itertools import islice

from .ciphers import primes
from .corpus import Corpus
from .gematria import N, PRIME_VALUES, gematria_sum
from .solved import SOLVED_SECTIONS, decrypt_section


def solved_plaintext_words(corpus: Corpus, translation: dict[str, list[list[str]]],
                           exclude: Sequence[int] = ()) -> list[tuple[int, ...]]:
    """Plaintext rune words of every solved section in book order (magic-square cells dropped)."""
    out: list[tuple[int, ...]] = []
    for section in SOLVED_SECTIONS:
        if section.segment in exclude:
            continue
        words, english = decrypt_section(corpus, translation, section)
        out += words[:len(english)]
    return out


def prime_stream(length: int) -> list[int]:
    """K-A: p(1), p(2), … = 2, 3, 5, 7, …"""
    return list(islice(primes(), length))


def word_sum_stream(words: Sequence[Sequence[int]]) -> list[int]:
    """K-C: gematria sum of each solved-plaintext word, one value per cipher rune."""
    return [gematria_sum(w) for w in words]


def plaintext_value_stream(words: Sequence[Sequence[int]]) -> list[int]:
    """K-D: prime value of each solved-plaintext rune, in order."""
    return [PRIME_VALUES[r] for w in words for r in w]


BASE60_DIGITS = string.digits + string.ascii_uppercase + string.ascii_lowercase[:24]   # 0-9 A-Z a-x
GRID_SCANS = (66, 67)
GRID_SEGMENT = 15


def grid_tokens(corpus: Corpus) -> list[str]:
    """The two-character base-60 tokens of the scan 66–67 grid, in reading order."""
    tokens = [w.text for w in corpus.words if w.kind == "number" and w.scan in GRID_SCANS]
    bad = [t for t in tokens if len(t) != 2 or any(ch not in BASE60_DIGITS for ch in t)]
    if bad or not tokens:
        raise ValueError(f"unexpected grid tokens: {bad[:5]} (of {len(tokens)})")
    return tokens


def grid_bytes(corpus: Corpus) -> list[int]:
    """G-B: each token as 60·a + b. All 184 values are below 256, so the grid is a byte stream."""
    values = [60 * BASE60_DIGITS.index(a) + BASE60_DIGITS.index(b) for a, b in grid_tokens(corpus)]
    if max(values) > 255:
        raise ValueError(f"grid value {max(values)} is not a byte")
    return values


def grid_5bit(corpus: Corpus) -> list[int]:
    """G-5: the grid's bits regrouped into 5-bit values, most significant bit first (a short tail is dropped)."""
    bits = "".join(f"{v:08b}" for v in grid_bytes(corpus))
    return [int(bits[i:i + 5], 2) for i in range(0, len(bits) - 4, 5)]


def grid_digits(corpus: Corpus) -> list[int]:
    """G-D: the single base-60 digits of the grid, two per token."""
    return [BASE60_DIGITS.index(ch) for t in grid_tokens(corpus) for ch in t]


def grid_rune_offset(corpus: Corpus) -> int:
    """Index, within segment 15's rune stream, of the first rune after the grid begins."""
    count = 0
    for w in corpus.words:
        if w.segment != GRID_SEGMENT:
            continue
        if w.kind == "number" and w.scan in GRID_SCANS:
            return count
        count += len(w.runes)
    raise ValueError("grid not found in segment 15")


AN_END_SCAN = 73


def an_end_hash(corpus: Corpus) -> bytes:
    """The 64-byte hash printed on AN END (scan 73): 'within the deep web there exists a page that hashes to'."""
    hexdigits = "".join(w.text for w in corpus.words if w.kind == "number" and w.scan == AN_END_SCAN)
    if len(hexdigits) != 128 or any(ch not in "0123456789abcdef" for ch in hexdigits):
        raise ValueError(f"AN END hash has unexpected form: {hexdigits[:20]}… ({len(hexdigits)} chars)")
    return bytes.fromhex(hexdigits)


def random_key(length: int, seed: int) -> list[int]:
    rng = random.Random(seed)
    return [rng.randrange(N) for _ in range(length)]


def encrypt_dodging(plain: Sequence[int], key: Sequence[int], *, keep: float, seed: int,
                    rekey: str = "next") -> list[int]:
    """c = p + k, except that a would-be doublet is re-keyed with probability 1 − keep.

    rekey "next": use the NEXT key value and consume it, so the key drifts (a C8 "skip" rule).
    rekey "fresh": use an independent random value and consume nothing, so the key stays in step.
    keep = 0.19 gives the leak rate measured in findings §7. Raises IndexError if the key runs out.
    """
    if rekey not in ("next", "fresh"):
        raise ValueError(f"unknown rekey {rekey!r}")
    rng = random.Random(seed)
    out: list[int] = []
    j = 0
    for p in plain:
        c = (p + key[j]) % N
        j += 1
        if out and c == out[-1] and rng.random() >= keep:
            if rekey == "next":
                c = (p + key[j]) % N
                j += 1
            else:
                c = (p + rng.randrange(N)) % N
        out.append(c)
    return out
