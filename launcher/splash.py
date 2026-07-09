"""水墨启动画面 - 老旧宣纸质感"""
import math
import random
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt6.QtGui import (QPainter, QColor, QPen, QBrush, QFont,
                         QRadialGradient, QLinearGradient, QPainterPath)


class SplashWindow(QWidget):
    """水墨启动画面"""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(650, 400)

        self.frame = 0
        self.alpha = 0
        self.on_finished = None

        self.phase = 0.0
        self.phase_speed = 0.008

        self.ink_radius = 0
        self.ink_target_radius = 160
        self.ink_drops = []
        self.ink_shape = self._generate_ink_shape()

        self.text_alpha = 0

        # 生成老旧纸张元素
        self._generate_aging_elements()

        # 动画定时器
        self.timer = QTimer()
        self.timer.setInterval(16)
        self.timer.timeout.connect(self.animate)
        self.timer.start()

    def _generate_aging_elements(self):
        """生成老化元素"""
        random.seed(42)

        # 水渍痕迹
        self.water_stains = []
        for _ in range(4):
            x = random.randint(80, 570)
            y = random.randint(50, 350)
            rx = random.randint(40, 100)
            ry = random.randint(30, 70)
            self.water_stains.append((x, y, rx, ry))

        # 折痕
        self.creases = []
        for _ in range(3):
            x1 = random.randint(50, 600)
            y1 = random.randint(30, 370)
            x2 = x1 + random.randint(-100, 100)
            y2 = y1 + random.randint(-80, 80)
            self.creases.append((x1, y1, x2, y2))

        # 纸张斑点（更多）
        self.spots = []
        for _ in range(50):
            x = random.randint(15, 635)
            y = random.randint(15, 385)
            size = random.uniform(1, 6)
            color_type = random.choice(['dark', 'light', 'brown'])
            self.spots.append((x, y, size, color_type))

        # 纤维
        self.fibers = []
        for _ in range(60):
            x = random.randint(20, 630)
            y = random.randint(20, 380)
            length = random.randint(5, 30)
            angle = random.uniform(0, math.pi)
            self.fibers.append((x, y, length, angle))

        # 破损边缘点
        self.torn_edges = []
        for _ in range(30):
            side = random.choice(['top', 'bottom', 'left', 'right'])
            if side == 'top':
                x, y = random.randint(0, 650), random.randint(0, 15)
            elif side == 'bottom':
                x, y = random.randint(0, 650), random.randint(385, 400)
            elif side == 'left':
                x, y = random.randint(0, 15), random.randint(0, 400)
            else:
                x, y = random.randint(635, 650), random.randint(0, 400)
            self.torn_edges.append((x, y, random.randint(5, 15)))

    def _generate_ink_shape(self):
        random.seed(123)
        points = []
        for i in range(24):
            angle = (2 * math.pi * i) / 24
            r = self.ink_target_radius * (0.75 + 0.25 * random.random())
            x = r * math.cos(angle)
            y = r * math.sin(angle) * 0.7
            points.append((x, y))
        return points

    def animate(self):
        self.frame += 1
        self.phase += self.phase_speed

        if self.phase < 1:
            self.alpha = min(255, int(self.phase * 280))
        elif self.phase < 2:
            progress = self.phase - 1
            self.ink_radius = self.ink_target_radius * self._ease_out_cubic(progress)
            if random.random() > 0.6 and progress < 0.7:
                angle = random.uniform(0, 2 * math.pi)
                dist = self.ink_radius * random.uniform(0.85, 1.15)
                self.ink_drops.append({
                    'x': dist * math.cos(angle),
                    'y': dist * math.sin(angle) * 0.7,
                    'r': random.uniform(2, 6),
                    'opacity': random.uniform(0.2, 0.5)
                })
        elif self.phase < 3:
            progress = self.phase - 2
            self.text_alpha = int(self._ease_out_cubic(progress) * 255)
        elif self.phase < 4:
            self.alpha = 255
            self.text_alpha = 255
        elif self.phase < 5:
            progress = self.phase - 4
            fade = 1 - self._ease_in_cubic(progress)
            self.alpha = int(255 * fade)
            self.text_alpha = int(255 * fade)
        else:
            self.timer.stop()
            if self.on_finished:
                self.on_finished()
            self.close()
            return

        self.update()

    def _ease_out_cubic(self, t):
        return 1 - pow(1 - t, 3)

    def _ease_in_cubic(self, t):
        return t * t * t

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.alpha <= 0:
            painter.end()
            return

        opacity = self.alpha / 255

        # 1. 基础纸张颜色（更黄更旧）
        self._draw_base_paper(painter, opacity)

        # 2. 纸张纹理变化
        self._draw_paper_texture(painter, opacity)

        # 3. 水渍痕迹
        self._draw_water_stains(painter, opacity)

        # 4. 折痕
        self._draw_creases(painter, opacity)

        # 5. 斑点和污渍
        self._draw_spots(painter, opacity)

        # 6. 纤维
        self._draw_fibers(painter, opacity)

        # 7. 边缘氧化
        self._draw_edge_oxidation(painter, opacity)

        # 8. 破损边缘
        self._draw_torn_edges(painter, opacity)

        # 9. 墨渍背景
        self._draw_ink_spots(painter, opacity)

        # 10. 主墨痕
        if self.ink_radius > 0:
            self._draw_main_ink(painter)

        # 11. 文字
        if self.text_alpha > 0:
            self._draw_text(painter)

        # 12. 装饰
        if self.phase > 2.5:
            self._draw_decorations(painter)

        painter.end()

    def _draw_base_paper(self, painter, opacity):
        """基础纸张 - 泛黄陈旧"""
        # 主体颜色（偏黄偏暗）
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(235, 225, 205, self.alpha))
        painter.drawRect(self.rect())

        # 渐变叠加
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(240, 228, 200, int(40 * opacity)))
        gradient.setColorAt(0.3, QColor(230, 218, 195, int(30 * opacity)))
        gradient.setColorAt(0.7, QColor(238, 225, 198, int(35 * opacity)))
        gradient.setColorAt(1, QColor(228, 215, 190, int(40 * opacity)))
        painter.setBrush(QBrush(gradient))
        painter.drawRect(self.rect())

    def _draw_paper_texture(self, painter, opacity):
        """纸张纹理"""
        random.seed(888)
        painter.setPen(Qt.PenStyle.NoPen)

        # 大块颜色变化
        for _ in range(15):
            x = random.randint(0, 650)
            y = random.randint(0, 400)
            size = random.randint(30, 80)
            r_offset = random.randint(-12, 8)
            g_offset = random.randint(-15, 5)
            b_offset = random.randint(-18, 3)
            color = QColor(235 + r_offset, 225 + g_offset, 205 + b_offset, int(20 * opacity))
            painter.setBrush(color)
            painter.drawEllipse(QPointF(x, y), size, size * 0.7)

    def _draw_water_stains(self, painter, opacity):
        """水渍痕迹"""
        painter.setPen(Qt.PenStyle.NoPen)

        for x, y, rx, ry in self.water_stains:
            # 外圈淡色
            gradient = QRadialGradient(QPointF(x, y), max(rx, ry))
            gradient.setColorAt(0, QColor(220, 200, 170, int(25 * opacity)))
            gradient.setColorAt(0.5, QColor(225, 205, 175, int(15 * opacity)))
            gradient.setColorAt(1, QColor(235, 225, 205, 0))
            painter.setBrush(QBrush(gradient))
            painter.drawEllipse(QPointF(x, y), rx, ry)

            # 内圈稍深
            gradient2 = QRadialGradient(QPointF(x, y), max(rx, ry) * 0.6)
            gradient2.setColorAt(0, QColor(215, 195, 165, int(15 * opacity)))
            gradient2.setColorAt(1, QColor(225, 205, 175, 0))
            painter.setBrush(QBrush(gradient2))
            painter.drawEllipse(QPointF(x, y), rx * 0.6, ry * 0.6)

    def _draw_creases(self, painter, opacity):
        """折痕"""
        for x1, y1, x2, y2 in self.creases:
            # 主折痕线
            pen = QPen(QColor(200, 185, 160, int(35 * opacity)))
            pen.setWidthF(1.5)
            painter.setPen(pen)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

            # 旁边的阴影
            pen2 = QPen(QColor(180, 165, 140, int(20 * opacity)))
            pen2.setWidthF(2)
            painter.setPen(pen2)
            painter.drawLine(QPointF(x1 + 2, y1 + 2), QPointF(x2 + 2, y2 + 2))

    def _draw_spots(self, painter, opacity):
        """斑点和污渍"""
        painter.setPen(Qt.PenStyle.NoPen)

        for x, y, size, color_type in self.spots:
            if color_type == 'dark':
                color = QColor(180, 165, 145, int(40 * opacity))
            elif color_type == 'light':
                color = QColor(245, 238, 220, int(30 * opacity))
            else:  # brown
                color = QColor(190, 170, 140, int(35 * opacity))
            painter.setBrush(color)
            painter.drawEllipse(QPointF(x, y), size, size)

    def _draw_fibers(self, painter, opacity):
        """纸张纤维"""
        pen = QPen(QColor(210, 195, 170, int(20 * opacity)))
        pen.setWidthF(0.5)
        painter.setPen(pen)

        for x, y, length, angle in self.fibers:
            end_x = x + length * math.cos(angle)
            end_y = y + length * math.sin(angle)
            painter.drawLine(QPointF(x, y), QPointF(end_x, end_y))

    def _draw_edge_oxidation(self, painter, opacity):
        """边缘氧化发黄"""
        w, h = self.width(), self.height()
        edge_width = 50

        painter.setPen(Qt.PenStyle.NoPen)

        # 上边缘
        gradient = QLinearGradient(0, 0, 0, edge_width)
        gradient.setColorAt(0, QColor(195, 175, 145, int(50 * opacity)))
        gradient.setColorAt(1, QColor(235, 225, 205, 0))
        painter.setBrush(QBrush(gradient))
        painter.drawRect(0, 0, w, edge_width)

        # 下边缘
        gradient = QLinearGradient(0, h - edge_width, 0, h)
        gradient.setColorAt(0, QColor(235, 225, 205, 0))
        gradient.setColorAt(1, QColor(190, 170, 140, int(55 * opacity)))
        painter.setBrush(QBrush(gradient))
        painter.drawRect(0, h - edge_width, w, edge_width)

        # 左边缘
        gradient = QLinearGradient(0, 0, edge_width, 0)
        gradient.setColorAt(0, QColor(200, 180, 150, int(45 * opacity)))
        gradient.setColorAt(1, QColor(235, 225, 205, 0))
        painter.setBrush(QBrush(gradient))
        painter.drawRect(0, 0, edge_width, h)

        # 右边缘
        gradient = QLinearGradient(w - edge_width, 0, w, 0)
        gradient.setColorAt(0, QColor(235, 225, 205, 0))
        gradient.setColorAt(1, QColor(185, 165, 135, int(50 * opacity)))
        painter.setBrush(QBrush(gradient))
        painter.drawRect(w - edge_width, 0, edge_width, h)

        # 角落加重
        for cx, cy in [(0, 0), (w, 0), (0, h), (w, h)]:
            gradient = QRadialGradient(QPointF(cx, cy), 80)
            gradient.setColorAt(0, QColor(180, 160, 130, int(35 * opacity)))
            gradient.setColorAt(1, QColor(235, 225, 205, 0))
            painter.setBrush(QBrush(gradient))
            painter.drawEllipse(QPointF(cx, cy), 80, 80)

    def _draw_torn_edges(self, painter, opacity):
        """破损边缘"""
        painter.setPen(Qt.PenStyle.NoPen)

        for x, y, size in self.torn_edges:
            color = QColor(175, 155, 125, int(50 * opacity))
            painter.setBrush(color)
            painter.drawEllipse(QPointF(x, y), size * 0.5, size * 0.3)

    def _draw_ink_spots(self, painter, opacity):
        """墨渍背景"""
        random.seed(42)
        painter.setPen(Qt.PenStyle.NoPen)

        for _ in range(5):
            x = random.randint(100, 550)
            y = random.randint(60, 340)
            size = random.randint(25, 55)
            spot_phase = min(1.0, self.phase / 2.5)
            if spot_phase > 0:
                gradient = QRadialGradient(QPointF(x, y), size)
                gradient.setColorAt(0, QColor(44, 44, 44, int(25 * spot_phase * opacity)))
                gradient.setColorAt(0.5, QColor(44, 44, 44, int(15 * spot_phase * opacity)))
                gradient.setColorAt(1, QColor(44, 44, 44, 0))
                painter.setBrush(QBrush(gradient))
                painter.drawEllipse(QPointF(x, y), size, size * 0.8)

    def _draw_main_ink(self, painter):
        """绘制主墨痕"""
        r = self.ink_radius
        opacity = self.alpha / 255
        cx, cy = self.width() // 2, self.height() // 2

        gradient = QRadialGradient(QPointF(cx, cy), r)
        gradient.setColorAt(0, QColor(44, 44, 44, int(35 * opacity)))
        gradient.setColorAt(0.4, QColor(44, 44, 44, int(45 * opacity)))
        gradient.setColorAt(0.7, QColor(44, 44, 44, int(25 * opacity)))
        gradient.setColorAt(1, QColor(44, 44, 44, 0))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))

        path = QPainterPath()
        points = []
        for px, py in self.ink_shape:
            points.append(QPointF(cx + px * (r / self.ink_target_radius),
                                 cy + py * (r / self.ink_target_radius)))
        if points:
            path.moveTo(points[0])
            for p in points[1:]:
                path.lineTo(p)
            path.closeSubpath()
            painter.drawPath(path)

        for drop in self.ink_drops:
            drop_r = drop['r'] * (r / self.ink_target_radius)
            if drop_r > 0.5:
                dg = QRadialGradient(QPointF(cx + drop['x'], cy + drop['y']), drop_r)
                dg.setColorAt(0, QColor(44, 44, 44, int(100 * opacity * drop['opacity'])))
                dg.setColorAt(1, QColor(44, 44, 44, 0))
                painter.setBrush(QBrush(dg))
                painter.drawEllipse(QPointF(cx + drop['x'], cy + drop['y']), drop_r, drop_r)

    def _draw_text(self, painter):
        """绘制毛笔字"""
        opacity = self.text_alpha / 255 * (self.alpha / 255)
        cx, cy = self.width() // 2, self.height() // 2 - 15

        # 墨迹晕染底层
        painter.setPen(Qt.PenStyle.NoPen)
        gradient = QRadialGradient(QPointF(cx, cy), 120)
        gradient.setColorAt(0, QColor(44, 44, 44, int(18 * opacity)))
        gradient.setColorAt(1, QColor(44, 44, 44, 0))
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(QPointF(cx, cy), 140, 65)

        calligraphy_fonts = ["STXingkai", "STKaiti", "KaiTi", "FangSong"]
        selected_font = "KaiTi"
        for font_name in calligraphy_fonts:
            if QFont(font_name).exactMatch():
                selected_font = font_name
                break

        self._draw_char(painter, "余", cx - 65, cy, selected_font, opacity)
        self._draw_char(painter, "音", cx + 65, cy, selected_font, opacity)

    def _draw_char(self, painter, char, x, y, font_name, opacity):
        font = QFont(font_name, 72, QFont.Weight.Bold)
        painter.setFont(font)
        text_rect = QRectF(x - 50, y - 50, 100, 100)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(44, 44, 44, int(25 * opacity)))
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, char)

        painter.setPen(QColor(44, 44, 44, int(100 * opacity)))
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, char)

        painter.setPen(QColor(35, 35, 35, int(210 * opacity)))
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, char)

    def _draw_decorations(self, painter):
        progress = min(1.0, (self.phase - 2.5) * 2)
        opacity = self.alpha / 255 * progress

        self._draw_seal(painter, 530, 290, opacity)

        painter.setPen(QColor(139, 37, 0, int(100 * opacity)))
        font = QFont("KaiTi", 10)
        painter.setFont(font)
        painter.drawText(QRectF(510, 315, 80, 25), Qt.AlignmentFlag.AlignCenter, "甲辰年制")

    def _draw_seal(self, painter, x, y, opacity):
        size = 42
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(139, 37, 0, int(170 * opacity)))
        painter.drawRoundedRect(x - size//2, y - size//2, size, size, 2, 2)

        painter.setPen(QColor(235, 225, 205, int(190 * opacity)))
        font = QFont("KaiTi", 15, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(x - size//2, y - size//2, size, size),
                        Qt.AlignmentFlag.AlignCenter, "余")

    def mousePressEvent(self, event):
        self.phase = 5
        self.alpha = 0
        self.text_alpha = 0
        self.timer.stop()
        if self.on_finished:
            self.on_finished()
        self.close()