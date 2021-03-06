from __future__ import division

# Algorithm variables


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~ KEY SIGNATURE RELEVANCE VARIABLES ~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Variables that help determine key signatures by providing a specific relevance of
# chords to specific key signatures.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Represents I or i in the key (major and minor respectively)
ONE_CHORD_HARMONY = 0.10

# Represents ii or ii(dim) in the key (major and minor respectively)
TWO_CHORD_HARMONY = 0.05

# Represents iii or III in the key (major and minor respectively)
THREE_CHORD_HARMONY = 0.05

# Represents IV or iv in the key (major and minor)
FOUR_CHORD_HARMONY = 0.05

# Represents V7 in the key
FIVE_DOMINANT_HARMONY = 0.20

# Represents V in the key
FIVE_MAJOR_HARMONY = 0.05

# Represents vi or VI in the key (major and minor)
SIX_CHORD_HARMONY = 0.05

# Represents vii(dim) in the keys (both major and minor)
MAJOR_SEVEN_DIMINISHED_HARMONY = 0.05

# Dominant V's are much more valuable in functional relationships
DOMINANT_FIVE_IN_FUNCTIONAL_RELEVANCE = 0.20

# Major V's are much less valuable than dominant V's in functional relationships
MAJOR_FIVE_IN_FUNCTIONAL_RELEVANCE = 0.05

# Represents a V -> I in a key
FIVE_ONE_FUNCTIONALITY = 0.25

# Represents a vii -> I in a key
SEVEN_ONE_FUNCTIONALITY = 0.10

# Represents a ii -> V in a key
TWO_FIVE_FUNCTIONALITY = 0.10

# Represents a IV -> V in a key
FOUR_FIVE_FUNCTIONALITY = 0.10

# Represents a V -> vi relationship
FIVE_SIX_FUNCTIONALITY = 0.10

# Chords that are on beat 1 are more indicative of a specific key signature
BEAT_ONE_COEF = 1.5

# The first chords of the piece is ultra indicative of the key
FIRST_BEAT_COEF = 2.5

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~ MISC VARIABLES ~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Variables whose family of variables is significant enough to have its own section.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Used to figure out measure phrasing. This is multiplied by the number of notes in the group.
RHYTHM_PHRASING_COEF = 0.01

# Added to a value determining measure phrasing when the placement of harmony (in time) matching phasing candidates
CHORD_PHRASING = 0.10

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~ NOTE PICKER VARIABLES ~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Note picker variables impact which config.resolution-level notes are selected
# on the first round of composition. See note_picker.py for more
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Until I'm 100% confident on how to implement rests, severely penalize all rests.
REST_PENALTY = -2.0

# Penalize lines that form parallel movement. Note candidates can receive this penalty up to three times
# in the event that all lines are parallel.
PARALLEL_MOVEMENT = -0.20

# Award 0.05 for each line that is in harmony with another one. Is not applied to harmony formed with
# the soprano line. Can be awarded up to 3 times per beat.
HARMONY_COEF = 0.6


def unique_pitch_score(unique_pitches):
    return ((2 ** unique_pitches) / 100) * HARMONY_COEF


# We're allowed to have some duplicates, but more than one every once in a while is too much.
DUPLICATE_COEF = 0.1


def duplicate(duplicate_count):
    return 0 - duplicate_count * DUPLICATE_COEF


# We don't want the bass to play the root of the next chord right before we hear the next chord
PREEMPTION = -0.1

# Prefer to have the bass play the root note on the first beat of the piece.
FIRST_BEAT_BASS_ROOT = 0.10

# Prefer to have the bass play the bass note on the beat 1
FIRST_BEAT_BASS_NOTE = 0.10

# Slight preference for the bass to choose the root. Comes into play when the same chord that is active
# on any given beat is the same chord as the previous beat and the bass note isn't the root.
BASS_ROOT_SAME_CHORD = 0.12

# For any given dominant seven chord, give a slight preference to voicing with the third.
THIRD_PREFERENCE = 0.05

# If there's a different note in the bass than the root, we should always choose it.
NON_ROOT_BASS_NOTE = 0.5

# When the chord changes, we really want to hear the root in the bass line.
BASS_NOTE_NEW_CHORD = 0.5

# As a line approaches the extremes of its register, start to decrease score. This variable is modified
# as it moves closer to register extremes with the following:
#
# (2 ** abs(soft_limit - val)) * vars.THRESHOLD_ENCROACHMENT
#
THRESHOLD_ENCROACHMENT = -0.01

# Similar to threshold encroachment in implementation. Score is modified as it move closer to a
# bad range. Modification follows:
#
# abs(soft_limit - val) * vars.PREFERRED_REGISTER
#
PREFERRED_REGISTER = -0.01

# All parts have a default motion tendency of 0.5. At 0.5, config.resolution level movement is "preferred" only in
# that no score is added or subtracted.
#
# If a new note candidate is a different pitch from the preview note, it "creates motion." If the part for which this
# note has a motion tendency > 0.5, then it will receive a score of (motion_tendency - 0.5) / MOTION_TENDENCY_DIVISOR
#
# If a new note candidate is the same pitch as the previous note, the candidate will receive a score of
# (0.5 - motion_tendency / MOTION_TENDENCY_DIVISOR)
#
#
MOTION_TENDENCY_DIVISOR = 2

# If a note pitch candidate results in linear motion, award it
LINEAR_MOTION = 0.20

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~ MOTIONIZER VARIABLES ~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Motionizer variables impact the synergy of transforms that are applied to the first
# round of composition.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Penalize note candidate pitches whose species is a half step away from the soprano
VERY_DISSONANT_WITH_SOPRANO = -0.20

# Penalize note candidate pitches which are a whole step away from the soprano
SLIGHTLY_DISSONANT_WITH_SOPRANO = -0.10

# We don't want to the bass to syncopate
SYNCOPATION_AVOIDANCE = -0.10

# Join transforms can result in 1's not being played in the bass. This is ordinarily bad
BASS_CROSS_BAR_LINE = -0.20

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~ TRANSFORM VARIABLES ~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Transform variables effect the score of individual transforms and how they
# react to one another.
#
# For all motion variables, remember that 0.50 is considered "no motion"
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Slightly penalize JoinTransforms that are the same on the same beat
JOIN_SAME = -0.02

# Motion score is equal to 0.50 - duration * JOIN_MOTION_COEFFICIENT
JOIN_MOTION_COEFFICIENT = 0.08

# In time signatures whose numerator is evenly divisible by 3, prefer big beats
JOIN_PREFER_BIG_BEATS = 1.0

# Slightly prefer the first beat of a the measure
TWO_BEAT_FIRST_BEAT = 0.02
# Strongly prefer being on weak beats (2 or 4 in 2/4 or 4/4 etc, and 3 and 5 in 6/8 etc)
TWO_BEAT_WEAK_BEAT = 0.10
# For every chord beyond one which this note spans, increase score by 0.04 (0.04 max of course)
TWO_BEAT_MULTIPLE_CHORDS = 0.04

# Slightly prefer the first beat of a the measure
THREE_BEAT_FIRST_BEAT = 0.02
# Strongly prefer being on weak beats in 2/4, 4/4, 6/4, etc
THREE_BEAT_WEAK_BEAT_DENOM_MULTIPLE_OF_2 = 0.15
# Slightly prefer being on weak beats in 3/4 or 6/8, etc. Significantly less musical in signatures like 4/4
THREE_BEAT_WEAK_BEAT_DENOM_MULTIPLE_OF_3 = 0.02
# For every chord beyond one which this note spans, increase score by 0.04 (0.04 max of course)
THREE_BEAT_MULTIPLE_CHORDS = 0.04

# Slightly prefer the first beat of a the measure
FOUR_BEAT_FIRST_BEAT = 0.02
# Slight prefer being on beat 2 in 4/4, but it's really not all that great
FOUR_BEAT_SECOND_BEAT = 0.03
# For every chord beyond one which this note spans, increase score by 0.04 (0.04 max of course)
FOUR_BEAT_MULTIPLE_CHORDS = 0.04

# Slightly prefer the first beat of a the measure
FIVE_BEAT_FIRST_BEAT = 0.14
# Slight prefer being on beat 5 in 6/8, cause I guess that's nice
FIVE_BEAT_FIFTH_BEAT = 0.03
# For every chord beyond one which this note spans, increase score by 0.04 (0.04 max of course)
FIVE_BEAT_MULTIPLE_CHORDS = 0.04

# Slightly dissuade the beat 2 in 6/8
SIX_BEAT_SECOND_BEAT = -0.02
# Slight prefer being on any beat but 2 in 6/8
SIX_BEAT_ANY_OTHER_BEAT = 0.05
# Slightly prefer 3/4 because I guess it's nice
SIX_BEAT_THREE_FOUR = 0.03
# For every chord beyond one which this note spans, increase score by 0.04 (0.04 max of course)
SIX_BEAT_MULTIPLE_CHORDS = 0.04

# Two EighthNoteTransforms, when applied at the same time, result in dissonance
EIGHTH_NOTE_DISSONANCE = -0.10
# Two EighthNoteTransforms, when applied at the same time, indicate dominant relationship with the next chord
EIGHTH_NOTE_DOMINANT = 0.10
# Two EighthNoteTransforms, when applied at the same time, indicate subdominant relationship with the next chord
EIGHTH_NOTE_SUBDOMINANT = 0.05
# Two EighthNoteTransforms, when applied at the same time, create parallel movement
EIGHTH_NOTE_PARALLEL = -0.20
# Two EighthNoteTransforms being applied at the same time are probably the exact same
EIGHTH_NOTE_SAME = -0.02
# While sustain one chord for an extended period of time, notes tend to "flicker" back and forth.
FLICKER_COEF = -0.20

# MajorThirdScalarTransform intrinsic motion
MAJOR_THIRD_SCALAR_MOTION = 0.58
# First beat of the piece we would like some movement
MAJOR_THIRD_SCALAR_BEAT_ONE = 0.08
# Transforms continues a linear line
MAJOR_THIRD_SCALAR_CONTINUES_LINEARITY = 0.20
# Default musicality
MAJOR_THIRD_SCALAR_DEFAULT_MUSICALITY = 0.08

# MinorThirdScalarTransform intrinsic motion
MINOR_THIRD_SCALAR_MOTION = 0.56
# First beat of the piece we would like some movement
MINOR_THIRD_SCALAR_BEAT_ONE = 0.08
# Transforms continues a linear line
MINOR_THIRD_SCALAR_CONTINUES_LINEARITY = 0.20
# Default musicality
MINOR_THIRD_SCALAR_DEFAULT_MUSICALITY = 0.08

# ArpeggialTransform intrinsic motion
ARPEGGIAL_MOTION = 0.62
# Chord during transform and immediately after transform are the same
ARPEGGIAL_SAME_CHORD = 0.08
# Default musicality
ARPEGGIAL_NEW_CHORD = 0.14

# HalfStepNeighborTransform intrinsic motion
HALF_NEIGHBOR_MOTION = 0.53
# Default musicality
HALF_NEIGHBOR_DEFAULT_MUSICALITY = 0.08
# If the chord during the transform and immediately after are the same
HALF_NEIGHBOR_SAME_CHORD = 0.05

# WholeStepNeighborTransform intrinsic motion
WHOLE_NEIGHBOR_MOTION = 0.54
# Default musicality
WHOLE_NEIGHBOR_DEFAULT_MUSICALITY = 0.08
# If the chord during the transform and immediately after are the same
WHOLE_NEIGHBOR_SAME_CHORD = 0.05

# ApproachTransform intrinsic motion
APPROACH_MOTION = 0.60
# Default musicality
APPROACH_DEFAULT_MUSICALITY = 0.07
# If the next chord is the tonic and the key changes next beat
APPROACH_KEY_CHANGE = 0.20
# If the next chord is new and the next pitch is the root
APPROACH_NEW_CHORD_ROOT = 0.12
