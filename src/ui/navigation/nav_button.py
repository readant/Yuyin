"""导航按钮"""
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor

from ..theme import theme_manager


class NavButton(QPushButton):
    """侧边栏导航按钮"""

    def __init__(self, text: str, icon: str = "", parent=None):
        super().__init__(parent)

        self.nav_text = text
        self.nav_icon = icon
        self._is_active = False

        self.setText(text)
        self.setFixedHeight(36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        font = QFont("Microsoft YaHei", 11)
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
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-weight: bold;
                    text-align: left;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {p.text};
                    border: none;
                    border-radius: 6px;
                    padding: 8px 12px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background-color: {p.primary}15;
                    color: {p.primary};
                }}
            """)