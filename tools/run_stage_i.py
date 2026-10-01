"""Stage I candidate run (TODO.md, declared 2026-10-01 before this script first ran).

Part 1 scores every declared key-source hypothesis with the drift-tolerant detector and writes one row per
decode to reference/findings/stage_i_candidates.tsv. PASS means log LR ≥ detect.THRESHOLD (30 nats).
Part 2 decodes the 9-rune title of segment 10 with the scan-32 square's own numbers and checks both words
against an English vocabulary, after measuring how often random keys pass the same check.

Deterministic: same input, same output. Usage: python -m tools.run_stage_i [--quick]
"""

from __future__ import annotations

import argparse
import logging
import random
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from itertools import islice
from pathlib import Path

from tools.lpcore import detect, keys, stats
from tools.lpcore.ciphers import primes
from tools.lpcore.corpus import REPO_ROOT, load_corpus
from tools.lpcore.gematria import N, indices_to_latin, spellings_of
from tools.lpcore.verify import load_translation

log = logging.getLogger("stage_i")

OUT_PATH = REPO_ROOT / "reference" / "findings" / "stage_i_candidates.tsv"
VOCAB_SOURCES = ("emerson_essays.txt", "self_reliance.txt", "liber_al_vel_legis.txt", "deor_poem.txt")
NULL_TITLE_KEYS = 20000


# --- part 1: key-source family -------------------------------------------------------------------

def candidate_keys(words: list[tuple[int, ...]], length: int) -> dict[str, list[int]]:
    return {
        "K-A primes": keys.prime_stream(length),
        "K-C word sums": keys.word_sum_stream(words),
        "K-D plaintext values": keys.plaintext_value_stream(words),
    }


def _score(job: tuple) -> tuple:
    name, alignment, segment, mode, shift, cipher, key, q = job
    return name, alignment, segment, mode, shift, len(cipher), detect.log_lr(cipher, key, q, mode=mode, shift=shift)


def run_family(quick: bool) -> list[tuple]:
    corpus, translation = load_corpus(), load_translation()
    words = keys.solved_plaintext_words(corpus, translation)
    q = detect.unigram([r for w in words for r in w])
    sections = {s: corpus.segment_runes(s) for s in stats.UNSOLVED_SEGMENTS}
    continuous = [r for s in stats.UNSOLVED_SEGMENTS for r in sections[s]]
    family = candidate_keys(words, 2 * len(continuous))
    shifts = range(2) if quick else range(N)
    jobs = []
    for name, key in family.items():
        for mode in detect.MODES:
            for shift in shifts:
                for seg, cipher in sections.items():
                    jobs.append((name, "per-section", seg, mode, shift, cipher, key, q))
                jobs.append((name, "continuous", "7-15", mode, shift, continuous, key, q))
    log.info("scoring %d decodes (key lengths: %s)", len(jobs), {k: len(v) for k, v in family.items()})
    with ProcessPoolExecutor() as pool:
        rows = list(pool.map(_score, jobs, chunksize=4))
    return rows


def write_rows(rows: list[tuple], path: Path) -> None:
    lines = ["key\talignment\tsegment\tmode\tshift\trunes\tlog_lr_nats"]
    lines += [f"{k}\t{a}\t{s}\t{m}\t{sh}\t{n}\t{lr:.2f}" for k, a, s, m, sh, n, lr in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    log.info("wrote %d rows to %s", len(rows), path)


# --- part 2: the segment-10 title ----------------------------------------------------------------

def english_vocabulary(translation: dict[str, list[list[str]]]) -> set[tuple[int, ...]]:
    """Rune spellings of every word in the solved translation and the English corpora."""
    text = " ".join(c for paras in translation.values() for para in paras for c in para)
    for name in VOCAB_SOURCES:
        path = REPO_ROOT / "data" / "corpora" / name
        try:
            text += " " + path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            log.exception("cannot read vocabulary source %s", path)
            raise
    english = {w for w in re.findall(r"[A-Z]+", text.upper().replace("'", "").replace("’", ""))}
    return {s for w in english for s in spellings_of(w)}


def square_key_sources() -> dict[str, list[int]]:
    """The scan-32 square's numbers in spiral order, outward from the centre (16 terms each)."""
    fib: list[int] = []
    a, b = 0, 1
    while len(fib) < 16:
        if a not in fib:
            fib.append(a)
        a, b = b, a + b
    prime_list = list(islice(primes(), fib[-1] + 1))
    return {
        "cell values": stats.fibonacci_prime_square(),
        "primes p(F+1)": [prime_list[f] for f in fib],
        "phi = p(F+1) - 1": [prime_list[f] - 1 for f in fib],
        "ordinals F+1": [f + 1 for f in fib],
        "Fibonacci F": fib,
    }


def decode_title(title: list[tuple[int, ...]], key: list[int], mode: str) -> list[tuple[int, ...]]:
    flat = [r for w in title for r in w]
    ops = {"sub": lambda c, k: c - k, "add": lambda c, k: c + k, "beaufort": lambda c, k: k - c}
    plain = [ops[mode](c, k) % N for c, k in zip(flat, key)]
    out, i = [], 0
    for w in title:
        out.append(tuple(plain[i:i + len(w)]))
        i += len(w)
    return out


def run_title(vocab: set[tuple[int, ...]]) -> None:
    corpus = load_corpus()
    title = [w.runes for w in corpus.rune_words(10)]
    log.info("segment 10 words: %s", [indices_to_latin(w, "-") for w in title])
    length = sum(map(len, title))
    rng = random.Random(3301)
    chance = sum(
        all(w in vocab for w in decode_title(title, [rng.randrange(N) for _ in range(length)], "sub"))
        for _ in range(NULL_TITLE_KEYS)
    )
    rate = chance / NULL_TITLE_KEYS
    print(f"\nSegment 10 title: chance that a random key decodes both words into V = {chance}/{NULL_TITLE_KEYS} = {rate:.4%}")
    hits = 0
    tried = 0
    for name, values in square_key_sources().items():
        for direction, seq in (("outward", values[:length]), ("inward", values[::-1][:length])):
            for mode in detect.MODES:
                tried += 1
                plain = decode_title(title, [v % N for v in seq], mode)
                ok = all(w in vocab for w in plain)
                hits += ok
                print(f"  {'PASS' if ok else 'fail'}  {name:18s} {direction:8s} {mode:9s} "
                      f"{' '.join(indices_to_latin(w, '-') for w in plain)}")
    print(f"Title verdict: {hits}/{tried} decodes pass; expected by chance {tried * rate:.2f}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--quick", action="store_true", help="shifts 0-1 only, no TSV written (smoke test)")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    rows = run_family(args.quick)
    if not args.quick:
        write_rows(rows, OUT_PATH)
    passed = [r for r in rows if r[6] >= detect.THRESHOLD]
    print(f"\nFamily: {len(rows)} decodes, false-positive bound {len(rows)} * e^-30 = {len(rows) * 9.36e-14:.1e}")
    for name in sorted({r[0] for r in rows}):
        best = max((r for r in rows if r[0] == name), key=lambda r: r[6])
        print(f"  {name:22s} best log LR {best[6]:9.2f} ({best[1]}, seg {best[2]}, {best[3]}, shift {best[4]})")
    print(f"PASS (log LR >= {detect.THRESHOLD:.0f}): {len(passed)}")
    for r in passed:
        print("  ", r)

    run_title(english_vocabulary(load_translation()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
