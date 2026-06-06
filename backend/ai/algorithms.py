"""
algorithms.py
Contains AI strategies for playing Othello.
"""
import random
from backend.engine.constants import get_opponent
from .utils import AIAnalytics
from .heuristics import evaluate_state

class RandomAI:
    @staticmethod
    def get_best_move(board, player):
        """Returns a random valid move and basic metrics."""
        analytics = AIAnalytics()
        analytics.start_timer()
        
        valid_moves = board.get_valid_moves(player)
        move = random.choice(valid_moves) if valid_moves else None
        
        analytics.increment_node()
        analytics.stop_timer()
        
        return move, analytics.get_metrics()

class GreedyAI:
    @staticmethod
    def get_best_move(board, player):
        """
        Returns the move that captures the maximum number of opponent pieces 
        in the current turn.
        """
        analytics = AIAnalytics()
        analytics.start_timer()
        
        valid_moves = board.get_valid_moves(player)
        best_move = None
        max_flips = -1
        
        for r, c in valid_moves:
            analytics.increment_node()
            # Calculate flips by comparing piece counts before and after move
            new_board = board.apply_move(r, c, player)
            if new_board:
                b1, w1 = board.count_pieces()
                b2, w2 = new_board.count_pieces()
                
                player_pieces_before = b1 if player == 1 else w1
                player_pieces_after = b2 if player == 1 else w2
                flips = (player_pieces_after - player_pieces_before) - 1 # -1 because we placed a piece
                
                if flips > max_flips:
                    max_flips = flips
                    best_move = (r, c)
                    
        analytics.stop_timer()
        return best_move, analytics.get_metrics()

class MinimaxAI:
    def __init__(self, max_depth=4):
        self.max_depth = max_depth
        self.analytics = AIAnalytics()

    def get_best_move(self, board, player):
        """Finds the best move using Minimax with Alpha-Beta Pruning."""
        self.analytics.start_timer()
        opponent = get_opponent(player)
        
        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        
        valid_moves = board.get_valid_moves(player)
        
        if not valid_moves:
            self.analytics.stop_timer()
            return None, self.analytics.get_metrics()
            
        # Move Ordering: Evaluate corners first or use a shallow heuristic 
        # to sort moves and improve alpha-beta pruning efficiency.
        # For simplicity, we just sort by POSITIONAL_WEIGHTS loosely.
        from .heuristics import POSITIONAL_WEIGHTS
        valid_moves.sort(key=lambda m: POSITIONAL_WEIGHTS[m[0]][m[1]], reverse=True)

        for r, c in valid_moves:
            self.analytics.increment_node()
            new_board = board.apply_move(r, c, player)
            if new_board:
                score = self._minimax(new_board, self.max_depth - 1, alpha, beta, False, player, opponent)
                
                if score > best_score:
                    best_score = score
                    best_move = (r, c)
                    
                alpha = max(alpha, best_score)
                
        self.analytics.stop_timer()
        return best_move, self.analytics.get_metrics()

    def _minimax(self, board, depth, alpha, beta, is_maximizing, ai_player, opponent):
        """Recursive Minimax function."""
        # Check termination conditions: depth reached or game over
        current_player = ai_player if is_maximizing else opponent
        valid_moves = board.get_valid_moves(current_player)
        
        if depth == 0 or len(valid_moves) == 0:
            # Check if game is completely over (both have no moves)
            if len(valid_moves) == 0 and len(board.get_valid_moves(get_opponent(current_player))) == 0:
                pass # terminal state
            else:
                if len(valid_moves) == 0:
                    # Pass turn
                    return self._minimax(board, depth - 1, alpha, beta, not is_maximizing, ai_player, opponent)
                    
            # Evaluate leaf node
            return evaluate_state(board, ai_player, opponent)

        # Optimization: Move ordering
        from .heuristics import POSITIONAL_WEIGHTS
        valid_moves.sort(key=lambda m: POSITIONAL_WEIGHTS[m[0]][m[1]], reverse=is_maximizing)

        if is_maximizing:
            max_eval = float('-inf')
            for r, c in valid_moves:
                self.analytics.increment_node()
                new_board = board.apply_move(r, c, ai_player)
                if new_board:
                    eval = self._minimax(new_board, depth - 1, alpha, beta, False, ai_player, opponent)
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break # Beta cut-off
            return max_eval
        else:
            min_eval = float('inf')
            for r, c in valid_moves:
                self.analytics.increment_node()
                new_board = board.apply_move(r, c, opponent)
                if new_board:
                    eval = self._minimax(new_board, depth - 1, alpha, beta, True, ai_player, opponent)
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break # Alpha cut-off
            return min_eval
