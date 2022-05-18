from ChessTypes import PiecePosTuple, MoveTuple, EMPTY_CELL, WHITE_PIECE_PREFIX, BLACK_PIECE_PREFIX, \
    ROOK_PIECE, BISHOP_PIECE, PAWN_PIECE, QUEEN_PIECE, KING_PIECE, KNIGHT_PIECE


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    # maps keys to values:
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}
    UNICODE_PIECES = {
        'bR': '♜', 'bN': '♞', 'bB': '♝', 'bQ': '♛',
        'bK': '♚', 'bp': '♟', 'wR': '♖', 'wN': '♘',
        'wB': '♗', 'wQ': '♕', 'wK': '♔', 'wp': '♙',
        '--': ''
    }

    # Typing declarations:
    startRow: int
    startCol: int
    endRow: int
    endCol: int
    pieceMoved: str
    pieceCaptured: str
    isEnPassantMove: bool
    modeID: float
    isCastleMove: bool

    def __init__(self, startSq, endSq, board, isEnPassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # en passant
        self.isEnPassantMove = isEnPassantMove
        if self.isEnPassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        self.modeID = self.startRow * 1000 + self.startCol * \
            100 + self.endRow * 10 + self.endCol
        self.isCastleMove = isCastleMove

    '''Override'''

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.modeID == other.modeID
        return False

    def getChessNotation(self):
        from ChessHelper import ChessHelper
        piece_key = ChessHelper.get_piece_side_and_type(self.pieceMoved)
        return self.UNICODE_PIECES[piece_key] + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]


ORIGINAL_BLACK_PIECES = ['bR1', 'bN1', 'bB1', 'bQ', 'bK', 'bB2', 'bN2', 'bR2', 'bp1', 'bp2', 'bp3', 'bp4', 'bp5', 'bp6',
                         'bp7', 'bp8']

ORIGINAL_WHITE_PIECES = ['wp1', 'wp2', 'wp3', 'wp4', 'wp5', 'wp6', 'wp7', 'wp8', 'wR1', 'wN1', 'wB1', 'wQ', 'wK', 'wB2',
                         'wN2', 'wR2']

ORIGINAL_BLACK_PIECES_SET = {'bR1', 'bN1', 'bB1', 'bQ', 'bK', 'bB2', 'bN2', 'bR2', 'bp1',
                             'bp2', 'bp3', 'bp4', 'bp5', 'bp6',
                             'bp7', 'bp8'}

ORIGINAL_WHITE_PIECES_SET = {'wp1', 'wp2', 'wp3', 'wp4', 'wp5', 'wp6', 'wp7', 'wp8', 'wR1', 'wN1', 'wB1', 'wQ', 'wK',
                             'wB2',
                             'wN2', 'wR2'}

# Sets for fast checking draw by insufficient materials:
KING_VS_KING = {('bK', 'wK')}
KING_BISHOP_VS_KING = {('bK', 'wB', 'wK'), ('wK', 'bB', 'bK')}
KING_KNIGHT_VS_KING = {('bK', 'wN', 'wK'), ('wK', 'bN', 'bK')}
KING_BISHOP_VS_KING_BISHOP = {('bK', 'bB', 'wB', 'wK')}


class GameState:
    def __init__(self):

        # self.color = randint(0,1)
        self.board = [
            ['bR1', 'bN1', 'bB1', 'bQ', 'bK', 'bB2', 'bN2', 'bR2'],
            ['bp1', 'bp2', 'bp3', 'bp4', 'bp5', 'bp6', 'bp7', 'bp8'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp1', 'wp2', 'wp3', 'wp4', 'wp5', 'wp6', 'wp7', 'wp8'],
            ['wR1', 'wN1', 'wB1', 'wQ', 'wK', 'wB2', 'wN2', 'wR2'],
        ]

        # if self.color == 1:
        #     self.board = [
        #         ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
        #         ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
        #         ['--', '--', '--', '--', '--', '--', '--', '--'],
        #         ['--', '--', '--', '--', '--', '--', '--', '--'],
        #         ['--', '--', '--', '--', '--', '--', '--', '--'],
        #         ['--', '--', '--', '--', '--', '--', '--', '--'],
        #         ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
        #         ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR']]

        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'K': self.getKingMoves, 'Q': self.getQueenMoves}
        self.whiteToMove = True  # White turn or not
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.promotionDone = True
        # coordinates for the square where en passant capture is possible
        self.enPassantPossible = ()
        self.enPassantPossibleLog = [self.enPassantPossible]
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]
        # Game Ending Flags: To know which outcome happened
        self.checkmate = False
        self.stalemate = False
        self.draw_by_insufficent_material = False
        # Keep track of the captured pieces for game draw checking
        self.blackCapturedPieces = []
        self.whiteCapturedPieces = []

        # Alive pieces on the board
        self.alive_pieces_dict = self.get_alive_pieces_dict()
        # Seed to mark the pieces as promoted
        self.promotion_seed = 3

    # Self helper method
    def check_game_ended(self):
        return self.stalemate or self.checkmate or self.draw_by_insufficent_material

    # Note: Expensive calculation, should be used sparingly
    # Return: example: [ ('wK', (1,1)) , ('bK', (2,2)) ]
    def get_alive_pieces_with_pos(self) -> list[PiecePosTuple]:
        piece_pos_list = []
        for (row_index, row) in enumerate(self.board):
            for (col_index, cell) in enumerate(row):
                from ChessHelper import ChessHelper
                if not ChessHelper.is_empty_cell(self.get_pos_value((row_index, col_index))):
                    piece_pos_tuple = (cell, (row_index, col_index))
                    piece_pos_list.append(piece_pos_tuple)
        return piece_pos_list

    def get_alive_pieces_set(self) -> list[str]:
        pass

    # Note: Expensive calculation, should be used sparingly
    def get_alive_pieces_dict(self) -> dict[str, MoveTuple]:
        piece_pos_dict = {}
        for (row_index, row) in enumerate(self.board):
            for (col_index, cell) in enumerate(row):
                from ChessHelper import ChessHelper
                if not ChessHelper.is_empty_cell(cell):
                    piece_pos_dict[cell] = (row_index, col_index)
        return piece_pos_dict

    def get_white_alive_pieces(self) -> list[str]:
        return list(ORIGINAL_WHITE_PIECES_SET.difference(self.whiteCapturedPieces))

    def get_black_alive_pieces(self) -> list[str]:
        return list(ORIGINAL_BLACK_PIECES_SET.difference(self.blackCapturedPieces))

    # https://en.wikipedia.org/wiki/Draw_(chess)
    def check_for_insufficient_material(self) -> bool:
        num_of_white_captured = len(self.whiteCapturedPieces)
        num_of_black_captured = len(self.blackCapturedPieces)
        total_alive_pieces = 32 - num_of_black_captured - num_of_white_captured
        # Draw of this type only happen when there are at most 32 - 28 = 4 pieces left
        if total_alive_pieces < 28:
            return False

        # check for 2 at most each side: avoid 3 - 1 case
        elif total_alive_pieces <= 4 and num_of_black_captured <= 2 and num_of_white_captured <= 2:
            white_alive_pieces = self.get_white_alive_pieces()
            black_alive_pieces = self.get_black_alive_pieces()

            alive_pieces = white_alive_pieces + black_alive_pieces
            alive_pieces_tuple = tuple(alive_pieces)
            if alive_pieces_tuple in KING_VS_KING:
                return True
            if alive_pieces_tuple in KING_BISHOP_VS_KING:
                return True
            if alive_pieces_tuple in KING_KNIGHT_VS_KING:
                return True
            if alive_pieces_tuple in KING_BISHOP_VS_KING_BISHOP:
                current_alive_pieces_with_pos = self.get_alive_pieces_with_pos()
                from ChessHelper import ChessHelper
                bishop_piece_pos_list = [item for item in current_alive_pieces_with_pos if
                                         ChessHelper.is_bishop_piece_pos(item)]
                if len(bishop_piece_pos_list) != 2:
                    raise TypeError(
                        "This should contain exactly two Bishop piecepos")
                first_bishop_pos = bishop_piece_pos_list[0][1]
                second_bishop_pos = bishop_piece_pos_list[1][1]
                both_black_square = ChessHelper.is_black_square(first_bishop_pos) and ChessHelper.is_black_square(
                    second_bishop_pos)
                both_white_square = ChessHelper.is_white_square(first_bishop_pos) and ChessHelper.is_white_square(
                    second_bishop_pos)
                return both_white_square or both_black_square
                # Only draw if both bishop are both black or both white squared

        return False

    def get_pos_value(self, pos: MoveTuple):
        row, col = pos
        return self.board[row][col]

    def capture_piece(self, pos: MoveTuple):
        piece_value = self.get_pos_value(pos)
        from ChessHelper import ChessHelper
        if not ChessHelper.is_empty_cell(pos):
            self.alive_pieces_dict.pop(piece_value)

    def erase_piece_at_pos(self, pos: MoveTuple):
        row, col = pos
        board_value = self.get_pos_value(pos)
        from ChessHelper import ChessHelper
        if not ChessHelper.is_empty_cell(board_value):
            if ChessHelper.is_white_piece(board_value):
                self.whiteCapturedPieces.append(board_value)
            else:
                self.blackCapturedPieces.append(board_value)
        self.board[row][col] = EMPTY_CELL
        # self.alive_pieces_dict[]

    def makeMove(self, move: Move):
        # Object destructuring: Need double-check if this is correct
        startCol, startRow, endRow, endCol, pieceMoved = move.startCol, move.startRow, move.endRow, move.endCol, move.pieceMoved
        self.erase_piece_at_pos((startRow, startCol))
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        # update King's location if moved
        from ChessHelper import ChessHelper
        if ChessHelper.is_white_king(pieceMoved):
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif ChessHelper.is_black_king(pieceMoved):
            self.blackKingLocation = (move.endRow, move.endCol)
        # Pawn promotion
        elif ChessHelper.is_white_pawn(pieceMoved) and endRow == 0:
            self.eR, self.eC, self.sR, self.sC = move.endRow, move.endCol, move.startRow, move.startCol
            self.promotionDone = False
        elif ChessHelper.is_black_pawn(pieceMoved) and endRow == 7:
            self.eR, self.eC, self.sR, self.sC = move.endRow, move.endCol, move.startRow, move.startCol
            self.promotionDone = False
        # update en passant possible
        if ChessHelper.is_pawn_piece(pieceMoved) and abs(startRow - endRow) == 2:
            # print((move.startRow + move.endRow) // 2, move.startCol)
            self.enPassantPossible = (
                (startRow + endRow) // 2, startCol)
        else:
            self.enPassantPossible = ()
        # En Passant move
        if move.isEnPassantMove:
            self.erase_piece_at_pos((startRow, endCol))
            # caslte move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # king side
                self.board[move.endRow][move.endCol -
                                        1] = self.board[move.endRow][move.endCol + 1]  # move rook
                # self.board[move.endRow][move.endCol + 1] = '--'  # erase old rook
                self.erase_piece_at_pos((endRow, endCol + 1))
            else:  # queen side
                self.board[move.endRow][move.endCol +
                                        1] = self.board[move.endRow][move.endCol - 2]  # move rook
                # self.board[move.endRow][move.endCol - 2] = '--'  # erase old rook
                self.erase_piece_at_pos((endRow, endCol - 2))

        self.enPassantPossibleLog.append(self.enPassantPossible)

        # update castling rights when a rook/ a king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

        # Check for draw by insufficient material
        self.draw_by_insufficent_material = self.check_for_insufficient_material()

        print(f'Moved: {move.pieceMoved} to ({move.endRow},{move.endCol})')

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            pieceMoved = move.pieceMoved
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            # update King's location if moved
            from ChessHelper import ChessHelper
            if ChessHelper.is_white_king(pieceMoved):
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif ChessHelper.is_black_king(pieceMoved):
                self.blackKingLocation = (move.startRow, move.startCol)
            # en passant
            if move.isEnPassantMove:
                # leave landing square blank
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured
            self.enPassantPossibleLog.pop()
            self.enPassantPossible = self.enPassantPossibleLog[-1]
            # undo castling rights
            self.castleRightsLog.pop()  # get rid of the new satle rights from the move we undo
            # set the current CR to the last one in list
            self.currentCastlingRight = self.castleRightsLog[-1]
            # undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # king side
                    self.board[move.endRow][move.endCol +
                                            1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:  # queen side
                    self.board[move.endRow][move.endCol -
                                            2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'
            self.checkmate = False
            self.stalemate = False

    def updateCastleRights(self, move):
        pieceMoved = move.pieceMoved
        from ChessHelper import ChessHelper
        if ChessHelper.is_white_king(pieceMoved):
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif ChessHelper.is_black_king(pieceMoved):
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif ChessHelper.is_white_rook(pieceMoved):
            if move.startRow == 7:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRight.wks = False
        elif ChessHelper.is_black_rook(pieceMoved):
            if move.startRow == 0:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRight.bks = False
        elif move.pieceMoved[0] == WHITE_PIECE_PREFIX and move.endRow == 0:
            if move.endCol == 0:
                self.currentCastlingRight.bqs = False
            elif move.endCol == 7:
                self.currentCastlingRight.bks = False
        elif move.pieceMoved[0] == BLACK_PIECE_PREFIX and move.endRow == 7:
            if move.endCol == 7:
                self.currentCastlingRight.wqs = False
            elif move.endCol == 0:
                self.currentCastlingRight.wks = False

    '''
    All moves considering checks
    '''

    def getValidMoves(self):
        moves = []
        tempEnPassantPossible = self.enPassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1:  # Only 1 check, block check or move king
                moves = self.getAllPossibleMoves()
                # To block a check, must move a piece into one of the square between the enemy piece an king
                check = self.checks[0]  # check information
                checkRow = check[0]
                checkCol = check[1]
                # enemy piece causing the check
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []  # squares the pieces can move to
                # if knight, must capture knight or move king, other piece can block
                from ChessHelper import ChessHelper
                if ChessHelper.is_knight_piece(pieceChecking):
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (
                            kingRow + check[2] * i,
                            kingCol + check[3] * i)  # check[2], check[3] are the check directions
                        validSquares.append(validSquare)
                        # get to piece end checks
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                # get rid of any moves that don't block check or move king
                # go through backwards when removing a list as iterating
                for i in range(len(moves) - 1, -1, -1):
                    # move doesn't move king so it must block or capture
                    if ChessHelper.is_king_piece(moves[i].pieceMoved):
                        if not (moves[i].endRow,
                                moves[i].endCol) in validSquares:  # move doesn't block check or capture piece
                            moves.remove(moves[i])
            else:  # double check, king has to move
                self.getKnightMoves(kingRow, kingCol, moves)
        else:  # not in check so all moves are fine
            moves = self.getAllPossibleMoves()
        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True
        if self.whiteToMove:
            self.getCastleMoves(
                self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(
                self.blackKingLocation[0], self.blackKingLocation[1], moves)
        self.enPassantPossible = tempEnPassantPossible
        self.currentCastlingRight = tempCastleRights
        return moves

    '''
    Determine if the current player is in check
    '''

    # def inCheck(self):
    #     if self.whiteToMove:
    #         return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
    #     else:
    #         return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])
    #
    '''
    determine if the enemy can attack the square r, c
    '''

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    '''
    All moves without considering checks
    '''

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == WHITE_PIECE_PREFIX and self.whiteToMove) or (
                        turn == BLACK_PIECE_PREFIX and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        return moves

    '''
    Get all the pawn moves for the pawn located at row, col and add these moves to the list
    '''

    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        if self.whiteToMove:
            if r > 0:
                if self.board[r - 1][c] == '--':
                    if not piecePinned or pinDirection == (-1, 0):
                        moves.append(Move((r, c), (r - 1, c), self.board))
                        if r == 6 and self.board[r - 2][c] == '--':
                            moves.append(Move((r, c), (r - 2, c), self.board))
                # captures
                if c - 1 >= 0:  # capture left
                    if self.board[r - 1][c - 1][0] == BLACK_PIECE_PREFIX:
                        if not piecePinned or pinDirection == (-1, -1):
                            moves.append(
                                Move((r, c), (r - 1, c - 1), self.board))
                    elif (r - 1, c - 1) == self.enPassantPossible:
                        if not piecePinned or pinDirection == (-1, -1):
                            moves.append(
                                Move((r, c), (r - 1, c - 1), self.board, True))
                if c + 1 <= 7:  # capture right
                    if self.board[r - 1][c + 1][0] == BLACK_PIECE_PREFIX:
                        if not piecePinned or pinDirection == (-1, 1):
                            moves.append(
                                Move((r, c), (r - 1, c + 1), self.board))
                    elif (r - 1, c + 1) == self.enPassantPossible:
                        if not piecePinned or pinDirection == (-1, 1):
                            moves.append(
                                Move((r, c), (r - 1, c + 1), self.board, True))
        else:
            if r < 7:
                if self.board[r + 1][c] == '--':
                    if not piecePinned or pinDirection == (1, 0):
                        moves.append(Move((r, c), (r + 1, c), self.board))
                        if r == 1 and self.board[r + 2][c] == '--':
                            moves.append(Move((r, c), (r + 2, c), self.board))
                # captures
                if c - 1 >= 0:  # capture left
                    # print((r + 1, c - 1))
                    if self.board[r + 1][c - 1][0] == WHITE_PIECE_PREFIX:
                        if not piecePinned or pinDirection == (1, -1):
                            moves.append(
                                Move((r, c), (r + 1, c - 1), self.board))
                    elif (r + 1, c - 1) == self.enPassantPossible:
                        if not piecePinned or pinDirection == (1, -1):
                            moves.append(
                                Move((r, c), (r + 1, c - 1), self.board, True))
                if c + 1 <= 7:  # capture right
                    if self.board[r + 1][c + 1][0] == WHITE_PIECE_PREFIX:
                        if not piecePinned or pinDirection == (1, 1):
                            moves.append(
                                Move((r, c), (r + 1, c + 1), self.board))
                    elif (r + 1, c + 1) == self.enPassantPossible:
                        if not piecePinned or pinDirection == (1, 1):
                            moves.append(
                                Move((r, c), (r + 1, c + 1), self.board, True))

    '''
    Get all the rook moves for the rook located at row, col and add these moves to the list
    '''

    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][
                        1] != 'Q':  # can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = BLACK_PIECE_PREFIX if self.whiteToMove else WHITE_PIECE_PREFIX
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--':  # empty space valid
                            moves.append(
                                Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:  # enemy piece valid
                            moves.append(
                                Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # ally piece invalid
                            break
                else:  # off board
                    break

    '''
    Get all the knight moves for the knight located at row, col and add these moves to the list
    '''

    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = WHITE_PIECE_PREFIX if self.whiteToMove else BLACK_PIECE_PREFIX
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:  # not an ally piece
                        moves.append(
                            Move((r, c), (endRow, endCol), self.board))

    '''
    Get all the bishop moves for the bishop located at row, col and add these moves to the list
    '''

    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = BLACK_PIECE_PREFIX if self.whiteToMove else WHITE_PIECE_PREFIX
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--':  # empty space valid
                            moves.append(
                                Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:  # enemy piece valid
                            moves.append(
                                Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # ally piece valid
                            break
                else:
                    break

    '''
    Get all the queen moves for the queen located at row, col and add these moves to the list
    '''

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    '''
    Calculate the heuristics values for alpha beta pruning
    '''

    # TODO: This function should check if their is one wining side or a draw game
    # ! Problem: We dont have data structure to keep tracks of pieces on the board :((
    def getScoreBoardValue(self):
        if self.check_game_ended():
            if self.checkmate:
                # IF white being checkmated return high values else return small value
                return 1000
            elif self.stalemate or self.draw_by_insufficent_material:
                return 0
        else:
            # Calculate heuristic value
            return 0

    '''
    Get all the king moves for the king located at row, col and add these moves to the list
    '''

    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = WHITE_PIECE_PREFIX if self.whiteToMove else BLACK_PIECE_PREFIX
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # Not an ally piece
                    # place king in end square and check for checks
                    if allyColor == WHITE_PIECE_PREFIX:
                        row, col = self.whiteKingLocation[0], self.whiteKingLocation[1]
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        row, col = self.blackKingLocation[0], self.blackKingLocation[1]
                        self.blackKingLocation = (endRow, endCol)
                    print(f"DEBUG::ERASE_WEIRD::CALLED {row} {col}")
                    # self.board[row][col] = '--'
                    inChecks, pins, checks = self.checkForPinsAndChecks()
                    from ChessHelper import ChessHelper
                    if allyColor == WHITE_PIECE_PREFIX:
                        ChessHelper.is_white_king(
                            self.get_pos_value((row, col)))
                    else:
                        ChessHelper.is_black_king(
                            self.get_pos_value((row, col)))
                    if not inChecks:
                        moves.append(
                            Move((r, c), (endRow, endCol), self.board))
                    # place king back on original location
                    if allyColor == WHITE_PIECE_PREFIX:
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)
        # self.getCastleMoves(r, c, moves, allyColor)

    def pawnPromotion(self, char):
        piece_promoted_to = WHITE_PIECE_PREFIX + \
            char if self.whiteToMove else BLACK_PIECE_PREFIX + char

        self.board[self.eR][self.eC] = piece_promoted_to + self.promotion_seed
        self.promotion_seed = self.promotion_seed + 1

        self.board[self.sR][self.sC] = '--'
        self.promotionDone = True
        self.whiteToMove = not self.whiteToMove

    '''
    Generate all valid castle moves for the king at (r, c) and add them to the list of moves
    '''

    def getCastleMoves(self, r, c, moves):
        # if is check, can't castling
        if self.squareUnderAttack(r, c):
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or (
                not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingSideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (
                not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueenSideCastleMoves(r, c, moves)

    def getKingSideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                moves.append(
                    Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueenSideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(
                    Move((r, c), (r, c - 2), self.board, isCastleMove=True))

    def checkForPinsAndChecks(self):
        pins = []  # Squares where the allied pinned piece is and direction pinned from
        checks = []  # Squares where enemy is applying a check
        inCheck = False
        if self.whiteToMove:
            enemyColor = BLACK_PIECE_PREFIX
            allyColor = WHITE_PIECE_PREFIX
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = WHITE_PIECE_PREFIX
            allyColor = BLACK_PIECE_PREFIX
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        # Check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            dir = directions[j]
            possiblePin = ()  # reset possible pins
            for i in range(1, 8):
                endRow = startRow + dir[0] * i
                endCol = startCol + dir[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor:
                        if possiblePin == ():  # 1st allied piece could be pinned
                            possiblePin = (endRow, endCol, dir[0], dir[1])
                        else:  # 2nd allied piece, so no pin or check possible in this direction
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        # 5 possibilities in this conditional
                        # 1. orthogonally away from king and piece is a rook
                        # 2. diagonally away from king and piece is a bishop
                        # 3. 1 square away diagonally from king and piece is a pawn
                        # 4. any direction and piece is a queen
                        # 5. any direction 1 square away and piece is a king (prevent king to move to a square controlled by another king)
                        if (0 <= j <= 3 and type == ROOK_PIECE) or \
                                (4 <= j <= 7 and type == BISHOP_PIECE) or \
                                (i == 1 and type == PAWN_PIECE and (
                                    (enemyColor == WHITE_PIECE_PREFIX and 6 <= j <= 7) or (
                                        enemyColor == BLACK_PIECE_PREFIX and 4 <= j <= 5))) or \
                                (type == QUEEN_PIECE) or (i == 1 and type == KING_PIECE):
                            if possiblePin == ():  # no piece blocking, so check
                                inCheck = True
                                checks.append((endRow, endCol, dir[0], dir[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else:  # Enemy piece not applying check
                            break
                else:
                    break
        # Check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                # enemy knight attacking king
                if endPiece[0] == enemyColor and endPiece[1] == KNIGHT_PIECE:
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks
