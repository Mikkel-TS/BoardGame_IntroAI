import math

from game_engine import *

DEFAULT_DEPTH = 3
LINE_DIRS = ((0, 1), (1, 0), (1, 1), (-1, 1))


def ai_move(board, reserves, ai_player, depth=DEFAULT_DEPTH):
    best_score = -math.inf
    best_move = None
    best_ptype = None
    cache = {}

    for move, ptype in ordered_moves(board, reserves, ai_player):
        new_board, new_reserves = apply_move(board, reserves, move, ai_player, ptype)
        score = minimax(
            new_board,
            new_reserves,
            depth - 1,
            False,
            ai_player,
            -math.inf,
            math.inf,
            cache,
        )

        if score > best_score:
            best_score = score
            best_move = move
            best_ptype = ptype

    return best_move, best_ptype


def minimax(board, reserves, depth, maximizing_player, ai_player, alpha, beta, cache):
    state_key = make_state_key(board, reserves, depth, maximizing_player, ai_player)
    cached = cache.get(state_key)
    if cached is not None:
        return cached

    opponent = switch_turn(ai_player)
    winner = check_winner(board, reserves)

    if winner == ai_player:
        return 10000 + depth
    if winner == opponent:
        return -10000 - depth

    if depth == 0:
        score = evaluate(board, reserves, ai_player)
        cache[state_key] = score
        return score

    current_player = ai_player if maximizing_player else opponent
    moves = ordered_moves(board, reserves, current_player)
    if not moves:
        score = evaluate(board, reserves, ai_player)
        cache[state_key] = score
        return score

    if maximizing_player:
        best_score = -math.inf
        for move, ptype in moves:
            new_board, new_reserves = apply_move(board, reserves, move, current_player, ptype)
            eval_score = minimax(
                new_board,
                new_reserves,
                depth - 1,
                False,
                ai_player,
                alpha,
                beta,
                cache,
            )
            if eval_score > best_score:
                best_score = eval_score
            if eval_score > alpha:
                alpha = eval_score
            if beta <= alpha:
                break
    else:
        best_score = math.inf
        for move, ptype in moves:
            new_board, new_reserves = apply_move(board, reserves, move, current_player, ptype)
            eval_score = minimax(
                new_board,
                new_reserves,
                depth - 1,
                True,
                ai_player,
                alpha,
                beta,
                cache,
            )
            if eval_score < best_score:
                best_score = eval_score
            if eval_score < beta:
                beta = eval_score
            if beta <= alpha:
                break

    cache[state_key] = best_score
    return best_score


def ordered_moves(board, reserves, player):
    moves = []
    center = (BOARD_SIZE - 1) / 2

    for move in get_legal_moves(board):
        r, c = move
        center_bias = abs(r - center) + abs(c - center)

        for ptype in ("k", "c"):
            if reserves[player][ptype] <= 0:
                continue

            score = -center_bias
            if ptype == "c":
                score += 1.5

            moves.append((score, move, ptype))

    moves.sort(reverse=True)
    return [(move, ptype) for _, move, ptype in moves]


def make_state_key(board, reserves, depth, maximizing_player, ai_player):
    return (
        tuple(board.flat),
        reserves["r"]["k"],
        reserves["r"]["c"],
        reserves["b"]["k"],
        reserves["b"]["c"],
        depth,
        maximizing_player,
        ai_player,
    )


def evaluate(board, reserves, ai_player):
    opponent = switch_turn(ai_player)

    ai_kittens, ai_cats = count_pieces(board, ai_player)
    op_kittens, op_cats = count_pieces(board, opponent)

    score = 0
    score += reserves[ai_player]["c"] * 15
    score -= reserves[opponent]["c"] * 15
    score += ai_cats * 20
    score -= op_cats * 20
    score += ai_kittens * 5
    score -= op_kittens * 5
    score += count_cat_threats(board, ai_player) * 30
    score -= count_cat_threats(board, opponent) * 30

    return score


def count_pieces(board, player):
    kittens = 0
    cats = 0
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            piece = board[r, c]
            if piece == player + "k":
                kittens += 1
            elif piece == player + "c":
                cats += 1
    return kittens, cats


def count_cat_threats(board, player):
    count = 0
    cat = player + "c"

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            for dr, dc in LINE_DIRS:
                coords = [(r + i * dr, c + i * dc) for i in range(3)]
                if not all(inside_board(rr, cc) for rr, cc in coords):
                    continue

                cells = [board[rr, cc] for rr, cc in coords]
                if cells.count(cat) == 2 and cells.count(".") == 1:
                    count += 1

    return count
