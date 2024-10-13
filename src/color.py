from enum import Enum
from typing import Tuple

class Color:
    class ColorBase(Enum): 
        RED = (255, 0, 0)
        ORANGE = (255, 165, 0)
        GREEN = (0, 255, 0)
        BLUE = (0, 0, 255)
        MAGENTA = (255, 0, 255)
        YELLOW = (255, 255, 0)
        CYAN = (0, 255, 255)
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
    
    def __init__(self, rgb: Tuple = ColorBase.BLACK.value):
        self.__rgb: Tuple = (0, 0, 0) 
        self.rgb = rgb
    
    @property
    def rgb(self):
        return self.__rgb

    @rgb.setter
    def rgb(self, color: Tuple):
        new_rgb: Tuple = tuple(max(min(color[i], 255), 0) for i in range(3))
        self.__rgb: Tuple = new_rgb

    def change_color(self, color: Tuple):
        # Subtract two RGB values and clamp them to the maximum value of 255
        new_rgb: Tuple = tuple(max(min(self.__rgb[i] + color[i], 255), 0) for i in range(3))
        self.__rgb = new_rgb

    def __repr__(self):
        return f"Color({self.__rgb[0]}, {self.__rgb[1]}, {self.__rgb[2]})"