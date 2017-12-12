#!/usr/bin/env python
"""
Utility methods for dealing with midi.Pattern objects
"""

from __future__ import division
from constants import *


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


def resolution_too_small(pattern):
    track = pattern[0]

    for event in track:
        if THIRTY_SECOND_NOTE_TRIPLET > event.tick > 0:
            return True

    return False


def is_quantized(pattern):
    track = pattern[0]

    for event in track:
        if 0 < event.tick < RESOLUTION and event.tick not in SUBDIVISIONS:
            print event.tick
            return False

    return True
