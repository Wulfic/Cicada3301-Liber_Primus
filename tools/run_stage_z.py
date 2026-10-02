"""Stage Z: deterministic local encryption, word and block codebooks (TODO.md, declared 2026-10-01 in be4a200 / 3015705
before this script existed).

A cipher whose output for a local plaintext unit depends only on that unit maps equal units to equal cipher units, so
it keeps the plaintext's repeat count K (pairs of equal units) whatever its table is. Two families:

- Zw: cipher word = T(plaintext word). Cells "Zw-sec" (pairs within each section) and "Zw-all" (pairs across LP2).
  Words of 1 rune are left out.
- Zb: aligned n-rune blocks through a fixed bijection of Z29^n (Hill, polygraphic codebooks), n = 2…8, offset a.
  Mode "sec" aligns at each section start and counts pairs within sections; mode "cont" reads segments 7–15 as one
  stream and counts pairs over all of it.

Each cipher is followed by the measured anti-doublet rule: a would-be doublet in a section's continuous stream is
re-drawn uniformly with probability 0.81.

Declared rule, per cell:
- lower = exp(m − 5s) − 1, with m, s the mean and sd of ln(K + 1) over a source's positive draws (amended from
  μ − 5σ after --quick showed right skew, before LP2 was scored).
- Testable iff, for both control sources, lower > the null's maximum and every positive draw > the null's maximum.
- Excluded iff testable and K_LP2 < lower for both sources.
- PASS iff K_LP2 > null max and (K_LP2 − μ0)/σ0 ≥ 6, with σ0 floored at 1.
- Otherwise inconclusive.
The run is valid iff every Zb cell with n ≤ 4 has a null mean within 3 s.e. of the analytic E[K].

Deterministic. Usage: python -m tools.run_stage_z [--quick]   (--quick scores no LP2 runes and writes nothing)
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from collections import Counter, deque
from collections.abc import Sequence
from math import comb

import numpy as np

from tools.lpcore import keys, stats
from tools.lpcore.corpus import REPO_ROOT, Corpus, load_corpus
from tools.lpcore.gematria import N, spellings_of
from tools.lpcore.verify import load_translation
from tools.run_stage_x import write_tsv

log = logging.getLogger("stage_z")

RESULTS_PATH = REPO_ROOT / "reference" / "findings" / "stage_z_results.tsv"
CONTROLS_PATH = REPO_ROOT / "reference" / "findings" / "stage_z_controls.tsv"
EMERSON = REPO_ROOT / "data" / "corpora" / "emerson_essays.txt"
KEEP = 0.19
BLOCK_LENGTHS = range(2, 9)
MODES = ("sec", "cont")
NULL_DRAWS = 1_000
POSITIVE_DRAWS = 200
SOURCES = ("E", "L")
SEED = 3301
PASS_Z = 6.0
POSITIVE_SIGMAS = 5.0
VALIDITY_SE = 3.0
VALIDITY_MAX_N = 4
MIN_WORD = 2

Sections = list[list[tuple[int, ...]]]           # per section, its words as rune tuples


def cells() -> list[tuple]:
    """The 72 declared cells: ("Zw", scope) and ("Zb", n, mode, a)."""
    out: list[tuple] = [("Zw", "sec"), ("Zw", "all")]
    out += [("Zb", n, mode, a) for n in BLOCK_LENGTHS for mode in MODES for a in range(n)]
    if len(out) != 72:
        raise AssertionError(f"declared 72 cells, built {len(out)}")
    return out


def cell_name(cell: tuple) -> str:
    return "-".join(str(x) for x in cell)


def lp2_sections(corpus: Corpus) -> Sections:
    return [[w.runes for w in corpus.rune_words(s)] for s in stats.UNSOLVED_SEGMENTS]


def anti_doublet(stream: np.ndarray, rng: np.random.Generator, keep: float = KEEP) -> np.ndarray:
    """A would-be doublet c_i = c_{i−1} is re-drawn uniformly with probability 1 − keep, left to right.

    Equivalent to a sequential pass: only doublet positions are visited, and a re-draw that creates a doublet with the
    next rune queues that position.
    """
    c = stream.copy()
    todo = deque((np.flatnonzero(c[1:] == c[:-1]) + 1).tolist())
    while todo:
        i = todo.popleft()
        if c[i] != c[i - 1]:
            continue
        if rng.random() >= keep:
            c[i] = rng.integers(N)
        if i + 1 < len(c) and c[i + 1] == c[i] and (not todo or todo[0] != i + 1):
            todo.appendleft(i + 1)
    return c


def split(stream: np.ndarray, lengths: Sequence[int]) -> list[tuple[int, ...]]:
    out, pos = [], 0
    for n in lengths:
        out.append(tuple(int(x) for x in stream[pos:pos + n]))
        pos += n
    return out


def pairs(counts) -> int:
    return int(sum(v * (v - 1) // 2 for v in counts))


def block_codes(stream: np.ndarray, n: int, a: int) -> np.ndarray:
    """Base-29 codes of the aligned blocks stream[a + n·t : a + n·t + n]."""
    t = (len(stream) - a) // n
    if t <= 0:
        return np.zeros(0, dtype=np.int64)
    blocks = stream[a:a + n * t].reshape(t, n).astype(np.int64)
    return blocks @ (N ** np.arange(n - 1, -1, -1, dtype=np.int64))


def block_K(streams: Sequence[np.ndarray], n: int, mode: str, a: int) -> int:
    if mode == "sec":
        return sum(pairs(np.unique(block_codes(s, n, a), return_counts=True)[1]) for s in streams)
    return pairs(np.unique(block_codes(np.concatenate(streams), n, a), return_counts=True)[1])


def word_K(sections: Sections, scope: str) -> int:
    if scope == "sec":
        return sum(pairs(Counter(w for w in sec if len(w) >= MIN_WORD).values()) for sec in sections)
    return pairs(Counter(w for sec in sections for w in sec if len(w) >= MIN_WORD).values())


def statistic(cell: tuple, sections: Sections) -> int:
    if cell[0] == "Zw":
        return word_K(sections, cell[1])
    _, n, mode, a = cell
    return block_K([np.array([r for w in sec for r in w], dtype=np.int64) for sec in sections], n, mode, a)


def doublet_probability(keep: float = KEEP) -> float:
    """P(c_i = c_{i−1}) under uniform runes and the re-draw rule (a re-draw can repeat the value)."""
    return (keep + (1 - keep) / N) / N


def p_equal(length: int, keep: float = KEEP) -> float:
    """P(two independent windows of `length` runes are equal): the chain is Markov with a uniform stationary law."""
    s = doublet_probability(keep)
    return (s * s + (1 - s) ** 2 / (N - 1)) ** (length - 1) / N


def analytic_mean(cell: tuple, sections: Sections) -> float:
    """E[K] under the null, ignoring the O(1/29) correlation between adjacent blocks."""
    if cell[0] == "Zw":
        groups = sections if cell[1] == "sec" else [[w for sec in sections for w in sec]]
        total = 0.0
        for group in groups:
            for length, count in Counter(len(w) for w in group if len(w) >= MIN_WORD).items():
                total += comb(count, 2) * p_equal(length)
        return total
    _, n, mode, a = cell
    lengths = [sum(map(len, sec)) for sec in sections]
    groups = lengths if mode == "sec" else [sum(lengths)]
    return sum(comb(max(0, (m - a) // n), 2) for m in groups) * p_equal(n)


def null_sections(shape: Sections, rng: np.random.Generator) -> Sections:
    out = []
    for sec in shape:
        stream = anti_doublet(rng.integers(0, N, sum(map(len, sec))), rng)
        out.append(split(stream, [len(w) for w in sec]))
    return out


# ---- positive controls -------------------------------------------------------------------------------------------

def emerson_words() -> list[tuple[int, ...]]:
    """Emerson's essays as rune words, each word in its first `spellings_of` spelling (words with none dropped)."""
    cache: dict[str, tuple[int, ...] | None] = {}
    out = []
    for word in re.findall(r"[A-Z]+", EMERSON.read_text(encoding="utf-8").upper()):
        if word not in cache:
            spellings = spellings_of(word)
            cache[word] = spellings[0] if spellings else None
        if cache[word]:
            out.append(cache[word])
    if len(out) < 50_000:
        raise ValueError(f"Emerson gave only {len(out)} rune words")
    return out


def fill_sections(source: Sequence[tuple[int, ...]], sizes: Sequence[int], rng: np.random.Generator,
                  contiguous: bool) -> Sections:
    """Plaintext words cut to the section rune counts: a contiguous window from a random start, or shuffled passes."""
    if contiguous:
        start = int(rng.integers(len(source)))
        stream = (source[(start + i) % len(source)] for i in range(10 ** 9))
    else:
        def shuffled():
            while True:
                for i in rng.permutation(len(source)):
                    yield source[i]
        stream = shuffled()
    out = []
    for size in sizes:
        sec, total = [], 0
        while total < size:
            w = next(stream)[:size - total]
            sec.append(tuple(w))
            total += len(w)
        out.append(sec)
    return out


def injective_table(units: Sequence[tuple[int, ...]], rng: np.random.Generator) -> dict[tuple[int, ...], tuple[int, ...]]:
    """A fresh random injective map from each distinct unit to a rune string of the same length."""
    table: dict[tuple[int, ...], tuple[int, ...]] = {}
    used: set[tuple[int, ...]] = set()
    distinct = sorted(set(units))
    for length, count in Counter(map(len, distinct)).items():
        if count > N ** length:
            raise ValueError(f"{count} distinct units of length {length}: no injective table exists")
    for u in distinct:
        while True:
            v = tuple(int(x) for x in rng.integers(0, N, len(u)))
            if v not in used:
                break
        table[u] = v
        used.add(v)
    return table


def encipher(cell: tuple, plain: Sections, rng: np.random.Generator, keep: float = KEEP) -> Sections:
    """The plaintext through a random table at the cell's unit and alignment, then the anti-doublet rule."""
    lengths = [[len(w) for w in sec] for sec in plain]
    streams = [np.array([r for w in sec for r in w], dtype=np.int64) for sec in plain]
    if cell[0] == "Zw":
        table = injective_table([w for sec in plain for w in sec], rng)
        streams = [np.array([r for w in sec for r in table[w]], dtype=np.int64) for sec in plain]
    else:
        _, n, mode, a = cell
        groups = streams if mode == "sec" else [np.concatenate(streams)]
        blocked = []
        for g in groups:
            t = (len(g) - a) // n
            body = [tuple(int(x) for x in g[a + n * j:a + n * j + n]) for j in range(max(t, 0))]
            table = injective_table(body, rng)
            out = rng.integers(0, N, len(g))            # runes outside whole blocks: any table, here random
            for j, u in enumerate(body):
                out[a + n * j:a + n * j + n] = table[u]
            blocked.append(out)
        if mode == "cont":
            cuts = np.cumsum([len(s) for s in streams])[:-1]
            blocked = np.split(blocked[0], cuts)
        streams = blocked
    return [split(anti_doublet(s, rng, keep), lens) for s, lens in zip(streams, lengths)]


def summarise(values: Sequence[int]) -> tuple[float, float, int]:
    arr = np.asarray(values, dtype=float)
    return float(arr.mean()), float(arr.std(ddof=1)), int(arr.max())


def log_lower(values: Sequence[int]) -> float:
    """exp(m − 5s) − 1 over ln(K + 1): the positive counts are right-skewed (amendment, before LP2 was scored)."""
    logs = np.log1p(np.asarray(values, dtype=float))
    return float(np.expm1(logs.mean() - POSITIVE_SIGMAS * logs.std(ddof=1)))


def verdict(k: int, mu0: float, sd0: float, null_max: int, lower: dict[str, float],
            minimum: dict[str, int]) -> tuple[str, float]:
    z0 = (k - mu0) / max(sd0, 1.0)
    testable = all(lo > null_max for lo in lower.values()) and all(m > null_max for m in minimum.values())
    if k > null_max and z0 >= PASS_Z:
        return "PASS", z0
    if testable and all(k < lo for lo in lower.values()):
        return "EXCLUDED", z0
    return ("INCONCLUSIVE" if testable else "UNTESTABLE"), z0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--quick", action="store_true",
                        help="50 nulls and 20 controls per source; LP2 is not scored and nothing is written")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    null_draws, pos_draws = (50, 20) if args.quick else (NULL_DRAWS, POSITIVE_DRAWS)

    corpus = load_corpus()
    shape = lp2_sections(corpus)
    sizes = [sum(map(len, sec)) for sec in shape]
    log.info("LP2 shape: %d sections, %d runes, %d words", len(shape), sum(sizes), sum(map(len, shape)))
    sources = {"E": (emerson_words(), True),
               "L": (keys.solved_plaintext_words(corpus, load_translation()), False)}
    all_cells = cells()

    rng = np.random.default_rng(SEED)
    null_values: dict[tuple, list[int]] = {c: [] for c in all_cells}
    for _ in range(null_draws):
        sample = null_sections(shape, rng)
        for c in all_cells:
            null_values[c].append(statistic(c, sample))
    log.info("nulls done (%d draws)", null_draws)

    control_rows, results, valid, testable = [], [], True, []
    for c in all_cells:
        mu0, sd0, null_max = summarise(null_values[c])
        expected = analytic_mean(c, shape)
        se = sd0 / np.sqrt(null_draws)
        checked = c[0] == "Zb" and c[1] <= VALIDITY_MAX_N
        ok = abs(mu0 - expected) <= VALIDITY_SE * se if checked else True
        valid &= ok
        lower, minimum = {}, {}
        for name in SOURCES:
            words, contiguous = sources[name]
            crng = np.random.default_rng([SEED, all_cells.index(c), SOURCES.index(name)])
            ks = [statistic(c, encipher(c, fill_sections(words, sizes, crng, contiguous), crng))
                  for _ in range(pos_draws)]
            mu, sd, _ = summarise(ks)
            lower[name], minimum[name] = log_lower(ks), min(ks)
            control_rows.append((cell_name(c), name, pos_draws, f"{mu:.2f}", f"{sd:.2f}", min(ks), max(ks),
                                 f"{lower[name]:.2f}"))
        if all(lo > null_max for lo in lower.values()) and all(m > null_max for m in minimum.values()):
            testable.append(cell_name(c))
        log.info("%-12s null %.2f ± %.2f (max %d, analytic %.2f%s) | E low %.1f | L low %.1f", cell_name(c), mu0, sd0,
                 null_max, expected, "" if ok else " MISMATCH", lower["E"], lower["L"])
        if args.quick:
            continue
        k = statistic(c, lp2_sections(corpus))
        v, z0 = verdict(k, mu0, sd0, null_max, lower, minimum)
        results.append((cell_name(c), k, f"{mu0:.3f}", f"{sd0:.3f}", null_max, f"{expected:.3f}",
                        "ok" if ok else ("MISMATCH" if checked else "-"), f"{lower['E']:.2f}", f"{lower['L']:.2f}",
                        f"{z0:.2f}", v))

    log.info("run %s", "VALID" if valid else "VOID")
    if args.quick:
        log.info("quick run: LP2 not scored, nothing written; %d testable cells: %s", len(testable), testable)
        return 0 if valid else 2
    if not valid:
        results = [(*row[:-1], "VOID") for row in results]
    for row in results:
        log.info("%s", row)
    log.info("verdicts: %s", dict(Counter(row[-1] for row in results)))
    write_tsv(RESULTS_PATH, ("cell", "K_LP2", "null_mean", "null_sd", "null_max", "analytic_mean", "validity",
                             "E_lower", "L_lower", "z_null", "verdict"), results)
    write_tsv(CONTROLS_PATH, ("cell", "source", "draws", "mean", "sd", "min", "max", "log_lower_5sd"), control_rows)
    log.info("wrote %s and %s", RESULTS_PATH.name, CONTROLS_PATH.name)
    return 0 if valid else 2


if __name__ == "__main__":
    sys.exit(main())
