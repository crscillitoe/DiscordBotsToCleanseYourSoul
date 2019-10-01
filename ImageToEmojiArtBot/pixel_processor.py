"""
Contains helper functions for processing
images and converting them to emojis
"""
from typing import *
from constants_two import color_dictionary

def get_closest_key(red: int, green: int, blue: int) -> Tuple[int, int, int]:
    """
    Iterates over the keys in the dictionary, returns closest key
    """
    smallest_distance = 1000000 # Larger than max smallest distance
    r = 0
    g = 0
    b = 0
    for k in color_dictionary.keys():
        diff_red   = abs(k[0] - red) ** 2
        diff_green = abs(k[1] - green) ** 2
        diff_blue  = abs(k[2] - blue) ** 2
        summation = diff_red + diff_green + diff_blue
        if summation < smallest_distance:
            smallest_distance = summation
            r, g, b = k

    return (r, g, b)

def convert_pixel_to_emoji(red: int, green: int, blue: int ) -> str:
    """
    Given an RGB value (0-255, 0-255, 0-255),
    returns the emoji closest to this color in the
    dictionary.
    """
    return f'{color_dictionary[get_closest_key(red, green, blue)]}'

def convert_image_to_string(image):
    to_return = ''
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            red: int   = image[i][j][0]
            green: int = image[i][j][1]
            blue: int  = image[i][j][2]
            to_return += convert_pixel_to_emoji(red, green, blue)
        to_return += '|'

    return to_return

if __name__ == "__main__":
    print(convert_pixel_to_emoji(0, 0, 0))
    print(convert_pixel_to_emoji(1, 2, 3))