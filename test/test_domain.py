from unittest import TestCase

import midi

from cybach import chords, transforms
from cybach import domain
from cybach import ks
from cybach import parts
from cybach.constants import RESOLUTION
from cybach.pat_util import normalize_resolution


class TestDomain(TestCase):
    def test_Note_contains_linear_motion(self):
        pattern = normalize_resolution(read_pattern('test/midi/linear_motion.mid'))
        sequence = domain.Sequence(track=pattern[0])

        has_linear_motion = sequence.beat_at(RESOLUTION * 2)
        has_linear_and_non_linear = sequence.beat_at(RESOLUTION)
        has_no_motion = sequence.beat_at(0)

        self.assertTrue(has_linear_motion.contains_linear_movement())
        self.assertFalse(has_linear_and_non_linear.contains_linear_movement())
        self.assertFalse(has_no_motion.contains_linear_movement())

def read_pattern(file_name):
    try:
        return midi.read_midifile(file_name)
    except TypeError:
        print 'Midi file is malformed. Try exporting a new one from any DAW'
        exit(2)
    raise Exception
