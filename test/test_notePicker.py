from unittest import TestCase
from cybach import note_picker
from cybach import notes
from cybach.pat_util import normalize_resolution
from cybach import domain
from cybach import chords
import midi
from cybach import parts
from cybach.constants import RESOLUTION


class TestNotePicker(TestCase):
    # deprecated
    # def test___contains_parallel_movement(self):
    #     c_major = notes.Note(12), notes.Note(19), notes.Note(24), notes.Note(28)
    #     non_parallel = notes.Note(11), notes.Note(19), notes.Note(26), notes.Note(31)
    #     perfect_fifth_movement = notes.Note(5), notes.Note(12), notes.Note(24), notes.Note(29)
    #     perfect_octave_movement = notes.Note(11), notes.Note(19), notes.Note(23), notes.Note(26)
    #     perfect_fourth_movement = notes.Note(12), notes.Note(24), notes.Note(29), notes.Note(33)
    #
    #     self.assertTrue(note_picker.contains_parallel_movement(c_major, perfect_fifth_movement))
    #     self.assertTrue(note_picker.contains_parallel_movement(c_major, perfect_octave_movement))
    #     self.assertTrue(note_picker.contains_parallel_movement(c_major, perfect_fourth_movement))
    #     self.assertFalse(note_picker.contains_parallel_movement(c_major, non_parallel))

    # deprecated
    # def test___first_at_or_below(self):
    #     threshold = 36
    #     note = notes.Note(midi_value=7)
    #     first_at_or_below = 31
    #
    #     self.assertEqual(first_at_or_below, note_picker.first_at_or_below(note, threshold))

    # deprecated
    # def test___all_available_pitches(self):
    #     pitches = notes.Note(text_value='A'), notes.Note(text_value='C')
    #     low_threshold = 10
    #     high_threshold = 30
    #
    #     c1 = notes.MIDI_VALUES['C1']
    #     a1 = notes.MIDI_VALUES['A1']
    #     c2 = notes.MIDI_VALUES['C2']
    #
    #     available_pitches = note_picker.all_available_pitches(pitches, low_threshold, high_threshold)
    #
    #     self.assertTrue(c1 in available_pitches)
    #     self.assertTrue(a1 in available_pitches)
    #     self.assertTrue(c2 in available_pitches)
    #     self.assertEqual(len(available_pitches), 3)

    def test__threshold_encroachment_score(self):
        min_thresh = 10
        min_lim = 13
        max_thresh = 20
        max_lim = 17
        min_return_val = -0.04
        max_return_val = -0.08

        self.assertEqual(note_picker.threshold_encroachment_score(11, min_thresh, min_lim), min_return_val)
        self.assertEqual(note_picker.threshold_encroachment_score(20, max_thresh, max_lim), max_return_val)
        self.assertEqual(note_picker.threshold_encroachment_score(19, max_thresh, max_lim), min_return_val)
        self.assertEqual(note_picker.threshold_encroachment_score(15, min_thresh, min_lim), 0.0)
        self.assertEqual(note_picker.threshold_encroachment_score(15, max_thresh, max_lim), 0.0)

    def test__preferred_register_scored(self):
        min_thresh = 10
        min_lim = 13
        max_thresh = 20
        max_lim = 17
        min_return_val = -0.02
        max_return_val = -0.03

        self.assertEqual(note_picker.preferred_register_score(11, min_thresh, min_lim), min_return_val)
        self.assertEqual(note_picker.preferred_register_score(20, max_thresh, max_lim), max_return_val)
        self.assertEqual(note_picker.preferred_register_score(19, max_thresh, max_lim), min_return_val)
        self.assertEqual(note_picker.preferred_register_score(15, min_thresh, min_lim), 0.0)
        self.assertEqual(note_picker.preferred_register_score(15, max_thresh, max_lim), 0.0)

    def test__motion_tendency_score(self):
        pattern = normalize_resolution(read_pattern('test/midi/quarter_arpeg.mid'))

        zero_tendency = domain.Sequence(track=pattern[0], part=parts.BASS, motion_tendency=0.0)
        no_tendency = domain.Sequence(track=pattern[0], part=parts.BASS, motion_tendency=0.5)
        max_tendency = domain.Sequence(track=pattern[0], part=parts.BASS, motion_tendency=1.0)

        beat_0_pitch = 59
        beat_2_pitch = 62

        # start of midi clip, no motion, return 0
        self.assertEqual(note_picker.motion_tendency_score(beat_0_pitch, 0, zero_tendency), 0.0)

        # same note as last beat
        self.assertEqual(note_picker.motion_tendency_score(beat_0_pitch, RESOLUTION, zero_tendency), 0.25)

        # client doesn't care either way
        self.assertEqual(note_picker.motion_tendency_score(beat_0_pitch, RESOLUTION, no_tendency), 0.0)

        # client much prefers motion
        self.assertEqual(note_picker.motion_tendency_score(beat_2_pitch, RESOLUTION * 1, max_tendency), 0.25)

    def test__linear_motion_score(self):
        pattern = normalize_resolution(read_pattern('test/midi/quarter_arpeg.mid'))
        sequence = domain.Sequence(track=pattern[0], part=parts.BASS, motion_tendency=0.0)

        beat_0_pitch = 59
        motion_pitch = 61

        # start of midi clip, no motion, return 0
        self.assertEqual(note_picker.linear_motion_score(beat_0_pitch, 0, sequence), 0.0)

        # same note as last beat
        self.assertEqual(note_picker.linear_motion_score(beat_0_pitch, RESOLUTION, sequence), 0.0)

        # linear motion exists
        self.assertEqual(note_picker.linear_motion_score(motion_pitch, RESOLUTION, sequence), 0.2)

    def test__root_tendency_score(self):
        g = 55
        e = 64

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('G')
        chord_progression[1 * RESOLUTION] = chords.parse('G')
        chord_progression[2 * RESOLUTION] = chords.parse('E-')
        chord_progression[3 * RESOLUTION] = chords.parse('E-')

        self.assertEqual(note_picker.root_tendency_score(g, 0, chord_progression), 0.10)
        self.assertEqual(note_picker.root_tendency_score(g, 1 * RESOLUTION, chord_progression), 0.03)
        self.assertEqual(note_picker.root_tendency_score(e, 2 * RESOLUTION, chord_progression), 0.10)


def read_pattern(file_name):
    try:
        return midi.read_midifile(file_name)
    except TypeError:
        print 'Midi file is malformed. Try exporting a new one from any DAW'
        exit(2)
    raise Exception
