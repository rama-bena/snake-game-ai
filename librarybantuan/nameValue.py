from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])

class Move():
    UP    = [1, 0, 0, 0]
    RIGHT = [0, 1, 0, 0]
    DOWN  = [0, 0, 1, 0]
    LEFT  = [0, 0, 0, 1]

class Color:
    SCORE = (255, 255, 255)      # putih
    FOOD  = (200, 0, 0)          # merah
    BACKGROUND = (0, 0, 0)       # hitam
    BORDER = (85, 224, 127)      # hijau
    SNAKE_BODY = (0, 0, 255)     # biru muda
    SNAKE_BORDER = (0, 100, 255) # biru tua