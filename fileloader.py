import re

import midi

import chords
import config
import domain
import examples
import ks_detector
import parts
import pat_util
import phrasing
from rhythm import time

REGEX_MIDI = re.compile('.+\.(mid|midi)')
REGEX_MUSIC_XML = re.compile('.+\\\.(musicxml|xml)')


def load(file_name, manual_signature_entry):
    """
    Tries to load the file specified, and initializes manual time+key signature entry if required. If the file type
    specified isn't supported, complains and exits.

    :param file_name: name of the file we're trying to parse
    :param manual_signature_entry: should we make the client manually enter time+key signature data?
    """
    if file_name in examples.ALL.keys():
        __load_example(file_name)
    elif REGEX_MIDI.match(file_name):
        __load_midi(file_name)
    else:
        print 'Unsupported file type provided'
        exit(1)

    if manual_signature_entry:
        __init_manual_signature_entry()
        ks_detector.detect_and_set_key_signatures()
        phrasing.detect_and_set_measure_phrasing()

    config.name = file_name


def __load_example(file_name):
    """
    Effectively a wrapper around __load_midi, but gets the file name for the example from examples.py first.

    :param file_name: name of the example
    """
    example = examples.ALL.get(file_name)
    __load_midi(example.file_name())
    config.chord_progression = example.chord_progression()
    ks_detector.detect_and_set_key_signatures()
    phrasing.detect_and_set_measure_phrasing()


def __load_midi(file_name):
    """
    Loads the melodic information, resolution, and time signature data into config. Also initialize individual tracks.

    :param file_name: name of the MIDI file
    """
    try:
        pattern = midi.read_midifile(file_name)
        __enforce_midi_validity(pattern)
        config.resolution = pattern.resolution

        config.soprano = domain.RootSequence(pattern[0])
        config.alto = domain.AccompanimentSequence(config.soprano, parts.ALTO)
        config.tenor = domain.AccompanimentSequence(config.soprano, parts.TENOR)
        config.bass = domain.AccompanimentSequence(config.soprano, parts.BASS)

        __load_time_signature_events(pattern)

        config.chord_progression = chords.ChordProgression()
    except TypeError:
        print 'Midi file is malformed. Try exporting a new one from any DAW'
        exit(2)


def __load_music_xml(file_name):
    print 'Music XML is not currently supported but will be soon.'
    exit(1)


# region manual data entry


def __init_manual_signature_entry():
    __init_time_signature_entry(sequence)
    while not __verify_measure_count(sequence):
        __init_time_signature_entry(sequence)

    __init_key_signature_entry(sequence, pattern)


def __init_key_signature_entry(sequence, pattern):
    if pat_util.contains_key_signature_data(pattern):
        __report_key_signature_data(pattern)
        __manual_delete_key_signatures(pattern)

    return __manual_create_key_signatures(sequence)


def __init_time_signature_entry(sequence):
    time_signatures = time.__signatures

    if time_signatures:
        __report_time_signature_data()
        __manual_delete_time_signatures()

    enter = 'y'
    while enter == 'y':
        enter = raw_input('Would you like to insert a time signature? y/n ')

        if enter == 'y':
            numerator = int(raw_input('Signature numerator: '))
            denominator = int(raw_input('Signature denominator: '))
            measure = int(raw_input('Measure: '))

            event = midi.TimeSignatureEvent(data=[numerator, denominator, 36, 8])
            time.__signatures[sequence.measure(measure - 1).start()] = event


def __verify_measure_count(sequence):
    measure_count = len(sequence.measures())

    correct = raw_input('It looks like the midi has %d measures. Is this correct? y/n ' % measure_count)
    while not (correct == 'y' or correct == 'n'):
        correct = raw_input('It looks like the midi has %d measures. Is this correct? y/n ' % measure_count)

    return False if correct == 'n' else True


def __report_time_signature_data():
    print 'Midi clip has the following time signature data:'
    for key in time_signatures:
        print time_signatures[key].numerator, '/', time_signatures[key].denominator, \
            ' at beat ', key / config.resolution


def __manual_delete_time_signatures():
    time_sigs_to_delete = []

    for key in copy:
        signature = copy[key]
        delete = raw_input('Would you like to delete the %d/%d at beat %d? y/n '
                           % (signature.numerator, signature.denominator, key))

        if delete == 'y':
            time_sigs_to_delete.append(key)

    for sig in time_sigs_to_delete:
        del time_signatures[sig]


def __manual_delete_key_signatures(sequence):
    key_sigs_to_delete = []

    for key in key_signatures:
        signature = key_signatures[key]
        delete = raw_input('Would you like to delete the %s key signature at beat %d? y/n '
                           % (signature, key))

        if delete == 'y':
            key_sigs_to_delete.append(key)
    for sig in key_sigs_to_delete:
        del time_signatures[sig]


def __manual_create_key_signatures(sequence):
    key_signatures = sequence.key_signatures

    enter = 'y'
    while enter == 'y':
        enter = raw_input('Would you like to insert a key signature? y/n ')

        if enter == 'y':
            signature = raw_input('Enter key: ')
            measure = int(raw_input('Enter measure number: '))

            key_signatures[sequence.measure(measure - 1).start()] = signature

    return key_signatures


def __report_key_signature_data(item):
    print 'Midi clip has the following key signature data:'


def __manual_enter_chords(sequence):
    chord_progression = chords.ChordProgression()

    enter = 'y'
    while enter == 'y':
        enter = raw_input('Would you like to enter a chord? y/n ')

        if enter == 'y':
            chord = chords.parse(raw_input('Enter chord: '))
            measure = int(raw_input('Enter measure number: '))
            beat = int(raw_input('Enter beat number: '))

            chord_progression[sequence.measure(measure - 1).start() + (beat - 1) * config.resolution] = chord

    return chord_progression


def __offer_part_customization():
    enter = None
    while enter != 'y' and enter != 'n':
        enter = raw_input('Would you like to configure individual parts (alto, tenor bass)? y/n ')

        if enter == 'y':
            print 'Currently configuring alto...'
            alto_configuration = __configure_part()

            print 'Currently configuring tenor...'
            tenor_configuration = __configure_part()

            print 'Currently configuring bass...'
            bass_configuration = __configure_part()

            return {
                'alto': alto_configuration,
                'tenor': tenor_configuration,
                'bass': bass_configuration
            }

    return {}


# endregion


def __load_time_signature_events(pattern):
    """
    Loads time signature data into the config file.

    :param pattern: pattern retrieved by parsing MIDI
    """
    time.clear()
    events = pat_util.get_time_signature_events(pattern)
    for key in events.keys():
        time.add_signature(key, time.TimeSignature(event=events[key]))


def __enforce_midi_validity(pattern):
    """
    Checks for disallowed characteristics of MIDI and exits if characteristic exists.

    :param pattern: pattern retrieved by parsing MIDI
    """
    if len(pattern) > 1:
        print 'CyBach doesn\'t support multitrack midi files'
        exit(2)

    if not pat_util.is_quantized(pattern):
        print 'Midi file is not quantized. Cybach only operates on quantized midi'
        exit(2)

    if pat_util.contains_harmony(pattern):
        print 'Midi file contains harmony. Cybach only supports single lines from input midi'
        exit(2)
