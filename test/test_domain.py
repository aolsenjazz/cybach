from unittest import TestCase

import config
import constants
import fileloader
import pitches
import util
import vars
from rhythm import time


class TestDomain(TestCase):

    def test__Sequence_note_duration_count(self):
        fileloader.load(constants.TEST_MIDI + 'linear_motion.mid', False)
        sequence = config.soprano

        number_of_sixteenths = 2
        number_of_eighths = 5

        duration_count = sequence.note_duration_count()

        self.assertEqual(duration_count.get(constants.SIXTEENTH_NOTE, 0), number_of_sixteenths)
        self.assertEqual(duration_count.get(constants.EIGHTH_NOTE, 0), number_of_eighths)

    def test__Sequence_get_entity_length(self):
        fileloader.load(constants.TEST_MIDI + 'linear_motion.mid', False)
        sequence = config.soprano

        first_note_duration = 96
        second_note_duration = 24

        self.assertEqual(first_note_duration, sequence.get_entity_length(0))
        self.assertEqual(second_note_duration, sequence.get_entity_length(120))

    def test__Sequence_get_entity_start_rest(self):
        fileloader.load(constants.TEST_MIDI + 'entities.mid', False)
        sequence = config.soprano

        rest_start = 96
        middle_of_rest = 144

        self.assertEqual(rest_start, sequence.get_entity_start(middle_of_rest))

    def test__Sequence_get_entity_start_pitch(self):
        fileloader.load(constants.TEST_MIDI + 'linear_motion.mid', False)
        sequence = config.soprano

        pitch_start = 0
        middle_of_pitch = 48

        self.assertEqual(pitch_start, sequence.get_entity_start(middle_of_pitch))

    def test__Sequence_get_entity_length_rest(self):
        fileloader.load(constants.TEST_MIDI + 'entities.mid', False)
        sequence = config.soprano

        rest_start = 96
        rest_length = 96

        self.assertEqual(rest_length, sequence.get_entity_length(rest_start))
