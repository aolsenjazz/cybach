from unittest import TestCase
from cybach import notes
from cybach import chords


class TestChords(TestCase):

    def test_is_perfect_fifth(self):
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
