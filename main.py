#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""余音 - 主入口"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

from src.ui.theme import theme_manager


def main():
    os.makedirs('data', exist_ok=True)

    app = QApplication(sys.argv)
    app.setFont(QFont('Microsoft YaHei', 10))

    theme_manager.apply_theme()

    # 启动动画
    from src.ui.splash import SplashWindow

    def show_main():
        from src.ui.main_window import MainWindow
        window = MainWindow()
        window.show()
        app._main_window = window

    splash = SplashWindow()
    splash.on_finished = show_main
    splash.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()