"""导航按钮"""
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ..theme import theme_manager


class NavButton(QPushButton):
    """侧边栏导航按钮"""

    def __init__(self, icon: str, text: str, parent=None):
        super().__init__(parent)

        self.icon_text = icon
        self.label_text = text
        self._is_active = False

        self.setText(f"{icon}\n{text}")
        self.setFixedSize(60, 60)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        font = QFont("Microsoft YaHei", 9)
        self.setFont(font)

        self._update_style()

    def set_active(self, active: bool):
        self._is_active = active
        self._update_style()

    def _update_style(self):
        p = theme_manager.current_palette

        if self._is_active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {p.primary};
                    color: {p.paper};
                    border: none;
                    border-radius: 10px;
                    padding: 8px;
                    font-weight: bold;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {p.text_secondary};
                    border: none;
                    border-radius: 10px;
                    padding: 8px;
                }}
                QPushButton:hover {{
                    background-color: {p.surface};
                    color: {p.text};
                }}
            """)