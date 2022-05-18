from Sample_ChessAI.ChessEngine import GameState
from Sample_ChessAI.ChessTypes import EMPTY_CELL, WHITE_PIECE_PREFIX, MoveTuple, BLACK_PIECE_PREFIX, PiecePosTuple, \
    KNIGHT_PIECE, QUEEN_PIECE, PAWN_PIECE, KING_PIECE, BISHOP_PIECE, ROOK_PIECE


def is_even(x: int):
    return x % 2 == 0


class ChessHelper():
    @classmethod
    def is_capture_move(cls):
        pass

    @classmethod
    def is_empty_cell(cls, pos_value: str) -> bool:
        return pos_value == EMPTY_CELL

    @classmethod
    def is_occupied_py_a_piece(cls, pos_value: str) -> bool:
        return not cls.is_empty_cell(pos_value)

    @classmethod
    def get_piece_side(cls, pos_value: str):
        return pos_value[0]

    @classmethod
    def is_white_piece(cls, pos_value: str) -> bool:
        return cls.get_piece_side(pos_value) == WHITE_PIECE_PREFIX

    @classmethod
    def is_black_piece(cls, pos_value: str) -> bool:
        return cls.get_piece_side(pos_value) == BLACK_PIECE_PREFIX

    @classmethod
    def is_white_turn(cls, game_state: GameState) -> bool:
        pass

    # from the current pos of a bishop pieces: Check if it is a white squared or black squared one
    @classmethod
    def is_white_square(cls, pos: MoveTuple) -> bool:
        row, col = pos
        x = col + 1
        y = row + 1
        return (is_even(x) and is_even(y)) or (not is_even(x) and not is_even(y))

    @classmethod
    def is_black_square(cls, pos: MoveTuple) -> bool:
        return not cls.is_white_square(pos)

    @classmethod
    def get_piece_from_piece_pos(cls, piece_pos: PiecePosTuple):
        return piece_pos[0]

    @classmethod
    def is_bishop_piece_pos(cls, piece_pos: PiecePosTuple) -> bool:
        piece = cls.get_piece_from_piece_pos(piece_pos)
        return cls.is_bishop_piece(piece)

    @classmethod
    def get_piece_type(cls, piece_value: str):
        return piece_value[1]

    @classmethod
    def is_bishop_piece(cls, piece_value: str):
        return cls.get_piece_type(piece_value) == BISHOP_PIECE

    @classmethod
    def is_rook_piece(cls, piece_values: str):
        return cls.get_piece_type(piece_values) == ROOK_PIECE

    @classmethod
    def is_knight_piece(cls, piece_values: str):
        return cls.get_piece_type(piece_values) == KNIGHT_PIECE

    @classmethod
    def is_queen_piece(cls, piece_values: str):
        return cls.get_piece_type(piece_values) == QUEEN_PIECE

    @classmethod
    def is_pawn_piece(cls, piece_values: str):
        return cls.get_piece_type(piece_values) == PAWN_PIECE

    @classmethod
    def is_king_piece(cls, piece_values: str):
        return cls.get_piece_type(piece_values) == KING_PIECE

    @classmethod
    def get_piece_side_and_type(cls, piece_value: str):
        return piece_value[:2]

    @classmethod
    def is_white_king(cls, piece_value: str):
        return cls.is_white_piece(piece_value) and cls.is_king_piece(piece_value)

    @classmethod
    def is_black_king(cls, piece_value: str):
        return cls.is_black_piece(piece_value) and cls.is_king_piece(piece_value)

    @classmethod
    def is_white_pawn(cls, piece_value: str):
        return cls.is_white_piece(piece_value) and cls.is_pawn_piece(piece_value)

    @classmethod
    def is_black_pawn(cls, piece_value: str):
        return cls.is_black_piece(piece_value) and cls.is_pawn_piece(piece_value)

    @classmethod
    def is_white_rook(cls, piece_value: str):
        return cls.is_white_piece(piece_value) and cls.is_rook_piece(piece_value)

    @classmethod
    def is_black_rook(cls, piece_value: str):
        return cls.is_black_piece(piece_value) and cls.is_rook_piece(piece_value)
