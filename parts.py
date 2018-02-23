import notes


class Part:

    def __init__(self, max_low, max_high, title):
        self.max_low = max_low
        self.max_high = max_high
        self.middle = (max_high + max_low) / 2
        self.title = title

    def available_notes(self, chord):
        return [pitch for pitch in chord.all_octaves() if self.max_low < pitch < self.max_high]

    def __repr__(self):
        return self.title


ALTO = Part(54, 72, 'alto')
TENOR = Part(48, 65, 'tenor')
BASS = Part(38, 60, 'bass')
