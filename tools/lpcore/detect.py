"""Does a candidate key stream decrypt a rune stream, allowing the key to drift? (TODO stage I)

The unsolved text dodges doublets (C8): a would-be doublet is re-keyed about 81 % of the time. If the re-keying
consumes key values, key and cipher drift out of step every ~36 runes and a fixed-sync decode of the right key
looks like noise. `log_lr` sums over every drift path with the forward algorithm, so it is exact inference:
nothing is maximised or fitted.

Model, at cipher position i with key index j:
    step     j → j+1 (1 − 2ρ) · j → j+2, a skipped key value (ρ) · j → j, a stalled key / interrupter (ρ)
    emission r = (1 − ε)·29·q(p) + ε, where p is the decoded rune and q the plaintext unigram model

The result is log LR = log Σ_paths Π r against "the decode is uniform noise". Under that null E[r] = 1 at every
step, so E[LR] = 1 and P(log LR ≥ T) ≤ e^−T (Markov). Pruning only removes positive terms, so it keeps the bound.
Unigram emissions are blind to the order of the plaintext: a transposition before encryption still scores.
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Sequence

from .gematria import N

THRESHOLD = 30.0          # nats; declared in TODO.md before any candidate ran
RHO = 0.02
EPS = 0.1
PRUNE = 1e-12
MODES = ("sub", "add", "beaufort")


def unigram(plain: Sequence[int]) -> list[float]:
    """Add-one smoothed rune frequencies of a plaintext stream."""
    if not plain:
        raise ValueError("unigram: empty plaintext")
    counts = Counter(plain)
    total = len(plain) + N
    return [(counts[r] + 1) / total for r in range(N)]


def emission_ratios(q: Sequence[float], eps: float = EPS) -> list[float]:
    if len(q) != N or abs(sum(q) - 1.0) > 1e-9:
        raise ValueError("q must be a distribution over the 29 runes")
    return [(1 - eps) * N * q[p] + eps for p in range(N)]


def _decoder(mode: str):
    if mode == "sub":
        return lambda c, k: (c - k) % N
    if mode == "add":
        return lambda c, k: (c + k) % N
    if mode == "beaufort":
        return lambda c, k: (k - c) % N
    raise ValueError(f"unknown mode {mode!r}; expected one of {MODES}")


def log_lr(
    cipher: Sequence[int],
    key: Sequence[int],
    q: Sequence[float],
    *,
    mode: str = "sub",
    shift: int = 0,
    start: int = 0,
    starts: Sequence[int] | None = None,
    rho: float = RHO,
    eps: float = EPS,
    prune: float = PRUNE,
) -> float:
    """Drift-tolerant log likelihood ratio (nats) that `key` + `shift` decrypts `cipher` in `mode`.

    Positions where the key index has run past the end of `key` carry no information (r = 1).
    `starts` replaces `start` with a uniform prior over several start indices (an unknown key phase or offset).
    The result is then the log of the mean LR over those starts, so the e^−T bound still holds per call.
    """
    if not 0 <= rho < 0.5:
        raise ValueError("rho must be in [0, 0.5)")
    if not cipher:
        raise ValueError("log_lr: empty cipher")
    decode = _decoder(mode)
    ratio = emission_ratios(q, eps)
    keyed = [(k + shift) % N for k in key]
    length = len(keyed)
    stay, skip, advance = rho, rho, 1 - 2 * rho

    if starts is not None:
        if start != 0:
            raise ValueError("pass start or starts, not both")
        if not starts:
            raise ValueError("starts must not be empty")
        alpha: dict[int, float] = {j: 1.0 / len(starts) for j in starts}
        if len(alpha) != len(starts):
            raise ValueError("starts must not repeat")
    else:
        alpha = {start: 1.0}
    total = 0.0
    for i, c in enumerate(cipher):
        if i:
            nxt: dict[int, float] = {}
            for j, w in alpha.items():
                nxt[j] = nxt.get(j, 0.0) + w * stay
                nxt[j + 1] = nxt.get(j + 1, 0.0) + w * advance
                nxt[j + 2] = nxt.get(j + 2, 0.0) + w * skip
            alpha = nxt
        norm = 0.0
        for j in alpha:
            w = alpha[j] * (ratio[decode(c, keyed[j])] if j < length else 1.0)
            alpha[j] = w
            norm += w
        if norm <= 0.0:
            raise ArithmeticError(f"forward mass vanished at position {i}")
        total += math.log(norm)
        floor = max(alpha.values()) / norm * prune
        alpha = {j: w / norm for j, w in alpha.items() if w / norm >= floor}
    return total


def fixed_sync_log_lr(
    cipher: Sequence[int], key: Sequence[int], q: Sequence[float], *, mode: str = "sub", shift: int = 0,
    eps: float = EPS,
) -> float:
    """The same score with the key locked to the cipher (no drift): what a naive decode measures."""
    decode = _decoder(mode)
    ratio = emission_ratios(q, eps)
    return sum(math.log(ratio[decode(c, (k + shift) % N)]) for c, k in zip(cipher, key))
