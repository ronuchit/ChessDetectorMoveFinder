import numpy as np
import time
import scipy
import cv2
import itertools
from matplotlib import pyplot as plt
from scipy import misc

SECONDS_TO_WAIT = 3
plt.rcParams['image.cmap'] = 'gray' # set default image to grayscale

IMAGE_FOLDER = "../images/samples/"

img_filename = IMAGE_FOLDER + "pic4.png"
DARK_COLOR = [77, 92, 84] # TODO: pick it manually
DARK_THRESHOLD = 100

def unrotate(image):
    #image = cv2.imread(img_filename)
    image = cv2.medianBlur(image, 5)
    subbed = np.linalg.norm(image - DARK_COLOR, axis=2)
    image[:, :] = [255, 255, 255]
    for ind in zip(*np.where(subbed < DARK_THRESHOLD)):
        image[(ind[0], ind[1])] = [0, 0, 0]
    contours, hierarchy = cv2.findContours(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # test = cv2.drawContours(image, contours, -1, (0, 255, 0), 3)
    colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255)]
    num_selected = 0
    min_x, max_x, min_y, max_y = float("inf"), float("-inf"), float("inf"), float("-inf")
    angles = []
    for i, c in enumerate(contours):
        if cv2.contourArea(c) < 2000:
            continue
        # a is a list of two tuples: x indices and y indices for this contour
        a = zip(*[x[0][0] for x in zip(c)])[::-1]
        low_x, high_x, low_y, high_y = min(a[0]), max(a[0]), min(a[1]), max(a[1])
        dim0 = high_x - low_x
        dim1 = high_y - low_y
        # should match with known dimensions of the square
        if dim0 < 50 or dim0 > 90 or dim1 < 50 or dim1 > 90:
            continue
        # update mins and maxes so we can crop later
        min_x = min(low_x, min_x)
        max_x = max(high_x, max_x)
        min_y = min(low_y, min_y)
        max_y = max(high_y, max_y)
        # find norm across 36 evenly sampled points in square
        x_space = np.linspace(low_x, high_x, num=8)[1:-1].astype(int)
        y_space = np.linspace(low_y, high_y, num=8)[1:-1].astype(int)
        if np.linalg.norm(image[zip(*list(itertools.product(x_space, y_space)))]) > 1e-5:
            continue

        num_selected += 1
        # draw contour for debugging
        cv2.drawContours(image, contours, i, colors[i % 3], 3)
        # cv2.rectangle(image, (low_y, low_x), (high_y, high_x), colors[i % 3])
        rect_corners = cv2.cv.BoxPoints(cv2.minAreaRect(c))
        rect_corners = sorted(rect_corners, key=lambda r: r[1])[:2]
        rect_corners = sorted(rect_corners, key=lambda r: r[0])
        angles.append(np.arctan2(rect_corners[1][1] - rect_corners[0][1], rect_corners[1][0] - rect_corners[0][0]))
    image = image[min_x-10:max_x+10, min_y-10:max_y+10]
    image = misc.imrotate(image, np.average(angles) / (2 * np.pi) * 360)
    return image

if __name__ == "__main__":
    plt.imshow(unrotate())
    plt.show()
