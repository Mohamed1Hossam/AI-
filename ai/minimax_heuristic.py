from ai.heuristics import HeuristicEvaluator
from game.board import Board
import sys
from typing import Tuple, List


class MinimaxHeuristicAI:
    """Minimax with Heuristic Evaluation"""
    
    def __init__(self, max_depth: int = 2, heuristic_version: int = 1):
        self.max_depth = max_depth
        self.heuristic_version = heuristic_version
        self.nodes_evaluated = 0
        self.max_nodes = 30000
        self.search_time = 0.0
    
    def get_best_move(self, board: Board, player: int = 2) -> Tuple[int, int, int]:
        """Get best move for the AI player"""
        self.nodes_evaluated = 0
        
        empty_cells = len(board.get_available_moves())
        if empty_cells > 50:
            depth = 1
        elif empty_cells > 30:
            depth = 2
        elif empty_cells > 15:
            depth = 3
        else:
            depth = 4
        
        depth = min(depth, self.max_depth)
        
        best_score = -sys.maxsize
        best_move = None
        
        moves = self._get_ordered_moves(board, player)
        
        for move in moves:
            z, x, y = move
            board.make_move(x, y, z, player)
            score = self._minimax(board, depth - 1, False, player)
            board.undo_move(x, y, z)
            
            if score > best_score:
                best_score = score
                best_move = move
            
            if self.nodes_evaluated > self.max_nodes:
                break
        
        if best_move is None:
            moves = board.get_available_moves()
            best_move = moves[0] if moves else None
        
        if best_move:
            return (best_move[1], best_move[2], best_move[0])
        return None
    
    def clear_cache(self):
        """Clear any caches (for compatibility)"""
        pass
    
    def _get_ordered_moves(self, board: Board, player: int) -> List[Tuple[int, int, int]]:
        """Order moves by heuristic value"""
        moves = board.get_available_moves()
        
        move_scores = []
        for move in moves:
            z, x, y = move
            board.make_move(x, y, z, player)
            
            if board.check_winner() == player:
                board.undo_move(x, y, z)
                return [move]
            
            score = self._evaluate(board, player)
            board.undo_move(x, y, z)
            move_scores.append((score, move))
        
        move_scores.sort(reverse=True, key=lambda x: x[0])
        return [move for score, move in move_scores]
    
    def _evaluate(self, board: Board, player: int) -> int:
        """Evaluate board position"""
        if self.heuristic_version == 1:
            return HeuristicEvaluator.evaluate_v1_basic(board, player)
        elif self.heuristic_version == 2:
            return HeuristicEvaluator.evaluate_v2_positional(board, player)
        else:
            return HeuristicEvaluator.evaluate_v3_aggressive(board, player)
    
    def _minimax(self, board: Board, depth: int, is_max: bool, player: int) -> int:
        """Minimax algorithm with heuristic evaluation"""
        self.nodes_evaluated += 1
        
        if self.nodes_evaluated > self.max_nodes:
            return self._evaluate(board, player)
        
        winner = board.check_winner()
        if winner == player:
            return 1000 + depth
        elif winner is not None and winner != 0:
            return -1000 - depth
        elif board.is_full() or depth == 0:
            return self._evaluate(board, player)
        
        if is_max:
            max_score = -sys.maxsize
            for move in board.get_available_moves():
                z, x, y = move
                board.make_move(x, y, z, player)
                score = self._minimax(board, depth - 1, False, player)
                board.undo_move(x, y, z)
                max_score = max(max_score, score)
                
                if max_score >= 1000:
                    break
            
            return max_score
        else:
            min_score = sys.maxsize
            opponent = 3 - player
            for move in board.get_available_moves():
                z, x, y = move
                board.make_move(x, y, z, opponent)
                score = self._minimax(board, depth - 1, True, player)
                board.undo_move(x, y, z)
                min_score = min(min_score, score)
                
                if min_score <= -1000:
                    break
            
            return min_score