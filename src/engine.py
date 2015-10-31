import argparse
import numpy as np
import string
import pyttsx
import chess as pychess
import chess.uci as pychess_uci

#BASE_PATH = ".."
#STOCKFISH_PATH = "/lib/stockfish-6-linux/src/stockfish"
BASE_PATH = "/Users/shaunsingh/Documents/BerkeleyAcademics/Fall2015/csua/ChessDetectorMoveFinder"
STOCKFISH_PATH = "/lib/stockfish-6-mac/src/stockfish"
TIMEOUT = 5000


BOARD_DIM = 8

SFISH_WHITE = 0
SFISH_BLACK = 1
SFISH_BOTH = 2


class IllegalMoveException(Exception):
        pass

class BadBoardStateException(Exception):
        pass

class Game(object):
    def __init__(self, win, stockfish_path, stockfish_timeout=2000, stockfish_player=SFISH_BLACK):
        self.win = win
        self.board = pychess.Board()
        self.engine = pychess_uci.popen_engine(stockfish_path)
        self.engine.uci()
        self.engine.setoption({"UCI_Chess960": True})
        self.stockfish_timeout = stockfish_timeout
        self.stockfish_player = stockfish_player
	self.tts_engine = pyttsx.init()

    
    def _apply_move(self, move):
        if move in self.board.legal_moves:
            self.board.push(move)
            self.engine.position(self.board)
        else:
            raise IllegalMoveException(move)

    def _receive_move(self, move_string):
        move_string = self._valid_string(move_string)
        move = pychess.Move.from_uci(move_string)
        self._apply_move(move)

    # TODO: currently identity
    def _valid_string(self, move_string):
        return move_string

    def start_game(self):
        self.engine.ucinewgame()
        return True

    def assisted_human_turn(self, speak=True):
	best_move = None
        if self.stockfish_player = SFISH_BLACK and self.board.turn == False:
            best_move, ponder = self.engine.go(movetime=self.stockfish_timeout)
        elif self.stockfish_player = SFISH_WHITE and self.board.turn == True:
            best_move, ponder = self.engine.go(movetime=self.stockfish_timeout)
        elif self.stockfish_player = SFISH_BOTH:
            best_move, ponder = self.engine.go(movetime=self.stockfish_timeout)
	if speak and best_move:
            self.read_move(best_move)
        return best_move

    #TODO: verify
    def read_move(self, move):
	horizontalPos = None
	verticalPos = None
	playerColor = None
	self.tts_engine.say(move)
	voices = self.tts_eengine.getProp


    def human_turn(self, move_string):
        self._receive_move(move_string)


EMPTY = 0
WHITE = 1
BLACK = 2
# values enum for pychess
WHITE_PYCH = True
BLACK_PYCH = False

# reversed board of string representation!
initial_state = np.array( 
        [[1,1,1,1,1,1,1,1],
        [1,1,1,1,1,0,1,1],
        [0,0,0,0,0,1,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [2,2,2,2,2,2,2,2],
        [2,2,2,2,2,2,2,2]])

bad_state = np.array( 
        [[1,1,1,1,1,1,1,1],
        [1,1,1,1,1,0,1,1],
        [0,0,0,0,0,1,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,2,0,0],
        [2,2,2,2,2,0,2,2],
        [2,2,2,2,2,2,2,2]])


def changed_positions(cv_board, pychess_board):
    new_filled = []
    new_empty = [] 
    captured_pieces = []
    for i in range(BOARD_DIM):
        offset = i * BOARD_DIM
        for j in range(BOARD_DIM):
            # old value = {(True:White), (False:Black), (None:Empty)}
            old_value = pychess_board.piece_at(offset+j)
            if old_value:
                old_value = old_value.color
            #old_fill_color = None
            new_value = cv_board[i,j]
            changed = changed_val(new_value, old_value)
            if changed:
                if captured_val(new_value, old_value):
                    captured_pieces.append((i,j))
                if new_value == 0:
                    new_empty.append((i,j))
                else:
                    new_filled.append((i,j))
    return (new_empty, new_filled, captured_pieces) 


def changed_val(cv_val, pychess_val):
    if cv_val == WHITE and pychess_val == WHITE_PYCH: 
        return False
    elif cv_val == BLACK and pychess_val == BLACK_PYCH: 
        return False
    elif cv_val == EMPTY and pychess_val == None: 
        return False
    return True


def captured_val(cv_val, pychess_val):
    if cv_val == WHITE and pychess_val == BLACK_PYCH: 
        return True
    elif cv_val == BLACK and pychess_val == WHITE_PYCH: 
        return True


def np_to_uci(coords):
    row, col = coords
    row += 1
    col = string.lowercase[col]
    return "%s%s" % (col, row)


def obtain_moves(cv_board, pychess_board):
    (new_empty, new_filled, captured_pieces) = changed_positions(cv_board, pychess_board)

    new_filled = map(lambda np: np_to_uci(np), new_filled)
    new_empty = map(lambda np: np_to_uci(np), new_empty)

    # print new_empty
    # print new_filled
    # print captured_pieces
  
    if len(new_filled) > 1:
        return handle_castle(new_filled)

    moves = zip(new_empty, new_filled)
    if not moves:
        print "No move detected!"
        return None
    # string bullshit
    move_str = ""
    for move in moves: 
        for m in move:
            move_str += m
    return move_str

def handle_castle(new_filled):
    # Kingside castle
    if 'g8' in new_filled:
        return 'e8h8'
    elif 'g1' in new_filled:
        return 'e1h1'
    # Queenside castle
    if 'c8' in new_filled:
        return 'e8a8'
    elif 'c1' in new_filled:
        return 'e1a1'
    print "Two moves!"
    return None

chess = Game(win=True, stockfish_path=BASE_PATH + STOCKFISH_PATH)
# move = obtain_moves(initial_state, chess.board)
# chess._receive_move(move)
# print "First pawn move"
# print chess.board
# move = obtain_moves(bad_state, chess.board)
# chess._receive_move(move)
# print "Bad error pawn move"
# print chess.board

