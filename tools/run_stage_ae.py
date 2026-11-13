"""Stage AE: periodic keys under any alphabets, every lag of the continuous stream (TODO.md, declared 2026-10-12 in
434060d before this script existed).

A periodic key that selects any alphabet, c_i = σ_{k_i}(p_i) with k_{i+L} = k_i, gives c_i = c_{i+L} exactly when
p_i = p_{i+L}, at the plaintext's agreement rate (Σq² ≈ 0.062) whatever the alphabets. Statistic: k(L) = #{t : c_t =
c_{t+L}} over n(L) = N − L pairs, L = 11…N − 11, segments 7–15 read as one stream.

Declared rule:
- PASS iff P(X ≥ k | n, p0) ≤ 0.01 / 12,935, with p0 = stats.repeat_probability of the stream (C9's null).
- Excluded iff P(X ≤ k | n, p_H) ≤ e^−10, with p_H = 0.050.
- Valid iff 20 flat null streams with the anti-doublet rule give no PASS at any lag, and the periodic-tabula controls
  (P ∈ {1033, 1729, 3301, 6000, 9000}, 10 draws each from E and L) give no exclusion at their own period. Power is
  reported: they should PASS at P ≤ 6000.

Deterministic. Usage: python -m tools.run_stage_ae [--quick]   (--quick: 3 nulls and 2 control draws, no LP2, no files)
"""

from __future__ import annotations

import argparse
import logging
import math
import sys

import numpy as np

from tools.lpcore import leak, stats
from tools.lpcore.corpus import REPO_ROOT, load_corpus
from tools.lpcore.gematria import N
from tools.run_stage_ac import MIN_SEPARATION, Plaintexts, lp2_stream
from tools.run_stage_x import write_tsv
from tools.run_stage_z import anti_doublet

log = logging.getLogger("stage_ae")

LAGS_PATH = REPO_ROOT / "reference" / "findings" / "stage_ae_lags.tsv"
CONTROLS_PATH = REPO_ROOT / "reference" / "findings" / "stage_ae_controls.tsv"
P_H = 0.050
EXCLUDE_LOG = -10.0
FAMILY_ALPHA = 0.01
CONTROL_PERIODS = (1033, 1729, 3301, 6000, 9000)
POWER_MAX_PERIOD = 6000
NAMED_PERIODS = (1033, 1729, 3301)
SOURCES = ("E", "L")
NULL_STREAMS = 20
CONTROL_DRAWS = 10
SEED = 3301


def lag_agreements(c: np.ndarray) -> np.ndarray:
    """a[L] = #{t : c_t = c_{t+L}} for every L = 0…len − 1, exactly (FFT autocorrelation per rune, rounded)."""
    n = len(c)
    size = 1 << (2 * n - 1).bit_length()
    total = np.zeros(n)
    for v in range(N):
        f = np.fft.rfft((c == v).astype(float), size)
        total += np.fft.irfft(f * np.conj(f), size)[:n]
    return np.rint(total).astype(np.int64)


def lags_of(length: int) -> range:
    return range(MIN_SEPARATION, length - MIN_SEPARATION + 1)


def pass_threshold(length: int) -> float:
    return FAMILY_ALPHA / len(lags_of(length))


def upper_p(k: int, n: int, p0: float) -> float:
    return leak.binom_sf(k, n, p0)


def excluded(k: int, n: int) -> bool:
    return leak.binom_cdf(k, n, P_H) <= math.exp(EXCLUDE_LOG)


def any_pass(c: np.ndarray) -> tuple[bool, float]:
    """Whether some lag passes, and the smallest upper-tail p. Lags under mean + 4 sd cannot pass and are skipped."""
    p0 = stats.repeat_probability([c.tolist()])
    agree, length = lag_agreements(c), len(c)
    best = 1.0
    for L in lags_of(length):
        n, k = length - L, int(agree[L])
        if k > n * p0 + 4 * math.sqrt(n * p0):
            best = min(best, upper_p(k, n, p0))
    return best <= pass_threshold(length), best


def periodic_tabula(plain: np.ndarray, period: int, rng: np.random.Generator) -> np.ndarray:
    """c_i = σ_{i mod P}(p_i), one fresh random alphabet per residue class, then the anti-doublet rule."""
    alphabets = np.argsort(rng.random((period, N)), axis=1)
    return anti_doublet(alphabets[np.arange(len(plain)) % period, plain], rng)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--quick", action="store_true", help="3 nulls and 2 control draws; LP2 not scored, no files")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    null_streams, draws = (3, 2) if args.quick else (NULL_STREAMS, CONTROL_DRAWS)

    corpus = load_corpus()
    c_lp2 = lp2_stream(corpus)
    length = len(c_lp2)
    threshold = pass_threshold(length)
    log.info("LP2 stream %d runes; PASS threshold p ≤ %.3g; exclusion P(X ≤ k | p_H = %.3f) ≤ e^%.0f", length,
             threshold, P_H, EXCLUDE_LOG)

    rng = np.random.default_rng([SEED, 1])
    valid = True
    null_best = []
    for _ in range(null_streams):
        passed, best = any_pass(anti_doublet(rng.integers(0, N, length), rng))
        valid &= not passed
        null_best.append(best)
    log.info("nulls: %d streams, smallest upper p among lags above mean + 4 sd: %s (threshold %.3g)", null_streams,
             f"{min(null_best):.3g}" if min(null_best) < 1.0 else "none above", threshold)

    texts = Plaintexts(corpus)
    rows = []
    for period in CONTROL_PERIODS:
        for source in SOURCES:
            k_rates, n_excluded, n_passed = [], 0, 0
            for _ in range(draws):
                c = periodic_tabula(np.array(texts.draw(source, length, rng)), period, rng)
                agree = lag_agreements(c)
                n, k = length - period, int(agree[period])
                k_rates.append(k / n)
                n_excluded += excluded(k, n)
                n_passed += upper_p(k, n, stats.repeat_probability([c.tolist()])) <= threshold
            valid &= n_excluded == 0
            rows.append((period, source, draws, f"{min(k_rates):.4f}", f"{np.mean(k_rates):.4f}", n_excluded, n_passed))
            log.info("control P=%-5d %s: agreement rate min %.4f mean %.4f; excluded %d, passed %d of %d", period,
                     source, min(k_rates), np.mean(k_rates), n_excluded, n_passed, draws)
    log.info("run %s", "VALID" if valid else "VOID")
    if args.quick:
        log.info("quick run: LP2 not scored, nothing written")
        return 0 if valid else 2

    p0 = stats.repeat_probability([c_lp2.tolist()])
    agree = lag_agreements(c_lp2)
    lag_rows, n_pass, n_excl, best = [], 0, 0, (1.0, 0)
    for L in lags_of(length):
        n, k = length - L, int(agree[L])
        p_up = upper_p(k, n, p0)
        excl = excluded(k, n) and valid
        n_pass += p_up <= threshold
        n_excl += excl
        best = min(best, (p_up, L))
        lag_rows.append((L, n, k, f"{k / n:.5f}", f"{p_up:.4g}", f"{leak.binom_cdf(k, n, P_H):.4g}",
                         "EXCLUDED" if excl else "-"))
    open_lags = [r[0] for r in lag_rows if r[-1] != "EXCLUDED"]
    log.info("LP2: p0 %.5f; best lag %d (upper p %.3g); %s", p0, best[1], best[0],
             "VOID" if not valid else ("PASS" if n_pass else "NO PASS"))
    log.info("excluded %d of %d lags; first lag not excluded: %s", n_excl, len(lag_rows), min(open_lags) if open_lags else "-")
    for period in NAMED_PERIODS:
        row = lag_rows[period - MIN_SEPARATION]
        log.info("named period %d: %s", period, row)
    write_tsv(LAGS_PATH, ("lag", "pairs", "agreements", "rate", "upper_p_null", "lower_p_model", "verdict"), lag_rows)
    write_tsv(CONTROLS_PATH, ("period", "source", "draws", "rate_min", "rate_mean", "excluded", "passed"), rows)
    log.info("wrote %s and %s", LAGS_PATH.name, CONTROLS_PATH.name)
    return 0 if valid else 2


if __name__ == "__main__":
    sys.exit(main())
