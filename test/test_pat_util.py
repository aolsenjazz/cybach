from unittest import TestCase

import midi

from cybach import chords, transforms
from cybach import domain
from cybach import ks
from cybach import parts
from cybach.constants import RESOLUTION
from cybach import pat_util
from cybach.pat_util import normalize_resolution


class TestPatUtil(TestCase):

    def test__is_quantized(self):
        pattern = normalize_resolution(read_pattern('test/midi/resolution_too_small.mid'))
        self.assertTrue(pat_util.is_quantized(pattern))

    def test__contains_harmony(self):
        pattern = normalize_resolution(read_pattern('test/midi/contains_harmony.mid'))
        self.assertTrue(pat_util.contains_harmony(pattern))


def read_pattern(file_name):
    try:
        return midi.read_midifile(file_name)
    except TypeError:
        print 'Midi file is malformed. Try exporting a new one from any DAW'
        exit(2)
    raise Exception
