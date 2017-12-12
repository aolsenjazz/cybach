# Note picker that involves the use of instruments

from domain import *
import chords
import notes
from constants import *


class NotePicker:
    def __init__(self, soprano, alto, tenor, bass, key_signatures, chord_progression):
        self.soprano = soprano
        self.alto = alto
        self.tenor = tenor
        self.bass = bass
        self.key_signatures = key_signatures
        self.chord_progression = chord_progression

    def pick_bass(self, index):
        if self.bass[index].is_empty():
            chord = self.chord_progression[index]
            return Sample(self.bass.instrument.first_at_or_below_middle(chord.root), Sample.TYPE_START)

        return self.bass[index]

    def pick_alto(self, index):
        soprano_threshold = self.soprano[index].note.midi_value - 2

        unused = self.__unused_notes(index)
        all_available_octaves = self.alto.instrument.all_available_octaves(unused)
        available = [x for x in all_available_octaves if x < soprano_threshold]
        available.sort(reverse=True)
        print available

        if index >= RESOLUTION:
            last_beat = self.__used_notes(index - RESOLUTION)

            for pitch in available:
                self.alto[index] = Sample(pitch, Sample.TYPE_START)

                if contains_parallel_movement(last_beat, self.__used_notes(index)):
                    self.alto[index] = Sample(-1, None)
                else:
                    self.alto[index] = Sample(-1, None)
                    return Sample(pitch, Sample.TYPE_START)

        if not available:
            # handle me better
            return self.alto[index]
        else:
            return Sample(available[0], Sample.TYPE_START)

    def pick_tenor(self, index):
        if not self.tenor[index].note.is_empty():
            return self.tenor[index]

        bass_threshold = self.bass[index].note.midi_value + 3

        unused = self.__unused_notes(index)
        if not unused:
            unused = self.chord_progression[index].all()

        available_octaves = self.tenor.instrument.all_available_octaves(unused)
        available_above_threshold = [x for x in available_octaves if x > bass_threshold]
        available_without_parallel_motion = []

        if index >= RESOLUTION:
            last_beat = self.__used_notes(index - RESOLUTION)

            for pitch in available_above_threshold:
                self.tenor[index] = Sample(pitch, Sample.TYPE_START)

                if contains_parallel_movement(last_beat, self.__used_notes(index)):
                    self.tenor[index] = Sample(-1, None)
                else:
                    available_without_parallel_motion.append(pitch)
                    self.tenor[index] = Sample(-1, None)
        else:
            available_without_parallel_motion.extend(available_above_threshold)

        if not available_without_parallel_motion:
            # handle me better
            return self.tenor[index]
        else:
            # now we have all of the notes that wouldn't cause parallel motion, are within the available range
            # of the instrument, and above bass threshold
            mean_bass_alto = (self.bass[index].note.midi_value + self.alto[index].note.midi_value) / 2
            midi_val = min(available_without_parallel_motion, key=lambda note: abs(note - mean_bass_alto))
            return Sample(midi_val, Sample.TYPE_START)

    def __used_notes(self, index):
        return [self.soprano[index].note, self.alto[index].note, self.tenor[index].note, self.bass[index].note]

    def __unused_notes(self, index):
        used_notes = self.__used_notes(index)

        chord = self.chord_progression[index]

        unused_notes = []
        for chord_note in chord.all():
            contains = False
            for used_note in used_notes:
                if chord_note.as_text_without_octave() == used_note.as_text_without_octave():
                    contains = True
            if not contains:
                unused_notes.append(chord_note)

        return unused_notes


def contains_parallel_movement(first_set, second_set):
    for i in range(0, len(first_set)):
        first = first_set[i]

        for j in range(0, len(first_set)):
            second = first_set[j]

            if first.midi_value == second.midi_value:
                continue

            if notes.is_perfect_interval(first.midi_value, second.midi_value):
                first_interval = abs(first.midi_value - second.midi_value)
                second_interval = abs(second_set[i].midi_value - second_set[j].midi_value)
                if first_interval != 0 and first_interval == second_interval:
                    return True

    return False
