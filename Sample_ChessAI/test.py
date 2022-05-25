# import chess.pgn
# import os


# class ChessMLVisitor(chess.pgn.BaseVisitor):
#     def visit_move(self, board, move):
#         print(board.san(move))

#     def result(self):
#         return None


# pgn_path = os.path.join(os.path.curdir, "chess_dataset", "Carlsen.pgn")

# pgn_file = open(pgn_path)

# first_game = chess.pgn.read_game(pgn_file, Visitor=ChessMLVisitor)
# # second_game = chess.pgn.read_game(pgn_file)

# for move in game.mainline_moves():
#     print(f"Move found is: {move}")
#     board.push(move)
#     print(f"\nCurrent board is:\n {board}")


# print('Hello, world!')


from ChessHelper import *


def row_col_to_chess_square(row, col):
    new_row = (7 - row)
    new_col = col
    pgn_row = int(new_row * 8)
    pgn_col = new_col
    print(f"row: {pgn_row} col: {pgn_col}")
    pgn_indx = pgn_row + pgn_col
    return pgn_indx


# print(row_col_to_chess_square(6, 5))
board = [
    ['bR1', 'bN1', 'bB1', 'bQ', 'bK', 'bB2', 'bN2', 'bR2'],
    ['bp1', 'bp2', 'bp3', 'bp4', 'bp5', 'bp6', 'bp7', 'bp8'],
    ['--', '--', '--', '--', '--', '--', '--', '--'],
    ['--', '--', '--', '--', '--', '--', '--', '--'],
    ['--', '--', '--', '--', '--', '--', '--', '--'],
    ['--', '--', '--', '--', '--', 'wK', '--', '--'],
    ['wp1', 'wp2', 'wp3', 'wp4', 'wp5', 'wp6', 'wp7', 'wp8'],
    ['wR1', 'wN1', 'wB1', 'wQ', '--', 'wB2', 'wN2', 'wR2'],
]

print("BOARD: " + ChessHelper.board_to_fen(board))
