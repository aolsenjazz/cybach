import notes
import re
import collections

RE_MAJOR = re.compile('[A-G]')
RE_MINOR = re.compile('[A-G]-')
RE_SEVEN = re.compile('[A-G]7')
RE_DIMIN = re.compile('[A-G]dim')


class Chord:

    def __init__(self, root):
        note = -1

        if isinstance(root, notes.Note):
            note = root
        elif isinstance(root, int):
            note = notes.Note(root)
        elif isinstance(root, str):
            note = notes.Note(root)

        self.root = note

    def __repr__(self):
        return str(self.root)

    def __contains__(self, note):
        parsed = None

        if isinstance(note, notes.Note):
            parsed = note
        elif isinstance(note, int):
            parsed = notes.Note(note)

        if parsed.species() == self.root.species():
            return True
        if parsed.species() == self.third.species():
            return True
        if parsed.species() == self.fifth.species():
            return True
        return False

    def note_above(self, note):
        """
        Basically just a wrapper for the private method to make up for improper API usage

        :param note: midi value, text value, or Note object
        :return:
        """
        if isinstance(note, notes.Note):
            return self.__note_above(note.midi())
        elif isinstance(note, int):
            return self.__note_above(note)
        elif isinstance(note, str):
            return self.__note_above(notes.Note(note).midi())

    def __note_above(self, pitch):
        """
        Returns the next highest note in the chord (e.g. submitted G to a C7 chord would return Bb above)

        :param pitch: midi value pitch
        :return: a midi value higher than the submitted pitch
        """
        all_octaves = self.__all_octaves()
        for p in all_octaves:
            if p > pitch:
                return p

        raise ValueError('midi value %d appears to be invalid' % pitch)

    def scale(self):
        """
        Returns all of the pitches in this chord's chord scale. Minor chords return aeolian mode.
        """
        raise NotImplementedError

    def indicates_dominant(self, *pitches):
        """
        Returns whether the pitches submitted indicate a dominant relationship to this chord

        :param pitches: array of pitches
        """
        raise NotImplementedError

    def indicates_subdominant(self, *pitches):
        """
        Returns whether the pitches submitted indicate a subdominant relationship to this chord

        :param pitches: array of pitches
        """
        raise NotImplementedError


class MajorChord(Chord):

    def __init__(self, root_note):
        Chord.__init__(self, root_note)
        self.third = notes.Note(self.root.midi() + 4)
        self.fifth = notes.Note(self.root.midi() + 7)

    def _Chord__all_octaves(self):
        all_roots = notes.OCTAVES[self.root.species()]
        all_thirds = notes.OCTAVES[self.third.species()]
        all_fifths = notes.OCTAVES[self.fifth.species()]

        all = []
        all.extend(all_roots)
        all.extend(all_thirds)
        all.extend(all_fifths)
        all.sort()

        return all

    def __repr__(self):
        return str(self.root) + ', ' + str(self.third) + ', ' + str(self.fifth)

    def all(self):
        return self.root, self.third, self.fifth

    def scale(self):
        return notes.ionian(self.root.midi())

    def indicates_dominant(self, *pitches):
        root_pitch = self.root.midi()

        black_list = (root_pitch % 12, (root_pitch + 6) % 12, (root_pitch + 10) % 12)
        major_indicators = (root_pitch + 11) % 12, (root_pitch + 7) % 12
        minor_indicators = (root_pitch + 2) % 12, (root_pitch + 5) % 12

        return len([p for p in pitches if (p % 12) in black_list]) == 0 \
            and len([p for p in pitches if (p % 12) in major_indicators]) == 1 \
            and len([p for p in pitches if (p % 12) in minor_indicators]) >= 1

    def indicates_subdominant(self, *pitches):
        root_pitch = self.root.midi()

        black_list = ((root_pitch + 4) % 12, (root_pitch + 11) % 12)
        indicators = ((root_pitch + 2) % 12, (root_pitch + 5) % 12, (root_pitch + 9) % 12)

        return len([p for p in pitches if (p % 12) in black_list]) == 0 \
               and len([p for p in pitches if (p % 12) in indicators]) >= 2


class MinorChord(Chord):

    def __init__(self, root_note):
        Chord.__init__(self, root_note)
        self.third = notes.Note(self.root.midi() + 3)
        self.fifth = notes.Note(self.root.midi() + 7)

    def _Chord__all_octaves(self):
        all_roots = notes.OCTAVES[self.root.species()]
        all_thirds = notes.OCTAVES[self.third.species()]
        all_fifths = notes.OCTAVES[self.fifth.species()]

        all = []
        all.extend(all_roots)
        all.extend(all_thirds)
        all.extend(all_fifths)
        all.sort()

        return all

    def all(self):
        return self.root, self.third, self.fifth

    def __repr__(self):
        return str(self.root) + ', ' + str(self.third) + ', ' + str(self.fifth)

    def scale(self):
        return notes.aeolian(self.root.midi())

    def indicates_dominant(self, *pitches):
        root_pitch = self.root.midi()

        black_list = (root_pitch % 12, (root_pitch + 10) % 12)
        major_indicators = ((root_pitch + 11) % 12,)
        minor_indicators = ((root_pitch + 2) % 12, (root_pitch + 5) % 12, (root_pitch + 7) % 12, (root_pitch + 8) % 12)

        return len([p for p in pitches if (p % 12) in black_list]) == 0 \
            and len([p for p in pitches if (p % 12) in major_indicators]) == 1 \
            and len([p for p in pitches if (p % 12) in minor_indicators]) >= 1

    def indicates_subdominant(self, *pitches):
        root_pitch = self.root.midi()

        black_list = ((root_pitch + 10) % 12, (root_pitch + 11) % 12)
        indicators = ((root_pitch + 2) % 12, (root_pitch + 5) % 12, (root_pitch + 8) % 12)

        return len([p for p in pitches if (p % 12) in black_list]) == 0 \
               and len([p for p in pitches if (p % 12) in indicators]) >= 2


class SevenChord(MajorChord):

    def __init__(self, root_note):
        Chord.__init__(self, root_note)
        self.third = notes.Note(self.root.midi() + 4)
        self.fifth = notes.Note(self.root.midi() + 7)
        self.seventh = notes.Note(self.root.midi() + 10)

    def __contains__(self, note):
        parsed = None

        if isinstance(note, notes.Note):
            parsed = note
        elif isinstance(note, int):
            parsed = notes.Note(note)

        if parsed.species() == self.seventh.species():
            return True
        return Chord.__contains__(self, parsed)

    def all(self):
        return self.root, self.third, self.fifth, self.seventh

    def __note_above(self, pitch):
        if pitch == self.fifth:
            return self.seventh.species

        if pitch == self.seventh.species:
            return self.root

        return Chord.__note_above(self, pitch)

    def _Chord__all_octaves(self):
        all_roots = notes.OCTAVES[self.root.species()]
        all_thirds = notes.OCTAVES[self.third.species()]
        all_fifths = notes.OCTAVES[self.fifth.species()]
        all_sevenths = notes.OCTAVES[self.seventh.species()]

        all = []
        all.extend(all_roots)
        all.extend(all_thirds)
        all.extend(all_fifths)
        all.extend(all_sevenths)
        all.sort()
        return all

    def __repr__(self):
        return str(self.root) + ', ' + str(self.third) + ', ' + str(self.fifth) + ', ' + str(self.seventh)

    def scale(self):
        return notes.mixolydian(self.root.midi())


class DiminishedChord(MinorChord):

    def __init__(self, root_note):
        Chord.__init__(self, root_note)
        self.third = notes.Note(self.root.midi() + 3)
        self.fifth = notes.Note(self.root.midi() + 6)
        self.seventh = notes.Note(self.root.midi() + 9)

    def __contains__(self, note):
        parsed = None

        if isinstance(note, notes.Note):
            parsed = note
        elif isinstance(note, int):
            parsed = notes.Note(note)

        if parsed.species() == self.seventh.species():
            return True
        return Chord.__contains__(self, parsed)

    def all(self):
        return self.root, self.third, self.fifth

    def __note_above(self, pitch):
        if pitch == self.fifth:
            return self.seventh.species

        if pitch == self.seventh.species:
            return self.root

        return Chord.__note_above(self, pitch)

    def _Chord__all_octaves(self):
        all_roots = notes.OCTAVES[self.root.species()]
        all_thirds = notes.OCTAVES[self.third.species()]
        all_fifths = notes.OCTAVES[self.fifth.species()]
        all_sevenths = notes.OCTAVES[self.seventh.species()]

        all = []
        all.extend(all_roots)
        all.extend(all_thirds)
        all.extend(all_fifths)
        all.extend(all_sevenths)
        all.sort()

        return all

    def __repr__(self):
        return str(self.root) + ', ' + str(self.third) + ', ' + str(self.fifth) + ', ' + str(self.seventh)

    def scale(self):
        return notes.half_whole(self.root.midi())

    def indicates_subdominant(self, *pitches):
        return False


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
            string += '\n' + str(key) + ': ' + (self.store[key].root.species()) + \
                      self.store[key].third.species() + \
                      self.store[key].fifth.species()

        return string


def parse(chord):
    parsed = chord[0:1].upper() + chord[1:]
    return CHORDS.get(parsed, None)


def same(chord1, chord2):
    return chord1.root.midi_value % 12 == chord2.root.midi_value % 12


CHORDS = {
    'C': MajorChord(notes.Note(notes.C)),
    'C-': MinorChord(notes.Note(notes.C)),
    'C7': SevenChord(notes.Note(notes.C)),
    'Cdim': DiminishedChord(notes.Note(notes.C)),
    'C#': MajorChord(notes.Note(notes.C_SHARP)),
    'C#-': MinorChord(notes.Note(notes.C_SHARP)),
    'C#7': SevenChord(notes.Note(notes.C_SHARP)),
    'C#dim': DiminishedChord(notes.Note(notes.C_SHARP)),
    'Db': MajorChord(notes.Note(notes.C_SHARP)),
    'Db-': MinorChord(notes.Note(notes.C_SHARP)),
    'Db7': SevenChord(notes.Note(notes.C_SHARP)),
    'Dbdim': DiminishedChord(notes.Note(notes.C_SHARP)),
    'D': MajorChord(notes.Note(notes.D)),
    'D-': MinorChord(notes.Note(notes.D)),
    'D7': SevenChord(notes.Note(notes.D)),
    'Ddim': DiminishedChord(notes.Note(notes.D)),
    'D#': MajorChord(notes.Note(notes.D_SHARP)),
    'D#-': MinorChord(notes.Note(notes.D_SHARP)),
    'D#7': SevenChord(notes.Note(notes.D_SHARP)),
    'D#dim': DiminishedChord(notes.Note(notes.D_SHARP)),
    'Eb': MajorChord(notes.Note(notes.D_SHARP)),
    'Eb-': MinorChord(notes.Note(notes.D_SHARP)),
    'Eb7': SevenChord(notes.Note(notes.D_SHARP)),
    'Ebdim': DiminishedChord(notes.Note(notes.D_SHARP)),
    'E': MajorChord(notes.Note(notes.E)),
    'E-': MinorChord(notes.Note(notes.E)),
    'E7': SevenChord(notes.Note(notes.E)),
    'Edim': DiminishedChord(notes.Note(notes.E)),
    'F': MajorChord(notes.Note(notes.F)),
    'F-': MinorChord(notes.Note(notes.F)),
    'F7': SevenChord(notes.Note(notes.F)),
    'Fdim': DiminishedChord(notes.Note(notes.F)),
    'F#': MajorChord(notes.Note(notes.F_SHARP)),
    'F#-': MinorChord(notes.Note(notes.F_SHARP)),
    'F#7': SevenChord(notes.Note(notes.F_SHARP)),
    'F#dim': DiminishedChord(notes.Note(notes.F_SHARP)),
    'Gb': MajorChord(notes.Note(notes.F_SHARP)),
    'Gb-': MinorChord(notes.Note(notes.F_SHARP)),
    'Gb7': SevenChord(notes.Note(notes.F_SHARP)),
    'Gbdim': DiminishedChord(notes.Note(notes.F_SHARP)),
    'G': MajorChord(notes.Note(notes.G)),
    'G-': MinorChord(notes.Note(notes.G)),
    'G7': SevenChord(notes.Note(notes.G)),
    'Gdim': DiminishedChord(notes.Note(notes.G)),
    'G#': MajorChord(notes.Note(notes.G_SHARP)),
    'G#-': MinorChord(notes.Note(notes.G_SHARP)),
    'G#7': SevenChord(notes.Note(notes.G_SHARP)),
    'G#dim': DiminishedChord(notes.Note(notes.G_SHARP)),
    'Ab': MajorChord(notes.Note(notes.G_SHARP)),
    'Ab-': MinorChord(notes.Note(notes.G_SHARP)),
    'Ab7': SevenChord(notes.Note(notes.G_SHARP)),
    'Abdim': DiminishedChord(notes.Note(notes.G_SHARP)),
    'A': MajorChord(notes.Note(notes.A)),
    'A-': MinorChord(notes.Note(notes.A)),
    'A7': SevenChord(notes.Note(notes.A)),
    'Adim': DiminishedChord(notes.Note(notes.A)),
    'A#': MajorChord(notes.Note(notes.A_SHARP)),
    'A#-': MinorChord(notes.Note(notes.A_SHARP)),
    'A#7': SevenChord(notes.Note(notes.A_SHARP)),
    'A#dim': DiminishedChord(notes.Note(notes.A_SHARP)),
    'Bb': MajorChord(notes.Note(notes.A_SHARP)),
    'Bb-': MinorChord(notes.Note(notes.A_SHARP)),
    'Bb7': SevenChord(notes.Note(notes.A_SHARP)),
    'Bbdim': DiminishedChord(notes.Note(notes.A_SHARP)),
    'B': MajorChord(notes.Note(notes.B)),
    'B-': MinorChord(notes.Note(notes.B)),
    'B7': SevenChord(notes.Note(notes.B)),
    'Bdim': DiminishedChord(notes.Note(notes.B)),
}