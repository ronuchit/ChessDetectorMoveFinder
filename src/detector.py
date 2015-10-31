import numpy as np
import time
import scipy
import cv2
from matplotlib import pyplot as plt
from scipy import misc
import pdb
import unrotate as ur

SECONDS_TO_WAIT = 3
plt.rcParams['image.cmap'] = 'gray' # set default image to grayscale

IMAGE_FOLDER = "../images/samples/"

img_filename = IMAGE_FOLDER + "pic1_cropped.png"
SLEEP = False
L_THRESH = 80
H_THRESH = 200

def get_counts(edge_img, i, max_h, do_col=False):
    window_size = 2
    if do_col:
        if (i - window_size/2 < 0):
            count = np.count_nonzero((edge_img[0:i+window_size/2, :] == 255) - 0)
        elif (i +window_size/2 > max_h-1):
            count = np.count_nonzero((edge_img[i-window_size/2:, :] == 255) - 0)
        else:
            count = np.count_nonzero((edge_img[i-window_size/2:i+window_size/2, :] == 255) - 0)
    else:
        if (i - window_size/2 < 0):
            count = np.count_nonzero((edge_img[:, 0:i+window_size/2] == 255) - 0)
        elif (i +window_size/2 > max_h-1):
            count = np.count_nonzero((edge_img[:, i-window_size/2:] == 255) - 0)
        else:
            count = np.count_nonzero((edge_img[:, i-window_size/2:i+window_size/2] == 255) - 0)
    return count


def get_rows(edges, do_col=False):
    h, w, d = edges.shape
    row_counts = []
    for i in xrange(0, w):
        count = get_counts(edges, i, w, do_col)
        row_counts.append(count)
    return row_counts

def get_vert_grad(img):
    sharp_filter = np.array([[-1, 0, 1], [-1, 0, 1], [-1,0,1]])
    edges = cv2.filter2D(img, -1, sharp_filter)
    sharp_filter = np.array([[1, 0, -1], [1, 0, -1], [1,0,-1]])
    edges_2 = cv2.filter2D(img, -1, sharp_filter)
    vert_edges = edges | edges_2
    return vert_edges

def get_rows_changed(max_row_indexes, do_cols=False):
    rows_changed = []
    num_rows_changed = 0
    for idx, row_idx in enumerate(max_row_indexes):
        in_range = False
        for r_changed in rows_changed:
            if (row_idx < r_changed+25 and row_idx > r_changed-25):
                in_range = True
        if (not in_range):
            if do_cols:
                cv2.line(image_unrotated, (0, row_idx), (h, row_idx), (0, 0, 255), 1)
            else:
                cv2.line(image_unrotated, (row_idx, 0), (row_idx, w), (0, 255, 0), 1)
            rows_changed.append(row_idx)
            num_rows_changed += 1
            if (num_rows_changed >= 9):
                break
    return rows_changed


# given images
while(True):
    image = cv2.imread(img_filename)
    image_unrotated = ur.unrotate(image)
    h, w, d = image_unrotated.shape
    edges = get_vert_grad(image_unrotated)

    # count rows and cols where edges are within a certain window_size range
    row_counts = get_rows(edges)
    max_row_indexes = sorted(range(len(row_counts)), key = lambda k: row_counts[k], reverse=True)
    rows_changed = get_rows_changed(max_row_indexes)

    edges = np.rot90(image_unrotated)
    #image_unrotated = np.rot90(image_unrotated)
    edges = get_vert_grad(edges)

####
    col_counts = get_rows(edges, True)
    max_col_indexes = sorted(range(len(col_counts)), key = lambda k: col_counts[k], reverse=True)
    print col_counts
    print max_col_indexes
    cols_changed = get_rows_changed(max_col_indexes, True)
    edges = np.rot90(edges, k=3)
    plt.figure()
    plt.subplot(1,2,1)
    plt.imshow(edges)
    plt.subplot(1,2,2)
    plt.imshow(image_unrotated)
    plt.show()
    pdb.set_trace()

    if SLEEP: # just cause i dont want it to sleep each time i test right now
        time.sleep(SECONDS_TO_WAIT)
