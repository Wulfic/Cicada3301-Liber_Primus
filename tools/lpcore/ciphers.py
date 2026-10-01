"""Deterministic cipher primitives over the 29-rune alphabet.

Every function here computes exactly ONE decryption from fully specified parameters. There is no
search, scoring, or optimisation in this module, by design: hill-climbing is banned in this repo
(owner directive, 2026-09-29) and anything that searches belongs in an explicitly-labelled
hypothesis test that logs every candidate it tries.
"""

from __future__ import annotations

from collections.abc import Callable, Container, Iterable, Iterator, Sequence
from itertools import count, cycle, repeat

from .gematria import N

KeyStream = Iterator[int]


def invert(cipher: Iterable[int]) -> list[int]:
    """Reversed gematria (atbash): index i ↔ 28 − i. Solves A WARNING."""
    return [(N - 1 - c) % N for c in cipher]


def invert_shift(cipher: Iterable[int], shift: int) -> list[int]:
    """p = (28 − c + shift) mod 29, i.e. atbash then shift. Parameterised so a test can pin the sign."""
    return [(N - 1 - c + shift) % N for c in cipher]


def shift(cipher: Iterable[int], k: int) -> list[int]:
    """Caesar: p = c − k."""
    return [(c - k) % N for c in cipher]


def repeating_key(key: Sequence[int]) -> KeyStream:
    if not key:
        raise ValueError("repeating_key: empty key")
    return cycle([k % N for k in key])


def constant_key(k: int) -> KeyStream:
    return repeat(k % N)


def primes() -> Iterator[int]:
    """2, 3, 5, 7, … (incremental sieve, unbounded)."""
    composites: dict[int, list[int]] = {}
    for n in count(2):
        factors = composites.pop(n, None)
        if factors is None:
            yield n
            composites[n * n] = [n]
        else:
            for p in factors:
                composites.setdefault(n + p, []).append(p)


def totient_prime_stream(offset: int = 0) -> KeyStream:
    """φ(p) = p − 1 for p = 2, 3, 5, …, skipping the first `offset` primes. Solves AN END."""
    stream = primes()
    for _ in range(offset):
        next(stream)
    return (p - 1 for p in stream)


def apply_stream(
    cipher: Sequence[int],
    keystream: KeyStream,
    *,
    mode: str = "sub",
    skip: Container[int] = frozenset(),
) -> list[int]:
    """Stream decryption with interrupters.

    mode "sub": p = c − k (the mode of every keyed solved section); "add": p = c + k;
    "beaufort": p = k − c. Positions in `skip` are copied through unchanged and do NOT consume a
    key value — this is how the book leaves plaintext F unenciphered ("interrupters").
    """
    ops: dict[str, Callable[[int, int], int]] = {
        "sub": lambda c, k: c - k,
        "add": lambda c, k: c + k,
        "beaufort": lambda c, k: k - c,
    }
    if mode not in ops:
        raise ValueError(f"unknown mode {mode!r}; expected one of {sorted(ops)}")
    op = ops[mode]
    out: list[int] = []
    for i, c in enumerate(cipher):
        if i in skip:
            out.append(c)
        else:
            out.append(op(c, next(keystream)) % N)
    return out
