import re

import midi

import chords
import config
import domain
import pat_util
import rhythm

REGEX_MIDI = re.compile('.+\.(mid|midi)')
REGEX_MUSIC_XML = re.compile('.+\\\.(musicxml|xml)')


def load_file(file_name):
    if REGEX_MIDI.match(file_name):
        __load_midi(file_name)
    elif REGEX_MUSIC_XML.match(file_name):
        __load_music_xml(file_name)


def __load_midi(file_name):
    try:
        pattern = midi.read_midifile(file_name)
        config.resolution = pattern.resolution
        __load_time_signature_events(pattern)
        config.soprano = domain.Sequence(track=pattern[0])
        config.chord_progression = chords.ChordProgression()
    except TypeError:
        print 'Midi file is malformed. Try exporting a new one from any DAW'
        exit(2)


def __load_music_xml(file_name):
    print 'Music XML is not currently supported but will be soon.'
    exit(1)


def __load_time_signature_events(pattern):
    config.time_signatures = rhythm.TimeSignatures()
    events = pat_util.get_time_signature_events(pattern)
    for key in events.keys():
        config.time_signatures[key] = rhythm.TimeSignature(event=events[key])
