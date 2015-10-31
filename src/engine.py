import argparse
import chess as pychess
import chess.uci as pychess_uci

BASE_PATH = "/Users/shaunsingh/Documents/BerkeleyAcademics/Fall2015/csua/ChessDetectorMoveFinder"
STOCKFISH_PATH = "/lib/stockfish-6-mac/src/stockfish"
TIMEOUT = 2000


class IllegalMoveException(Exception):
        pass


class Game(object):
    def __init__(self, win, stockfish_path, stockfish_timeout=2000):
        self.win = win
        self.board = pychess.Board()
        self.engine = pychess_uci.popen_engine(stockfish_path)
        self.engine.uci()
        self.stockfish_timeout = stockfish_timeout

    def _best_move(self):
        best_move, ponder = self.engine.go(movetime=self.stockfish_timeout)
        return best_move
    
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

    def assisted_human_turn(self):
        best_move = self._best_move()
        self._apply_move(best_move)

    def human_turn(self, move_string):
        self._receive_move(move_string)

def play_game():
    chess = Game(win=True, stockfish_path=BASE_PATH + STOCKFISH_PATH)
    chess.start_game()
    print(chess.board)

    while True:
        chess.human_turn()
        print(chess.board)
        chess.assisted_human_turn()
        print(chess.board)
    
play_game()
   

