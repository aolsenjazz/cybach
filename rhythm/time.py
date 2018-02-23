from __future__ import division

import collections
import itertools
import math

import config


# TODO: this has to go
def is_big_beat(time_signature, beat_base_zero):
    numerator = time_signature.numerator

    if numerator <= 10:
        return beat_base_zero % (numerator / math.floor(math.sqrt(numerator))) == 0
    elif numerator == 12:
        return beat_base_zero % 3 == 0
    else:
        raise ValueError('What the hell time signature did you submit?')


class TimeSignature:
    def __init__(self, event=None, numerator=0, denominator=0):
        if event is not None:
            self.numerator = event.numerator
            self.denominator = event.denominator
        else:
            self.numerator = numerator
            self.denominator = denominator

        self._samples_per_beat = int(config.resolution / (self.denominator / 4))
        self._samples_per_measure = int(self.numerator * self._samples_per_beat)
        self._strong_beat_pattern = [i for i in range(self.numerator)]

    def __repr__(self):
        return 'num: %d || den: %d' % (self.numerator, self.denominator)

    def samples_per_measure(self):
        return self._samples_per_measure

    def samples_per_beat(self):
        return self._samples_per_beat

    def set_strong_beat_pattern(self, pattern):
        self._strong_beat_pattern = pattern

    def strong_beat_pattern(self):
        return self._strong_beat_pattern


class TimeSignatures(collections.MutableMapping):
    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))

    def __getitemhardway(self, index):
        active_key = 0
        for k in self.store:
            if index >= k >= active_key:
                active_key = k
        return self.store[active_key]

    def __getitem__(self, key):
        return self.store.get(key, self.__getitemhardway(key))

    def __setitem__(self, key, value):
        self.store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        del self.store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        return key

    def __repr__(self):
        string = ''
        for key in self.store:
            string += '\n' + str(key) + ': ' + str(self.store[key]) + str(self.store[key]) + str(self.store[key])

        return string

    def sample_position(self, measure=0, beat=0):
        position = 0

        for i in range(0, measure):
            active_time_signature = self[position]
            position += active_time_signature.samples_per_measure()

        active_time_signature = self[position]
        position += beat * active_time_signature.samples_per_beat()

        return int(position)


class Measure:

    def __init__(self, start):
        self._start = start
        self._time_signature = signatures()[start]
        self._samples_per_beat = int(4 / self.time_signature().denominator * config.resolution)
        self._beats = self.__beats()

    def start(self):
        return self._start

    def end(self):
        return self.start() + self._samples_per_beat * self._time_signature.numerator

    def samples_per_beat(self):
        return self._samples_per_beat

    def time_signature(self):
        return self._time_signature

    def beats(self):
        return self._beats

    def beat(self, index):
        return self.beats()[index]

    def strong_beat_pattern(self):
        return self.time_signature().strong_beat_pattern()

    def __beats(self):
        beats = []

        for i in range(0, self._time_signature.numerator):
            sample_position = self.start() + i * self.samples_per_beat()
            beats.append(Beat(sample_position, i, self))

        return beats

    def strong_beats(self):
        return [beat for beat in self.beats() if beat.index_in_measure() in self.strong_beat_pattern()]


class Beat:

    def __init__(self, position, index_in_measure, parent):
        self._start = position
        self._time_signature = signatures()[position]
        self._end = position + parent.samples_per_beat()
        self._index_in_measure = index_in_measure
        self._parent = parent

    def start(self):
        return self._start

    def length(self):
        return self.end() - self.start()

    def end(self):
        return self._end

    def time_signature(self):
        return self._time_signature

    def parent(self):
        return self._parent

    def index_in_measure(self):
        return self._index_in_measure

    def strong_beat(self):
        return self.index_in_measure() in self.parent().strong_beat_pattern()

    def first_beat(self):
        return self.index_in_measure() == 0

    def last_beat(self):
        return self.index_in_measure() == self.time_signature().numerator - 1

    def on_beat(self):
        numerator = self.time_signature().numerator

        if numerator == 2 or numerator == 3:
            return self.first_beat()
        elif numerator == 4:
            return self.index_in_measure() == 0 or self.index_in_measure() == 2

        return self.strong_beat()


__signatures = TimeSignatures()
__measures = {}
__beats = {}


def measure(index):
    keys = __measures.keys()
    keys.sort()
    return __measures[keys[index]]


def signatures():
    return __signatures


def measures():
    return __measures


def clear():
    global __signatures
    __signatures = TimeSignatures()


def add_signature(sample_position, signature):
    __signatures[sample_position] = signature
    __compute_time_increments()


def delete_signature(sample_position):
    del __signatures[sample_position]
    __compute_time_increments()


def __compute_time_increments():
    global __measures, __beats
    __measures = {}
    __beats = {}

    song_length = len(config.soprano)
    signature_positions_plus_end = __signatures.keys() + [song_length]
    signature_positions_plus_end.sort()

    for pos1, pos2 in zip(signature_positions_plus_end, signature_positions_plus_end[1::]):
        sig1 = __signatures[pos1]

        measure_group = {position: Measure(position) for position in range(pos1, pos2)[::sig1.samples_per_measure()]}
        __measures.update(measure_group)
        beat_group = [beat for k in measure_group.keys() for beat in measure_group[k].beats()]
        __beats.update({beat.start(): beat for beat in beat_group})
