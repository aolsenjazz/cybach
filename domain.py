from __future__ import division

import math
from pprint import pformat

import midi

import config
import constants
from notes import Note
from rhythm import time


class Sequence(list):

    def __init__(self):
        super(Sequence, self).__init__()

        self._samples = []

    def __len__(self):
        return len(self._samples)

    def __setitem__(self, i, v):
        self._samples[i] = v

    def __repr__(self):
        return 'Sequence(samples: %s)' % pformat(self._samples)

    def __getitem__(self, item):
        return self._samples[item]

    def __iter__(self):
        return self._samples.__iter__()

    def __delitem__(self, key):
        del self._samples[key]

    def __getslice__(self, i, j):
        return self._samples.__getslice__(i, j)

    def pitch(self, position):
        return self._samples[position].pitch()

    def apply_transform(self, transform):
        self._samples = transform.apply()

    def __build_empty_samples(self, length):
        for i in range(0, length):
            self._samples.append(Sample(-1, None))

    def note_duration_count(self):
        i = -1
        preferences = {}

        for sample in self._samples:
            if sample.type == Sample.TYPE_START:
                i = 1
            elif sample.type == Sample.TYPE_END and i != config.resolution:
                if preferences.get(i, None) is None:
                    preferences[i] = 0

                preferences[i] += 1
            i += 1

        return preferences

    def to_pattern(self):
        pattern = midi.Pattern(resolution=config.resolution)
        track = midi.Track()

        track.append(midi.KeySignatureEvent(data=[0, 0]))

        ticks = 0
        for i in range(0, len(self._samples)):
            if i in time.signatures().keys():
                ts = time.signatures()[i]
                track.append(midi.TimeSignatureEvent(data=[ts.numerator, int(math.sqrt(ts.denominator)), 36, 8]))

            sample = self._samples[i]
            new_event = False

            if sample.type == Sample.TYPE_START:
                track.append(
                    midi.NoteOnEvent(velocity=constants.DEFAULT_VELOCITY, pitch=sample.note.midi(), tick=ticks))
                new_event = True
            if sample.type == Sample.TYPE_END:
                track.append(midi.NoteOffEvent(pitch=sample.note.midi(), tick=ticks + 2))
                new_event = True

            ticks = 0 if new_event else ticks + 1

        track.append(midi.EndOfTrackEvent())
        pattern.append(track)
        return pattern


class RootSequence(Sequence):

    def __init__(self, track=None):
        super(RootSequence, self).__init__()

        self.__build_samples(track)

    def __build_samples(self, track):
        active_event = None
        for event in track:
            if isinstance(event, midi.NoteOnEvent):
                if active_event is not None:
                    for i in range(0, event.tick):
                        if i == 0:
                            self._samples.append(Sample(active_event.data[0], Sample.TYPE_START))
                            continue
                        elif i == event.tick - 1:
                            self._samples.append(Sample(active_event.data[0], Sample.TYPE_END))
                        else:
                            self._samples.append(Sample(active_event.data[0], Sample.TYPE_SUSTAIN))

                    active_event = None
                else:
                    for i in range(0, event.tick):
                        self._samples.append(Sample(-1, None))

                active_event = event
            elif isinstance(event, midi.NoteOffEvent):
                if active_event is not None:
                    if active_event.data[0] == event.data[0]:
                        for i in range(0, event.tick):
                            if i == 0:
                                self._samples.append(Sample(active_event.data[0], Sample.TYPE_START))
                                continue
                            elif i == event.tick - 1:
                                self._samples.append(Sample(active_event.data[0], Sample.TYPE_END))
                            else:
                                self._samples.append(Sample(active_event.data[0], Sample.TYPE_SUSTAIN))
                        active_event = None


class AccompanimentSequence(Sequence):

    def __init__(self, seed, part, configuration={}):
        super(AccompanimentSequence, self).__init__()
        self._samples = [None] * len(seed)
        self.set_pitch(0, len(seed), -1)

        self._part = part
        self._motion_tendency = configuration.get('motion_tendency', 0.5)

    def part(self):
        return self._part

    def motion_tendency(self):
        return self._motion_tendency

    def set_pitch(self, start, end, note):
        if isinstance(note, Note):
            pitch = note.midi()
        elif isinstance(note, int):
            pitch = note

        for i in range(start, end):
            if pitch == -1:
                self[i] = Sample(-1, None)
                continue

            if i == start:
                self[i] = Sample(pitch, Sample.TYPE_START)
            elif i == end - 1:
                self[i] = Sample(pitch, Sample.TYPE_END)
            else:
                self[i] = Sample(pitch, Sample.TYPE_SUSTAIN)


class Sample:
    TYPE_START = 1
    TYPE_SUSTAIN = 2
    TYPE_END = 3

    def __init__(self, pitch, type):
        self.note = Note(pitch)
        self.type = type

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.note == other.pitch
        return False

    def __repr__(self):
        return 'pitch: %s, type: %s' % (str(self.note), self.type)

    def is_empty(self):
        return self.note.midi() == -1

    def pitch(self):
        return self.note.midi()
