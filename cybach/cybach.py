#!/usr/bin/env python
"""
CYBACH
"""

import os.path
import re
import sys

import midi

import chords
import instruments
import pat_util
import track_util
import note_picker
import ks
from notes import Note
from domain import *

# verify command line arguments
midi_regex = re.compile('.+\.(midi|mid)')

if len(sys.argv) < 2:
    print 'Usage: cybach.py <midi_file_name.py>'
    exit(2)

if not re.match(midi_regex, sys.argv[1]):
    print 'Must supply a midi file'
    exit(2)

if not os.path.isfile(sys.argv[1]):
    print 'File ' + sys.argv[1] + ' does not exist'
    exit(2)

# read midi track
pattern = None
track = None

try:
    pattern = midi.read_midifile(sys.argv[1])
except TypeError:
    print 'Midi file is malformed. Try exporting a new one from any DAW'
    exit(2)

# verify resolution, quantization, etc.
if len(pattern) > 1:
    print 'CyBach doesn\'t support multitrack midi files'
    exit(2)

if pat_util.resolution_too_small(pattern):
    print 'Midi file contains notes faster than 32nd note triplets, which Cybach doesn\'t support'
    exit(2)

pattern = pat_util.normalize_resolution(pattern)

if not pat_util.is_quantized(pattern):
    print 'Midi file is not quantized. Cybach only operates on quantized midi'
    exit(2)

if track_util.contains_harmony(pattern[0]):
    print 'Midi file contains harmony. Cybach only supports single lines from input midi'
    exit(2)

# Composition data
soprano = Sequence(pattern[0])
chord_progression = chords.ChordProgression()
key_signatures = ks.KeySignatures()

# # Set instruments
# instrument_alto = None
# while instrument_alto is None:
#     instrument_alto = instruments.parse(raw_input('Enter alto instrument: '))
#
# instrument_tenor = None
# while instrument_tenor is None:
#     instrument_tenor = instruments.parse(raw_input('Enter tenor instrument: '))
#
# instrument_bass = None
# while instrument_bass is None:
#     instrument_bass = instruments.parse(raw_input('Enter bass instrument: '))

# # Verify that MIDI was parsed correctly
# correct = raw_input('It looks like the composition has %d measures. Is this correct? y/n ' % len(soprano.measures()))
# while not (correct == 'y' or correct == 'n'):
#     correct = raw_input(
#         'It looks like the composition has %d measures. Is this correct? y/n ' % len(soprano.measures()))
#
# if correct == 'n':
#     print 'Failed to correctly parse midi'
#     exit(1)
#
# # enter time signatures
# enter = 'y'
# while enter == 'y':
#     enter = raw_input('Would you like to insert a time signature? y/n ')
#
#     if enter == 'y':
#         numerator = int(raw_input('Signature numerator: '))
#         denominator = int(raw_input('Signature denominator: '))
#         measure = int(raw_input('Measure: '))
#
#         event = midi.TimeSignatureEvent(data=[numerator, denominator, 36, 8])
#         soprano.time_signatures[soprano.measure(measure - 1).sample_position()] = event
#
# time_sigs_to_delete = []
# # manual time signature entry
# for key in soprano.time_signatures:
#     signature = soprano.time_signatures[key]
#     delete = raw_input('Would you like to delete the %d/%d at beat %d? y/n '
#                        % (signature.numerator, signature.denominator, key))
#
#     if delete == 'y':
#         time_sigs_to_delete.append(key)
# for sig in time_sigs_to_delete:
#     del soprano.time_signatures[sig]
#
# # enter key signatures
# enter = 'y'
# while enter == 'y':
#     enter = raw_input('Would you like to insert a key signature? y/n ')
#
#     if enter == 'y':
#         signature = raw_input('Enter key: ')
#         measure = int(raw_input('Enter measure number: '))
#
#         key_signatures[soprano.measure(measure - 1).sample_position()] = signature
#
# # enter chords
# enter = 'y'
# while enter == 'y':
#     enter = raw_input('Would you like to enter a chord? y/n ')
#
#     if enter == 'y':
#         chord = chords.parse(raw_input('Enter chord: '))
#         measure = int(raw_input('Enter measure number: '))
#         beat = int(raw_input('Enter beat number: '))
#
#         chord_progression[soprano.measure(measure - 1).sample_position() + (beat - 1) * RESOLUTION] = chord

key_signatures[0] = 'C'
chord_progression[0] = chords.parse('C')
chord_progression[(0 * 96) + (2 * 24)] = chords.parse('A-')
chord_progression[(1 * 96) + (0 * 24)] = chords.parse('E-')
chord_progression[(1 * 96) + (2 * 24)] = chords.parse('G')
chord_progression[(2 * 96) + (0 * 24)] = chords.parse('A-')
chord_progression[(2 * 96) + (2 * 24)] = chords.parse('C')
chord_progression[(3 * 96) + (2 * 24)] = chords.parse('G')
chord_progression[(3 * 96) + (3 * 24)] = chords.parse('C')

instrument_alto = instruments.VIOLA
instrument_tenor = instruments.CELLO
instrument_bass = instruments.BASS

alto = Sequence(sequence=soprano)
tenor = Sequence(sequence=soprano)
bass = Sequence(sequence=soprano)
picker = note_picker.NotePicker(soprano, alto, tenor, bass, key_signatures, chord_progression)

for measure in bass.measures():
    for beat in measure.beats():
        position = measure.sample_position() + beat.beat_index * RESOLUTION

        bass.set_beat_at_position(position, picker.pick_bass(position))
        alto.set_beat_at_position(position, picker.pick_alto(position))
        tenor.set_beat_at_position(position, picker.pick_tenor(position))

midi.write_midifile('alto.mid', alto.to_pattern())
midi.write_midifile('tenor.mid', tenor.to_pattern())
midi.write_midifile('bass.mid', bass.to_pattern())
