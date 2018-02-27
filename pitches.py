import itertools
import re

TEXT_WITH_OCTAVE = re.compile('[A-G]#?[0-9]+')
TEXT_WITHOUT_OCTAVE = re.compile('[A-G]#?')

# Sorry PEP, some rules need to be broken
C_FLAT  = 'Cb'
C       = 'C'
C_SHARP = 'C#'
D_FLAT  = 'Db'
D       = 'D'
D_SHARP = 'D#'
E_FLAT  = 'Eb'
E       = 'E'
E_SHARP = 'E#'
F_FLAT  = 'Fb'
F       = 'F'
F_SHARP = 'F#'
G_FLAT  = 'Gb'
G       = 'G'
G_SHARP = 'G#'
A_FLAT  = 'Ab'
A       = 'A'
A_SHARP = 'A#'
B_FLAT  = 'Bb'
B       = 'B'
B_SHARP = 'B#'

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

PITCH_COEFS = {
    C: 0,
    C_SHARP: 1,
    D_FLAT: 1,
    D: 2,
    D_SHARP: 3,
    E_FLAT: 3,
    E: 4,
    F_FLAT: 4,
    E_SHARP: 5,
    F: 5,
    F_SHARP: 6,
    G_FLAT: 6,
    G: 7,
    G_SHARP: 8,
    A_FLAT: 8,
    A: 9,
    A_SHARP: 10,
    B_FLAT: 10,
    B: 11,
    C_FLAT: 11
}

OCTAVES = {
    C:       range(0, 128)[::12],
    C_SHARP: range(0, 128)[PITCH_COEFS[C_SHARP]::12],
    D_FLAT: range(0, 128)[PITCH_COEFS[D_FLAT]::12],
    D: range(0, 128)[PITCH_COEFS[D]::12],
    D_SHARP: range(0, 128)[PITCH_COEFS[D_SHARP]::12],
    E_FLAT: range(0, 128)[PITCH_COEFS[E_FLAT]::12],
    E: range(0, 128)[PITCH_COEFS[E]::12],
    F_FLAT: range(0, 128)[PITCH_COEFS[F_FLAT]::12],
    E_SHARP: range(0, 128)[PITCH_COEFS[E_SHARP]::12],
    F: range(0, 128)[PITCH_COEFS[F]::12],
    F_SHARP: range(0, 128)[PITCH_COEFS[F_SHARP]::12],
    G_FLAT: range(0, 128)[PITCH_COEFS[G_FLAT]::12],
    G: range(0, 128)[PITCH_COEFS[G]::12],
    G_SHARP: range(0, 128)[PITCH_COEFS[G_SHARP]::12],
    A_FLAT: range(0, 128)[PITCH_COEFS[A_FLAT]::12],
    A: range(0, 128)[PITCH_COEFS[A]::12],
    A_SHARP: range(0, 128)[PITCH_COEFS[A_SHARP]::12],
    B_FLAT: range(0, 128)[PITCH_COEFS[B_FLAT]::12],
    B: range(0, 128)[PITCH_COEFS[B]::12],
    C_FLAT: range(0, 128)[PITCH_COEFS[C_FLAT]::12]
}


def species(value):
    int_value = value
    if isinstance(value, str):
        int_value = midi_value(value)
    elif isinstance(value, Pitch):
        int_value = value.midi()

    for key in MIDI_VALUES:
        remainder = int_value % 12

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
    pitches = \
        species(pitch), \
        species(pitch + 2), \
        species(pitch + 4), \
        species(pitch + 5), \
        species(pitch + 7), \
        species(pitch + 9), \
        species(pitch + 11)

    all_pitches = list(itertools.chain.from_iterable([OCTAVES[p] for p in pitches]))
    all_pitches.sort()

    return all_pitches


def dorian(pitch):
    pitches = \
        species(pitch), \
        species(pitch + 2), \
        species(pitch + 3), \
        species(pitch + 5), \
        species(pitch + 7), \
        species(pitch + 9), \
        species(pitch + 10)

    all_pitches = list(itertools.chain.from_iterable([OCTAVES[p] for p in pitches]))
    all_pitches.sort()

    return all_pitches


def phrygian(pitch):
    pitches = \
        species(pitch), \
        species(pitch + 1), \
        species(pitch + 3), \
        species(pitch + 5), \
        species(pitch + 7), \
        species(pitch + 8), \
        species(pitch + 10)

    all_pitches = list(itertools.chain.from_iterable([OCTAVES[p] for p in pitches]))
    all_pitches.sort()

    return all_pitches


def lydian(pitch):
    pitches = \
        species(pitch), \
        species(pitch + 2), \
        species(pitch + 4), \
        species(pitch + 6), \
        species(pitch + 7), \
        species(pitch + 9), \
        species(pitch + 11)

    all_pitches = list(itertools.chain.from_iterable([OCTAVES[p] for p in pitches]))
    all_pitches.sort()

    return all_pitches


def mixolydian(pitch):
    pitches = \
        species(pitch), \
        species(pitch + 2), \
        species(pitch + 4), \
        species(pitch + 5), \
        species(pitch + 7), \
        species(pitch + 9), \
        species(pitch + 10)

    all_pitches = list(itertools.chain.from_iterable([OCTAVES[p] for p in pitches]))
    all_pitches.sort()

    return all_pitches


def aeolian(pitch):
    pitches = \
        species(pitch), \
        species(pitch + 2), \
        species(pitch + 3), \
        species(pitch + 5), \
        species(pitch + 7), \
        species(pitch + 8), \
        species(pitch + 10)

    all_pitches = list(itertools.chain.from_iterable([OCTAVES[p] for p in pitches]))
    all_pitches.sort()

    return all_pitches


def locrian(pitch):
    pitches = \
        species(pitch), \
        species(pitch + 1), \
        species(pitch + 3), \
        species(pitch + 5), \
        species(pitch + 6), \
        species(pitch + 8), \
        species(pitch + 10)

    all_pitches = list(itertools.chain.from_iterable([OCTAVES[p] for p in pitches]))
    all_pitches.sort()

    return all_pitches


def half_whole(pitch):
    pitches = \
        species(pitch), \
        species(pitch + 1), \
        species(pitch + 3), \
        species(pitch + 4), \
        species(pitch + 6), \
        species(pitch + 7), \
        species(pitch + 8), \
        species(pitch + 9), \
        species(pitch + 11)

    all_pitches = list(itertools.chain.from_iterable([OCTAVES[p] for p in pitches]))
    all_pitches.sort()

    return all_pitches


def whole_half(pitch):
    pitches = \
        species(pitch), \
        species(pitch + 2), \
        species(pitch + 3), \
        species(pitch + 5), \
        species(pitch + 6), \
        species(pitch + 8), \
        species(pitch + 9), \
        species(pitch + 11)

    all_pitches = list(itertools.chain.from_iterable([OCTAVES[p] for p in pitches]))
    all_pitches.sort()

    return all_pitches


def midi_value(string):
    if TEXT_WITH_OCTAVE.match(string):
        value_with_octave = string
    elif TEXT_WITHOUT_OCTAVE.match(string):
        value_with_octave = string + '0'
    else:
        raise ValueError('Invalid string value ' + value + ' submitted')

    pitch_without_octave = ''.join(c for c in value_with_octave if not c.isdigit())
    octave = int(''.join(c for c in value_with_octave if c.isdigit()))
    coef = PITCH_COEFS[[key for key in PITCH_COEFS.keys() if key.lower() == pitch_without_octave.lower()][0]]
    return 12 * octave + coef


def parse(value):
    if isinstance(value, int):
        if 0 <= value <= 127:
            return Pitch(value)
        else:
            raise ValueError('value ' + str(value) + ' is out of midi range')
    elif isinstance(value, str):
        return Pitch(midi_value(value))
    elif isinstance(value, Pitch):
        return value
    else:
        raise TypeError(str(value) + ' is not a valid Pitch, int or string')


class Pitch:

    def __init__(self, value):
        if not isinstance(value, int) or 0 > value > 127:
            raise TypeError('Must submit a valid int between 0 and 128 (inclusive)')

        self._midi_value = value
        self._species = species(self.midi())

    def midi(self):
        return self._midi_value

    def species(self):
        return self._species

    def __eq__(self, other):
        if isinstance(other, int):
            return self.midi() == other
        elif isinstance(other, Pitch):
            return other.midi() == self.midi()

        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '%s' % self._midi_value
