import pat_util
import chords
import song
import ks
import ts
import midi
import domain


def __read_midi(file_name):
    try:
        return midi.read_midifile(file_name)
    except TypeError:
        print 'Midi file is malformed. Try exporting a new one from any DAW'
        exit(2)


def simple():
    pattern = pat_util.normalize_resolution(__read_midi('examples/simple.mid'))
    soprano = domain.Sequence(pattern[0])

    time_signatures = soprano.time_signatures

    key_signatures = ks.KeySignatures()
    key_signatures[0] = chords.parse('C')

    chord_progression = chords.ChordProgression()
    chord_progression[0] = chords.parse('C')
    chord_progression[(0 * 96) + (2 * 24)] = chords.parse('A-')
    chord_progression[(1 * 96) + (0 * 24)] = chords.parse('E-')
    chord_progression[(1 * 96) + (1 * 24)] = chords.parse('F')
    chord_progression[(1 * 96) + (2 * 24)] = chords.parse('G')
    chord_progression[(2 * 96) + (0 * 24)] = chords.parse('A-')
    chord_progression[(2 * 96) + (2 * 24)] = chords.parse('C')
    chord_progression[(3 * 96) + (2 * 24)] = chords.parse('G')
    chord_progression[(3 * 96) + (3 * 24)] = chords.parse('E7')

    return song.Song('simple', soprano, time_signatures, key_signatures, chord_progression, {})


def key_changes():
    return 1


def time_changes():
    return 1


def two_four():
    return 1


def three_four():
    pattern = pat_util.normalize_resolution(__read_midi('examples/three_four.mid'))
    soprano = domain.Sequence(pattern[0])

    time_signatures = ts.TimeSignatures()
    time_signatures[0] = midi.TimeSignatureEvent(tick=0, data=[3, 2, 36, 8])

    key_signatures = ks.KeySignatures()
    key_signatures[0] = chords.parse('C-')

    chord_progression = chords.ChordProgression()
    chord_progression[0] = chords.parse('C-')
    chord_progression[(1 * 72) + (0 * 24)] = chords.parse('Eb')
    chord_progression[(2 * 72) + (0 * 24)] = chords.parse('Ab')
    chord_progression[(3 * 72) + (0 * 24)] = chords.parse('G7')
    chord_progression[(3 * 72) + (2 * 24)] = chords.parse('C-')

    return song.Song('three_four', soprano, time_signatures, key_signatures, chord_progression, {})


def six_four():
    return 1


def four_eight():
    return 1


def six_eight():
    pattern = pat_util.normalize_resolution(__read_midi('examples/six_eight.mid'))
    pattern = pat_util.scale_tick_values(pattern, 16, 24)

    soprano = domain.Sequence(pattern[0])

    time_signatures = ts.TimeSignatures()
    time_signatures[0] = midi.TimeSignatureEvent(tick=0, data=[6, 3, 36, 8])
    soprano.time_signatures = time_signatures

    key_signatures = ks.KeySignatures()
    key_signatures[0] = chords.parse('C-')

    chord_progression = chords.ChordProgression()
    chord_progression[0] = chords.parse('C-')
    chord_progression[(0 * 144) + (3 * 24)] = chords.parse('Ab')
    chord_progression[(1 * 144) + (0 * 24)] = chords.parse('Abdim')
    chord_progression[(1 * 144) + (3 * 24)] = chords.parse('G7')
    chord_progression[(1 * 144) + (5 * 24)] = chords.parse('Bb7')
    chord_progression[(2 * 144) + (0 * 24)] = chords.parse('Eb')
    chord_progression[(2 * 144) + (3 * 24)] = chords.parse('F-')
    chord_progression[(3 * 144) + (0 * 24)] = chords.parse('Abdim')
    chord_progression[(3 * 144) + (3 * 24)] = chords.parse('G7')

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
