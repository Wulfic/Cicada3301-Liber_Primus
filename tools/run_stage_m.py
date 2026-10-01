"""Stage M: the scan 66–68 base-60 grid as a key (TODO.md, declared 2026-10-01 before this script first ran).

Scores G-B (bytes), G-5 (5-bit groups) and G-D (base-60 digits), all mod 29, with the drift-tolerant detector in
3 modes × 29 shifts × 12 alignments. Writes one row per decode to reference/findings/stage_m_candidates.tsv.
PASS means log LR ≥ detect.THRESHOLD (30 nats).

Deterministic. Usage: python -m tools.run_stage_m
"""

from __future__ import annotations

import logging
import sys
from concurrent.futures import ProcessPoolExecutor

from tools.lpcore import detect, keys, stats
from tools.lpcore.corpus import REPO_ROOT, load_corpus
from tools.lpcore.gematria import N
from tools.lpcore.verify import load_translation
from tools.run_stage_i import _score, write_rows

log = logging.getLogger("stage_m")

OUT_PATH = REPO_ROOT / "reference" / "findings" / "stage_m_candidates.tsv"


def grid_keys(corpus) -> dict[str, list[int]]:
    return {
        "G-B bytes": [v % N for v in keys.grid_bytes(corpus)],
        "G-5 5-bit groups": [v % N for v in keys.grid_5bit(corpus)],
        "G-D base-60 digits": [v % N for v in keys.grid_digits(corpus)],
    }


def alignments(corpus, key_length: int) -> dict[str, list[int]]:
    sections = {f"section {s}": corpus.segment_runes(s) for s in stats.UNSOLVED_SEGMENTS}
    seg15 = corpus.segment_runes(keys.GRID_SEGMENT)
    at = keys.grid_rune_offset(corpus)
    return {
        **sections,
        "LP2 continuous": [r for s in stats.UNSOLVED_SEGMENTS for r in corpus.segment_runes(s)],
        "after the grid": seg15[at:],
        "ending at the grid": seg15[max(0, at - key_length):at],
    }


def run() -> list[tuple]:
    corpus = load_corpus()
    q = detect.unigram([r for w in keys.solved_plaintext_words(corpus, load_translation()) for r in w])
    jobs = []
    for name, key in grid_keys(corpus).items():
        for where, cipher in alignments(corpus, len(key)).items():
            for mode in detect.MODES:
                for shift in range(N):
                    jobs.append((name, "grid", where, mode, shift, cipher, key, q))
    log.info("scoring %d decodes", len(jobs))
    with ProcessPoolExecutor() as pool:
        return list(pool.map(_score, jobs, chunksize=8))


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    rows = run()
    write_rows(rows, OUT_PATH)
    print(f"\n{len(rows)} decodes; false-positive bound {len(rows)} * e^-30 = {len(rows) * 9.36e-14:.1e}")
    for name in sorted({r[0] for r in rows}):
        best = max((r for r in rows if r[0] == name), key=lambda r: r[6])
        print(f"  {name:20s} best log LR {best[6]:8.2f} ({best[2]}, {best[3]}, shift {best[4]})")
    passed = [r for r in rows if r[6] >= detect.THRESHOLD]
    print(f"PASS (log LR >= {detect.THRESHOLD:.0f}): {len(passed)}")
    for r in passed:
        print("  ", r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
