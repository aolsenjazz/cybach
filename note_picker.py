import notes
import parts
import motion
import transforms
import config
import vars
import chords


class NotePicker:
    def __init__(self):
        self.position = 0

    def compute(self, position):
        self.position = position

        chord = self.current_chord()
        candidates = self.get_candidate_matrix(chord)

        return self.compute_winner(candidates)

    def has_next(self):
        return self.position == len(config.soprano)

    def get_candidate_matrix(self, chord):
        alto_candidates = config.alto.part.available_notes(chord)
        tenor_candidates = config.tenor.part.available_notes(chord)
        bass_candidates = config.bass.part.available_notes(chord)

        alto_candidates.append(-1)  # -1 represents rest
        tenor_candidates.append(-1)  # -1 represents rest
        bass_candidates.append(-1)  # -1 represents rest

        matrix = combine_pitch_candidates(alto_candidates, tenor_candidates, bass_candidates)

        return self.filter_candidates(matrix)

    def filter_candidates(self, matrix):
        filtered = []
        sop_pitch = config.soprano[self.position].pitch()

        for g in matrix:
            if (g['bass'] < g['tenor'] < g['alto'] or g['tenor'] == -1 or g['alto'] == -1) \
                    and (g['alto'] < sop_pitch or sop_pitch == -1):
                filtered.append(g)

        return filtered

    def current_chord(self):
        return config.chord_progression[self.position]

    def compute_winner(self, candidates):
        high_score = -9999
        current_winner = None

        for candidate in candidates:
            candidate['soprano'] = (config.soprano[self.position].pitch())

            bass_score = get_bass_score(candidate['bass'], self.position, config.bass)
            tenor_score = get_tenor_score(candidate['tenor'], self.position, config.tenor)
            alto_score = get_alto_score(candidate['alto'], self.position, config.alto)
            harmony_score = get_harmony_score(candidate, self.current_chord())
            motion_score = get_motion_score(candidate, self.position, config.alto, config.tenor, config.bass)
            rest_penalty = get_rest_penalty(candidate)

            score = sum([bass_score, tenor_score, alto_score, harmony_score, motion_score, rest_penalty])

            if score > high_score:
                high_score = score
                current_winner = candidate

        return current_winner


def get_rest_penalty(candidate):
    return len([key for key in candidate.keys() if candidate[key] == -1]) * vars.REST_PENALTY


def get_motion_score(candidate, position, alto, tenor, bass):
    if position == 0:
        return 0.0

    last_alto = alto[position - config.resolution].pitch()
    last_tenor = tenor[position - config.resolution].pitch()
    last_bass = bass[position - config.resolution].pitch()

    score = 0.0

    if transforms.notes_cause_parallel_movement(last_alto, last_tenor, candidate['alto'], candidate['tenor']):
        score += vars.PARALLEL_MOVEMENT
    if transforms.notes_cause_parallel_movement(last_tenor, last_bass, candidate['tenor'], candidate['bass']):
        score += vars.PARALLEL_MOVEMENT
    if transforms.notes_cause_parallel_movement(last_bass, last_alto, candidate['bass'], candidate['alto']):
        score += vars.PARALLEL_MOVEMENT

    return score


def get_bass_score(candidate, position, sequence):
    score = 0.0
    low_thresh = parts.BASS.max_low
    high_thresh = parts.BASS.max_high

    score += threshold_encroachment_score(candidate, low_thresh, low_thresh + 4)
    score += threshold_encroachment_score(candidate, high_thresh, high_thresh - 4)
    score += preferred_register_score(candidate, high_thresh, high_thresh - 7)
    score += motion_tendency_score(candidate, position, sequence)
    score += linear_motion_score(candidate, position, sequence)
    score += flicker_avoidance_score(candidate, position, sequence)
    score += bass_note_tendency_score(candidate, position, sequence)

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

    if position >= config.resolution:
        last_note = sequence[position - config.resolution]

    if position >= config.resolution * 2:
        two_notes_ago = sequence[position - config.resolution * 2]

        if candidate == two_notes_ago.pitch() and candidate != last_note.pitch():
            score += vars.SAME_PITCH_AS_TWO_BEATS_AGO

    if position >= config.resolution * 3:
        three_notes_ago = sequence[position - config.resolution * 3]

        if candidate == two_notes_ago.pitch() and last_note.pitch() == three_notes_ago.pitch() \
                and candidate != last_note.pitch():
            score = vars.TWO_BEATS_REPEATED

    return score


def get_harmony_score(candidate, chord):
    base_position_chord = [notes.OCTAVES[n.species()][0] for n in chord.all()]
    base_position_candidate = [candidate[key] % 12 for key in candidate.keys()]
    added = []
    count = 0

    for pitch in base_position_candidate:
        if pitch % 12 in base_position_chord and pitch not in added:
            count += 1
            added.append(pitch)

    return count * vars.HARMONY


def bass_note_tendency_score(candidate, position, sequence):
    this_chord = config.chord_progression[position]
    score = 0.0

    # first bass note should definitely be the root
    if position == 0 and notes.species(candidate) == this_chord.bass_note.species():
        return vars.FIRST_BEAT_BASS_ROOT

    last_chord = config.chord_progression[position - config.resolution]

    # If beat one, we definitely want to hear the bass note
    if sequence.beat_at(position).is_first_beat():
        score += vars.FIRST_BEAT_BASS_NOTE

    # Chord is the same as the last chord, and this is root note. Less important as root was likely
    # already established
    if chords.same(last_chord, this_chord) and notes.same_species(candidate, this_chord.bass_note) and \
            this_chord.root_in_bass():
        score += vars.BASS_ROOT_SAME_CHORD

    # Bass note does not equal root note, therefore it is especially important
    if notes.same_species(candidate, this_chord.bass_note) and not this_chord.root_in_bass():
        score += vars.NON_ROOT_BASS_NOTE

    # new chord, we definitely want to hear the bass_note
    if not chords.same(last_chord, this_chord) and notes.same_species(candidate, this_chord.bass_note):
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
        return score

    last_pitch = sequence[position - config.resolution].pitch()

    if is_motion(candidate, last_pitch):
        score += sequence.motion_tendency - 0.5
    else:
        score += 0.5 - sequence.motion_tendency

    return score / vars.MOTION_TENDENCY_DIVISOR


def linear_motion_score(candidate, position, sequence):
    score = 0.0

    if position == 0:
        return score
    last_pitch = sequence[position - config.resolution].pitch()

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

    candidates = []
    for group in r:
        candidates.append({'alto': group[0], 'tenor': group[1], 'bass': group[2]})

    return candidates
