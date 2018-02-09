import collections
import config
import chords
import notes
import vars


class KeySignatures(collections.MutableMapping):

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

    def __repr__(self):
        string = ''
        for key in self.store:
            string += '\n' + str(key) + ': ' + str(self.store[key])

        return string

    def __keytransform__(self, key):
        return key

    def set(self):
        return KeySignatureSetter(self)


class _KeySignature:
    def __init__(self):
        pass

    def __repr__(self):
        return str(self.root_chord)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return chords.same(other.root_chord, self.root_chord)

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return False

        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.root_chord.root, self.root_chord.three))

    def is_functional(self, chord):
        raise NotImplementedError

    def harmonic_relevance(self, chord):
        if notes.same_species(chord.root, self.five()) and \
                isinstance(chord, chords.SevenChord):
            return vars.FIVE_DOMINANT_HARMONY
        elif notes.same_species(chord.root, self.five()) and \
                isinstance(chord, chords.MajorChord):
            return vars.FIVE_MAJOR_HARMONY
        elif notes.same_species(chord.root, self.seven()) and \
                isinstance(chord, chords.DiminishedChord):
            return vars.MAJOR_SEVEN_DIMINISHED_HARMONY

        return 0.0

    def functional_relevance(self, c1, c2):
        score = 0.0

        if self.is_functional(c1) and self.is_functional(c2):
            # Dominant five chords in functional relationship are more valuable than just major fives
            if (notes.same_species(c1.root, self.five()) and isinstance(c1, chords.SevenChord)) or \
                    (notes.same_species(c2.root, self.five()) and isinstance(c2, chords.SevenChord)):
                score += vars.DOMINANT_FIVE_IN_FUNCTIONAL_RELEVANCE
            elif (notes.same_species(c1.root, self.five()) and isinstance(c1, chords.MajorChord)) or \
                    (notes.same_species(c2.root, self.five()) and isinstance(c2, chords.MajorChord)):
                score += vars.MAJOR_FIVE_IN_FUNCTIONAL_RELEVANCE

            if notes.same_species(c1.root, self.five()) and notes.same_species(c2.root, self.root()):
                score += vars.FIVE_ONE_FUNCTIONALITY
            elif notes.same_species(c1.root, self.seven()) and notes.same_species(c2.root, self.root()):
                score += vars.SEVEN_ONE_FUNCTIONALITY
            elif notes.same_species(c1.root, self.two()) and notes.same_species(c2.root, self.five()):
                score += vars.TWO_FIVE_FUNCTIONALITY
            elif notes.same_species(c1.root, self.fourth()) and notes.same_species(c2.root, self.five()):
                score += vars.FOUR_FIVE_FUNCTIONALITY

        return score

    def root(self):
        return self.root_chord.root

    def two(self):
        return notes.parse(self.root().midi() + 2)

    def three(self):
        return self.root_chord.three()

    def fourth(self):
        return notes.parse(self.root().midi() + 5)

    def five(self):
        return self.root_chord.five()

    def flat_six(self):
        return notes.parse(self.root().midi() + 8)

    def six(self):
        return notes.parse(self.root().midi() + 9)

    def flat_seventh(self):
        return notes.parse(self.root().midi() + 10)

    def seven(self):
        return notes.parse(self.root().midi() + 11)


class MajorKeySignature(_KeySignature):

    def __init__(self, root_note):
        _KeySignature.__init__(self)

        self.root_chord = chords.MajorChord(notes.parse(root_note))

    def is_functional(self, chord):
        chord_root = chord.root

        if (notes.same_species(chord_root, self.root()) or
            notes.same_species(chord_root, self.fourth()) or
            notes.same_species(chord_root, self.five())) and \
                isinstance(chord, chords.MajorChord):
            return True
        elif (notes.same_species(chord_root, self.five())) \
                and isinstance(chord, chords.SevenChord):
            return True
        elif (notes.same_species(chord_root, self.two()) or
              notes.same_species(chord_root, self.three()) or
              notes.same_species(chord_root, self.six())) and \
                isinstance(chord, chords.MinorChord):
            return True
        elif (notes.same_species(chord_root, self.seven()) and
              isinstance(chord, chords.DiminishedChord)):
            return True

        return False

    def harmonic_relevance(self, chord):
        if notes.same_species(chord.root, self.root()) and \
                isinstance(chord, chords.MajorChord):
            return vars.ONE_CHORD_HARMONY

        elif notes.same_species(chord.root, self.two()) and \
                isinstance(chord, chords.MinorChord):
            return vars.TWO_CHORD_HARMONY
        elif notes.same_species(chord.root, self.three()) and \
                isinstance(chord, chords.MinorChord):
            return vars.THREE_CHORD_HARMONY

        elif notes.same_species(chord.root, self.fourth()) and \
                isinstance(chord, chords.MajorChord):
            return vars.FOUR_CHORD_HARMONY

        elif notes.same_species(chord.root, self.six()) and \
                isinstance(chord, chords.MinorChord):
            return vars.SIX_CHORD_HARMONY

        return _KeySignature.harmonic_relevance(self, chord)

    def functional_relevance(self, c1, c2):
        score = _KeySignature.functional_relevance(self, c1, c2)

        if self.is_functional(c1) and self.is_functional(c2) and \
                notes.same_species(c1.root, self.five()) and notes.same_species(c2.root, self.six()):
            score += vars.FIVE_SIX_FUNCTIONALITY

        return score


class MinorKeySignature(_KeySignature):

    def __init__(self, root_note):
        _KeySignature.__init__(self)

        self.root_chord = chords.MinorChord(notes.parse(root_note))

    def is_functional(self, chord):
        chord_root = chord.root

        if (notes.same_species(chord_root, self.three()) or
            notes.same_species(chord_root, self.flat_six()) or
            notes.same_species(chord_root, self.five())) and \
                isinstance(chord, chords.MajorChord):
            return True
        elif (notes.same_species(chord_root, self.five())) \
                and isinstance(chord, chords.SevenChord):
            return True
        elif (notes.same_species(chord_root, self.root()) or
              notes.same_species(chord_root, self.fourth())) and \
                isinstance(chord, chords.MinorChord):
            return True
        elif (notes.same_species(chord_root, self.seven() or
              notes.same_species(chord_root, self.two())) and
              isinstance(chord_root, chords.DiminishedChord)):
            return True

        return False

    def harmonic_relevance(self, chord):
        if notes.same_species(chord.root, self.root()) and \
                isinstance(chord, chords.MinorChord):
            return vars.ONE_CHORD_HARMONY
        elif notes.same_species(chord.root, self.two()) and \
                isinstance(chord, chords.DiminishedChord):
            return vars.TWO_CHORD_HARMONY
        elif notes.same_species(chord.root, self.three()) and \
                isinstance(chord, chords.MajorChord):
            return vars.THREE_CHORD_HARMONY
        elif notes.same_species(chord.root, self.fourth()) and \
                isinstance(chord, chords.MinorChord):
            return vars.FOUR_CHORD_HARMONY
        elif notes.same_species(chord.root, self.flat_six()) and \
                isinstance(chord, chords.MajorChord):
            return vars.SIX_CHORD_HARMONY

        return _KeySignature.harmonic_relevance(self, chord)

    def functional_relevance(self, c1, c2):
        score = _KeySignature.functional_relevance(self, c1, c2)

        if self.is_functional(c1) and self.is_functional(c2) and \
                notes.same_species(c1.root, self.five()) and notes.same_species(c2.root, self.flat_six()):
            score += vars.FIVE_SIX_FUNCTIONALITY

        return score


class KeySignatureSetter:

    def __init__(self, key_signatures):
        self.key_signatures = key_signatures
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
            parsed = chords.parse(chord)
        elif isinstance(chord, Chord):
            parsed = chord
        else:
            raise TypeError

        sample_pos = config.time_signatures.sample_position(measure=self.internal_measure, beat=self.internal_beat)

        self.key_signatures[sample_pos] = parsed
