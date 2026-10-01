"""Stage I: the drift-tolerant key detector and the periodic-key scan (declared in TODO.md before the run).

The detector's controls must pass before any candidate key is judged by it. Every number pinned here is the
observed value; the verdict rules were written first.
"""

from __future__ import annotations

import math
import unittest

from tools.lpcore import detect, keys, leak, stats
from tools.lpcore.corpus import load_corpus
from tools.lpcore.gematria import N
from tools.lpcore.solved import DIVINITY, FIRFUMFERENFE
from tools.lpcore.verify import load_translation

CORPUS = load_corpus()
TRANSLATION = load_translation()
WORDS = keys.solved_plaintext_words(CORPUS, TRANSLATION)
PLAIN = [r for w in WORDS for r in w]
Q = detect.unigram(PLAIN)
LP2 = [CORPUS.segment_runes(s) for s in stats.UNSOLVED_SEGMENTS]
C9_LAGS = range(11, 1001)
C9_BONFERRONI = 0.01 / len(C9_LAGS)


def q_without(segment: int) -> list[float]:
    """Unigram model built without the segment under test, so a control is not scored on its own text."""
    return detect.unigram([r for w in keys.solved_plaintext_words(CORPUS, TRANSLATION, exclude=(segment,)) for r in w])


def totient_key(length: int) -> list[int]:
    return [p - 1 for p in keys.prime_stream(length)]


def split_like_lp2(stream: list[int]) -> list[list[int]]:
    out, i = [], 0
    for s in LP2:
        out.append(stream[i:i + len(s)])
        i += len(s)
    return out


class TestDetectorMechanics(unittest.TestCase):
    def test_emission_ratio_has_mean_one_under_the_null(self) -> None:
        # E[r] = 1 for a uniform decode: this is what makes P(log LR ≥ T) ≤ e^−T.
        self.assertAlmostEqual(sum(detect.emission_ratios(Q)) / N, 1.0, places=12)

    def test_exhausted_key_carries_no_information(self) -> None:
        self.assertAlmostEqual(detect.log_lr(LP2[0][:50], [], Q), 0.0, places=9)   # pruning drops ~1e-11

    def test_pruning_only_lowers_the_ratio(self) -> None:
        cipher, key = LP2[0][:150], keys.random_key(400, 7)
        exact = detect.log_lr(cipher, key, Q, prune=0.0)
        self.assertLessEqual(detect.log_lr(cipher, key, Q, prune=1e-3), exact + 1e-9)
        self.assertAlmostEqual(detect.log_lr(cipher, key, Q), exact, places=6)

    def test_fixed_sync_equals_forward_without_drift(self) -> None:
        cipher, key = LP2[1][:200], keys.random_key(200, 3)
        self.assertAlmostEqual(detect.log_lr(cipher, key, Q, rho=0.0), detect.fixed_sync_log_lr(cipher, key, Q))

    def test_modes_and_shift(self) -> None:
        plain, key = PLAIN[:300], totient_key(300)
        for mode, enc in (("sub", lambda p, k: p + k), ("add", lambda p, k: p - k), ("beaufort", lambda p, k: k - p)):
            cipher = [enc(p, k + 5) % N for p, k in zip(plain, key)]
            with self.subTest(mode=mode):
                self.assertGreater(detect.log_lr(cipher, key, Q, mode=mode, shift=5), detect.THRESHOLD)
                self.assertLess(detect.log_lr(cipher, key, Q, mode=mode, shift=6), detect.THRESHOLD)
        with self.assertRaises(ValueError):
            detect.log_lr(plain, key, Q, mode="xor")


class TestDetectorControls(unittest.TestCase):
    """Declared controls (TODO stage I §3). They gate the candidate run."""

    def test_solved_sections_are_detected(self) -> None:
        seg1 = CORPUS.segment_runes(1)
        lr1 = detect.log_lr(seg1, list(DIVINITY) * 100, q_without(1))
        self.assertGreater(lr1, detect.THRESHOLD)
        self.assertAlmostEqual(lr1, 142.0, delta=0.5)
        # Plaintext F passes through without consuming key: a fixed-sync decode loses the key.
        self.assertLess(detect.fixed_sync_log_lr(seg1, list(DIVINITY) * 100, q_without(1)), 0.0)
        lr5 = detect.log_lr(CORPUS.segment_runes(5), list(FIRFUMFERENFE) * 40, q_without(5))
        self.assertGreater(lr5, detect.THRESHOLD)

    def test_an_end_misses_the_threshold_by_length(self) -> None:
        # DECLARED CONTROL FAILED, recorded as observed: AN END has only 85 runes, and at ≈ 0.35 nats per rune it
        # scores 29.6 < 30. The detector needs ≳ 100 runes in step. Every LP2 section but segment 10 has ≥ 729.
        seg16 = CORPUS.segment_runes(16)
        self.assertEqual(len(seg16), 85)
        lr = detect.log_lr(seg16, totient_key(200), q_without(16))
        self.assertAlmostEqual(lr, 29.6, delta=0.1)
        self.assertLess(lr, detect.THRESHOLD)

    def test_wrong_solved_key_is_rejected(self) -> None:
        self.assertLess(detect.log_lr(CORPUS.segment_runes(5), list(DIVINITY) * 50, Q), detect.THRESHOLD)

    def test_drifting_anti_doublet_rule_is_detected(self) -> None:
        key = totient_key(2 * len(PLAIN))
        cipher = keys.encrypt_dodging(PLAIN, key, keep=0.19, seed=1)
        self.assertLess(sum(a == b for a, b in zip(cipher, cipher[1:])) / (len(cipher) - 1), 0.01)  # LP2-like
        self.assertGreater(detect.log_lr(cipher, key, Q), detect.THRESHOLD)
        self.assertLess(detect.fixed_sync_log_lr(cipher, key, Q), 0.0)          # a naive decode misses it
        self.assertLess(detect.log_lr(cipher, keys.prime_stream(len(key)), Q), detect.THRESHOLD)

    def test_random_keys_stay_below_threshold_on_every_lp2_section(self) -> None:
        worst = max(detect.log_lr(seg, keys.random_key(len(seg) * 2, seed), Q) for seg in LP2 for seed in range(20))
        self.assertLess(worst, detect.THRESHOLD)


class TestC9PeriodicKeys(unittest.TestCase):
    """C9: no lag 11–1000 shows the excess repeats a periodic key leaves (declared: Bonferroni 0.01 / 990)."""

    def periodic_cipher(self, period: int, rekey: str) -> list[list[int]]:
        plain = (PLAIN * 5)[:sum(map(len, LP2))]
        key = keys.random_key(period, 1000 + period) * (2 * len(plain) // period + 2)
        return split_like_lp2(keys.encrypt_dodging(plain, key, keep=0.19, seed=period, rekey=rekey))

    def lag_p(self, streams: list[list[int]], lag: int) -> float:
        ((_, hits, total),) = stats.lag_scan(streams, [lag])
        return leak.binom_sf(hits, total, stats.repeat_probability(streams))

    def test_positive_controls(self) -> None:
        # Under a rule that keeps the key in step, every period is visible; a drifting rule hides periods above ~25.
        for period in (16, 100, 1000):
            self.assertLess(self.lag_p(self.periodic_cipher(period, "fresh"), period), C9_BONFERRONI)
        self.assertLess(self.lag_p(self.periodic_cipher(16, "next"), 16), C9_BONFERRONI)
        self.assertLess(self.lag_p(self.periodic_cipher(25, "next"), 25), C9_BONFERRONI)

    def test_no_period_in_the_unsolved_text(self) -> None:
        p0 = stats.repeat_probability(LP2)
        scan = [(m, leak.binom_sf(h, t, p0)) for m, h, t in stats.lag_scan(LP2, C9_LAGS)]
        lag, p = min(scan, key=lambda r: r[1])
        self.assertGreater(p, C9_BONFERRONI)                                    # verdict: no periodic key
        self.assertEqual(lag, 717)
        self.assertAlmostEqual(math.log10(p), math.log10(3.36e-4), places=2)

    def test_fibonacci_and_lucas_mod_29_are_periodic(self) -> None:
        # Pisano period π(29) = 14, so these sequences are period-14 keys, inside C9 and C5's reach.
        for a, b in ((0, 1), (2, 1)):
            seq = [a, b]
            for _ in range(60):
                seq.append((seq[-1] + seq[-2]) % N)
            self.assertEqual(seq[:30], seq[14:44])


if __name__ == "__main__":
    unittest.main()
