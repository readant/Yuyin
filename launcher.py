"""余音 - Web启动器"""
import os
import sys
import signal
import threading
import webbrowser
import time

# 确保项目根目录在路径中
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "web"))

HOST = "127.0.0.1"
PORT = 5000
URL = f"http://{HOST}:{PORT}"

# 检测 PyQt6 是否可用
_HAS_PYQT6 = False
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer
    _HAS_PYQT6 = True
except ImportError:
    pass


def open_browser():
    """延迟打开浏览器，等待服务就绪"""
    time.sleep(1.5)
    webbrowser.open(URL)


def _start_server_thread():
    """后台启动 uvicorn"""
    from app import app
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")


def _create_tray_icon():
    """生成系统托盘图标"""
    from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
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


def run_with_splash():
    """带水墨启动动画的启动流程"""
    from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
    from src.ui.splash import SplashWindow

    app_qt = QApplication(sys.argv)
    app_qt.setQuitOnLastWindowClosed(False)

    # 后台启动 Web 服务
    server_thread = threading.Thread(target=_start_server_thread, daemon=True)
    server_thread.start()

    # 显示水墨启动动画
    splash = SplashWindow()
    tray = {}  # 用字典保持引用

    def _setup_tray():
        """创建系统托盘"""
        icon = _create_tray_icon()
        tray_icon = QSystemTrayIcon(icon, app_qt)
        tray_icon.setToolTip("余音 - 竹笛学习助手")

        menu = QMenu()
        open_action = menu.addAction("打开页面")
        open_action.triggered.connect(lambda: webbrowser.open(URL))
        menu.addSeparator()
        quit_action = menu.addAction("退出")
        quit_action.triggered.connect(app_qt.quit)

        tray_icon.setContextMenu(menu)
        tray_icon.activated.connect(
            lambda reason: webbrowser.open(URL)
            if reason == QSystemTrayIcon.ActivationReason.DoubleClick else None
        )
        tray_icon.show()
        tray['icon'] = tray_icon

    def on_splash_finished():
        splash.close()
        webbrowser.open(URL)
        _setup_tray()

    splash.on_finished = on_splash_finished
    splash.show()

    # Ctrl+C 退出
    def shutdown(sig, frame):
        app_qt.quit()

    signal.signal(signal.SIGINT, shutdown)

    app_qt.exec()


def run_without_splash():
    """无动画的启动流程（纯终端）"""
    print()
    print("  ╔══════════════════════════════════╗")
    print("  ║        余音 - 清笛谱笺            ║")
    print("  ╚══════════════════════════════════╝")
    print()
    print(f"  服务启动中: {URL}")
    print("  按 Ctrl+C 停止服务")
    print()

    # 后台线程打开浏览器
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    # 优雅退出
    def shutdown(sig, frame):
        print("\n  服务已停止")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    from app import app
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")


def main():
    if _HAS_PYQT6:
        run_with_splash()
    else:
        run_without_splash()


if __name__ == "__main__":
    main()
