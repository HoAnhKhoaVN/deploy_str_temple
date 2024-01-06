

def get_para_in_line(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    a = (y1-y2)/(x1-x2-1e-9)
    b = y1-a*x1

    return a, b



if __name__ == '__main__':
    bbox = [[117, 99], [217, 74], [284, 353], [184, 378]]
    tl, tr, br, bl = bbox

    a_line_left, b_line_left = get_para_in_line(tl,bl)
    print(a_line_left, b_line_left )

    a_line_right, b_line_right = get_para_in_line(tr,br)
    print(a_line_right, b_line_right)
