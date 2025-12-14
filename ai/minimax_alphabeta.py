from typing import Tuple
from game.board import Board
from ai.minimax import MinimaxAI
from ai.alphabeta import AlphaBetaAI

class MinimaxAlphaBetaAI:

    
    def __init__(self, max_depth: int = 3, switch_depth: int = 2):
        self.max_depth = max_depth
        self.switch_depth = switch_depth
        self.minimax_ai = MinimaxAI(max_depth)
        self.alphabeta_ai = AlphaBetaAI(max_depth)
    
    def get_best_move(self, board: Board, player: int = 2) -> Tuple[int, int, int]:
        available_moves = board.get_available_moves()
        if not available_moves:
            return None
        
        num_moves = len(available_moves)
        
        
        if num_moves > 35:
            return self.minimax_ai.get_best_move(board, player)
        else:
            return self.alphabeta_ai.get_best_move(board, player)