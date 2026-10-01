"""Stage N: do the scan 66–68 grid's 256 bytes decrypt under LP-native keys? (TODO.md, declared 2026-10-01.)

Byte readings pass on ≥ 90 % printable ASCII or a known file signature; rune readings pass on
`detect.log_lr` ≥ 30. Writes every result to reference/findings/stage_n_results.tsv.

Deterministic. Usage: python -m tools.run_stage_n
"""

from __future__ import annotations

import logging
import sys
from collections.abc import Callable, Sequence
from itertools import islice

from tools.lpcore import detect, keys, stats
from tools.lpcore.ciphers import primes
from tools.lpcore.corpus import REPO_ROOT, Corpus, load_corpus
from tools.lpcore.gematria import N
from tools.lpcore.solved import DIVINITY, FIRFUMFERENFE
from tools.lpcore.verify import load_translation

log = logging.getLogger("stage_n")

OUT_PATH = REPO_ROOT / "reference" / "findings" / "stage_n_results.tsv"
PRINTABLE = set(range(0x20, 0x7F)) | {0x09, 0x0A, 0x0D}
PRINTABLE_PASS = 0.90
SIGNATURES: dict[str, bytes] = {
    "PNG": b"\x89PNG", "JPEG": b"\xff\xd8\xff", "GIF": b"GIF8", "gzip": b"\x1f\x8b", "zip": b"PK\x03\x04",
    "bzip2": b"BZh", "PDF": b"%PDF", "ELF": b"\x7fELF", "PGP armour": b"-----BEGIN PGP",
}

BYTE_OPS: dict[str, Callable[[int, int], int]] = {
    "xor": lambda b, k: b ^ k,
    "b-k": lambda b, k: (b - k) % 256,
    "b+k": lambda b, k: (b + k) % 256,
}


def byte_keys(corpus: Corpus) -> dict[str, list[int]]:
    h = list(keys.an_end_hash(corpus))
    grid_length = len(keys.grid_bytes(corpus))
    out = {
        "AN END hash": h,
        "AN END hash reversed": h[::-1],
        "phi(prime) mod 256": [(p - 1) % 256 for p in islice(primes(), grid_length)],
        "primes mod 256": [p % 256 for p in islice(primes(), grid_length)],
        "scan-32 square cells mod 256": [v % 256 for v in stats.fibonacci_prime_square()],
    }
    for word in ("DIVINITY", "FIRFUMFERENFE", "CIRCUMFERENCE"):
        out[f"ASCII {word}"] = list(word.encode())
        out[f"ASCII {word.lower()}"] = list(word.lower().encode())
    out["ASCII 3301"] = list(b"3301")
    return out


def apply_bytes(data: Sequence[int], key: Sequence[int], op: str) -> bytes:
    f = BYTE_OPS[op]
    return bytes(f(b, key[i % len(key)]) for i, b in enumerate(data))


def printable_fraction(data: bytes) -> float:
    return sum(b in PRINTABLE for b in data) / len(data)


def pgp_packet_fits(data: bytes) -> bool:
    """True if `data` is exactly one OpenPGP packet: a valid header whose body length is the rest of the data.

    A bare tag byte matches often. For 256-byte blocks, tests/test_grid.py records 4 hits in 20,000
    seeded random samples (0.020 %, or about 0.014 expected hits over 72 decodes at that measured rate).
    """
    if len(data) < 2 or not data[0] & 0x80:
        return False
    if data[0] & 0x40:                                   # new format: 1-, 2- or 5-octet length
        first = data[1]
        if first < 192:
            return first == len(data) - 2
        if first < 224 and len(data) >= 3:
            return ((first - 192) << 8) + data[2] + 192 == len(data) - 3
        return False
    length_type = data[0] & 0x03                         # old format: 1-, 2- or 4-octet length
    size = {0: 1, 1: 2, 2: 4}.get(length_type)
    if size is None or len(data) < 1 + size:
        return False
    return int.from_bytes(data[1:1 + size], "big") == len(data) - 1 - size


def signature(data: bytes) -> str:
    for name, magic in SIGNATURES.items():
        if data.startswith(magic):
            return name
    return "PGP packet" if pgp_packet_fits(data) else ""


def byte_results(corpus: Corpus) -> list[tuple]:
    grid = keys.grid_bytes(corpus)
    rows = []
    for direction, data in (("forward", grid), ("reversed", grid[::-1])):
        for name, key in byte_keys(corpus).items():
            for op in BYTE_OPS:
                out = apply_bytes(data, key, op)
                frac, sig = printable_fraction(out), signature(out)
                rows.append(("bytes", name, op, direction, f"{frac:.3f}", sig or "-", "",
                             "PASS" if frac >= PRINTABLE_PASS or sig else "fail"))
    return rows


def rune_results(corpus: Corpus, q: Sequence[float]) -> list[tuple]:
    rune_keys: dict[str, list[int]] = {
        "phi(prime)": [p - 1 for p in islice(primes(), 800)],
        "DIVINITY": list(DIVINITY) * 100,
        "FIRFUMFERENFE": list(FIRFUMFERENFE) * 60,
    }
    rows = []
    readings = {"bytes mod 29": [b % N for b in keys.grid_bytes(corpus)],
                "base-60 digits mod 29": [d % N for d in keys.grid_digits(corpus)]}
    for reading, cipher in readings.items():
        for direction, c in (("forward", cipher), ("reversed", cipher[::-1])):
            for mode in detect.MODES:
                for shift in range(N):
                    lr = detect.log_lr(c, [0] * len(c), q, mode=mode, shift=shift)
                    rows.append((reading, "constant", mode, f"{direction} shift {shift}", "", "", f"{lr:.2f}",
                                 "PASS" if lr >= detect.THRESHOLD else "fail"))
                for name, key in rune_keys.items():
                    lr = detect.log_lr(c, key, q, mode=mode)
                    rows.append((reading, name, mode, direction, "", "", f"{lr:.2f}",
                                 "PASS" if lr >= detect.THRESHOLD else "fail"))
    return rows


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    corpus = load_corpus()
    q = detect.unigram([r for w in keys.solved_plaintext_words(corpus, load_translation()) for r in w])
    rows = byte_results(corpus) + rune_results(corpus, q)
    header = "reading\tkey\top_or_mode\tdirection\tprintable\tsignature\tlog_lr_nats\tverdict"
    OUT_PATH.write_text(header + "\n" + "\n".join("\t".join(map(str, r)) for r in rows) + "\n",
                        encoding="utf-8", newline="\n")
    log.info("wrote %d rows to %s", len(rows), OUT_PATH)
    byte_rows = [r for r in rows if r[0] == "bytes"]
    rune_rows = [r for r in rows if r[0] != "bytes"]
    print(f"\nbyte decryptions: {len(byte_rows)}; best printable fraction "
          f"{max(float(r[4]) for r in byte_rows):.3f} (pass at {PRINTABLE_PASS}); "
          f"signatures: {[r for r in byte_rows if r[5] != '-']}")
    print(f"rune readings: {len(rune_rows)}; best log LR {max(float(r[6]) for r in rune_rows):.2f} "
          f"(pass at {detect.THRESHOLD:.0f})")
    passed = [r for r in rows if r[7] == "PASS"]
    print(f"PASS: {len(passed)}")
    for r in passed:
        print("  ", r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
