from ai.heuristics import HeuristicEvaluator
from game.board import Board
import sys
from typing import Tuple, List


class MinimaxHeuristicAI:
    """Optimized Minimax with Heuristic Evaluation"""
    
    def __init__(self, max_depth: int = 2, heuristic_version: int = 1):
        # Reduced default depth from 4 to 2 (Minimax is slower than Alpha-Beta)
        self.max_depth = max_depth
        self.heuristic_version = heuristic_version
        self.nodes_evaluated = 0
        self.max_nodes = 30000  # Lower limit for Minimax (it's slower)
    
    def get_best_move(self, board: Board, player: int) -> Tuple[int, int, int]:
        self.nodes_evaluated = 0
        
        # Adaptive depth based on game state
        empty_cells = len(board.get_available_moves())
        if empty_cells > 50:
            depth = 1  # Very early game
        elif empty_cells > 30:
            depth = 2  # Early-mid game
        elif empty_cells > 15:
            depth = 3  # Mid-late game
        else:
            depth = 4  # End game
        
        depth = min(depth, self.max_depth)
        
        best_score = -sys.maxsize
        best_move = None
        
        # Order moves by heuristic for better performance
        moves = self._get_ordered_moves(board, player)
        
        for move in moves:
            z, x, y = move
            board.make_move(z, x, y, player)
            score = self._minimax(board, depth - 1, False, player)
            board.undo_move(z, x, y)
            
            if score > best_score:
                best_score = score
                best_move = move
            
            # Safety check
            if self.nodes_evaluated > self.max_nodes:
                print(f"Warning: Node limit reached ({self.max_nodes})")
                break
        
        if best_move is None:
            moves = board.get_available_moves()
            best_move = moves[0] if moves else None
        
        return best_move
    
    def _get_ordered_moves(self, board: Board, player: int) -> List[Tuple[int, int, int]]:
        """Order moves by heuristic value for better performance"""
        moves = board.get_available_moves()
        
        # Quick evaluation of each move
        move_scores = []
        for move in moves:
            z, x, y = move
            board.make_move(z, x, y, player)
            
            # Check for immediate win
            if board.check_winner() == player:
                board.undo_move(z, x, y)
                return [move]  # Return immediately if winning move found
            
            score = self._evaluate(board, player)
            board.undo_move(z, x, y)
            move_scores.append((score, move))
        
        # Sort moves by score (best first)
        move_scores.sort(reverse=True, key=lambda x: x[0])
        return [move for score, move in move_scores]
    
    def _evaluate(self, board: Board, player: int) -> int:
        if self.heuristic_version == 1:
            return HeuristicEvaluator.evaluate_v1_basic(board, player)
        elif self.heuristic_version == 2:
            return HeuristicEvaluator.evaluate_v2_positional(board, player)
        else:
            return HeuristicEvaluator.evaluate_v3_aggressive(board, player)
    
    def _minimax(self, board: Board, depth: int, is_max: bool, player: int) -> int:
        self.nodes_evaluated += 1
        
        # Safety check to prevent excessive computation
        if self.nodes_evaluated > self.max_nodes:
            return self._evaluate(board, player)
        
        # Terminal state checks
        winner = board.check_winner()
        if winner == player:
            return 1000 + depth  # Prefer faster wins
        elif winner is not None:
            return -1000 - depth  # Prefer slower losses
        elif board.is_full() or depth == 0:
            return self._evaluate(board, player)
        
        if is_max:
            max_score = -sys.maxsize
            for move in board.get_available_moves():
                z, x, y = move
                board.make_move(z, x, y, player)
                score = self._minimax(board, depth - 1, False, player)
                board.undo_move(z, x, y)
                max_score = max(max_score, score)
                
                # Early termination if we find a winning move
                if max_score >= 1000:
                    break
            
            return max_score
        else:
            min_score = sys.maxsize
            for move in board.get_available_moves():
                z, x, y = move
                board.make_move(z, x, y, -player)
                score = self._minimax(board, depth - 1, True, player)
                board.undo_move(z, x, y)
                min_score = min(min_score, score)
                
                # Early termination if opponent finds a winning move
                if min_score <= -1000:
                    break
            
            return min_score