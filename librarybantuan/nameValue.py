from enum import Enum

class Color:
    def RGB(r, g, b):
        return (r, g, b)

    SCORE        = RGB(255, 255, 255)      
    FOOD         = RGB(200, 0, 0)          
    BACKGROUND   = RGB(0, 0, 0)       
    BORDER       = RGB(85, 224, 127)      
    SNAKE_BODY   = RGB(0, 0, 255)     
    SNAKE_BORDER = RGB(0, 100, 255) 
    

class Direction(Enum):
    LEFT  = 1
    RIGHT = 2
    UP    = 3
    DOWN  = 4

class Turn:
    STRAIGHT = [1, 0, 0]
    RIGHT    = [0, 1, 0]
    LEFT     = [0, 0, 1]

class Path:
    MODEL = './model/mymodel.model'
    MEMORY = './model/memory.mem'