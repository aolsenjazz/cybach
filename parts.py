import notes


class Part:

    def __init__(self, max_low, max_high, title):
        self.max_low = max_low
        self.max_high = max_high
        self.middle = (max_high + max_low) / 2
        self.title = title

    def available_notes(self, chord):
        available = []

        for pitch in chord.all():
            octaves = notes.OCTAVES[notes.Note(pitch.midi()).species()]
            for octave in octaves:
                if self.max_low < octave < self.max_high:
                    available.append(octave)

        return available

    def __repr__(self):
        return self.title


ALTO = Part(54, 72, 'alto')
TENOR = Part(48, 65, 'tenor')
BASS = Part(40, 60, 'bass')
