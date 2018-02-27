from __future__ import division

import copy

import midi

import config
import parts
import pat_util
from pitches import Pitch
from rhythm import time

__soprano = None
__alto = None
__tenor = None
__bass = None


def init(track, alto_config={}, tenor_config={}, bass_config={}):
    global __soprano
    global __alto
    global __tenor
    global __bass

    __soprano = RootSequence(track)
    __alto = AccompanimentSequence(config.song_length, parts.ALTO, alto_config)
    __tenor = AccompanimentSequence(config.song_length, parts.TENOR, tenor_config)
    __bass = AccompanimentSequence(config.song_length, parts.BASS, bass_config)


def soprano():
    return __soprano


def alto():
    return __alto


def tenor():
    return __tenor


def bass():
    return __bass


class Sequence:

    def __init__(self):
        self._entities = {}

    def pitch(self, position):
        """
        Returns the pitches.Pitch object of the entity at the given position. Be careful to check whether
        entity at the position is a timed entity, otherwise will throw.

        :param position: sample_position
        :return: pitches.Pitch object
        """
        return self.entity(position).pitch()

    def entities(self):
        return self._entities

    def add_entities(self, *args):
        """
        Wrapper around add_entity to add multiple

        :param args: Entity objects, probably Note or Rest entities
        """
        for arg in args:
            self.add_entity(arg)

    def add_entity(self, new_entity):
        """
        Adds an entity into the map, using entity's internal location variables. Adjusts preexisting
        entity positions or delete overwritten entities

        :param new_entity: Entity object, probably a Note or Rest
        """
        current_entity_at_start = self.entity(new_entity.start())
        current_entity_at_end = self.entity(new_entity.end())

        if current_entity_at_start == current_entity_at_end:
            new_end_entity = copy.copy(current_entity_at_start)
            current_entity_at_start._end = new_entity.start()
            new_end_entity._start = new_entity.end()
            self._entities[new_end_entity.start()] = new_end_entity
        else:
            current_entity_at_start._end = new_entity.start()
            self._entities[new_entity.end()] = current_entity_at_end
            current_entity_at_end._start = new_entity.end()

            if isinstance(current_entity_at_end, TimedEntity) and current_entity_at_end.length() == 0:
                del self._entities[current_entity_at_end.start()]

        if current_entity_at_start.length() == 0:
            del self._entities[current_entity_at_start.start()]

        self._entities[new_entity.start()] = new_entity

        keys_to_remove = [key for key in self._entities.keys() if new_entity.start() < key < new_entity.end()]
        for key in keys_to_remove:
            del self._entities[key]

    def entity(self, position):
        """
        Gets the Entity at the given sample position
        :param position: sample position
        :return: Entity object
        """
        if position < 0:
            return TrackStart(self)
        elif position >= self._length:
            return TrackEnd(self)

        entity_or_none = self._entities.get(position, None)

        if entity_or_none is None:
            keys = self._entities.keys()
            keys.sort()
            keys = reversed(keys)

            for key in keys:
                if position > key:
                    return self._entities[key]

        return entity_or_none

    def is_rest(self, position):
        return self.entity(position).is_rest()

    def apply_transform(self, transform):
        pass

    def note_duration_count(self):
        notes = [entity for entity in self._entities.values() if isinstance(entity, Note)]
        note_count = {}

        for note in notes:
            if note_count.get(note.length(), None) is None:
                note_count[note.length()] = 0

            note_count[note.length()] += 1

        return note_count

    def to_pattern(self):
        pass


class RootSequence(Sequence):

    def __init__(self, track):
        Sequence.__init__(self)
        self._length = pat_util.sample_length(track)
        self.__build_entities(track)

    def __build_entities(self, track):
        """
        Parses a midi.Track object and builds Entities
        :param track: midi.Track object
        """
        note_events = [event for event in track
                       if isinstance(event, midi.NoteOffEvent) or isinstance(event, midi.NoteOnEvent)]

        position = 0
        for current, last in zip(note_events[1:], note_events):
            if isinstance(last, midi.NoteOnEvent):
                if last.tick > 0:
                    self._entities[position] = Rest(self, position, position + last.tick)
                    position += last.tick

                self._entities[position] = Note(self, position, position + current.tick, Pitch(last.data[0]))
                position += current.tick


class AccompanimentSequence(Sequence):

    def __init__(self, length, part, configuration={}):
        Sequence.__init__(self)
        self._entities = {0: Rest(self, 0, length)}

        self._length = length
        self._part = part
        self._motion_tendency = configuration.get('motion_tendency', 0.5)

    def part(self):
        return self._part

    def motion_tendency(self):
        return self._motion_tendency


class Entity:

    def __init__(self, sequence):
        self._sequence = sequence

    def previous_entity(self):
        raise NotImplementedError

    def next_entity(self):
        raise NotImplementedError

    def is_rest(self):
        raise NotImplementedError

    def is_note(self):
        raise NotImplementedError

    def length(self):
        raise NotImplementedError


class TimedEntity(Entity):

    def __init__(self, sequence, start, end):
        Entity.__init__(self, sequence)

        self._end = end
        self._start = start

    def previous_entity(self):
        return self._sequence.entity(self._start - 1)

    def next_entity(self):
        return self._sequence.entity(self._end)

    def length(self):
        return self._end - self._start

    def is_rest(self):
        raise NotImplementedError

    def is_note(self):
        raise NotImplementedError

    def pitch(self):
        raise NotImplementedError

    def start(self):
        return self._start

    def end(self):
        return self._end

    def __eq__(self, other):
        if isinstance(other, TimedEntity):
            return other.start() == self.start() and other.end() == self.end()

        return False

    def __repr__(self):
        return '\n' + str(self.__class__) + ' start: ' + str(self.start()) + ' end: ' + str(self.end())


class Rest(TimedEntity):

    def __init__(self, sequence, start, end):
        TimedEntity.__init__(self, sequence, start, end)

    def is_rest(self):
        return True

    def is_note(self):
        return False

    def pitch(self):
        return Pitch(-1)


class Note(TimedEntity):

    def __init__(self, sequence, start, end, pitch):
        TimedEntity.__init__(self, sequence, start, end)

        if isinstance(pitch, int):
            self._pitch = Pitch(pitch)
        elif isinstance(pitch, Pitch):
            self._pitch = pitch
        else:
            raise ValueError

    def is_rest(self):
        return False

    def is_note(self):
        return True

    def __eq__(self, other):
        if isinstance(other, TimedEntity):
            return other.start() == self.start() and other.end() == self.end() and other.pitch() == self.pitch()

        return False

    def pitch(self):
        return self._pitch

    def __repr__(self):
        return '\n' + str(self.__class__) \
               + ' start: ' + str(self.start()) \
               + ' end: ' + str(self.end()) \
               + ' pitch: ' + str(self.pitch())


class TrackStart(Entity):

    def __init__(self, sequence):
        Entity.__init__(self, sequence)

    def previous_entity(self):
        return self

    def next_entity(self):
        return self._sequence.entity(0)

    def is_rest(self):
        return False

    def length(self):
        return 0

    def is_note(self):
        return False


class TrackEnd(Entity):

    def __init__(self, sequence):
        Entity.__init__(self, sequence)

    def previous_entity(self):
        return self._sequence.entity(time.__beats()[-1])

    def next_entity(self):
        return self

    def is_rest(self):
        return False

    def length(self):
        return 0

    def is_note(self):
        return False
