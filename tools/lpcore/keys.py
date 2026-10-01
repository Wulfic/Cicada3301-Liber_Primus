"""Candidate key streams for stage I, and a reference encryptor with an anti-doublet rule (for controls).

Every stream is fully determined by its definition; nothing is fitted. A constant shift and the mode are applied
by `detect.log_lr`, so `primes` also stands for p ± 1, φ(p) = p − 1 and 3301 − p (3301 ≡ 24 mod 29).
"""

from __future__ import annotations

import random
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
