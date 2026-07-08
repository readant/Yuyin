"""歌词编辑器面板"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QTextEdit, QListWidget, QListWidgetItem,
                            QPushButton, QFileDialog, QMessageBox, QSplitter,
                            QTimeEdit, QInputDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QTime
from PyQt6.QtGui import QFont

from ..theme import theme_manager
from ...application.services.lyrics_service import lyrics_manager, LyricLine


class LyricsEditorPanel(QWidget):
    """歌词编辑器"""

    lyrics_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        p = theme_manager.current_palette

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 标题
        header = QHBoxLayout()

        title = QLabel("歌词编辑器")
        title.setFont(QFont("FangSong", 18, QFont.Weight.Bold))
        header.addWidget(title)

        header.addStretch()

        # 文件信息
        self.file_label = QLabel("未加载")
        self.file_label.setStyleSheet(f"color: {p.text_secondary};")
        header.addWidget(self.file_label)

        layout.addLayout(header)

        # 工具栏
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        import_btn = QPushButton("📂 导入LRC")
        import_btn.clicked.connect(self._import_lrc)
        toolbar.addWidget(import_btn)

        save_btn = QPushButton("💾 保存")
        save_btn.clicked.connect(self._save)
        toolbar.addWidget(save_btn)

        save_as_btn = QPushButton("📄 另存为")
        save_as_btn.clicked.connect(self._save_as)
        toolbar.addWidget(save_as_btn)

        toolbar.addStretch()

        add_btn = QPushButton("➕ 添加行")
        add_btn.clicked.connect(self._add_line)
        toolbar.addWidget(add_btn)

        delete_btn = QPushButton("🗑️ 删除行")
        delete_btn.clicked.connect(self._delete_line)
        toolbar.addWidget(delete_btn)

        toolbar.addStretch()

        # 搜索
        self.search_input = QTextEdit()
        self.search_input.setPlaceholderText("搜索歌词...")
        self.search_input.setMaximumHeight(30)
        self.search_input.setMaximumWidth(150)
        toolbar.addWidget(self.search_input)

        search_btn = QPushButton("🔍 搜索")
        search_btn.clicked.connect(self._search)
        toolbar.addWidget(search_btn)

        layout.addLayout(toolbar)

        # 主内容区
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧：歌词列表
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        left_label = QLabel("歌词列表")
        left_label.setStyleSheet(f"color: {p.primary}; font-weight: bold;")
        left_layout.addWidget(left_label)

        self.lyrics_list = QListWidget()
        self.lyrics_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {p.panel_bg};
                border: 1px solid {p.border};
                border-radius: 8px;
                padding: 5px;
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
        left_layout.addWidget(self.lyrics_list)

        splitter.addWidget(left_panel)

        # 右侧：编辑区
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        right_label = QLabel("编辑区")
        right_label.setStyleSheet(f"color: {p.primary}; font-weight: bold;")
        right_layout.addWidget(right_label)

        # 时间编辑
        time_layout = QHBoxLayout()
        time_layout.setSpacing(10)

        time_label = QLabel("时间:")
        time_layout.addWidget(time_label)

        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("mm:ss.zzz")
        self.time_edit.setStyleSheet(f"""
            QTimeEdit {{
                background-color: {p.input_bg};
                color: {p.text};
                border: 1px solid {p.input_border};
                border-radius: 6px;
                padding: 8px;
            }}
        """)
        time_layout.addWidget(self.time_edit)

        set_time_btn = QPushButton("设置当前时间")
        set_time_btn.clicked.connect(self._set_current_time)
        time_layout.addWidget(set_time_btn)

        time_layout.addStretch()
        right_layout.addLayout(time_layout)

        # 文本编辑
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("输入歌词文本...")
        self.text_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {p.input_bg};
                color: {p.text};
                border: 1px solid {p.input_border};
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
            }}
        """)
        right_layout.addWidget(self.text_edit)

        # 编辑按钮
        edit_btn_layout = QHBoxLayout()
        edit_btn_layout.setSpacing(10)

        update_btn = QPushButton("✅ 更新选中行")
        update_btn.clicked.connect(self._update_line)
        edit_btn_layout.addWidget(update_btn)

        preview_btn = QPushButton("👁️ 预览LRC")
        preview_btn.clicked.connect(self._preview_lrc)
        edit_btn_layout.addWidget(preview_btn)

        edit_btn_layout.addStretch()
        right_layout.addLayout(edit_btn_layout)

        splitter.addWidget(right_panel)

        # 设置分割比例
        splitter.setSizes([400, 400])

        layout.addWidget(splitter, 1)

        # 底部统计
        stats_layout = QHBoxLayout()

        self.stats_label = QLabel("共 0 行歌词")
        self.stats_label.setStyleSheet(f"color: {p.text_secondary};")
        stats_layout.addWidget(self.stats_label)

        stats_layout.addStretch()

        layout.addLayout(stats_layout)

    def _import_lrc(self):
        """导入LRC文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入LRC文件", "",
            "LRC文件 (*.lrc);;所有文件 (*.*)"
        )

        if file_path:
            if lyrics_manager.load_from_file(file_path):
                self._refresh_list()
                self.file_label.setText(os.path.basename(file_path))
                self.stats_label.setText(f"共 {lyrics_manager.count} 行歌词")
            else:
                QMessageBox.warning(self, "警告", "无法加载歌词文件")

    def _save(self):
        """保存歌词"""
        if lyrics_manager.file_path:
            if lyrics_manager.save():
                QMessageBox.information(self, "成功", "歌词已保存")
            else:
                QMessageBox.warning(self, "警告", "保存失败")
        else:
            self._save_as()

    def _save_as(self):
        """另存为"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存歌词", "",
            "LRC文件 (*.lrc)"
        )

        if file_path:
            if lyrics_manager.save_to_file(file_path):
                self.file_label.setText(os.path.basename(file_path))
                QMessageBox.information(self, "成功", "歌词已保存")
            else:
                QMessageBox.warning(self, "警告", "保存失败")

    def _add_line(self):
        """添加歌词行"""
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
        """删除歌词行"""
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
        """更新歌词行"""
        current_row = self.lyrics_list.currentRow()
        if current_row >= 0:
            time = self.time_edit.time().secsTo(QTime(0, 0, 0)) * -1
            text = self.text_edit.toPlainText()
            if text:
                lyrics_manager.update_line(current_row, time=time, text=text)
                self._refresh_list()
                self.lyrics_changed.emit()

    def _set_current_time(self):
        """设置当前时间"""
        # TODO: 从播放器获取当前时间
        pass

    def _search(self):
        """搜索歌词"""
        keyword = self.search_input.toPlainText()
        if keyword:
            results = lyrics_manager.search(keyword)
            self.lyrics_list.clear()
            for index, line in results:
                item = QListWidgetItem(f"[{self._format_time(line.time)}] {line.text}")
                item.setData(Qt.ItemDataRole.UserRole, index)
                self.lyrics_list.addItem(item)

    def _preview_lrc(self):
        """预览LRC格式"""
        text = lyrics_manager.get_all_as_text()
        QMessageBox.information(self, "LRC预览", text[:2000] if len(text) > 2000 else text)

    def _edit_line(self, item: QListWidgetItem):
        """编辑歌词行"""
        index = item.data(Qt.ItemDataRole.UserRole)
        if index is not None and 0 <= index < len(lyrics_manager.lyrics):
            line = lyrics_manager.lyrics[index]
            self.time_edit.setTime(QTime.fromMSecsSinceStartOfDay(int(line.time * 1000)))
            self.text_edit.setText(line.text)

    def _refresh_list(self):
        """刷新歌词列表"""
        self.lyrics_list.clear()
        for i, line in enumerate(lyrics_manager.lyrics):
            item = QListWidgetItem(f"[{self._format_time(line.time)}] {line.text}")
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.lyrics_list.addItem(item)
        self.stats_label.setText(f"共 {lyrics_manager.count} 行歌词")

    def _format_time(self, seconds: float) -> str:
        """格式化时间"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{minutes:02d}:{secs:02d}.{ms:03d}"

    def load_lyrics(self, file_path: str):
        """加载歌词文件"""
        if lyrics_manager.load_from_file(file_path):
            self._refresh_list()
            self.file_label.setText(os.path.basename(file_path))


import os