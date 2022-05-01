from enum import Enum
from tkinter import LEFT, RIGHT

from matplotlib.pyplot import cla

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4