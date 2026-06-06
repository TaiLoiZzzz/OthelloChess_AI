"""
constants.py
Defines fundamental constants for the Othello Game Engine.
"""

# Board specifications
BOARD_SIZE = 8

# Cell states
EMPTY = 0
BLACK = 1
WHITE = 2

# 8 possible directions for piece flipping:
# (row_offset, col_offset)
# Top-Left, Top, Top-Right, Left, Right, Bottom-Left, Bottom, Bottom-Right
DIRECTIONS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1)
]

def get_opponent(player):
    """Returns the opponent of the given player."""
    if player == BLACK:
        return WHITE
    elif player == WHITE:
        return BLACK
    return EMPTY
