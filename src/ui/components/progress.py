"""进度条组件"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient

from ..theme import theme_manager


class ProgressWidget(QWidget):
    """精美进度条"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self._value = 0
        self._max_value = 100

    def set_value(self, value: int):
        self._value = value
        self.update()

    def set_range(self, max_val: int):
        self._max_value = max_val

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        p = theme_manager.current_palette
        rect = self.rect()
        y = rect.height() // 2
        margin = 20
        width = rect.width() - margin * 2

        # 轨道
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(p.border + "60"))
        painter.drawRoundedRect(margin, y - 3, width, 6, 3, 3)

        # 进度
        if self._max_value > 0:
            progress_width = int(width * self._value / self._max_value)
            if progress_width > 0:
                gradient = QLinearGradient(margin, 0, margin + progress_width, 0)
                gradient.setColorAt(0, QColor(p.primary))
                gradient.setColorAt(1, QColor(p.accent))
                painter.setBrush(QBrush(gradient))
                painter.drawRoundedRect(margin, y - 3, progress_width, 6, 3, 3)

                # 圆点
                painter.setBrush(QColor(p.primary))
                painter.drawEllipse(QPointF(margin + progress_width, y), 6, 6)
                painter.setBrush(QColor(p.paper))
                painter.drawEllipse(QPointF(margin + progress_width, y), 3, 3)

        painter.end()

    def mousePressEvent(self, event):
        if self._max_value > 0:
            x = event.position().x() - 20
            width = self.width() - 40
            value = int(x / width * self._max_value)
            value = max(0, min(value, self._max_value))
            if hasattr(self.parent(), '_seek'):
                self.parent()._seek(value)