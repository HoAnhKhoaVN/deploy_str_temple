from equation_line import get_para_in_line
from distance import euclidean_distance

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


def get_center_point(
    bbox: list
)-> list[int, int]:
    _tl, _tr, _br, _bl = bbox
    a, b = get_para_in_line(_tl, _br)
    # print(f"a, b: {a,b}")

    # print(f"_tl, _br: {_tr, _bl}")
    _a, _b = get_para_in_line(_tr, _bl)
    # print(f"_a , _b : {_a,_b}")

    x_center = int((_b-b)//(a - _a))
    y_center = int(a*x_center + b)

    return [x_center, y_center]


if __name__ == '__main__':
    text = "Tĩnh Lan"
    len_text  = len(text.split())
    bbox = [[117, 99], [217, 74], [284, 353], [184, 378]]
    tl, tr, br, bl = bbox

    # region get height
    height = euclidean_distance(tl, bl)
    print(f'height" {height}')
    # endregion



    # region get line
    a_line_left, b_line_left = get_para_in_line(tl,bl)
    print(a_line_left, b_line_left )

    a_line_right, b_line_right = get_para_in_line(tr,br)
    print(a_line_right, b_line_right)
    # endregion


    lst_point_in_top_left = get_point_in_line(
        len_text = len_text,
        a_line = a_line_left,
        b_line = b_line_left,
        size  = height,
        first_point = tl,
    )

    lst_point_in_top_left.append(bl)
    print(f'lst_point_in_top_left : {lst_point_in_top_left}')

    lst_point_in_top_right = get_point_in_line(
        len_text = len_text,
        a_line = a_line_right,
        b_line = b_line_right,
        size  = height,
        first_point = tr,
        )
    lst_point_in_top_right.append(br)
    print(f'lst_point_in_top_right : {lst_point_in_top_right}')


    # region merge point
    lst_bbox = []
    for idx in range(len(lst_point_in_top_left)-1):
        tl = lst_point_in_top_left[idx]
        tr = lst_point_in_top_right[idx]
        br = lst_point_in_top_right[idx+1]
        bl = lst_point_in_top_left[idx+1]
        lst_bbox.append([tl, tr, br, bl])

    print(f'List of bboxes: {lst_bbox}')
    # endregion


    # region get center coordinates
    _tl, _tr, _br, _bl = lst_bbox[0]
    x_center, y_center = get_center_point(lst_bbox[0])
    print(f'x center: {x_center, y_center}')
    # endregion


    



