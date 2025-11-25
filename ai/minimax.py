import sys
from typing import Tuple, List
from game.board import Board

class MinimaxAI:
    """Minimax Algorithm with Transposition Table"""
    
    def __init__(self, max_depth: int = 2):
        self.max_depth = max_depth
        self.nodes_evaluated = 0
        self.transposition_table = {}
        self.max_cache_size = 100000
        self.search_time = 0.0
    
    def get_best_move(self, board: Board, player: int = 2) -> Tuple[int, int, int]:
        """Get best move for the AI player"""
        self.nodes_evaluated = 0
        self.transposition_table.clear()
        
        available_moves = board.get_available_moves()
        if not available_moves:
            return None
        
        num_moves = len(available_moves)
        
        if num_moves > 55:
            depth = 1
        elif num_moves > 45:
            depth = 2
        elif num_moves > 25:
            depth = 3
        else:
            depth = 4
        
        # Check for immediate winning move
        for move in available_moves:
            z, x, y = move
            board.make_move(x, y, z, player)
            winner = board.check_winner()
            board.undo_move(x, y, z)
            
            if winner == player:
                return (x, y, z)
        
        # Block opponent's winning move
        opponent = 3 - player
        for move in available_moves:
            z, x, y = move
            board.make_move(x, y, z, opponent)
            winner = board.check_winner()
            board.undo_move(x, y, z)
            
            if winner == opponent:
                return (x, y, z)
        
        # Score all moves
        move_scores = []
        for move in available_moves:
            z, x, y = move
            score = self._quick_evaluate_move(board, z, x, y, player)
            move_scores.append((score, move))
        
        move_scores.sort(reverse=True, key=lambda x: x[0])
        
        best_score = -sys.maxsize
        best_move = move_scores[0][1]
        
        moves_to_search = move_scores[:min(25, len(move_scores))]
        
        for _, move in moves_to_search:
            z, x, y = move
            board.make_move(x, y, z, player)
            score = self._minimax(board, depth - 1, False, player)
            board.undo_move(x, y, z)
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return (best_move[1], best_move[2], best_move[0])
    
    def clear_cache(self):
        """Clear transposition table"""
        self.transposition_table.clear()
    
    def _quick_evaluate_move(self, board: Board, z: int, x: int, y: int, player: int) -> int:
        """Quick position evaluation for move ordering"""
        score = 0
        
        center_dist = abs(z - 1.5) + abs(x - 1.5) + abs(y - 1.5)
        score += (10 - center_dist * 2)
        
        board.make_move(x, y, z, player)
        
        directions = [
            (1, 0, 0), (0, 1, 0), (0, 0, 1),
            (1, 1, 0), (1, 0, 1), (0, 1, 1),
            (1, -1, 0), (1, 0, -1), (0, 1, -1),
            (1, 1, 1), (1, 1, -1), (1, -1, 1), (-1, 1, 1)
        ]
        
        for dx, dy, dz in directions:
            line_score = self._evaluate_line(board, x, y, z, dx, dy, dz, player)
            score += line_score
        
        board.undo_move(x, y, z)
        
        return score
    
    def _evaluate_line(self, board: Board, x: int, y: int, z: int, 
                       dx: int, dy: int, dz: int, player: int) -> int:
        """Evaluate a single line for threats"""
        player_count = 0
        opponent_count = 0
        
        for i in range(-3, 4):
            nx, ny, nz = x + i*dx, y + i*dy, z + i*dz
            if 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 4:
                cell = board.grid[nx, ny, nz]
                if cell == player:
                    player_count += 1
                elif cell == (3 - player):
                    opponent_count += 1
        
        if player_count == 4:
            return 1000
        elif opponent_count == 4:
            return -1000
        elif player_count > 0 and opponent_count == 0:
            return player_count * player_count * 5
        elif opponent_count > 0 and player_count == 0:
            return -(opponent_count * opponent_count * 4)
        
        return 0
    
    def _get_board_hash(self, board: Board) -> int:
        """Create hash for transposition table"""
        try:
            return hash(board.grid.tobytes())
        except:
            return hash(str(board.grid))
    
    def _minimax(self, board: Board, depth: int, is_max: bool, player: int) -> int:
        """Minimax algorithm with transposition table"""
        self.nodes_evaluated += 1
        
        board_hash = self._get_board_hash(board)
        cache_key = (board_hash, depth, is_max)
        
        if cache_key in self.transposition_table:
            return self.transposition_table[cache_key]
        
        winner = board.check_winner()
        
        if winner == player:
            result = 10000 + depth
        elif winner is not None and winner != 0:
            result = -10000 - depth
        elif board.is_full():
            result = 0
        elif depth == 0:
            result = 0
        else:
            if is_max:
                max_score = -sys.maxsize
                moves = board.get_available_moves()
                
                if depth <= 2 and len(moves) > 15:
                    moves = moves[:15]
                
                for move in moves:
                    z, x, y = move
                    board.make_move(x, y, z, player)
                    score = self._minimax(board, depth - 1, False, player)
                    board.undo_move(x, y, z)
                    
                    max_score = max(max_score, score)
                    
                    if max_score >= 10000:
                        break
                
                result = max_score
            else:
                min_score = sys.maxsize
                opponent = 3 - player
                moves = board.get_available_moves()
                
                if depth <= 2 and len(moves) > 15:
                    moves = moves[:15]
                
                for move in moves:
                    z, x, y = move
                    board.make_move(x, y, z, opponent)
                    score = self._minimax(board, depth - 1, True, player)
                    board.undo_move(x, y, z)
                    
                    min_score = min(min_score, score)
                    
                    if min_score <= -10000:
                        break
                
                result = min_score
        
        if len(self.transposition_table) < self.max_cache_size:
            self.transposition_table[cache_key] = result
        
        return result