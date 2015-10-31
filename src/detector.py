import numpy as np
import time
import scipy
import cv2
from matplotlib import pyplot as plt
from scipy import misc
import pdb

SECONDS_TO_WAIT = 3
plt.rcParams['image.cmap'] = 'gray' # set default image to grayscale

IMAGE_FOLDER = "../images/samples/"

img_filename = IMAGE_FOLDER + "pic1_cropped.png"
SLEEP = False
L_THRESH = 50
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
    pdb.set_trace()
    return row_counts

# given images
while(True):
    #image = scipy.misc.imread(img_filename)
    image = cv2.imread(img_filename)
    image = cv2.medianBlur(image, 5)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = np.float32(gray)
    edges = cv2.Canny(image, L_THRESH, H_THRESH)

    dst = cv2.cornerHarris(gray, 2, 5, 0.04)
    dst = cv2.dilate(dst, None)
    image[dst>0.01*dst.max()] = [0,0,255]
    # count rows and cols where edges are within a certain window_size range
    #row = get_rows(edges)
    #rotated = np.rot90(edges)
    #cols = get_rows(rotated)
    #plt.imshow(image)
    #plt.show()
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    pdb.set_trace()
    test = cv2.drawContours(image, contours, -1, (0, 255, 0), 3)
    cv2.imshow('image', image)
    cv2.waitKey(0)

    pdb.set_trace()
    if SLEEP: # just cause i dont want it to sleep each time i test right now
        time.sleep(SECONDS_TO_WAIT)
