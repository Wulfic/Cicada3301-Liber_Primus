"""Stage S: named long keys as per-position alphabets c_i = σ_{k_i}(p_i), scored label-free (TODO.md, declared
2026-10-01 before this script first ran on LP2).

Each key classing is scored by `alphabets.log_mean_lr`: the mean Dirichlet-multinomial LR over every key phase,
with the key in step. Controls run first (stage_s_controls.tsv): positive (the solved plaintext's words in random
order, under the key with a random σ per class, fresh re-key, keep 0.19), negative (the same cipher against the
shuffled key), and a real-data null (the shuffled key on LP2 continuous). The family (20 classings × 10 alignments)
goes to stage_s_candidates.tsv. PASS means a score ≥ detect.THRESHOLD (30 nats). Run 1 was void (TODO stage S).

Deterministic. Usage: python -m tools.run_stage_s [--quick]
"""

from __future__ import annotations

import argparse
import logging
import random
import sys
from collections.abc import Hashable, Sequence
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from tools.lpcore import alphabets, detect, keys, stats
from tools.lpcore.corpus import REPO_ROOT, load_corpus
from tools.lpcore.gematria import N, PRIME_VALUES
from tools.lpcore.verify import load_translation
from tools.run_stage_r import OUTGUESS, map_values

log = logging.getLogger("stage_s")

OUT_PATH = REPO_ROOT / "reference" / "findings" / "stage_s_candidates.tsv"
CONTROLS_PATH = REPO_ROOT / "reference" / "findings" / "stage_s_controls.tsv"
CORPORA = REPO_ROOT / "data" / "corpora"
CORPUS_FILES = ("emerson_essays.txt", "self_reliance.txt", "liber_al_vel_legis.txt", "deor_poem.txt")
PRIME_PHASES = 25_912                    # stage I's K-A length: a start anywhere in it
LP2_RUNES = 12_956
CONTROL_SIZES = (729, 1894, LP2_RUNES)
CONTROL_SEEDS = 2
CONTROL_SEED = 3301
WORKERS = 8                              # each worker holds ~0.2 GB of FFTs for the longest corpus

_FAMILY: dict[str, tuple[Sequence[Hashable], int, bool]] = {}
_CIPHERS: dict[str, list[int]] = {}


def corpus_letters(name: str) -> list[str]:
    """Every alphabetic character of a corpus file, upper-cased; each distinct one is a key class."""
    text = (CORPORA / name).read_text(encoding="utf-8")
    letters = [ch.upper() for ch in text if ch.isalpha()]
    if len(letters) < 1000:
        raise ValueError(f"{name}: only {len(letters)} letters")
    return letters


def family(plain: Sequence[int]) -> dict[str, tuple[Sequence[Hashable], int, bool]]:
    """Each declared key classing as (key, number of phases, cyclic)."""
    out: dict[str, tuple[Sequence[Hashable], int, bool]] = {}
    primes = keys.prime_stream(PRIME_PHASES + LP2_RUNES)
    out["primes mod29"] = ([p % N for p in primes], PRIME_PHASES, False)
    out["plaintext rune"] = (list(plain), len(plain), True)
    out["plaintext prime-mod29"] = ([PRIME_VALUES[r] % N for r in plain], len(plain), True)
    hint = list((OUTGUESS / "wisdom_hint.txt").read_bytes())
    for name, data in (("hint", hint), ("hint-reversed", hint[::-1])):
        out[f"{name} raw"] = (data, len(data), True)
        out[f"{name} mod29"] = (map_values(data, 256, "mod"), len(data), True)
    for page in ("page_17.bin", "page_21.bin", "page_43.bin"):
        data = list((OUTGUESS / page).read_bytes())
        out[f"{page} raw"] = (data, len(data), True)
        for mapping in ("mod", "reject"):
            mapped = map_values(data, 256, mapping)
            out[f"{page} {mapping}29"] = (mapped, len(mapped), True)
    for name in CORPUS_FILES:
        letters = corpus_letters(name)
        out[f"{name.removesuffix('.txt')} letters"] = (letters, len(letters), True)
    if len(out) != 20:
        raise AssertionError(f"declared 20 key classings, built {len(out)}")
    return out


def score(cipher: Sequence[int], key: Sequence[Hashable], phases: int, cyclic: bool) -> tuple[float, int, float]:
    return alphabets.log_mean_lr(cipher, key, phases, ALPHA, cyclic=cyclic)


def key_from(key: Sequence[Hashable], phase: int, length: int, cyclic: bool) -> list[Hashable]:
    if cyclic:
        return [key[(phase + i) % len(key)] for i in range(length)]
    return list(key[phase:phase + length])


WORDS = keys.solved_plaintext_words(load_corpus(), load_translation())
PLAIN = [r for w in WORDS for r in w]
ALPHA = alphabets.dm_alpha(PLAIN)


def control_text(size: int, rng: random.Random) -> list[int]:
    """The solved plaintext's words in a fresh random order each pass: no period (run 1's tiled text had period
    2,901, the same as the plaintext-derived keys), and no phase of such a key equals it."""
    out: list[int] = []
    while len(out) < size:
        order = WORDS[:]
        rng.shuffle(order)
        out += [r for w in order for r in w]
    return out[:size]


def _init_worker() -> None:
    corpus = load_corpus()
    _FAMILY.update(family(PLAIN))
    for s in stats.UNSOLVED_SEGMENTS:
        _CIPHERS[str(s)] = corpus.segment_runes(s)
    _CIPHERS["7-15"] = [r for s in stats.UNSOLVED_SEGMENTS for r in corpus.segment_runes(s)]


def _control(job: tuple[str, int, int]) -> list[tuple]:
    """Positive and negative control for one (key, size, seed)."""
    name, size, seed = job
    key, phases, cyclic = _FAMILY[name]
    rng = random.Random(f"{CONTROL_SEED}/{name}/{size}/{seed}")
    phase = rng.randrange(phases)
    text = control_text(size, rng)
    cipher = alphabets.encrypt_alphabets(text, key_from(key, phase, size, cyclic), keep=0.19,
                                         seed=rng.randrange(10**9))
    shuffled = list(key)
    rng.shuffle(shuffled)
    pos, best, _ = score(cipher, key, phases, cyclic)
    neg, _, _ = score(cipher, shuffled, phases, cyclic)
    return [(name, "positive", size, seed, phase, best, pos), (name, "negative", size, seed, phase, -1, neg)]


def _null(name: str) -> tuple:
    """The shuffled key on LP2 continuous: the null measured on the real ciphertext."""
    key, phases, cyclic = _FAMILY[name]
    shuffled = list(key)
    random.Random(f"{CONTROL_SEED}/{name}/null").shuffle(shuffled)
    value, best, _ = score(_CIPHERS["7-15"], shuffled, phases, cyclic)
    return name, "lp2-null", LP2_RUNES, 0, -1, best, value


def _decode(job: tuple[str, str]) -> tuple:
    name, segment = job
    key, phases, cyclic = _FAMILY[name]
    cipher = _CIPHERS[segment]
    value, best, top = score(cipher, key, phases, cyclic)
    alignment = "continuous" if segment == "7-15" else "per-section"
    return name, alignment, segment, len(cipher), phases, best, top, value


def has_power(controls: list[tuple], name: str, runes: int) -> bool:
    """Declared: both positive controls at the largest control size ≤ runes score ≥ the threshold."""
    sizes = [s for s in CONTROL_SIZES if s <= runes]
    if not sizes:
        return False
    pos = [r[6] for r in controls if r[0] == name and r[1] == "positive" and r[2] == max(sizes)]
    return len(pos) == CONTROL_SEEDS and min(pos) >= detect.THRESHOLD


def write_tsv(header: str, rows: list[str], path: Path) -> None:
    path.write_text("\n".join([header, *rows]) + "\n", encoding="utf-8", newline="\n")
    log.info("wrote %d rows to %s", len(rows), path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--quick", action="store_true", help="positive and negative controls at 729 runes only; never reads LP2, writes nothing")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    log.info("alpha = %.4f", ALPHA)

    _init_worker()
    names = sorted(_FAMILY, key=lambda n: -_FAMILY[n][1])                 # most phases first, for load balance
    log.info("family: %s", {n: (_FAMILY[n][1], len(set(_FAMILY[n][0]))) for n in names})
    sizes = CONTROL_SIZES[:1] if args.quick else CONTROL_SIZES
    segments = [str(s) for s in stats.UNSOLVED_SEGMENTS] + ["7-15"]

    with ProcessPoolExecutor(max_workers=WORKERS, initializer=_init_worker) as pool:
        jobs = [(n, size, seed) for n in names for size in sizes for seed in range(CONTROL_SEEDS)]
        controls = [row for rows in pool.map(_control, jobs) for row in rows]
        if args.quick:
            for r in controls:
                print(f"  {r[0]:28s} {r[1]:8s} {r[6]:9.1f}")
            return 0
        controls += list(pool.map(_null, names))
        log.info("controls done: %d rows", len(controls))
        decodes = list(pool.map(_decode, [(n, s) for n in names for s in segments]))

    if not args.quick:
        write_tsv("key\tkind\trunes\tseed\tphase\tbest_phase\tlog_mean_lr",
                  [f"{k}\t{kind}\t{n}\t{sd}\t{ph}\t{b}\t{v:.2f}" for k, kind, n, sd, ph, b, v in controls],
                  CONTROLS_PATH)
        write_tsv("key\talignment\tsegment\trunes\tphases\tbest_phase\tbest_phase_log_lr\tlog_mean_lr",
                  [f"{k}\t{a}\t{s}\t{n}\t{ph}\t{b}\t{t:.2f}\t{v:.2f}" for k, a, s, n, ph, b, t, v in decodes],
                  OUT_PATH)

    pos = [r for r in controls if r[1] == "positive"]
    neg = [r for r in controls if r[1] != "positive"]
    print(f"controls: positive min {min(r[6] for r in pos):.1f}, negative/null max {max(r[6] for r in neg):.1f}")
    void = [r for r in neg if r[6] >= detect.THRESHOLD]
    if void:
        print(f"VOID: {len(void)} negative or null controls reached the threshold: {void}")
    print(f"\n{len(decodes)} decodes; false-positive bound {len(decodes)} * e^-30 = {len(decodes) * 9.36e-14:.1e}")
    for name in names:
        rows = [r for r in decodes if r[0] == name]
        powered = [r for r in rows if has_power(controls, name, r[3])]
        best = max(rows, key=lambda r: r[7])
        print(f"  {name:28s} best {best[7]:9.2f} (seg {best[2]}); power at {len(powered)}/{len(rows)} alignments; "
              f"positive min {min(r[6] for r in pos if r[0] == name):.1f}")
    passed = [r for r in decodes if r[7] >= detect.THRESHOLD]
    print(f"PASS (score >= {detect.THRESHOLD:.0f}): {len(passed)}")
    for r in passed:
        print("  ", r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
