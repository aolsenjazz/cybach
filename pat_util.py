#!/usr/bin/env python
"""
Utility methods for dealing with midi.Pattern objects
"""

from __future__ import division

import midi
import constants


def scale_tick_values(pattern, current_duration, correct_duration):
    scale_ratio = correct_duration / current_duration

    for event in pattern[0]:
        event.tick = int(event.tick * scale_ratio)

    return pattern


def is_quantized(pattern):
    """
    Midi data should be quantized so that we don't have any 32.5nd notes. Also guarantees that we don't have
    any notes that are smaller than our tolerated resolution (32nd note triplets)
    :param pattern: pattern
    :return: True if all of the midi data fits within our grid
    """
    track = pattern[0]

    for event in track:
        duration = event.tick

        for value in constants.ACCEPTABLE_NOTE_VALUES:
            if duration % value == 0:
                return True

    return False


def contains_harmony(pattern):
    """
    Processing midi files that contain harmony would be a pain in the butt. Maybe implement this later.
    :param pattern: pattern
    :return: True if two midi notes are active at once at any point during the clip
    """
    active_pitches = []
    relevant_events = [e for e in pattern[0] if isinstance(e, midi.NoteOnEvent) or isinstance(e, midi.NoteOffEvent)]

    i = 0
    for event in relevant_events:
        i += 1 # position of next event

        if isinstance(event, midi.NoteOnEvent):
            active_pitches.append(event.data[0])
        elif isinstance(event, midi.NoteOffEvent):
            if event.tick > 0 and len(active_pitches) > 1:
                return True

            active_pitches.remove(event.data[0])

        if isinstance(event, midi.NoteOnEvent) and len(active_pitches) > 1:
            if event.tick > 0 and not isinstance(relevant_events[i], midi.NoteOffEvent):
                return True

    return False


def get_time_signature_events(pattern):
    time_signature_events = {}

    position = 0
    for event in pattern[0]:
        position += event.tick
        if isinstance(event, midi.TimeSignatureEvent):
            time_signature_events[position] = event

    return time_signature_events


def contains_time_signature_data(pattern):
    for event in pattern[0]:
        if isinstance(event, midi.TimeSignatureEvent):
            return True
    return False


def contains_key_signature_data(pattern):
    for event in pattern[0]:
        if isinstance(event, midi.KeySignature_Event):
            return True
    return False
