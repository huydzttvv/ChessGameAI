import pygame as p

class GameState:
    def __init__(self):
        
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]
        
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'K': self.getKingMoves, 'Q': self.getQueenMoves}
        self.whiteToMove = True     # White turn or not
        self.moveLog = []           
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False        
        self.pins = []
        self.checks = []
        self.promotionDone = True
        self.enPassantPossible = ()  # coordinates for the square where en passant capture is possible
        self.enPassantPossibleLog = [self.enPassantPossible]  
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]
        self.checkmate = False
        self.stalemate = False

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = '--'
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        # update King's location if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
        # Pawn promotion
        elif move.pieceMoved == 'wp' and move.endRow == 0:
            self.eR, self.eC, self.sR, self.sC = move.endRow, move.endCol, move.startRow, move.startCol 
            self.promotionDone = False
        elif move.pieceMoved == 'bp' and move.endRow == 7:
            self.eR, self.eC, self.sR, self.sC = move.endRow, move.endCol, move.startRow, move.startCol 
            self.promotionDone = False
        # update en passant possible
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            # print((move.startRow + move.endRow) // 2, move.startCol)
            self.enPassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enPassantPossible = ()
        # En Passant move
        if move.isEnPassantMove:
            self.board[move.startRow][move.endCol] = '--'
        # caslte move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # king side
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]  # move rook
                self.board[move.endRow][move.endCol + 1] = '--'  # erase old rook
            else:  # queen side
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]  # move rook
                self.board[move.endRow][move.endCol - 2] = '--'  # erase old rook

        self.enPassantPossibleLog.append(self.enPassantPossible)

        # update castling rights when a rook/ a king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            # update King's location if moved
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            # en passant
            if move.isEnPassantMove:
                self.board[move.endRow][move.endCol] = '--'  # leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
            self.enPassantPossibleLog.pop()
            self.enPassantPossible = self.enPassantPossibleLog[-1]
            # undo castling rights
            self.castleRightsLog.pop()  # get rid of the new satle rights from the move we undo
            self.currentCastlingRight = self.castleRightsLog[-1]  # set the current CR to the last one in list
            # undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # king side
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:  # queen side
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'
            self.checkmate = False
            self.stalemate = False

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRight.bks = False
        elif move.pieceMoved[0] == 'w' and move.endRow == 0:
            if move.endCol == 0:
                self.currentCastlingRight.bqs = False
            elif move.endCol == 7:
                self.currentCastlingRight.bks = False
        elif move.pieceMoved[0] == 'b' and move.endRow == 7:
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
                pieceChecking = self.board[checkRow][checkCol]  # enemy piece causing the check
                validSquares = []  # squares the pieces can move to
                # if knight, must capture knight or move king, other piece can block
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (
                            kingRow + check[2] * i,
                            kingCol + check[3] * i)  # check[2], check[3] are the check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:  # get to piece end checks
                            break
                # get rid of any moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1):  # go through backwards when removing a list as iterating
                    if moves[i].pieceMoved[1] != 'K':  # move doesn't move king so it must block or capture
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
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
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
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
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
                    if self.board[r - 1][c - 1][0] == 'b':
                        if not piecePinned or pinDirection == (-1, -1):
                            moves.append(Move((r, c), (r - 1, c - 1), self.board))
                    elif (r - 1, c - 1) == self.enPassantPossible:
                        if not piecePinned or pinDirection == (-1, -1):
                            moves.append(Move((r, c), (r - 1, c - 1), self.board, True))
                if c + 1 <= 7:  # capture right
                    if self.board[r - 1][c + 1][0] == 'b':
                        if not piecePinned or pinDirection == (-1, 1):
                            moves.append(Move((r, c), (r - 1, c + 1), self.board))
                    elif (r - 1, c + 1) == self.enPassantPossible:
                        if not piecePinned or pinDirection == (-1, 1):
                            moves.append(Move((r, c), (r - 1, c + 1), self.board, True))
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
                    if self.board[r + 1][c - 1][0] == 'w':
                        if not piecePinned or pinDirection == (1, -1):
                            moves.append(Move((r, c), (r + 1, c - 1), self.board))
                    elif (r + 1, c - 1) == self.enPassantPossible:
                        if not piecePinned or pinDirection == (1, -1):
                            moves.append(Move((r, c), (r + 1, c - 1), self.board, True))
                if c + 1 <= 7:  # capture right
                    if self.board[r + 1][c + 1][0] == 'w':
                        if not piecePinned or pinDirection == (1, 1):
                            moves.append(Move((r, c), (r + 1, c + 1), self.board))
                    elif (r + 1, c + 1) == self.enPassantPossible:
                        if not piecePinned or pinDirection == (1, 1):
                            moves.append(Move((r, c), (r + 1, c + 1), self.board, True))

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
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--':  # empty space valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:  # enemy piece valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
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
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:  # not an ally piece
                        moves.append(Move((r, c), (endRow, endCol), self.board))

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
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--':  # empty space valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:  # enemy piece valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
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
    Get all the king moves for the king located at row, col and add these moves to the list
    '''

    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # Not an ally piece
                    # place king in end square and check for checks
                    if allyColor == 'w':
                        row, col = self.whiteKingLocation[0], self.whiteKingLocation[1]
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        row, col = self.blackKingLocation[0], self.blackKingLocation[1]
                        self.blackKingLocation = (endRow, endCol)
                    self.board[row][col] = '--'
                    inChecks, pins, checks = self.checkForPinsAndChecks()
                    if allyColor == 'w':
                        self.board[row][col] = 'wK'
                    else:
                        self.board[row][col] = 'bK'
                    if not inChecks:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    # place king back on original location
                    if allyColor == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)
        # self.getCastleMoves(r, c, moves, allyColor)


    def pawnPromotion(self, char):
        self.board[self.eR][self.eC] = 'w'+char if self.whiteToMove else 'b'+char
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
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueenSideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))

    def checkForPinsAndChecks(self):
        pins = []  # Squares where the allied pinned piece is and direction pinned from
        checks = []  # Squares where enemy is applying a check
        inCheck = False
        if self.whiteToMove:
            enemyColor = 'b'
            allyColor = 'w'
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = 'w'
            allyColor = 'b'
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        # Check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
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
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'p' and (
                                        (enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
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
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':  # enemy knight attacking king
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks


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
        self.modeID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        self.isCastleMove = isCastleMove

    '''Override'''

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.modeID == other.modeID
        return False

    def getChessNotation(self):
        return self.UNICODE_PIECES[self.pieceMoved] + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

