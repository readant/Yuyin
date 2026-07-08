"""主题管理器"""
from typing import Optional, Dict
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import QSettings

from .palettes import Palette, PRESETS, DEFAULT_PALETTE


class ThemeManager:
    """主题管理器单例"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self._current_palette: Palette = DEFAULT_PALETTE
        self._settings = QSettings("Yuyin", "Theme")
        self._load_settings()

    @property
    def current_palette(self) -> Palette:
        return self._current_palette

    def get_palette(self, name: str) -> Optional[Palette]:
        return PRESETS.get(name)

    def get_all_palettes(self) -> Dict[str, str]:
        return {name: p.display_name for name, p in PRESETS.items()}

    def set_theme(self, name: str):
        palette = PRESETS.get(name)
        if palette:
            self._current_palette = palette
            self._save_settings()
            self.apply_theme()

    def apply_theme(self):
        app = QApplication.instance()
        if not app:
            return

        p = self._current_palette

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(p.background))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(p.text))
        palette.setColor(QPalette.ColorRole.Base, QColor(p.panel_bg))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(p.surface))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(p.panel_bg))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(p.text))
        palette.setColor(QPalette.ColorRole.Text, QColor(p.text))
        palette.setColor(QPalette.ColorRole.Button, QColor(p.button_bg))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(p.text))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(p.accent))
        palette.setColor(QPalette.ColorRole.Link, QColor(p.primary))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(p.primary))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(p.paper))

        app.setPalette(palette)
        app.setStyleSheet(self._generate_stylesheet(p))

    def _generate_stylesheet(self, p: Palette) -> str:
        return f"""
        QWidget {{
            font-family: 'Microsoft YaHei', sans-serif;
            color: {p.text};
        }}

        QMainWindow {{
            background-color: {p.background};
        }}

        QPushButton {{
            background-color: {p.button_bg};
            color: {p.paper};
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            min-height: 20px;
        }}

        QPushButton:hover {{
            background-color: {p.button_hover};
        }}

        QPushButton:pressed {{
            background-color: {p.button_pressed};
        }}

        QPushButton:disabled {{
            background-color: {p.button_disabled};
            color: {p.text_light};
        }}

        QTextEdit, QSpinBox, QComboBox, QLineEdit {{
            background-color: {p.input_bg};
            color: {p.text};
            border: 1px solid {p.input_border};
            border-radius: 6px;
            padding: 8px;
            selection-background-color: {p.primary};
            selection-color: {p.paper};
        }}

        QTextEdit:focus, QSpinBox:focus, QComboBox:focus, QLineEdit:focus {{
            border-color: {p.input_focus};
        }}

        QComboBox::drop-down {{
            border: none;
            padding-right: 8px;
        }}

        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid {p.text};
        }}

        QComboBox QAbstractItemView {{
            background-color: {p.input_bg};
            color: {p.text};
            border: 1px solid {p.border};
            border-radius: 4px;
            selection-background-color: {p.primary};
            selection-color: {p.paper};
        }}

        QProgressBar {{
            background-color: {p.progress_bg};
            border: none;
            border-radius: 4px;
            text-align: center;
            color: {p.text};
            height: 8px;
        }}

        QProgressBar::chunk {{
            background-color: {p.progress_fill};
            border-radius: 4px;
        }}

        QSlider::groove:horizontal {{
            background-color: {p.slider_bg};
            height: 6px;
            border-radius: 3px;
        }}

        QSlider::handle:horizontal {{
            background-color: {p.slider_handle};
            width: 16px;
            height: 16px;
            margin: -5px 0;
            border-radius: 8px;
        }}

        QSlider::sub-page:horizontal {{
            background-color: {p.slider_fill};
            border-radius: 3px;
        }}

        QLabel {{
            color: {p.text};
            background: transparent;
        }}

        QListWidget {{
            background-color: {p.panel_bg};
            border: 1px solid {p.border};
            border-radius: 6px;
            padding: 4px;
        }}

        QListWidget::item {{
            background-color: transparent;
            border: none;
            border-radius: 4px;
            padding: 8px;
            margin: 2px;
        }}

        QListWidget::item:selected {{
            background-color: {p.primary};
            color: {p.paper};
        }}

        QListWidget::item:hover {{
            background-color: {p.surface};
        }}

        QScrollBar:vertical {{
            background-color: {p.surface};
            width: 10px;
            margin: 0;
        }}

        QScrollBar::handle:vertical {{
            background-color: {p.border};
            min-height: 20px;
            border-radius: 5px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {p.primary};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}

        QStatusBar {{
            background-color: {p.surface};
            color: {p.text_secondary};
            border-top: 1px solid {p.border};
        }}
        """

    def _load_settings(self):
        theme_name = self._settings.value("theme_name", DEFAULT_PALETTE.name)
        if theme_name in PRESETS:
            self._current_palette = PRESETS[theme_name]

    def _save_settings(self):
        self._settings.setValue("theme_name", self._current_palette.name)


theme_manager = ThemeManager()