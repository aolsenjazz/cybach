from __future__ import division
from pprint import pformat

import midi
import config
from rhythm import time
import math
import constants
import vars
from notes import Note


class Sequence(list):
    """
    Represents a sequence of pitches and rests over time. This is instantiated either with an initial set capacity
    or a midi.Pattern object obtained by reading MIDI. If initialized with a seed, it only contains rests so that
    we can iterate over it and insert pitches.
    """

    def __init__(self, track=None, seed=None, part=None, configuration={}):
        """
        Has two initialization processes: Pattern-based and seed-based.

        Pattern-based initializing reads a midi.Pattern object to create note events. We convert from that model to
        our model because it's easier toupdate note values with our model. Time signature and key signature data are
        also read from the pattern and stored here.

        Seed-based initialization reads another Sequence object and creates empty Samples equal to the length
        of the seed Sequence. Time signature and key signature data are ignored.

        :param track: midi.Pattern which we get note, key signature, and time signature info from
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
        if track is not None:
            self.__build_samples(track)

        else:
            if part is None:
                raise ValueError('\'part\' argument may not be None without supplying a track')
            if seed is None:
                raise ValueError('\'seed\' arg may not be None without supplying a track')

            self.part = part
            self.__build_empty_samples(len(seed.samples))

        self.__precompute_measures()
        self._beats = self.__precompute_beats()

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

    def __precompute_measures(self):
        more_measures = True
        measures = []
        sample_position = 0
        index = 0

        while more_measures:
            active_time_signature = time.signatures[sample_position]
            samples = self[sample_position:sample_position + active_time_signature.samples_per_measure()]
            measures.append(Measure(index, samples, active_time_signature, sample_position, self))
            sample_position += active_time_signature.samples_per_measure()
            index += 1
            more_measures = sample_position < len(self)

        self._measures = measures

    def __precompute_beats(self):
        self._beats = {}

        for measure in self.measures():
            for beat in measure.beats():
                self._beats[beat.sample_position()] = beat

    def strong_beat_positions(self):
        beats = []

        for measure in self.measures():
            phrasing = measure.time_signature.phrasing
            beats.extend([measure.beats()[i].sample_position() for i in phrasing])

        return beats

    def parent_measure(self, index):
        measures = self.measures()
        measures.reverse()
        for measure in measures:
            sample_position = measure.sample_position()
            if index >= sample_position:
                return measure

    def apply_transform(self, transform):
        self.samples = transform.apply()

    def beats(self):
        beats = []
        for measure in self.measures():
            beats.extend(measure.beats())

    def beat_at(self, sample_index):
        time_signature = time.signatures[sample_index]
        samples = self.samples[sample_index:(sample_index + time_signature.samples_per_beat())]
        measure = self.parent_measure(sample_index)
        beat_index = (sample_index - measure.sample_position()) / config.resolution
        return Beat(samples, measure, beat_index)

    def measures(self):
        return self._measures

    def to_pattern(self):
        pattern = midi.Pattern(resolution=config.resolution)
        track = midi.Track()

        track.append(midi.KeySignatureEvent(data=[0, 0]))

        ticks = 0
        for i in range(0, len(self.samples)):
            if i in time.signatures.keys():
                time_signature = time.signatures[i]
                track.append(midi.TimeSignatureEvent(data=[time_signature.numerator,
                                                           int(math.sqrt(time_signature.denominator)),
                                                           36,
                                                           8]))

            sample = self.samples[i]
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

    def __build_empty_samples(self, length):
        for i in range(0, length):
            self.samples.append(Sample(-1, None))

    def beat_index_in_measure(self, position):
        measure = self.parent_measure(position)
        return (position - measure.sample_position()) / config.resolution

    def note_duration_count(self):
        i = -1
        preferences = {}

        for sample in self.samples:
            if sample.type == Sample.TYPE_START:
                i = 1
            elif sample.type == Sample.TYPE_END and i != config.resolution:
                if preferences.get(i, None) is None:
                    preferences[i] = 0

                preferences[i] += 1
            i += 1

        return preferences


class Measure(list):

    def __init__(self, measure_index, samples, time_signature, sample_position, parent):
        super(Measure, self).__init__()
        self.samples = samples
        self.parent = parent
        self.measure_index = measure_index
        self.time_signature = time_signature
        self._sample_position = sample_position
        self._beats = self.__precompute_beats()

    def __repr__(self):
        return '\nMeasure(samples: %s)' % pformat(self.samples)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        return self.samples[index]

    def sample_position(self):
        return self._sample_position

    def __precompute_beats(self):
        beats = []
        time_signature = self.time_signature
        samples_per_beat = time_signature.samples_per_beat()

        j = 0
        while j < len(self.samples):
            beats.append(Beat(self.samples[j:j + samples_per_beat], int(j / samples_per_beat), self))

            j += samples_per_beat

        return beats

    def beats(self):
        return self._beats

    def phrasing_candidates(self):
        if self.time_signature.numerator <= 4:
            t = self.beats()
            return {tuple([i for i in range(0, self.time_signature.numerator)]): 1}
        else:
            phrase_combinations = time.phrase_combinations(self.time_signature.numerator)
            combination_map = {}

            for combination in phrase_combinations:
                combination_map[combination] = 0.0

            # Guess the phrase groupings based on the position of chords in the measure
            chord_based_prediction = self.chord_based_phrasing_prediction()
            if combination_map.get(chord_based_prediction, None) is not None:
                combination_map[chord_based_prediction] = combination_map[chord_based_prediction] + vars.CHORD_PHRASING

            # Based on the rhythms of the melody, rank phrase grouping likeliness
            for combination in combination_map.keys():
                combination_map[combination] = combination_map[combination] + \
                                               self.phrasing_likelihood(combination)

            return combination_map

    def beats_for_phrasing(self, phrasing):
        position = 0
        beats = [self.beats()[position]]

        for i in range(0, len(phrasing)):
            if i == len(phrasing) - 1:
                return beats

            position += phrasing[i]
            beats.append(self.beats()[position])

    def phrasing_likelihood(self, phrase_combination):
        """
        Returns how likely the the measure is to conform to the submitted phrase grouping. Phrase groupings
        are submitted as a tuple with any permutation of the number 2, 3, 4 provided that the sum of all of them
        is the current time signature numerator.

        E.g. tuples that can be submitted for 7/8 could include (2, 3, 2), (4, 3), (3, 4)

        :param phrase_combination: A tuple consisting of the numbers 2, 3, 4
        """
        likelihood_score = 0.0
        position = 0

        for value in phrase_combination:
            beat = self.beats()[position]
            target_duration = value * len(beat)

            if (beat.is_note_start() or beat.is_rest()) and beat.sustain_duration() == target_duration:
                likelihood_score += vars.RHYTHM_PHRASING_COEF * value

            position += value

        return likelihood_score

    def chord_based_phrasing_prediction(self):
        """
        Based on where the chords are in the measure, tries to guess the phrase groupings.

        E.g. 1: in a 6/8 measure, if there are chords on 0 and 3, will return phrase grouping of (0, 3)
        E.g. 2: in a 7/8 measure, if there are chords on 0, 2, and 4, will return phrase grouping of (0, 2, 4)
        """
        candidate = [0]
        chords = config.chord_progression.chords_in_measure(self.measure_index)
        beats = self.beats()
        beats.sort()

        for beat in beats:
            if beat.is_first_beat() or beat.is_last_beat():
                continue  # let's assume that 1 is a phrase start, and that the last beat is a phrase end

            if chords.get(beat.sample_position(), None) is not None and \
                    chords.get(beat.sample_position() - len(beat), None) is None and \
                    chords.get(beat.sample_position() + len(beat), None) is None:
                candidate.append(int(beat.beat_index - sum(candidate)))

        return tuple(candidate)


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

    def sustain_duration(self):
        sequence_samples = self.parent.parent.samples
        pitch = self.pitch()
        note_type = Sample.TYPE_SUSTAIN
        i = 0

        while i < len(sequence_samples) and pitch == self.pitch() and \
                (note_type == Sample.TYPE_SUSTAIN or i == 1 or pitch == -1):
            pitch = sequence_samples[self.sample_position() + i].pitch()
            note_type = sequence_samples[self.sample_position() + i].type
            i += 1

        if self.pitch() == -1:
            i -= 1

        return i

    def sample_position(self):
        time_signature = time.signatures[self.parent.sample_position()]
        return int(self.parent.sample_position() + time_signature.samples_per_beat() * self.beat_index)

    def pitch(self):
        return self.samples[0].pitch()

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

    def is_first_beat(self):
        return self.beat_index == 0

    def is_last_beat(self):
        return self.sample_position() == len(self.parent) - len(self)

    def is_note_start(self):
        return self.samples[0].type == Sample.TYPE_START

    def is_pitch_change(self):
        if self.sample_position() == 0:
            return True
        return self.parent.parent.samples[self.sample_position() - 1].pitch() != self.samples[0].pitch()

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

    def is_rest(self):
        return self.samples[0].is_empty()


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
