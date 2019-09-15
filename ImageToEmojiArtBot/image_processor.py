import numpy as np
import cv2

def convert_image_to_pixel_matrix(request):
    image = create_opencv_image_from_url(request)
    return image

def create_opencv_image_from_url(image_as_bytearray: bytearray, width: int = 25, height: int = 25) -> np.matrix:
    img_array = np.asarray(image_as_bytearray, dtype=np.uint8)
    image_bgr = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)

if __name__ == "__main__":
    print(convert_image_to_pixel_matrix(1))