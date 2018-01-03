from pprint import pformat

import midi

import ts
from constants import *
from notes import Note


class Sequence(list):
    """
    Represents a sequence of pitches and rests over time. This is instantiated either with
    an initial set capacity or a Track object obtained by reading MIDI. If initialized with a capacity,
    it only contains rests so that we can iterate over it and insert harmony.
    """

    def __init__(self, track=None, sequence=None, part=None, motion_tendency = 0.5):
        super(Sequence, self).__init__()

        self.time_signatures = ts.TimeSignature()
        self.samples = []
        self.motion_tendency = motion_tendency

        if track is not None:
            self.__build_samples(track)

        if part is not None:
            self.part = part

        if sequence is not None:
            self.__build_empty_samples(len(sequence.samples))
            self.time_signatures = sequence.time_signatures

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

    def measure_at(self, index):
        for measure in self.measures():
            if index >= measure.sample_position():
                return measure

    def apply_transform(self, transform):
        self.samples = transform.apply()

    def beats(self):
        beats = []
        for measure in self.measures():
            beats.extend(measure.beats())

    def measure(self, index):
        return self.measures()[index]

    def beat_at(self, index):
        samples = self.samples[index:index + RESOLUTION]
        measure = self.measure_at(index)
        beat_index = (index - measure.sample_position()) / RESOLUTION

        return Beat(samples, measure, beat_index)

    def measure_indexes(self):
        measures = self.measures()
        indexes = []

        index = 0
        for m in measures:
            indexes.append(index)
            index += len(m)
        return indexes

    def measure_subdivision_indexes(self):
        measures = self.measures()
        indexes = []

        index = 0
        for m in measures:
            index += m.subdivision_index()
            indexes.append(index)
            index += m.subdivision_index()
        return indexes

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

        ticks = 0
        for i in range(0, len(self.samples)):
            if i in self.time_signatures:
                track.append(self.time_signatures[i])

            sample = self.samples[i]
            new_event = False

            if sample.type == Sample.TYPE_START:
                track.append(midi.NoteOnEvent(velocity=DEFAULT_VELOCITY, pitch=sample.note.as_midi_value(), tick=ticks))
                new_event = True
            if sample.type == Sample.TYPE_END:
                track.append(midi.NoteOffEvent(pitch=sample.note.as_midi_value(), tick=ticks + 2))
                new_event = True

            ticks = 0 if new_event else ticks + 1

        track.append(midi.EndOfTrackEvent())
        pattern.append(track)
        return pattern

    def set_beat_at_position(self, position, note):
        if isinstance(note, Note):
            pitch = note.midi_value
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

                            self.samples.append(Sample(active_event.data[0], Sample.TYPE_SUSTAIN))
                        active_event = None

            elif isinstance(event, midi.TimeSignatureEvent):
                self.__add_time_signature(event)

    def __build_empty_samples(self, length):
        for i in range(0, length):
            self.samples.append(Sample(-1, None))

    def __add_time_signature(self, event):
        self.time_signatures[len(self.samples)] = event

    def beat_index_in_measure(self, position):
        measure = self.measure_at(position)
        return position - measure.sample_position() / RESOLUTION

    def extend_samples(self):
        new_samples = []

        last_sample = None
        for i in range(0, len(self)):
            sample = self[i]

            if last_sample is None:
                last_sample = sample
                new_samples.append(sample)
                continue

            if last_sample.type == Sample.TYPE_SUSTAIN and sample.type == Sample.TYPE_START:
                new_samples[i - 1] = Sample(new_samples[i - 1].note.midi_value, Sample.TYPE_END)
                last_sample = sample
                new_samples.append(sample)
                continue

            if sample.type is None:
                sample = Sample(last_sample.note.midi_value, Sample.TYPE_SUSTAIN)
                last_sample = sample
                new_samples.append(sample)

        new_samples[-1] = Sample(last_sample.note.midi_value, Sample.TYPE_END)
        self.samples = new_samples


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
        self.note = Note(midi_value=pitch)
        self.type = type

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.note == other.pitch
        return False

    def __repr__(self):
        return 'pitch: %s, type: %s' % (str(self.note), self.type)

    def is_empty(self):
        return self.note.as_midi_value() == -1

    def pitch(self):
        return self.note.midi_value
