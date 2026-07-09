"""歌词编辑器面板"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QTextEdit, QListWidget, QListWidgetItem,
                            QPushButton, QFileDialog, QMessageBox, QSplitter,
                            QTimeEdit, QInputDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QTime
from PyQt6.QtGui import QFont

from .base_panel import BasePanel
from ..theme import theme_manager
from ...application.services.lyrics_service import lyrics_manager, LyricLine


class LyricsEditorPanel(BasePanel):
    """歌词编辑器"""

    lyrics_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("词韵编辑", parent)
        self._init_content()

    def _init_content(self):
        p = theme_manager.current_palette

        # 工具栏
        toolbar_frame = self.create_section_frame()
        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)

        import_btn = QPushButton("导入LRC")
        import_btn.clicked.connect(self._import_lrc)
        toolbar_layout.addWidget(import_btn)

        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self._save)
        toolbar_layout.addWidget(save_btn)

        save_as_btn = QPushButton("另存为")
        save_as_btn.clicked.connect(self._save_as)
        toolbar_layout.addWidget(save_as_btn)

        toolbar_layout.addStretch()

        add_btn = QPushButton("添加行")
        add_btn.clicked.connect(self._add_line)
        toolbar_layout.addWidget(add_btn)

        delete_btn = QPushButton("删除行")
        delete_btn.clicked.connect(self._delete_line)
        toolbar_layout.addWidget(delete_btn)

        self.add_content(toolbar_frame)

        # 编辑区
        edit_frame = self.create_section_frame()
        edit_layout = QVBoxLayout(edit_frame)

        # 左侧：歌词列表
        left_panel = QVBoxLayout()
        left_label = self.create_section_title("词句列表")
        left_panel.addWidget(left_label)

        self.lyrics_list = QListWidget()
        self.lyrics_list.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: none;
            }}
            QListWidget::item {{
                padding: 8px;
                border-radius: 4px;
                margin: 2px;
            }}
            QListWidget::item:selected {{
                background-color: {p.primary}30;
            }}
        """)
        self.lyrics_list.itemDoubleClicked.connect(self._edit_line)
        left_panel.addWidget(self.lyrics_list)

        # 右侧：编辑区
        right_panel = QVBoxLayout()
        right_label = self.create_section_title("编辑区")
        right_panel.addWidget(right_label)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("输入歌词文本...")
        right_panel.addWidget(self.text_edit)

        update_btn = QPushButton("更新选中行")
        update_btn.clicked.connect(self._update_line)
        right_panel.addWidget(update_btn)

        edit_layout.addLayout(left_panel, 1)
        edit_layout.addLayout(right_panel, 1)

        self.add_content(edit_frame)

        # 底部统计
        self.stats_label = QLabel("共 0 行歌词")
        self.stats_label.setStyleSheet(f"color: {p.text_secondary};")
        self.add_content(self.stats_label)

    def _import_lrc(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入LRC文件", "",
            "LRC文件 (*.lrc);;所有文件 (*.*)"
        )
        if file_path:
            if lyrics_manager.load_from_file(file_path):
                self._refresh_list()
                self.stats_label.setText(f"共 {lyrics_manager.count} 行歌词")
            else:
                QMessageBox.warning(self, "警告", "无法加载歌词文件")

    def _save(self):
        if lyrics_manager.file_path:
            if lyrics_manager.save():
                QMessageBox.information(self, "成功", "歌词已保存")
        else:
            self._save_as()

    def _save_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存歌词", "",
            "LRC文件 (*.lrc)"
        )
        if file_path:
            if lyrics_manager.save_to_file(file_path):
                QMessageBox.information(self, "成功", "歌词已保存")

    def _add_line(self):
        time, ok = QInputDialog.getDouble(
            self, "添加歌词行", "时间（秒）:", 0.0, 0, 600, 2
        )
        if ok:
            text, ok = QInputDialog.getText(self, "添加歌词行", "歌词文本:")
            if ok and text:
                lyrics_manager.add_line(time, text)
                self._refresh_list()
                self.lyrics_changed.emit()

    def _delete_line(self):
        current_row = self.lyrics_list.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(
                self, "确认删除", "确定要删除这行歌词吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                lyrics_manager.remove_line(current_row)
                self._refresh_list()
                self.lyrics_changed.emit()

    def _update_line(self):
        current_row = self.lyrics_list.currentRow()
        if current_row >= 0:
            text = self.text_edit.toPlainText()
            if text:
                lyrics_manager.update_line(current_row, text=text)
                self._refresh_list()
                self.lyrics_changed.emit()

    def _edit_line(self, item: QListWidgetItem):
        index = item.data(Qt.ItemDataRole.UserRole)
        if index is not None and 0 <= index < len(lyrics_manager.lyrics):
            line = lyrics_manager.lyrics[index]
            self.text_edit.setText(line.text)

    def _refresh_list(self):
        self.lyrics_list.clear()
        for i, line in enumerate(lyrics_manager.lyrics):
            item = QListWidgetItem(f"[{self._format_time(line.time)}] {line.text}")
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.lyrics_list.addItem(item)
        self.stats_label.setText(f"共 {lyrics_manager.count} 行歌词")

    def _format_time(self, seconds: float) -> str:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{minutes:02d}:{secs:02d}.{ms:03d}"