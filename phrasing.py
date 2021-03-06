import itertools
import math

import chords
import config
import sequences
import util
import vars
from rhythm import time


def detect_and_set_measure_phrasing():
    signatures_plus_end = time.__signatures.keys() + [config.song_length]
    signatures_plus_end.sort()
    for pos1, pos2 in zip(signatures_plus_end, signatures_plus_end[1::]):
        measures = [time.__measures[key] for key in time.__measures.keys() if pos1 <= key < pos2]

        winner = get_most_likely_phrasing(measures)
        time.signature(pos1).set_strong_beat_pattern(winner)


def get_most_likely_phrasing(measures):
    """
    Returns the phrasing permutation which is most likely present.

    :param measures: list of time.Measure
    :return: a tuple representing phrasing. see potential_strong_beat_permutations() for more
    """
    permutations = potential_strong_beat_permutations(measures[0].time_signature().numerator)

    if len(permutations) == 1:
        return permutations[0]

    candidates = {p: 0.0 for p in permutations}

    for permutation in [chord_based_strong_beat_prediction(measure) for measure in measures]:
        if permutation in candidates.keys():
            candidates[permutation] += vars.CHORD_PHRASING

    for permutation in permutations:
        for score in [rhythm_based_strong_beat_score(measure, permutation) for measure in measures]:
            candidates[permutation] += score

    return util.key_for_highest_value(candidates)


def potential_strong_beat_permutations(numerator):
    """
    Returns a tuple of all possible strong beat permutations for a given time signature numerator. Permutations
    are groups of 2, 3, and occasionally 4. Each number represents a phrase grouping.

    E.g. 4/4 would receive (0, 1, 2, 3), 3/4 would receive (0, 1, 2), and 5/4 would receive (0, 2), (0, 3)

    :param numerator:
    :return:
    """
    if numerator <= 4:
        return [tuple(i for i in range(0, numerator))]
    else:
        max_phrases = int(math.floor(numerator / 2))

        potential_combinations = [[0, 2, 3, 4] for i in range(max_phrases)]
        parsed = {tuple(j for j in unfiltered_sublist if j != 0)
                  for unfiltered_sublist
                  in [i for i in itertools.product(*potential_combinations) if sum(i) == numerator]}
        return [tuple([0] + [sublist[i] + sum(sublist[:i]) for i in range(len(sublist[:-1]))]) for sublist in parsed]


def chord_based_strong_beat_prediction(measure):
    """
    Based on where the chords are in the measure, tries to guess the phrase grouping. Returns a single tuple
    containing the indexes of beats with chords. In order to be considered, chord may not be immediately adjacent
    to other chords in time.

    E.g. 1: in a 6/8 measure, if there are chords on 0 and 3, will return phrase grouping of (0, 3)
    E.g. 2: in a 7/8 measure, if there are chords on 0, 2, and 4, will return phrase grouping of (0, 2, 4)
    """
    candidate = [0]
    beats = [beat for beat in measure.beats() if not beat.first_beat() and not beat.last_beat()]
    candidate = candidate + [beat.index_in_measure() for beat in beats if __no_chord_before_or_after(beat)]

    return tuple(candidate)


def __no_chord_before_or_after(beat):
    """
    Returns True if there are no chords the beat before or after the given beat
    :param beat: time.Beat object
    :return: True if no other chords nearby
    """
    return beat.start() in chords.keys() and \
           beat.start() - beat.length() not in chords.keys() and \
           beat.end() not in chords.keys()


def rhythm_based_strong_beat_score(measure, pattern):
    """
    Returns the likelihood that a measure's strong beat pattern is the given pattern

    :param measure: time.Measure that we're testing
    :param pattern: tuple with the pattern, e.g. (0, 2, 4) or (3, 2, 2) in 7
    :return: likelihood score
    """
    likelihood_score = 0.0
    position = 0
    sequence = sequences.soprano()

    for i in range(len(pattern)):
        target_duration = ((pattern + (len(measure.beats()), ))[i + 1] - pattern[i]) * measure.beat_length()
        entity = sequence.entity(measure.start() + sum([j * measure.beat_length() for j in pattern[:i + 1]]))

        if entity.length() == target_duration and entity.start() == position:
            likelihood_score += vars.RHYTHM_PHRASING_COEF * ((pattern + (len(measure.beats()), ))[i + 1] - pattern[i])

        position += target_duration

    return likelihood_score
