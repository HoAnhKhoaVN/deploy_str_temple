import os
from typing import List, Text, Tuple
from PIL import ImageFont, ImageDraw, Image
import numpy as np
import math
from .background_generator import image
from .config import (
    PADDING_IMG_H,
    PADDING_IMG_W,
    VI_LANGUAGE,
    CH_LANGUAGE,
    BACKGROUND_IMG_DIR,
    FONT_PATH,
    RESIZE_CHAR_RATIO
)

class BlendText(object):
    def __init__(
        self,
        text: Text,
        height: int,
        width: int,
        font_path: Text = FONT_PATH,
        fg: Tuple = (255, 0, 0),
        fd_out: Text = "", 
        backgroud_img_dir : Text = "",
        lang : Text = VI_LANGUAGE
    )->None:
        self.fg = fg

        self.text = text

        self.height = height
        self.width = width

        self.lang = lang

        self.backgroud_img_dir = backgroud_img_dir
        self.image = self._init_image()

        self.font_path = font_path

        self.fd_out = fd_out
        self._makedirs()

    def _init_image(self)-> Image:
        if self.backgroud_img_dir and os.path.exists(self.backgroud_img_dir):
            return image(
            height= self.height,
            width= self.width,
            image_dir= self.backgroud_img_dir
        )
        else:
            return Image.new(
                mode = "RGBA",
                size = (self.width, self.height),
                color= (0,0,0,0)
            )

    def _makedirs(self):
        if self.fd_out and not os.path.exists(self.fd_out):
            os.makedirs(name = self.fd_out)

    @staticmethod
    def get_para_in_line(p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        a = (y1-y2)/(x1-x2-1e-9)
        b = y1-a*x1

        return a, b
    
    @staticmethod
    def get_point_in_line_y_axis_tl_bl(
        len_text: int,
        a_line: float,
        b_line: float,
        size : float,
        first_point: List,
        padding_x : int = 1,
        padding_y : int = 1
    )->List:
        kc = size // len_text
        _first_point = [
            first_point[0] + padding_x, #x
            first_point[1] + padding_y, #y
        ]
        res = [_first_point]
        point = first_point
        for _ in range(len_text-1):
            _ , y = point

            res_y = int(y + kc)
            _res_y = int(y + kc) - padding_y

            if int(abs(a_line)) == 0:
                res_x = 0
                _res_x = padding_x
            else:
                res_x = int((_res_y - b_line)//a_line)
                _res_x = int((_res_y - b_line)//a_line) + padding_x

            res_point  = [res_x, res_y]
            _res_point  = [_res_x, _res_y]

            res.append(_res_point)
            point = res_point
        return res

    @staticmethod
    def get_point_in_line_y_axis_tr_br(
        len_text: int,
        a_line: float,
        b_line: float,
        size : float,
        first_point: List,
        padding_x : int = 1,
        padding_y : int = 1
    )->List:
        kc = size // len_text
        _first_point = [
            first_point[0] - padding_x, #x
            first_point[1] + padding_y, #y
        ]
        res = [_first_point]
        point = first_point
        for _ in range(len_text-1):
            _ , y = point

            res_y = int(y + kc)
            _res_y = int(y + kc) - padding_y

            if int(abs(a_line)) == 0:
                res_x = 0
                _res_x = padding_x
            else:
                res_x = int((_res_y - b_line)//a_line)
                _res_x = int((_res_y - b_line)//a_line) - padding_x

            res_point  = [res_x, res_y]
            _res_point  = [_res_x, _res_y]

            res.append(_res_point)
            point = res_point
        return res

    @staticmethod
    def get_text_dimensions(
        text_string: str,
        font: ImageFont
        ):
        # https://stackoverflow.com/a/46220683/9263761
        ascent, descent = font.getmetrics()

        text_width = font.getmask(text_string).getbbox()[2]
        text_height = font.getmask(text_string).getbbox()[3] + descent

        return (text_width, text_height)
    
    def get_center_point(
        self,
        bbox: list,
        text_str: str,
        font: ImageFont,
    )-> List:
        _tl, _tr, _br, _bl = bbox
        a, b = self.get_para_in_line(_tl, _br)
        _a, _b = self.get_para_in_line(_tr, _bl)

        x_center = int((_b-b)//(a - _a))
        y_center = int(a*x_center + b)


        #region get text size
        text_size = self.get_text_dimensions(
            text_string= text_str,
            font= font
        )
        #endregion

        # # region get position
        # x_center -= text_size[0]//2
        # y_center -= text_size[1]//2

        # # endregion

        return [x_center , y_center], text_size
    
    @staticmethod
    def euclidean_distance(
        a : list,
        b : list
    )-> float:
        """Calculates the Euclidean distance between two vectors.

        Args:
            a: A numpy array representing the first vector.
            b: A numpy array representing the second vector.

        Returns:
            A float representing the Euclidean distance between the two vectors.
        """
        a =  np.array(a)
        b =  np.array(b)
        return np.sqrt(np.sum((a - b)**2))

    @staticmethod
    def get_rotated_text_size(
        text_size: List,
        angle: float
    )-> List:
        W, H = text_size
        radian_angle = math.radians(angle)
        tan_a = math.tan(radian_angle)
        w_1 = (H*tan_a - W)/(tan_a**2 - 1)
        w_2 = W - w_1
        h_1 = w_1 * tan_a
        h_2 = H - h_1
        X = np.sqrt(w_1**2 + h_1**2)
        Y = np.sqrt(w_2**2 + h_2**2)
        return X, Y
    
    def check_text_size(
        self,
        text_string: Text,
        bbox: List[List[int]],
        angle: float,
        font_path: Text,
    )-> Tuple:
        # region get height and width of bounding box
        tl, tr, br, bl = bbox
        width = self.euclidean_distance(tl, tr)
        height = self.euclidean_distance(tl, bl)
        # print(f'width : {width}')
        # print(f'height : {height}')
        # endregion
        font_size = 10
        while True:
            pil_font = ImageFont.truetype(font_path, font_size)
            text_size = self.get_text_dimensions(
                    text_string= text_string,
                    font= pil_font
                )
            # print(f'Font size: {font_size} - Text size: {text_size}')
            # region Mapping rotated image
            rotated_text_width, rotated_text_height = self.get_rotated_text_size(
                text_size= text_size,
                angle = angle
            )
            # endregion

            width_x = (width - rotated_text_width ) // 2 # mở rộng kích thước ra xíu -> Để lúc nào cũng vẽ đủ chữ
            height_y = (height - rotated_text_height) // 2

            if width_x < 0 or height_y < 0:
                # Return font size before
                pil_font = ImageFont.truetype(font_path, font_size - 1)
                text_size = self.get_text_dimensions(
                        text_string= text_string,
                        font= pil_font
                    )
                # print(f'Width x : {width_x}')
                # print(f'Height y : {height_y}')
                font_size -=1
                return font_size
            else:
                font_size+=1
    
    def get_height_by_bbox(self, bbox: List[List[int]])->int:
        tl, _,_, bl = bbox
        res = self.euclidean_distance(tl, bl)
        return int(res)

    def draw_text_vertical(self):
        tl, tr, br, bl = (0,0), (self.width, 0), (self.width, self.height), (0, self.height)
        # region 1: Xác định bbox cho mỗi chữ trong văn bản
        # region 1.1: Viết phương trình đường thẳng của top-left và bottom-left
        a_line_left, b_line_left = self.get_para_in_line(tl,bl)
        
        # endregion

        # region 1.2: Viết phương trình đường thẳng của top-right và bottom-right
        a_line_right, b_line_right = self.get_para_in_line(tr,br)

        # endregion
        # region 2: Tính toán trung điểm cho mỗi từ
        if self.lang == VI_LANGUAGE:
            len_text  = len(self.text.split(' '))
        elif self.lang  == CH_LANGUAGE:
            len_text = len(self.text)
        else:
            print(f'Only suport:\n\tVietnamese: "vi"\n\tChinese: "ch"')

        # region 2.1: Lấy các điểm trên đường thẳng top-left và bottom-left
        lst_point_in_top_left = self.get_point_in_line_y_axis_tl_bl(
            len_text = len_text,
            a_line = a_line_left,
            b_line = b_line_left,
            size  = self.height,
            first_point = tl,
            padding_x = PADDING_IMG_W, 
            padding_y= PADDING_IMG_H
        )

        lst_point_in_top_left.append([bl[0] + PADDING_IMG_W , bl[1] - PADDING_IMG_H])
        # endregion

        # region 2.2: Lấy các điểm trên đường thẳng top-right và bottom-right
        lst_point_in_top_right = self.get_point_in_line_y_axis_tr_br(
            len_text = len_text,
            a_line = a_line_right,
            b_line = b_line_right,
            size  = self.height,
            first_point = tr,
            padding_x = PADDING_IMG_W, 
            padding_y= PADDING_IMG_H
            )
        lst_point_in_top_right.append([br[0] - PADDING_IMG_W, br[1] - PADDING_IMG_H])
        # endregion

        # region 2.3: Xác định bbox cho mỗi chữ
        lst_bbox = []
        for idx in range(len(lst_point_in_top_left)-1):
            tl = lst_point_in_top_left[idx]
            tr = lst_point_in_top_right[idx]
            br = lst_point_in_top_right[idx+1]
            bl = lst_point_in_top_left[idx+1]
            lst_bbox.append([tl, tr, br, bl])
        # print(f'lst_bbox: {lst_bbox}')
        # endregion

        # endregion

        # region 3: Tính toán kích thước của mỗi chữ
        lst_size = []
        if self.lang == VI_LANGUAGE:
            lst_char  = self.text.split(' ')
        elif self.lang  == CH_LANGUAGE:
            lst_char = self.text
        else:
            print(f'Only suport:\n\tVietnamese: "vi"\n\tChinese: "ch"')

        for w, _bbox in zip(lst_char, lst_bbox):
            # print(f'w: {w } - __bbox : {_bbox}')
            font_size = self.check_text_size(
                text_string= w,
                bbox = _bbox,
                angle= 0,
                font_path= self.font_path
            )
            lst_size.append(font_size)
        # endregion

        # region 4: Viết và xoay chữ
        # font = ImageFont.truetype(self.font_path , max_font_sizes)
        for w , _bbox, fs in zip(lst_char, lst_bbox, lst_size):
            # print(f'w: {w } - __bbox : {_bbox} - font size: {fs}')
            font = ImageFont.truetype(self.font_path , fs)
            p_center, text_size = self.get_center_point(_bbox, w, font)

            w_text, h_text = text_size
            # region 4.1: Create temporary image
            tmp_img = Image.new(
                mode = 'RGBA',
                size = (w_text, h_text),
                color = (0,0,0,0)
            )
            # endregion

            # region 4.2: Draw text
            tmp_draw = ImageDraw.Draw(tmp_img)
            tmp_draw.text(
                xy= (0,0),
                text = w,
                align= 'center',
                font= font,
                fill= self.fg
            )
            

            # endregion

            # region 4.3: Rotate text
            # tmp_img = tmp_img.rotate(
            #     angle= 0,
            #     expand= True,
            #     fillcolor= bg_color,
            # )
            # endregion

            # region resize image
            _h = self.get_height_by_bbox(_bbox)
            new_h = int(_h * 0.9)
            tmp_img = tmp_img.resize(
                size = (
                    tmp_img.width,
                    new_h,
                )
            )
            # endregion
            

            # region 4.4: Paste text
            new_p_x = p_center[0] - text_size[0]//2
            new_p_y = p_center[1] - new_h//2+ PADDING_IMG_H
            # print(f'p_center: {(new_p_x, new_p_y)}')
            # print(f'Size of img with text: {(tmp_img.height, tmp_img.width)}')  
            self.image.paste(
                im = tmp_img,
                box= (new_p_x, new_p_y),
                mask = tmp_img
            )
        # endregion
        # endregion
        return self.image

    def draw_text_hor(self):
        
        BBOX = [
                [PADDING_IMG_W, PADDING_IMG_H], 
                [self.width - PADDING_IMG_W, PADDING_IMG_H],
                [self.width - PADDING_IMG_W, self.height - PADDING_IMG_H],
                [PADDING_IMG_W, self.height - PADDING_IMG_H]
            ]
        # region 1: Xác định kích thước của văn bản
        font_size = self.check_text_size(
            text_string= self.text,
            bbox = BBOX,
            angle= 0,
            font_path= self.font_path
        )
        # print(f'Final font size: {font_size}')
        # endregion

        # region 2: Viết và xoay văn bản (tất cả các từ trên một dòng)
        # region 2.1: Xác định font chữ
        font = ImageFont.truetype(self.font_path , font_size)
        # endregion

        # region 2.2: Xác định điểm trung tâm
        p_center, text_size = self.get_center_point(BBOX, self.text, font)
        w_text, h_text = text_size
        # print(f'text size: {text_size}')
        # endregion
        
        # region 2.3: Tạo một ảnh giả có kích thước bằng với độ dài và rộng của văn bản
        tmp_img = Image.new(
            mode = 'RGBA',
            size = (w_text, h_text),
            color = (0,0,0,0)
        )
        # endregion



        # region 2.4: Viết văn bản
        tmp_draw = ImageDraw.Draw(tmp_img)
        tmp_draw.text(
            xy= (0,0),
            text = self.text,
            align= 'center',
            font= font,
            fill= self.fg
        )
        

        # endregion

        # # region 2.5: Xoay văn bản
        # tmp_img = tmp_img.rotate(
        #     angle= 0,
        #     expand= True,
        #     fillcolor= bg_color,
        # )
        # # endregion

        new_h = int(self.height * RESIZE_CHAR_RATIO)
        # region resize image
        tmp_img = tmp_img.resize(
                size = (
                    tmp_img.width,
                    new_h
                )
            )
        # endregion

        # region 2.6: Chèn văn bản vào hình góc
        # endregion
        new_p_x = p_center[0] - text_size[0]//2
        new_p_y = p_center[1] - new_h//2 + PADDING_IMG_H
        # print(f'new_p_x: {new_p_x}')
        # print(f'new_p_y: {new_p_y}')
        # print(f'Size of img with text: {(tmp_img.height, tmp_img.width)}')

        self.image.paste(
            im = tmp_img,
            box= (new_p_x, new_p_y),
            mask = tmp_img
        )
        # endregion
        # endregion
        return self.image

    def blend_text(self):
        if self.height < self.width:
            image_pil = self.draw_text_hor()
        else:    
            image_pil = self.draw_text_vertical()

        return image_pil
    
    def save_final_img(
        self,
        file_name: Text = ""
    ):
        # region 1. Blend text
        final_img = self.blend_text()
        # endregion

        # region 2. Get file name
        if not file_name:
            _basename = os.path.basename(p = self.font_path)
            name = _basename.split('.')[0]
            text = '_'.join(self.text.split(' '))
            draw_text_path = os.path.join(
                self.fd_out,
                f'{text}_{name}_h{self.height}_w{self.width}.png'
            )
        else:
            draw_text_path = os.path.join(
                self.fd_out,
                file_name
            )
        # endregion

        # region 3. Save image
        final_img.save(
            fp = draw_text_path
        )

        # endregion
        

if __name__ == '__main__':
    # Vertical
    # vertical_obj = BlendText(
    #     text= 'Hồ Anh Khoa',
    #     height= 200,
    #     width= 80,
    #     font_path= "font/arial.ttf",
    #     fd_out='output',
    #     bg=(0,0,0,0),
    #     fg = (255,0,0),
    #     backgroud_img_dir= BACKGROUND_IMG_DIR
    # )
    # vertical_obj()

    # # Horizontal
    # horizontal_obj = BlendText(
    #     text= 'Hồ Anh Khoa',
    #     height= 80,
    #     width= 200,
    #     font_path= "font/arial.ttf",
    #     fd_out='output',
    #     bg=(0,0,0,0),
    #     fg = (255,0,0),
    #     backgroud_img_dir= BACKGROUND_IMG_DIR
    # )
    # horizontal_obj()

    # Vertical non background
    # vertical_obj_non_bg = BlendText(
    #     text= 'Hà Thanh Nhân',
    #     height= 200,
    #     width= 80,
    #     font_path= "font/Fz-Thu-Phap-Giao-Long-Full.ttf",
    #     fd_out='output',
    #     fg = (255,0,0),
    #     backgroud_img_dir= ""
    # )
    # vertical_obj_non_bg.save_final_img()

    # vertical_obj_non_bg = BlendText(
    #     text= 'Hồ Kim Tuyết',
    #     height= 200,
    #     width= 80,
    #     font_path= "font/Fz-Thu-Phap-Giao-Long-Full.ttf",
    #     fd_out='output',
    #     fg = (255,0,0),
    #     backgroud_img_dir= ""
    # )
    # vertical_obj_non_bg.save_final_img()

    # Horizontal non background
    horizontal_obj_non_bg = BlendText(
        text= 'Nguyễn Chung Thùy Dương',
        height= 100,
        width= 500,
        font_path= "font/Fz-Thu-Phap-Giao-Long-Full.ttf",
        fd_out='',
        fg = (255,0,0),
        backgroud_img_dir= ""
    )
    horizontal_obj_non_bg.save_final_img()