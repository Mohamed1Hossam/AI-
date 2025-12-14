import tkinter as tk
from tkinter import messagebox
from typing import Callable, Dict, Any
from game.rules import GameRules
from gui.styles import StyleManager
import os


class HomePage:

    # Only these files are valid AI opponents
    VALID_ALGORITHMS = {
        'alphabeta',
        'alphabeta_heuristic',
        'minimax',
        'minimax_heuristic',
        'minimax_heuristic_reduction',
        'minimax_alphabeta'
    }

    def __init__(self, parent, start_callback: Callable[[Dict[str, Any]], None]):
        self.parent = parent
        self.start_callback = start_callback

        self.frame = tk.Frame(parent, bg=StyleManager.COLORS['bg_dark'])

        # ================= TITLE =================
        header = tk.Frame(self.frame, bg=StyleManager.COLORS['bg_dark'])
        header.pack(fill=tk.X, padx=16, pady=(16, 10))

        tk.Label(
            header,
            text="INTELLIGENT CUBIC PLAYER",
            font=("Helvetica", 28, "bold"),
            fg=StyleManager.COLORS['player'],
            bg=StyleManager.COLORS['bg_dark']
        ).pack(anchor=tk.W)

        tk.Label(
            header,
            text="4×4×4 Tic-Tac-Toe with Advanced AI",
            font=("Helvetica", 13),
            fg=StyleManager.COLORS['neutral'],
            bg=StyleManager.COLORS['bg_dark']
        ).pack(anchor=tk.W, pady=(0, 20))

        # ================= PLAYER NAME =================
        name_frame = tk.Frame(header, bg=StyleManager.COLORS['bg_dark'])
        name_frame.pack(fill=tk.X)

        tk.Label(
            name_frame,
            text="Your Name:",
            font=("Helvetica", 11, "bold"),
            fg=StyleManager.COLORS['white'],
            bg=StyleManager.COLORS['bg_dark']
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.name_var = tk.StringVar(value="Player")
        tk.Entry(
            name_frame,
            textvariable=self.name_var,
            font=("Helvetica", 12),
            width=24
        ).pack(side=tk.LEFT)

        # ================= CENTER =================
        center = tk.Frame(self.frame, bg=StyleManager.COLORS['bg_dark'])
        center.pack(expand=True, fill=tk.BOTH, padx=16, pady=12)

        tk.Label(
            center,
            text="Choose Your AI Opponent:",
            font=("Helvetica", 15, "bold"),
            fg=StyleManager.COLORS['white'],
            bg=StyleManager.COLORS['bg_dark']
        ).pack(anchor=tk.W, pady=(0, 12))

        # ================= LOAD & FILTER AI FILES =================
        project_root = os.path.dirname(os.path.dirname(__file__))
        ai_dir = os.path.join(project_root, 'ai')

        algorithms = []
        for fname in os.listdir(ai_dir):
            if not fname.endswith('.py'):
                continue
            name = fname[:-3]
            if name in self.VALID_ALGORITHMS:
                algorithms.append(name)

        algorithms.sort()

        # Grouping
        groups = {
            'AlphaBeta': [a for a in algorithms if 'alphabeta' in a],
            'Minimax': [a for a in algorithms if 'minimax' in a]
        }

        self.alg_var = tk.StringVar(value=algorithms[0])

        cards = tk.Frame(center, bg=StyleManager.COLORS['bg_dark'])
        cards.pack(fill=tk.BOTH, expand=True)

        def render_group(title, items):
            card = tk.Frame(
                cards,
                bg=StyleManager.COLORS['bg_medium'],
                bd=2,
                relief=tk.RIDGE,
                padx=12,
                pady=12
            )
            card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=6)

            tk.Label(
                card,
                text=title,
                font=("Helvetica", 14, "bold"),
                fg=StyleManager.COLORS['white'],
                bg=StyleManager.COLORS['bg_medium']
            ).pack(anchor=tk.W, pady=(0, 10))

            for alg in items:
                tk.Radiobutton(
                    card,
                    text=f"{alg}.py",
                    variable=self.alg_var,
                    value=alg,
                    font=("Helvetica", 12),
                    fg=StyleManager.COLORS['white'],
                    bg=StyleManager.COLORS['bg_medium'],
                    selectcolor=StyleManager.COLORS['bg_dark'],
                    anchor=tk.W,
                    command=self._update_heuristic_visibility
                ).pack(fill=tk.X, pady=4)

        render_group("AlphaBeta", groups['AlphaBeta'])
        render_group("Minimax", groups['Minimax'])

        # ================= HEURISTICS =================
        self.heur_frame = tk.Frame(center, bg=StyleManager.COLORS['bg_dark'])
        self.heur_frame.pack(fill=tk.X, pady=(14, 0))

        tk.Label(
            self.heur_frame,
            text="Heuristic Function:",
            font=("Helvetica", 11, "bold"),
            fg=StyleManager.COLORS['white'],
            bg=StyleManager.COLORS['bg_dark']
        ).pack(anchor=tk.W)

        self.heur_var = tk.StringVar(value="v2_positional")

        heuristics = [
            ("Basic Line Counting", "v1_basic"),
            ("Positional Strategy", "v2_positional"),
            ("Aggressive Play", "v3_aggressive")
        ]

        row = tk.Frame(self.heur_frame, bg=StyleManager.COLORS['bg_dark'])
        row.pack(anchor=tk.W, pady=6)

        for label, val in heuristics:
            tk.Radiobutton(
                row,
                text=label,
                variable=self.heur_var,
                value=val,
                bg=StyleManager.COLORS['bg_dark'],
                fg=StyleManager.COLORS['white'],
                selectcolor=StyleManager.COLORS['bg_medium']
            ).pack(side=tk.LEFT, padx=12)

        # ================= BOTTOM =================
        bottom = tk.Frame(self.frame, bg=StyleManager.COLORS['bg_dark'])
        bottom.pack(fill=tk.X, padx=16, pady=12)

        tk.Button(
            bottom,
            text="▶ START GAME",
            font=("Helvetica", 13, "bold"),
            bg=StyleManager.COLORS['success'],
            fg=StyleManager.COLORS['white'],
            padx=40,
            pady=12,
            command=self._on_start
        ).pack(side=tk.LEFT)

        tk.Button(
            bottom,
            text="VIEW RULES",
            font=("Helvetica", 10),
            bg=StyleManager.COLORS['player'],
            fg=StyleManager.COLORS['white'],
            padx=14,
            pady=8,
            command=self._show_rules
        ).pack(side=tk.RIGHT)

        self._update_heuristic_visibility()

    # ================= HELPERS =================
    def pack(self, **kwargs):
        self.frame.pack(fill=tk.BOTH, expand=True)

    def hide(self):
        self.frame.pack_forget()

    def _update_heuristic_visibility(self):
        val = self.alg_var.get().lower()
        if 'heuristic' in val or 'minimax_alphabeta' in val:
            self.heur_frame.pack(fill=tk.X, pady=(14, 0))
        else:
            self.heur_frame.pack_forget()

    def _show_rules(self):
        rules = GameRules()

        rules_text = f"""
    4×4×4 TIC-TAC-TOE – GAME RULES
    ============================

    OBJECTIVE
    ---------
    Be the first player to place FOUR marks in a straight line.

    BOARD
    -----
    • 4 layers, each a 4×4 grid
    • 64 total cells (4×4×4)
    • Each move places one mark in an empty cell

    PLAYERS
    -------
    • Human: X
    • AI: O
    • Players alternate turns

    WINNING LINES
    -------------
    A winning line can be formed in any direction:
    • Rows or columns within a layer
    • Vertical lines across layers
    • Diagonals in a 2D plane
    • Diagonals through the 3D cube

    There are {len(rules.winning_lines)} possible winning lines.

    DRAW
    ----
    If all cells are filled and no line is completed,
    the game ends in a draw.
    """
        messagebox.showinfo(
            "Game Rules – 4×4×4 Tic-Tac-Toe",
            rules_text
        )

    def _on_start(self):
        selected = self.alg_var.get()
        alg = 'AlphaBeta' if 'alphabeta' in selected else 'Minimax'

        self.start_callback({
            'player_name': self.name_var.get(),
            'algorithm': alg,
            'impl': selected,
            'heuristic': self.heur_var.get()
        })
