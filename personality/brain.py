from random import randint, choice
from typing import Any
from time import sleep
from enum import IntEnum
from threading import Thread

ActionTuple = tuple[
    int,  # min wellness
    int,  # min fullness
    int,  # min displeasedness
    int,  # min tiredness
    int,  # min excitedness
    int,  # max wellness
    int,  # max fullness
    int,  # max displeasedness
    int,  # max tiredness
    int,  # max excitedness
    int,  # interaction (0 = no interaction required)
    Any,  # payload (string for example)
]


class Interaction(IntEnum):
    """
    enumerator class defining interaction types

    for all intents and purposes, this is an IntEnum, but the IntEnum base class is not supported by micropython.
    """

    NONE = 0
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

        # decay each attribute, and snap it to the range 0-100 if outside it.
        for attr in [
            "wellness",
            "fullness",
            "displeasedness",
            "tiredness",
            "excitedness",
        ]:
            value = getattr(self, attr)
            value = max(0, value - decay_rate)
            setattr(self, attr, min(100, value))


# TODO: add logic for reactions
class Brain(Thread):
    """Contains the login implementing the behavior of the animatronic toy."""

    ACTION_TABLE: list[ActionTuple] = [
        (0, 0, 0, 0, 0, 100, 100, 100, 100, 100, 0, "idle action")
    ]

    def __init__(self):
        # set thread parameters up and initialize the class as a thread
        super().__init__()
        self.daemon = True

        # holding these in a separate class lets us call the values out with dot notation like self.emotions.wellness which looks very nice.
        self.emotions = Emotions()

    def run(self):
        """thread run function, ticks constantly once the thread starts."""
        while True:
            self._tick()

    def _tick(self):
        """tick function used for periodic action running and emotion decay"""
        self.emotions.decay()
        self._random_delay()
        self._action(Interaction.NONE)

    def interact(self, interaction: Interaction):
        """logic for handling user interaction with the animatronic toy"""
        self._action(interaction)

    def _random_delay(self):
        """factoring in current state, provide a random delay before running an interval action"""
        # work out using the emotion values an overall "stress" factor.
        # if the toy is tired, it should react less quickly. it should be more quick to react if it's unwell, excited, or hungry.
        wellness, fullness, displeasedness, tiredness, excitedness = self.emotions.get()
        # Invert wellness and fullness
        unwell = 100 - wellness
        hungry = 100 - fullness

        # Combine factors with integer weights (powers of 2 for shifts)
        stress = (
            (unwell << 1)
            + (hungry << 1)
            + displeasedness
            + excitedness
            - (tiredness << 1)
        )

        # Clamp stress to 0-255 for byte-friendly delay scaling
        stress = max(0, min(255, stress >> 2))
        print(f"calculated stress: {stress}")

        # sleep for the stress value + a random offset
        sleep((stress + randint(1, 100)) >> 1)

    def _action(self, interaction: Interaction = Interaction.NONE):
        """private method that finds a runnable action in the action table and passes it to the  action runner"""
        emotions = self.emotions.get()
        runnable = []
        for entry in self.ACTION_TABLE:
            mins = entry[0:5]
            maxs = entry[5:10]
            int_req = entry[10]
            payload = entry[11]

            # Check if emotions fall within min-max ranges and interaction matches (or zero)
            if all(
                min_v <= emo <= max_v for min_v, emo, max_v in zip(mins, emotions, maxs)
            ):
                if int_req == 0 or int_req == interaction:
                    runnable.append(payload)

        if runnable:
            selected = choice(runnable)
            self._execute_action(selected)
        else:
            print("No runnable actions found for current state.")

    def _execute_action(self, payload: Any):
        """example action runner: print the payload string. intended to be overwritten by subclasses"""
        print(payload)
