from unittest import TestCase

import midi

import chords
import config
import constants
import domain
import parts
import phrasing
from rhythm import time


class TestPhrasing(TestCase):

    def test__chord_based_strong_beat_prediction(self):
        pattern = read_pattern(constants.TEST_MIDI + 'mixed_meter.mid')
        sequence = domain.RootSequence(pattern[0])

        config.soprano = sequence
        time.add_signature(0, time.TimeSignature(numerator=4, denominator=4))
        time.add_signature(768, time.TimeSignature(numerator=6, denominator=8))

        config.chord_progression = chords.ChordProgression()
        config.chord_progression.set().measure(0).commit('C')
        config.chord_progression.set().measure(2).commit('F')
        config.chord_progression.set().measure(2).beat(3).commit('G7')

        prediction = phrasing.chord_based_strong_beat_prediction(time.measure(2))

        self.assertEqual((0, 3), prediction)

    def test__phrase_combinations(self):
        four_four_combinations = phrasing.potential_strong_beat_permutations(4)
        six_eight_combinations = phrasing.potential_strong_beat_permutations(6)

        self.assertEqual({(0, 1, 2, 3),}, four_four_combinations)
        self.assertEqual({(2, 4), (4, 2), (3, 3), (2, 2, 2)}, six_eight_combinations)

    def test__potential_strong_beat_permutations(self):
        beats_per_bar = 7
        total_combinations = 5

        self.assertEqual(total_combinations, len(phrasing.potential_strong_beat_permutations(beats_per_bar)))
        time.clear()

    def test__phrasing_likelihood(self):
        fileloader.load(constants.TEST_MIDI + 'seven_eight.mid', False)

        phrasing = (0, 2, 4)
        score = 2 * vars.RHYTHM_PHRASING_COEF + 3 * vars.RHYTHM_PHRASING_COEF
        first_measure = time.measures()[0]

        self.assertEqual(score, first_measure.phrasing_likelihood(phrasing))


def read_pattern(file_name):
    try:
        return midi.read_midifile(file_name)
    except TypeError:
        print 'Midi file is malformed. Try exporting a new one from any DAW'
        exit(2)
    raise Exception
