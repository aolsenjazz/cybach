import rhythm
import util


def get_most_likely_phrasing(measures):
    all_candidates = rhythm.phrase_combinations(measures[0].time_signature.numerator)
    candidate_map = {}

    for candidate in all_candidates:
        candidate_map[candidate] = 0.0

    for measure in measures:
        measure_candidates = measure.phrasing_candidates()

        for candidate in measure_candidates.keys():
            candidate_map[candidate] = candidate_map[candidate] + measure_candidates[candidate]

    return util.key_for_highest_value(candidate_map)