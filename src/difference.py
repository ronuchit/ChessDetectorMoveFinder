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
    changed_squares = {}
    for i in range(len(rows_changed) - 1):
        for j in range(len(cols_changed) - 1):
            low_y, high_y, low_x, high_x = rows_changed[i], rows_changed[i+1], cols_changed[j], cols_changed[j+1]
            square = img[low_x+10:high_x-10, low_y+10:high_y-10]
            prev_square = prev_image[low_x+10:high_x-10, low_y+10:high_y-10]
            indices = np.where(np.abs(square - prev_square) >= threshold)
            changed_squares[(i, j)] = len(indices[0])
    sorted_x = sorted(changed_squares.items(), key=operator.itemgetter(1), reverse=True)
    return sorted_x
