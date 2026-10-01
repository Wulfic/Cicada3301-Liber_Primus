"""Stage V: Quagmire with named keyword alphabets, scored with labels (TODO.md, declared 2026-10-01 in 8880e3b
before this script first ran).

Model: c = π₂(s·π₁(p) + t·π₃(k) + a), k iid from one of stage U's six key families, (π₁, π₂, π₃) ∈ A³ where A is
the identity plus the keyed alphabet K and its inverse K⁻¹ of each declared keyword. Each member's free parameters are
mode (s, t) and offset a (87). Statistic: the best `stats.unigram_llr` over those 87 on the pooled LP2 counts, model
r = π₂(π₁q ⊛ π₃b), q = `detect.unigram` of the solved plaintext (C13's q).

Exclude a member if its best LLR ≤ −10; a lead if ≥ +10. G1 (calibration, void rule): 300 own-member synthetic
ciphers (50 per family, random member, mode and offset), none excluded. G2 (power): a member is testable if the rule
excludes it on ≥ 18 / 20 flat-key ciphers. Synthetic ciphers: word-shuffled solved plaintext, 12,956 runes,
keep 0.19, fresh re-key. Rows go to stage_v_results.tsv: gates, identity checks against C13, per-family counts, and a
row for every testable member not excluded and every lead.

Deterministic. Usage: python -m tools.run_stage_v [--quick]
"""

from __future__ import annotations

import argparse
import logging
import random
import sys

import numpy as np

from tools.lpcore import detect, keys, quagmire, stats
from tools.lpcore.corpus import REPO_ROOT, load_corpus
from tools.lpcore.gematria import N, indices_to_runes, spellings_of
from tools.lpcore.solved import DIVINITY, FIRFUMFERENFE
from tools.run_stage_s import LP2_RUNES, PLAIN, control_text
from tools.run_stage_u import families

log = logging.getLogger("stage_v")

OUT_PATH = REPO_ROOT / "reference" / "findings" / "stage_v_results.tsv"
EXCLUDE = -10.0
LEAD = 10.0
KEEP = 0.19
SEED = 3301
CALIBRATION_PER_FAMILY = 50
POWER_CIPHERS = 20
POWER_MIN = 18
Q = detect.unigram(PLAIN)

TITLES = ("A WARNING", "WELCOME", "WISDOM", "SOME WISDOM", "KNOW THIS", "A KOAN", "AN INSTRUCTION",
          "THE LOSS OF DIVINITY", "AN END", "PARABLE")
PARABLE_WORDS = ("LIKE", "THE", "INSTAR", "TUNNELING", "TO", "SURFACE", "WE", "MUST", "SHED", "OUR", "OWN",
                 "CIRCUMFERENCES", "FIND", "DIVINITY", "WITHIN", "AND", "EMERGE")
OTHERS = ("CIRCUMFERENCE", "LIBER PRIMUS", "PRIMUS", "CICADA", "PRIMES", "TOTIENT")


def keywords() -> dict[str, tuple[int, ...]]:
    """The 34 declared keywords as runes: the solved keys literally, the rest by their greedy spelling."""
    out = {"DIVINITY": DIVINITY, "FIRFUMFERENFE": FIRFUMFERENFE}
    for phrase in (*TITLES, *PARABLE_WORDS, *OTHERS):
        word = phrase.replace(" ", "")
        out.setdefault(word, spellings_of(word)[0])
    return out


def alphabets() -> tuple[list[str], np.ndarray]:
    """The identity, then K and K⁻¹ for each keyword, with duplicate permutations collapsed (first name kept)."""
    named: dict[tuple[int, ...], str] = {tuple(range(N)): "id"}
    for word, runes in keywords().items():
        k = quagmire.keyed_alphabet(runes)
        for name, perm in ((word, k), (word + "^-1", quagmire.inverse(k))):
            named.setdefault(tuple(perm), name)
    return list(named.values()), np.array(list(named.keys()))


def synthetic(b: np.ndarray, member: tuple[int, int, int], mode: str, offset: int, alph: np.ndarray,
              rng: random.Random, nrng: np.random.Generator) -> np.ndarray:
    """Counts of one synthetic cipher c = π₂(s·π₁(p) + t·π₃(k) + a) at LP2's length."""
    s, t = quagmire.MODE_SIGNS[mode]
    i1, i2, i3 = member
    pi1 = [(s * x) % N for x in alph[i1]]
    kappa = [(t * int(alph[i3][v]) + offset) % N for v in nrng.choice(N, size=LP2_RUNES, p=b)]
    cipher = quagmire.encrypt(control_text(LP2_RUNES, rng), kappa, pi1, list(alph[i2]), keep=KEEP,
                              seed=rng.randrange(2**31))
    return np.bincount(cipher, minlength=N)


def flat_counts(count: int, seed: int) -> np.ndarray:
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        key = [rng.randrange(N) for _ in range(LP2_RUNES)]
        cipher = keys.encrypt_dodging(control_text(LP2_RUNES, rng), key, keep=KEEP, seed=rng.randrange(2**31),
                                      rekey="fresh")
        out.append(np.bincount(cipher, minlength=N))
    return np.array(out)


def lp2_counts() -> np.ndarray:
    corpus = load_corpus()
    runes = [r for seg in stats.UNSOLVED_SEGMENTS for r in corpus.segment_runes(seg)]
    if len(runes) != LP2_RUNES:
        raise ValueError(f"LP2 has {len(runes)} runes, expected {LP2_RUNES}")
    return np.bincount(runes, minlength=N)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--quick", action="store_true", help="10 calibration and 5 power ciphers; never scores LP2, writes nothing")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    per_family = 10 if args.quick else CALIBRATION_PER_FAMILY
    power_ciphers = 5 if args.quick else POWER_CIPHERS
    power_min = power_ciphers - 1 if args.quick else POWER_MIN
    names, alph = alphabets()
    na = len(alph)
    fams = families()
    log.info("%d keywords, %d distinct alphabets, %d members per family", len(keywords()), na, na ** 3)
    rows = [f"alphabets\t-\t{na}\t" + ", ".join(f"{w}={indices_to_runes(r)}" for w, r in keywords().items())]
    void: list[str] = []
    models = {name: quagmire.log_models(Q, b, alph) for name, b in fams.items()}

    # G1: calibration on own-member ciphers.
    nrng = np.random.default_rng(SEED)
    rng = random.Random(SEED)
    for f_i, (name, b) in enumerate(fams.items()):
        worst = np.inf
        for _ in range(per_family):
            member = tuple(int(x) for x in nrng.integers(0, na, 3))
            mode = list(quagmire.MODE_SIGNS)[int(nrng.integers(0, 3))]
            counts = synthetic(b, member, mode, int(nrng.integers(0, N)), alph, rng, nrng)
            m = member[0] * na + member[2]
            worst = min(worst, float(quagmire.best_llr(models[name][m:m + 1], counts, alph)[0, 0, member[1]]))
        ok = worst > EXCLUDE
        log.info("G1 %-22s worst own-member best LLR %+.1f %s", name, worst, "ok" if ok else "FAIL")
        rows.append(f"gate_G1\t{name}\t{per_family}\tworst own-member best LLR {worst:+.2f} {'ok' if ok else 'FAIL'}")
        if not ok:
            void.append(f"G1 {name}")

    # G2: power per member on flat-key ciphers.
    flats = flat_counts(power_ciphers, SEED + 1)
    testable = {}
    for name in fams:
        excluded = (quagmire.best_llr(models[name], flats, alph) <= EXCLUDE).sum(axis=0)
        testable[name] = excluded >= power_min
        log.info("G2 %-22s testable %d / %d (%.1f %%)", name, testable[name].sum(), excluded.size,
                 100 * testable[name].mean())
        rows.append(f"gate_G2\t{name}\t{power_ciphers}\ttestable {testable[name].sum()} / {excluded.size}")

    if args.quick:
        print("quick run: gates only" + (f"; would be VOID: {void}" if void else "; gates pass"))
        return 0
    if void:
        print(f"VOID: {void}. Stopping before LP2.")
        write(rows)
        return 0

    # LP2.
    observed = lp2_counts()
    for name in fams:
        llr = quagmire.best_llr(models[name], observed, alph)[0]           # (A·A, A): row π₁·A + π₃, column π₂
        excl = llr <= EXCLUDE
        test = testable[name]
        rows.append(f"identity\t{name}\t-\tbest LLR {llr[0, 0]:+.2f}")
        rows.append(f"lp2\t{name}\t{llr.size}\texcluded {excl.sum()}; not excluded, testable {(~excl & test).sum()}; "
                    f"untestable, not excluded {(~excl & ~test).sum()}; leads {(llr >= LEAD).sum()}; "
                    f"max {llr.max():+.2f}")
        log.info("LP2 %-22s identity %+.2f excluded %d / %d, testable survivors %d, leads %d, max %+.2f", name,
                 llr[0, 0], excl.sum(), llr.size, (~excl & test).sum(), (llr >= LEAD).sum(), llr.max())
        for m, j in zip(*np.nonzero((~excl & test) | (llr >= LEAD))):
            rows.append(f"member\t{name}\t{names[m // na]} | {names[j]} | {names[m % na]}\t"
                        f"best LLR {llr[m, j]:+.2f}; {'testable' if test[m, j] else 'untestable'}")
    write(rows)
    print("\n".join(r for r in rows if not r.startswith(("member", "alphabets"))))
    return 0


def write(rows: list[str]) -> None:
    header = "kind\tfamily\tsize\tdetail"
    OUT_PATH.write_text("\n".join([header, *rows]) + "\n", encoding="utf-8", newline="\n")
    log.info("wrote %d rows to %s", len(rows), OUT_PATH)


if __name__ == "__main__":
    sys.exit(main())
