"""Statistics of rune streams — the key-independent facts about the unsolved text.

Every function is deterministic and parameter-free beyond its inputs; nothing here searches.
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Iterable, Sequence
from itertools import combinations_with_replacement, islice
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

def cipher_distribution(q: Sequence[float], key: Sequence[float], mode: str, shift: int = 0) -> list[float]:
    """Distribution of the cipher rune when p ~ q and the key value ~ `key` + shift, independently.

    `mode` names the decryption, as in `ciphers.apply_stream`: "sub" (c = p + k), "add" (c = p − k),
    "beaufort" (c = k − p).
    """
    if mode not in ("sub", "add", "beaufort") or len(q) != N or len(key) != N:
        raise ValueError("cipher_distribution: bad arguments")
    out = [0.0] * N
    for p in range(N):
        for k in range(N):
            c = {"sub": p + k + shift, "add": p - k - shift, "beaufort": k + shift - p}[mode] % N
            out[c] += q[p] * key[k]
    return out


def values_distribution(weights: Sequence[float]) -> list[float]:
    """Reduce a distribution over key values 0, 1, 2, … (any count) to a distribution mod 29."""
    total = sum(weights)
    if total <= 0 or min(weights) < 0:
        raise ValueError("values_distribution needs non-negative weights with a positive sum")
    out = [0.0] * N
    for v, w in enumerate(weights):
        out[v % N] += w / total
    return out


def running_key_distribution(q: Sequence[float], mapping: Sequence[int], mode: str, lam: float = 1.0,
                             shift: int = 0) -> list[float]:
    """`cipher_distribution` for a key letter k ~ λ·q + (1 − λ)·uniform whose value is σ(k) + shift, σ = `mapping`."""
    if not 0.0 <= lam <= 1.0 or len(q) != N or len(mapping) != N:
        raise ValueError("running_key_distribution: bad arguments")
    key = [0.0] * N
    for letter in range(N):
        key[mapping[letter] % N] += lam * q[letter] + (1 - lam) / N
    return cipher_distribution(q, key, mode, shift)


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


def chi2_sf_wilson_hilferty(x: float, df: int) -> float:
    """P(χ²_df ≥ x) by the Wilson–Hilferty cube-root normal approximation (good for df in the hundreds)."""
    if df <= 0:
        raise ValueError("df must be positive")
    z = ((x / df) ** (1 / 3) - (1 - 2 / (9 * df))) / math.sqrt(2 / (9 * df))
    return 0.5 * math.erfc(z / math.sqrt(2))


def homophonic_min_chi2(q: Sequence[float], n: int) -> tuple[float, tuple[int, ...]]:
    """(least χ² of the expected rune counts against flat, homophones per letter) over every homophonic substitution.

    Each plaintext letter with q > 0 gets its own set of ≥ 1 cipher runes, used evenly (optimal by convexity).
    The 29 − k spare runes, k = letters used, are handed out in every possible way, including leaving runes
    unused (each costs n/29). Exhaustive over all C(29, spare) multisets: no search, no fitting.
    The result is the noncentrality: n runes from the best substitution would show about this χ² plus 28 (the df).
    """
    if len(q) != N or min(q) < 0 or abs(sum(q) - 1) > 1e-9:
        raise ValueError("homophonic_min_chi2 needs a 29-letter distribution")
    used = [x for x in range(N) if q[x] > 0]
    spare = N - len(used)
    e = n / N
    best: tuple[float, tuple[int, ...]] = (math.inf, ())
    for extra in combinations_with_replacement(range(len(used) + 1), spare):   # index len(used) = unused rune
        homophones = [1 + extra.count(i) for i in range(len(used))]
        chi2 = extra.count(len(used)) * e
        chi2 += sum(h * (n * q[x] / h - e) ** 2 / e for x, h in zip(used, homophones))
        alloc = tuple(homophones[used.index(x)] if x in used else 0 for x in range(N))
        if chi2 < best[0]:
            best = (chi2, alloc)
    return best


def transition_chi2(streams: Sequence[Sequence[int]], lag: int) -> tuple[float, int]:
    """(Pearson χ², df) that the rune at i is independent of the rune at i − lag, diagonal cells excluded (C12).

    Under c_i = σ_{c_{i−lag}}(p_i) every row is a permuted plaintext distribution, so χ² is far above df.
    E_xy = R_x · f_y / (1 − f_x): row x's off-diagonal total spread by the pooled frequencies f.
    """
    if lag < 1:
        raise ValueError("lag must be >= 1")
    freq: Counter[int] = Counter()
    for s in streams:
        freq.update(s)
    n = sum(freq.values())
    f = [freq[r] / n for r in range(N)]
    table = [[0] * N for _ in range(N)]
    for s in streams:
        for a, b in zip(s, s[lag:]):
            table[a][b] += 1
    chi2 = 0.0
    for x in range(N):
        row = sum(table[x]) - table[x][x]
        if row == 0:
            raise ValueError(f"transition_chi2: empty row {x} at lag {lag}")
        for y in range(N):
            if y != x:
                e = row * f[y] / (1 - f[x])
                chi2 += (table[x][y] - e) ** 2 / e
    return chi2, N * (N - 2)
