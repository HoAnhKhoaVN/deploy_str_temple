from copy import deepcopy
from typing import Any, Dict, List, Text

from tqdm import tqdm
from _postprocess import PostProcess
import numpy as np
from blend_text_with_bbox import BlendTextWithBBox
from config import FONT_PATH, VI_LANGUAGE, NUM_REMOVE_TEXT_REPEAT
from pylette.color_extraction import get_bg_fg_color
from rotate_img.crop_image import crop_image_polygon
import cv2
from clean_text.big_lama.src.core import process_inpaint
from PIL import Image
from rotate_img.detect_rectangle_box import detect_and_crop_image

from rotate_img.rotate_image import rotate_image
from utils.distance import euclidean_distance

class BlendTextOps(BlendTextWithBBox):
    def __init__(
        self,
        text: Text, 
        bbox: List[List[int]],
        src_image: Image,
        inpaint_img: Image,
        font_path: Text = FONT_PATH,
        fd_out: Text = "",
        lang : Text = VI_LANGUAGE
    ) -> None:
        self.bbox = bbox
        self.width, self.height = self.get_size_bbox()
        self.angle = self.get_angle_bbox()

        self.text = text
        self.image = inpaint_img
        self.src_img = src_image
        self.font_path = font_path

        self.fg, self.bg = self.get_color()

        self.fd_out = fd_out
        self.lang = lang

    def get_color(self):
        tl, tr, br, bl = self.bbox
        tl = (int(tl[0]), int(tl[1]))
        tr = (int(tr[0]), int(tr[1]))
        br = (int(br[0]), int(br[1]))
        bl = (int(bl[0]), int(bl[1]))

        np_img = np.asarray(
            a = self.src_img,
            dtype= np.uint8
            )
        mask_image = np.zeros(np_img.shape, dtype= np.uint8)

        _mask_image, crop_img= crop_image_polygon(
            img = np_img,
            points= self.bbox
        )
        _mask_image = _mask_image[:, :, np.newaxis] # Add a new axis for the third dimension
        _mask_image = np.repeat(
            a = _mask_image,
            repeats= 3,
            axis=2
        )
        mask_image = cv2.bitwise_or(mask_image, _mask_image)
        rotate_img = rotate_image(
            image= crop_img,
            angle= -self.angle,
        )
        cropped_image_pil = detect_and_crop_image(img = rotate_img)


         # region : Get backgroud and foregroud color
        c1, c2 = get_bg_fg_color(cropped_image_pil)
        H, W = cropped_image_pil.shape[:2]
        np_rgb = np.vstack(
            tup = (
                cropped_image_pil[0, :, :],
                cropped_image_pil[H-1, :, :],
                cropped_image_pil[:, 0, :],
                cropped_image_pil[:, W-1, :]
            )
        )

        # region get mean RBG
        mean_corner_pixel = np.mean(
            np_rgb, axis= 0
        )
        d_c1 = euclidean_distance(
            a = mean_corner_pixel,
            b = np.array(c1)                      
        )
        d_c2 = euclidean_distance(
            a = mean_corner_pixel,
            b = np.array(c2)
        )

        if d_c1 < d_c2:
            bg_color = c1
            fg_color = c2
        else:
            bg_color = c2
            fg_color = c1
        print(f"Mean pixel: {mean_corner_pixel}")
        # endregion

        print(f"Background color: {bg_color}")
        print(f"foreground color: {fg_color}")
        return fg_color, bg_color
        # endregion

class PostProcessRmText(PostProcess):
    def __init__(
        self,
        image: Any,
        list_bbox_text: List[Dict],
        debug: bool = True,
        quality: bool = True
    ) -> None:
        self.debug = debug
        super().__init__(image, list_bbox_text)
        if quality:
            self.inpaint_img = self.remove_text_quality()
        else:
            self.inpaint_img = self.remove_text()

    def remove_text(self):
        w, h = self.image.size
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

        return Image.fromarray(inpaint_img)

    def remove_text_quality(self):
        for i in range(NUM_REMOVE_TEXT_REPEAT):
            image = self.remove_text()
        
        return image
            
    def postprocess(self)-> Image:
        final_img = deepcopy(self.inpaint_img)
        for _dict in tqdm(self.list_bbox_text, desc = "Progress blendtext: "):
            bbox = _dict.get('bbox', None)
            text = _dict.get('text', None)

            if bbox is None:
                return None

            if text is None:
                return None
            
            final_img = BlendTextOps(
                text= text,
                bbox = bbox,
                src_image = self.image,
                inpaint_img= self.inpaint_img,
                font_path="font/Fz-Thu-Phap-Giao-Long-Full.ttf",
                fd_out='',
            ).blend_text()
        
        self.final_img = final_img
        return final_img

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
        list_bbox_text = DICT_BBOX_TEXT,
        quality= False,
        debug= False
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
        list_bbox_text = DICT_BBOX_TEXT,
        debug= False,
        quality= False,
    )
    
    obj_postprocess.postprocess()
    obj_postprocess.save_img(f"output/{PREFIX}__13925854_308100976209095_8956468595154727390_o.jpg")

def testcase_4():
    PREFIX = "blendtext_rm_bg"
    IMAGE_PATH = "input/cau_doi_1.jpg"
    DICT_BBOX_TEXT = [
        {
            'bbox': [[245, 8], [293, 11], [256, 614], [209, 612]], 
            'text': 'Hiện Thế Vi Nhất Sư Đương Lai Tác Phật Tô'
        }, 
        {
            'bbox': [[747, 16], [790, 18], [774, 576], [730, 575]], 
            'text': 'Hữu Thiền Hữu Tịnh Thổ Hoành Như Dải Giác Hổ'
        }
    ]
    obj_postprocess = PostProcessRmText(
        image = IMAGE_PATH,
        list_bbox_text = DICT_BBOX_TEXT,
        debug= False,
        quality= False,
    )
    
    obj_postprocess.postprocess()
    obj_postprocess.save_img(f"output/{PREFIX}__cau_doi_1.jpg")

def testcase_5():
    PREFIX = "blendtext_rm_bg"
    IMAGE_PATH = "input/err1.jpg"
    DICT_BBOX_TEXT = [{'bbox': [[1314, 426], [1393, 424], [1404, 952], [1325, 954]], 'text': 'Nể Mong Phủ Xướng Năng Nhãn'}, {'bbox': [[566, 441], [641, 436], [673, 976], [598, 980]], 'text': 'Cung Phủ Thái Lai Chi Phúc'}]
    obj_postprocess = PostProcessRmText(
        image = IMAGE_PATH,
        list_bbox_text = DICT_BBOX_TEXT,
        debug= False,
        quality= False,
    )
    
    obj_postprocess.postprocess()
    obj_postprocess.save_img(f"output/{PREFIX}__err1.jpg")


if __name__ == "__main__":
    # testcase_1()
    # testcase_2()
    # testcase_3()
    # testcase_4()
    testcase_5()