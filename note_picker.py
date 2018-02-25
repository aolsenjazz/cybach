import pitches
import parts
import transforms
import config
import chords
import vars

ALTO_POSITION = 0
TENOR_POSITION = 1
BASS_POSITION = 2
SOPRANO_POSITION = 3


class NotePicker:
    def __init__(self):
        self.beat = None

    def compute(self, beat):
        candidates = get_candidate_matrix(beat, config.soprano.pitch(beat.start()).midi())
        print len(candidates)
        winner = self.compute_winner(beat, candidates)

        return winner

    def current_chord(self):
        return config.chord_progression[self.beat]

    def compute_winner(self, beat, candidates):
        high_score = -9999
        current_winner = None

        for candidate in candidates:
            bass_score = get_bass_score(candidate[BASS_POSITION], beat, config.bass)
            # tenor_score = get_tenor_score(candidate[TENOR_POSITION], beat, config.tenor)
            # alto_score = get_alto_score(candidate[ALTO_POSITION], beat, config.alto)
            # harmony_score = get_harmony_score(candidate, self.current_chord())
            # motion_score = get_motion_score(candidate, self.beat, config.alto, config.tenor, config.bass)
            # rest_penalty = get_rest_penalty(candidate)
            #
            # score = sum([bass_score, tenor_score, alto_score, harmony_score, motion_score, rest_penalty])
            #
            # if score > high_score:
            #     high_score = score
            #     current_winner = candidate

        return current_winner


def get_rest_penalty(candidate):
    return len([c for c in candidate if c == -1]) * vars.REST_PENALTY


def get_motion_score(candidate, position, alto, tenor, bass):
    if position == 0:
        return 0.0

    # FIXME: using resolution again :)
    last_alto = alto[position - config.resolution].midi()
    last_tenor = tenor[position - config.resolution].midi()
    last_bass = bass[position - config.resolution].midi()

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


def get_bass_score(candidate, beat, sequence):
    score = 0.0
    low_thresh = parts.BASS.max_low
    high_thresh = parts.BASS.max_high
    # last_entity = sequence.entity(beat.start() - 1)
    # TODO: creating entities every time i need to calculate a score is killing the program now. precompute
    score += threshold_encroachment_score(candidate, low_thresh, low_thresh + 4)
    score += threshold_encroachment_score(candidate, high_thresh, high_thresh - 4)
    score += preferred_register_score(candidate, high_thresh, high_thresh - 7)
    score += bass_note_tendency_score(candidate, beat)

    # score += motion_tendency_score(candidate, beat, sequence)
    # score += linear_motion_score(candidate, last_entity, sequence)
    # score += flicker_avoidance_score(candidate, beat, sequence)

    return score


def get_tenor_score(candidate, beat, sequence):
    score = 0.0
    low_thresh = parts.TENOR.max_low
    high_thresh = parts.TENOR.max_high

    score += threshold_encroachment_score(candidate, low_thresh, low_thresh + 4)
    score += threshold_encroachment_score(candidate, high_thresh, high_thresh - 4)
    score += preferred_register_score(candidate, low_thresh, low_thresh + 7)

    score += motion_tendency_score(candidate, beat, sequence)
    score += linear_motion_score(candidate, beat, sequence)
    # score += flicker_avoidance_score(candidate, beat, sequence)

    return score


def get_alto_score(candidate, beat, sequence):
    score = 0.0
    low_thresh = parts.ALTO.max_low
    high_thresh = parts.ALTO.max_high

    score += threshold_encroachment_score(candidate, low_thresh, low_thresh + 4)
    score += threshold_encroachment_score(candidate, high_thresh, high_thresh - 4)
    score += preferred_register_score(candidate, high_thresh, high_thresh - 7)

    score += motion_tendency_score(candidate, beat, sequence)
    score += linear_motion_score(candidate, beat, sequence)
    # score += flicker_avoidance_score(candidate, beat, sequence)

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


def get_harmony_score(candidate, chord):
    base_position_chord = [pitches.OCTAVES[pitches.species(n)][0] for n in chord.all_octaves()]
    base_position_candidate = [c % 12 for c in candidate]
    added = []
    count = 0

    for pitch in base_position_candidate:
        if pitch % 12 in base_position_chord and pitch not in added:
            count += 1
            added.append(pitch)

    return count * vars.HARMONY


def bass_note_tendency_score(candidate, beat):
    this_chord = config.chord_progression[beat.start()]
    score = 0.0

    # first bass note should definitely be the root
    if beat.start() == 0 and pitches.same_species(candidate, this_chord.bass_note):
        return vars.FIRST_BEAT_BASS_ROOT

    last_chord = config.chord_progression[0 if beat.start() == 0 else beat.previous().start()]

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


def linear_motion_score(candidate, last_entity, sequence):
    score = 0.0

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
    current_chord = config.chord_progression[beat.start()]

    alto_candidates = config.alto.part().available_notes(current_chord) + [-1]
    tenor_candidates = config.tenor.part().available_notes(current_chord) + [-1]
    bass_candidates = config.bass.part().available_notes(current_chord) + [-1]

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
