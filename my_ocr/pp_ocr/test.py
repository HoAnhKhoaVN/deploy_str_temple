# from log.logger import setup_logger
# setup_logger()
from paddleocr import PaddleOCR
pdocr = PaddleOCR(use_angle_cls=True, lang='ch', det_db_thresh=0.2)
from time import time


def ocr(
    img_path : str,
    time_analysis: dict = {}
)-> list:
    s = time()
    # result = pdocr.ocr(img_path, cls=False, det= False, rec= True)[0]
    result = pdocr.ocr(img_path, cls=False)[0]
    print(f"result in test OCR: {result}")
    e = time()
    time_analysis['ppocr_time'] = e - s

    s = time()
    res= []
    # region Postprocessing  
    if result:
        for line in result:
            _bbox, (text, prop) = line
            bbox = [[int(bb[0]), int(bb[1])] for bb in _bbox]
            res.append([bbox, text, prop])
    # endregion
    e = time()
    time_analysis['ppocr_postprocess'] = e - s
    return res, time_analysis
    


if __name__ == "__main__":
    img_path = "D:\\Master\\OCR_Nom\\deploy\\azure\\str_vietnam_temple\\input_2\\err2.jpg"
    result, time_analysis = ocr(img_path)
    bbox, text, prop = result[0]
    print(f'bbox: {bbox}')
    print(f'text: {text} - prop: {prop}')
    print(f'Time analysis: {time_analysis}')
        

