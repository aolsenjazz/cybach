from unittest import TestCase

import midi

import chords
import config
import constants
import fileloader
import ks
import note_picker
import parts
import pitches
import sequences
import vars
from rhythm import time


class TestNotePicker(TestCase):

    def tearDown(self):
        super(TestNotePicker, self).tearDown()
        chords.clear()
        time.clear()
        ks.clear()

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
        fileloader.load(constants.TEST_MIDI + 'quarter_arpeg.mid', False)

        zero_tendency = sequences.AccompanimentSequence(config.song_length, parts.BASS, {'motion_tendency': 0.0})
        no_tendency = sequences.AccompanimentSequence(config.song_length, parts.BASS)
        max_tendency = sequences.AccompanimentSequence(config.song_length,  parts.BASS, {'motion_tendency': 1.0})

        beat_0_pitch = 59
        beat_2_pitch = 62

        beat_0_entity = sequences.Note(zero_tendency, 0, 96, beat_0_pitch)
        beat_2_entity = sequences.Note(zero_tendency, 192, 288, beat_2_pitch)

        zero_tendency.add_entities(beat_0_entity, beat_2_entity)
        no_tendency.add_entities(beat_0_entity, beat_2_entity)
        max_tendency.add_entities(beat_0_entity, beat_2_entity)

        # start of midi clip, no motion, return 0
        self.assertEqual(0.0, note_picker.motion_tendency_score(beat_0_pitch, time.beat_at_index(0), zero_tendency))

        # same note as last beat
        self.assertEqual(0.25, note_picker.motion_tendency_score(beat_0_pitch, time.beat_at_index(1), zero_tendency))

        # client doesn't care either way
        self.assertEqual(0.0, note_picker.motion_tendency_score(beat_0_pitch, time.beat_at_index(1), no_tendency))

        # client much prefers motion
        self.assertEqual(0.25, note_picker.motion_tendency_score(beat_2_pitch, time.beat_at_index(1), max_tendency))

    def test__linear_motion_score(self):
        fileloader.load(constants.TEST_MIDI + 'quarter_arpeg.mid', False)
        sequence = sequences.soprano()

        beat_0_pitch = 59
        motion_pitch = 61

        # start of midi clip, no motion, return 0
        self.assertEqual(0.0, note_picker.linear_motion_score(beat_0_pitch, time.beat_at_index(0), sequence))

        # same note as last beat
        self.assertEqual(0.0, note_picker.linear_motion_score(beat_0_pitch, time.beat_at_index(1), sequence))

        # linear motion exists
        self.assertEqual(vars.LINEAR_MOTION, note_picker.linear_motion_score(motion_pitch, time.beat_at_index(1), sequence))

    def test__root_tendency_score(self):
        fileloader.load(constants.TEST_MIDI + 'quarter_arpeg.mid', False)

        chords.write('G')
        chords.write('E-', beat=2)

        g = 55
        e = 64

        beat1 = time.beat_at_index(0)
        beat2 = time.beat_at_index(1)
        beat3 = time.beat_at_index(2)

        self.assertEqual(vars.FIRST_BEAT_BASS_ROOT, note_picker.bass_note_tendency_score(g, beat1))
        self.assertEqual(vars.BASS_ROOT_SAME_CHORD,note_picker.bass_note_tendency_score(g, beat2))
        self.assertEqual(vars.BASS_NOTE_NEW_CHORD, note_picker.bass_note_tendency_score(e, beat3))

    def test__get_motion_score(self):
        fileloader.load(constants.TEST_MIDI + 'parallel1.mid', False)
        soprano = sequences.soprano()
        tenor = sequences.RootSequence(read_pattern(constants.TEST_MIDI + 'parallel2.mid')[0])

        irrelevant_pitch = 11

        # [0] = alto, [1] = tenor, [2] = bass
        candidate = pitches.MIDI_VALUES['D5'], pitches.MIDI_VALUES['A5'], irrelevant_pitch,

        self.assertEqual(0.0, note_picker
                         .parallel_motion_score(candidate, time.beat_at_index(0),
                                                soprano, sequences.alto(), tenor, sequences.bass()))
        self.assertEqual(vars.PARALLEL_MOVEMENT, note_picker
                         .parallel_motion_score(candidate, time.beat_at_index(1),
                                                soprano, sequences.alto(), tenor, sequences.bass()))

    def test__flicker_avoidance_score(self):
        fileloader.load(constants.TEST_MIDI + 'flicker.mid', False)
        sequence = sequences.soprano()

        c = pitches.MIDI_VALUES['C5']
        e = pitches.MIDI_VALUES['E5']

        beat2 = time.beat_at_index(2)
        beat3 = time.beat_at_index(3)

        self.assertEqual(1 * vars.FLICKER_COEF, note_picker.flicker_avoidance_score(c, beat2, sequence))
        self.assertEqual(2 * vars.FLICKER_COEF, note_picker.flicker_avoidance_score(e, beat3, sequence))


def read_pattern(file_name):
    try:
        return midi.read_midifile(file_name)
    except TypeError:
        print 'Midi file is malformed. Try exporting a new one from any DAW'
        exit(2)
    raise Exception
