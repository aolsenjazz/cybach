import chords
import constants


class Example:

    def __init__(self, name, chord_progression):
        self._file_name = constants.EXAMPLES + name + '.mid'
        self._chord_progression = chord_progression

    def file_name(self):
        return self._file_name

    def chord_progression(self):
        return self._chord_progression()


# it's so frustrating that python doesn't have a good implementation of overriding abstract classes like in java.
# we deal with it by declaring individual methods for chord progressions so that chord progression code isn't executed
# when the file is read.


def simple():
    chord_progression = chords.ChordProgression()
    chord_progression.set().measure(0).beat(0).commit('C')
    chord_progression.set().measure(0).beat(2).commit('A-')
    chord_progression.set().measure(1).beat(0).commit('E-')
    chord_progression.set().measure(1).beat(1).commit('F')
    chord_progression.set().measure(1).beat(2).commit('G')
    chord_progression.set().measure(2).beat(0).commit('A-')
    chord_progression.set().measure(2).beat(2).commit('C')
    chord_progression.set().measure(3).beat(2).commit('G')
    chord_progression.set().measure(3).beat(3).commit('E7')
    return chord_progression


def mixed_meter():
    chord_progression = chords.ChordProgression()
    chord_progression.set().measure(0).beat(0).commit('C')
    chord_progression.set().measure(0).beat(2).commit('G')
    chord_progression.set().measure(1).beat(0).commit('C')
    chord_progression.set().measure(1).beat(1).commit('G')
    chord_progression.set().measure(1).beat(2).commit('C')
    chord_progression.set().measure(1).beat(3).commit('C7')
    chord_progression.set().measure(2).beat(0).commit('F')
    chord_progression.set().measure(2).beat(3).commit('D7')
    chord_progression.set().measure(3).beat(0).commit('G')
    chord_progression.set().measure(3).beat(3).commit('G7')
    chord_progression.set().measure(4).beat(0).commit('C')
    chord_progression.set().measure(4).beat(3).commit('A-')
    chord_progression.set().measure(5).beat(0).commit('F')
    chord_progression.set().measure(6).beat(0).commit('F#dim')
    chord_progression.set().measure(7).beat(0).commit('A7')
    chord_progression.set().measure(8).beat(0).commit('D')
    chord_progression.set().measure(8).beat(1).commit('A')
    chord_progression.set().measure(9).beat(0).commit('D7')
    chord_progression.set().measure(9).beat(2).commit('G7')
    chord_progression.set().measure(10).beat(0).commit('C')
    return chord_progression


def key_changes():
    chord_progression = chords.ChordProgression()
    chord_progression.set().measure(0).beat(0).commit('C')
    chord_progression.set().measure(0).beat(2).commit('F-')
    chord_progression.set().measure(0).beat(3).commit('Bb7')
    chord_progression.set().measure(1).beat(0).commit('Eb')
    chord_progression.set().measure(2).beat(0).commit('A-')
    chord_progression.set().measure(2).beat(1).commit('D7')
    chord_progression.set().measure(2).beat(2).commit('G')
    chord_progression.set().measure(3).beat(0).commit('B-')
    chord_progression.set().measure(3).beat(2).commit('E7')
    chord_progression.set().measure(4).beat(0).commit('A')
    return chord_progression


def two_four():
    chord_progression = chords.ChordProgression()
    chord_progression.set().measure(0).beat(0).commit('C')
    chord_progression.set().measure(2).beat(0).commit('G')
    chord_progression.set().measure(3).beat(0).commit('C')
    chord_progression.set().measure(4).beat(0).commit('D-')
    chord_progression.set().measure(4).beat(1).commit('G7')
    chord_progression.set().measure(5).beat(0).commit('A-')
    chord_progression.set().measure(6).beat(0).commit('F')
    chord_progression.set().measure(7).beat(0).commit('G')
    return chord_progression


def three_four():
    chord_progression = chords.ChordProgression()
    chord_progression.set().measure(0).beat(0).commit('C-')
    chord_progression.set().measure(1).beat(0).commit('Eb')
    chord_progression.set().measure(2).beat(0).commit('Ab')
    chord_progression.set().measure(3).beat(0).commit('G7')
    chord_progression.set().measure(3).beat(2).commit('C-')
    return chord_progression


def six_four():
    chord_progression = chords.ChordProgression()
    chord_progression.set().measure(0).beat(0).commit('C-')
    chord_progression.set().measure(0).beat(3).commit('Ab')
    chord_progression.set().measure(1).beat(0).commit('C-')
    chord_progression.set().measure(1).beat(2).commit('G7')
    chord_progression.set().measure(1).beat(3).commit('C-')
    chord_progression.set().measure(2).beat(0).commit('F-')
    chord_progression.set().measure(2).beat(3).commit('C-')
    chord_progression.set().measure(3).beat(0).commit('Ddim')
    chord_progression.set().measure(3).beat(3).commit('G7')
    return chord_progression


def four_eight():
    chord_progression = chords.ChordProgression()
    chord_progression.set().measure(0).beat(0).commit('F')
    chord_progression.set().measure(0).beat(1).commit('C7')
    chord_progression.set().measure(0).beat(2).commit('A-')
    chord_progression.set().measure(0).beat(3).commit('G-')
    chord_progression.set().measure(1).beat(0).commit('F')
    chord_progression.set().measure(1).beat(2).commit('Bb')
    chord_progression.set().measure(2).beat(0).commit('F')
    chord_progression.set().measure(2).beat(1).commit('C')
    chord_progression.set().measure(2).beat(2).commit('D-')
    chord_progression.set().measure(2).beat(3).commit('Bb')
    chord_progression.set().measure(3).beat(0).commit('F')
    chord_progression.set().measure(3).beat(2).commit('C7')
    return chord_progression


def six_eight():
    chord_progression = chords.ChordProgression()
    chord_progression.set().measure(0).beat(0).commit('C-')
    chord_progression.set().measure(0).beat(3).commit('Ab')
    chord_progression.set().measure(1).beat(0).commit('Abdim')
    chord_progression.set().measure(1).beat(3).commit('G7')
    chord_progression.set().measure(1).beat(5).commit('Bb7')
    chord_progression.set().measure(2).beat(0).commit('Eb')
    chord_progression.set().measure(2).beat(3).commit('F-')
    chord_progression.set().measure(3).beat(0).commit('G7')
    return chord_progression


def nine_eight():
    chord_progression = chords.ChordProgression()
    chord_progression.set().measure(0).beat(0).commit('G')
    chord_progression.set().measure(0).beat(2).commit('D7')
    chord_progression.set().measure(1).beat(0).commit('C')
    chord_progression.set().measure(1).beat(1).commit('G')
    chord_progression.set().measure(1).beat(2).commit('A-')
    chord_progression.set().measure(2).beat(0).commit('G')
    chord_progression.set().measure(2).beat(1).commit('A-')
    chord_progression.set().measure(2).beat(2).commit('G')
    chord_progression.set().measure(3).beat(0).commit('D')
    chord_progression.set().measure(3).beat(1).commit('A7')
    chord_progression.set().measure(3).beat(2).commit('D')
    return chord_progression


def twelve_eight():
    return 1


def __bach():
    chord_progression = chords.ChordProgression()
    chord_progression.set().measure(0).beat(0).commit('C-')
    chord_progression.set().measure(1).beat(0).commit('Eb')
    chord_progression.set().measure(2).beat(0).commit('Ab')
    chord_progression.set().measure(3).beat(0).commit('G7')
    chord_progression.set().measure(3).beat(2).commit('C-')

    return {
        'name': constants.EXAMPLES + 'bach.mid',
        'chord_progression': chord_progression
    }


_SIMPLE = Example('simple', simple)
_KEY_CHANGES = Example('key_changes', key_changes)
_MIXED_METER = Example('mixed_meter', mixed_meter)
_TWO_FOUR = Example('two_four', two_four)
_THREE_FOUR = Example('three_four', three_four)
_SIX_FOUR = Example('six_four', six_four)
_FOUR_EIGHT = Example('four_eight', four_eight)
_SIX_EIGHT = Example('six_eight', six_eight)
_NINE_EIGHT = Example('nine_eight', nine_eight)
_TWELVE_EIGHT = Example('twelve_eight', twelve_eight)

ALL = {
    'simple': _SIMPLE,
    'key_changes': _KEY_CHANGES,
    'mixed_meter': _MIXED_METER,
    'two_four': _TWO_FOUR,
    'three_four': _THREE_FOUR,
    'six_four': _SIX_FOUR,
    'four_eight': _FOUR_EIGHT,
    'six_eight': _SIX_EIGHT,
    'nine_eight': _NINE_EIGHT,
    'twelve_eight': _TWELVE_EIGHT
}
