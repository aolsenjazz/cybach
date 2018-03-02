# config file for transferring globals. global variables set in other files are:
#
# resolution: samples per quarter note
# song_length: length of the song in samples

resolution = 96
song_length = 0
minimum_time_divisor = 4
maximum_strong_beat_subdivisions = 3


def minimum_time_unit():
    """
    When composing rhythms < a beat, we need to set an artificial limit on what can be composed;
    nobody wants to hear composition with 96th notes. Function rather than a variable because it depends
    on resolution, which is mutable.

    :return: Number representing the smallest number of samples which can be composed.
    """
    return resolution / minimum_time_divisor
