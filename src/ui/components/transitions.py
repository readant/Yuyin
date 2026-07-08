"""转场动效组件"""
import math
from PyQt6.QtWidgets import QWidget, QStackedWidget
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QPointF
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QRadialGradient

from ..theme import theme_manager


class CurtainTransition(QWidget):
    """卷帘转场效果"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._progress = 0
        self._is_animating = False

    def start(self, duration: int = 500):
        """开始动画"""
        self._is_animating = True
        self._progress = 0
        self.show()

        self._animation = QPropertyAnimation(self, b"curtainProgress")
        self._animation.setDuration(duration)
        self._animation.setStartValue(0)
        self._animation.setEndValue(100)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._animation.finished.connect(self._on_finished)
        self._animation.start()

    def _on_finished(self):
        self._is_animating = False
        self.hide()

    def getCurtainProgress(self):
        return self._progress

    def setCurtainProgress(self, value):
        self._progress = value
        self.update()

    curtainProgress = property(getCurtainProgress, setCurtainProgress)

    def paintEvent(self, event):
        if not self._is_animating:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        p = theme_manager.current_palette
        rect = self.rect()

        # 卷帘效果 - 从上往下展开
        curtain_height = int(rect.height() * self._progress / 100)

        # 绘制卷帘
        gradient = QLinearGradient(0, 0, 0, curtain_height)
        gradient.setColorAt(0, QColor(p.primary + "CC"))
        gradient.setColorAt(0.5, QColor(p.primary))
        gradient.setColorAt(1, QColor(p.primary_dark))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawRect(0, 0, rect.width(), curtain_height)

        # 卷帘底部阴影
        shadow_gradient = QLinearGradient(0, curtain_height - 20, 0, curtain_height)
        shadow_gradient.setColorAt(0, QColor(0, 0, 0, 0))
        shadow_gradient.setColorAt(1, QColor(0, 0, 0, 50))

        painter.setBrush(QBrush(shadow_gradient))
        painter.drawRect(0, curtain_height - 20, rect.width(), 20)

        painter.end()


class InkSplashTransition(QWidget):
    """墨晕转场效果"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._progress = 0
        self._is_animating = False

    def start(self, duration: int = 600):
        """开始动画"""
        self._is_animating = True
        self._progress = 0
        self.show()

        self._animation = QPropertyAnimation(self, b"inkProgress")
        self._animation.setDuration(duration)
        self._animation.setStartValue(0)
        self._animation.setEndValue(100)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._animation.finished.connect(self._on_finished)
        self._animation.start()

    def _on_finished(self):
        self._is_animating = False
        self.hide()

    def getInkProgress(self):
        return self._progress

    def setInkProgress(self, value):
        self._progress = value
        self.update()

    inkProgress = property(getInkProgress, setInkProgress)

    def paintEvent(self, event):
        if not self._is_animating:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        p = theme_manager.current_palette
        rect = self.rect()
        center = QPointF(rect.center().x(), rect.center().y())

        # 墨晕效果 - 从中心扩散
        max_radius = math.sqrt(rect.width()**2 + rect.height()**2) / 2
        radius = max_radius * self._progress / 100

        # 创建径向渐变
        gradient = QRadialGradient(center, radius)
        gradient.setColorAt(0, QColor(p.ink + "FF"))
        gradient.setColorAt(0.7, QColor(p.ink + "DD"))
        gradient.setColorAt(0.9, QColor(p.ink + "88"))
        gradient.setColorAt(1, QColor(p.ink + "00"))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(center, radius, radius)

        painter.end()


class PageFlipTransition(QWidget):
    """翻页转场效果"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._progress = 0
        self._is_animating = False

    def start(self, duration: int = 500):
        """开始动画"""
        self._is_animating = True
        self._progress = 0
        self.show()

        self._animation = QPropertyAnimation(self, b"pageProgress")
        self._animation.setDuration(duration)
        self._animation.setStartValue(0)
        self._animation.setEndValue(100)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._animation.finished.connect(self._on_finished)
        self._animation.start()

    def _on_finished(self):
        self._is_animating = False
        self.hide()

    def getPageProgress(self):
        return self._progress

    def setPageProgress(self, value):
        self._progress = value
        self.update()

    pageProgress = property(getPageProgress, setPageProgress)

    def paintEvent(self, event):
        if not self._is_animating:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        p = theme_manager.current_palette
        rect = self.rect()

        # 翻页效果 - 从右往左
        flip_progress = self._progress / 100
        page_width = rect.width() * flip_progress

        # 绘制翻页阴影
        if flip_progress > 0 and flip_progress < 1:
            shadow_x = rect.width() - page_width
            shadow_gradient = QLinearGradient(shadow_x - 30, 0, shadow_x, 0)
            shadow_gradient.setColorAt(0, QColor(0, 0, 0, 0))
            shadow_gradient.setColorAt(1, QColor(0, 0, 0, 80))

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(shadow_gradient))
            painter.drawRect(int(shadow_x - 30), 0, 30, rect.height())

        # 绘制页面
        page_gradient = QLinearGradient(rect.width() - page_width, 0, rect.width(), 0)
        page_gradient.setColorAt(0, QColor(p.paper))
        page_gradient.setColorAt(0.3, QColor(p.paper + "EE"))
        page_gradient.setColorAt(1, QColor(p.paper + "CC"))

        painter.setBrush(QBrush(page_gradient))
        painter.setPen(QPen(QColor(p.border), 1))
        painter.drawRect(int(rect.width() - page_width), 0, int(page_width), rect.height())

        # 页面纹理
        if page_width > 50:
            painter.setPen(QPen(QColor(p.border + "40"), 0.5))
            for i in range(0, int(page_width), 15):
                x = int(rect.width() - page_width + i)
                painter.drawLine(x, 10, x, rect.height() - 10)

        painter.end()


class TransitionManager:
    """转场管理器"""

    def __init__(self, stacked_widget: QStackedWidget):
        self.stacked_widget = stacked_widget
        self.current_index = stacked_widget.currentIndex()

        # 转场效果
        self.transitions = {
            'curtain': CurtainTransition(stacked_widget),
            'ink': InkSplashTransition(stacked_widget),
            'page': PageFlipTransition(stacked_widget)
        }

        self.current_transition = None

    def set_transition(self, name: str):
        """设置转场效果"""
        if name in self.transitions:
            self.current_transition = self.transitions[name]

    def transition_to(self, index: int, transition_name: str = None):
        """切换到指定页面"""
        if index == self.current_index:
            return

        if transition_name:
            self.set_transition(transition_name)

        if self.current_transition:
            # 执行转场动画
            self.current_transition.start()
            # 延迟切换页面
            QTimer.singleShot(250, lambda: self._switch_page(index))
        else:
            self._switch_page(index)

    def _switch_page(self, index: int):
        """切换页面"""
        self.stacked_widget.setCurrentIndex(index)
        self.current_index = index