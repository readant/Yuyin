"""歌词显示组件"""
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QScrollArea
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

from ..theme import theme_manager
from ...application.services.lyrics_service import lyrics_manager


class LyricsWidget(QWidget):
    """歌词显示组件"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(0)

        # 歌词滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)

        # 歌词容器
        self.lyrics_container = QWidget()
        self.lyrics_container.setStyleSheet("background: transparent;")
        self.lyrics_layout = QVBoxLayout(self.lyrics_container)
        self.lyrics_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lyrics_layout.setSpacing(8)

        self.scroll_area.setWidget(self.lyrics_container)
        layout.addWidget(self.scroll_area)

        # 占位标签
        self.placeholder = QLabel("暂无歌词")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setStyleSheet("color: #999; font-size: 14px;")
        layout.addWidget(self.placeholder)

        self._update_display()

    def _update_display(self):
        """更新歌词显示"""
        # 清空现有歌词
        while self.lyrics_layout.count():
            item = self.lyrics_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not lyrics_manager.has_lyrics:
            self.placeholder.show()
            self.scroll_area.hide()
            return

        self.placeholder.hide()
        self.scroll_area.show()

        # 获取要显示的歌词
        display_lines = lyrics_manager.get_lyrics_for_display(center_index=5, count=11)

        for index, line, is_current in display_lines:
            label = QLabel(line.text)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setWordWrap(True)

            if is_current:
                # 当前行 - 高亮
                label.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
                label.setStyleSheet("""
                    color: #8B2500;
                    padding: 8px;
                    background: rgba(139, 37, 0, 0.1);
                    border-radius: 8px;
                """)
            else:
                # 非当前行 - 淡色
                label.setFont(QFont("Microsoft YaHei", 14))
                label.setStyleSheet("color: #666; padding: 5px;")

            self.lyrics_layout.addWidget(label)

        # 添加弹性空间
        self.lyrics_layout.addStretch()

    def update_position(self, current_time: float):
        """更新播放位置"""
        lyrics_manager.update_position(current_time)
        self._update_display()

    def clear(self):
        """清空歌词"""
        lyrics_manager.clear()
        self._update_display()

    def load_lyrics(self, file_path: str) -> bool:
        """加载歌词文件"""
        success = lyrics_manager.load_from_file(file_path)
        self._update_display()
        return success

    def set_lyrics_text(self, text: str, format: str = 'lrc'):
        """设置歌词文本"""
        lyrics_manager.load_from_text(text, format)
        self._update_display()