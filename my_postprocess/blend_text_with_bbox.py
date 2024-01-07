from typing import Text, List, Tuple
from blend_text import BlendText
from PIL import Image, ImageFont, ImageDraw
from config import (
    BACKGROUND_IMG_DIR, 
    VI_LANGUAGE, 
    FONT_PATH,
    CH_LANGUAGE,
    PADDING_IMG_W,
    PADDING_IMG_H,
    RESIZE_CHAR_RATIO
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
        return angle

    def get_size_bbox(self)->Tuple[int, int]:    
        tl, tr, _, bl = self.bbox
        width = int(euclidean_distance(tl, tr))
        height = int(euclidean_distance(tl, bl))
        return width, height

    def draw_text_vertical(self):
        tl, tr, br, bl = self.bbox
        # region 1: Xác định bbox cho mỗi chữ trong văn bản
        # region 1.1: Viết phương trình đường thẳng của top-left và bottom-left
        a_line_left, b_line_left = self.get_para_in_line(tl,bl)
        
        # endregion

        # region 1.2: Viết phương trình đường thẳng của top-right và bottom-right
        a_line_right, b_line_right = self.get_para_in_line(tr,br)

        # endregion
        
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
            tmp_img = tmp_img.rotate(
                angle= self.angle,
                expand= True,
                fillcolor= (0,0,0,0),
            )
            # endregion

            # region 4.4: Resize image
            _h = self.get_height_by_bbox(_bbox)
            new_h = int(_h * RESIZE_CHAR_RATIO)
            tmp_img = tmp_img.resize(
                size = (
                    tmp_img.width,
                    new_h,
                )
            )
            # endregion
            
            # region 4.4: Paste text
            new_p_x = p_center[0] - text_size[0] // 2
            new_p_y = p_center[1] - new_h // 2+ PADDING_IMG_H
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
        tl, tr, br, bl = self.bbox
        BBOX = [
                [tl[0] + PADDING_IMG_W, tl[1] +PADDING_IMG_H], 
                [tr[0] + self.width - PADDING_IMG_W, tr[1] - PADDING_IMG_H],
                [br[0] + self.width - PADDING_IMG_W, br[1] + self.height - PADDING_IMG_H],
                [bl[0] + PADDING_IMG_W, bl[1] + self.height - PADDING_IMG_H]
            ]
        # region 1: Xác định kích thước của văn bản
        font_size = self.check_text_size(
            text_string= self.text,
            bbox = BBOX,
            angle= self.angle,
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

        # region 2.5: Xoay văn bản
        tmp_img = tmp_img.rotate(
            angle= self.angle,
            expand= True,
            fillcolor= (0,0,0,0),
        )
        # # endregion

        new_h = int(self.height * 0.9)
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

if __name__ == "__main__":
    IMG_PATH = "input/366641616_2264556887067173_1651877982799532575_n.jpg"
    vertical_obj_non_bg = BlendTextWithBBox(
        text= 'Tĩnh Lan',
        bbox = [[117, 99], [217, 74], [284, 353], [184, 378]],
        image = Image.open(fp= IMG_PATH),
        font_path= "font/Fz-Thu-Phap-Giao-Long-Full.ttf",
        fd_out='output',
        fg = (255,0,0),
    )
    vertical_obj_non_bg.save_final_img()

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