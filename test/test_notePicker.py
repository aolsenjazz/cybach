from unittest import TestCase
import note_picker
import notes
from pat_util import normalize_resolution
import domain
import chords
import vars
import constants
import midi
import parts
from constants import RESOLUTION


class TestNotePicker(TestCase):

    def test__threshold_encroachment_score(self):
        min_thresh = 10
        min_lim = 13
        max_thresh = 20
        max_lim = 17
        min_return_val = (2 ** abs(2)) * vars.THRESHOLD_ENCROACHMENT
        max_return_val = (2 ** abs(3)) * vars.THRESHOLD_ENCROACHMENT

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
        min_return_val = vars.PREFERRED_REGISTER * 2
        max_return_val = vars.PREFERRED_REGISTER * 3

        self.assertEqual(note_picker.preferred_register_score(11, min_thresh, min_lim), min_return_val)
        self.assertEqual(note_picker.preferred_register_score(20, max_thresh, max_lim), max_return_val)
        self.assertEqual(note_picker.preferred_register_score(19, max_thresh, max_lim), min_return_val)
        self.assertEqual(note_picker.preferred_register_score(15, min_thresh, min_lim), 0.0)
        self.assertEqual(note_picker.preferred_register_score(15, max_thresh, max_lim), 0.0)

    def test__motion_tendency_score(self):
        pattern = normalize_resolution(read_pattern(constants.TEST_MIDI + 'quarter_arpeg.mid'))

        zero_tendency = domain.Sequence(pattern=pattern[0], part=parts.BASS, configuration={'motion_tendency': 0.0})
        no_tendency = domain.Sequence(pattern=pattern[0], part=parts.BASS, configuration={})
        max_tendency = domain.Sequence(pattern=pattern[0], part=parts.BASS, configuration={'motion_tendency': 1.0})

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
        pattern = normalize_resolution(read_pattern(constants.TEST_MIDI + 'quarter_arpeg.mid'))
        sequence = domain.Sequence(pattern=pattern[0], part=parts.BASS, configuration={})

        beat_0_pitch = 59
        motion_pitch = 61

        # start of midi clip, no motion, return 0
        self.assertEqual(note_picker.linear_motion_score(beat_0_pitch, 0, sequence), 0.0)

        # same note as last beat
        self.assertEqual(note_picker.linear_motion_score(beat_0_pitch, RESOLUTION, sequence), 0.0)

        # linear motion exists
        self.assertEqual(note_picker.linear_motion_score(motion_pitch, RESOLUTION, sequence), vars.LINEAR_MOTION)

    def test__root_tendency_score(self):
        g = 55
        e = 64

        # sequence isn't very relevant here, just establishes time sig really
        pattern = normalize_resolution(read_pattern(constants.TEST_MIDI + 'quarter_arpeg.mid'))
        sequence = domain.Sequence(pattern=pattern[0], part=parts.BASS, configuration={})

        chord_progression = chords.ChordProgression()
        chord_progression[0] = chords.parse('G')
        chord_progression[2 * RESOLUTION] = chords.parse('E-')

        self.assertEqual(note_picker.root_tendency_score(g, 0, sequence, chord_progression), vars.FIRST_BEAT_BASS_ROOT)
        self.assertEqual(note_picker.root_tendency_score(g, 1 * RESOLUTION, sequence, chord_progression),
                         vars.BASS_ROOT_SAME_CHORD)
        self.assertEqual(note_picker.root_tendency_score(e, 2 * RESOLUTION, sequence, chord_progression),
                               vars.BASS_ROOT_NEW_CHORD + vars.BIG_BEAT_BASS_ROOT)

    def test__get_motion_score(self):
        pattern = normalize_resolution(read_pattern(constants.TEST_MIDI + 'parallel1.mid'))
        alto = domain.Sequence(pattern=pattern[0], part=parts.BASS, configuration={})

        pattern = normalize_resolution(read_pattern(constants.TEST_MIDI + 'parallel2.mid'))
        tenor = domain.Sequence(pattern=pattern[0], part=parts.BASS, configuration={})

        pattern = normalize_resolution(read_pattern(constants.TEST_MIDI + 'quarter_arpeg.mid'))
        bass = domain.Sequence(pattern=pattern[0], part=parts.BASS, configuration={})

        irrelevant_pitch = 11

        # [0] = bass, [1] = tenor, [2] = alto
        candidate = {'bass': irrelevant_pitch, 'tenor': notes.MIDI_VALUES['A5'], 'alto': notes.MIDI_VALUES['D5']}

        self.assertEqual(note_picker.get_motion_score(candidate, 0, alto, tenor, bass), 0.0)
        self.assertEqual(note_picker.get_motion_score(candidate, RESOLUTION, alto, tenor, bass), vars.PARALLEL_MOVEMENT)

    def test__flicker_avoidance_score(self):
        pattern = normalize_resolution(read_pattern(constants.TEST_MIDI + 'flicker.mid'))
        sequence = domain.Sequence(pattern=pattern[0], part=parts.BASS, configuration={})

        c = notes.MIDI_VALUES['C5']
        e = notes.MIDI_VALUES['E5']

        self.assertEqual(note_picker.flicker_avoidance_score(c, RESOLUTION * 2, sequence),
                         vars.SAME_PITCH_AS_TWO_BEATS_AGO)
        self.assertEqual(note_picker.flicker_avoidance_score(e, RESOLUTION * 3, sequence),
                         vars.TWO_BEATS_REPEATED)


def read_pattern(file_name):
    try:
        return midi.read_midifile(file_name)
    except TypeError:
        print 'Midi file is malformed. Try exporting a new one from any DAW'
        exit(2)
    raise Exception
