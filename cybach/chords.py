import notes
import re
import collections

RE_MAJOR = re.compile('[A-G]')
RE_MINOR = re.compile('[A-G]-')
RE_SEVEN = re.compile('[A-G]7')
RE_DIMIN = re.compile('[A-G]dim')


class Chord:

    def __init__(self, root):
        self.root = root

    def __repr__(self):
        return str(self.root)

    def __contains__(self, note):
        if note.as_text_without_octave() == self.root.as_text_without_octave():
            return True
        if note.as_text_without_octave() == self.third.as_text_without_octave():
            return True
        if note.as_text_without_octave() == self.fifth.as_text_without_octave():
            return True
        return False


class MajorChord(Chord):

    def __init__(self, root_note):
        Chord.__init__(self, root_note)
        self.third = notes.Note(self.root.as_midi_value() + 4)
        self.fifth = notes.Note(self.root.as_midi_value() + 7)

    def all(self):
        return self.root, self.third, self.fifth


class MinorChord(Chord):

    def __init__(self, root_note):
        Chord.__init__(self, root_note)
        self.third = notes.Note(self.root.as_midi_value() + 3)
        self.fifth = notes.Note(self.root.as_midi_value() + 7)

    def all(self):
        return self.root, self.third, self.fifth

class SevenChord(Chord):

    def __init__(self, root_note):
        Chord.__init__(self, root_note)
        self.third = notes.Note(self.root.as_midi_value() + 4)
        self.fifth = notes.Note(self.root.as_midi_value() + 7)
        self.seventh = notes.Note(self.root.as_midi_value() + 10)

    def __contains__(self, note):
        if note.as_text_without_octave() == self.seventh.as_text_without_octave():
            return True
        return Chord.__contains__(self, note)

    def all(self):
        return self.root, self.third, self.fifth, self.seventh


class DiminishedChord(Chord):

    def __init__(self, root_note):
        Chord.__init__(self, root_note)
        self.third = notes.Note(self.root.as_midi_value() + 3)
        self.fifth = notes.Note(self.root.as_midi_value() + 6)
        self.seventh = notes.Note(self.root.as_midi_value() + 9)

    def __contains__(self, note):
        if note.as_text_without_octave() == self.seventh.as_text_without_octave():
            return True
        return Chord.__contains__(self, note)

    def all(self):
        return self.root, self.third, self.fifth


class ChordProgression(collections.MutableMapping):

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))

    def __getitemhardway(self, index):
        active_key = 0
        for k in self.store:
            if index >= k >= active_key:
                active_key = k
        return self.store[active_key]

    def __getitem__(self, key):
        return self.store.get(key, self.__getitemhardway(key))

    def __setitem__(self, key, value):
        self.store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        del self.store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        return key

    def __repr__(self):
        string = ''
        for key in self.store:
            string += '\n' + str(key) + ': ' + (self.store[key].root.as_text_without_octave()) + \
                self.store[key].third.as_text_without_octave() + \
                self.store[key].fifth.as_text_without_octave()

        return string


def parse(chord):
    parsed = chord[0:1].upper() + chord[1:]
    return CHORDS.get(parsed, None)


CHORDS = {
    'C': MajorChord(notes.Note(text_value=notes.C)),
    'C-': MinorChord(notes.Note(text_value=notes.C)),
    'C7': SevenChord(notes.Note(text_value=notes.C)),
    'Cdim': DiminishedChord(notes.Note(text_value=notes.C)),
    'C#': MajorChord(notes.Note(text_value=notes.C_SHARP)),
    'C#-': MinorChord(notes.Note(text_value=notes.C_SHARP)),
    'C#7': SevenChord(notes.Note(text_value=notes.C_SHARP)),
    'C#dim': DiminishedChord(notes.Note(text_value=notes.C_SHARP)),
    'D': MajorChord(notes.Note(text_value=notes.D)),
    'D-': MinorChord(notes.Note(text_value=notes.D)),
    'D7': SevenChord(notes.Note(text_value=notes.D)),
    'Ddim': DiminishedChord(notes.Note(text_value=notes.D)),
    'D#': MajorChord(notes.Note(text_value=notes.D_SHARP)),
    'D#-': MinorChord(notes.Note(text_value=notes.D_SHARP)),
    'D#7': SevenChord(notes.Note(text_value=notes.D_SHARP)),
    'D#dim': DiminishedChord(notes.Note(text_value=notes.D_SHARP)),
    'E': MajorChord(notes.Note(text_value=notes.E)),
    'E-': MinorChord(notes.Note(text_value=notes.E)),
    'E7': SevenChord(notes.Note(text_value=notes.E)),
    'Edim': DiminishedChord(notes.Note(text_value=notes.E)),
    'F': MajorChord(notes.Note(text_value=notes.F)),
    'F-': MinorChord(notes.Note(text_value=notes.F)),
    'F7': SevenChord(notes.Note(text_value=notes.F)),
    'Fdim': DiminishedChord(notes.Note(text_value=notes.F)),
    'F#': MajorChord(notes.Note(text_value=notes.F_SHARP)),
    'F#-': MinorChord(notes.Note(text_value=notes.F_SHARP)),
    'F#7': SevenChord(notes.Note(text_value=notes.F_SHARP)),
    'F#dim': DiminishedChord(notes.Note(text_value=notes.F_SHARP)),
    'G': MajorChord(notes.Note(text_value=notes.G)),
    'G-': MinorChord(notes.Note(text_value=notes.G)),
    'G7': SevenChord(notes.Note(text_value=notes.G)),
    'Gdim': DiminishedChord(notes.Note(text_value=notes.G)),
    'G#': MajorChord(notes.Note(text_value=notes.G_SHARP)),
    'G#-': MinorChord(notes.Note(text_value=notes.G_SHARP)),
    'G#7': SevenChord(notes.Note(text_value=notes.G_SHARP)),
    'G#dim': DiminishedChord(notes.Note(text_value=notes.G_SHARP)),
    'A': MajorChord(notes.Note(text_value=notes.A)),
    'A-': MinorChord(notes.Note(text_value=notes.A)),
    'A7': SevenChord(notes.Note(text_value=notes.A)),
    'Adim': DiminishedChord(notes.Note(text_value=notes.A)),
    'A#': MajorChord(notes.Note(text_value=notes.A_SHARP)),
    'A#-': MinorChord(notes.Note(text_value=notes.A_SHARP)),
    'A#7': SevenChord(notes.Note(text_value=notes.A_SHARP)),
    'A#dim': DiminishedChord(notes.Note(text_value=notes.A_SHARP)),
    'B': MajorChord(notes.Note(text_value=notes.B)),
    'B-': MinorChord(notes.Note(text_value=notes.B)),
    'B7': SevenChord(notes.Note(text_value=notes.B)),
    'Bdim': DiminishedChord(notes.Note(text_value=notes.B)),
}