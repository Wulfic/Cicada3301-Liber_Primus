"""Stage T: the flatness bound on per-position alphabets c_i = σ_{k_i}(p_i) with random σ (TODO.md, declared
2026-10-01 in f0c8e39 before this script first ran).

Validity gates run first on synthetic ciphers (the solved plaintext's words in random order, a random σ per class,
`alphabets.encrypt_alphabets` with keep 0.19). Gate A: mean χ² within 15 % of 28 + λ̄ at V = 29, 256, 1024.
Gate B: at V = 1024, the pooled P under the true V is ≤ 1e-4 for none of 200 ciphers and ≤ 0.05 for at most 10 %.
If a gate fails the run is VOID and stops before the LP2 per-section statistic is computed.

Then LP2: the pooled χ² (one tabula) and Σ of per-section χ² over sections 7–9 and 11–15 (a fresh tabula per section).
A model with V effective classes is excluded if P ≤ 1e-4. Rows go to stage_t_results.tsv.

Deterministic. Usage: python -m tools.run_stage_t [--quick]
"""

from __future__ import annotations

import argparse
import logging
import random
import sys
from collections.abc import Sequence

import numpy as np

from tools.lpcore import alphabets, flatness, keys, stats
from tools.lpcore.corpus import REPO_ROOT, load_corpus
from tools.run_stage_s import LP2_RUNES, PLAIN, PRIME_PHASES, control_text, family

log = logging.getLogger("stage_t")

OUT_PATH = REPO_ROOT / "reference" / "findings" / "stage_t_results.tsv"
ALPHA = 1e-4
KEEP = 0.19
GATE_A_V = (29, 256, 1024)
GATE_A_TOLERANCE = 0.15
GATE_B_V = 1024
GATE_B_MAX_AT_05 = 0.10
CIPHERS = 200
SECTIONS = (7, 8, 9, 11, 12, 13, 14, 15)          # segment 10 (9 runes) left out, as declared
MC_TRIALS = 2_000_000
SEED = 3301
S = flatness.coincidence(PLAIN)


def synthetic(v: int, sizes: Sequence[int], seed: int) -> list[list[int]]:
    """One cipher per size from word-shuffled solved plaintext, iid uniform keys over v classes, a fresh tabula each."""
    rng = random.Random(seed)
    out = []
    for size in sizes:
        plain = control_text(size, rng)
        key = [rng.randrange(v) for _ in range(size)]
        out.append(alphabets.encrypt_alphabets(plain, key, keep=KEEP, seed=rng.randrange(2**31)))
    return out


def pooled(v: int, count: int, seed: int) -> list[tuple[float, float]]:
    """(χ², P under the true V) for `count` LP2-length single-tabula ciphers."""
    rows = []
    for i in range(count):
        chi2, n = flatness.chi2_uniform(synthetic(v, [LP2_RUNES], seed + i)[0])
        rows.append((chi2, flatness.random_tabula_p(chi2, n, S, v)))
    return rows


def sectioned(v: int, sizes: Sequence[int], count: int, seed: int, draws: np.ndarray) -> list[tuple[float, float]]:
    """(Σ χ²_s, P under the true V) for `count` ciphers with a fresh tabula per section."""
    rows = []
    for i in range(count):
        total = sum(flatness.chi2_uniform(c)[0] for c in synthetic(v, sizes, seed + i))
        rows.append((total, flatness.per_section_p(total, sizes, S, v, draws)))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--quick", action="store_true", help="20 ciphers per gate; never reads LP2, writes nothing")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    count = 20 if args.quick else CIPHERS
    log.info("plaintext Σq² = %.5f over %d runes; 29s − 1 = %.4f", S, len(PLAIN), 29 * S - 1)
    rows: list[str] = []
    void = []

    # Gate A: formula. Gate B: no false exclusion at the true V.
    sets = {v: pooled(v, count, SEED + 1000 * v) for v in GATE_A_V}
    for v, res in sets.items():
        mean = float(np.mean([c for c, _ in res]))
        want = flatness.DF + flatness.mean_noncentrality(LP2_RUNES, S, v)
        ok = abs(mean / want - 1) <= GATE_A_TOLERANCE
        log.info("gate A V=%d: mean χ² %.1f vs predicted %.1f (%+.1f %%) %s", v, mean, want, 100 * (mean / want - 1),
                 "ok" if ok else "FAIL")
        rows.append(f"gate_A\tV={v}\t{v}\t{mean:.2f}\t{want:.2f}\t{'ok' if ok else 'FAIL'}")
        if not ok:
            void.append(f"gate A at V={v}")
    ps = [p for _, p in sets[GATE_B_V]]
    hard, soft = sum(p <= ALPHA for p in ps), float(np.mean([p <= 0.05 for p in ps]))
    ok = hard == 0 and soft <= GATE_B_MAX_AT_05
    log.info("gate B V=%d: P ≤ 1e-4 in %d/%d, P ≤ 0.05 in %.1f %% %s", GATE_B_V, hard, len(ps), 100 * soft,
             "ok" if ok else "FAIL")
    rows.append(f"gate_B\tV={GATE_B_V}\t{GATE_B_V}\t{hard}\t{soft:.3f}\t{'ok' if ok else 'FAIL'}")
    if not ok:
        void.append("gate B")

    # Structural control: additive (a Latin-square tabula) under a uniform key, fresh re-key.
    rng = random.Random(SEED)
    add = [flatness.chi2_uniform(keys.encrypt_dodging(control_text(LP2_RUNES, rng), keys.random_key(LP2_RUNES, SEED + i),
                                                      keep=KEEP, seed=SEED + i, rekey="fresh"))[0] for i in range(count)]
    log.info("structural control (additive, uniform key): mean χ² %.1f over %d ciphers", np.mean(add), count)
    rows.append(f"control\tadditive uniform key\t29\t{np.mean(add):.2f}\t{flatness.DF}\treported")

    if args.quick:
        print("quick run: gates only" + (f"; would be VOID: {void}" if void else "; gates pass"))
        return 0
    if void:
        print(f"VOID: {void}. Stopping before the LP2 per-section statistic.")
        write(rows)
        return 0

    # LP2.
    corpus = load_corpus()
    lp2 = [r for seg in stats.UNSOLVED_SEGMENTS for r in corpus.segment_runes(seg)]
    chi2_pooled, n = flatness.chi2_uniform(lp2)
    sec = [corpus.segment_runes(seg) for seg in SECTIONS]
    sizes = [len(r) for r in sec]
    chi2_sec = [flatness.chi2_uniform(r)[0] for r in sec]
    total = sum(chi2_sec)
    draws = flatness.chi2_draws(MC_TRIALS, len(SECTIONS), SEED)
    log.info("LP2 pooled χ² %.2f (n %d); per-section %s, Σ %.2f on %d df", chi2_pooled, n,
             [round(c, 1) for c in chi2_sec], total, flatness.DF * len(SECTIONS))
    lam = flatness.lambda_max(chi2_pooled, flatness.DF, ALPHA)
    v_pool = flatness.boundary(lambda v: flatness.random_tabula_p(chi2_pooled, n, S, v), ALPHA)
    v_sec = flatness.boundary(lambda v: flatness.per_section_p(total, sizes, S, v, draws), ALPHA, v_max=100_000)
    null_sec = float(np.mean(draws.sum(axis=1) <= total))
    rows += [f"lp2\tpooled chi2\t{n}\t{chi2_pooled:.2f}\t{flatness.chi2_cdf_small(chi2_pooled, flatness.DF):.4f}\tP under flat",
             f"lp2\tper-section sum chi2\t{sum(sizes)}\t{total:.2f}\t{null_sec:.4f}\tP under flat",
             f"lp2\tlambda_max (any system)\t{n}\t{lam:.2f}\t{ALPHA:g}\tdata fact",
             f"boundary\tpooled (one tabula)\t{v_pool}\t{chi2_pooled:.2f}\t{ALPHA:g}\texcluded V_eff <= {v_pool}",
             f"boundary\tper-section (fresh tabula)\t{v_sec}\t{total:.2f}\t{ALPHA:g}\texcluded V_eff <= {v_sec}"]
    # Sensitivity, added after the run (not part of the declared rule): the anti-doublet rule makes counts more even
    # than multinomial, so the additive control averages below 28. Scale the observed statistics by that factor.
    k = float(np.mean(add)) / flatness.DF
    v_pool_k = flatness.boundary(lambda v: flatness.random_tabula_p(chi2_pooled / k, n, S, v), ALPHA)
    v_sec_k = flatness.boundary(lambda v: flatness.per_section_p(total / k, sizes, S, v, draws), ALPHA, v_max=100_000)
    rows += [f"sensitivity\tpooled, dodging factor {k:.3f}\t{v_pool_k}\t{chi2_pooled / k:.2f}\t{ALPHA:g}\t"
             f"excluded V_eff <= {v_pool_k}",
             f"sensitivity\tper-section, dodging factor {k:.3f}\t{v_sec_k}\t{total / k:.2f}\t{ALPHA:g}\t"
             f"excluded V_eff <= {v_sec_k}"]
    for seg, size, c in zip(SECTIONS, sizes, chi2_sec):
        rows.append(f"lp2_section\t{seg}\t{size}\t{c:.2f}\t{flatness.chi2_cdf_small(c, flatness.DF):.4f}\tP under flat")

    # Calibration (reported; declared as "power"): ciphers at V = 29 and half each boundary, scored against their own
    # true V. The value column is the false-exclusion rate (P ≤ 1e-4), which should be 0.
    for v in sorted({29, max(1, v_pool // 2)}):
        res = sets[v] if v in sets else pooled(v, count, SEED + 7 * v)
        frac = float(np.mean([flatness.random_tabula_p(c, LP2_RUNES, S, v) <= ALPHA for c, _ in res]))
        rows.append(f"calibration\tpooled V={v}\t{v}\t{np.mean([c for c, _ in res]):.2f}\t{frac:.3f}\treported")
    for v in sorted({29, max(1, v_sec // 2), GATE_B_V}):
        res = sectioned(v, sizes, count, SEED + 11 * v, draws)
        frac = float(np.mean([p <= ALPHA for _, p in res]))
        frac05 = float(np.mean([p <= 0.05 for _, p in res]))
        rows.append(f"calibration\tper-section V={v}\t{v}\t{np.mean([c for c, _ in res]):.2f}\t{frac:.3f}\t"
                    f"reported; P<=0.05 in {frac05:.3f}")

    # Named key classings (stage S family), pooled rule on their empirical weights.
    for name, (key, phases, cyclic) in family(PLAIN).items():
        stream = key if cyclic else key[:PRIME_PHASES + LP2_RUNES]
        ve = flatness.v_eff(stream)
        p = flatness.random_tabula_p(chi2_pooled, n, S, ve)
        rows.append(f"named\t{name}\t{ve:.1f}\t{chi2_pooled:.2f}\t{p:.3g}\t{'EXCLUDED' if p <= ALPHA else 'not excluded'}")

    write(rows)
    print("\n".join(rows))
    return 0


def write(rows: list[str]) -> None:
    header = "kind\tname\tV_or_n\tstatistic\tvalue\tverdict"
    OUT_PATH.write_text("\n".join([header, *rows]) + "\n", encoding="utf-8", newline="\n")
    log.info("wrote %d rows to %s", len(rows), OUT_PATH)


if __name__ == "__main__":
    sys.exit(main())
