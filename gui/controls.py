import tkinter as tk
from typing import Dict, Callable, Union, Any
from gui.styles import StyleManager

class ControlPanel:

    def __init__(self, parent: Union[tk.Tk, tk.Frame], callbacks: Dict[str, Callable[..., None]]):

        self.callbacks = callbacks

        # Main frame
        self.frame = tk.Frame(parent, bg=StyleManager.COLORS['bg_dark'],
                              padx=10, pady=10)

        # Title
        title = tk.Label(
            self.frame,
            text="Intelligent Cubic Player",
            font=StyleManager.FONT_TITLE,
            bg=StyleManager.COLORS['bg_dark'],
            fg=StyleManager.COLORS['white']
        )
        title.pack(pady=5)

        # Player name is entered on the Home screen; remove name entry from control panel

        # Button frame
        button_frame = tk.Frame(self.frame, bg=StyleManager.COLORS['bg_dark'])
        button_frame.pack(pady=10)

        # New Game button
        new_game_btn = tk.Button(
            button_frame,
            text="New Game",
            command=self._on_new_game,
            padx=20,
            pady=5
        )
        StyleManager.configure_button(new_game_btn, 'primary')
        new_game_btn.pack(side=tk.LEFT, padx=5)

        # Exit button
        exit_btn = tk.Button(
            button_frame,
            text="Exit",
            command=self._on_exit,
            padx=20,
            pady=5
        )
        StyleManager.configure_button(exit_btn, 'danger')
        exit_btn.pack(side=tk.LEFT, padx=5)

    def pack(self, **kwargs: Any) -> None:
        """Pack the frame"""
        self.frame.pack(**kwargs)

    def _on_name_change(self):
        """Handle name change button click"""
        if 'name_change' in self.callbacks:
            # If a name_change callback exists (legacy support), call it with default
            self.callbacks['name_change']("Player")

    def get_player_name(self) -> str:
        """Return the current player name from the entry"""
        # Legacy support: name is now provided from Home page
        return "Player"


    def _on_new_game(self):
        """Handle new game button"""
        if 'new_game' in self.callbacks:
            self.callbacks['new_game']()

    def _on_exit(self):
        """Handle exit button"""
        if 'exit' in self.callbacks:
            self.callbacks['exit']()