from unittest import TestCase

import midi

import chords, transforms
import domain
import ks
import constants
import parts
import songloader
from constants import RESOLUTION
from pat_util import normalize_resolution


class TestDomain(TestCase):

    def test__Note_contains_linear_motion(self):
        pattern = normalize_resolution(read_pattern(constants.TEST_MIDI + 'linear_motion.mid'))
        sequence = domain.Sequence(pattern=pattern[0])

        has_linear_motion = sequence.beat_at(RESOLUTION * 2)
        has_linear_and_non_linear = sequence.beat_at(RESOLUTION)
        has_no_motion = sequence.beat_at(0)

        self.assertTrue(has_linear_motion.contains_linear_movement())
        self.assertFalse(has_linear_and_non_linear.contains_linear_movement())
        self.assertFalse(has_no_motion.contains_linear_movement())

    def test__Beat_contains_motion(self):
        pattern = normalize_resolution(read_pattern(constants.TEST_MIDI + 'linear_motion.mid'))
        sequence = domain.Sequence(pattern=pattern[0])

        self.assertFalse(sequence.beat_at(0).contains_motion())
        self.assertTrue(sequence.beat_at(24).contains_motion())

    def test__Sequence_note_duration_count(self):
        pattern = normalize_resolution(read_pattern(constants.TEST_MIDI + 'linear_motion.mid'))
        sequence = domain.Sequence(pattern=pattern[0])

        number_of_sixteenths = 2
        number_of_eighths = 5

        self.assertEqual(sequence.note_duration_count().get(domain.SIXTEENTH_NOTE, 0), number_of_sixteenths)
        self.assertEqual(sequence.note_duration_count().get(domain.EIGHTH_NOTE, 0), number_of_eighths)

    def test__Sequence_measures(self):
        pattern = normalize_resolution(read_pattern(constants.TEST_MIDI + 'linear_motion.mid'))
        sequence = domain.Sequence(pattern=pattern[0])

        number_of_measures = 2

        self.assertEqual(len(sequence.measures()), number_of_measures)

    def test__Measure_sample_position(self):
        pattern = normalize_resolution(read_pattern(constants.TEST_MIDI + 'linear_motion.mid'))
        sequence = domain.Sequence(pattern=pattern[0])

        measure_index = 1
        measure_sample_duration = 4 * RESOLUTION
        measure_position = measure_index * measure_sample_duration

        measures = sequence.measures()

        self.assertEqual(measures[measure_index].sample_position(), measure_position)

    def test__Sequence_beat_index_in_measure(self):
        pattern = normalize_resolution(read_pattern(constants.TEST_MIDI + 'linear_motion.mid'))
        sequence = domain.Sequence(pattern=pattern[0])

        beat_index_in_composition = 5
        beat_index_in_measure = 1

        self.assertEqual(sequence.beat_index_in_measure(beat_index_in_composition * RESOLUTION), beat_index_in_measure)


def read_pattern(file_name):
    try:
        return midi.read_midifile(file_name)
    except TypeError:
        print 'Midi file is malformed. Try exporting a new one from any DAW'
        exit(2)
    raise Exception
