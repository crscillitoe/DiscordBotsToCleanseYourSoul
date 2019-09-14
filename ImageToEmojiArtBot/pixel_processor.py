"""
Contains helper functions for processing
images and converting them to emojis
"""
from typing import *

color_dictionary = {
    (0, 0, 0): 'Sample Text'
}

def get_closest_key(red: int, green: int, blue: int) -> Tuple[int, int, int]:
    smallest_distance = 10000 # Larger than max smallest distance
    for k in color_dictionary.keys():
        diff_red   = abs(k[0] - red)
        diff_green = abs(k[1] - green)
        diff_blue  = abs(k[2] - blue)
        if diff

    return (red, green, blue)

def convert_pixel_to_emoji(red: int, green: int, blue: int ) -> str:
    """
    Given an RGB value (0-255, 0-255, 0-255),
    returns the emoji closest to this color in the
    dictionary.
    """
    return color_dictionary[get_closest_key(red, green, blue)]


if __name__ == "__main__":
    print(convert_pixel_to_emoji(0, 0, 0))
    print(convert_pixel_to_emoji(1, 2, 3))