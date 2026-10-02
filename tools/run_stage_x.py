"""Stage X: key-free structure of the grid's 256 bytes (TODO.md, declared 2026-10-01 in 225ff30 before this script
existed).

X1 describes the bytes against iid uniform blocks. X2 is the key-free test: under c_i = σ_{i mod p}(m_i) with any byte
bijections σ, the coincident pairs within each residue class mod p are those of the plaintext, so plaintext windows are
the controls for every key at once. X3 reads the grid as a 2,048-bit integer. X4 tries five decompressors and stage N's
signature list on the unkeyed readings, with chance rates calibrated on uniform blocks.

Readings: R = printed order (`keys.grid_bytes`); C = column-major over the 32 × 8 grid.

Declared rules: X1 non-uniform if any two-sided p < 0.01/7. X2 PASS for (O, p) if C_p exceeds all null draws; EXCLUDED
for (O, p, K) if C_p < the 0.1 % quantile of K's controls. X3 excluded as an RSA-2048 modulus if even, not 2,048 bits,
or a prime factor < 10^6. X4 PASS on end-of-stream where the calibrated rate × 20 ≤ 0.01, inconclusive where higher.

Deterministic. Usage: python -m tools.run_stage_x [--quick]
"""

from __future__ import annotations

import argparse
import bz2
import csv
import logging
import lzma
import sys
import zlib
from pathlib import Path

import numpy as np

from tools.lpcore import keys
from tools.lpcore.corpus import REPO_ROOT, load_corpus
from tools.lpcore.verify import load_translation
from tools.run_stage_n import signature

log = logging.getLogger("stage_x")

PERIODIC_PATH = REPO_ROOT / "reference" / "findings" / "stage_x_periodic.tsv"
OTHER_PATH = REPO_ROOT / "reference" / "findings" / "stage_x_other.tsv"
EMERSON = REPO_ROOT / "data" / "corpora" / "emerson_essays.txt"
SIZE = 256
ROWS, COLS = 32, 8
PERIODS = range(1, 129)
NULL_DRAWS = 100_000
CONTROL_BLOCKS = 10_000
SEED = 3301
X1_ALPHA = 0.01 / 7
X2_QUANTILE = 0.001
X4_FAMILY = 20
X4_PASS = 0.01
FACTOR_BOUND = 10**6
HEX = np.frombuffer(b"0123456789abcdef", dtype=np.uint8)
B64 = np.frombuffer(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/", dtype=np.uint8)
CLASSES = ("EN", "RUNES", "HEX", "B64")
DECODERS = ("zlib raw deflate", "zlib", "gzip", "bz2", "lzma auto")
COLUMN_MAJOR = np.array([r * COLS + c for c in range(COLS) for r in range(ROWS)])


def column_major(data: np.ndarray) -> np.ndarray:
    """Read 256-byte rows (shape (..., 256)) down the 8 columns of the 32 × 8 grid."""
    return data[..., COLUMN_MAJOR]


def coincidences(blocks: np.ndarray, period: int) -> np.ndarray:
    """C_p per row of `blocks` (shape (n, 256)): equal-byte pairs within each residue class mod `period`."""
    tagged = np.sort((np.arange(SIZE) % period) * 256 + blocks.astype(np.int64), axis=1)
    idx = np.arange(SIZE)
    new_run = np.ones(tagged.shape, dtype=bool)
    new_run[:, 1:] = tagged[:, 1:] != tagged[:, :-1]
    start = np.maximum.accumulate(np.where(new_run, idx, 0), axis=1)
    return (idx - start).sum(axis=1)


def within_pairs(period: int) -> int:
    sizes = np.bincount(np.arange(SIZE) % period)
    return int((sizes * (sizes - 1) // 2).sum())


def control_blocks(corpus, quick: bool) -> dict[str, np.ndarray]:
    """256-byte plaintext windows per declared class K."""
    text = np.frombuffer(EMERSON.read_bytes(), dtype=np.uint8)
    starts = range(0, len(text) - SIZE + 1, 64)
    runes = np.array([r for w in keys.solved_plaintext_words(corpus, load_translation()) for r in w], dtype=np.uint8)
    rng = np.random.default_rng(SEED + 1)
    n = 500 if quick else CONTROL_BLOCKS
    out = {
        "EN": np.stack([text[s:s + SIZE] for s in starts]),
        "RUNES": np.stack([runes[s:s + SIZE] for s in range(len(runes) - SIZE + 1)]),
        "HEX": HEX[rng.integers(0, 16, (n, SIZE))],
        "B64": B64[rng.integers(0, 64, (n, SIZE))],
    }
    for name, blocks in out.items():
        log.info("controls %s: %d windows", name, len(blocks))
    return out


def null_blocks(draws: int, seed: int = SEED):
    """iid uniform 256-byte blocks in chunks, the X1/X2 null."""
    rng = np.random.default_rng(seed)
    for done in range(0, draws, 10_000):
        yield rng.integers(0, 256, (min(10_000, draws - done), SIZE), dtype=np.uint8)


def uniformity_stats(blocks: np.ndarray) -> dict[str, np.ndarray]:
    """X1's seven statistics per row."""
    counts = np.apply_along_axis(np.bincount, 1, blocks, minlength=256)
    hi = np.apply_along_axis(np.bincount, 1, blocks >> 4, minlength=16)
    lo = np.apply_along_axis(np.bincount, 1, blocks & 15, minlength=16)
    cols = column_major(blocks)
    return {
        "distinct values": (counts > 0).sum(axis=1),
        "chi2 256 bins": ((counts - 1.0) ** 2).sum(axis=1),
        "ones in 2048 bits": np.unpackbits(blocks, axis=1).sum(axis=1),
        "high-nibble chi2": ((hi - 16.0) ** 2 / 16.0).sum(axis=1),
        "low-nibble chi2": ((lo - 16.0) ** 2 / 16.0).sum(axis=1),
        "adjacent equal R": (blocks[:, 1:] == blocks[:, :-1]).sum(axis=1),
        "adjacent equal C": (cols[:, 1:] == cols[:, :-1]).sum(axis=1),
    }


def two_sided_p(null: np.ndarray, value: float) -> float:
    n = len(null)
    low = (np.count_nonzero(null <= value) + 1) / (n + 1)
    high = (np.count_nonzero(null >= value) + 1) / (n + 1)
    return min(1.0, 2 * min(low, high))


def x1_rows(grid: np.ndarray, draws: int) -> list[tuple]:
    observed = uniformity_stats(grid[None, :])
    parts: dict[str, list[np.ndarray]] = {name: [] for name in observed}
    for chunk in null_blocks(draws, SEED + 10):
        for name, values in uniformity_stats(chunk).items():
            parts[name].append(values)
    rows = []
    for name, value in observed.items():
        null = np.concatenate(parts[name])
        p = two_sided_p(null, float(value[0]))
        rows.append(("X1", name, "R+C", f"{float(value[0]):.4f}", f"null mean {null.mean():.4f}", f"{p:.4g}",
                     "NON-UNIFORM" if p < X1_ALPHA else "consistent"))
    return rows


def x2_rows(grid: np.ndarray, controls: dict[str, np.ndarray], draws: int) -> list[tuple]:
    """One row per (reading, period). iid blocks are exchangeable, so one null serves both readings."""
    null = np.zeros((draws, len(PERIODS)), dtype=np.int32)
    row = 0
    for chunk in null_blocks(draws):
        for j, p in enumerate(PERIODS):
            null[row:row + len(chunk), j] = coincidences(chunk, p)
        row += len(chunk)
    readings = {"R": grid, "C": column_major(grid)}
    quantiles = {(o, k): [] for o in readings for k in CLASSES}
    for k, blocks in controls.items():
        ordered = {"R": blocks, "C": column_major(blocks)}
        for o in readings:
            for p in PERIODS:
                quantiles[(o, k)].append(float(np.quantile(coincidences(ordered[o], p), X2_QUANTILE, method="lower")))
    rows = []
    for o, data in readings.items():
        for j, p in enumerate(PERIODS):
            c = int(coincidences(data[None, :], p)[0])
            column = null[:, j]
            structure = "PASS" if c > column.max() else "-"
            verdicts = ["EXCLUDED" if c < quantiles[(o, k)][j] else "not excluded" for k in CLASSES]
            rows.append((o, p, within_pairs(p), c, f"{column.mean():.3f}", int(column.max()),
                         f"{np.count_nonzero(column >= c) / len(column):.5f}", structure,
                         *(f"{quantiles[(o, k)][j]:g}" for k in CLASSES), *verdicts))
    return rows


def readings_bytes(grid: np.ndarray) -> dict[str, bytes]:
    r, c = bytes(grid.tolist()), bytes(column_major(grid).tolist())
    return {"R": r, "R reversed": r[::-1], "C": c, "C reversed": c[::-1]}


def primes_below(bound: int) -> list[int]:
    sieve = np.ones(bound, dtype=bool)
    sieve[:2] = False
    for q in range(2, int(bound ** 0.5) + 1):
        if sieve[q]:
            sieve[q * q::q] = False
    return np.flatnonzero(sieve).tolist()


def probable_prime(n: int, bases: list[int]) -> bool:
    """Miller–Rabin with the given bases (a composite passes all 25 first-prime bases with probability < 4^-25)."""
    if n < 2:
        return False
    for q in bases:
        if n % q == 0:
            return n == q
    d, s = n - 1, 0
    while d % 2 == 0:
        d, s = d // 2, s + 1
    for a in bases:
        y = pow(a, d, n)
        if y in (1, n - 1):
            continue
        for _ in range(s - 1):
            y = pow(y, 2, n)
            if y == n - 1:
                break
        else:
            return False
    return True


def x3_rows(grid: np.ndarray) -> list[tuple]:
    data = readings_bytes(grid)
    integers = {"R big-endian": int.from_bytes(data["R"], "big"), "R little-endian": int.from_bytes(data["R"], "little"),
                "C big-endian": int.from_bytes(data["C"], "big"), "C little-endian": int.from_bytes(data["C"], "little")}
    primes = primes_below(FACTOR_BOUND)
    rows = []
    for name, n in integers.items():
        factors = [q for q in primes if n % q == 0]
        failures = [f for f, bad in (("even", n % 2 == 0), (f"{n.bit_length()} bits", n.bit_length() != 2048),
                                     (f"factors < 10^6: {factors[:8]}", bool(factors))) if bad]
        rows.append(("X3", name, "integer", f"{n.bit_length()} bits", f"prime={probable_prime(n, primes[:25])}",
                     "; ".join(failures) or "-", "EXCLUDED as RSA modulus" if failures else "not excluded"))
    return rows


def decode(name: str, data: bytes) -> tuple[bool, int, str]:
    """(end-of-stream reached, output bytes, error) for one decoder."""
    if name.startswith("zlib") or name == "gzip":
        obj = zlib.decompressobj({"zlib raw deflate": -15, "zlib": 15, "gzip": 31}[name])
        error_type: type[Exception] = zlib.error
    elif name == "bz2":
        obj, error_type = bz2.BZ2Decompressor(), OSError
    else:
        obj, error_type = lzma.LZMADecompressor(lzma.FORMAT_AUTO), lzma.LZMAError
    try:
        out = obj.decompress(data, 1 << 20)
    except error_type as exc:
        return False, 0, str(exc)
    return bool(obj.eof), len(out), ""


def x4_rows(grid: np.ndarray, draws: int) -> list[tuple]:
    rates = {}
    for name in DECODERS:
        hits = sum(decode(name, bytes(block.tolist()))[0] for chunk in null_blocks(draws, SEED + 20) for block in chunk)
        rates[name] = hits / draws
        log.info("X4 calibration %s: %d / %d reach end-of-stream", name, hits, draws)
    rows = []
    for reading, data in readings_bytes(grid).items():
        for name in DECODERS:
            eof, produced, error = decode(name, data)
            if not eof:
                verdict = "EXCLUDED"
            elif rates[name] * X4_FAMILY <= X4_PASS:
                verdict = "PASS"
            else:
                verdict = "inconclusive"
            rows.append(("X4", name, reading, f"eof={eof} out={produced}", f"chance {rates[name]:.5f}",
                         error or "-", verdict))
        rows.append(("X4", "stage N signatures", reading, signature(data) or "-", "-", "-",
                     "PASS" if signature(data) else "EXCLUDED"))
    return rows


def write_tsv(path: Path, header: tuple[str, ...], rows: list[tuple]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--quick", action="store_true", help="smoke test: 2,000 null draws, 500 random controls")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    corpus = load_corpus()
    grid = np.array(keys.grid_bytes(corpus), dtype=np.uint8)
    if grid.shape != (SIZE,):
        log.error("grid has %d bytes, expected %d", len(grid), SIZE)
        return 1
    draws = 2_000 if args.quick else NULL_DRAWS
    controls = control_blocks(corpus, args.quick)

    periodic = x2_rows(grid, controls, draws)
    other = x1_rows(grid, draws) + x3_rows(grid) + x4_rows(grid, draws)

    for row in other:
        log.info("%s", row)
    log.info("X2 structure PASS: %s", [(r[0], r[1]) for r in periodic if r[7] == "PASS"])
    for i, k in enumerate(CLASSES):
        excluded = [f"{r[0]}{r[1]}" for r in periodic if r[12 + i] == "EXCLUDED"]
        log.info("X2 %s excluded in %d / %d cells: %s", k, len(excluded), len(periodic), excluded)
    if args.quick:
        log.info("quick run: nothing written")
        return 0
    write_tsv(PERIODIC_PATH, ("reading", "period", "pairs", "coincidences", "null_mean", "null_max", "null_p_ge",
                              "structure", *(f"q001_{k}" for k in CLASSES), *(f"verdict_{k}" for k in CLASSES)),
              periodic)
    write_tsv(OTHER_PATH, ("part", "test", "reading", "value", "reference", "detail", "verdict"), other)
    log.info("wrote %s and %s", PERIODIC_PATH.name, OTHER_PATH.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
