from __future__ import division

import cybach.transforms
from constants import RESOLUTION


class Motionizer:

    def __init__(self, key_sigs, chord_prog):
        self.key_sigs = key_sigs
        self.chord_prog = chord_prog

        self.alto_motion_exhaustion = 0.0
        self.bass_motion_exhaustion = 0.0
        self.tenor_motion_exhaustion = 0.0

        self.position = 0

    def compute_next(self, soprano, alto, tenor, bass):
        candidates = self.__get_candidate_matrix(alto, tenor, bass)
        winner = self.__compute_winner(self.position, soprano, alto, tenor, bass, candidates)

        self.position += RESOLUTION


    def __compute_winner(self, position, soprano, alto, tenor, bass, candidates):
        high_score = -1
        current_winner = None

        for candidate in candidates:
            pass
            # transform_synergy = self.__compute_transform_synergies(candidates)
            # soprano_synergy = self.__compute_soprano_synergies(candidates, soprano, position)
            # motion_score = self.__compute_motion_scores(candidates)
            # musicality_score = self.__compute_musicality_scores(candidates)

        return current_winner

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


    def __get_candidate_matrix(self, alto, tenor, bass):
        alto_transforms = self.__alto_transformations(self.position, alto)
        tenor_transforms = self.__tenor_transformations(self.position, tenor)
        bass_transforms = self.__bass_transformations(self.position, bass)

        return combinations(alto_transforms, tenor_transforms, bass_transforms)

    def __bass_transformations(self, position, sequence):
        trans = self.__join_transforms(position, sequence)

        trans.extend(self.__micro_transforms(position, sequence))
        trans.append(cybach.motion.transforms.NoneTransform(sequence))

        return trans

    def __alto_transformations(self, position, sequence):
        trans = self.__join_transforms(position, sequence)

        trans.extend(self.__micro_transforms(position, sequence))
        trans.append(cybach.motion.transforms.NoneTransform(sequence))

        return trans

    def __tenor_transformations(self, position, sequence):
        trans = self.__join_transforms(position, sequence)

        trans.extend(self.__micro_transforms(position, sequence))
        trans.append(cybach.motion.transforms.NoneTransform(sequence))

        return trans

    def __micro_transforms(self, position, sequence):
        trans = []

        if cybach.motion.transforms.MajorThirdScalarTransform.applicable_at(position, sequence, self.key_sigs):
            trans.append(cybach.motion.transforms.MajorThirdScalarTransform(position, sequence, self.key_sigs))

        if cybach.motion.transforms.MinorThirdScalarTransform.applicable_at(position, sequence, self.key_sigs):
            trans.append(cybach.motion.transforms.MinorThirdScalarTransform(position, sequence, self.key_sigs))

        if cybach.motion.transforms.ArpeggialTransform.applicable_at(position, sequence, self.chord_prog):
            trans.append(cybach.motion.transforms.ArpeggialTransform(position, sequence, self.chord_prog))

        if cybach.motion.transforms.HalfStepNeighborTransform.applicable_at(position, sequence, self.key_sigs):
            trans.append(cybach.motion.transforms.HalfStepNeighborTransform(position, sequence, self.key_sigs))

        if cybach.motion.transforms.WholeStepNeighborTransform.applicable_at(position, sequence, self.key_sigs):
            trans.append(cybach.motion.transforms.WholeStepNeighborTransform(position, sequence, self.key_sigs))

        if cybach.motion.transforms.ApproachTransform.applicable_at(position, sequence, self.chord_prog):
            trans.append(cybach.motion.transforms.ApproachTransform(position, sequence, self.chord_prog))

        return trans


    def __join_transforms(self, position, sequence):
        trans = []

        if cybach.motion.transforms.TwoBeatJoinTransform.applicable_at(position, sequence):
            trans.append(cybach.motion.transforms.TwoBeatJoinTransform(position, sequence, self.chord_prog))

        if cybach.motion.transforms.ThreeBeatJoinTransform.applicable_at(position, sequence):
            trans.append(cybach.motion.transforms.ThreeBeatJoinTransform(position, sequence, self.chord_prog))

        if cybach.motion.transforms.FourBeatJoinTransform.applicable_at(position, sequence):
            trans.append(cybach.motion.transforms.FourBeatJoinTransform(position, sequence, self.chord_prog))

        if cybach.motion.transforms.FiveBeatJoinTransform.applicable_at(position, sequence):
            trans.append(cybach.motion.transforms.FiveBeatJoinTransform(position, sequence, self.chord_prog))

        if cybach.motion.transforms.SixBeatJoinTransform.applicable_at(position, sequence):
            trans.append(cybach.motion.transforms.SixBeatJoinTransform(position, sequence, self.chord_prog))

        return trans


    def calculate_score(self, motion_factors, musicality_factors):
        pass


def combinations(*args):
    r = [[]]
    for x in args:
        t = []
        for y in x:
            for i in r:
                t.append(i + [y])
        r = t
    return r
