import sys
from typing import Tuple, List
from ai.heuristics import HeuristicEvaluator
from game.board import Board

class MinimaxHeuristicReductionAI:
    """Minimax with Heuristic Evaluation and Move Reduction"""
    
    def __init__(self, max_depth: int = 2, heuristic_version: int = 1):
        self.max_depth = max_depth
        self.heuristic_version = heuristic_version
        self.nodes_evaluated = 0
        self.max_nodes = 30000
        self.search_time = 0.0

    def get_best_move(self, board: Board, player: int = 2) -> Tuple[int, int, int]:
        """Get best move for the AI player"""
        self.nodes_evaluated = 0
        
        available_moves = board.get_available_moves()
        if not available_moves:
            return None
        
        # Adaptive depth
        num_moves = len(available_moves)
        if num_moves > 50:
            depth = 1
        elif num_moves > 30:
            depth = 2
        elif num_moves > 15:
            depth = 3
        else:
            depth = min(4, self.max_depth)
        
        # Check for immediate winning move
        for move in available_moves:
            z, x, y = move
            board.make_move(x, y, z, player)
            if board.check_winner() == player:
                board.undo_move(x, y, z)
                return (x, y, z)
            board.undo_move(x, y, z)
        
        # Check for blocking opponent's winning move
        opponent = 3 - player  # If player is 2, opponent is 1; if player is 1, opponent is 2
        for move in available_moves:
            z, x, y = move
            board.make_move(x, y, z, opponent)
            if board.check_winner() == opponent:
                board.undo_move(x, y, z)
                return (x, y, z)
            board.undo_move(x, y, z)
        
        # Get ordered moves with reductions
        moves = self._get_ordered_moves(board, player)
        
        if not moves:
            return (available_moves[0][1], available_moves[0][2], available_moves[0][0])
        
        best_score = -sys.maxsize
        best_move = moves[0]
        
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
        
        # Convert from (z, x, y) to (x, y, z) format
        return (best_move[1], best_move[2], best_move[0])

    def clear_cache(self):
        """Clear any caches (for compatibility)"""
        pass

    def _get_ordered_moves(self, board: Board, player: int) -> List[Tuple[int, int, int]]:
        """Order moves using heuristic + reductions"""
        moves = board.get_available_moves()
        
        if not moves:
            return []
        
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
        
        move_scores = self._apply_reductions(move_scores)
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

    def _apply_reductions(self, move_scores: List[Tuple[int, Tuple]]) -> List[Tuple[int, Tuple]]:
        """Reduce number of moves using heuristic filtering"""
        if not move_scores:
            return move_scores
        
        move_scores.sort(reverse=True, key=lambda x: x[0])
        
        K = 8
        reduced = move_scores[:K]
        
        seen = set()
        unique_moves = []
        
        for score, move in reduced:
            z, x, y = move
            
            sym1 = (z, x, y)
            sym2 = (z, y, x)
            sym3 = (z, 3 - x, y)
            sym4 = (z, x, 3 - y)
            
            signature = min(sym1, sym2, sym3, sym4)
            
            if signature not in seen:
                seen.add(signature)
                unique_moves.append((score, move))
        
        reduced = unique_moves
        
        if len(reduced) > 4:
            best_score = reduced[0][0]
            threshold = best_score * 0.5
            reduced = [(s, m) for (s, m) in reduced if s >= threshold]
        
        if len(reduced) < 3:
            reduced = move_scores[:3]
        
        return reduced

    def _minimax(self, board: Board, depth: int, is_max: bool, player: int) -> int:
        """Minimax algorithm"""
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