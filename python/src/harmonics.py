from enum import Enum

class Harmonics(Enum):
    Low = 0
    High = 1

    def flip(self):
        return Low if self == High else Low
