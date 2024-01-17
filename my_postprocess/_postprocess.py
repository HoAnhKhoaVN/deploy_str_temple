from copy import deepcopy
import os
from PIL import Image
from typing import Any, Text, Dict, List
from tqdm import tqdm
from .blend_text_with_bbox import BlendTextWithBBox


class PostProcess(object):
    def __init__(
        self,
        image: Any,
        list_bbox_text: List[Dict]
    ) -> None:
        self.image = self.init_image(image)
        self.list_bbox_text = list_bbox_text
        self.final_img = None

    @staticmethod
    def init_image(
        image: Any
    )-> Image:
        print(f'Type if image: {type(image)}')
        # if isinstance(image, Image):
        #     return image
        if isinstance(image, str):
            try:
                image = Image.open(fp = image)
                return image
            except Exception as err_init_image:
                print(f"Err: {err_init_image} - Image path: {image}")
        else:
            raise Exception(f"Error in type of image (not {type(image)})")

    def postprocess(self)-> Image:
        final_img = deepcopy(self.image)
        for _dict in tqdm(self.list_bbox_text, desc = "Progress blendtext: "):
            bbox = _dict.get('bbox', None)
            text = _dict.get('text', None)

            if bbox is None:
                return None

            if text is None:
                return None
            
            final_img = BlendTextWithBBox(
                text= text,
                bbox = bbox,
                image = self.image,
                font_path="font/Fz-Thu-Phap-Giao-Long-Full.ttf",
                fd_out='',
            ).blend_text()
        
        self.final_img = final_img
        return final_img

    def save_img(
        self,
        fn: Text,
    )-> None:
        # Get final image
        if self.final_img is None:
            final_img : Image = self.postprocess()
        else:
            final_img : Image = self.final_img

        # Save image
        final_img.save(fn)

def testcase_1():
    PREFIX = "blendtext"
    IMAGE_PATH = 'input/hoang_phi_cau_doi.jpg'
    DICT_BBOX_TEXT = [
        {"bbox": [[263, 72], [436, 77], [435, 122], [262, 117]], "text": "Điện Bảo Hùng Đại"}, 
        {"bbox": [[26, 82], [177, 77], [178, 118], [28, 123]], "text": "Sứ Lai Như Thái"},
        {"bbox": [[518, 82], [669, 86], [669, 124], [517, 120]], "text": "Thành Vương Pháp Lâu"}
    ]

    obj_postprocess = PostProcess(
        image = IMAGE_PATH,
        list_bbox_text = DICT_BBOX_TEXT
    )
    
    obj_postprocess.postprocess()
    obj_postprocess.save_img(f"output/{PREFIX}_hoang_phi_cau_doi.jpg")

def testcase_2():
    PREFIX = "blendtext"
    IMAGE_PATH = 'input/366641616_2264556887067173_1651877982799532575_n.jpg'
    DICT_BBOX_TEXT = [
        {
            'bbox': [[117, 99], [217, 74], [284, 353], [184, 378]],
            'text': 'Tĩnh Lan'
        }
    ]

    obj_postprocess = PostProcess(
        image = IMAGE_PATH,
        list_bbox_text = DICT_BBOX_TEXT
    )
    
    obj_postprocess.postprocess()
    obj_postprocess.save_img(f"output/{PREFIX}__366641616_2264556887067173_1651877982799532575_n.jpg")

def testcase_3():
    PREFIX = "blendtext"
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
    obj_postprocess = PostProcess(
        image = IMAGE_PATH,
        list_bbox_text = DICT_BBOX_TEXT
    )
    
    obj_postprocess.postprocess()
    obj_postprocess.save_img(f"output/{PREFIX}__13925854_308100976209095_8956468595154727390_o.jpg")

if __name__ == "__main__":
    testcase_1()
    # testcase_2()
    # testcase_3()