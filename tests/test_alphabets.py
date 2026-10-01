"""Stage S: the label-free detector for per-position alphabets c_i = σ_{k_i}(p_i) (declared in TODO.md first).

The mechanics must hold before any named key is judged: FFT counts equal direct counts, the mean LR under a
uniform cipher is exactly 1, and a synthetic σ cipher scores far above the threshold while a shuffled key does not.
"""

from __future__ import annotations

import csv
import itertools
import math
import random
import unittest
from collections import Counter

import numpy as np

from tests.test_detect import C9_BONFERRONI, LP2, PLAIN, split_like_lp2
from tools import run_stage_s
from tools.lpcore import alphabets, detect, leak, stats
from tools.lpcore.gematria import N

ALPHA = alphabets.dm_alpha(PLAIN)


class TestDetectorMechanics(unittest.TestCase):
    def test_alpha_matches_the_plaintext_coincidence_rate(self) -> None:
        self.assertAlmostEqual(ALPHA, 1.1652, places=4)                        # declared in TODO stage S
        s = (ALPHA + 1) / (N * ALPHA + 1)                                       # E[Σθ²] of Dirichlet(α)
        self.assertAlmostEqual(s, 0.06224, places=5)

    def test_mean_lr_under_a_uniform_cipher_is_one(self) -> None:
        # Exact enumeration of every 3-rune cipher in one class: E[LR] = 1 is what gives the e^−T bound.
        total = sum(math.exp(alphabets.log_lr(seq, [0, 0, 0], ALPHA))
                    for seq in itertools.product(range(N), repeat=3))
        self.assertAlmostEqual(total / N ** 3, 1.0, places=9)

    def test_fft_counts_equal_direct_counts(self) -> None:
        rng = random.Random(5)
        cipher = [rng.randrange(N) for _ in range(60)]
        linear = [rng.randrange(7) for _ in range(100)]
        got = alphabets.phase_log_lrs(cipher, linear, 41, ALPHA, cyclic=False)
        want = [alphabets.log_lr(cipher, linear[t:t + 60], ALPHA) for t in range(41)]
        np.testing.assert_allclose(got, want, rtol=0, atol=1e-8)
        short = "ABCDEABQ"                                                      # cyclic, shorter than the cipher
        got = alphabets.phase_log_lrs(cipher, short, len(short), ALPHA, cyclic=True)
        want = [alphabets.log_lr(cipher, [short[(t + i) % len(short)] for i in range(60)], ALPHA)
                for t in range(len(short))]
        np.testing.assert_allclose(got, want, rtol=0, atol=1e-8)

    def test_bad_input_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            alphabets.phase_log_lrs([0, 1, 2], [0, 1, 2, 3], 3, ALPHA, cyclic=False)   # needs 5 key values
        with self.assertRaises(ValueError):
            alphabets.phase_log_lrs([0, 29], [0, 1], 1, ALPHA, cyclic=True)
        with self.assertRaises(ValueError):
            alphabets.log_lr([0, 1, 2], [0], ALPHA)

    def test_mean_over_phases_is_bounded_by_the_best_phase(self) -> None:
        rng = random.Random(9)
        cipher, key = [rng.randrange(N) for _ in range(200)], [rng.randrange(29) for _ in range(500)]
        score, best, top = alphabets.log_mean_lr(cipher, key, 500, ALPHA, cyclic=True)
        self.assertLessEqual(score, top)
        self.assertGreaterEqual(score, top - math.log(500))
        self.assertAlmostEqual(top, alphabets.log_lr(cipher, [key[(best + i) % 500] for i in range(200)], ALPHA),
                               places=8)


class TestPower(unittest.TestCase):
    """In step, the right key scores far above 30 at the smallest LP2 section size; a shuffled key does not."""

    def test_mod_29_classes_at_729_runes(self) -> None:
        rng = random.Random(11)
        key = [rng.randrange(N) for _ in range(5000)]
        phase = 1234
        cipher = alphabets.encrypt_alphabets(PLAIN[:729], key[phase:], keep=0.19, seed=1)
        score, best, _ = alphabets.log_mean_lr(cipher, key, len(key), ALPHA, cyclic=True)
        self.assertGreater(score, detect.THRESHOLD)
        self.assertEqual(best, phase)
        shuffled = key[:]
        rng.shuffle(shuffled)
        self.assertLess(alphabets.log_mean_lr(cipher, shuffled, len(key), ALPHA, cyclic=True)[0], detect.THRESHOLD)

    def test_doublet_dodging_matches_lp2(self) -> None:
        rng = random.Random(12)
        key = [rng.randrange(256) for _ in range(len(PLAIN))]
        cipher = alphabets.encrypt_alphabets(PLAIN, key, keep=0.19, seed=2)
        rate = sum(a == b for a, b in zip(cipher, cipher[1:])) / (len(cipher) - 1)
        self.assertLess(rate, 0.012)                                            # LP2: 0.66 %; no dodging: 3.4 %

    def test_one_percent_desync_kills_the_signal(self) -> None:
        # Why the stage is in-step only: dropping 1 key value in 100 smears the classes.
        rng = random.Random(13)
        key = [rng.randrange(N) for _ in range(3000)]
        drifted = [k for k in key if rng.random() >= 0.01]
        cipher = alphabets.encrypt_alphabets(PLAIN[:2000], drifted, keep=0.19, seed=3)
        self.assertLess(alphabets.log_lr(cipher, key, ALPHA), detect.THRESHOLD)


class TestC9CoversShortSigmaKeys(unittest.TestCase):
    """A σ key of period P ≤ 1000 in step repeats plaintext coincidences at lag P, so C9's scan sees it."""

    def test_sigma_periodic_keys_are_flagged_at_their_period(self) -> None:
        plain = (PLAIN * 5)[:sum(map(len, LP2))]
        for period in (500, 1000):
            rng = random.Random(period)
            key = [rng.randrange(256) for _ in range(period)] * (len(plain) // period + 1)
            streams = split_like_lp2(alphabets.encrypt_alphabets(plain, key, keep=0.19, seed=period))
            ((_, hits, total),) = stats.lag_scan(streams, [period])
            self.assertLess(leak.binom_sf(hits, total, stats.repeat_probability(streams)), C9_BONFERRONI)


def read_tsv(path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="	"))


def control_cipher(name: str, size: int, seed: int, text: list[int]) -> list[int]:
    """Rebuild one positive-control cipher of run 2 with a given control text."""
    key, phases, cyclic = run_stage_s.family(run_stage_s.PLAIN)[name]
    rng = random.Random(f"{run_stage_s.CONTROL_SEED}/{name}/{size}/{seed}")
    phase = rng.randrange(phases)
    if text is None:
        text = run_stage_s.control_text(size, rng)
    return alphabets.encrypt_alphabets(text, run_stage_s.key_from(key, phase, size, cyclic), keep=0.19,
                                       seed=rng.randrange(10**9))


class TestStageSRecorded(unittest.TestCase):
    """Stage S is VOID by its declared rule (TODO stage S): it excludes nothing. These tests pin why."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.decodes = read_tsv(run_stage_s.OUT_PATH)
        cls.controls = read_tsv(run_stage_s.CONTROLS_PATH)

    def test_recorded_family_is_complete(self) -> None:
        self.assertEqual(len(self.decodes), 20 * 10)
        self.assertEqual(len(self.controls), 20 * 3 * 2 * 2 + 20)

    def test_run_2_is_void(self) -> None:
        bad = [r for r in self.controls if r["kind"] == "negative" and float(r["log_mean_lr"]) >= detect.THRESHOLD]
        self.assertEqual([(r["key"], r["runes"], r["log_mean_lr"]) for r in bad],
                         [("liber_al_vel_legis letters", "12956", "53.49")])

    def test_real_data_null_holds_and_no_decode_scores(self) -> None:
        nulls = [float(r["log_mean_lr"]) for r in self.controls if r["kind"] == "lp2-null"]
        self.assertEqual(len(nulls), 20)
        self.assertAlmostEqual(max(nulls), -489.50, places=2)
        self.assertAlmostEqual(max(float(r["log_mean_lr"]) for r in self.decodes), 0.84, places=2)

    def test_a_recorded_decode_reproduces(self) -> None:
        row = next(r for r in self.decodes if r["key"] == "deor_poem letters" and r["segment"] == "7")
        key, phases, cyclic = run_stage_s.family(run_stage_s.PLAIN)["deor_poem letters"]
        value, _, _ = alphabets.log_mean_lr(LP2[0], key, phases, ALPHA, cyclic=cyclic)
        self.assertAlmostEqual(value, float(row["log_mean_lr"]), places=2)

    def test_run_1_diagnosis_tiled_text_made_the_control_periodic(self) -> None:
        tiled = (run_stage_s.PLAIN[::-1] * 5)[:12956]                           # run 1's control text
        cipher = control_cipher("plaintext rune", 12956, 0, tiled)
        same = sum(a == b for a, b in zip(cipher, cipher[2901:])) / (len(cipher) - 2901)
        self.assertAlmostEqual(same, 0.968, places=3)
        ((_, hits, total),) = stats.lag_scan([[r for s in LP2 for r in s]], [2901])
        self.assertEqual((hits, total), (328, 10055))

    def test_run_2_diagnosis_sigma_controls_are_not_flat(self) -> None:
        # Random σ per class leaves the cipher's marginal uneven; a DM score against uniform rewards that, so the
        # synthetic negative controls were never nulls. LP2 itself is flat (χ² 26.4).
        def chi2(c: list[int]) -> float:
            counts, e = Counter(c), len(c) / N
            return sum((counts[x] - e) ** 2 / e for x in range(N))
        self.assertAlmostEqual(chi2(control_cipher("liber_al_vel_legis letters", 12956, 0, None)), 1141.0, places=1)
        self.assertAlmostEqual(chi2(control_cipher("page_17.bin mod29", 12956, 0, None)), 355.6, places=1)


if __name__ == "__main__":
    unittest.main()
