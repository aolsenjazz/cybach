from unittest import TestCase
from rhythm import time


class TestRhythm(TestCase):

    def test__sample_position(self):
        ts = time.TimeSignatures()

        four_four = time.TimeSignature(numerator=4, denominator=4)
        six_eight = time.TimeSignature(numerator=6, denominator=8)
        three_two = time.TimeSignature(numerator=3, denominator=2)

        ts[0] = four_four
        ts[four_four.samples_per_measure()] = six_eight
        ts[four_four.samples_per_measure() + six_eight.samples_per_measure()] = three_two

        measure_index = 3
        beat_index = 1
        sample_position = 1440

        ts.sample_position(measure_index, beat_index)

        self.assertEqual(sample_position, ts.sample_position(measure_index, beat_index))

    def test__phrase_combinations(self):
        beats_per_bar = 7
        total_combinations = 5

        self.assertEqual(total_combinations, len(time.phrase_combinations(beats_per_bar)))