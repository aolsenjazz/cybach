from pprint import pformat
import midi
import math
from constants import *
from notes import Note


class Sequence(list):
    """
    Represents a sequence of pitches and rests over time. This is instantiated either with
    an initial set capacity or a Track object obtained by reading MIDI. If initialized with a capacity,
    it only contains rests so that we can iterate over it and insert harmony.
    """

    # MIDI files can have multiple time signatures
    time_signatures = {}

    # Represents a pitch and type. Types are either Note.TYPE_START, Note.TYPE_SUSTAIN, or Note.TYPE_END
    samples = []

    def __init__(self, track=None, length=0):
        if track is not None:
            self.__build_samples(track)

        if length != 0:
            for i in range(0, length):
                samples.append(Sample(-1, None))

        super(Sequence, self).__init__()

    def __repr__(self):
        return '\n Sequence(measures: %s)' % pformat(self.measures())

    def __getitem__(self, item):
        return self.samples[item]

    def beats(self):
        beats = []
        for measure in self.measures():
            beats.extend(measure.beats())

    def measure(self, index):
        return self.measures()[index]

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

    def __build_samples(self, track):
        for event in track:
            if isinstance(event, midi.NoteOnEvent):
                for i in range(0, event.tick):
                    self.samples.append(Sample(-1, None))

            elif isinstance(event, midi.NoteOffEvent):
                for i in range(0, event.tick):
                    note_type = Sample.TYPE_START if i == 0 \
                        else (Sample.TYPE_END if i == event.tick - 1 else Sample.TYPE_SUSTAIN)
                    self.samples.append(Sample(event.data[0], note_type))

            elif isinstance(event, midi.TimeSignatureEvent):
                self.__add_time_signature(event)

    def __add_time_signature(self, event):
        self.time_signatures[len(self.samples)] = event


class Measure(list):

    samples = []
    parent = None
    measure_index = None
    signature = None

    def __init__(self, measure_index, samples, signature, parent):
        super(Measure, self).__init__()
        self.samples = samples
        self.parent = parent
        self.measure_index = measure_index
        self.signature = signature

    def __repr__(self):
        return '\nMeasure(samples: %s)' % pformat(self.samples)

    def __getitem__(self, item):
        return super(Measure, self).__getitem__(item)

    def first_sample(self):
        return self.samples[0]

    def primary_subdivision(self):
        index = int(math.ceil(signature.numerator / 2))
        return self.samples[index]

    def beats(self):
        beats = []

        j = 0
        while j < len(self.samples):
            beats.append(self.samples[j:(j + RESOLUTION)])

            j += RESOLUTION

        return beats

    def beat_value(self):
        if self.measure_index == 0:
            return 0

        beats = 0

        for i in range(0, self.measure_index):
            beats += self.parent.measure(i).signature.numerator

        return beats + 1


class Beat(list):

    samples = []

    def __init__(self, samples):
        super(Beat, self).__init__()
        self.samples = samples

    def __repr__(self):
        return '\nBeat(samples: %s)' % pformat(list(self))

    def __getitem__(self, item):
        return super(Beat, self).__getitem__(item)


class Sample:
    TYPE_START = 1
    TYPE_SUSTAIN = 2
    TYPE_END = 3

    note = None
    type = None

    def __init__(self, pitch, sample_type):
        self.note = Note(midi_value=pitch)
        self.type = sample_type

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.note == other.pitch
        return False

    def __repr__(self):
        return '\npitch: %s, type: %s' % (str(self.note), self.type)

