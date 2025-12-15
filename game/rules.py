import numpy as np
from config import BOARD_SIZE, PLAYER_HUMAN, PLAYER_AI, EMPTY_CELL
from game.board import Board

class GameRules:

    def __init__(self):
        self.winning_lines = self._generate_all_winning_lines()
        self.last_winning_line = None

    def _generate_all_winning_lines(self):
        lines = []

        # 1. Rows (parallel to x-axis): 16 lines
        for y in range(BOARD_SIZE):
            for z in range(BOARD_SIZE):
                lines.append([(x, y, z) for x in range(BOARD_SIZE)])

        # 2. Columns (parallel to y-axis): 16 lines
        for x in range(BOARD_SIZE):
            for z in range(BOARD_SIZE):
                lines.append([(x, y, z) for y in range(BOARD_SIZE)])

        # 3. Pillars (parallel to z-axis): 16 lines
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                lines.append([(x, y, z) for z in range(BOARD_SIZE)])

        # 4. Diagonals in XY planes: 8 lines
        for z in range(BOARD_SIZE):
            lines.append([(i, i, z) for i in range(BOARD_SIZE)])
            lines.append([(i, BOARD_SIZE - 1 - i, z) for i in range(BOARD_SIZE)])

        # 5. Diagonals in XZ planes: 8 lines
        for y in range(BOARD_SIZE):
            lines.append([(i, y, i) for i in range(BOARD_SIZE)])
            lines.append([(i, y, BOARD_SIZE - 1 - i) for i in range(BOARD_SIZE)])

        # 6. Diagonals in YZ planes: 8 lines
        for x in range(BOARD_SIZE):
            lines.append([(x, i, i) for i in range(BOARD_SIZE)])
            lines.append([(x, i, BOARD_SIZE - 1 - i) for i in range(BOARD_SIZE)])

        # 7. Space diagonals (through the cube): 4 lines
        lines.append([(i, i, i) for i in range(BOARD_SIZE)])
        lines.append([(i, i, BOARD_SIZE - 1 - i) for i in range(BOARD_SIZE)])
        lines.append([(i, BOARD_SIZE - 1 - i, i) for i in range(BOARD_SIZE)])
        lines.append([(BOARD_SIZE - 1 - i, i, i) for i in range(BOARD_SIZE)])

        return lines

    def check_winner(self, board):

        self.last_winning_line = None 
        
        for line in self.winning_lines:
            values = [board.get_cell(*pos) for pos in line]

            if all(v == PLAYER_HUMAN for v in values):
                self.last_winning_line = line 
                return PLAYER_HUMAN
            elif all(v == PLAYER_AI for v in values):
                self.last_winning_line = line 
                return PLAYER_AI


        if board.is_full():
            return 0  

        return None 

    def get_winning_line(self):
        """Get the last winning line positions"""
        return self.last_winning_line

    def get_line_value(self, board, line):

        values = [board.get_cell(*pos) for pos in line]
        player_count = values.count(PLAYER_HUMAN)
        ai_count = values.count(PLAYER_AI)
        empty_count = values.count(EMPTY_CELL)

        return (player_count, ai_count, empty_count)

    def is_line_blocked(self, board, line):

        player_count, ai_count, _ = self.get_line_value(board, line)
        return player_count > 0 and ai_count > 0

    def count_winning_lines(self):
        """Return total number of winning lines"""
        return len(self.winning_lines)