 

from game.board import Board  
class HeuristicEvaluator:
    """
    Heuristic Evaluation Functions
    Demonstrates: Strategy Pattern
    """
    
    @staticmethod
    def evaluate_v1_basic(board: Board, player: int) -> int:
        """Heuristic V1: Basic line counting"""
        score = 0
        opponent = -player
        
        for line in board.get_winning_lines():
            ai_count = sum(1 for pos in line if board.get_cell(*pos) == player)
            opp_count = sum(1 for pos in line if board.get_cell(*pos) == opponent)
            
            if ai_count > 0 and opp_count == 0:
                score += ai_count ** 2
            elif opp_count > 0 and ai_count == 0:
                score -= opp_count ** 2
        
        return score
    
    @staticmethod
    def evaluate_v2_positional(board: Board, player: int) -> int:
        """Heuristic V2: Positional strategy"""
        score = HeuristicEvaluator.evaluate_v1_basic(board, player)
        
        # Center bonus
        center = [(1,1,1), (1,1,2), (1,2,1), (1,2,2), 
                  (2,1,1), (2,1,2), (2,2,1), (2,2,2)]
        for pos in center:
            cell = board.get_cell(*pos)
            if cell == player:
                score += 10
            elif cell == -player:
                score -= 10
        
        # Corner bonus
        corners = [(0,0,0), (0,0,3), (0,3,0), (0,3,3),
                   (3,0,0), (3,0,3), (3,3,0), (3,3,3)]
        for pos in corners:
            cell = board.get_cell(*pos)
            if cell == player:
                score += 5
            elif cell == -player:
                score -= 5
        
        return score
    
    @staticmethod
    def evaluate_v3_aggressive(board: Board, player: int) -> int:
        """Heuristic V3: Aggressive strategy"""
        score = HeuristicEvaluator.evaluate_v2_positional(board, player)
        opponent = -player
        
        for line in board.get_winning_lines():
            ai_count = sum(1 for pos in line if board.get_cell(*pos) == player)
            opp_count = sum(1 for pos in line if board.get_cell(*pos) == opponent)
            empty = sum(1 for pos in line if board.get_cell(*pos) == 0)
            
            if ai_count == 3 and empty == 1:
                score += 100
            if opp_count == 3 and empty == 1:
                score -= 150
        
        return score
