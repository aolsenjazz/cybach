import notes
import parts
import motion
import transforms
from constants import *


class NotePicker:
    def __init__(self, soprano, alto, tenor, bass, key_signatures, chord_progression):
        self.soprano = soprano
        self.alto = alto
        self.tenor = tenor
        self.bass = bass
        self.key_signatures = key_signatures
        self.chord_progression = chord_progression
        self.position = 0

    def compute_next(self):
        chord = self.chord_progression[self.position]

        candidates = self.get_candidate_matrix(chord)
        winner = self.compute_winner(candidates)

        self.position += RESOLUTION

        return winner

    def get_candidate_matrix(self, chord):
        alto_candidates = self.alto.part.available_notes(chord)
        alto_candidates.append(-1)  # -1 represents rest

        tenor_candidates = self.tenor.part.available_notes(chord)
        tenor_candidates.append(-1)  # -1 represents rest

        bass_candidates = self.bass.part.available_notes(chord)
        bass_candidates.append(-1)  # -1 represents rest

        matrix = motion.combinations(bass_candidates, tenor_candidates, alto_candidates)

        return self.filter_candidates(matrix)

    def filter_candidates(self, matrix):
        filtered = []

        for g in matrix:
            if (g[0] < g[1] or g[1] == -1) and (g[2] < self.soprano[self.position].pitch() or g[2] == -1) \
                    or (g[0] < g[1] or g[1] == -1) and (self.soprano[self.position].pitch() == -1):
                filtered.append(g)

        return filtered

    def current_chord(self):
        return self.chord_progression[self.position]

    def compute_winner(self, candidates):
        high_score = -9999
        current_winner = None

        for candidate in candidates:
            candidate.append(self.soprano[self.position].pitch())

            bass_score = get_bass_score(candidate[0], self.position, self.bass, self.chord_progression)
            tenor_score = get_tenor_score(candidate[1], self.position, self.tenor, self.chord_progression)
            alto_score = get_alto_score(candidate[2], self.position, self.alto, self.chord_progression)
            shape_score = get_shape_score(candidate)
            harmony_score = get_harmony_score(candidate, self.current_chord())
            motion_score = get_motion_score(candidate, self.position, self.alto, self.tenor, self.bass)

            score = sum([bass_score, tenor_score, alto_score, shape_score, harmony_score, motion_score])

            if score > high_score:
                high_score = score
                current_winner = candidate

        return current_winner


def get_motion_score(candidate, position, alto, tenor, bass):
    if position == 0:
        return 0

    last_alto = alto[position - RESOLUTION].pitch()
    last_tenor = tenor[position - RESOLUTION].pitch()
    last_bass = bass[position - RESOLUTION].pitch()

    score = 0.0

    if transforms.notes_cause_parallel_movement(last_alto, last_tenor, candidate[2], candidate[1]):
        score += -0.20
    if transforms.notes_cause_parallel_movement(last_tenor, last_bass, candidate[1], candidate[0]):
        score += -0.20
    if transforms.notes_cause_parallel_movement(last_bass, last_alto, candidate[0], candidate[2]):
        score += -0.20

    return score


def get_bass_score(candidate, position, sequence, chord_progression):
    score = 0.0
    low_thresh = parts.BASS.max_low
    high_thresh = parts.BASS.max_high

    score += threshold_encroachment_score(candidate, low_thresh, low_thresh + 4)
    score += threshold_encroachment_score(candidate, high_thresh, high_thresh - 4)
    score += preferred_register_score(candidate, high_thresh, high_thresh - 7)
    score += motion_tendency_score(candidate, position, sequence)
    score += linear_motion_score(candidate, position, sequence)
    score += root_tendency_score(candidate, position, sequence, chord_progression)

    return score


def get_tenor_score(candidate, position, sequence, chord_progression):
    score = 0.0
    low_thresh = parts.TENOR.max_low
    high_thresh = parts.TENOR.max_high

    score += threshold_encroachment_score(candidate, low_thresh, low_thresh + 4)
    score += threshold_encroachment_score(candidate, high_thresh, high_thresh - 4)
    score += preferred_register_score(candidate, low_thresh, low_thresh + 7)
    score += motion_tendency_score(candidate, position, sequence)
    score += linear_motion_score(candidate, position, sequence)

    return score


def get_alto_score(candidate, position, sequence, chord_progression):
    score = 0.0
    low_thresh = parts.ALTO.max_low
    high_thresh = parts.ALTO.max_high

    score += threshold_encroachment_score(candidate, low_thresh, low_thresh + 4)
    score += threshold_encroachment_score(candidate, high_thresh, high_thresh - 4)
    score += preferred_register_score(candidate, high_thresh, high_thresh - 7)
    score += motion_tendency_score(candidate, position, sequence)
    score += linear_motion_score(candidate, position, sequence)

    return score


def get_shape_score(candidate):
    return 0


def get_harmony_score(candidate, chord):
    base_position_chord = [notes.OCTAVES[n.species()][0] for n in chord.all()]
    base_position_candidate = [pitch % 12 for pitch in candidate]
    added = []
    count = 0

    for pitch in base_position_candidate:
        if pitch % 12 in base_position_chord and pitch not in added:
            count += 1
            added.append(pitch)

    return count * 0.05


def root_tendency_score(candidate, position, sequence, chord_progression):
    this_chord = chord_progression[position]
    score = 0.0

    # first bass note should definitely be the root
    if position == 0 and notes.species(candidate) == this_chord.root.species():
        return 0.10

    last_chord = chord_progression[position - RESOLUTION]

    # if location is a "big beat" (1 or 3 in 4/4, 1 or 4 in 6/8), root is more valuable
    measure = sequence.parent_measure(position)

    if position == measure.sample_position() or (measure.sample_position() + position) == measure.subdivision_index():
        score += 0.05

    # Chord is the same as the last chord, and this is root note. Less important as root was likely
    # already established
    if notes.same_species(last_chord.root, this_chord.root) and notes.same_species(candidate, this_chord.root):
        score += 0.03

    # new chord, we definitely want to hear the root
    if not notes.same_species(last_chord.root, this_chord.root) and notes.same_species(candidate, this_chord.root):
        score += 0.20

    return score


def threshold_encroachment_score(val, threshold, soft_limit):
    score = 0.0

    if soft_limit < val <= threshold or threshold <= val < soft_limit:
        score -= (2 ** abs(soft_limit - val)) * 0.01

    return score


def preferred_register_score(val, threshold, soft_limit):
    score = 0.0

    if soft_limit < val <= threshold or threshold <= val < soft_limit:
        score -= abs(soft_limit - val) * 0.01

    return score


def motion_tendency_score(candidate, position, sequence):
    score = 0.0

    if position == 0:
        return score

    last_pitch = sequence[position - RESOLUTION].pitch()

    if is_motion(candidate, last_pitch) and sequence.motion_tendency > 0.5:
        score += sequence.motion_tendency - 0.5
    elif not is_motion(candidate, last_pitch) and sequence.motion_tendency < 0.5:
        score += 0.5 - sequence.motion_tendency

    return score / 2


def linear_motion_score(candidate, position, sequence):
    score = 0.0

    if position == 0:
        return score
    last_pitch = sequence[position - RESOLUTION].pitch()

    if is_linear_motion(candidate, last_pitch):
        score += 0.20

    return score


def is_motion(pitch1, pitch2):
    return pitch2 - pitch1 != 0


def is_linear_motion(pitch1, pitch2):
    return abs(pitch1 - pitch2) < 3 and pitch1 - pitch2 != 0
