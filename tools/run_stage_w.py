"""Stage W: the long named byte keys as random tabulae c_i = σ_{k_i}(p_i), in step, with flat negatives (TODO.md,
declared 2026-10-01 in 106c634 before this script existed).

The family is stage S's five raw-byte classings × 10 alignments, scored by the same `alphabets.log_mean_lr`. Stage S
was void because its negative controls were uneven random-σ ciphers. Here every (classing, alignment) gets controls at
that alignment's exact length: 5 positives (random σ per byte value, in step, keep 0.19) and 5 flat negatives (an
additive cipher under a uniform random key, keep 0.19, scored against the named key). A real-data null per classing
scores the shuffled key on LP2 continuous.

Declared rules: VOID if any flat negative or null ≥ 30; an alignment is testable if all 5 positives ≥ 30; PASS if any
LP2 decode ≥ 30; EXCLUDED where testable and LP2 < 30.

Deterministic. Usage: python -m tools.run_stage_w [--quick]
"""

from __future__ import annotations

import argparse
import csv
import logging
import random
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from tools.lpcore import alphabets, detect, keys, stats
from tools.lpcore.corpus import REPO_ROOT, load_corpus
from tools.run_stage_s import OUT_PATH as STAGE_S_PATH
from tools.run_stage_s import PLAIN, control_text, family, key_from, score

log = logging.getLogger("stage_w")

CANDIDATES_PATH = REPO_ROOT / "reference" / "findings" / "stage_w_candidates.tsv"
CONTROLS_PATH = REPO_ROOT / "reference" / "findings" / "stage_w_controls.tsv"
CLASSINGS = ("hint raw", "hint-reversed raw", "page_17.bin raw", "page_21.bin raw", "page_43.bin raw")
CONTINUOUS = "7-15"
ALIGNMENTS = (CONTINUOUS, *(str(s) for s in stats.UNSOLVED_SEGMENTS))
SEEDS = 5
KEEP = 0.19
SEED = 3301
WORKERS = 8

_FAMILY: dict = {}
_CIPHERS: dict[str, list[int]] = {}


def _init_worker() -> None:
    corpus = load_corpus()
    full = family(PLAIN)
    _FAMILY.update({name: full[name] for name in CLASSINGS})
    for s in stats.UNSOLVED_SEGMENTS:
        _CIPHERS[str(s)] = corpus.segment_runes(s)
    _CIPHERS[CONTINUOUS] = [r for s in stats.UNSOLVED_SEGMENTS for r in corpus.segment_runes(s)]


def _control(job: tuple[str, str, str, int]) -> tuple:
    """One positive or flat-negative control at the alignment's exact length."""
    name, alignment, kind, seed = job
    key, phases, cyclic = _FAMILY[name]
    size = len(_CIPHERS[alignment])
    rng = random.Random(f"W/{SEED}/{name}/{alignment}/{kind}/{seed}")
    phase = rng.randrange(phases)
    text = control_text(size, rng)
    if kind == "positive":
        cipher = alphabets.encrypt_alphabets(text, key_from(key, phase, size, cyclic), keep=KEEP,
                                             seed=rng.randrange(10**9))
    elif kind == "flat-negative":
        cipher = keys.encrypt_dodging(text, keys.random_key(size, rng.randrange(10**9)), keep=KEEP,
                                      seed=rng.randrange(10**9), rekey="fresh")
        phase = -1
    else:
        raise ValueError(f"unknown control kind {kind!r}")
    value, best, _ = score(cipher, key, phases, cyclic)
    return name, alignment, kind, size, seed, phase, best, round(value, 2)


def _null(name: str) -> tuple:
    key, phases, cyclic = _FAMILY[name]
    shuffled = list(key)
    random.Random(f"W/{SEED}/{name}/null").shuffle(shuffled)
    value, best, _ = score(_CIPHERS[CONTINUOUS], shuffled, phases, cyclic)
    return name, CONTINUOUS, "lp2-null", len(_CIPHERS[CONTINUOUS]), 0, -1, best, round(value, 2)


def _decode(job: tuple[str, str]) -> tuple:
    name, alignment = job
    key, phases, cyclic = _FAMILY[name]
    cipher = _CIPHERS[alignment]
    value, best, top = score(cipher, key, phases, cyclic)
    return name, alignment, len(cipher), phases, best, round(top, 2), round(value, 2)


def verdicts(controls: list[tuple], decodes: list[tuple]) -> tuple[bool, dict[tuple[str, str], str]]:
    """(void, {(classing, alignment): PASS | EXCLUDED | untestable}) by the declared rules."""
    negatives = [r[7] for r in controls if r[2] in ("flat-negative", "lp2-null")]
    void = any(v >= detect.THRESHOLD for v in negatives)
    out: dict[tuple[str, str], str] = {}
    for name, alignment, *_, value in decodes:
        pos = [r[7] for r in controls if r[0] == name and r[1] == alignment and r[2] == "positive"]
        if value >= detect.THRESHOLD:
            out[(name, alignment)] = "PASS"
        elif len(pos) == SEEDS and min(pos) >= detect.THRESHOLD:
            out[(name, alignment)] = "EXCLUDED"
        else:
            out[(name, alignment)] = "untestable"
    return void, out


def stage_s_values() -> dict[tuple[str, str], float]:
    """Stage S's log_mean_lr for this family: the LP2 numbers declared to be reproduced exactly."""
    with STAGE_S_PATH.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    return {(r["key"], r["segment"]): float(r["log_mean_lr"]) for r in rows if r["key"] in CLASSINGS}


def write_tsv(path: Path, header: tuple[str, ...], rows: list[tuple]) -> None:
    lines = ["\t".join(header), *("\t".join(str(x) for x in r) for r in rows)]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    log.info("wrote %d rows to %s", len(rows), path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--quick", action="store_true", help="smoke test: one classing, two alignments, 1 seed")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    classings = CLASSINGS[:1] if args.quick else CLASSINGS
    alignments = ("12", CONTINUOUS) if args.quick else ALIGNMENTS
    seeds = 1 if args.quick else SEEDS
    control_jobs = [(n, a, k, s) for n in classings for a in alignments
                    for k in ("positive", "flat-negative") for s in range(seeds)]
    decode_jobs = [(n, a) for n in classings for a in alignments]
    log.info("%d controls, %d nulls, %d decodes on %d workers", len(control_jobs), len(classings),
             len(decode_jobs), WORKERS)

    with ProcessPoolExecutor(WORKERS, initializer=_init_worker) as pool:
        controls = list(pool.map(_control, control_jobs))
        controls += list(pool.map(_null, classings))
        decodes = list(pool.map(_decode, decode_jobs))

    expected = stage_s_values()
    drift = [(d[0], d[1], d[6], expected.get((d[0], d[1]))) for d in decodes
             if expected.get((d[0], d[1])) is None or abs(expected[(d[0], d[1])] - d[6]) > 0.005]
    if drift:
        log.error("LP2 decodes differ from stage S, which the declaration forbids: %s", drift)
        return 1

    void, verdict = verdicts(controls, decodes)
    if args.quick:
        for r in controls + decodes:
            log.info("quick: %s", r)
        log.info("quick run: void=%s verdicts=%s (nothing written)", void, verdict)
        return 0

    write_tsv(CONTROLS_PATH, ("key", "alignment", "kind", "runes", "seed", "phase", "best_phase", "log_mean_lr"),
              controls)
    write_tsv(CANDIDATES_PATH, ("key", "alignment", "runes", "phases", "best_phase", "best_phase_log_lr",
                                "log_mean_lr", "verdict"),
              [(*d, verdict[(d[0], d[1])]) for d in decodes])
    worst_negative = max(r[7] for r in controls if r[2] != "positive")
    log.info("worst negative control %.2f; void=%s", worst_negative, void)
    for state in ("PASS", "EXCLUDED", "untestable"):
        cells = sorted(k for k, v in verdict.items() if v == state)
        log.info("%s: %d %s", state, len(cells), cells)
    return 0


if __name__ == "__main__":
    sys.exit(main())
