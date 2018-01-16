from domain import *
import chords
import notes
import parts
import math
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
            return Note(first_at_or_below(chord.root, parts.BASS.middle))

        return self.bass[index].note

    def pick_alto(self, index):
        soprano_threshold = self.__last_soprano_pitch(index) - 2
        unused = self.__unused_notes(index)

        all_available_octaves = all_available_pitches \
            (unused, parts.ALTO.max_low, min(soprano_threshold, parts.ALTO.max_high))
        available = [x for x in all_available_octaves if x < soprano_threshold]
        available.sort(reverse=True)

        if index >= RESOLUTION:
            last_beat = self.__used_notes(index - RESOLUTION)

            for pitch in available:
                self.alto[index] = Sample(pitch, Sample.TYPE_START)

                if contains_parallel_movement(last_beat, self.__used_notes(index)):
                    self.alto[index] = Sample(-1, None)
                else:
                    self.alto[index] = Sample(-1, None)
                    return Note(pitch)

        if not available:
            # handle me better
            return self.alto[index].note
        else:
            return Note(available[0])

    def pick_tenor(self, index):
        bass_threshold = self.bass[index].note.midi() + 3

        unused = self.__unused_notes(index)
        if not unused:
            unused = self.chord_progression[index].all()

        available_octaves = all_available_pitches \
            (unused, max(bass_threshold, parts.TENOR.max_low), parts.TENOR.max_high)
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
            return self.tenor[index].note
        else:
            # now we have all of the notes that wouldn't cause parallel motion, are within the available range
            # of the instrument, and above bass threshold
            mean_bass_alto = (self.bass[index].note.midi() + self.alto[index].note.midi()) / 2
            # print mean_bass_alto
            midi_val = min(available_without_parallel_motion, key=lambda note: abs(note - mean_bass_alto))

            return Note(midi_val)

    def __used_notes(self, index):
        return [self.soprano[index].note, self.alto[index].note, self.tenor[index].note, self.bass[index].note]

    def __unused_notes(self, index):
        used_notes = self.__used_notes(index)

        chord = self.chord_progression[index]

        unused_notes = []
        for chord_note in chord.all():
            contains = False
            for used_note in used_notes:
                if chord_note.species() == used_note.species():
                    contains = True
            if not contains:
                unused_notes.append(chord_note)

        return unused_notes

    def __last_soprano_pitch(self, position):
        for i in reversed(range(0, position + 1)):
            sample = self.soprano[i]

            if sample.note.midi() > -1:
                return sample.note.midi()

        return 1000


def contains_parallel_movement(first_set, second_set):
    for i in range(0, len(first_set)):
        first = first_set[i]

        for j in range(0, len(first_set)):
            second = first_set[j]

            if first.midi() == second.midi():
                continue

            if notes.is_perfect_interval(first.midi(), second.midi()):
                first_interval = abs(first.midi() - second.midi())
                second_interval = abs(second_set[i].midi() - second_set[j].midi())
                if first_interval == second_interval and first.midi() - second_set[i].midi() != 0:
                    return True

    return False


def first_at_or_below(note, threshold):
    text = note.species()
    octaves = notes.OCTAVES[text]

    last_pitch = octaves[0]
    for pitch in octaves:
        if pitch > threshold:
            return last_pitch
        last_pitch = pitch


def all_available_pitches(note_list, low_threshold, high_threshold):
    available = []

    for note in note_list:
        octaves = notes.OCTAVES[note.species()]
        for octave in octaves:
            if low_threshold <= octave <= high_threshold:
                available.append(octave)

    return available
