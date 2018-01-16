from unittest import TestCase

import midi

from cybach import chords, transforms
from cybach import domain
from cybach import ks
from cybach import constants
from cybach import parts
from cybach.constants import RESOLUTION
from cybach.pat_util import normalize_resolution


class TestDomain(TestCase):
    def test__Note_contains_linear_motion(self):
        pattern = normalize_resolution(read_pattern('test/midi/linear_motion.mid'))
        sequence = domain.Sequence(pattern=pattern[0])

        has_linear_motion = sequence.beat_at(RESOLUTION * 2)
        has_linear_and_non_linear = sequence.beat_at(RESOLUTION)
        has_no_motion = sequence.beat_at(0)

        self.assertTrue(has_linear_motion.contains_linear_movement())
        self.assertFalse(has_linear_and_non_linear.contains_linear_movement())
        self.assertFalse(has_no_motion.contains_linear_movement())

    def test__Beat_contains_motion(self):
        pattern = normalize_resolution(read_pattern('test/midi/linear_motion.mid'))
        sequence = domain.Sequence(pattern=pattern[0])

        self.assertFalse(sequence.beat_at(0).contains_motion())
        self.assertTrue(sequence.beat_at(24).contains_motion())

    def test__Sequence_note_duration_count(self):
        pattern = normalize_resolution(read_pattern('test/midi/linear_motion.mid'))
        sequence = domain.Sequence(pattern=pattern[0])

        number_of_sixteenths = 2
        number_of_eighths = 5

        self.assertEqual(sequence.note_duration_count().get(domain.SIXTEENTH_NOTE, 0), number_of_sixteenths)
        self.assertEqual(sequence.note_duration_count().get(domain.EIGHTH_NOTE, 0), number_of_eighths)


def read_pattern(file_name):
    try:
        return midi.read_midifile(file_name)
    except TypeError:
        print 'Midi file is malformed. Try exporting a new one from any DAW'
        exit(2)
    raise Exception
