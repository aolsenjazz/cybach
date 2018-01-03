import notes


class Part:

    def __init__(self, max_low, max_high):
        self.max_low = max_low
        self.max_high = max_high
        self.middle = (max_high + max_low) / 2

    def available_notes(self, chord):
        available = []

        for pitch in chord.all():
            octaves = notes.OCTAVES[notes.Note(midi_value=pitch.midi_value).as_text_without_octave()]
            for octave in octaves:
                if self.max_low < octave < self.max_high:
                    available.append(octave)

        return available


ALTO = Part(55, 72)
TENOR = Part(48, 65)
BASS = Part(40, 60)
