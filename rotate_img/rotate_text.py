from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
from utils.distance import euclidean_distance
from equation_line import get_para_in_line
from calc_angle_between_2_line import calculate_angle_between_line
import math

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

def get_point_in_line(
    len_text: int,
    a_line: float,
    b_line: float,
    size : float,
    first_point: list[int, int],
)->list[list[int, int]]:
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

def get_rotated_text_size(
  text_size: list[float, float],
  angle: float
)-> list[float, float]:
  print(f'degree angle: {angle}')
  W, H = text_size
  print(f'W, H: {W,H}')
  radian_angle = math.radians(angle)
  print(f'radian_angle: {radian_angle}')
  tan_a = math.tan(radian_angle)
  w_1 = (H*tan_a - W)/(tan_a**2 - 1)
  w_2 = W - w_1
  print(f'W1: {w_1} - w_2: {w_2}')
  h_1 = w_1 * tan_a
  h_2 = H - h_1
  print(f'h1: {h_1} - h_2: {h_2}')
  X = np.sqrt(w_1**2 + h_1**2)
  Y = np.sqrt(w_2**2 + h_2**2)
  print(f"X: {X}, Y: {Y}")
  return X, Y
  
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
    print(a_line_left, b_line_left )

    a_line_right, b_line_right = get_para_in_line(tr,br)
    print(a_line_right, b_line_right)
    # endregion

    # region 2: Calculate position for each word
    len_text  = len(text.split())
    print(f'len_text: {len_text} words')

    # region 2.1: Get point in top left corner
    lst_point_in_top_left = get_point_in_line(
        len_text = len_text,
        a_line = a_line_left,
        b_line = b_line_left,
        size  = height,
        first_point = tl,
    )

    lst_point_in_top_left.append(bl)
    print(f'lst_point_in_top_left : {lst_point_in_top_left}')
    # endregion

    # region 2.2: Get point in top right corner
    lst_point_in_top_right = get_point_in_line(
        len_text = len_text,
        a_line = a_line_right,
        b_line = b_line_right,
        size  = height,
        first_point = tr,
        )
    lst_point_in_top_right.append(br)
    print(f'lst_point_in_top_right : {lst_point_in_top_right}')
    # endregion

    # region 2.3: Merge point
    lst_bbox = []
    for idx in range(len(lst_point_in_top_left)-1):
        tl = lst_point_in_top_left[idx]
        tr = lst_point_in_top_right[idx]
        br = lst_point_in_top_right[idx+1]
        bl = lst_point_in_top_left[idx+1]
        lst_bbox.append([tl, tr, br, bl])

    print(f'List of bboxes: {lst_bbox}')
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
    print(f'Font size: {lst_size}')
    print(f'Min font size: {max_font_size}')
    # endregion

    # region 4: Draw the text
    font = ImageFont.truetype( font_path , max_font_size)
    for w , _bbox in zip(text.split(), lst_bbox):
      p_center, text_size = get_center_point(_bbox, w, font)
      print(f'x center: {p_center}')

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
        fillcolor= bg_cv,
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

def check_text_size(
    text_string: str,
    bbox: list,
    angle: float,
    font_path: str = 'font/arial.ttf'
)->  tuple:
    # region get height and width of bounding box
    tl, tr, br, bl = bbox
    width = euclidean_distance(tl, tr)
    height = euclidean_distance(tl, bl)
    # endregion
    print(f'Height:{height} Width:{width}')

    font_size = 1
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

        width_x = (width - rotated_text_width) // 2
        height_y = (height - rotated_text_height) // 2

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

def get_center_point(
    bbox: list,
    text_str: str,
    font: ImageFont,
)-> list[int, int]:
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

if __name__ == "__main__":
    # image = Image.open("366641616_2264556887067173_1651877982799532575_n.jpg")
    # region INPUT
    text = "Tĩnh Lan"
    bbox = [[117, 99], [217, 74], [284, 353], [184, 378]]
    src_img = cv2.imread(filename='366641616_2264556887067173_1651877982799532575_n.jpg')
    mask_image = cv2.imread('mask_image.png')
    # bbox = [[245, 8], [293, 11], [256, 614], [209, 612]]

    # endregion
    tl, tr, br, bl = bbox
    fg = (5, 5, 16)
    fg_cv = tuple(list(fg)[::-1])


    # region Get mask
    
    
    # endregion

    # region get temporary image
    bg = (96, 115, 205)
    bg_cv = tuple(list(bg)[::-1])
    bg_img= np.full_like(
      a = mask_image,
      fill_value= bg_cv,
      dtype= np.uint8
    )

    _bg_img = cv2.bitwise_and(
      bg_img,
      mask_image,
    )
    cv2.imwrite(
      filename= 'bg_img.png',
      img = _bg_img
    )

    image = Image.fromarray(_bg_img).convert('RGB')
    # endregion
    
    # region calculate angle between two line
    line1 = [tl, bl]
    x_axis = (tl[0], 0)
    line2 = [x_axis, tl]
    angle = calculate_angle_between_line(line1, line2)
    print("Angle between Line 1 and Line 2 (degrees):", angle)
    # endregion

    # region Get height, width and direction
    width = euclidean_distance(tl, tr)
    height = euclidean_distance(tl, bl)
    print(f"Height x Width : {height}x{width}")
    if width >= height:
      direction = 'horizontal'
    else:
      direction = 'vertical'
    print(f'Direction: {direction}')
    # endregion

    if direction == 'horizontal':
      pass
    else:
      draw_text_vertical(
        text = text,
        bbox= bbox,
        bg_color=bg_cv,
        fg_color= fg_cv,
        image= image,
        height = height,
        width = width,
        angle= angle,
      )
    #   # region write the equation of the line
    #   a_line_left, b_line_left = get_para_in_line(tl,bl)
    #   print(a_line_left, b_line_left )

    #   a_line_right, b_line_right = get_para_in_line(tr,br)
    #   print(a_line_right, b_line_right)
    #   # endregion
      
    #   # region Calculate position for each word
    #   len_text  = len(text.split())
    #   print(f'len_text: {len_text} words')

    #   # region get point in top left corner
    #   lst_point_in_top_left = get_point_in_line(
    #       len_text = len_text,
    #       a_line = a_line_left,
    #       b_line = b_line_left,
    #       size  = height,
    #       first_point = tl,
    #   )

    #   lst_point_in_top_left.append(bl)
    #   print(f'lst_point_in_top_left : {lst_point_in_top_left}')
    #   # endregion

    #   # region get point in top right corner
    #   lst_point_in_top_right = get_point_in_line(
    #       len_text = len_text,
    #       a_line = a_line_right,
    #       b_line = b_line_right,
    #       size  = height,
    #       first_point = tr,
    #       )
    #   lst_point_in_top_right.append(br)
    #   print(f'lst_point_in_top_right : {lst_point_in_top_right}')
    #   # endregion

    #   # region merge point
    #   lst_bbox = []
    #   for idx in range(len(lst_point_in_top_left)-1):
    #       tl = lst_point_in_top_left[idx]
    #       tr = lst_point_in_top_right[idx]
    #       br = lst_point_in_top_right[idx+1]
    #       bl = lst_point_in_top_left[idx+1]
    #       lst_bbox.append([tl, tr, br, bl])

    #   print(f'List of bboxes: {lst_bbox}')
    #   # endregion

    # # endregion
      
    #   # region calculate size of text
    #   lst_size = []
    #   for w, _bbox in zip(text.split(), lst_bbox):
    #     font_size = check_text_size(
    #       text_string= w,
    #       bbox = _bbox,
    #       angle= angle,
    #     )
    #     lst_size.append(font_size)
    #   max_font_size = min(lst_size)
    #   print(f'Font size: {lst_size}')
    #   print(f'Max font size: {max_font_size}')

    #   # endregion
      
    #   # region draw text
    #   font = ImageFont.truetype("arial.ttf", max_font_size)
    #   # draw = ImageDraw.Draw(image, "RGB")
    #   for w , _bbox in zip(text.split(), lst_bbox):
    #     p_center, text_size = get_center_point(_bbox, w, font)
    #     print(f'x center: {p_center}')

    #     w_text, h_text = text_size
    #     # region draw text with rotate
    #     tmp_img = Image.new(
    #       mode = 'RGB',
    #       size = (w_text, h_text),
    #       color = bg_cv
    #     )
    #     # endregion

    #     # region draw text
    #     tmp_draw = ImageDraw.Draw(tmp_img)
    #     tmp_draw.text(
    #       xy= (0,0),
    #       text = w,
    #       align= 'center',
    #       font= font,
    #       fill= fg_cv
    #     )
        

    #     # endregion

    #     # region rotate text
    #     tmp_img = tmp_img.rotate(
    #       angle= angle,
    #       expand= True,
    #       fillcolor= bg_cv,
    #     )
    #     # endregion

    #     # region paste text
    #     image.paste(
    #       im = tmp_img,
    #       box= p_center
    #     )

    #     # endregion
    #   # endregion
    #   # image.save('output_image.jpg')

    # region paste background with polygons      
    cv_img = np.array(image)
    cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    cv_img = cv2.bitwise_and(cv_img, mask_image)
    not_masked_image = cv2.bitwise_not(mask_image)
    not_src_img = cv2.bitwise_and(not_masked_image, src_img)
    final_image = cv2.bitwise_or(cv_img, not_src_img)
    
    
    # cv2.imwrite(
    #     'outpt_mask.jpg',
    #     cv_img
    # )
    # cv2.imwrite(
    #     filename="not_masked_image.jpg",
    #     img = not_masked_image
    # )
    cv2.imwrite(
        filename="final_image_v2.jpg",
        img = final_image
    )
    # endregion










    # cv2.imwrite(
    #     filename="not_src_img.jpg",
    #     img = not_src_img
    # )

    # cv2.imwrite(
    #     filename="src.jpg",
    #     img = src_img
    # )

    # cv2.imwrite(
    #     filename="cv_img.jpg",
    #     img = cv_img
    # )
    # rotated_image.save("rotated_image.png")