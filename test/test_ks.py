from unittest import TestCase

import chords
import ks
import vars
from rhythm import time


class TestKs(TestCase):

    def tearDown(self):
        super(TestKs, self).tearDown()
        chords.clear()
        time.clear()
        ks.clear()

    def test__harmonic_relevance(self):
        major = ks.MajorKeySignature('C')
        minor = ks.MinorKeySignature('C')

        c_major = chords.parse('C')
        c_minor = chords.parse('C-')
        d_minor = chords.parse('D-')
        d_dimin = chords.parse('Ddim')
        e_minor = chords.parse('E-')
        eb_major = chords.parse('Eb')
        f_major = chords.parse('F')
        f_minor = chords.parse('F-')
        g_major = chords.parse('G')
        g_seven = chords.parse('G7')
        ab_major = chords.parse('Ab')
        a_minor = chords.parse('A-')
        b_dimin = chords.parse('Bdim')

        self.assertEqual(vars.ONE_CHORD_HARMONY, major.harmonic_relevance(c_major))
        self.assertEqual(vars.TWO_CHORD_HARMONY, major.harmonic_relevance(d_minor))
        self.assertEqual(vars.THREE_CHORD_HARMONY, major.harmonic_relevance(e_minor))
        self.assertEqual(vars.FOUR_CHORD_HARMONY, major.harmonic_relevance(f_major))
        self.assertEqual(vars.FIVE_DOMINANT_HARMONY, major.harmonic_relevance(g_seven))
        self.assertEqual(vars.FIVE_MAJOR_HARMONY, major.harmonic_relevance(g_major))
        self.assertEqual(vars.SIX_CHORD_HARMONY, major.harmonic_relevance(a_minor))
        self.assertEqual(vars.MAJOR_SEVEN_DIMINISHED_HARMONY, major.harmonic_relevance(b_dimin))

        self.assertEqual(vars.ONE_CHORD_HARMONY, minor.harmonic_relevance(c_minor))
        self.assertEqual(vars.TWO_CHORD_HARMONY, minor.harmonic_relevance(d_dimin))
        self.assertEqual(vars.THREE_CHORD_HARMONY, minor.harmonic_relevance(eb_major))
        self.assertEqual(vars.FOUR_CHORD_HARMONY, minor.harmonic_relevance(f_minor))
        self.assertEqual(vars.FIVE_MAJOR_HARMONY, minor.harmonic_relevance(g_major))
        self.assertEqual(vars.FIVE_DOMINANT_HARMONY, minor.harmonic_relevance(g_seven))
        self.assertEqual(vars.SIX_CHORD_HARMONY, minor.harmonic_relevance(ab_major))
        self.assertEqual(vars.MAJOR_SEVEN_DIMINISHED_HARMONY, minor.harmonic_relevance(b_dimin))

        self.assertEqual(0, minor.harmonic_relevance(c_major))
        self.assertEqual(0, minor.harmonic_relevance(d_minor))
        self.assertEqual(0, minor.harmonic_relevance(e_minor))
        self.assertEqual(0, minor.harmonic_relevance(f_major))
        self.assertEqual(0, minor.harmonic_relevance(a_minor))

    def test__functional_relevance(self):
        major = ks.MajorKeySignature('C')
        minor = ks.MinorKeySignature('C')

        c_major = chords.parse('C')
        d_minor = chords.parse('D-')
        f_major = chords.parse('F')
        g_major = chords.parse('G')
        g_seven = chords.parse('G7')
        ab_major = chords.parse('Ab')
        a_minor = chords.parse('A-')
        b_dimin = chords.parse('Bdim')

        DOM_FIVE = vars.DOMINANT_FIVE_IN_FUNCTIONAL_RELEVANCE # shortening ;)
        FIVE = vars.MAJOR_FIVE_IN_FUNCTIONAL_RELEVANCE  # shortening ;)

        self.assertEqual(DOM_FIVE + vars.FIVE_ONE_FUNCTIONALITY, major.functional_relevance(g_seven, c_major))
        self.assertEqual(FIVE + vars.FIVE_ONE_FUNCTIONALITY, major.functional_relevance(g_major, c_major))
        self.assertEqual(vars.SEVEN_ONE_FUNCTIONALITY, major.functional_relevance(b_dimin, c_major))
        self.assertEqual(DOM_FIVE + vars.TWO_FIVE_FUNCTIONALITY, major.functional_relevance(d_minor, g_seven))
        self.assertEqual(FIVE + vars.TWO_FIVE_FUNCTIONALITY, major.functional_relevance(d_minor, g_major))
        self.assertEqual(DOM_FIVE + vars.FOUR_FIVE_FUNCTIONALITY, major.functional_relevance(f_major, g_seven))
        self.assertEqual(FIVE + vars.FOUR_FIVE_FUNCTIONALITY, major.functional_relevance(f_major, g_major))

        self.assertEqual(FIVE + vars.FIVE_SIX_FUNCTIONALITY, major.functional_relevance(g_major, a_minor))
        self.assertEqual(DOM_FIVE + vars.FIVE_SIX_FUNCTIONALITY, major.functional_relevance(g_seven, a_minor))

        self.assertEqual(FIVE + vars.FIVE_SIX_FUNCTIONALITY, minor.functional_relevance(g_major, ab_major))
        self.assertEqual(DOM_FIVE + vars.FIVE_SIX_FUNCTIONALITY, minor.functional_relevance(g_seven, ab_major))

