import re
import math
import itertools
from pprint import pformat

TEXT_WITH_OCTAVE = re.compile('[A-G]#?[0-9]+')
TEXT_WITHOUT_OCTAVE = re.compile('[A-G]#?')

C = 'C'
C_SHARP = 'C#'
D = 'D'
D_SHARP = 'D#'
E = 'E'
F = 'F'
F_SHARP = 'F#'
G = 'G'
G_SHARP = 'G#'
A = 'A'
A_SHARP = 'A#'
B = 'B'

MIDI_VALUES = {
    'C0': 0, 'C#0': 1, 'D0': 2, 'D#0': 3, 'E0': 4, 'F0': 5, 'F#0': 6, 'G0': 7, 'G#0': 8, 'A0': 9, 'A#0': 10, 'B0': 11,
    'C1': 12, 'C#1': 13, 'D1': 14, 'D#1': 15, 'E1': 16, 'F1': 17, 'F#1': 18, 'G1': 19, 'G#1': 20, 'A1': 21, 'A#1': 22, 'B1': 23,
    'C2': 24, 'C#2': 25, 'D2': 26, 'D#2': 27, 'E2': 28, 'F2': 29, 'F#2': 30, 'G2': 31, 'G#2': 32, 'A2': 33, 'A#2': 34, 'B2': 35,
    'C3': 36, 'C#3': 37, 'D3': 38, 'D#3': 39, 'E3': 40, 'F3': 41, 'F#3': 42, 'G3': 43, 'G#3': 44, 'A3': 45, 'A#3': 46, 'B3': 47,
    'C4': 48, 'C#4': 49, 'D4': 50, 'D#4': 51, 'E4': 52, 'F4': 53, 'F#4': 54, 'G4': 55, 'G#4': 56, 'A4': 57, 'A#4': 58, 'B4': 59,
    'C5': 60, 'C#5': 61, 'D5': 62, 'D#5': 63, 'E5': 64, 'F5': 65, 'F#5': 66, 'G5': 67, 'G#5': 68, 'A5': 69, 'A#5': 70, 'B5': 71,
    'C6': 72, 'C#6': 73, 'D6': 74, 'D#6': 75, 'E6': 76, 'F6': 77, 'F#6': 78, 'G6': 79, 'G#6': 80, 'A6': 81, 'A#6': 82, 'B6': 83,
    'C7': 84, 'C#7': 85, 'D7': 86, 'D#7': 87, 'E7': 88, 'F7': 89, 'F#7': 90, 'G7': 91, 'G#7': 92, 'A7': 93, 'A#7': 94, 'B7': 95,
    'C8': 96, 'C#8': 97, 'D8': 98, 'D#8': 99, 'E8': 100, 'F8': 101, 'F#8': 102, 'G8': 103, 'G#8': 104, 'A8': 105, 'A#8': 106,'B8': 107,
    'C9': 108, 'C#9': 109, 'D9': 110,'D#9': 111, 'E9': 112, 'F9': 113, 'F#9': 114, 'G9': 115, 'G#9': 116, 'A9': 117, 'A#9': 118,'B9': 119,
    'C10': 120, 'C#10': 121, 'D10': 122, 'D#10': 123, 'E10': 124, 'F10': 125, 'F#10': 126, 'G10': 127
}

OCTAVES = {
    C: [0, 12, 24, 36, 48, 60, 72, 84, 96, 108, 120],
    C_SHARP: [1, 13, 25, 37, 49, 61, 73, 85, 97, 109, 121],
    D: [2, 14, 26, 38, 50, 62, 74, 86, 98, 110, 122],
    D_SHARP: [3, 15, 27, 39, 51, 63, 75, 87, 99, 111, 123],
    E: [4, 16, 28, 40, 52, 64, 76, 88, 100, 112, 124],
    F: [5, 17, 29, 41, 53, 65, 77, 89, 101, 113, 125],
    F_SHARP: [6, 18, 30, 42, 54, 66, 78, 90, 102, 114, 126],
    G: [7, 19, 31, 43, 55, 67, 79, 91, 103, 115, 127],
    G_SHARP: [8, 20, 32, 44, 56, 68, 80, 92,  104, 116],
    A: [9, 21, 33, 45, 57, 69, 81, 93, 105, 117],
    A_SHARP: [10, 22, 34, 46, 58, 70, 82, 94, 106, 118],
    B: [11, 23, 35, 47, 59, 71, 83, 95, 107, 119]
}


def species(value):
    parsed_value = None

    if isinstance(value, Note):
        parsed_value = value.midi()
    elif isinstance(value, int):
        parsed_value = value
    elif isinstance(value, str):
        if TEXT_WITH_OCTAVE.match(value):
            return value[0:len(value) - 1]
        elif TEXT_WITHOUT_OCTAVE.match(value):
            return value
    else:
        raise TypeError('must submit either int, note, or str')

    for key in MIDI_VALUES:
        remainder = parsed_value % 12

        if MIDI_VALUES[key] % 12 == remainder:
            return key[0:len(key) - 2] if '10' in key else key[0:len(key) - 1]


def same_species(value1, value2):
    return species(value1) == species(value2)


def is_perfect_fifth(first, second):
    return abs(second - first) == 7


def is_perfect_fourth(first, second):
    return abs(second - first) == 5


def is_perfect_octave(first, second):
    return abs(second - first) == 12


def is_perfect_interval(first, second):
    return is_perfect_fifth(first, second) or is_perfect_fourth(first, second) or is_perfect_octave(first, second)


def ionian(pitch):
    notes = \
        species(pitch), \
        species(pitch + 2), \
        species(pitch + 4), \
        species(pitch + 5), \
        species(pitch + 7), \
        species(pitch + 9), \
        species(pitch + 11)

    all_pitches = list(itertools.chain.from_iterable([OCTAVES[note] for note in notes]))
    all_pitches.sort()

    return all_pitches


def dorian(pitch):
    notes = \
        species(pitch), \
        species(pitch + 2), \
        species(pitch + 3), \
        species(pitch + 5), \
        species(pitch + 7), \
        species(pitch + 9), \
        species(pitch + 10)

    all_pitches = list(itertools.chain.from_iterable([OCTAVES[note] for note in notes]))
    all_pitches.sort()

    return all_pitches


def phrygian(pitch):
    notes = \
        species(pitch), \
        species(pitch + 1), \
        species(pitch + 3), \
        species(pitch + 5), \
        species(pitch + 7), \
        species(pitch + 8), \
        species(pitch + 10)

    all_pitches = list(itertools.chain.from_iterable([OCTAVES[note] for note in notes]))
    all_pitches.sort()

    return all_pitches


def lydian(pitch):
    notes = \
        species(pitch), \
        species(pitch + 2), \
        species(pitch + 4), \
        species(pitch + 6), \
        species(pitch + 7), \
        species(pitch + 9), \
        species(pitch + 11)

    all_pitches = list(itertools.chain.from_iterable([OCTAVES[note] for note in notes]))
    all_pitches.sort()

    return all_pitches


def mixolydian(pitch):
    notes = \
        species(pitch), \
        species(pitch + 2), \
        species(pitch + 4), \
        species(pitch + 5), \
        species(pitch + 7), \
        species(pitch + 9), \
        species(pitch + 10)

    all_pitches = list(itertools.chain.from_iterable([OCTAVES[note] for note in notes]))
    all_pitches.sort()

    return all_pitches


def aeolian(pitch):
    notes = \
        species(pitch), \
        species(pitch + 2), \
        species(pitch + 3), \
        species(pitch + 5), \
        species(pitch + 7), \
        species(pitch + 8), \
        species(pitch + 10)

    all_pitches = list(itertools.chain.from_iterable([OCTAVES[note] for note in notes]))
    all_pitches.sort()

    return all_pitches


def locrian(pitch):
    notes = \
        species(pitch), \
        species(pitch + 1), \
        species(pitch + 3), \
        species(pitch + 5), \
        species(pitch + 6), \
        species(pitch + 8), \
        species(pitch + 10)

    all_pitches = list(itertools.chain.from_iterable([OCTAVES[note] for note in notes]))
    all_pitches.sort()

    return all_pitches


def half_whole(pitch):
    notes = \
        species(pitch), \
        species(pitch + 1), \
        species(pitch + 3), \
        species(pitch + 4), \
        species(pitch + 6), \
        species(pitch + 7), \
        species(pitch + 8), \
        species(pitch + 9), \
        species(pitch + 11)

    all_pitches = list(itertools.chain.from_iterable([OCTAVES[note] for note in notes]))
    all_pitches.sort()

    return all_pitches


def whole_half(pitch):
    notes = \
        species(pitch), \
        species(pitch + 2), \
        species(pitch + 3), \
        species(pitch + 5), \
        species(pitch + 6), \
        species(pitch + 8), \
        species(pitch + 9), \
        species(pitch + 11)

    all_pitches = list(itertools.chain.from_iterable([OCTAVES[note] for note in notes]))
    all_pitches.sort()

    return all_pitches


class Note:

    def __init__(self, value):
        if isinstance(value, int):
            self.midi_value = value
        elif isinstance(value, str):
            if TEXT_WITH_OCTAVE.match(value):
                self.midi_value = MIDI_VALUES[value]
            elif TEXT_WITHOUT_OCTAVE.match(value):
                self.midi_value = MIDI_VALUES[value + '0']
        else:
            raise TypeError('submit a valid int or string')
            

    def midi(self):
        return self.midi_value

    def species(self):
        return species(self.midi())

    def is_empty(self):
        return self.midi_value == -1

    def __repr__(self):
        return '\n%s' % self.midi_value