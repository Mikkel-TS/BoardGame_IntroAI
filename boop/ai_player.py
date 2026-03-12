import math
from game_engine import *

MAX_DEPTH = 3

# AI move
def ai_move(board, reserves, ai_player):

    best_score = -math.inf
    best_move  = None
    best_ptype = None

    moves = get_legal_moves(board)

    for move in moves:
        for ptype in ('k', 'c'):
            if reserves[ai_player][ptype] <= 0:
                continue

            new_board, new_reserves = apply_move(board, reserves, move, ai_player, ptype)

            score = minimax(
                new_board, new_reserves,
                MAX_DEPTH - 1,
                False,    
                ai_player,
                -math.inf, math.inf
            )

            if score > best_score:
                best_score = score
                best_move  = move
                best_ptype = ptype

    return best_move, best_ptype


# Minimax with alpha-beta pruning

def minimax(board, reserves, depth, maximizing_player, ai_player, alpha, beta):

    opponent = switch_turn(ai_player)
    winner   = check_winner(board, reserves)

    if winner == ai_player:
        return 10000 + depth  
    if winner == opponent:
        return -10000 - depth 

    if depth == 0:
        return evaluate(board, reserves, ai_player)

    moves = get_legal_moves(board)
    if not moves:
        return evaluate(board, reserves, ai_player)

    current_player = ai_player if maximizing_player else opponent

    if maximizing_player:
        max_eval = -math.inf
        done = False
        for move in moves:
            if done:
                break
            for ptype in ('k', 'c'):
                if reserves[current_player][ptype] <= 0:
                    continue

                new_board, new_reserves = apply_move(board, reserves, move, current_player, ptype)
                eval_score = minimax(
                    new_board, new_reserves,
                    depth - 1, False,
                    ai_player, alpha, beta
                )

                if eval_score > max_eval:
                    max_eval = eval_score
                if eval_score > alpha:
                    alpha = eval_score
                if beta <= alpha:
                    done = True
                    break

        return max_eval

    else:
        min_eval = math.inf
        done = False
        for move in moves:
            if done:
                break
            for ptype in ('k', 'c'):
                if reserves[current_player][ptype] <= 0:
                    continue

                new_board, new_reserves = apply_move(board, reserves, move, current_player, ptype)
                eval_score = minimax(
                    new_board, new_reserves,
                    depth - 1, True,
                    ai_player, alpha, beta
                )

                if eval_score < min_eval:
                    min_eval = eval_score
                if eval_score < beta:
                    beta = eval_score
                if beta <= alpha:
                    done = True
                    break

        return min_eval


# evaluation func

def evaluate(board, reserves, ai_player):

    opponent = switch_turn(ai_player)

    ai_kittens, ai_cats = count_pieces(board, ai_player)
    op_kittens, op_cats = count_pieces(board, opponent)

    score = 0

    score += reserves[ai_player]['c'] * 15
    score -= reserves[opponent]['c']  * 15

    score += ai_cats * 20
    score -= op_cats * 20

    score += ai_kittens * 5
    score -= op_kittens * 5

    score += count_cat_threats(board, ai_player) * 30
    score -= count_cat_threats(board, opponent)  * 30

    return score


def count_pieces(board, player):
    kittens = 0
    cats    = 0
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            piece = board[r, c]
            if   piece == player + 'k': kittens += 1
            elif piece == player + 'c': cats    += 1
    return kittens, cats


def count_cat_threats(board, player):
    count      = 0
    cat        = player + 'c'
    line_dirs  = [(0,1),(1,0),(1,1),(-1,1)]

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            for dr, dc in line_dirs:
                coords = [(r + i*dr, c + i*dc) for i in range(3)]
                if not all(inside_board(rr, cc) for rr, cc in coords):
                    continue
                cells = [board[rr, cc] for rr, cc in coords]
                n_cats  = cells.count(cat)
                n_empty = cells.count('.')
                if n_cats == 2 and n_empty == 1:
                    count += 1

    return count
