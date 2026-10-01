"""Latin-square (Quagmire) tabulae c_i = π₂(π₁(p_i) + κ_i), κ_i = π₃(k_i) (TODO stage U).

For a fixed key stream this is the additive cipher on x = π₁(p), with its output renamed by π₂. A ciphertext statistic
that depends only on equality patterns (doublets, lag repeats, χ² against flat) cannot see π₂. A plaintext model
that uses only the multiset of q cannot see π₁. Under a flat iid key the cipher is uniform iid whatever π is.

Two key-independent handles survive the relabelling:

* **Doublets (C17).** For an iid key with value distribution b, independent of the plaintext,
  P(κ_{i+1} − κ_i = e) = (1/29)·Σ_f |b̂(f)|²·ω^{fe} lies in [2/29 − Σb², Σb²]. The doublet rate is that probability
  averaged over the plaintext's differences, so it lies in the same interval for any π and any plaintext.
* **Flatness (C18).** The cipher marginal is π₂(π₁q ⊛ π₃b). If π₁ is uniformly random, E|â(f)|² = (29Σq² − 1)/28
  at every f ≠ 0, so E[λ] = n·(29Σq² − 1)(29Σb² − 1)/28 for any b. Each draw's λ is computed exactly.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np

from . import keys
from .gematria import N

DF = N - 1


def encrypt(plain: Sequence[int], key: Sequence[int], pi1: Sequence[int], pi2: Sequence[int], *, keep: float,
            seed: int) -> list[int]:
    """c = π₂(π₁(p) + κ), with a would-be doublet re-keyed by a fresh value with probability 1 − keep.

    `key` is the relabelled key κ (apply π₃ before calling). A doublet in c is a doublet in π₁(p) + κ, since π₂ is a
    bijection, so dodging in either space is the same rule.
    """
    for name, pi in (("pi1", pi1), ("pi2", pi2)):
        if sorted(pi) != list(range(N)):
            raise ValueError(f"{name} is not a permutation of 0..{N - 1}")
    y = keys.encrypt_dodging([pi1[p] for p in plain], key, keep=keep, seed=seed, rekey="fresh")
    return [pi2[v] for v in y]


def _distribution(b: Sequence[float]) -> np.ndarray:
    arr = np.asarray(b, dtype=float)
    if arr.shape != (N,) or arr.min() < 0 or not math.isclose(arr.sum(), 1.0, abs_tol=1e-9):
        raise ValueError("need a probability distribution over 29 values")
    return arr


def key_difference_distribution(b: Sequence[float]) -> np.ndarray:
    """P(κ_{i+1} − κ_i = e) for an iid key with distribution b: K(e) = Σ_j b_j·b_{j+e}."""
    arr = _distribution(b)
    return np.array([float(arr @ np.roll(arr, -e)) for e in range(N)])


def doublet_rate_interval(b: Sequence[float]) -> tuple[float, float]:
    """(max(0, 2/29 − Σb²), Σb²): the doublet rate of c = π₂(π₁(p) + κ) for an iid key κ ~ b, any π, any plaintext."""
    s = float(np.sum(_distribution(b) ** 2))
    return max(0.0, 2 / N - s), s


def doublet_rate(bigrams: np.ndarray, pi1: Sequence[int], b: Sequence[float]) -> float:
    """Exact doublet rate before any dodging rule: Σ_{p,p'} B(p,p')·K(π₁(p) − π₁(p'))."""
    if bigrams.shape != (N, N) or not math.isclose(float(bigrams.sum()), 1.0, abs_tol=1e-9):
        raise ValueError("bigrams must be a 29×29 joint distribution")
    k = key_difference_distribution(b)
    x = np.asarray(pi1)
    return float(np.sum(bigrams * k[(x[:, None] - x[None, :]) % N]))


def min_key_coincidence(rate: float) -> float:
    """The smallest Σb² of an iid key that can bring the doublet rate down to `rate`: 2/29 − rate."""
    return 2 / N - rate


def mean_noncentrality(n: int, s_plain: float, s_key: float) -> float:
    """E[λ] = n·(29Σq² − 1)(29Σb² − 1)/28 when π₁ is uniformly random (π₃ and π₂ do not matter)."""
    return n * (N * s_plain - 1) * (N * s_key - 1) / DF


def random_permutations(count: int, rng: np.random.Generator) -> np.ndarray:
    """`count` independent uniformly random permutations of 0..28, one per row."""
    return np.argsort(rng.random((count, N)), axis=1)


def deviations(q: Sequence[float], b: Sequence[float], count: int, rng: np.random.Generator, *,
               tied: bool) -> np.ndarray:
    """δ = 29·Σ_c (r_c − 1/29)² per draw, r = π₁q ⊛ π₃b, for `count` draws of random π₁ and π₃ (π₃ = π₁ if tied).

    The noncentrality of a χ² on n runes is λ = n·δ. π₂ permutes r and leaves δ unchanged.
    """
    qa, ba = _distribution(q), _distribution(b)
    p1 = random_permutations(count, rng)
    p3 = p1 if tied else random_permutations(count, rng)
    a = np.zeros((count, N))
    k = np.zeros((count, N))
    rows = np.arange(count)[:, None]
    a[rows, p1] = qa                       # π₁q: the plaintext letter p lands on π₁(p)
    k[rows, p3] = ba
    r = np.real(np.fft.ifft(np.fft.fft(a, axis=1) * np.fft.fft(k, axis=1), axis=1))
    return N * np.sum((r - 1 / N) ** 2, axis=1)


def _poisson_tails(h: float, m_max: int) -> np.ndarray:
    """T[m] = P(Poisson(h) ≥ m) for m = 0..m_max, by a reverse sum (no cancellation in the far tail)."""
    top = m_max + int(h + 40 * math.sqrt(h + 1) + 50)
    i = np.arange(top + 1)
    log_fact = np.concatenate(([0.0], np.cumsum(np.log(np.arange(1, top + 1)))))
    pmf = np.exp(i * math.log(h) - h - log_fact) if h > 0 else (i == 0).astype(float)
    return np.cumsum(pmf[::-1])[::-1][:m_max + 1]


def noncentral_cdf(x: float, df: int, lams: np.ndarray, chunk: int = 2000) -> np.ndarray:
    """P(χ²_df(λ) ≤ x) for each λ in `lams` (even df), vectorised.

    The noncentral χ² is a Poisson(λ/2) mixture of central χ²_{df+2j}, and for even df the central CDF is
    P(χ²_{2m} ≤ x) = P(Poisson(x/2) ≥ m). Agrees with `flatness.noncentral_chi2_cdf`.
    """
    if df <= 0 or df % 2:
        raise ValueError(f"noncentral_cdf needs a positive even df, got {df}")
    lams = np.asarray(lams, dtype=float)
    if lams.size and lams.min() < 0:
        raise ValueError("noncentrality must be ≥ 0")
    if x <= 0:
        return np.zeros_like(lams)
    out = np.empty_like(lams)
    for start in range(0, lams.size, chunk):
        part = lams.flat[start:start + chunk]
        half = part / 2
        jmax = int(half.max() + 40 * math.sqrt(half.max() + 1) + 50)
        tails = _poisson_tails(x / 2, df // 2 + jmax)[df // 2:]
        j = np.arange(jmax + 1)
        log_fact = np.concatenate(([0.0], np.cumsum(np.log(np.arange(1, jmax + 1)))))
        with np.errstate(divide="ignore", invalid="ignore"):
            logw = j[None, :] * np.log(half[:, None]) - half[:, None] - log_fact[None, :]
        logw = np.where(half[:, None] == 0, np.where(j[None, :] == 0, 0.0, -np.inf), logw)
        out.flat[start:start + chunk] = np.minimum(1.0, np.exp(logw) @ tails)
    return out


def family_p(chi2: float, df: int, lams: np.ndarray, chunk: int = 2000, floor: float = 1e-15) -> float:
    """P(χ² ≤ observed) under the family: the mean over alphabet draws of the noncentral CDF.

    The CDF falls as λ grows, so draws are scored in ascending order and the rest are dropped once a whole chunk is
    below `floor`. That changes the mean by less than `floor`.
    """
    ordered = np.sort(np.asarray(lams, dtype=float))
    total = 0.0
    for start in range(0, ordered.size, chunk):
        part = noncentral_cdf(chi2, df, ordered[start:start + chunk], chunk)
        total += float(part.sum())
        if part.max() < floor:
            break
    return total / ordered.size
