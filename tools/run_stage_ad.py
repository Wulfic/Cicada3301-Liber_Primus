"""Stage AD: LP2's own ciphertext as the key, at any lag, forwards or backwards (TODO.md, declared 2026-10-12 in 03dad0b
before this script existed).

LP2 is read as one 12,956-rune stream c. For pairs i < j on a forward diagonal (j = i + L) or a reverse anti-diagonal
(i + j = σ), j − i ≥ 11, one rune is the other's plaintext under the other's ciphertext as key, up to a shift a:
- diff:    x = c_j − c_i, plaintext x − a     (c_j = p_j + c_i + a)
- diffrev: x = c_j − c_i, plaintext a − x     (Beaufort c_j = c_i + a − p_j)
- sum:     x = c_j + c_i, plaintext x − a     (c_j = p_j + a − c_i)
- sumrev:  x = c_j + c_i, plaintext a − x     (Beaufort c_j = a − c_i − p_j)
Score per pair: s = ln((1 − ε)·29·q(plaintext) + ε), detect's emission (ε = 0.1), so E[e^s] = 1 under a flat cipher.
- F(L, rel, a): Σ s over the whole forward diagonal, an autokey at lag L. PASS iff F ≥ 30; excluded iff F ≤ −10 for
  L ≤ P_max.
- S: the best segment per (rel, a) on every forward and reverse diagonal, one reused ciphertext stretch. PASS iff S ≥ 30.
- Valid iff 4 flat null streams with the rule give max F < 30 and max S < 30.

Deterministic. Usage: python -m tools.run_stage_ad [--quick]   (--quick scans a few lags of one null, scores no LP2 runes
and writes nothing)
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from tools.lpcore import detect
from tools.lpcore.corpus import REPO_ROOT, load_corpus
from tools.lpcore.gematria import N
from tools.run_stage_ac import (EXCLUDE, MIN_SEPARATION, PASS, Plaintexts, lp2_stream, plaintext_model, reverse_pairs,
                                reverse_sigmas, segment_stats)
from tools.run_stage_x import write_tsv
from tools.run_stage_z import anti_doublet

log = logging.getLogger("stage_ad")

LAGS_PATH = REPO_ROOT / "reference" / "findings" / "stage_ad_lags.tsv"
TOP_PATH = REPO_ROOT / "reference" / "findings" / "stage_ad_top.tsv"
CONTROLS_PATH = REPO_ROOT / "reference" / "findings" / "stage_ad_controls.tsv"
RELATIONS = ("diff", "diffrev", "sum", "sumrev")
AUTOKEY_LAGS = (11, 100, 1000, 1033, 1729, 3301, 6000, 9000, 11000, 12000, 12500, 12800, 12900)
NAMED_LAGS = (1033, 1729, 3301)
REUSE_LENGTHS = (100, 200, 300, 500, 1000)
ORIENTATIONS = ("forward", "reverse")
SOURCES = ("E", "L")
NULL_STREAMS = 4
AUTOKEY_DRAWS = 10
REUSE_DRAWS = 25
KEEP = 0.19
SEED = 3301
TOP = 20


def score_tables(q: Sequence[float]) -> np.ndarray:
    """tables[rel, a, x] = ln emission of the plaintext the relation implies for combination x and shift a."""
    log_e = np.log(np.array(detect.emission_ratios(list(q))))
    x = np.arange(N)
    out = np.empty((len(RELATIONS), N, N))
    for a in range(N):
        out[0, a] = out[2, a] = log_e[(x - a) % N]
        out[1, a] = out[3, a] = log_e[(a - x) % N]
    return out


def combine(ci: np.ndarray, cj: np.ndarray) -> tuple[np.ndarray, ...]:
    d, s = (cj - ci) % N, (cj + ci) % N
    return d, d, s, s


def forward_scan(c: np.ndarray, tables: np.ndarray, lags: Sequence[int]) -> tuple[np.ndarray, np.ndarray]:
    F = np.empty((len(lags), len(RELATIONS), N))
    S = np.empty_like(F)
    for n, L in enumerate(lags):
        for r, x in enumerate(combine(c[:-L], c[L:])):
            F[n, r], S[n, r] = segment_stats(tables[r], x)
    return F, S


def reverse_scan(c: np.ndarray, tables: np.ndarray, sigmas: Sequence[int]) -> np.ndarray:
    S = np.full((len(sigmas), len(RELATIONS), N), -np.inf)
    for n, sigma in enumerate(sigmas):
        i, j = reverse_pairs(sigma, len(c))
        if len(i):
            for r, x in enumerate(combine(c[i], c[j])):
                S[n, r] = segment_stats(tables[r], x)[1]
    return S


def full_scan(args):
    c, tables, lags, sigmas = args
    F, S_fwd = forward_scan(c, tables, lags)
    return F, S_fwd, reverse_scan(c, tables, sigmas)


# ---- controls -----------------------------------------------------------------------------------------------------

def encipher_rune(p: int, key_rune: int, rel: str, a: int) -> int:
    """The cipher rune at j given its plaintext and the ciphertext rune c_i used as key."""
    if rel == "diff":
        return (p + key_rune + a) % N
    if rel == "sum":
        return (p - key_rune + a) % N
    if rel == "diffrev":
        return (key_rune + a - p) % N
    return (a - key_rune - p) % N


def autokey_encipher(plain: Sequence[int], rel: str, a: int, rng: np.random.Generator, *, lag: int | None = None,
                     reuse: tuple[str, int, int, int] | None = None) -> np.ndarray:
    """Encipher with ciphertext as key: every j ≥ lag keyed by c_{j−lag}, or one stretch (orientation, i, j0, m) keyed
    by c[i:i+m] (forward) or that stretch reversed; all other runes take a fresh random key. The anti-doublet rule
    re-draws a would-be doublet uniformly with probability 1 − KEEP, and later runes use the re-drawn value."""
    n = len(plain)
    source = np.full(n, -1, dtype=np.int64)
    if lag is not None:
        source[lag:] = np.arange(n - lag)
    if reuse is not None:
        orientation, i, j0, m = reuse
        src = np.arange(i, i + m)
        source[j0:j0 + m] = src if orientation == "forward" else src[::-1]
    c = np.empty(n, dtype=np.int64)
    fresh = rng.integers(0, N, n)
    for j in range(n):
        c[j] = (plain[j] + fresh[j]) % N if source[j] < 0 else encipher_rune(plain[j], int(c[source[j]]), rel, a)
        if j and c[j] == c[j - 1] and rng.random() >= KEEP:
            c[j] = rng.integers(N)
    return c


def reuse_positions(length: int, m: int, rng: np.random.Generator) -> tuple[int, int]:
    i = int(rng.integers(0, length - 2 * m - MIN_SEPARATION))
    return i, int(rng.integers(i + m + MIN_SEPARATION, length - m + 1))


def planted_F(c: np.ndarray, tables: np.ndarray, lag: int, rel: str, a: int) -> float:
    r = RELATIONS.index(rel)
    return float(tables[r, a, combine(c[:-lag], c[lag:])[r]].sum())


def planted_S(c: np.ndarray, tables: np.ndarray, orientation: str, i: int, j: int, m: int, rel: str, a: int) -> float:
    r = RELATIONS.index(rel)
    if orientation == "forward":
        x = combine(c[:-(j - i)], c[j - i:])[r]
    else:
        ii, jj = reverse_pairs(i + m - 1 + j, len(c))
        x = combine(c[ii], c[jj])[r]
    return float(segment_stats(tables[r][a:a + 1], x)[1][0])


def run_controls(tables: np.ndarray, texts: Plaintexts, length: int, quick: bool) -> tuple[list, int, int | None]:
    rows: list[tuple] = []
    rng = np.random.default_rng([SEED, 1])
    auto_draws, reuse_draws = (2, 3) if quick else (AUTOKEY_DRAWS, REUSE_DRAWS)
    min_F = {}
    for lag in AUTOKEY_LAGS:
        lows = []
        for source in SOURCES:
            for rel in RELATIONS:
                vals = []
                for _ in range(auto_draws):
                    a = int(rng.integers(N))
                    c = autokey_encipher(texts.draw(source, length, rng), rel, a, rng, lag=lag)
                    vals.append(planted_F(c, tables, lag, rel, a))
                lows.append(min(vals))
                rows.append(("autokey", lag, "forward", rel, source, len(vals), f"{min(vals):.2f}",
                             f"{np.mean(vals):.2f}", f"{max(vals):.2f}", sum(v >= PASS for v in vals)))
        min_F[lag] = min(lows)
        log.info("autokey L=%-5d min F %.1f", lag, min_F[lag])
    p_max = 0
    for lag in AUTOKEY_LAGS:
        if min_F[lag] <= EXCLUDE:
            break
        p_max = lag
    m_min = None
    for m in REUSE_LENGTHS:
        all_found = True
        for orientation in ORIENTATIONS:
            for source in SOURCES:
                for rel in RELATIONS:
                    vals = []
                    for _ in range(reuse_draws):
                        a = int(rng.integers(N))
                        i, j = reuse_positions(length, m, rng)
                        c = autokey_encipher(texts.draw(source, length, rng), rel, a, rng, reuse=(orientation, i, j, m))
                        vals.append(planted_S(c, tables, orientation, i, j, m, rel, a))
                    found = sum(v >= PASS for v in vals)
                    all_found &= found == len(vals)
                    rows.append(("reuse", m, orientation, rel, source, len(vals), f"{min(vals):.2f}",
                                 f"{np.mean(vals):.2f}", f"{max(vals):.2f}", found))
        log.info("reuse M=%-4d every draw found: %s", m, all_found)
        if all_found and m_min is None:
            m_min = m
    return rows, p_max, m_min


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--quick", action="store_true", help="one null over a few lags, few controls, no LP2, no files")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    corpus = load_corpus()
    c_lp2 = lp2_stream(corpus)
    length = len(c_lp2)
    tables = score_tables(plaintext_model(corpus))
    rows, p_max, m_min = run_controls(tables, Plaintexts(corpus), length, args.quick)
    log.info("model check: P_max = %d, M_min = %s", p_max, m_min)

    lags = range(MIN_SEPARATION, length - MIN_SEPARATION + 1)
    sigmas = reverse_sigmas(length)
    rng = np.random.default_rng([SEED, 2])
    nulls = [anti_doublet(rng.integers(0, N, length), rng) for _ in range(NULL_STREAMS)]
    if args.quick:
        F, S_fwd, S_rev = full_scan((nulls[0], tables, lags[:300], sigmas[:600]))
        log.info("quick null (300 lags, 600 sigmas): max F %.2f, max S fwd %.2f, rev %.2f", F.max(), S_fwd.max(),
                 S_rev.max())
        log.info("quick run: LP2 not scored, nothing written")
        return 0

    jobs = [(c, tables, lags, sigmas) for c in [c_lp2, *nulls]]
    with ProcessPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(full_scan, jobs))
    valid = True
    for n, (F, S_fwd, S_rev) in enumerate(results[1:]):
        null_max = (float(F.max()), float(S_fwd.max()), float(S_rev.max()))
        valid &= max(null_max) < PASS
        log.info("null %d: max F %.2f, max S fwd %.2f, rev %.2f", n, *null_max)
    log.info("run %s", "VALID" if valid else "VOID")

    F, S_fwd, S_rev = results[0]
    trusted = np.array(lags) <= p_max
    excluded = (F <= EXCLUDE) & trusted[:, None, None]
    hypotheses = len(RELATIONS) * N
    lag_rows = []
    for n, L in enumerate(lags):
        best = np.unravel_index(np.argmax(F[n]), F[n].shape)
        lag_rows.append((L, length - L, f"{F[n, 0, 0]:.2f}", f"{F[n].max():.2f}", RELATIONS[best[0]], int(best[1]),
                         int(excluded[n].sum()), f"{S_fwd[n].max():.2f}"))
    top = []
    for kind, arr, index in (("F", F, lags), ("S-forward", S_fwd, lags), ("S-reverse", S_rev, sigmas)):
        for f in np.argsort(arr, axis=None)[::-1][:TOP]:
            n, r, a = np.unravel_index(f, arr.shape)
            top.append((kind, index[n], RELATIONS[r], int(a), f"{arr[n, r, a]:.2f}"))
    best = {"F": float(F.max()), "S-forward": float(S_fwd.max()), "S-reverse": float(S_rev.max())}
    verdict = "VOID" if not valid else ("PASS" if max(best.values()) >= PASS else "NO PASS")
    log.info("LP2 best: %s → %s", {k: round(v, 2) for k, v in best.items()}, verdict)
    log.info("excluded hypotheses: %d of %d trusted (L ≤ %d); plain autokey (diff, a = 0) excluded for %d of %d lags",
             int(excluded.sum()), int(trusted.sum()) * hypotheses, p_max, int(excluded[:, 0, 0].sum()),
             int(trusted.sum()))
    for lag in NAMED_LAGS:
        n = lag - MIN_SEPARATION
        log.info("named lag %d: F(diff, 0) %.2f; best F %.2f; excluded %d of %d", lag, F[n, 0, 0], F[n].max(),
                 int(excluded[n].sum()), hypotheses)
    write_tsv(LAGS_PATH, ("lag", "pairs", "F_diff0", "F_best", "best_rel", "best_a", f"excluded_of_{hypotheses}",
                          "S_fwd_best"), lag_rows)
    write_tsv(TOP_PATH, ("statistic", "lag_or_sigma", "relation", "a", "nats"), top)
    write_tsv(CONTROLS_PATH, ("kind", "L_or_M", "orientation", "relation", "source", "draws", "min", "mean", "max",
                              "at_least_30"), rows)
    log.info("wrote %s, %s and %s", LAGS_PATH.name, TOP_PATH.name, CONTROLS_PATH.name)
    return 0 if valid else 2


if __name__ == "__main__":
    sys.exit(main())
