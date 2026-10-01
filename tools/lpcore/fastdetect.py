"""numpy implementation of `detect.log_lr` (TODO stage R), for families with many start phases.

Same model, same pruning rule, same result to ~1e-9 nats (tests/test_detect.py asserts the equality). The
reference is `detect.log_lr`: if the two ever disagree, this module is wrong. It is ~5× faster when the start prior
spans tens of thousands of phases (a 58,152-byte key read from an unknown offset). Needs numpy; `detect` does not.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np

from . import detect
from .gematria import N


def log_lr(
    cipher: Sequence[int],
    key: Sequence[int],
    q: Sequence[float],
    *,
    mode: str = "sub",
    shift: int = 0,
    starts: Sequence[int] = (0,),
    rho: float = detect.RHO,
    eps: float = detect.EPS,
    prune: float = detect.PRUNE,
) -> float:
    """`detect.log_lr(cipher, key, q, mode=, shift=, starts=)`, computed with arrays."""
    if mode not in detect.MODES:
        raise ValueError(f"unknown mode {mode!r}; expected one of {detect.MODES}")
    if not 0 <= rho < 0.5:
        raise ValueError("rho must be in [0, 0.5)")
    if not cipher:
        raise ValueError("log_lr: empty cipher")
    if not key:
        raise ValueError("fastdetect.log_lr: empty key (use detect.log_lr)")
    idx = np.unique(np.asarray(starts, dtype=np.int64))
    if len(idx) == 0 or len(idx) != len(starts):
        raise ValueError("starts must be non-empty and must not repeat")
    ratio = np.asarray(detect.emission_ratios(q, eps))
    keyed = (np.asarray(key, dtype=np.int64) + shift) % N
    length = len(keyed)
    weight = np.full(len(idx), 1.0 / len(idx))
    stay, advance, skip = rho, 1 - 2 * rho, rho

    total = 0.0
    for i, c in enumerate(cipher):
        if i:
            idx, inverse = np.unique(np.concatenate((idx, idx + 1, idx + 2)), return_inverse=True)
            moved = np.concatenate((weight * stay, weight * advance, weight * skip))
            weight = np.bincount(inverse, weights=moved, minlength=len(idx))
        k = keyed[np.minimum(idx, length - 1)]
        if mode == "sub":
            p = (c - k) % N
        elif mode == "add":
            p = (c + k) % N
        else:
            p = (k - c) % N
        weight = weight * np.where(idx < length, ratio[p], 1.0)
        norm = float(weight.sum())
        if norm <= 0.0:
            raise ArithmeticError(f"forward mass vanished at position {i}")
        total += math.log(norm)
        weight /= norm
        keep = weight >= weight.max() * prune
        idx, weight = idx[keep], weight[keep]
    return total
