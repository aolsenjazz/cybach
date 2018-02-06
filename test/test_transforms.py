from unittest import TestCase

import midi

import chords, transforms
import domain
import rhythm
import ks
import vars
import parts
import config
from notes import MIDI_VALUES

import constants


class TestMotionTransforms(TestCase):

    def test_ApproachTransform_is_applicable(self):
        pattern = read_pattern(constants.TEST_MIDI + 'approach.mid')
        sequence = domain.Sequence(pattern=pattern[0], part=parts.BASS)

        key_signatures = ks.KeySignatures()
        key_signatures[0] = chords.parse('A')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('A')
        chord_progression[config.resolution] = chords.parse('D')
        chord_progression[config.resolution * 4] = chords.parse('E')
        chord_progression[config.resolution * 5] = chords.parse('A')

        set_config(sequence, chord_progression, key_signatures)

        self.assertTrue(transforms.ApproachTransform.applicable_at(0, sequence))
        self.assertTrue(
            transforms.ApproachTransform.applicable_at(4 * config.resolution, sequence))
        self.assertFalse(
            transforms.ApproachTransform.applicable_at(6 * config.resolution, sequence))

    def test_HalfStepNeighborTransform_is_applicable(self):
        pattern = read_pattern(constants.TEST_MIDI + 'neighbor.mid')
        sequence = domain.Sequence(pattern=pattern[0], part=parts.BASS)

        key_signatures = ks.KeySignatures()
        key_signatures[0] = chords.parse('C')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C')

        set_config(sequence, chord_progression, key_signatures)

        self.assertTrue(transforms.HalfStepNeighborTransform.applicable_at(0, sequence))
        self.assertFalse(
            transforms.HalfStepNeighborTransform.applicable_at(2 * config.resolution, sequence))
        self.assertTrue(
            transforms.HalfStepNeighborTransform.applicable_at(4 * config.resolution, sequence))

    def test_WholeStepNeighborTransform_is_applicable(self):
        pattern = read_pattern(constants.TEST_MIDI + 'neighbor.mid')
        sequence = domain.Sequence(pattern=pattern[0], part=parts.BASS)

        key_signatures = ks.KeySignatures()
        key_signatures[0] = chords.parse('C')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C')

        set_config(sequence, chord_progression, key_signatures)

        self.assertTrue(transforms.WholeStepNeighborTransform.applicable_at(0, sequence))
        self.assertTrue(
            transforms.WholeStepNeighborTransform.applicable_at(2 * config.resolution, sequence))

    def test_MajorThirdScalarTransform_is_applicable(self):
        pattern = read_pattern(constants.TEST_MIDI + 'maj3_scalar.mid')
        sequence = domain.Sequence(pattern=pattern[0], part=parts.BASS)

        key_signatures = ks.KeySignatures()
        key_signatures[0] = chords.parse('C')

        self.assertTrue(transforms.MajorThirdScalarTransform.applicable_at(0, sequence))
        self.assertFalse(transforms.MajorThirdScalarTransform.applicable_at(2, sequence))

    def test_MinorThirdScalarTransform_is_applicable(self):
        pattern = read_pattern(constants.TEST_MIDI + 'min3_scalar.mid')
        sequence = domain.Sequence(pattern=pattern[0], part=parts.BASS)

        key_signatures = ks.KeySignatures()
        key_signatures[0] = chords.parse('C-')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C-')

        set_config(sequence, chord_progression, key_signatures)

        self.assertTrue(transforms.MinorThirdScalarTransform.applicable_at(0, sequence))
        self.assertFalse(transforms.MinorThirdScalarTransform.applicable_at(2, sequence))

    def test_ArpeggialTransform_is_applicable(self):
        pattern = read_pattern(constants.TEST_MIDI + 'arpeggial.mid')
        sequence = domain.Sequence(pattern=pattern[0], part=parts.ALTO)

        key_signatures = ks.KeySignatures()
        key_signatures[0] = chords.parse('C')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C')
        chord_progression[5 * config.resolution] = chords.parse('A-')

        set_config(sequence, chord_progression, key_signatures)

        self.assertTrue(transforms.ArpeggialTransform.applicable_at(0, sequence))
        self.assertTrue(
            transforms.ArpeggialTransform.applicable_at(4 * config.resolution, sequence))

    def test_MajorThirdScalarTransform_intermediate_pitch(self):
        pattern = read_pattern(constants.TEST_MIDI + 'maj3_scalar.mid')
        sequence = domain.Sequence(pattern=pattern[0], part=parts.BASS)

        key_signatures = ks.KeySignatures()
        key_signatures[0] = chords.parse('C')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C')

        set_config(sequence, chord_progression, key_signatures)

        trans = transforms.MajorThirdScalarTransform(0, sequence)
        pitch_should_be = sequence[0].pitch() + 2

        self.assertEqual(trans.intermediate_pitch, pitch_should_be)

    def test_MinorThirdScalarTransform_intermediate_pitch(self):
        pattern = read_pattern(constants.TEST_MIDI + 'min3_scalar.mid')
        sequence = domain.Sequence(pattern=pattern[0], part=parts.BASS)

        key_signatures = ks.KeySignatures()
        key_signatures[0] = chords.parse('C-')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C-')

        set_config(sequence, chord_progression, key_signatures)

        trans = transforms.MinorThirdScalarTransform(0, sequence)
        pitch_should_be = sequence[0].pitch() + 2

        self.assertEqual(trans.intermediate_pitch, pitch_should_be)

    def test_ArpeggialTransform_intermediate_pitch(self):
        pattern = read_pattern(constants.TEST_MIDI + 'arpeggial.mid')
        sequence = domain.Sequence(pattern=pattern[0], part=parts.ALTO)

        key_signatures = ks.KeySignatures()
        key_signatures[0] = chords.parse('C')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C')

        set_config(sequence, chord_progression, key_signatures)

        trans = transforms.ArpeggialTransform(0, sequence)
        major_third_above = sequence[0].pitch() + 4

        self.assertEqual(trans.intermediate_pitch, major_third_above)

    def test_HalfStepNeighborTransform_intermediate_pitch(self):
        pattern = read_pattern(constants.TEST_MIDI + 'neighbor.mid')
        sequence = domain.Sequence(pattern=pattern[0], part=parts.BASS)

        key_signatures = ks.KeySignatures()
        key_signatures[0] = chords.parse('C')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C')

        set_config(sequence, chord_progression, key_signatures)

        trans = transforms.HalfStepNeighborTransform(0, sequence)
        half_step_below = sequence[0].pitch() - 1

        self.assertEqual(trans.intermediate_pitch, half_step_below)

    def test_WholeStepNeighborTransform_intermediate_pitch(self):
        pattern = read_pattern(constants.TEST_MIDI + 'neighbor.mid')
        sequence = domain.Sequence(pattern=pattern[0], part=parts.BASS)

        key_signatures = ks.KeySignatures()
        key_signatures[0] = chords.parse('C')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C')

        set_config(sequence, chord_progression, key_signatures)

        trans = transforms.WholeStepNeighborTransform(0, sequence)
        whole_step_above = sequence[0].pitch() + 2

        self.assertEqual(trans.intermediate_pitch, whole_step_above)

    def test_ApproachTransform_intermediate_pitch(self):
        pattern = read_pattern(constants.TEST_MIDI + 'approach.mid')
        sequence = domain.Sequence(pattern=pattern[0], part=parts.BASS)

        key_signatures = ks.KeySignatures()
        key_signatures[0] = chords.parse('A')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('A')
        chord_progression[config.resolution] = chords.parse('D')

        set_config(sequence, chord_progression, key_signatures)

        trans = transforms.ApproachTransform(0, sequence)
        c_sharp_below = sequence[0].pitch() - 8

        self.assertEqual(trans.intermediate_pitch, c_sharp_below)

    def test_MajorThirdScalarTransform_synergy(self):
        scalar_pattern = read_pattern(constants.TEST_MIDI + 'maj3_scalar.mid')
        neighbor_pattern = read_pattern(constants.TEST_MIDI + 'neighbor.mid')

        scalar_sequence = domain.Sequence(pattern=scalar_pattern[0], part=parts.TENOR)
        neighbor_sequence = domain.Sequence(pattern=neighbor_pattern[0], part=parts.BASS)

        key_signatures = ks.KeySignatures()
        key_signatures[0] = chords.parse('C')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C')

        set_config(scalar_sequence, chord_progression, key_signatures)

        # Small tests, reall should ever change unless we manipulate values
        scalar_trans = transforms.MajorThirdScalarTransform(0, scalar_sequence)
        same_trans = transforms.MajorThirdScalarTransform(0, scalar_sequence)
        join = transforms.JoinTransform(2, 0, scalar_sequence)
        join3 = transforms.JoinTransform(3, 0, scalar_sequence)

        self.assertEqual(scalar_trans.synergy(same_trans), vars.EIGHTH_NOTE_SAME)
        self.assertEqual(scalar_trans.synergy(join), 0.0)
        self.assertEqual(join.synergy(join), vars.JOIN_SAME)
        self.assertEqual(join.synergy(join3), 0.0)

        set_config(neighbor_sequence, chord_progression, key_signatures)

        # More important tests that have more logic attached
        dom_neighbor_trans = transforms.HalfStepNeighborTransform(0, neighbor_sequence)
        subdom_neighbor_trans = transforms.HalfStepNeighborTransform(config.resolution * 4, neighbor_sequence)

        self.assertEqual(scalar_trans.synergy(dom_neighbor_trans), vars.EIGHTH_NOTE_DOMINANT)
        self.assertEqual(scalar_trans.synergy(subdom_neighbor_trans), vars.EIGHTH_NOTE_SUBDOMINANT)

    def test_ApproachTransform_set_musicality(self):
        pattern = read_pattern(constants.TEST_MIDI + 'approach.mid')
        sequence = domain.Sequence(pattern=pattern[0], part=parts.BASS)

        key_signatures = ks.KeySignatures()
        key_signatures[0] = chords.parse('A')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('A')
        chord_progression[config.resolution] = chords.parse('D')
        chord_progression[config.resolution * 4] = chords.parse('A')

        set_config(sequence, chord_progression, key_signatures)

        weaker_trans = transforms.ApproachTransform(11 * config.resolution, sequence)
        stronger_trans = transforms.ApproachTransform(0, sequence)
        strong_trans = transforms.ApproachTransform(4 * config.resolution, sequence)

        self.assertEqual(weaker_trans.intrinsic_musicality, vars.APPROACH_DEFAULT_MUSICALITY)
        self.assertEqual(stronger_trans.intrinsic_musicality, vars.APPROACH_NEW_CHORD_ROOT)
        self.assertEqual(strong_trans.intrinsic_musicality, vars.APPROACH_KEY_CHANGE)

    def test_MajorThird_set_musicality(self):
        pattern = read_pattern(constants.TEST_MIDI + 'linear_motion.mid')
        sequence = domain.Sequence(pattern=pattern[0])

        key_signatures = ks.KeySignatures()
        key_signatures[0] = chords.parse('C')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C')

        set_config(sequence, chord_progression, key_signatures)

        trans = transforms.MajorThirdScalarTransform(6 * config.resolution, sequence)
        self.assertEqual(trans.intrinsic_musicality, vars.MAJOR_THIRD_SCALAR_CONTINUES_LINEARITY)

    def test_ArpeggialTransform_set_musicality(self):
        pattern = read_pattern(constants.TEST_MIDI + 'arpeggial.mid')
        sequence = domain.Sequence(pattern=pattern[0], part=parts.ALTO)

        key_signatures = ks.KeySignatures()
        key_signatures[0] = chords.parse('C')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C')
        chord_progression[5 * config.resolution] = chords.parse('A-')

        set_config(sequence, chord_progression, key_signatures)

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
        pattern = read_pattern(constants.TEST_MIDI + '2beat_join.mid')
        sequence = domain.Sequence(pattern=pattern[0])

        key_signatures = ks.KeySignatures()
        key_signatures[0] = chords.parse('C')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C')

        set_config(sequence, chord_progression, key_signatures)

        syncopation = transforms.JoinTransform(2, config.resolution, sequence)
        nonsyncopated = transforms.JoinTransform(2, 0, sequence)

        self.assertTrue(syncopation.is_syncopation())
        self.assertFalse(nonsyncopated.is_syncopation())

    def test__JoinTransform_crosses_bar_line(self):
        pattern = read_pattern(constants.TEST_MIDI + '2beat_join.mid')
        sequence = domain.Sequence(pattern=pattern[0])

        key_signatures = ks.KeySignatures()
        key_signatures[0] = chords.parse('C')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C')

        set_config(sequence, chord_progression, key_signatures)

        over_bar_line = transforms.JoinTransform(2, config.resolution * 3, sequence)
        inside_bar = transforms.JoinTransform(2, config.resolution * 2, sequence)

        self.assertTrue(over_bar_line.crosses_bar_line())
        self.assertFalse(inside_bar.crosses_bar_line())

    def test__EighthNoteTransform_causes_flickering(self):
        pattern = read_pattern(constants.TEST_MIDI + 'flicker.mid')
        sequence = domain.Sequence(pattern=pattern[0])

        key_signatures = ks.KeySignatures()
        key_signatures[0] = chords.parse('C')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C')

        set_config(sequence, chord_progression, key_signatures)

        transform1 = transforms.WholeStepNeighborTransform((1 * config.resolution * 4) + (1 * config.resolution), sequence)

        transform2 = transforms.HalfStepNeighborTransform((2 * config.resolution * 4) + (1 * config.resolution), sequence)

        transform3 = transforms.HalfStepNeighborTransform((2 * config.resolution * 4) + (1 * config.resolution), sequence)

        self.assertTrue(transform1.causes_flickering())
        self.assertTrue(transform2.causes_flickering())
        self.assertTrue(transform3.causes_flickering())


def set_config(soprano, chord_progression, key_signatures):
    time_signatures = rhythm.TimeSignatures()
    time_signatures[0] = rhythm.TimeSignature(numerator=4, denominator=4)

    config.soprano = soprano
    config.chord_progression = chord_progression
    config.key_signatures = key_signatures
    config.time_signatures = time_signatures


def read_pattern(file_name):
    try:
        return midi.read_midifile(file_name)
    except TypeError:
        print 'Midi file is malformed. Try exporting a new one from any DAW'
        exit(2)
    raise Exception
