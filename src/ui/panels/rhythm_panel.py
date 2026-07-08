"""节奏训练面板"""
import math
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QComboBox, QSlider, QFrame,
                            QStackedWidget, QGridLayout)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush

from ..theme import theme_manager
from ...application.services.rhythm_service import (
    Metronome, RhythmCoach, rhythm_coach,
    BEAT_PATTERNS, RHYTHM_EXERCISES, BeatPattern
)


class MetronomeVisualizer(QWidget):
    """节拍器可视化组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self.setMaximumSize(250, 250)

        self.beat_count = 4
        self.current_beat = -1
        self.pattern = None

    def set_beat_count(self, count: int):
        self.beat_count = count
        self.update()

    def set_current_beat(self, beat: int):
        self.current_beat = beat
        self.update()

    def set_pattern(self, pattern: BeatPattern):
        self.pattern = pattern
        self.beat_count = len(pattern.accents)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        p = theme_manager.current_palette
        rect = self.rect()
        center_x = rect.width() // 2
        center_y = rect.height() // 2
        radius = min(rect.width(), rect.height()) // 2 - 20

        # 背景圆
        painter.setPen(QPen(QColor(p.border), 2))
        painter.setBrush(QColor(p.panel_bg))
        painter.drawEllipse(center_x - radius, center_y - radius,
                          radius * 2, radius * 2)

        # 绘制节拍点
        for i in range(self.beat_count):
            angle = 2 * math.pi * i / self.beat_count - math.pi / 2
            x = center_x + int(radius * 0.7 * math.cos(angle))
            y = center_y + int(radius * 0.7 * math.sin(angle))

            # 根据模式设置大小
            if self.pattern and i < len(self.pattern.accents):
                accent = self.pattern.accents[i]
                dot_radius = int(8 + accent * 12)
            else:
                dot_radius = 12 if i == 0 else 8

            # 当前拍高亮
            if i == self.current_beat % self.beat_count:
                painter.setPen(QPen(QColor(p.primary), 3))
                painter.setBrush(QColor(p.primary))
                dot_radius += 4
            else:
                painter.setPen(QPen(QColor(p.secondary), 2))
                painter.setBrush(QColor(p.secondary + "80"))

            painter.drawEllipse(x - dot_radius, y - dot_radius,
                              dot_radius * 2, dot_radius * 2)

        # 中心点
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(p.primary))
        painter.drawEllipse(center_x - 8, center_y - 8, 16, 16)

        painter.end()


class RhythmGameWidget(QWidget):
    """节奏游戏组件"""

    score_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(150)

        self.score = 0
        self.target_beat = -1
        self.user_hits = []
        self.is_active = False

        # 动画
        self.pulse = 0
        self.timer = QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self._animate)

    def start(self):
        self.is_active = True
        self.score = 0
        self.user_hits.clear()
        self.timer.start()

    def stop(self):
        self.is_active = False
        self.timer.stop()
        self.update()

    def register_hit(self):
        """注册用户点击"""
        if self.is_active:
            self.user_hits.append(self.target_beat)

    def on_beat(self, beat: int):
        """收到节拍"""
        self.target_beat = beat
        self.update()

    def _animate(self):
        self.pulse = (self.pulse + 0.1) % (2 * math.pi)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        p = theme_manager.current_palette
        rect = self.rect()

        # 背景
        painter.fillRect(rect, QColor(p.panel_bg))

        if not self.is_active:
            painter.setPen(QColor(p.text_secondary))
            painter.setFont(QFont("Microsoft YaHei", 14))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "点击开始练习")
            painter.end()
            return

        # 分数显示
        painter.setPen(QColor(p.primary))
        painter.setFont(QFont("Consolas", 24, QFont.Weight.Bold))
        painter.drawText(rect.adjusted(0, 20, 0, 0),
                        Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter,
                        f"分数: {self.score}")

        # 提示文字
        painter.setPen(QColor(p.text_secondary))
        painter.setFont(QFont("Microsoft YaHei", 12))
        painter.drawText(rect.adjusted(0, 60, 0, 0),
                        Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter,
                        "跟着节拍点击空格键")

        # 脉冲效果
        if self.target_beat >= 0:
            pulse_size = int(20 + 10 * math.sin(self.pulse))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(p.primary + "40"))
            painter.drawEllipse(rect.center(), pulse_size, pulse_size)

        painter.end()


class RhythmPanel(QWidget):
    """节奏训练面板"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self._init_ui()
        self._setup_connections()

    def _init_ui(self):
        p = theme_manager.current_palette

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 标题
        header = QHBoxLayout()
        title = QLabel("节奏训练")
        title.setFont(QFont("FangSong", 18, QFont.Weight.Bold))
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # 模式选择
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(10)

        mode_label = QLabel("模式:")
        mode_layout.addWidget(mode_label)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["自由练习", "跟练模式", "挑战模式"])
        self.mode_combo.currentTextChanged.connect(self._on_mode_changed)
        mode_layout.addWidget(self.mode_combo)

        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        # 主内容区
        content = QHBoxLayout()
        content.setSpacing(20)

        # 左侧：控制面板
        left_panel = QFrame()
        left_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {p.panel_bg};
                border: 1px solid {p.border};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)

        # BPM控制
        bpm_group = QFrame()
        bpm_group.setStyleSheet(f"""
            QFrame {{
                background-color: {p.surface};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        bpm_layout = QVBoxLayout(bpm_group)

        bpm_label = QLabel("BPM (速度)")
        bpm_label.setStyleSheet(f"color: {p.primary}; font-weight: bold;")
        bpm_layout.addWidget(bpm_label)

        bpm_slider_layout = QHBoxLayout()
        self.bpm_slider = QSlider(Qt.Orientation.Horizontal)
        self.bpm_slider.setRange(40, 240)
        self.bpm_slider.setValue(80)
        self.bpm_slider.valueChanged.connect(self._on_bpm_changed)
        bpm_slider_layout.addWidget(self.bpm_slider)

        self.bpm_label = QLabel("80")
        self.bpm_label.setFixedWidth(40)
        self.bpm_label.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        bpm_slider_layout.addWidget(self.bpm_label)

        bpm_layout.addLayout(bpm_slider_layout)

        # Tap按钮
        tap_layout = QHBoxLayout()
        self.tap_btn = QPushButton("TAP")
        self.tap_btn.setFixedHeight(40)
        self.tap_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {p.primary};
                color: {p.paper};
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {p.primary_light};
            }}
            QPushButton:pressed {{
                background-color: {p.primary_dark};
            }}
        """)
        self.tap_btn.clicked.connect(self._on_tap)
        tap_layout.addWidget(self.tap_btn)

        reset_tap_btn = QPushButton("重置")
        reset_tap_btn.clicked.connect(self._on_reset_tap)
        tap_layout.addWidget(reset_tap_btn)

        bpm_layout.addLayout(tap_layout)

        left_layout.addWidget(bpm_group)

        # 拍号选择
        time_sig_layout = QHBoxLayout()
        time_sig_label = QLabel("拍号:")
        time_sig_layout.addWidget(time_sig_label)

        self.time_sig_combo = QComboBox()
        self.time_sig_combo.addItems(["4/4", "3/4", "2/4", "6/8"])
        self.time_sig_combo.currentTextChanged.connect(self._on_time_sig_changed)
        time_sig_layout.addWidget(self.time_sig_combo)

        time_sig_layout.addStretch()
        left_layout.addLayout(time_sig_layout)

        # 节拍模式
        pattern_layout = QHBoxLayout()
        pattern_label = QLabel("模式:")
        pattern_layout.addWidget(pattern_label)

        self.pattern_combo = QComboBox()
        for key, pattern in BEAT_PATTERNS.items():
            self.pattern_combo.addItem(pattern.name, key)
        self.pattern_combo.currentTextChanged.connect(self._on_pattern_changed)
        pattern_layout.addWidget(self.pattern_combo)

        pattern_layout.addStretch()
        left_layout.addLayout(pattern_layout)

        # 控制按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.play_btn = QPushButton("开始")
        self.play_btn.setFixedHeight(50)
        self.play_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {p.success};
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {p.success}dd;
            }}
        """)
        self.play_btn.clicked.connect(self._toggle_play)
        btn_layout.addWidget(self.play_btn)

        left_layout.addLayout(btn_layout)

        left_layout.addStretch()

        content.addWidget(left_panel, 1)

        # 右侧：可视化
        right_panel = QFrame()
        right_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {p.panel_bg};
                border: 1px solid {p.border};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        right_layout = QVBoxLayout(right_panel)

        # 节拍可视化
        self.visualizer = MetronomeVisualizer()
        right_layout.addWidget(self.visualizer, alignment=Qt.AlignmentFlag.AlignCenter)

        # 节奏游戏
        self.game_widget = RhythmGameWidget()
        right_layout.addWidget(self.game_widget)

        content.addWidget(right_panel, 1)

        layout.addLayout(content, 1)

        # 底部统计
        stats_layout = QHBoxLayout()

        self.stats_label = QLabel("练习统计: 暂无数据")
        self.stats_label.setStyleSheet(f"color: {p.text_secondary};")
        stats_layout.addWidget(self.stats_label)

        stats_layout.addStretch()

        layout.addLayout(stats_layout)

    def _setup_connections(self):
        """设置信号连接"""
        self.visualizer.set_pattern(BEAT_PATTERNS["4/4_pop"])

    def _on_bpm_changed(self, value: int):
        """BPM改变"""
        self.bpm_label.setText(str(value))
        rhythm_coach.metronome.set_bpm(value)

    def _on_time_sig_changed(self, text: str):
        """拍号改变"""
        parts = text.split("/")
        if len(parts) == 2:
            numerator, denominator = int(parts[0]), int(parts[1])
            rhythm_coach.metronome.set_time_signature(numerator, denominator)
            self.visualizer.set_beat_count(numerator)

    def _on_pattern_changed(self, text: str):
        """模式改变"""
        index = self.pattern_combo.currentIndex()
        key = self.pattern_combo.itemData(index)
        if key and key in BEAT_PATTERNS:
            pattern = BEAT_PATTERNS[key]
            self.visualizer.set_pattern(pattern)
            rhythm_coach.set_pattern(pattern)

    def _on_mode_changed(self, text: str):
        """模式改变"""
        pass

    def _on_tap(self):
        """Tap检测"""
        bpm = rhythm_coach.metronome.tap()
        if bpm > 0:
            self.bpm_slider.setValue(bpm)
            self.bpm_label.setText(str(bpm))

    def _on_reset_tap(self):
        """重置Tap"""
        rhythm_coach.metronome.reset_tap()

    def _toggle_play(self):
        """切换播放"""
        if rhythm_coach.metronome.is_playing:
            rhythm_coach.stop()
            self.play_btn.setText("开始")
            self.play_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {theme_manager.current_palette.success};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 16px;
                }}
            """)
            self.visualizer.set_current_beat(-1)
        else:
            rhythm_coach.start(callback=self._on_beat)
            self.play_btn.setText("停止")
            self.play_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {theme_manager.current_palette.error};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 16px;
                }}
            """)
            self.game_widget.start()

    def _on_beat(self, beat: int, is_downbeat: bool):
        """收到节拍回调"""
        # 注意：这个回调在子线程中执行，需要跨线程更新UI
        self.visualizer.set_current_beat(beat)
        self.game_widget.on_beat(beat)

    def keyPressEvent(self, event):
        """按键事件"""
        if event.key() == Qt.Key.Key_Space:
            self.game_widget.register_hit()
        super().keyPressEvent(event)