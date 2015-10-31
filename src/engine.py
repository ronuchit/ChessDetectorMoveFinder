import numpy as np
import string
import pyttsx
import time
import chess as pychess
import chess.uci as pychess_uci

BASE_PATH = ".."
STOCKFISH_PATH = "/lib/stockfish-6-linux/src/stockfish"
# BASE_PATH = "/Users/shaunsingh/Documents/BerkeleyAcademics/Fall2015/csua/ChessDetectorMoveFinder"
# STOCKFISH_PATH = "/lib/stockfish-6-mac/src/stockfish"
BOARD_DIM = 8
SFISH_WHITE = 0
SFISH_BLACK = 1
SFISH_BOTH = 2
TIMEOUT_MS = 3000

class IllegalMoveException(Exception):
        pass

class BadBoardStateException(Exception):
        pass

class Game(object):
    def __init__(self, win, stockfish_path, stockfish_timeout=TIMEOUT_MS, stockfish_player=SFISH_WHITE):
        self.win = win
        self.board = pychess.Board()
        self.engine = pychess_uci.popen_engine(stockfish_path)
        self.engine.uci()
        self.engine.setoption({"UCI_Chess960": True})
        self.stockfish_timeout = stockfish_timeout
        self.stockfish_player = stockfish_player
	self.tts_engine = pyttsx.init()
        self.tts_engine.setProperty("rate", 130)
        voices = self.tts_engine.getProperty("voices")
        self.tts_engine.setProperty("voice", voices[9].id)
        if self.stockfish_player == SFISH_WHITE:
            what_playing = "white"
        elif self.stockfish_player == SFISH_BLACK:
            what_playing = "black"
        else:
            what_playing = "both white and black"
        self.tts_engine.say("i am playing %s"%what_playing)
        self.tts_engine.runAndWait()
        self.engine.info_handlers.append(pychess_uci.InfoHandler())

    def _apply_move(self, move):
        if move in self.board.legal_moves:
            self.board.push(move)
            self.engine.position(self.board)
        else:
            raise IllegalMoveException(move)

    def _receive_move(self, move_string):
        move = pychess.Move.from_uci(move_string)
        self._apply_move(move)

    def assisted_human_turn(self, speak=True):
	best_move = None
        if self.stockfish_player == SFISH_BLACK and self.board.turn == False:
            self.engine.go(movetime=self.stockfish_timeout, async_callback=True)
            time.sleep(self.stockfish_timeout / 1000)
            ih = self.engine.info_handlers[0]
            best_move = ih.info["pv"][1][0]
            score = ih.info["score"][1].cp
            mate = ih.info["score"][1].mate
        elif self.stockfish_player == SFISH_WHITE and self.board.turn == True:
            self.engine.go(movetime=self.stockfish_timeout, async_callback=True)
            time.sleep(self.stockfish_timeout / 1000)
            ih = self.engine.info_handlers[0]
            best_move = ih.info["pv"][1][0]
            score = ih.info["score"][1].cp
            mate = ih.info["score"][1].mate
        elif self.stockfish_player == SFISH_BOTH:
            self.engine.go(movetime=self.stockfish_timeout, async_callback=True)
            time.sleep(self.stockfish_timeout / 1000)
            ih = self.engine.info_handlers[0]
            best_move = ih.info["pv"][1][0]
            score = ih.info["score"][1].cp
            mate = ih.info["score"][1].mate
        if best_move is None:
            self.tts_engine.say("your turn")
            self.tts_engine.runAndWait()
            return None, None, None
	if speak:
            self.read_move(best_move, score, mate)
        return best_move, score, mate

    def read_move(self, move, score, mate):
        move_start, move_end = move.uci()[:2], move.uci()[2:]
        piece = self.board.piece_at(move.from_square).piece_type
        piece_name = "default"
        if piece == pychess.PAWN:
            piece_name = "pawn"
        elif piece == pychess.KNIGHT:
            piece_name = "knight"
        elif piece == pychess.BISHOP:
            piece_name = "bishop"
        elif piece == pychess.ROOK:
            piece_name = "rook"
        elif piece == pychess.QUEEN:
            piece_name = "queen"
        elif piece == pychess.KING:
            piece_name = "king"
	self.tts_engine.say("move %s from %s to %s"%(piece_name, move_start, move_end))
        if mate:
            self.tts_engine.say("checkmate in %d, loser"%mate)
        else:
            if score < 0:
                self.tts_engine.say("score is negative %.2f"%(abs(score) / 100.0))
            else:
                self.tts_engine.say("score is %.2f"%(score / 100.0))
        self.tts_engine.runAndWait()

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
