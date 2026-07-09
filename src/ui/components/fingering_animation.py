"""指法动画组件"""
import math
from typing import List, Optional
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QRadialGradient, QFont, QBrush

from ..theme import theme_manager


class FingeringAnimationWidget(QWidget):
    """指法动画组件 - 带过渡动画的指法图"""

    fingering_changed = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._current_fingering: List[int] = [0, 0, 0, 0, 0, 0]
        self._target_fingering: List[int] = [0, 0, 0, 0, 0, 0]
        self._animated_fingering: List[float] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        self._animation_timer = QTimer()
        self._animation_timer.setInterval(30)  # ~33fps
        self._animation_timer.timeout.connect(self._animate)
        self._animation_timer.start()

        self._animation_speed = 0.15
        self._isAnimating = False

        self.setMinimumSize(80, 240)
        self.setMaximumWidth(100)

    def set_fingering(self, fingering: List[int], animate: bool = True):
        """设置指法"""
        self._target_fingering = fingering.copy()

        if animate:
            self._isAnimating = True
        else:
            self._current_fingering = fingering.copy()
            self._animated_fingering = [float(f) for f in fingering]
            self.update()

    def _animate(self):
        """动画更新"""
        if not self._isAnimating:
            return

        all_reached = True
        for i in range(len(self._animated_fingering)):
            target = float(self._target_fingering[i])
            current = self._animated_fingering[i]

            diff = target - current
            if abs(diff) > 0.01:
                self._animated_fingering[i] += diff * self._animation_speed
                all_reached = False
            else:
                self._animated_fingering[i] = target

        if all_reached:
            self._isAnimating = False
            self._current_fingering = self._target_fingering.copy()
            self.fingering_changed.emit(self._current_fingering)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        p = theme_manager.current_palette
        rect = self.rect()

        # 笛身
        body_x = rect.width() // 2 - 18
        body_width = 36
        body_height = rect.height() - 20

        # 笛身渐变
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
        painter.drawRoundedRect(body_x, 10, body_width, body_height, 18, 18)

        # 笛身纹理
        painter.setPen(QPen(QColor(p.paper + "15"), 0.5))
        for y in range(30, rect.height() - 20, 12):
            painter.drawLine(body_x + 5, y, body_x + body_width - 5, y)

        # 孔位
        hole_spacing = 32
        hole_radius = 12
        center_x = rect.width() // 2

        for i in range(6):
            y = 35 + i * hole_spacing
            animated_value = self._animated_fingering[i]

            # 计算孔位状态（0-1之间的连续值）
            # 0 = 完全打开，1 = 完全关闭
            hole_openness = 1.0 - animated_value

            # 绘制孔位
            self._draw_hole(painter, center_x, y, hole_radius, hole_openness, p)

            # 绘制手指指示
            if animated_value > 0.5:
                self._draw_finger(painter, center_x, y, hole_radius, animated_value, p)

        # 绘制当前指法文本
        self._draw_fingering_text(painter, rect, p)

        painter.end()

    def _draw_hole(self, painter: QPainter, x: int, y: int, radius: int,
                   openness: float, palette):
        """绘制孔位"""
        # 孔位背景
        gradient = QRadialGradient(x, y + radius, radius)
        gradient.setColorAt(0, QColor(palette.paper))
        gradient.setColorAt(0.8, QColor(palette.border_light))
        gradient.setColorAt(1, QColor(palette.border))

        painter.setPen(QPen(QColor(palette.secondary), 2))
        painter.setBrush(gradient)
        painter.drawEllipse(x - radius, y, radius * 2, radius * 2)

        # 孔位内部（根据开放程度）
        if openness > 0:
            inner_radius = int(radius * openness * 0.8)
            if inner_radius > 0:
                inner_gradient = QRadialGradient(x, y + radius, inner_radius)
                inner_gradient.setColorAt(0, QColor(palette.panel_bg))
                inner_gradient.setColorAt(1, QColor(palette.border + "80"))

                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(inner_gradient)
                painter.drawEllipse(x - inner_radius, y + radius - inner_radius,
                                  inner_radius * 2, inner_radius * 2)

    def _draw_finger(self, painter: QPainter, x: int, y: int, radius: int,
                     pressed: float, palette):
        """绘制手指"""
        # 手指大小根据按压力度变化
        finger_radius = int(radius * 0.6 * pressed)

        if finger_radius > 0:
            # 手指渐变
            gradient = QRadialGradient(x, y + radius, finger_radius)
            gradient.setColorAt(0, QColor(palette.primary))
            gradient.setColorAt(0.7, QColor(palette.primary_dark))
            gradient.setColorAt(1, QColor(palette.primary_dark + "80"))

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(gradient)
            painter.drawEllipse(x - finger_radius, y + radius - finger_radius,
                              finger_radius * 2, finger_radius * 2)

            # 手指高光
            painter.setBrush(QColor(palette.paper + "60"))
            painter.drawEllipse(x - finger_radius // 3, y + radius - finger_radius,
                              finger_radius // 2, finger_radius // 2)

    def _draw_fingering_text(self, painter: QPainter, rect, palette):
        """绘制指法文本"""
        painter.setPen(QColor(palette.text))
        font = QFont("Consolas", 12, QFont.Weight.Bold)
        painter.setFont(font)

        text = "".join(["●" if f > 0.5 else "○" for f in self._animated_fingering])
        painter.drawText(rect.adjusted(0, rect.height() - 25, 0, 0),
                        Qt.AlignmentFlag.AlignCenter, text)


class FingeringSequenceWidget(QWidget):
    """指法序列动画组件 - 播放时显示多个指法"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self._sequence: List[List[int]] = []
        self._current_index: int = -1
        self._animation_phase: float = 0

        self._animation_timer = QTimer()
        self._animation_timer.setInterval(30)
        self._animation_timer.timeout.connect(self._animate)
        self._animation_timer.start()

        self.setMinimumHeight(120)
        self.setMaximumHeight(150)

    def set_sequence(self, sequence: List[List[int]]):
        """设置指法序列"""
        self._sequence = sequence
        self._current_index = -1
        self.update()

    def set_current_index(self, index: int):
        """设置当前索引"""
        if index != self._current_index:
            self._current_index = index
            self._animation_phase = 0
            self.update()

    def _animate(self):
        """动画更新"""
        self._animation_phase += 0.1
        self.update()

    def paintEvent(self, event):
        if not self._sequence:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        p = theme_manager.current_palette
        rect = self.rect()

        # 绘制标题
        painter.setPen(QColor(p.text))
        painter.setFont(QFont("FangSong", 12, QFont.Weight.Bold))
        painter.drawText(rect.adjusted(0, 5, 0, 0), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter,
                        "指法序列")

        # 绘制指法序列
        y = 35
        hole_spacing = 14
        hole_radius = 5

        for i, fingering in enumerate(self._sequence):
            if i >= 5:  # 最多显示5个
                break

            # 判断是否是当前指法
            is_current = (i == self._current_index)
            x_offset = 30

            # 绘制指法编号
            painter.setPen(QColor(p.primary if is_current else p.text_secondary))
            painter.setFont(QFont("Consolas", 10))
            painter.drawText(10, y + 10, str(i + 1))

            # 绘制孔位
            for j, pressed in enumerate(fingering):
                hole_y = y + j * hole_spacing

                if is_current:
                    # 当前指法 - 高亮
                    pulse = 1.0 + 0.2 * math.sin(self._animation_phase * 3)
                    radius = int(hole_radius * pulse)

                    if pressed:
                        painter.setBrush(QColor(p.primary))
                        painter.setPen(QPen(QColor(p.primary), 2))
                    else:
                        painter.setBrush(QColor(p.paper))
                        painter.setPen(QPen(QColor(p.border), 1))
                else:
                    # 非当前指法
                    radius = hole_radius
                    if pressed:
                        painter.setBrush(QColor(p.secondary + "80"))
                        painter.setPen(QPen(QColor(p.secondary), 1))
                    else:
                        painter.setBrush(QColor(p.paper + "80"))
                        painter.setPen(QPen(QColor(p.border + "80"), 1))

                painter.drawEllipse(x_offset - radius, hole_y, radius * 2, radius * 2)

            # 绘制指法文本
            text = "".join(["●" if f else "○" for f in fingering])
            painter.setPen(QColor(p.primary if is_current else p.text_secondary))
            painter.setFont(QFont("Consolas", 8))
            painter.drawText(x_offset + 25, y + 10, text)

            y += hole_spacing * 6 + 15

        painter.end()