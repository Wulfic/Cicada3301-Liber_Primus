"""Stage AA: keyless sliding-context ciphers (TODO.md, declared 2026-10-12 in 5364609 before this script existed).

A cipher with c_i = F(p_{i−a}, …, p_{i+b}), context width w = a + b, no key and no position dependence, sends equal
plaintext windows of n + w runes to equal cipher n-grams wherever they occur. So it keeps the plaintext's repeat count
of long windows, whatever F is.

Statistic K_n: pairs (i, j), j − i ≥ n, of equal cipher n-grams over all sliding windows. Mode "sec" counts pairs within
each section; mode "cont" counts them over segments 7–15 as one stream. n = 3…7.

Controls, per (mode, w, source): c_i = σ_ctx(p_i), ctx = (p_{i−w}, …, p_{i−1}) padded with a 30th symbol before the
context start (each section in "sec", the stream start in "cont"), σ_ctx a fresh random permutation per distinct
context, then stage Z's anti-doublet rule within each section.

Declared rule:
- Per (n, mode, w): lower = exp(m − 5s) − 1 over ln(K + 1). Testable iff, for both sources, lower > null max and every
  draw > null max. Excluded iff testable and K_LP2 < lower for both sources.
- Per (mode, w): excluded if any n excludes; else inconclusive if any n is testable; else untestable.
- Per (n, mode): PASS iff K_LP2 > null max and (K_LP2 − μ0)/σ0 ≥ 6, σ0 floored at 1.
- Valid iff every (n ≤ 5, mode) null mean lies within 3 s.e. of the analytic E[K_n]; otherwise every row is VOID.

Deterministic. Usage: python -m tools.run_stage_aa [--quick]   (--quick scores no LP2 runes and writes nothing)
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections import Counter
from collections.abc import Sequence
from math import comb

import numpy as np

from tools.lpcore import keys
from tools.lpcore.corpus import REPO_ROOT, load_corpus
from tools.lpcore.gematria import N
from tools.lpcore.verify import load_translation
from tools.run_stage_x import write_tsv
from tools.run_stage_z import (Sections, anti_doublet, emerson_words, fill_sections, log_lower, lp2_sections,
                               null_sections, p_equal, pairs, summarise)

log = logging.getLogger("stage_aa")

RESULTS_PATH = REPO_ROOT / "reference" / "findings" / "stage_aa_results.tsv"
VERDICTS_PATH = REPO_ROOT / "reference" / "findings" / "stage_aa_verdicts.tsv"
CONTROLS_PATH = REPO_ROOT / "reference" / "findings" / "stage_aa_controls.tsv"
NGRAMS = range(3, 8)
WIDTHS = range(0, 13)
MODES = ("sec", "cont")
SOURCES = ("E", "L")
NULL_DRAWS = 1_000
POSITIVE_DRAWS = 200
SEED = 3301
PASS_Z = 6.0
VALIDITY_SE = 3.0
VALIDITY_MAX_N = 5
PAD = N                                           # the 30th symbol before a context start


def streams_of(sections: Sections) -> list[np.ndarray]:
    return [np.array([r for w in sec for r in w], dtype=np.int64) for sec in sections]


def ngram_codes(stream: np.ndarray, n: int) -> np.ndarray:
    """Base-29 codes of every sliding n-gram of `stream`."""
    if len(stream) < n:
        return np.zeros(0, dtype=np.int64)
    windows = np.lib.stride_tricks.sliding_window_view(stream.astype(np.int64), n)
    return windows @ (N ** np.arange(n - 1, -1, -1, dtype=np.int64))


def separated_pairs(stream: np.ndarray, n: int) -> int:
    """Pairs (i, j), j − i ≥ n, of equal sliding n-grams: all equal pairs minus the overlapping ones."""
    codes = ngram_codes(stream, n)
    total = pairs(np.unique(codes, return_counts=True)[1])
    for d in range(1, n):
        total -= int(np.count_nonzero(codes[d:] == codes[:-d]))
    return total


def statistic(streams: Sequence[np.ndarray], n: int, mode: str) -> int:
    if mode == "sec":
        return sum(separated_pairs(s, n) for s in streams)
    return separated_pairs(np.concatenate(streams), n)


def separated_window_pairs(length: int, n: int) -> int:
    """How many pairs of n-windows with j − i ≥ n a stream of `length` runes has."""
    m = length - n + 1
    if m <= 0:
        return 0
    return comb(m, 2) - sum(max(0, m - d) for d in range(1, n))


def analytic_mean(sizes: Sequence[int], n: int, mode: str) -> float:
    """E[K_n] under the flat null with the rule: disjoint windows are equal with stage Z's p_equal(n)."""
    groups = sizes if mode == "sec" else [sum(sizes)]
    return sum(separated_window_pairs(m, n) for m in groups) * p_equal(n)


def context_encipher(stream: np.ndarray, w: int, rng: np.random.Generator) -> np.ndarray:
    """c_i = σ_ctx(p_i) with ctx = the w runes before i (PAD before the stream start), σ_ctx a fresh permutation."""
    if w == 0:
        return rng.permutation(N)[stream]
    padded = np.concatenate([np.full(w, PAD, dtype=np.int64), stream])
    contexts = np.lib.stride_tricks.sliding_window_view(padded, w)[:len(stream)]
    _, which = np.unique(contexts, axis=0, return_inverse=True)
    which = which.reshape(-1)
    perms = np.argsort(rng.random((int(which.max()) + 1, N)), axis=1)
    return perms[which, stream]


def encipher(plain: Sections, w: int, mode: str, rng: np.random.Generator) -> list[np.ndarray]:
    """The plaintext through a random context-w cipher, then the anti-doublet rule within each section."""
    streams = streams_of(plain)
    if mode == "sec":
        ciphered = [context_encipher(s, w, rng) for s in streams]
    else:
        cuts = np.cumsum([len(s) for s in streams])[:-1]
        ciphered = np.split(context_encipher(np.concatenate(streams), w, rng), cuts)
    return [anti_doublet(c, rng) for c in ciphered]


def cell_verdict(k: int, null_max: int, lower: dict[str, float], minimum: dict[str, int]) -> str:
    testable = all(lo > null_max for lo in lower.values()) and all(m > null_max for m in minimum.values())
    if not testable:
        return "UNTESTABLE"
    return "EXCLUDED" if all(k < lo for lo in lower.values()) else "INCONCLUSIVE"


def width_verdict(cell_verdicts: Sequence[str]) -> str:
    if "EXCLUDED" in cell_verdicts:
        return "EXCLUDED"
    return "INCONCLUSIVE" if "INCONCLUSIVE" in cell_verdicts else "UNTESTABLE"


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
    log.info("LP2 shape: %d sections, %d runes", len(shape), sum(sizes))
    sources = {"E": (emerson_words(), True),
               "L": (keys.solved_plaintext_words(corpus, load_translation()), False)}
    stat_cells = [(n, mode) for n in NGRAMS for mode in MODES]

    rng = np.random.default_rng(SEED)
    null_values: dict[tuple, list[int]] = {c: [] for c in stat_cells}
    for _ in range(null_draws):
        sample = streams_of(null_sections(shape, rng))
        for n, mode in stat_cells:
            null_values[(n, mode)].append(statistic(sample, n, mode))
    null = {c: summarise(v) for c, v in null_values.items()}
    valid = True
    for (n, mode), (mu0, sd0, null_max) in null.items():
        expected = analytic_mean(sizes, n, mode)
        ok = n > VALIDITY_MAX_N or abs(mu0 - expected) <= VALIDITY_SE * sd0 / np.sqrt(null_draws)
        valid &= ok
        log.info("null K_%d %-4s %.3f ± %.3f (max %d), analytic %.3f%s", n, mode, mu0, sd0, null_max, expected,
                 "" if ok else " MISMATCH")
    log.info("run %s", "VALID" if valid else "VOID")

    controls: dict[tuple, dict[str, list[int]]] = {}
    for mode in MODES:
        for w in WIDTHS:
            for name in SOURCES:
                words, contiguous = sources[name]
                crng = np.random.default_rng([SEED, MODES.index(mode), w, SOURCES.index(name)])
                ks: dict[int, list[int]] = {n: [] for n in NGRAMS}
                for _ in range(pos_draws):
                    cipher = encipher(fill_sections(words, sizes, crng, contiguous), w, mode, crng)
                    for n in NGRAMS:
                        ks[n].append(statistic(cipher, n, mode))
                for n in NGRAMS:
                    controls.setdefault((n, mode, w), {})[name] = ks[n]
            log.info("controls %-4s w=%-2d %s", mode, w,
                     " ".join(f"n{n}:E{log_lower(controls[(n, mode, w)]['E']):.0f}/"
                              f"L{log_lower(controls[(n, mode, w)]['L']):.0f}" for n in NGRAMS))

    control_rows = []
    testable_cells = []
    for (n, mode, w), by_source in controls.items():
        null_max = null[(n, mode)][2]
        lower = {s: log_lower(v) for s, v in by_source.items()}
        if all(lo > null_max for lo in lower.values()) and all(min(v) > null_max for v in by_source.values()):
            testable_cells.append((n, mode, w))
        for s, v in by_source.items():
            mu, sd, _ = summarise(v)
            control_rows.append((n, mode, w, s, len(v), f"{mu:.2f}", f"{sd:.2f}", min(v), max(v), f"{lower[s]:.2f}"))
    if args.quick:
        log.info("quick run: LP2 not scored, nothing written; %d testable cells", len(testable_cells))
        for mode in MODES:
            log.info("  %s: widths with a testable n: %s", mode,
                     sorted({w for n, m, w in testable_cells if m == mode}))
        return 0 if valid else 2

    lp2 = streams_of(lp2_sections(corpus))
    results, k_lp2 = [], {}
    for n, mode in stat_cells:
        mu0, sd0, null_max = null[(n, mode)]
        k = statistic(lp2, n, mode)
        k_lp2[(n, mode)] = k
        z0 = (k - mu0) / max(sd0, 1.0)
        v = "PASS" if k > null_max and z0 >= PASS_Z else "NO PASS"
        results.append((n, mode, k, f"{mu0:.3f}", f"{sd0:.3f}", null_max, f"{analytic_mean(sizes, n, mode):.3f}",
                        f"{z0:.2f}", v if valid else "VOID"))
    verdict_rows = []
    for mode in MODES:
        for w in WIDTHS:
            per_n = []
            for n in NGRAMS:
                by_source = controls[(n, mode, w)]
                lower = {s: log_lower(v) for s, v in by_source.items()}
                minimum = {s: min(v) for s, v in by_source.items()}
                per_n.append(cell_verdict(k_lp2[(n, mode)], null[(n, mode)][2], lower, minimum))
            v = width_verdict(per_n) if valid else "VOID"
            excluding = ",".join(str(n) for n, x in zip(NGRAMS, per_n) if x == "EXCLUDED") or "-"
            verdict_rows.append((mode, w, *per_n, excluding, v))
    for row in results + verdict_rows:
        log.info("%s", row)
    log.info("statistic cells: %s; width verdicts: %s", dict(Counter(r[-1] for r in results)),
             dict(Counter(r[-1] for r in verdict_rows)))
    write_tsv(RESULTS_PATH, ("n", "mode", "K_LP2", "null_mean", "null_sd", "null_max", "analytic_mean", "z_null",
                             "verdict"), results)
    write_tsv(VERDICTS_PATH, ("mode", "w", *(f"n{n}" for n in NGRAMS), "excluded_by_n", "verdict"), verdict_rows)
    write_tsv(CONTROLS_PATH, ("n", "mode", "w", "source", "draws", "mean", "sd", "min", "max", "log_lower_5sd"),
              control_rows)
    log.info("wrote %s, %s and %s", RESULTS_PATH.name, VERDICTS_PATH.name, CONTROLS_PATH.name)
    return 0 if valid else 2


if __name__ == "__main__":
    sys.exit(main())
