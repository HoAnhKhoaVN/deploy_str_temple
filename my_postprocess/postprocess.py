#####################
##   POST PROCESS  ##
#####################
from copy import deepcopy
from typing import Text, List, Dict, Any, Tuple
from PIL import Image, ImageFont, ImageDraw
from pylette.color_extraction import get_bg_fg_color
from translate_to_modern_vietnamese.translate_to_modern_vietnamese import translate_to_modern_vietnamese
# from log.logger import setup_logger
import logging
from experiment.calc_angle_between_2_line import calculate_angle_between_line
from experiment.crop_image import crop_image_polygon
from experiment.distance import euclidean_distance
from experiment.equation_line import get_para_in_line
from experiment.calc_angle_between_2_line import calculate_angle_between_line
import cv2
import os
import numpy as np
import math
# setup_logger()

def postprocess_text(text: Text):
    # Uppercase characters
    text = text.upper()
    return text

# SRC: https://gist.github.com/Ze1598/420c7eb600899c86d1d65e83c3cc8b25
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
    bbox: list,
    text_str: str,
    font: ImageFont,
)-> List:
    _tl, _tr, _br, _bl = bbox
    a, b = get_para_in_line(_tl, _br)
    _a, _b = get_para_in_line(_tr, _bl)

    x_center = int((_b-b)//(a - _a))
    y_center = int(a*x_center + b)


    #region get text size
    text_size = get_text_dimensions(
          text_string= text_str,
          font= font
      )
    #endregion

    # region get position
    x_center -= text_size[0]//2
    y_center -= text_size[1]//2

    # endregion

    return [x_center , y_center], text_size

def get_point_in_line_y_axis(
    len_text: int,
    a_line: float,
    b_line: float,
    size : float,
    first_point: List,
)->List:
    kc = size // len_text
    res = [first_point]
    point = first_point
    for _ in range(len_text-1):
        _ , y = point

        res_y = int(y + kc)
        res_x = int((res_y - b_line)//a_line)
        res_point  = [res_x, res_y]

        res.append(res_point)
        point = res_point
    return res

def get_point_in_line_x_axis(
    len_text,
    a_line,
    b_line,
    size,
    first_point,
)->List[List]:
    kc = size // len_text
    res = [first_point]
    point = first_point
    for _ in range(len_text-1):
        x , _ = point

        res_x = int(x + kc)
        res_y = a_line * res_x + b_line
        res_point  = [res_x, res_y]

        res.append(res_point)
        point = res_point
    return res

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
    text_string: str,
    bbox: list,
    angle: float,
    font_path: str = 'font/arial.ttf'
)-> Tuple:
    # region get height and width of bounding box
    tl, tr, br, bl = bbox
    width = euclidean_distance(tl, tr)
    height = euclidean_distance(tl, bl)
    # endregion
    font_size = 10
    while True:
        pil_font = ImageFont.truetype(font_path, font_size)
        text_size = get_text_dimensions(
                text_string= text_string,
                font= pil_font
            )
        # region Mapping rotated image
        rotated_text_width, rotated_text_height = get_rotated_text_size(
            text_size= text_size,
            angle = angle
        )

        # endregion

        width_x = (width - rotated_text_width * 10 / 9) // 2 # mở rộng kích thước ra xíu -> Để lúc nào cũng vẽ đủ chữ
        height_y = (height - rotated_text_height * 10 / 9) // 2

        if width_x < 0 or height_y < 0:
            # Return font size before
            pil_font = ImageFont.truetype(font_path, font_size - 1)
            text_size = get_text_dimensions(
                    text_string= text_string,
                    font= pil_font
                )
            return font_size
        else:
            font_size+=1

def rotate_vertical_bbox_rectange(
    bbox
):
    tl = bbox[0]
    br = bbox[1]
    x1, y1 = tl
    x2, y2 = br
    cen_x  =x1 + (x2 - x1) //2
    cen_y = y1 + (y2 - y1) //2
    print(cen_x, cen_y)

    #
    width = (x2 -x1)
    height = (y2 -y1)
    half_width = width // 2
    half_height = height // 2

    print(f'Half width: {half_width}, half height: {half_height}')


    # top-left corner
    x_tl = cen_x -half_height
    y_tl = cen_y -half_width
    print(f'tl: {(x_tl, y_tl)}')
    # rotate bottom right
    x_br = cen_x + half_height
    y_br = cen_y + half_width
    print(f'br: {(x_br, y_br)}')
    return ((x_tl, y_tl),(x_br, y_br))

def check_bbox_is_horizontal_rectangle(
    bbox
)-> bool:
    # region 1: Get top-left and bottom-right
    tl = bbox[0]
    br = bbox[1]
    # endregion

    # region 2: Get height and width
    x1, y1 = tl
    x2, y2 = br

    height = x2 - x1
    width = y2 - y1
    # endregion


    # region check bbox is horizontal rectangle
    if height > width: # vertical
        # region rotate rectangle I(tl[0],tl[1]) 
        return rotate_vertical_bbox_rectange(
            bbox=(tl, br)
        ), (height, width)
        # endregion
    # endregion
    return bbox, (height, width)

def draw_text_horizontal_each_word(
    text: str,
    bbox: list,
    fg_color: tuple,
    bg_color: tuple,
    image,
    height,
    width,
    angle,
    font_path : str = 'font/arial.ttf',
):
    tl, tr, br, bl = bbox

    # region 1: Write the equation of the line
    a_line_left, b_line_left = get_para_in_line(tl,tr)
    # print(a_line_left, b_line_left )

    a_line_right, b_line_right = get_para_in_line(bl,br)
    # print(a_line_right, b_line_right)
    # endregion

    # region 2: Calculate position for each word
    len_text  = len(text.split())
    # print(f'len_text: {len_text} words')

    # region 2.1: Get point in top left corner
    lst_point_in_top_left = get_point_in_line_x_axis(
        len_text = len_text,
        a_line = a_line_left,
        b_line = b_line_left,
        size  = width,
        first_point = tl,
    )

    lst_point_in_top_left.append(tr)
    # print(f'lst_point_in_top_left : {lst_point_in_top_left}')
    # endregion

    # region 2.2: Get point in top right corner
    lst_point_in_top_right = get_point_in_line_x_axis(
        len_text = len_text,
        a_line = a_line_right,
        b_line = b_line_right,
        size  = width,
        first_point = bl,
        )
    lst_point_in_top_right.append(br)
    # print(f'lst_point_in_top_right : {lst_point_in_top_right}')
    # endregion

    # region 2.3: Merge point
    lst_bbox = []
    for idx in range(len(lst_point_in_top_left)-1):
        tl = lst_point_in_top_left[idx]
        tr = lst_point_in_top_right[idx]
        br = lst_point_in_top_right[idx+1]
        bl = lst_point_in_top_left[idx+1]
        lst_bbox.append([tl, tr, br, bl])

    # print(f'List of bboxes: {lst_bbox}')
    # endregion

    # endregion

    # region 3: Calculate size of text
    lst_size = []
    for w, _bbox in zip(text.split(), lst_bbox):
      font_size = check_text_size(
        text_string= w,
        bbox = _bbox,
        angle= angle,
      )
      lst_size.append(font_size)
    max_font_size = min(lst_size)
    # print(f'Font size: {lst_size}')
    print(f'Min font size: {max_font_size}')
    # endregion

    # region 4: Draw the text
    font = ImageFont.truetype( font_path , max_font_size)
    for w , _bbox in zip(text.split(), lst_bbox):
      p_center, text_size = get_center_point(_bbox, w, font)
    #   print(f'x center: {p_center}')

      w_text, h_text = text_size
      # region 4.1: Create temporary image
      tmp_img = Image.new(
        mode = 'RGB',
        size = (w_text, h_text),
        color = bg_color
      )
      # endregion

      # region 4.2: Draw text
      tmp_draw = ImageDraw.Draw(tmp_img)
      tmp_draw.text(
        xy= (0,0),
        text = w,
        align= 'center',
        font= font,
        fill= fg_color
      )
      

      # endregion

      # region 4.3: Rotate text
      tmp_img = tmp_img.rotate(
        angle= angle,
        expand= True,
        fillcolor= bg_color,
      )
      # endregion

      # region 4.4: Paste text
      image.paste(
        im = tmp_img,
        box= p_center
      )
      # endregion
    # endregion
    return image

def draw_text_horizontal_full_word(
    text: str,
    bbox: list,
    fg_color: tuple,
    bg_color: tuple,
    image,
    angle,
    font_path : str = 'font/arial.ttf',
):
    font_size = check_text_size(
        text_string= text,
        bbox = bbox,
        angle= angle,
      )

    # region 4: Draw the text
    font = ImageFont.truetype( font_path , font_size)
    p_center, text_size = get_center_point(bbox, text, font)
    w_text, h_text = text_size
    # region 4.1: Create temporary image
    tmp_img = Image.new(
        mode = 'RGB',
        size = (w_text, h_text),
        color = bg_color
    )
    # endregion

    # region 4.2: Draw text
    tmp_draw = ImageDraw.Draw(tmp_img)
    tmp_draw.text(
    xy= (0,0),
    text = text,
    align= 'center',
    font= font,
    fill= fg_color
    )
    

    # endregion

    # region 4.3: Rotate text
    tmp_img = tmp_img.rotate(
    angle= angle,
    expand= True,
    fillcolor= bg_color,
    )
    # endregion

    # region 4.4: Paste text
    image.paste(
        im = tmp_img,
        box= p_center
    )
    # endregion
    # endregion
    return image

def draw_text_vertical(
    text: str,
    bbox: list,
    fg_color: tuple,
    bg_color: tuple,
    image,
    height,
    width,
    angle,
    font_path : str = 'font/arial.ttf',
):
    tl, tr, br, bl = bbox

    # region 1: Write the equation of the line
    a_line_left, b_line_left = get_para_in_line(tl,bl)
    # print(a_line_left, b_line_left )

    a_line_right, b_line_right = get_para_in_line(tr,br)
    # print(a_line_right, b_line_right)
    # endregion

    # region 2: Calculate position for each word
    len_text  = len(text.split())
    # print(f'len_text: {len_text} words')

    # region 2.1: Get point in top left corner
    lst_point_in_top_left = get_point_in_line_y_axis(
        len_text = len_text,
        a_line = a_line_left,
        b_line = b_line_left,
        size  = height,
        first_point = tl,
    )

    lst_point_in_top_left.append(bl)
    # print(f'lst_point_in_top_left : {lst_point_in_top_left}')
    # endregion

    # region 2.2: Get point in top right corner
    lst_point_in_top_right = get_point_in_line_y_axis(
        len_text = len_text,
        a_line = a_line_right,
        b_line = b_line_right,
        size  = height,
        first_point = tr,
        )
    lst_point_in_top_right.append(br)
    # print(f'lst_point_in_top_right : {lst_point_in_top_right}')
    # endregion

    # region 2.3: Merge point
    lst_bbox = []
    for idx in range(len(lst_point_in_top_left)-1):
        tl = lst_point_in_top_left[idx]
        tr = lst_point_in_top_right[idx]
        br = lst_point_in_top_right[idx+1]
        bl = lst_point_in_top_left[idx+1]
        lst_bbox.append([tl, tr, br, bl])

    # print(f'List of bboxes: {lst_bbox}')
    # endregion

    # endregion

    # region 3: Calculate size of text
    lst_size = []
    for w, _bbox in zip(text.split(), lst_bbox):
      font_size = check_text_size(
        text_string= w,
        bbox = _bbox,
        angle= angle,
      )
      lst_size.append(font_size)
    max_font_size = min(lst_size)
    # print(f'Font size: {lst_size}')
    # print(f'Min font size: {max_font_size}')
    # endregion

    # region 4: Draw the text
    font = ImageFont.truetype( font_path , max_font_size)
    for w , _bbox in zip(text.split(), lst_bbox):
      p_center, text_size = get_center_point(_bbox, w, font)
    #   print(f'x center: {p_center}')

      w_text, h_text = text_size
      # region 4.1: Create temporary image
      tmp_img = Image.new(
        mode = 'RGB',
        size = (w_text, h_text),
        color = bg_color
      )
      # endregion

      # region 4.2: Draw text
      tmp_draw = ImageDraw.Draw(tmp_img)
      tmp_draw.text(
        xy= (0,0),
        text = w,
        align= 'center',
        font= font,
        fill= fg_color
      )
      

      # endregion

      # region 4.3: Rotate text
      tmp_img = tmp_img.rotate(
        angle= angle,
        expand= True,
        fillcolor= bg_color,
      )
      # endregion

      # region 4.4: Paste text
      image.paste(
        im = tmp_img,
        box= p_center
      )
      # endregion
    # endregion
    return image

def _postprocess(
    image_fn: Text,
    list_dict_result: List[Dict[Text, Any]]
):
    # region Create a PIL image and draw each text using the custom font
    if isinstance(image_fn, str):
        pil_image = Image.open(image_fn)
        src_img = cv2.imread(image_fn)
    else:
        pil_image = Image.fromarray(image_fn)
        src_img = image_fn
    src_img = cv2.cvtColor(src_img, cv2.COLOR_BGR2RGB)
    h, w = src_img.shape[:2]

    mask_image = np.zeros((h, w,3), dtype= np.uint8) * 225
    draw = ImageDraw.Draw(pil_image)


    # endregion


    for idx, _dict in enumerate(list_dict_result):
        # print(f"===== IDX: {idx+1} =====")

        # region extract input
        bbox, text= _dict['bbox'], _dict['text']
        if not text:
            continue
        logging.info(f"Text: {text}")
        # endregion
        
        # region Calculate the angle between the lines
        tl, tr, br, bl = bbox
        x_axis = (tl[0], 0)
        line1 = [tl, bl]
        line2 = [x_axis, tl]
        
        angle = calculate_angle_between_line(line1, line2)

        a1, b1 = get_para_in_line(x_axis, tl)
        a2, b2 = get_para_in_line(bl, br)
        x_intersect =(b2 - b1)/(a1 - a2)
        print(f'x_intersect: {x_intersect}')
        if x_intersect > bl[0]:
            angle = -angle
        else:
            angle = angle


        print("Angle between Line 1 and Line 2 (degrees):", angle)
        # endregion

        # region 1. Unpack the bounding box
        (tl, tr, br, bl) = bbox
        tl = (int(tl[0]), int(tl[1]))
        tr = (int(tr[0]), int(tr[1]))
        br = (int(br[0]), int(br[1]))
        bl = (int(bl[0]), int(bl[1]))
        # endregion

        x1, y1 = tl
        x2, y2 = br
        _mask_image= crop_image_polygon(
            img = src_img,
            points= bbox
        )
        _mask_image = _mask_image[:, :, np.newaxis] # Add a new axis for the third dimension
        _mask_image = np.repeat(
            a = _mask_image,
            repeats= 3,
            axis=2
        )
        mask_image = cv2.bitwise_or(mask_image, _mask_image)
        cropped_image_pil = pil_image.crop((x1, y1, x2, y2))

        # region 3. Get backgroud and foregroud color
        c1, c2 = get_bg_fg_color(cropped_image_pil)
        # endregion

        # region calculate average value of 4 pixel
        # region get line
        a_tl_tr, b_tl_tr = get_para_in_line(tl, tr)
        a_bl_br, b_bl_br = get_para_in_line(bl, br)
        a_tr_br, b_tr_br = get_para_in_line(tr, br)
        a_tl_bl, b_tl_bl = get_para_in_line(tl, bl)
        # endregion
        N = 500
        # region get 10 points in line top left, top right -> x -> y
        x_tl, x_tr = tl[0], tr[0]
        delta_x = np.abs(x_tl - x_tr)
        kc_x = delta_x / (N +1)
        tmp_x = x_tl
        tmp_x_arr = []
        for _ in range(N):
            tmp_x+=int(kc_x)
            tmp_x_arr.append(tmp_x)
        
        tmp_y_arr = []
        for x in tmp_x_arr:
            tmp_y = int(a_tl_tr * x + b_tl_tr)
            tmp_y_arr.append(tmp_y)

        lst_point_in_line_tl_tr= [[x, y] for x, y in zip(tmp_y_arr, tmp_x_arr)]
        # endregion
            
        # region get 10 points in line bottom left, bottom right
        x_bl, x_br = bl[0], br[0]
        delta_x = np.abs(x_bl - x_br)
        kc_x = delta_x / (N +1)
        tmp_x = x_bl
        tmp_x_arr = []
        for _ in range(N):
            tmp_x+=int(kc_x)
            tmp_x_arr.append(tmp_x)
        
        tmp_y_arr = []
        for x in tmp_x_arr:
            tmp_y = int(a_bl_br * x + b_bl_br)
            tmp_y_arr.append(tmp_y)

        lst_point_in_line_bl_br= [[x, y] for x, y in zip(tmp_y_arr, tmp_x_arr)]

        # endregion

        # region get 10 points in line top left, bottom left
        y_tl, y_bl = tl[1], bl[1]
        delta_y = np.abs(y_tl - y_bl)
        kc_y = delta_y / (N + 1)
        tmp_y = y_tl
        tmp_y_arr = []
        for _ in range(N):
            tmp_y+=int(kc_y)
            tmp_y_arr.append(tmp_y)
        
        tmp_x_arr = []
        for y in tmp_y_arr:
            tmp_x = int((y - b_tl_bl)/a_tl_bl)
            tmp_x_arr.append(tmp_x)

        lst_point_in_line_tl_bl= [[x, y] for x, y in zip(tmp_y_arr, tmp_x_arr)]
        # endregion

        # region get 10 points in line top right , bottom right
        y_tr, y_br = tr[1], br[1]
        delta_y = np.abs(y_tr - y_br)
        kc_y = delta_y / (N + 1)
        tmp_y = y_tr
        tmp_y_arr = []
        for _ in range(N):
            tmp_y+=int(kc_y)
            tmp_y_arr.append(tmp_y)
        
        tmp_x_arr = []
        for y in tmp_y_arr:
            tmp_x = int((y - b_tr_br)/a_tr_br)
            tmp_x_arr.append(tmp_x)

        lst_point_in_line_tr_br= [[x, y] for x, y in zip(tmp_y_arr, tmp_x_arr)]
        # endregion

        points = [
            [tl[1], tl[0]],
            [tr[1], tr[0]],
            [br[1], br[0]],
            [bl[1], bl[0]]
        ]


        points.extend(lst_point_in_line_tl_tr)
        points.extend(lst_point_in_line_bl_br)
        points.extend(lst_point_in_line_tl_bl)
        points.extend(lst_point_in_line_tr_br)

        print(f'Length points: {len(points)}')

        # region get RGB color from points
        lst_rgb = []
        for p in points:
            lst_rgb.append(src_img[p[0],p[1]])
        np_rgb  = np.array(lst_rgb)
        # endregion

        mean_corner_pixel = np.mean(
           np_rgb, axis=0
        )

        # print(mean_corner_pixel)
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
        print(f"Background color: {bg_color}")
        print(f"foreground color: {fg_color}")
        # endregion

        fg_cv = tuple(list(fg_color)[::-1])
        bg_cv = tuple(list(bg_color)[::-1])
        # region 5. Create polygon
        draw.polygon(
            xy=(tl, tr, br, bl),
            fill = bg_cv
        )
        # endregion

        # region calculate height and width in euclidean coordinates
        width = euclidean_distance(tl, tr)
        height = euclidean_distance(tl, bl)
        # print(f"Height x Width : {height}x{width}")
        # endregion

        # region 4. Check image is horizontally or vertically
        # height, width = cropped_image.shape[0:2]
        if width >= height:
            direction = 'horizontal'
        else:
            direction = 'vertical'
        # print(f'Direction: {direction}')
        # endregion

        # # region 5. Translate to modern Vietnamese
        # text = translate_to_modern_vietnamese(text)
        # # endregion

        if direction == 'horizontal':
            # draw_text_horizontal_each_word(
            #     text = text,
            #     bbox= bbox,
            #     bg_color=bg_cv,
            #     fg_color= fg_cv,
            #     image= pil_image,
            #     height = height,
            #     width = width,
            #     angle= angle,
            # )

            draw_text_horizontal_full_word(
                text = text,
                bbox= bbox,
                bg_color=bg_cv,
                fg_color= fg_cv,
                image= pil_image,
                angle= angle,
            )
        else:
            draw_text_vertical(
                text = text,
                bbox= bbox,
                bg_color=bg_cv,
                fg_color= fg_cv,
                image= pil_image,
                height = height,
                width = width,
                angle= angle,
            )
        src_img = np.array(pil_image)
        

    # region paste background with polygons      
    cv_img = np.array(pil_image)
    cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    cv_img = cv2.bitwise_and(mask_image, cv_img)
    
    if isinstance(image_fn, str):
        src_img = cv2.imread(image_fn)
    else:
        src_img = image_fn
        src_img = cv2.cvtColor(src_img, cv2.COLOR_BGR2RGB)
    src_img = cv2.cvtColor(src_img, cv2.COLOR_BGR2RGB)
    not_masked_image = cv2.bitwise_not(mask_image)
    not_src_img = cv2.bitwise_and(not_masked_image, src_img)
    final_image = cv2.bitwise_or(cv_img, not_src_img)
    # endregion
    return Image.fromarray(final_image)


if __name__ == "__main__":
    # region Input
    res = [{'bbox': [[117, 99], [217, 74], [284, 353], [184, 378]], 'text': 'Tĩnh Lan'}]
    TGT = 'experiment/'
    image_path = 'input_demo/test_image.jpg'
    # endregion

    # region postprocessing
    res_img = _postprocess(
        image_fn= image_path,
        list_dict_result= res
    )

    PATH = os.path.join(TGT, "test_image.jpg")
    res_img.save(PATH)
    print(PATH)



    # endregion
