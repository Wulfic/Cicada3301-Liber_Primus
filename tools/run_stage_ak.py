"""Stage AK: label coincidences (TODO.md, declared 2026-11-14 in 59c5b56 before this script existed).

K_u = Σ over (class, rune) of C(n, 2): pairs of positions with the same label u and the same rune. If the alphabet at
position i is any function of u(i), each class is a monoalphabetic sample and K_u rises to about 1.79 × its null.
307 labels: two-rune ciphertext contexts (c_{i−a}, c_{i−b}), 1 ≤ a < b ≤ 12; the three-rune context (1, 2, 3); and
six unit types × L = 1…40, each unit with its own period-L key (class = unit × i mod L).

Null: 1,000 seeded streams of iid runes from LP2's unigram with stage Z's anti-doublet rule (keep 0.19) per segment.
Fires: z ≥ 5 and above every null value. Testable: the positive control fires in ≥ 18 / 20. Excluded: testable,
not firing, and K ≤ mean₊ − 5·sd₊. Void if the negative control fires more than once or < half the labels are testable.

Deterministic. Usage: python -m tools.run_stage_ak [--quick]   (--quick: 200 null streams, controls only, nothing written)
"""

from __future__ import annotations

import argparse
import logging
import random
import sys
from dataclasses import dataclass

import numpy as np

from tools.lpcore.corpus import REPO_ROOT, Corpus, load_corpus
from tools.lpcore.gematria import N
from tools.lpcore.stats import UNSOLVED_SEGMENTS
from tools.run_stage_ab import plaintext, with_rule
from tools.run_stage_x import write_tsv
from tools.run_stage_z import KEEP, emerson_words

log = logging.getLogger("stage_ak")

RESULTS_PATH = REPO_ROOT / "reference" / "findings" / "stage_ak_labels.tsv"
CONTROLS_PATH = REPO_ROOT / "reference" / "findings" / "stage_ak_negative.tsv"
SEED = 3301
N_NULL = 1_000
N_NULL_QUICK = 200
N_POS = 20
N_NEG = 20
Z_FIRE = 5.0
POS_REQUIRED = 18
EXCLUDE_SD = 5.0
NEG_MAX_FIRES = 1
MAX_LAG = 12
MAX_PERIOD = 40
UNITS = ("section", "paragraph", "clause", "line", "page", "stretch")


@dataclass(frozen=True)
class Label:
    family: str                # "context" or a unit name
    name: str
    lags: tuple[int, ...] = ()  # context labels
    period: int = 0             # unit labels


def labels() -> list[Label]:
    out = [Label("context", f"c[i-{a}],c[i-{b}]", (a, b)) for a in range(1, MAX_LAG + 1)
           for b in range(a + 1, MAX_LAG + 1)]
    out.append(Label("context", "c[i-1],c[i-2],c[i-3]", (1, 2, 3)))
    out += [Label(u, f"{u} x i mod {L}", period=L) for u in UNITS for L in range(1, MAX_PERIOD + 1)]
    return out


@dataclass(frozen=True)
class Layout:
    """LP2's stream (segments 7–15 in order) with what every label needs that does not depend on the runes."""
    runes: np.ndarray          # LP2's ciphertext
    seg_pos: np.ndarray        # offset of each rune in its segment
    seg_sizes: tuple[int, ...]
    units: dict[str, np.ndarray]   # unit id per rune, units cut at segment ends


def factorize(*cols: np.ndarray) -> np.ndarray:
    _, ids = np.unique(np.stack(cols, axis=1), axis=0, return_inverse=True)
    return ids.ravel()


def build_layout(corpus: Corpus) -> Layout:
    all_units = corpus.rune_units()
    idx, seg_ids, seg_pos, sizes = [], [], [], []
    for seg in UNSOLVED_SEGMENTS:
        words = corpus.rune_words(seg)
        n = sum(len(w.runes) for w in words)
        start = words[0].rune_offset
        idx.extend(range(start, start + n))
        seg_ids += [seg] * n
        seg_pos.extend(range(n))
        sizes.append(n)
    idx_a = np.array(idx)
    runes = np.array(all_units["rune"])[idx_a]
    segment = np.array(seg_ids)
    for s, size in zip(UNSOLVED_SEGMENTS, sizes):
        if not np.array_equal(runes[segment == s], corpus.segment_runes(s)):
            raise ValueError(f"segment {s}: layout runes differ from segment_runes")
    pos = np.array(seg_pos)
    doublet_second = np.r_[False, (runes[1:] == runes[:-1]) & (pos[1:] > 0)]
    stretch = np.cumsum(doublet_second | (pos == 0))
    units = {"section": factorize(segment), "stretch": stretch}
    for u in ("paragraph", "clause", "line", "page"):
        units[u] = factorize(segment, np.array(all_units[u])[idx_a])
    return Layout(runes, pos, tuple(sizes), units)


def coincidences(codes: np.ndarray, runes: np.ndarray) -> int:
    """Σ C(n, 2) over (code, rune) cells; codes < 0 are unlabelled."""
    ok = codes >= 0
    counts = np.bincount(codes[ok] * N + runes[ok])
    return int((counts * (counts - 1) // 2).sum())


def context_codes(c: np.ndarray, seg_pos: np.ndarray, lags: tuple[int, ...]) -> np.ndarray:
    code = np.zeros(len(c), dtype=np.int64)
    for lag in lags:
        code = code * N + np.roll(c, lag)
    return np.where(seg_pos >= max(lags), code, -1)


def all_k(c: np.ndarray, layout: Layout, labs: list[Label]) -> np.ndarray:
    i = np.arange(len(c))
    out = np.empty(len(labs))
    for j, lab in enumerate(labs):
        if lab.family == "context":
            codes = context_codes(c, layout.seg_pos, lab.lags)
        else:
            codes = layout.units[lab.family] * lab.period + i % lab.period
        out[j] = coincidences(codes, c)
    return out


def null_stream(layout: Layout, freq: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    return with_rule(rng.choice(N, size=len(layout.runes), p=freq), layout.seg_sizes, rng)


def english(layout: Layout, words: list[tuple[int, ...]], rng: np.random.Generator) -> np.ndarray:
    return plaintext(words, len(layout.runes), rng, contiguous=True)


def chain_encipher(p: np.ndarray, seg_pos: np.ndarray, lags: tuple[int, ...], rng: np.random.Generator) -> np.ndarray:
    """c_i = p_i + f(c_{i−lags}) with a random table f, left to right; a would-be doublet is re-keyed w.p. 1 − KEEP."""
    table = rng.integers(N, size=N ** len(lags)).tolist()
    r = random.Random(int(rng.integers(2 ** 63)))
    pl, sp, c = p.tolist(), seg_pos.tolist(), [0] * len(p)
    top = max(lags)
    for i in range(len(pl)):
        if sp[i] >= top:
            code = 0
            for lag in lags:
                code = code * N + c[i - lag]
            v = (pl[i] + table[code]) % N
        else:
            v = (pl[i] + r.randrange(N)) % N
        if sp[i] > 0 and v == c[i - 1] and r.random() >= KEEP:
            v = (v + r.randrange(1, N)) % N
        c[i] = v
    return np.array(c, dtype=np.int64)


def unit_encipher(p: np.ndarray, layout: Layout, lab: Label, rng: np.random.Generator) -> np.ndarray:
    unit = layout.units[lab.family]
    key = rng.integers(N, size=(int(unit.max()) + 1, lab.period))
    c = (p + key[unit, np.arange(len(p)) % lab.period]) % N
    return with_rule(c, layout.seg_sizes, rng)


def positive_k(layout: Layout, lab: Label, words: list[tuple[int, ...]], rng: np.random.Generator) -> np.ndarray:
    """K of `lab` on N_POS English streams enciphered under that label's own model."""
    ks = []
    for _ in range(N_POS):
        p = english(layout, words, rng)
        if lab.family == "context":
            c = chain_encipher(p, layout.seg_pos, lab.lags, rng)
        else:
            c = unit_encipher(p, layout, lab, rng)
        ks.append(all_k(c, layout, [lab])[0])
    return np.array(ks)


def zscore(k: np.ndarray, mu: np.ndarray, sd: np.ndarray) -> np.ndarray:
    """(k − μ₀) / σ₀, and NaN for a label whose null never varies (no position pairs share a class)."""
    diff = np.broadcast_to(k - mu, np.broadcast_shapes(np.shape(k), np.shape(sd)))
    return np.divide(diff, sd, out=np.full(diff.shape, np.nan), where=sd > 0)


def fires(k: np.ndarray, mu: np.ndarray, sd: np.ndarray, null_max: np.ndarray) -> np.ndarray:
    z = zscore(k, mu, sd)
    return np.where(np.isnan(z), False, z >= Z_FIRE) & (k > null_max)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--quick", action="store_true", help="200 null streams, controls only, nothing written")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    layout = build_layout(load_corpus())
    labs = labels()
    log.info("%d runes in %d segments; %d labels; units: %s", len(layout.runes), len(layout.seg_sizes), len(labs),
             {u: int(v.max()) + 1 for u, v in layout.units.items()})
    freq = np.bincount(layout.runes, minlength=N) / len(layout.runes)
    rng = np.random.default_rng(SEED)

    n_null = N_NULL_QUICK if args.quick else N_NULL
    null = np.empty((n_null, len(labs)))
    for s in range(n_null):
        null[s] = all_k(null_stream(layout, freq, rng), layout, labs)
        if (s + 1) % 100 == 0:
            log.info("null streams: %d / %d", s + 1, n_null)
    mu, sd, null_max = null.mean(axis=0), null.std(axis=0, ddof=1), null.max(axis=0)

    words = emerson_words()
    neg = np.array([all_k(with_rule((english(layout, words, rng) + rng.integers(N, size=len(layout.runes))) % N,
                                    layout.seg_sizes, rng), layout, labs) for _ in range(N_NEG)])
    neg_fires = fires(neg, mu, sd, null_max)
    no_pairs = sd == 0
    log.info("labels with no pairs in any null stream: %d (%s)", int(no_pairs.sum()),
             ", ".join(lab.name for lab, z0 in zip(labs, no_pairs) if z0) or "none")
    log.info("negative control: %d fires in %d x %d; max z %.2f", int(neg_fires.sum()), N_NEG, len(labs),
             float(np.nanmax(zscore(neg, mu, sd))))

    pos = np.empty((N_POS, len(labs)))
    for j, lab in enumerate(labs):
        pos[:, j] = positive_k(layout, lab, words, rng)
    pos_fires = fires(pos, mu, sd, null_max).sum(axis=0)
    pos_mean, pos_sd = pos.mean(axis=0), pos.std(axis=0, ddof=1)
    testable = pos_fires >= POS_REQUIRED
    log.info("testable: %d / %d labels", int(testable.sum()), len(labs))
    for fam in ("context",) + UNITS:
        cols = [j for j, lab in enumerate(labs) if lab.family == fam]
        zp = zscore(pos_mean, mu, sd)[cols]
        log.info("  %-9s testable %3d / %3d; positive mean z %.1f to %.1f", fam, int(testable[cols].sum()), len(cols),
                 float(np.nanmin(zp)), float(np.nanmax(zp)))

    void = []
    if neg_fires.sum() > NEG_MAX_FIRES:
        void.append(f"negative control fired {int(neg_fires.sum())} times")
    if testable.sum() < len(labs) / 2:
        void.append(f"only {int(testable.sum())} of {len(labs)} labels testable")
    if void:
        log.error("stage void: %s; LP2 not scored", "; ".join(void))
        return 1
    if args.quick:
        log.info("quick run: LP2 not scored, nothing written")
        return 0

    k = all_k(layout.runes, layout, labs)
    z = zscore(k, mu, sd)
    fire = fires(k, mu, sd, null_max)
    excluded = testable & ~fire & (k <= pos_mean - EXCLUDE_SD * pos_sd)
    rows = []
    for j, lab in enumerate(labs):
        status = "FIRES" if fire[j] else ("no pairs" if no_pairs[j] else "untestable" if not testable[j] else
                                          ("excluded" if excluded[j] else "not excluded"))
        rows.append((lab.family, lab.name, int(k[j]), round(float(mu[j]), 2), round(float(sd[j]), 3), int(null_max[j]),
                     round(float(z[j]), 3), round(float(pos_mean[j]), 1), round(float(pos_sd[j]), 2), int(pos_fires[j]),
                     status))
    write_tsv(RESULTS_PATH, ("family", "label", "K", "null_mean", "null_sd", "null_max", "z", "pos_mean", "pos_sd",
                             "pos_fires_of_20", "status"), rows)
    write_tsv(CONTROLS_PATH, ("draw",) + tuple(lab.name for lab in labs),
              [(d,) + tuple(round(float(x), 3) for x in zscore(neg[d], mu, sd)) for d in range(N_NEG)])
    best = int(np.nanargmax(z))
    log.info("LP2: %d fire, %d excluded, %d not excluded, %d untestable; max z %.2f (%s), min z %.2f",
             int(fire.sum()), int(excluded.sum()), int((testable & ~fire & ~excluded).sum()), int((~testable).sum()),
             float(z[best]), labs[best].name, float(np.nanmin(z)))
    for j in np.flatnonzero(fire):
        log.info("  FIRES %s: K %d, z %.2f", labs[j].name, int(k[j]), float(z[j]))
    log.info("wrote %s and %s", RESULTS_PATH.name, CONTROLS_PATH.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
