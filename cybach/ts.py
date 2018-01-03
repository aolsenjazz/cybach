import collections


class TimeSignature(collections.MutableMapping):
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


def is_four_four(time_signature_event):
    return time_signature_event.numerator == 4 and time_signature_event.denominator == 4


def is_six_eight(time_signature_event):
    return time_signature_event.numerator == 6 and time_signature_event.denominator == 8


def is_two_four(time_signature_event):
    return time_signature_event.numerator == 2 and time_signature_event.denominator == 4


def is_three_four(time_signature_event):
    return time_signature_event.numerator == 3 and time_signature_event.denominator == 4