import pat_util
import chords
import config
import ks
import parts
import rhythm
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
    pattern = __read_midi(constants.EXAMPLES + 'simple.mid')
    soprano = domain.Sequence(pattern[0])

    config.time_signatures = soprano.time_signatures

    key_signatures = ks.KeySignatures()
    key_signatures.set().measure(0).commit('C')

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

    __set_config(soprano, chord_progression, key_signatures, config.time_signatures)


def key_changes():
    pattern = __read_midi(constants.EXAMPLES + 'key_changes.mid')
    soprano = domain.Sequence(pattern[0])

    time_signatures = soprano.time_signatures

    key_signatures = ks.KeySignatures()
    key_signatures.set().measure(0).commit('C')
    key_signatures.set().measure(0).beat(2).commit('Eb')
    key_signatures.set().measure(2).commit('G')
    key_signatures.set().measure(3).commit('A')

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

    __set_config(soprano, chord_progression, key_signatures, time_signatures)


def time_changes():
    return 1


def two_four():
    pattern = __read_midi(constants.EXAMPLES + 'two_four.mid')
    soprano = domain.Sequence(pattern[0])

    time_signatures = rhythm.TimeSignatures()
    time_signatures[0] = midi.TimeSignatureEvent(tick=0, data=[2, 2, 36, 8])

    key_signatures = ks.KeySignatures()
    key_signatures.set().measure(0).commit('C')

    chord_progression = chords.ChordProgression()
    chord_progression.set().measure(0).beat(0).commit('C')
    chord_progression.set().measure(2).beat(0).commit('G')
    chord_progression.set().measure(3).beat(0).commit('C')
    chord_progression.set().measure(4).beat(0).commit('D-')
    chord_progression.set().measure(4).beat(1).commit('G7')
    chord_progression.set().measure(5).beat(0).commit('A-')
    chord_progression.set().measure(6).beat(0).commit('F')
    chord_progression.set().measure(7).beat(0).commit('G')

    __set_config(soprano, chord_progression, key_signatures, time_signatures)


def three_four():
    pattern = __read_midi(constants.EXAMPLES + 'three_four.mid')
    soprano = domain.Sequence(pattern[0])

    time_signatures = rhythm.TimeSignatures()
    time_signatures[0] = midi.TimeSignatureEvent(tick=0, data=[3, 2, 36, 8])

    key_signatures = ks.KeySignatures()
    key_signatures.set().measure(0).commit('C-')

    chord_progression = chords.ChordProgression()
    chord_progression.set().measure(0).beat(0).commit('C-')
    chord_progression.set().measure(1).beat(0).commit('Eb')
    chord_progression.set().measure(2).beat(0).commit('Ab')
    chord_progression.set().measure(3).beat(0).commit('G7')
    chord_progression.set().measure(3).beat(2).commit('C-')

    __set_config(soprano, chord_progression, key_signatures, time_signatures)


def six_four():
    pattern = __read_midi(constants.EXAMPLES + 'six_four.mid')
    soprano = domain.Sequence(pattern[0])

    time_signatures = rhythm.TimeSignatures()
    time_signatures[0] = midi.TimeSignatureEvent(tick=0, data=[6, 2, 36, 8])

    key_signatures = ks.KeySignatures()
    key_signatures.set().measure(0).commit('C-')

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

    __set_config(soprano, chord_progression, key_signatures, time_signatures)


def four_eight():
    pattern = __read_midi(constants.EXAMPLES + 'four_eight.mid')

    soprano = domain.Sequence(pattern[0])

    time_signatures = rhythm.TimeSignatures()
    time_signatures[0] = midi.TimeSignatureEvent(tick=0, data=[4, 3, 36, 8])
    soprano.time_signatures = time_signatures

    key_signatures = ks.KeySignatures()
    key_signatures.set().measure(0).commit('F')

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

    __set_config(soprano, chord_progression, key_signatures, time_signatures)


def six_eight():
    pattern = __read_midi(constants.EXAMPLES + 'six_eight.mid')
    pattern = pat_util.scale_tick_values(pattern, 16, config.resolution)

    soprano = domain.Sequence(pattern[0])

    time_signatures = rhythm.TimeSignatures()
    time_signatures[0] = midi.TimeSignatureEvent(tick=0, data=[6, 3, 36, 8])
    soprano.time_signatures = time_signatures

    key_signatures = ks.KeySignatures()
    key_signatures.set().measure(0).commit('C-')

    chord_progression = chords.ChordProgression()
    chord_progression.set().measure(0).beat(0).commit('C-')
    chord_progression.set().measure(0).beat(3).commit('Ab')
    chord_progression.set().measure(1).beat(0).commit('Abdim')
    chord_progression.set().measure(1).beat(3).commit('G7')
    chord_progression.set().measure(1).beat(5).commit('Bb7')
    chord_progression.set().measure(2).beat(0).commit('Eb')
    chord_progression.set().measure(2).beat(3).commit('F-')
    chord_progression.set().measure(3).beat(0).commit('G7')

    __set_config(soprano, chord_progression, key_signatures, time_signatures)


def nine_eight():
    pattern = __read_midi(constants.EXAMPLES + 'nine_eight.mid')
    pattern = pat_util.scale_tick_values(pattern, 36, config.resolution * 3)

    soprano = domain.Sequence(pattern[0])

    time_signatures = rhythm.TimeSignatures()
    time_signatures[0] = midi.TimeSignatureEvent(tick=0, data=[9, 3, 36, 8])
    soprano.time_signatures = time_signatures

    key_signatures = ks.KeySignatures()
    key_signatures.set().measure(0).commit('G')

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

    __set_config(soprano, chord_progression, key_signatures, time_signatures)


def twelve_eight():
    return 1

def __bach():
    pattern = __read_midi(constants.EXAMPLES + 'bach.mid')
    soprano = domain.Sequence(pattern[0])

    time_signatures = rhythm.TimeSignatures()
    time_signatures[0] = midi.TimeSignatureEvent(tick=0, data=[3, 2, 36, 8])

    key_signatures = ks.KeySignatures()
    key_signatures.set().measure(0).commit('G')

    chord_progression = chords.ChordProgression()
    chord_progression.set().measure(0).beat(0).commit('C-')
    chord_progression.set().measure(1).beat(0).commit('Eb')
    chord_progression.set().measure(2).beat(0).commit('Ab')
    chord_progression.set().measure(3).beat(0).commit('G7')
    chord_progression.set().measure(3).beat(2).commit('C-')

    __set_config(soprano, chord_progression, key_signatures, time_signatures)


def __set_config(soprano, chord_progression, key_signatures, time_signatures):
    config.resolution = 96
    config.soprano = soprano
    config.alto = domain.Sequence(seed=soprano, part=parts.ALTO, configuration={})
    config.tenor = domain.Sequence(seed=soprano, part=parts.TENOR, configuration={})
    config.bass = domain.Sequence(seed=soprano, part=parts.BASS,
                                  configuration={'motion_tendency': 0.3})
    config.chord_progression = chord_progression
    config.key_signatures = key_signatures
    config.time_signatures = time_signatures


def load(name):
    config.name = name
    ALL.get(name, None)()


ALL = {
    'simple': simple,
    'key_changes': key_changes,
    'time_changes': time_changes,
    'two_four': two_four,
    'three_four': three_four,
    'six_four': six_four,
    'four_eight': four_eight,
    'six_eight': six_eight,
    'nine_eight': nine_eight,
    'twelve_eight': twelve_eight
}
