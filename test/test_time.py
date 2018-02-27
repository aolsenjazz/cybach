from unittest import TestCase

import chords
import constants
import fileloader
import ks
from rhythm import time


class TestTime(TestCase):

    def tearDown(self):
        super(TestTime, self).tearDown()
        chords.clear()
        time.clear()
        ks.clear()

    def test__sample_position(self):
        measure_index = 4
        beat_index = 1
        sample_position = 1392

        should_be_1392 = time.measure(measure_index).beat(beat_index).start()

        self.assertEqual(sample_position, should_be_1392)

    def test__Beat_first_beat(self):
        fileloader.load(constants.TEST_MIDI + 'mixed_meter.mid', False)

        third_measure = 2
        first_beat = 0
        second_beat = 1

        self.assertTrue(time.measure(third_measure).beat(first_beat).first_beat())
        self.assertFalse(time.measure(third_measure).beat(second_beat).first_beat())

    def test__Beat_last_beat(self):
        fileloader.load(constants.TEST_MIDI + 'mixed_meter.mid', False)

        third_measure = 2
        last_beat = 5
        second_beat = 1

        self.assertTrue(time.measure(third_measure).beat(last_beat).last_beat())
        self.assertFalse(time.measure(third_measure).beat(second_beat).last_beat())

    def test__Sequence_measures(self):
        fileloader.load(constants.TEST_MIDI + 'mixed_meter.mid', False)

        number_of_measures = 11

        self.assertEqual(number_of_measures, len(time.measures().keys()))