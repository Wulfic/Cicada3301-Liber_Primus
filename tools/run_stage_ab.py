"""Stage AB: a key that restarts at every section, paragraph, clause, line or page (TODO.md, declared 2026-10-12 in
78f7c37 before this script existed).

If the key (or the alphabet σ_t) restarts at each unit's first rune, every unit uses the same σ_t at in-unit position
t. Equal plaintext at equal t then gives equal cipher, under any alphabets. Statistic, label-free:
K_u = Σ_t Σ_v C(m_{t,v}, 2), the pairs of units of type u that agree at the same in-unit position.

Declared rule, per unit type:
- lower = exp(m − 5s) − 1 over ln(K + 1) for a source's positive draws (stage Z's bound). Testable iff, for both
  sources, lower > null max and every draw > null max. Excluded iff testable and K_LP2 < lower for both sources.
- PASS iff K_LP2 > null max and (K_LP2 − μ0)/σ0 ≥ 6, σ0 floored at 1.
- Valid iff each null mean lies within 3 s.e. of the analytic Σ_t C(m_t, 2)/29; otherwise every row is VOID.

Deterministic. Usage: python -m tools.run_stage_ab [--quick]   (--quick scores no LP2 runes and writes nothing)
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections import Counter
from collections.abc import Sequence
from math import comb

import numpy as np

from tools.lpcore import keys, stats
from tools.lpcore.corpus import REPO_ROOT, Corpus, load_corpus
from tools.lpcore.gematria import N
from tools.lpcore.verify import load_translation
from tools.run_stage_x import write_tsv
from tools.run_stage_z import anti_doublet, emerson_words, fill_sections, log_lower, summarise

log = logging.getLogger("stage_ab")

RESULTS_PATH = REPO_ROOT / "reference" / "findings" / "stage_ab_results.tsv"
CONTROLS_PATH = REPO_ROOT / "reference" / "findings" / "stage_ab_controls.tsv"
UNITS = ("segment", "paragraph", "clause", "line", "page")
SOURCES = ("E", "L")
NULL_DRAWS = 1_000
POSITIVE_DRAWS = 200
SEED = 3301
PASS_Z = 6.0
VALIDITY_SE = 3.0


class Layout:
    """LP2's runes with, per unit type, each rune's in-unit position, and the section boundaries for the rule."""

    def __init__(self, corpus: Corpus) -> None:
        units = corpus.rune_units()
        keep = [i for i, s in enumerate(units["segment"]) if s in stats.UNSOLVED_SEGMENTS]
        self.runes = np.array([units["rune"][i] for i in keep], dtype=np.int64)
        self.positions: dict[str, np.ndarray] = {}
        self.unit_lengths: dict[str, list[int]] = {}
        for u in UNITS:
            ids = [units[u][i] for i in keep]
            pos, lengths = [], []
            for i, x in enumerate(ids):
                if i == 0 or x != ids[i - 1]:
                    lengths.append(0)
                pos.append(lengths[-1])
                lengths[-1] += 1
            if len(lengths) != len(set(ids)):
                raise ValueError(f"{u} units are not contiguous in LP2")
            self.positions[u] = np.array(pos, dtype=np.int64)
            self.unit_lengths[u] = lengths
        self.section_sizes = self.unit_lengths["segment"]

    def __len__(self) -> int:
        return len(self.runes)


def agreements(cipher: np.ndarray, positions: np.ndarray) -> int:
    """K = Σ_t Σ_v C(m_{t,v}, 2): pairs of units with the same rune at the same in-unit position."""
    counts = np.bincount(positions * N + cipher)
    return int((counts * (counts - 1) // 2).sum())


def analytic_mean(lengths: Sequence[int]) -> float:
    """Σ_t C(m_t, 2)/29, where m_t is the number of units longer than t (flat iid null)."""
    m = np.bincount(np.concatenate([np.arange(n) for n in lengths]))
    return sum(comb(int(k), 2) for k in m) / N


def with_rule(stream: np.ndarray, section_sizes: Sequence[int], rng: np.random.Generator) -> np.ndarray:
    """Stage Z's anti-doublet rule, applied within each section's continuous stream."""
    cuts = np.cumsum(section_sizes)[:-1]
    return np.concatenate([anti_doublet(s, rng) for s in np.split(stream, cuts)])


def restart_encipher(plain: np.ndarray, positions: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """c = σ_t(p), one fresh random alphabet per in-unit position t, shared by every unit."""
    alphabets = np.argsort(rng.random((int(positions.max()) + 1, N)), axis=1)
    return alphabets[positions, plain]


def plaintext(words: Sequence[tuple[int, ...]], length: int, rng: np.random.Generator, contiguous: bool) -> np.ndarray:
    sec = fill_sections(words, [length], rng, contiguous)[0]
    return np.array([r for w in sec for r in w], dtype=np.int64)


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
    layout = Layout(corpus)
    log.info("LP2: %d runes; units %s", len(layout), {u: len(v) for u, v in layout.unit_lengths.items()})
    sources = {"E": (emerson_words(), True),
               "L": (keys.solved_plaintext_words(corpus, load_translation()), False)}

    rng = np.random.default_rng(SEED)
    null_values: dict[str, list[int]] = {u: [] for u in UNITS}
    for _ in range(null_draws):
        flat = with_rule(rng.integers(0, N, len(layout)), layout.section_sizes, rng)
        for u in UNITS:
            null_values[u].append(agreements(flat, layout.positions[u]))

    valid, control_rows, rows = True, [], []
    for u in UNITS:
        mu0, sd0, null_max = summarise(null_values[u])
        expected = analytic_mean(layout.unit_lengths[u])
        ok = abs(mu0 - expected) <= VALIDITY_SE * sd0 / np.sqrt(null_draws)
        valid &= ok
        lower, minimum = {}, {}
        for name in SOURCES:
            words, contiguous = sources[name]
            crng = np.random.default_rng([SEED, UNITS.index(u), SOURCES.index(name)])
            ks = []
            for _ in range(pos_draws):
                plain = plaintext(words, len(layout), crng, contiguous)
                cipher = with_rule(restart_encipher(plain, layout.positions[u], crng), layout.section_sizes, crng)
                ks.append(agreements(cipher, layout.positions[u]))
            mu, sd, _ = summarise(ks)
            lower[name], minimum[name] = log_lower(ks), min(ks)
            control_rows.append((u, name, pos_draws, f"{mu:.2f}", f"{sd:.2f}", min(ks), max(ks), f"{lower[name]:.2f}"))
        log.info("%-9s null %.2f ± %.2f (max %d), analytic %.2f%s | E low %.1f (min %d) | L low %.1f (min %d)", u, mu0,
                 sd0, null_max, expected, "" if ok else " MISMATCH", lower["E"], minimum["E"], lower["L"], minimum["L"])
        if args.quick:
            continue
        k = agreements(layout.runes, layout.positions[u])
        v, z0 = verdict(k, mu0, sd0, null_max, lower, minimum)
        rows.append((u, len(layout.unit_lengths[u]), k, f"{mu0:.3f}", f"{sd0:.3f}", null_max, f"{expected:.3f}",
                     f"{lower['E']:.2f}", f"{lower['L']:.2f}", f"{z0:.2f}", v))

    log.info("run %s", "VALID" if valid else "VOID")
    if args.quick:
        log.info("quick run: LP2 not scored, nothing written")
        return 0 if valid else 2
    if not valid:
        rows = [(*row[:-1], "VOID") for row in rows]
    for row in rows:
        log.info("%s", row)
    log.info("verdicts: %s", dict(Counter(row[-1] for row in rows)))
    write_tsv(RESULTS_PATH, ("unit", "units", "K_LP2", "null_mean", "null_sd", "null_max", "analytic_mean", "E_lower",
                             "L_lower", "z_null", "verdict"), rows)
    write_tsv(CONTROLS_PATH, ("unit", "source", "draws", "mean", "sd", "min", "max", "log_lower_5sd"), control_rows)
    log.info("wrote %s and %s", RESULTS_PATH.name, CONTROLS_PATH.name)
    return 0 if valid else 2


if __name__ == "__main__":
    sys.exit(main())
