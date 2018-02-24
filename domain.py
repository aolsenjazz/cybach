from __future__ import division

import math
from pprint import pformat

import midi

import config
import constants
from pitches import Pitch
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

    def entity(self, position):
        if position < 0:
            return TrackStart(self)
        elif position >= len(self):
            return TrackEnd(self)

        entity_start = self.get_entity_start(position)
        entity_length = self.get_entity_length(entity_start)

        start_sample = self[entity_start]

        if start_sample.is_rest():
            return Rest(self, entity_start, entity_length)
        else:
            return Note(self, entity_start, entity_length, start_sample.pitch())

    def timed_entities(self):
        entities = []

        entity = self.entity(0)
        while isinstance(entity, TimedEntity):
            entities.append(entity)
            entity = entity.next_entity()

        return entities

    def get_entity_start(self, position):
        beat = position
        if isinstance(position, int):
            beat = time.beat_at_position(position)

        base_sample = self[position]
        entity_start = position
        while True:
            sample = self[entity_start]

            if base_sample.is_rest() and (not sample.is_rest() or entity_start == beat.parent().start()):
                entity_start += 1
                break
            elif sample.is_start():
                break

            entity_start -= 1

        return entity_start

    def get_entity_length(self, start_position):
        length = 0
        base_sample = self[start_position]
        measure = time.beat_at_position(start_position).parent()

        while True:
            sample = self[start_position + length]

            if base_sample.is_rest() and (not sample.is_rest() or start_position + length == measure.end()):
                break
            elif sample.type() == Sample.TYPE_END:
                length += 1
                break

            length += 1

        return length

    def is_rest(self, position):
        return self._samples[position].is_rest()

    def apply_transform(self, transform):
        self._samples = transform.apply()

    def __build_empty_samples(self, length):
        for i in range(0, length):
            self._samples.append(Sample(-1, None))

    def note_duration_count(self):
        notes = [entity for entity in self.timed_entities() if isinstance(entity, Note)]
        note_count = {}

        for note in notes:
            if note_count.get(note.length(), None) is None:
                note_count[note.length()] = 0

            note_count[note.length()] += 1

        return note_count

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
                    midi.NoteOnEvent(velocity=constants.DEFAULT_VELOCITY, pitch=sample.pitch.midi(), tick=ticks))
                new_event = True
            if sample.type == Sample.TYPE_END:
                track.append(midi.NoteOffEvent(pitch=sample.pitch.midi(), tick=ticks + 2))
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


class Entity:

    def __init__(self, sequence):
        self._sequence = sequence

    def previous_entity(self):
        raise NotImplementedError

    def next_entity(self):
        raise NotImplementedError


class TimedEntity(Entity):

    def __init__(self, sequence, start, length):
        Entity.__init__(self, sequence)

        self._length = length
        self._start = start

    def previous_entity(self):
        return self._sequence.entity(self._start - 1)

    def next_entity(self):
        return self._sequence.entity(self._start + self._length)

    def length(self):
        return self._length

    def start(self):
        return self._start

    def end(self):
        return self._start + self._length


class Rest(TimedEntity):

    def __init__(self, sequence, start, length):
        TimedEntity.__init__(self, sequence, start, length)


class Note(TimedEntity):

    def __init__(self, sequence, start, length, pitch):
        TimedEntity.__init__(self, sequence, start, length)

        self._pitch = pitch


class TrackStart(Entity):

    def __init__(self, sequence):
        Entity.__init__(self, sequence)

    def previous_entity(self):
        return self

    def next_entity(self):
        return self._sequence.entity(0)


class TrackEnd(Entity):

    def __init__(self, sequence):
        Entity.__init__(self, sequence)

    def previous_entity(self):
        return self._sequence.entity(time.beats()[-1])

    def next_entity(self):
        return self


class Sample:

    TYPE_START = 1
    TYPE_SUSTAIN = 2
    TYPE_END = 3

    def __init__(self, pitch, type):
        self._pitch = Pitch(pitch)
        self._type = type

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self._pitch == other.midi
        return False

    def __repr__(self):
        return 'pitch: %s, type: %s' % (str(self._pitch), self._type)

    def is_rest(self):
        return self._pitch.midi() == -1

    def type(self):
        return self._type

    def pitch(self):
        return self._pitch

    def is_start(self):
        return self._type == Sample.TYPE_START

    def midi(self):
        return self._pitch.midi()
