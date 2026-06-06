# Othello (Reversi) AI Laboratory & Benchmark Dashboard

Ứng dụng Desktop chuyên nghiệp mô phỏng trò chơi Othello (Reversi) phục vụ học tập, nghiên cứu và benchmark các thuật toán tìm kiếm đối kháng (Adversarial Search).

## Các tính năng chính

1. **Core Game Engine độc lập**:
   - Ma trận 8x8 quản lý trạng thái, tính toán nước đi hợp lệ theo 8 hướng.
   - Hỗ trợ đổi lượt (turn switching), bỏ lượt (pass turn) và tính điểm cuối ván cờ.

2. **4 Cấp độ thuật toán AI đối kháng**:
   - **Cấp độ 1 (Baseline - Random)**: Chọn ngẫu nhiên nước đi hợp lệ.
   - **Cấp độ 2 (Greedy - Tham lam)**: Đi nước ăn được nhiều quân nhất ngay lập tức.
   - **Cấp độ 3 (Core - Pure Minimax)**: Duyệt cây đối kháng đầy đủ theo độ sâu.
   - **Cấp độ 4 (Optimized - Alpha-Beta Pruning)**: Cắt tỉa nhánh Alpha-Beta kết hợp với **Move Ordering** (sắp xếp thứ tự ưu tiên ô cờ trọng số cao để cắt tỉa tối đa cây tìm kiếm).

3. **Giao diện Desktop chuyên nghiệp (PyQt6)**:
   - Giao diện Dark Mode trực quan, mượt mà.
   - **Heuristic Heatmap Overlay**: Hiển thị trực tiếp bản đồ nhiệt giá trị chiến lược của các ô cờ (Ví dụ: Góc hiển thị xanh lục điểm cộng lớn, các ô cạnh góc hiển thị màu đỏ cảnh báo nguy hiểm). Thay đổi độ ưu tiên tùy theo giai đoạn trận đấu.
   - **Hint (Gợi ý)**: Người chơi có thể yêu cầu AI tính toán và hiển thị gợi ý nước đi tối ưu ngay lập tức.
   - **Real-time Performance Chart**: Biểu đồ tích hợp bằng `matplotlib` hiển thị trực tiếp thời gian phản hồi (Response Time - ms) và tổng số node đã duyệt của AI qua từng lượt đi, giúp so sánh hiệu năng cắt tỉa rõ rệt.

## Cách chạy ứng dụng

### Cách 1: Sử dụng file chạy nhanh (Khuyên dùng)
Bạn chỉ cần kích đúp chuột vào file:
- **`run_gui.bat`** (Tự động kích hoạt môi trường ảo Python venv được cài trên ổ E và khởi chạy ứng dụng).

### Cách 2: Chạy thủ công từ Terminal
1. Kích hoạt môi trường ảo Python:
   ```powershell
   venv\Scripts\activate
   ```
2. Khởi chạy ứng dụng:
   ```powershell
   python gui/app.py
   ```

## Các lệnh kiểm thử (Unit Tests)

- Chạy kiểm thử Game Engine:
  ```powershell
  python -m unittest backend/test_engine.py
  ```
- Chạy kiểm thử Thuật toán AI:
  ```powershell
  python -m unittest backend/test_ai.py
  ```
