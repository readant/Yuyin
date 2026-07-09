"""黑胶唱片组件"""
import math
from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QPainter, QColor, QRadialGradient, QPen

from ..theme import theme_manager


class VinylWidget(QWidget):
    """黑胶唱片组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(280, 280)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        self._rotation = 0
        self._is_playing = False
        self._glow_intensity = 0

        self.timer = QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self._rotate)

    def set_playing(self, playing: bool):
        self._is_playing = playing
        if playing:
            self.timer.start()
        else:
            self.timer.stop()
        self.update()

    def _rotate(self):
        self._rotation = (self._rotation + 2) % 360
        self._glow_intensity = (math.sin(self._rotation * 0.1) + 1) / 2
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        p = theme_manager.current_palette
        rect = self.rect()
        center = rect.center()
        radius = min(rect.width(), rect.height()) // 2 - 15

        # 外发光
        if self._is_playing:
            glow = QRadialGradient(QPointF(center), radius + 30)
            glow_color = QColor(p.primary)
            glow_color.setAlpha(int(40 + 20 * self._glow_intensity))
            glow.setColorAt(0.7, QColor(0, 0, 0, 0))
            glow.setColorAt(1, glow_color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(glow)
            painter.drawEllipse(center, radius + 30, radius + 30)

        painter.save()
        painter.translate(center)
        painter.rotate(self._rotation)

        # 唱片主体
        outer = QRadialGradient(0, 0, radius)
        outer.setColorAt(0, QColor(p.primary))
        outer.setColorAt(0.8, QColor(p.primary_dark))
        outer.setColorAt(1, QColor(p.ink))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(outer)
        painter.drawEllipse(QPointF(0, 0), radius, radius)

        # 纹理环
        tex_color = QColor(p.paper)
        tex_color.setAlpha(21)
        painter.setPen(QPen(tex_color, 1))
        for r in range(30, radius - 20, 6):
            painter.drawEllipse(QPointF(0, 0), r, r)

        # 沟槽
        groove_color = QColor(p.paper)
        groove_color.setAlpha(8)
        painter.setPen(QPen(groove_color, 0.5))
        for r in range(40, radius - 30, 3):
            painter.drawEllipse(QPointF(0, 0), r, r)

        # 内圈
        inner_r = radius * 0.35
        inner = QRadialGradient(0, 0, inner_r)
        inner.setColorAt(0, QColor(p.panel_bg))
        inner.setColorAt(0.7, QColor(p.surface))
        inner.setColorAt(1, QColor(p.border))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(inner)
        painter.drawEllipse(QPointF(0, 0), inner_r, inner_r)

        # 中心孔
        painter.setBrush(QColor(p.ink))
        painter.drawEllipse(QPointF(0, 0), 8, 8)

        painter.restore()

        # 文字
        text_color = QColor(p.text)
        text_color.setAlpha(144)
        painter.setPen(text_color)
        font = QFont("FangSong", 16, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "余音")

        painter.end()