import tkinter as tk
from gui.styles import StyleManager

class InfoPanel:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg=StyleManager.COLORS['bg_medium'],
                              padx=10, pady=10)

        self.status_label = tk.Label(
            self.frame,
            text="Game Ready - Your Turn!",
            font=StyleManager.FONT_HEADING,
            bg=StyleManager.COLORS['bg_medium'],
            fg=StyleManager.COLORS['player']
        )
        self.status_label.pack(pady=5)

        stats_frame = tk.Frame(self.frame, bg=StyleManager.COLORS['bg_medium'])
        stats_frame.pack(pady=5)

        self.move_count_label = tk.Label(
            stats_frame,
            text="Moves: 0",
            font=StyleManager.FONT_NORMAL,
            bg=StyleManager.COLORS['bg_medium'],
            fg=StyleManager.COLORS['white']
        )
        self.move_count_label.pack(side=tk.LEFT, padx=10)

        self.ai_time_label = tk.Label(
            stats_frame,
            text="AI Time: -",
            font=StyleManager.FONT_NORMAL,
            bg=StyleManager.COLORS['bg_medium'],
            fg=StyleManager.COLORS['white']
        )
        self.ai_time_label.pack(side=tk.LEFT, padx=10)

        self.player_time_label = tk.Label(
            stats_frame,
            text="Player Time: -",
            font=StyleManager.FONT_NORMAL,
            bg=StyleManager.COLORS['bg_medium'],
            fg=StyleManager.COLORS['white']
        )
        self.player_time_label.pack(side=tk.LEFT, padx=10)

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def update_status(self, text: str, color: str = None):
        self.status_label.config(text=text)
        if color:
            self.status_label.config(fg=color)

    def update_move_count(self, count: int):
        self.move_count_label.config(text=f"Moves: {count}")

    def update_ai_time(self, time: float):
        self.ai_time_label.config(text=f"AI Time: {time:.2f}s")

    def update_player_time(self, time: float):
        try:
            self.player_time_label.config(text=f"Player Time: {time:.2f}s")
        except Exception:
            self.player_time_label.config(text=f"Player Time: {time}")