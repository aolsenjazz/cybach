import config
import ks
import util


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

    chord_progression = dict(config.chord_progression)

    keys = chord_progression.keys()
    keys.sort()
    keys.append(config.song_length)

    chord_progression[config.song_length] = chord_progression[keys[-2]]

    potential_keys = list(all_key_signatures)
    last_key_signature_end = 0
    for key in keys:
        chord = chord_progression[key]

        removed = [key_sig for key_sig in potential_keys if not key_sig.is_functional(chord)]
        remaining = [key_sig for key_sig in potential_keys if key_sig.is_functional(chord)]

        for key_signature in removed:
            potential_keys.remove(key_signature)

        if len(remaining) == 0:
            this_segments_chords = [chord_progression[k] for k in keys if last_key_signature_end <= k <= key]
            config.key_signatures[last_key_signature_end] = __get_most_likely_key(removed, this_segments_chords)

            last_key_signature_end = key
            potential_keys = list(all_key_signatures)
        elif key == config.song_length:
            this_segments_chords = [chord_progression[k] for k in keys if last_key_signature_end <= k <= key]
            config.key_signatures[last_key_signature_end] = __get_most_likely_key(remaining, this_segments_chords)

            last_key_signature_end = key
            potential_keys = list(all_key_signatures)


def __get_most_likely_key(potential_key_signatures, chord_progression_stub):
    scores = {}

    for key_signature in potential_key_signatures:
        harmony_score = sum([key_signature.harmonic_relevance(chord) for chord in chord_progression_stub])
        functionality_score = sum([key_signature.functional_relevance(c1, c2)
                                   for c1, c2
                                   in zip(chord_progression_stub[0:], chord_progression_stub[1:])])

        scores[key_signature] = harmony_score + functionality_score

    print scores

    return util.key_for_highest_value(scores)
