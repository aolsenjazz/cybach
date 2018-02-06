import re
import config
import examples
import pat_util
import domain
import constants
import chords
import midi

midi_regex = re.compile('.+\.(midi|mid)')


def load(example_or_file):
    if re.match(midi_regex, example_or_file):
        __load_file(example_or_file)
    else:
        examples.load(example_or_file)


def __load_file(file_name):
    pattern = __read_midi(file_name)
    pattern = __enforce_midi_validity(file_name, pattern)
    sequence = domain.Sequence(pattern[0])

    __set_time_signatures(sequence)
    __verify_measure_count(sequence, pattern)
    __set_key_signatures(sequence, pattern)
    __offer_enter_chords(sequence)

    part_customization = __offer_part_customization()

    return config.Arrangement(file_name, sequence, part_customization)


def __set_key_signatures(sequence, pattern):
    if pat_util.contains_key_signature_data(pattern):
        __report_key_signature_data(pattern)
        __offer_delete_key_signatures(pattern)

    __offer_create_key_signatures(sequence)


def __set_time_signatures(sequence):
    time_signatures = sequence.time_signatures

    if time_signatures:
        __report_time_signature_data()
        __offer_delete_time_signatures()

    __offer_create_time_signatures(sequence)


def __read_midi(file_name):
    try:
        return midi.read_midifile(file_name)
    except TypeError:
        print 'Midi file is malformed. Try exporting a new one from any DAW'
        exit(2)


def __enforce_midi_validity(file_name, pattern):
    if len(pattern) > 1:
        print 'CyBach doesn\'t support multitrack midi files'
        exit(2)

    if not pat_util.is_quantized(pattern):
        print 'Midi file is not quantized. Cybach only operates on quantized midi'
        exit(2)

    if pat_util.contains_harmony(pattern):
        print file_name, ' contains harmony. Cybach only supports single lines from input midi'
        exit(2)

    return pattern


def __verify_measure_count(sequence, pattern):
    measure_count = len(sequence.measures())

    correct = raw_input('It looks like the midi has %d measures. Is this correct? y/n ' % measure_count)
    while not (correct == 'y' or correct == 'n'):
        correct = raw_input('It looks like the midi has %d measures. Is this correct? y/n ' % measure_count)

    correct = False if correct == 'n' else True

    if not correct:
        pattern = __correct_midi_time_scale(pattern)
        sequence = domain.Sequence(pattern[0])

        print 'We need to readjust time signatures now.'

        __set_time_signatures(sequence)


def __correct_midi_time_scale(pattern):
    """
    It's very possible that the midi clip submitted is scaled incorrectly. E.g. a midi clip made + exported
    from Ableton used the triplet grid, and the user assumed that because of this, one beat, would be equal to
    one triplet. This almost definitely won't be the case until Ableton updates it because it appears that
    all Ableton clips are exported as 4/4
    :param pattern: Pattern
    :param time_signatures: Time signatures
    :return: pattern with updated tick values
    """
    note_type = __get_first_note_type(pattern, time_signatures)
    correct = 'a'

    print 'It appears that there\'s a mixup in the duration of notes.'
    print 'To me, it looks like the first note is a ', note_type, '.'

    while correct != 'n' and correct != 'y':
        correct = raw_input('Is this correct? (y/n) ')

        if correct == 'y':
            print 'Proceeding despite having a suspected mix-up.'

        if correct == 'n':
            duration = 'incorrect, irrelevant value for now'

            while duration not in note_durations:
                duration = raw_input('What is the first non-rest note duration? ')

                if duration not in note_durations:
                    print 'Unrecognized duration. You can enter the following durations: '
                    print constants.TEXT_DURATION_MAP.keys()
                else:
                    parsed = duration.lower().strip(' \t\n\r').replace(' ', '_')
                    int_val = constants.TEXT_DURATION_MAP[parsed]

                    return pat_util.scale_tick_values(pattern, __get_first_note_tick(pattern), int_val)

    return pattern


def __report_time_signature_data():
    print 'Midi clip has the following time signature data:'
    for key in time_signatures:
        print time_signatures[key].numerator, '/', time_signatures[key].denominator, \
            ' at beat ', key / config.resolution


def __offer_delete_time_signatures():
    time_sigs_to_delete = []

    for key in copy:
        signature = copy[key]
        delete = raw_input('Would you like to delete the %d/%d at beat %d? y/n '
                           % (signature.numerator, signature.denominator, key))

        if delete == 'y':
            time_sigs_to_delete.append(key)
    for sig in time_sigs_to_delete:
        del time_signatures[sig]


def __offer_create_time_signatures(sequence):
    enter = 'y'
    while enter == 'y':
        enter = raw_input('Would you like to insert a time signature? y/n ')

        if enter == 'y':
            numerator = int(raw_input('Signature numerator: '))
            denominator = int(raw_input('Signature denominator: '))
            measure = int(raw_input('Measure: '))

            event = midi.TimeSignatureEvent(data=[numerator, denominator, 36, 8])
            time_signatures[sequence.measure(measure - 1).sample_position()] = event


def __offer_delete_key_signatures(sequence):
    key_sigs_to_delete = []

    for key in key_signatures:
        signature = key_signatures[key]
        delete = raw_input('Would you like to delete the %s key signature at beat %d? y/n '
                           % (signature, key))

        if delete == 'y':
            key_sigs_to_delete.append(key)
    for sig in key_sigs_to_delete:
        del time_signatures[sig]


def __offer_create_key_signatures(sequence):
    enter = 'y'
    while enter == 'y':
        enter = raw_input('Would you like to insert a key signature? y/n ')

        if enter == 'y':
            signature = raw_input('Enter key: ')
            measure = int(raw_input('Enter measure number: '))

            global key_signatures
            key_signatures[sequence.measure(measure - 1).sample_position()] = signature


def __report_key_signature_data(item):
    print 'Midi clip has the following key signature data:'


def __offer_create_chords(sequence):
    chord_progression = chords.ChordProgression()

    enter = 'y'
    while enter == 'y':
        enter = raw_input('Would you like to enter a chord? y/n ')

        if enter == 'y':
            chord = chords.parse(raw_input('Enter chord: '))
            measure = int(raw_input('Enter measure number: '))
            beat = int(raw_input('Enter beat number: '))

            chord_progression[sequence.measure(measure - 1).sample_position() + (beat - 1) * config.resolution] = chord

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


def __configure_part():
    motion_tendency = raw_input('MOTION TENDENCY || Enter a value between 0.0 and 1.0 (default 0.5): ')

    return {
        'motion_tendency': float(motion_tendency)
    }


def __get_first_note_tick(pattern):
    for event in pattern[0]:
        if isinstance(event, midi.NoteOffEvent):
            return event.tick


def __get_first_note_type(pattern, time_signatures):
    first_signature = time_signatures[0]
    ratio_to_signature_over_four = 4 / first_signature.denominator
    first_note_duration = __get_first_note_tick(pattern)

    scaled = first_note_duration * ratio_to_signature_over_four

    return constants.INT_DURATION_MAP[scaled]
