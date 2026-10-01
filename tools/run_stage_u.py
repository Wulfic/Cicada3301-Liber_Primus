"""Stage U: C10 and C13 under Quagmire relabelling, c = π₂(π₁(p) + π₃(k)) with random alphabets (TODO.md, declared
2026-10-01 in 4051fe2 before this script first ran).

Families: six key value distributions b. Variants: π₃ independent of π₁ (I) or tied to it (T). Statistics: the pooled
χ² (one set of alphabets, 28 df) and Σ per-section χ² over sections 7–9 and 11–15 (fresh alphabets per section,
224 df). P = mean over alphabet draws of P(χ²_df(λ) ≤ observed), with λ exact per draw.

A row is excluded if P ≤ 1e-4 under both the raw χ² and the χ² divided by the dodging factor (mean χ² / df of 200
flat-key ciphers). Gates on synthetic ciphers run first (word-shuffled solved plaintext, keep 0.19, fresh re-key),
as amended in TODO.md before LP2 was scored (the declared G2 and G3 had their roles swapped):
G1: variant I's mean λ within 3 % of n·(29Σq² − 1)(29Σb² − 1)/28. G2 (power): a row is testable only if the rule
excludes it on ≥ 18 / 20 flat-key ciphers. G3 (calibration): the rule excludes a row on none of 20 ciphers made with
that row's own key family and random alphabets, or the run is VOID. Rows go to stage_u_results.tsv.

Deterministic. Usage: python -m tools.run_stage_u [--quick]
"""

from __future__ import annotations

import argparse
import logging
import random
import sys
from collections import Counter
from collections.abc import Sequence

import numpy as np

from tools.lpcore import flatness, quagmire, stats
from tools.lpcore.corpus import REPO_ROOT, load_corpus
from tools.lpcore.gematria import N, PRIME_VALUES
from tools.lpcore.verify import load_translation
from tools.run_stage_s import LP2_RUNES, PLAIN, control_text
from tools.run_stage_t import SECTIONS

log = logging.getLogger("stage_u")

OUT_PATH = REPO_ROOT / "reference" / "findings" / "stage_u_results.tsv"
ALPHA = 1e-4
KEEP = 0.19
SEED = 3301
DRAWS_LP2 = 100_000
DRAWS_CONTROL = 100_000
CONTROLS = 20
POWER_MIN = 18
FACTOR_CIPHERS = 200
G1_TOLERANCE = 0.03
VARIANTS = {"I": False, "T": True}
STATS = ("pooled", "per-section")
Q = np.bincount(PLAIN, minlength=N) / len(PLAIN)
S = float(np.sum(Q ** 2))


def section_sizes() -> list[int]:
    corpus = load_corpus()
    return [len(corpus.segment_runes(s)) for s in SECTIONS]


def latin_letter_weights() -> list[int]:
    """A–Z counts of the solved English translation (as in C13's test): A = 0 … Z = 25."""
    text = " ".join(c for paras in load_translation().values() for para in paras for c in para).upper()
    counts = Counter(ch for ch in text if "A" <= ch <= "Z")
    return [counts[chr(ord("A") + i)] for i in range(26)]


def families() -> dict[str, np.ndarray]:
    """The key value distributions b over Z₂₉, as declared."""
    primes = np.zeros(N)
    for letter in range(N):
        primes[PRIME_VALUES[letter] % N] += Q[letter]
    return {
        "English runes": Q.copy(),
        "English prime values": primes,
        "English Latin A-Z": np.array(stats.values_distribution(latin_letter_weights())),
        "decimal digits": np.array(stats.values_distribution([1] * 10)),
        "hex digits": np.array(stats.values_distribution([1] * 16)),
        "letters A-Z": np.array(stats.values_distribution([1] * 26)),
    }


def lambdas(b: np.ndarray, tied: bool, stat: str, sizes: Sequence[int], count: int, seed: int) -> np.ndarray:
    """Noncentralities of `count` alphabet draws: one draw for LP2 (pooled) or a fresh draw per section."""
    rng = np.random.default_rng(seed)
    if stat == "pooled":
        return LP2_RUNES * quagmire.deviations(Q, b, count, rng, tied=tied)
    return sum(m * quagmire.deviations(Q, b, count, rng, tied=tied) for m in sizes)


def cipher_stat(b: np.ndarray, tied: bool, stat: str, sizes: Sequence[int], seed: int) -> float:
    """χ² (pooled) or Σ per-section χ² of one synthetic Quagmire cipher with key ~ b and random alphabets."""
    rng = random.Random(seed)
    nrng = np.random.default_rng(seed)
    parts = [LP2_RUNES] if stat == "pooled" else list(sizes)
    total = 0.0
    for size in parts:
        pi1, pi2 = (list(p) for p in quagmire.random_permutations(2, nrng))
        pi3 = pi1 if tied else list(quagmire.random_permutations(1, nrng)[0])
        k = nrng.choice(N, size=size, p=b)
        cipher = quagmire.encrypt(control_text(size, rng), [pi3[v] for v in k], pi1, pi2, keep=KEEP,
                                  seed=rng.randrange(2**31))
        total += flatness.chi2_uniform(cipher)[0]
    return total


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--quick", action="store_true", help="5 ciphers and 2,000 draws per row; never scores LP2, writes nothing")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    controls = 5 if args.quick else CONTROLS
    draws_control = 2_000 if args.quick else DRAWS_CONTROL
    draws_lp2 = 2_000 if args.quick else DRAWS_LP2
    sizes = section_sizes()
    fams = families()
    flat = np.full(N, 1 / N)
    rows: list[str] = []
    void: list[str] = []
    log.info("plaintext Σq² = %.5f; section sizes %s", S, sizes)

    # G1: the mean-λ formula, on the draws that will score LP2 (model only).
    lp2_lams: dict[tuple[str, str, str], np.ndarray] = {}
    for f_i, (name, b) in enumerate(fams.items()):
        for v_i, (variant, tied) in enumerate(VARIANTS.items()):
            for s_i, stat in enumerate(STATS):
                lp2_lams[name, variant, stat] = lambdas(b, tied, stat, sizes, draws_lp2, SEED + 100 * f_i + 10 * v_i + s_i)
        lam = lp2_lams[name, "I", "pooled"]
        want = quagmire.mean_noncentrality(LP2_RUNES, S, float(np.sum(b ** 2)))
        ok = abs(lam.mean() / want - 1) <= G1_TOLERANCE
        log.info("G1 %-22s Σb² %.4f mean λ %.1f vs %.1f %s", name, np.sum(b ** 2), lam.mean(), want, "ok" if ok else "FAIL")
        rows.append(f"gate_G1\t{name}\tI\tpooled\t{lam.mean():.2f}\t{want:.2f} {'ok' if ok else 'FAIL'}")
        if not ok:
            void.append(f"G1 {name}")

    # Dodging factor from flat-key ciphers.
    factor = {}
    for s_i, stat in enumerate(STATS):
        df = flatness.DF * (1 if stat == "pooled" else len(sizes))
        vals = [cipher_stat(flat, False, stat, sizes, SEED + 50_000 + 1_000 * s_i + i)
                for i in range(controls if args.quick else FACTOR_CIPHERS)]
        factor[stat] = float(np.mean(vals)) / df
        log.info("dodging factor %s: %.4f", stat, factor[stat])
        rows.append(f"factor\tflat key\t-\t{stat}\t{factor[stat]:.4f}\tmean chi2 / {df}")

    # G2 (power: flat-key ciphers excluded) and G3 (calibration: own-family ciphers not excluded), by the LP2 rule.
    def excluded(chi2: float, stat: str, df: int, lams: np.ndarray) -> bool:
        return (quagmire.family_p(chi2, df, lams) <= ALPHA
                and quagmire.family_p(chi2 / factor[stat], df, lams) <= ALPHA)

    testable = {}
    flat_stats = {stat: [cipher_stat(flat, False, stat, sizes, SEED + 60_000 + 1_000 * s_i + i) for i in range(controls)]
                  for s_i, stat in enumerate(STATS)}
    for f_i, (name, b) in enumerate(fams.items()):
        for v_i, (variant, tied) in enumerate(VARIANTS.items()):
            for s_i, stat in enumerate(STATS):
                df = flatness.DF * (1 if stat == "pooled" else len(sizes))
                tag = 100 * f_i + 10 * v_i + s_i
                lams = lambdas(b, tied, stat, sizes, draws_control, SEED + 70_000 + tag)
                power = sum(excluded(c, stat, df, lams) for c in flat_stats[stat])
                false = sum(excluded(cipher_stat(b, tied, stat, sizes, SEED + 80_000 + 100 * tag + i), stat, df, lams)
                            for i in range(controls))
                need = POWER_MIN if not args.quick else controls - 1
                testable[name, variant, stat] = power >= need
                log.info("%-22s %s %-11s G2 power %2d/%d %s  G3 false %d/%d", name, variant, stat, power, controls,
                         "testable" if power >= need else "untestable", false, controls)
                rows.append(f"gate_G2	{name}	{variant}	{stat}	{power}/{controls}	"
                            f"{'testable' if power >= need else 'untestable'}")
                rows.append(f"gate_G3	{name}	{variant}	{stat}	{false}/{controls}	{'ok' if false == 0 else 'FAIL'}")
                if false:
                    void.append(f"G3 {name} {variant} {stat}")

    if args.quick:
        print("quick run: gates only" + (f"; would be VOID: {void}" if void else "; gates pass"))
        return 0
    if void:
        print(f"VOID: {void}. Stopping before LP2.")
        write(rows)
        return 0

    # LP2.
    corpus = load_corpus()
    lp2 = [r for seg in stats.UNSOLVED_SEGMENTS for r in corpus.segment_runes(seg)]
    observed = {"pooled": flatness.chi2_uniform(lp2)[0],
                "per-section": sum(flatness.chi2_uniform(corpus.segment_runes(s))[0] for s in SECTIONS)}
    log.info("LP2 pooled χ² %.2f, per-section Σ %.2f", observed["pooled"], observed["per-section"])
    for name in fams:
        for variant in VARIANTS:
            for stat in STATS:
                df = flatness.DF * (1 if stat == "pooled" else len(sizes))
                lams = lp2_lams[name, variant, stat]
                raw = quagmire.family_p(observed[stat], df, lams)
                corr = quagmire.family_p(observed[stat] / factor[stat], df, lams)
                lam_max = flatness.lambda_max(observed[stat], df, ALPHA)
                survive = float(np.mean(lams <= lam_max))
                if not testable[name, variant, stat]:
                    verdict = "untestable"
                else:
                    verdict = "EXCLUDED" if raw <= ALPHA and corr <= ALPHA else "not excluded"
                rows.append(f"lp2\t{name}\t{variant}\t{stat}\t{raw:.3g} / {corr:.3g}\t"
                            f"{verdict}; min lambda {lams.min():.1f}, median {np.median(lams):.1f}, "
                            f"draws with lambda <= {lam_max:.2f}: {survive:.2e}")
    write(rows)
    print("\n".join(rows))
    return 0


def write(rows: list[str]) -> None:
    header = "kind\tfamily\tvariant\tstatistic\tvalue\tdetail"
    OUT_PATH.write_text("\n".join([header, *rows]) + "\n", encoding="utf-8", newline="\n")
    log.info("wrote %d rows to %s", len(rows), OUT_PATH)


if __name__ == "__main__":
    sys.exit(main())
