import pitches


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


ALTO = Part(pitches.MIDI_VALUES['F#4'], pitches.MIDI_VALUES['C6'], 'alto')
TENOR = Part(pitches.MIDI_VALUES['C4'], pitches.MIDI_VALUES['F5'], 'tenor')
BASS = Part(pitches.MIDI_VALUES['D3'], pitches.MIDI_VALUES['C5'], 'bass')
