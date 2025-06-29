# NOTE: this file has been kept intentionally barren of stdlibs to ensure that this module is valid both in full python as well as micropython.
# This is to support the potential use of this as a personality module for brain-chipped animatronic toys.


class Interaction:
    """
    enumerator class defining interaction types

    for all intents and purposes, this is an IntEnum, but the IntEnum base class is not supported by micropython.
    """

    SOUND = 1
    BACK_SENSOR = 2
    TAIL_PULL = 3
    UPSIDE_DOWN = 4
    SHAKE = 5


class Emotions:
    """
    holds the emotion values used to manage an animatronic toy's personality

    The reverse engineering efforts revealed that the original toy used 5 values, each stored as an integer 0-100 as a single unsigned byte.
    """

    def __init__(self):
        # initialize the emotions at 0.
        self.wellness: int = 0
        self.fullness: int = 0
        self.displeasedness: int = 0
        self.tiredness: int = 0
        self.excitedness: int = 0

    def get(self) -> tuple[int, int, int, int, int]:
        """returns the emotion values as a tuple"""
        return (
            self.wellness,
            self.fullness,
            self.displeasedness,
            self.tiredness,
            self.excitedness,
        )

    def set(self, vals: tuple[int, int, int, int, int]):
        """takes a tuple and replaces the current emotion values with it"""
        self.wellness = vals[0]
        self.fullness = vals[1]
        self.displeasedness = vals[2]
        self.tiredness = vals[3]
        self.excitedness = vals[4]

    def decay(self):
        """
        causes the emotion value decay when triggered, intended to be run as a ticker.

        the exact decay rate is not made clear by the reverse engineering documentation.
        for now, we assume a decay rate of 1 per tick.
        """
        decay_rate: int = 1

        for emotion in [
            self.wellness,
            self.fullness,
            self.displeasedness,
            self.tiredness,
            self.excitedness,
        ]:
            # if the emotion is larger than the decay rate, decay by that amount. if it's smaller, snap to minimum.
            if emotion >= decay_rate:
                emotion -= decay_rate
            else:
                emotion = 0

            # snap the emotion to the max value if it's grown larger.
            emotion = 100 if emotion > 100 else emotion


class Brain:
    def __init__(self):
        # holding these in a separate class lets us call the values out with dot notation like self.emotions.wellness which looks very nice.
        self.emotions = Emotions()

    def tick(self):
        """tick function used for periodic action running and emotion decay"""
        self.emotions.decay()

    def interact(self, interaction: Interaction):
        """logic for handling user interaction with the animatronic toy"""
