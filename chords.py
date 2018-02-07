import notes
import re
import config
import collections

RE_MAJOR = re.compile('^[A-Ga-g]([Bb]|#)?(maj)?$')
RE_MINOR = re.compile('^[A-Ga-g]([Bb]|#)?(-|m(in)?)?$')
RE_SEVEN = re.compile('^[A-Ga-g]([Bb]|#)?7?$')
RE_DIMIN = re.compile('^[A-Ga-g]([Bb]|#)?dim$')
RE_SLASH = re.compile('^[A-Ga-g]([Bb]|#)?(7|-|m(in)?|dim|maj)?/[A-Ga-g]([Bb]|#)?$')

RE_CHORD_ROOT = re.compile('([A-Ga-g]|#)')


class Chord:

    def __init__(self, root, bass_note=None):
        note = -1

        if isinstance(root, notes.Note):
            note = root
        elif isinstance(root, int):
            note = notes.Note(root)
        elif isinstance(root, str):
            note = notes.Note(root)

        self.root = note

        if bass_note is None:
            self.bass_note = self.root
        else:
            if isinstance(bass_note, notes.Note):
                self.bass_note = bass_note
            elif isinstance(root, int):
                self.bass_note = notes.Note(bass_note)
            elif isinstance(root, str):
                self.bass_note = notes.Note(bass_note)

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

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return notes.same_species(other.bass_note, self.bass_note) and notes.same_species(other.root, self.root)

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return False

        return not (notes.same_species(other.bass_note, self.bass_note) and notes.same_species(other.root, self.root))

    def __hash__(self):
        return hash((self.bass_note, self.root))

    def root_in_bass(self):
        return notes.same_species(self.root, self.bass_note)

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

    def __init__(self, root_note, bass_note=None):
        Chord.__init__(self, root_note, bass_note)
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

    def __init__(self, root_note, bass_note=None):
        Chord.__init__(self, root_note, bass_note)
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

    def __init__(self, root_note, bass_note=None):
        Chord.__init__(self, root_note, bass_note)
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

    def __init__(self, root_note, bass_note=None):
        Chord.__init__(self, root_note, bass_note)
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

    def set(self):
        return ChordProgressionSetter(self)

    def chords_in_measure(self, measure_index):
        sample_pos = config.time_signatures.sample_position(measure=measure_index)
        time_signature = config.time_signatures[sample_pos]
        measure_end_pos = sample_pos + time_signature.samples_per_measure()
        chords = {}

        for key in [k for k in config.chord_progression.keys() if sample_pos <= k < measure_end_pos]:
            chords[key] = self[key]

        return chords


class ChordProgressionSetter:

    def __init__(self, chord_progression):
        self.chord_progression = chord_progression
        self.internal_measure = 0
        self.internal_beat = 0

    def measure(self, measure):
        self.internal_measure = measure
        return self

    def beat(self, beat):
        self.internal_beat = beat
        return self

    def commit(self, chord):
        if isinstance(chord, str):
            parsed = parse(chord)
        elif isinstance(chord, Chord):
            parsed = chord
        else:
            raise TypeError

        sample_pos = config.time_signatures.sample_position(measure=self.internal_measure, beat=self.internal_beat)
        self.chord_progression[sample_pos] = parsed


def parse(chord, bass_note=None):
    if RE_MAJOR.match(chord):
        return MajorChord(__get_root(chord), bass_note)
    elif RE_MINOR.match(chord):
        return MinorChord(__get_root(chord), bass_note)
    elif RE_SEVEN.match(chord):
        return SevenChord(__get_root(chord), bass_note)
    elif RE_DIMIN.match(chord):
        return DiminishedChord(__get_root(chord), bass_note)
    elif RE_SLASH.match(chord):
        return parse(chord.split('/')[0], chord.split('/')[1])


def __get_root(chord):
    match = RE_CHORD_ROOT.search(chord)
    return match.group()


def same(chord1, chord2):
    return chord1.root.midi_value % 12 == chord2.root.midi_value % 12
