import sys
from typing import Tuple, List, Optional
from game.board import Board

class MinimaxAI:
    """Corrected Minimax with Proper Win Detection"""
    
    def __init__(self, max_depth: int = 2):
        self.max_depth = max_depth
        self.nodes_evaluated = 0
        self.transposition_table = {}
        self.max_cache_size = 100000
    
    def get_best_move(self, board: Board, player: int) -> Tuple[int, int, int]:
        self.nodes_evaluated = 0
        self.transposition_table.clear()
        
        available_moves = board.get_available_moves()
        if not available_moves:
            return None
        
        num_moves = len(available_moves)
        
        # Adaptive depth
        if num_moves > 55:
            depth = 1
        elif num_moves > 45:
            depth = 2
        elif num_moves > 25:
            depth = 3
        else:
            depth = 4
        
        # CRITICAL: Check for immediate winning move first
        for move in available_moves:
            z, x, y = move
            board.make_move(z, x, y, player)
            winner = board.check_winner()
            board.undo_move(z, x, y)
            
            if winner == player:
                print(f"Found winning move: {move}")
                return move
        
        # CRITICAL: Block opponent's winning move
        opponent = -player
        for move in available_moves:
            z, x, y = move
            board.make_move(z, x, y, opponent)
            winner = board.check_winner()
            board.undo_move(z, x, y)
            
            if winner == opponent:
                print(f"Blocking opponent win: {move}")
                return move
        
        # Score all moves with quick evaluation
        move_scores = []
        for move in available_moves:
            z, x, y = move
            score = self._quick_evaluate_move(board, z, x, y, player)
            move_scores.append((score, move))
        
        # Sort best moves first
        move_scores.sort(reverse=True, key=lambda x: x[0])
        
        # Search top moves with minimax
        best_score = -sys.maxsize
        best_move = move_scores[0][1]
        
        moves_to_search = move_scores[:min(25, len(move_scores))]
        
        for _, move in moves_to_search:
            z, x, y = move
            board.make_move(z, x, y, player)
            
            # Call minimax for opponent's turn (minimizing)
            score = self._minimax(board, depth - 1, False, player)
            
            board.undo_move(z, x, y)
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move
    
    def _quick_evaluate_move(self, board: Board, z: int, x: int, y: int, player: int) -> int:
        """Quick position evaluation for move ordering"""
        score = 0
        
        # Favor center positions
        center_dist = abs(z - 1.5) + abs(x - 1.5) + abs(y - 1.5)
        score += (10 - center_dist * 2)
        
        # Make a temporary move to evaluate threats
        board.make_move(z, x, y, player)
        
        # Count how many lines this move is part of
        directions = [
            (1, 0, 0), (0, 1, 0), (0, 0, 1),
            (1, 1, 0), (1, 0, 1), (0, 1, 1),
            (1, -1, 0), (1, 0, -1), (0, 1, -1),
            (1, 1, 1), (1, 1, -1), (1, -1, 1), (-1, 1, 1)
        ]
        
        for dz, dx, dy in directions:
            line_score = self._evaluate_line(board, z, x, y, dz, dx, dy, player)
            score += line_score
        
        board.undo_move(z, x, y)
        
        return score
    
    def _evaluate_line(self, board: Board, z: int, x: int, y: int, 
                       dz: int, dx: int, dy: int, player: int) -> int:
        """Evaluate a single line for threats"""
        player_count = 0
        opponent_count = 0
        empty_count = 0
        
        for i in range(-3, 4):
            nz, nx, ny = z + i*dz, x + i*dx, y + i*dy
            if 0 <= nz < 4 and 0 <= nx < 4 and 0 <= ny < 4:
                cell = board.grid[nz][nx][ny]
                if cell == player:
                    player_count += 1
                elif cell == -player:
                    opponent_count += 1
                elif cell == 0:
                    empty_count += 1
        
        # Scoring logic
        if player_count == 4:
            return 1000  # Winning line
        elif opponent_count == 4:
            return -1000  # Opponent winning line
        elif player_count > 0 and opponent_count == 0:
            return player_count * player_count * 5  # Our threat
        elif opponent_count > 0 and player_count == 0:
            return -(opponent_count * opponent_count * 4)  # Their threat
        
        return 0
    
    def _get_board_hash(self, board: Board) -> int:
        """Create hash for transposition table"""
        try:
            return hash(board.grid.tobytes())
        except:
            # Fallback if tobytes doesn't work
            return hash(str(board.grid))
    
    def _minimax(self, board: Board, depth: int, is_max: bool, player: int) -> int:
        self.nodes_evaluated += 1
        
        # Check cache
        board_hash = self._get_board_hash(board)
        cache_key = (board_hash, depth, is_max)
        
        if cache_key in self.transposition_table:
            return self.transposition_table[cache_key]
        
        # CRITICAL: Terminal state check
        winner = board.check_winner()
        
        if winner == player:
            # We win - return high positive score
            result = 10000 + depth
        elif winner == -player:
            # Opponent wins - return high negative score
            result = -10000 - depth
        elif board.is_full():
            # Draw
            result = 0
        elif depth == 0:
            # Depth limit - evaluate position
            result = 0  # Neutral if no heuristic
        else:
            # Continue search
            if is_max:
                # Maximizing player's turn
                max_score = -sys.maxsize
                moves = board.get_available_moves()
                
                # Limit branching at low depths
                if depth <= 2 and len(moves) > 15:
                    moves = moves[:15]
                
                for move in moves:
                    z, x, y = move
                    board.make_move(z, x, y, player)
                    score = self._minimax(board, depth - 1, False, player)
                    board.undo_move(z, x, y)
                    
                    max_score = max(max_score, score)
                    
                    # Alpha-beta style early exit
                    if max_score >= 10000:
                        break
                
                result = max_score
            else:
                # Minimizing player's turn (opponent)
                min_score = sys.maxsize
                opponent = -player
                moves = board.get_available_moves()
                
                # Limit branching at low depths
                if depth <= 2 and len(moves) > 15:
                    moves = moves[:15]
                
                for move in moves:
                    z, x, y = move
                    board.make_move(z, x, y, opponent)
                    score = self._minimax(board, depth - 1, True, player)
                    board.undo_move(z, x, y)
                    
                    min_score = min(min_score, score)
                    
                    # Alpha-beta style early exit
                    if min_score <= -10000:
                        break
                
                result = min_score
        
        # Cache result
        if len(self.transposition_table) < self.max_cache_size:
            self.transposition_table[cache_key] = result
        
        return result