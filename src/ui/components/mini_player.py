"""迷你播放器栏 - 底部控制条"""
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QFileDialog, QSlider)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ..theme import theme_manager
from ...infrastructure.audio.player import AudioPlayer
from ...shared.i18n import texts


class MiniPlayerBar(QWidget):
    """底部迷你播放器栏"""

    play_track = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.audio_player = AudioPlayer()
        self._is_playing = False
        self._current_volume = 80

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        p = theme_manager.current_palette

        self.setStyleSheet(f"""
            MiniPlayerBar {{
                background-color: {p.surface};
                border-top: 1px solid {p.border};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(20)

        # 左侧：曲目信息
        left_panel = QVBoxLayout()
        left_panel.setSpacing(5)

        self.title_label = QLabel(texts.PLAYER_NO_PLAY)
        self.title_label.setFont(QFont("FangSong", 14, QFont.Weight.Bold))
        left_panel.addWidget(self.title_label)

        self.artist_label = QLabel(texts.PLAYER_SELECT_SONG)
        self.artist_label.setStyleSheet(f"color: {p.text_secondary};")
        left_panel.addWidget(self.artist_label)

        layout.addLayout(left_panel, 1)

        # 中间：控制按钮
        controls = QHBoxLayout()
        controls.setSpacing(15)
        controls.setAlignment(Qt.AlignmentFlag.AlignCenter)

        prev_btn = QPushButton("◁◁")
        prev_btn.setFixedSize(36, 36)
        prev_btn.setStyleSheet(self._get_control_btn_style())
        controls.addWidget(prev_btn)

        self.play_btn = QPushButton("▷")
        self.play_btn.setFixedSize(50, 50)
        self.play_btn.setStyleSheet(self._get_play_btn_style())
        self.play_btn.clicked.connect(self._toggle_play)
        controls.addWidget(self.play_btn)

        next_btn = QPushButton("▷▷")
        next_btn.setFixedSize(36, 36)
        next_btn.setStyleSheet(self._get_control_btn_style())
        controls.addWidget(next_btn)

        layout.addLayout(controls)

        # 进度条
        progress_panel = QVBoxLayout()
        progress_panel.setSpacing(5)

        progress_row = QHBoxLayout()
        self.time_current = QLabel("00:00")
        self.time_current.setStyleSheet(f"color: {p.text_secondary}; font-family: Consolas; font-size: 11px;")
        progress_row.addWidget(self.time_current)

        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background-color: {p.border};
                height: 4px;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background-color: {p.primary};
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }}
            QSlider::sub-page:horizontal {{
                background-color: {p.primary};
                border-radius: 2px;
            }}
        """)
        self.progress_slider.sliderMoved.connect(self._seek)
        progress_row.addWidget(self.progress_slider, 1)

        self.time_total = QLabel("00:00")
        self.time_total.setStyleSheet(f"color: {p.text_secondary}; font-family: Consolas; font-size: 11px;")
        self.time_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        progress_row.addWidget(self.time_total)

        progress_panel.addLayout(progress_row)
        layout.addLayout(progress_panel, 2)

        # 右侧：音量控制
        volume_panel = QHBoxLayout()
        volume_panel.setSpacing(8)

        vol_icon = QLabel("音")
        vol_icon.setStyleSheet(f"color: {p.text_secondary}; font-size: 12px;")
        volume_panel.addWidget(vol_icon)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background-color: {p.border};
                height: 4px;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background-color: {p.primary};
                width: 10px;
                height: 10px;
                margin: -3px 0;
                border-radius: 5px;
            }}
            QSlider::sub-page:horizontal {{
                background-color: {p.primary};
                border-radius: 2px;
            }}
        """)
        self.volume_slider.valueChanged.connect(self._on_volume)
        volume_panel.addWidget(self.volume_slider)

        self.volume_label = QLabel("80%")
        self.volume_label.setStyleSheet(f"color: {p.text_secondary}; font-size: 11px;")
        self.volume_label.setFixedWidth(30)
        volume_panel.addWidget(self.volume_label)

        layout.addLayout(volume_panel)

    def _get_control_btn_style(self) -> str:
        p = theme_manager.current_palette
        return f"""
            QPushButton {{
                background-color: {p.surface};
                color: {p.text};
                border: 1px solid {p.border};
                border-radius: 18px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {p.primary};
                color: {p.paper};
                border-color: {p.primary};
            }}
        """

    def _get_play_btn_style(self) -> str:
        p = theme_manager.current_palette
        return f"""
            QPushButton {{
                background-color: {p.primary};
                color: {p.paper};
                border: none;
                border-radius: 25px;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: {p.primary_light};
            }}
        """

    def _connect_signals(self):
        self.audio_player.position_changed.connect(self._on_position_changed)
        self.audio_player.duration_changed.connect(self._on_duration_changed)
        self.audio_player.playback_finished.connect(self._on_finished)

    def _toggle_play(self):
        if self._is_playing:
            self.audio_player.pause()
            self.play_btn.setText("▷")
            self._is_playing = False
        else:
            self.audio_player.play()
            self.play_btn.setText("||")
            self._is_playing = True

    def load_track(self, file_path: str):
        """加载曲目"""
        self.audio_player.load_file(file_path)
        title = os.path.splitext(os.path.basename(file_path))[0]
        self.title_label.setText(title)
        self.artist_label.setText("本地音乐")

    def _on_position_changed(self, pos: float):
        dur = self.audio_player.get_duration()
        if dur > 0:
            self.progress_slider.blockSignals(True)
            self.progress_slider.setValue(int(pos))
            self.progress_slider.blockSignals(False)
            self.time_current.setText(self._fmt(pos))

    def _on_duration_changed(self, dur: float):
        self.progress_slider.setRange(0, int(dur))
        self.time_total.setText(self._fmt(dur))

    def _on_finished(self):
        self.play_btn.setText("▶")
        self._is_playing = False
        self.progress_slider.setValue(0)

    def _seek(self, pos: int):
        self.audio_player.set_position(pos * 1000)

    def _on_volume(self, val: int):
        self.audio_player.set_volume(val / 100.0)
        self.volume_label.setText(f"{val}%")

    def _fmt(self, s: float) -> str:
        m, sec = int(s // 60), int(s % 60)
        return f"{m:02d}:{sec:02d}"