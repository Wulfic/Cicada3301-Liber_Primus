"""Label-free test for per-position alphabets c_i = σ_{k_i}(p_i) (TODO stage S).

A key value v picks one secret permutation σ_v of the 29 runes. Every cipher rune in class v is then σ_v of a
plaintext rune, so inside a class the cipher repeats itself as often as the plaintext does (s = Σq² ≈ 0.062), not
1/29. The score never uses plaintext labels, so it is blind to σ: it covers mixed-alphabet tabulae, a running key
with a secret tabula, and the additive case alike.

Per class the emission model is a symmetric Dirichlet-multinomial (DM) with α = (1 − s)/(29s − 1), which is the α
whose expected coincidence rate is s. For one key phase t,

    LR(t) = Π_v DM(cipher runes in class v; α) / 29^−n.

DM is a proper distribution over sequences, so under an iid-uniform cipher E[LR(t)] = 1 for every fixed t.
`log_mean_lr` averages LR over a set of phases (a uniform prior on an unknown phase, as in stage R), so the result
keeps P(score ≥ T) ≤ e^−T with no calibration. Fewer coincidences than uniform (LP2's doublet deficit) only lowers
the score.

The key must stay in step with the cipher. Under even 1 % desync the classes smear and the test loses its power.
"""

from __future__ import annotations

import math
import random
from collections import Counter
from collections.abc import Hashable, Sequence

import numpy as np

from .gematria import N


def dm_alpha(plain: Sequence[int]) -> float:
    """α of the symmetric Dirichlet whose expected coincidence rate equals the plaintext's Σq²."""
    if not plain:
        raise ValueError("dm_alpha: empty plaintext")
    counts = Counter(plain)
    s = sum((c / len(plain)) ** 2 for c in counts.values())
    if not 1 / N < s < 1:
        raise ValueError(f"plaintext coincidence rate {s} is not above uniform")
    return (1 - s) / (N * s - 1)


def log_lr(cipher: Sequence[int], classes: Sequence[Hashable], alpha: float) -> float:
    """Reference: log LR (nats) of one fixed classing of the cipher positions. `classes[i]` labels position i."""
    if len(classes) < len(cipher):
        raise ValueError(f"{len(classes)} classes for {len(cipher)} cipher runes")
    table: dict[Hashable, Counter[int]] = {}
    for v, c in zip(classes, cipher):
        table.setdefault(v, Counter())[c] += 1
    total = len(cipher) * math.log(N)
    for counts in table.values():
        n = sum(counts.values())
        total += math.lgamma(N * alpha) - math.lgamma(N * alpha + n)
        total += sum(math.lgamma(alpha + m) - math.lgamma(alpha) for m in counts.values())
    return total


def class_indices(key: Sequence[Hashable]) -> tuple[np.ndarray, int]:
    """Relabel key values as 0…V−1 in order of first appearance. Returns (indices, V)."""
    labels: dict[Hashable, int] = {}
    out = np.fromiter((labels.setdefault(v, len(labels)) for v in key), dtype=np.int64, count=len(key))
    return out, len(labels)


def phase_log_lrs(cipher: Sequence[int], key: Sequence[Hashable], phases: int, alpha: float, *,
                  cyclic: bool) -> np.ndarray:
    """log LR(t) for t = 0 … phases−1, where position i falls in class key[t + i] (indices wrap if `cyclic`).

    Counts n_vx(t) = #{i : key[t + i] = v, cipher[i] = x} come from FFT cross-correlation of the indicator
    sequences, rounded to integers (tests assert they equal a direct count).
    """
    n = len(cipher)
    if n == 0 or phases < 1:
        raise ValueError("phase_log_lrs: empty cipher or no phases")
    if any(not 0 <= c < N for c in cipher):
        raise ValueError("cipher runes must be 0..28")
    span = phases + n - 1
    if cyclic:
        if phases > len(key):
            raise ValueError(f"{phases} phases for a cyclic key of length {len(key)}")
        reps = span // len(key) + 1
        key = list(key) * reps
    elif span > len(key):
        raise ValueError(f"linear key of length {len(key)} is too short for {phases} phases of {n} runes")
    idx, n_classes = class_indices(key[:span])
    size = 1 << (span - 1).bit_length()
    c = np.asarray(cipher, dtype=np.int64)
    cipher_fft = [np.conj(np.fft.rfft((c == x).astype(np.float64), size)) for x in range(N)]
    top = n + 1
    lg_cell = np.array([math.lgamma(alpha + m) - math.lgamma(alpha) for m in range(top)])
    lg_class = np.array([math.lgamma(N * alpha) - math.lgamma(N * alpha + m) for m in range(top)])
    total = np.full(phases, n * math.log(N))
    for v in range(n_classes):
        key_fft = np.fft.rfft((idx == v).astype(np.float64), size)
        in_class = np.zeros(phases, dtype=np.int64)
        for x in range(N):
            counts = np.rint(np.fft.irfft(key_fft * cipher_fft[x], size)[:phases]).astype(np.int64)
            in_class += counts
            total += lg_cell[counts]
        total += lg_class[in_class]
    return total


def log_mean_lr(cipher: Sequence[int], key: Sequence[Hashable], phases: int, alpha: float, *,
                cyclic: bool) -> tuple[float, int, float]:
    """(log of the mean LR over every phase, the best single phase, its log LR). The first value is the test."""
    per_phase = phase_log_lrs(cipher, key, phases, alpha, cyclic=cyclic)
    best = int(np.argmax(per_phase))
    top = float(per_phase[best])
    return top + math.log(float(np.exp(per_phase - top).sum())) - math.log(phases), best, top


def encrypt_alphabets(plain: Sequence[int], key: Sequence[Hashable], *, keep: float, seed: int) -> list[int]:
    """Positive control: c_i = σ_{key[i]}(p_i), one random permutation per class, in step.

    A would-be doublet is re-keyed with probability 1 − keep, by a fresh draw of a key value from `key` itself (the
    key stays in step, as encrypt_dodging's rekey="fresh"). Raises IndexError if the key is shorter than the text.
    """
    rng = random.Random(seed)
    sigma: dict[Hashable, list[int]] = {}

    def alphabet(v: Hashable) -> list[int]:
        if v not in sigma:
            perm = list(range(N))
            rng.shuffle(perm)
            sigma[v] = perm
        return sigma[v]

    out: list[int] = []
    for i, p in enumerate(plain):
        c = alphabet(key[i])[p]
        if out and c == out[-1] and rng.random() >= keep:
            c = alphabet(key[rng.randrange(len(key))])[p]
        out.append(c)
    return out
