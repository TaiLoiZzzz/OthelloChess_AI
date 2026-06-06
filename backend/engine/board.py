"""
board.py
Contains the Board class to represent the 8x8 matrix and logic for move generation and piece flipping.
"""
import copy
from .constants import BOARD_SIZE, EMPTY, BLACK, WHITE, DIRECTIONS

class Board:
    def __init__(self):
        """
        Initializes an 8x8 Othello board.
        The board is represented as a 2D list.
        """
        self.grid = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        # Initial 4 pieces in the center
        center = BOARD_SIZE // 2
        self.grid[center - 1][center - 1] = WHITE
        self.grid[center][center] = WHITE
        self.grid[center - 1][center] = BLACK
        self.grid[center][center - 1] = BLACK

    def is_on_board(self, row, col):
        """Checks if a given coordinate is within the board boundaries."""
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

    def get_cell(self, row, col):
        """Returns the value of the cell at (row, col)."""
        if self.is_on_board(row, col):
            return self.grid[row][col]
        return None

    def _get_flipped_pieces_in_direction(self, row, col, player, d_row, d_col):
        """
        Finds all pieces that would be flipped in a specific direction if 'player'
        places a piece at (row, col).
        Returns a list of tuples (r, c) representing the pieces to be flipped.
        """
        flipped = []
        r, c = row + d_row, col + d_col
        opponent = WHITE if player == BLACK else BLACK

        while self.is_on_board(r, c) and self.grid[r][c] == opponent:
            flipped.append((r, c))
            r += d_row
            c += d_col

        # If the sequence of opponent pieces is capped by the player's own piece, it's valid
        if self.is_on_board(r, c) and self.grid[r][c] == player and len(flipped) > 0:
            return flipped
        
        return []

    def get_valid_moves(self, player):
        """
        Generates all valid moves for the given player.
        Returns a list of tuples (row, col) representing valid moves.
        """
        valid_moves = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.grid[r][c] != EMPTY:
                    continue
                
                # Check all 8 directions to see if any pieces would be flipped
                for d_row, d_col in DIRECTIONS:
                    if self._get_flipped_pieces_in_direction(r, c, player, d_row, d_col):
                        valid_moves.append((r, c))
                        break # Only need one valid direction to make the move valid
                        
        return valid_moves

    def apply_move(self, row, col, player):
        """
        Places a piece for the player at (row, col) and flips all captured opponent pieces.
        Returns a new Board instance with the move applied (to preserve state for AI search).
        If the move is invalid, returns None.
        """
        if self.grid[row][col] != EMPTY:
            return None

        pieces_to_flip = []
        for d_row, d_col in DIRECTIONS:
            pieces_to_flip.extend(self._get_flipped_pieces_in_direction(row, col, player, d_row, d_col))
        
        if not pieces_to_flip:
            return None # Invalid move if no pieces are flipped

        # Create a deep copy to ensure immutability for AI tree search
        new_board = Board()
        new_board.grid = copy.deepcopy(self.grid)
        
        # Apply the move
        new_board.grid[row][col] = player
        for r, c in pieces_to_flip:
            new_board.grid[r][c] = player
            
        return new_board

    def count_pieces(self):
        """Returns a tuple (black_count, white_count)."""
        black = sum(row.count(BLACK) for row in self.grid)
        white = sum(row.count(WHITE) for row in self.grid)
        return black, white

    def display(self):
        """Helper to print the board to console."""
        symbols = {EMPTY: '.', BLACK: 'B', WHITE: 'W'}
        for row in self.grid:
            print(" ".join(symbols[cell] for cell in row))
        print()
