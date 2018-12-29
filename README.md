# cybach
CYBACH is an algorithmic musical arrangement writer using abstract representations of notes, harmony, and rhythm to create musically substantive arrangements based on user-generated melodies and chord progressions. Cybach uses variables + weights to ensure musicality, e.g. two notes that are a minor 9th away will receive a negative score.

Cybach's composition process is basically:

<b>1.</b> Load user-generated melody and chords.

<b>2.</b> For each strong beat, insert a note for each part. Each note should be comfortably of in the range of the part it's writing for (S/A/T/B), not <b>too</b> far away from the last, etc.

<b>3.</b> Once a quarter note arrangement has been written, apply rhythmic/melodic transforms. Transforms could mean increasing the durations of some notes, adding suspension, turns, etc, while being mindful of what's going on in the rest of the parts/melody. E.g. Cybach discourages excessive simultaenous motion in both melody and other parts.
