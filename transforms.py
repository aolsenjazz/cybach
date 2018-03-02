import itertools
import chords
import config
import sequences
from rhythm import time


def transforms(start_position, end_position):
    pass


def get_all_transforms(start_position, end_position, max_subdivisions):
    satb = sequences.soprano(), sequences.alto(), sequences.tenor(), sequences.bass()
    pitches = [(sequence.pitch(start_position), sequence.pitch(end_position)) for sequence in satb]

    chord = chords.get(start_position)

    rhythm_set_groups = get_rhythm_sets(config.minimum_time_unit(), max_subdivisions, end_position - start_position)
    direction_set_groups = [direction_permutations(i) for i in range(1, max_subdivisions)]

    all_transforms = []
    for i, (sequence, (start_pitch, end_pitch)) in enumerate(zip(satb[1:], pitches[1:])):
        # We can't (read: don't want to) transform to or from a rest; skip if the start or end pitch is a rest.
        if start_pitch == -1 or end_pitch == -1:
            all_transforms.append([[]])
            continue

        high_thresh = min([p for p in pitches[i] if p != -1] + [sequence.part().max_high])
        low_thresh = sequence.part().max_low if i == len(satb) - 1 else min(sequence.part().max_low, pitches[i - 1])

        bounded_pitches = [pitch for pitch in chord.scale() if low_thresh <= pitch <= high_thresh]

        sequence_transforms = []
        for i, direction_set_group in enumerate(direction_set_groups):
            pitch_sets = [group for direction_set in direction_set_group
                          for group in
                          pitch_sets_for_directions(bounded_pitches, start_pitch, end_pitch, direction_set)]
            trans = [StrongBeatPhrase(r, p) for p in pitch_sets for r in rhythm_set_groups[i]]

            sequence_transforms.extend(trans)

        all_transforms.append(sequence_transforms)

    product = list(itertools.product(*all_transforms))
    return product


def get_rhythm_sets(minimum_time_unit, max_time_unit_count, length):
    pool = [i for i in range(minimum_time_unit, length)[::minimum_time_unit]]
    pools = [pool for i in range(max_time_unit_count)]

    sets = []
    product = [[]]
    for pool in pools:
        product = [x + [y] for x in product for y in pool]

        temp = []
        for sublist in [sublist for sublist in product if sum(sublist) == length]:
            temp.append(RhythmSet(sublist))
        else:
            if temp:
                sets.append(temp)

    return sets


def pitch_sets_for_directions(bounded_pitches, start, target, directions):
    groupings = [[i for i in bounded_pitches if _same_direction(directions[0], start, i)]]
    groupings.extend([bounded_pitches for direction in directions[1:]])

    product = [[]]
    for i in range(len(groupings)):
        direction = directions[i]
        pool = groupings[i]
        temp = []

        for pool_entry in pool:
            for result_entry in product:
                if not result_entry or _same_direction(direction, result_entry[-1], pool_entry):
                    temp.append(result_entry + [pool_entry])
        product = temp

    return [PitchSet(start, target, *pitches) for pitches in product]


def direction_permutations(total_directions):
    groupings = [[Direction.UP, Direction.SAME, Direction.DOWN] for d in range(total_directions)]
    return [i for i in itertools.product(*[i for i in groupings])]


class Direction:
    UP = 1
    SAME = 0
    DOWN = -1

    def __init__(self):
        pass


class RhythmSet:

    def __init__(self, rhythm_list):
        self._homogeneous = len(set(rhythm_list)) == 1
        self._syncopation = False if len(rhythm_list) == 1 else rhythm_list[1] > rhythm_list[0]
        self.rhythm_list = rhythm_list

    def is_homogeneous(self):
        return self._homogenous

    def is_syncopation(self):
        return self._syncopation

    def __repr__(self):
        return '\nRhythmSet: ' + str(self.rhythm_list)


class PitchSet:

    def __init__(self, first_pitch, last_pitch, *args):
        self.first_pitch = first_pitch
        self.last_pitch = last_pitch
        self.intermediaries = args
        self.all = (first_pitch,) + args + (last_pitch,)
        self.direction = self._direction()
        self.unidirectional = self._unidirectional()

    def _direction(self):
        direction = 0
        for p1, p2 in zip(self.all, self.all[1:]):
            if direction == 0:
                direction = _direction(p1, p2)
            else:
                if not _continues_linearity(direction, p1, p2):
                    return None

        return direction

    def _unidirectional(self):
        return self.direction is not None

    def __repr__(self):
        return '\nPitchSet: ' + str(self.first_pitch) + ', ' + str(self.intermediaries) + ', ' + str(self.last_pitch)


class StrongBeatPhrase:

    def __init__(self, rhythm_set, pitch_set):
        self._rhythm_set = rhythm_set
        self._pitch_set = pitch_set

    def __repr__(self):
        return '\nStrongBeatPhrase: ' + self._rhythm_set.__repr__() + self._pitch_set.__repr__()


def _direction(p1, p2):
    return Direction.UP if p1 < p2 else Direction.DOWN if p1 > p2 else Direction.SAME


def _same_direction(direction, p1, p2):
    return _direction(p1, p2) == direction


def _continues_linearity(direction, p1, p2):
    pitch_direction = _direction(p1, p2)

    return pitch_direction == direction \
           or pitch_direction == Direction.SAME \
           or direction == Direction.SAME
