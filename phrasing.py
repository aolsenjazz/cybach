from rhythm import time
import util
import config


def detect_and_set_measure_phrasing():
    signatures_plus_end = time.signatures.keys()
    signatures_plus_end.append(len(config.soprano))
    signatures_plus_end.sort()
    last_position = signatures_plus_end[0]
    for i in range(1, len(signatures_plus_end)):
        measures = [measure for measure in config.soprano.measures()
                    if last_position <= measure.sample_position() < signatures_plus_end[i]]

        winner = get_most_likely_phrasing(measures)

        time.signatures[measures[0].sample_position()].phrasing = winner

        last_position = signatures_plus_end[i]


def get_most_likely_phrasing(measures):
    all_candidates = time.phrase_combinations(measures[0].time_signature.numerator)
    candidate_map = {}

    for candidate in all_candidates:
        candidate_map[candidate] = 0.0

    for measure in measures:
        measure_candidates = measure.phrasing_candidates()

        for candidate in measure_candidates.keys():
            if candidate == (0, 1):
                test = 't'
            candidate_map[candidate] = candidate_map[candidate] + measure_candidates[candidate]

    return util.key_for_highest_value(candidate_map)