"""Statistics of rune streams — the key-independent facts about the unsolved text.

Every function is deterministic and parameter-free beyond its inputs; nothing here searches.
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Iterable, Sequence
from itertools import islice
from operator import eq

from .ciphers import primes
from .corpus import Corpus
from .gematria import N

UNSOLVED_SEGMENTS = tuple(range(7, 16))


def ioc(stream: Sequence[int]) -> float:
    """Normalised index of coincidence: 1.0 for uniform random text, ~1.7–1.9 for LP English."""
    n = len(stream)
    if n < 2:
        raise ValueError("ioc needs at least 2 runes")
    counts = Counter(stream)
    return N * sum(v * (v - 1) for v in counts.values()) / (n * (n - 1))


def lag_repeats(streams: Iterable[Sequence[int]], lag: int) -> tuple[int, int]:
    """(# positions i with s[i] == s[i+lag], # positions compared), summed over independent streams."""
    if lag < 1:
        raise ValueError("lag must be >= 1")
    hits = total = 0
    for s in streams:
        m = len(s) - lag
        if m > 0:
            total += m
            hits += sum(1 for i in range(m) if s[i] == s[i + lag])
    return hits, total


def difference_distribution(stream: Sequence[int]) -> list[float]:
    """P(s[i+1] − s[i] ≡ d mod 29) for d = 0..28."""
    diffs = Counter((stream[i + 1] - stream[i]) % N for i in range(len(stream) - 1))
    total = sum(diffs.values())
    if total == 0:
        raise ValueError("difference_distribution needs at least 2 runes")
    return [diffs[d] / total for d in range(N)]


def predicted_doublet_rate(plain_diffs: Sequence[float], key_diffs: Sequence[float]) -> float:
    """Doublet rate of c = p + k when key and plaintext are independent.

    c[i+1] = c[i]  ⇔  Δp ≡ −Δk, so the rate is Σ_d P(Δp = d)·P(Δk = −d). Key-text independent:
    it needs only the difference distributions, never a key.
    """
    return sum(plain_diffs[d] * key_diffs[(-d) % N] for d in range(N))


def doublets_by_boundary(corpus: Corpus, segments: Iterable[int] = UNSOLVED_SEGMENTS) -> dict[str, tuple[int, int]]:
    """{"within-word": (doublets, pairs), "across-word": (doublets, pairs)} over the given segments.

    Pairs never cross a segment boundary. A pair is "across-word" when a word break separates it.
    """
    out = {"within-word": [0, 0], "across-word": [0, 0]}
    for seg in segments:
        words = corpus.rune_words(seg)
        prev_last: int | None = None
        for w in words:
            if prev_last is not None:
                out["across-word"][1] += 1
                out["across-word"][0] += w.runes[0] == prev_last
            for a, b in zip(w.runes, w.runes[1:]):
                out["within-word"][1] += 1
                out["within-word"][0] += a == b
            prev_last = w.runes[-1]
    return {k: (v[0], v[1]) for k, v in out.items()}


def fibonacci_prime_square(size: int = 16) -> list[int]:
    """|3301 − p(F+1)| for the first `size` distinct Fibonacci numbers F = 0,1,2,3,5,8,…

    Read as a spiral out from the centre, this reproduces all 16 cells of the 4×4 square on
    scan 32 (LP2 p15, segment 10). The sign flips once the prime exceeds 3301 (bottom row).
    """
    distinct: list[int] = []
    a, b = 0, 1
    while len(distinct) < size:
        if a not in distinct:
            distinct.append(a)
        a, b = b, a + b
    prime_list = list(islice(primes(), distinct[-1] + 1))   # prime_list[F] is the (F+1)-th prime
    return [abs(3301 - prime_list[f]) for f in distinct]


def repeat_probability(streams: Iterable[Sequence[int]]) -> float:
    """Σ f_r²: the chance two independent positions hold the same rune, given the streams' own frequencies."""
    counts: Counter[int] = Counter()
    for s in streams:
        counts.update(s)
    n = sum(counts.values())
    if n == 0:
        raise ValueError("repeat_probability: no runes")
    return sum((v / n) ** 2 for v in counts.values())


def lag_scan(streams: Sequence[Sequence[int]], lags: Iterable[int]) -> list[tuple[int, int, int]]:
    """[(lag, repeats, pairs compared)] for each lag, summed over independent streams (C9)."""
    out = []
    for m in lags:
        if m < 1:
            raise ValueError("lag must be >= 1")
        hits = sum(sum(map(eq, s, s[m:])) for s in streams)
        out.append((m, hits, sum(max(0, len(s) - m) for s in streams)))
    return out


# --- C10/C11: what the key's own statistics must be (TODO stage J) -------------------------------

def running_key_distribution(q: Sequence[float], mapping: Sequence[int], mode: str, lam: float = 1.0,
                             shift: int = 0) -> list[float]:
    """Distribution of the cipher rune when p ~ q and the key value is σ(k) + shift, k ~ λ·q + (1 − λ)·uniform.

    `mode` names the decryption, as in `ciphers.apply_stream`: "sub" (c = p + k), "add" (c = p − k),
    "beaufort" (c = k − p). σ = `mapping`, a table from key letter to key value.
    """
    if mode not in ("sub", "add", "beaufort") or not 0.0 <= lam <= 1.0 or len(q) != N or len(mapping) != N:
        raise ValueError("running_key_distribution: bad arguments")
    key = [0.0] * N
    for letter in range(N):
        key[(mapping[letter] + shift) % N] += lam * q[letter] + (1 - lam) / N
    out = [0.0] * N
    for p in range(N):
        for k in range(N):
            c = {"sub": p + k, "add": p - k, "beaufort": k - p}[mode] % N
            out[c] += q[p] * key[k]
    return out


def unigram_llr(counts: Sequence[int], model: Sequence[float]) -> float:
    """Σ_c O_c · log(29·r_c): log-likelihood of the model against a flat distribution, in nats."""
    if len(counts) != N or len(model) != N or min(model) <= 0.0:
        raise ValueError("unigram_llr needs 29 counts and a strictly positive model")
    return sum(o * math.log(N * r) for o, r in zip(counts, model))


def lag_combination_chi2(streams: Sequence[Sequence[int]], lag: int, sign: int) -> tuple[float, int]:
    """(Pearson χ², pairs) of (s[i+lag] + sign·s[i]) mod 29 within each stream (C11).

    The expectation is built from the streams' own rune frequencies f: P(x) = Σ_a f_a · f_{x − sign·a}.
    Under a ciphertext autokey c_i = p_i − sign·c_{i−lag} this combination is the plaintext itself.
    """
    if lag < 1 or sign not in (1, -1):
        raise ValueError("lag_combination_chi2: bad arguments")
    freq = Counter()
    for s in streams:
        freq.update(s)
    total_runes = sum(freq.values())
    f = [freq[r] / total_runes for r in range(N)]
    expected = [sum(f[a] * f[(x - sign * a) % N] for a in range(N)) for x in range(N)]
    observed = [0] * N
    for s in streams:
        for a, b in zip(s, s[lag:]):
            observed[(b + sign * a) % N] += 1
    pairs = sum(observed)
    if pairs == 0:
        raise ValueError("lag_combination_chi2: no pairs at this lag")
    chi2 = sum((o - pairs * e) ** 2 / (pairs * e) for o, e in zip(observed, expected))
    return chi2, pairs
