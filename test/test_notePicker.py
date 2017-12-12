from unittest import TestCase
from cybach import note_picker
from cybach import notes


class TestNotePicker(TestCase):
    def test___contains_parallel_movement(self):
        c_major = notes.Note(12), notes.Note(19), notes.Note(24), notes.Note(28)
        non_parallel = notes.Note(11), notes.Note(19), notes.Note(26), notes.Note(31)
        perfect_fifth_movement = notes.Note(5), notes.Note(12), notes.Note(24), notes.Note(29)
        perfect_octave_movement = notes.Note(11), notes.Note(19), notes.Note(23), notes.Note(26)
        perfect_fourth_movement = notes.Note(12), notes.Note(24), notes.Note(29), notes.Note(33)

        self.assertTrue(note_picker.contains_parallel_movement(c_major, perfect_fifth_movement))
        self.assertTrue(note_picker.contains_parallel_movement(c_major, perfect_octave_movement))
        self.assertTrue(note_picker.contains_parallel_movement(c_major, perfect_fourth_movement))
        self.assertFalse(note_picker.contains_parallel_movement(c_major, non_parallel))

    def test___first_at_or_below(self):
        threshold = 36
        note = notes.Note(midi_value=7)
        first_at_or_below = 31

        self.assertEqual(first_at_or_below, note_picker.first_at_or_below(note, threshold))

    def test___all_available_pitches(self):
        pitches = notes.Note(text_value='A'), notes.Note(text_value='C')
        low_threshold = 10
        high_threshold = 30

        c1 = notes.MIDI_VALUES['C1']
        a1 = notes.MIDI_VALUES['A1']
        c2 = notes.MIDI_VALUES['C2']

        available_pitches = note_picker.all_available_pitches(pitches, low_threshold, high_threshold)

        self.assertTrue(c1 in available_pitches)
        self.assertTrue(a1 in available_pitches)
        self.assertTrue(c2 in available_pitches)
        self.assertEqual(len(available_pitches), 3)