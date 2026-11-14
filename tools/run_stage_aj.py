"""Stage AJ: anatomy of the 86 surviving doublets (TODO.md, declared 2026-11-14 in 45bc943 before this script existed).

Null (M1/M2): the 86 survivors are a uniform sample, without replacement, of the 12,947 adjacent pairs in segments
7-15. Seventeen statistics of the survivors (identity, the M3 concentration, the two-spelling runes, word, line,
page and clause position, neighbours) are scored against 10^6 seeded null draws. A test fires at
p <= 1e-3 / 17. Controls (null draws, pure M3, planted cells) run first; if the negative or an M3 control fails,
the stage is void and LP2 is not scored.

Deterministic. Usage: python -m tools.run_stage_aj [--quick]   (--quick: controls only, 10^5 null draws, nothing written)
"""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass

import numpy as np

from tools.lpcore import leak
from tools.lpcore.corpus import REPO_ROOT, Corpus, load_corpus
from tools.lpcore.gematria import N, RUNE_INDEX
from tools.run_stage_x import write_tsv

log = logging.getLogger("stage_aj")

RESULTS_PATH = REPO_ROOT / "reference" / "findings" / "stage_aj_tests.tsv"
CONTROLS_PATH = REPO_ROOT / "reference" / "findings" / "stage_aj_controls.tsv"
SEED = 3301
N_SURVIVORS = 86
N_NULL = 1_000_000
N_NULL_QUICK = 100_000
BATCH = 50_000
N_CONTROL = 100
FAMILY_ALPHA = 1e-3
N_TESTS = 17
ALPHA = FAMILY_ALPHA / N_TESTS
TOP_K = 6                                   # M3: 86 survivors / 15.4 per rune = 5.6 runes
NAMED = tuple(RUNE_INDEX[r] for r in "ᚢᚳᛋᛝᛡ")  # U/V, C/K, S/Z, NG/ING, IA/IO
PLANT_EXCESS = 0.25
POWER_REQUIRED = 80                         # of N_CONTROL
NEGATIVE_MAX_FIRES = 1                      # over N_CONTROL x N_TESTS results
MIXTURES = (0.5, 0.25)
WORD_CLASSES = ("initial", "medial", "final", "sole")


@dataclass(frozen=True)
class Test:
    name: str
    variable: str
    cells: np.ndarray          # cell of every pair, -1 where the variable is undefined
    labels: tuple[str, ...]
    kind: str = "chi2"         # "chi2", "topk" or "named"

    @property
    def n_cells(self) -> int:
        return len(self.labels)

    @property
    def share(self) -> np.ndarray:
        valid = self.cells[self.cells >= 0]
        return np.bincount(valid, minlength=self.n_cells) / len(valid)


def contiguous_positions(ids: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Index of every element within its run of equal ids, from the start and from the end. Runs must be contiguous."""
    starts = np.flatnonzero(np.r_[True, ids[1:] != ids[:-1]])
    if len(np.unique(ids)) != len(starts):
        raise ValueError("unit ids are not contiguous in reading order")
    ends = np.r_[starts[1:], len(ids)]
    lengths = ends - starts
    run = np.repeat(np.arange(len(starts)), lengths)
    from_start = np.arange(len(ids)) - starts[run]
    return from_start, lengths[run] - 1 - from_start


def decile_cells(values: np.ndarray) -> tuple[np.ndarray, tuple[str, ...]]:
    """Cells bounded by the deciles of `values` (actual data values, ties kept in one cell); empty cells dropped."""
    edges = np.unique(np.quantile(values, np.arange(1, 10) / 10, method="lower"))
    cells = np.searchsorted(edges, values, side="left")
    bounds = [-1, *edges.tolist(), int(values.max())]
    used = np.unique(cells)
    remap = np.full(len(edges) + 1, -1)
    remap[used] = np.arange(len(used))
    labels = tuple(f"{bounds[c] + 1}-{bounds[c + 1]}" for c in used)
    return remap[cells], labels


def capped(values: np.ndarray, lo: int, cap: int) -> tuple[np.ndarray, tuple[str, ...]]:
    """Cells lo, lo+1, ..., cap-1, cap+ (values below lo are an error)."""
    if values.min() < lo:
        raise ValueError(f"value below {lo}")
    cells = np.minimum(values, cap) - lo
    return cells, tuple(str(v) for v in range(lo, cap)) + (f"{cap}+",)


def build_tests(corpus: Corpus) -> tuple[list[Test], np.ndarray]:
    """The 17 declared tests as per-pair cell arrays, and the doublet mask of the pairs."""
    pairs = leak.adjacent_pairs(corpus)
    units = corpus.rune_units()
    n_runes = len(units["rune"])

    word_len = np.zeros(n_runes, dtype=np.int64)
    word_idx = np.zeros(n_runes, dtype=np.int64)
    seg_start, seg_len = {}, {}
    for w in corpus.rune_words():
        for k in range(len(w.runes)):
            word_len[w.rune_offset + k] = len(w.runes)
            word_idx[w.rune_offset + k] = k
        seg_start.setdefault(w.segment, w.rune_offset)
        seg_len[w.segment] = seg_len.get(w.segment, 0) + len(w.runes)
    if not np.array_equal(np.array(units["rune"]), np.array(corpus.all_runes())):
        raise ValueError("rune_units and all_runes disagree on rune order")

    line = np.array(units["line"])
    page = np.array(units["page"])
    clause = np.array(units["clause"])
    col_start, col_end = contiguous_positions(line)
    cl_start, cl_end = contiguous_positions(clause)
    first_line_on_page = {}
    for ln, pg in zip(line, page):
        first_line_on_page.setdefault(int(pg), int(ln))
    line_on_page = line - np.array([first_line_on_page[int(pg)] for pg in page])

    runes = np.array(units["rune"])
    g = np.array([seg_start[p.segment] + p.seg_pos + 1 for p in pairs])     # global offset of c_{i+1}
    if not (np.array_equal(runes[g - 1], [p.a for p in pairs]) and np.array_equal(runes[g], [p.b for p in pairs])):
        raise ValueError("pair runes do not match the corpus at the computed offsets")
    has_before = np.array([p.seg_pos >= 1 for p in pairs])
    has_after = np.array([p.seg_pos + 2 < seg_len[p.segment] for p in pairs])
    before = np.where(has_before, runes[np.maximum(g - 2, 0)], -1)
    after = np.where(has_after, runes[np.minimum(g + 1, n_runes - 1)], -1)
    a = np.array([p.a for p in pairs])
    b = np.array([p.b for p in pairs])

    rune_labels = tuple(str(r) for r in range(N))
    delta_labels = tuple(str(d) for d in range(N))
    wc = np.array([WORD_CLASSES.index(leak.word_class(int(word_idx[x]), int(word_len[x]))) for x in g])
    pages_used = np.unique(page[g])
    page_cell = np.searchsorted(pages_used, page[g])

    tests = [
        Test("T1", "doubled rune c_i", a, rune_labels),
        Test("T2", f"top-{TOP_K} sum of doubled-rune counts", a, rune_labels, "topk"),
        Test("T3", "doubled rune in {U, C, S, NG, IA}", a, rune_labels, "named"),
        Test("T4", "word class of c_{i+1}", wc, WORD_CLASSES),
        Test("T5", "length of c_{i+1}'s word", *capped(word_len[g], 1, 8)),
        Test("T6", "index in word from start", *capped(word_idx[g], 0, 6)),
        Test("T7", "index in word from end", *capped(word_len[g] - 1 - word_idx[g], 0, 6)),
        Test("T8", "column in line from start", *decile_cells(col_start[g])),
        Test("T9", "column in line from end", *decile_cells(col_end[g])),
        Test("T10", "line on page from top", *decile_cells(line_on_page[g])),
        Test("T11", "index in clause from start", *decile_cells(cl_start[g])),
        Test("T12", "index in clause from end", *decile_cells(cl_end[g])),
        Test("T13", "rune before c_{i-1}", before, rune_labels),
        Test("T14", "rune after c_{i+2}", after, rune_labels),
        Test("T15", "delta in (c_i - c_{i-1}) mod 29", np.where(has_before, (a - before) % N, -1), delta_labels),
        Test("T16", "delta out (c_{i+2} - c_{i+1}) mod 29", np.where(has_after, (after - b) % N, -1), delta_labels),
        Test("T17", "page (scan) of c_{i+1}", page_cell, tuple(str(s) for s in pages_used)),
    ]
    if len(tests) != N_TESTS:
        raise ValueError(f"declared {N_TESTS} tests, built {len(tests)}")
    return tests, a == b


def statistics(tests: list[Test], draws: np.ndarray) -> np.ndarray:
    """Statistic of every test on every draw (rows of pair indices). Shape (len(draws), N_TESTS)."""
    out = np.empty((len(draws), len(tests)))
    rows = np.repeat(np.arange(len(draws)), draws.shape[1])
    for t, test in enumerate(tests):
        cells = test.cells[draws.ravel()]
        ok = cells >= 0
        counts = np.bincount(rows[ok] * test.n_cells + cells[ok],
                             minlength=len(draws) * test.n_cells).reshape(len(draws), test.n_cells)
        if test.kind == "topk":
            out[:, t] = np.sort(counts, axis=1)[:, -TOP_K:].sum(axis=1)
        elif test.kind == "named":
            out[:, t] = counts[:, list(NAMED)].sum(axis=1)
        else:
            expected = counts.sum(axis=1, keepdims=True) * test.share
            with np.errstate(divide="ignore", invalid="ignore"):
                out[:, t] = np.where(expected > 0, (counts - expected) ** 2 / expected, 0.0).sum(axis=1)
    return out


def distinct_draws(rng: np.random.Generator, pool: np.ndarray, size: int, n: int) -> np.ndarray:
    """`n` rows of `size` distinct elements of `pool`, uniformly (rejection of rows with a repeat)."""
    out: list[np.ndarray] = []
    have = 0
    while have < n:
        idx = np.sort(rng.integers(0, len(pool), (int((n - have) * 1.6) + 16, size)), axis=1)
        good = idx[(np.diff(idx, axis=1) != 0).all(axis=1)]
        out.append(pool[good])
        have += len(good)
    return np.concatenate(out)[:n]


def mixed_draws(rng: np.random.Generator, n_pairs: int, inside: np.ndarray, k_inside: int, n: int,
                outside: np.ndarray | None = None) -> np.ndarray:
    """Rows of N_SURVIVORS distinct pairs: k_inside from `inside`, the rest from `outside` (default: any pair)."""
    rows = np.empty((n, N_SURVIVORS), dtype=np.int64)
    rest_pool = np.arange(n_pairs) if outside is None else outside
    for r in range(n):
        first = rng.choice(inside, k_inside, replace=False)
        rest_candidates = np.setdiff1d(rest_pool, first, assume_unique=True)
        rows[r] = np.r_[first, rng.choice(rest_candidates, N_SURVIVORS - k_inside, replace=False)]
    return rows


class Null:
    """Sorted null statistic of every test, from `n` uniform draws of N_SURVIVORS distinct pairs."""

    def __init__(self, tests: list[Test], n_pairs: int, n: int, rng: np.random.Generator) -> None:
        pool = np.arange(n_pairs)
        parts = []
        for done in range(0, n, BATCH):
            parts.append(statistics(tests, distinct_draws(rng, pool, N_SURVIVORS, min(BATCH, n - done))))
            log.info("null draws: %d / %d", done + len(parts[-1]), n)
        self.sorted = np.sort(np.concatenate(parts), axis=0)
        self.n = n

    def p_values(self, stats: np.ndarray) -> np.ndarray:
        """Upper-tail p = (1 + #null >= observed) / (1 + n), per test, for each row of `stats`."""
        stats = np.atleast_2d(stats)
        ge = np.stack([self.n - np.searchsorted(self.sorted[:, t], stats[:, t], side="left")
                       for t in range(stats.shape[1])], axis=1)
        return (1 + ge) / (1 + self.n)


def run_controls(tests: list[Test], null: Null, rng: np.random.Generator) -> tuple[list[tuple], list[str]]:
    """Control rows (name, test, fires out of N_CONTROL, required) and the names of failed required controls."""
    n_pairs = len(tests[0].cells)
    a = tests[0].cells
    rows: list[tuple] = []
    failed: list[str] = []

    def fires(draws: np.ndarray) -> np.ndarray:
        return (null.p_values(statistics(tests, draws)) <= ALPHA).sum(axis=0)

    neg = fires(distinct_draws(rng, np.arange(n_pairs), N_SURVIVORS, N_CONTROL))
    total = int(neg.sum())
    rows += [("negative null", tests[t].name, int(neg[t]), "") for t in range(N_TESTS)]
    rows.append(("negative null", "all", total, f"<= {NEGATIVE_MAX_FIRES}"))
    if total > NEGATIVE_MAX_FIRES:
        failed.append("negative null")

    def blind_rows(phi: float, named: bool) -> np.ndarray:
        out = []
        for _ in range(N_CONTROL):
            blind = np.array(NAMED) if named else rng.choice(N, TOP_K, replace=False)
            inside = np.flatnonzero(np.isin(a, blind))
            out.append(mixed_draws(rng, n_pairs, inside, round(N_SURVIVORS * phi), 1)[0])
        return np.array(out)

    m3 = fires(blind_rows(1.0, named=False))
    rows.append(("M3 pure, random 6 runes", "T2", int(m3[1]), f">= {POWER_REQUIRED}"))
    rows.append(("M3 pure, random 6 runes", "T1", int(m3[0]), ""))
    if m3[1] < POWER_REQUIRED:
        failed.append("M3 pure")
    named = fires(blind_rows(1.0, named=True))
    rows.append(("M3 pure, named 5 runes", "T3", int(named[2]), f">= {POWER_REQUIRED}"))
    if named[2] < POWER_REQUIRED:
        failed.append("M3 named")
    for phi in MIXTURES:
        mix = fires(blind_rows(phi, named=False))
        rows += [(f"M3 mixture phi={phi}", tests[t].name, int(mix[t]), "") for t in (0, 1)]

    for t, test in enumerate(tests):
        if test.kind != "chi2":
            continue
        valid = np.flatnonzero(test.cells >= 0)
        cell0 = valid[test.cells[valid] == 0]
        others = np.setdiff1d(np.arange(n_pairs), cell0, assume_unique=True)
        k0 = round(N_SURVIVORS * (test.share[0] + PLANT_EXCESS))
        planted = fires(mixed_draws(rng, n_pairs, cell0, k0, N_CONTROL, outside=others))
        rows.append((f"planted cell 0 ({test.labels[0]}), share +{PLANT_EXCESS}", test.name, int(planted[t]),
                     f">= {POWER_REQUIRED} else untestable"))
    return rows, failed


def untestable(control_rows: list[tuple]) -> set[str]:
    return {r[1] for r in control_rows if r[0].startswith("planted") and r[2] < POWER_REQUIRED}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--quick", action="store_true", help="controls only, 10^5 null draws, nothing written")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    tests, doublet = build_tests(load_corpus())
    n_pairs = len(doublet)
    log.info("%d pairs, %d doublets; %d tests, fire at p <= %.3g", n_pairs, int(doublet.sum()), N_TESTS, ALPHA)
    if int(doublet.sum()) != N_SURVIVORS:
        log.error("expected %d doublets, found %d", N_SURVIVORS, int(doublet.sum()))
        return 1

    rng = np.random.default_rng(SEED)
    null = Null(tests, n_pairs, N_NULL_QUICK if args.quick else N_NULL, rng)
    control_rows, failed = run_controls(tests, null, rng)
    for r in control_rows:
        log.info("control %-48s %-4s fires %3d / %d  %s", r[0], r[1], r[2], N_CONTROL, r[3])
    weak = untestable(control_rows)
    log.info("untestable by the planted control: %s", sorted(weak) or "none")
    if failed:
        log.error("stage void: required control(s) failed: %s; LP2 not scored", failed)
        return 1
    if args.quick:
        log.info("quick run: LP2 not scored, nothing written")
        return 0

    survivors = np.flatnonzero(doublet)[None, :]
    obs = statistics(tests, survivors)[0]
    p = null.p_values(obs[None, :])[0]
    rows = []
    for t, test in enumerate(tests):
        cells = test.cells[survivors[0]]
        counts = np.bincount(cells[cells >= 0], minlength=test.n_cells)
        expected = counts.sum() * test.share
        status = "untestable" if test.name in weak else ("FIRES" if p[t] <= ALPHA else "silent")
        rows.append((test.name, test.variable, int(counts.sum()), round(float(obs[t]), 3), f"{p[t]:.3g}", status,
                     " ".join(test.labels), " ".join(map(str, counts)), " ".join(f"{e:.2f}" for e in expected)))
        log.info("%-4s %-40s n=%2d stat %9.3f p %.3g %s", test.name, test.variable, counts.sum(), obs[t], p[t], status)
    write_tsv(RESULTS_PATH, ("test", "variable", "n", "statistic", "p", "status", "cells", "observed", "expected"),
              rows)
    write_tsv(CONTROLS_PATH, ("control", "test", "fires_of_100", "required"), control_rows)
    log.info("wrote %s and %s", RESULTS_PATH.name, CONTROLS_PATH.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
