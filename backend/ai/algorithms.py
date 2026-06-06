"""
algorithms.py
Contains AI strategies for playing Othello.
"""
import random
from backend.engine.constants import get_opponent, BLACK, WHITE, EMPTY
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
    def __init__(self, max_depth=3):
        # Pure Minimax is slower, so we use max_depth=3 by default
        self.max_depth = max_depth
        self.analytics = AIAnalytics()

    def get_best_move(self, board, player):
        """Finds the best move using Pure Minimax (no pruning)."""
        self.analytics.start_timer()
        opponent = get_opponent(player)
        
        best_score = float('-inf')
        best_move = None
        
        valid_moves = board.get_valid_moves(player)
        if not valid_moves:
            self.analytics.stop_timer()
            return None, self.analytics.get_metrics()
            
        for r, c in valid_moves:
            self.analytics.increment_node()
            new_board = board.apply_move(r, c, player)
            if new_board:
                score = self._minimax(new_board, self.max_depth - 1, False, player, opponent)
                if score > best_score:
                    best_score = score
                    best_move = (r, c)
                    
        self.analytics.stop_timer()
        return best_move, self.analytics.get_metrics()

    def _minimax(self, board, depth, is_maximizing, ai_player, opponent):
        """Recursive pure Minimax function."""
        current_player = ai_player if is_maximizing else opponent
        valid_moves = board.get_valid_moves(current_player)
        
        if depth == 0 or len(valid_moves) == 0:
            if len(valid_moves) == 0 and len(board.get_valid_moves(get_opponent(current_player))) == 0:
                pass # terminal state
            else:
                if len(valid_moves) == 0:
                    # Pass turn
                    return self._minimax(board, depth - 1, not is_maximizing, ai_player, opponent)
                    
            return evaluate_state(board, ai_player, opponent)

        if is_maximizing:
            max_eval = float('-inf')
            for r, c in valid_moves:
                self.analytics.increment_node()
                new_board = board.apply_move(r, c, ai_player)
                if new_board:
                    eval = self._minimax(new_board, depth - 1, False, ai_player, opponent)
                    max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = float('inf')
            for r, c in valid_moves:
                self.analytics.increment_node()
                new_board = board.apply_move(r, c, opponent)
                if new_board:
                    eval = self._minimax(new_board, depth - 1, True, ai_player, opponent)
                    min_eval = min(min_eval, eval)
            return min_eval

class AlphaBetaAI:
    def __init__(self, max_depth=4):
        self.max_depth = max_depth
        self.analytics = AIAnalytics()

    def get_best_move(self, board, player):
        """Finds the best move using Minimax with Alpha-Beta Pruning and Move Ordering."""
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
            
        # Move Ordering: Sắp xếp các ô cờ có trọng số cao lên trước để duyệt trước
        from .heuristics import POSITIONAL_WEIGHTS
        valid_moves.sort(key=lambda m: POSITIONAL_WEIGHTS[m[0]][m[1]], reverse=True)

        for r, c in valid_moves:
            self.analytics.increment_node()
            new_board = board.apply_move(r, c, player)
            if new_board:
                score = self._alphabeta(new_board, self.max_depth - 1, alpha, beta, False, player, opponent)
                if score > best_score:
                    best_score = score
                    best_move = (r, c)
                alpha = max(alpha, best_score)
                
        self.analytics.stop_timer()
        return best_move, self.analytics.get_metrics()

    def _alphabeta(self, board, depth, alpha, beta, is_maximizing, ai_player, opponent):
        """Recursive Minimax with Alpha-Beta pruning."""
        current_player = ai_player if is_maximizing else opponent
        valid_moves = board.get_valid_moves(current_player)
        
        if depth == 0 or len(valid_moves) == 0:
            if len(valid_moves) == 0 and len(board.get_valid_moves(get_opponent(current_player))) == 0:
                pass
            else:
                if len(valid_moves) == 0:
                    return self._alphabeta(board, depth - 1, alpha, beta, not is_maximizing, ai_player, opponent)
            return evaluate_state(board, ai_player, opponent)

        # Move Ordering
        from .heuristics import POSITIONAL_WEIGHTS
        valid_moves.sort(key=lambda m: POSITIONAL_WEIGHTS[m[0]][m[1]], reverse=is_maximizing)

        if is_maximizing:
            max_eval = float('-inf')
            for r, c in valid_moves:
                self.analytics.increment_node()
                new_board = board.apply_move(r, c, ai_player)
                if new_board:
                    eval = self._alphabeta(new_board, depth - 1, alpha, beta, False, ai_player, opponent)
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
                    eval = self._alphabeta(new_board, depth - 1, alpha, beta, True, ai_player, opponent)
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break # Alpha cut-off
            return min_eval

import math

class MCTSNode:
    def __init__(self, board, parent=None, move=None, player=None):
        self.board = board
        self.parent = parent
        self.move = move  # Nước đi dẫn tới trạng thái này
        self.player = player  # Người chơi chuẩn bị đi từ trạng thái này
        self.children = {}  # Map từ move (tuple) -> MCTSNode
        self.visits = 0
        self.wins = 0.0

    def is_fully_expanded(self, valid_moves):
        return len(self.children) == len(valid_moves)

    def best_child(self, c_param=1.414):
        best_score = float('-inf')
        best_nodes = []
        for child in self.children.values():
            exploitation = child.wins / child.visits if child.visits > 0 else 0
            exploration = c_param * math.sqrt(math.log(self.visits) / child.visits) if child.visits > 0 else float('inf')
            score = exploitation + exploration
            if score > best_score:
                best_score = score
                best_nodes = [child]
            elif score == best_score:
                best_nodes.append(child)
        return random.choice(best_nodes) if best_nodes else None

class MCTSAI:
    def __init__(self, iterations=800, c_param=1.414):
        self.iterations = iterations
        self.c_param = c_param
        self.analytics = AIAnalytics()

    def get_best_move(self, board, player):
        """Tìm nước đi tối ưu bằng thuật toán Monte Carlo Tree Search (MCTS)."""
        self.analytics.start_timer()
        
        valid_moves = board.get_valid_moves(player)
        if not valid_moves:
            self.analytics.stop_timer()
            return None, self.analytics.get_metrics()
            
        if len(valid_moves) == 1:
            self.analytics.increment_node()
            self.analytics.stop_timer()
            return valid_moves[0], self.analytics.get_metrics()

        # Nút gốc đại diện cho trạng thái hiện tại
        root = MCTSNode(board, player=player)
        
        for _ in range(self.iterations):
            self.analytics.increment_node() # Đếm mỗi lần lặp (mô phỏng) là một node được mở rộng/duyệt qua
            node = root
            
            # 1. Selection (Lựa chọn)
            curr_board = node.board
            curr_player = node.player
            
            while True:
                moves = curr_board.get_valid_moves(curr_player)
                if not moves:
                    opp = get_opponent(curr_player)
                    opp_moves = curr_board.get_valid_moves(opp)
                    if not opp_moves:
                        break # Trạng thái kết thúc game
                    else:
                        curr_player = opp
                        break # Cần lật lượt đi trong cây, dừng lại để expand
                
                if not node.is_fully_expanded(moves):
                    break
                
                node = node.best_child(self.c_param)
                curr_board = node.board
                curr_player = node.player

            # 2. Expansion (Mở rộng)
            moves = node.board.get_valid_moves(node.player)
            if moves:
                unexpanded = [m for m in moves if m not in node.children]
                if unexpanded:
                    move = random.choice(unexpanded)
                    next_board = node.board.apply_move(move[0], move[1], node.player)
                    if next_board:
                        next_player = get_opponent(node.player)
                        # Xử lý bỏ lượt (pass)
                        if not next_board.get_valid_moves(next_player):
                            if next_board.get_valid_moves(node.player):
                                next_player = node.player
                        
                        child_node = MCTSNode(next_board, parent=node, move=move, player=next_player)
                        node.children[move] = child_node
                        node = child_node

            # 3. Simulation (Mô phỏng / Rollout)
            winner = self._simulate(node.board, node.player)

            # 4. Backpropagation (Lan truyền ngược)
            curr_node = node
            while curr_node is not None:
                curr_node.visits += 1
                if curr_node.parent:
                    parent_player = curr_node.parent.player
                    if winner == parent_player:
                        curr_node.wins += 1.0
                    elif winner == EMPTY:
                        curr_node.wins += 0.5
                curr_node = curr_node.parent

        # Nước đi tốt nhất là nước đi có số lượt ghé thăm (visits) nhiều nhất
        best_move = None
        max_visits = -1
        for move, child in root.children.items():
            if child.visits > max_visits:
                max_visits = child.visits
                best_move = move
                
        self.analytics.stop_timer()
        return best_move, self.analytics.get_metrics()

    def _simulate(self, board, start_player):
        """Thực hiện một ván đấu ngẫu nhiên đến khi kết thúc game."""
        curr_board = board
        curr_player = start_player
        consecutive_passes = 0
        
        while consecutive_passes < 2:
            moves = curr_board.get_valid_moves(curr_player)
            if not moves:
                consecutive_passes += 1
                curr_player = get_opponent(curr_player)
                continue
            
            consecutive_passes = 0
            move = random.choice(moves)
            new_board = curr_board.apply_move(move[0], move[1], curr_player)
            if new_board:
                curr_board = new_board
            curr_player = get_opponent(curr_player)
            
        black, white = curr_board.count_pieces()
        if black > white:
            return BLACK
        elif white > black:
            return WHITE
        return EMPTY
