"""简谱同步显示组件"""
from typing import List, Tuple, Optional
from PyQt6.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QLinearGradient

from ..theme import theme_manager


class NoteUnit:
    """音符单元"""

    def __init__(self, value: str, start_time: float, duration: float, index: int):
        self.value = value
        self.start_time = start_time
        self.duration = duration
        self.index = index
        self.is_bar = value == '|'
        self.is_space = value == ' '
        self.fingering = None

    @property
    def end_time(self) -> float:
        return self.start_time + self.duration

    @property
    def display_value(self) -> str:
        """显示值（清理括号）"""
        return self.value.replace('(', '').replace(')', '').replace('[', '').replace(']', '')


class ScoreDisplayWidget(QWidget):
    """简谱同步显示组件"""

    note_clicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.notes: List[NoteUnit] = []
        self.current_index: int = -1
        self.selected_indices: set = set()
        self.fingering_map: dict = {}

        self.setMinimumHeight(200)
        self.setMinimumWidth(400)

    def set_notes(self, notes: List[NoteUnit], fingering_map: dict = None):
        """设置音符数据"""
        self.notes = notes
        self.fingering_map = fingering_map or {}
        self.update()

    def set_current_index(self, index: int):
        """设置当前播放位置"""
        if index != self.current_index:
            self.current_index = index
            self.update()
            self._ensure_visible(index)

    def set_selected(self, indices: set):
        """设置选中的音符"""
        self.selected_indices = indices
        self.update()

    def _ensure_visible(self, index: int):
        """确保当前音符可见"""
        if index < 0 or index >= len(self.notes):
            return

        # 计算音符位置
        note_width = 55
        x = 15 + index * note_width
        y = 50

        # 检查是否需要滚动
        if x > self.width() - 50:
            self.scroll(x - self.width() + 100, 0)
        elif x < 50:
            self.scroll(max(0, x - 50), 0)

    def paintEvent(self, event):
        if not self.notes:
            self._draw_empty_state(painter)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        p = theme_manager.current_palette
        rect = self.rect()

        # 绘制背景
        painter.fillRect(rect, QColor(p.panel_bg))

        # 绘制标题
        painter.setPen(QColor(p.text))
        painter.setFont(QFont("FangSong", 14, QFont.Weight.Bold))
        painter.drawText(15, 25, "简谱预览")

        # 绘制音符
        self._draw_notes(painter, rect, p)

        painter.end()

    def _draw_empty_state(self, painter: QPainter):
        """绘制空状态"""
        p = theme_manager.current_palette
        painter.fillRect(self.rect(), QColor(p.panel_bg))

        painter.setPen(QColor(p.text_secondary))
        painter.setFont(QFont("Microsoft YaHei", 14))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "暂无简谱\n请输入简谱或导入文件")

    def _draw_notes(self, painter: QPainter, rect, palette):
        """绘制音符"""
        x = 15
        y = 60
        note_width = 55
        line_height = 110

        for i, note in enumerate(self.notes):
            # 检查是否需要换行
            if x + note_width > rect.width() - 15:
                x = 15
                y += line_height

            note_rect = QRect(x, y - 30, note_width, line_height)

            # 绘制高亮背景
            if i == self.current_index:
                # 当前播放位置 - 主色调高亮
                painter.setBrush(QColor(palette.primary + "30"))
                painter.setPen(QPen(QColor(palette.primary), 2))
                painter.drawRoundedRect(note_rect, 6, 6)

                # 绘制发光效果
                painter.setBrush(QColor(palette.primary + "15"))
                painter.drawRoundedRect(note_rect.adjusted(-3, -3, 3, 3), 8, 8)
            elif i in self.selected_indices:
                # 选中状态
                painter.setBrush(QColor(palette.accent + "20"))
                painter.setPen(QPen(QColor(palette.accent), 1))
                painter.drawRoundedRect(note_rect, 4, 4)

            if note.is_bar:
                # 小节线
                painter.setPen(QPen(QColor(palette.border), 1))
                painter.drawLine(x + note_width // 2, y - 20,
                               x + note_width // 2, y + 55)
            elif note.is_space:
                # 空格
                pass
            else:
                # 音符数字
                self._draw_note_value(painter, x, y, note_width, note, palette)

                # 指法图
                if note.value in self.fingering_map:
                    fingering = self.fingering_map[note.value]
                    self._draw_fingering(painter, x + note_width // 2, y + 25, fingering, palette)

            x += note_width + 5

    def _draw_note_value(self, painter: QPainter, x: int, y: int, width: int,
                         note: NoteUnit, palette):
        """绘制音符值"""
        display_note = note.display_value

        # 设置字体
        font = QFont("FangSong", 16, QFont.Weight.Bold)
        painter.setFont(font)

        # 设置颜色
        if note.value.startswith('(') or note.value.startswith('['):
            painter.setPen(QColor(palette.primary))
        else:
            painter.setPen(QColor(palette.text))

        # 绘制文本
        painter.drawText(x, y - 15, width, 25,
                        Qt.AlignmentFlag.AlignCenter, display_note)

        # 绘制时值线
        if note.duration < 0.5:
            # 十六分音符
            painter.setPen(QPen(QColor(palette.text), 1))
            painter.drawLine(x + 5, y + 40, x + width - 5, y + 40)
            painter.drawLine(x + 5, y + 45, x + width - 5, y + 45)
        elif note.duration < 1.0:
            # 八分音符
            painter.setPen(QPen(QColor(palette.text), 1))
            painter.drawLine(x + 5, y + 40, x + width - 5, y + 40)

    def _draw_fingering(self, painter: QPainter, center_x: int, y: int,
                        fingering: List[int], palette):
        """绘制指法图"""
        hole_spacing = 10
        hole_radius = 3

        for i, pressed in enumerate(fingering):
            hole_y = y + i * hole_spacing

            if pressed:
                painter.setBrush(QColor(palette.ink))
                painter.setPen(QPen(QColor(palette.ink), 1))
            else:
                painter.setBrush(QColor(palette.paper))
                painter.setPen(QPen(QColor(palette.secondary), 1))

            painter.drawEllipse(center_x - hole_radius, hole_y,
                              hole_radius * 2, hole_radius * 2)

    def mousePressEvent(self, event):
        """处理鼠标点击"""
        if not self.notes:
            return

        x = event.position().x()
        y = event.position().y()

        # 计算点击的音符索引
        note_index = int((x - 15) / 60)
        if 0 <= note_index < len(self.notes):
            self.note_clicked.emit(note_index)


# 导入 QRect
from PyQt6.QtCore import QRect