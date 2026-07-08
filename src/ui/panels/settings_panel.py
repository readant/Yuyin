"""设置面板"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QComboBox, QFrame, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

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
        self.setFixedSize(180, 120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 预览色块
        colors_layout = QHBoxLayout()
        colors_layout.setSpacing(4)
        
        for color in [p.background, p.primary, p.accent, p.secondary]:
            block = QLabel()
            block.setFixedSize(25, 25)
            block.setStyleSheet(f"""
                background-color: {color};
                border-radius: 4px;
                border: 1px solid {p.border};
            """)
            colors_layout.addWidget(block)
        
        layout.addLayout(colors_layout)
        
        # 主题名称
        name_label = QLabel(p.display_name)
        name_label.setStyleSheet(f"color: {p.text}; font-weight: bold;")
        layout.addWidget(name_label)
        
        # 色值预览
        hex_label = QLabel(p.primary)
        hex_label.setStyleSheet(f"color: {p.text_secondary}; font-size: 10px;")
        layout.addWidget(hex_label)
        
        layout.addStretch()
        
        # 选中标记
        self.selected_indicator = QLabel("✓")
        self.selected_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.selected_indicator.setStyleSheet(f"""
            background-color: {p.primary};
            color: {p.paper};
            border-radius: 10px;
            font-weight: bold;
        """)
        self.selected_indicator.hide()
        layout.addWidget(self.selected_indicator, alignment=Qt.AlignmentFlag.AlignRight)
        
        # 默认样式
        self._update_style(False)
    
    def _update_style(self, selected: bool):
        p = self.palette
        border = p.primary if selected else p.border
        self.setStyleSheet(f"""
            ThemeCard {{
                background-color: {p.panel_bg};
                border: 2px solid {border};
                border-radius: 10px;
            }}
        """)
        if selected:
            self.selected_indicator.show()
        else:
            self.selected_indicator.hide()
    
    def set_selected(self, selected: bool):
        self._update_style(selected)


class SettingsPanel(QWidget):
    """设置面板"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        p = theme_manager.current_palette
        
        # 使用滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(25)
        
        # 标题
        title = QLabel(texts.SETTINGS_TITLE)
        title.setFont(QFont("FangSong", 20, QFont.Weight.Bold))
        layout.addWidget(title)

        # 主题设置
        theme_section = self._create_section(texts.SETTINGS_THEME)
        layout.addWidget(theme_section)
        
        # 主题卡片网格
        themes_grid = QHBoxLayout()
        themes_grid.setSpacing(15)
        
        self.theme_cards = []
        current_name = theme_manager.current_palette.name
        
        for name, palette in PRESETS.items():
            card = ThemeCard(palette)
            card.mousePressEvent = lambda e, n=name: self._select_theme(n)
            card.set_selected(name == current_name)
            themes_grid.addWidget(card)
            self.theme_cards.append((name, card))
        
        themes_grid.addStretch()
        layout.addLayout(themes_grid)
        
        # 音频设置
        audio_section = self._create_section("🔊 音频设置")
        layout.addWidget(audio_section)
        
        audio_frame = self._create_option_frame()
        audio_layout = QVBoxLayout(audio_frame)
        
        # 输出设备
        device_row = QHBoxLayout()
        device_row.addWidget(QLabel("输出设备"))
        device_combo = QComboBox()
        device_combo.addItems(["系统默认", "扬声器", "耳机"])
        device_row.addWidget(device_combo)
        device_row.addStretch()
        audio_layout.addLayout(device_row)
        
        # 均衡器
        eq_row = QHBoxLayout()
        eq_row.addWidget(QLabel("均衡器"))
        eq_combo = QComboBox()
        eq_combo.addItems(["关闭", "流行", "古典", "爵士", "摇滚"])
        eq_row.addWidget(eq_combo)
        eq_row.addStretch()
        audio_layout.addLayout(eq_row)
        
        layout.addWidget(audio_frame)
        
        # 关于
        about_section = self._create_section("ℹ 关于")
        layout.addWidget(about_section)
        
        about_frame = self._create_option_frame()
        about_layout = QVBoxLayout(about_frame)
        
        about_text = QLabel("余音 v2.0\n专业的音乐播放器，兼具竹笛学习功能\n\n© 2024 余音团队")
        about_text.setStyleSheet(f"color: {p.text_secondary};")
        about_layout.addWidget(about_text)
        
        layout.addWidget(about_frame)
        
        layout.addStretch()
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def _create_section(self, title: str) -> QLabel:
        p = theme_manager.current_palette
        label = QLabel(title)
        label.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        label.setStyleSheet(f"color: {p.primary};")
        return label
    
    def _create_option_frame(self) -> QFrame:
        p = theme_manager.current_palette
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {p.panel_bg};
                border: 1px solid {p.border};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        return frame
    
    def _select_theme(self, name: str):
        theme_manager.set_theme(name)
        
        # 更新卡片选中状态
        for card_name, card in self.theme_cards:
            card.set_selected(card_name == name)