"""Stage AF: a key restarting at every unit with a per-unit shift (TODO.md, declared 2026-10-12 in e2e305f before this
script existed).

c_U[t] = p_U[t] + k[t] + a_U (or Beaufort k[t] + a_U − p_U[t]) at in-unit position t of unit U. The within-unit difference
δ_U(t, t′) = c_U[t′] − c_U[t] cancels a_U, so two units agree on it exactly when their plaintext differences agree.
Statistic: S_u = Σ_{t < t′, 2 ≤ t′ − t ≤ 300} Σ_v C(m_{t,t′,v}, 2), with m_{t,t′,v} the units of type u whose δ(t, t′) is v.

Declared rule, per unit type (stage AB's units and rule):
- lower = exp(m − 5s) − 1 over ln(S + 1) per source. Testable iff, for both sources, lower > null max and every draw >
  null max. Excluded iff testable and S_LP2 < lower for both sources.
- PASS iff S_LP2 > null max and (S_LP2 − μ0)/σ0 ≥ 6.
- Valid iff every null mean lies within 3 s.e. of Σ C(m_{t,t′}, 2) / 29.

Deterministic. Usage: python -m tools.run_stage_af [--quick]   (--quick: 20 nulls, 10 controls, no LP2, no files)
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections import Counter
from collections.abc import Sequence

import numpy as np

from tools.lpcore import keys
from tools.lpcore.corpus import REPO_ROOT, load_corpus
from tools.lpcore.gematria import N
from tools.lpcore.verify import load_translation
from tools.run_stage_ab import SOURCES, UNITS, Layout, plaintext, verdict, with_rule
from tools.run_stage_x import write_tsv
from tools.run_stage_z import emerson_words, log_lower, summarise

log = logging.getLogger("stage_af")

RESULTS_PATH = REPO_ROOT / "reference" / "findings" / "stage_af_results.tsv"
CONTROLS_PATH = REPO_ROOT / "reference" / "findings" / "stage_af_controls.tsv"
MIN_GAP = 2
MAX_GAP = 300
NULL_DRAWS = 200
POSITIVE_DRAWS = 100
SEED = 3301
VALIDITY_SE = 3.0


def unit_matrix(cipher: np.ndarray, positions: np.ndarray) -> np.ndarray:
    """Runes laid out as (unit, in-unit position), −1 where a unit is shorter."""
    unit = np.cumsum(positions == 0) - 1
    out = np.full((int(unit.max()) + 1, int(positions.max()) + 1), -1, dtype=np.int64)
    out[unit, positions] = cipher
    return out


def difference_agreements(cipher: np.ndarray, positions: np.ndarray, max_gap: int = MAX_GAP) -> int:
    """S = pairs of units with equal within-unit difference c[t + g] − c[t], summed over t and 2 ≤ g ≤ max_gap."""
    m = unit_matrix(cipher, positions)
    width = m.shape[1]
    total = 0
    for g in range(MIN_GAP, min(max_gap, width - 1) + 1):
        a, b = m[:, :-g], m[:, g:]
        valid = (a >= 0) & (b >= 0)
        cols = np.broadcast_to(np.arange(width - g), a.shape)
        counts = np.bincount(cols[valid] * N + (b - a)[valid] % N)
        total += int((counts * (counts - 1) // 2).sum())
    return total


def analytic_mean(lengths: Sequence[int], max_gap: int = MAX_GAP) -> float:
    """Σ over position pairs (t, t + g) of C(units holding both, 2) / 29: flat iid null."""
    longer = np.array([sum(1 for n in lengths if n > x) for x in range(max(lengths) + 1)])  # units longer than x
    width = max(lengths)
    total = 0.0
    for g in range(MIN_GAP, min(max_gap, width - 1) + 1):
        m = longer[g:width]                 # position pair (t, t + g) is held by units longer than t + g
        total += float((m * (m - 1) // 2).sum())
    return total / N


def shifted_restart(plain: np.ndarray, positions: np.ndarray, beaufort: bool, rng: np.random.Generator) -> np.ndarray:
    """c = p + k[t] + a_U, or Beaufort k[t] + a_U − p: one key per in-unit position, one shift per unit."""
    unit = np.cumsum(positions == 0) - 1
    k = rng.integers(0, N, int(positions.max()) + 1)[positions]
    a = rng.integers(0, N, int(unit.max()) + 1)[unit]
    return ((k + a - plain) if beaufort else (plain + k + a)) % N


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--quick", action="store_true", help="20 nulls and 10 controls per source; no LP2, no files")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    null_draws, pos_draws = (20, 10) if args.quick else (NULL_DRAWS, POSITIVE_DRAWS)

    corpus = load_corpus()
    layout = Layout(corpus)
    sources = {"E": (emerson_words(), True),
               "L": (keys.solved_plaintext_words(corpus, load_translation()), False)}
    rng = np.random.default_rng(SEED)
    null_values: dict[str, list[int]] = {u: [] for u in UNITS}
    for _ in range(null_draws):
        flat = with_rule(rng.integers(0, N, len(layout)), layout.section_sizes, rng)
        for u in UNITS:
            null_values[u].append(difference_agreements(flat, layout.positions[u]))
    log.info("nulls done (%d draws)", null_draws)

    valid, rows, control_rows = True, [], []
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
            for d in range(pos_draws):
                plain = plaintext(words, len(layout), crng, contiguous)
                cipher = shifted_restart(plain, layout.positions[u], d % 2 == 1, crng)
                ks.append(difference_agreements(with_rule(cipher, layout.section_sizes, crng), layout.positions[u]))
            mu, sd, _ = summarise(ks)
            lower[name], minimum[name] = log_lower(ks), min(ks)
            control_rows.append((u, name, pos_draws, f"{mu:.2f}", f"{sd:.2f}", min(ks), max(ks), f"{lower[name]:.2f}"))
        log.info("%-9s null %.1f ± %.1f (max %d), analytic %.1f%s | E low %.1f (min %d) | L low %.1f (min %d)", u, mu0,
                 sd0, null_max, expected, "" if ok else " MISMATCH", lower["E"], minimum["E"], lower["L"], minimum["L"])
        if args.quick:
            continue
        s = difference_agreements(layout.runes, layout.positions[u])
        v, z0 = verdict(s, mu0, sd0, null_max, lower, minimum)
        rows.append((u, len(layout.unit_lengths[u]), s, f"{mu0:.3f}", f"{sd0:.3f}", null_max, f"{expected:.3f}",
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
    write_tsv(RESULTS_PATH, ("unit", "units", "S_LP2", "null_mean", "null_sd", "null_max", "analytic_mean", "E_lower",
                             "L_lower", "z_null", "verdict"), rows)
    write_tsv(CONTROLS_PATH, ("unit", "source", "draws", "mean", "sd", "min", "max", "log_lower_5sd"), control_rows)
    log.info("wrote %s and %s", RESULTS_PATH.name, CONTROLS_PATH.name)
    return 0 if valid else 2


if __name__ == "__main__":
    sys.exit(main())
