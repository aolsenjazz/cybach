from pprint import pformat

import midi

import ts
import ks
from constants import *
from notes import Note


class Sequence(list):
    """
    Represents a sequence of pitches and rests over time. This is instantiated either with an initial set capacity
    or a midi.Pattern object obtained by reading MIDI. If initialized with a seed, it only contains rests so that
    we can iterate over it and insert pitches.
    """

    def __init__(self, pattern=None, seed=None, part=None, configuration={}, time_signatures=None):
        """
        Has two initialization processes: Pattern-based and seed-based.

        Pattern-based initializing reads a midi.Pattern object to create note events. We convert from that model to
        our model because it's easier toupdate note values with our model. Time signature and key signature data are
        also read from the pattern and stored here.

        Seed-based initialization reads another Sequence object and creates empty Samples equal to the length
        of the seed Sequence. Time signature and key signature data are ignored.

        :param pattern: midi.Pattern which we get note, key signature, and time signature info from
        :param seed: Sequence object that we get duration info from
        :param part: parts.BASS, parts.TENOR, or parts.ALTO
        :param configuration: Misc configuration
        """
        super(Sequence, self).__init__()

        self.samples = []
        self.motion_tendency = configuration.get('motion_tendency', 0.5)

        # Initialize this sequence with the midi data obtained via this track. Also populates time
        # signature data and key signature data. Maybe should be decoupled, but it's much easier this way.
        #
        # Note that 'track' being non-None and any other arg being non-None is mutually exclusive
        if pattern is not None:
            self.time_signatures = ts.TimeSignatures()
            self.key_signatures = ks.KeySignatures()
            self.__build_samples(pattern)

        else:
            if part is None:
                raise ValueError('\'part\' argument may not be None without supplying a track')
            if seed is None:
                raise ValueError('\'seed\' arg may not be None without supplying a track')
            if time_signatures is None:
                raise ValueError('\'time_signatures\' arg may not be None without supplying a track')

            self.part = part
            self.time_signatures = time_signatures
            self.__build_empty_samples(len(seed.samples))


    def __len__(self):
        return len(self.samples)

    def __setitem__(self, i, v):
        self.samples[i] = v

    def __repr__(self):
        return '\n Sequence(measures: %s)' % pformat(self.measures())

    def __getitem__(self, item):
        return self.samples[item]

    def __iter__(self):
        return self.samples.__iter__()

    def __delitem__(self, key):
        del self.samples[key]

    def __getslice__(self, i, j):
        return self.samples.__getslice__(i, j)

    def parent_measure(self, index):
        for measure in self.measures():
            if index >= measure.sample_position():
                return measure

    def apply_transform(self, transform):
        self.samples = transform.apply()

    def beats(self):
        beats = []
        for measure in self.measures():
            beats.extend(measure.beats())

    def beat_at(self, index):
        samples = self.samples[index:index + RESOLUTION]
        measure = self.parent_measure(index)
        beat_index = (index - measure.sample_position()) / RESOLUTION

        return Beat(samples, measure, beat_index)

    def measures(self):
        measures = []
        index = 0
        thresholds = self.time_signatures.keys()

        for i in range(0, len(thresholds)):
            signature = self.time_signatures[thresholds[i]]
            signature_start = thresholds[i]

            if len(thresholds) > i + 1:
                signature_end = self.time_signatures[thresholds[i + 1]]
            else:
                signature_end = len(self.samples)

            j = signature_start

            while j < signature_end:
                measures.append(Measure(index, self.samples[j:(j + signature.numerator * RESOLUTION)], signature, self))

                index += 1
                j += (signature.numerator * RESOLUTION)
        return measures

    def to_pattern(self):
        pattern = midi.Pattern(resolution=RESOLUTION)
        track = midi.Track()

        track.append(midi.KeySignatureEvent(data=[0, 0]))

        ticks = 0
        for i in range(0, len(self.samples)):
            if i in self.time_signatures:
                track.append(self.time_signatures[i])

            sample = self.samples[i]
            new_event = False

            if sample.type == Sample.TYPE_START:
                track.append(midi.NoteOnEvent(velocity=DEFAULT_VELOCITY, pitch=sample.note.midi(), tick=ticks))
                new_event = True
            if sample.type == Sample.TYPE_END:
                track.append(midi.NoteOffEvent(pitch=sample.note.midi(), tick=ticks + 2))
                new_event = True

            ticks = 0 if new_event else ticks + 1

        track.append(midi.EndOfTrackEvent())
        pattern.append(track)
        return pattern

    def set_beat_at_position(self, position, note):
        if isinstance(note, Note):
            pitch = note.midi()
        elif isinstance(note, int):
            pitch = note

        for i in range(position, position + RESOLUTION):
            if pitch == -1:
                self[i] = Sample(-1, None)
                continue

            if i == position:
                self[i] = Sample(pitch, Sample.TYPE_START)
            elif i == position + RESOLUTION - 1:
                self[i] = Sample(pitch, Sample.TYPE_END)
            else:
                self[i] = Sample(pitch, Sample.TYPE_SUSTAIN)

    def __build_samples(self, track):
        active_event = None
        for event in track:
            if isinstance(event, midi.NoteOnEvent):
                if active_event is not None:
                    for i in range(0, event.tick):
                        if i == 0:
                            self.samples.append(Sample(active_event.data[0], Sample.TYPE_START))
                            continue
                        elif i == event.tick - 1:
                            self.samples.append(Sample(active_event.data[0], Sample.TYPE_END))
                        else:
                            self.samples.append(Sample(active_event.data[0], Sample.TYPE_SUSTAIN))

                    active_event = None
                else:
                    for i in range(0, event.tick):
                        self.samples.append(Sample(-1, None))

                active_event = event
            elif isinstance(event, midi.NoteOffEvent):
                if active_event is not None:
                    if active_event.data[0] == event.data[0]:
                        for i in range(0, event.tick):
                            if i == 0:
                                self.samples.append(Sample(active_event.data[0], Sample.TYPE_START))
                                continue
                            elif i == event.tick - 1:
                                self.samples.append(Sample(active_event.data[0], Sample.TYPE_END))
                            else:
                                self.samples.append(Sample(active_event.data[0], Sample.TYPE_SUSTAIN))
                        active_event = None

            elif isinstance(event, midi.TimeSignatureEvent):
                self.__add_time_signature(event)
            elif isinstance(event, midi.KeySignatureEvent):
                self.__add_key_signature(event)

    def __build_empty_samples(self, length):
        for i in range(0, length):
            self.samples.append(Sample(-1, None))

    def __add_time_signature(self, event):
        self.time_signatures[len(self.samples)] = event

    def __add_key_signature(self, event):
        pass

    def beat_index_in_measure(self, position):
        measure = self.parent_measure(position)
        return position - measure.sample_position() / RESOLUTION

    def motion_preferences(self):
        i = -1
        preferences = {}

        for sample in self.samples:
            if sample.type == Sample.TYPE_START:
                i = 0
            elif sample.type == Sample.TYPE_END and i != RESOLUTION:
                if preferences.get(i, None) is None:
                    preferences[i] = 0

                preferences[i] += 1

        return preferences


class Measure(list):

    def __init__(self, measure_index, samples, signature, parent):
        super(Measure, self).__init__()
        self.samples = samples
        self.parent = parent
        self.measure_index = measure_index
        self.signature = signature

    def __repr__(self):
        return '\nMeasure(samples: %s)' % pformat(self.samples)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        return self.samples[index]

    def subdivision_index(self):
        return self.signature.numerator / 2 * RESOLUTION

    def sample_position(self):
        measures = self.parent.measures()

        sample_count = 0
        for i in range(0, self.measure_index):
            sample_count += len(measures[i])

        return sample_count

    def beats(self):
        beats = []

        j = 0
        while j < len(self.samples):
            beats.append(Beat(self.samples[j:(j + RESOLUTION)], j / RESOLUTION, self))

            j += RESOLUTION

        return beats


class Beat(list):

    def __init__(self, samples, beat_index, parent):
        super(Beat, self).__init__()
        self.samples = samples
        self.parent = parent
        self.beat_index = beat_index

    def __repr__(self):
        return '\nBeat(samples: %s)' % pformat(list(self.samples))

    def __getitem__(self, item):
        return self.samples[item]

    def __setitem__(self, key, value):
        self.samples[key] = value

    def __len__(self):
        return len(self.samples)

    def beat_position(self):
        return len(self.parent) + (self.beat_index * RESOLUTION)

    def contains_motion(self):
        last_pitch = -1
        i = 0
        for sample in self.samples:
            if last_pitch == -1:
                last_pitch = sample.pitch()
                continue

            if sample.pitch() != last_pitch:
                return True

        return False

    def contains_linear_movement(self):
        last_pitch = self.samples[0].pitch()
        contains_linear_motion = False

        for sample in self.samples:
            if last_pitch - 2 <= sample.pitch() <= last_pitch + 2 and sample.pitch() != last_pitch:
                contains_linear_motion = True

            if sample.pitch() < last_pitch - 2 or sample.pitch() > last_pitch + 2:
                contains_linear_motion = False

            last_pitch = sample.pitch()

        return contains_linear_motion


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
