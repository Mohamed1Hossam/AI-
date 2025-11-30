"""
Main game window
"""

import tkinter as tk
from tkinter import messagebox
import threading
import time
from typing import Optional

from game.board import Board
from game.rules import GameRules
from ai.heuristics import HeuristicEvaluator
import importlib
import inspect
from gui.controls import ControlPanel
from gui.board_display import BoardDisplay
from gui.info_panel import InfoPanel
from gui.styles import StyleManager
from gui.home_page import HomePage
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, PLAYER_HUMAN, PLAYER_AI,
    DEFAULT_MAX_DEPTH
)


class MainWindow:
    """Main application window"""

    def __init__(self):
        # Create main window
        self.root = tk.Tk()
        self.root.title("Intelligent Cubic Player - 4x4x4 Tic-Tac-Toe")

        # Game state placeholders (will be initialized after Home)
        self.board = None
        self.rules = None
        self.evaluator = None
        self.ai = None

        self.current_player = PLAYER_HUMAN
        self.game_over = False
        self.ai_thinking = False
        self.move_count = 0
        self.player_turn_start: Optional[float] = None

        # Show Home Page to choose name/algorithm/heuristic
        self.home = HomePage(self.root, self._on_start_from_home)
        # Ensure home fills available window space with no unused margins
        self.home.pack(fill=tk.BOTH, expand=True)

        # Print welcome message to console
        self._print_welcome()

    def _setup_gui(self):
        """Setup all GUI components"""
        # Create main game container
        game_container = tk.Frame(self.root, bg=StyleManager.COLORS['bg_light'])
        game_container.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        # Control panel at top
        self.control_panel = ControlPanel(game_container, {
            'new_game': self._on_new_game,
            'exit': self._on_exit
        })
        self.control_panel.pack(side=tk.TOP, fill=tk.X)

        # Info panel
        self.info_panel = InfoPanel(game_container)
        self.info_panel.pack(side=tk.TOP, fill=tk.X)

        # Board display in center
        self.board_display = BoardDisplay(game_container, self._on_cell_click)
        self.board_display.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

    def _print_welcome(self):
        """Print welcome message to console"""
        print("\n" + "=" * 70)
        print("INTELLIGENT CUBIC PLAYER - 4x4x4 TIC-TAC-TOE")
        print("=" * 70)
        print("\nProject Features:")
        print("  * Minimax Algorithm with Alpha-Beta Pruning")
        print("  * Advanced Heuristic Evaluation (76 winning lines)")
        print("  * Transposition Table for Position Caching")
        print("  * Move Ordering for Better Pruning")
        print("  * Adaptive Search Depth")
        print("  * User-Friendly 3D Visualization")
        print("=" * 70 + "\n")

    def _on_start_from_home(self, options: dict):
        """Callback when Home page Start Game is pressed."""
        # Initialize game components FIRST
        self.board = Board()
        self.rules = GameRules()
        self.evaluator = HeuristicEvaluator

        hv = 2
        try:
            hv = 1 if options.get('heuristic', '').startswith('v1') else (3 if options.get('heuristic','').startswith('v3') else 2)
        except Exception:
            hv = 2

        selected_impl = options.get('impl', '')
        alg_name = options.get('algorithm', 'AlphaBetaHeuristic')

        # Try to dynamically import the selected implementation from ai.<impl>
        ai_instance = None
        if selected_impl:
            try:
                mod = importlib.import_module(f"ai.{selected_impl}")
                ai_class = None
                for name, obj in inspect.getmembers(mod, inspect.isclass):
                    if getattr(obj, '__module__', '') != mod.__name__:
                        continue
                    if hasattr(obj, 'get_best_move'):
                        ai_class = obj
                        break

                if ai_class:
                    try:
                        ai_instance = ai_class(max_depth=DEFAULT_MAX_DEPTH, heuristic_version=hv)
                    except Exception:
                        try:
                            ai_instance = ai_class(DEFAULT_MAX_DEPTH)
                        except Exception:
                            try:
                                ai_instance = ai_class()
                            except Exception:
                                ai_instance = None
            except Exception:
                ai_instance = None

        # Fallback: instantiate by algorithm name using known modules
        if ai_instance is None:
            try:
                if alg_name == 'AlphaBetaHeuristic' or alg_name == 'AlphaBeta':
                    from ai.alphabeta import AlphaBetaAI
                    ai_instance = AlphaBetaAI(DEFAULT_MAX_DEPTH)
                elif alg_name == 'Minimax':
                    from ai.minimax import MinimaxAI
                    ai_instance = MinimaxAI(DEFAULT_MAX_DEPTH)
            except Exception:
                ai_instance = None

        self.ai = ai_instance
        self.player_name = options.get('player_name', 'Player')

        # Setup GUI components now that we have game objects
        self._setup_gui()

        # Set AI label in the board display using provided options
        try:
            impl = options.get('impl', '')
            impl_map = {
                'alphabeta_heuristic': 'AlphaBeta (heuristic)',
                'alphabeta': 'AlphaBeta',
                'minimax': 'Minimax',
                'minimax_heuristic': 'Minimax (heuristic)',
                'minimax_heuristic_reduction': 'Minimax (heuristic reduction)'
            }
            alg_label = impl_map.get(impl, options.get('algorithm', 'AI'))
            heur_text = options.get('heuristic', '')
            try:
                self.board_display.set_ai_info(alg_label, heur_text)
            except Exception:
                pass
        except Exception:
            pass

        # Update initial info status
        self.info_panel.update_status(f"{self.player_name} turn", StyleManager.COLORS['player'])

        # Start measuring player's response time
        try:
            self.player_turn_start = time.time()
            self.info_panel.update_player_time(0.0)
        except Exception:
            self.player_turn_start = None

        # Hide home page LAST
        self.home.hide()

    def _on_cell_click(self, x: int, y: int, z: int):
        """Handle cell click"""
        if self.game_over or self.ai_thinking or self.current_player != PLAYER_HUMAN:
            return

        # Try to make move
        if self.board.make_move(x, y, z, PLAYER_HUMAN):
            # Measure player response time
            try:
                if self.player_turn_start is not None:
                    player_delta = time.time() - self.player_turn_start
                else:
                    player_delta = 0.0
                self.info_panel.update_player_time(player_delta)
            except Exception:
                pass
            
            self.move_count += 1
            self.info_panel.update_move_count(self.move_count)
            self.board_display.update_cell(x, y, z, PLAYER_HUMAN, False)

            # Check if game over
            winner = self.rules.check_winner(self.board)
            if winner is not None:
                self._handle_game_over(winner)
                return

            # Switch to AI turn
            self.current_player = PLAYER_AI
            self.info_panel.update_status("AI is thinking...",
                                          StyleManager.COLORS['ai'])
            self.ai_thinking = True
            self.board_display.set_all_cells_state(False)

            # Run AI in separate thread
            threading.Thread(target=self._ai_make_move, daemon=True).start()

    def _ai_make_move(self):
        """AI makes a move (runs in separate thread)"""
        time.sleep(0.3)  # Brief pause for better UX

        # Measure AI thinking time
        try:
            ai_start = time.time()
            move = self.ai.get_best_move(self.board)
            ai_end = time.time()
            self.ai.search_time = (ai_end - ai_start)
        except Exception:
            move = self.ai.get_best_move(self.board)

        if move:
            x, y, z = move
            self.board.make_move(x, y, z, PLAYER_AI)
            self.move_count += 1

            # Update GUI in main thread
            self.root.after(0, lambda: self._after_ai_move(x, y, z))

    def _after_ai_move(self, x: int, y: int, z: int):
        """Update GUI after AI move"""
        self.info_panel.update_move_count(self.move_count)
        self.info_panel.update_ai_time(self.ai.search_time)
        self.board_display.refresh_all_cells(self.board, True)

        # Check if game over
        winner = self.rules.check_winner(self.board)
        if winner is not None:
            self._handle_game_over(winner)
            return

        # Switch back to human
        self.current_player = PLAYER_HUMAN
        self.ai_thinking = False
        self.info_panel.update_status(f"{self.player_name} turn",
                                      StyleManager.COLORS['player'])
        # Start measuring player's response time
        try:
            self.player_turn_start = time.time()
        except Exception:
            self.player_turn_start = None
        self.board_display.set_all_cells_state(True)

    def _handle_game_over(self, winner: int):
        """Handle game over"""
        self.game_over = True
        self.board_display.set_all_cells_state(False)

        # Get winning line and highlight it
        winning_line = self.rules.get_winning_line()
        if winning_line:
            self.board_display.set_winning_positions(winning_line)
            self.board_display.refresh_all_cells(self.board, False)

        if winner == PLAYER_HUMAN:
            message = "*** Congratulations! You won! ***"
            self.info_panel.update_status("You Won!",
                                          StyleManager.COLORS['success'])
        elif winner == PLAYER_AI:
            message = "### AI wins! Better luck next time! ###"
            self.info_panel.update_status("AI Won!",
                                          StyleManager.COLORS['danger'])
        else:
            message = "=== It's a draw! Well played! ==="
            self.info_panel.update_status("Draw!",
                                          StyleManager.COLORS['neutral'])

        messagebox.showinfo("Game Over", message)

    def _on_new_game(self):
        """Start new game"""
        # Reset game state
        self.board.reset()
        # self.ai.clear_cache()
        self.current_player = PLAYER_HUMAN
        self.game_over = False
        self.ai_thinking = False
        self.move_count = 0
        
        # Clear winning positions
        self.board_display.set_winning_positions([])
        
        # Reset GUI
        self.info_panel.update_status(f"{self.player_name} turn",
                                      StyleManager.COLORS['player'])
        self.info_panel.update_move_count(0)
        self.info_panel.update_ai_time(0)
        self.board_display.refresh_all_cells(self.board, True)

        print("\n" + "=" * 70)
        print("NEW GAME STARTED")
        print("=" * 70 + "\n")

    def _on_exit(self):
        """Exit application"""
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.root.quit()

    def run(self):
        """Run the application"""
        self.root.mainloop()