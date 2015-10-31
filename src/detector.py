import numpy as np
import time
import scipy
import cv2
from matplotlib import pyplot as plt
from scipy import misc
import pdb
import unrotate

SECONDS_TO_WAIT = 3
plt.rcParams['image.cmap'] = 'gray' # set default image to grayscale

IMAGE_FOLDER = "../images/samples/"

img_filename = IMAGE_FOLDER + "pic1_cropped.png"
SLEEP = False
L_THRESH = 80
H_THRESH = 200

def get_counts(edge_img, i, max_h, window_size):
    if (i - window_size/2 < 0):
        count = np.count_nonzero((edge_img[0:i+window_size/2, :] == 255) - 0)
    elif (i +window_size/2 > max_h-1):
        count = np.count_nonzero((edge_img[i-window_size/2:, :] == 255) - 0)
    else:
        count = np.count_nonzero((edge_img[i-window_size/2:i+window_size/2, :] == 255) - 0)
    return count


def get_rows(edges,window_size=2):
    h, w = edges.shape
    row_counts = []
    for i in xrange(0, h):
        count = get_counts(edges, i, h, window_size)
        row_counts.append(count)
    return row_counts

def get_sorted_indexes(counts):
    indx = sorted(range(len(counts)), key = lambda k: counts[k])
    indx.reverse()
    return indx

def get_hough_transform_lines(image, edges):
    minLineLength = 300
    maxLineGap = 10
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength, maxLineGap)
    for (x1, y1, x2, y2) in lines[0]:
        cv2.line(image, (x1, y1), (x2, y2), (0,255,0), 2)
    return (image, edges)
    #plt.imshow(image)
    #plt.show()


# given images
while(True):
    #image = scipy.misc.imread(img_filename)
    image = cv2.imread(img_filename)
    image = cv2.medianBlur(image, 5)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = np.float32(gray)
    edges = cv2.Canny(image, L_THRESH, H_THRESH)

    #image, edges = get_hough_transform_lines(image, edges)

    # count rows and cols where edges are within a certain window_size range
    h, w = edges.shape
    row_counts = get_rows(edges)
    max_row_indexes = get_sorted_indexes(row_counts)
    curr_index = max_row_indexes[0]
    edges[curr_index, :] = 255
    rows_changed = [curr_index]
    num_rows_changed = 1
    for idx, row_idx in enumerate(max_row_indexes):
        #actual_row = row_counts[row_idx]
        in_range = False
        for r_changed in rows_changed:
            if (row_idx < r_changed+25 and row_idx > r_changed-25):
                in_range = True
        if (not in_range):
            edges[row_idx, :] = 255
            rows_changed.append(row_idx)
            num_rows_changed += 1
            if (num_rows_changed > 10):
                break

    #max_row_index = np.argmax(row_counts)
    rotated = np.rot90(edges)
    col_counts = get_rows(rotated)
    max_row_indexes = get_sorted_indexes(col_counts)
    curr_index = max_row_indexes[0]
    edges[:, w-curr_index] = 255
    rows_changed = [curr_index]
    num_rows_changed = 1
    for idx, row_idx in enumerate(max_row_indexes):
        #actual_row = row_counts[row_idx]
        in_range = False
        for r_changed in rows_changed:
            if (row_idx < r_changed+25 and row_idx > r_changed-25):
                in_range = True
        if (not in_range):
            edges[:, w-row_idx] = 255
            rows_changed.append(row_idx)
            num_rows_changed += 1
            if (num_rows_changed > 10):
                break

    #max_col_index = np.argmax(col_counts)
    h, w = edges.shape
    #edges[max_row_index, :] = 255
    #edges[:, w-max_col_index] = 255
    plt.imshow(edges)
    plt.show()

    if SLEEP: # just cause i dont want it to sleep each time i test right now
        time.sleep(SECONDS_TO_WAIT)
