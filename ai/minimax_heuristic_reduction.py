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

def _evaluate(self, board, player):
    if self.heuristic_version == 1:
        return HeuristicEvaluator.evaluate_v1_basic(board, player)
    elif self.heuristic_version == 2:
        return HeuristicEvaluator.evaluate_v2_positional(board, player)
    else:
        return HeuristicEvaluator.evaluate_v3_aggressive(board, player)

def _apply_reductions(self, move_scores):
    """
    Reduce number of moves using:
    1. Keep Top-K based on heuristic (Heuristic Reduction)
    2. Remove symmetric moves (Symmetry Reduction)
    3. Remove clearly bad moves (Threshold Filtering)
    """
    if not move_scores:
        return move_scores

    # ---------------------------
    # 1️⃣ Heuristic Top-K Reduction
    # ---------------------------

    # Sort high → low
    move_scores.sort(reverse=True, key=lambda x: x[0])

    K = 8  # keep only best 8 moves
    reduced = move_scores[:K]

    # ---------------------------
    # 2️⃣ Remove symmetric moves
    # ---------------------------
    seen = set()
    unique_moves = []

    for score, move in reduced:
        z, x, y = move

        # Generate symmetry signatures
        sym1 = (z, x, y)
        sym2 = (z, y, x)        # reflection
        sym3 = (z, 3 - x, y)    # flip x
        sym4 = (z, x, 3 - y)    # flip y

        signature = min(sym1, sym2, sym3, sym4)

        if signature not in seen:
            seen.add(signature)
            unique_moves.append((score, move))

    reduced = unique_moves

    # ---------------------------
    # 3️⃣ Threshold Filtering
    # Remove moves too weak
    # ---------------------------
    if len(reduced) > 4:
        best_score = reduced[0][0]
        threshold = best_score * 0.5  # keep moves >= 50% of best score
        reduced = [(s, m) for (s, m) in reduced if s >= threshold]

    # Ensure at least 3 moves remain
    if len(reduced) < 3:
        reduced = move_scores[:3]

    return reduced
