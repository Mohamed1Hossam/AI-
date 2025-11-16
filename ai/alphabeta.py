import sys
from typing import Tuple, List
from game.board import Board

class AlphaBetaAI:
    """Alpha-Beta Pruning Algorithm with Resign Logic"""
    
    def __init__(self, max_depth: int = 3):
        self.max_depth = max_depth
        self.nodes_evaluated = 0
        self.pruned_branches = 0
    
    def get_best_move(self, board: Board, player: int) -> Tuple[int, int, int]:
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
            board.make_move(z, x, y, player)
            if board.check_winner() == player:
                board.undo_move(z, x, y)
                print("AI found winning move!")
                return move
            board.undo_move(z, x, y)
        
        # Check for must-block opponent winning move
        opponent = -player
        opponent_winning_moves = []
        for move in available_moves:
            z, x, y = move
            board.make_move(z, x, y, opponent)
            if board.check_winner() == opponent:
                opponent_winning_moves.append(move)
            board.undo_move(z, x, y)
        
        # If opponent has winning move, must block it
        if len(opponent_winning_moves) == 1:
            print("AI blocking opponent's winning move")
            return opponent_winning_moves[0]
        elif len(opponent_winning_moves) > 1:
            # Multiple winning threats - we cannot block all
            print("AI cannot prevent loss - opponent has multiple winning moves")
            print("AI resigns and plays random move")
            return available_moves[0]  # Just play any move (resigned)
        
        # Normal alpha-beta search
        best_score = -sys.maxsize
        best_move = None
        alpha = -sys.maxsize
        beta = sys.maxsize
        
        # Order moves for better pruning
        ordered_moves = self._order_moves(board, available_moves, player)
        
        for move in ordered_moves:
            z, x, y = move
            board.make_move(z, x, y, player)
            score = self._alphabeta(board, depth - 1, alpha, beta, False, player)
            board.undo_move(z, x, y)
            
            if score > best_score:
                best_score = score
                best_move = move
                alpha = max(alpha, best_score)
        
        # Check if best score indicates inevitable loss
        if best_score <= -900:
            print(f"AI evaluation: {best_score} (inevitable loss detected)")
            print("AI cannot prevent opponent from winning - playing random move")
            return available_moves[0]  # Resigned - just play any move
        
        return best_move if best_move else available_moves[0]
    
    def _order_moves(self, board: Board, moves: List[Tuple[int, int, int]], 
                     player: int) -> List[Tuple[int, int, int]]:
        """Order moves by strategic value for better pruning"""
        move_scores = []
        
        for move in moves:
            z, x, y = move
            # Prioritize center positions
            center_dist = abs(z - 1.5) + abs(x - 1.5) + abs(y - 1.5)
            score = 10 - center_dist
            move_scores.append((score, move))
        
        move_scores.sort(reverse=True, key=lambda x: x[0])
        return [move for _, move in move_scores]
    
    def _alphabeta(self, board: Board, depth: int, alpha: int, beta: int,
                   is_max: bool, player: int) -> int:
        self.nodes_evaluated += 1
        
        winner = board.check_winner()
        if winner == player:
            return 1000 + depth  # Faster wins are better
        elif winner is not None:
            return -1000 - depth  # Slower losses are better
        elif board.is_full() or depth == 0:
            return 0  # Draw or depth limit
        
        if is_max:
            max_score = -sys.maxsize
            for move in board.get_available_moves():
                z, x, y = move
                board.make_move(z, x, y, player)
                score = self._alphabeta(board, depth - 1, alpha, beta, False, player)
                board.undo_move(z, x, y)
                
                max_score = max(max_score, score)
                alpha = max(alpha, score)
                if beta <= alpha:
                    self.pruned_branches += 1
                    break  # Beta cutoff
            return max_score
        else:
            min_score = sys.maxsize
            opponent = -player
            for move in board.get_available_moves():
                z, x, y = move
                board.make_move(z, x, y, opponent)
                score = self._alphabeta(board, depth - 1, alpha, beta, True, player)
                board.undo_move(z, x, y)
                
                min_score = min(min_score, score)
                beta = min(beta, score)
                if beta <= alpha:
                    self.pruned_branches += 1
                    break  # Alpha cutoff
            return min_score