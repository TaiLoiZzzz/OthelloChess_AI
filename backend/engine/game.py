"""
game.py
Contains the Game class to manage the state of an Othello game, turn switching, and endgame conditions.
"""
from .constants import BLACK, WHITE, EMPTY, get_opponent
from .board import Board

class Game:
    def __init__(self):
        """Initializes a new game of Othello."""
        self.board = Board()
        self.current_player = BLACK # Black always moves first
        self.is_game_over = False
        self.winner = None
        self.last_move = None
        self.skipped_turn = False

    def play_turn(self, row, col):
        """
        Attempts to apply a move for the current player at (row, col).
        If the move is valid, updates the game state.
        Returns True if the move was successful, False otherwise.
        """
        if self.is_game_over:
            return False

        # Apply move generates a new board state if valid
        new_board = self.board.apply_move(row, col, self.current_player)
        
        if new_board is None:
            return False # Invalid move

        # Update board and state
        self.board = new_board
        self.last_move = (row, col)
        self.skipped_turn = False
        
        self._switch_turn_and_check_endgame()
        return True

    def pass_turn(self):
        """
        Passes the turn if the current player has no valid moves.
        Returns True if passed successfully, False if passing is not allowed.
        """
        if self.is_game_over:
            return False

        valid_moves = self.board.get_valid_moves(self.current_player)
        if len(valid_moves) > 0:
            # Player cannot pass if they have valid moves
            return False

        self.skipped_turn = True
        self._switch_turn_and_check_endgame()
        return True

    def _switch_turn_and_check_endgame(self):
        """
        Switches the turn to the opponent. Checks if both players have no valid moves
        or if the board is full to determine endgame.
        """
        opponent = get_opponent(self.current_player)
        opponent_moves = self.board.get_valid_moves(opponent)
        
        # If opponent has valid moves, just switch turn
        if len(opponent_moves) > 0:
            self.current_player = opponent
        else:
            # Opponent has no moves. Check if current player also has no moves
            current_moves = self.board.get_valid_moves(self.current_player)
            if len(current_moves) == 0:
                # Neither player has moves, game over
                self._handle_game_over()
            else:
                # Opponent skips turn, current player keeps turn
                pass 

    def _handle_game_over(self):
        """Sets game over state and calculates the winner."""
        self.is_game_over = True
        black_score, white_score = self.board.count_pieces()
        
        if black_score > white_score:
            self.winner = BLACK
        elif white_score > black_score:
            self.winner = WHITE
        else:
            self.winner = EMPTY # Tie

    def get_state(self):
        """Returns a dictionary representing the current game state."""
        black_score, white_score = self.board.count_pieces()
        return {
            "board": self.board.grid,
            "current_player": self.current_player,
            "black_score": black_score,
            "white_score": white_score,
            "is_game_over": self.is_game_over,
            "winner": self.winner,
            "last_move": self.last_move,
            "valid_moves": self.board.get_valid_moves(self.current_player)
        }
