import config
import ks
import util
import vars
import notes
import domain


all_key_signatures = [
    ks.MajorKeySignature('C'),
    ks.MajorKeySignature('C#'),
    ks.MajorKeySignature('D'),
    ks.MajorKeySignature('D#'),
    ks.MajorKeySignature('E'),
    ks.MajorKeySignature('F'),
    ks.MajorKeySignature('F#'),
    ks.MajorKeySignature('G'),
    ks.MajorKeySignature('G#'),
    ks.MajorKeySignature('A'),
    ks.MajorKeySignature('A#'),
    ks.MajorKeySignature('B'),
    ks.MinorKeySignature('C'),
    ks.MinorKeySignature('C#'),
    ks.MinorKeySignature('D'),
    ks.MinorKeySignature('D#'),
    ks.MinorKeySignature('E'),
    ks.MinorKeySignature('F'),
    ks.MinorKeySignature('F#'),
    ks.MinorKeySignature('G'),
    ks.MinorKeySignature('G#'),
    ks.MinorKeySignature('A'),
    ks.MinorKeySignature('A#'),
    ks.MinorKeySignature('B')
]


def detect_and_set_key_signatures():
    config.key_signatures = ks.KeySignatures()

    song_length = len(config.soprano)
    chord_progression = dict(config.chord_progression)

    keys = chord_progression.keys()
    keys.sort()
    keys.append(song_length)

    chord_progression[song_length] = chord_progression[keys[-2]]

    potential_keys = list(all_key_signatures)
    last_key_signature_end = 0
    for key in keys:
        chord = chord_progression[key]
        removed = [key_sig for key_sig in potential_keys if not key_sig.is_functional(chord)]
        potential_keys = [key_signature for key_signature in potential_keys if key_signature not in removed]

        if len(potential_keys) == 0 or key == song_length:
            signature_pool = removed if len(potential_keys) == 0 else potential_keys
            chord_segment = {k: chord_progression[k] for k in keys if last_key_signature_end <= k < key}

            if [sig for sig in signature_pool if __contains_one_or_five_seven(sig, chord_segment)]:
                config.key_signatures[last_key_signature_end] = __most_likely_key(signature_pool, chord_segment)
            else:
                this_segments_keys = [k for k in keys if last_key_signature_end <= k < key]
                config.key_signatures.update({key: ks.parse(chord_progression[key]) for key in this_segments_keys})

            last_key_signature_end = key
            removed = [key_sig for key_sig in potential_keys if not key_sig.is_functional(chord)]
            potential_keys = [key_signature for key_signature in potential_keys if key_signature in removed]


def __most_likely_key(potential_key_signatures, chord_segment):
    scores = {}

    for ks in potential_key_signatures:

        harmony_score = sum([ks.harmonic_relevance(chord_segment[key]) * __time_coef(key, min(chord_segment.keys()))
                             for key
                             in chord_segment.keys()])

        scores[ks] = harmony_score

    return util.key_for_highest_value(scores)


def __contains_one_or_five_seven(key_signature, chord_progression_stub):
    for key in chord_progression_stub.keys():
        chord = chord_progression_stub[key]
        if key_signature.is_functional(chord) and notes.same_species(key_signature.one(), chord.root()):
            return True
    return False


def __time_coef(sample_index, segment_start):
    if sample_index == 0 or sample_index == segment_start:
        return vars.FIRST_BEAT_COEF

    beat = config.soprano.beat_at(sample_index)

    return vars.BEAT_ONE_COEF if beat.is_first_beat() else 1.0
