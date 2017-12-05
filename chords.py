import notes

class Chord:

    root = None
    third = None
    fifth = None
    seventh = None

    def __init__(self, root):
        pass


class MajorChord(Chord):

    def __init__(self, root_note):
        Chord.__init__(self, root_note)
        self.root = root_note.as_midi_value
        self.third = self.root + 4
        self.fifth = self.fifth + 7


class MinorChord(Chord):

    def __init__(self, root_note):
        Chord.__init__(self, root_note)
        self.root = root_note.as_midi_value
        self.third = self.root + 3
        self.fifth = self.root + 7


class SevenChord(Chord):

    def __init__(self, root_note):
        Chord.__init__(self, root_note)
        self.root = root_note.as_midi_value
        self.third = self.root + 4
        self.fifth = self.root + 7
        self.seventh = self.root + 10


class DiminishedChord(Chord):

    def __init__(self, root_note):
        Chord.__init__(self, root_note)
        self.root = root_note.as_midi_value
        self.third = self.root + 3
        self.fifth = self.fifth + 6
        self.seventh = self.root + 9


CHORDS = {
    'C': MajorChord(notes.Note(text_value=notes.C)),
    'C-': MinorChord(notes.Note(text_value=notes.C)),
    'C7': SevenChord(notes.Note(text_value=notes.C)),
    'Cdim': DiminishedChord(notes.Note(text_value=notes.C)),
    'C#': MajorChord(notes.Note(text_value=notes.C_SHARP)),
    'C#-': MinorChord(notes.Note(text_value=notes.C_SHARP)),
    'C#7': SevenChord(notes.Note(text_value=notes.C_SHARP)),
    'C#dim': DiminishedChord(notes.Note(text_value=notes.C_SHARP)),
    'D': MajorChord(notes.Note(text_value=notes.D)),
    'D-': MinorChord(notes.Note(text_value=notes.D)),
    'D7': SevenChord(notes.Note(text_value=notes.D)),
    'Ddim': DiminishedChord(notes.Note(text_value=notes.D)),
    'D#': MajorChord(notes.Note(text_value=notes.D_SHARP)),
    'D#-': MinorChord(notes.Note(text_value=notes.D_SHARP)),
    'D#7': SevenChord(notes.Note(text_value=notes.D_SHARP)),
    'D#dim': DiminishedChord(notes.Note(text_value=notes.D_SHARP)),
    'E': MajorChord(notes.Note(text_value=notes.E)),
    'E-': MinorChord(notes.Note(text_value=notes.E)),
    'E7': SevenChord(notes.Note(text_value=notes.E)),
    'Edim': DiminishedChord(notes.Note(text_value=notes.E)),
    'F': MajorChord(notes.Note(text_value=notes.F)),
    'F-': MinorChord(notes.Note(text_value=notes.F)),
    'F7': SevenChord(notes.Note(text_value=notes.F)),
    'Fdim': DiminishedChord(notes.Note(text_value=notes.F)),
    'F#': MajorChord(notes.Note(text_value=notes.F_SHARP)),
    'F#-': MinorChord(notes.Note(text_value=notes.F_SHARP)),
    'F#7': SevenChord(notes.Note(text_value=notes.F_SHARP)),
    'F#dim': DiminishedChord(notes.Note(text_value=notes.F_SHARP)),
    'G': MajorChord(notes.Note(text_value=notes.G)),
    'G-': MinorChord(notes.Note(text_value=notes.G)),
    'G7': SevenChord(notes.Note(text_value=notes.G)),
    'Gdim': DiminishedChord(notes.Note(text_value=notes.G)),
    'G#': MajorChord(notes.Note(text_value=notes.G_SHARP)),
    'G#-': MinorChord(notes.Note(text_value=notes.G_SHARP)),
    'G#7': SevenChord(notes.Note(text_value=notes.G_SHARP)),
    'G#dim': DiminishedChord(notes.Note(text_value=notes.G_SHARP)),
    'A': MajorChord(notes.Note(text_value=notes.A)),
    'A-': MinorChord(notes.Note(text_value=notes.A)),
    'A7': SevenChord(notes.Note(text_value=notes.A)),
    'Adim': DiminishedChord(notes.Note(text_value=notes.A)),
    'A#': MajorChord(notes.Note(text_value=notes.A_SHARP)),
    'A#-': MinorChord(notes.Note(text_value=notes.A_SHARP)),
    'A#7': SevenChord(notes.Note(text_value=notes.A_SHARP)),
    'A#dim': DiminishedChord(notes.Note(text_value=notes.A_SHARP)),
    'B': MajorChord(notes.Note(text_value=notes.B)),
    'B-': MinorChord(notes.Note(text_value=notes.B)),
    'B7': SevenChord(notes.Note(text_value=notes.B)),
    'Bdim': DiminishedChord(notes.Note(text_value=notes.B)),
}