from typing import Text
from PIL import Image
import numpy as np
import cv2

def rgba2rgb(
    pil_img: Image,
)-> Image:
    """"""
    row, col = pil_img.size
    mode = pil_img.mode
    
    print(f'row:{row}\ncol: {col}\nmode: {mode}')

    np_img = np.asarray(
        a = pil_img,
        dtype= np.uint8
    )

    if mode == "RGB": # RGB
        return pil_img
    elif mode == "RGBA": # RGBA
        rgb = np.zeros(
            shape= (row, col, 3),
            dtype= np.float32
        )

        image, a = np_img[...,:3], np_img[...,3:]/255.0

        # Convert
        rgb = image * a
        res = np.asarray(image, np.uint8)

        return Image.fromarray(res)
    else:
        raise Exception("Error image format")
    

if __name__ == "__main__":
    IMG_PATH = "input/Cao_Son_Hanh_Canh.png"
    print(IMG_PATH)
    img = rgba2rgb(
        Image.open(IMG_PATH)
    )

    img.save("input/demo_convert_rgba_2_rgb.jpg")