from typing import Text, List, Tuple
from blend_text import BlendText
from PIL import Image
from config import (
    BACKGROUND_IMG_DIR, 
    VI_LANGUAGE, 
    FONT_PATH
)
from utils.distance import euclidean_distance
from rotate_img.calc_angle_between_2_line import calculate_angle_between_line

class BlendTextWithBBox(BlendText):
    def __init__(
        self,
        text: Text, 
        bbox: List[List[int]],
        image: Image,
        font_path: Text = FONT_PATH,
        fg: Tuple = (255, 0, 0),
        fd_out: Text = "",
        lang : Text = VI_LANGUAGE
    ) -> None:
        self.bbox = bbox
        self.width, self.height = self.get_size_bbox()
        self.angle = self.get_angle_bbox()

        self.text = text
        self.image = image
        self.font_path = font_path

        self.fg = fg

        self.fd_out = fd_out
        self.lang = lang

        
    def get_angle_bbox(self)-> float:
        tl, _, br, bl = self.bbox
        x_axis = (tl[0], 0)
        line1 = [tl, bl]
        line2 = [x_axis, tl]
        
        angle = calculate_angle_between_line(line1, line2)

        a1, b1 = self.get_para_in_line(x_axis, tl)
        a2, b2 = self.get_para_in_line(bl, br)
        x_intersect =(b2 - b1)/(a1 - a2)

        if x_intersect > bl[0]:
            angle = -angle
        else:
            angle = angle
        print("Angle between Line 1 and Line 2 (degrees):", angle)

    def get_size_bbox(self)->Tuple[int, int]:    
        tl, tr, _, bl = self.bbox
        width = int(euclidean_distance(tl, tr))
        height = int(euclidean_distance(tl, bl))
        return width, height


if __name__ == "__main__":
    vertical_obj_non_bg = BlendTextWithBBox(
        text= 'Tĩnh Lan',
        bbox = [[117, 99], [217, 74], [284, 353], [184, 378]],
        font_path= "font/arial.ttf",
        fd_out='output',
        bg=(0,0,0,0),
        fg = (255,0,0),
        backgroud_img_dir= ""
    )
    vertical_obj_non_bg()

    # # Horizontal non background
    # horizontal_obj_non_bg = BlendTextWithBBox(
    #     text= 'Hồ Anh Khoa',
    #     height= 80,
    #     width= 200,
    #     font_path= "font/arial.ttf",
    #     fd_out='output',
    #     bg=(0,0,0,0),
    #     fg = (255,0,0),
    #     backgroud_img_dir= ""
    # )
    # horizontal_obj_non_bg()