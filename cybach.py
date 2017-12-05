#!/usr/bin/env python
"""
CYBACH
"""

import sys
import re
import midi
import os.path
import track_util
import pat_util
from constants import *
from domain import *
import instruments

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
alto = None
tenor = None
bass = None
chords = {}
key_signatures = {}

# Set instruments
instrument_alto = None
while instrument_alto is None:
    instrument_alto = instruments.parse(raw_input('Enter alto instrument: '))

instrument_tenor = None
while instrument_tenor is None:
    instrument_tenor = instruments.parse(raw_input('Enter tenor instrument: '))

instrument_bass = None
while instrument_bass is None:
    instrument_bass = instruments.parse(raw_input('Enter bass instrument: '))

# Verify that MIDI was parsed correctly
correct = raw_input('It looks like the composition has %d measures. Is this correct? y/n ' % len(soprano.measures()))
while not (correct == 'y' or correct == 'n'):
    correct = raw_input(
        'It looks like the composition has %d measures. Is this correct? y/n ' % len(soprano.measures()))

if correct == 'n':
    print 'Failed to correctly parse midi'
    exit(1)

# enter time signatures
enter = 'y'
while enter == 'y':
    enter = raw_input('Would you like to insert a time signature? y/n ')

    if enter == 'y':
        numerator = int(raw_input('Signature numerator: '))
        denominator = int(raw_input('Signature denominator: '))
        measure = int(raw_input('Measure: '))

        event = midi.TimeSignatureEvent(data=[numerator, denominator, 36, 8])
        soprano.time_signatures[soprano.measure(measure - 1).beat_value() * RESOLUTION] = event

time_sigs_to_delete = []
# manual time signature entry
for key in soprano.time_signatures:
    signature = soprano.time_signatures[key]
    delete = raw_input('Would you like to delete the %d/%d at beat %d? y/n '
                       % (signature.numerator, signature.denominator, key))

    if delete == 'y':
        time_sigs_to_delete.append(key)
for sig in time_sigs_to_delete:
    del soprano.time_signatures[sig]

# enter key signatures
enter = 'y'
while enter == 'y':
    enter = raw_input('Would you like to insert a key signature? y/n ')

    if enter == 'y':
        signature = raw_input('Enter key: ')
        measure = int(raw_input('Enter measure number: '))

        key_signatures[soprano.measure(measure - 1).beat_value() * RESOLUTION] = signature

print key_signatures
# enter chords
enter = 'y'
while enter == 'y':
    enter = raw_input('Would you like to enter a chord? y/n ')

    if enter == 'y':
        chord = raw_input('Enter chord: ')
        measure = int(raw_input('Enter measure number: '))
        beat = int(raw_input('Enter beat number: '))

        chords[soprano.measure(measure - 1).beat_value + (beat - 1) * RESOLUTION] = chord
