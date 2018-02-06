from unittest import TestCase

import midi

import chords, transforms
import domain
import ks
import constants
import rhythm
import config
import parts
import songloader



class TestDomain(TestCase):

    def test__Note_contains_linear_motion(self):
        pattern = read_pattern(constants.TEST_MIDI + 'linear_motion.mid')
        sequence = domain.Sequence(pattern=pattern[0])

        set_config(sequence)

        has_linear_motion = sequence.beat_at(config.resolution * 2)
        has_linear_and_non_linear = sequence.beat_at(config.resolution)
        has_no_motion = sequence.beat_at(0)

        self.assertTrue(has_linear_motion.contains_linear_movement())
        self.assertFalse(has_linear_and_non_linear.contains_linear_movement())
        self.assertFalse(has_no_motion.contains_linear_movement())

    def test__Beat_contains_motion(self):
        pattern = read_pattern(constants.TEST_MIDI + 'linear_motion.mid')
        sequence = domain.Sequence(pattern=pattern[0])

        set_config(sequence)

        self.assertFalse(sequence.beat_at(0).contains_motion())
        self.assertTrue(sequence.beat_at(config.resolution).contains_motion())

    def test__Sequence_note_duration_count(self):
        pattern = read_pattern(constants.TEST_MIDI + 'linear_motion.mid')
        sequence = domain.Sequence(pattern=pattern[0])

        number_of_sixteenths = 2
        number_of_eighths = 5

        set_config(sequence)

        self.assertEqual(sequence.note_duration_count().get(constants.SIXTEENTH_NOTE, 0), number_of_sixteenths)
        self.assertEqual(sequence.note_duration_count().get(constants.EIGHTH_NOTE, 0), number_of_eighths)

    def test__Sequence_measures(self):
        pattern = read_pattern(constants.TEST_MIDI + 'linear_motion.mid')
        sequence = domain.Sequence(pattern=pattern[0])

        number_of_measures = 2

        set_config(sequence)

        length = len(sequence.measures())
        self.assertEqual(number_of_measures, length)

    def test__Measure_sample_position(self):
        pattern = read_pattern(constants.TEST_MIDI + 'linear_motion.mid')
        sequence = domain.Sequence(pattern=pattern[0])

        measure_index = 1
        measure_sample_duration = 4 * config.resolution
        measure_position = measure_index * measure_sample_duration

        measures = sequence.measures()

        set_config(sequence)

        self.assertEqual(measures[measure_index].sample_position(), measure_position)

    def test__Sequence_beat_index_in_measure(self):
        pattern = read_pattern(constants.TEST_MIDI + 'linear_motion.mid')
        sequence = domain.Sequence(pattern=pattern[0])

        beat_index_in_composition = 5
        beat_index_in_measure = 1

        set_config(sequence)

        self.assertEqual(sequence.beat_index_in_measure(beat_index_in_composition * config.resolution), beat_index_in_measure)


def set_config(soprano):
    time_signatures = rhythm.TimeSignatures()
    time_signatures[0] = rhythm.TimeSignature(numerator=4, denominator=4)

    chord_progression = chords.ChordProgression()
    chord_progression[0] = chords.parse('C')

    key_signatures = ks.KeySignatures()
    key_signatures[0] = chords.parse('C')

    config.soprano = soprano
    config.chord_progression = chord_progression
    config.key_signatures = key_signatures
    config.time_signatures = time_signatures


def read_pattern(file_name):
    try:
        return midi.read_midifile(file_name)
    except TypeError:
        print 'Midi file is malformed. Try exporting a new one from any DAW'
        exit(2)
    raise Exception
