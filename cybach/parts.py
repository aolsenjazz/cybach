import notes


class Part:

    def __init__(self, max_low, max_high):
        self.max_low = max_low
        self.max_high = max_high
        self.middle = (max_high + max_low) / 2


ALTO = Part(55, 72)
TENOR = Part(48, 65)
BASS = Part(40, 60)
