import numpy as np

BOARD_SIZE = 6


#Board creation 

def initiate_board():
    board = np.full((BOARD_SIZE, BOARD_SIZE), '.', dtype=object)
    reserves = {
        'r': {'k': 8, 'c': 0},
        'b': {'k': 8, 'c': 0},
    }
    return board, reserves


def copy_reserves(reserves):
    """Shallow-copy delle reserves (molto più veloce di deepcopy)."""
    return {
        'r': {'k': reserves['r']['k'], 'c': reserves['r']['c']},
        'b': {'k': reserves['b']['k'], 'c': reserves['b']['c']},
    }


#Utilities 

def switch_turn(player):
    return 'b' if player == 'r' else 'r'


def inside_board(r, c):
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE


def piece_owner(piece):
    return None if piece == '.' else piece[0]


def piece_type(piece):
    return None if piece == '.' else piece[1]


# Legal moves

def get_legal_moves(board):
    moves = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r, c] == '.':
                moves.append((r, c))
    return moves


#  Push mechanics

_DIRECTIONS = [
    (-1,  0), (1,  0), (0, -1), (0,  1),
    (-1, -1), (-1,  1), (1, -1), (1,  1),
]


def _push_tiles(board, reserves, r, c):
    pusher_t = piece_type(board[r, c])

    for dr, dc in _DIRECTIONS:
        nr, nc = r + dr, c + dc

        if not inside_board(nr, nc):
            continue

        target = board[nr, nc]
        if target == '.':
            continue

        target_owner = piece_owner(target)
        target_t     = piece_type(target)

        if pusher_t == 'k' and target_t == 'c':
            continue

        tr, tc = nr + dr, nc + dc

        if inside_board(tr, tc) and board[tr, tc] != '.':
            continue

        if not inside_board(tr, tc):
            reserves[target_owner][target_t] += 1
            board[nr, nc] = '.'
            continue

        board[tr, tc] = target
        board[nr, nc] = '.'


#  Promotion 

def _find_kitten_lines(board, player):
    line_dirs = [(0, 1), (1, 0), (1, 1), (-1, 1)]
    found = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            for dr, dc in line_dirs:
                coords = [(r + i*dr, c + i*dc) for i in range(3)]
                if all(
                    inside_board(rr, cc) and board[rr, cc] == player + 'k'
                    for rr, cc in coords
                ):
                    found.append(coords)
    return found


def _promote_kittens(board, reserves):

    changed = True
    while changed:
        changed = False
        for player in ('r', 'b'):
            lines = _find_kitten_lines(board, player)
            if not lines:
                continue
            cells = {coord for line in lines for coord in line}
            for (r, c) in cells:
                board[r, c] = '.'
                reserves[player]['c'] += 1
            changed = True


#  Apply move 

def apply_move(board, reserves, move, player, ptype=None):
    r, c = move

    if ptype is None:
        ptype = 'c' if reserves[player]['c'] > 0 else 'k'

    if reserves[player][ptype] <= 0:
        raise ValueError(
            f"Player '{player}' has no {'cat' if ptype == 'c' else 'kitten'} in reserve."
        )

    new_board    = board.copy()
    new_reserves = copy_reserves(reserves)

    new_reserves[player][ptype] -= 1
    new_board[r, c] = player + ptype

    _push_tiles(new_board, new_reserves, r, c)
    _promote_kittens(new_board, new_reserves)

    return new_board, new_reserves


def check_winner(board, reserves):
    for player in ('r', 'b'):
        if _three_cats_in_row(board, player):
            return player
    for player in ('r', 'b'):
        if reserves[player]['c'] == 8:
            return player
    return None


def _three_cats_in_row(board, player):
    line_dirs = [(0, 1), (1, 0), (1, 1), (-1, 1)]
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            for dr, dc in line_dirs:
                coords = [(r + i*dr, c + i*dc) for i in range(3)]
                if all(
                    inside_board(rr, cc) and board[rr, cc] == player + 'c'
                    for rr, cc in coords
                ):
                    return True
    return False
