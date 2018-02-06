from unittest import TestCase
import notes
import chords
import config

from notes import MIDI_VALUES

class TestChords(TestCase):

    def test_chord_progression(self):
        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C')
        chord_progression[(0 * (config.resolution * 4)) + (2 * config.resolution)] = chords.parse('A-')
        chord_progression[(1 * (config.resolution * 4)) + (0 * config.resolution)] = chords.parse('E-')
        chord_progression[(1 * (config.resolution * 4)) + (2 * config.resolution)] = chords.parse('G')
        chord_progression[(2 * (config.resolution * 4)) + (0 * config.resolution)] = chords.parse('A-')
        chord_progression[(2 * (config.resolution * 4)) + (2 * config.resolution)] = chords.parse('C')
        chord_progression[(3 * (config.resolution * 4)) + (0 * config.resolution)] = chords.parse('G')
        chord_progression[(3 * (config.resolution * 4)) + (2 * config.resolution)] = chords.parse('C')

        self.assertEqual(chord_progression[(1 * (config.resolution * 4)) + (1 * config.resolution)], chords.CHORDS['E-'])
        self.assertEqual(chord_progression[(1 * (config.resolution * 4)) + (3 * config.resolution) + 5], chords.CHORDS['G'])
        self.assertEqual(chord_progression[(3 * (config.resolution * 4)) + (3 * config.resolution) + 2], chords.CHORDS['C'])

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

