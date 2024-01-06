import cv2
import numpy as np


if __name__ == '__main__':
    img = cv2.imread('cropped.png')
    print(f'Shape: {img.shape}')
    H, W = img.shape[:2]
    print(f'Shape Top edge: {img[0, :, :].shape}')
    print(f'Shape Bottom edge: {img[H-1, :, :].shape}')
    print(f'Shape Left edge: {img[:, 0, :].shape}')
    print(f'Shape Top edge: {img[:, W-1, :].shape}')
    np_agg = np.vstack(
        tup = (
            img[0, :, :],
            img[H-1, :, :],
            img[:, 0, :],
            img[:, W-1, :]
        )
    )

    print(f'Shape np_agg: {np_agg.shape}')
    avg_pixel = np.average(np_agg, axis= 0)

    print(f'avg_pixel: {avg_pixel}')

