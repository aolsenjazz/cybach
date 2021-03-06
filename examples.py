import chords
import constants


class Example:

    def __init__(self, name, chord_progression):
        self._file_name = constants.EXAMPLES + name + '.mid'
        self._chord_progression = chord_progression

    def file_name(self):
        return self._file_name

    def load_chord_progression(self):
        return self._chord_progression()


# it's so frustrating that python doesn't have a good implementation of overriding abstract classes like in java.
# we deal with it by declaring individual methods for chord progressions so that chord progression code isn't executed
# when the file is read.


def simple():
    chords.write('C')
    chords.write('A-', beat=2)
    chords.write('E-', measure=1)
    chords.write('F', measure=1, beat=1)
    chords.write('G', measure=1, beat=2)
    chords.write('A-', measure=2)
    chords.write('C', measure=2, beat=2)
    chords.write('G', measure=3, beat=2)
    chords.write('E7', measure=3, beat=3)


def mixed_meter():
    chords.write('C')
    chords.write('G', beat=2)
    chords.write('C', measure=1)
    chords.write('G', measure=1, beat=1)
    chords.write('C', measure=1, beat=2)
    chords.write('C7', measure=1, beat=3)
    chords.write('F', measure=2)
    chords.write('D7sus', measure=2, beat=3)
    chords.write('G', measure=3)
    chords.write('G7', measure=3, beat=3)
    chords.write('C', measure=4)
    chords.write('A-', measure=4, beat=3)
    chords.write('F', measure=5)
    chords.write('F#dim', measure=6)
    chords.write('A7', measure=7)
    chords.write('D', measure=8)
    chords.write('A', measure=8, beat=1)
    chords.write('D7', measure=9)
    chords.write('G7', measure=9, beat=2)
    chords.write('C', measure=10)


def key_changes():
    chords.write('C')
    chords.write('F-', measure=0, beat=2)
    chords.write('Bb7', measure=0, beat=3)
    chords.write('Eb', measure=1)
    chords.write('A-', measure=2)
    chords.write('D7', measure=2, beat=1)
    chords.write('G', measure=2, beat=2)
    chords.write('B-', measure=3)
    chords.write('E7', measure=3, beat=2)
    chords.write('A', measure=4)


def two_four():
    chords.write('C', measure=0, beat=0)
    chords.write('G', measure=2)
    chords.write('C', measure=3)
    chords.write('D-', measure=4)
    chords.write('G7', measure=4, beat=1)
    chords.write('A-', measure=5)
    chords.write('F', measure=6)
    chords.write('G', measure=7)


def three_four():
    chords.write('C', measure=0, beat=0)
    chords.write('Eb', measure=1)
    chords.write('Ab', measure=2)
    chords.write('G7', measure=3)
    chords.write('C-', measure=3, beat=2)


def six_four():
    chords.write('C-', measure=0, beat=0)
    chords.write('Ab', measure=0, beat=3)
    chords.write('G7', measure=1)
    chords.write('C-', measure=1, beat=2)
    chords.write('F-', measure=1, beat=3)
    chords.write('C-', measure=2)
    chords.write('Ddim', measure=2, beat=3)
    chords.write('G7', measure=3, beat=3)


def four_eight():
    chords.write('F', measure=0)
    chords.write('C7', measure=0, beat=1)
    chords.write('A-', measure=0, beat=2)
    chords.write('G-', measure=0, beat=3)
    chords.write('F', measure=1)
    chords.write('Bb', measure=1, beat=2)
    chords.write('F', measure=2)
    chords.write('C', measure=2, beat=1)
    chords.write('D-', measure=2, beat=2)
    chords.write('Bb', measure=2, beat=3)
    chords.write('F', measure=3)
    chords.write('C7', measure=3, beat=2)


def six_eight():
    chords.write('C-')
    chords.write('Ab', measure=0, beat=3)
    chords.write('Abdim', measure=1)
    chords.write('G7', measure=1, beat=3)
    chords.write('Bb7', measure=1, beat=5)
    chords.write('Eb', measure=2)
    chords.write('F-', measure=2, beat=3)
    chords.write('G7', measure=3)


def nine_eight():
    chords.write('G')
    chords.write('D7', measure=0, beat=2)
    chords.write('C', measure=1)
    chords.write('G', measure=1, beat=1)
    chords.write('A-', measure=1, beat=2)
    chords.write('G', measure=2)
    chords.write('A-', measure=2, beat=1)
    chords.write('G', measure=2, beat=2)
    chords.write('D', measure=3)
    chords.write('A7', measure=3, beat=1)
    chords.write('D', measure=3, beat=2)


_SIMPLE = Example('simple', simple)
_KEY_CHANGES = Example('key_changes', key_changes)
_MIXED_METER = Example('mixed_meter', mixed_meter)
_TWO_FOUR = Example('two_four', two_four)
_THREE_FOUR = Example('three_four', three_four)
_SIX_FOUR = Example('six_four', six_four)
_FOUR_EIGHT = Example('four_eight', four_eight)
_SIX_EIGHT = Example('six_eight', six_eight)
_NINE_EIGHT = Example('nine_eight', nine_eight)

ALL = {
    'simple': _SIMPLE,
    'key_changes': _KEY_CHANGES,
    'mixed_meter': _MIXED_METER,
    'two_four': _TWO_FOUR,
    'three_four': _THREE_FOUR,
    'six_four': _SIX_FOUR,
    'four_eight': _FOUR_EIGHT,
    'six_eight': _SIX_EIGHT,
    'nine_eight': _NINE_EIGHT
}
