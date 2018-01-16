import notes


class Instrument:

    def __init__(self, max_low_pitch, max_high_pitch):
        self.max_low_pitch = max_low_pitch
        self.max_high_pitch = max_high_pitch
        self.comfy_low_pitch = max_low_pitch + 5
        self.comfy_high_pitch = max_high_pitch - 5
        self.middle = (max_low_pitch + max_high_pitch) / 2

    def __repr__(self):
        return 'Max low pitch: %d // Max high pitch: %d' % (self.max_low_pitch, self.max_high_pitch)

    def lowest_comfy(self, note):
        text = note.species()
        octaves = notes.OCTAVES[text]

        for pitch in octaves:
            if pitch > self.comfy_low_pitch:
                return pitch

    def lowest_max(self, note):
        text = note.species()
        octaves = notes.OCTAVES[text]

        for pitch in octaves:
            if pitch > self.max_low_pitch:
                return pitch

    def highest_comfy(self, note):
        text = note.species()
        octaves = notes.OCTAVES[text]

        last_pitch = octaves[0]
        for pitch in octaves:
            if pitch > self.comfy_high_pitch:
                return last_pitch
            last_pitch = pitch

    def highest_max(self, note):
        text = note.species()
        octaves = notes.OCTAVES[text]

        last_pitch = octaves[0]
        for pitch in octaves:
            if pitch > self.max_high_pitch:
                return last_pitch
            last_pitch = pitch


PICCOLO = Instrument(notes.MIDI_VALUES['D4'], notes.MIDI_VALUES['C7'])
FLUTE = Instrument(notes.MIDI_VALUES['C4'], notes.MIDI_VALUES['D7'])
OBOE = Instrument(notes.MIDI_VALUES['D#4'], notes.MIDI_VALUES['C7'])
ENGLISH_HORN = Instrument(notes.MIDI_VALUES['B3'], notes.MIDI_VALUES['G6'])
CLARINET = Instrument(notes.MIDI_VALUES['E3'], notes.MIDI_VALUES['C7'])
BASS_CLARINET = Instrument(notes.MIDI_VALUES['D#3'], notes.MIDI_VALUES['G6'])
BASSOON = Instrument(notes.MIDI_VALUES['A#1'], notes.MIDI_VALUES['D#5'])
CONTRABASSOON = Instrument(notes.MIDI_VALUES['A#1'], notes.MIDI_VALUES['A#4'])
SAXOPHONE = Instrument(notes.MIDI_VALUES['A#3'], notes.MIDI_VALUES['G6'])

TRUMPET = Instrument(notes.MIDI_VALUES['F#3'], notes.MIDI_VALUES['D6'])
PICCOLO_TRUMPET = Instrument(notes.MIDI_VALUES['F#3'], notes.MIDI_VALUES['G5'])
TROMBONE = Instrument(notes.MIDI_VALUES['E2'], notes.MIDI_VALUES['F5'])
TUBA = Instrument(notes.MIDI_VALUES['D1'], notes.MIDI_VALUES['F4'])

VIOLIN = Instrument(notes.MIDI_VALUES['G3'], notes.MIDI_VALUES['A7'])
VIOLA = Instrument(notes.MIDI_VALUES['C3'], notes.MIDI_VALUES['E6'])
CELLO = Instrument(notes.MIDI_VALUES['C2'], notes.MIDI_VALUES['C6'])
BASS = Instrument(notes.MIDI_VALUES['E1'], notes.MIDI_VALUES['C5'])

INSTRUMENTS = {
    'piccolo': PICCOLO,
    'pic': PICCOLO,
    'picc': PICCOLO,
    'flute': FLUTE,
    'alto_flute': FLUTE,
    'oboe': OBOE,
    'english_horn': ENGLISH_HORN,
    'clarinet': CLARINET,
    'bass_clarinet': BASS_CLARINET,
    'bassoon': BASSOON,
    'contrabassoon': CONTRABASSOON,
    'saxophone': SAXOPHONE,
    'sax': SAXOPHONE,
    'tenor_sax': SAXOPHONE,
    'tenor_saxophone': SAXOPHONE,
    'alto_sax': SAXOPHONE,
    'alto_saxophone': SAXOPHONE,
    'soprano_sax': SAXOPHONE,
    'soprano_saxophone': SAXOPHONE,
    'bari_saxophone': SAXOPHONE,
    'bari_sax': SAXOPHONE,
    'trumpet': TRUMPET,
    'piccolo_trumpet': TRUMPET,
    'trombone': TROMBONE,
    'tuba': TUBA,
    'violin': VIOLIN,
    'viola': VIOLA,
    'cello': CELLO,
    'bass': BASS
}


def parse(name):
    return INSTRUMENTS.get(name.lower().replace(' ', '_'), None)
