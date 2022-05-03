from enum import Enum

class Direction(Enum):
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4

class Turn:
    STRAIGHT = [1, 0, 0]
    RIGHT = [0, 1, 0]
    LEFT = [0, 0, 1]