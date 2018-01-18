import os

#
# Constants
#

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

TEST_MIDI = ROOT_DIR + '/test/midi/'
EXAMPLES = ROOT_DIR + '/examples/'
OUT_DIR = ROOT_DIR + '/out/'

# The midi note resolution. This resolution lets us support up to 24 notes/beat. If a midi track is supplied
# with a smaller resolution, it gets rejected. Nobody was composing classical music at that resolution.
RESOLUTION = 24

EIGHTH_NOTE = RESOLUTION / 2
DOTTED_EIGHTH_NOTE = int(EIGHTH_NOTE * 1.5)
SIXTEENTH_NOTE = RESOLUTION / 4
DOTTED_SIXTEENTH_NOTE = int(SIXTEENTH_NOTE * 1.5)
THIRTY_SECOND_NOTE = RESOLUTION / 8
DOTTED_THIRTY_SECOND_NOTE = THIRTY_SECOND_NOTE + (THIRTY_SECOND_NOTE / 2)
EIGHTH_NOTE_TRIPLET = RESOLUTION / 3
SIXTEENTH_NOTE_TRIPLET = RESOLUTION / 6
THIRTY_SECOND_NOTE_TRIPLET = RESOLUTION / 12
QUARTER_NOTE = RESOLUTION
DOTTED_QUARTER_NOTE = RESOLUTION + (RESOLUTION / 2)
HALF_NOTE = QUARTER_NOTE * 2
DOTTED_HALF_NOTE = HALF_NOTE + QUARTER_NOTE
WHOLE_NOTE = QUARTER_NOTE * 4
DOTTED_WHOLE_NOTE = WHOLE_NOTE + HALF_NOTE

ACCEPTABLE_NOTE_VALUES = [EIGHTH_NOTE, DOTTED_EIGHTH_NOTE, SIXTEENTH_NOTE, DOTTED_SIXTEENTH_NOTE,
                          DOTTED_THIRTY_SECOND_NOTE, THIRTY_SECOND_NOTE, EIGHTH_NOTE_TRIPLET,
                          SIXTEENTH_NOTE_TRIPLET, THIRTY_SECOND_NOTE_TRIPLET, QUARTER_NOTE, DOTTED_QUARTER_NOTE,
                          HALF_NOTE, DOTTED_HALF_NOTE, WHOLE_NOTE, DOTTED_WHOLE_NOTE]

INT_DURATION_MAP = {
    EIGHTH_NOTE: 'eighth_note',
    DOTTED_EIGHTH_NOTE: 'dotted_eighth_note',
    SIXTEENTH_NOTE: 'sixteenth_note',
    DOTTED_SIXTEENTH_NOTE: 'dotted_sixteenth_note',
    THIRTY_SECOND_NOTE: 'thirty_second_note',
    DOTTED_THIRTY_SECOND_NOTE: 'dotted_thirty_second_note',
    EIGHTH_NOTE_TRIPLET: 'eighth_note_triplet',
    SIXTEENTH_NOTE_TRIPLET: 'sixteenth_note_triplet',
    THIRTY_SECOND_NOTE_TRIPLET: 'thirty_second_note_triplet',
    QUARTER_NOTE: 'quarter_note',
    DOTTED_QUARTER_NOTE: 'dotted_quarter_note',
    HALF_NOTE: 'half_note',
    DOTTED_HALF_NOTE: 'dotted_half_note',
    WHOLE_NOTE: 'whole_note',
    DOTTED_WHOLE_NOTE: 'dotted_whole_note'
}


TEXT_DURATION_MAP = {
    'eighth_note': EIGHTH_NOTE,
    '8th_note': EIGHTH_NOTE,
    '8th': EIGHTH_NOTE,
    'eighth': EIGHTH_NOTE,
    'dotted_eighth_note': DOTTED_EIGHTH_NOTE,
    'dotted_8th_note': DOTTED_EIGHTH_NOTE,
    'dotted_8th': DOTTED_EIGHTH_NOTE,
    'dotted_eighth': DOTTED_EIGHTH_NOTE,
    'sixteenth_note': SIXTEENTH_NOTE,
    '16th_note': SIXTEENTH_NOTE,
    '16th': SIXTEENTH_NOTE,
    'sixteenth': SIXTEENTH_NOTE,
    'dotted_sixteenth_note': DOTTED_SIXTEENTH_NOTE,
    'dotted_16th_note': DOTTED_SIXTEENTH_NOTE,
    'dotted_16th': DOTTED_SIXTEENTH_NOTE,
    'dotted_sixteenth': DOTTED_SIXTEENTH_NOTE,
    'thirty_second_note': THIRTY_SECOND_NOTE,
    '32nd_note': THIRTY_SECOND_NOTE,
    '32nd': THIRTY_SECOND_NOTE,
    'thirty_second': THIRTY_SECOND_NOTE,
    'thirtysecond': THIRTY_SECOND_NOTE,
    'thirtysecond_note': THIRTY_SECOND_NOTE,
    'dotted_thirty_second_note': DOTTED_THIRTY_SECOND_NOTE,
    'dotted_thirtysecond_note': DOTTED_THIRTY_SECOND_NOTE,
    'dotted_32nd_note': DOTTED_THIRTY_SECOND_NOTE,
    'dotted_32nd': DOTTED_THIRTY_SECOND_NOTE,
    'dotted_thirty_second': DOTTED_THIRTY_SECOND_NOTE,
    'dotted_thirtysecond': DOTTED_THIRTY_SECOND_NOTE,
    'eighth_note_triplet': EIGHTH_NOTE_TRIPLET,
    '8th_note_triplet': EIGHTH_NOTE_TRIPLET,
    '8th_triplet': EIGHTH_NOTE_TRIPLET,
    'eighth_triplet': EIGHTH_NOTE_TRIPLET,
    'sixteenth_note_triplet': SIXTEENTH_NOTE_TRIPLET,
    '16th_note_triplet': SIXTEENTH_NOTE_TRIPLET,
    '16th_triplet': SIXTEENTH_NOTE_TRIPLET,
    'sixteenth_triplet': SIXTEENTH_NOTE_TRIPLET,
    'thirty_second_note_triplet': THIRTY_SECOND_NOTE_TRIPLET,
    '32nd_note_triplet': THIRTY_SECOND_NOTE_TRIPLET,
    '32nd_triplet': THIRTY_SECOND_NOTE_TRIPLET,
    'thirty_second_triplet': THIRTY_SECOND_NOTE_TRIPLET,
    'thirtysecond_triplet': THIRTY_SECOND_NOTE_TRIPLET,
    'thirtysecond_note_triplet': THIRTY_SECOND_NOTE_TRIPLET,
    'quarter_note': QUARTER_NOTE,
    '1/4_note': QUARTER_NOTE,
    'quarter': QUARTER_NOTE,
    '1/4': QUARTER_NOTE,
    'dotted_quarter_note': DOTTED_QUARTER_NOTE,
    'dotted_1/4_note': DOTTED_QUARTER_NOTE,
    'dotted_quarter': DOTTED_QUARTER_NOTE,
    'dotted_1/4': DOTTED_QUARTER_NOTE,
    'half_note': HALF_NOTE,
    '1/2_note': HALF_NOTE,
    'half': HALF_NOTE,
    '1/2': HALF_NOTE,
    'dotted_half_note': DOTTED_HALF_NOTE,
    'dotted_1/2_note': DOTTED_HALF_NOTE,
    'dotted_half': DOTTED_HALF_NOTE,
    'dotted_1/2': DOTTED_HALF_NOTE,
    'whole_note': WHOLE_NOTE,
    'whole': WHOLE_NOTE,
    'dotted_whole_note': DOTTED_WHOLE_NOTE,
    'dotted_whole': DOTTED_WHOLE_NOTE
}


SUBDIVISIONS = (EIGHTH_NOTE, SIXTEENTH_NOTE, THIRTY_SECOND_NOTE, EIGHTH_NOTE_TRIPLET, SIXTEENTH_NOTE_TRIPLET,
                THIRTY_SECOND_NOTE_TRIPLET, QUARTER_NOTE, DOTTED_EIGHTH_NOTE, DOTTED_SIXTEENTH_NOTE)

DEFAULT_VELOCITY = 120
