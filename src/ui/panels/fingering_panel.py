"""指法查询面板"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QComboBox, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ..components.fingering import FingeringWidget, FingeringDisplay
from ..theme import theme_manager
from ...domain.models.notes import (get_fingering_map, get_all_notes_for_fingering,
                                   get_fingering_display, KEY_CONFIGS)
from ...application.services.zhudi_service import zhudi_service


class FingeringPanel(QWidget):
    """指法速查"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.current_key = "D"
        self.current_fingering = "5"
        self.current_note = "1"
        
        self._init_ui()
    
    def _init_ui(self):
        p = theme_manager.current_palette
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(20)
        
        # 标题
        title = QLabel("🎯 指法速查")
        title.setFont(QFont("FangSong", 20, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 选择区域
        select_frame = QFrame()
        select_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {p.panel_bg};
                border: 1px solid {p.border};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        select_layout = QHBoxLayout(select_frame)
        select_layout.setSpacing(30)
        
        # 调性
        key_group = QVBoxLayout()
        key_group.addWidget(QLabel("调性"))
        self.key_combo = QComboBox()
        self.key_combo.addItems(["D", "G", "C", "F", "E"])
        self.key_combo.currentTextChanged.connect(self._on_change)
        key_group.addWidget(self.key_combo)
        select_layout.addLayout(key_group)
        
        # 指法类型
        fing_group = QVBoxLayout()
        fing_group.addWidget(QLabel("指法"))
        self.fing_combo = QComboBox()
        self.fing_combo.addItems(["5", "1", "2"])
        self.fing_combo.currentTextChanged.connect(self._on_change)
        fing_group.addWidget(self.fing_combo)
        select_layout.addLayout(fing_group)
        
        # 音符
        note_group = QVBoxLayout()
        note_group.addWidget(QLabel("音符"))
        self.note_combo = QComboBox()
        self.note_combo.addItems(get_all_notes_for_fingering("5"))
        self.note_combo.currentTextChanged.connect(self._on_change)
        note_group.addWidget(self.note_combo)
        select_layout.addLayout(note_group)
        
        select_layout.addStretch()
        layout.addWidget(select_frame)
        
        # 指法显示区域
        display_frame = QFrame()
        display_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {p.panel_bg};
                border: 1px solid {p.border};
                border-radius: 10px;
                padding: 20px;
            }}
        """)
        display_layout = QHBoxLayout(display_frame)
        display_layout.setSpacing(40)
        
        # 左侧：孔位图
        left_panel = QVBoxLayout()
        left_panel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        left_panel.addWidget(QLabel("指法图示"), alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.fingering_widget = FingeringWidget()
        self.fingering_widget.setMinimumSize(80, 200)
        left_panel.addWidget(self.fingering_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.fingering_display = FingeringDisplay()
        left_panel.addWidget(self.fingering_display, alignment=Qt.AlignmentFlag.AlignCenter)
        
        display_layout.addLayout(left_panel)
        
        # 右侧：各种指法对照
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)
        
        right_panel.addWidget(QLabel("各指法对照"))
        
        # 筒音作5
        fing5_frame = self._create_fingering_card("筒音作5", "5")
        right_panel.addWidget(fing5_frame)
        
        # 筒音作1
        fing1_frame = self._create_fingering_card("筒音作1", "1")
        right_panel.addWidget(fing1_frame)
        
        # 筒音作2
        fing2_frame = self._create_fingering_card("筒音作2", "2")
        right_panel.addWidget(fing2_frame)
        
        right_panel.addStretch()
        display_layout.addLayout(right_panel, 1)
        
        layout.addWidget(display_frame, 1)
    
    def _create_fingering_card(self, title: str, fingering_type: str) -> QFrame:
        p = theme_manager.current_palette
        
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {p.surface};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        
        layout = QHBoxLayout(frame)
        layout.setSpacing(15)
        
        label = QLabel(title)
        label.setFixedWidth(70)
        label.setStyleSheet(f"color: {p.primary}; font-weight: bold;")
        layout.addWidget(label)
        
        self.fingering_texts = getattr(self, 'fingering_texts', {})
        text_label = QLabel("●●●○○○")
        text_label.setFont(QFont("Consolas", 14))
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fingering_texts[fingering_type] = text_label
        layout.addWidget(text_label, 1)
        
        return frame
    
    def _on_change(self):
        self.current_key = self.key_combo.currentText()
        self.current_fingering = self.fing_combo.currentText()
        self.current_note = self.note_combo.currentText()

        # 更新竹笛学习服务
        zhudi_service.set_key(self.current_key)
        zhudi_service.set_fingering(self.current_fingering)

        # 更新指法显示
        fingering_map = get_fingering_map(self.current_fingering)
        if self.current_note in fingering_map:
            fingering = fingering_map[self.current_note]
            self.fingering_widget.set_fingering(fingering)
            self.fingering_display.set_fingering(fingering)

        # 更新各指法对照
        for ftype, label in self.fingering_texts.items():
            map_data = get_fingering_map(ftype)
            if self.current_note in map_data:
                label.setText(get_fingering_display(map_data[self.current_note]))