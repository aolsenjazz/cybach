#!/usr/bin/env python
"""
Utility methods for dealing with midi.Pattern objects
"""

from __future__ import division
from constants import *
import midi


def scale_tick_values(pattern, current_duration, correct_duration):
    scale_ratio = correct_duration / current_duration

    for event in pattern[0]:
        event.tick = int(event.tick * scale_ratio)

    return pattern


def normalize_resolution(pattern):
    """
    Reduces the resolution from > 24 to 24. Simply easier to manipulate at lower resolution.
    :param pattern: pattern retrieved from parsing midi track
    :return: Pattern object with resolution = 24
    """
    if pattern.resolution == RESOLUTION:
        return pattern

    track = pattern[0]
    ratio = RESOLUTION / pattern.resolution

    for event in track:
        event.tick = int(event.tick * ratio)

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

        for value in ACCEPTABLE_NOTE_VALUES:
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

    for event in pattern[0]:
        if isinstance(event, midi.NoteOnEvent):
            active_pitches.append(event.data[0])
        elif isinstance(event, midi.NoteOffEvent):
            if event.tick > 0 and len(active_pitches) > 1:
                return True

            active_pitches.remove(event.data[0])

        if isinstance(event, midi.NoteOnEvent) and len(active_pitches) > 1:
            if event.tick > 0:
                return True

    return False


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
