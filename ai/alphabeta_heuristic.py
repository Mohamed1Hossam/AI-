import sys
from typing import Tuple, List
from game.board import Board
from ai.heuristics import HeuristicEvaluator

class AlphaBetaHeuristicAI:
    """Highly Optimized Alpha-Beta with Heuristic Evaluation"""
    
    def __init__(self, max_depth: int = 3, heuristic_version: int = 2):
        self.max_depth = max_depth
        self.heuristic_version = heuristic_version
        self.nodes_evaluated = 0
        self.pruned_branches = 0
        self.transposition_table = {}
        self.max_cache_size = 100000
    
    def get_best_move(self, board: Board, player: int) -> Tuple[int, int, int]:
        self.nodes_evaluated = 0
        self.pruned_branches = 0
        self.transposition_table.clear()
        
        available_moves = board.get_available_moves()
        if not available_moves:
            return None
        
        num_moves = len(available_moves)
        
        # Aggressive adaptive depth
        if num_moves > 50:
            depth = 2
        elif num_moves > 35:
            depth = 3
        elif num_moves > 20:
            depth = 4
        else:
            depth = min(5, self.max_depth)
        
        # CRITICAL: Check for immediate winning move
        for move in available_moves:
            z, x, y = move
            board.make_move(z, x, y, player)
            if board.check_winner() == player:
                board.undo_move(z, x, y)
                return move
            board.undo_move(z, x, y)
        
        # CRITICAL: Block opponent's winning move
        opponent = -player
        blocking_moves = []
        for move in available_moves:
            z, x, y = move
            board.make_move(z, x, y, opponent)
            if board.check_winner() == opponent:
                blocking_moves.append(move)
            board.undo_move(z, x, y)
        
        # Must block if only one threat
        if len(blocking_moves) == 1:
            return blocking_moves[0]
        elif len(blocking_moves) > 1:
            # Multiple threats - search among blocking moves only
            available_moves = blocking_moves
        
        # Get moves ordered by heuristic
        moves = self._get_ordered_moves(board, available_moves, player)
        
        # Limit moves to search if too many
        if len(moves) > 25:
            moves = moves[:25]
        
        best_score = -sys.maxsize
        best_move = moves[0]  # Default to best heuristic move
        alpha = -sys.maxsize
        beta = sys.maxsize
        
        for move in moves:
            z, x, y = move
            board.make_move(z, x, y, player)
            score = self._alphabeta(board, depth - 1, alpha, beta, False, player)
            board.undo_move(z, x, y)
            
            if score > best_score:
                best_score = score
                best_move = move
                alpha = max(alpha, best_score)
            
            # Early exit if winning move found
            if best_score >= 900:
                break
        
        return best_move
    
    def _get_ordered_moves(self, board: Board, moves: List[Tuple[int, int, int]], 
                          player: int) -> List[Tuple[int, int, int]]:
        """Order moves by heuristic value for better pruning"""
        move_scores = []
        
        for move in moves:
            z, x, y = move
            board.make_move(z, x, y, player)
            
            # Check for immediate win
            if board.check_winner() == player:
                board.undo_move(z, x, y)
                return [move]  # Return winning move immediately
            
            # Quick heuristic evaluation
            score = self._evaluate(board, player)
            
            board.undo_move(z, x, y)
            move_scores.append((score, move))
        
        # Sort by best score first
        move_scores.sort(reverse=True, key=lambda x: x[0])
        return [move for score, move in move_scores]
    
    def _evaluate(self, board: Board, player: int) -> int:
        if self.heuristic_version == 1:
            return HeuristicEvaluator.evaluate_v1_basic(board, player)
        elif self.heuristic_version == 2:
            return HeuristicEvaluator.evaluate_v2_positional(board, player)
        else:
            return HeuristicEvaluator.evaluate_v3_aggressive(board, player)
    
    def _get_board_hash(self, board: Board) -> int:
        """Create hash for transposition table"""
        try:
            return hash(board.grid.tobytes())
        except:
            return hash(str(board.grid))
    
    def _alphabeta(self, board: Board, depth: int, alpha: int, beta: int,
                   is_max: bool, player: int) -> int:
        self.nodes_evaluated += 1
        
        # Check transposition table
        board_hash = self._get_board_hash(board)
        cache_key = (board_hash, depth, is_max)
        
        if cache_key in self.transposition_table:
            return self.transposition_table[cache_key]
        
        # Terminal state checks
        winner = board.check_winner()
        if winner == player:
            result = 1000 + depth
        elif winner == -player:
            result = -1000 - depth
        elif board.is_full():
            result = 0
        elif depth == 0:
            result = self._evaluate(board, player)
        else:
            # Continue search
            if is_max:
                max_score = -sys.maxsize
                moves = board.get_available_moves()
                
                # Aggressive move pruning at low depths
                if depth <= 2 and len(moves) > 20:
                    # Use heuristic to pick best 20 moves
                    move_scores = []
                    for move in moves:
                        z, x, y = move
                        board.make_move(z, x, y, player)
                        score = self._evaluate(board, player)
                        board.undo_move(z, x, y)
                        move_scores.append((score, move))
                    move_scores.sort(reverse=True, key=lambda x: x[0])
                    moves = [move for _, move in move_scores[:20]]
                
                for move in moves:
                    z, x, y = move
                    board.make_move(z, x, y, player)
                    score = self._alphabeta(board, depth - 1, alpha, beta, False, player)
                    board.undo_move(z, x, y)
                    
                    max_score = max(max_score, score)
                    alpha = max(alpha, score)
                    
                    if beta <= alpha:
                        self.pruned_branches += 1
                        break  # Beta cutoff
                
                result = max_score
            else:
                min_score = sys.maxsize
                opponent = -player
                moves = board.get_available_moves()
                
                # Aggressive move pruning at low depths
                if depth <= 2 and len(moves) > 20:
                    # Use heuristic to pick best 20 moves for opponent
                    move_scores = []
                    for move in moves:
                        z, x, y = move
                        board.make_move(z, x, y, opponent)
                        score = self._evaluate(board, opponent)
                        board.undo_move(z, x, y)
                        move_scores.append((score, move))
                    move_scores.sort(reverse=True, key=lambda x: x[0])
                    moves = [move for _, move in move_scores[:20]]
                
                for move in moves:
                    z, x, y = move
                    board.make_move(z, x, y, opponent)
                    score = self._alphabeta(board, depth - 1, alpha, beta, True, player)
                    board.undo_move(z, x, y)
                    
                    min_score = min(min_score, score)
                    beta = min(beta, score)
                    
                    if beta <= alpha:
                        self.pruned_branches += 1
                        break  # Alpha cutoff
                
                result = min_score
        
        # Cache result
        if len(self.transposition_table) < self.max_cache_size:
            self.transposition_table[cache_key] = result
        
        return result