"""Stage AC: key reuse at any lag, periods over 1,000 and reused key stretches (TODO.md, declared 2026-10-12 in b2f22d9
before this script existed; the "sumrev" relation was added before LP2 was scored, see below).

LP2 is read as one continuous stream c (segments 7–15, 12,956 runes). Positions i < j share a key value up to a relation:
- diff:   k_j = k_i + a  →  c_j − c_i = p_j − p_i + a
- sum:    k_j = a − k_i  →  c_j + c_i = p_j + p_i + a        (c = p + k or c = p − k)
- sumrev: k_j = a − k_i under Beaufort c = k − p  →  c_j + c_i = a − (p_j + p_i)
"sumrev" was added to the declared diff and sum before the runner was committed: under Beaufort the sum law is reflected,
which no shift a reproduces (the difference law is symmetric, so diff needs no twin).

Per pair the score is s = ln(29 · r(x)), where r is the law of the combination under the LP-English unigram model, so
E[e^s] = 1 for a flat cipher and E[e^−s] = 1 under the model.
- F(L, rel, a): Σ s over the whole forward diagonal j = i + L, L = 11…N − 11: a periodic key of period L.
  PASS iff F ≥ 30; excluded iff F ≤ −10, for L ≤ P_max (the model check).
- S: the maximum segment sum on every forward diagonal and every reverse anti-diagonal i + j = σ (j − i ≥ 11), for each
  (rel, a): one reused key stretch read forwards or backwards. PASS iff S ≥ 30.
- Valid iff 4 flat null streams with the anti-doublet rule give max F < 30 and max S < 30.
- P_max: the largest grid period such that every control draw at every grid period up to it has F > −10.
- M_min: the smallest grid length at which every reuse control draw in every cell has S ≥ 30 at its planted diagonal.

Deterministic. Usage: python -m tools.run_stage_ac [--quick]   (--quick scans a few lags of one null, scores no LP2 runes
and writes nothing)
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from tools.lpcore import detect, keys, stats
from tools.lpcore.corpus import REPO_ROOT, load_corpus
from tools.lpcore.gematria import N
from tools.lpcore.verify import load_translation
from tools.run_stage_x import write_tsv
from tools.run_stage_z import anti_doublet, emerson_words

log = logging.getLogger("stage_ac")

LAGS_PATH = REPO_ROOT / "reference" / "findings" / "stage_ac_lags.tsv"
TOP_PATH = REPO_ROOT / "reference" / "findings" / "stage_ac_top.tsv"
CONTROLS_PATH = REPO_ROOT / "reference" / "findings" / "stage_ac_controls.tsv"
RELATIONS = ("diff", "sum", "sumrev")
MIN_SEPARATION = 11
PASS = 30.0
EXCLUDE = -10.0
PERIODS = (1033, 1729, 3301, 5000, 7000, 9000, 10000, 11000, 11500, 12000, 12500)
NAMED_PERIODS = (1033, 1729, 3301)
REUSE_LENGTHS = (500, 1000, 1500, 2000, 2500, 3000)
ORIENTATIONS = ("forward", "reverse")
SOURCES = ("E", "L")
NULL_STREAMS = 4
PERIODIC_DRAWS = 10
REUSE_DRAWS = 25
KEEP = 0.19
SEED = 3301
TOP = 20


# ---- model --------------------------------------------------------------------------------------------------------

def plaintext_model(corpus=None) -> np.ndarray:
    corpus = corpus or load_corpus()
    words = keys.solved_plaintext_words(corpus, load_translation())
    return np.array(detect.unigram([r for w in words for r in w]))


def score_tables(q: np.ndarray) -> np.ndarray:
    """tables[rel, a, x] = ln(29 · P(combination = x | shift a)) for rel in RELATIONS."""
    diff = np.array([sum(q[p] * q[(p + d) % N] for p in range(N)) for d in range(N)])    # law of p_j − p_i
    total = np.array([sum(q[p] * q[(d - p) % N] for p in range(N)) for d in range(N)])  # law of p_j + p_i
    x = np.arange(N)
    out = np.empty((len(RELATIONS), N, N))
    for a in range(N):
        out[0, a] = np.log(N * diff[(x - a) % N])
        out[1, a] = np.log(N * total[(x - a) % N])
        out[2, a] = np.log(N * total[(a - x) % N])
    return out


def combine(ci: np.ndarray, cj: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """The observed combination per relation: (c_j − c_i, c_j + c_i, c_j + c_i)."""
    s = (cj + ci) % N
    return (cj - ci) % N, s, s


def segment_stats(table: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(F, S) per shift a: the total and the maximum contiguous segment sum of table[a, x]."""
    cs = np.zeros((N, len(x) + 1))
    np.cumsum(table[:, x], axis=1, out=cs[:, 1:])
    return cs[:, -1].copy(), (cs - np.minimum.accumulate(cs, axis=1)).max(axis=1)


def forward_scan(c: np.ndarray, tables: np.ndarray, lags: Sequence[int]) -> tuple[np.ndarray, np.ndarray]:
    """F and S of shape (len(lags), relations, 29) over forward diagonals."""
    F = np.empty((len(lags), len(RELATIONS), N))
    S = np.empty_like(F)
    for n, L in enumerate(lags):
        for r, x in enumerate(combine(c[:-L], c[L:])):
            F[n, r], S[n, r] = segment_stats(tables[r], x)
    return F, S


def reverse_pairs(sigma: int, length: int) -> tuple[np.ndarray, np.ndarray]:
    """Pairs (i, σ − i) with σ − 2i ≥ MIN_SEPARATION and σ − i < length, in increasing i."""
    i = np.arange(max(0, sigma - length + 1), (sigma - MIN_SEPARATION) // 2 + 1)
    return i, sigma - i


def reverse_sigmas(length: int) -> range:
    return range(MIN_SEPARATION, 2 * length - 2 - MIN_SEPARATION + 1)


def reverse_scan(c: np.ndarray, tables: np.ndarray, sigmas: Sequence[int]) -> np.ndarray:
    """S of shape (len(sigmas), relations, 29) over reverse anti-diagonals."""
    S = np.full((len(sigmas), len(RELATIONS), N), -np.inf)
    for n, sigma in enumerate(sigmas):
        i, j = reverse_pairs(sigma, len(c))
        if len(i) == 0:
            continue
        for r, x in enumerate(combine(c[i], c[j])):
            S[n, r] = segment_stats(tables[r], x)[1]
    return S


def full_scan(args: tuple[np.ndarray, np.ndarray, Sequence[int], Sequence[int]]):
    c, tables, lags, sigmas = args
    F, S_fwd = forward_scan(c, tables, lags)
    return F, S_fwd, reverse_scan(c, tables, sigmas)


# ---- controls -----------------------------------------------------------------------------------------------------

def related(k: np.ndarray, rel: str, a: int) -> np.ndarray:
    return (k + a) % N if rel == "diff" else (a - k) % N


def encipher(plain: Sequence[int], key: np.ndarray, rng: np.random.Generator, rel: str) -> np.ndarray:
    """c = p + k (sumrev: c = k − p, Beaufort) with the anti-doublet rule, re-keying fresh, key in step."""
    if rel == "sumrev":
        c = np.array(keys.encrypt_dodging([(-p) % N for p in plain], key.tolist(), keep=KEEP,
                                          seed=int(rng.integers(2 ** 31)), rekey="fresh"))
        return c
    return np.array(keys.encrypt_dodging(list(plain), key.tolist(), keep=KEEP, seed=int(rng.integers(2 ** 31)),
                                         rekey="fresh"))


def periodic_key(period: int, length: int, rel: str, a: int, rng: np.random.Generator) -> np.ndarray:
    """k_{t+P} = f(k_t): plain repetition for diff with a = 0, a progressive or reflected chain otherwise."""
    key = np.empty(length, dtype=np.int64)
    key[:period] = rng.integers(0, N, period)
    for start in range(period, length, period):
        block = key[start - period:start][:length - start]
        key[start:start + len(block)] = related(block, rel, a)
    return key


def reuse_key(length: int, m: int, orientation: str, rel: str, a: int,
              rng: np.random.Generator) -> tuple[np.ndarray, int, int]:
    """A random key with key[j:j+m] = f(key[i:i+m]) (forward) or f of it reversed (reverse); returns (key, i, j)."""
    key = rng.integers(0, N, length)
    i = int(rng.integers(0, length - 2 * m - MIN_SEPARATION))
    j = int(rng.integers(i + m + MIN_SEPARATION, length - m + 1))
    block = key[i:i + m] if orientation == "forward" else key[i:i + m][::-1]
    key[j:j + m] = related(block, rel, a)
    return key, i, j


def planted_F(c: np.ndarray, tables: np.ndarray, lag: int, rel: str, a: int) -> float:
    r = RELATIONS.index(rel)
    x = combine(c[:-lag], c[lag:])[r]
    return float(tables[r, a, x].sum())


def planted_S(c: np.ndarray, tables: np.ndarray, orientation: str, i: int, j: int, m: int, rel: str, a: int) -> float:
    r = RELATIONS.index(rel)
    if orientation == "forward":
        x = combine(c[:-(j - i)], c[j - i:])[r]
    else:
        ii, jj = reverse_pairs(i + m - 1 + j, len(c))
        x = combine(c[ii], c[jj])[r]
    return float(segment_stats(tables[r][a:a + 1], x)[1][0])


class Plaintexts:
    def __init__(self, corpus) -> None:
        self.emerson = [r for w in emerson_words() for r in w]
        self.words = keys.solved_plaintext_words(corpus, load_translation())

    def draw(self, source: str, length: int, rng: np.random.Generator) -> list[int]:
        if source == "E":
            start = int(rng.integers(0, len(self.emerson) - length))
            return self.emerson[start:start + length]
        out: list[int] = []
        while len(out) < length:
            out += [r for i in rng.permutation(len(self.words)) for r in self.words[i]]
        return out[:length]


def run_controls(tables: np.ndarray, texts: Plaintexts, length: int, quick: bool) -> tuple[list, int, int | None]:
    rows: list[tuple] = []
    rng = np.random.default_rng([SEED, 1])
    periodic_draws, reuse_draws = (2, 3) if quick else (PERIODIC_DRAWS, REUSE_DRAWS)
    min_F: dict[int, float] = {}
    for period in PERIODS:
        lows = []
        for source in SOURCES:
            for rel in RELATIONS:
                vals = []
                for _ in range(periodic_draws):
                    a = int(rng.integers(N))
                    c = encipher(texts.draw(source, length, rng), periodic_key(period, length, rel, a, rng), rng, rel)
                    vals.append(planted_F(c, tables, period, rel, a))
                lows.append(min(vals))
                rows.append(("periodic", period, "forward", rel, source, len(vals), f"{min(vals):.2f}",
                             f"{np.mean(vals):.2f}", f"{max(vals):.2f}", sum(v >= PASS for v in vals)))
        min_F[period] = min(lows)
        log.info("periodic P=%-5d min F %.1f", period, min_F[period])
    p_max = 0
    for period in PERIODS:
        if min_F[period] <= EXCLUDE:
            break
        p_max = period
    m_min = None
    for m in REUSE_LENGTHS:
        all_found = True
        for orientation in ORIENTATIONS:
            for source in SOURCES:
                for rel in RELATIONS:
                    vals = []
                    for _ in range(reuse_draws):
                        a = int(rng.integers(N))
                        key, i, j = reuse_key(length, m, orientation, rel, a, rng)
                        c = encipher(texts.draw(source, length, rng), key, rng, rel)
                        vals.append(planted_S(c, tables, orientation, i, j, m, rel, a))
                    found = sum(v >= PASS for v in vals)
                    all_found &= found == len(vals)
                    rows.append(("reuse", m, orientation, rel, source, len(vals), f"{min(vals):.2f}",
                                 f"{np.mean(vals):.2f}", f"{max(vals):.2f}", found))
        log.info("reuse M=%-4d every draw found: %s", m, all_found)
        if all_found and m_min is None:
            m_min = m
    return rows, p_max, m_min


# ---- main ---------------------------------------------------------------------------------------------------------

def lp2_stream(corpus) -> np.ndarray:
    return np.array([r for s in stats.UNSOLVED_SEGMENTS for r in corpus.segment_runes(s)], dtype=np.int64)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--quick", action="store_true", help="one null over a few lags, few controls, no LP2, no files")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    corpus = load_corpus()
    c_lp2 = lp2_stream(corpus)
    length = len(c_lp2)
    tables = score_tables(plaintext_model(corpus))
    log.info("LP2 stream: %d runes; KL per pair under the model: %s", length,
             {rel: round(float(np.sum(np.exp(tables[r, 0]) / N * tables[r, 0])), 4) for r, rel in enumerate(RELATIONS)})

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
    with ProcessPoolExecutor(max_workers=min(4, len(jobs))) as pool:
        results = list(pool.map(full_scan, jobs))
    valid = True
    for n, (F, S_fwd, S_rev) in enumerate(results[1:]):
        null_max = (float(F.max()), float(S_fwd.max()), float(S_rev.max()))
        valid &= max(null_max) < PASS
        log.info("null %d: max F %.2f, max S fwd %.2f, rev %.2f", n, *null_max)
    log.info("run %s", "VALID" if valid else "VOID")

    F, S_fwd, S_rev = results[0]
    lag_arr = np.array(lags)
    trusted = lag_arr <= p_max
    excluded = (F <= EXCLUDE) & trusted[:, None, None]
    lag_rows = []
    for n, L in enumerate(lags):
        best = np.unravel_index(np.argmax(F[n]), F[n].shape)
        lag_rows.append((L, length - L, f"{F[n, 0, 0]:.2f}", f"{F[n].max():.2f}", RELATIONS[best[0]], int(best[1]),
                         int(excluded[n].sum()), f"{S_fwd[n].max():.2f}"))
    top = []
    for kind, arr, index in (("F", F, lags), ("S-forward", S_fwd, lags), ("S-reverse", S_rev, sigmas)):
        flat = np.argsort(arr, axis=None)[::-1][:TOP]
        for f in flat:
            n, r, a = np.unravel_index(f, arr.shape)
            top.append((kind, index[n], RELATIONS[r], int(a), f"{arr[n, r, a]:.2f}"))
    best = {"F": float(F.max()), "S-forward": float(S_fwd.max()), "S-reverse": float(S_rev.max())}
    verdict = "VOID" if not valid else ("PASS" if max(best.values()) >= PASS else "NO PASS")
    log.info("LP2 best: %s → %s", {k: round(v, 2) for k, v in best.items()}, verdict)
    log.info("excluded hypotheses: %d of %d trusted (L ≤ %d); plain periodic (diff, a = 0) excluded for %d of %d lags",
             int(excluded.sum()), int(trusted.sum()) * len(RELATIONS) * N, p_max, int(excluded[:, 0, 0].sum()),
             int(trusted.sum()))
    for period in NAMED_PERIODS:
        n = period - MIN_SEPARATION
        log.info("named period %d: F(diff, 0) %.2f; best F %.2f; excluded %d of %d", period, F[n, 0, 0], F[n].max(),
                 int(excluded[n].sum()), len(RELATIONS) * N)
    write_tsv(LAGS_PATH, ("lag", "pairs", "F_diff0", "F_best", "best_rel", "best_a", "excluded_of_87", "S_fwd_best"),
              lag_rows)
    write_tsv(TOP_PATH, ("statistic", "lag_or_sigma", "relation", "a", "nats"), top)
    write_tsv(CONTROLS_PATH, ("kind", "P_or_M", "orientation", "relation", "source", "draws", "min", "mean", "max",
                              "at_least_30"), rows)
    log.info("wrote %s, %s and %s", LAGS_PATH.name, TOP_PATH.name, CONTROLS_PATH.name)
    return 0 if valid else 2


if __name__ == "__main__":
    sys.exit(main())
