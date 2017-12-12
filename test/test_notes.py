from unittest import TestCase
from cybach import notes

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