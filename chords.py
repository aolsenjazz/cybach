import notes
import re
import config
import collections
import itertools
from rhythm import time

RE_MAJOR = re.compile('^[A-Ga-g]([Bb]|#)?(maj)?$')
RE_MINOR = re.compile('^[A-Ga-g]([Bb]|#)?(-|m(in)?)?$')
RE_SEVEN = re.compile('^[A-Ga-g]([Bb]|#)?7?$')
RE_DIMIN = re.compile('^[A-Ga-g]([Bb]|#)?dim$')
RE_SLASH = re.compile('^[A-Ga-g]([Bb]|#)?(7|-|m(in)?|dim|maj)?/[A-Ga-g]([Bb]|#)?$')

RE_CHORD_ROOT = re.compile('[A-Ga-g]([Bb]|#)?')


class Chord:

    def __init__(self, root, bass_note=None):
        self._root = notes.parse(root)

        if bass_note is None:
            self.bass_note = self._root
        else:
            self.bass_note = notes.parse(bass_note)

    def __repr__(self):
        return self.string()

    def __contains__(self, note):
        parsed = None

        if isinstance(note, notes.Note):
            parsed = note
        elif isinstance(note, int):
            parsed = notes.parse(note)

        if parsed.species() == self._root.species():
            return True
        if parsed.species() == self.three().species():
            return True
        if parsed.species() == self.five().species():
            return True
        return False

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return notes.same_species(other.bass_note, self.bass_note) and notes.same_species(other._root, self._root)

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return False

        return not (notes.same_species(other.bass_note, self.bass_note) and notes.same_species(other.one, self._root))

    def __hash__(self):
        return hash((self.bass_note, self._root))

    def root_in_bass(self):
        return notes.same_species(self._root, self.bass_note)

    def string(self):
        raise NotImplementedError

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
            return self.__note_above(notes.parse(note).midi())

    def __note_above(self, pitch):
        """
        Returns the next highest note in the chord (e.g. submitted G to a C7 chord would return Bb above)

        :param pitch: midi value pitch
        :return: a midi value higher than the submitted pitch
        """
        all_octaves = self.all_octaves()
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

    def all_degrees(self):
        return self.root(), self.three(), self.five()

    def root(self):
        return self._root

    def three(self):
        raise NotImplementedError

    def five(self):
        raise NotImplementedError

    def indicates_subdominant(self, *pitches):
        """
        Returns whether the pitches submitted indicate a subdominant relationship to this chord

        :param pitches: array of pitches
        """
        raise NotImplementedError

    def all_octaves(self):
        all_notes = list(itertools.chain(*[notes.OCTAVES[note.species()] for note in self.all_degrees()]))
        all_notes.sort()
        return all_notes


class MajorChord(Chord):

    def __init__(self, root_note, bass_note=None):
        Chord.__init__(self, root_note, bass_note)
        self.__three = notes.parse(self._root.midi() + 4)
        self.__five = notes.parse(self._root.midi() + 7)

    def three(self):
        return self.__three

    def five(self):
        return self.__five

    def scale(self):
        return notes.ionian(self._root.midi())

    def string(self):
        return notes.species(self._root)

    def indicates_dominant(self, *pitches):
        root_pitch = self._root.midi()

        black_list = (root_pitch % 12, (root_pitch + 6) % 12, (root_pitch + 10) % 12)
        major_indicators = (root_pitch + 11) % 12, (root_pitch + 7) % 12
        minor_indicators = (root_pitch + 2) % 12, (root_pitch + 5) % 12

        return len([p for p in pitches if (p % 12) in black_list]) == 0 \
            and len([p for p in pitches if (p % 12) in major_indicators]) == 1 \
            and len([p for p in pitches if (p % 12) in minor_indicators]) >= 1

    def indicates_subdominant(self, *pitches):
        root_pitch = self._root.midi()

        black_list = ((root_pitch + 4) % 12, (root_pitch + 11) % 12)
        indicators = ((root_pitch + 2) % 12, (root_pitch + 5) % 12, (root_pitch + 9) % 12)

        return len([p for p in pitches if (p % 12) in black_list]) == 0 \
               and len([p for p in pitches if (p % 12) in indicators]) >= 2


class MinorChord(Chord):

    def __init__(self, root_note, bass_note=None):
        Chord.__init__(self, root_note, bass_note)
        self.__three = notes.parse(self._root.midi() + 3)
        self.__five = notes.parse(self._root.midi() + 7)

    def three(self):
        return self.__three

    def five(self):
        return self.__five

    def string(self):
        return notes.species(self._root) + '-'

    def scale(self):
        return notes.aeolian(self._root.midi())

    def indicates_dominant(self, *pitches):
        root_pitch = self._root.midi()

        black_list = (root_pitch % 12, (root_pitch + 10) % 12)
        major_indicators = ((root_pitch + 11) % 12,)
        minor_indicators = ((root_pitch + 2) % 12, (root_pitch + 5) % 12, (root_pitch + 7) % 12, (root_pitch + 8) % 12)

        return len([p for p in pitches if (p % 12) in black_list]) == 0 \
            and len([p for p in pitches if (p % 12) in major_indicators]) == 1 \
            and len([p for p in pitches if (p % 12) in minor_indicators]) >= 1

    def indicates_subdominant(self, *pitches):
        root_pitch = self._root.midi()

        black_list = ((root_pitch + 10) % 12, (root_pitch + 11) % 12)
        indicators = ((root_pitch + 2) % 12, (root_pitch + 5) % 12, (root_pitch + 8) % 12)

        return len([p for p in pitches if (p % 12) in black_list]) == 0 \
               and len([p for p in pitches if (p % 12) in indicators]) >= 2


class SevenChord(MajorChord):

    def __init__(self, root_note, bass_note=None):
        Chord.__init__(self, root_note, bass_note)
        self.__three = notes.parse(self._root.midi() + 4)
        self.__five = notes.parse(self._root.midi() + 7)
        self.__seven = notes.parse(self._root.midi() + 10)

    def __contains__(self, note):
        parsed = None

        if isinstance(note, notes.Note):
            parsed = note
        elif isinstance(note, int):
            parsed = notes.parse(note)

        if parsed.species() == self.__seven.species():
            return True
        return Chord.__contains__(self, parsed)

    def three(self):
        return self.__three

    def five(self):
        return self.__five

    def string(self):
        return notes.species(self._root) + '7'

    def all_degrees(self):
        most = Chord.all_degrees(self)
        all = list(most)
        all.append(self.__seven)
        return all

    def __note_above(self, pitch):
        if pitch == self.__five:
            return self.__seven.species

        if pitch == self.__seven.species:
            return self._root

        return Chord.__note_above(self, pitch)

    def scale(self):
        return notes.mixolydian(self._root.midi())


class DiminishedChord(MinorChord):

    def __init__(self, root_note, bass_note=None):
        Chord.__init__(self, root_note, bass_note)
        self.__three = notes.parse(self._root.midi() + 3)
        self.__five = notes.parse(self._root.midi() + 6)
        self.__seven = notes.parse(self._root.midi() + 9)

    def __contains__(self, note):
        parsed = None

        if isinstance(note, notes.Note):
            parsed = note
        elif isinstance(note, int):
            parsed = notes.parse(note)

        if parsed.species() == self.__seven.species():
            return True
        return Chord.__contains__(self, parsed)

    def three(self):
        return self.__three

    def five(self):
        return self.__five

    def string(self):
        return notes.species(self._root) + 'dim'

    def all_degrees(self):
        return Chord.all_degrees(self) + self.__seven

    def all_octaves(self):
        all_of_em = Chord.all_octaves(self) + notes.OCTAVES[self.__seven.species()]
        all_of_em.sort()
        return all_of_em

    def __note_above(self, pitch):
        if pitch == self.__five:
            return self.__seven.species

        if pitch == self.__seven.species:
            return self._root

        return Chord.__note_above(self, pitch)

    def scale(self):
        return notes.half_whole(self._root.midi())

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
            string += '\n' + str(key) + ': ' + (self.store[key].one.species()) + \
                      self.store[key].three.species() + \
                      self.store[key].five.species()

        return string

    def set(self):
        return ChordProgressionSetter(self)

    def chords(self, measure):
        return {key: self[key] for key in self.keys() if measure.start() <= key < measure.end()}


class ChordProgressionSetter:

    def __init__(self, chord_progression):
        self.chord_progression = chord_progression
        self._measure = 0
        self._beat = 0

    def measure(self, measure):
        self._measure = measure
        return self

    def beat(self, beat):
        self._beat = beat
        return self

    def commit(self, chord):
        if isinstance(chord, str):
            parsed = parse(chord)
        elif isinstance(chord, Chord):
            parsed = chord
        else:
            raise TypeError

        sample_pos = time.measure(self._measure).beat(self._beat).start()
        self.chord_progression[sample_pos] = parsed


def parse(chord, bass_note=None):
    if RE_MAJOR.match(chord):
        return MajorChord(get_root(chord), bass_note)
    elif RE_MINOR.match(chord):
        return MinorChord(get_root(chord), bass_note)
    elif RE_SEVEN.match(chord):
        return SevenChord(get_root(chord), bass_note)
    elif RE_DIMIN.match(chord):
        return DiminishedChord(get_root(chord), bass_note)
    elif RE_SLASH.match(chord):
        return parse(chord.split('/')[0], chord.split('/')[1])


def get_root(chord):
    matches = RE_CHORD_ROOT.match(chord)
    return matches.group()


def same(chord1, chord2):
    return chord1.root().midi() % 12 == chord2.root().midi() % 12
