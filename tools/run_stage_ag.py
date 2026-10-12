"""Stage AG: constants and number streams written in base 29 as the key (TODO.md, declared 2026-10-12 in 7c83e52
before this script existed).

Ten sources, each as exact base-29 digits (key values 0–28, no mapping): π, e, φ, √2, √3, ln 2, √3301 (integer part
first), and the concatenated base-29 digits of the primes (Copeland–Erdős), of 1, 2, 3, … (Champernowne) and of
φ(p) = p − 1. The key is read from an unknown start s ∈ [0, 1000) under a uniform prior (`detect.log_lr(starts=)`,
computed by `fastdetect`), drift-tolerant, in 3 modes × 29 shifts × 10 alignments: 8,700 decodes.

Declared rule: PASS iff log LR ≥ 30. A (source, alignment, mode) is excluded iff all 29 shifts decode ≤ −10 and the
source's controls pass (positives ≥ 30, negatives < 30, at 729 and 3,316 runes, rekey fresh and next).

Deterministic. Usage: python -m tools.run_stage_ag [--quick]   (--quick: controls and shifts 0–1 on sections 7 and 10
only, writes nothing)
"""

from __future__ import annotations

import argparse
import logging
import random
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from itertools import count

from tools.lpcore import detect, fastdetect, keys, stats
from tools.lpcore.ciphers import primes
from tools.lpcore.corpus import REPO_ROOT, load_corpus
from tools.lpcore.gematria import N
from tools.lpcore.verify import load_translation
from tools.run_stage_x import write_tsv

log = logging.getLogger("stage_ag")

CANDIDATES_PATH = REPO_ROOT / "reference" / "findings" / "stage_ag_candidates.tsv"
CONTROLS_PATH = REPO_ROOT / "reference" / "findings" / "stage_ag_controls.tsv"
STARTS = 1000
EXCLUDE = -10.0
CONTROL_SIZES = (729, 3316)
SEED = 3301


def digit_count(longest_cipher: int) -> int:
    """Enough digits that any start plus two key steps per rune stays inside the source."""
    return STARTS + 2 * longest_cipher + 2


def sources(length: int) -> dict[str, list[int]]:
    out = {name: keys.constant_digits(name, length) for name in keys.CONSTANTS}
    out["copeland-erdos"] = keys.concatenated_digits(primes(), length)
    out["champernowne"] = keys.concatenated_digits(count(1), length)
    out["prime-totients"] = keys.concatenated_digits((p - 1 for p in primes()), length)
    return out


_STATE: dict[str, object] = {}


def _init_worker(length: int) -> None:
    corpus = load_corpus()
    _STATE["sources"] = sources(length)
    ciphers = {str(s): corpus.segment_runes(s) for s in stats.UNSOLVED_SEGMENTS}
    ciphers["7-15"] = [r for s in stats.UNSOLVED_SEGMENTS for r in corpus.segment_runes(s)]
    _STATE["ciphers"] = ciphers
    words = keys.solved_plaintext_words(corpus, load_translation())
    _STATE["q"] = detect.unigram([r for w in words for r in w])


def score(cipher: list[int], key: list[int], q: list[float], mode: str, shift: int) -> float:
    return fastdetect.log_lr(cipher, key, q, mode=mode, shift=shift, starts=range(STARTS))


def _score(job: tuple[str, str, str, int]) -> tuple:
    name, segment, mode, shift = job
    cipher = _STATE["ciphers"][segment]
    value = score(cipher, _STATE["sources"][name], _STATE["q"], mode, shift)
    return name, "continuous" if segment == "7-15" else "per-section", segment, mode, shift, len(cipher), f"{value:.2f}"


def controls(fam: dict[str, list[int]], q: list[float], plain: list[int]) -> list[tuple]:
    """Positive: the source's own encryption (dodging, keep 0.19) from a random start < STARTS. Negative: a random key."""
    rng = random.Random(SEED)
    rows = []
    for name, key in fam.items():
        for size in CONTROL_SIZES:
            text = (plain * (size // len(plain) + 1))[:size]
            for rekey in ("fresh", "next"):
                start = rng.randrange(STARTS)
                cipher = keys.encrypt_dodging(text, key[start:], keep=0.19, seed=rng.randrange(10 ** 9), rekey=rekey)
                wrong = keys.random_key(len(key), rng.randrange(10 ** 9))
                rows.append((name, size, rekey, start, f"{score(cipher, key, q, 'sub', 0):.2f}",
                             f"{score(cipher, wrong, q, 'sub', 0):.2f}"))
        log.info("controls %-15s positive min %s", name, min(float(r[4]) for r in rows if r[0] == name))
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--quick", action="store_true", help="controls, then shifts 0–1 on sections 7 and 10; no files")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    corpus = load_corpus()
    longest = sum(len(corpus.segment_runes(s)) for s in stats.UNSOLVED_SEGMENTS)
    length = digit_count(longest)
    fam = sources(length)
    words = keys.solved_plaintext_words(corpus, load_translation())
    plain = [r for w in words for r in w]
    q = detect.unigram(plain)
    log.info("sources: %d × %d digits; first digits %s", len(fam), length, {k: v[:4] for k, v in fam.items()})

    control_rows = controls(fam, q, plain)
    failing = {r[0] for r in control_rows if float(r[4]) < detect.THRESHOLD or float(r[5]) >= detect.THRESHOLD}
    log.info("controls: positive min %.1f, negative max %.1f; sources failing: %s",
             min(float(r[4]) for r in control_rows), max(float(r[5]) for r in control_rows), sorted(failing) or "none")

    segments = ["7", "10"] if args.quick else [str(s) for s in stats.UNSOLVED_SEGMENTS] + ["7-15"]
    shifts = range(2) if args.quick else range(N)
    jobs = [(name, seg, mode, shift) for name in fam for seg in segments for mode in detect.MODES for shift in shifts]
    log.info("scoring %d decodes", len(jobs))
    rows = []
    with ProcessPoolExecutor(max_workers=4, initializer=_init_worker, initargs=(length,)) as pool:
        for row in pool.map(_score, jobs, chunksize=8):
            rows.append(row)
            if len(rows) % 500 == 0:
                log.info("scored %d / %d", len(rows), len(jobs))
    best = max(rows, key=lambda r: float(r[-1]))
    real = [r for r in rows if r[2] != "10"]
    log.info("best decode: %s; best on a real section (not seg 10): %s", best, max(real, key=lambda r: float(r[-1])))
    passed = [r for r in rows if float(r[-1]) >= detect.THRESHOLD]
    cells: dict[tuple, list[float]] = {}
    for r in rows:
        cells.setdefault((r[0], r[2], r[3]), []).append(float(r[-1]))
    excluded = [c for c, v in cells.items() if c[0] not in failing and max(v) <= EXCLUDE]
    log.info("PASS: %d; excluded (source, alignment, mode): %d of %d", len(passed), len(excluded), len(cells))
    log.info("not excluded: %s", sorted(Counter(c[1] for c in cells if c not in excluded).items()))
    if args.quick:
        log.info("quick run: nothing written")
        return 0
    write_tsv(CANDIDATES_PATH, ("source", "alignment", "segment", "mode", "shift", "runes", "log_lr"), rows)
    write_tsv(CONTROLS_PATH, ("source", "runes", "rekey", "start", "positive_log_lr", "negative_log_lr"), control_rows)
    log.info("wrote %s and %s", CANDIDATES_PATH.name, CONTROLS_PATH.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
