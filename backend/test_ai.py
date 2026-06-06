import unittest
from backend.engine.constants import BLACK, WHITE
from backend.engine.board import Board
from backend.ai.algorithms import RandomAI, GreedyAI, MinimaxAI, AlphaBetaAI

class TestAIModule(unittest.TestCase):
    def setUp(self):
        self.board = Board()

    def test_random_ai(self):
        """Test if Random AI returns a valid move"""
        move, metrics = RandomAI.get_best_move(self.board, BLACK)
        self.assertIsNotNone(move)
        self.assertIn(move, self.board.get_valid_moves(BLACK))
        self.assertIn('response_time_ms', metrics)
        self.assertIn('nodes_expanded', metrics)
        self.assertEqual(metrics['nodes_expanded'], 1)

    def test_greedy_ai(self):
        """Test if Greedy AI picks the move with max flips"""
        # In initial state, all moves flip exactly 1 piece.
        # So we just ensure it returns a valid move.
        move, metrics = GreedyAI.get_best_move(self.board, BLACK)
        self.assertIsNotNone(move)
        self.assertIn(move, self.board.get_valid_moves(BLACK))
        self.assertTrue(metrics['nodes_expanded'] >= len(self.board.get_valid_moves(BLACK)))

    def test_minimax_ai(self):
        """Test if Pure Minimax AI works correctly without crashing"""
        ai = MinimaxAI(max_depth=2)
        move, metrics = ai.get_best_move(self.board, BLACK)
        self.assertIsNotNone(move)
        self.assertIn(move, self.board.get_valid_moves(BLACK))
        self.assertTrue(metrics['nodes_expanded'] > 4) 
        self.assertIn('response_time_ms', metrics)

    def test_alphabeta_ai(self):
        """Test if Alpha-Beta AI works correctly and optimizes search space"""
        # Search at depth 3 for both, pure minimax should expand more nodes than alpha-beta
        pure_ai = MinimaxAI(max_depth=3)
        ab_ai = AlphaBetaAI(max_depth=3)
        
        _, pure_metrics = pure_ai.get_best_move(self.board, BLACK)
        _, ab_metrics = ab_ai.get_best_move(self.board, BLACK)
        
        # Alpha-Beta should expand strictly fewer nodes than pure minimax due to pruning
        self.assertTrue(ab_metrics['nodes_expanded'] < pure_metrics['nodes_expanded'])
        self.assertIn('response_time_ms', ab_metrics)

    def test_greedy_vs_random_sanity_check(self):
        """
        Simple sanity check. We simulate a small interaction.
        Greedy should process valid moves correctly.
        """
        b = Board()
        # Give Black a very obvious winning move configuration if possible
        # We will just verify the APIs are consistent
        m1, _ = GreedyAI.get_best_move(b, BLACK)
        b = b.apply_move(m1[0], m1[1], BLACK)
        m2, _ = RandomAI.get_best_move(b, WHITE)
        self.assertIsNotNone(m2)

if __name__ == '__main__':
    unittest.main()
