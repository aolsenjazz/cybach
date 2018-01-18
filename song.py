from domain import Sequence
import parts


class Song:

    def __init__(self, file_name, soprano, time_signatures, key_signatures, chord_progression, part_customization):
        self.name = file_name.split('.')[0]
        self.time_signatures = time_signatures
        self.key_signatures = key_signatures
        self.chord_progression = chord_progression

        self.soprano = soprano
        self.alto = Sequence(seed=soprano, part=parts.ALTO, time_signatures=time_signatures,
                             configuration=part_customization.get('alto', {}))
        self.tenor = Sequence(seed=soprano, part=parts.TENOR, time_signatures=time_signatures,
                              configuration=part_customization.get('tenor', {}))
        self.bass = Sequence(seed=soprano, part=parts.BASS, time_signatures=time_signatures,
                             configuration=part_customization.get('bass', {'motion_tendency': 0.3}))
