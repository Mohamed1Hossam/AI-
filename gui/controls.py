import tkinter as tk
from typing import Dict, Callable, Union, Any
from gui.styles import StyleManager

class ControlPanel:
    def __init__(self, parent: Union[tk.Tk, tk.Frame], callbacks: Dict[str, Callable[..., None]]):
        self.callbacks = callbacks

        self.frame = tk.Frame(parent, bg=StyleManager.COLORS['bg_dark'],
                              padx=10, pady=10)

        title = tk.Label(
            self.frame,
            text="Intelligent Cubic Player",
            font=StyleManager.FONT_TITLE,
            bg=StyleManager.COLORS['bg_dark'],
            fg=StyleManager.COLORS['white']
        )
        title.pack(pady=5)


        button_frame = tk.Frame(self.frame, bg=StyleManager.COLORS['bg_dark'])
        button_frame.pack(pady=10)

        new_game_btn = tk.Button(
            button_frame,
            text="New Game",
            command=self._on_new_game,
            padx=20,
            pady=5
        )
        StyleManager.configure_button(new_game_btn, 'primary')
        new_game_btn.pack(side=tk.LEFT, padx=5)

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
        self.frame.pack(**kwargs)

    def _on_name_change(self):
        if 'name_change' in self.callbacks:
            self.callbacks['name_change']("Player")

    def get_player_name(self) -> str:
        return "Player"

    def _on_new_game(self):
        if 'new_game' in self.callbacks:
            self.callbacks['new_game']()

    def _on_exit(self):
        if 'exit' in self.callbacks:
            self.callbacks['exit']()