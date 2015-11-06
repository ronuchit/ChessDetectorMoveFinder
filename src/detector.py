import numpy as np
import time
import scipy
import itertools
import cv2
from matplotlib import pyplot as plt
from scipy import misc
import pdb
import unrotate as ur
from engine import *

IMAGE_FOLDER = "../images/"
plt.rcParams['image.cmap'] = 'gray'

img_filename = IMAGE_FOLDER + "pic.pngout.png"
GRAPH = True

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

def fix_rows(rows, do_cols=False):
    rows = sorted(rows)
    first_elem = rows[0]
    rows = rows[1:-1]
    avg = np.average([rows[i] - rows[i-1] for i in range(1, len(rows))])
    # second if condition is a major hack -- do not try this at home
    if rows[0] - avg < 0 or (first_elem < 15 and not do_cols):
        rows.append(int(rows[-1] + avg))
        rows.append(int(rows[-1] + avg))
    else:
        rows.append(int(rows[-1] + avg))
        rows.insert(0, int(rows[0] - avg))
    return rows

def get_rows_changed(max_row_indexes, do_cols=False):
    rows_changed = []
    num_rows_changed = 0
    for idx, row_idx in enumerate(max_row_indexes):
        in_range = False
        for r_changed in rows_changed:
            if (row_idx < r_changed+25 and row_idx > r_changed-25):
                in_range = True
        if (not in_range):
            rows_changed.append(row_idx)
            num_rows_changed += 1
            if (num_rows_changed >= 9):
                break
    if len(rows_changed) <= 3:
        print "Too few rows changed, skipping"
        return None
    rows_changed = fix_rows(rows_changed, do_cols)
    return rows_changed

def determine_board_configuration(img_r, img_binary, rows_changed, cols_changed):
    canny_edges = cv2.Canny(img_r, 30, 110)
    # plt.imshow(canny_edges)
    # plt.show()
    board = -1 * np.ones((8, 8))
    for i in range(len(rows_changed) - 1):
        for j in range(len(cols_changed) - 1):
            low_y, high_y, low_x, high_x = rows_changed[i], rows_changed[i+1], cols_changed[j], cols_changed[j+1]
            # determine empty squares
            square = canny_edges[low_x+10:high_x-10, low_y+10:high_y-10]
            if np.linalg.norm(square) < 1e-5:
                cv2.circle(img_r, ((high_y - low_y) / 2 + low_y, (high_x - low_x) / 2 + low_x), 1, (255, 0, 0), 10)
                board[i, j] = 0
            # determine black or white pieces
            if board[i, j] == -1:
                if i % 2 == j % 2:
                    square = img_binary[low_x+10:high_x-10, low_y+10:high_y-10]
                    # white square
                    if np.average(square) > 230:
                        cv2.circle(img_r, ((high_y - low_y) / 2 + low_y, (high_x - low_x) / 2 + low_x), 1, (0, 255, 0), 10)
                        board[i, j] = 1
                    else:
                        cv2.circle(img_r, ((high_y - low_y) / 2 + low_y, (high_x - low_x) / 2 + low_x), 1, (0, 0, 255), 10)
                        board[i, j] = 2
                else:
                    square = img_r[low_x+10:high_x-10, low_y+10:high_y-10]
                    # black square
                    if np.average(square) > 80:
                        cv2.circle(img_r, ((high_y - low_y) / 2 + low_y, (high_x - low_x) / 2 + low_x), 1, (0, 255, 0), 10)
                        board[i, j] = 1
                    else:
                        cv2.circle(img_r, ((high_y - low_y) / 2 + low_y, (high_x - low_x) / 2 + low_x), 1, (0, 0, 255), 10)
                        board[i, j] = 2
    return board

def main(chess):
    ran_stockfish = False
    while True:
        image = cv2.imread(img_filename)
        if image is None:
            continue
        img_binary, img_r = ur.unrotate(image)
        if img_r is None or np.max(img_binary) < 1e-5:
            continue
        h, w, d = img_r.shape

        edges = get_vert_grad(img_r)
        row_counts = get_rows(edges)
        max_row_indexes = sorted(range(len(row_counts)), key = lambda k: row_counts[k], reverse=True)
        rows_changed = get_rows_changed(max_row_indexes)
        if rows_changed is None or len(rows_changed) != 9:
            continue

        edges = np.rot90(img_r)
        edges = get_vert_grad(edges)
        col_counts = get_rows(edges)
        max_col_indexes = sorted(range(len(col_counts)), key = lambda k: col_counts[k], reverse=True)
        cols_changed = get_rows_changed(max_col_indexes, True)
        if cols_changed is None or len(cols_changed) != 9:
            continue
        edges = np.rot90(edges, k=3)

        low_y, high_y, low_x, high_x = rows_changed[7], rows_changed[8], cols_changed[7], cols_changed[8]
        square = img_binary[low_x+10:high_x-10, low_y+10:high_y-10]
        if np.average(square) < 100:
            print "Could not properly detect bottom right corner: %d with threshold >=100."%np.average(square)
            continue
        low_y, high_y, low_x, high_x = rows_changed[7], rows_changed[8], cols_changed[0], cols_changed[1]
        square = img_r[low_x+10:high_x-10, low_y+10:high_y-10]
        if np.average(square) > 80:
            print "Could not properly detect top right corner: %d with threshold <=50."%np.average(square)
            continue

        board = determine_board_configuration(img_r, img_binary, rows_changed, cols_changed)

        if GRAPH:
            for row_idx in cols_changed:
                cv2.line(img_r, (0, row_idx), (w, row_idx), (0, 0, 255), 1)
            for row_idx in rows_changed:
                cv2.line(img_r, (row_idx, 0), (row_idx, h), (0, 255, 0), 1)
        cv2.imwrite("../images/temp.png", img_r)

        board = board[:, ::-1].T
        if not ran_stockfish:
            best_move, score, mate = chess.assisted_human_turn()
            if best_move is not None and score is None:
                print "\n\nSTOCKFISH RECOMMENDS: %s with mate in %s\n\n"%(best_move, mate)
            elif best_move is not None:
                print "\n\nSTOCKFISH RECOMMENDS: %s with a score of %f\n\n"%(best_move, score / 100.0)
            ran_stockfish = True
        move = obtain_moves(board, chess.board)
        if move is None:
            continue
        try:
            chess._receive_move(move)
        except IllegalMoveException as e:
            print "Illegal move detected!"
            continue
        print "Move %s successful!"%move
        ran_stockfish = False

if __name__ == "__main__":
    chess = Game(win=True, stockfish_path=BASE_PATH + STOCKFISH_PATH)
    main(chess)
