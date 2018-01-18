from unittest import TestCase

import midi

import chords, transforms
import domain
import ks
import motion
import parts
from notes import MIDI_VALUES
from constants import RESOLUTION
import constants
from pat_util import normalize_resolution


class TestMotion(TestCase):

    def test__note_duration_at_position(self):
        pattern = normalize_resolution(read_pattern(constants.TEST_MIDI + '2beat_join.mid'))
        sequence = domain.Sequence(pattern=pattern[0])

        self.assertEqual(motion.note_duration_at_position(0, sequence), 2)


def read_pattern(file_name):
    try:
        return midi.read_midifile(file_name)
    except TypeError:
        print 'Midi file is malformed. Try exporting a new one from any DAW'
        exit(2)
    raise Exception
