import random

from ChessEngine import GameState

piecesScore = {
    "K": 900, "Q": 90, "R": 50,
    "B": 30, "N": 30, "p": 10
}

wK = [
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0],
    [-1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0],
    [2.0, 2.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0],
    [2.0, 3.0, 1.0, 0.0, 0.0, 1.0, 3.0, 2.0]
]

wQ = [
    [-2, -1, -1, -0.5, -0, .5 - 1, -1, -2],
    [-1, 0, 0, 0, 0, 0, 0, -1],
    [-1, 0, 0.5, 0.5, 0.5, 0.5, 0, -1],
    [-0.5, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5],
    [0, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5],
    [-1, 0.5, 0.5, 0.5, 0.5, 0.5, 0, -1],
    [-1, 0, 0.5, 0, 0, 0, 0, -1],
    [-2, -1, -1, -0.5, -0.5, -1, -1, -2]
]

wR = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0.5, 1, 1, 1, 1, 1, 1, 0.5],
    [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
    [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
    [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
    [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
    [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
    [0, 0, 0, 0.5, 0.5, 0, 0, 0]
]

wB = [
    [-2, -1, -1, -1, -1, -1, -1, -2],
    [-1, 0, 0, 0, 0, 0, 0, -1],
    [-1, 0, 0.5, 1, 1, 0.5, 0, -1],
    [-1, 0.5, 0.5, 1, 1, 0.5, 0.5, -1],
    [-1, 0, 1, 1, 1, 1, 0, -1],
    [-1, 1, 1, 1, 1, 1, 1, -1],
    [-2, -1, -1, -1, -1, -1, -1, -2]
]

wN = [
    [-5, -4, -3, -3, -3, -3, -4, -5],
    [-4, -2, 0, 0, 0, 0, -2, -4],
    [-3, 0, 1, 1.5, 1.5, 1, 0, -3],
    [-3, 0.5, 1.5, 2, 2, 1.5, 0.5, -3],
    [-3, 0.5, 1, 1.5, 1.5, 1, 0.5, -3],
    [-4, -2, 0, 0.5, 0.5, 0, -2, -4],
    [-5, -4, -3, -3, -3, -3, -4, -5]
]

wp = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [5, 5, 5, 5, 5, 5, 5, 5],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [0.5, 0.5, 1, 2.5, 2.5, 1, 0.5, 0.5],
    [0, 0, 0, 2, 2, 0, 0, 0],
    [0.5, -0.5, -1, 0, 0, -1, -0.5, 0.5],
    [0.5, 1, 1, -2, -2, 1, 1, 0.5],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

CHECKMATE = 1000
STALEMATE = -1000
DEPTH = 2

MAX_PLAYER_WORST = -10000
MIN_PLAYER_WORST = 10000

MIN_MAX_WITHOUT_PRUNING = 1
MIN_MAX_WITH_BETA_PRUNING = 2
MIN_MAX_WITHOUT_PRUNING_EASY = 3


def move_with_strategy(gs: GameState, depth: int = 2, strategy=MIN_MAX_WITH_BETA_PRUNING, validMoves=None):
    next_move = None
    if strategy == MIN_MAX_WITH_BETA_PRUNING:
        chess_alpha_beta_best_move(node=gs, depth=depth, alpha=MAX_PLAYER_WORST, beta=MIN_PLAYER_WORST,
                                   is_max_player=True)
    elif strategy == MIN_MAX_WITHOUT_PRUNING:
        findBestMoveMinMax(gs=gs, validMoves=validMoves if validMoves else gs.getValidMoves(), depth=depth)
    elif strategy == MIN_MAX_WITHOUT_PRUNING_EASY:
        # Move chosen is almost random
        findBestMoveMinMax(gs=gs, validMoves=validMoves if validMoves else gs.getValidMoves(), depth=1)
    return next_move


# * ------------------- Code Refactor +  Alpha - beta pruning ----------------
def isTerminalNode(gs: GameState):
    return gs.check_game_ended()


# TODO: Calculate heuristic for the node based on material and the game flow (Some combination of pieces position are more powerful than others)
def calculateHeuristicScoreForNode(gs: GameState):
    return gs.getScoreBoardValue()


# TODO: For better performance we should not choose moves randomly when searching
# TODO: ---> Move Order matters: Check for pawn structures + isolation + king postition + forks and pins
# TODO: Below code is wrong in part that child is not a game state: GS = makeMove(currentGameState, child);
def chessAlphaBeta(node: GameState, depth: int = 2, alpha: int = MAX_PLAYER_WORST, beta: int = MIN_PLAYER_WORST,
                   is_max_player: bool = True):
    if depth == 0 or isTerminalNode(node):
        return calculateHeuristicScoreForNode(node)
    if is_max_player:
        value = MAX_PLAYER_WORST
        for move in node.getValidMoves():
            node.makeMove(move)
            value = max(value, chessAlphaBeta(
                node, depth - 1, alpha, beta, False))
            node.undoMove()
            if (value >= beta):
                break  # Beta cutofff
            alpha = max(alpha, value)
        return value
    # * Min Player:
    else:
        value = MIN_PLAYER_WORST
        for move in node.getValidMoves():
            node.makeMove(move)
            value = min(value, chessAlphaBeta(
                node, depth - 1, alpha, beta, True))
            node.undoMove()
            if value <= alpha:
                break  # Alpha cutoff
            beta = min(beta, value)
        return value


def chess_alpha_beta_best_move(node: GameState, depth, alpha, beta, is_max_player):
    global next_move
    if depth == 0 or isTerminalNode(node):
        return calculateHeuristicScoreForNode(node)
    if is_max_player:
        value = MAX_PLAYER_WORST
        for move in node.getValidMoves():
            node.makeMove(move)
            value = max(value, chessAlphaBeta(
                node, depth - 1, alpha, beta, False))
            node.undoMove()
            if (value >= beta):
                break  # Beta cutofff
            if value > alpha:
                alpha = value
                best_move = next_move
        return value
    # * Min Player:
    else:
        value = MIN_PLAYER_WORST
        for move in node.getValidMoves():
            node.makeMove(move)
            value = min(value, chessAlphaBeta(
                node, depth - 1, alpha, beta, True))
            node.undoMove()
            if value <= alpha:
                break  # Alpha cutoff
            if value < beta:
                beta = value
                next_move = move
            beta = min(beta, value)
        return value


# * ----------------------------------------------------------- *
def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]


def findBestMove(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opponentsMoves = gs.getValidMoves()
        opponentMaxScore = -CHECKMATE
        for opponentsMove in opponentsMoves:
            gs.makeMove(opponentsMove)
            if gs.checkmate:
                score = -turnMultiplier * CHECKMATE
            elif gs.stalemate:
                score = STALEMATE
            else:
                score = -turnMultiplier * scoreMaterial(gs.board)
            if score > opponentMaxScore:
                opponentMaxScore = score
            gs.undoMove()
        if opponentMinMaxScore > opponentMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()
    return bestPlayerMove


def findBestMoveMinMax(gs: GameState, validMoves, depth=2):
    global nextMove
    nextMove = None
    findMoveMinMax(gs, validMoves, depth, gs.whiteToMove)
    return nextMove


def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global next_move
    if depth == 0:
        return scoreMaterial(gs.board)
    if whiteToMove:
        maxScore = -CHECKMATE
        random.shuffle(validMoves)
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    next_move = move
            gs.undoMove()
        return maxScore
    else:
        minScore = CHECKMATE
        random.shuffle(validMoves)
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    next_move = move
            gs.undoMove()
        return minScore


def findBestMoveMinMaxEasy(gs, validMoves):
    global nextMove
    nextMove = None
    findMoveMinMaxEasy(gs, validMoves, 1, gs.whiteToMove)
    return nextMove


def findMoveMinMaxEasy(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreMaterial(gs.board)
    if whiteToMove:
        maxScore = -CHECKMATE
        random.shuffle(validMoves)
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMaxEasy(gs, nextMoves, depth - 1, False)
            if score > maxScore:
                maxScore = score
                if depth == 1:
                    nextMove = move
            gs.undoMove()
        return maxScore
    else:
        minScore = CHECKMATE
        random.shuffle(validMoves)
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMaxEasy(gs, nextMoves, depth - 1, True)
            if score < minScore:
                minScore = score
                if depth == 1:
                    nextMove = move
            gs.undoMove()
        return minScore


'''
>0 score -> good for white
<0 score -> good for black
'''


def scoreBoard(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE  # black wins
        else:
            return CHECKMATE  # white wins
    elif gs.stalemate:
        return STALEMATE
    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == 'w':
                score += piecesScore[square[1]]
            elif square[0] == 'b':
                score -= piecesScore[square[1]]
    return score


'''
Score the board base on material
'''


def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += piecesScore[square[1]]
            elif square[0] == 'b':
                score -= piecesScore[square[1]]
    return score
