from unittest import TestCase
import notes
import midi
import chords
import rhythm
from notes import MIDI_VALUES


class TestTs(TestCase):

    def test__is_big_beat(self):
        four_four = midi.TimeSignatureEvent(data=[4, 2])
        six_eight = midi.TimeSignatureEvent(data=[6, 3])
        twelve_eight = midi.TimeSignatureEvent(data=[12, 3])

        self.assertTrue(rhythm.is_big_beat(four_four, 0))
        self.assertTrue(rhythm.is_big_beat(four_four, 2))
        self.assertTrue(rhythm.is_big_beat(six_eight, 3))
        self.assertTrue(rhythm.is_big_beat(twelve_eight, 3))

        self.assertFalse(rhythm.is_big_beat(four_four, 1))
        self.assertFalse(rhythm.is_big_beat(six_eight, 5))
        self.assertFalse(rhythm.is_big_beat(twelve_eight, 2))
