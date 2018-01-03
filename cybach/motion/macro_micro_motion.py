from __future__ import division

import cybach.constants


class MacroMotionizer:

    def __init__(self, key_sigs, chord_prog, bass_motion_tendency=0.5,
                 tenor_motion_tendency=0.5, alto_motion_tendency=0.5):
        self.key_sigs = key_sigs
        self.chords = chord_prog
        self.position = 0

        self.bass_transform = None
        self.alto_transform = None
        self.tenor_transform = None

        self.bass_motion_tendency = bass_motion_tendency
        self.tenor_motion_tendency = tenor_motion_tendency
        self.alto_motion_tendency = alto_motion_tendency

        self.current_bass_motion_tendency = bass_motion_tendency
        self.current_tenor_motion_tendency = tenor_motion_tendency
        self.current_alto_motion_tendency = alto_motion_tendency

    def compute_next(self, bass, alto, tenor):
        bass_transforms = self.__bass_transformations(self.position, bass)
        alto_transforms = self.__alto_transformations(self.position, alto)
        tenor_transforms = self.__tenor_transformations(self.position, tenor)

        transforms = combinations(bass_transforms, alto_transforms, tenor_transforms)
        high_score = -1.0
        current_winner = None


        for batch in transforms:
            motion_factors = []
            musicality_factors = []
            repetitiveness_factors = []
            # print batch

            for i in range(0, len(batch)):
                transform = batch[i]

                if i % 3 == 0:
                    motion_factors.append(abs(self.current_bass_motion_tendency - transform.intrinsic_motion))
                elif i % 3 == 1:
                    motion_factors.append(abs(self.current_alto_motion_tendency - transform.intrinsic_motion))
                else:
                    motion_factors.append(abs(self.current_tenor_motion_tendency - transform.intrinsic_motion))

                musicality_factors.append(transform.intrinsic_musicality)

            score = self.calculate_score(motion_factors, musicality_factors)

            if score > high_score:
                current_winner = batch
                high_score = score

        self.bass_transform = current_winner[0]
        self.alto_transform = current_winner[1]
        self.tenor_transform = current_winner[2]

        self.position += cybach.constants.RESOLUTION

    def __bass_transformations(self, position, sequence):
        transforms = self.__join_transforms(position, sequence)
        transforms.append(transforms.NoneTransform(sequence))

        return transforms

    def __alto_transformations(self, position, sequence):
        transforms = self.__join_transforms(position, sequence)
        transforms.append(transforms.NoneTransform(sequence))

        if transforms.QuarterNoteArpeggiateTransform.applicable_at(position, sequence, self.chords):
            transforms.append(transforms.QuarterNoteArpeggiateTransform(position, sequence, self.chords))

        return transforms

    def __tenor_transformations(self, position, sequence):
        transforms = self.__join_transforms(position, sequence)
        transforms.append(transforms.NoneTransform(sequence))

        if transforms.QuarterNoteArpeggiateTransform.applicable_at(position, sequence, self.chords):
            transforms.append(transforms.QuarterNoteArpeggiateTransform(position, sequence, self.chords))

        return transforms

    def __join_transforms(self, position, sequence):
        transforms = []

        if transforms.TwoBeatJoinTransform.applicable_at(position, sequence):
            transforms.append(transforms.TwoBeatJoinTransform(position, sequence, self.chords))

        if transforms.ThreeBeatJoinTransform.applicable_at(position, sequence):
            transforms.append(transforms.ThreeBeatJoinTransform(position, sequence, self.chords))

        if transforms.FourBeatJoinTransform.applicable_at(position, sequence):
            transforms.append(transforms.FourBeatJoinTransform(position, sequence, self.chords))

        if transforms.FiveBeatJoinTransform.applicable_at(position, sequence):
            transforms.append(transforms.FiveBeatJoinTransform(position, sequence, self.chords))

        if transforms.SixBeatJoinTransform.applicable_at(position, sequence):
            transforms.append(transforms.SixBeatJoinTransform(position, sequence, self.chords))

        return transforms

    # High motion score: bad
    # High musicality score: good
    def calculate_score(self, motion_factors, musicality_factors):
        motion_factor = sum(motion_factors) / len(motion_factors)

        musicality_factor = sum(musicality_factors) / len(musicality_factors)

        return 0 - motion_factor + musicality_factor


class MicroMotionizer:

    def __init__(self, key_sigs, chord_prog, bass_motion_tendency=0.5,
                 tenor_motion_tendency=0.5, alto_motion_tendency=0.5):
        self.key_sigs = key_sigs
        self.chords = chord_prog
        self.position = 0

        self.bass_transform = None
        self.alto_transform = None
        self.tenor_transform = None

        self.bass_motion_tendency = bass_motion_tendency
        self.tenor_motion_tendency = tenor_motion_tendency
        self.alto_motion_tendency = alto_motion_tendency

        self.current_bass_motion_tendency = bass_motion_tendency
        self.current_tenor_motion_tendency = tenor_motion_tendency
        self.current_alto_motion_tendency = alto_motion_tendency

    def compute_next(self, bass, alto, tenor):
        bass_transforms = self.__bass_transformations(self.position, bass)
        alto_transforms = self.__alto_transformations(self.position, alto)
        tenor_transforms = self.__tenor_transformations(self.position, tenor)

        transforms = combinations(bass_transforms, alto_transforms, tenor_transforms)
        del transforms[0]  # index 0 is always a series of NoneTransform's

        # print transforms
        # high_score = -1.0
        # current_winner = None
        #
        # for batch in transforms:
        #     motion_factors = []
        #     musicality_factors = []
        #     repetitiveness_factors = []
        #
        #     for i in range(0, len(batch)):
        #         transform = batch[i]
        #
        #         if i % 3 == 0:
        #             motion_factors.append(abs(self.current_bass_motion_tendency - transform.intrinsic_motion))
        #         elif i% 3 == 1:
        #             motion_factors.append(abs(self.current_alto_motion_tendency - transform.intrinsic_motion))
        #         else:
        #             motion_factors.append(abs(self.current_tenor_motion_tendency - transform.intrinsic_motion))
        #
        #         musicality_factors.append(transform.intrinsic_musicality)
        #
        #     if calculate_score(motion_factors, musicality_factors) > high_score:
        #         current_winner = batch
        #         high_score = calculate_score(motion_factors, musicality_factors)
        #
        # self.bass_transform = current_winner[0]
        # self.alto_transform = current_winner[1]
        # self.tenor_transform = current_winner[2]

        self.position += cybach.constants.RESOLUTION

    def __bass_transformations(self, position, sequence):
        return self.default_transforms(position, sequence)

    def __alto_transformations(self, position, sequence):
        return self.default_transforms(position, sequence)

    def __tenor_transformations(self, position, sequence):
        return self.default_transforms(position, sequence)

    def calculate_score(self, motion_factors, musicality_factors):
        pass

    def default_transforms(self, position, sequence):
        transforms = [transforms.NoneTransform(sequence)]

        if transforms.MajorThirdScalarTransform.applicable_at(position, sequence, self.chords, self.key_sigs):
            transforms.append(transforms.MajorThirdScalarTransform())

        if transforms.MinorThirdScalarTransform.applicable_at(position, sequence, self.chords, self.key_sigs):
            transforms.append(transforms.MinorThirdScalarTransform())

        if transforms.ArpeggialTransform.applicable_at(position, sequence, self.chords, self.key_sigs):
            transforms.append(transforms.ArpeggialTransform())

        if transforms.NeighborTransform.applicable_at(position, sequence, self.chords, self.key_sigs):
            transforms.append(transforms.NeighborTransform())

        if transforms.ApproachTransform.applicable_at(position, sequence, self.chords, self.key_sigs):
            transforms.append(transforms.ApproachTransform())

        return transforms


def combinations(*args):
    r = [[]]
    for x in args:
        t = []
        for y in x:
            for i in r:
                t.append(i + [y])
        r = t
    return r
