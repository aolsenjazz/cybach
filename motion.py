from __future__ import division

import transforms
import ts
import constants
import vars
import domain
from constants import RESOLUTION


class Motionizer:

    def __init__(self, key_signatures, chord_progression):
        self.key_signatures = key_signatures
        self.chord_progression = chord_progression

        self.position = 0

    def compute_next(self, soprano, alto, tenor, bass):
        candidates = self.__get_candidate_matrix(soprano, alto, tenor, bass)

        winner = self.__compute_winner(self.position, soprano, alto, tenor, bass, candidates)

        self.position += RESOLUTION

        return winner

    def __compute_winner(self, position, soprano, alto, tenor, bass, candidates):
        high_score = -1
        current_winner = None

        for candidate in candidates:
            transform_synergy = self.__compute_transform_synergies(candidate)
            musicality_score = self.__compute_musicality_scores(candidate)
            motion_score = self.__compute_motion_scores(candidate, alto, tenor, bass)
            soprano_synergy = self.__compute_soprano_synergies(candidate, soprano, position)

            bass_score = self.__bass_score(candidate['bass'])

            score = (soprano_synergy + transform_synergy + musicality_score + bass_score - motion_score)

            if score > high_score:
                current_winner = candidate
                high_score = score

        return current_winner

    def __bass_score(self, transform):
        score = 0.0

        if transform.is_syncopation():
            score += vars.SYNCOPATION_AVOIDANCE

        if transform.crosses_bar_line():
            score += vars.BASS_CROSS_BAR_LINE

        return score

    def __compute_soprano_synergies(self, candidates, soprano, position):
        soprano_pitch = soprano[int(position + RESOLUTION / 2)].pitch()
        scores = []

        for key in candidates.keys():
            score = 0.0

            if isinstance(candidates[key], transforms.EighthNoteTransform):
                inter_pitch = candidates[key].intermediate_pitch
                difference = abs(inter_pitch - soprano_pitch)

                if difference == 1 or difference % 12 == 1:
                    score += vars.VERY_DISSONANT_WITH_SOPRANO
                elif difference == 2:
                    score += vars.SLIGHTLY_DISSONANT_WITH_SOPRANO
                elif difference == 6:
                    score += vars.SLIGHTLY_DISSONANT_WITH_SOPRANO

            scores.append(score)

        return 0 if len(scores) == 0 else sum(scores) / len(scores)

    def __compute_transform_synergies(self, group):
        synergies = []

        for i in range(0, len(group.keys())):

            if i == len(group) - 1:
                break

            low_candidate = group[group.keys()[i]]

            for j in range(i + 1, len(group.keys())):
                high_candidate = group[group.keys()[j]]

                synergies.append(low_candidate.synergy(high_candidate))

        return sum(synergies) / len(synergies)

    def __compute_motion_scores(self, trans, alto, tenor, bass):
        amt = alto.motion_tendency
        tmt = tenor.motion_tendency
        bmt = bass.motion_tendency

        alto_score = abs(trans['alto'].intrinsic_motion - amt)
        tenor_score = abs(trans['tenor'].intrinsic_motion - tmt)
        bass_score = abs(trans['bass'].intrinsic_motion - bmt)

        return (alto_score + tenor_score + bass_score) / 3

    def __compute_musicality_scores(self, transforms):
        scores = []

        for key in transforms.keys():
            scores.append(transforms[key].intrinsic_musicality)

        return sum(scores) / len(scores)

    def __get_candidate_matrix(self, soprano, alto, tenor, bass):
        alto_transforms = self.__all_transformations(self.position, alto, soprano)
        tenor_transforms = self.__all_transformations(self.position, tenor, soprano)
        bass_transforms = self.__all_transformations(self.position, bass, soprano)

        return candidates(alto_transforms, tenor_transforms, bass_transforms)

    def __all_transformations(self, position, sequence, soprano):
        trans = [transforms.NoneTransform(sequence)]

        if sequence[position].pitch() != -1:
            trans.extend(self.__join_transforms(position, sequence))

            if constants.EIGHTH_NOTE in soprano.note_duration_count().keys():
                trans.extend(self.__micro_transforms(position, sequence))

        return trans

    def __micro_transforms(self, position, sequence):
        trans = []

        if transforms.MajorThirdScalarTransform.applicable_at(position, sequence, self.key_signatures):
            trans.append(transforms.MajorThirdScalarTransform(position, sequence, self.key_signatures, self.chord_progression))

        if transforms.MinorThirdScalarTransform.applicable_at(position, sequence, self.key_signatures):
            trans.append(transforms.MinorThirdScalarTransform(position, sequence, self.key_signatures, self.chord_progression))

        if transforms.ArpeggialTransform.applicable_at(position, sequence, self.chord_progression):
            trans.append(transforms.ArpeggialTransform(position, sequence, self.key_signatures, self.chord_progression))

        if transforms.HalfStepNeighborTransform.applicable_at(position, sequence, self.key_signatures):
            trans.append(transforms.HalfStepNeighborTransform(position, sequence, self.key_signatures, self.chord_progression))

        if transforms.WholeStepNeighborTransform.applicable_at(position, sequence, self.key_signatures):
            trans.append(transforms.WholeStepNeighborTransform(position, sequence, self.key_signatures, self.chord_progression))

        if transforms.ApproachTransform.applicable_at(position, sequence, self.chord_progression):
            trans.append(transforms.ApproachTransform(position, sequence, self.key_signatures, self.chord_progression))

        return trans

    def __join_transforms(self, position, sequence):
        if sequence[self.position].type != domain.Sample.TYPE_START:
            return []

        trans = []
        beats_of_same_note = note_duration_at_position(position, sequence)

        if beats_of_same_note >= 2:
            for i in range(2, beats_of_same_note + 1):
                trans.append(transforms.JoinTransform(i, position, sequence, self.chord_progression))

        return trans


def note_duration_at_position(position, sequence):
    duration = 0

    pitch = sequence[position].pitch()
    for i in range(position, len(sequence)):
        if i % RESOLUTION == 0 and sequence[i].pitch() == pitch:
            duration += 1
        elif i % RESOLUTION == 0 and sequence[i].pitch() != pitch:
            break

    return duration


def candidates(*args):
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
