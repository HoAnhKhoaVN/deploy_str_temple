import cv2
import numpy as np
PADDING_PIXEL = 3

def detect_and_crop_image(
    img: np.ndarray
)-> np.ndarray:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    contours, _ = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt, True), True)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(cnt)
            cropped = img[y+PADDING_PIXEL: y + h-PADDING_PIXEL, x+PADDING_PIXEL: x + w-PADDING_PIXEL]
            return cropped
    else: # don't find any rectangle box
        return img
    



if __name__ == '__main__':
    IMG = 'cropped_image_pil_1.png'
    img = cv2.imread(IMG)

    cropped = detect_and_crop_image(
        img= img
    )
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # contours, _ = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # for cnt in contours:
    #     approx = cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt, True), True)
    #     if len(approx) == 4:
    #         x, y, w, h = cv2.boundingRect(cnt)
    # cropped = img[y: y + h, x: x + w]
    cv2.imwrite("cropped.png",cropped)