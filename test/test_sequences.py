from unittest import TestCase

import constants
import fileloader
import pitches
import sequences


class TestDomain(TestCase):

    def test__Sequence_note_duration_count(self):
        fileloader.load(constants.TEST_MIDI + 'linear_motion.mid', False)
        sequence = sequences.soprano()

        number_of_sixteenths = 2
        number_of_eighths = 5

        duration_count = sequence.note_duration_count()
        print sequence

        self.assertEqual(duration_count.get(constants.SIXTEENTH_NOTE, 0), number_of_sixteenths)
        self.assertEqual(duration_count.get(constants.EIGHTH_NOTE, 0), number_of_eighths)

    def test__Sequence_get_entity_length(self):
        fileloader.load(constants.TEST_MIDI + 'linear_motion.mid', False)
        sequence = sequences.soprano()

        first_note_position = 0
        second_note_position = 96

        first_note_duration = 96
        second_note_duration = 24

        self.assertEqual(first_note_duration + first_note_position, sequence._get_entity_end(first_note_position))
        self.assertEqual(second_note_duration + second_note_position, sequence._get_entity_end(second_note_position))

    def test__Sequence_get_entity_start_rest(self):
        fileloader.load(constants.TEST_MIDI + 'entities.mid', False)
        sequence = sequences.soprano()

        rest_start = 96
        middle_of_rest = 144

        self.assertEqual(rest_start, sequence._get_entity_start(middle_of_rest))

    def test__Sequence_get_entity_start_pitch(self):
        fileloader.load(constants.TEST_MIDI + 'linear_motion.mid', False)
        sequence = sequences.soprano()

        pitch_start = 0
        middle_of_pitch = 48

        self.assertEqual(pitch_start, sequence._get_entity_start(middle_of_pitch))

    def test__Sequence_get_entity_end_rest(self):
        fileloader.load(constants.TEST_MIDI + 'entities.mid', False)
        sequence = sequences.soprano()

        rest_start = 96
        rest_length = 96

        self.assertEqual(rest_length + rest_start, sequence._get_entity_end(rest_start))
    
    def test__Sequence_add_entities_consumes(self):
        fileloader.load(constants.TEST_MIDI + 'entities.mid', False)
        sequence = sequences.soprano()
        
        new_entity_start = 144
        new_entity_end = 528

        note = sequences.Note(sequence, new_entity_start, new_entity_end, pitches.Pitch(61))
        sequence.add_entities(note)

        self.assertEqual(new_entity_start, sequence.timed_entities()[1].end())
        self.assertEqual(new_entity_end, sequence.timed_entities()[3].start())

    def test__Sequence_add_entities_splits(self):
        fileloader.load(constants.TEST_MIDI + 'entities.mid', False)
        sequence = sequences.soprano()

        new_entity_start = 480
        new_entity_end = 576

        note = sequences.Rest(sequence, new_entity_start, new_entity_end)
        sequence.add_entities(note)

        self.assertEqual(new_entity_start, sequence.timed_entities()[3].end())
        self.assertEqual(new_entity_end, sequence.timed_entities()[5].start())
