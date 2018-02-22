from unittest import TestCase

import config
import constants
import fileloader
import notes
import util
import vars


class TestDomain(TestCase):

    def test__Note_contains_linear_motion(self):
        fileloader.load_file(constants.TEST_MIDI + 'linear_motion.mid')
        sequence = config.soprano

        has_linear_motion = sequence.beat_at(config.resolution * 2)
        has_linear_and_non_linear = sequence.beat_at(config.resolution)
        has_no_motion = sequence.beat_at(0)

        self.assertTrue(has_linear_motion.contains_linear_movement())
        self.assertFalse(has_linear_and_non_linear.contains_linear_movement())
        self.assertFalse(has_no_motion.contains_linear_movement())

    def test__Beat_contains_motion(self):
        fileloader.load_file(constants.TEST_MIDI + 'linear_motion.mid')
        sequence = config.soprano

        self.assertFalse(sequence.beat_at(0).contains_motion())
        self.assertTrue(sequence.beat_at(config.resolution).contains_motion())

    def test__Sequence_note_duration_count(self):
        fileloader.load_file(constants.TEST_MIDI + 'linear_motion.mid')
        sequence = config.soprano

        number_of_sixteenths = 2
        number_of_eighths = 5

        self.assertEqual(sequence.note_duration_count().get(constants.SIXTEENTH_NOTE, 0), number_of_sixteenths)
        self.assertEqual(sequence.note_duration_count().get(constants.EIGHTH_NOTE, 0), number_of_eighths)

    def test__Sequence_measures(self):
        fileloader.load_file(constants.TEST_MIDI + 'linear_motion.mid')
        sequence = config.soprano

        number_of_measures = 2

        self.assertEqual(number_of_measures, len(sequence.measures()))

    def test__Measure_sample_position(self):
        fileloader.load_file(constants.TEST_MIDI + 'linear_motion.mid')
        sequence = config.soprano

        measure_index = 1
        measure_sample_duration = 4 * config.resolution
        measure_position = measure_index * measure_sample_duration

        measures = sequence.measures()

        self.assertEqual(measures[measure_index].sample_position(), measure_position)

    def test__Sequence_beat_index_in_measure(self):
        fileloader.load_file(constants.TEST_MIDI + 'linear_motion.mid')
        sequence = config.soprano

        beat_index_in_composition = 5
        beat_index_in_measure = 1

        self.assertEqual(sequence.beat_index_in_measure(beat_index_in_composition * config.resolution),
                         beat_index_in_measure)

    def test__Beat_is_first_beat(self):
        fileloader.load_file(constants.TEST_MIDI + 'linear_motion.mid')
        sequence = config.soprano

        first_measure = sequence.measures()[0]

        beat1 = first_measure.beats()[0]
        beat2 = first_measure.beats()[3]

        self.assertTrue(beat1.is_first_beat())
        self.assertTrue(beat2.is_last_beat())

    def test__Beat_is_note_start(self):
        fileloader.load_file(constants.TEST_MIDI + 'linear_motion.mid')
        sequence = config.soprano

        first_measure = sequence.measures()[0]
        beat1 = first_measure.beats()[0]

        self.assertTrue(beat1.is_note_start())

    def test__Beat_is_pitch_change(self):
        fileloader.load_file(constants.TEST_MIDI + 'linear_motion.mid')
        sequence = config.soprano

        first_measure = sequence.measures()[0]
        beat2 = first_measure.beats()[1]

        self.assertTrue(beat2.is_pitch_change())

    def test__Beat_sustain_duration(self):
        fileloader.load_file(constants.TEST_MIDI + 'linear_motion.mid')
        sequence = config.soprano

        first_measure = sequence.measures()[0]
        beat1 = first_measure.beats()[0]

        self.assertEqual(config.resolution, beat1.sustain_duration())

    def test__Measure_beats_for_phrase(self):
        fileloader.load_file(constants.TEST_MIDI + 'six_eight.mid')
        sequence = config.soprano

        phrasing = (2, 2, 2)
        first_measure = sequence.measures()[0]

        beats = first_measure.beats_for_phrasing(phrasing)

        self.assertTrue(notes.same_species(beats[0].pitch(), 'C'))
        self.assertTrue(notes.same_species(beats[1].pitch(), 'E'))
        self.assertTrue(notes.same_species(beats[2].pitch(), 'D'))

    def test__Measure_phrasing_likelihood(self):
        fileloader.load_file(constants.TEST_MIDI + 'seven_eight.mid')
        sequence = config.soprano

        phrasing = (2, 2, 3)
        score = 2 * vars.RHYTHM_PHRASING_COEF + 3 * vars.RHYTHM_PHRASING_COEF
        first_measure = sequence.measures()[0]

        self.assertEqual(score, first_measure.phrasing_likelihood(phrasing))

    def test__Measure_chord_based_phrasing_prediction(self):
        fileloader.load_file(constants.TEST_MIDI + 'seven_eight.mid')
        sequence = config.soprano

        config.chord_progression.set().measure(0).beat(2).commit('G')
        config.chord_progression.set().measure(0).beat(4).commit('A')

        phrasing = (0, 2, 2)
        first_measure = sequence.measures()[0]

        self.assertEqual(phrasing, first_measure.chord_based_phrasing_prediction())

    def test__properly_parse_mixed_meters(self):
        fileloader.load_file(constants.TEST_MIDI + 'mixed_meter.mid')
        sequence = config.soprano

        number_of_measures = 11

        self.assertEqual(number_of_measures, len(sequence.measures()))

    def test__Measure_phrasing_candidates(self):
        fileloader.load_file(constants.TEST_MIDI + 'mixed_meter.mid')
        sequence = config.soprano

        config.chord_progression.set().measure(4).beat(3).commit('F')

        measures = sequence.measures()
        four_four_measure = measures[0]
        seven_eight_measure = measures[4]

        self.assertEqual({(0, 1, 2, 3): 1}, four_four_measure.phrasing_candidates())
        candidates = seven_eight_measure.phrasing_candidates()
        self.assertEqual((0, 3), util.key_for_highest_value(candidates))
