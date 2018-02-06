import collections
import config
import chords

class KeySignatures(collections.MutableMapping):

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

    def __repr__(self):
        string = ''
        for key in self.store:
            string += '\n' + str(key) + ': ' + str(self.store[key])

        return string

    def __keytransform__(self, key):
        return key

    def set(self):
        return KeySignatureSetter(self)


class KeySignatureSetter:

    def __init__(self, key_signatures):
        self.key_signatures = key_signatures
        self.internal_measure = 0
        self.internal_beat = 0

    def measure(self, measure):
        self.internal_measure = measure
        return self

    def beat(self, beat):
        self.internal_beat = beat
        return self

    def commit(self, chord):
        if isinstance(chord, str):
            parsed = chords.parse(chord)
        elif isinstance(chord, Chord):
            parsed = chord
        else:
            raise TypeError

        sample_pos = config.time_signatures.sample_position(measure=self.internal_measure, beat=self.internal_beat)

        self.key_signatures[sample_pos] = parsed
