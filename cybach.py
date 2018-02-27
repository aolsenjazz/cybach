#!/usr/bin/env python
"""
CYBACH
"""

import os.path
import re
import sys
import midi
from itertools import chain

import examples
import constants
import fileloader
import note_picker
import config
import sequences
from rhythm import time

# ~~~~~~~~ verify command line arguments ~~~~~~~~
midi_regex = re.compile('.+\.(midi|mid)')

if len(sys.argv) < 2:
    print 'Usage: cybach.py {<midi_file_name>|examples}'
    exit(2)

if sys.argv[1] == 'examples':
    print 'Valid example names:'
    for key in examples.ALL.keys():
        print key
    exit(1)

if not re.match(midi_regex, sys.argv[1]) and sys.argv[1] not in examples.ALL.keys():
    print 'Must supply a valid midi file or example name.'
    print 'To find example names, run cybach.py examples'
    print 'Midi file example: python cybach.py simple.mid'
    exit(2)

if re.match(midi_regex, sys.argv[1]) and not os.path.isfile(sys.argv[1]):
    print 'File or example ' + sys.argv[1] + ' does not exist'
    exit(2)

# ~~~~~~~~ load midi and initialize parts ~~~~~~~~
print 'Parsing MIDI and initializing...'
fileloader.load(sys.argv[1], False)

# ~~~~~~~~ Write simple accompaniment, using only notes equal to time signature denominators ~~~~~~~~
# ~~~~~~~~ (quarter notes for 4/4, eights for 6/8) ~~~~~~~~

print 'Selecting initial accompaniment...'
picker = note_picker.NotePicker()
keys = time.measures().keys()
keys.sort()
strong_beats = list(chain.from_iterable([time.measures()[key].strong_beats() for key in keys]))
for beat in strong_beats:
    pitches = picker.compute(beat)

    bass_note = sequences.Note(sequences.bass(), beat.start(), beat.end(), pitches[note_picker.BASS_POSITION])
    tenor_note = sequences.Note(sequences.tenor(), beat.start(), beat.end(), pitches[note_picker.TENOR_POSITION])
    alto_note = sequences.Note(sequences.alto(), beat.start(), beat.end(), pitches[note_picker.ALTO_POSITION])

    sequences.bass().add_entities(bass_note)
    sequences.tenor().add_entities(tenor_note)
    sequences.alto().add_entities(alto_note)

# ~~~~~~~~ Increase or decrease motion by grouping notes together or adding inter-beat motion ~~~~~~~~

# motionizer = motion.Motionizer()
# for measure in sequences.bass().measures():
#     for beat in measure.beats():
#         position = measure.sample_position() + beat.beat_index * config.resolution
#
#         transforms = motionizer.compute_next(sequences.soprano, sequences.alto(), sequences.tenor(), sequences.bass())
#
#         sequences.alto().apply_transform(transforms['alto'])
#         sequences.tenor().apply_transform(transforms['tenor'])
#         sequences.bass().apply_transform(transforms['bass'])

# ~~~~~~~~ Write to file ~~~~~~~~
folder = constants.OUT_DIR + config.name + '/'
if not os.path.exists(folder):
    os.makedirs(folder)

midi.write_midifile(folder + 'soprano.mid', sequences.soprano().to_pattern())
midi.write_midifile(folder + 'alto.mid', sequences.alto().to_pattern())
midi.write_midifile(folder + 'tenor.mid', sequences.tenor().to_pattern())
midi.write_midifile(folder + 'bass.mid', sequences.bass().to_pattern())

print 'Your arrangement has been written to ', folder, ' :)'
