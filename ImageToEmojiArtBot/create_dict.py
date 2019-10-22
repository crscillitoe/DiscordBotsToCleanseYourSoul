import numpy as np
import cv2
import requests
from requests import Response
import json

def main():
    with open('emojis.json') as f:
        json_data = json.load(f)

    to_save = {}
    for i in json_data['emojis']:
        src: str  = i['src']
        name: str = i['name']

        try:
            req: Response = requests.get(src)
            if req.status_code != 200:
                raise FuckException(bruh_wtf=True,
                                    jeff_coffin='is_a_very_dangerous_man',
                                    what_to_do_now="???")

            image = create_opencv_image_from_url(bytearray(req.content), 1, 1)

            red   = image[0][0][0]
            green = image[0][0][1]
            blue  = image[0][0][2]

            to_save[(red, green, blue)] = name
        except FuckException:
            print('fuk')
            pass

    print(to_save)

class FuckException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, None)

def create_opencv_image_from_url(image_as_bytearray: bytearray, width: int = 25, height: int = 25) -> np.matrix:
    img_array = np.asarray(image_as_bytearray, dtype=np.uint8)
    image_bgr = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)

if __name__ == '__main__':
    main()