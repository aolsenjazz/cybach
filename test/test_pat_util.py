from unittest import TestCase

import midi

import chords, transforms
import domain
import constants
import ks
import parts

import pat_util


class TestPatUtil(TestCase):

    def test__is_quantized(self):
        pattern = read_pattern(constants.TEST_MIDI + 'resolution_too_small.mid')
        self.assertTrue(pat_util.is_quantized(pattern))

    def test__contains_harmony(self):
        pattern = read_pattern(constants.TEST_MIDI + 'contains_harmony.mid')
        self.assertTrue(pat_util.contains_harmony(pattern))


def read_pattern(file_name):
    try:
        return midi.read_midifile(file_name)
    except TypeError:
        print 'Midi file is malformed. Try exporting a new one from any DAW'
        exit(2)
    raise Exception
