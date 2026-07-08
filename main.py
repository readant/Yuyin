#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""余音 - 主入口"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

from src.config import settings
from src.shared.logging import setup_logging, get_logger


def main():
    # 设置日志
    setup_logging(
        level="DEBUG" if settings.app.debug else "INFO",
        log_file="yuyin.log" if not settings.app.debug else None
    )
    logger = get_logger(__name__)
    logger.info(f"启动 {settings.app.name} v{settings.app.version}")

    # 确保数据目录存在
    os.makedirs('data', exist_ok=True)

    app = QApplication(sys.argv)
    app.setFont(QFont('Microsoft YaHei', 10))

    from src.ui.theme import theme_manager
    theme_manager.apply_theme()

    # 启动动画
    from src.ui.splash import SplashWindow

    def show_main():
        from src.ui.main_window import MainWindow
        window = MainWindow()
        window.show()
        app._main_window = window
        logger.info("主窗口已显示")

    splash = SplashWindow()
    splash.on_finished = show_main
    splash.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()