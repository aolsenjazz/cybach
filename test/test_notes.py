from unittest import TestCase
from cybach import notes
from cybach import chords


class TestNotes(TestCase):

    def test_is_perfect_fifth(self):
        c = 0
        g = 7
        a = 9

        self.assertTrue(notes.is_perfect_fifth(c, g))
        self.assertFalse(notes.is_perfect_fifth(c, a))

    def test_is_perfect_fourth(self):
        c = 0
        f = 5
        a = 9

        self.assertTrue(notes.is_perfect_fourth(c, f))
        self.assertFalse(notes.is_perfect_fourth(c, a))

    def test_is_perfect_octave(self):
        c = 0
        c1 = 12
        a = 9

        self.assertTrue(notes.is_perfect_octave(c, c1))
        self.assertFalse(notes.is_perfect_octave(c, a))

    def test_is_perfect_interval(self):
        c = 0
        f = 5
        g = 7
        c1 = 12
        a = 9

        self.assertTrue(notes.is_perfect_interval(c, g))
        self.assertTrue(notes.is_perfect_interval(c, f))
        self.assertTrue(notes.is_perfect_interval(c, c1))
        self.assertFalse(notes.is_perfect_interval(c, a))

    def test_ionian(self):
        c_val = 0

        all_notes_length = 75
        all_pitches = notes.ionian(c_val)

        self.assertEqual(len(all_pitches), all_notes_length)
        self.assertTrue(notes.OCTAVES['C'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['D'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['E'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['F'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['G'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['A'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['B'][0] in all_pitches)

    def test_dorian(self):
        c_val = 0

        all_notes_length = 75
        all_pitches = notes.dorian(c_val)

        self.assertEqual(len(all_pitches), all_notes_length)
        self.assertTrue(notes.OCTAVES['C'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['D'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['D#'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['F'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['G'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['A'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['A#'][0] in all_pitches)

    def test_phrygian(self):
        c_val = 0

        all_notes_length = 75
        all_pitches = notes.phrygian(c_val)

        self.assertEqual(len(all_pitches), all_notes_length)
        self.assertTrue(notes.OCTAVES['C'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['C#'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['D#'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['F'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['G'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['G#'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['A#'][0] in all_pitches)

    def test_lydian(self):
        c_val = 0

        all_notes_length = 75
        all_pitches = notes.lydian(c_val)

        self.assertEqual(len(all_pitches), all_notes_length)
        self.assertTrue(notes.OCTAVES['C'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['D'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['E'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['F#'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['G'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['A'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['B'][0] in all_pitches)

    def test_mixolydian(self):
        c_val = 0

        all_notes_length = 75
        all_pitches = notes.mixolydian(c_val)

        self.assertEqual(len(all_pitches), all_notes_length)
        self.assertTrue(notes.OCTAVES['C'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['D'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['E'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['F'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['G'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['A'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['A#'][0] in all_pitches)

    def test_aeolian(self):
        c_val = 0

        all_notes_length = 75
        all_pitches = notes.aeolian(c_val)

        self.assertEqual(len(all_pitches), all_notes_length)
        self.assertTrue(notes.OCTAVES['C'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['D'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['D#'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['F'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['G'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['G#'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['A#'][0] in all_pitches)

    def test_locrian(self):
        c_val = 0

        all_notes_length = 75
        all_pitches = notes.locrian(c_val)

        self.assertEqual(len(all_pitches), all_notes_length)
        self.assertTrue(notes.OCTAVES['C'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['C#'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['D#'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['F'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['F#'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['G#'][0] in all_pitches)
        self.assertTrue(notes.OCTAVES['A#'][0] in all_pitches)

    def test_species(self):
        c = 24
        note_c = notes.Note('C')
        species_c = 'C'
        octave_c = 'C2'

        correct = 'C'

        self.assertEqual(notes.species(c), correct)
        self.assertEqual(notes.species(note_c), correct)
        self.assertEqual(notes.species(species_c), correct)
        self.assertEqual(notes.species(octave_c), correct)
