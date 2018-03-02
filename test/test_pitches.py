from unittest import TestCase

import pitches


class TestPitches(TestCase):

    def test_is_perfect_fifth(self):
        c = 0
        g = 7
        a = 9

        self.assertTrue(pitches.is_perfect_fifth(c, g))
        self.assertFalse(pitches.is_perfect_fifth(c, a))

    def test_is_perfect_fourth(self):
        c = 0
        f = 5
        a = 9

        self.assertTrue(pitches.is_perfect_fourth(c, f))
        self.assertFalse(pitches.is_perfect_fourth(c, a))

    def test_is_perfect_octave(self):
        c = 0
        c1 = 12
        a = 9

        self.assertTrue(pitches.is_perfect_octave(c, c1))
        self.assertFalse(pitches.is_perfect_octave(c, a))

    def test_is_perfect_interval(self):
        c = 0
        f = 5
        g = 7
        c1 = 12
        a = 9

        self.assertTrue(pitches.is_perfect_interval(c, g))
        self.assertTrue(pitches.is_perfect_interval(c, f))
        self.assertTrue(pitches.is_perfect_interval(c, c1))
        self.assertFalse(pitches.is_perfect_interval(c, a))

    def test_ionian(self):
        c_val = 0

        all_notes_length = 75
        all_pitches = pitches.ionian(c_val)

        self.assertEqual(len(all_pitches), all_notes_length)
        self.assertTrue(pitches.OCTAVES['C'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['D'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['E'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['F'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['G'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['A'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['B'][0] in all_pitches)

    def test_dorian(self):
        c_val = 0

        all_notes_length = 75
        all_pitches = pitches.dorian(c_val)

        self.assertEqual(len(all_pitches), all_notes_length)
        self.assertTrue(pitches.OCTAVES['C'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['D'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['D#'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['F'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['G'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['A'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['A#'][0] in all_pitches)

    def test_phrygian(self):
        c_val = 0

        all_notes_length = 75
        all_pitches = pitches.phrygian(c_val)

        self.assertEqual(len(all_pitches), all_notes_length)
        self.assertTrue(pitches.OCTAVES['C'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['C#'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['D#'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['F'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['G'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['G#'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['A#'][0] in all_pitches)

    def test_lydian(self):
        c_val = 0

        all_notes_length = 75
        all_pitches = pitches.lydian(c_val)

        self.assertEqual(len(all_pitches), all_notes_length)
        self.assertTrue(pitches.OCTAVES['C'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['D'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['E'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['F#'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['G'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['A'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['B'][0] in all_pitches)

    def test_mixolydian(self):
        c_val = 0

        all_notes_length = 75
        all_pitches = pitches.mixolydian(c_val)

        self.assertEqual(len(all_pitches), all_notes_length)
        self.assertTrue(pitches.OCTAVES['C'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['D'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['E'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['F'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['G'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['A'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['A#'][0] in all_pitches)

    def test_aeolian(self):
        c_val = 0

        all_notes_length = 75
        all_pitches = pitches.aeolian(c_val)

        self.assertEqual(len(all_pitches), all_notes_length)
        self.assertTrue(pitches.OCTAVES['C'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['D'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['D#'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['F'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['G'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['G#'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['A#'][0] in all_pitches)

    def test_locrian(self):
        c_val = 0

        all_notes_length = 75
        all_pitches = pitches.locrian(c_val)

        self.assertEqual(len(all_pitches), all_notes_length)
        self.assertTrue(pitches.OCTAVES['C'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['C#'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['D#'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['F'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['F#'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['G#'][0] in all_pitches)
        self.assertTrue(pitches.OCTAVES['A#'][0] in all_pitches)

    def test_species(self):
        c = 24
        note_c = pitches.parse('C')
        species_c = 'C'
        octave_c = 'C2'

        correct = 'C'

        self.assertEqual(pitches.species(c), correct)
        self.assertEqual(pitches.species(note_c), correct)
        self.assertEqual(pitches.species(species_c), correct)
        self.assertEqual(pitches.species(octave_c), correct)

    def test__midi_value(self):
        c0 = 0
        c2 = 24

        string_c0 = 'C'
        string_c2 = 'C2'

        self.assertEqual(c0, pitches.midi_value(string_c0))
        self.assertEqual(c2, pitches.midi_value(string_c2))

    def test__parallel_motion(self):
        par_4ths = 59, 60, 64, 65
        par_5ths = 59, 60, 66, 67
        par_8ths = 60, 65, 48, 53
        oblique = 60, 58, 72, 68

        self.assertTrue(pitches.parallel_movement(par_4ths[0], par_4ths[1], par_4ths[2], par_4ths[3]))
        self.assertTrue(pitches.parallel_movement(par_5ths[0], par_5ths[1], par_5ths[2], par_5ths[3]))
        self.assertTrue(pitches.parallel_movement(par_8ths[0], par_8ths[1], par_8ths[2], par_8ths[3]))
        self.assertFalse(pitches.parallel_movement(oblique[0], oblique[1], oblique[2], oblique[3]))

