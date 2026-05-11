# -*- coding: utf-8 -*-
"""
main.py — Entry point Football Manager
Cài đặt: pip install PySide6
Chạy:    python main.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QDialog, QFormLayout, QLineEdit,
    QListWidget, QListWidgetItem, QMessageBox, QDialogButtonBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from models.tournament import Tournament
from db.database import init_db, get_db
from ui.teams_tab     import TeamsTab
from ui.schedule_tab  import ScheduleTab
from ui.standings_tab import StandingsTab
from ui.knockout_tab  import KnockoutTab
from ui.stats_tab     import StatsTab
from utils.helpers    import STYLE, make_btn, make_label, separator


class _NewTournamentDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Tạo giải đấu mới")
        self.setMinimumWidth(320)
        self.setStyleSheet(STYLE)
        layout = QFormLayout(self)
        layout.setSpacing(12)
        self.name_edit   = QLineEdit("Giải Đấu Bóng Đá")
        self.season_edit = QLineEdit("2024-2025")
        layout.addRow("Tên giải:", self.name_edit)
        layout.addRow("Mùa giải:", self.season_edit)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.Ok).setStyleSheet(
            "background:#00d084;color:#0d1117;font-weight:bold;padding:7px 20px;border-radius:5px;")
        btns.button(QDialogButtonBox.Cancel).setStyleSheet(
            "background:#2e3440;color:#cdd6e0;padding:7px 20px;border-radius:5px;")
        layout.addRow(btns)

    def get_data(self):
        return self.name_edit.text().strip(), self.season_edit.text().strip()


class TournamentSelectorDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Football Manager")
        self.setMinimumSize(520, 420)
        self.setStyleSheet(STYLE)
        self.selected_id = None
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        v = QVBoxLayout(self)
        v.setSpacing(12)
        v.setContentsMargins(20, 20, 20, 20)

        title = QLabel("⚽  FOOTBALL MANAGER")
        title.setStyleSheet("font-size:26px;font-weight:bold;color:#00d084;letter-spacing:2px;")
        title.setAlignment(Qt.AlignCenter)
        v.addWidget(title)

        sub = QLabel("Chọn giải đấu hoặc tạo mới")
        sub.setStyleSheet("font-size:13px;color:#8a9bb0;")
        sub.setAlignment(Qt.AlignCenter)
        v.addWidget(sub)
        v.addWidget(separator())

        self.lst = QListWidget()
        self.lst.setStyleSheet("""
            QListWidget{background:#1e2128;border:1px solid #2e3440;border-radius:8px;}
            QListWidget::item{padding:14px 16px;border-bottom:1px solid #252930;color:#e8eaf0;font-size:13px;}
            QListWidget::item:selected{background:#00d08430;color:#00d084;border-left:3px solid #00d084;}
            QListWidget::item:hover{background:#2a2f38;}
        """)
        self.lst.itemDoubleClicked.connect(self._open)
        v.addWidget(self.lst)

        btn_row = QHBoxLayout()
        btn_new  = make_btn("➕  Tạo mới", self._create)
        btn_open = make_btn("📂  Mở",      self._open)
        btn_del  = make_btn("🗑  Xóa",     self._delete, "danger")
        btn_open.setStyleSheet("background:#4a9eff;color:white;font-weight:bold;padding:10px 20px;border-radius:6px;")
        for b in [btn_new, btn_open, btn_del]:
            b.setFixedHeight(40)
            btn_row.addWidget(b)
        v.addLayout(btn_row)

    def _refresh(self):
        self.lst.clear()
        for r in get_db().list_tournaments():
            updated = r['updated_at'][:16].replace('T', ' ')
            item = QListWidgetItem(f"🏆  {r['name']}   |   Mùa {r['season']}   |   {updated}")
            item.setData(Qt.UserRole, r['id'])
            self.lst.addItem(item)

    def _create(self):
        dlg = _NewTournamentDialog(self)
        if dlg.exec():
            name, season = dlg.get_data()
            if name:
                t = Tournament(); t.name = name; t.season = season
                self.selected_id = get_db().save_tournament(t)
                self.accept()

    def _open(self):
        item = self.lst.currentItem()
        if not item:
            QMessageBox.information(self, "Chú ý", "Hãy chọn một giải đấu!")
            return
        self.selected_id = item.data(Qt.UserRole)
        self.accept()

    def _delete(self):
        item = self.lst.currentItem()
        if not item: return
        if QMessageBox.question(self, "Xóa", f"Xóa giải:\n{item.text()}?") == QMessageBox.Yes:
            get_db().delete_tournament(item.data(Qt.UserRole))
            self._refresh()


class MainWindow(QMainWindow):
    def __init__(self, tourn: Tournament, tid: int):
        super().__init__()
        self.tourn = tourn
        self.tid   = tid
        self._dirty = False
        self.setWindowTitle("Football Manager")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)
        self.setStyleSheet(STYLE)
        self._build()
        QTimer.singleShot(0, self._auto_save_loop)

    def _build(self):
        cw = QWidget(); self.setCentralWidget(cw)
        mv = QVBoxLayout(cw); mv.setSpacing(0); mv.setContentsMargins(0,0,0,0)

        # Top bar
        bar = QWidget()
        bar.setStyleSheet("background:#0d1117;border-bottom:2px solid #00d084;")
        bar.setFixedHeight(50)
        bh = QHBoxLayout(bar); bh.setContentsMargins(16,0,16,0)
        logo = QLabel("⚽  FOOTBALL MANAGER")
        logo.setStyleSheet("color:#00d084;font-size:17px;font-weight:bold;letter-spacing:1px;")
        bh.addWidget(logo)
        self.info_lbl = QLabel()
        self.info_lbl.setStyleSheet("color:#8a9bb0;font-size:12px;")
        bh.addWidget(self.info_lbl)
        bh.addStretch()
        self.save_lbl = QLabel("✅ Đã lưu")
        self.save_lbl.setStyleSheet("color:#00d084;font-size:11px;")
        bh.addWidget(self.save_lbl)
        bh.addSpacing(12)
        btn_switch = make_btn("📂 Đổi giải", self._switch, "secondary")
        btn_save   = QPushButton("💾 Lưu")
        btn_save.setStyleSheet("background:#00d084;color:#0d1117;font-weight:bold;padding:6px 16px;border-radius:5px;font-size:12px;")
        btn_save.clicked.connect(self._save)
        for b in [btn_switch, btn_save]: b.setFixedHeight(32); bh.addWidget(b)
        mv.addWidget(bar)

        # Tabs
        self.tabs = QTabWidget()
        self.tab_teams     = TeamsTab(self.tourn)
        self.tab_schedule  = ScheduleTab(self.tourn)
        self.tab_standings = StandingsTab(self.tourn)
        self.tab_knockout  = KnockoutTab(self.tourn)
        self.tab_stats     = StatsTab(self.tourn)
        self.tabs.addTab(self.tab_teams,     "👥  Đội / Cầu thủ")
        self.tabs.addTab(self.tab_schedule,  "📅  Lịch Vòng Bảng")
        self.tabs.addTab(self.tab_standings, "📊  Bảng xếp hạng")
        self.tabs.addTab(self.tab_knockout,  "🏆  Knockout")
        self.tabs.addTab(self.tab_stats,     "📈  Thống kê")
        self.tabs.currentChanged.connect(self._on_tab)
        mv.addWidget(self.tabs)

        for tab in [self.tab_teams, self.tab_schedule, self.tab_knockout]:
            if hasattr(tab, 'changed'):
                tab.changed.connect(self._mark_dirty)

        self._update_info()

    def _update_info(self):
        t = self.tourn
        played = sum(1 for m in t.matches if m.played)
        self.info_lbl.setText(
            f"  {t.name}  |  Mùa {t.season}  |  "
            f"{len(t.teams)} đội  |  {played}/{len(t.matches)} trận")

    def _mark_dirty(self):
        self._dirty = True
        self.save_lbl.setText("⚠ Chưa lưu")
        self.save_lbl.setStyleSheet("color:#f0a500;font-size:11px;")
        self._update_info()

    def _on_tab(self, idx):
        tab = self.tabs.widget(idx)
        if hasattr(tab, 'refresh'): tab.refresh()

    def _save(self):
        try:
            self.tid = get_db().save_tournament(self.tourn, self.tid)
            self._dirty = False
            self.save_lbl.setText("✅ Đã lưu")
            self.save_lbl.setStyleSheet("color:#00d084;font-size:11px;")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi lưu", str(e))

    def _auto_save_loop(self):
        if self._dirty: self._save()
        QTimer.singleShot(60_000, self._auto_save_loop)

    def _switch(self):
        if self._dirty:
            r = QMessageBox.question(self, "Chưa lưu", "Lưu trước khi chuyển?",
                QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel)
            if r == QMessageBox.Cancel: return
            if r == QMessageBox.Yes: self._save()
        self.close()
        launch()

    def closeEvent(self, e):
        if self._dirty:
            r = QMessageBox.question(self, "Thoát", "Lưu trước khi thoát?",
                QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel)
            if r == QMessageBox.Cancel: e.ignore(); return
            if r == QMessageBox.Yes: self._save()
        e.accept()


def launch():
    dlg = TournamentSelectorDialog()
    if dlg.exec() != QDialog.Accepted or not dlg.selected_id:
        sys.exit(0)
    tourn = get_db().load_tournament(dlg.selected_id)
    win = MainWindow(tourn, dlg.selected_id)
    win.show()
    launch._win = win   # prevent GC


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Football Manager")
    app.setStyle("Fusion")
    init_db()
    launch()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
