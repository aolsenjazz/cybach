from __future__ import division

import transforms
import constants
import vars
from constants import RESOLUTION


class Motionizer:

    def __init__(self, key_sigs, chord_prog):
        self.key_sigs = key_sigs
        self.chord_prog = chord_prog

        self.position = 0

    def compute_next(self, soprano, alto, tenor, bass):
        candidates = self.__get_candidate_matrix(alto, tenor, bass)

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

            score = (soprano_synergy + transform_synergy + musicality_score - motion_score) / 4

            if score > high_score:
                current_winner = candidate
                high_score = score

        return current_winner

    def __compute_soprano_synergies(self, candidates, soprano, position):
        soprano_pitch = soprano[int(position + RESOLUTION / 2)].pitch()
        scores = []

        for transform in candidates:
            score = 0.0

            if isinstance(transform, transforms.EighthNoteTransform):
                inter_pitch = transform.intermediate_pitch
                difference = abs(inter_pitch - soprano_pitch)

                if difference == 1 or difference % 12 == 1:
                    score += vars.VERY_DISSONANT_WITH_SOPRANO
                elif difference == 2:
                    score += vars.SLIGHTLY_DISSONANT_WITH_SOPRANO

            scores.append(score)

        return 0 if len(scores) == 0 else sum(scores) / len(scores)

    def __compute_transform_synergies(self, candidates):
        synergies = []

        for i in range(0, len(candidates)):
            if i == len(candidates) - 1:
                break

            low_candidate = candidates[i]

            for j in range(i + 1, len(candidates)):
                high_candidate = candidates[j]

                synergies.append(low_candidate.synergy(high_candidate))

        return sum(synergies) / len(synergies)

    def __compute_motion_scores(self, trans, alto, tenor, bass):
        amt = alto.motion_tendency
        tmt = tenor.motion_tendency
        bmt = bass.motion_tendency

        alto_score = abs(trans[0].intrinsic_motion - amt)
        tenor_score = abs(trans[0].intrinsic_motion - tmt)
        bass_score = abs(trans[0].intrinsic_motion - bmt)

        return (alto_score + tenor_score + bass_score) / 3

    def __compute_musicality_scores(self, transforms):
        scores = []

        for transform in transforms:
            scores.append(transform.intrinsic_musicality)

        return sum(scores) / len(scores)

    def __get_candidate_matrix(self, alto, tenor, bass):
        alto_transforms = self.__alto_transformations(self.position, alto)
        tenor_transforms = self.__tenor_transformations(self.position, tenor)
        bass_transforms = self.__bass_transformations(self.position, bass)

        return combinations(alto_transforms, tenor_transforms, bass_transforms)

    def __bass_transformations(self, position, sequence):
        trans = [transforms.NoneTransform(sequence)]

        if sequence[position].pitch() != -1:
            trans.extend(self.__join_transforms(position, sequence))

            if constants.EIGHTH_NOTE in sequence.note_duration_count().keys():
                trans.extend(self.__micro_transforms(position, sequence))

        return trans

    def __alto_transformations(self, position, sequence):
        trans = [transforms.NoneTransform(sequence)]

        if sequence[position].pitch() != -1:
            trans.extend(self.__join_transforms(position, sequence))

            if constants.EIGHTH_NOTE in sequence.note_duration_count().keys():
                trans.extend(self.__micro_transforms(position, sequence))

        return trans

    def __tenor_transformations(self, position, sequence):
        trans = [transforms.NoneTransform(sequence)]

        if sequence[position].pitch() != -1:
            trans.extend(self.__join_transforms(position, sequence))

            if constants.EIGHTH_NOTE in sequence.note_duration_count().keys():
                trans.extend(self.__micro_transforms(position, sequence))

        return trans

    def __micro_transforms(self, position, sequence):
        trans = []

        if transforms.MajorThirdScalarTransform.applicable_at(position, sequence, self.key_sigs):
            trans.append(transforms.MajorThirdScalarTransform(position, sequence, self.key_sigs, self.chord_prog))

        if transforms.MinorThirdScalarTransform.applicable_at(position, sequence, self.key_sigs):
            trans.append(transforms.MinorThirdScalarTransform(position, sequence, self.key_sigs, self.chord_prog))

        if transforms.ArpeggialTransform.applicable_at(position, sequence, self.chord_prog):
            trans.append(transforms.ArpeggialTransform(position, sequence, self.key_sigs, self.chord_prog))

        if transforms.HalfStepNeighborTransform.applicable_at(position, sequence, self.key_sigs):
            trans.append(transforms.HalfStepNeighborTransform(position, sequence, self.key_sigs, self.chord_prog))

        if transforms.WholeStepNeighborTransform.applicable_at(position, sequence, self.key_sigs):
            trans.append(transforms.WholeStepNeighborTransform(position, sequence, self.key_sigs, self.chord_prog))

        if transforms.ApproachTransform.applicable_at(position, sequence, self.chord_prog):
            trans.append(transforms.ApproachTransform(position, sequence, self.key_sigs, self.chord_prog))

        return trans

    def __join_transforms(self, position, sequence):
        trans = []

        if transforms.TwoBeatJoinTransform.applicable_at(position, sequence):
            trans.append(transforms.TwoBeatJoinTransform(position, sequence, self.chord_prog))

        if transforms.ThreeBeatJoinTransform.applicable_at(position, sequence):
            trans.append(transforms.ThreeBeatJoinTransform(position, sequence, self.chord_prog))

        if transforms.FourBeatJoinTransform.applicable_at(position, sequence):
            trans.append(transforms.FourBeatJoinTransform(position, sequence, self.chord_prog))

        if transforms.FiveBeatJoinTransform.applicable_at(position, sequence):
            trans.append(transforms.FiveBeatJoinTransform(position, sequence, self.chord_prog))

        if transforms.SixBeatJoinTransform.applicable_at(position, sequence):
            trans.append(transforms.SixBeatJoinTransform(position, sequence, self.chord_prog))

        return trans


def combinations(*args):
    r = [[]]
    for x in args:
        t = []
        for y in x:
            for i in r:
                t.append(i + [y])
        r = t
    return r
