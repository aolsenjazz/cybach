import chords
import config
import parts
import sequences
import pitches
import util
import transforms
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
        motion_score = get_motion_score(candidate, beat)
        rest_penalty = get_rest_penalty(candidate)

        return sum([bass_score, tenor_score, alto_score, harmony_score, motion_score, rest_penalty])


def get_rest_penalty(candidate):
    return len([c for c in candidate if c == -1]) * vars.REST_PENALTY


def get_motion_score(candidate, beat):
    last_beat = beat.previous()
    if last_beat is None:
        return 0.0

    last_alto = sequences.alto().pitch(last_beat.start()).midi()
    last_tenor = sequences.tenor().pitch(last_beat.start()).midi()
    last_bass = sequences.bass().pitch(last_beat.start()).midi()

    score = 0.0

    if transforms.notes_cause_parallel_movement(last_alto, last_tenor,
                                                candidate[ALTO_POSITION], candidate[TENOR_POSITION]):
        score += vars.PARALLEL_MOVEMENT
    if transforms.notes_cause_parallel_movement(last_tenor, last_bass,
                                                candidate[TENOR_POSITION], candidate[BASS_POSITION]):
        score += vars.PARALLEL_MOVEMENT
    if transforms.notes_cause_parallel_movement(last_bass, last_alto,
                                                candidate[BASS_POSITION], candidate[ALTO_POSITION]):
        score += vars.PARALLEL_MOVEMENT

    return score


def get_bass_score(candidate, beat):
    score = 0.0
    low_thresh = parts.BASS.max_low
    high_thresh = parts.BASS.max_high

    score += threshold_encroachment_score(candidate, low_thresh, low_thresh + 4)
    score += threshold_encroachment_score(candidate, high_thresh, high_thresh - 4)
    score += preferred_register_score(candidate, high_thresh, high_thresh - 7)
    score += bass_note_tendency_score(candidate, beat)

    score += motion_tendency_score(candidate, beat, sequences.bass())
    score += linear_motion_score(candidate, beat, sequences.bass())
    score += flicker_avoidance_score(candidate, beat, sequences.bass())

    return score


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


def flicker_avoidance_score(candidate, position, sequence):
    score = 0.0
    last_note = None
    two_notes_ago = None

    # FIXME: still using resolution
    if position >= config.resolution:
        last_note = sequence[position - config.resolution]

    if position >= config.resolution * 2:
        two_notes_ago = sequence[position - config.resolution * 2]

        if candidate == two_notes_ago.midi() and candidate != last_note.pitch():
            score += vars.SAME_PITCH_AS_TWO_BEATS_AGO

    if position >= config.resolution * 3:
        three_notes_ago = sequence[position - config.resolution * 3]

        if candidate == two_notes_ago.pitch() and last_note.pitch() == three_notes_ago.midi() \
                and candidate != last_note.pitch():
            score = vars.TWO_BEATS_REPEATED

    return score


def get_harmony_score(candidate, beat):
    chord = chords.get(beat.start())
    return len(set([pitch % 12 for pitch in candidate if pitch in chord.all_octaves()])) * vars.HARMONY


def bass_note_tendency_score(candidate, beat):
    this_chord = chords.get(beat.start())
    score = 0.0

    # first bass note should definitely be the root
    if beat.start() == 0 and pitches.same_species(candidate, this_chord.bass_note):
        return vars.FIRST_BEAT_BASS_ROOT

    last_chord = chords.get(0 if beat.start() == 0 else beat.previous().start())

    # If beat one, we want to hear the bass note
    if beat.first_beat():
        score += vars.FIRST_BEAT_BASS_NOTE

    # Chord is the same as the last chord, and this is root note. Less important as root was likely
    # already established
    if chords.same(last_chord, this_chord) and pitches.same_species(candidate, this_chord.bass_note) and \
            this_chord.root_in_bass():
        score += vars.BASS_ROOT_SAME_CHORD

    # Bass note does not equal root note, therefore it is especially important
    if pitches.same_species(candidate, this_chord.bass_note) and not this_chord.root_in_bass():
        score += vars.NON_ROOT_BASS_NOTE

    # new chord, we definitely want to hear the bass_note
    if not chords.same(last_chord, this_chord) and pitches.same_species(candidate, this_chord.bass_note):
        score += vars.BASS_NOTE_NEW_CHORD

    return score


def threshold_encroachment_score(val, threshold, soft_limit):
    score = 0.0

    if soft_limit < val <= threshold or threshold <= val < soft_limit:
        score += (2 ** abs(soft_limit - val)) * vars.THRESHOLD_ENCROACHMENT

    return score


def preferred_register_score(val, threshold, soft_limit):
    score = 0.0

    if soft_limit < val <= threshold or threshold <= val < soft_limit:
        score += abs(soft_limit - val) * vars.PREFERRED_REGISTER

    return score


def motion_tendency_score(candidate, beat, sequence):
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
