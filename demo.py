import numpy as np
import cv2


if __name__ == '__main__':
    path = 'D:/Desktop/tang_tuong_phan.png'
    img = cv2.imread(filename=path)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    print(img.shape)
    # img.('D:/Desktop/tang_tuong_phan_RGB.png')
