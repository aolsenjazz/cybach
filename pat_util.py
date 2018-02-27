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
    """
    Returns a map of time signature events and their position in the first track

    :param pattern: midi.Pattern
    :return: Map of time sig events, eg {0: time.TimeSignature, 384: time.TimeSignature}
    """
    time_signature_events = {}

    position = 0
    for event in pattern[0]:
        position += event.tick
        if isinstance(event, midi.TimeSignatureEvent):
            time_signature_events[position] = event

    return time_signature_events


def contains_time_signature_data(pattern):
    """
    Returns True if the first track of the pattern contains at least one time signature event.

    :param pattern: midi.Pattern
    :return: True or False
    """
    for event in pattern[0]:
        if isinstance(event, midi.TimeSignatureEvent):
            return True
    return False


def contains_key_signature_data(pattern):
    """
    Returns True if the first track of the pattern contains at least one key signature event

    :param pattern: midi.Pattern
    :return: True or False
    """
    for event in pattern[0]:
        if isinstance(event, midi.KeySignatureEvent):
            return True
    return False


def sample_length(pattern):
    """
    Returns the sample length of the first track of the Pattern

    :param pattern: midi.Pattern
    :return: Length of the first track of the pattern
    """
    if isinstance(pattern, midi.Track):
        track = pattern
    elif isinstance(pattern, midi.Pattern):
        track = pattern[0]
    elif isinstance(pattern, list):
        track = pattern
    else:
        raise ValueError
    return sum([event.tick for event in track])


def sorted_note_events(pattern):
    """
    Some patterns have gnarly ordering of NoteOn and NoteOff event, which, while valid, are a pain in the
    ass to parse. Correct it here.

    :param pattern: midi.Pattern
    """
    track = [e for e in pattern[0] if isinstance(e, midi.NoteOnEvent) or isinstance(e, midi.NoteOffEvent)]

    sort_again = True
    while sort_again:
        sort_again = False

        swap = [i for i, (current, last)
                in enumerate(zip(track, track[1:]))
                if __are_note_on_events(current, last) and current.__class__ == last.__class__]

        for i in swap:
            track[i + 2].tick, track[i + 1].tick = track[i + 1].tick, track[i + 2].tick
            track[i + 2], track[i + 1] = track[i + 1], track[i + 2]
            sort_again = True

    return track


def __are_note_on_events(*args):
    """
    Convenience method to check if object is a midi.NoteOnEvent
    :param args: series of Objects
    :return: True or False
    """
    for item in args:
        if isinstance(item, midi.NoteOnEvent):
            return True

    return False