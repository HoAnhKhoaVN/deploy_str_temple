import numpy as np
from PIL import Image
import cv2
# import imutils

def crop_image_polygon(
    img,
    points: list,

)-> tuple:
    # region Get mask
    mask = np.zeros(img.shape[0:2], dtype=np.uint8)
    points = np.array([points])
    # endregion

    # region get contours
    cv2.drawContours(
        mask,
        [points],
        -1,
        (255, 255, 255), # White
        -1,
        cv2.LINE_AA
    )
    # res = cv2.bitwise_and(img,img,mask = mask)
    # x,y,w,h = cv2.boundingRect(points) # returns (x,y,w,h) of the rect
    # cropped = res[y: y + h, x: x + w]
    # endregion

    # region get 
    return mask
    # endregion

if __name__ == '__main__':

    img = cv2.imread("366641616_2264556887067173_1651877982799532575_n.jpg")
    bbox = [[117, 99], [217, 74], [284, 353], [184, 378]]
    (
        res,
        mask,
        cropped
    )= crop_image_polygon(
        img = img,
        points= bbox
    )
    # mask = np.zeros(img.shape[0:2], dtype=np.uint8)
    # points = np.array([[[117, 99], [217, 74], [284, 353], [184, 378]]])

    # #method 1 smooth region
    # cv2.drawContours(mask, [points], -1, (255, 255, 255), -1, cv2.LINE_AA)

    # #method 2 not so smooth region
    # # cv2.fillPoly(mask, points, (255))

    # res = cv2.bitwise_and(img,img,mask = mask)
    # rect = cv2.boundingRect(points) # returns (x,y,w,h) of the rect
    # cropped = res[rect[1]: rect[1] + rect[3], rect[0]: rect[0] + rect[2]]

    # ## create the white background of the same size of original image
    # wbg = np.ones_like(img, np.uint8)*255
    # cv2.bitwise_not(wbg,wbg, mask=mask)
    # # overlap the resulted cropped image on the white background
    # dst = wbg+res

    # cv2.imshow('Original',img)
    # cv2.imshow("Mask",mask)
    # cv2.imshow("Cropped", cropped )
    # cv2.imshow("Samed Size Black Image", res)
    # cv2.imshow("Samed Size White Image", dst)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    cv2.imwrite(
        filename= "D:/Master/OCR_Nom/fulllow_ocr_temple/experiment/cropped.png",
        img = cropped
    )