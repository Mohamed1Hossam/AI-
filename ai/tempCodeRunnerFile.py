    def _get_ordered_moves(self, board: Board, player: int) -> List[Tuple[int, int, int]]:
        """Order moves by heuristic value for better performance"""
        moves = board.get_available_moves()
        
        # Quick evaluation of each move
        move_scores = []
        for move in moves:
            z, x, y = move
            board.make_move(z, x, y, player)
            
            # Check for immediate win
            if board.check_winner() == player:
                board.undo_move(z, x, y)
                return [move]  # Return immediately if winning move found
            
            score = self._evaluate(board, player)
            board.undo_move(z, x, y)
            move_scores.append((score, move))
        
        # Sort moves by score (best first)
        move_scores.sort(reverse=True, key=lambda x: x[0])
        return [move for score, move in move_scores]