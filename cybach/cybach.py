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
import parts
import examples
import songloader
from domain import RESOLUTION

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
song = songloader.load(sys.argv[1])

# ~~~~~~~~ Write simple accompaniment, using only notes equal to time signature denominators ~~~~~~~~
# ~~~~~~~~ (quarter notes for 4/4, eights for 6/8) ~~~~~~~~

picker = note_picker.NotePicker(song.soprano, song.alto, song.tenor, song.bass,
                                song.key_signatures, song.chord_progression)
for measure in song.bass.measures():
    for beat in measure.beats():
        position = measure.sample_position() + beat.beat_index * RESOLUTION
        pitches = picker.compute_next()

        song.bass.set_beat_at_position(position, pitches[0])
        song.tenor.set_beat_at_position(position, pitches[1])
        song.alto.set_beat_at_position(position, pitches[2])

# ~~~~~~~~ Increase or decrease motion by grouping notes together or adding inter-beat motion ~~~~~~~~

motionizer = motion.Motionizer(song.key_signatures, song.chord_progression)
for measure in song.bass.measures():
    for beat in measure.beats():
        position = measure.sample_position() + beat.beat_index * RESOLUTION

        transforms = motionizer.compute_next(song.soprano, song.alto, song.tenor, song.bass)

        song.alto.apply_transform(transforms[0])
        song.tenor.apply_transform(transforms[1])
        song.bass.apply_transform(transforms[2])

# ~~~~~~~~ Write to file ~~~~~~~~
folder = 'out/' + song.name + '/'
if not os.path.exists(folder):
    os.makedirs(folder)

midi.write_midifile(folder + 'soprano.mid', song.soprano.to_pattern())
midi.write_midifile(folder + 'alto.mid', song.alto.to_pattern())
midi.write_midifile(folder + 'tenor.mid', song.tenor.to_pattern())
midi.write_midifile(folder + 'bass.mid', song.bass.to_pattern())

print 'Your arrangement has been written to ', folder, ' :)'
