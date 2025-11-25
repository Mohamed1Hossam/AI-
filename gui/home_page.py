"""
Home page UI for selecting player name, viewing rules, and choosing algorithm.
Modern design with card-based algorithm selection and bottom-right rules button.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Callable, Dict, Any
from game.rules import GameRules
from gui.styles import StyleManager


class HomePage:
    """Modern home page with card-based design and better visual hierarchy."""

    def __init__(self, parent, start_callback: Callable[[Dict[str, Any]], None]):
        self.parent = parent
        self.start_callback = start_callback

        # Main container with background that will expand to fill window
        self.frame = tk.Frame(parent, bg=StyleManager.COLORS['bg_dark'])

        # Top section: Title and player name
        top_section = tk.Frame(self.frame, bg=StyleManager.COLORS['bg_dark'])
        top_section.pack(fill=tk.X, padx=12, pady=(12, 0))

        title = tk.Label(
            top_section,
            text="INTELLIGENT CUBIC PLAYER",
            font=("Helvetica", 28, "bold"),
            bg=StyleManager.COLORS['bg_dark'],
            fg=StyleManager.COLORS['player']
        )
        title.pack(anchor=tk.W, pady=(0, 5))

        subtitle = tk.Label(
            top_section,
            text="4×4×4 Tic-Tac-Toe with Advanced AI",
            font=("Helvetica", 13),
            bg=StyleManager.COLORS['bg_dark'],
            fg=StyleManager.COLORS['neutral']
        )
        subtitle.pack(anchor=tk.W, pady=(0, 20))

        # Player name input
        name_section = tk.Frame(top_section, bg=StyleManager.COLORS['bg_dark'])
        name_section.pack(fill=tk.X, pady=(0, 12))

        name_label = tk.Label(
            name_section,
            text="Your Name:",
            font=("Helvetica", 11, "bold"),
            bg=StyleManager.COLORS['bg_dark'],
            fg=StyleManager.COLORS['white']
        )
        name_label.pack(side=tk.LEFT, padx=(0, 10))

        self.name_var = tk.StringVar(value="Player")
        name_entry = tk.Entry(
            name_section,
            textvariable=self.name_var,
            font=("Helvetica", 12),
            width=25,
            relief=tk.SUNKEN,
            bd=2
        )
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Center section: Algorithm cards
        center_section = tk.Frame(self.frame, bg=StyleManager.COLORS['bg_dark'])
        center_section.pack(expand=True, fill=tk.BOTH, padx=12, pady=12)

        alg_title = tk.Label(
            center_section,
            text="Choose Your AI Opponent:",
            font=("Helvetica", 14, "bold"),
            bg=StyleManager.COLORS['bg_dark'],
            fg=StyleManager.COLORS['white']
        )
        alg_title.pack(anchor=tk.W, pady=(0, 15))

        # Algorithm cards container
        cards_frame = tk.Frame(center_section, bg=StyleManager.COLORS['bg_dark'])
        cards_frame.pack(fill=tk.BOTH, expand=True)

        self.alg_var = tk.StringVar(value="AlphaBetaHeuristic")
        self.cards = []

        algorithms = [
            ("AlphaBeta + Heuristic", "Combines alpha-beta pruning\nwith smart evaluation", "AlphaBetaHeuristic"),
            ("AlphaBeta Pruning", "Efficient game tree search\nwith branch elimination", "AlphaBeta"),
            ("Minimax", "Classic minimax algorithm\nwith full depth search", "Minimax")
        ]

        for alg_name, desc, value in algorithms:
            card_frame = tk.Frame(cards_frame, bg=StyleManager.COLORS['bg_medium'], relief=tk.RAISED, bd=2, padx=12, pady=12)
            card_frame.pack(side=tk.LEFT, padx=6, fill=tk.BOTH, expand=True, pady=6)

            card_title = tk.Label(
                card_frame,
                text=alg_name,
                font=("Helvetica", 11, "bold"),
                bg=StyleManager.COLORS['bg_medium'],
                fg=StyleManager.COLORS['white']
            )
            card_title.pack(pady=(0, 8))

            card_desc = tk.Label(
                card_frame,
                text=desc,
                font=("Helvetica", 9),
                bg=StyleManager.COLORS['bg_medium'],
                fg=StyleManager.COLORS['neutral'],
                wraplength=140,
                justify=tk.CENTER
            )
            card_desc.pack(pady=(0, 12), expand=True)

            rb = tk.Radiobutton(
                card_frame,
                text="Select",
                variable=self.alg_var,
                value=value,
                font=("Helvetica", 10),
                bg=StyleManager.COLORS['bg_medium'],
                fg=StyleManager.COLORS['player'],
                selectcolor=StyleManager.COLORS['bg_medium'],
                pady=4,
                command=self._update_heuristic_visibility
            )
            rb.pack()

            self.cards.append((card_frame, rb, value))

        # Heuristic selection (only for heuristic algorithm)
        self.heur_frame = tk.Frame(center_section, bg=StyleManager.COLORS['bg_dark'])
        self.heur_frame.pack(fill=tk.X, pady=(12, 0))

        self.heur_label = tk.Label(
            self.heur_frame,
            text="Heuristic Function:",
            font=("Helvetica", 11, "bold"),
            bg=StyleManager.COLORS['bg_dark'],
            fg=StyleManager.COLORS['white']
        )
        self.heur_label.pack(anchor=tk.W, pady=(0, 8))

        heur_radio_frame = tk.Frame(self.heur_frame, bg=StyleManager.COLORS['bg_dark'])
        heur_radio_frame.pack(anchor=tk.W, fill=tk.X)

        self.heur_var = tk.StringVar(value="v2_positional")
        heur_options = [
            ("Basic Line Counting", "v1_basic"),
            ("Positional Strategy", "v2_positional"),
            ("Aggressive Play", "v3_aggressive")
        ]

        for label_text, value in heur_options:
            rb = tk.Radiobutton(
                heur_radio_frame,
                text=label_text,
                variable=self.heur_var,
                value=value,
                font=("Helvetica", 10),
                bg=StyleManager.COLORS['bg_dark'],
                fg=StyleManager.COLORS['white'],
                selectcolor=StyleManager.COLORS['bg_medium'],
                pady=3
            )
            rb.pack(side=tk.LEFT, padx=(0, 20))

        # Bottom section: Start button and rules icon
        bottom_section = tk.Frame(self.frame, bg=StyleManager.COLORS['bg_dark'])
        bottom_section.pack(fill=tk.X, padx=12, pady=(0, 12))

        # Start button (left side)
        start_btn = tk.Button(
            bottom_section,
            text="▶  START GAME",
            command=self._on_start,
            font=("Helvetica", 13, "bold"),
            padx=40,
            pady=12,
            bg=StyleManager.COLORS['success'],
            fg=StyleManager.COLORS['white'],
            relief=tk.RAISED,
            bd=2,
            cursor="hand2"
        )
        start_btn.pack(side=tk.LEFT, padx=(0, 20))

        # Rules info button (right side - bottom-right corner effect)
        rules_btn = tk.Button(
            bottom_section,
            text="?  VIEW RULES",
            command=self._show_rules,
            font=("Helvetica", 10),
            padx=12,
            pady=8,
            bg=StyleManager.COLORS['player'],
            fg=StyleManager.COLORS['white'],
            relief=tk.RAISED,
            bd=1,
            cursor="hand2"
        )
        rules_btn.pack(side=tk.RIGHT)

        # Initial state
        self._update_heuristic_visibility()

    def pack(self, **kwargs):
        # Default to filling both directions so the home page uses all available space
        if 'fill' not in kwargs and 'expand' not in kwargs:
            self.frame.pack(fill=tk.BOTH, expand=True)
        else:
            self.frame.pack(**kwargs)

    def hide(self):
        self.frame.pack_forget()

    def _update_heuristic_visibility(self):
        """Show/hide heuristic selection based on algorithm."""
        if self.alg_var.get() == "AlphaBetaHeuristic":
            self.heur_frame.pack(fill=tk.X, pady=(15, 0))
            self.heur_label.config(state=tk.NORMAL, fg=StyleManager.COLORS['white'])
        else:
            self.heur_frame.pack_forget()

    def _show_rules(self):
        """Show detailed rules in a popup."""
        rules = GameRules()
        text = f"""
GAME RULES - 4×4×4 TIC-TAC-TOE

OBJECTIVE:
Get 4 of your marks in a row to win!

BOARD STRUCTURE:
• 4 layers displayed as 4×4 tables (64 total cells)
• {len(rules.winning_lines)} possible winning lines

WINNING LINES INCLUDE:
✓ Rows (4 horizontal cells)
✓ Columns (4 vertical cells)  
✓ Pillars (4 depth cells)
✓ Plane diagonals (4 diagonal cells in 2D)
✓ Space diagonals (4 diagonal cells in 3D)

HOW TO PLAY:
1. Enter your name at the top
2. Choose which AI opponent to play
3. Click START GAME to begin
4. Click on any empty cell to place your mark (X)
5. AI will automatically place its mark (O)
6. First to get 4 in a row wins!

GAMEPLAY INTERFACE:
• Move Counter: Tracks total moves made
• AI Time: Shows how long AI takes to decide
• Turn Indicator: Shows whose turn it is
• Four 4×4 layers: All game boards visible at once

TIPS FOR WINNING:
• Focus on the center - it's strategically important
• Create multiple winning threats to limit AI options
• Block the AI's potential winning lines
• Watch for 3-in-a-row patterns from the AI
• Use the 3D nature - threats can come from many directions
"""
        messagebox.showinfo("Game Rules - 4×4×4 Tic-Tac-Toe", text)

    def _on_start(self):
        """Trigger game start with selected options."""
        opts = {
            'player_name': self.name_var.get().strip() or "Player",
            'algorithm': self.alg_var.get(),
            'heuristic': self.heur_var.get()
        }
        self.start_callback(opts)
