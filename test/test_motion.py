from unittest import TestCase

import midi

import constants
import fileloader
import motion
import chords
import config


class TestMotion(TestCase):

    def test__note_duration_at_position(self):
        fileloader.load(constants.TEST_MIDI + '2beat_join.mid', False)
        sequence = sequences.soprano

        self.assertEqual(motion.note_duration_at_position(0, sequence), 2)


def read_pattern(file_name):
    try:
        return midi.read_midifile(file_name)
    except TypeError:
        print 'Midi file is malformed. Try exporting a new one from any DAW'
        exit(2)
    raise Exception
