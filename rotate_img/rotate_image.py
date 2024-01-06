import cv2
import numpy as np
def rotate_image(
    image,
    angle: float,
):
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)
    # rotate our image by 45 degrees around the center of the image
    M = cv2.getRotationMatrix2D((cX, cY), angle , 1.0)
    rotated = cv2.warpAffine(image, M, (w, h))
    return rotated
    

if __name__ == '__main__':
    # Thanks: https://pyimagesearch.com/2021/01/20/opencv-rotate-image/
    # load the image and show it
    img_path = "cropped.png"
    image = cv2.imread(img_path)
    
    cv2.imshow("Original", image)
    
    # grab the dimensions of the image and calculate the center of the
    # image
    # (h, w) = image.shape[:2]
    # (cX, cY) = (w // 2, h // 2)
    # # rotate our image by 45 degrees around the center of the image
    angle = -13
    # M = cv2.getRotationMatrix2D((cX, cY), angle , 1.0)
    # rotated = cv2.warpAffine(image, M, (w, h))
    rotated = rotate_image(
        image,
        angle
    )
    
    cv2.imshow(f"Rotated by {angle} Degrees", rotated)
    # # rotate our image by -90 degrees around the image
    # M = cv2.getRotationMatrix2D((cX, cY), -90, 1.0)
    # rotated = cv2.warpAffine(image, M, (w, h))
    # cv2.imshow("Rotated by -90 Degrees", rotated)
    print(rotated)

    cv2.waitKey(0)
    cv2.destroyAllWindows()