import unittest

import midi

import chords
import config
import constants
import fileloader
import ks_detector
import sequences
import transforms
import vars
from pitches import MIDI_VALUES


@unittest.skip
class TestMotionTransforms(unittest.TestCase):

    def test_ApproachTransform_is_applicable(self):
        fileloader.load(constants.TEST_MIDI + 'approach.mid', False)
        sequence = sequences.soprano

        config.chord_progression[0] = chords.parse('A')
        config.chord_progression[config.resolution] = chords.parse('D')
        config.chord_progression[config.resolution * 4] = chords.parse('E')
        config.chord_progression[config.resolution * 5] = chords.parse('F')
        config.chord_progression[config.resolution * 6] = chords.parse('A')
        ks_detector.detect_and_set_key_signatures()

        self.assertTrue(transforms.ApproachTransform.applicable_at(0, sequence))
        self.assertTrue(
            transforms.ApproachTransform.applicable_at(4 * config.resolution, sequence))
        self.assertFalse(
            transforms.ApproachTransform.applicable_at(6 * config.resolution, sequence))

    def test_HalfStepNeighborTransform_is_applicable(self):
        fileloader.load(constants.TEST_MIDI + 'neighbor.mid', False)
        sequence = sequences.soprano

        config.chord_progression[0] = chords.parse('C')
        ks_detector.detect_and_set_key_signatures()

        app = transforms.HalfStepNeighborTransform.applicable_at(0, sequence)

        self.assertTrue(transforms.HalfStepNeighborTransform.applicable_at(0, sequence))
        self.assertFalse(
            transforms.HalfStepNeighborTransform.applicable_at(2 * config.resolution, sequence))
        self.assertTrue(
            transforms.HalfStepNeighborTransform.applicable_at(4 * config.resolution, sequence))

    def test_WholeStepNeighborTransform_is_applicable(self):
        fileloader.load(constants.TEST_MIDI + 'neighbor.mid', False)
        sequence = sequences.soprano

        config.chord_progression[0] = chords.parse('C')
        ks_detector.detect_and_set_key_signatures()

        self.assertTrue(transforms.WholeStepNeighborTransform.applicable_at(0, sequence))
        self.assertTrue(
            transforms.WholeStepNeighborTransform.applicable_at(2 * config.resolution, sequence))

    def test_MajorThirdScalarTransform_is_applicable(self):
        fileloader.load(constants.TEST_MIDI + 'maj3_scalar.mid', False)
        sequence = sequences.soprano

        self.assertTrue(transforms.MajorThirdScalarTransform.applicable_at(0, sequence))
        self.assertFalse(transforms.MajorThirdScalarTransform.applicable_at(2, sequence))

    def test_MinorThirdScalarTransform_is_applicable(self):
        fileloader.load(constants.TEST_MIDI + 'min3_scalar.mid', False)
        sequence = sequences.soprano

        config.chord_progression[0] = chords.parse('C-')
        ks_detector.detect_and_set_key_signatures()

        self.assertTrue(transforms.MinorThirdScalarTransform.applicable_at(0, sequence))
        self.assertFalse(transforms.MinorThirdScalarTransform.applicable_at(2, sequence))

    def test_ArpeggialTransform_is_applicable(self):
        fileloader.load(constants.TEST_MIDI + 'arpeggial.mid', False)
        sequence = sequences.soprano

        config.chord_progression[0] = chords.parse('C')
        config.chord_progression[5 * config.resolution] = chords.parse('A-')
        ks_detector.detect_and_set_key_signatures()

        self.assertTrue(transforms.ArpeggialTransform.applicable_at(0, sequence))
        self.assertTrue(
            transforms.ArpeggialTransform.applicable_at(4 * config.resolution, sequence))

    def test_MajorThirdScalarTransform_intermediate_pitch(self):
        fileloader.load(constants.TEST_MIDI + 'maj3_scalar.mid', False)
        sequence = sequences.soprano

        config.chord_progression[0] = chords.parse('C')
        ks_detector.detect_and_set_key_signatures()

        trans = transforms.MajorThirdScalarTransform(0, sequence)
        pitch_should_be = sequence[0].midi() + 2

        self.assertEqual(trans.intermediate_pitch, pitch_should_be)

    def test_MinorThirdScalarTransform_intermediate_pitch(self):
        fileloader.load(constants.TEST_MIDI + 'min3_scalar.mid', False)
        sequence = sequences.soprano

        config.chord_progression[0] = chords.parse('C-')
        ks_detector.detect_and_set_key_signatures()

        trans = transforms.MinorThirdScalarTransform(0, sequence)
        pitch_should_be = sequence[0].midi() + 2

        self.assertEqual(trans.intermediate_pitch, pitch_should_be)

    def test_ArpeggialTransform_intermediate_pitch(self):
        fileloader.load(constants.TEST_MIDI + 'arpeggial.mid', False)
        sequence = sequences.soprano

        config.chord_progression[0] = chords.parse('C')
        ks_detector.detect_and_set_key_signatures()

        trans = transforms.ArpeggialTransform(0, sequence)
        major_third_above = sequence[0].midi() + 4

        self.assertEqual(trans.intermediate_pitch, major_third_above)

    def test_HalfStepNeighborTransform_intermediate_pitch(self):
        fileloader.load(constants.TEST_MIDI + 'neighbor.mid', False)
        sequence = sequences.soprano

        config.chord_progression[0] = chords.parse('C')
        ks_detector.detect_and_set_key_signatures()

        trans = transforms.HalfStepNeighborTransform(0, sequence)
        half_step_below = sequence[0].midi() - 1

        self.assertEqual(trans.intermediate_pitch, half_step_below)

    def test_WholeStepNeighborTransform_intermediate_pitch(self):
        fileloader.load(constants.TEST_MIDI + 'neighbor.mid', False)
        sequence = sequences.soprano
        
        config.chord_progression[0] = chords.parse('C')
        ks_detector.detect_and_set_key_signatures()

        trans = transforms.WholeStepNeighborTransform(0, sequence)
        whole_step_above = sequence[0].midi() + 2

        self.assertEqual(trans.intermediate_pitch, whole_step_above)

    def test_ApproachTransform_intermediate_pitch(self):
        fileloader.load(constants.TEST_MIDI + 'approach.mid', False)
        sequence = sequences.soprano
        
        config.chord_progression[0] = chords.parse('A')
        config.chord_progression[config.resolution] = chords.parse('D')
        ks_detector.detect_and_set_key_signatures()

        trans = transforms.ApproachTransform(0, sequence)
        c_sharp_below = sequence[0].midi() - 8

        self.assertEqual(trans.intermediate_pitch, c_sharp_below)

    def test_MajorThirdScalarTransform_Scalar_synergy(self):
        fileloader.load(constants.TEST_MIDI + 'maj3_scalar.mid', False)
        sequence = sequences.soprano
        
        config.chord_progression[0] = chords.parse('C')
        ks_detector.detect_and_set_key_signatures()

        scalar_trans = transforms.MajorThirdScalarTransform(0, sequence)
        same_trans = transforms.MajorThirdScalarTransform(0, sequence)
        join = transforms.JoinTransform(2, 0, sequence)
        join3 = transforms.JoinTransform(3, 0, sequence)

        self.assertEqual(scalar_trans.synergy(same_trans), vars.EIGHTH_NOTE_SAME)
        self.assertEqual(scalar_trans.synergy(join), 0.0)
        self.assertEqual(join.synergy(join), vars.JOIN_SAME)
        self.assertEqual(join.synergy(join3), 0.0)

    def test_MajorThirdScalarTransform_Neighbor_synergy(self):
        fileloader.load(constants.TEST_MIDI + 'neighbor.mid', False)
        sequence = sequences.soprano
        scalar_sequence = sequences.RootSequence(read_pattern(constants.TEST_MIDI + 'maj3_scalar.mid')[0])

        config.chord_progression[0] = chords.parse('C')
        ks_detector.detect_and_set_key_signatures()

        scalar_trans = transforms.MajorThirdScalarTransform(0, scalar_sequence)
        dom_neighbor_trans = transforms.HalfStepNeighborTransform(0, sequence)
        subdom_neighbor_trans = transforms.HalfStepNeighborTransform(config.resolution * 4, sequence)

        self.assertEqual(scalar_trans.synergy(dom_neighbor_trans), vars.EIGHTH_NOTE_DOMINANT)
        self.assertEqual(scalar_trans.synergy(subdom_neighbor_trans), vars.EIGHTH_NOTE_SUBDOMINANT)

    def test_ApproachTransform_set_musicality(self):
        fileloader.load(constants.TEST_MIDI + 'approach.mid', False)
        sequence = sequences.soprano
        
        config.chord_progression[0] = chords.parse('A')
        config.chord_progression[config.resolution] = chords.parse('D')
        config.chord_progression[config.resolution * 5] = chords.parse('F')
        config.chord_progression[config.resolution * 6] = chords.parse('A')
        ks_detector.detect_and_set_key_signatures()
        ks = config.key_signatures

        weaker_trans = transforms.ApproachTransform(11 * config.resolution, sequence)
        stronger_trans = transforms.ApproachTransform(0, sequence)
        strong_trans = transforms.ApproachTransform(4 * config.resolution, sequence)

        self.assertEqual(vars.APPROACH_DEFAULT_MUSICALITY, weaker_trans.intrinsic_musicality)
        self.assertEqual(vars.APPROACH_NEW_CHORD_ROOT, stronger_trans.intrinsic_musicality)
        self.assertEqual(vars.APPROACH_KEY_CHANGE, strong_trans.intrinsic_musicality)

    def test_MajorThird_set_musicality(self):
        fileloader.load(constants.TEST_MIDI + 'linear_motion.mid', False)
        sequence = sequences.soprano
        
        config.chord_progression[0] = chords.parse('C')
        ks_detector.detect_and_set_key_signatures()

        trans = transforms.MajorThirdScalarTransform(6 * config.resolution, sequence)
        self.assertEqual(trans.intrinsic_musicality, vars.MAJOR_THIRD_SCALAR_CONTINUES_LINEARITY)

    def test_ArpeggialTransform_set_musicality(self):
        fileloader.load(constants.TEST_MIDI + 'arpeggial.mid', False)
        sequence = sequences.soprano
        
        config.chord_progression[0] = chords.parse('C')
        config.chord_progression[5 * config.resolution] = chords.parse('A-')
        ks_detector.detect_and_set_key_signatures()

        weaker_trans = transforms.ArpeggialTransform(0, sequence)
        stronger_trans = transforms.ArpeggialTransform(config.resolution * 4, sequence)

        self.assertEqual(weaker_trans.intrinsic_musicality, vars.ARPEGGIAL_SAME_CHORD)
        self.assertEqual(stronger_trans.intrinsic_musicality, vars.ARPEGGIAL_NEW_CHORD)

    def test_notes_cause_parallel_movement(self):
        part1_first = MIDI_VALUES['C1']
        part2_first_fourth = MIDI_VALUES['F1']
        part2_first_fifth = MIDI_VALUES['G1']
        part2_first_octave = MIDI_VALUES['C2']

        part1_second = MIDI_VALUES['D1']
        part2_second_fourth = MIDI_VALUES['G1']
        part2_second_fifth = MIDI_VALUES['A1']
        part2_second_octave = MIDI_VALUES['D2']

        self.assertTrue(transforms.notes_cause_parallel_movement(part1_first, part2_first_fourth,
                                                                 part1_second, part2_second_fourth))
        self.assertTrue(transforms.notes_cause_parallel_movement(part1_first, part2_first_fifth,
                                                                 part1_second, part2_second_fifth))
        self.assertTrue(transforms.notes_cause_parallel_movement(part1_first, part2_first_octave,
                                                                 part1_second, part2_second_octave))

    def test__is_syncopation(self):
        fileloader.load(constants.TEST_MIDI + '2beat_join.mid', False)
        sequence = sequences.soprano

        config.chord_progression[0] = chords.parse('C')
        ks_detector.detect_and_set_key_signatures()

        syncopation = transforms.JoinTransform(2, config.resolution, sequence)
        nonsyncopated = transforms.JoinTransform(2, 0, sequence)

        self.assertTrue(syncopation.is_syncopation())
        self.assertFalse(nonsyncopated.is_syncopation())

    def test__JoinTransform_crosses_bar_line(self):
        fileloader.load(constants.TEST_MIDI + '2beat_join.mid', False)
        sequence = sequences.soprano
        
        config.chord_progression[0] = chords.parse('C')
        ks_detector.detect_and_set_key_signatures()

        over_bar_line = transforms.JoinTransform(2, config.resolution * 3, sequence)
        inside_bar = transforms.JoinTransform(2, config.resolution * 2, sequence)

        self.assertTrue(over_bar_line.crosses_bar_line())
        self.assertFalse(inside_bar.crosses_bar_line())

    def test__EighthNoteTransform_causes_flickering(self):
        fileloader.load(constants.TEST_MIDI + 'flicker.mid', False)
        sequence = sequences.soprano

        c = config

        config.chord_progression[0] = chords.parse('C')
        ks_detector.detect_and_set_key_signatures()

        transform1 = transforms.WholeStepNeighborTransform((1 * config.resolution * 4) +
                                                           (1 * config.resolution), sequence)

        transform2 = transforms.HalfStepNeighborTransform((2 * config.resolution * 4) +
                                                          (1 * config.resolution), sequence)

        transform3 = transforms.HalfStepNeighborTransform((2 * config.resolution * 4) +
                                                          (1 * config.resolution), sequence)

        self.assertTrue(transform1.causes_flickering())
        self.assertTrue(transform2.causes_flickering())
        self.assertTrue(transform3.causes_flickering())


def read_pattern(file_name):
    try:
        return midi.read_midifile(file_name)
    except TypeError:
        print 'Midi file is malformed. Try exporting a new one from any DAW'
        exit(2)
    raise Exception
