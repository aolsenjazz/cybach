import chords
import config
import entity_util
import parts
import pitches
import sequences
import transforms
import util
import vars

ALTO_POSITION = 0
TENOR_POSITION = 1
BASS_POSITION = 2
SOPRANO_POSITION = 3


class NotePicker:
    def __init__(self):
        self.beat = None

    def compute(self, beat):
        if sequences.soprano().is_rest(beat.start()):
            soprano_pitch = -1
        else:
            soprano_pitch = sequences.soprano().pitch(beat.start()).midi()

        candidates = get_candidate_matrix(beat, soprano_pitch)
        scored = {tuple(candidate): self.score(beat, candidate) for candidate in candidates}

        return util.key_for_highest_value(scored)

    def score(self, beat, candidate):
        bass_score = get_bass_score(candidate[BASS_POSITION], beat)
        tenor_score = get_tenor_score(candidate[TENOR_POSITION], beat)
        alto_score = get_alto_score(candidate[ALTO_POSITION], beat)
        harmony_score = get_harmony_score(candidate, beat)
        duplicate_penalty = get_duplicate_penalty(candidate)
        rest_penalty = get_rest_penalty(candidate)
        motion_score = parallel_motion_score(candidate, beat, sequences.soprano(), sequences.alto(),
                                             sequences.tenor(), sequences.bass())

        return sum([bass_score, tenor_score, alto_score, harmony_score, motion_score, rest_penalty, duplicate_penalty])


def get_duplicate_penalty(candidate):
    return vars.duplicate(len(candidate) - len(set(candidate)))


def get_rest_penalty(candidate):
    return len([c for c in candidate if c == -1]) * vars.REST_PENALTY


def parallel_motion_score(candidate, beat, soprano, alto, tenor, bass):
    last_beat = beat.previous()
    if last_beat is None:
        return 0.0

    last_soprano = soprano.pitch(last_beat.start()).midi()
    last_alto = alto.pitch(last_beat.start()).midi()
    last_tenor = tenor.pitch(last_beat.start()).midi()
    last_bass = bass.pitch(last_beat.start()).midi()
    this_soprano = soprano.pitch(beat.start()).midi()

    score = 0.0

    if pitches.parallel_movement(last_alto, candidate[ALTO_POSITION], last_soprano, this_soprano):
        score += vars.PARALLEL_MOVEMENT
    if pitches.parallel_movement(last_tenor, candidate[TENOR_POSITION], last_soprano, this_soprano):
        score += vars.PARALLEL_MOVEMENT
    if pitches.parallel_movement(last_bass, candidate[BASS_POSITION], last_soprano, this_soprano):
        score += vars.PARALLEL_MOVEMENT
    if pitches.parallel_movement(last_alto, candidate[ALTO_POSITION], last_tenor, candidate[TENOR_POSITION]):
        score += vars.PARALLEL_MOVEMENT
    if pitches.parallel_movement(last_tenor,candidate[TENOR_POSITION], last_bass, candidate[BASS_POSITION]):
        score += vars.PARALLEL_MOVEMENT
    if pitches.parallel_movement(last_bass, candidate[BASS_POSITION], last_alto, candidate[ALTO_POSITION]):
        score += vars.PARALLEL_MOVEMENT

    return score


def get_bass_score(candidate, beat):
    low_thresh = parts.BASS.max_low
    high_thresh = parts.BASS.max_high

    bottom_encroachment = threshold_encroachment_score(candidate, low_thresh, low_thresh + 4)
    top_encroachment =  threshold_encroachment_score(candidate, high_thresh, high_thresh - 4)
    preferred_register = preferred_register_score(candidate, high_thresh, high_thresh - 7)
    bass_note_tendency = bass_note_tendency_score(candidate, beat)
    preemption = preemption_penalty(candidate, beat)

    motion_tendency = motion_tendency_score(candidate, beat, sequences.bass())
    linear_motion = linear_motion_score(candidate, beat, sequences.bass())
    flicker_avoidance = flicker_avoidance_score(candidate, beat, sequences.bass())

    return sum((bottom_encroachment, top_encroachment, preferred_register, bass_note_tendency, preemption,
                motion_tendency, linear_motion, flicker_avoidance))


def get_tenor_score(candidate, beat):
    score = 0.0
    low_thresh = parts.TENOR.max_low
    high_thresh = parts.TENOR.max_high

    score += threshold_encroachment_score(candidate, low_thresh, low_thresh + 4)
    score += threshold_encroachment_score(candidate, high_thresh, high_thresh - 4)
    score += preferred_register_score(candidate, low_thresh, low_thresh + 7)

    score += motion_tendency_score(candidate, beat, sequences.tenor())
    score += linear_motion_score(candidate, beat, sequences.tenor())
    score += flicker_avoidance_score(candidate, beat, sequences.tenor())

    return score


def get_alto_score(candidate, beat):
    score = 0.0
    low_thresh = parts.ALTO.max_low
    high_thresh = parts.ALTO.max_high

    score += threshold_encroachment_score(candidate, low_thresh, low_thresh + 4)
    score += threshold_encroachment_score(candidate, high_thresh, high_thresh - 4)
    score += preferred_register_score(candidate, high_thresh, high_thresh - 7)

    score += motion_tendency_score(candidate, beat, sequences.alto())
    score += linear_motion_score(candidate, beat, sequences.alto())
    score += flicker_avoidance_score(candidate, beat, sequences.alto())

    return score


def preemption_penalty(candidate, beat):
    if beat.end() == config.song_length:
        return 0.0

    this_chord = chords.get(beat.start())
    next_chord = chords.get(beat.next().start())

    if pitches.same_species(candidate, next_chord.root()) and this_chord != next_chord:
        return vars.PREEMPTION

    return 0.0


def flicker_avoidance_score(candidate, beat, sequence):
    candidate_entity = sequences.Note(sequence, beat.start(), beat.end(), candidate)

    flicker_count = 0
    current_entity = candidate_entity
    is_flicker = True
    while current_entity.is_note() and current_entity.start() > 0 and is_flicker:
        is_flicker = False
        last_entity = current_entity.previous_entity()
        if entity_util.is_flicker(current_entity, last_entity, last_entity.previous_entity()):
            flicker_count += 1
            is_flicker = True
        current_entity = last_entity

    return flicker_count * vars.FLICKER_COEF


def get_harmony_score(candidate, beat):
    unique_pitches_score = unique_pitch_score(candidate, beat)
    third_preference = third_preference_score(candidate, beat)

    return sum((unique_pitches_score, third_preference))


def unique_pitch_score(candidate, beat):
    chord = chords.get(beat.start())
    unique_pitches = len(set([pitch % 12 for pitch in candidate if pitch in chord.all_octaves()]))
    return vars.unique_pitch_score(unique_pitches)


def third_preference_score(candidate, beat):
    chord = chords.get(beat.start())
    if isinstance(chord, chords.SevenChord):
        if [pitch for pitch in candidate if pitches.same_species(pitch, chord.three())]:
            return vars.THIRD_PREFERENCE

    return 0.0


def bass_note_tendency_score(candidate, beat):
    this_chord = chords.get(beat.start())
    score = 0.0

    candidate_is_this_chord_bass_note = pitches.same_species(candidate, this_chord.bass_note)

    # first bass note should definitely be the root
    if beat.start() == 0 and candidate_is_this_chord_bass_note:
        return vars.FIRST_BEAT_BASS_ROOT

    # If beat one, we want to hear the bass note
    if beat.first_beat() and candidate_is_this_chord_bass_note:
        score += vars.FIRST_BEAT_BASS_NOTE

    last_chord = chords.get(0 if beat.start() == 0 else beat.previous().start())
    this_and_next_chord_are_same = chords.same(last_chord, this_chord)
    this_chord_root_in_bass = this_chord.root_in_bass()

    # Chord is the same as the last chord, and this is root note. Less important as root was likely
    # already established
    if this_and_next_chord_are_same and candidate_is_this_chord_bass_note and this_chord_root_in_bass:
        score += vars.BASS_ROOT_SAME_CHORD

    # Bass note does not equal root note, therefore it is especially important
    if pitches.same_species(candidate, this_chord.bass_note) and not this_chord_root_in_bass:
        score += vars.NON_ROOT_BASS_NOTE

    # new chord, we definitely want to hear the bass_note
    if not this_and_next_chord_are_same and candidate_is_this_chord_bass_note:
        score += vars.BASS_NOTE_NEW_CHORD

    return score


def threshold_encroachment_score(val, threshold, soft_limit):
    if soft_limit < val <= threshold or threshold <= val < soft_limit:
        return (2 ** abs(soft_limit - val)) * vars.THRESHOLD_ENCROACHMENT

    return 0.0


def preferred_register_score(val, threshold, soft_limit):
    if soft_limit < val <= threshold or threshold <= val < soft_limit:
        return abs(soft_limit - val) * vars.PREFERRED_REGISTER

    return 0.0


def motion_tendency_score(candidate, beat, sequence):
    if beat.start() == 0:
        return 0.0

    score = 0.0
    last_entity = sequence.entity(beat.start() - 1)

    if is_motion(candidate, last_entity):
        score += sequence.motion_tendency() - 0.5
    else:
        score += 0.5 - sequence.motion_tendency()

    return score / vars.MOTION_TENDENCY_DIVISOR


def linear_motion_score(candidate, beat, sequence):
    score = 0.0
    last_entity = sequence.entity(beat.start() - 1)

    if is_linear_motion(candidate, last_entity):
        score += vars.LINEAR_MOTION

    return score


def is_motion(pitch1, last_entity):
    return last_entity.is_note() and last_entity.pitch().midi() - pitch1 != 0


def is_linear_motion(candidate, last_entity):
    return last_entity.is_note() \
           and abs(candidate - last_entity.pitch().midi()) < 3 \
           and candidate - last_entity.pitch().midi() != 0


def parts_dont_cross(group, soprano_value):
    return (group[BASS_POSITION] <= group[TENOR_POSITION] or group[TENOR_POSITION] == -1) and \
           (group[TENOR_POSITION] <= group[ALTO_POSITION] or group[ALTO_POSITION] == -1) and \
           (group[ALTO_POSITION] <= soprano_value or soprano_value == -1)


def get_candidate_matrix(beat, soprano_value):
    current_chord = chords.get(beat.start())

    alto_candidates = sequences.alto().part().available_notes(current_chord) + [-1]
    tenor_candidates = sequences.tenor().part().available_notes(current_chord) + [-1]
    bass_candidates = sequences.bass().part().available_notes(current_chord) + [-1]

    return [g + [soprano_value] for g
            in combine_pitch_candidates(alto_candidates, tenor_candidates, bass_candidates)
            if parts_dont_cross(g, soprano_value)]


def combine_pitch_candidates(*args):
    r = [[]]
    for x in args:
        t = []
        for y in x:
            for i in r:
                t.append(i + [y])
        r = t
    return r
