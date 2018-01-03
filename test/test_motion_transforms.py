from unittest import TestCase

import midi

from cybach import chords, transforms
from cybach import domain
from cybach import ks
from cybach import parts
from cybach.constants import RESOLUTION
from cybach.pat_util import normalize_resolution


class TestMotionTransforms(TestCase):

    def test_TwoBeatJoinTransform_is_applicable(self):
        pattern = normalize_resolution(read_pattern('test/midi/2beat_join.mid'))
        sequence = domain.Sequence(track=pattern[0])

        self.assertTrue(transforms.TwoBeatJoinTransform.applicable_at(0, sequence))
        self.assertFalse(transforms.ThreeBeatJoinTransform.applicable_at(0, sequence))

    def test_ThreeBeatJoinTransform_is_applicable(self):
        pattern = normalize_resolution(read_pattern('test/midi/3beat_join.mid'))
        sequence = domain.Sequence(track=pattern[0])

        self.assertTrue(transforms.ThreeBeatJoinTransform.applicable_at(0, sequence))
        self.assertFalse(transforms.FourBeatJoinTransform.applicable_at(0, sequence))

    def test_FourBeatJoinTransform_is_applicable(self):
        pattern = normalize_resolution(read_pattern('test/midi/4beat_join.mid'))
        sequence = domain.Sequence(track=pattern[0])

        self.assertTrue(transforms.FourBeatJoinTransform.applicable_at(0, sequence))
        self.assertFalse(transforms.FiveBeatJoinTransform.applicable_at(0, sequence))

    def test_FiveBeatJoinTransform_is_applicable(self):
        pattern = normalize_resolution(read_pattern('test/midi/5beat_join.mid'))
        sequence = domain.Sequence(track=pattern[0])

        self.assertTrue(transforms.FiveBeatJoinTransform.applicable_at(0, sequence))
        self.assertFalse(transforms.SixBeatJoinTransform.applicable_at(0, sequence))

    def test_SixBeatJoinTransform_is_applicable(self):
        pattern = normalize_resolution(read_pattern('test/midi/6beat_join.mid'))
        sequence = domain.Sequence(track=pattern[0])

        self.assertTrue(transforms.SixBeatJoinTransform.applicable_at(0, sequence))

    def test_ApproachTransform_is_applicable(self):
        pattern = normalize_resolution(read_pattern('test/midi/approach.mid'))
        sequence = domain.Sequence(track=pattern[0], part=parts.BASS)

        key_sigs = ks.KeySignatures()
        key_sigs[0] = chords.parse('A')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('A')
        chord_progression[RESOLUTION] = chords.parse('D')
        chord_progression[RESOLUTION * 4] = chords.parse('E')
        chord_progression[RESOLUTION * 5] = chords.parse('A')

        self.assertTrue(transforms.ApproachTransform.applicable_at(0, sequence, chord_progression))
        self.assertTrue(
            transforms.ApproachTransform.applicable_at(4 * RESOLUTION, sequence, chord_progression))
        self.assertFalse(
            transforms.ApproachTransform.applicable_at(6 * RESOLUTION, sequence, chord_progression))

    def test_HalfStepNeighborTransform_is_applicable(self):
        pattern = normalize_resolution(read_pattern('test/midi/neighbor.mid'))
        sequence = domain.Sequence(track=pattern[0], part=parts.BASS)

        key_sigs = ks.KeySignatures()
        key_sigs[0] = chords.parse('C')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C')

        self.assertTrue(transforms.HalfStepNeighborTransform.applicable_at(0, sequence, key_sigs))
        self.assertFalse(
            transforms.HalfStepNeighborTransform.applicable_at(2 * RESOLUTION, sequence, key_sigs))
        self.assertTrue(
            transforms.HalfStepNeighborTransform.applicable_at(4 * RESOLUTION, sequence, key_sigs))

    def test_WholeStepNeighborTransform_is_applicable(self):
        pattern = normalize_resolution(read_pattern('test/midi/neighbor.mid'))
        sequence = domain.Sequence(track=pattern[0], part=parts.BASS)

        key_sigs = ks.KeySignatures()
        key_sigs[0] = chords.parse('C')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C')

        self.assertTrue(transforms.WholeStepNeighborTransform.applicable_at(0, sequence, key_sigs))
        self.assertTrue(
            transforms.WholeStepNeighborTransform.applicable_at(2 * RESOLUTION, sequence, key_sigs))

    def test_MajorThirdScalarTransform_is_applicable(self):
        pattern = normalize_resolution(read_pattern('test/midi/maj3_scalar.mid'))
        sequence = domain.Sequence(track=pattern[0], part=parts.BASS)

        key_sigs = ks.KeySignatures()
        key_sigs[0] = chords.parse('C')

        self.assertTrue(transforms.MajorThirdScalarTransform.applicable_at(0, sequence, key_sigs))
        self.assertFalse(transforms.MajorThirdScalarTransform.applicable_at(2, sequence, key_sigs))

    def test_MinorThirdScalarTransform_is_applicable(self):
        pattern = normalize_resolution(read_pattern('test/midi/min3_scalar.mid'))
        sequence = domain.Sequence(track=pattern[0], part=parts.BASS)

        key_sigs = ks.KeySignatures()
        key_sigs[0] = chords.parse('C-')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C-')

        self.assertTrue(transforms.MinorThirdScalarTransform.applicable_at(0, sequence, key_sigs))
        self.assertFalse(transforms.MinorThirdScalarTransform.applicable_at(2, sequence, key_sigs))

    def test_ArpeggialTransform_is_applicable(self):
        pattern = normalize_resolution(read_pattern('test/midi/arpeggial.mid'))
        sequence = domain.Sequence(track=pattern[0], part=parts.ALTO)

        key_sigs = ks.KeySignatures()
        key_sigs[0] = chords.parse('C')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C')
        chord_progression[5 * RESOLUTION] = chords.parse('A-')

        self.assertTrue(transforms.ArpeggialTransform.applicable_at(0, sequence, chord_progression))
        self.assertTrue(
            transforms.ArpeggialTransform.applicable_at(4 * RESOLUTION, sequence, chord_progression))

    def test_MajorThirdScalarTransform_intermediate_pitch(self):
        pattern = normalize_resolution(read_pattern('test/midi/maj3_scalar.mid'))
        sequence = domain.Sequence(track=pattern[0], part=parts.BASS)

        key_sigs = ks.KeySignatures()
        key_sigs[0] = chords.parse('C')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C')

        trans = transforms.MajorThirdScalarTransform(0, sequence, key_sigs, chord_progression)
        pitch_should_be = sequence[0].pitch() + 2

        self.assertEqual(trans.intermediate_pitch, pitch_should_be)

    def test_MinorThirdScalarTransform_intermediate_pitch(self):
        pattern = normalize_resolution(read_pattern('test/midi/min3_scalar.mid'))
        sequence = domain.Sequence(track=pattern[0], part=parts.BASS)

        key_sigs = ks.KeySignatures()
        key_sigs[0] = chords.parse('C-')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C-')

        trans = transforms.MinorThirdScalarTransform(0, sequence, key_sigs, chord_progression)
        pitch_should_be = sequence[0].pitch() + 2

        self.assertEqual(trans.intermediate_pitch, pitch_should_be)

    def test_ArpeggialTransform_intermediate_pitch(self):
        pattern = normalize_resolution(read_pattern('test/midi/arpeggial.mid'))
        sequence = domain.Sequence(track=pattern[0], part=parts.ALTO)

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C')

        trans = transforms.ArpeggialTransform(0, sequence, chord_progression, chord_progression)
        major_third_above = sequence[0].pitch() + 4

        self.assertEqual(trans.intermediate_pitch, major_third_above)

    def test_HalfStepNeighborTransform_intermediate_pitch(self):
        pattern = normalize_resolution(read_pattern('test/midi/neighbor.mid'))
        sequence = domain.Sequence(track=pattern[0], part=parts.BASS)

        key_sigs = ks.KeySignatures()
        key_sigs[0] = chords.parse('C')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C')

        trans = transforms.HalfStepNeighborTransform(0, sequence, key_sigs, chord_progression)
        half_step_below = sequence[0].pitch() - 1

        self.assertEqual(trans.intermediate_pitch, half_step_below)

    def test_WholeStepNeighborTransform_intermediate_pitch(self):
        pattern = normalize_resolution(read_pattern('test/midi/neighbor.mid'))
        sequence = domain.Sequence(track=pattern[0], part=parts.BASS)

        key_sigs = ks.KeySignatures()
        key_sigs[0] = chords.parse('C')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C')

        trans = transforms.WholeStepNeighborTransform(0, sequence, key_sigs, chord_progression)
        whole_step_above = sequence[0].pitch() + 2

        self.assertEqual(trans.intermediate_pitch, whole_step_above)

    def test_ApproachTransform_intermediate_pitch(self):
        pattern = normalize_resolution(read_pattern('test/midi/approach.mid'))
        sequence = domain.Sequence(track=pattern[0], part=parts.BASS)

        key_sigs = ks.KeySignatures()
        key_sigs[0] = chords.parse('A')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('A')
        chord_progression[RESOLUTION] = chords.parse('D')

        trans = transforms.ApproachTransform(0, sequence, key_sigs, chord_progression)
        c_sharp_below = sequence[0].pitch() - 8

        self.assertEqual(trans.intermediate_pitch, c_sharp_below)

    def test_MajorThirdScalarTransform_synergy(self):
        scalar_pattern = normalize_resolution(read_pattern('test/midi/maj3_scalar.mid'))
        neighbor_pattern = normalize_resolution(read_pattern('test/midi/neighbor.mid'))

        scalar_sequence = domain.Sequence(track=scalar_pattern[0], part=parts.TENOR)
        neighbor_sequence = domain.Sequence(track=neighbor_pattern[0], part=parts.BASS)

        key_sigs = ks.KeySignatures()
        key_sigs[0] = chords.parse('C')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C')

        # Small tests, reall should ever change unless we manipulate values
        scalar_trans = transforms.MajorThirdScalarTransform(0, scalar_sequence, key_sigs, chord_progression)
        same_trans = transforms.MajorThirdScalarTransform(0, scalar_sequence, key_sigs, chord_progression)
        join = transforms.TwoBeatJoinTransform(0, scalar_sequence, key_sigs)

        self.assertEqual(scalar_trans.synergy(same_trans), -0.02)
        self.assertEqual(scalar_trans.synergy(join), 0.0)

        # More important tests that have more logic attached
        dom_neighbor_trans = transforms.HalfStepNeighborTransform(0, neighbor_sequence, key_sigs, chord_progression)
        subdom_neighbor_trans = transforms.HalfStepNeighborTransform(96, neighbor_sequence, key_sigs, chord_progression)

        self.assertEqual(scalar_trans.synergy(dom_neighbor_trans), 0.1)
        self.assertEqual(scalar_trans.synergy(subdom_neighbor_trans), 0.05)

    def test_ApproachTransform_set_musicality(self):
        pattern = normalize_resolution(read_pattern('test/midi/approach.mid'))
        sequence = domain.Sequence(track=pattern[0], part=parts.BASS)

        key_signatures = ks.KeySignatures()
        key_signatures[0] = chords.parse('A')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('A')
        chord_progression[RESOLUTION] = chords.parse('D')
        chord_progression[96] = chords.parse('A')

        weaker_trans = transforms.ApproachTransform(264, sequence, key_signatures, chord_progression)
        stronger_trans = transforms.ApproachTransform(0, sequence, key_signatures, chord_progression)
        strong_trans = transforms.ApproachTransform(96, sequence, key_signatures, chord_progression)

        self.assertEqual(weaker_trans.intrinsic_musicality, 0.07)
        self.assertEqual(stronger_trans.intrinsic_musicality, 0.12)
        self.assertEqual(strong_trans.intrinsic_musicality, 0.2)

    def test_MajorThird_set_musicality(self):
        pattern = normalize_resolution(read_pattern('test/midi/linear_motion.mid'))
        sequence = domain.Sequence(track=pattern[0])

        key_signatures = ks.KeySignatures()
        key_signatures[0] = chords.parse('C')

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C')

        trans = transforms.MajorThirdScalarTransform(144, sequence, key_signatures, chord_progression)
        self.assertEqual(trans.intrinsic_musicality, 0.2)

    def test_ArpeggialTransform_set_musicality(self):
        pattern = normalize_resolution(read_pattern('test/midi/arpeggial.mid'))
        sequence = domain.Sequence(track=pattern[0], part=parts.ALTO)

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('C')
        chord_progression[120] = chords.parse('A-')

        weaker_trans = transforms.ArpeggialTransform(0, sequence, chord_progression, chord_progression)
        stronger_trans = transforms.ArpeggialTransform(96, sequence, chord_progression, chord_progression)

        self.assertEqual(weaker_trans.intrinsic_musicality, 0.08)
        self.assertEqual(stronger_trans.intrinsic_musicality, 0.14)

def read_pattern(file_name):
    try:
        return midi.read_midifile(file_name)
    except TypeError:
        print 'Midi file is malformed. Try exporting a new one from any DAW'
        exit(2)
    raise Exception
