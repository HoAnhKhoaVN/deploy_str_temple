import numpy as np
from time import time
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


if __name__ == '__main__':
    bbox = [[117, 99], [217, 74], [284, 353], [184, 378]]
    tl, tr, br, bl = bbox
    s= time()
    width = euclidean_distance(tl, tr)
    height = euclidean_distance(tl, bl)
    e = time()
    print(f'Time v2: {e-s} s')

    print(f"Height x Width : {height}x{width}")
