"""频谱可视化组件"""
import math
import random
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRect
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient

from ..theme import theme_manager


class SpectrumWidget(QWidget):
    """水墨风格频谱可视化"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumHeight(80)
        self.setMaximumHeight(100)

        self.bars = [0.0] * 32
        self.target_bars = [0.0] * 32
        self.phase = 0.0

        # 固定的水墨点
        self._ink_spots = [(random.randint(0, 300), random.randint(0, 150),
                           random.randint(30, 80)) for _ in range(5)]

        self.animation_timer = QTimer()
        self.animation_timer.setInterval(30)
        self.animation_timer.timeout.connect(self._animate)
        self.animation_timer.start()

    def set_bars(self, bars: list):
        self.target_bars = bars[:32] if len(bars) >= 32 else bars + [0.0] * (32 - len(bars))

    def set_playing(self, is_playing: bool):
        if is_playing:
            self.animation_timer.start()
        else:
            self.animation_timer.stop()
            self.bars = [0.0] * 32
            self.update()

    def _animate(self):
        self.phase += 0.15

        for i in range(len(self.bars)):
            diff = self.target_bars[i] - self.bars[i]
            self.bars[i] += diff * 0.3
            if self.bars[i] > 0:
                wave = math.sin(self.phase + i * 0.3) * 3
                self.bars[i] = max(0, self.bars[i] + wave)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        p = theme_manager.current_palette
        rect = self.rect()

        # 背景
        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, QColor(p.panel_bg))
        gradient.setColorAt(0.5, QColor(p.surface))
        gradient.setColorAt(1, QColor(p.panel_bg))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawRect(rect)

        # 水墨点
        painter.setBrush(QColor(p.ink + "08"))
        for x, y, size in self._ink_spots:
            painter.drawEllipse(x - size // 2, y - size // 2, size, size)

        # 频谱柱
        bar_count = len(self.bars)
        bar_width = max(4, (rect.width() - 40) / bar_count - 2)
        spacing = 2
        start_x = 20
        max_height = rect.height() - 40

        for i, value in enumerate(self.bars):
            if value > 1:
                bar_height = max(2, min(value * 1.5, max_height))
                x = start_x + i * (bar_width + spacing)
                y = rect.height() - 20 - bar_height

                grad = QLinearGradient(x, y + bar_height, x, y)
                ratio = min(1.0, bar_height / max_height)

                if ratio < 0.3:
                    color = QColor(p.spectrum_1 + "CC")
                elif ratio < 0.7:
                    color = QColor(p.spectrum_2 + "CC")
                else:
                    color = QColor(p.spectrum_3 + "CC")

                grad.setColorAt(0, color)
                grad.setColorAt(1, QColor(p.spectrum_1 + "44"))

                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(grad))
                painter.drawRoundedRect(int(x), int(y), int(bar_width), int(bar_height), 2, 2)

                painter.setBrush(QBrush(QColor(p.paper + "40")))
                painter.drawEllipse(int(x + bar_width / 2 - 2), int(y), 4, 4)

        painter.end()