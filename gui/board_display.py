"""
Board display widget
"""

import tkinter as tk
from typing import Callable, Optional
from gui.styles import StyleManager
from config import BOARD_SIZE, BUTTON_WIDTH, BUTTON_HEIGHT

class BoardDisplay:
    """Displays the 4x4x4 game board with multiple layers"""

    def __init__(self, parent, on_cell_click: Callable):
        """
        Args:
            parent: Parent widget
            on_cell_click: Callback for cell click (x, y, z)
        """
        from config import LAYERS_TO_SHOW
        self.on_cell_click = on_cell_click
        self.current_layer = 0
        self.layers_to_show = LAYERS_TO_SHOW

        # Main frame
        self.frame = tk.Frame(parent, bg=StyleManager.COLORS['bg_light'])
        
        # Container for AI info and layers; center its contents
        self.layers_frame = tk.Frame(self.frame, bg=StyleManager.COLORS['bg_light'])
        self.layers_frame.pack(expand=True, fill=tk.BOTH, padx=6, pady=6)

        # AI info label (shows which algorithm is used)
        self.ai_info_label = tk.Label(
            self.layers_frame,
            text="AI: (not set)",
            font=StyleManager.FONT_NORMAL,
            bg=StyleManager.COLORS['bg_light'],
            fg=StyleManager.COLORS['neutral']
        )
        # Place AI info at the top center
        self.ai_info_label.pack(anchor='n', pady=(8, 6))
        
        # Create frames for each visible layer
        self.layer_frames = []
        self.layer_labels = []
        # Create a centered container for the horizontal layout of layers
        self.center_layers = tk.Frame(self.layers_frame, bg=StyleManager.COLORS['bg_light'])
        self.center_layers.pack(expand=False)

        for i in range(self.layers_to_show):
            layer_frame = tk.Frame(self.center_layers, bg=StyleManager.COLORS['bg_light'])
            layer_frame.grid(row=0, column=i, padx=8, pady=8)
            
            # Layer title
            layer_label = tk.Label(
                layer_frame,
                text=f"Layer {i+1} (Z = {i+1})",
                font=StyleManager.FONT_HEADING,
                bg=StyleManager.COLORS['bg_light']
            )
            layer_label.grid(row=0, column=0, columnspan=BOARD_SIZE, pady=10)
            
            self.layer_frames.append(layer_frame)
            self.layer_labels.append(layer_label)

        # Create button grid
        self.buttons = {}
        self._create_grid()

    def _create_grid(self):
        """Create the button grid for all visible layers"""
        for layer_idx in range(self.layers_to_show):
            frame = self.layer_frames[layer_idx]
            for x in range(BOARD_SIZE):
                for y in range(BOARD_SIZE):
                    btn = tk.Button(
                        frame,
                        text="",
                        width=BUTTON_WIDTH,
                        height=BUTTON_HEIGHT,
                        command=lambda x=x, y=y, z=layer_idx: self.on_cell_click(x, y, z)
                    )
                    StyleManager.configure_button(btn, 'cell')
                    btn.grid(row=x + 1, column=y, padx=2, pady=2)
                    self.buttons[(x, y, layer_idx)] = btn

    def _cell_clicked(self, x: int, y: int):
        """Handle cell click (deprecated)"""
        # Kept for compatibility; new buttons pass z directly.
        self.on_cell_click(x, y, self.current_layer)

    def pack(self, **kwargs):
        """Pack the frame"""
        # Default to center the board display in its parent
        if 'fill' not in kwargs and 'expand' not in kwargs:
            self.frame.pack(fill=tk.BOTH, expand=True)
        else:
            self.frame.pack(**kwargs)

    def set_ai_info(self, algorithm_name: str, heuristic: str = ""):
        """Set the AI algorithm information shown on the gameplay page."""
        text = f"AI: {algorithm_name}"
        if heuristic:
            text += f" ({heuristic})"
        self.ai_info_label.config(text=text)

    def set_layer(self, layer: int):
        """Change displayed layer"""
        # Multi-layer view: explicit layer switching is deprecated.
        return

    def _refresh_grid(self):
        """Refresh the button grid"""
        # Not used in multi-layer layout
        return

    def update_cell(self, x: int, y: int, z: int, player: int, enabled: bool = True):
        """
        Update a cell's appearance

        Args:
            x, y, z: Position
            player: Player ID (0=empty, 1=human, 2=AI)
            enabled: Whether cell is clickable
        """
        btn = self.buttons.get((x, y, z))
        if btn:
            if player == 0:
                btn.config(
                    text="",
                    bg=StyleManager.COLORS['white'],
                    state=tk.NORMAL if enabled else tk.DISABLED
                )
            else:
                color = StyleManager.get_player_color(player)
                # Use X for player and O for AI
                text = "X" if player == 1 else "O"
                btn.config(
                    text=text,
                    bg=color,
                    fg=StyleManager.COLORS['white'],
                    state=tk.DISABLED
                )

    def set_all_cells_state(self, enabled: bool):
        """Enable or disable all cells"""
        state = tk.NORMAL if enabled else tk.DISABLED
        for btn in self.buttons.values():
            if btn.cget('text') == "":  # Only affect empty cells
                btn.config(state=state)

    def refresh_all_cells(self, board, enabled: bool = True):
        """Refresh all cells from board state"""
        for z in range(self.layers_to_show):
            for x in range(BOARD_SIZE):
                for y in range(BOARD_SIZE):
                    player = board.get_cell(x, y, z)
                    self.update_cell(x, y, z, player, enabled)