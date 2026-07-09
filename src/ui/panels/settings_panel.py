"""设置面板"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QComboBox, QFrame, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .base_panel import BasePanel
from ..theme import theme_manager, PRESETS
from ..theme.palettes import Palette
from ...shared.i18n import texts


class ThemeCard(QFrame):
    """主题卡片"""

    def __init__(self, palette: Palette, parent=None):
        super().__init__(parent)
        self.palette = palette
        self._init_ui()

    def _init_ui(self):
        p = self.palette
        self.setFixedSize(160, 100)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(5)

        # 预览色块
        colors_layout = QHBoxLayout()
        colors_layout.setSpacing(3)

        for color in [p.background, p.primary, p.accent, p.secondary]:
            block = QLabel()
            block.setFixedSize(20, 20)
            block.setStyleSheet(f"""
                background-color: {color};
                border-radius: 3px;
                border: 1px solid {p.border};
            """)
            colors_layout.addWidget(block)

        layout.addLayout(colors_layout)

        # 主题名称
        name_label = QLabel(p.display_name)
        name_label.setStyleSheet(f"color: {p.text}; font-weight: bold; font-size: 11px;")
        layout.addWidget(name_label)

        # 选中标记
        self.selected_indicator = QLabel("✓")
        self.selected_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.selected_indicator.setStyleSheet(f"""
            background-color: {p.primary};
            color: {p.paper};
            border-radius: 8px;
            font-weight: bold;
            font-size: 10px;
            padding: 2px;
        """)
        self.selected_indicator.hide()
        layout.addWidget(self.selected_indicator, alignment=Qt.AlignmentFlag.AlignRight)

        layout.addStretch()

        self._update_style(False)

    def _update_style(self, selected: bool):
        p = self.palette
        border = p.primary if selected else p.border
        self.setStyleSheet(f"""
            ThemeCard {{
                background-color: {p.panel_bg};
                border: 2px solid {border};
                border-radius: 8px;
            }}
        """)
        self.selected_indicator.setVisible(selected)

    def set_selected(self, selected: bool):
        self._update_style(selected)


class SettingsPanel(BasePanel):
    """设置面板"""

    def __init__(self, parent=None):
        super().__init__("设置", parent)
        self._init_content()

    def _init_content(self):
        p = theme_manager.current_palette

        # 主题设置
        theme_frame = self.create_section_frame()
        theme_layout = QVBoxLayout(theme_frame)

        theme_title = self.create_section_title("主题风格")
        theme_layout.addWidget(theme_title)

        # 主题卡片网格
        themes_grid = QHBoxLayout()
        themes_grid.setSpacing(12)

        self.theme_cards = []
        current_name = theme_manager.current_palette.name

        for name, palette in PRESETS.items():
            card = ThemeCard(palette)
            card.mousePressEvent = lambda e, n=name: self._select_theme(n)
            card.set_selected(name == current_name)
            themes_grid.addWidget(card)
            self.theme_cards.append((name, card))

        themes_grid.addStretch()
        theme_layout.addLayout(themes_grid)

        self.add_content(theme_frame)

        # 音频设置
        audio_frame = self.create_section_frame()
        audio_layout = QVBoxLayout(audio_frame)

        audio_title = self.create_section_title("音频设置")
        audio_layout.addWidget(audio_title)

        device_row = QHBoxLayout()
        device_row.addWidget(QLabel("输出设备"))
        device_combo = QComboBox()
        device_combo.addItems(["系统默认", "扬声器", "耳机"])
        device_row.addWidget(device_combo)
        device_row.addStretch()
        audio_layout.addLayout(device_row)

        eq_row = QHBoxLayout()
        eq_row.addWidget(QLabel("均衡器"))
        eq_combo = QComboBox()
        eq_combo.addItems(["关闭", "流行", "古典", "爵士", "摇滚"])
        eq_row.addWidget(eq_combo)
        eq_row.addStretch()
        audio_layout.addLayout(eq_row)

        self.add_content(audio_frame)

        # 关于
        about_frame = self.create_section_frame()
        about_layout = QVBoxLayout(about_frame)

        about_title = self.create_section_title("关于")
        about_layout.addWidget(about_title)

        about_text = QLabel("余音 v2.0\n竹笛学习助手\n\n专业的竹笛简谱学习工具")
        about_text.setStyleSheet(f"color: {p.text_secondary};")
        about_layout.addWidget(about_text)

        self.add_content(about_frame)

        self.add_stretch()

    def _select_theme(self, name: str):
        theme_manager.set_theme(name)
        for card_name, card in self.theme_cards:
            card.set_selected(card_name == name)