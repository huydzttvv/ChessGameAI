import pandas as pd
import numpy as np
import enum
import os
from ChessTypes import *
import chess.pgn
import chess
import pickle
from sklearn import feature_extraction, model_selection, naive_bayes, metrics, svm

"""
    How this works? We save the model in some a table
    [===================32 Columns===============] [======]
    |wP1|wP2....|wP8|wK|wQ|wR1|wR2|wN1|wN2|wB1|wB2| OUTCOME|

    Values of each column:
        + Outcome: WHITE | BLACK
        + Pieces: positional values (as used in scoreBoard Material)
    Can we search throu

    Only need to calculate all the probabilities for white:
        + The probailities for black would be: 1 - P(White_win) - P(draw)

    The target is to avoid losing the game:
        + Draws are acceptable

    Classes:  White Win | Black Win | Draw (By any mean)
"""


piecesScore = {
    "K": 900, "Q": 90, "R": 50,
    "B": 30, "N": 30, "p": 10
}

# * The matrix below indicates the positional advantages of white pieces
# * Index: (x, y)
# * Black values = White Values (7 - x , y )
# * Example:  B(7, 7) =  White(0 , 0)  | B(3,5) = White(3, 2)
KING_POS_VAL = [
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0],
    [-1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0],
    [2.0, 2.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0],
    [2.0, 3.0, 1.0, 0.0, 0.0, 1.0, 3.0, 2.0]
]

QUEEN_POS_VAL = [
    [-2, -1, -1, -0.5, -0, .5 - 1, -1, -2],
    [-1, 0, 0, 0, 0, 0, 0, -1],
    [-1, 0, 0.5, 0.5, 0.5, 0.5, 0, -1],
    [-0.5, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5],
    [0, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5],
    [-1, 0.5, 0.5, 0.5, 0.5, 0.5, 0, -1],
    [-1, 0, 0.5, 0, 0, 0, 0, -1],
    [-2, -1, -1, -0.5, -0.5, -1, -1, -2]
]

ROOK_POS_VAL = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0.5, 1, 1, 1, 1, 1, 1, 0.5],
    [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
    [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
    [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
    [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
    [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
    [0, 0, 0, 0.5, 0.5, 0, 0, 0]
]

BISHOP_POS_VAL = [
    [-2, -1, -1, -1, -1, -1, -1, -2],
    [-1, 0, 0, 0, 0, 0, 0, -1],
    [-1, 0, 0.5, 1, 1, 0.5, 0, -1],
    [-1, 0.5, 0.5, 1, 1, 0.5, 0.5, -1],
    [-1, 0, 1, 1, 1, 1, 0, -1],
    [-1, 1, 1, 1, 1, 1, 1, -1],
    [-2, -1, -1, -1, -1, -1, -1, -2]
]

KNIGHT_POS_VAL = [
    [-5, -4, -3, -3, -3, -3, -4, -5],
    [-4, -2, 0, 0, 0, 0, -2, -4],
    [-3, 0, 1, 1.5, 1.5, 1, 0, -3],
    [-3, 0.5, 1.5, 2, 2, 1.5, 0.5, -3],
    [-3, 0.5, 1, 1.5, 1.5, 1, 0.5, -3],
    [-4, -2, 0, 0.5, 0.5, 0, -2, -4],
    [-5, -4, -3, -3, -3, -3, -4, -5]
]

PAWN_POS_VAL = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [5, 5, 5, 5, 5, 5, 5, 5],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [0.5, 0.5, 1, 2.5, 2.5, 1, 0.5, 0.5],
    [0, 0, 0, 2, 2, 0, 0, 0],
    [0.5, -0.5, -1, 0, 0, -1, -0.5, 0.5],
    [0.5, 1, 1, -2, -2, 1, 1, 0.5],
    [0, 0, 0, 0, 0, 0, 0, 0]
]


# * KING POS
WHITE_KING_DICT = {0: 2.0, 1: 3.0, 2: 1.0, 3: 0.0, 4: 0.0, 5: 1.0, 6: 3.0, 7: 2.0, 8: 2.0, 9: 2.0, 10: 0.0, 11: 0.0, 12: 0.0, 13: 0.0, 14: 2.0, 15: 2.0, 16: -1.0, 17: -2.0, 18: -2.0, 19: -2.0, 20: -2.0, 21: -2.0, 22: -2.0, 23: -1.0, 24: -2.0, 25: -3.0, 26: -3.0, 27: -4.0, 28: -4.0, 29: -3.0, 30: -3.0, 31: -2.0, 32: -
                   3.0, 33: -4.0, 34: -4.0, 35: -5.0, 36: -5.0, 37: -4.0, 38: -4.0, 39: -3.0, 40: -3.0, 41: -4.0, 42: -4.0, 43: -5.0, 44: -5.0, 45: -4.0, 46: -4.0, 47: -3.0, 48: -3.0, 49: -4.0, 50: -4.0, 51: -5.0, 52: -5.0, 53: -4.0, 54: -4.0, 55: -3.0, 56: -3.0, 57: -4.0, 58: -4.0, 59: -5.0, 60: -5.0, 61: -4.0, 62: -4.0, 63: -3.0}

BLACK_KING_DICT = {0: -3.0, 1: -4.0, 2: -4.0, 3: -5.0, 4: -5.0, 5: -4.0, 6: -4.0, 7: -3.0, 8: -3.0, 9: -4.0, 10: -4.0, 11: -5.0, 12: -5.0, 13: -4.0, 14: -4.0, 15: -3.0, 16: -3.0, 17: -4.0, 18: -4.0, 19: -5.0, 20: -5.0, 21: -4.0, 22: -4.0, 23: -3.0, 24: -3.0, 25: -4.0, 26: -4.0, 27: -5.0, 28: -5.0, 29: -4.0, 30: -4.0,
                   31: -3.0, 32: -2.0, 33: -3.0, 34: -3.0, 35: -4.0, 36: -4.0, 37: -3.0, 38: -3.0, 39: -2.0, 40: -1.0, 41: -2.0, 42: -2.0, 43: -2.0, 44: -2.0, 45: -2.0, 46: -2.0, 47: -1.0, 48: 2.0, 49: 2.0, 50: 0.0, 51: 0.0, 52: 0.0, 53: 0.0, 54: 2.0, 55: 2.0, 56: 2.0, 57: 3.0, 58: 1.0, 59: 0.0, 60: 0.0, 61: 1.0, 62: 3.0, 63: 2.0}

# * QUEEN POS
BLACK_QUEEN_DICT = {0: -2, 1: -1, 2: -1, 3: -0.5, 4: 0, 5: -0.5, 6: -1, 7: -2, 8: -1, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: -1, 16: -1, 17: 0, 18: 0.5, 19: 0.5, 20: 0.5, 21: 0.5, 22: 0, 23: -1, 24: -0.5, 25: 0, 26: 0.5, 27: 0.5, 28: 0.5, 29: 0.5, 30: 0, 31: -
                    0.5, 32: 0, 33: 0, 34: 0.5, 35: 0.5, 36: 0.5, 37: 0.5, 38: 0, 39: -0.5, 40: -1, 41: 0.5, 42: 0.5, 43: 0.5, 44: 0.5, 45: 0.5, 46: 0, 47: -1, 48: -1, 49: 0, 50: 0.5, 51: 0, 52: 0, 53: 0, 54: 0, 55: -1, 56: -2, 57: -1, 58: -1, 59: -0.5, 60: -0.5, 61: -1, 62: -1, 63: -2}
WHITE_QUEEN_DICT = {0: -2, 1: -1, 2: -1, 3: -0.5, 4: -0.5, 5: -1, 6: -1, 7: -2, 8: -1, 9: 0, 10: 0.5, 11: 0, 12: 0, 13: 0, 14: 0, 15: -1, 16: -1, 17: 0.5, 18: 0.5, 19: 0.5, 20: 0.5, 21: 0.5, 22: 0, 23: -1, 24: 0, 25: 0, 26: 0.5, 27: 0.5, 28: 0.5, 29: 0.5, 30: 0, 31: -
                    0.5, 32: -0.5, 33: 0, 34: 0.5, 35: 0.5, 36: 0.5, 37: 0.5, 38: 0, 39: -0.5, 40: -1, 41: 0, 42: 0.5, 43: 0.5, 44: 0.5, 45: 0.5, 46: 0, 47: -1, 48: -1, 49: 0, 50: 0, 51: 0, 52: 0, 53: 0, 54: 0, 55: -1, 56: -2, 57: -1, 58: -1, 59: -0.5, 60: 0, 61: -0.5, 62: -1, 63: -2}
# * KNIGHT POS
BLACK_KNIGHT_DICT = {0: -5, 1: -4, 2: -3, 3: -3, 4: -3, 5: -3, 6: -4, 7: -5, 8: -4, 9: -2, 10: 0, 11: 0, 12: 0, 13: 0, 14: -2, 15: -4, 16: -3, 17: 0, 18: 1, 19: 1.5, 20: 1.5, 21: 1, 22: 0, 23: -3, 24: -3, 25: 0.5, 26: 1.5, 27: 2, 28: 2, 29: 1.5, 30: 0.5, 31: -
                     3, 32: -3, 33: 0.5, 34: 1, 35: 1.5, 36: 1.5, 37: 1, 38: 0.5, 39: -3, 40: -3, 41: 0, 42: 1, 43: 1.5, 44: 1.5, 45: 1, 46: 0, 47: -3, 48: -4, 49: -2, 50: 0, 51: 0.5, 52: 0.5, 53: 0, 54: -2, 55: -4, 56: -5, 57: -4, 58: -3, 59: -3, 60: -3, 61: -3, 62: -4, 63: -5}
WHITE_KNIGHT_DICT = {0: -5, 1: -4, 2: -3, 3: -3, 4: -3, 5: -3, 6: -4, 7: -5, 8: -4, 9: -2, 10: 0, 11: 0.5, 12: 0.5, 13: 0, 14: -2, 15: -4, 16: -3, 17: 0, 18: 1, 19: 1.5, 20: 1.5, 21: 1, 22: 0, 23: -3, 24: -3, 25: 0.5, 26: 1, 27: 1.5, 28: 1.5, 29: 1, 30: 0.5,
                     31: -3, 32: -3, 33: 0.5, 34: 1.5, 35: 2, 36: 2, 37: 1.5, 38: 0.5, 39: -3, 40: -3, 41: 0, 42: 1, 43: 1.5, 44: 1.5, 45: 1, 46: 0, 47: -3, 48: -4, 49: -2, 50: 0, 51: 0, 52: 0, 53: 0, 54: -2, 55: -4, 56: -5, 57: -4, 58: -3, 59: -3, 60: -3, 61: -3, 62: -4, 63: -5}

# * BISHOP POS
BLACK_BISHOP_DICT = {0: -2, 1: -1, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -2, 8: -1, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: -1, 16: -1, 17: 0, 18: 0.5, 19: 1, 20: 1, 21: 0.5, 22: 0, 23: -1, 24: -1, 25: 0.5, 26: 0.5, 27: 1, 28: 1, 29: 0.5, 30: 0.5,
                     31: -1, 32: -1, 33: 0, 34: 1, 35: 1, 36: 1, 37: 1, 38: 0, 39: -1, 40: -1, 41: 0, 42: 0.5, 43: 1, 44: 1, 45: 0.5, 46: 0, 47: -1, 48: -1, 49: 1, 50: 1, 51: 1, 52: 1, 53: 1, 54: 1, 55: -1, 56: -2, 57: -1, 58: -1, 59: -1, 60: -1, 61: -1, 62: -1, 63: -2}
WHITE_BISHOP_DICT = {0: -2, 1: -1, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -2, 8: -1, 9: 1, 10: 1, 11: 1, 12: 1, 13: 1, 14: 1, 15: -1, 16: -1, 17: 0, 18: 0.5, 19: 1, 20: 1, 21: 0.5, 22: 0, 23: -1, 24: -1, 25: 0, 26: 1, 27: 1, 28: 1, 29: 1, 30: 0, 31: -1,
                     32: -1, 33: 0.5, 34: 0.5, 35: 1, 36: 1, 37: 0.5, 38: 0.5, 39: -1, 40: -1, 41: 0, 42: 0.5, 43: 1, 44: 1, 45: 0.5, 46: 0, 47: -1, 48: -1, 49: 0, 50: 0, 51: 0, 52: 0, 53: 0, 54: 0, 55: -1, 56: -2, 57: -1, 58: -1, 59: -1, 60: -1, 61: -1, 62: -1, 63: -2}

# * ROOK POS
BLACK_ROOK_DICT = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0.5, 9: 1, 10: 1, 11: 1, 12: 1, 13: 1, 14: 1, 15: 0.5, 16: -0.5, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: -0.5, 24: -0.5, 25: 0, 26: 0, 27: 0, 28: 0, 29: 0, 30: 0, 31: -0.5,
                   32: -0.5, 33: 0, 34: 0, 35: 0, 36: 0, 37: 0, 38: 0, 39: -0.5, 40: -0.5, 41: 0, 42: 0, 43: 0, 44: 0, 45: 0, 46: 0, 47: -0.5, 48: -0.5, 49: 0, 50: 0, 51: 0, 52: 0, 53: 0, 54: 0, 55: -0.5, 56: 0, 57: 0, 58: 0, 59: 0.5, 60: 0.5, 61: 0, 62: 0, 63: 0}
WHITE_ROOK_DICT = {0: 0, 1: 0, 2: 0, 3: 0.5, 4: 0.5, 5: 0, 6: 0, 7: 0, 8: -0.5, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: -0.5, 16: -0.5, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: -0.5, 24: -0.5, 25: 0, 26: 0, 27: 0, 28: 0, 29: 0, 30: 0,
                   31: -0.5, 32: -0.5, 33: 0, 34: 0, 35: 0, 36: 0, 37: 0, 38: 0, 39: -0.5, 40: -0.5, 41: 0, 42: 0, 43: 0, 44: 0, 45: 0, 46: 0, 47: -0.5, 48: 0.5, 49: 1, 50: 1, 51: 1, 52: 1, 53: 1, 54: 1, 55: 0.5, 56: 0, 57: 0, 58: 0, 59: 0, 60: 0, 61: 0, 62: 0, 63: 0}

# * PAWN POS
BLACK_PAWN_DICT = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 5, 9: 5, 10: 5, 11: 5, 12: 5, 13: 5, 14: 5, 15: 5, 16: 1, 17: 1, 18: 2, 19: 3, 20: 3, 21: 2, 22: 1, 23: 1, 24: 0.5, 25: 0.5, 26: 1, 27: 2.5, 28: 2.5, 29: 1, 30: 0.5, 31: 0.5,
                   32: 0, 33: 0, 34: 0, 35: 2, 36: 2, 37: 0, 38: 0, 39: 0, 40: 0.5, 41: -0.5, 42: -1, 43: 0, 44: 0, 45: -1, 46: -0.5, 47: 0.5, 48: 0.5, 49: 1, 50: 1, 51: -2, 52: -2, 53: 1, 54: 1, 55: 0.5, 56: 0, 57: 0, 58: 0, 59: 0, 60: 0, 61: 0, 62: 0, 63: 0}
WHITE_PAWN_DICT = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0.5, 9: 1, 10: 1, 11: -2, 12: -2, 13: 1, 14: 1, 15: 0.5, 16: 0.5, 17: -0.5, 18: -1, 19: 0, 20: 0, 21: -1, 22: -0.5, 23: 0.5, 24: 0, 25: 0, 26: 0, 27: 2, 28: 2, 29: 0, 30: 0,
                   31: 0, 32: 0.5, 33: 0.5, 34: 1, 35: 2.5, 36: 2.5, 37: 1, 38: 0.5, 39: 0.5, 40: 1, 41: 1, 42: 2, 43: 3, 44: 3, 45: 2, 46: 1, 47: 1, 48: 5, 49: 5, 50: 5, 51: 5, 52: 5, 53: 5, 54: 5, 55: 5, 56: 0, 57: 0, 58: 0, 59: 0, 60: 0, 61: 0, 62: 0, 63: 0}

# * OUTCOME DICT
OUT_COME_DICT = {
    "1-0": "WHITE",
    "0-1": "BLACK",
    "draw": "DRAW"
}

MODEL_NAME = "model.pkl"
DATA_IN_CSV = "data.csv"


pieces_score_column = ["king_score", "queen_score", "rook_score", "bishop_score",
                       "knight_score",   "pawn_score"]

white_pieces_score = ["white_king", "white_queen", "white_rook", "white_bishop",
                      "white_knight",  "white_pawn", "white_captures"]
black_pieces_score = ["black_king", "black_queen", "black_rook", "black_bishop",
                      "black_knight",  "black_pawn", "black_captures"]
outcome = ["outcome"]

# creating enumerations using class


class ChessMLVisitor(chess.pgn.BaseVisitor):
    def visit_move(self, board, move):
        print(board.san(move))

    def result(self):
        return None


class GameNotationType(enum.Enum):
    pgn = "PGN"
    fen = "FEN"


class ChessMachineLearning():
    def __init__(self, fresh_run=False):
        self.X_train = None
        self.y_train = None
        self.X_test = None
        self.y_test = None
        self.model = None
        if not fresh_run:
            self.load_model()

    def is_black_side(self, piece: chess.Piece):
        return piece.color == chess.BLACK
    #  0  -  70
    #  1  - 71
    #  56 -  0
    #  57 - 1
    #  55 -  17

    # Old = row * 10 + col
    # New =
    def row_col_to_chess_square(self, row, col):
        new_row = (7 - row)
        new_col = col
        pgn_row = int(new_row * 8)
        pgn_col = new_col
        # print(f"row: {pgn_row} col: {pgn_col}")
        pgn_indx = pgn_row + pgn_col
        return pgn_indx

    def move_from_engine_to_pgn_move(self, move):
        startRow = move.startRow
        startCol = move.startCol
        endRow = move.endRow
        endCol = move.endCol

        start_square = self.row_col_to_chess_square(startRow, startCol)
        end_square = self.row_col_to_chess_square(endRow, endCol)
        print(
            f"\nConverted Start: ({startRow}, {startCol}) --> {start_square}")
        print(f"Converted End :({endRow}, {endCol}) --> {end_square}\n")
        return chess.Move(from_square=start_square, to_square=end_square)

    def transform_game_moves_to_pgn_moves(self, moves):
        return [self.move_from_engine_to_pgn_move(move) for move in moves]

    def is_white_side(self, piece):
        return piece.color == chess.WHITE

    def get_piece_score(self, piece: str):
        return piecesScore[self.get_piece_notation(piece)]

    def new_row_from_board(self, board, with_outcome=None):
        color = chess.WHITE
        result = with_outcome
        king_pos = board.pieces(chess.KING, color)
        queen_pos = board.pieces(chess.QUEEN, color)
        rook_pos = board.pieces(chess.ROOK, color)
        bishop_pos = board.pieces(chess.BISHOP, color)
        knight_pos = board.pieces(chess.KNIGHT, color)
        pawn = board.pieces(chess.PAWN, color)

        color = chess.BLACK

        black_king_pos = board.pieces(chess.KING, color)
        black_queen_pos = board.pieces(chess.QUEEN, color)
        black_rook_pos = board.pieces(chess.ROOK, color)
        black_bishop_pos = board.pieces(chess.BISHOP, color)
        black_knight_pos = board.pieces(chess.KNIGHT, color)
        black_pawn = board.pieces(chess.PAWN, color)
        new_data = {
            # white data
            "white_king":  sum(WHITE_KING_DICT[pos] for pos in king_pos) or 0,
            "white_queen": sum(WHITE_QUEEN_DICT[pos] for pos in queen_pos) or 0,
            "white_rook": sum(WHITE_ROOK_DICT[pos] for pos in rook_pos) or 0,
            "white_bishop": sum(WHITE_BISHOP_DICT[pos] for pos in bishop_pos) or 0,
            "white_knight": sum(WHITE_KNIGHT_DICT[pos] for pos in knight_pos) or 0,
            "white_pawn": sum(WHITE_PAWN_DICT[pos] for pos in pawn) or 0,

            # black data
            "black_king": sum(BLACK_KING_DICT[pos] for pos in black_king_pos) or 0,
            "black_queen": sum(BLACK_QUEEN_DICT[pos] for pos in black_queen_pos) or 0,
            "black_rook": sum(BLACK_ROOK_DICT[pos] for pos in black_rook_pos) or 0,
            "black_bishop": sum(BLACK_BISHOP_DICT[pos] for pos in black_bishop_pos) or 0,
            "black_knight": sum(BLACK_KNIGHT_DICT[pos] for pos in black_knight_pos) or 0,
            "black_pawn": sum(BLACK_PAWN_DICT[pos] for pos in black_pawn) or 0,
        }
        if with_outcome:
            new_data["outcome"] = result
        return new_data

    def get_piece_pos_val(self, piece_type: chess.PieceType, pos: tuple([int, int]), color: chess.Color):
        row, col = pos
        if color == chess.BLACK:
            row = 7 - row
        if piece_type == chess.KING:
            return KING_POS_VAL[row][col]
        elif piece_type == chess.QUEEN:
            return QUEEN_POS_VAL[row][col]
        elif piece_type == chess.KNIGHT:
            return KNIGHT_POS_VAL[row][col]
        elif piece_type == chess.BISHOP:
            return BISHOP_POS_VAL[row][col]
        elif piece_type == chess.PAWN:
            return PAWN_POS_VAL[row][col]
        else:
            raise RuntimeError("Weird piece tcolpe encountered")

    def score_piece(self, piece):
        if self.is_black_side(piece):
            return self.get_piece_pos_val(piece, pos)
        elif self.is_white_side(piece):
            return self.get_piece_pos_val(piece, pos)

    def learn_board(self, board: chess.Board):
        # Loop through pieces and collect theire score values
        pieces_locations: chess.SquareSet = None
        pieces_type = [chess.PAWN, chess.KNIGHT,
                       chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]
        pieces_color = [chess.BLACK, chess.WHITE]
        for color in pieces_color:
            for piece_type in pieces_type:
                pieces_locations = board.pieces(piece_type, color)

    def save_model(self):
        with open(MODEL_NAME, 'wb') as f:
            pickle.dump(self.model, f)

    # Get next move based on the model loaded
    # Return the move of the best next move from the original move_list
    def predict_next_move(self, move_list, board_fen):
        # update the probability

        # Calculate the probability of white wining
        if not self.model:
            print("Error: Model not loaded")
            return
        moves_transformed = self.transform_game_moves_to_pgn_moves(move_list)
        X_data = []
        board = chess.Board(fen=board_fen)
        for move in moves_transformed:
            board.push(move)
            print(f"Board\n {board}")
            print(f"Executing Move {move}")
            board.pop()
            X_data.append(self.new_row_from_board(board))

        X_data_frame_input = pd.DataFrame(X_data)
        # X_data_frame_input = X_data_frame_input.drop("outcome")
        print(f"Data input to model: {X_data_frame_input.head()}")
        # move_result_prob = self.model.predict_proba(X_data_frame_input)
        # * TESTING CODE
        class_proba = self.model.predict_proba(X_data_frame_input)
        np_white_class_proba = class_proba[:, 1]
        max_idx = np.argmax(np_white_class_proba)
        return move_list[max_idx]
        # Choose the move with the best posibility
    # Load the model from the last time trained

    def load_model(self):
        try:
            with open(MODEL_NAME, 'rb') as f:
                self.model = pickle.load(f)
        except EOFError:
            print("ERROR loading model")

    def update_model(self, csv_data_file=DATA_IN_CSV):
        from sklearn.model_selection import train_test_split
        from sklearn.naive_bayes import GaussianNB
        raw_data = pd.read_csv(DATA_IN_CSV, index_col=False)
        # data = raw_data.drop()
        # * Drop the index column
        df = raw_data.iloc[:, 1:]
        y = df['outcome'].values  # target
        X = df.drop(['outcome'], axis=1).values  # features

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y)
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test

        clf = GaussianNB()
        # fit it to training data
        clf.fit(X_train, y_train)
        self.model = clf

        self.save_model()
        # print("X data:", X[0:5])
        # print(X.shape)
        # # print(X.head())
        # print("y data: ",y)
        # print(y.shape)
        # print(y.head())
        # print(df.head())
    # * Cross validation for choosing the best alpha for Laplacian Smoothing:

    def model_cross_validation(self):
        list_alpha = np.arange(1/100000, 20, 0.11)
        print("Cross validating the model")
        score_train = np.zeros(len(list_alpha))
        score_test = np.zeros(len(list_alpha))
        recall_test = np.zeros(len(list_alpha))
        precision_test = np.zeros(len(list_alpha))
        count = 0
        X_train, y_train, X_test, y_test = (
            self.X_train, self.y_train, self.X_test, self.y_test)
        for alpha in list_alpha:
            bayes = naive_bayes.GaussianNB(var_smoothing=alpha)
            bayes.fit(X_train, y_train)
            score_train[count] = bayes.score(X_train, y_train)
            score_test[count] = bayes.score(X_test, y_test)
            recall_test[count] = metrics.recall_score(
                y_test, bayes.predict(X_test), average="weighted")
            precision_test[count] = metrics.precision_score(
                y_test, bayes.predict(X_test), average="weighted")
            count = count + 1
        print("Done, Showing the result: ")
        matrix = np.matrix(
            np.c_[list_alpha, score_train, score_test, recall_test, precision_test])
        models = pd.DataFrame(data=matrix, columns=[
                              'alpha', 'Train Accuracy', 'Test Accuracy', 'Test Recall', 'Test Precision'])
        print(models.head(n=10))

        # Best alpha to use is:
        print("Best alpha value is: ")
        best_index = models[models['Test Precision']
                            >= 0.5]['Test Accuracy'].idxmax()
        bayes = naive_bayes.GaussianNB(var_smoothing=list_alpha[best_index])
        bayes.fit(X_train, y_train)
        print(models.iloc[best_index, :])

    def preprocessing_game_file(self, game_file_path=None, type: GameNotationType = GameNotationType.pgn):
        pgn_path = game_file_path if game_file_path else os.path.join(
            os.path.curdir, "chess_dataset", "Carlsen.pgn")
        print(f"Processing File: {pgn_path}")
        pgn_file = open(pgn_path)
        num_of_game = 0
        df = pd.read_csv(DATA_IN_CSV)
        while True:
            game_to_learn = chess.pgn.read_game(pgn_file)
            board = game_to_learn.board()
            outcome = board.outcome()
            result = game_to_learn.headers["Result"]
            # print("HEADERS: ", game_to_learn.headers["Result"])

            num_of_game = num_of_algame + 1
            if not game_to_learn:
                print("Done Processing")
                print("Data Saved in " + DATA_IN_CSV)
                return
            for move in game_to_learn.mainline_moves():
                # Make move
                board.push(move)
                new_data = self.new_row_from_board(board, with_outcome=result)
                new_df = pd.DataFrame([new_data])
                df = pd.concat([df, new_df], axis=0, ignore_index=True)

            print(f"Iteration: {num_of_game} ")
            df.to_csv(DATA_IN_CSV)

    def learn_batch_of_game(self, batch_file):
        pass

    # Add new data to the game model: (use for self traning)
    def update_model_from_game(self, move_log, game_result):
        pass


if __name__ == "__main__":
    pgn_path = os.path.join(os.path.curdir, "chess_dataset", "test_2.pgn")
    chess_ml = ChessMachineLearning(fresh_run=True)
    # chess_ml.preprocessing_game_file(game_file_path=pgn_path)
    chess_ml.update_model(csv_data_file=DATA_IN_CSV)
    # chess_ml.model_cross_validation()
