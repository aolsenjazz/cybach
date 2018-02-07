from unittest import TestCase
import notes
import chords
import rhythm
import config

from notes import MIDI_VALUES


class TestRhythm(TestCase):

    def test__sample_position(self):
        ts = rhythm.TimeSignatures()

        four_four = rhythm.TimeSignature(numerator=4, denominator=4)
        six_eight = rhythm.TimeSignature(numerator=6, denominator=8)
        three_two = rhythm.TimeSignature(numerator=3, denominator=2)

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

        self.assertEqual(total_combinations, len(rhythm.phrase_combinations(beats_per_bar)))