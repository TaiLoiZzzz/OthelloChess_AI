"""
heuristics.py
Contains heuristic evaluation functions for the Othello AI.
"""
from backend.engine.constants import BOARD_SIZE, EMPTY

# Static Positional Weights Matrix
# Corners are extremely valuable (+100)
# Squares adjacent to corners are dangerous (-20, -50)
# Edges are valuable (+10)
POSITIONAL_WEIGHTS = [
    [100, -20,  10,   5,   5,  10, -20, 100],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [ 10,  -2,   5,   1,   1,   5,  -2,  10],
    [  5,  -2,   1,   3,   3,   1,  -2,   5],
    [  5,  -2,   1,   3,   3,   1,  -2,   5],
    [ 10,  -2,   5,   1,   1,   5,  -2,  10],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [100, -20,  10,   5,   5,  10, -20, 100],
]

def evaluate_state(board, player, opponent):
    """
    Evaluates the board state for the given player.
    Uses a simplified dynamic weighting approach based on the game phase.
    """
    black_count, white_count = board.count_pieces()
    total_pieces = black_count + white_count
    
    player_count = black_count if player == 1 else white_count
    opponent_count = white_count if player == 1 else black_count

    # 1. Coin Parity Score (difference in pieces)
    # Important in endgame
    parity_score = 100 * (player_count - opponent_count) / max(1, (player_count + opponent_count))

    # 2. Mobility Score (difference in valid moves)
    # Extremely important in opening/midgame
    player_moves = len(board.get_valid_moves(player))
    opponent_moves = len(board.get_valid_moves(opponent))
    mobility_score = 0
    if (player_moves + opponent_moves) > 0:
        mobility_score = 100 * (player_moves - opponent_moves) / (player_moves + opponent_moves)

    # 3. Positional Score (corner control, edge stability)
    player_pos_score = 0
    opponent_pos_score = 0
    
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            cell = board.grid[r][c]
            if cell == player:
                player_pos_score += POSITIONAL_WEIGHTS[r][c]
            elif cell == opponent:
                opponent_pos_score += POSITIONAL_WEIGHTS[r][c]
                
    positional_score = player_pos_score - opponent_pos_score

    # DYNAMIC WEIGHTS BASED ON GAME PHASE
    # Early Game (<= 20 pieces), Mid Game (21 - 50 pieces), End Game (> 50 pieces)
    if total_pieces <= 20:
        # Opening: Focus heavily on positioning and mobility, ignore pieces
        w_parity = 0
        w_mobility = 10
        w_position = 50
    elif total_pieces <= 50:
        # Midgame: Still focus on mobility and position, start caring about pieces slightly
        w_parity = 5
        w_mobility = 20
        w_position = 50
    else:
        # Endgame: Exact piece count is what matters to win
        w_parity = 50
        w_mobility = 5
        w_position = 20
        
    final_score = (w_parity * parity_score) + (w_mobility * mobility_score) + (w_position * positional_score)
    return final_score
