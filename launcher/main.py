"""余音启动器 - PyQt6水墨动画 + Web应用"""
import sys
import os
import threading
import webbrowser

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont

# 将项目根目录加入路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from splash import SplashWindow
from server import WebServer


def create_tray_icon():
    """生成简约的托盘图标"""
    pixmap = QPixmap(64, 64)
    pixmap.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    painter.setBrush(QColor(139, 37, 0))
    painter.setPen(QColor(0, 0, 0, 0))
    painter.drawEllipse(4, 4, 56, 56)

    painter.setPen(QColor(235, 225, 205))
    painter.setFont(QFont("KaiTi", 28, QFont.Weight.Bold))
    painter.drawText(pixmap.rect(), 0x0084, "余")
    painter.end()

    return QIcon(pixmap)


class Launcher:
    """启动器主类"""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        self.server = None
        self.splash = None
        self.tray = None
        self.PORT = 5000

    def run(self):
        # 1. 启动Web服务（后台线程）
        self.server = WebServer(port=self.PORT)
        server_thread = threading.Thread(
            target=self.server.start, daemon=True
        )
        server_thread.start()

        # 2. 显示水墨启动动画
        self.splash = SplashWindow()
        self.splash.on_finished = self._on_splash_finished
        self.splash.show()

        sys.exit(self.app.exec())

    def _on_splash_finished(self):
        """动画结束后打开浏览器并显示托盘"""
        webbrowser.open(f"http://localhost:{self.PORT}")
        self._setup_tray()

    def _setup_tray(self):
        """创建系统托盘"""
        self.tray = QSystemTrayIcon(create_tray_icon(), self.app)
        self.tray.setToolTip("余音 - 竹笛学习助手")

        menu = QMenu()
        open_action = menu.addAction("打开余音")
        open_action.triggered.connect(
            lambda: webbrowser.open(f"http://localhost:{self.PORT}")
        )
        menu.addSeparator()
        quit_action = menu.addAction("退出")
        quit_action.triggered.connect(self._quit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            webbrowser.open(f"http://localhost:{self.PORT}")

    def _quit(self):
        if self.server:
            self.server.stop()
        self.app.quit()


if __name__ == '__main__':
    Launcher().run()
