import sys
from typing import Tuple, List
from game.board import Board

class AlphaBetaAI:
    """Alpha-Beta Pruning Algorithm"""
    
    def __init__(self, max_depth: int = 3):
        self.max_depth = max_depth
        self.nodes_evaluated = 0
        self.pruned_branches = 0
        self.search_time = 0.0
    
    def get_best_move(self, board: Board, player: int = 2) -> Tuple[int, int, int]:
        """Get best move for the AI player"""
        self.nodes_evaluated = 0
        self.pruned_branches = 0
        
        available_moves = board.get_available_moves()
        if not available_moves:
            return None
        
        # Adaptive depth based on game state
        num_moves = len(available_moves)
        if num_moves > 50:
            depth = 2
        elif num_moves > 30:
            depth = 3
        elif num_moves > 15:
            depth = 4
        else:
            depth = min(5, self.max_depth)
        
        # Check for immediate winning move
        for move in available_moves:
            z, x, y = move
            board.make_move(x, y, z, player)
            if board.check_winner() == player:
                board.undo_move(x, y, z)
                return (x, y, z)
            board.undo_move(x, y, z)
        
        # Check for must-block opponent winning move
        opponent = 3 - player  # If player is 2, opponent is 1
        blocking_moves = []
        for move in available_moves:
            z, x, y = move
            board.make_move(x, y, z, opponent)
            if board.check_winner() == opponent:
                blocking_moves.append(move)
            board.undo_move(x, y, z)
        
        if len(blocking_moves) == 1:
            z, x, y = blocking_moves[0]
            return (x, y, z)
        elif len(blocking_moves) > 1:
            available_moves = blocking_moves
        
        # Normal alpha-beta search
        best_score = -sys.maxsize
        best_move = None
        alpha = -sys.maxsize
        beta = sys.maxsize
        
        ordered_moves = self._order_moves(board, available_moves, player)
        
        for move in ordered_moves:
            z, x, y = move
            board.make_move(x, y, z, player)
            score = self._alphabeta(board, depth - 1, alpha, beta, False, player)
            board.undo_move(x, y, z)
            
            if score > best_score:
                best_score = score
                best_move = move
                alpha = max(alpha, best_score)
        
        if best_move:
            return (best_move[1], best_move[2], best_move[0])
        else:
            return (available_moves[0][1], available_moves[0][2], available_moves[0][0])
    
    def clear_cache(self):
        """Clear any caches (for compatibility)"""
        pass
    
    def _order_moves(self, board: Board, moves: List[Tuple[int, int, int]], 
                     player: int) -> List[Tuple[int, int, int]]:
        """Order moves by strategic value for better pruning"""
        move_scores = []
        
        for move in moves:
            z, x, y = move
            center_dist = abs(z - 1.5) + abs(x - 1.5) + abs(y - 1.5)
            score = 10 - center_dist
            move_scores.append((score, move))
        
        move_scores.sort(reverse=True, key=lambda x: x[0])
        return [move for _, move in move_scores]
    
    def _alphabeta(self, board: Board, depth: int, alpha: int, beta: int,
                   is_max: bool, player: int) -> int:
        """Alpha-beta pruning algorithm"""
        self.nodes_evaluated += 1
        
        winner = board.check_winner()
        if winner == player:
            return 1000 + depth
        elif winner is not None and winner != 0:
            return -1000 - depth
        elif board.is_full() or depth == 0:
            return 0
        
        if is_max:
            max_score = -sys.maxsize
            for move in board.get_available_moves():
                z, x, y = move
                board.make_move(x, y, z, player)
                score = self._alphabeta(board, depth - 1, alpha, beta, False, player)
                board.undo_move(x, y, z)
                
                max_score = max(max_score, score)
                alpha = max(alpha, score)
                if beta <= alpha:
                    self.pruned_branches += 1
                    break
            return max_score
        else:
            min_score = sys.maxsize
            opponent = 3 - player
            for move in board.get_available_moves():
                z, x, y = move
                board.make_move(x, y, z, opponent)
                score = self._alphabeta(board, depth - 1, alpha, beta, True, player)
                board.undo_move(x, y, z)
                
                min_score = min(min_score, score)
                beta = min(beta, score)
                if beta <= alpha:
                    self.pruned_branches += 1
                    break
            return min_score