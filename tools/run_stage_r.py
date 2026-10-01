"""Stage R: Cicada's own numbers and OutGuess payloads as wide-alphabet keys (TODO.md, declared 2026-10-01 in
commit 2c209dc, before this script first ran).

Every source is read cyclically from an unknown phase. `detect.log_lr(starts=…)` puts a uniform prior on the phase,
so each decode is one hypothesis with the e^−30 bound. Controls run first and are written to
stage_r_controls.tsv. The LP2 family (25 keys × 2 mappings × 3 modes × 29 shifts × 10 alignments) goes to
stage_r_candidates.tsv. PASS means log LR ≥ detect.THRESHOLD (30 nats).

Deterministic. Usage: python -m tools.run_stage_r [--quick]
"""

from __future__ import annotations

import argparse
import logging
import random
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from tools.lpcore import detect, fastdetect, keys, stats
from tools.lpcore.corpus import REPO_ROOT, load_corpus
from tools.lpcore.gematria import N
from tools.lpcore.verify import load_translation
from tools.run_stage_i import write_rows

log = logging.getLogger("stage_r")

OUT_PATH = REPO_ROOT / "reference" / "findings" / "stage_r_candidates.tsv"
CONTROLS_PATH = REPO_ROOT / "reference" / "findings" / "stage_r_controls.tsv"
OUTGUESS = REPO_ROOT / "data" / "outguess"
CONTROL_SIZES = (729, 3316)
CONTROL_SEED = 3301

# Sources outside data/ (community tier, see TODO stage R for provenance).
PS_131 = ("1041279065891998535982789873959431895640"
          "44251069556756437392269523726824238529590817"
          "39834390370374475764863415203423499357108713631")          # community_research.md §2b
PS_132 = PS_131 + "1"                                                    # archived tracker §9.5 variant
RSA_N_2014 = ("75579125746085351644267182920580212556413102071876330957950694457000592"
              "10248050757270234679993673844203148013173091173786572116639")   # people_2014.md, 1033.jpg
COOKIE_167 = "6941f707ff39d259ff71657a79cb6b54c184d2f0455810109c1a960860bde0e6"  # community_research.md §2c
COOKIE_761 = "7bc1e7805ccfa518920f0d94fc4e8f7dbd83287a03b337b89109cd2287befae5"
ONION_2_HEX_SOURCE = REPO_ROOT / "reference" / "community" / "people_2014.md"     # "Patience is a virtue" page

_KEYS: dict[str, list[int]] = {}
_CIPHERS: dict[str, list[int]] = {}
_Q: list[float] = []


def digit_groups(digits: str, width: int, phase: int) -> list[int]:
    if not digits.isdigit():
        raise ValueError("digit source contains a non-digit")
    return [int(digits[i:i + width]) for i in range(phase, len(digits) - width + 1, width)]


def page_00_bytes() -> bytes:
    text = (OUTGUESS / "page_00.txt").read_text(encoding="ascii")
    body = text.split("\n\n", 1)[1].split("-----BEGIN PGP SIGNATURE-----")[0]
    hexdigits = re.sub(r"\s", "", body)
    if len(hexdigits) != 1982:
        raise ValueError(f"page_00 hex has {len(hexdigits)} chars, expected 1982")
    return bytes.fromhex(hexdigits)


def onion_2_bytes() -> bytes:
    text = ONION_2_HEX_SOURCE.read_text(encoding="utf-8")
    found = re.findall(r"<!--Patience is a virtue-->\s*([0-9a-f]+)", text)
    if len(found) != 1 or len(found[0]) != 512:
        raise ValueError(f"second-onion hex not found once at 512 chars: {[len(f) for f in found]}")
    return bytes.fromhex(found[0])


def raw_sources(corpus) -> dict[str, tuple[list[int], int]]:
    """Each source as (values, V): V is the alphabet size the values are drawn from."""
    out: dict[str, tuple[list[int], int]] = {}
    for label, digits in (("PS131", PS_131), ("PS132", PS_132), ("RSA-n-2014", RSA_N_2014)):
        for phase in (0, 1):
            out[f"{label} pairs@{phase}"] = (digit_groups(digits, 2, phase), 100)
        for phase in (0, 1, 2):
            out[f"{label} triples@{phase}"] = (digit_groups(digits, 3, phase), 1000)
    hint = (OUTGUESS / "wisdom_hint.txt").read_bytes()
    byte_sources = {
        "cookie-167": bytes.fromhex(COOKIE_167),
        "cookie-761": bytes.fromhex(COOKIE_761),
        "AN-END-hash": keys.an_end_hash(corpus),
        "page_00-hex": page_00_bytes(),
        "onion-2-hex": onion_2_bytes(),
        "hint": hint,
        "hint-reversed": hint[::-1],
        "page_17.bin": (OUTGUESS / "page_17.bin").read_bytes(),
        "page_21.bin": (OUTGUESS / "page_21.bin").read_bytes(),
        "page_43.bin": (OUTGUESS / "page_43.bin").read_bytes(),
    }
    out.update({name: (list(data), 256) for name, data in byte_sources.items()})
    if len(out) != 25:
        raise AssertionError(f"declared 25 sources, built {len(out)}")
    return out


def map_values(values: list[int], alphabet: int, mapping: str) -> list[int]:
    if mapping == "mod":
        return [v % N for v in values]
    if mapping == "reject":
        cut = N * (alphabet // N)
        return [v % N for v in values if v < cut]
    raise ValueError(f"unknown mapping {mapping!r}")


def family(corpus) -> dict[str, list[int]]:
    return {f"{name} {mapping}": map_values(values, alphabet, mapping)
            for name, (values, alphabet) in raw_sources(corpus).items() for mapping in ("mod", "reject")}


def tiled(key: list[int], cipher_length: int) -> list[int]:
    """Enough cyclic copies that any phase plus 2 key steps per rune stays inside the list."""
    need = len(key) + 2 * cipher_length + 2
    return (key * (need // len(key) + 1))[:need]


def score_cyclic(cipher: list[int], key: list[int], q: list[float], mode: str, shift: int) -> float:
    """`detect.log_lr` with a uniform prior over every phase, computed by `fastdetect` (tested equal)."""
    return fastdetect.log_lr(cipher, tiled(key, len(cipher)), q, mode=mode, shift=shift, starts=range(len(key)))


def _init_worker() -> None:
    corpus = load_corpus()
    _KEYS.update(family(corpus))
    for s in stats.UNSOLVED_SEGMENTS:
        _CIPHERS[str(s)] = corpus.segment_runes(s)
    _CIPHERS["7-15"] = [r for s in stats.UNSOLVED_SEGMENTS for r in corpus.segment_runes(s)]
    words = keys.solved_plaintext_words(corpus, load_translation())
    _Q[:] = detect.unigram([r for w in words for r in w])


def _score(job: tuple[str, str, str, int]) -> tuple:
    name, segment, mode, shift = job
    cipher = _CIPHERS[segment]
    alignment = "continuous" if segment == "7-15" else "per-section"
    return name, alignment, segment, mode, shift, len(cipher), score_cyclic(cipher, _KEYS[name], _Q, mode, shift)


def controls(fam: dict[str, list[int]], q: list[float], plain: list[int]) -> list[tuple]:
    """Positive: the key's own encryption (dodging, keep 0.19) from a random phase. Negative: a random key."""
    rng = random.Random(CONTROL_SEED)
    rows = []
    for name, key in fam.items():
        for size in CONTROL_SIZES:
            text = (plain * (size // len(plain) + 1))[:size]
            for rekey in ("fresh", "next"):
                phase = rng.randrange(len(key))
                long_key = tiled(key, size)[phase:]
                cipher = keys.encrypt_dodging(text, long_key, keep=0.19, seed=rng.randrange(10**9), rekey=rekey)
                wrong = keys.random_key(len(key), rng.randrange(10**9))
                rows.append((name, size, rekey, phase,
                             score_cyclic(cipher, key, q, "sub", 0), score_cyclic(cipher, wrong, q, "sub", 0)))
        log.info("controls %-28s pos min %.1f", name, min(r[4] for r in rows if r[0] == name))
    return rows


def write_controls(rows: list[tuple], path: Path) -> None:
    lines = ["key\trunes\trekey\tphase\tpositive_log_lr\tnegative_log_lr"]
    lines += [f"{k}\t{n}\t{rk}\t{ph}\t{pos:.2f}\t{neg:.2f}" for k, n, rk, ph, pos, neg in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    log.info("wrote %d control rows to %s", len(rows), path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--quick", action="store_true", help="shifts 0-1 only; writes nothing")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    corpus = load_corpus()
    fam = family(corpus)
    words = keys.solved_plaintext_words(corpus, load_translation())
    plain = [r for w in words for r in w]
    q = detect.unigram(plain)
    log.info("family: %s", {k: len(v) for k, v in fam.items()})

    control_rows = controls(fam, q, plain)
    weak = [r for r in control_rows if r[4] < detect.THRESHOLD or r[5] >= detect.THRESHOLD]
    if not args.quick:
        write_controls(control_rows, CONTROLS_PATH)
    print(f"controls: {len(control_rows)} pairs; positive min {min(r[4] for r in control_rows):.1f}, "
          f"negative max {max(r[5] for r in control_rows):.1f}; failing {len(weak)}")

    segments = [str(s) for s in stats.UNSOLVED_SEGMENTS] + ["7-15"]
    shifts = range(2) if args.quick else range(N)
    by_cost = sorted(fam, key=lambda name: -len(fam[name]))       # longest phase sets first, for load balance
    jobs = [(name, seg, mode, shift) for name in by_cost for seg in segments
            for mode in detect.MODES for shift in shifts]
    log.info("scoring %d decodes", len(jobs))
    rows = []
    with ProcessPoolExecutor(initializer=_init_worker) as pool:
        for row in pool.map(_score, jobs, chunksize=4):
            rows.append(row)
            if len(rows) % 1000 == 0:
                log.info("scored %d / %d", len(rows), len(jobs))
    if not args.quick:
        write_rows(rows, OUT_PATH)

    print(f"\n{len(rows)} decodes; false-positive bound {len(rows)} * e^-30 = {len(rows) * 9.36e-14:.1e}")
    for name in by_cost:
        best = max((r for r in rows if r[0] == name), key=lambda r: r[6])
        print(f"  {name:30s} best {best[6]:9.2f} ({best[2]}, {best[3]}, shift {best[4]})")
    passed = [r for r in rows if r[6] >= detect.THRESHOLD]
    print(f"PASS (log LR >= {detect.THRESHOLD:.0f}): {len(passed)}")
    for r in passed:
        print("  ", r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
