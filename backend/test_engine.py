import unittest
from backend.engine.constants import BLACK, WHITE, EMPTY
from backend.engine.board import Board
from backend.engine.game import Game

class TestCoreEngine(unittest.TestCase):
    def setUp(self):
        """Initialize objects before each test"""
        self.board = Board()
        self.game = Game()

    def test_initial_board(self):
        """Test the initial 4 pieces are placed correctly"""
        black_count, white_count = self.board.count_pieces()
        self.assertEqual(black_count, 2)
        self.assertEqual(white_count, 2)
        self.assertEqual(self.board.get_cell(3, 3), WHITE)
        self.assertEqual(self.board.get_cell(4, 4), WHITE)
        self.assertEqual(self.board.get_cell(3, 4), BLACK)
        self.assertEqual(self.board.get_cell(4, 3), BLACK)

    def test_valid_moves_initial(self):
        """Test that black has exactly 4 valid moves at the start"""
        valid_moves = self.board.get_valid_moves(BLACK)
        expected_moves = [(2, 3), (3, 2), (4, 5), (5, 4)]
        self.assertEqual(len(valid_moves), 4)
        for move in expected_moves:
            self.assertIn(move, valid_moves)

    def test_apply_move(self):
        """Test applying a valid move and flipping pieces"""
        # Black moves to (2, 3)
        new_board = self.board.apply_move(2, 3, BLACK)
        self.assertIsNotNone(new_board)
        
        # Piece at (2,3) should be BLACK
        self.assertEqual(new_board.get_cell(2, 3), BLACK)
        # Piece at (3,3) should be flipped to BLACK
        self.assertEqual(new_board.get_cell(3, 3), BLACK)
        
        black_count, white_count = new_board.count_pieces()
        self.assertEqual(black_count, 4) # 2 initial + 1 placed + 1 flipped
        self.assertEqual(white_count, 1) # 2 initial - 1 flipped

    def test_invalid_move(self):
        """Test that an invalid move returns None"""
        # Try placing piece far away
        new_board = self.board.apply_move(0, 0, BLACK)
        self.assertIsNone(new_board)
        
        # Try placing piece on an occupied cell
        new_board_2 = self.board.apply_move(3, 3, BLACK)
        self.assertIsNone(new_board_2)

    def test_game_flow(self):
        """Test standard turn switching and state update"""
        # Black plays (2, 3)
        success = self.game.play_turn(2, 3)
        self.assertTrue(success)
        self.assertEqual(self.game.current_player, WHITE)
        
        state = self.game.get_state()
        self.assertEqual(state['black_score'], 4)
        self.assertEqual(state['white_score'], 1)
        
        # White plays (2, 2) or (2, 4) or (4, 2)
        valid_white = self.game.board.get_valid_moves(WHITE)
        self.assertTrue(len(valid_white) > 0)
        
        success_white = self.game.play_turn(valid_white[0][0], valid_white[0][1])
        self.assertTrue(success_white)
        self.assertEqual(self.game.current_player, BLACK)

if __name__ == '__main__':
    unittest.main()
