"""指法查询面板"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QComboBox, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .base_panel import BasePanel
from ..components.fingering import FingeringWidget, FingeringDisplay
from ..theme import theme_manager
from ...domain.models.notes import (get_fingering_map, get_all_notes_for_fingering,
                                   get_fingering_display, KEY_CONFIGS)
from ...application.services.zhudi_service import zhudi_service


class FingeringPanel(BasePanel):
    """指法查询面板"""

    def __init__(self, parent=None):
        super().__init__("指法速查", parent)
        self.current_key = "D"
        self.current_fingering = "5"
        self.current_note = "1"
        self._init_content()

    def _init_content(self):
        p = theme_manager.current_palette

        # 选择区域
        select_frame = self.create_section_frame()
        select_layout = QHBoxLayout(select_frame)
        select_layout.setSpacing(30)

        # 调性
        key_group = QVBoxLayout()
        key_group.addWidget(self.create_section_title("调性"))
        self.key_combo = QComboBox()
        self.key_combo.addItems(["D", "G", "C", "F", "E"])
        self.key_combo.currentTextChanged.connect(self._on_change)
        key_group.addWidget(self.key_combo)
        select_layout.addLayout(key_group)

        # 指法类型
        fing_group = QVBoxLayout()
        fing_group.addWidget(self.create_section_title("指法"))
        self.fing_combo = QComboBox()
        self.fing_combo.addItems(["5", "1", "2"])
        self.fing_combo.currentTextChanged.connect(self._on_change)
        fing_group.addWidget(self.fing_combo)
        select_layout.addLayout(fing_group)

        # 音符
        note_group = QVBoxLayout()
        note_group.addWidget(self.create_section_title("音符"))
        self.note_combo = QComboBox()
        self.note_combo.addItems(get_all_notes_for_fingering("5"))
        self.note_combo.currentTextChanged.connect(self._on_change)
        note_group.addWidget(self.note_combo)
        select_layout.addLayout(note_group)

        select_layout.addStretch()
        self.add_content(select_frame)

        # 指法显示区域
        display_frame = self.create_section_frame()
        display_layout = QHBoxLayout(display_frame)
        display_layout.setSpacing(30)

        # 左侧：孔位图
        left_panel = QVBoxLayout()
        left_panel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        left_panel.addWidget(self.create_section_title("指法图示"), alignment=Qt.AlignmentFlag.AlignCenter)

        self.fingering_widget = FingeringWidget()
        self.fingering_widget.setMinimumSize(80, 200)
        left_panel.addWidget(self.fingering_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        self.fingering_display = FingeringDisplay()
        left_panel.addWidget(self.fingering_display, alignment=Qt.AlignmentFlag.AlignCenter)

        display_layout.addLayout(left_panel)

        # 右侧：各种指法对照
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)

        right_panel.addWidget(self.create_section_title("各指法对照"))

        self.fingering_texts = {}
        for fing_type, label_text in [("5", "筒音作5"), ("1", "筒音作1"), ("2", "筒音作2")]:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {p.surface};
                    border-radius: 6px;
                    padding: 8px;
                }}
            """)
            card_layout = QHBoxLayout(card)
            card_layout.setSpacing(10)

            type_label = QLabel(label_text)
            type_label.setFixedWidth(70)
            type_label.setStyleSheet(f"color: {p.primary}; font-weight: bold;")
            card_layout.addWidget(type_label)

            text_label = QLabel("●●●○○○")
            text_label.setFont(QFont("Consolas", 14))
            text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.fingering_texts[fing_type] = text_label
            card_layout.addWidget(text_label, 1)

            right_panel.addWidget(card)

        right_panel.addStretch()
        display_layout.addLayout(right_panel, 1)

        self.add_content(display_frame)

    def _on_change(self):
        self.current_key = self.key_combo.currentText()
        self.current_fingering = self.fing_combo.currentText()
        self.current_note = self.note_combo.currentText()

        zhudi_service.set_key(self.current_key)
        zhudi_service.set_fingering(self.current_fingering)

        fingering_map = get_fingering_map(self.current_fingering)
        if self.current_note in fingering_map:
            fingering = fingering_map[self.current_note]
            self.fingering_widget.set_fingering(fingering)
            self.fingering_display.set_fingering(fingering)

        for ftype, label in self.fingering_texts.items():
            map_data = get_fingering_map(ftype)
            if self.current_note in map_data:
                label.setText(get_fingering_display(map_data[self.current_note]))