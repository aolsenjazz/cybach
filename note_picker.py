import pitches
import parts
import transforms
import config
import chords
import vars

ALTO_POSITION = 0
TENOR_POSITION = 1
BASS_POSITION = 2


class NotePicker:
    def __init__(self):
        self.beat = None

    def compute(self, beat):
        self.beat = beat

        chord = self.current_chord()
        candidates = self.get_candidate_matrix(chord)
        winner = self.compute_winner(candidates)

        return winner

    def get_candidate_matrix(self, chord):
        alto_candidates = config.alto.part().available_notes(chord)
        tenor_candidates = config.tenor.part().available_notes(chord)
        bass_candidates = config.bass.part().available_notes(chord)

        alto_candidates.append(-1)  # -1 represents rest
        tenor_candidates.append(-1)  # -1 represents rest
        bass_candidates.append(-1)  # -1 represents rest

        matrix = combine_pitch_candidates(alto_candidates, tenor_candidates, bass_candidates)

        return self.filter_candidates(matrix)

    def filter_candidates(self, matrix):
        filtered = []
        sop_pitch = config.soprano.midi(self.beat.start())

        for g in matrix:
            if (g[BASS_POSITION] < g[TENOR_POSITION] < g[ALTO_POSITION]
                or g[TENOR_POSITION] == -1 or g[ALTO_POSITION] == -1) \
                    and (g[ALTO_POSITION] < sop_pitch or sop_pitch == -1):
                filtered.append(g)

        return filtered

    def current_chord(self):
        return config.chord_progression[self.beat]

    def compute_winner(self, candidates):
        high_score = -9999
        current_winner = None

        for candidate in candidates:
            candidate.append(config.soprano[self.beat.start()].midi())

            bass_score = get_bass_score(candidate[BASS_POSITION], self.beat, config.bass)
            # tenor_score = get_tenor_score(candidate[TENOR_POSITION], self.beat, config.tenor)
            # alto_score = get_alto_score(candidate[ALTO_POSITION], self.beat, config.alto)
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

    score += threshold_encroachment_score(candidate, low_thresh, low_thresh + 4)
    score += threshold_encroachment_score(candidate, high_thresh, high_thresh - 4)
    score += preferred_register_score(candidate, high_thresh, high_thresh - 7)
    score += motion_tendency_score(candidate, beat.start(), sequence)
    score += linear_motion_score(candidate, beat.start(), sequence)
    score += flicker_avoidance_score(candidate, beat.start(), sequence)
    score += bass_note_tendency_score(candidate, beat)

    return score


def get_tenor_score(candidate, position, sequence):
    score = 0.0
    low_thresh = parts.TENOR.max_low
    high_thresh = parts.TENOR.max_high

    score += threshold_encroachment_score(candidate, low_thresh, low_thresh + 4)
    score += threshold_encroachment_score(candidate, high_thresh, high_thresh - 4)
    score += preferred_register_score(candidate, low_thresh, low_thresh + 7)
    score += motion_tendency_score(candidate, position, sequence)
    score += linear_motion_score(candidate, position, sequence)
    score += flicker_avoidance_score(candidate, position, sequence)

    return score


def get_alto_score(candidate, position, sequence):
    score = 0.0
    low_thresh = parts.ALTO.max_low
    high_thresh = parts.ALTO.max_high

    score += threshold_encroachment_score(candidate, low_thresh, low_thresh + 4)
    score += threshold_encroachment_score(candidate, high_thresh, high_thresh - 4)
    score += preferred_register_score(candidate, high_thresh, high_thresh - 7)
    score += motion_tendency_score(candidate, position, sequence)
    score += linear_motion_score(candidate, position, sequence)
    score += flicker_avoidance_score(candidate, position, sequence)

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
    if beat.start() == 0 and pitches.species(candidate) == this_chord.bass_note.species():
        return vars.FIRST_BEAT_BASS_ROOT

    # FIXME - config.resolution is an old artifact
    last_chord = config.chord_progression[beat.start() - config.resolution]

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


def motion_tendency_score(candidate, position, sequence):
    score = 0.0

    if position == 0:
        return 0.0

    # Fixme - using resolution
    last_pitch = sequence[position - config.resolution].midi()

    if is_motion(candidate, last_pitch):
        score += sequence.motion_tendency() - 0.5
    else:
        score += 0.5 - sequence.motion_tendency()

    return score / vars.MOTION_TENDENCY_DIVISOR


def linear_motion_score(candidate, position, sequence):
    score = 0.0

    if position == 0:
        return score
    # Fixme - using resolution
    last_pitch = sequence[position - config.resolution].midi()

    if is_linear_motion(candidate, last_pitch):
        score += vars.LINEAR_MOTION

    return score


def is_motion(pitch1, pitch2):
    return pitch2 - pitch1 != 0


def is_linear_motion(pitch1, pitch2):
    return abs(pitch1 - pitch2) < 3 and pitch1 - pitch2 != 0


def combine_pitch_candidates(*args):
    r = [[]]
    for x in args:
        t = []
        for y in x:
            for i in r:
                t.append(i + [y])
        r = t
    return r
