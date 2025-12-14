from typing import Tuple, Optional
from game.board import Board
from ai.minimax import MinimaxAI
from ai.alphabeta import AlphaBetaAI


class MinimaxAlphaBetaAI:
    """
    Hybrid AI:
    - Uses Minimax when branching factor is large
    - Switches to Alpha-Beta when the board becomes smaller
    """

    def __init__(
        self,
        max_depth: int = 3,
        switch_depth: int = 2,
        heuristic_version: int = 2
    ):
        self.max_depth = max_depth
        self.switch_depth = switch_depth
        self.heuristic_version = heuristic_version

        self.minimax_ai = MinimaxAI(
            max_depth=max_depth,
            heuristic_version=heuristic_version
        )

        self.alphabeta_ai = AlphaBetaAI(
            max_depth=max_depth,
            heuristic_version=heuristic_version
        )

        self.search_time = 0.0

    def get_best_move(
        self,
        board: Board,
        player: int = 2
    ) -> Optional[Tuple[int, int, int]]:

        available_moves = board.get_available_moves()
        if not available_moves:
            return None

        # Large branching → Minimax
        if len(available_moves) > 35:
            return self.minimax_ai.get_best_move(board, player)

        # Smaller branching → Alpha-Beta
        return self.alphabeta_ai.get_best_move(board, player)
