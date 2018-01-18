import pat_util
import chords
import song
import ks
from constants import RESOLUTION
import ts
import midi
import domain
import constants


def __read_midi(file_name):
    try:
        return midi.read_midifile(file_name)
    except TypeError:
        print 'Midi file is malformed. Try exporting a new one from any DAW'
        exit(2)


def simple():
    pattern = pat_util.normalize_resolution(__read_midi(constants.EXAMPLES + 'simple.mid'))
    soprano = domain.Sequence(pattern[0])

    time_signatures = soprano.time_signatures

    key_signatures = ks.KeySignatures()
    key_signatures[0] = chords.parse('C')

    chord_progression = chords.ChordProgression()
    chord_progression[0] = chords.parse('C')
    chord_progression[(0 * (RESOLUTION * 4)) + (2 * RESOLUTION)] = chords.parse('A-')
    chord_progression[(1 * (RESOLUTION * 4)) + (0 * RESOLUTION)] = chords.parse('E-')
    chord_progression[(1 * (RESOLUTION * 4)) + (1 * RESOLUTION)] = chords.parse('F')
    chord_progression[(1 * (RESOLUTION * 4)) + (2 * RESOLUTION)] = chords.parse('G')
    chord_progression[(2 * (RESOLUTION * 4)) + (0 * RESOLUTION)] = chords.parse('A-')
    chord_progression[(2 * (RESOLUTION * 4)) + (2 * RESOLUTION)] = chords.parse('C')
    chord_progression[(3 * (RESOLUTION * 4)) + (2 * RESOLUTION)] = chords.parse('G')
    chord_progression[(3 * (RESOLUTION * 4)) + (3 * RESOLUTION)] = chords.parse('E7')

    return song.Song('simple', soprano, time_signatures, key_signatures, chord_progression, {})


def key_changes():
    pattern = pat_util.normalize_resolution(__read_midi(constants.EXAMPLES + 'key_changes.mid'))
    soprano = domain.Sequence(pattern[0])

    time_signatures = soprano.time_signatures

    key_signatures = ks.KeySignatures()
    key_signatures[0] = chords.parse('C')
    key_signatures[(0 * (RESOLUTION * 4)) + (2 * RESOLUTION)] = chords.parse('Eb')
    key_signatures[(2 * (RESOLUTION * 4)) + (0 * RESOLUTION)] = chords.parse('G')
    key_signatures[(3 * (RESOLUTION * 4)) + (0 * RESOLUTION)] = chords.parse('A')

    chord_progression = chords.ChordProgression()
    chord_progression[0] = chords.parse('C')
    chord_progression[(0 * (RESOLUTION * 4)) + (2 * RESOLUTION)] = chords.parse('F-')
    chord_progression[(0 * (RESOLUTION * 4)) + (3 * RESOLUTION)] = chords.parse('Bb7')
    chord_progression[(1 * (RESOLUTION * 4)) + (0 * RESOLUTION)] = chords.parse('Eb')
    chord_progression[(2 * (RESOLUTION * 4)) + (0 * RESOLUTION)] = chords.parse('A-')
    chord_progression[(2 * (RESOLUTION * 4)) + (1 * RESOLUTION)] = chords.parse('D7')
    chord_progression[(2 * (RESOLUTION * 4)) + (2 * RESOLUTION)] = chords.parse('G')
    chord_progression[(3 * (RESOLUTION * 4)) + (0 * RESOLUTION)] = chords.parse('B-')
    chord_progression[(3 * (RESOLUTION * 4)) + (2 * RESOLUTION)] = chords.parse('E7')
    chord_progression[(4 * (RESOLUTION * 4)) + (0 * RESOLUTION)] = chords.parse('A')

    return song.Song('key_changes', soprano, time_signatures, key_signatures, chord_progression, {})


def time_changes():
    return 1


def two_four():
    pattern = pat_util.normalize_resolution(__read_midi(constants.EXAMPLES + 'two_four.mid'))
    soprano = domain.Sequence(pattern[0])

    time_signatures = ts.TimeSignatures()
    time_signatures[0] = midi.TimeSignatureEvent(tick=0, data=[2, 2, 36, 8])

    key_signatures = ks.KeySignatures()
    key_signatures[0] = chords.parse('C')

    chord_progression = chords.ChordProgression()
    chord_progression[0] = chords.parse('C')
    chord_progression[(2 * (RESOLUTION * 2)) + (0 * RESOLUTION)] = chords.parse('G')
    chord_progression[(3 * (RESOLUTION * 2)) + (0 * RESOLUTION)] = chords.parse('C')
    chord_progression[(4 * (RESOLUTION * 2)) + (0 * RESOLUTION)] = chords.parse('D-')
    chord_progression[(4 * (RESOLUTION * 2)) + (1 * RESOLUTION)] = chords.parse('G7')
    chord_progression[(5 * (RESOLUTION * 2)) + (0 * RESOLUTION)] = chords.parse('A-')
    chord_progression[(6 * (RESOLUTION * 2)) + (0 * RESOLUTION)] = chords.parse('F')
    chord_progression[(7 * (RESOLUTION * 2)) + (0 * RESOLUTION)] = chords.parse('G')

    return song.Song('two_four', soprano, time_signatures, key_signatures, chord_progression, {})


def three_four():
    pattern = pat_util.normalize_resolution(__read_midi(constants.EXAMPLES + 'three_four.mid'))
    soprano = domain.Sequence(pattern[0])

    time_signatures = ts.TimeSignatures()
    time_signatures[0] = midi.TimeSignatureEvent(tick=0, data=[3, 2, 36, 8])

    key_signatures = ks.KeySignatures()
    key_signatures[0] = chords.parse('C-')

    chord_progression = chords.ChordProgression()
    chord_progression[0] = chords.parse('C-')
    chord_progression[(1 * (RESOLUTION * 3)) + (0 * RESOLUTION)] = chords.parse('Eb')
    chord_progression[(2 * (RESOLUTION * 3)) + (0 * RESOLUTION)] = chords.parse('Ab')
    chord_progression[(3 * (RESOLUTION * 3)) + (0 * RESOLUTION)] = chords.parse('G7')
    chord_progression[(3 * (RESOLUTION * 3)) + (2 * RESOLUTION)] = chords.parse('C-')

    return song.Song('three_four', soprano, time_signatures, key_signatures, chord_progression, {})


def six_four():
    return 1


def four_eight():
    return 1


def six_eight():
    pattern = pat_util.normalize_resolution(__read_midi(constants.EXAMPLES + 'six_eight.mid'))
    pattern = pat_util.scale_tick_values(pattern, 16, RESOLUTION)

    soprano = domain.Sequence(pattern[0])

    time_signatures = ts.TimeSignatures()
    time_signatures[0] = midi.TimeSignatureEvent(tick=0, data=[6, 3, 36, 8])
    soprano.time_signatures = time_signatures

    key_signatures = ks.KeySignatures()
    key_signatures[0] = chords.parse('C-')

    chord_progression = chords.ChordProgression()
    chord_progression[0] = chords.parse('C-')
    chord_progression[(0 * (RESOLUTION * 6)) + (3 * RESOLUTION)] = chords.parse('Ab')
    chord_progression[(1 * (RESOLUTION * 6)) + (0 * RESOLUTION)] = chords.parse('Abdim')
    chord_progression[(1 * (RESOLUTION * 6)) + (3 * RESOLUTION)] = chords.parse('G7')
    chord_progression[(1 * (RESOLUTION * 6)) + (5 * RESOLUTION)] = chords.parse('Bb7')
    chord_progression[(2 * (RESOLUTION * 6)) + (0 * RESOLUTION)] = chords.parse('Eb')
    chord_progression[(2 * (RESOLUTION * 6)) + (3 * RESOLUTION)] = chords.parse('F-')
    chord_progression[(3 * (RESOLUTION * 6)) + (0 * RESOLUTION)] = chords.parse('G7')

    return song.Song('six_eight', soprano, time_signatures, key_signatures, chord_progression, {})


def nine_eight():
    return 1


def twelve_eight():
    return 1


SIMPLE = simple()
KEY_CHANGES = key_changes()
TIME_CHANGES = time_changes()
TWO_FOUR = two_four()
THREE_FOUR = three_four()
SIX_FOUR = six_four()
FOUR_EIGHT = four_eight()
SIX_EIGHT = six_eight()
NINE_EIGHT = nine_eight()
TWELVE_EIGHT = twelve_eight()


ALL = {
    'simple': SIMPLE,
    'key_changes': KEY_CHANGES,
    'time_changes': TIME_CHANGES,
    'two_four': TWO_FOUR,
    'three_four': THREE_FOUR,
    'six_four': SIX_FOUR,
    'four_eight': FOUR_EIGHT,
    'six_eight': SIX_EIGHT,
    'nine_eight': NINE_EIGHT,
    'twelve_eight': TWELVE_EIGHT
}
