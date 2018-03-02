import unittest

import midi
import transforms
import chords
import fileloader
import pitches
import constants
import pitches
import sequences


class TestTransforms(unittest.TestCase):

    def test__direction_permutations(self):
        one_direction = [(1, ), (0, ), (-1, )]
        two_directions = [(1, 1), (1, 0), (1, -1), (0, 1), (0, 0), (0, -1), (-1, 1), (-1, 0), (-1, -1)]

        self.assertEqual(one_direction, transforms.direction_permutations(1))
        self.assertEqual(two_directions, transforms.direction_permutations(2))

    def test__PitchSet_unidirectional(self):
        down = transforms.PitchSet(60, 50, 58, 55)
        up = transforms.PitchSet(60, 70, 62, 65)
        bidirectional = transforms.PitchSet(60, 65, 62, 70)

        self.assertTrue(down.unidirectional)
        self.assertTrue(up.unidirectional)
        self.assertFalse(bidirectional.unidirectional)

    def test__pitch_set_for_directions(self):
        bounded_pitches = [i for i in range(60, 73) if i in chords.parse('C').scale()]
        start = pitches.MIDI_VALUES['G5']
        target = pitches.MIDI_VALUES['E5']
        one_direction = [1]
        two_directions = [-1, 1]

        self.assertEqual(3, len(transforms.pitch_sets_for_directions(bounded_pitches, start, target, one_direction)))
        self.assertEqual(22, len(transforms.pitch_sets_for_directions(bounded_pitches, start, target, two_directions)))

    def test__get_rhythm_sets(self):
        max_time_unit_count = 2
        minimum_time_unit = 24

        self.assertEqual(3, len(transforms.get_rhythm_sets(minimum_time_unit, max_time_unit_count, 96)[0]))

    def test__get_all_transforms_minimal(self):
        fileloader.load(constants.TEST_MIDI + 'maj3_scalar.mid', False)
        chords.write('C')

        alto = sequences.alto()

        g4 = sequences.Note(alto, 0, 96, pitches.MIDI_VALUES['G4'])
        b4 = sequences.Note(alto, 96, 192, pitches.MIDI_VALUES['B4'])

        alto.add_entities(g4, b4)

        self.assertEqual(124, len(transforms.get_all_transforms(0, 96, 4)))

    def test__get_all_transforms(self):
        fileloader.load(constants.TEST_MIDI + 'maj3_scalar.mid', False)
        chords.write('C')

        alto = sequences.alto()
        tenor = sequences.tenor()
        bass = sequences.bass()

        g4_alto = sequences.Note(alto, 0, 96, pitches.MIDI_VALUES['G4'])
        b4_alto = sequences.Note(alto, 96, 192, pitches.MIDI_VALUES['B4'])
        e4_tenor = sequences.Note(tenor, 0, 96, pitches.MIDI_VALUES['E4'])
        g4_tenor = sequences.Note(tenor, 96, 192, pitches.MIDI_VALUES['G4'])
        c4_bass = sequences.Note(bass, 0, 96, pitches.MIDI_VALUES['C4'])
        e4_bass = sequences.Note(bass, 96, 192, pitches.MIDI_VALUES['E4'])

        alto.add_entities(g4_alto, b4_alto)
        tenor.add_entities(e4_tenor, g4_tenor)
        bass.add_entities(c4_bass, e4_bass)

        t = transforms.get_all_transforms(0, 96, 3)
        e = 1

        # self.assertEqual(124, len(transforms.get_all_transforms(0, 96)))
