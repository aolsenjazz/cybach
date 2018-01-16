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

        zero_tendency = domain.Sequence(pattern=pattern[0], part=parts.BASS, motion_tendency=0.0)
        no_tendency = domain.Sequence(pattern=pattern[0], part=parts.BASS, motion_tendency=0.5)
        max_tendency = domain.Sequence(pattern=pattern[0], part=parts.BASS, motion_tendency=1.0)

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
        sequence = domain.Sequence(pattern=pattern[0], part=parts.BASS, motion_tendency=0.0)

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

        # sequence isn't very relevant here, just establishes time sig really
        pattern = normalize_resolution(read_pattern('test/midi/quarter_arpeg.mid'))
        sequence = domain.Sequence(pattern=pattern[0], part=parts.BASS, motion_tendency=0.0)

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('G')
        chord_progression[2 * RESOLUTION] = chords.parse('E-')

        self.assertEqual(note_picker.root_tendency_score(g, 0, sequence, chord_progression), 0.10)
        self.assertEqual(note_picker.root_tendency_score(g, 1 * RESOLUTION, sequence, chord_progression), 0.03)
        self.assertAlmostEqual(note_picker.root_tendency_score(e, 2 * RESOLUTION, sequence, chord_progression), 0.25)

    def test__get_motion_score(self):
        pattern = normalize_resolution(read_pattern('test/midi/parallel1.mid'))
        alto = domain.Sequence(pattern=pattern[0], part=parts.BASS, motion_tendency=0.0)

        pattern = normalize_resolution(read_pattern('test/midi/parallel2.mid'))
        tenor = domain.Sequence(pattern=pattern[0], part=parts.BASS, motion_tendency=0.0)

        pattern = normalize_resolution(read_pattern('test/midi/quarter_arpeg.mid'))
        bass = domain.Sequence(pattern=pattern[0], part=parts.BASS, motion_tendency=0.0)

        irrelevant_pitch = 11

        # [0] = bass, [1] = tenor, [2] = alto
        candidate = [irrelevant_pitch, notes.MIDI_VALUES['A5'], notes.MIDI_VALUES['D5']]

        self.assertEqual(note_picker.get_motion_score(candidate, 0, alto, tenor, bass), 0.0)
        self.assertEqual(note_picker.get_motion_score(candidate, RESOLUTION, alto, tenor, bass), -0.20)


def read_pattern(file_name):
    try:
        return midi.read_midifile(file_name)
    except TypeError:
        print 'Midi file is malformed. Try exporting a new one from any DAW'
        exit(2)
    raise Exception
