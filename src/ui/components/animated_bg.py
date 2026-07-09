"""动态背景组件"""
import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient

from ..theme import theme_manager


class CloudLayer:
    """云纹层"""

    def __init__(self, x: float, y: float, size: float, speed: float, opacity: float):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.opacity = opacity
        self.phase = random.uniform(0, 2 * math.pi)

    def update(self, width: float, height: float):
        """更新位置"""
        self.x += self.speed
        self.phase += 0.02

        # 超出边界时重置
        if self.x > width + self.size:
            self.x = -self.size
            self.y = random.uniform(0, height)

        # 轻微上下浮动
        self.y += math.sin(self.phase) * 0.3


import random


class AnimatedBackground(QWidget):
    """动态背景组件"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.clouds: list[CloudLayer] = []
        self._init_clouds()

        # 动画定时器
        self.timer = QTimer()
        self.timer.setInterval(33)  # ~30fps
        self.timer.timeout.connect(self._animate)
        self.timer.start()

    def _init_clouds(self):
        """初始化云纹"""
        for _ in range(8):
            cloud = CloudLayer(
                x=random.uniform(-100, 800),
                y=random.uniform(0, 600),
                size=random.uniform(80, 200),
                speed=random.uniform(0.2, 0.8),
                opacity=random.uniform(0.03, 0.08)
            )
            self.clouds.append(cloud)

    def _animate(self):
        """动画更新"""
        for cloud in self.clouds:
            cloud.update(self.width(), self.height())
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        p = theme_manager.current_palette
        rect = self.rect()

        # 绘制云纹
        for cloud in self.clouds:
            self._draw_cloud(painter, cloud, p)

        painter.end()

    def _draw_cloud(self, painter: QPainter, cloud: CloudLayer, palette):
        """绘制云纹"""
        # 创建渐变
        gradient = QLinearGradient(
            cloud.x - cloud.size / 2, cloud.y,
            cloud.x + cloud.size / 2, cloud.y
        )

        # 云纹颜色
        cloud_color = QColor(palette.secondary)
        cloud_color.setAlpha(int(cloud.opacity * 255))

        center_color = QColor(cloud_color)
        edge_color = QColor(cloud_color)
        edge_color.setAlpha(0)

        gradient.setColorAt(0, edge_color)
        gradient.setColorAt(0.3, cloud_color)
        gradient.setColorAt(0.5, center_color)
        gradient.setColorAt(0.7, cloud_color)
        gradient.setColorAt(1, edge_color)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))

        # 绘制椭圆云纹
        painter.drawEllipse(
            QPointF(cloud.x, cloud.y),
            cloud.size / 2,
            cloud.size / 4
        )


class DynamicBackground(QWidget):
    """动态背景容器"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 云纹层
        self.cloud_layer = AnimatedBackground(self)

    def resizeEvent(self, event):
        """窗口大小改变时调整云纹层大小"""
        self.cloud_layer.resize(self.size())
        super().resizeEvent(event)

    def paintEvent(self, event):
        """绘制背景"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        p = theme_manager.current_palette

        # 绘制渐变背景
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(p.background))
        gradient.setColorAt(0.5, QColor(p.surface))
        gradient.setColorAt(1, QColor(p.background))

        painter.fillRect(self.rect(), gradient)

        painter.end()