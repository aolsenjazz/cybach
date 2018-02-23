from __future__ import division

import collections
import itertools
import math

import config


def phrase_combinations(beats_per_bar):
    if beats_per_bar <= 4:
        return [tuple([i for i in range(0, beats_per_bar)])]
    else:
        max_phrases = int(math.floor(beats_per_bar / 2))

        potential_combinations = []

        for i in range(0, max_phrases):
            potential_combinations.append([0, 2, 3, 4])

        all_combinations = [i for i in itertools.product(*potential_combinations) if sum(i) == beats_per_bar]
        parsed = set()

        for combination in all_combinations:
            parsed_combination = tuple([item for item in combination if item != 0])
            reformatted_combination = [0]

            for item in parsed_combination:
                if len(reformatted_combination) == len(parsed_combination):
                    parsed.add(tuple(reformatted_combination))
                    break

                reformatted_combination.append(item + sum(reformatted_combination))

        return parsed

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

    def __repr__(self):
        return 'num: %d || den: %d' % (self.numerator, self.denominator)

    def samples_per_measure(self):
        return self._samples_per_measure

    def samples_per_beat(self):
        return self._samples_per_beat


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


signatures = TimeSignatures()