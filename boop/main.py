import numpy as np
from game_engine import (
    initiate_board, apply_move, check_winner,
    switch_turn, get_legal_moves, BOARD_SIZE
)
from ai_player import ai_move


# ── Board display ─────────────────────────────────────────────

def print_board(board, reserves):
    rownames = ['A', 'B', 'C', 'D', 'E', 'F']

    print(f"\n  Red  (you) — kittens: {reserves['r']['k']}  cats: {reserves['r']['c']}")
    print(f"  Blue (AI)  — kittens: {reserves['b']['k']}  cats: {reserves['b']['c']}")
    print("\n    1  2  3  4  5  6")
    for r in range(BOARD_SIZE):
        row_string = " ".join(
            f"{cell:2}" if cell != '.' else ".." for cell in board[r]
        )
        print(f"{rownames[r]} | {row_string}")
    print()


# ── Human move ────────────────────────────────────────────────

def human_move(board, reserves, player):
    """Returns (row, col), ptype."""

    available = []
    if reserves[player]['k'] > 0:
        available.append('k')
    if reserves[player]['c'] > 0:
        available.append('c')

    # Choose piece type
    if len(available) == 1:
        ptype = available[0]
        label = 'kitten' if ptype == 'k' else 'cat'
        print(f"  Placing a {label} (only option available).")
    else:
        while True:
            choice = input("  Place a (k)itten or a (c)at? ").strip().lower()
            if choice in ('k', 'kitten'):
                ptype = 'k'
                break
            elif choice in ('c', 'cat'):
                ptype = 'c'
                break
            print("  Type 'k' for kitten or 'c' for cat.")

    # Choose cell
    while True:
        raw = input("  Enter cell (example: A3): ").strip().upper()

        if len(raw) != 2:
            print("  Invalid format — use a letter and a digit, e.g. B4.")
            continue

        row = ord(raw[0]) - ord('A')
        col = int(raw[1]) - 1

        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            print("  Out of board.")
            continue

        if board[row, col] != '.':
            print("  That cell is already occupied.")
            continue

        return (row, col), ptype


# ── Main loop ─────────────────────────────────────────────────

def main():
    board, reserves = initiate_board()

    player_turn = 'r'   # human plays red
    ai_color    = 'b'

    while True:
        print_board(board, reserves)

        if player_turn != ai_color:
            print("Your turn (Red)")
            move, ptype = human_move(board, reserves, player_turn)
        else:
            print("AI thinking...")
            move, ptype = ai_move(board, reserves, ai_color)

        board, reserves = apply_move(board, reserves, move, player_turn, ptype)

        winner = check_winner(board, reserves)
        if winner is not None:
            print_board(board, reserves)
            print("AI wins!" if winner == ai_color else "You win!")
            break

        player_turn = switch_turn(player_turn)


if __name__ == "__main__":
    main()