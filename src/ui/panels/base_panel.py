"""面板基类"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ..theme import theme_manager


class BasePanel(QWidget):
    """面板基类 - 统一样式和布局"""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.panel_title = title
        self._init_base_ui()

    def _init_base_ui(self):
        """初始化基础UI"""
        p = theme_manager.current_palette

        self.setStyleSheet(f"""
            BasePanel {{
                background-color: {p.panel_bg};
                border: 1px solid {p.border};
                border-radius: 10px;
            }}
        """)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # 标题
        title = QLabel(self.panel_title)
        title.setFont(QFont("FangSong", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {p.primary};")
        self.main_layout.addWidget(title)

        # 分隔线
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {p.border};")
        self.main_layout.addWidget(sep)

    def add_content(self, widget):
        """添加内容组件"""
        self.main_layout.addWidget(widget)

    def add_stretch(self):
        """添加弹性空间"""
        self.main_layout.addStretch()

    def create_section_frame(self) -> QFrame:
        """创建区域框架"""
        p = theme_manager.current_palette
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {p.surface};
                border: 1px solid {p.border};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        return frame

    def create_section_title(self, text: str) -> QLabel:
        """创建区域标题"""
        p = theme_manager.current_palette
        label = QLabel(text)
        label.setStyleSheet(f"color: {p.text_secondary}; font-size: 12px;")
        return label