import argparse
import os
from utils.check_language import is_han_nom
from my_ocr.pp_ocr.predict import ocr
from translate.hcmus_api import hcmus_translate
from my_postprocess.postprocess import _postprocess
from my_postprocess._postprocess_remove_bg import PostProcessRmText
import logging
from typing import Text
from PIL import Image
# from log.logger import setup_logger
from time import time
# setup_logger()
from my_postprocess.config import (
    REMOVE_TEXT,
    FILL_COLOR
)

def process(
    image_input_file: Text,
    silent: bool = False,
    mode: Text = REMOVE_TEXT

)-> Image:
    time_analysis = dict()
    # region 1. Preprocessing
    # endregion Preprocessing

    # region 2. OCR
    start_time = time()
    result, time_analysis = ocr(image_input_file, time_analysis)
    end_time = time()
    time_analysis['full_ocr_time'] = end_time - start_time
    if not silent:
        print(f'Result: {result}')

    # endregion OCR

    # region 3. Chinese language model
    # endregion

    # region 4. Translate to Vietnamese
    start_time = time()
    list_dict_result = []

    for bbox, han_nom_script, _ in result:
        # print(f'bbox: {bbox}')
        # print(f'text: {han_nom_script}')
        logging.debug(f"han_nom_script : {han_nom_script}")
        
        # region check is latin characters
        if not is_han_nom(han_nom_script):
            if not silent:
                print(f'==> {han_nom_script} is Latin characters!!!')
            continue

        # endregion

        # translation_script = hvdic_translate(text = han_nom_script)
        translation_script = hcmus_translate(text = han_nom_script)
        list_dict_result.append({
            'bbox': bbox,
            'text': translation_script
            }
        )
    end_time = time()
    time_analysis['translate_time'] = end_time - start_time

    if not silent:
        print(f'list_dict_result: {list_dict_result}')
    logging.debug(f"After: {list_dict_result}")

    # endregion

    # region 5. Postprocessing
    start_time = time()
    if mode == FILL_COLOR:
        pil_img_output = _postprocess(
            image_fn= image_input_file,
            list_dict_result = list_dict_result,
        )

    # remove text from background
    elif mode == REMOVE_TEXT:
        PostProcessRmText(
            image = image_input_file,
            list_bbox_text = list_dict_result,
            debug= False,
            quality= False,
        ).postprocess()
    else:
        raise Exception(f'Wrong type of mode for postprocess. Only `rm_text` or `fill_color` (not `{mode}`)')

    end_time = time()
    time_analysis['postprocess_time'] = end_time - start_time
    # endregion

    end_time = time()
    return pil_img_output, time_analysis

def main():
    # region 1. Input
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", required=True,
        help="Đường dẫn đến ảnh muốn nhận dạng")
    
    ap.add_argument("-o", "--output", required=True,
        help="Đường dẫn đến ảnh kết quả")
    args = vars(ap.parse_args())

    _INPUT = args["input"]
    _OUTPUT = args["output"]
    
    logging.info("================================")
    logging.info(f"Input: {_INPUT}")
    logging.info(f"Output: {_OUTPUT}")
    # endregion Input

    # region 2. main process
    pil_img_output, time_analysis = process(image_input_file=_INPUT)

    # endregion

    # region 3. Output
    pil_img_output.save(_OUTPUT)
    # endregion

    # region 4. Analysis time
    print(time_analysis)
    # endregion
    logging.info("==============END TASK==================")


def testcase_1():
    IMG_NAME = 'cau_doi_1'
    MODE = FILL_COLOR
    img, time_analysis = process(
        image_input_file=f'input/{IMG_NAME}.jpg',
        mode= MODE
    )
    
    OUT_PATH = f"output/{IMG_NAME}__{MODE}.jpg"
    img.save(OUT_PATH)

    print(f'Save success with path : {OUT_PATH}')

    print(f'Time analysis: {time_analysis}')

    
def testcase_2():
    IMG_NAME = 'cau_doi_1'
    MODE = REMOVE_TEXT
    img, time_analysis = process(
        image_input_file=f'input/{IMG_NAME}.jpg',
        mode= MODE
    )

    OUT_PATH = f"output/{IMG_NAME}__{MODE}.jpg"
    img.save(OUT_PATH)

    print(f'Save success with path : {OUT_PATH}')
    print(f'Time analysis: {time_analysis}')
if __name__ == "__main__":
    # main()
    # IMG_NAME = "366641616_2264556887067173_1651877982799532575_n"
    # IMG_NAME = "365277540_2640178542812959_3109842896588336028_n"
    # IMG_NAME = "13925854_308100976209095_8956468595154727390_o"
    # IMG_NAME = '241649023_543306286939449_2854614152112438955_n'
    # IMG_NAME = 'err1'
    # IMG_NAME = '1923962_1370238453082504_4224712044219484343_n'
    # IMG_NAME = '366641616_2264556887067173_1651877982799532575_n'
    # IMG_NAME = '18278972_297318970702821_2600128763625419236_o'
    # IMG_NAME = 'cau_doi_1'
    # IMG_NAME = "test_image"
    # IMG_NAME = "14718859_208204472925484_1150455697377965541_n"
    # IMG_NAME = '13718780_847719332039821_170320190789157617_n'

    testcase_1()
    testcase_2()

    