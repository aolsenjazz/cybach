import abc
import constants
import ts
import chords
import domain
import vars
import notes
from constants import RESOLUTION


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


class JoinTransform(MotionTransform):

    def __init__(self):
        MotionTransform.__init__(self)
        self.scale = self.SCALE_MACRO

    def synergy(self, transform):
        return vars.JOIN_SAME if isinstance(transform, self.__class__) else 0.0

    def apply(self):
        raise NotImplementedError


class TwoBeatJoinTransform(JoinTransform):

    def __init__(self, position, sequence, chord_progression):
        JoinTransform.__init__(self)

        self.sequence = sequence
        self.position = position
        self.intrinsic_motion = vars.TWO_BEAT_MOTION
        self.intrinsic_musicality = 0.0
        self.__set_musicality(position, sequence, chord_progression)

    def __set_musicality(self, position, sequence, chord_progression):
        sig = sequence.time_signatures[position]
        beat_index = sequence.beat_index_in_measure(position)

        if beat_index == 0:
            self.intrinsic_musicality += vars.TWO_BEAT_FIRST_BEAT
        elif ts.is_four_four(sig) or ts.is_two_four(sig):
            if beat_index % 2 == 1:
                self.intrinsic_musicality += vars.TWO_BEAT_WEAK_BEAT
        elif ts.is_three_four(sig) or ts.is_six_eight(sig):
            if beat_index % 2 == 0:
                self.intrinsic_musicality += vars.TWO_BEAT_WEAK_BEAT

        num_unique_chords = unique_chord_count(position, 1, chord_progression)
        self.intrinsic_musicality += vars.TWO_BEAT_MULTIPLE_CHORDS * num_unique_chords

    def apply(self):
        return apply_join(self.position, 2, self.sequence)

    @staticmethod
    def applicable_at(position, sequence):
        try:
            sequence[position + (1 * RESOLUTION)]
        except IndexError:
            return False  # we've reached the end of the track

        pitch_at_position = sequence[position].note.midi_value

        for i in range(position, position + (constants.QUARTER_NOTE * 2)):
            sample = sequence[i]

            if sample.note.midi_value != pitch_at_position:
                return False

        return True


class ThreeBeatJoinTransform(JoinTransform):

    def __init__(self, position, sequence, chord_progression):
        JoinTransform.__init__(self)

        self.sequence = sequence
        self.position = position
        self.intrinsic_motion = vars.THREE_BEAT_MOTION
        self.intrinsic_musicality = vars.THREE_BEAT_MUSICALITY
        self.__set_musicality(position, sequence, chord_progression)

    @staticmethod
    def applicable_at(position, sequence):
        try:
            sequence[position + (2 * RESOLUTION)]
        except IndexError:
            return False  # we've reached the end of the track

        pitch_at_position = sequence[position].note.midi_value

        for i in range(position, position + (constants.QUARTER_NOTE * 3)):
            sample = sequence[i]

            if sample.note.midi_value != pitch_at_position:
                return False

        return sequence[position].type == domain.Sample.TYPE_START

    def apply(self):
        return apply_join(self.position, 3, self.sequence)

    def __set_musicality(self, position, sequence, chord_progression):
        sig = sequence.time_signatures[position]
        beat_index = sequence.beat_index_in_measure(position)

        if beat_index == 0:
            self.intrinsic_musicality += vars.THREE_BEAT_FIRST_BEAT
        elif ts.is_four_four(sig) or ts.is_two_four(sig):
            if beat_index % 2 == 0:
                self.intrinsic_musicality += vars.THREE_BEAT_WEAK_BEAT_DENOM_MULTIPLE_OF_2
        elif ts.is_three_four(sig) or ts.is_six_eight(sig):
            self.intrinsic_musicality += vars.THREE_BEAT_WEAK_BEAT_DENOM_MULTIPLE_OF_3

        num_unique_chords = unique_chord_count(position, 2, chord_progression)
        self.intrinsic_musicality += vars.THREE_BEAT_MULTIPLE_CHORDS * num_unique_chords


class FourBeatJoinTransform(JoinTransform):

    def __init__(self, position, sequence, chord_progression):
        JoinTransform.__init__(self)

        self.sequence = sequence
        self.position = position
        self.intrinsic_motion = vars.FOUR_BEAT_MOTION
        self.intrinsic_musicality = vars.FOUR_BEAT_MUSICALITY
        self.__set_musicality(position, sequence, chord_progression)

    @staticmethod
    def applicable_at(position, sequence):
        try:
            sequence[position + (3 * RESOLUTION)]
        except IndexError:
            return False  # we've reached the end of the track

        pitch_at_position = sequence[position].note.midi_value

        for i in range(position, position + (constants.QUARTER_NOTE * 4)):
            sample = sequence[i]

            if sample.note.midi_value != pitch_at_position:
                return False

        return sequence[position].type == domain.Sample.TYPE_START

    def apply(self):
        return apply_join(self.position, 4, self.sequence)

    def __set_musicality(self, position, sequence, chord_progression):
        sig = sequence.time_signatures[position]
        beat_index = sequence.beat_index_in_measure(position)

        if beat_index == 0:
            self.intrinsic_musicality += vars.FOUR_BEAT_FIRST_BEAT
        elif ts.is_four_four(sig):
            if beat_index == 1:
                self.intrinsic_musicality += vars.FOUR_BEAT_SECOND_BEAT

        num_unique_chords = unique_chord_count(position, 3, chord_progression)
        self.intrinsic_musicality += vars.FOUR_BEAT_MULTIPLE_CHORDS * num_unique_chords


class FiveBeatJoinTransform(JoinTransform):

    def __init__(self, position, sequence, chord_progression):
        JoinTransform.__init__(self)

        self.sequence = sequence
        self.position = position
        self.intrinsic_motion = 0.18
        self.intrinsic_musicality = 0.2  # default
        self.__set_musicality(position, sequence, chord_progression)

    @staticmethod
    def applicable_at(position, sequence):
        try:
            sequence[position + (4 * RESOLUTION)]
        except IndexError:
            return False  # we've reached the end of the track

        pitch_at_position = sequence[position].note.midi_value

        for i in range(position, position + (constants.QUARTER_NOTE * 5)):
            sample = sequence[i]

            if sample.note.midi_value != pitch_at_position:
                return False

        return sequence[position].type == domain.Sample.TYPE_START

    def apply(self):
        return apply_join(self.position, 5, self.sequence)

    def __set_musicality(self, position, sequence, chord_progression):
        sig = sequence.time_signatures[position]
        beat_index = sequence.beat_index_in_measure(position)

        if beat_index == 0:
            self.intrinsic_musicality += vars.FIVE_BEAT_FIRST_BEAT
        elif ts.is_six_eight(sig):
            if beat_index == 4:
                self.intrinsic_musicality += vars.FIVE_BEAT_FIFTH_BEAT

        num_unique_chords = unique_chord_count(position, 4, chord_progression)
        self.intrinsic_musicality += vars.FIVE_BEAT_MULTIPLE_CHORDS * num_unique_chords


class SixBeatJoinTransform(JoinTransform):

    def __init__(self, position, sequence, chord_progression):
        JoinTransform.__init__(self)

        self.sequence = sequence
        self.position = position
        self.intrinsic_motion = vars.SIX_BEAT_MOTION
        self.intrinsic_musicality = vars.SIX_BEAT_MUSICALITY
        self.__set_musicality(position, sequence, chord_progression)

    def apply(self):
        return apply_join(self.position, 6, self.sequence)

    @staticmethod
    def applicable_at(position, sequence):
        try:
            sequence[position + (5 * RESOLUTION)]
        except IndexError:
            return False  # we've reached the end of the track

        pitch_at_position = sequence[position].note.midi_value

        for i in range(position, position + (constants.QUARTER_NOTE * 6)):
            sample = sequence[i]

            if sample.note.midi_value != pitch_at_position:
                return False

        return sequence[position].type == domain.Sample.TYPE_START

    def __set_musicality(self, position, sequence, chord_progression):
        sig = sequence.time_signatures[position]
        beat_index = sequence.beat_index_in_measure(position)

        if ts.is_six_eight(sig):
            if beat_index == 1:
                self.intrinsic_musicality += vars.SIX_BEAT_SECOND_BEAT
            else:
                self.intrinsic_musicality += vars.SIX_BEAT_ANY_OTHER_BEAT
        elif ts.is_three_four(sig):
            self.intrinsic_musicality += vars.SIX_BEAT_THREE_FOUR

        num_unique_chords = unique_chord_count(position, 5, chord_progression)
        self.intrinsic_musicality += vars.SIX_BEAT_MULTIPLE_CHORDS * num_unique_chords


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


class EighthNoteTransform(MotionTransform):

    def __init__(self, position, sequence, key_signatures, chord_progression):
        MotionTransform.__init__(self)

        self.position = position
        self.sequence = sequence
        self.key_signatures = key_signatures
        self.chord_progression = chord_progression
        self.intermediate_pitch = -1

    def apply(self):
        half_way = self.position + (RESOLUTION / 2)
        for i in range(half_way, self.position + RESOLUTION):
            if i == half_way:
                self.sequence[i - 1] = domain.Sample(self.sequence[i - 1].pitch(), domain.Sample.TYPE_END)
                self.sequence[i] = domain.Sample(self.intermediate_pitch, domain.Sample.TYPE_START)
            elif i == self.position + RESOLUTION - 1:
                self.sequence[i] = domain.Sample(self.intermediate_pitch, domain.Sample.TYPE_END)
            else:
                self.sequence[i] = domain.Sample(self.intermediate_pitch, domain.Sample.TYPE_SUSTAIN)

        return self.sequence.samples

    def synergy(self, transform):
        if isinstance(transform, EighthNoteTransform) and not isinstance(transform, self.__class__):
            next_chord = self.chord_progression[self.position + RESOLUTION]

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


class MajorThirdScalarTransform(EighthNoteTransform):

    def __init__(self, position, sequence, key_signatures, chord_progression):
        EighthNoteTransform.__init__(self, position, sequence, key_signatures, chord_progression)
        self.intrinsic_motion = vars.MAJOR_THIRD_SCALAR_MOTION
        self.intrinsic_musicality = self.__get_musicality()

        this_note = sequence[position]
        next_note = sequence[position + RESOLUTION]
        self.intermediate_pitch = (this_note.pitch() + next_note.pitch()) / 2

    def __get_musicality(self):
        # no previous motion
        if self.position == 0:
            return vars.MAJOR_THIRD_SCALAR_BEAT_ONE

        last_beat = self.sequence.beat_at(self.position - RESOLUTION)

        return vars.MAJOR_THIRD_SCALAR_CONTINUES_LINEARITY if last_beat.contains_linear_movement() \
            else vars.MAJOR_THIRD_SCALAR_DEFAULT_MUSICALITY

    @staticmethod
    def applicable_at(position, sequence, key_signatures):
        try:
            sequence[position + (1 * RESOLUTION)]
        except IndexError:
            return False  # we've reached the end of the track

        this_note = sequence[position]
        next_note = sequence[position + RESOLUTION]
        intermediate_pitch = (this_note.pitch() + next_note.pitch()) / 2

        this_signature = key_signatures[position]

        return this_note.type == domain.Sample.TYPE_START and next_note.type == domain.Sample.TYPE_START \
            and abs(this_note.pitch() - next_note.pitch()) == 4 and intermediate_pitch in this_signature.scale()


class MinorThirdScalarTransform(EighthNoteTransform):

    def __init__(self, position, sequence, key_signatures, chord_progression):
        EighthNoteTransform.__init__(self, position, sequence, key_signatures, chord_progression)
        self.intrinsic_motion = vars.MINOR_THIRD_SCALAR_MOTION
        self.intrinsic_musicality = self.__get_musicality()

        this_pitch = sequence[position].pitch()
        next_pitch = sequence[position + RESOLUTION].pitch()
        this_signature = key_signatures[position + RESOLUTION]

        intermediary_notes = this_pitch + 2, this_pitch + 1, this_pitch - 1, this_pitch - 2
        for note in intermediary_notes:
            if note in this_signature.scale() and min(this_pitch, next_pitch) < note < max(this_pitch, next_pitch):
                self.intermediate_pitch = note

    def __get_musicality(self):
        # no previous motion
        if self.position == 0:
            return vars.MINOR_THIRD_SCALAR_BEAT_ONE

        last_beat = self.sequence.beat_at(self.position - RESOLUTION)

        return vars.MINOR_THIRD_SCALAR_CONTINUES_LINEARITY if last_beat.contains_linear_movement() \
            else vars.MINOR_THIRD_SCALAR_DEFAULT_MUSICALITY

    @staticmethod
    def applicable_at(position, sequence, key_signatures):
        try:
            sequence[position + (1 * RESOLUTION)]
        except IndexError:
            return False  # we've reached the end of the track

        this_note = sequence[position]
        next_note = sequence[position + RESOLUTION]
        intermediary_notes = this_note.pitch() + 2, this_note.pitch() + 1, this_note.pitch() - 1, this_note.pitch() - 2

        this_signature = key_signatures[position + RESOLUTION]

        if this_note.type == domain.Sample.TYPE_START and next_note.type == domain.Sample.TYPE_START \
                and abs(this_note.pitch() - next_note.pitch()) == 3:

            for note in intermediary_notes:
                if note in this_signature.scale():
                    return True
                
        return False


class ArpeggialTransform(EighthNoteTransform):

    def __init__(self, position, sequence, key_signatures, chord_progression):
        EighthNoteTransform.__init__(self, position, sequence, key_signatures, chord_progression)
        self.intrinsic_motion = vars.ARPEGGIAL_MOTION
        self.intrinsic_musicality = self.__get_musicality()

        this_note = sequence[position]
        next_note = sequence[position + RESOLUTION]

        this_chord = chord_progression[position]
        next_chord = chord_progression[position + RESOLUTION]

        intermediary_notes = [i for i in range(min(this_note.pitch() + 1, next_note.pitch() + 1),
                                               max(this_note.pitch(), next_note.pitch()))]

        for i in intermediary_notes:
            if i in this_chord and i in next_chord:
                self.intermediate_pitch = i
                break

    def __get_musicality(self):
        this_chord = self.chord_progression[self.position]
        next_chord = self.chord_progression[self.position + RESOLUTION]

        return vars.ARPEGGIAL_SAME_CHORD if chords.same(this_chord, next_chord) \
            else vars.ARPEGGIAL_DEFAULT_MUSICALITY

    @staticmethod
    def applicable_at(position, sequence, chord_progression):
        try:
            sequence[position + (1 * RESOLUTION)]
        except IndexError:
            return False  # we've reached the end of the track

        this_note = sequence[position]
        next_note = sequence[position + RESOLUTION]

        intermediary_notes = [i for i in range(min(this_note.pitch() + 1, next_note.pitch() + 1),
                                               max(this_note.pitch(), next_note.pitch()))]

        this_chord = chord_progression[position]
        next_chord = chord_progression[position + RESOLUTION]

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

    def __init__(self, position, sequence, key_signatures, chord_progression):
        EighthNoteTransform.__init__(self, position, sequence, key_signatures, chord_progression)
        self.intrinsic_motion = vars.HALF_NEIGHBOR_MOTION
        self.intrinsic_musicality = self.__get_musicality()

        this_pitch = sequence[position].pitch()
        this_sig = key_signatures[position]

        self.intermediate_pitch = this_pitch + 1 if this_pitch + 1 in this_sig.scale() else this_pitch - 1

    def __get_musicality(self):
        this_chord = self.chord_progression[self.position]
        next_chord = self.chord_progression[self.position + RESOLUTION]

        return vars.HALF_NEIGHBOR_SAME_CHORD if chords.same(this_chord, next_chord) \
            else vars.HALF_NEIGHBOR_DEFAULT_MUSICALITY

    @staticmethod
    def applicable_at(position, sequence, key_signatures):
        try:
            sequence[position + (1 * RESOLUTION)]
        except IndexError:
            return False  # we've reached the end of the track

        this_note = sequence[position]
        next_note = sequence[position + RESOLUTION]

        this_sig = key_signatures[position]

        return this_note.note.midi_value == next_note.note.midi_value \
            and (this_note.type == domain.Sample.TYPE_START and next_note.type == domain.Sample.TYPE_START) \
            and (this_note.note.midi_value - 1 in this_sig.scale() or this_note.note.midi_value + 1 in this_sig.scale())


class WholeStepNeighborTransform(EighthNoteTransform):

    def __init__(self, position, sequence, key_signatures, chord_progression):
        EighthNoteTransform.__init__(self, position, sequence, key_signatures, chord_progression)
        self.intrinsic_motion = vars.WHOLE_NEIGHBOR_MOTION
        self.intrinsic_musicality = self.__get_musicality()

        this_pitch = sequence[position].pitch()
        this_sig = key_signatures[position]

        self.intermediate_pitch = this_pitch + 2 if this_pitch + 2 in this_sig.scale() else this_pitch - 2

    def __get_musicality(self):
        this_chord = self.chord_progression[self.position]
        next_chord = self.chord_progression[self.position + RESOLUTION]

        return vars.WHOLE_NEIGHBOR_SAME_CHORD if chords.same(this_chord, next_chord) \
            else vars.WHOLE_NEIGHBOR_DEFAULT_MUSICALITY

    @staticmethod
    def applicable_at(position, sequence, key_signatures):
        try:
            sequence[position + (1 * RESOLUTION)]
        except IndexError:
            return False  # we've reached the end of the track

        this_note = sequence[position]
        next_note = sequence[position + RESOLUTION]

        this_sig = key_signatures[position]

        return this_note.note.midi_value == next_note.note.midi_value \
               and (this_note.type == domain.Sample.TYPE_START and next_note.type == domain.Sample.TYPE_START) \
               and (this_note.pitch() - 2 in this_sig.scale() or this_note.pitch() + 2 in this_sig.scale())


class ApproachTransform(EighthNoteTransform):

    def __init__(self, position, sequence, key_signatures, chord_progression):
        EighthNoteTransform.__init__(self, position, sequence, key_signatures, chord_progression)
        self.intrinsic_motion = vars.APPROACH_MOTION
        self.intrinsic_musicality = self.__get_musicality()

        next_pitch = sequence[position + RESOLUTION].pitch()
        this_chord = chord_progression[position]

        self.intermediate_pitch = next_pitch + 1 if next_pitch + 1 in this_chord else next_pitch - 1

    def __get_musicality(self):
        next_pitch = self.sequence[self.position + RESOLUTION].pitch()
        next_chord = self.chord_progression[self.position + RESOLUTION]
        next_key = self.key_signatures[self.position + RESOLUTION]
        if notes.same_species(next_pitch, next_chord.root):
            return vars.APPROACH_KEY_CHANGE if notes.same_species(next_chord.root, next_key.root) \
                else vars.APPROACH_NEW_CHORD_ROOT
        else:
            return vars.APPROACH_DEFAULT_MUSICALITY

    @staticmethod
    def applicable_at(position, sequence, chord_progression):
        try:
            sequence[position + (1 * RESOLUTION)]
        except IndexError:
            return False  # we've reached the end of the track

        this_note = sequence[position]
        next_note = sequence[position + RESOLUTION]

        this_chord = chord_progression[position]

        return (next_note.pitch() - 1 in this_chord or next_note.pitch() + 1 in this_chord) \
            and (this_note.pitch() < next_note.pitch() - 2 or this_note.pitch() > next_note.pitch() + 2) \
            and next_note.pitch() != -1


def unique_chord_count(position, beats, chord_progression):
    return len(set(*[map(lambda key: chord_progression[key], range(position, position + beats * RESOLUTION))]))


def apply_join(position, beats, sequence):
    for i in range(position, position + beats * RESOLUTION):
        if i == position:
            continue
        elif i == position + (beats * RESOLUTION) - 1:
            sequence[i].type = domain.Sample.TYPE_END
        else:
            sequence[i].type = domain.Sample.TYPE_SUSTAIN

    return sequence.samples


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

