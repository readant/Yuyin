"""指法图示组件"""
from typing import List
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QRadialGradient

from ..theme import theme_manager


class FingeringWidget(QWidget):
    """指法孔位图"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.fingering: List[int] = [0, 0, 0, 0, 0, 0]
        self.setMinimumSize(60, 180)
        self.setMaximumWidth(80)

    def set_fingering(self, fingering: List[int]):
        self.fingering = fingering
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        p = theme_manager.current_palette
        rect = self.rect()

        # 笛身
        body_x = rect.width() // 2 - 15
        body_width = 30
        body_height = rect.height() - 20

        gradient = QRadialGradient(rect.width() // 2, rect.height() // 2,
                                   max(body_width, body_height) // 2)
        sec_color = QColor(p.secondary)
        gradient.setColorAt(0, sec_color)
        sec_color.setAlpha(204)
        gradient.setColorAt(0.7, sec_color)
        sec_color.setAlpha(68)
        gradient.setColorAt(1, sec_color)

        painter.setPen(QPen(QColor(p.secondary), 1))
        painter.setBrush(gradient)
        painter.drawRoundedRect(body_x, 10, body_width, body_height, 15, 15)

        # 孔位
        hole_spacing = 28
        hole_radius = 10
        center_x = rect.width() // 2

        for i, pressed in enumerate(self.fingering):
            y = 30 + i * hole_spacing

            if pressed:
                grad = QRadialGradient(center_x, y + hole_radius, hole_radius)
                grad.setColorAt(0, QColor(p.ink))
                ink_alpha = QColor(p.ink)
                ink_alpha.setAlpha(204)
                grad.setColorAt(0.8, ink_alpha)
                ink_light = QColor(p.ink)
                ink_light.setAlpha(136)
                grad.setColorAt(1, ink_light)
                painter.setPen(QPen(QColor(p.ink), 1))
            else:
                grad = QRadialGradient(center_x, y + hole_radius, hole_radius)
                grad.setColorAt(0, QColor(p.paper))
                grad.setColorAt(0.8, QColor(p.border_light))
                grad.setColorAt(1, QColor(p.border))
                painter.setPen(QPen(QColor(p.secondary), 2))

            painter.setBrush(grad)
            painter.drawEllipse(center_x - hole_radius, y, hole_radius * 2, hole_radius * 2)

        painter.end()


class FingeringDisplay(QWidget):
    """指法文本显示"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.fingering: List[int] = [0, 0, 0, 0, 0, 0]
        self.setFixedHeight(30)

    def set_fingering(self, fingering: List[int]):
        self.fingering = fingering
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        p = theme_manager.current_palette

        painter.fillRect(self.rect(), QColor(p.panel_bg))

        painter.setPen(QColor(p.text))
        painter.setFont(painter.font())

        text = "".join(["●" if f else "○" for f in self.fingering])
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, text)

        painter.end()