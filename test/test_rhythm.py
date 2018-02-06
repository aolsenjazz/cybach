from unittest import TestCase
import notes
import chords
import rhythm
import config

from notes import MIDI_VALUES


class TestRhythm(TestCase):

    def test__sample_position(self):
        ts = rhythm.TimeSignatures()
        ts[0] = rhythm.TimeSignature(numerator=4, denominator=4)
        ts[config.resolution * 4] = rhythm.TimeSignature(numerator=6, denominator=8)
        ts[config.resolution * 4 + (config.resolution / 2) * 6] = rhythm.TimeSignature(numerator=3, denominator=2)

        measure_index = 4
        beat_index = 1
        sample_position = (config.resolution * 4) + (config.resolution / 2 * 6) + (config.resolution * 2 * 3 * 2) + \
                          (beat_index * config.resolution * 2)

        self.assertEqual(sample_position, ts.sample_position(measure_index, beat_index))

    def test__phrase_combinations(self):
        beats_per_bar = 7
        total_combinations = 5

        self.assertEqual(total_combinations, len(rhythm.phrase_combinations(beats_per_bar)))