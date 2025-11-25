"""
Compatibility adapter for AI expected by GUI.
Provides `AlphaBetaPruning` class used by `gui.main_window.MainWindow`.
This wrapper uses available heuristics to pick moves while exposing
`get_best_move(board)` and `clear_cache()` and `search_time` attributes.

Note: This adapter provides a lightweight, compatible interface so the
rest of the GUI can run without requiring invasive changes to algorithm
module names or signatures.
"""

import time
from typing import Optional, Tuple
from config import PLAYER_AI
from ai.heuristics import HeuristicEvaluator


class _BoardAdapter:
    """Adapter to present the board in the shapes/APIs expected by older AI modules.

    Many AI modules expect moves and indexing in (z,x,y) order and access
    `board.grid[z][x][y]`. This adapter translates those calls into the
    project's `Board` implementation which uses (x,y,z) ordering.
    """

    def __init__(self, board):
        self._b = board

    @property
    def grid(self):
        # Provide a view such that adapter.grid[z][x][y] maps to underlying [x,y,z]
        try:
            return self._b.grid.transpose((2, 0, 1))
        except Exception:
            return self._b.grid

    def get_available_moves(self):
        # Underlying board provides (z,x,y) from get_available_moves
        return self._b.get_available_moves()

    def make_move(self, z, x, y, player):
        # Translate to underlying (x,y,z)
        return self._b.make_move(x, y, z, player)

    def undo_move(self, z, x, y):
        return self._b.undo_move(x, y, z)

    def check_winner(self):
        # Return underlying winner as-is
        return self._b.check_winner()

    def is_full(self):
        return self._b.is_full()

    def get_cell(self, x, y, z):
        # Heuristics may call get_cell(x,y,z)
        return self._b.get_cell(x, y, z)


class AlphaBetaPruning:
    """Simple adapter that selects moves using heuristics and reports time.

    It intentionally avoids reimplementing or changing the project's
    original heavy algorithms; instead it provides a stable entry point
    matching the GUI's expectations (`get_best_move(board)`) so the app
    can run end-to-end. The wrapper uses the available `HeuristicEvaluator`
    to score candidate moves and returns the best.
    """

    def __init__(self, rules=None, evaluator: Optional[HeuristicEvaluator]=None,
                 max_depth: int = 3, heuristic_version: int = 2, algorithm: str = 'AlphaBetaHeuristic'):
        self.rules = rules
        self.evaluator = evaluator or HeuristicEvaluator
        self.max_depth = max_depth
        self.heuristic_version = heuristic_version
        self.algorithm = algorithm
        self.search_time = 0.0

    def clear_cache(self):
        # Compatibility method for GUI calling clear_cache
        return

    def get_best_move(self, board) -> Optional[Tuple[int, int, int]]:
        """Select and run the chosen algorithm, translating board convention when needed.

        We prefer to call the original algorithm implementations when possible by
        adapting the board interface. If import or runtime errors occur, we
        gracefully fall back to a heuristic-based selector using
        `HeuristicEvaluator` so the GUI remains functional.
        """
        start = time.time()

        # Try to use chosen algorithm implementation via adapter
        adapter = _BoardAdapter(board)

        try:
            if 'AlphaBetaHeuristic' == self.algorithm:
                from ai.alphabeta_heuristic import AlphaBetaHeuristicAI
                ai_impl = AlphaBetaHeuristicAI(max_depth=self.max_depth, heuristic_version=self.heuristic_version)
                move = ai_impl.get_best_move(adapter, 1)
                # move often is (z,x,y) -> translate to (x,y,z)
                if move is None:
                    result = None
                else:
                    mz, mx, my = move
                    result = (mx, my, mz)
            elif 'AlphaBeta' == self.algorithm:
                from ai.alphabeta import AlphaBetaAI
                ai_impl = AlphaBetaAI(max_depth=self.max_depth)
                move = ai_impl.get_best_move(adapter, 1)
                if move is None:
                    result = None
                else:
                    mz, mx, my = move
                    result = (mx, my, mz)
            elif 'Minimax' == self.algorithm:
                from ai.minimax import MinimaxAI
                ai_impl = MinimaxAI(max_depth=self.max_depth)
                move = ai_impl.get_best_move(adapter, 1)
                if move is None:
                    result = None
                else:
                    mz, mx, my = move
                    result = (mx, my, mz)
            else:
                # Unknown algorithm: fall back to heuristic scorer below
                result = None
        except Exception:
            # If anything fails, fall back to safe heuristic evaluator
            result = None

        # Fallback: use heuristic evaluator directly on main board
        if result is None:
            moves = board.get_valid_moves()
            if not moves:
                self.search_time = time.time() - start
                return None

            best_score = None
            best_move = moves[0]
            for move in moves:
                x, y, z = move
                board.make_move(x, y, z, PLAYER_AI)
                if self.heuristic_version == 1:
                    score = HeuristicEvaluator.evaluate_v1_basic(board, PLAYER_AI)
                elif self.heuristic_version == 2:
                    score = HeuristicEvaluator.evaluate_v2_positional(board, PLAYER_AI)
                else:
                    score = HeuristicEvaluator.evaluate_v3_aggressive(board, PLAYER_AI)
                board.undo_move(x, y, z)
                if best_score is None or score > best_score:
                    best_score = score
                    best_move = (x, y, z)
            result = best_move

        self.search_time = time.time() - start
        return result
