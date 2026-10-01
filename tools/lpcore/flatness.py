"""Key-independent flatness bound for per-position alphabets c_i = σ_{k_i}(p_i) (TODO stage T).

A key value v picks its own alphabet σ_v, with weight w_v. The cipher marginal is then a mixture,
P(c) = Σ_v w_v q(σ_v⁻¹(c)), and a χ² against flat sees its noncentrality λ = n·29·Σ_c (P(c) − 1/29)².

If the σ_v are independent uniformly random permutations (a secret tabula with unstructured rows), then

    E[λ] = λ̄ = n·(29·Σq² − 1)·Σw²,

and by permutation symmetry the deviation is isotropic in the 28-dim sum-zero space. With a CLT over the classes,
the observed χ² is about (1 + λ̄/28)·χ²₂₈. Only the weights enter, never the key's order, so the bound holds under any
desync, drift or re-key rule that redraws a class from the same weights.

A Latin-square tabula (Vigenère, Quagmire, affine with flat shifts) under a near-flat key has an exactly flat mixture.
This test cannot see it, and it says nothing about it.
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Hashable, Iterable, Sequence

import numpy as np

from .gematria import N

DF = N - 1


def chi2_uniform(runes: Iterable[int]) -> tuple[float, int]:
    """(Pearson χ² of the rune counts against flat, number of runes)."""
    counts = Counter(runes)
    n = sum(counts.values())
    if n == 0:
        raise ValueError("chi2_uniform: no runes")
    e = n / N
    return sum((counts[r] - e) ** 2 / e for r in range(N)), n


def chi2_cdf_even(x: float, df: int) -> float:
    """P(χ²_df ≤ x), exact for even df: 1 − e^{−x/2} Σ_{j<df/2} (x/2)^j / j!."""
    if df <= 0 or df % 2:
        raise ValueError(f"chi2_cdf_even needs a positive even df, got {df}")
    if x <= 0:
        return 0.0
    h = x / 2
    term, total = 1.0, 1.0
    for j in range(1, df // 2):
        term *= h / j
        total += term
    return max(0.0, 1.0 - math.exp(-h) * total) if h < 700 else 1.0


def chi2_cdf_small(x: float, df: int) -> float:
    """P(χ²_df ≤ x) for even df without cancellation when it is tiny: e^{−x/2} Σ_{j≥df/2} (x/2)^j / j!."""
    if df <= 0 or df % 2:
        raise ValueError(f"chi2_cdf_small needs a positive even df, got {df}")
    if x <= 0:
        return 0.0
    h = x / 2
    m = df // 2
    log_first = m * math.log(h) - h - math.lgamma(m + 1)
    term, total, j = 1.0, 1.0, m
    while term > 1e-17 * total:
        j += 1
        term *= h / j
        total += term
    return min(1.0, math.exp(log_first) * total)


def noncentral_chi2_cdf(x: float, df: int, lam: float) -> float:
    """P(χ²_df(λ) ≤ x) for even df: a Poisson(λ/2) mixture of central χ²_{df+2j}."""
    if lam < 0:
        raise ValueError("noncentrality must be ≥ 0")
    if lam == 0:
        return chi2_cdf_small(x, df)
    half = lam / 2
    jmax = int(half + 40 * math.sqrt(half + 1) + 50)
    return sum(math.exp(j * math.log(half) - half - math.lgamma(j + 1)) * chi2_cdf_small(x, df + 2 * j)
               for j in range(jmax + 1))


def lambda_max(chi2: float, df: int, alpha: float) -> float:
    """The noncentrality λ at which P(χ²_df(λ) ≤ chi2) = alpha (bisection; the CDF falls as λ grows)."""
    if not 0 < alpha < noncentral_chi2_cdf(chi2, df, 0.0):
        raise ValueError("alpha must lie below the central CDF at chi2")
    lo, hi = 0.0, 1.0
    while noncentral_chi2_cdf(chi2, df, hi) > alpha:
        hi *= 2
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if noncentral_chi2_cdf(chi2, df, mid) > alpha else (lo, mid)
    return (lo + hi) / 2


def coincidence(plain: Sequence[int]) -> float:
    """Σq² of a plaintext rune stream."""
    if not plain:
        raise ValueError("coincidence: empty plaintext")
    return sum((c / len(plain)) ** 2 for c in Counter(plain).values())


def v_eff(key: Iterable[Hashable]) -> float:
    """1/Σw² of a key's class frequencies: the number of equal classes with the same collision rate."""
    counts = Counter(key)
    n = sum(counts.values())
    if n == 0:
        raise ValueError("v_eff: empty key")
    return n * n / sum(c * c for c in counts.values())


def mean_noncentrality(n: int, s: float, v: float) -> float:
    """λ̄ = n·(29s − 1)/V for V effective classes of random alphabets."""
    if v <= 0:
        raise ValueError("V must be positive")
    return n * (N * s - 1) / v


def random_tabula_p(chi2: float, n: int, s: float, v: float) -> float:
    """P(χ² ≤ observed) for one random tabula with V effective classes: F₂₈(χ² / (1 + λ̄/28))."""
    return chi2_cdf_small(chi2 / (1 + mean_noncentrality(n, s, v) / DF), DF)


def per_section_p(total: float, sizes: Sequence[int], s: float, v: float, draws: np.ndarray) -> float:
    """P(Σ_s χ²_s ≤ total) for a fresh random tabula per section, by Monte Carlo over fixed χ²₂₈ draws.

    `draws` has shape (trials, len(sizes)). Reusing the same draws for every V keeps P monotone in V.
    """
    if draws.ndim != 2 or draws.shape[1] != len(sizes):
        raise ValueError("draws must have one column per section")
    scales = np.array([1 + mean_noncentrality(m, s, v) / DF for m in sizes])
    return float(np.mean(draws @ scales <= total))


def chi2_draws(trials: int, sections: int, seed: int) -> np.ndarray:
    return np.random.default_rng(seed).chisquare(DF, size=(trials, sections))


def boundary(p_of_v, alpha: float, v_max: int = 1_000_000) -> int:
    """The largest integer V with p_of_V(V) ≤ alpha (P rises with V). 0 if even V = 1 is not excluded."""
    if p_of_v(1) > alpha:
        return 0
    if p_of_v(v_max) <= alpha:
        raise ValueError(f"still excluded at V = {v_max}")
    lo, hi = 1, v_max
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (mid, hi) if p_of_v(mid) <= alpha else (lo, mid)
    return lo
