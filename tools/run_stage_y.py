"""Stage Y: the grid under every long byte source on disk, at every offset (TODO.md, declared 2026-10-01 in edd9c53
before this script existed).

Each source s is a running key on the grid from every cyclic phase o: k_i = s[(o + i) mod |s|], in step. Four readings
of the grid (R, R reversed, C, C reversed; C = column-major over the 32 × 8 grid, as in stage X) and four operations
(m = g ⊕ k, g − k, g + k, k − g mod 256). The statistic is D, the number of distinct byte values in m. For a fixed key,
an unrelated grid makes m uniform, so P(D ≤ d) is exact (`null_cdf`).

Declared rule: PASS if D ≤ 120 in any trial (3.79e-17 per trial). A (source, reading, op) cell is EXCLUDED if no trial
passes. The run is valid only if all 24 planted positives pass at their planted cell, no negative (uniform random grid)
passes, and the negatives' mean D is within 0.5 of 162.0.

Deterministic. Usage: python -m tools.run_stage_y [--quick]
"""

from __future__ import annotations

import argparse
import logging
import sys
from fractions import Fraction
from functools import lru_cache
from math import comb, factorial
from pathlib import Path

import numpy as np

from tools.lpcore import keys
from tools.lpcore.corpus import REPO_ROOT, load_corpus
from tools.run_stage_r import OUTGUESS, onion_2_bytes, page_00_bytes
from tools.run_stage_x import COLUMN_MAJOR, SIZE, control_blocks, write_tsv

log = logging.getLogger("stage_y")

RESULTS_PATH = REPO_ROOT / "reference" / "findings" / "stage_y_results.tsv"
CONTROLS_PATH = REPO_ROOT / "reference" / "findings" / "stage_y_controls.tsv"
THRESHOLD = 120
SEED = 3301
NEGATIVE_SEEDS = (1, 2, 3)
NEGATIVE_MEAN = 162.0
NEGATIVE_TOLERANCE = 0.5
READINGS = ("R", "R-rev", "C", "C-rev")
OPS = ("g^k", "g-k", "g+k", "k-g")
CLASSES = ("EN", "RUNES", "HEX", "B64")
PRINTABLE = np.zeros(256, dtype=bool)
PRINTABLE[32:127] = True
PRINTABLE[[9, 10, 13]] = True


@lru_cache(maxsize=1)
def _null_counts() -> tuple[int, ...]:
    """Number of 256-byte blocks with exactly d distinct values, d = 0…256: C(256, d) · S(256, d) · d!."""
    stirling = [1] + [0] * SIZE
    for i in range(1, SIZE + 1):
        row = [0] * (SIZE + 1)
        for k in range(1, i + 1):
            row[k] = k * stirling[k] + stirling[k - 1]
        stirling = row
    return tuple(comb(256, d) * stirling[d] * factorial(d) for d in range(SIZE + 1))


def null_cdf(d: int) -> float:
    """Exact P(D ≤ d) for iid uniform bytes."""
    counts = _null_counts()
    return float(Fraction(sum(counts[:d + 1]), 256 ** SIZE))


def null_mean() -> float:
    return float(Fraction(sum(d * c for d, c in enumerate(_null_counts())), 256 ** SIZE))


def sources() -> dict[str, bytes]:
    out = {
        "page_17.bin": (OUTGUESS / "page_17.bin").read_bytes(),
        "page_21.bin": (OUTGUESS / "page_21.bin").read_bytes(),
        "page_43.bin": (OUTGUESS / "page_43.bin").read_bytes(),
        "hint": (OUTGUESS / "wisdom_hint.txt").read_bytes(),
        "page_00-hex": page_00_bytes(),
        "onion-2-hex": onion_2_bytes(),
    }
    lengths = {name: len(data) for name, data in out.items()}
    if lengths != {"page_17.bin": 58152, "page_21.bin": 58152, "page_43.bin": 58152, "hint": 3368,
                   "page_00-hex": 991, "onion-2-hex": 256}:
        raise ValueError(f"source lengths differ from the declaration: {lengths}")
    return out


def read(grid: np.ndarray, reading: str) -> np.ndarray:
    if reading == "R":
        return grid
    if reading == "R-rev":
        return grid[::-1]
    if reading == "C":
        return grid[COLUMN_MAJOR]
    if reading == "C-rev":
        return grid[COLUMN_MAJOR][::-1]
    raise ValueError(f"unknown reading {reading!r}")


def unread(text: np.ndarray, reading: str) -> np.ndarray:
    """The grid whose `reading` is `text`."""
    if reading in ("R", "R-rev"):
        return text if reading == "R" else text[::-1]
    grid = np.empty(SIZE, dtype=np.uint8)
    grid[COLUMN_MAJOR] = text if reading == "C" else text[::-1]
    return grid


def decrypt(g: np.ndarray, k: np.ndarray, op: str) -> np.ndarray:
    """The plaintext candidate m for grid bytes g under key bytes k (both uint8, broadcastable)."""
    if op == "g^k":
        return g ^ k
    if op == "g-k":
        return g - k
    if op == "g+k":
        return g + k
    if op == "k-g":
        return k - g
    raise ValueError(f"unknown op {op!r}")


def encrypt(m: np.ndarray, k: np.ndarray, op: str) -> np.ndarray:
    """The inverse of `decrypt`: the grid bytes that decrypt to m."""
    if op == "g^k":
        return m ^ k
    if op == "g-k":
        return m + k
    if op == "g+k":
        return m - k
    if op == "k-g":
        return k - m
    raise ValueError(f"unknown op {op!r}")


def key_windows(source: bytes) -> np.ndarray:
    """Row o is the 256 key bytes from phase o, read cyclically: shape (|s|, 256)."""
    s = np.frombuffer(source, dtype=np.uint8)
    idx = (np.arange(len(s))[:, None] + np.arange(SIZE)[None, :]) % len(s)
    return s[idx]


def distinct(blocks: np.ndarray) -> np.ndarray:
    """D per row of a (n, 256) uint8 array."""
    ordered = np.sort(blocks, axis=1)
    return 1 + (ordered[:, 1:] != ordered[:, :-1]).sum(axis=1)


def search(grid: np.ndarray, windows: np.ndarray) -> dict[tuple[str, str], np.ndarray]:
    """D for every phase, per (reading, op)."""
    return {(r, op): distinct(decrypt(read(grid, r)[None, :], windows, op)) for r in READINGS for op in OPS}


def passes(found: dict[tuple[str, str], np.ndarray]) -> list[tuple[str, str, int, int]]:
    return [(r, op, int(o), int(d[o])) for (r, op), d in found.items() for o in np.flatnonzero(d <= THRESHOLD)]


def printable_fraction(m: np.ndarray) -> float:
    return float(PRINTABLE[m].mean())


def result_rows(grid: np.ndarray, name: str, source: bytes, windows: np.ndarray) -> list[tuple]:
    rows = []
    for (r, op), d in search(grid, windows).items():
        o = int(d.argmin())
        low = int(d[o])
        m = decrypt(read(grid, r), windows[o], op)
        per_trial = null_cdf(low)
        rows.append((name, len(source), r, op, len(d), low, o, f"{per_trial:.3e}", f"{per_trial * len(d):.3g}",
                     f"{printable_fraction(m):.3f}", f"{d.mean():.2f}",
                     "PASS" if low <= THRESHOLD else "EXCLUDED"))
    return rows


def positive_rows(corpus, srcs: dict[str, bytes], all_windows: dict[str, np.ndarray], quick: bool) -> list[tuple]:
    rng = np.random.default_rng(SEED)
    plains = control_blocks(corpus, quick)
    rows = []
    for name, source in srcs.items():
        windows = all_windows[name]
        for cls in CLASSES:
            m = plains[cls][rng.integers(len(plains[cls]))]
            o = int(rng.integers(len(source)))
            r = READINGS[rng.integers(len(READINGS))]
            op = OPS[rng.integers(len(OPS))]
            grid = unread(encrypt(m, windows[o], op), r)
            found = search(grid, windows)
            hits = passes(found)
            at_plant = int(found[(r, op)][o])
            ok = any(h[:3] == (r, op, o) for h in hits)
            rows.append(("positive", name, cls, "", r, op, o, at_plant, len(hits), "PASS" if ok else "FAIL"))
    return rows


def negative_rows(srcs: dict[str, bytes], all_windows: dict[str, np.ndarray]) -> tuple[list[tuple], float]:
    rows = []
    total, count = 0.0, 0
    for seed in NEGATIVE_SEEDS:
        grid = np.random.default_rng(seed).integers(0, 256, SIZE, dtype=np.uint8)
        for name in srcs:
            found = search(grid, all_windows[name])
            hits = passes(found)
            low = min(int(d.min()) for d in found.values())
            total += sum(float(d.sum()) for d in found.values())
            count += sum(len(d) for d in found.values())
            rows.append(("negative", name, "uniform", seed, "", "", "", low, len(hits),
                         "FAIL" if hits else "PASS"))
    return rows, total / count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--quick", action="store_true", help="smoke test on the three short sources; nothing written")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    corpus = load_corpus()
    grid = np.array(keys.grid_bytes(corpus), dtype=np.uint8)
    if grid.shape != (SIZE,):
        log.error("grid has %d bytes, expected %d", len(grid), SIZE)
        return 1
    srcs = sources()
    if args.quick:
        srcs = {k: v for k, v in srcs.items() if not k.endswith(".bin")}
    all_windows = {name: key_windows(data) for name, data in srcs.items()}
    trials = sum(len(w) for w in all_windows.values()) * len(READINGS) * len(OPS)
    log.info("%d sources, %d trials; null P(D <= %d) = %.3e per trial, %.3e family-wise; null mean D %.3f",
             len(srcs), trials, THRESHOLD, null_cdf(THRESHOLD), null_cdf(THRESHOLD) * trials, null_mean())

    controls = positive_rows(corpus, srcs, all_windows, args.quick)
    negatives, mean_d = negative_rows(srcs, all_windows)
    controls += negatives
    for row in controls:
        log.info("control %s", row)
    failed = [row for row in controls if row[-1] != "PASS"]
    valid = not failed and abs(mean_d - NEGATIVE_MEAN) <= NEGATIVE_TOLERANCE
    log.info("negatives mean D %.3f (declared %.1f ± %.1f); failed controls %d; run %s",
             mean_d, NEGATIVE_MEAN, NEGATIVE_TOLERANCE, len(failed), "VALID" if valid else "VOID")

    results = [row for name, data in srcs.items() for row in result_rows(grid, name, data, all_windows[name])]
    if not valid:
        results = [(*row[:-1], "VOID") for row in results]
    for row in results:
        log.info("%s", row)
    log.info("PASS cells: %s", [row[:4] for row in results if row[-1] == "PASS"])
    if args.quick:
        log.info("quick run: nothing written")
        return 0
    write_tsv(RESULTS_PATH, ("source", "length", "reading", "op", "trials", "min_D", "phase_at_min", "null_p_le_min",
                             "expected_trials_le_min", "printable_at_min", "mean_D", "verdict"), results)
    write_tsv(CONTROLS_PATH, ("kind", "source", "class", "seed", "reading", "op", "phase", "D", "passing_trials",
                              "verdict"), controls)
    log.info("wrote %s and %s", RESULTS_PATH.name, CONTROLS_PATH.name)
    return 0 if valid else 2


if __name__ == "__main__":
    sys.exit(main())
