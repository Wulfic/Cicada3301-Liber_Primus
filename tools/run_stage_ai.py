"""Stage AI: are the three OutGuess payloads a depth? (TODO.md, declared 2026-11-13 in 9d79642 before this script existed.)

`data/outguess/page_17.bin`, `page_21.bin` and `page_43.bin` share a head and a tail byte for byte. For each pair the
XOR X = P_a ⊕ P_b of the bytes where they differ is scored three ways:
  S1  bit phase: is bit j of X zero at the same rate for j = 0…7? (8 × 2 homogeneity χ², 7 df)
  S2  bit agreement: zero bits of X against Binomial(8n, ½) (two-sided z)
  S3  byte uniformity: X's 256 byte values against uniform (χ², 255 df)
Each test fires at p ≤ 1e-5. Verdict: DEPTH if S1 fires for any pair; else RELATED if S2 or S3 fires for any pair;
else INDEPENDENT. Controls (seeded, at the real lengths) must all be classed as declared, or the stage is void.

Deterministic. Usage: python -m tools.run_stage_ai [--quick]   (--quick: controls only, payloads not scored, nothing written)
"""

from __future__ import annotations

import argparse
import base64
import logging
import math
import sys

import numpy as np

from tools.lpcore.corpus import REPO_ROOT
from tools.lpcore.stats import chi2_sf_wilson_hilferty
from tools.run_stage_x import write_tsv

log = logging.getLogger("stage_ai")

OUTGUESS = REPO_ROOT / "data" / "outguess"
CORPORA = REPO_ROOT / "data" / "corpora"
RESULTS_PATH = REPO_ROOT / "reference" / "findings" / "stage_ai_pairs.tsv"
CONTROLS_PATH = REPO_ROOT / "reference" / "findings" / "stage_ai_controls.tsv"
PAIRS = (("17", "21"), ("17", "43"), ("21", "43"))
ALPHA = 1e-5
SEED = 3301
N_NEGATIVE = 100
N_RAW = 20
RAW_MEAN_RUN = 64        # bytes, geometric
RAW_SHARED = 0.30        # share of runs that are "shared"
RAW_FLIP = 0.03          # P(bit of X is 1) inside a shared run

HEADER = ("name", "lo", "hi", "n", "chi2_phase", "p_phase", "z_agree", "p_agree", "chi2_bytes", "p_bytes",
          "zero_bytes", "longest_zero_run", "fires", "verdict") + tuple(f"zero_rate_bit{j}" for j in range(7, -1, -1))


def load_payloads() -> dict[str, np.ndarray]:
    return {k: np.frombuffer((OUTGUESS / f"page_{k}.bin").read_bytes(), dtype=np.uint8) for k in ("17", "21", "43")}


def differing_span(a: np.ndarray, b: np.ndarray) -> tuple[int, int]:
    """[first, last + 1) of the positions where a and b differ."""
    diff = np.flatnonzero(a != b)
    if len(diff) == 0:
        raise ValueError("arrays are identical: no differing span")
    return int(diff[0]), int(diff[-1]) + 1


def longest_zero_run(x: np.ndarray) -> int:
    best = run = 0
    for v in (x == 0):
        run = run + 1 if v else 0
        best = max(best, run)
    return best


def statistics(x: np.ndarray) -> dict[str, object]:
    """S1, S2, S3 and the reported descriptives for one XOR stream x (uint8)."""
    n = len(x)
    if n == 0:
        raise ValueError("empty XOR stream")
    ones = np.unpackbits(x[:, None], axis=1).sum(axis=0).astype(float)   # column 0 is bit 7
    zeros = n - ones
    p1 = ones.sum() / (8 * n)
    if p1 in (0.0, 1.0):
        chi_phase = 0.0
    else:
        chi_phase = float((((ones - n * p1) ** 2) / (n * p1) + ((zeros - n * (1 - p1)) ** 2) / (n * (1 - p1))).sum())
    z_agree = float((zeros.sum() - 4 * n) / math.sqrt(2 * n))
    counts = np.bincount(x, minlength=256).astype(float)
    chi_bytes = float(((counts - n / 256) ** 2 / (n / 256)).sum())
    return {
        "n": n,
        "chi2_phase": chi_phase, "p_phase": chi2_sf_wilson_hilferty(chi_phase, 7) if chi_phase > 0 else 1.0,
        "z_agree": z_agree, "p_agree": math.erfc(abs(z_agree) / math.sqrt(2)),
        "chi2_bytes": chi_bytes, "p_bytes": chi2_sf_wilson_hilferty(chi_bytes, 255),
        "zero_bytes": int(counts[0]), "longest_zero_run": longest_zero_run(x),
        "zero_rates": (zeros / n).tolist(),
    }


def fires(s: dict[str, object]) -> str:
    """Which of S1, S2, S3 fire, e.g. 'S1+S3', or '-'."""
    hit = [name for name, key in (("S1", "p_phase"), ("S2", "p_agree"), ("S3", "p_bytes")) if s[key] <= ALPHA]
    return "+".join(hit) or "-"


def verdict(fired: list[str]) -> str:
    """The declared rule over a set of pairs."""
    if any("S1" in f for f in fired):
        return "DEPTH"
    if any("S2" in f or "S3" in f for f in fired):
        return "RELATED"
    return "INDEPENDENT"


def row(name: str, lo: int, hi: int, x: np.ndarray, cls: str | None = None) -> tuple:
    s = statistics(x)
    f = fires(s)
    return (name, lo, hi, s["n"], f"{s['chi2_phase']:.3f}", f"{s['p_phase']:.3e}", f"{s['z_agree']:.3f}",
            f"{s['p_agree']:.3e}", f"{s['chi2_bytes']:.3f}", f"{s['p_bytes']:.3e}", s["zero_bytes"],
            s["longest_zero_run"], f, cls or verdict([f])) + tuple(f"{r:.5f}" for r in s["zero_rates"])


def in_depth(m_a: bytes, m_b: bytes, rng: np.random.Generator) -> np.ndarray:
    """XOR of two messages encrypted under one shared random pad (the pad cancels, as H-stream says)."""
    a = np.frombuffer(m_a, dtype=np.uint8)
    b = np.frombuffer(m_b, dtype=np.uint8)
    if len(a) != len(b):
        raise ValueError(f"messages differ in length: {len(a)} vs {len(b)}")
    pad = rng.integers(0, 256, len(a), dtype=np.uint8)
    return (a ^ pad) ^ (b ^ pad)


def simulated_raw(n: int, rng: np.random.Generator) -> np.ndarray:
    """Simulated H-raw XOR: geometric runs, RAW_SHARED of them near-identical, bit phase exchangeable by construction."""
    bits = np.empty(8 * n, dtype=np.uint8)
    i = 0
    while i < 8 * n:
        length = 8 * int(rng.geometric(1 / RAW_MEAN_RUN))
        stop = min(i + length, 8 * n)
        p = RAW_FLIP if rng.random() < RAW_SHARED else 0.5
        bits[i:stop] = rng.random(stop - i) < p
        i = stop
    return np.packbits(bits)


def controls(n: int) -> list[tuple]:
    """Every declared control at length n, each row carrying its expected class and length in the name."""
    rng = np.random.default_rng(SEED + n)
    rows = []
    for k in range(N_NEGATIVE):
        a = rng.integers(0, 256, n, dtype=np.uint8)
        b = rng.integers(0, 256, n, dtype=np.uint8)
        rows.append(row(f"n={n} negative-{k:03d} expect INDEPENDENT", 0, n, a ^ b))
    emerson = (CORPORA / "emerson_essays.txt").read_bytes()
    reliance = (CORPORA / "self_reliance.txt").read_bytes()
    if len(emerson) < 3 * n or len(reliance) < n:
        raise ValueError("corpora too short for the declared text controls")
    depth = {
        "english emerson[0:n] x emerson[n:2n]": (emerson[:n], emerson[n:2 * n]),
        "english emerson[2n:3n] x self_reliance[0:n]": (emerson[2 * n:3 * n], reliance[:n]),
        "hex": (rng.bytes(n // 2 + 1).hex()[:n].encode(), rng.bytes(n // 2 + 1).hex()[:n].encode()),
        "base64": (base64.b64encode(rng.bytes(n))[:n], base64.b64encode(rng.bytes(n))[:n]),
    }
    for name, (m_a, m_b) in depth.items():
        rows.append(row(f"n={n} depth {name} expect DEPTH", 0, n, in_depth(m_a, m_b, rng)))
    for k in range(N_RAW):
        rows.append(row(f"n={n} raw-{k:02d} expect RELATED", 0, n, simulated_raw(n, rng)))
    return rows


def controls_pass(rows: list[tuple]) -> list[str]:
    """Names of control rows whose class is not the expected one (empty means the stage is valid)."""
    bad = []
    for r in rows:
        expected = r[0].rsplit("expect ", 1)[1]
        if r[13] != expected or (expected == "RELATED" and "S1" in r[12]):
            bad.append(r[0])
    return bad


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--quick", action="store_true", help="controls only; payloads not scored, nothing written")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    p = load_payloads()
    spans = {pair: differing_span(p[pair[0]], p[pair[1]]) for pair in PAIRS}
    log.info("differing spans: %s", spans)
    lengths = sorted({hi - lo for lo, hi in spans.values()})

    control_rows = [r for n in lengths for r in controls(n)]
    bad = controls_pass(control_rows)
    log.info("controls: %d rows; misclassified: %s", len(control_rows), bad or "none")
    for r in control_rows:
        if "negative" not in r[0]:
            log.info("  %s: fires %s, class %s, p_phase %s", r[0], r[12], r[13], r[5])
    if bad:
        log.error("stage void: %d control(s) misclassified; payloads not scored", len(bad))
        return 1
    if args.quick:
        log.info("quick run: payloads not scored, nothing written")
        return 0

    rows = []
    for (a, b), (lo, hi) in spans.items():
        rows.append(row(f"{a}x{b}", lo, hi, p[a][lo:hi] ^ p[b][lo:hi]))
        log.info("%sx%s [%d, %d): fires %s; S1 χ² %s p %s; S2 z %s; S3 χ² %s p %s; zero bytes %d, longest run %d",
                 a, b, lo, hi, rows[-1][12], rows[-1][4], rows[-1][5], rows[-1][6], rows[-1][8], rows[-1][9],
                 rows[-1][10], rows[-1][11])
        log.info("  zero rate by bit 7..0: %s", rows[-1][14:])
    final = verdict([r[12] for r in rows])
    rows = [r[:13] + (final,) + r[14:] for r in rows]
    log.info("VERDICT: %s", final)
    write_tsv(RESULTS_PATH, HEADER, rows)
    write_tsv(CONTROLS_PATH, HEADER, control_rows)
    log.info("wrote %s and %s", RESULTS_PATH.name, CONTROLS_PATH.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
