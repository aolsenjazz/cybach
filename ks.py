import chords
import pitches
import vars


__signatures = {}


def signatures():
    return __signatures


def parse(value):
    if isinstance(value, str):

        if chords.RE_MAJOR.match(value):
            return MajorKeySignature(chords.get_root(value))
        elif chords.RE_MINOR.match(value):
            return MinorKeySignature(chords.get_root(value))
        else:
            raise ValueError

    elif isinstance(value, chords.Chord):
        return parse(value.string())


def clear():
    global __signatures
    __signatures = {}


def write(key_signature, position):
    if isinstance(key_signature, str):
        parsed = parse(key_signature)
    elif isinstance(key_signature, _KeySignature):
        parsed = key_signature
    else:
        raise TypeError

    __signatures[position] = parsed


def get(position):
    key_signature_or_none = __signatures[position]

    if key_signature_or_none is None:
        keys = __signatures.keys()
        keys.sort()
        keys = reversed(keys)

        for key in keys:
            if position > key:
                return __signatures[key]

    return key_signature_or_none


class _KeySignature:

    def __init__(self):
        pass

    def __repr__(self):
        return 'KS: ' + str(self.root_chord)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        elif isinstance(other, chords.Chord):
            return chords.same(other.root_chord, self.root_chord)

        return False

    def __ne__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.root_chord.root().midi(), self.root_chord.three().midi()))

    def is_functional(self, chord):
        """
        Returns True if the chord submitted is function within the key.

        :param chord: chords.Chord object
        :return: True or False
        """

        raise NotImplementedError

    def harmonic_relevance(self, chord):
        """
        Some chords are more indicative of a certain key than other. E.g. in C, the chords C and G7 strongly
        indicate that we're in the key of C. Returns a score based on harmonic relevance to the key

        :param chord: chords.Chords object
        :return: Harmony relevance score
        """
        if pitches.same_species(chord.root(), self.five()) and \
                isinstance(chord, chords.SevenChord):
            return vars.FIVE_DOMINANT_HARMONY
        elif pitches.same_species(chord.root(), self.five()) and \
                isinstance(chord, chords.MajorChord):
            return vars.FIVE_MAJOR_HARMONY
        elif pitches.same_species(chord.root(), self.seven()) and \
                isinstance(chord, chords.DiminishedChord):
            return vars.MAJOR_SEVEN_DIMINISHED_HARMONY

        return 0.0

    def functional_relevance(self, c1, c2):
        """
        Some functional relationships are more indicative of some key sigantures. E.g. A7 -> D is strongly
        indicative of the key of D. Returns a score based on how functionally relevant the two chords are in this key.

        * Not currently implemented: The dimension of time needs to be included within the scoring mechanism.
        The following example illustrates why. Assume we're in 4/4 and the actual key signature is A

        | A |   |   |   || D |   |   |   || F- |   |   |  ||

        Why humans can deduce that this relationship is indicative of A, the computer just see A -> D, which is
        more indicative of the key of D. The F- could be any chord that would force a key change to be registered.

        :param c1: first chord
        :param c2: second chord
        :return: functionality score based on the chords
        """
        score = 0.0

        if self.is_functional(c1) and self.is_functional(c2):
            # Dominant five chords in functional relationship are more valuable than just major fives
            if (pitches.same_species(c1.root(), self.five()) and isinstance(c1, chords.SevenChord)) or \
                    (pitches.same_species(c2.root(), self.five()) and isinstance(c2, chords.SevenChord)):
                score += vars.DOMINANT_FIVE_IN_FUNCTIONAL_RELEVANCE
            elif (pitches.same_species(c1.root(), self.five()) and isinstance(c1, chords.MajorChord)) or \
                    (pitches.same_species(c2.root(), self.five()) and isinstance(c2, chords.MajorChord)):
                score += vars.MAJOR_FIVE_IN_FUNCTIONAL_RELEVANCE

            if pitches.same_species(c1._root, self.five()) and pitches.same_species(c2._root, self.one()):
                score += vars.FIVE_ONE_FUNCTIONALITY
            elif pitches.same_species(c1._root, self.seven()) and pitches.same_species(c2._root, self.one()):
                score += vars.SEVEN_ONE_FUNCTIONALITY
            elif pitches.same_species(c1._root, self.two()) and pitches.same_species(c2._root, self.five()):
                score += vars.TWO_FIVE_FUNCTIONALITY
            elif pitches.same_species(c1._root, self.four()) and pitches.same_species(c2._root, self.five()):
                score += vars.FOUR_FIVE_FUNCTIONALITY

        return score

    def scale(self):
        return self.root_chord.scale()

    def one(self):
        return self.root_chord.root()

    def two(self):
        return pitches.parse(self.one().midi() + 2)

    def three(self):
        return self.root_chord.three()

    def four(self):
        return pitches.parse(self.one().midi() + 5)

    def five(self):
        return self.root_chord.five()

    def flat_six(self):
        return pitches.parse(self.one().midi() + 8)

    def six(self):
        return pitches.parse(self.one().midi() + 9)

    def flat_seven(self):
        return pitches.parse(self.one().midi() + 10)

    def seven(self):
        return pitches.parse(self.one().midi() + 11)


class MajorKeySignature(_KeySignature):

    def __init__(self, root_note):
        _KeySignature.__init__(self)

        self.root_chord = chords.MajorChord(pitches.parse(root_note))

    def is_functional(self, chord):
        chord_root = chord.root()

        if (pitches.same_species(chord_root, self.one()) or
            pitches.same_species(chord_root, self.four()) or
            pitches.same_species(chord_root, self.five())) and \
                isinstance(chord, chords.MajorChord):
            return True
        elif (pitches.same_species(chord_root, self.five())) \
                and isinstance(chord, chords.SevenChord):
            return True
        elif (pitches.same_species(chord_root, self.two()) or
              pitches.same_species(chord_root, self.three()) or
              pitches.same_species(chord_root, self.six())) and \
                isinstance(chord, chords.MinorChord):
            return True
        elif (pitches.same_species(chord_root, self.seven()) and
              isinstance(chord, chords.DiminishedChord)):
            return True

        return False

    def harmonic_relevance(self, chord):

        if pitches.same_species(chord.root(), self.one()) and \
                isinstance(chord, chords.MajorChord):
            return vars.ONE_CHORD_HARMONY

        elif pitches.same_species(chord.root(), self.two()) and \
                isinstance(chord, chords.MinorChord):
            return vars.TWO_CHORD_HARMONY
        elif pitches.same_species(chord.root(), self.three()) and \
                isinstance(chord, chords.MinorChord):
            return vars.THREE_CHORD_HARMONY

        elif pitches.same_species(chord.root(), self.four()) and \
                isinstance(chord, chords.MajorChord):
            return vars.FOUR_CHORD_HARMONY

        elif pitches.same_species(chord.root(), self.six()) and \
                isinstance(chord, chords.MinorChord):
            return vars.SIX_CHORD_HARMONY

        return _KeySignature.harmonic_relevance(self, chord)

    def functional_relevance(self, c1, c2):
        score = _KeySignature.functional_relevance(self, c1, c2)

        if self.is_functional(c1) and self.is_functional(c2) and \
                pitches.same_species(c1.root(), self.five()) and pitches.same_species(c2.root(), self.six()):
            score += vars.FIVE_SIX_FUNCTIONALITY

        return score


class MinorKeySignature(_KeySignature):

    def __init__(self, root_note):
        _KeySignature.__init__(self)

        self.root_chord = chords.MinorChord(pitches.parse(root_note))

    def is_functional(self, chord):
        chord_root = chord.root()

        if (pitches.same_species(chord_root, self.three()) or
            pitches.same_species(chord_root, self.flat_six()) or
            pitches.same_species(chord_root, self.five())) and \
                isinstance(chord, chords.MajorChord):
            return True
        elif (pitches.same_species(chord_root, self.five())) \
                and isinstance(chord, chords.SevenChord):
            return True
        elif (pitches.same_species(chord_root, self.one()) or
              pitches.same_species(chord_root, self.four())) and \
                isinstance(chord, chords.MinorChord):
            return True
        elif (pitches.same_species(chord_root, self.seven() or
                                               pitches.same_species(chord_root, self.two())) and
              isinstance(chord_root, chords.DiminishedChord)):
            return True

        return False

    def harmonic_relevance(self, chord):
        if pitches.same_species(chord.root(), self.one()) and \
                isinstance(chord, chords.MinorChord):
            return vars.ONE_CHORD_HARMONY
        elif pitches.same_species(chord.root(), self.two()) and \
                isinstance(chord, chords.DiminishedChord):
            return vars.TWO_CHORD_HARMONY
        elif pitches.same_species(chord.root(), self.three()) and \
                isinstance(chord, chords.MajorChord):
            return vars.THREE_CHORD_HARMONY
        elif pitches.same_species(chord.root(), self.four()) and \
                isinstance(chord, chords.MinorChord):
            return vars.FOUR_CHORD_HARMONY
        elif pitches.same_species(chord.root(), self.flat_six()) and \
                isinstance(chord, chords.MajorChord):
            return vars.SIX_CHORD_HARMONY

        return _KeySignature.harmonic_relevance(self, chord)

    def functional_relevance(self, c1, c2):
        score = _KeySignature.functional_relevance(self, c1, c2)

        if self.is_functional(c1) and self.is_functional(c2) and \
                pitches.same_species(c1.root(), self.five()) and pitches.same_species(c2.root(), self.flat_six()):
            score += vars.FIVE_SIX_FUNCTIONALITY

        return score
