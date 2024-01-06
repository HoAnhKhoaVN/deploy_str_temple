import math
from typing import Tuple, List
def calculate_direction_vector(
    point1 : Tuple[int, int],
    point2 : Tuple[int, int]
)-> Tuple[int, int]:
    return (
        point2[0] - point1[0],
        point2[1] - point1[1],
    )
    
def calculate_angle_between_line(
    line1: List[Tuple[int, int]],
    line2: List[Tuple[int, int]],
)-> float:
    """
    Get the angle between two lines.

    Args:
        line1 {list[tuple[int, int]]}: A list of two points, representing the start and end points of the first line.
        line2 {list[tuple[int, int]]}: A list of two points, representing the start and end points of the second line.

    Returns:
        The angle between the two lines in degree.
    """
    # region 0: Calculate the direction vector
    line1_direction = calculate_direction_vector(
        point1= line1[0],
        point2= line1[1]
    )
    # print(f"Line 1: {line1_direction}")

    line2_direction = calculate_direction_vector(
        point1= line2[0],
        point2= line2[1]
    )
    # print(f"Line 2: {line2_direction}")

    # endregion

    # region 1: Calculate the dot product of the direction vectors
    # The angle between two vectors can be calculated using the dot product.
    # The dot product of two vectors is defined as:
    #
    # dot(v1, v2) = v1_x * v2_x + v1_y * v2_y
    #
    # where v1_x and v1_y are the x and y components of vector v1, and v2_x and v2_y are the x and y components of vector v2.
    dot_product = line1_direction[0] * line2_direction[0] + line1_direction[1] * line2_direction[1]
    # endregion

    # region 2: Calculate the magnitude of each direction vector
    # The angle between two vectors is also equal to the arccos of the dot product, divided by the product of the lengths of the vectors.
    # The length of a vector can be calculated using the Pythagorean theorem.
    #
    # length(v) = sqrt(v_x^2 + v_y^2)
    #
    # where v_x and v_y are the x and y components of vector v.
    magnitude_line1 = math.sqrt(line1_direction[0] ** 2 + line1_direction[1] ** 2)
    magnitude_line2 = math.sqrt(line2_direction[0] ** 2 + line2_direction[1] ** 2)
    # endregion

    # region 3: Calculate the angle between the lines using the arccosine function
    angle_radians = math.acos(dot_product / (magnitude_line1 * magnitude_line2))
    # endregion

    # region 4: Convert the angle to degrees
    angle_degrees = math.degrees(angle_radians)
    
    # endregion
    return angle_degrees

if __name__ == '__main__':
    # bbox = [[117, 99], [217, 74], [284, 353], [184, 378]]
    bbox = [[747, 16], [790, 18], [774, 576], [730, 575]]
    tl, tr, br, bl = bbox
    x_axis = (tl[0], 0)

    line1 = [tl, bl]
    line2 = [x_axis, tl]

    angle = calculate_angle_between_line(line1, line2)

    print(angle)

    