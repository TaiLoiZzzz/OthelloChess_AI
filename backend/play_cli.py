import time
from backend.engine.constants import BLACK, WHITE, EMPTY
from backend.engine.game import Game
from backend.ai.algorithms import RandomAI, GreedyAI, MinimaxAI, AlphaBetaAI

def print_board_with_moves(board, valid_moves):
    symbols = {EMPTY: '.', BLACK: 'X', WHITE: 'O'}
    print("  0 1 2 3 4 5 6 7")
    for r in range(8):
        row_str = []
        for c in range(8):
            if (r, c) in valid_moves:
                row_str.append('*') # Valid move indicator
            else:
                row_str.append(symbols[board.grid[r][c]])
        print(f"{r} {' '.join(row_str)}")
    print()

def main():
    print("=== OTHELLO AI LABORATORY (CLI MODE) ===")
    print("Chế độ chơi:")
    print("1. Người chơi (X - Đen) vs Alpha-Beta AI (O - Trắng)")
    print("2. Pure Minimax AI (X - Đen) vs Alpha-Beta AI (O - Trắng) - ĐỂ BENCHMARK")
    print("3. Random AI (X - Đen) vs Greedy AI (O - Trắng)")
    
    choice = input("Lựa chọn (1-3): ").strip()
    if choice not in ['1', '2', '3']:
        choice = '1'

    game = Game()
    pure_minimax = MinimaxAI(max_depth=3) # Depth 3 cho pure minimax để không bị quá chậm
    alphabeta_ai = AlphaBetaAI(max_depth=4) # Depth 4 cho Alpha-Beta
    
    while not game.is_game_over:
        state = game.get_state()
        valid_moves = state["valid_moves"]
        current_player = game.current_player
        player_symbol = "X (Đen)" if current_player == BLACK else "O (Trắng)"
        
        print(f"\n--- Lượt của: {player_symbol} ---")
        print_board_with_moves(game.board, valid_moves)
        print(f"Điểm số - Đen (X): {state['black_score']} | Trắng (O): {state['white_score']}")

        if not valid_moves:
            print(f"{player_symbol} không có nước đi hợp lệ. Bỏ lượt!")
            game.pass_turn()
            continue

        # Chọn nước đi
        if choice == '1' and current_player == BLACK:
            # Lượt của Người chơi
            move_ok = False
            while not move_ok:
                try:
                    move_input = input("Nhập nước đi dạng 'dòng,cột' (VD: 2,3) hoặc 'exit' để thoát: ").strip()
                    if move_input.lower() == 'exit':
                        return
                    r, c = map(int, move_input.split(","))
                    if (r, c) in valid_moves:
                        game.play_turn(r, c)
                        move_ok = True
                    else:
                        print("Nước đi không hợp lệ! Hãy chọn ô có ký hiệu (*).")
                except ValueError:
                    print("Nhập sai định dạng. Ví dụ: 3,2")
        else:
            # Lượt của AI
            print("AI đang tính toán...")
            
            if current_player == BLACK:
                # Black AI
                if choice == '2':
                    move, metrics = pure_minimax.get_best_move(game.board, BLACK)
                    print(f"Pure Minimax AI (Depth 3) đi: {move} | Đã duyệt {metrics['nodes_expanded']} nodes trong {metrics['response_time_ms']}ms")
                else: # choice == '3'
                    move, metrics = RandomAI.get_best_move(game.board, BLACK)
                    print(f"Random AI đi: {move}")
            else:
                # White AI
                if choice == '3':
                    move, metrics = GreedyAI.get_best_move(game.board, WHITE)
                    print(f"Greedy AI đi: {move}")
                elif choice == '2':
                    move, metrics = alphabeta_ai.get_best_move(game.board, WHITE)
                    print(f"Alpha-Beta AI (Depth 4) đi: {move} | Đã duyệt {metrics['nodes_expanded']} nodes trong {metrics['response_time_ms']}ms")
                else: # choice == '1'
                    move, metrics = alphabeta_ai.get_best_move(game.board, WHITE)
                    print(f"Alpha-Beta AI (Depth 4) đi: {move} | Đã duyệt {metrics['nodes_expanded']} nodes trong {metrics['response_time_ms']}ms")
            
            if move:
                game.play_turn(move[0], move[1])
            time.sleep(0.5) # Dừng một chút để dễ theo dõi

    # Kết quả chung cuộc
    print("\n=== TRÒ CHƠI KẾT THÚC ===")
    state = game.get_state()
    print_board_with_moves(game.board, [])
    print(f"Điểm chung cuộc - Đen (X): {state['black_score']} | Trắng (O): {state['white_score']}")
    if state["winner"] == BLACK:
        print("Người thắng: Đen (X)")
    elif state["winner"] == WHITE:
        print("Người thắng: Trắng (O)")
    else:
        print("Kết quả: Hòa!")

if __name__ == "__main__":
    main()
