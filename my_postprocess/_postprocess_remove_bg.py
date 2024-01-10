from typing import Any, Dict, List, Text
from _postprocess import PostProcess
import numpy as np
from rotate_img.crop_image import crop_image_polygon
import cv2
from clean_text.big_lama.src.core import process_inpaint
from PIL import Image

class PostProcessRmText(PostProcess):
    def __init__(
        self,
        image: Any,
        list_bbox_text: List[Dict],
        debug: Text = True
    ) -> None:
        super().__init__(image, list_bbox_text)
        self.image = self.remove_text()
        self.debug = debug

    def remove_text(self):
        h, w = self.image.size()
        mask_image = np.zeros((h, w, 3), dtype= np.uint8)
        black_image = np.full((h, w, 4), [0, 0, 0, 255], dtype=np.uint8)

        np_img = np.asarray(
            a = self.image,
            dtype= np.uint8
            )

        for _dict in self.list_bbox_text:
            bbox = _dict['bbox']

            # region get mask
            _mask_image, _ = crop_image_polygon(
                img = np_img,
                points= bbox
            )
            _mask_image = _mask_image[:, :, np.newaxis] # Add a new axis for the third dimension
            _mask_image = np.repeat(
                a = _mask_image,
                repeats= 3,
                axis=2
            )
            mask_image = cv2.bitwise_or(mask_image, _mask_image)
            # endregion

            not_masked_image = cv2.bitwise_not(mask_image)

        drawing = np.where(
            (mask_image[:, :, 0] == 255) & 
            (mask_image[:, :, 1] == 255) & 
            (mask_image[:, :, 2] == 255)
        )
        black_image[drawing]=[0,0,0,0] # RGBA

        inpaint_img = process_inpaint(
            image = np_img,
            mask = black_image
        )

        if self.debug:
            Image.fromarray(np_img).save("src_img.png")
            Image.fromarray(mask_image).save("mask_image.png")
            Image.fromarray(black_image).save("black_image.png")
            Image.fromarray(inpaint_img).save("inplating.png")

def testcase_1():
    PREFIX = "blendtext_rm_bg"
    IMAGE_PATH = 'input/hoang_phi_cau_doi.jpg'
    DICT_BBOX_TEXT = [
        {"bbox": [[263, 72], [436, 77], [435, 122], [262, 117]], "text": "Điện Bảo Hùng Đại"}, 
        {"bbox": [[26, 82], [177, 77], [178, 118], [28, 123]], "text": "Sứ Lai Như Thái"},
        {"bbox": [[518, 82], [669, 86], [669, 124], [517, 120]], "text": "Thành Vương Pháp Lâu"}
    ]

    obj_postprocess = PostProcessRmText(
        image = IMAGE_PATH,
        list_bbox_text = DICT_BBOX_TEXT
    )
    
    obj_postprocess.postprocess()
    obj_postprocess.save_img(f"output/{PREFIX}_hoang_phi_cau_doi.jpg")

def testcase_2():
    PREFIX = "blendtext_rm_bg"
    IMAGE_PATH = 'input/366641616_2264556887067173_1651877982799532575_n.jpg'
    DICT_BBOX_TEXT = [
        {
            'bbox': [[117, 99], [217, 74], [284, 353], [184, 378]],
            'text': 'Tĩnh Lan'
        }
    ]

    obj_postprocess = PostProcessRmText(
        image = IMAGE_PATH,
        list_bbox_text = DICT_BBOX_TEXT
    )
    
    obj_postprocess.postprocess()
    obj_postprocess.save_img(f"output/{PREFIX}__366641616_2264556887067173_1651877982799532575_n.jpg")

def testcase_3():
    PREFIX = "blendtext_rm_bg"
    IMAGE_PATH = "input/13925854_308100976209095_8956468595154727390_o.jpg"
    DICT_BBOX_TEXT = [
        {
            "bbox": [[178, 512], [212, 512], [212, 910], [178, 910]],
            "text": "Quang Minh Chính Pháp Hoằng Nhàn Kinh Tạng Hợp Nhân Lục"
        }, 

        {
            "bbox": [[550, 508], [579, 508], [582, 896], [552, 896]], 
            "text": "Long Chân Như Phổ Phản Sinh Đồng Tin Thọ"
        }
    ]
    obj_postprocess = PostProcessRmText(
        image = IMAGE_PATH,
        list_bbox_text = DICT_BBOX_TEXT
    )
    
    obj_postprocess.postprocess()
    obj_postprocess.save_img(f"output/{PREFIX}__13925854_308100976209095_8956468595154727390_o.jpg")

if __name__ == "__main__":
    testcase_1()
    testcase_2()
    testcase_3()