from unittest import TestCase
import notes
import chords
import config
import rhythm
from notes import MIDI_VALUES


class TestChords(TestCase):

    def test_chord_progression(self):
        chord_progression = chords.ChordProgression()

        set_config(chord_progression)

        chord_progression.set().measure(0).beat(0).commit('C')
        chord_progression.set().measure(0).beat(2).commit('A-')
        chord_progression.set().measure(1).beat(0).commit('E-')
        chord_progression.set().measure(1).beat(2).commit('G')
        chord_progression.set().measure(2).beat(0).commit('A-')
        chord_progression.set().measure(2).beat(2).commit('C')
        chord_progression.set().measure(3).beat(0).commit('G')
        chord_progression.set().measure(3).beat(2).commit('C')

        self.assertEqual(chord_progression[(1 * (config.resolution * 4)) + (1 * config.resolution)],
                         chords.parse('E-'))
        self.assertEqual(chord_progression[(1 * (config.resolution * 4)) + (3 * config.resolution) + 5],
                         chords.parse('G'))
        self.assertEqual(chord_progression[(3 * (config.resolution * 4)) + (3 * config.resolution) + 2],
                         chords.parse('C'))

    def test_note_above(self):
        chord = chords.MajorChord(MIDI_VALUES['C1'])
        above = chord.note_above(MIDI_VALUES['E1'])
        above_with_note_object = chord.note_above(notes.parse(MIDI_VALUES['E1']))

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
        chord_progression = chords.ChordProgression()

        set_config(chord_progression)

        chord_progression.set().measure(0).beat(0).commit('C')
        chord_progression.set().measure(0).beat(1).commit('A-')
        chord_progression.set().measure(0).beat(2).commit('E-')
        chord_progression.set().measure(0).beat(3).commit('G')
        chord_progression.set().measure(3).beat(0).commit('G')
        chord_progression.set().measure(3).beat(2).commit('C')

        self.assertEqual(4, len(chord_progression.chords_in_measure(0)))
        self.assertEqual(0, len(chord_progression.chords_in_measure(1)))
        self.assertEqual(2, len(chord_progression.chords_in_measure(3)))

    def test__ChordProgression_root_in_bass(self):
        root_in_bass = chords.parse('C')
        root_not_in_bass = chords.parse('C/G')

        root_not_in_bass.root_in_bass()

        self.assertTrue(root_in_bass.root_in_bass())
        self.assertFalse(root_not_in_bass.root_in_bass())


def set_config(chord_progression):
    time_signatures = rhythm.TimeSignatures()
    time_signatures[0] = rhythm.TimeSignature(numerator=4, denominator=4)

    config.chord_progression = chord_progression
    config.time_signatures = time_signatures
