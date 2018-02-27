from unittest import TestCase

import chords
import config
import constants
import fileloader
import ks
import pitches
from pitches import MIDI_VALUES
from rhythm import time


class TestChords(TestCase):

    def tearDown(self):
        super(TestChords, self).tearDown()
        chords.clear()
        time.clear()
        ks.clear()

    def test_note_above(self):
        chord = chords.MajorChord(MIDI_VALUES['C1'])
        above = chord.note_above(MIDI_VALUES['E1'])
        above_with_note_object = chord.note_above(pitches.parse(MIDI_VALUES['E1']))

        self.assertEqual(MIDI_VALUES['G1'], above)
        self.assertEqual(MIDI_VALUES['G1'], above_with_note_object)

    def test_MajorChord_indicates_dominant(self):
        chord = chords.parse('C')

        self.assertTrue(chord.indicates_dominant(MIDI_VALUES['D0'], MIDI_VALUES['G0']))
        self.assertFalse(chord.indicates_dominant(MIDI_VALUES['D0'], MIDI_VALUES['G0'], MIDI_VALUES['C0']))

    def test_MajorChord_indicates_subdominant(self):
        chord = chords.parse('C')

        self.assertTrue(chord.indicates_subdominant(MIDI_VALUES['D0'], MIDI_VALUES['F0']))
        self.assertFalse(chord.indicates_subdominant(MIDI_VALUES['D0'], MIDI_VALUES['B0'], MIDI_VALUES['F0']))

    def test_MinorChord_indicates_dominant(self):
        chord = chords.parse('C-')

        self.assertTrue(chord.indicates_dominant(MIDI_VALUES['B0'], MIDI_VALUES['G0']))
        self.assertFalse(chord.indicates_dominant(MIDI_VALUES['B0'], MIDI_VALUES['G0'], MIDI_VALUES['C0']))

    def test_MinorChord_indicates_subdominant(self):
        chord = chords.parse('C-')

        self.assertTrue(chord.indicates_subdominant(MIDI_VALUES['D0'], MIDI_VALUES['F0']))
        self.assertFalse(chord.indicates_subdominant(MIDI_VALUES['D0'], MIDI_VALUES['B0'], MIDI_VALUES['F0']))

    def test__ChordProgression_chords_in_measure(self):
        fileloader.load(constants.TEST_MIDI + 'mixed_meter.mid', False)

        measure_0 = time.measure(0)
        measure_1 = time.measure(1)
        measure_3 = time.measure(3)

        chords.write('C')
        chords.write('A-', measure=0, beat=1)
        chords.write('E-', measure=0, beat=2)
        chords.write('G', measure=0, beat=3)
        chords.write('G', measure=3, beat=0)
        chords.write('C', measure=3, beat=3)

        self.assertEqual(4, len(chords.in_measure(measure_0)))
        self.assertEqual(0, len(chords.in_measure(measure_1)))
        self.assertEqual(2, len(chords.in_measure(measure_3)))

    def test__ChordProgression_root_in_bass(self):
        root_in_bass = chords.parse('C')
        root_not_in_bass = chords.parse('C/G')

        root_not_in_bass.root_in_bass()

        self.assertTrue(root_in_bass.root_in_bass())
        self.assertFalse(root_not_in_bass.root_in_bass())


def set_config(chord_progression):
    time.add_signature(0, time.TimeSignature(numerator=4, denominator=4))

    config.chord_progression = chord_progression
