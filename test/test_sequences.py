from unittest import TestCase

import chords
import constants
import fileloader
import ks
import pitches
import sequences
from rhythm import time


class TestSequences(TestCase):

    def tearDown(self):
        super(TestSequences, self).tearDown()
        chords.clear()
        time.clear()
        ks.clear()

    def test__Sequence_note_duration_count(self):
        fileloader.load(constants.TEST_MIDI + 'linear_motion.mid', False)
        sequence = sequences.soprano()

        number_of_sixteenths = 2
        number_of_eighths = 5

        duration_count = sequence.note_duration_count()

        self.assertEqual(duration_count.get(constants.SIXTEENTH_NOTE, 0), number_of_sixteenths)
        self.assertEqual(duration_count.get(constants.EIGHTH_NOTE, 0), number_of_eighths)

    def test__Sequence_add_entities_consumes(self):
        fileloader.load(constants.TEST_MIDI + 'entities.mid', False)
        sequence = sequences.soprano()
        
        new_entity_start = 144
        new_entity_end = 528

        note = sequences.Note(sequence, new_entity_start, new_entity_end, pitches.Pitch(61))
        sequence.add_entities(note)

        self.assertEqual(new_entity_start, sequence.entities().values()[1].end())
        self.assertEqual(new_entity_end, sequence.entities().values()[3].start())

    def test__Sequence_add_entities_splits(self):
        fileloader.load(constants.TEST_MIDI + 'entities.mid', False)
        sequence = sequences.soprano()

        new_entity_start = 480
        new_entity_end = 576

        note = sequences.Rest(sequence, new_entity_start, new_entity_end)
        sequence.add_entities(note)


        self.assertEqual(new_entity_start, sequence.entities().values()[3].end())
        self.assertEqual(new_entity_end, sequence.entities().values()[5].start())
