"""拟物化国风控件"""
import math
from PyQt6.QtWidgets import QWidget, QPushButton, QSlider
from PyQt6.QtCore import Qt, pyqtSignal, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QRadialGradient

from ..theme import theme_manager


class QingButton(QPushButton):
    """磬形播放按钮"""

    def __init__(self, text: str = "▶", parent=None):
        super().__init__(text, parent)
        self.setFixedSize(80, 80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._is_playing = False

        # 设置样式
        self._update_style()

    def set_playing(self, playing: bool):
        self._is_playing = playing
        self._update_style()

    def _update_style(self):
        p = theme_manager.current_palette

        if self._is_playing:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {p.primary};
                    color: {p.paper};
                    border: none;
                    border-radius: 40px;
                    font-size: 24px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {p.primary_light};
                }}
                QPushButton:pressed {{
                    background-color: {p.primary_dark};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {p.secondary};
                    color: {p.paper};
                    border: none;
                    border-radius: 40px;
                    font-size: 24px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {p.secondary}CC;
                }}
                QPushButton:pressed {{
                    background-color: {p.secondary}88;
                }}
            """)


class ScrollProgressBar(QWidget):
    """卷轴进度条"""

    value_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        self._value = 0
        self._max_value = 100
        self._is_dragging = False

    def set_value(self, value: int):
        self._value = max(0, min(value, self._max_value))
        self.update()

    def set_range(self, max_val: int):
        self._max_value = max_val
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        p = theme_manager.current_palette
        rect = self.rect()
        y = rect.height() // 2
        margin = 30
        width = rect.width() - margin * 2

        # 卷轴杆 - 左端
        self._draw_scroll_end(painter, margin - 15, y, p)

        # 卷轴杆 - 右端
        self._draw_scroll_end(painter, rect.width() - margin + 15, y, p)

        # 卷轴纸面
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(p.paper))
        painter.drawRoundedRect(margin, y - 8, width, 16, 3, 3)

        # 卷轴纹理
        painter.setPen(QPen(QColor(p.border + "40"), 0.5))
        for i in range(0, width, 12):
            x = margin + i
            painter.drawLine(x, y - 6, x, y + 6)

        # 进度填充
        if self._max_value > 0:
            progress_width = int(width * self._value / self._max_value)
            if progress_width > 0:
                gradient = QLinearGradient(margin, 0, margin + progress_width, 0)
                gradient.setColorAt(0, QColor(p.primary + "80"))
                gradient.setColorAt(1, QColor(p.primary))
                painter.setBrush(QBrush(gradient))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(margin, y - 6, progress_width, 12, 2, 2)

        # 进度指示器 - 小卷轴头
        if self._max_value > 0:
            indicator_x = margin + progress_width
            self._draw_scroll_indicator(painter, indicator_x, y, p)

        painter.end()

    def _draw_scroll_end(self, painter, x, y, palette):
        """绘制卷轴端头"""
        # 木质卷轴杆
        gradient = QLinearGradient(x - 8, y - 12, x + 8, y + 12)
        gradient.setColorAt(0, QColor("#8B7355"))
        gradient.setColorAt(0.3, QColor("#A08060"))
        gradient.setColorAt(0.5, QColor("#B8956A"))
        gradient.setColorAt(0.7, QColor("#A08060"))
        gradient.setColorAt(1, QColor("#6B5340"))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(x - 8, y - 12, 16, 24)

        # 端头装饰
        painter.setBrush(QColor("#C5A55A"))
        painter.drawEllipse(x - 4, y - 6, 8, 12)

    def _draw_scroll_indicator(self, painter, x, y, palette):
        """绘制进度指示器"""
        gradient = QRadialGradient(x, y, 10)
        gradient.setColorAt(0, QColor(palette.primary))
        gradient.setColorAt(1, QColor(palette.primary_dark))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(x - 8, y - 8, 16, 16)

        # 高光
        painter.setBrush(QColor(palette.paper + "60"))
        painter.drawEllipse(x - 3, y - 5, 4, 4)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._update_value_from_pos(event.position().x())

    def mouseMoveEvent(self, event):
        if self._is_dragging:
            self._update_value_from_pos(event.position().x())

    def mouseReleaseEvent(self, event):
        self._is_dragging = False

    def _update_value_from_pos(self, x: float):
        """根据鼠标位置更新值"""
        margin = 30
        width = self.width() - margin * 2
        if width > 0:
            value = int((x - margin) / width * self._max_value)
            value = max(0, min(value, self._max_value))
            self._value = value
            self.value_changed.emit(value)
            self.update()


class PluckVolumeSlider(QWidget):
    """拨弦音量滑块"""

    value_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(150, 40)
        self._value = 80
        self._max_value = 100
        self._is_dragging = False
        self._string_tension = 0

    def set_value(self, value: int):
        self._value = max(0, min(value, self._max_value))
        self._string_tension = self._value / self._max_value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        p = theme_manager.current_palette
        rect = self.rect()
        y = rect.height() // 2
        margin = 20
        width = rect.width() - margin * 2

        # 琴弦支架 - 左
        self._draw_peg(painter, margin - 10, y, p)

        # 琴弦支架 - 右
        self._draw_peg(painter, rect.width() - margin + 10, y, p)

        # 琴弦
        string_y = y
        tension = self._string_tension

        # 琴弦弯曲效果
        painter.setPen(QPen(QColor(p.secondary), 2))
        path_points = []
        for i in range(width + 1):
            x = margin + i
            # 根据音量值调整弯曲度
            bend = math.sin(i / width * math.pi) * tension * 5
            path_points.append(QPointF(x, string_y + bend))

        for i in range(len(path_points) - 1):
            painter.drawLine(path_points[i], path_points[i + 1])

        # 拨片指示器
        indicator_x = margin + int(width * self._value / self._max_value)
        self._draw_pick(painter, indicator_x, string_y, p)

        # 音量刻度
        painter.setPen(QColor(p.text_secondary))
        font = painter.font()
        font.setPixelSize(8)
        painter.setFont(font)

        for i in range(0, 101, 25):
            x = margin + int(width * i / 100)
            painter.drawText(x - 5, y + 18, str(i))

        painter.end()

    def _draw_peg(self, painter, x, y, palette):
        """绘制琴弦支架"""
        # 琴码
        gradient = QLinearGradient(x - 5, y - 10, x + 5, y + 10)
        gradient.setColorAt(0, QColor("#8B7355"))
        gradient.setColorAt(0.5, QColor("#A08060"))
        gradient.setColorAt(1, QColor("#6B5340"))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawRoundedRect(x - 5, y - 10, 10, 20, 2, 2)

    def _draw_pick(self, painter, x, y, palette):
        """绘制拨片"""
        gradient = QRadialGradient(x, y, 8)
        gradient.setColorAt(0, QColor(palette.primary))
        gradient.setColorAt(1, QColor(palette.primary_dark))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(x - 8, y - 8, 16, 16)

        # 拨片高光
        painter.setBrush(QColor(palette.paper + "40"))
        painter.drawEllipse(x - 3, y - 4, 4, 4)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._update_value_from_pos(event.position().x())

    def mouseMoveEvent(self, event):
        if self._is_dragging:
            self._update_value_from_pos(event.position().x())

    def mouseReleaseEvent(self, event):
        self._is_dragging = False

    def _update_value_from_pos(self, x: float):
        """根据鼠标位置更新值"""
        margin = 20
        width = self.width() - margin * 2
        if width > 0:
            value = int((x - margin) / width * self._max_value)
            value = max(0, min(value, self._max_value))
            self._value = value
            self._string_tension = value / self._max_value
            self.value_changed.emit(value)
            self.update()