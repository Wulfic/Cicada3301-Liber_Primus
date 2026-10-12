"""Stage AH: "THE TOTIENT FUNCTION IS SACRED", arithmetic functions mod 29 as the key (TODO.md, declared 2026-10-12 in
17cba27 before this script existed).

Six sequences over n = 1, 2, 3, … mod 29, each raw and as a running sum ("chain"): φ(n), σ(n), Σ_{k ≤ n} φ(k), the prime
gaps p_{n+1} − p_n, φ(φ(n)) and n·φ(n). Stage AG's model, rule and controls: the key is read from an unknown start
s ∈ [0, 1000) under a uniform prior, drift-tolerant, 3 modes × 29 shifts × 10 alignments, so 12 × 870 = 10,440 decodes.
PASS iff log LR ≥ 30; (source, alignment, mode) excluded iff all 29 shifts ≤ −10 and the source's controls pass.

Deterministic. Usage: python -m tools.run_stage_ah [--quick]   (--quick: controls only, writes nothing)
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from tools.lpcore import detect, keys, stats
from tools.lpcore.corpus import REPO_ROOT, load_corpus
from tools.lpcore.gematria import N
from tools.lpcore.verify import load_translation
from tools.run_stage_ag import EXCLUDE, controls, digit_count, score
from tools.run_stage_x import write_tsv

log = logging.getLogger("stage_ah")

CANDIDATES_PATH = REPO_ROOT / "reference" / "findings" / "stage_ah_candidates.tsv"
CONTROLS_PATH = REPO_ROOT / "reference" / "findings" / "stage_ah_controls.tsv"
SEQUENCES = ("totient", "sigma", "totient-sum", "prime-gaps", "totient-of-totient", "n-times-totient")


def totients(limit: int) -> np.ndarray:
    """φ(n) for n = 0…limit by the sieve (φ(0) = 0)."""
    phi = np.arange(limit + 1, dtype=np.int64)
    for p in range(2, limit + 1):
        if phi[p] == p:                      # p is prime: nothing below has touched it
            phi[p::p] -= phi[p::p] // p
    return phi


def divisor_sums(limit: int) -> np.ndarray:
    sigma = np.zeros(limit + 1, dtype=np.int64)
    for d in range(1, limit + 1):
        sigma[d::d] += d
    return sigma


def primes_up_to(limit: int) -> np.ndarray:
    sieve = np.ones(limit + 1, dtype=bool)
    sieve[:2] = False
    for p in range(2, int(limit ** 0.5) + 1):
        if sieve[p]:
            sieve[p * p::p] = False
    return np.flatnonzero(sieve)


def sequences(length: int) -> dict[str, np.ndarray]:
    """The six raw sequences, n = 1…length, as integers (not yet reduced)."""
    phi = totients(length)
    n = np.arange(1, length + 1, dtype=np.int64)
    plist = primes_up_to(20 * length)
    if len(plist) < length + 1:
        raise ValueError("prime sieve too small")
    return {
        "totient": phi[1:],
        "sigma": divisor_sums(length)[1:],
        "totient-sum": np.cumsum(phi[1:]),
        "prime-gaps": np.diff(plist[:length + 1]),
        "totient-of-totient": phi[phi[1:]],
        "n-times-totient": n * phi[1:],
    }


def sources(length: int) -> dict[str, list[int]]:
    out = {}
    for name, seq in sequences(length).items():
        raw = seq % N
        out[f"{name} raw"] = raw.tolist()
        out[f"{name} chain"] = (np.cumsum(raw) % N).tolist()
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


def _score(job: tuple[str, str, str, int]) -> tuple:
    name, segment, mode, shift = job
    cipher = _STATE["ciphers"][segment]
    value = score(cipher, _STATE["sources"][name], _STATE["q"], mode, shift)
    return name, "continuous" if segment == "7-15" else "per-section", segment, mode, shift, len(cipher), f"{value:.2f}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--quick", action="store_true", help="controls only; LP2 not scored, nothing written")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    corpus = load_corpus()
    length = digit_count(sum(len(corpus.segment_runes(s)) for s in stats.UNSOLVED_SEGMENTS))
    fam = sources(length)
    words = keys.solved_plaintext_words(corpus, load_translation())
    plain = [r for w in words for r in w]
    q = detect.unigram(plain)
    log.info("sources: %d × %d values; first values %s", len(fam), length, {k: v[:5] for k, v in fam.items()})
    log.info("value spread (max share of one residue): %s",
             {k: round(max(Counter(v).values()) / len(v), 3) for k, v in fam.items()})

    control_rows = controls(fam, q, plain)
    failing = {r[0] for r in control_rows if float(r[4]) < detect.THRESHOLD or float(r[5]) >= detect.THRESHOLD}
    log.info("controls: positive min %.1f, negative max %.1f; sources failing: %s",
             min(float(r[4]) for r in control_rows), max(float(r[5]) for r in control_rows), sorted(failing) or "none")
    if args.quick:
        log.info("quick run: LP2 not scored, nothing written")
        return 0

    segments = [str(s) for s in stats.UNSOLVED_SEGMENTS] + ["7-15"]
    jobs = [(name, seg, mode, shift) for name in fam for seg in segments for mode in detect.MODES for shift in range(N)]
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
    log.info("not excluded by segment: %s", sorted(Counter(c[1] for c in cells if c not in excluded).items()))
    write_tsv(CANDIDATES_PATH, ("source", "alignment", "segment", "mode", "shift", "runes", "log_lr"), rows)
    write_tsv(CONTROLS_PATH, ("source", "runes", "rekey", "start", "positive_log_lr", "negative_log_lr"), control_rows)
    log.info("wrote %s and %s", CANDIDATES_PATH.name, CONTROLS_PATH.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
