import collections
import itertools
import re

import pitches
from rhythm import time

RE_MAJOR = re.compile('^[A-Ga-g]([Bb]|#)?(maj)?$')
RE_MINOR = re.compile('^[A-Ga-g]([Bb]|#)?(-|m(in)?)$')
RE_SEVEN = re.compile('^[A-Ga-g]([Bb]|#)?7$')
RE_DIMIN = re.compile('^[A-Ga-g]([Bb]|#)?dim$')
RE_SLASH = re.compile('^[A-Ga-g]([Bb]|#)?(7(sus[24]?)?|-|m(in)?|dim|maj|sus[24]?)?/[A-Ga-g]([Bb]|#)?$')
RE_SUS2 = re.compile('^[A-Ga-g]([Bb]|#)?(sus2)$')
RE_SUS4 = re.compile('^[A-Ga-g]([Bb]|#)?(sus(4)?)$')
RE_7SUS = re.compile('^[A-Ga-g]([Bb]|#)?7(sus(4)?)$')
RE_CHORD_ROOT = re.compile('[A-Ga-g]([Bb]|#)?')


__progression = None


def __init():
    global __progression

    __progression = ChordProgression()


def write(chord, measure=0, beat=0):
    if isinstance(chord, str):
        parsed = parse(chord)
    elif isinstance(chord, Chord):
        parsed = chord
    else:
        raise TypeError

    sample_pos = time.measure(measure).beat(beat).start()
    __progression[sample_pos] = parsed


def clear():
    global __progression
    __progression = {}


def keys():
    return __progression.keys()


def get(position):
    chord_or_none = __progression.get(position, None)

    if chord_or_none is None:
        k = __progression.keys()
        k.sort()
        k = reversed(k)

        for key in k:
            if position > key:
                return __progression[key]

    return chord_or_none


def in_measure(measure):
    return {key: __progression[key] for key in __progression.keys() if measure.start() <= key < measure.end()}


def progression():
    return __progression


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
    elif RE_SUS2.match(chord):
        return Sus2Chord(get_root(chord), bass_note)
    elif RE_SUS4.match(chord):
        return Sus4Chord(get_root(chord), bass_note)
    elif RE_7SUS.match(chord):
        return SevenSusChord(get_root(chord), bass_note)


def get_root(chord):
    if not isinstance(chord, str):
        raise ValueError('must submit a string')

    matches = RE_CHORD_ROOT.match(chord)
    return matches.group()


def same(chord1, chord2):
    return chord1.root().midi() % 12 == chord2.root().midi() % 12


class Chord:

    def __init__(self, root, bass_note=None):
        self._root = pitches.parse(root)

        if bass_note is None:
            self.bass_note = self._root
        else:
            self.bass_note = pitches.parse(bass_note)

    def __repr__(self):
        return self.string()

    def __contains__(self, note):
        parsed = None

        if isinstance(note, pitches.Pitch):
            parsed = note
        elif isinstance(note, int):
            parsed = pitches.parse(note)

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

        return pitches.same_species(other.bass_note, self.bass_note) and pitches.same_species(other._root, self._root)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.bass_note, self._root))

    def root_in_bass(self):
        return pitches.same_species(self._root, self.bass_note)

    def string(self):
        raise NotImplementedError

    def note_above(self, note):
        """
        Basically just a wrapper for the private method to make up for improper API usage

        :param note: midi value, text value, or Note object
        :return:
        """
        if isinstance(note, pitches.Pitch):
            return self.__note_above(note.midi())
        elif isinstance(note, int):
            return self.__note_above(note)
        elif isinstance(note, str):
            return self.__note_above(pitches.parse(note).midi())

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

    def _compute_octaves(self):
        all_notes = list(itertools.chain(
            *[[i for i in range(128)[pitch.midi() % 12::12]]
              for pitch
              in self.all_degrees()]))
        all_notes.sort()
        return all_notes

    def all_octaves(self):
        return self._all_octaves


class Sus2Chord(Chord):

    def __init__(self, root_note, bass_note=None):
        Chord.__init__(self, root_note, bass_note)
        self.__two = pitches.parse(self._root.midi() + 2)
        self.__five = pitches.parse(self._root.midi() + 7)
        self._all_octaves = self._compute_octaves()

    def three(self):
        return self.__two

    def five(self):
        return self.__five

    def scale(self):
        return pitches.ionian(self._root.midi())

    def string(self):
        return pitches.species(self._root)

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


class Sus4Chord(Chord):

    def __init__(self, root_note, bass_note=None):
        Chord.__init__(self, root_note, bass_note)
        self.__four = pitches.parse(self._root.midi() + 5)
        self.__five = pitches.parse(self._root.midi() + 7)
        self._all_octaves = self._compute_octaves()

    def three(self):
        return self.__four

    def five(self):
        return self.__five

    def scale(self):
        return pitches.ionian(self._root.midi())

    def string(self):
        return pitches.species(self._root)

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


class MajorChord(Chord):

    def __init__(self, root_note, bass_note=None):
        Chord.__init__(self, root_note, bass_note)
        self.__three = pitches.parse(self._root.midi() + 4)
        self.__five = pitches.parse(self._root.midi() + 7)
        self._all_octaves = self._compute_octaves()

    def three(self):
        return self.__three

    def five(self):
        return self.__five

    def scale(self):
        return pitches.ionian(self._root.midi())

    def string(self):
        return pitches.species(self._root)

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
        self.__three = pitches.parse(self._root.midi() + 3)
        self.__five = pitches.parse(self._root.midi() + 7)
        self._all_octaves = self._compute_octaves()

    def three(self):
        return self.__three

    def five(self):
        return self.__five

    def string(self):
        return pitches.species(self._root) + '-'

    def scale(self):
        return pitches.aeolian(self._root.midi())

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


class SevenSusChord(Sus4Chord):
    def __init__(self, root_note, bass_note=None):
        self.__seven = pitches.parse(pitches.parse(root_note).midi() + 10)
        Sus4Chord.__init__(self, root_note, bass_note)
        self._all_octaves = self._compute_octaves()

    def __contains__(self, note):
        parsed = None

        if isinstance(note, pitches.Pitch):
            parsed = note
        elif isinstance(note, int):
            parsed = pitches.parse(note)

        if parsed.species() == self.__seven.species():
            return True
        return Chord.__contains__(self, parsed)

    def string(self):
        return pitches.species(self._root) + '7sus'

    def all_degrees(self):
        return Chord.all_degrees(self) + (self.__seven,)

    def _compute_octaves(self):
        all_of_em = Chord._compute_octaves(self) + [i for i in range(128)[self.__seven.midi() % 12::12]]
        all_of_em.sort()
        return all_of_em

    def __note_above(self, pitch):
        if pitch == self.__five:
            return self.__seven.species

        if pitch == self.__seven.species:
            return self._root

        return Chord.__note_above(self, pitch)

    def scale(self):
        return pitches.mixolydian(self._root.midi())


class SevenChord(MajorChord):

    def __init__(self, root_note, bass_note=None):
        self.__seven = pitches.parse(pitches.parse(root_note).midi() + 10)
        MajorChord.__init__(self, root_note, bass_note)
        self._all_octaves = self._compute_octaves()

    def __contains__(self, note):
        parsed = None

        if isinstance(note, pitches.Pitch):
            parsed = note
        elif isinstance(note, int):
            parsed = pitches.parse(note)

        if parsed.species() == self.__seven.species():
            return True
        return Chord.__contains__(self, parsed)

    def string(self):
        return pitches.species(self._root) + '7'

    def all_degrees(self):
        return Chord.all_degrees(self) + (self.__seven,)

    def _compute_octaves(self):
        all_of_em = Chord._compute_octaves(self) + [i for i in range(128)[self.__seven.midi() % 12::12]]
        all_of_em.sort()
        return all_of_em

    def __note_above(self, pitch):
        if pitch == self.__five:
            return self.__seven.species

        if pitch == self.__seven.species:
            return self._root

        return Chord.__note_above(self, pitch)

    def scale(self):
        return pitches.mixolydian(self._root.midi())


class DiminishedChord(MinorChord):

    def __init__(self, root_note, bass_note=None):
        self.__five = pitches.parse(pitches.parse(root_note).midi() + 6)
        self.__seven = pitches.parse(pitches.parse(root_note).midi() + 9)
        MinorChord.__init__(self, root_note, bass_note)
        self._all_octaves = self._compute_octaves()

    def __contains__(self, note):
        parsed = None

        if isinstance(note, pitches.Pitch):
            parsed = note
        elif isinstance(note, int):
            parsed = pitches.parse(note)

        if parsed.species() == self.__seven.species():
            return True
        return Chord.__contains__(self, parsed)

    def five(self):
        return self.__five

    def string(self):
        return pitches.species(self._root) + 'dim'

    def all_degrees(self):
        return Chord.all_degrees(self) + (self.__seven,)

    def _compute_octaves(self):
        all_of_em = Chord._compute_octaves(self) + [i for i in range(128)[self.__seven.midi() % 12::12]]
        all_of_em.sort()
        return all_of_em

    def __note_above(self, pitch):
        if pitch == self.__five:
            return self.__seven.species

        if pitch == self.__seven.species:
            return self._root

        return Chord.__note_above(self, pitch)

    def scale(self):
        return pitches.half_whole(self._root.midi())

    def indicates_subdominant(self, *pitches):
        return False


class ChordProgression(collections.MutableMapping):

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))

    def __getitem__(self, key):
        return self.store.get(key, None)

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


__init()
