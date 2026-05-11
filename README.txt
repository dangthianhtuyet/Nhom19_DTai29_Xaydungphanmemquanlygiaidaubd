╔══════════════════════════════════════════════╗
║         FOOTBALL MANAGER                    ║
║         Quản lý giải đấu bóng đá            ║
╚══════════════════════════════════════════════╝

CÀI ĐẶT:
  pip install PySide6

CHẠY:
  cd football_manager
  python main.py

CẤU TRÚC:
  main.py           — Entry point, màn hình chọn giải đấu
  models/           — Dữ liệu: Player, Team, Match, Tournament
  db/               — SQLite database (lưu tại ~/.football_manager/tournaments.db)
  ui/               — Giao diện: mỗi tab 1 file riêng
  utils/            — Hàm tiện ích dùng chung

DATABASE:
  Dữ liệu lưu tự động vào:
    Windows: C:\Users\<tên>\\.football_manager\tournaments.db
    Mac/Linux: ~/.football_manager/tournaments.db

  Có thể quản lý nhiều giải đấu cùng lúc.
  Auto-save mỗi 60 giây khi có thay đổi.
