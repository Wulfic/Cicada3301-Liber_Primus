"""The doublet "leak": what separates the 86 surviving doublets in the unsolved text (TODO stage H).

About 447 adjacent repeats are expected in the 12,947 adjacent pairs of the unsolved segments; 86 occur.
Every function here is a deterministic count or an exact tail probability. Nothing searches or fits.
Pairs never cross a segment boundary, as in `stats.lag_repeats`.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from .corpus import Corpus
from .gematria import N, RUNE_INDEX
from .stats import UNSOLVED_SEGMENTS


@dataclass(frozen=True)
class Pair:
    segment: int
    seg_pos: int        # index of the pair's first rune within its segment
    stream_pos: int     # index of the pair's first rune along the concatenated segments
    a: int
    b: int
    line_break: bool    # a `/` (written line end) falls between the two runes
    page_break: bool    # a `%` (page end) falls between the two runes

    @property
    def is_doublet(self) -> bool:
        return self.a == self.b


def rune_layout(corpus: Corpus) -> list[tuple[int, int]]:
    """(scan, line) of every rune, indexed by global rune offset (the order of `Corpus.all_runes()`)."""
    layout: list[tuple[int, int]] = []
    line = 0
    for page in corpus.pages:
        for ch in page.raw:
            if ch == "/":
                line += 1
            elif ch in RUNE_INDEX:
                layout.append((page.scan, line))
    return layout


def adjacent_pairs(corpus: Corpus, segments: Sequence[int] = UNSOLVED_SEGMENTS) -> list[Pair]:
    layout = rune_layout(corpus)
    pairs: list[Pair] = []
    stream_pos = 0
    for seg in segments:
        words = corpus.rune_words(seg)
        if not words:
            continue
        start = words[0].rune_offset
        runes = [r for w in words for r in w.runes]
        for i in range(len(runes) - 1):
            (scan_a, line_a), (scan_b, line_b) = layout[start + i], layout[start + i + 1]
            pairs.append(Pair(seg, i, stream_pos + i, runes[i], runes[i + 1],
                              line_a != line_b, scan_a != scan_b))
        stream_pos += len(runes)
    return pairs


# --- exact tail probabilities (stdlib only) ------------------------------------------------------

def _binom_log_pmf(j: int, n: int, p: float) -> float:
    """log P(X = j), in log space: math.comb(n, j) overflows a float for n in the thousands."""
    return (math.lgamma(n + 1) - math.lgamma(j + 1) - math.lgamma(n - j + 1)
            + j * math.log(p) + (n - j) * math.log1p(-p))


def _binom_sum(js: range, n: int, p: float) -> float:
    """Σ P(X = j) over `js`, stopping once the terms are past the mode and negligible."""
    if not 0.0 <= p <= 1.0:
        raise ValueError(f"binomial p must be in [0, 1], got {p}")
    if p in (0.0, 1.0):                       # all mass sits on j = n·p
        return 1.0 if int(n * p) in js else 0.0
    total = 0.0
    for j in js:
        term = math.exp(_binom_log_pmf(j, n, p))
        total += term
        past_mode = j > n * p if js.step > 0 else j < n * p
        if past_mode and term < total * 1e-17:
            break
    return min(1.0, total)


def binom_sf(k: int, n: int, p: float) -> float:
    """P(X ≥ k) for X ~ Binomial(n, p)."""
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    return _binom_sum(range(k, n + 1), n, p)


def binom_cdf(k: int, n: int, p: float) -> float:
    """P(X ≤ k) for X ~ Binomial(n, p)."""
    if k >= n:
        return 1.0
    if k < 0:
        return 0.0
    return _binom_sum(range(k, -1, -1), n, p)


def poisson_sf(k: int, lam: float) -> float:
    """P(X ≥ k) for X ~ Poisson(lam), summed upward from k to avoid cancellation."""
    if k <= 0:
        return 1.0
    term = math.exp(-lam + k * math.log(lam) - math.lgamma(k + 1))
    total, j = 0.0, k
    while term > 1e-300 and (j < k + 10 or term > total * 1e-17):
        total += term
        j += 1
        term *= lam / j
    return min(1.0, total)


def poisson_cdf(k: int, lam: float) -> float:
    """P(X ≤ k) for X ~ Poisson(lam), summed downward from k so a tiny lower tail is not lost to 1 − sf."""
    if k < 0:
        return 0.0
    if lam == 0.0:
        return 1.0
    term = math.exp(-lam + k * math.log(lam) - math.lgamma(k + 1))
    total = 0.0
    for j in range(k, -1, -1):
        total += term
        term *= j / lam
        if j < lam and term < total * 1e-17:
            break
    return min(1.0, total)


def chi2_sf_even_df(x: float, df: int) -> float:
    """P(χ²_df ≥ x) in closed form; df must be even."""
    if df <= 0 or df % 2:
        raise ValueError(f"chi2_sf_even_df needs a positive even df, got {df}")
    half = x / 2
    term, total = 1.0, 1.0
    for j in range(1, df // 2):
        term *= half / j
        total += term
    return min(1.0, math.exp(-half) * total)


# --- L1: where did the suppressed doublets go? ---------------------------------------------------

def delta_counts(pairs: Sequence[Pair]) -> list[int]:
    """Count of Δc = b − a (mod 29) for d = 0..28."""
    counts = [0] * N
    for p in pairs:
        counts[(p.b - p.a) % N] += 1
    return counts


def delta_z_scores(pairs: Sequence[Pair]) -> list[float]:
    """z of each bin d = 1..28 (index 0 is 0.0) against the missing doublets spread evenly over them."""
    counts = delta_counts(pairs)
    expected = (len(pairs) - counts[0]) / (N - 1)
    return [0.0] + [(counts[d] - expected) / math.sqrt(expected) for d in range(1, N)]


# --- L2: line and page breaks --------------------------------------------------------------------

def doublets_by_break(pairs: Sequence[Pair]) -> dict[str, tuple[int, int]]:
    """{"within-line" | "line-break" | "page-break": (doublets, pairs)}. Page breaks are also line breaks."""
    out = {"within-line": [0, 0], "line-break": [0, 0], "page-break": [0, 0]}
    for p in pairs:
        keys = ["line-break"] if p.line_break else ["within-line"]
        if p.page_break:
            keys.append("page-break")
        for k in keys:
            out[k][0] += p.is_doublet
            out[k][1] += 1
    return {k: (v[0], v[1]) for k, v in out.items()}


# --- L3: periodicity of survivor positions -------------------------------------------------------

def phase_test(pairs: Sequence[Pair], m: int, along_stream: bool) -> tuple[int, float]:
    """(largest survivor count in one phase mod m, union-bound p that a phase holds that many by chance).

    Each phase's null probability is its share of all pairs, so uneven phase sizes are accounted for.
    """
    if m < 2:
        raise ValueError("period must be >= 2")
    share = [0] * m
    hits = [0] * m
    for p in pairs:
        r = (p.stream_pos if along_stream else p.seg_pos) % m
        share[r] += 1
        hits[r] += p.is_doublet
    n = sum(hits)
    top = max(hits)
    p_union = sum(binom_sf(top, n, s / len(pairs)) for s in share)
    return top, min(1.0, p_union)


# --- L4: homogeneity and clustering --------------------------------------------------------------

def section_chi2(pairs: Sequence[Pair]) -> tuple[float, int, float]:
    """(χ², df, p) of survivor counts across the segments present in `pairs`, null = one common rate."""
    by_seg: dict[int, list[int]] = {}
    for p in pairs:
        by_seg.setdefault(p.segment, [0, 0])
        by_seg[p.segment][0] += p.is_doublet
        by_seg[p.segment][1] += 1
    rate = sum(v[0] for v in by_seg.values()) / len(pairs)
    chi2 = 0.0
    for hits, n in by_seg.values():
        e = rate * n
        chi2 += (hits - e) ** 2 / e + ((n - hits) - (n - e)) ** 2 / (n - e)
    df = len(by_seg) - 1
    return chi2, df, chi2_sf_even_df(chi2, df)


def dispersion_index(pairs: Sequence[Pair], window: int) -> float:
    """Variance / mean of survivor counts in consecutive full windows of `window` pairs along the stream."""
    counts = [sum(p.is_doublet for p in pairs[i:i + window]) for i in range(0, len(pairs) - window + 1, window)]
    if len(counts) < 2:
        raise ValueError("need at least two full windows")
    mean = sum(counts) / len(counts)
    var = sum((c - mean) ** 2 for c in counts) / (len(counts) - 1)
    return var / mean


# --- C3: do the survivors mark one plaintext letter? (TODO stage Q) ------------------------------
#
# Under c_i = c_{i−1} + (p_i − x)·k_i with k_i ≠ 0 (mod 29), c_i = c_{i−1} exactly where p_i = x. The doublets would
# then sit where the letter x sits in words, and their number would be x's share of the plaintext.

WORD_CLASSES = ("initial", "medial", "final", "sole")


def word_class(index: int, length: int) -> str:
    """Position class of rune `index` in a word of `length` runes."""
    if not 0 <= index < length:
        raise ValueError(f"word_class: index {index} outside a word of {length}")
    if length == 1:
        return "sole"
    if index == 0:
        return "initial"
    return "final" if index == length - 1 else "medial"


def word_stream_doublet_classes(words: Sequence[Sequence[int]]) -> list[str]:
    """Word class of the second rune of every doublet in one continuous stream of words."""
    cells = [(r, word_class(i, len(w))) for w in words for i, r in enumerate(w)]
    return [cls for (a, _), (b, cls) in zip(cells, cells[1:]) if a == b]


def doublet_classes(corpus: Corpus, segments: Sequence[int] = UNSOLVED_SEGMENTS) -> list[str]:
    """`word_stream_doublet_classes` over each segment. Pairs never cross a segment boundary."""
    return [cls for seg in segments
            for cls in word_stream_doublet_classes([w.runes for w in corpus.rune_words(seg)])]


def letter_class_counts(words: Sequence[Sequence[int]]) -> dict[str, list[int]]:
    """{class: count of each letter 0..28 at that word position} over plaintext words."""
    out = {cls: [0] * N for cls in WORD_CLASSES}
    for w in words:
        for i, r in enumerate(w):
            out[word_class(i, len(w))][r] += 1
    return out


def marker_letter_llr(classes: Sequence[str], words: Sequence[Sequence[int]], letter: int,
                      pseudo: float = 10.0) -> float:
    """LLR (nats) that doublets sit where `letter` sits in plaintext words, against doublets at random runes.

    Σ_doublets log[P̂(x | class) / f_x], with P̂(x | class) = (n_x,class + pseudo·f_x) / (n_class + pseudo): the
    Bayes form of P(class | x) / P(class), shrunk toward the base rate f_x when a class is thin.
    """
    counts = letter_class_counts(words)
    total = sum(sum(row) for row in counts.values())
    f = sum(row[letter] for row in counts.values()) / total
    if f == 0.0:
        raise ValueError(f"letter {letter} never occurs in the plaintext; its model predicts no doublets")
    return sum(math.log((counts[c][letter] + pseudo * f) / (sum(counts[c]) + pseudo) / f) for c in classes)


# --- L5: the community key-switch scheme (reference/community/images/Algorithm.png) ------------------

def key_switch_ideal(plain: Sequence[int], k1: Sequence[int], k2: Sequence[int]) -> list[int]:
    """When key 1 would repeat the last emitted rune, encrypt this rune with key 2 instead (kept even if it repeats)."""
    out: list[int] = []
    for i, p in enumerate(plain):
        c = (p + k1[i]) % N
        if out and c == out[-1]:
            c = (p + k2[i]) % N
        out.append(c)
    return out


def key_switch_literal(plain: Sequence[int], k1: Sequence[int], k2: Sequence[int]) -> list[int | None]:
    """The picture's code as written: it compares key-1 values of runes i and i+1 and re-keys rune i.

    If key 2 would also give equal values, the code `continue`s and leaves rune i unset (None here).
    The picture's 1-based indices only shift every output by a constant, which no doublet count sees.
    The last rune has no look-ahead and takes key 1.
    """
    n = len(plain)
    out: list[int | None] = [None] * n
    for i in range(n):
        if i + 1 < n and (plain[i + 1] + k1[i + 1]) % N == (plain[i] + k1[i]) % N:
            if (plain[i + 1] + k2[i + 1]) % N == (plain[i] + k2[i]) % N:
                continue
            out[i] = (plain[i] + k2[i]) % N
        else:
            out[i] = (plain[i] + k1[i]) % N
    return out


def doublet_rate(stream: Sequence[int | None]) -> tuple[int, int]:
    """(doublets, pairs) of a simulated stream; pairs touching an unset rune are not counted."""
    hits = total = 0
    for a, b in zip(stream, stream[1:]):
        if a is None or b is None:
            continue
        total += 1
        hits += a == b
    return hits, total


# --- C14: is the re-keying "skip to the next key value"? (TODO stage O) --------------------------

def skip_next_llr(pairs: Sequence[Pair], plain_diffs: Sequence[float], repeat: float = 0.19) -> float:
    """LLR (nats) of "Δc bins 1–28 carry English differences at rate `repeat`" against flat bins.

    Under a skip-next rule the 19 % leak forces the key to repeat adjacent values ≈ 19 % of the time (C8), and then
    Δc = Δp at those positions: P1(e) ∝ repeat·P(Δp = e) + (1 − repeat)/28·(1 − P(Δp = e)), e = 1..28.
    """
    if len(plain_diffs) != N or not 0.0 < repeat < 1.0:
        raise ValueError("skip_next_llr: bad arguments")
    model = [repeat * plain_diffs[e] + (1 - repeat) / (N - 1) * (1 - plain_diffs[e]) for e in range(1, N)]
    total = sum(model)
    model = [m / total for m in model]
    counts = delta_counts(pairs)[1:]
    return sum(o * math.log(m * (N - 1)) for o, m in zip(counts, model))
