from unittest import TestCase
import notes
import chords
from notes import MIDI_VALUES

class TestChords(TestCase):

    def test_chord_progression(self):
        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C')
        chord_progression[(0 * 96) + (2 * 24)] = chords.parse('A-')
        chord_progression[(1 * 96) + (0 * 24)] = chords.parse('E-')
        chord_progression[(1 * 96) + (2 * 24)] = chords.parse('G')
        chord_progression[(2 * 96) + (0 * 24)] = chords.parse('A-')
        chord_progression[(2 * 96) + (2 * 24)] = chords.parse('C')
        chord_progression[(3 * 96) + (0 * 24)] = chords.parse('G')
        chord_progression[(3 * 96) + (2 * 24)] = chords.parse('C')

        self.assertEqual(chord_progression[(1 * 96) + (1 * 24)], chords.CHORDS['E-'])
        self.assertEqual(chord_progression[(1 * 96) + (3 * 24) + 5], chords.CHORDS['G'])
        self.assertEqual(chord_progression[(3 * 96) + (3 * 24) + 2], chords.CHORDS['C'])

    def test_note_above(self):
        chord = chords.MajorChord(MIDI_VALUES['C1'])
        above = chord.note_above(MIDI_VALUES['E1'])
        above_with_note_object = chord.note_above(notes.Note(MIDI_VALUES['E1']))

        self.assertEqual(above, MIDI_VALUES['G1'])
        self.assertEqual(above_with_note_object, MIDI_VALUES['G1'])

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

