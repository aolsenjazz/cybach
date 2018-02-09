from __future__ import division

import abc
import constants
import rhythm
import chords
import domain
import config
import vars
import notes



class MotionTransform:

    SCALE_MICRO = 'micro'
    SCALE_MACRO = 'macro'

    def __init__(self):
        pass

    def synergy(self, transform):
        raise NotImplementedError

    def __repr__(self):
        return self.__class__.__name__ + ' - mu:%f - mo:%f' \
                                        % (self.intrinsic_musicality, self.intrinsic_motion)

    def apply(self):
        raise NotImplementedError

    def is_syncopation(self):
        raise NotImplementedError

    def crosses_bar_line(self):
        raise NotImplementedError

    def causes_flickering(self):
        raise NotImplementedError


class JoinTransform(MotionTransform):

    def __init__(self, duration, position, sequence):
        MotionTransform.__init__(self)

        self.scale = self.SCALE_MACRO
        self.sequence = sequence
        self.position = position
        self.duration = duration
        self.intrinsic_motion = 0.50 - (duration * vars.JOIN_MOTION_COEFFICIENT)
        self.intrinsic_musicality = self.set_musicality()

    def synergy(self, transform):
        return vars.JOIN_SAME if isinstance(transform, self.__class__) and self.duration == transform.duration else 0.0

    def set_musicality(self):
        score = 0.0

        # The longer a note is, the higher its musicality; longer notes less common within normal configurations
        duration_score = (((2 - (.1 * self.duration) / 2) ** self.duration) / 2) / 100
        score += duration_score

        num_unique_chords = unique_chord_count(self.position, self.duration)
        score += vars.TWO_BEAT_MULTIPLE_CHORDS * num_unique_chords

        time_signature = config.time_signatures[self.position]
        if time_signature.numerator % 3 == 0 and not self.is_syncopation():
            score += vars.JOIN_PREFER_BIG_BEATS

        return score

    def crosses_bar_line(self):
        beat_index = self.sequence.beat_index_in_measure(self.position)
        time_signature = config.time_signatures[self.position]

        return beat_index + self.duration > time_signature.numerator

    def is_syncopation(self):
        beat_index = self.sequence.beat_index_in_measure(self.position)
        time_signature = config.time_signatures[self.position]

        return not rhythm.is_big_beat(time_signature, beat_index)

    def apply(self):
        for i in range(self.position, self.position + self.duration * config.resolution):
            if i == self.position:
                continue
            elif i == self.position + (self.duration * config.resolution) - 1:
                self.sequence[i].type = domain.Sample.TYPE_END
            else:
                self.sequence[i].type = domain.Sample.TYPE_SUSTAIN

        return self.sequence.samples

    def causes_flickering(self):
        return False


class NoneTransform(MotionTransform):

    def __init__(self, sequence):
        MotionTransform.__init__(self)

        self.sequence = sequence
        self.intrinsic_musicality = 0.0
        self.intrinsic_motion = 0.5
        self.position = 0

    def synergy(self, transform):
        return 0.0

    def apply(self):
        return self.sequence.samples

    def is_syncopation(self):
        return False

    def crosses_bar_line(self):
        return False

    def causes_flickering(self):
        return False


class EighthNoteTransform(MotionTransform):

    def __init__(self, position, sequence):
        MotionTransform.__init__(self)

        self.position = position
        self.sequence = sequence
        self.intermediate_pitch = -1

    def apply(self):
        half_way = int(self.position + (config.resolution / 2))

        for i in range(half_way, self.position + config.resolution):
            if i == half_way:
                self.sequence[i - 1] = domain.Sample(self.sequence[i - 1].pitch(), domain.Sample.TYPE_END)
                self.sequence[i] = domain.Sample(self.intermediate_pitch, domain.Sample.TYPE_START)
            elif i == self.position + config.resolution - 1:
                self.sequence[i] = domain.Sample(self.intermediate_pitch, domain.Sample.TYPE_END)
            else:
                self.sequence[i] = domain.Sample(self.intermediate_pitch, domain.Sample.TYPE_SUSTAIN)

        return self.sequence.samples

    def synergy(self, transform):
        if isinstance(transform, EighthNoteTransform) and not isinstance(transform, self.__class__):
            next_chord = config.chord_progression[self.position + config.resolution]

            if dissonant(self.intermediate_pitch, transform.intermediate_pitch):
                return vars.EIGHTH_NOTE_DISSONANCE
            elif next_chord.indicates_dominant(self.intermediate_pitch, transform.intermediate_pitch):
                return vars.EIGHTH_NOTE_DOMINANT
            elif next_chord.indicates_subdominant(self.intermediate_pitch, transform.intermediate_pitch):
                return vars.EIGHTH_NOTE_SUBDOMINANT
            elif transforms_cause_parallel_movement(self, transform):
                return vars.EIGHTH_NOTE_PARALLEL

            return 0.0
        elif isinstance(transform, self.__class__):
            return vars.EIGHTH_NOTE_SAME

        return 0.0

    def is_syncopation(self):
        return False

    def crosses_bar_line(self):
        return False

    def causes_flickering(self):
        if self.position < config.resolution:
            return False

        one_whole_note_ago = self.sequence[self.position - config.resolution].pitch()
        one_half_note_ago = self.sequence[int(self.position - (config.resolution / 2))].pitch()

        pitch_at_position = self.sequence[self.position].pitch()

        return one_whole_note_ago == pitch_at_position and one_half_note_ago == self.intermediate_pitch \
            and one_whole_note_ago != one_half_note_ago


class MajorThirdScalarTransform(EighthNoteTransform):

    def __init__(self, position, sequence):
        EighthNoteTransform.__init__(self, position, sequence)

        this_note = sequence[position]
        next_note = sequence[position + config.resolution]
        self.intermediate_pitch = int((this_note.pitch() + next_note.pitch()) / 2)

        self.intrinsic_motion = vars.MAJOR_THIRD_SCALAR_MOTION
        self.intrinsic_musicality = self.__get_musicality()

    def __get_musicality(self):
        score = 0.0

        # no previous motion
        if self.position == 0:
            return vars.MAJOR_THIRD_SCALAR_BEAT_ONE

        last_beat = self.sequence.beat_at(self.position - config.resolution)

        score +=  vars.MAJOR_THIRD_SCALAR_CONTINUES_LINEARITY if last_beat.contains_linear_movement() \
            else vars.MAJOR_THIRD_SCALAR_DEFAULT_MUSICALITY

        score += vars.FLICKER_PENALTY if self.causes_flickering() else 0.0

        return score

    @staticmethod
    def applicable_at(position, sequence):
        try:
            sequence[position + (1 * config.resolution)]
        except IndexError:
            return False  # we've reached the end of the track

        this_note = sequence[position]
        next_note = sequence[position + config.resolution]
        intermediate_pitch = int((this_note.pitch() + next_note.pitch()) / 2)

        this_signature = config.key_signatures[position]

        return this_note.type == domain.Sample.TYPE_START and next_note.type == domain.Sample.TYPE_START \
            and abs(this_note.pitch() - next_note.pitch()) == 4 and intermediate_pitch in this_signature.scale()


class MinorThirdScalarTransform(EighthNoteTransform):

    def __init__(self, position, sequence):
        EighthNoteTransform.__init__(self, position, sequence)

        this_pitch = sequence[position].pitch()
        next_pitch = sequence[position + config.resolution].pitch()
        this_signature = config.key_signatures[position + config.resolution]

        intermediary_notes = this_pitch + 2, this_pitch + 1, this_pitch - 1, this_pitch - 2
        for note in intermediary_notes:
            if note in this_signature.scale() and min(this_pitch, next_pitch) < note < max(this_pitch, next_pitch):
                self.intermediate_pitch = note

        self.intrinsic_motion = vars.MINOR_THIRD_SCALAR_MOTION
        self.intrinsic_musicality = self.__get_musicality()

    def __get_musicality(self):
        score = 0.0

        # no previous motion
        if self.position == 0:
            return vars.MINOR_THIRD_SCALAR_BEAT_ONE

        last_beat = self.sequence.beat_at(self.position - config.resolution)

        score += vars.MINOR_THIRD_SCALAR_CONTINUES_LINEARITY if last_beat.contains_linear_movement() \
            else vars.MINOR_THIRD_SCALAR_DEFAULT_MUSICALITY

        score += vars.FLICKER_PENALTY if self.causes_flickering() else 0.0

        return score

    @staticmethod
    def applicable_at(position, sequence):
        try:
            sequence[position + (1 * config.resolution)]
        except IndexError:
            return False  # we've reached the end of the track

        this_note = sequence[position]
        next_note = sequence[position + config.resolution]
        intermediary_notes = this_note.pitch() + 2, this_note.pitch() + 1, this_note.pitch() - 1, this_note.pitch() - 2

        this_signature = config.key_signatures[position + config.resolution]

        if this_note.type == domain.Sample.TYPE_START and next_note.type == domain.Sample.TYPE_START \
                and abs(this_note.pitch() - next_note.pitch()) == 3:

            for note in intermediary_notes:
                if note in this_signature.scale():
                    return True
                
        return False


class ArpeggialTransform(EighthNoteTransform):

    def __init__(self, position, sequence):
        EighthNoteTransform.__init__(self, position, sequence)

        this_note = sequence[position]
        next_note = sequence[position + config.resolution]

        this_chord = config.chord_progression[position]
        next_chord = config.chord_progression[position + config.resolution]

        intermediary_notes = [i for i in range(min(this_note.pitch() + 1, next_note.pitch() + 1),
                                               max(this_note.pitch(), next_note.pitch()))]

        self.intrinsic_motion = vars.ARPEGGIAL_MOTION
        self.intrinsic_musicality = self.__get_musicality()

        for i in intermediary_notes:
            if i in this_chord and i in next_chord:
                self.intermediate_pitch = i
                break

    def __get_musicality(self):
        score = 0.0

        this_chord = config.chord_progression[self.position]
        next_chord = config.chord_progression[self.position + config.resolution]

        score += vars.ARPEGGIAL_SAME_CHORD if chords.same(this_chord, next_chord) \
            else vars.ARPEGGIAL_NEW_CHORD

        score += vars.FLICKER_PENALTY if self.causes_flickering() else 0.0

        return score

    @staticmethod
    def applicable_at(position, sequence):
        try:
            sequence[position + (1 * config.resolution)]
        except IndexError:
            return False  # we've reached the end of the track

        this_note = sequence[position]
        next_note = sequence[position + config.resolution]

        intermediary_notes = [i for i in range(min(this_note.pitch() + 1, next_note.pitch() + 1),
                                               max(this_note.pitch(), next_note.pitch()))]

        this_chord = config.chord_progression[position]
        next_chord = config.chord_progression[position + config.resolution]

        if this_chord == next_chord:
            return this_note.type == domain.Sample.TYPE_START and next_note.type == domain.Sample.TYPE_START \
                and next_note.pitch() == this_chord.note_above(this_chord.note_above(this_note.pitch()))
        else:
            if this_note.type == domain.Sample.TYPE_START and next_note.type == domain.Sample.TYPE_START:
                for i in intermediary_notes:
                    if i in this_chord and i in next_chord:
                        return True
        return False


class HalfStepNeighborTransform(EighthNoteTransform):

    def __init__(self, position, sequence):
        EighthNoteTransform.__init__(self, position, sequence)
        self.intrinsic_motion = vars.HALF_NEIGHBOR_MOTION

        this_pitch = sequence[position].pitch()
        this_sig = config.key_signatures[position]

        self.intermediate_pitch = this_pitch + 1 if this_pitch + 1 in this_sig.scale() else this_pitch - 1
        self.intrinsic_musicality = self.__get_musicality()

    def __get_musicality(self):
        score = 0.0

        this_chord = config.chord_progression[self.position]
        next_chord = config.chord_progression[self.position + config.resolution]

        score += vars.HALF_NEIGHBOR_SAME_CHORD if chords.same(this_chord, next_chord) \
            else vars.HALF_NEIGHBOR_DEFAULT_MUSICALITY

        score += vars.FLICKER_PENALTY if self.causes_flickering() else 0.0

        return score

    @staticmethod
    def applicable_at(position, sequence):
        try:
            sequence[position + (1 * config.resolution)]
        except IndexError:
            return False  # we've reached the end of the track

        this_note = sequence[position]
        next_note = sequence[position + config.resolution]

        this_sig = config.key_signatures[position]

        return this_note.note.midi() == next_note.note.midi() \
            and (this_note.type == domain.Sample.TYPE_START and next_note.type == domain.Sample.TYPE_START) \
            and (this_note.note.midi() - 1 in this_sig.scale() or this_note.note.midi() + 1 in this_sig.scale())


class WholeStepNeighborTransform(EighthNoteTransform):

    def __init__(self, position, sequence):
        EighthNoteTransform.__init__(self, position, sequence)
        self.intrinsic_motion = vars.WHOLE_NEIGHBOR_MOTION

        this_pitch = sequence[position].pitch()
        this_sig = config.key_signatures[position]

        self.intermediate_pitch = this_pitch + 2 if this_pitch + 2 in this_sig.scale() else this_pitch - 2
        self.intrinsic_musicality = self.__get_musicality()

    def __get_musicality(self):
        score = 0.0

        this_chord = config.chord_progression[self.position]
        next_chord = config.chord_progression[self.position + config.resolution]

        score += vars.WHOLE_NEIGHBOR_SAME_CHORD if chords.same(this_chord, next_chord) \
            else vars.WHOLE_NEIGHBOR_DEFAULT_MUSICALITY

        if self.causes_flickering():
            score += vars.FLICKER_PENALTY

        return score

    @staticmethod
    def applicable_at(position, sequence):
        try:
            sequence[position + (1 * config.resolution)]
        except IndexError:
            return False  # we've reached the end of the track

        this_note = sequence[position]
        next_note = sequence[position + config.resolution]

        this_sig = config.key_signatures[position]

        return this_note.note.midi() == next_note.note.midi() \
               and (this_note.type == domain.Sample.TYPE_START and next_note.type == domain.Sample.TYPE_START) \
               and (this_note.pitch() - 2 in this_sig.scale() or this_note.pitch() + 2 in this_sig.scale())


class ApproachTransform(EighthNoteTransform):

    def __init__(self, position, sequence):
        EighthNoteTransform.__init__(self, position, sequence)
        self.intrinsic_motion = vars.APPROACH_MOTION

        next_pitch = sequence[position + config.resolution].pitch()
        this_chord = config.chord_progression[position]

        self.intermediate_pitch = next_pitch + 1 if next_pitch + 1 in this_chord else next_pitch - 1
        self.intrinsic_musicality = self.__get_musicality()

    def __get_musicality(self):
        score = 0.0

        next_pitch = self.sequence[self.position + config.resolution].pitch()
        next_chord = config.chord_progression[self.position + config.resolution]
        next_key = config.key_signatures[self.position + config.resolution]

        if notes.same_species(next_pitch, next_chord.root):
            score += vars.APPROACH_KEY_CHANGE if notes.same_species(next_chord.root, next_key.root) \
                else vars.APPROACH_NEW_CHORD_ROOT
        else:
            score += vars.APPROACH_DEFAULT_MUSICALITY

        score += vars.FLICKER_PENALTY if self.causes_flickering() else 0.0

        return score

    @staticmethod
    def applicable_at(position, sequence):
        try:
            sequence[position + (1 * config.resolution)]
        except IndexError:
            return False  # we've reached the end of the track

        this_note = sequence[position]
        next_note = sequence[position + config.resolution]

        this_chord = config.chord_progression[position]

        return (next_note.pitch() - 1 in this_chord or next_note.pitch() + 1 in this_chord) \
            and (this_note.pitch() < next_note.pitch() - 2 or this_note.pitch() > next_note.pitch() + 2) \
            and next_note.pitch() != -1


def unique_chord_count(position, beats):
    return len(set(*[map(lambda key: config.chord_progression[key], range(position, position + beats * config.resolution))]))


def dissonant(pitch1, pitch2):
    return abs(pitch1 - pitch2) % 12 == 1


def transforms_cause_parallel_movement(transform1, transform2):
    if not isinstance(transform1, EighthNoteTransform) or not isinstance(transform2, EighthNoteTransform):
        return False

    f1 = transform1.sequence[transform1.position].pitch()
    f2 = transform2.sequence[transform2.position].pitch()

    i1 = transform1.intermediate_pitch
    i2 = transform2.intermediate_pitch

    return notes_cause_parallel_movement(f1, f2, i1, i2)


def notes_cause_parallel_movement(part1_first, part2_first, part1_second, part2_second):
    first_difference = abs(part1_first - part2_first)
    second_difference = abs(part1_second - part2_second)

    return first_difference == second_difference \
            and (first_difference == 0 or first_difference == 5 or first_difference == 7 or first_difference == 12)

