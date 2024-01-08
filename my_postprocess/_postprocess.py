import os
from PIL import Image
from typing import Any, Text, Dict

class PostProcess(object):
    def __init__(
        self,
        image: Any[Image,Text],
        dict_bbox_text: Dict
    ) -> None:
        self.image = self.init_image(image)
        self.dict_bbox_text = dict_bbox_text

    def init_image(
        image: Any[Image, Text]
    )-> Image:
        pass

    def postprocess(self):
        pass

    def save_img(self):
        pass

        
        

if __name__ == "__main__":
    IMAGE_PATH = "input/366641616_2264556887067173_1651877982799532575_n.jpg"
    DICT_BBOX_TEXT = {
            'bbox': [[117, 99], [217, 74], [284, 353], [184, 378]],
            'text': 'Tĩnh Lan'
        }

    obj_postprocess = PostProcess(
        image = IMAGE_PATH,
        dict_bbox_text = DICT_BBOX_TEXT
    )
    
    obj_postprocess.postprocess()
    obj_postprocess.save_img()