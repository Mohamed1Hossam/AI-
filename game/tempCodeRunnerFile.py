   """Reset the board to empty state"""
        self.grid = np.zeros((BOARD_SIZE, BOARD_SIZE, BOARD_SIZE), dtype=int)
        self.move_history = [