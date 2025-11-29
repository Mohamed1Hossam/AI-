from typing import Tuple
from game.board import Board
from ai.heuristics import HeuristicEvaluator

class AlphaBetaHeuristicAI:

    
    def __init__(self, max_depth: int = 3, heuristic_version: int = 2):
        self.max_depth = max_depth
        self.heuristic_version = heuristic_version
    
    def get_best_move(self, board: Board, player: int = 2) -> Tuple[int, int, int]:

        available_moves = board.get_available_moves()
        if not available_moves:
            return None
     
        num_moves = len(available_moves)
        if num_moves > 50:
            depth = 2
        elif num_moves > 35:
            depth = 3
        elif num_moves > 20:
            depth = 4
        else:
            depth = min(5, self.max_depth)
        
     
        for z, x, y in available_moves:
            board.make_move(x, y, z, player)
            if board.check_winner() == player:
                board.undo_move(x, y, z)
                return (x, y, z)
            board.undo_move(x, y, z)
        
    
        opponent = 3 - player
        for z, x, y in available_moves:
            board.make_move(x, y, z, opponent)
            if board.check_winner() == opponent:
                board.undo_move(x, y, z)
                return (x, y, z)
            board.undo_move(x, y, z)
        

        max_moves = min(25, num_moves)
        search_moves = available_moves[:max_moves]
        
        # Find best move using alpha-beta
        best_score = -999999
        best_move = search_moves[0]
        alpha = -999999
        beta = 999999
        
        for z, x, y in search_moves:
            board.make_move(x, y, z, player)
            score = self._alphabeta(board, depth - 1, alpha, beta, False, player)
            board.undo_move(x, y, z)
            
            if score > best_score:
                best_score = score
                best_move = (x, y, z)
                alpha = max(alpha, best_score)
            
            if best_score >= 900:
                break
        
        return best_move
    
    def _evaluate(self, board: Board, player: int) -> int:
     
        if self.heuristic_version == 1:
            return HeuristicEvaluator.evaluate_v1_basic(board, player)
        elif self.heuristic_version == 2:
            return HeuristicEvaluator.evaluate_v2_positional(board, player)
        else:
            return HeuristicEvaluator.evaluate_v3_aggressive(board, player)
    
    def _alphabeta(self, board: Board, depth: int, alpha: int, beta: int,
                   is_max: bool, player: int) -> int:
      
        # Check terminal states
        winner = board.check_winner()
        if winner == player:
            return 1000 + depth
        elif winner is not None and winner != 0:
            return -1000 - depth
        elif board.is_full() or depth == 0:
            return self._evaluate(board, player)
        
        opponent = 3 - player
        moves = board.get_available_moves()



        if depth <= 2 and len(moves) > 20:
            moves = moves[:20]


        
        if is_max:
            max_score = -999999
            for z, x, y in moves:
                board.make_move(x, y, z, player)
                score = self._alphabeta(board, depth - 1, alpha, beta, False, player)
                board.undo_move(x, y, z)
                
                max_score = max(max_score, score)
                alpha = max(alpha, score)
                
                if beta <= alpha:
                    break  # Beta cutoff
            return max_score
        else:
            min_score = 999999
            for z, x, y in moves:
                board.make_move(x, y, z, opponent)
                score = self._alphabeta(board, depth - 1, alpha, beta, True, player)
                board.undo_move(x, y, z)
                
                min_score = min(min_score, score)
                beta = min(beta, score)
                
                if beta <= alpha:
                    break  # Alpha cutoff
            return min_score