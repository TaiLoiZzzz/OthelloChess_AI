import sys
import os
import random
import time
import matplotlib
matplotlib.use("QtAgg")

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QComboBox, QLabel, QPushButton, QCheckBox, QSpinBox,
    QGroupBox, QFrame, QMessageBox
)
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QFont
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer

# Import Game Engine và AI
# Đảm bảo import đúng đường dẫn từ backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.engine.constants import BOARD_SIZE, EMPTY, BLACK, WHITE, get_opponent
from backend.engine.game import Game
from backend.ai.algorithms import RandomAI, GreedyAI, MinimaxAI, AlphaBetaAI
from backend.ai.heuristics import POSITIONAL_WEIGHTS

class AIWorker(QThread):
    """Worker Thread để tính toán nước đi AI, tránh đóng băng giao diện (GUI Freezing)"""
    move_found = pyqtSignal(tuple, dict)  # Trả về nước đi (row, col) và metrics hiệu năng

    def __init__(self, board, player, algorithm, depth):
        super().__init__()
        self.board = board
        self.player = player
        self.algorithm = algorithm
        self.depth = depth

    def run(self):
        if self.algorithm == "Random":
            move, metrics = RandomAI.get_best_move(self.board, self.player)
        elif self.algorithm == "Greedy":
            move, metrics = GreedyAI.get_best_move(self.board, self.player)
        elif self.algorithm == "Minimax":
            ai = MinimaxAI(max_depth=self.depth)
            move, metrics = ai.get_best_move(self.board, self.player)
        elif self.algorithm == "Alpha-Beta":
            ai = AlphaBetaAI(max_depth=self.depth)
            move, metrics = ai.get_best_move(self.board, self.player)
        else:
            move, metrics = None, {}

        self.move_found.emit(move if move is not None else (-1, -1), metrics)


class BoardWidget(QWidget):
    """Widget vẽ bàn cờ Othello 8x8"""
    cell_clicked = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.game = None
        self.show_heatmap = False
        self.show_hint = False
        self.hint_move = None
        self.setMinimumSize(450, 450)

    def update_board(self, game, show_heatmap=False, show_hint=False, hint_move=None):
        self.game = game
        self.show_heatmap = show_heatmap
        self.show_hint = show_hint
        self.hint_move = hint_move
        self.update()

    def paintEvent(self, event):
        if not self.game:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Tính toán kích thước ô cờ
        width = self.width()
        height = self.height()
        cell_w = width / BOARD_SIZE
        cell_h = height / BOARD_SIZE

        # 1. Vẽ nền bàn cờ màu xanh lục đậm chuẩn Othello
        painter.setBrush(QBrush(QColor("#27ae60")))
        painter.setPen(QPen(QColor("#2c3e50"), 2))
        painter.drawRect(0, 0, width, height)

        # 2. Vẽ lưới bàn cờ và Heatmap Overlay
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x = c * cell_w
                y = r * cell_h

                # Vẽ viền ô cờ
                painter.setPen(QPen(QColor("#1e824c"), 1))
                painter.drawRect(int(x), int(y), int(cell_w), int(cell_h))

                # Vẽ Heatmap nếu được bật
                if self.show_heatmap:
                    weight = POSITIONAL_WEIGHTS[r][c]
                    # Màu xanh lá đậm = Rất tốt (Corners)
                    # Màu vàng/xanh nhạt = Bình thường
                    # Màu đỏ = Rất nguy hiểm (Cạnh góc)
                    if weight >= 50:
                        color = QColor(46, 204, 113, 120)  # Green
                    elif weight >= 5:
                        color = QColor(241, 196, 15, 80)   # Yellow
                    elif weight <= -20:
                        color = QColor(231, 76, 60, 150)   # Red
                    else:
                        color = QColor(255, 255, 255, 30)  # White mờ
                    
                    painter.fillRect(int(x+1), int(y+1), int(cell_w-1), int(cell_h-1), QBrush(color))

        # 3. Vẽ quân cờ và nước đi hợp lệ
        state = self.game.get_state()
        valid_moves = state["valid_moves"]

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x = c * cell_w
                y = r * cell_h
                cell_val = self.game.board.grid[r][c]

                # Vẽ quân cờ
                if cell_val != EMPTY:
                    # Đổ bóng nhẹ cho quân cờ trông premium hơn
                    painter.setBrush(QBrush(QColor(0, 0, 0, 50)))
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawEllipse(int(x + cell_w*0.13), int(y + cell_h*0.13), int(cell_w*0.8), int(cell_h*0.8))

                    # Vẽ quân cờ chính
                    if cell_val == BLACK:
                        painter.setBrush(QBrush(QColor("#2c3e50"))) # Xanh đen
                        painter.setPen(QPen(QColor("#000000"), 1))
                    else: # WHITE
                        painter.setBrush(QBrush(QColor("#ecf0f1"))) # Trắng xám
                        painter.setPen(QPen(QColor("#bdc3c7"), 1))
                    
                    painter.drawEllipse(int(x + cell_w*0.1), int(y + cell_h*0.1), int(cell_w*0.8), int(cell_h*0.8))

                # Vẽ chấm gợi ý nước đi hợp lệ
                elif (r, c) in valid_moves:
                    painter.setBrush(QBrush(QColor(255, 255, 255, 120)))
                    painter.setPen(QPen(QColor(255, 255, 255, 200), 1, Qt.PenStyle.DashLine))
                    painter.drawEllipse(int(x + cell_w*0.4), int(y + cell_h*0.4), int(cell_w*0.2), int(cell_h*0.2))

        # 4. Vẽ gợi ý Hint (nếu được chọn)
        if self.show_hint and self.hint_move and self.game.current_player == BLACK:
            hr, hc = self.hint_move
            hx = hc * cell_w
            hy = hr * cell_h
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor("#f1c40f"), 3, Qt.PenStyle.SolidLine)) # Viền vàng lấp lánh
            painter.drawRect(int(hx + 2), int(hy + 2), int(cell_w - 4), int(cell_h - 4))

    def mousePressEvent(self, event):
        if not self.game:
            return
        
        # Lấy tọa độ ô cờ từ click chuột
        cell_w = self.width() / BOARD_SIZE
        cell_h = self.height() / BOARD_SIZE
        c = int(event.position().x() // cell_w)
        r = int(event.position().y() // cell_h)
        
        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            self.cell_clicked.emit(r, c)


class PerformanceCanvas(FigureCanvas):
    """Widget matplotlib vẽ biểu đồ benchmark thời gian thực"""
    def __init__(self, width=5, height=3, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#2c3e50')
        self.axes_time = fig.add_subplot(111)
        self.axes_nodes = self.axes_time.twinx()
        
        super().__init__(fig)
        
        self.time_data = []
        self.nodes_data = []
        self.move_indices = []
        self._setup_plot()

    def _setup_plot(self):
        self.axes_time.clear()
        self.axes_nodes.clear()
        
        self.axes_time.set_facecolor('#34495e')
        self.axes_time.set_title("Benchmark Hiệu Năng AI", color='white', fontsize=10, fontweight='bold')
        self.axes_time.set_xlabel("Nước Đi", color='white', fontsize=8)
        self.axes_time.set_ylabel("Thời Gian (ms)", color='#e74c3c', fontsize=8)
        self.axes_nodes.set_ylabel("Nodes Đã Duyệt", color='#3498db', fontsize=8)
        
        self.axes_time.tick_params(colors='white', labelsize=8)
        self.axes_nodes.tick_params(colors='white', labelsize=8)
        self.axes_time.grid(True, color='#7f8c8d', linestyle=':', alpha=0.5)

    def reset(self):
        self.time_data = []
        self.nodes_data = []
        self.move_indices = []
        self._setup_plot()
        self.draw()

    def add_metrics(self, response_time, nodes_expanded):
        move_num = len(self.move_indices) + 1
        self.move_indices.append(move_num)
        self.time_data.append(response_time)
        self.nodes_data.append(nodes_expanded)
        
        self._setup_plot()
        
        # Vẽ dữ liệu thời gian phản hồi (màu đỏ)
        self.axes_time.plot(self.move_indices, self.time_data, color='#e74c3c', marker='o', linewidth=2, label='Time (ms)')
        # Vẽ dữ liệu nodes đã duyệt (màu xanh dương)
        self.axes_nodes.plot(self.move_indices, self.nodes_data, color='#3498db', marker='s', linewidth=2, linestyle='--', label='Nodes')
        
        # Thêm chú thích (Legend)
        lines1, labels1 = self.axes_time.get_images_and_labels() if hasattr(self.axes_time, 'get_images_and_labels') else ([], [])
        # Matplotlib workaround
        h1, l1 = self.axes_time.get_legend_handles_labels()
        h2, l2 = self.axes_nodes.get_legend_handles_labels()
        self.axes_time.legend(h1+h2, l1+l2, loc='upper left', fontsize=7, facecolor='#2c3e50', edgecolor='white', labelcolor='white')
        
        self.draw()


class OthelloApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Othello AI Laboratory & Benchmark Dashboard")
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50;
            }
            QLabel {
                color: #ecf0f1;
                font-size: 12px;
            }
            QGroupBox {
                border: 2px solid #34495e;
                border-radius: 8px;
                margin-top: 10px;
                color: #ecf0f1;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QComboBox, QSpinBox {
                background-color: #34495e;
                color: white;
                border: 1px solid #7f8c8d;
                border-radius: 4px;
                padding: 4px;
                min-width: 100px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f3a52;
            }
            QCheckBox {
                color: #ecf0f1;
            }
        """)

        self.game = Game()
        self.ai_worker = None
        self.is_paused = False
        
        # Timer cho chế độ tự động AI vs AI
        self.ai_timer = QTimer()
        self.ai_timer.timeout.connect(self.process_ai_turn)

        self.setup_ui()
        self.start_new_game()

    def setup_ui(self):
        # Widget trung tâm
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # ---------------- BÊN TRÁI: BÀN CỜ ----------------
        left_layout = QVBoxLayout()
        
        # Header Điểm số
        self.score_frame = QFrame()
        self.score_frame.setStyleSheet("background-color: #34495e; border-radius: 8px; padding: 10px;")
        score_layout = QHBoxLayout(self.score_frame)
        
        self.lbl_turn = QLabel("Lượt đi: Đen (Human)")
        self.lbl_turn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.lbl_score_black = QLabel("Đen (X): 2")
        self.lbl_score_black.setFont(QFont("Arial", 12))
        self.lbl_score_white = QLabel("Trắng (O): 2")
        self.lbl_score_white.setFont(QFont("Arial", 12))
        
        score_layout.addWidget(self.lbl_turn)
        score_layout.addStretch()
        score_layout.addWidget(self.lbl_score_black)
        score_layout.addWidget(self.lbl_score_white)
        
        left_layout.addWidget(self.score_frame)

        # Bàn cờ vẽ bằng QPainter
        self.board_widget = BoardWidget()
        self.board_widget.cell_clicked.connect(self.handle_human_move)
        left_layout.addWidget(self.board_widget)

        # ---------------- BÊN PHẢI: BẢNG ĐIỀU KHIỂN & BIỂU ĐỒ ----------------
        right_layout = QVBoxLayout()

        # Group cấu hình Game Mode và Algorithms
        config_group = QGroupBox("Cấu Hình Trận Đấu")
        config_layout = QGridLayout(config_group)

        # Combo chọn chế độ
        config_layout.addWidget(QLabel("Chế độ chơi:"), 0, 0)
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["Người vs AI", "AI vs AI"])
        self.combo_mode.currentIndexChanged.connect(self.on_mode_changed)
        config_layout.addWidget(self.combo_mode, 0, 1)

        # Đen (Player 1)
        config_layout.addWidget(QLabel("Quân Đen (Đi trước):"), 1, 0)
        self.combo_black_algo = QComboBox()
        self.combo_black_algo.addItems(["Human", "Random", "Greedy", "Minimax", "Alpha-Beta"])
        self.combo_black_algo.currentIndexChanged.connect(self.on_players_changed)
        config_layout.addWidget(self.combo_black_algo, 1, 1)

        # Trắng (Player 2)
        config_layout.addWidget(QLabel("Quân Trắng (Đi sau):"), 2, 0)
        self.combo_white_algo = QComboBox()
        self.combo_white_algo.addItems(["Human", "Random", "Greedy", "Minimax", "Alpha-Beta"])
        self.combo_white_algo.setCurrentText("Alpha-Beta")
        self.combo_white_algo.currentIndexChanged.connect(self.on_players_changed)
        config_layout.addWidget(self.combo_white_algo, 2, 1)

        # Cấu hình chiều sâu Minimax/Alpha-Beta
        config_layout.addWidget(QLabel("Độ sâu Minimax/AB:"), 3, 0)
        self.spin_depth = QSpinBox()
        self.spin_depth.setRange(1, 8)
        self.spin_depth.setValue(4)
        config_layout.addWidget(self.spin_depth, 3, 1)

        right_layout.addWidget(config_group)

        # Group tính năng trực quan hóa nâng cao
        viz_group = QGroupBox("Tùy Chọn Trực Quan")
        viz_layout = QVBoxLayout(viz_group)
        
        self.chk_heatmap = QCheckBox("Hiển thị Heuristic Heatmap")
        self.chk_heatmap.stateChanged.connect(self.toggle_visuals)
        viz_layout.addWidget(self.chk_heatmap)

        self.chk_hint = QCheckBox("Bật gợi ý nước đi (Hint)")
        self.chk_hint.stateChanged.connect(self.toggle_visuals)
        viz_layout.addWidget(self.chk_hint)

        self.btn_hint = QPushButton("Yêu cầu gợi ý nước đi ngay")
        self.btn_hint.clicked.connect(self.request_immediate_hint)
        viz_layout.addWidget(self.btn_hint)

        right_layout.addWidget(viz_group)

        # Khu vực Biểu đồ Benchmark Matplotlib
        self.chart_canvas = PerformanceCanvas(width=5, height=3)
        right_layout.addWidget(self.chart_canvas)

        # Khu vực Nút chức năng tổng quát
        btn_layout = QHBoxLayout()
        self.btn_restart = QPushButton("Ván Mới")
        self.btn_restart.clicked.connect(self.start_new_game)
        self.btn_restart.setStyleSheet("background-color: #27ae60;")
        
        self.btn_pause = QPushButton("Tạm Dừng AI")
        self.btn_pause.clicked.connect(self.toggle_pause)
        self.btn_pause.setStyleSheet("background-color: #f39c12;")
        
        btn_layout.addWidget(self.btn_restart)
        btn_layout.addWidget(self.btn_pause)
        right_layout.addLayout(btn_layout)

        # Đặt tỷ lệ layout chính
        main_layout.addLayout(left_layout, 3)
        main_layout.addLayout(right_layout, 2)

    def on_mode_changed(self):
        """Tự động thay đổi Combobox thuật toán tương ứng khi chuyển Game Mode"""
        mode = self.combo_mode.currentText()
        if mode == "Người vs AI":
            self.combo_black_algo.setCurrentText("Human")
            self.combo_white_algo.setCurrentText("Alpha-Beta")
        else: # AI vs AI
            self.combo_black_algo.setCurrentText("Greedy")
            self.combo_white_algo.setCurrentText("Alpha-Beta")

    def on_players_changed(self):
        """Cập nhật giao diện khi thuật toán được đổi giữa chừng"""
        black_algo = self.combo_black_algo.currentText()
        if black_algo == "Human":
            self.combo_mode.setCurrentText("Người vs AI")
        else:
            # Nếu cả 2 đều không phải Human thì là AI vs AI
            white_algo = self.combo_white_algo.currentText()
            if white_algo != "Human":
                self.combo_mode.setCurrentText("AI vs AI")

    def start_new_game(self):
        # Kết thúc worker cũ nếu có
        if self.ai_worker and self.ai_worker.isRunning():
            self.ai_worker.terminate()
            self.ai_worker.wait()

        self.game = Game()
        self.is_paused = False
        self.btn_pause.setText("Tạm Dừng AI")
        self.chart_canvas.reset()
        self.board_widget.update_board(self.game)
        self.update_stats_display()

        # Kích hoạt vòng lặp AI nếu cần
        self.trigger_next_turn()

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.btn_pause.setText("Tiếp Tục AI")
            self.ai_timer.stop()
        else:
            self.btn_pause.setText("Tạm Dừng AI")
            self.trigger_next_turn()

    def toggle_visuals(self):
        self.board_widget.show_heatmap = self.chk_heatmap.isChecked()
        self.board_widget.show_hint = self.chk_hint.isChecked()
        if not self.board_widget.show_hint:
            self.board_widget.hint_move = None
        self.board_widget.update()

    def request_immediate_hint(self):
        """Tận dụng AlphaBetaAI để tìm kiếm gợi ý nước đi tối ưu ngay lập tức"""
        if self.game.is_game_over:
            return
        
        valid_moves = self.game.board.get_valid_moves(self.game.current_player)
        if not valid_moves:
            QMessageBox.information(self, "Gợi Ý Nước Đi", "Bạn không có nước đi hợp lệ nào trong lượt này!")
            return
            
        ai = AlphaBetaAI(max_depth=4)
        best_move, _ = ai.get_best_move(self.game.board, self.game.current_player)
        
        if best_move:
            self.board_widget.hint_move = best_move
            self.board_widget.show_hint = True
            self.chk_hint.setChecked(True)
            self.board_widget.update()
            
            # Tính toán vị trí tương ứng chữ cái cho dòng/cột để dễ nhận biết (Ví dụ: D3)
            col_letter = chr(ord('A') + best_move[1])
            row_num = best_move[0] + 1
            QMessageBox.information(
                self, 
                "Gợi Ý Nước Đi", 
                f"Nước đi tốt nhất cho bạn là ô {col_letter}{row_num} (Dòng {best_move[0]}, Cột {best_move[1]})."
            )

    def update_stats_display(self):
        """Cập nhật text hiển thị điểm và lượt chơi"""
        state = self.game.get_state()
        self.lbl_score_black.setText(f"Đen (X): {state['black_score']}")
        self.lbl_score_white.setText(f"Trắng (O): {state['white_score']}")

        if state["is_game_over"]:
            self.lbl_turn.setText("GAME OVER!")
            self.ai_timer.stop()
            winner = state["winner"]
            if winner == BLACK:
                msg = f"Đen (BLACK) CHIẾN THẮNG! Tỉ số {state['black_score']} - {state['white_score']}"
            elif winner == WHITE:
                msg = f"Trắng (WHITE) CHIẾN THẮNG! Tỉ số {state['white_score']} - {state['black_score']}"
            else:
                msg = f"HÒA CỜ! Tỉ số {state['black_score']} - {state['white_score']}"
            QMessageBox.information(self, "Kết Quả Trận Đấu", msg)
        else:
            player_name = "Đen (X)" if self.game.current_player == BLACK else "Trắng (O)"
            algo = self.combo_black_algo.currentText() if self.game.current_player == BLACK else self.combo_white_algo.currentText()
            self.lbl_turn.setText(f"Lượt: {player_name} - {algo}")

    def trigger_next_turn(self):
        if self.game.is_game_over or self.is_paused:
            return

        current_player = self.game.current_player
        algo = self.combo_black_algo.currentText() if current_player == BLACK else self.combo_white_algo.currentText()

        # Kiểm tra nếu đến lượt đi của AI
        if algo != "Human":
            self.ai_timer.start(500) # Đợi 500ms tạo độ trễ trực quan cho người xem
        else:
            self.ai_timer.stop()
            # Nếu bật chế độ gợi ý tự động cho người chơi
            if self.chk_hint.isChecked():
                # Chạy luồng ẩn tìm nước gợi ý để không gây đơ GUI
                QTimer.singleShot(100, self.compute_auto_hint)

    def compute_auto_hint(self):
        if self.game.is_game_over or self.game.current_player != BLACK:
            return
        
        valid_moves = self.game.board.get_valid_moves(self.game.current_player)
        if valid_moves:
            ai = AlphaBetaAI(max_depth=3)
            best_move, _ = ai.get_best_move(self.game.board, self.game.current_player)
            self.board_widget.hint_move = best_move
            self.board_widget.update()

    def process_ai_turn(self):
        self.ai_timer.stop()
        if self.game.is_game_over or self.is_paused:
            return

        current_player = self.game.current_player
        algo = self.combo_black_algo.currentText() if current_player == BLACK else self.combo_white_algo.currentText()

        if algo == "Human":
            return

        # Khởi chạy luồng Worker để AI suy nghĩ độc lập
        self.ai_worker = AIWorker(
            board=self.game.board,
            player=current_player,
            algorithm=algo,
            depth=self.spin_depth.value()
        )
        self.ai_worker.move_found.connect(self.handle_ai_move_result)
        self.ai_worker.start()

    def handle_ai_move_result(self, move, metrics):
        """Nhận kết quả nước đi từ luồng AI và cập nhật lên GUI"""
        if self.is_paused:
            return
            
        r, c = move
        if r != -1 and c != -1:
            # Đi cờ
            success = self.game.play_turn(r, c)
            if success:
                # Cập nhật biểu đồ Benchmark vẽ thời gian phản hồi và số node duyệt
                self.chart_canvas.add_metrics(metrics.get("response_time_ms", 0), metrics.get("nodes_expanded", 0))
        else:
            # Không có nước đi hợp lệ -> AI pass lượt
            self.game.pass_turn()

        self.board_widget.update_board(self.game, self.chk_heatmap.isChecked(), self.chk_hint.isChecked(), self.board_widget.hint_move)
        self.update_stats_display()
        self.trigger_next_turn()

    def handle_human_move(self, r, c):
        """Xử lý click chuột của người chơi trên bàn cờ"""
        if self.game.is_game_over or self.is_paused:
            return

        current_player = self.game.current_player
        algo = self.combo_black_algo.currentText() if current_player == BLACK else self.combo_white_algo.currentText()

        # Chỉ cho phép di chuyển nếu đến lượt của Human
        if algo == "Human":
            valid_moves = self.game.board.get_valid_moves(current_player)
            if (r, c) in valid_moves:
                self.game.play_turn(r, c)
                self.board_widget.hint_move = None  # Xóa hint cũ sau khi đi cờ
                self.board_widget.update_board(self.game, self.chk_heatmap.isChecked(), self.chk_hint.isChecked())
                self.update_stats_display()
                self.trigger_next_turn()


def main():
    app = QApplication(sys.argv)
    window = OthelloApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
