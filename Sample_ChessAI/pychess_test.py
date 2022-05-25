import pandas as pd
import numpy as np
import chess.pgn
import os
# ? Can use to read game continually until detecting NoneType in the game read (reaching end of file)

""" Visitor based move visiting  """


class PrintMovesVisitor(chess.pgn.BaseVisitor):
    def visit_move(self, board, move):
        print(board.san(move))

    def result(self):
        return None


class ChessMLVisitor(chess.pgn.BaseVisitor):
    def visit_move(self, board, move):
        print(board.san(move))

    def result(self):
        return None


pgn_path = os.path.join(os.path.curdir, "chess_dataset", "Carlsen.pgn")

pgn_file = open(pgn_path)

# first_game = chess.pgn.read_game(pgn_file, Visitor=ChessMLVisitor)
# # second_game = chess.pgn.read_game(pgn_file)

# print(f"First game header: {first_game.headers}")
# print(f"second game header: {second_game.headers}")

""" Iterator based game visiting """
# test_game = chess.pgn.read_game(pgn_file)

# board = test_game.board()

# for move in test_game.mainline_moves():
#     print(f"Move found is: {move}")
#     board.push(move)
#     print(f"\nCurrent board is:\n {board}")


# print(f"\n Last board: \n {board}")
# * Do something to current game state:

# score_dict = {}
# score_dict[chess.A1] = 12
# print(f"Score dict is : {score_dict}")


"""
    Extracting dictionary from list for faster scoring
"""
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
    [-1, 0, 0.5, 1, 1, 0.5, 0, -1],
    [-1, 1, 1, 1, 1, 1, 1, -1],
    [-2, -1, -1, -1, -1, -1, -1, -2]
]

KNIGHT_POS_VAL = [
    [-5, -4, -3, -3, -3, -3, -4, -5],
    [-4, -2, 0, 0, 0, 0, -2, -4],
    [-3, 0, 1, 1.5, 1.5, 1, 0, -3],
    [-3, 0.5, 1.5, 2, 2, 1.5, 0.5, -3],
    [-3, 0.5, 1, 1.5, 1.5, 1, 0.5, -3],
    [-3, 0, 1, 1.5, 1.5, 1, 0, -3],
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


def get_row_col_from_square(pos):
    col = pos % 8
    row = 7 - (int)(pos / 8)
    return (row, col)


# for pos in chess.SQUARES:
#     row, col = get_row_col_from_square(pos)
    # print(
    #     f'Square {chess.square_name(pos)} at  {pos} converted to: {get_row_col_from_square(pos)} with values {KING_POS_VAL[row][col]}')

def convert_olr_pos_list_to_dict(old_list):
    white_dict = {}
    black_dict = {}
    for pos in chess.SQUARES:
        row, col = get_row_col_from_square(pos)
        black_row, black_col = (7 - row, col)
        white_value = old_list[row][col]
        black_value = old_list[black_row][black_col]
        white_dict[pos] = white_value
        black_dict[pos] = black_value
    print(f"Black dict is: {black_dict} \n\n")
    print(f"white dict is: {white_dict}")


# POS_LIST = [KING_POS_VAL, QUEEN_POS_VAL, KNIGHT_POS_VAL,
#             BISHOP_POS_VAL, ROOK_POS_VAL, PAWN_POS_VAL]


# for index, item in enumerate(POS_LIST):
#     print(f"\n\nCONVERTING {index} \n\n")
#     try:
#         convert_olr_pos_list_to_dict(item)
#         print(f"\n\nDONE: {item}\n\n")
#     except IndexError as e:
#         print(f"WTFFFFFFF: {e.args}")


"""
    Init and preprocessing data with numpy and pandas
"""

pieces_score_column = ["king_score", "queen_score", "rook_score", "bishop_score",
                       "knight_score",   "pawn_score"]

white_pieces_score = ["white_king", "white_queen", "white_rook", "white_bishop",
                      "white_knight",  "white_pawn", "white_captures"]
black_pieces_score = ["black_king", "black_queen", "black_rook", "black_bishop",
                      "black_knight",  "black_pawn", "black_captures"]
outcome = ["outcome"]
# p(C | X) = p(C) * p (X | C)
columns_label_list = [pieces_score_column,
                      white_pieces_score, black_pieces_score, outcome]


columns = [item for list_label in columns_label_list for item in list_label]

sample_row1 = [900, 90, 50, 30, 30, 10, 0, 0,
               0, 0, 0, 0, 100, 0, 0, 0, 0, 0, 0, 100, "1-0"]

sample_row2 = [900, 90, 50, 30, 30, 10, 0, 0,
               0, 0, 0, 0, 100, 0, 0, 0, 0, 0, 0, 100, "1-0"]
init_data = np.array([sample_row1, sample_row2])
init_df = pd.DataFrame(data=init_data, columns=columns)
init_df.to_csv("test_data.csv")
print(init_df)
