from unittest import TestCase

import midi

import chords
import constants
import fileloader
import ks
import phrasing
import vars
from rhythm import time


class TestPhrasing(TestCase):

    def tearDown(self):
        super(TestPhrasing, self).tearDown()
        chords.clear()
        time.clear()
        ks.clear()

    def test__chord_based_strong_beat_prediction(self):
        fileloader.load(constants.TEST_MIDI + 'mixed_meter.mid', False)

        chords.write('C')
        chords.write('F', measure=2)
        chords.write('G7', measure=2, beat=3)

        prediction = phrasing.chord_based_strong_beat_prediction(time.measure(2))

        self.assertEqual((0, 3), prediction)

    def test__phrase_combinations(self):
        four_four_combinations = phrasing.potential_strong_beat_permutations(4)
        six_eight_combinations = phrasing.potential_strong_beat_permutations(6)

        self.assertEqual([(0, 1, 2, 3)], four_four_combinations)
        self.assertEqual([(0, 4), (0, 2, 4), (0, 2), (0, 3)], six_eight_combinations)

    def test__potential_strong_beat_permutations(self):
        beats_per_bar = 7
        total_combinations = 5

        self.assertEqual(total_combinations, len(phrasing.potential_strong_beat_permutations(beats_per_bar)))

    def test__phrasing_likelihood(self):
        fileloader.load(constants.TEST_MIDI + 'seven_eight.mid', False)

        p = (0, 2, 4)
        score = 2 * vars.RHYTHM_PHRASING_COEF + 3 * vars.RHYTHM_PHRASING_COEF

        self.assertEqual(score, phrasing.rhythm_based_strong_beat_score(time.measure(0), p))


def read_pattern(file_name):
    try:
        return midi.read_midifile(file_name)
    except TypeError:
        print 'Midi file is malformed. Try exporting a new one from any DAW'
        exit(2)
    raise Exception
