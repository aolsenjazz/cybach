from unittest import TestCase
from rhythm import time
import config
import fileloader
import constants


class TestTime(TestCase):

    def test__sample_position(self):
        sequences.soprano = [1] * 2000

        time.add_signature(0, time.TimeSignature(numerator=4, denominator=4))
        time.add_signature(384, time.TimeSignature(numerator=6, denominator=8))
        time.add_signature(672, time.TimeSignature(numerator=3, denominator=2))

        measure_index = 3
        beat_index = 1
        sample_position = 1440

        should_be_1440 = time.measure(measure_index).beat(beat_index).start()

        self.assertEqual(sample_position, should_be_1440)
        time.clear()

    def test__Beat_first_beat(self):
        sequences.soprano = [1] * 2000

        time.add_signature(0, time.TimeSignature(numerator=4, denominator=4))
        time.add_signature(384, time.TimeSignature(numerator=6, denominator=8))
        time.add_signature(672, time.TimeSignature(numerator=3, denominator=2))

        third_measure = 2
        first_beat = 0
        second_beat = 1

        self.assertTrue(time.measure(third_measure).beat(first_beat).first_beat())
        self.assertFalse(time.measure(third_measure).beat(second_beat).first_beat())
        time.clear()

    def test__Beat_last_beat(self):
        sequences.soprano = [1] * 2000

        time.add_signature(0, time.TimeSignature(numerator=4, denominator=4))
        time.add_signature(384, time.TimeSignature(numerator=6, denominator=8))
        time.add_signature(672, time.TimeSignature(numerator=3, denominator=2))

        third_measure = 2
        last_beat = 2
        second_beat = 1

        self.assertTrue(time.measure(third_measure).beat(last_beat).last_beat())
        self.assertFalse(time.measure(third_measure).beat(second_beat).last_beat())
        time.clear()

    def test__Sequence_measures(self):
        fileloader.load(constants.TEST_MIDI + 'mixed_meter.mid', False)

        number_of_measures = 11

        self.assertEqual(number_of_measures, len(time.__measures.keys()))
        time.clear()