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
import ks
import motion
import note_picker
import constants
import parts
import config
import examples
import songloader

# ~~~~~~~~ verify command line arguments ~~~~~~~~
midi_regex = re.compile('.+\.(midi|mid)')

if len(sys.argv) < 2:
    print 'Usage: cybach.py {<midi_file_name>|examples}'
    exit(2)

if sys.argv[1] == 'examples':
    print 'Valid example names:'
    for key in examples.ALL:
        print key
    exit(1)

if not re.match(midi_regex, sys.argv[1]) and sys.argv[1] not in examples.ALL:
    print 'Must supply a valid midi file or example name.'
    print 'To find example names, run cybach.py examples'
    print 'Midi file example: python cybach.py simple.mid'
    exit(2)

if re.match(midi_regex, sys.argv[1]) and not os.path.isfile(sys.argv[1]):
    print 'File or example ' + sys.argv[1] + ' does not exist'
    exit(2)

# ~~~~~~~~ load midi and initialize parts ~~~~~~~~
songloader.load(sys.argv[1])

# ~~~~~~~~ Write simple accompaniment, using only notes equal to time signature denominators ~~~~~~~~
# ~~~~~~~~ (quarter notes for 4/4, eights for 6/8) ~~~~~~~~

picker = note_picker.NotePicker()
for measure in config.bass.measures():
    for beat in measure.beats():
        position = measure.sample_position() + beat.beat_index * config.resolution
        pitches = picker.compute_next()

        config.bass.set_beat_at_position(position, pitches['bass'])
        config.tenor.set_beat_at_position(position, pitches['tenor'])
        config.alto.set_beat_at_position(position, pitches['alto'])

# ~~~~~~~~ Increase or decrease motion by grouping notes together or adding inter-beat motion ~~~~~~~~

motionizer = motion.Motionizer()
for measure in config.bass.measures():
    for beat in measure.beats():
        position = measure.sample_position() + beat.beat_index * config.resolution

        transforms = motionizer.compute_next(config.soprano, config.alto, config.tenor, config.bass)

        config.alto.apply_transform(transforms['alto'])
        config.tenor.apply_transform(transforms['tenor'])
        config.bass.apply_transform(transforms['bass'])

# ~~~~~~~~ Write to file ~~~~~~~~
folder = constants.OUT_DIR + config.name + '/'
if not os.path.exists(folder):
    os.makedirs(folder)

midi.write_midifile(folder + 'soprano.mid', config.soprano.to_pattern())
midi.write_midifile(folder + 'alto.mid', config.alto.to_pattern())
midi.write_midifile(folder + 'tenor.mid', config.tenor.to_pattern())
midi.write_midifile(folder + 'bass.mid', config.bass.to_pattern())

print 'Your arrangement has been written to ', folder, ' :)'
