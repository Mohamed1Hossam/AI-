from typing import Tuple
from game.board import Board

class MinimaxAI:

    
    def __init__(self, max_depth: int = 3):
        self.max_depth = max_depth
    
    def get_best_move(self, board: Board, player: int = 2) -> Tuple[int, int, int]:
        available_moves = board.get_available_moves()
        if not available_moves:
            return None
        
        num_moves = len(available_moves)
        if num_moves > 50:
            depth = 1
        elif num_moves > 35:
            depth = 2
        elif num_moves > 20:
            depth = 3
        else:
            depth = 4

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
        

        max_moves = min(20, num_moves)
        search_moves = available_moves[:max_moves]
        

        best_score = -999999
        best_move = search_moves[0]
        
        for z, x, y in search_moves:
            board.make_move(x, y, z, player)
            score = self._minimax(board, depth - 1, False, player)
            board.undo_move(x, y, z)
            
            if score > best_score:
                best_score = score
                best_move = (x, y, z)
        
        return best_move
    
    def _minimax(self, board: Board, depth: int, is_max: bool, player: int) -> int:

        winner = board.check_winner()
        if winner == player:
            return 100 + depth
        elif winner is not None and winner != 0:
            return -100 - depth
        elif board.is_full() or depth == 0:
            return 0
        
        opponent = 3 - player
        moves = board.get_available_moves()
 
        if depth <= 2:
            moves = moves[:15]
        
        if is_max:
            best_score = -999999
         
            for z, x, y in moves:
                board.make_move(x, y, z, player)
                score = self._minimax(board, depth - 1, False, player)
                board.undo_move(x, y, z)
                
                best_score = max(best_score, score)
           
       
            return best_score
        else:
            best_score = 999999
    
            for z, x, y in moves:
                board.make_move(x, y, z, opponent)
                score = self._minimax(board, depth - 1, True, player)
                board.undo_move(x, y, z)
                
                best_score = min(best_score, score)
         
            return best_score