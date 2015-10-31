import numpy as np
import operator
import pdb
import itertools

def get_square(coord, rows_changed, cols_changed):
    for i in xrange(len(rows_changed)-1):
        for j in xrange(len(cols_changed)-1):
            low_y, high_y, low_x, high_x = rows_changed[i], rows_changed[i+1], cols_changed[j], cols_changed[j+1]
            y, x = coord
            if (low_y <= coord[0] and coord[0] < high_y and low_x <= coord[1] and coord[1] < high_x):
                return (i, j)
    return None


def calc_difference(img, prev_image, rows_changed, cols_changed, threshold=1):
    difference = img - prev_image
    abs_diff = np.abs(difference)
    indexes = np.where(abs_diff >= threshold)
    changed_squares={}
    for i in indexes[0]:
        for j in indexes[1]:
            square = get_square((i, j), rows_changed, cols_changed)
            if square is not None:
                if not changed_squares.has_key(square):
                    changed_squares[square] = 1
                else:
                    changed_squares[square] += 1
    sorted_x = sorted(changed_squares.items(), key=operator.itemgetter(1), reverse=True)
    return sorted_x
