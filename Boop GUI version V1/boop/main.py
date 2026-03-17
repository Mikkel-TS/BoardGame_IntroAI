import tkinter as tk

from ai_player import ai_move
from game_engine import BOARD_SIZE, apply_move, check_winner, initiate_board, switch_turn


ROW_NAMES = ["A", "B", "C", "D", "E", "F"]
CELL_SIZE = 58
AI_DELAY_MS = 450

ICON_PLAYER = "\U0001F464"
ICON_AI = "\U0001F916"
ICON_KITTEN = "\U0001F43E"
ICON_CAT = "\U0001F408"
ICON_TITLE = "\U0001F43E"
ICON_WELCOME = "\U0001F431"
ICON_TROPHY = "\U0001F3C6"

AI_LEVELS = {
    "Easy": 2,
    "Normal": 3,
    "Hard": 4,
    "Hardest": 5,
}
PLAYER_COLORS = {"r": "red", "b": "blue"}
PLAYER_ACTIVE_BACKGROUNDS = {"r": "red_soft", "b": "blue_soft"}

COLORS = {
    "bg": "#f5f1eb",
    "panel": "#fffaf4",
    "card": "#ffffff",
    "card_border": "#eadfce",
    "text": "#2d241f",
    "muted": "#6e635c",
    "red": "#d94f5c",
    "red_soft": "#ffdce1",
    "blue": "#4d78d6",
    "blue_soft": "#deebff",
    "empty": "#d9d9dc",
    "accent": "#f4b544",
    "good": "#2c9a66",
    "danger": "#c65a5a",
}

FONTS = {
    "title": ("Segoe UI", 20, "bold"),
    "subtitle": ("Segoe UI", 11),
    "card_title": ("Segoe UI", 12, "bold"),
    "card_text": ("Segoe UI", 11),
    "board_label": ("Segoe UI", 11, "bold"),
    "piece": ("Segoe UI Emoji", 20),
    "status": ("Segoe UI", 13, "bold"),
    "button": ("Segoe UI", 10, "bold"),
    "banner": ("Segoe UI", 18, "bold"),
}

PIECE_STYLES = {
    ".": {"text": "", "bg": COLORS["empty"], "fg": COLORS["text"]},
    "rk": {"text": ICON_KITTEN, "bg": "#f8cfd7", "fg": COLORS["red"]},
    "rc": {"text": ICON_CAT, "bg": COLORS["red"], "fg": "white"},
    "bk": {"text": ICON_KITTEN, "bg": "#cfe0ff", "fg": COLORS["blue"]},
    "bc": {"text": ICON_CAT, "bg": COLORS["blue"], "fg": "white"},
}


class BoopGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Boop AI Arena")
        self.root.configure(bg=COLORS["bg"])
        self.root.geometry("900x900")
        self.root.minsize(860, 860)

        self.mode = None
        self.board = None
        self.reserves = None
        self.player_turn = None
        self.ai_color = "b"
        self.cells = []
        self.game_running = False
        self.ai_job = None
        self.winner = None
        self.ai_level_name = "Normal"
        self.ai_depth = AI_LEVELS[self.ai_level_name]
        self.selected_piece_type = "k"

        self.create_widgets()

    def create_widgets(self):
        if self.mode is None:
            self.create_welcome_screen()
        else:
            self.create_game_widgets()

    def create_welcome_screen(self):
        self.mode_frame = tk.Frame(self.root, bg=COLORS["bg"], padx=28, pady=28)
        self.mode_frame.pack(expand=True, fill=tk.BOTH)

        welcome_card = tk.Frame(
            self.mode_frame,
            bg=COLORS["panel"],
            highlightthickness=1,
            highlightbackground=COLORS["card_border"],
            padx=30,
            pady=30,
        )
        welcome_card.pack(expand=True)

        tk.Label(
            welcome_card,
            text=f"{ICON_WELCOME} Boop AI Arena",
            font=FONTS["title"],
            bg=COLORS["panel"],
            fg=COLORS["text"],
        ).pack(pady=(0, 12))

        tk.Label(
            welcome_card,
            text="Choose a mode and set the AI difficulty.",
            font=FONTS["subtitle"],
            bg=COLORS["panel"],
            fg=COLORS["muted"],
        ).pack(pady=(0, 20))

        difficulty_row = tk.Frame(welcome_card, bg=COLORS["panel"])
        difficulty_row.pack(fill=tk.X, pady=(0, 20))

        tk.Label(
            difficulty_row,
            text="AI Difficulty",
            font=FONTS["card_title"],
            bg=COLORS["panel"],
            fg=COLORS["text"],
        ).pack(anchor="w", pady=(0, 8))

        self.difficulty_buttons_frame = tk.Frame(difficulty_row, bg=COLORS["panel"])
        self.difficulty_buttons_frame.pack(anchor="w")
        self.difficulty_buttons = {}

        for index, level_name in enumerate(AI_LEVELS.keys()):
            button = tk.Button(
                self.difficulty_buttons_frame,
                text=level_name,
                command=lambda level_name=level_name: self.select_ai_level(level_name),
                font=FONTS["button"],
                relief=tk.FLAT,
                bd=0,
                padx=12,
                pady=10,
                cursor="hand2",
            )
            button.pack(side=tk.LEFT, padx=(0, 8 if index < len(AI_LEVELS) - 1 else 0))
            self.difficulty_buttons[level_name] = button

        self.update_difficulty_buttons()

        for text, mode in (
            (f"{ICON_PLAYER} Human vs AI", "human_ai"),
            (f"{ICON_AI} AI vs AI", "ai_ai"),
        ):
            self._mode_button(welcome_card, text, lambda mode=mode: self.set_mode(mode)).pack(
                fill=tk.X, pady=8
            )

    def _mode_button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=FONTS["button"],
            bg=COLORS["accent"],
            fg=COLORS["text"],
            activebackground="#f0a91c",
            activeforeground=COLORS["text"],
            relief=tk.FLAT,
            bd=0,
            padx=18,
            pady=14,
            cursor="hand2",
        )

    def select_ai_level(self, level_name):
        self.ai_level_name = level_name
        self.ai_depth = AI_LEVELS[level_name]
        if hasattr(self, "difficulty_buttons"):
            self.update_difficulty_buttons()

    def update_difficulty_buttons(self):
        for level_name, button in self.difficulty_buttons.items():
            selected = level_name == self.ai_level_name
            bg = COLORS["accent"] if selected else "#ece5db"
            button.config(
                bg=bg,
                fg=COLORS["text"],
                activebackground=bg,
                activeforeground=COLORS["text"],
            )

    def create_game_widgets(self):
        self.main_frame = tk.Frame(self.root, bg=COLORS["bg"], padx=16, pady=12)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(self.main_frame, bg=COLORS["bg"])
        header.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            header,
            text=f"{ICON_TITLE} Boop AI Arena",
            font=FONTS["title"],
            bg=COLORS["bg"],
            fg=COLORS["text"],
        ).pack(anchor="w")

        tk.Label(
            header,
            text=f"Difficulty: {self.ai_level_name}  |  Modern board view with icons for players, kittens, and cats.",
            font=FONTS["subtitle"],
            bg=COLORS["bg"],
            fg=COLORS["muted"],
        ).pack(anchor="w", pady=(4, 0))

        self.reserves_frame = tk.Frame(self.main_frame, bg=COLORS["bg"])
        self.reserves_frame.pack(fill=tk.X, pady=(0, 10))
        self.reserves_frame.grid_columnconfigure(0, weight=1)
        self.reserves_frame.grid_columnconfigure(1, weight=1)

        self.red_card = self._create_player_card(self.reserves_frame, 0)
        self.blue_card = self._create_player_card(self.reserves_frame, 1)
        self.player_cards = {"r": self.red_card, "b": self.blue_card}

        board_shell = tk.Frame(
            self.main_frame,
            bg=COLORS["panel"],
            highlightthickness=1,
            highlightbackground=COLORS["card_border"],
            padx=12,
            pady=12,
        )
        board_shell.pack(pady=(0, 6))

        self.board_frame = tk.Frame(board_shell, bg=COLORS["panel"])
        self.board_frame.pack()

        tk.Label(self.board_frame, text="", bg=COLORS["panel"], width=3).grid(
            row=0, column=0, padx=6, pady=6
        )

        for c in range(BOARD_SIZE):
            tk.Label(
                self.board_frame,
                text=str(c + 1),
                font=FONTS["board_label"],
                bg=COLORS["panel"],
                fg=COLORS["muted"],
                width=5,
            ).grid(row=0, column=c + 1, padx=3, pady=(0, 6))

        self.cells = []
        for r in range(BOARD_SIZE):
            tk.Label(
                self.board_frame,
                text=ROW_NAMES[r],
                font=FONTS["board_label"],
                bg=COLORS["panel"],
                fg=COLORS["muted"],
                width=3,
            ).grid(row=r + 1, column=0, padx=(0, 8), pady=3)

            row = []
            for c in range(BOARD_SIZE):
                cell_frame = tk.Frame(
                    self.board_frame,
                    width=CELL_SIZE,
                    height=CELL_SIZE,
                    bg=COLORS["empty"],
                    highlightthickness=0,
                    bd=0,
                )
                cell_frame.grid(row=r + 1, column=c + 1, padx=2, pady=2)
                cell_frame.grid_propagate(False)

                cell_label = tk.Label(
                    cell_frame,
                    text="",
                    font=FONTS["piece"],
                    bg=COLORS["empty"],
                    fg=COLORS["text"],
                    cursor="hand2",
                )
                cell_label.place(relx=0.5, rely=0.5, anchor="center")
                cell_frame.bind("<Button-1>", lambda _e, r=r, c=c: self.cell_clicked(r, c))
                cell_label.bind("<Button-1>", lambda _e, r=r, c=c: self.cell_clicked(r, c))

                row.append({"frame": cell_frame, "label": cell_label})
            self.cells.append(row)

        self.controls_frame = tk.Frame(self.main_frame, bg=COLORS["bg"])
        self.controls_frame.pack(fill=tk.X, pady=(4, 0), side=tk.BOTTOM)

        self.status_label = tk.Label(
            self.controls_frame,
            text="",
            font=FONTS["status"],
            bg=COLORS["bg"],
            fg=COLORS["good"],
        )
        self.status_label.pack(pady=(0, 3))

        self.winner_banner = tk.Label(
            self.controls_frame,
            text="",
            font=FONTS["banner"],
            bg=COLORS["bg"],
            fg=COLORS["text"],
        )
        self.winner_banner.pack(pady=(0, 4))

        buttons_row = tk.Frame(self.controls_frame, bg=COLORS["bg"])
        buttons_row.pack()

        self.restart_button = self._action_button(
            buttons_row, "Restart Game", self.restart_game, COLORS["accent"], COLORS["text"]
        )
        self.restart_button.pack(side=tk.LEFT, padx=6)

        self.menu_button = self._action_button(
            buttons_row, "Back to Menu", self.back_to_menu, "#ece5db", COLORS["text"]
        )
        self.menu_button.pack(side=tk.LEFT, padx=6)

        self.stop_button = self._action_button(
            buttons_row, "Stop Game", self.stop_game, "#f3d7d7", COLORS["danger"]
        )
        self.stop_button.pack(side=tk.LEFT, padx=6)

    def _action_button(self, parent, text, command, bg, fg):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=FONTS["button"],
            bg=bg,
            fg=fg,
            activebackground=bg,
            activeforeground=fg,
            relief=tk.FLAT,
            bd=0,
            padx=14,
            pady=10,
            cursor="hand2",
        )

    def _create_player_card(self, parent, column):
        card = tk.Frame(
            parent,
            bg=COLORS["card"],
            highlightthickness=1,
            highlightbackground=COLORS["card_border"],
            padx=16,
            pady=14,
            height=124,
        )
        card.grid(row=0, column=column, sticky="ew", padx=6)
        card.grid_propagate(False)

        title = tk.Label(card, text="", font=FONTS["card_title"], bg=COLORS["card"])
        title.pack(anchor="w")

        counts = tk.Label(card, text="", font=FONTS["card_text"], bg=COLORS["card"])
        counts.pack(anchor="w", pady=(6, 0))

        detail = tk.Label(card, text="", font=FONTS["subtitle"], bg=COLORS["card"])
        detail.pack(anchor="w", pady=(4, 0))

        selector = tk.Frame(card, bg=COLORS["card"], height=40)
        selector.pack(anchor="w", fill=tk.X, pady=(10, 0))
        selector.pack_propagate(False)

        kitten_button = tk.Button(
            selector,
            text=f"{ICON_KITTEN} Kitten",
            font=FONTS["button"],
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=8,
            cursor="hand2",
            command=lambda: self.select_piece_type("k"),
        )
        kitten_button.pack(side=tk.LEFT, padx=(0, 8))

        cat_button = tk.Button(
            selector,
            text=f"{ICON_CAT} Cat",
            font=FONTS["button"],
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=8,
            cursor="hand2",
            command=lambda: self.select_piece_type("c"),
        )
        cat_button.pack(side=tk.LEFT)

        return {
            "frame": card,
            "title": title,
            "counts": counts,
            "detail": detail,
            "selector": selector,
            "kitten_button": kitten_button,
            "cat_button": cat_button,
        }

    def set_mode(self, mode):
        self.mode = mode
        self.game_running = True
        if hasattr(self, "mode_frame"):
            self.mode_frame.destroy()
        self.start_new_game()

    def start_new_game(self):
        self.cancel_ai_job()
        if hasattr(self, "main_frame"):
            self.main_frame.destroy()

        self.board, self.reserves = initiate_board()
        self.player_turn = "r" if self.mode == "human_ai" else "b"
        self.cells = []
        self.winner = None
        self.game_running = True
        self.selected_piece_type = "k"
        self.create_game_widgets()
        self.update_display()
        self.schedule_ai_turn_if_needed()

    def update_display(self):
        for player_key in ("r", "b"):
            self._update_player_card(self.player_cards[player_key], player_key)

        if self.winner is None:
            self._draw_normal_board()
            self.winner_banner.config(text="", bg=COLORS["bg"])
        else:
            self._draw_winner_board()
            self._update_winner_banner()

        status_text, status_color = self._get_status_text()
        self.status_label.config(text=status_text, fg=status_color)

    def _player_detail(self, player, active):
        if self.winner == player:
            return "Winner"
        if self.winner is not None:
            return "Finished"
        return "Playing now" if active else "Waiting"

    def _draw_normal_board(self):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                self._apply_cell_style(r, c, PIECE_STYLES[self.board[r, c]])

    def _draw_winner_board(self):
        winner_bg = COLORS["red_soft"] if self.winner == "r" else COLORS["blue_soft"]
        winner_strong = COLORS["red"] if self.winner == "r" else COLORS["blue"]
        loser_strong = COLORS["blue"] if self.winner == "r" else COLORS["red"]
        winner_piece = self.winner + "c"
        winner_kitten = self.winner + "k"

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                cell = self.board[r, c]
                frame = self.cells[r][c]["frame"]
                label = self.cells[r][c]["label"]

                if cell == ".":
                    self._apply_cell_style(
                        r,
                        c,
                        {"text": "", "bg": winner_bg, "fg": COLORS["text"]},
                    )
                elif cell in (winner_piece, winner_kitten):
                    icon = ICON_CAT if cell.endswith("c") else ICON_KITTEN
                    self._apply_cell_style(
                        r,
                        c,
                        {"text": icon, "bg": winner_strong, "fg": "white"},
                    )
                else:
                    icon = ICON_CAT if cell.endswith("c") else ICON_KITTEN
                    self._apply_cell_style(
                        r,
                        c,
                        {"text": icon, "bg": winner_bg, "fg": loser_strong},
                    )

    def _update_winner_banner(self):
        banner_bg = COLORS["red_soft"] if self.winner == "r" else COLORS["blue_soft"]
        banner_fg = COLORS["red"] if self.winner == "r" else COLORS["blue"]
        self.winner_banner.config(
            text=f"{ICON_TROPHY} {self._winner_name(self.winner)} wins the game!",
            bg=banner_bg,
            fg=banner_fg,
            padx=14,
            pady=10,
        )

    def _winner_name(self, winner):
        if winner == "r":
            return "You" if self.mode == "human_ai" else "Red AI"
        return "Blue AI"

    def _update_player_card(self, card, player_key):
        active = self._is_player_active(player_key)
        bg = self._player_card_background(player_key, active)
        fg = COLORS[PLAYER_COLORS[player_key]]
        title = self._player_title(player_key)

        card["frame"].config(bg=bg)
        card["title"].config(text=title, fg=fg, bg=bg)
        card["counts"].config(
            text=(
                f"{ICON_KITTEN} Kittens: {self.reserves[player_key]['k']}    "
                f"{ICON_CAT} Cats: {self.reserves[player_key]['c']}"
            ),
            fg=COLORS["text"],
            bg=bg,
        )
        card["detail"].config(text=self._player_detail(player_key, active), fg=COLORS["muted"], bg=bg)
        card["selector"].config(bg=bg)

        if self._has_human_selector(player_key):
            self._ensure_selector_buttons_visible(card)
            self._update_piece_selector(card, bg)
        else:
            self._hide_selector_buttons(card)
        card["selector"].pack(anchor="w", pady=(10, 0))

    def _is_player_active(self, player_key):
        return self.player_turn == player_key and self.game_running and self.winner is None

    def _player_title(self, player_key):
        if player_key == "r":
            return f"{ICON_PLAYER} You" if self.mode == "human_ai" else f"{ICON_AI} Red AI"
        return f"{ICON_AI} Blue AI"

    def _player_card_background(self, player_key, active):
        if self.winner == player_key:
            return COLORS[PLAYER_ACTIVE_BACKGROUNDS[player_key]]
        if active:
            return COLORS[PLAYER_ACTIVE_BACKGROUNDS[player_key]]
        return COLORS["card"]

    def _has_human_selector(self, player_key):
        return self.mode == "human_ai" and player_key == "r" and self.winner is None

    def _ensure_selector_buttons_visible(self, card):
        if not card["kitten_button"].winfo_manager():
            card["kitten_button"].pack(side=tk.LEFT, padx=(0, 8))
        if not card["cat_button"].winfo_manager():
            card["cat_button"].pack(side=tk.LEFT)

    def _hide_selector_buttons(self, card):
        if card["kitten_button"].winfo_manager():
            card["kitten_button"].pack_forget()
        if card["cat_button"].winfo_manager():
            card["cat_button"].pack_forget()

    def _update_piece_selector(self, card, bg):
        can_use_kitten = self.reserves["r"]["k"] > 0
        can_use_cat = self.reserves["r"]["c"] > 0

        if self.selected_piece_type == "c" and not can_use_cat and can_use_kitten:
            self.selected_piece_type = "k"
        if self.selected_piece_type == "k" and not can_use_kitten and can_use_cat:
            self.selected_piece_type = "c"

        self._style_piece_button(
            card["kitten_button"],
            bg=bg,
            selected=self.selected_piece_type == "k",
            enabled=can_use_kitten,
            active_bg="#f8cfd7",
            active_fg=COLORS["red"],
        )
        self._style_piece_button(
            card["cat_button"],
            bg=bg,
            selected=self.selected_piece_type == "c",
            enabled=can_use_cat,
            active_bg="#cfe0ff",
            active_fg=COLORS["blue"],
        )

    def _style_piece_button(self, button, bg, selected, enabled, active_bg, active_fg):
        if not enabled:
            button.config(
                bg=bg,
                fg="#b4aaa2",
                activebackground=bg,
                activeforeground="#b4aaa2",
                state=tk.DISABLED,
            )
            return

        button_bg = active_bg if selected else bg
        button_fg = active_fg if selected else COLORS["text"]
        button.config(
            bg=button_bg,
            fg=button_fg,
            activebackground=button_bg,
            activeforeground=button_fg,
            state=tk.NORMAL,
        )

    def _apply_cell_style(self, r, c, style):
        self.cells[r][c]["frame"].config(bg=style["bg"])
        self.cells[r][c]["label"].config(
            text=style["text"],
            bg=style["bg"],
            fg=style["fg"],
        )

    def _get_status_text(self):
        if self.winner is not None:
            return "", COLORS["text"]
        if not self.game_running:
            return "Game stopped", COLORS["danger"]
        if self.player_turn == "r":
            if self.mode == "ai_ai":
                return f"{ICON_AI} Red AI is playing...", COLORS["red"]
            return f"{ICON_PLAYER} You are playing now", COLORS["good"]
        return f"{ICON_AI} Blue AI is playing...", COLORS["blue"]

    def select_piece_type(self, piece_type):
        if not self.game_running or self.winner is not None or self.mode != "human_ai":
            return
        if self.reserves["r"][piece_type] <= 0:
            return
        self.selected_piece_type = piece_type
        self.update_display()

    def schedule_ai_turn_if_needed(self):
        if not self.game_running or self.winner is not None:
            return
        if self.mode == "ai_ai" or self.player_turn == self.ai_color:
            self.cancel_ai_job()
            self.ai_job = self.root.after(AI_DELAY_MS, self.ai_turn)

    def cancel_ai_job(self):
        if self.ai_job is not None:
            self.root.after_cancel(self.ai_job)
            self.ai_job = None

    def restart_game(self):
        if self.mode is None:
            return
        self.start_new_game()

    def back_to_menu(self):
        self.game_running = False
        self.cancel_ai_job()
        if hasattr(self, "main_frame"):
            self.main_frame.destroy()
        self.mode = None
        self.create_welcome_screen()

    def stop_game(self):
        if self.winner is not None:
            return
        self.game_running = False
        self.cancel_ai_job()
        self.update_display()

    def cell_clicked(self, r, c):
        if not self.game_running or self.winner is not None:
            return
        if self.mode == "ai_ai" or self.player_turn != "r":
            return
        if self.board[r, c] != ".":
            return

        ptype = self.selected_piece_type
        if self.reserves["r"][ptype] <= 0:
            fallback = "k" if self.reserves["r"]["k"] > 0 else "c"
            if self.reserves["r"][fallback] <= 0:
                return
            self.selected_piece_type = fallback
            ptype = fallback
            self.update_display()

        self.make_move((r, c), ptype)

    def ai_turn(self):
        self.ai_job = None
        if not self.game_running or self.winner is not None:
            return

        move, ptype = ai_move(self.board, self.reserves, self.player_turn, depth=self.ai_depth)
        self.make_move(move, ptype)

    def finish_game(self, winner):
        self.cancel_ai_job()
        self.game_running = False
        self.winner = winner
        self.update_display()

    def make_move(self, move, ptype):
        if not self.game_running or self.winner is not None:
            return

        if move is None:
            self.finish_game(switch_turn(self.player_turn))
            return

        self.board, self.reserves = apply_move(
            self.board, self.reserves, move, self.player_turn, ptype
        )

        winner = check_winner(self.board, self.reserves)
        if winner is not None:
            self.finish_game(winner)
            return

        self.player_turn = switch_turn(self.player_turn)
        self.update_display()
        self.schedule_ai_turn_if_needed()


if __name__ == "__main__":
    root = tk.Tk()
    gui = BoopGUI(root)
    root.mainloop()
