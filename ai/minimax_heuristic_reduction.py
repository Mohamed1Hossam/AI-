import sys
from typing import Tuple, List
from ai.heuristics import HeuristicEvaluator
from game.board import Board

class MinimaxHeuristicReductionAI:
    def __init__(self, max_depth: int = 2, heuristic_version: int = 1):
        self.max_depth = max_depth
        self.heuristic_version = heuristic_version
        self.nodes_evaluated = 0
        self.max_nodes = 30000  # Lower limit for Minimax (it's slower)

def _get_ordered_moves(self, board: Board, player: int) -> List[Tuple[int, int, int]]:
    """Order moves using heuristic + reductions"""
    moves = board.get_available_moves()

    # If no moves, return empty
    if not moves:
        return []

    move_scores = []

    # Evaluate all moves
    for move in moves:
        z, x, y = move
        board.make_move(z, x, y, player)

        # Immediate win shortcut
        if board.check_winner() == player:
            board.undo_move(z, x, y)
            return [move]

        score = self._evaluate(board, player)

        board.undo_move(z, x, y)
        move_scores.append((score, move))

    # STEP 1: apply reduction BEFORE sorting
    move_scores = self._apply_reductions(move_scores)

    # Sort moves: best first
    move_scores.sort(reverse=True, key=lambda x: x[0])

    # Return only moves
    return [move for score, move in move_scores]
