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

def get_counts(edge_img, i, max_h, window_size):
    count = np.count_nonzero((edge_img[i, :] == 255) - 0)
    #if (i - window_size/2 < 0):
        #count = np.count_nonzero((edge_img[0:i+window_size/2, :] == 255) - 0)
    #elif (i +window_size/2 > max_h-1):
        #count = np.count_nonzero((edge_img[i-window_size/2:, :] == 255) - 0)
    #else:
        #count = np.count_nonzero((edge_img[i-window_size/2:i+window_size/2, :] == 255) - 0)
    return count


def get_rows(edges,window_size=2):
    h, w, d = edges.shape
    row_counts = []
    for i in xrange(0, h):
        count = get_counts(edges, i, h, window_size)
        row_counts.append(count)
    return row_counts

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
    image = cv2.imread(img_filename)
    image_unrotated = ur.unrotate(image)
    h, w, d = image_unrotated.shape
    #edges = cv2.Canny(image_unrotated, L_THRESH, H_THRESH)
    #edges = cv2.Sobel(image_unrotated, cv2.CV_64F, 1, 0, ksize=1)
    sharp_filter = np.array([[-1, 0, 1], [-1, 0, 1], [-1,0,1]])
    edges = cv2.filter2D(image_unrotated, -1, sharp_filter)
    sharp_filter = np.array([[1, 0, -1], [1, 0, -1], [1,0,-1]])
    edges_2 = cv2.filter2D(image_unrotated, -1, sharp_filter)
    edges = edges | edges_2
    #image, edges = get_hough_transform_lines(image, edges)

    # count rows and cols where edges are within a certain window_size range
    #h, w = image_unrotated.shape
    row_counts = get_rows(edges)
    print row_counts
    max_row_indexes = sorted(range(len(row_counts)), key = lambda k: row_counts[k], reverse=True)
    print max_row_indexes
    rows_changed = []
    num_rows_changed = 0
    for idx, row_idx in enumerate(max_row_indexes):
        in_range = False
        for r_changed in rows_changed:
            if (row_idx < r_changed+25 and row_idx > r_changed-25):
                in_range = True
        if (not in_range):
            #edges[row_idx, :] = 122
            cv2.line(image_unrotated, (row_idx, 0), (row_idx, w), (0, 255, 0), 1)
            image[row_idx, :, : ] = 0
            rows_changed.append(row_idx)
            num_rows_changed += 1
            if (num_rows_changed >= 9):
                break
    print rows_changed
    plt.figure()
    plt.subplot(1,2,1)
    plt.imshow(edges)
    plt.subplot(1,2,2)
    plt.imshow(image_unrotated)
    plt.show()

    pdb.set_trace()
    edges = cv2.Sobel(image_unrotated, cv2.CV_64F, 0, 1, ksize=5)
    rotated = np.rot90(edges)
    col_counts = get_rows(rotated)
    max_row_indexes = get_sorted_indexes(col_counts)
    rows_changed = []
    num_rows_changed = 0
    for idx, row_idx in enumerate(max_row_indexes):
        in_range = False
        for r_changed in rows_changed:
            if (row_idx < r_changed+25 and row_idx > r_changed-25):
                in_range = True
        if (not in_range):
            #edges[:, w-row_idx] = 122
            cv2.line(image_unrotated, (0, row_idx), (h, row_idx), (0, 255, 0), 1)
            rows_changed.append(row_idx)
            num_rows_changed += 1
            if (num_rows_changed >= 9):
                break

    plt.imshow(image_unrotated)
    plt.show()
    pdb.set_trace()

    if SLEEP: # just cause i dont want it to sleep each time i test right now
        time.sleep(SECONDS_TO_WAIT)
