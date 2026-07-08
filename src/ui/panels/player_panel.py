"""播放器面板"""
import os
import random
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QFileDialog, QStackedWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ..components.vinyl import VinylWidget
from ..components.spectrum import SpectrumWidget
from ..components.progress import ProgressWidget
from ..components.lyrics import LyricsWidget
from ..components.chinese_controls import QingButton, ScrollProgressBar, PluckVolumeSlider
from ..theme import theme_manager
from ...infrastructure.audio.player import AudioPlayer
from ...infrastructure.audio.device_detector import audio_device_detector
from ...application.services.music_service import Track
from ...application.services.fade_service import fade_controller
from ...shared.i18n import texts


class ControlButton(QPushButton):
    """控制按钮"""

    def __init__(self, icon: str, size: int = 45, parent=None):
        super().__init__(icon, parent)
        self.setFixedSize(size, size)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_style(False)

    def _update_style(self, is_play: bool):
        p = theme_manager.current_palette
        if is_play:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                        stop:0 {p.primary}, stop:1 {p.primary_dark});
                    color: {p.paper};
                    border: none;
                    border-radius: {self.width()//2}px;
                    font-size: 22px;
                }}
                QPushButton:hover {{
                    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                        stop:0 {p.primary_light}, stop:1 {p.primary});
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {p.surface};
                    color: {p.text};
                    border: none;
                    border-radius: {self.width()//2}px;
                    font-size: 16px;
                }}
                QPushButton:hover {{
                    background-color: {p.primary};
                    color: {p.paper};
                }}
            """)


class PlayerPanel(QWidget):
    """播放器面板"""

    learning_mode_changed = pyqtSignal(bool)
    note_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.audio_player = AudioPlayer()
        self._learning_enabled = False
        self._current_track = None
        self._is_playing = False

        self._connect_signals()
        self._init_ui()

    def _connect_signals(self):
        self.audio_player.position_changed.connect(self._on_position_changed)
        self.audio_player.duration_changed.connect(self._on_duration_changed)
        self.audio_player.playback_finished.connect(self._on_finished)

    def _init_ui(self):
        p = theme_manager.current_palette

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 背景
        bg = QWidget()
        bg.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {p.background}, stop:0.5 {p.surface}, stop:1 {p.background});
            }}
        """)
        bg_layout = QVBoxLayout(bg)
        bg_layout.setContentsMargins(30, 20, 30, 20)
        bg_layout.setSpacing(15)

        # 顶部栏
        top_bar = QHBoxLayout()

        self.learning_btn = QPushButton("🎯 学习模式")
        self.learning_btn.setCheckable(True)
        self.learning_btn.setFixedHeight(32)
        self.learning_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.learning_btn.clicked.connect(self._toggle_learning)
        self._update_learning_btn(False)
        top_bar.addWidget(self.learning_btn)

        top_bar.addStretch()

        # 音频设备状态
        self.device_label = QLabel()
        self.device_label.setStyleSheet(f"color: {p.text_secondary}; background: transparent;")
        self._update_device_display()
        audio_device_detector.device_changed.connect(lambda: self._update_device_display())
        top_bar.addWidget(self.device_label)

        # 视图切换按钮
        self.view_toggle = QPushButton("📜 歌词")
        self.view_toggle.setCheckable(True)
        self.view_toggle.setFixedHeight(32)
        self.view_toggle.clicked.connect(self._toggle_view)
        top_bar.addWidget(self.view_toggle)

        open_btn = QPushButton("📂 打开")
        open_btn.clicked.connect(self._open_file)
        top_bar.addWidget(open_btn)

        bg_layout.addLayout(top_bar)

        # 主内容区
        content = QHBoxLayout()
        content.setSpacing(30)

        # 左侧：唱片 + 歌词切换
        left_container = QStackedWidget()

        # 唱片视图
        cover = QWidget()
        cover.setStyleSheet("background: transparent;")
        cover_layout = QVBoxLayout(cover)
        cover_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vinyl = VinylWidget()
        cover_layout.addWidget(self.vinyl)
        left_container.addWidget(cover)

        # 歌词视图
        self.lyrics_widget = LyricsWidget()
        left_container.addWidget(self.lyrics_widget)

        left_container.setCurrentIndex(0)
        self.left_container = left_container

        content.addWidget(left_container, 1)

        # 右侧控制
        right = QVBoxLayout()
        right.setSpacing(12)
        right.setContentsMargins(0, 20, 0, 0)

        # 曲目信息
        self.title_label = QLabel(texts.PLAYER_NO_PLAY)
        self.title_label.setFont(QFont("FangSong", 24, QFont.Weight.Bold))
        self.title_label.setStyleSheet(f"color: {p.text}; background: transparent;")
        right.addWidget(self.title_label)

        self.artist_label = QLabel(texts.PLAYER_SELECT_SONG)
        self.artist_label.setStyleSheet(f"color: {p.text_secondary}; background: transparent;")
        right.addWidget(self.artist_label)

        right.addSpacing(5)

        # 频谱
        spec_container = QWidget()
        spec_container.setStyleSheet("QWidget { background: rgba(0,0,0,0.1); border-radius: 10px; }")
        spec_layout = QVBoxLayout(spec_container)
        spec_layout.setContentsMargins(10, 5, 10, 5)
        self.spectrum = SpectrumWidget()
        spec_layout.addWidget(self.spectrum)
        right.addWidget(spec_container)

        # 进度条
        # 卷轴进度条
        self.progress = ScrollProgressBar()
        self.progress.value_changed.connect(self._seek)
        right.addWidget(self.progress)

        # 时间显示
        time_layout = QHBoxLayout()
        self.time_current = QLabel("00:00")
        self.time_current.setStyleSheet(f"color: {p.text_secondary}; font-family: Consolas; font-size: 11px; background: transparent;")
        time_layout.addWidget(self.time_current)

        time_layout.addStretch()

        self.time_total = QLabel("00:00")
        self.time_total.setStyleSheet(f"color: {p.text_secondary}; font-family: Consolas; font-size: 11px; background: transparent;")
        time_layout.addWidget(self.time_total)

        right.addLayout(time_layout)

        # 控制按钮
        controls = QHBoxLayout()
        controls.setSpacing(15)
        controls.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.prev_btn = ControlButton("⏮")
        self.prev_btn.clicked.connect(self._prev_track)
        controls.addWidget(self.prev_btn)

        self.play_btn = QingButton()
        self.play_btn.clicked.connect(self._toggle_play)
        controls.addWidget(self.play_btn)

        self.next_btn = ControlButton("⏭")
        self.next_btn.clicked.connect(self._next_track)
        controls.addWidget(self.next_btn)

        right.addLayout(controls)

        # 拨弦音量滑块
        vol_layout = QHBoxLayout()
        vol_layout.setSpacing(10)
        vol_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        vol_icon = QLabel("音量")
        vol_icon.setStyleSheet(f"color: {p.text_secondary}; background: transparent;")
        vol_layout.addWidget(vol_icon)

        self.volume_slider = PluckVolumeSlider()
        self.volume_slider.value_changed.connect(self._on_volume)
        vol_layout.addWidget(self.volume_slider)

        right.addLayout(vol_layout)
        right.addStretch()

        content.addLayout(right, 1)

        bg_layout.addLayout(content, 1)

        layout.addWidget(bg)

    def _update_learning_btn(self, active: bool):
        p = theme_manager.current_palette
        if active:
            self.learning_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {p.primary};
                    color: {p.paper};
                    border: none;
                    border-radius: 16px;
                    padding: 5px 15px;
                    font-weight: bold;
                }}
            """)
        else:
            self.learning_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {p.text_secondary};
                    border: 1px solid {p.border};
                    border-radius: 16px;
                    padding: 5px 15px;
                }}
                QPushButton:hover {{
                    border-color: {p.primary};
                    color: {p.primary};
                }}
            """)

    def _update_device_display(self):
        """更新音频设备显示"""
        icon = audio_device_detector.get_device_icon()
        type_name = audio_device_detector.get_device_type_name()
        device_name = audio_device_detector.current_device.name if audio_device_detector.current_device else ""
        self.device_label.setText(f"{icon} {type_name}: {device_name}")

    def _toggle_learning(self):
        self._learning_enabled = self.learning_btn.isChecked()
        self._update_learning_btn(self._learning_enabled)
        self.learning_mode_changed.emit(self._learning_enabled)

    def _toggle_view(self):
        """切换唱片/歌词视图"""
        is_lyrics = self.view_toggle.isChecked()
        self.left_container.setCurrentIndex(1 if is_lyrics else 0)
        self.view_toggle.setText("💿 唱片" if is_lyrics else "📜 歌词")

    def _open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开音频", "",
            "音频文件 (*.wav *.mp3 *.flac *.ogg);;所有文件 (*.*)"
        )
        if file_path:
            self.load_track(file_path)

    def load_track(self, file_path: str, title: str = None, artist: str = None):
        """加载曲目"""
        self.audio_player.load_file(file_path)

        if not title:
            title = os.path.splitext(os.path.basename(file_path))[0]
        if not artist:
            artist = "本地音乐"

        self.title_label.setText(title)
        self.artist_label.setText(artist)

        # 尝试加载歌词
        lrc_path = os.path.splitext(file_path)[0] + '.lrc'
        if os.path.exists(lrc_path):
            self.lyrics_widget.load_lyrics(lrc_path)
        else:
            self.lyrics_widget.clear()

    def load_track_object(self, track: Track):
        """加载Track对象"""
        self._current_track = track
        self.load_track(track.file_path, track.title, track.artist)

    def _toggle_play(self):
        if self._is_playing:
            # 暂停
            self.audio_player.pause()
            self.play_btn.setText("▶")
            self.vinyl.set_playing(False)
            self.spectrum.set_playing(False)
            self._is_playing = False
        else:
            # 播放
            self.audio_player.play()
            # 设置初始音量
            self.audio_player.set_volume(self.volume_slider._value / 100.0)
            self.play_btn.setText("⏸")
            self.vinyl.set_playing(True)
            self.spectrum.set_playing(True)
            self._is_playing = True

    def _prev_track(self):
        """上一首"""
        # TODO: 从播放列表获取
        pass

    def _next_track(self):
        """下一首"""
        # TODO: 从播放列表获取
        pass

    def _on_position_changed(self, pos: float):
        dur = self.audio_player.get_duration()
        if dur > 0:
            self.progress.set_value(int(pos))
            self.time_current.setText(self._fmt(pos))

            bars = [random.randint(10, 80) for _ in range(32)]
            self.spectrum.set_bars(bars)

            # 更新歌词
            self.lyrics_widget.update_position(pos)

            if self._learning_enabled and random.random() > 0.7:
                notes = ['1', '2', '3', '4', '5', '6', '7']
                self.note_changed.emit(random.choice(notes))

    def _on_duration_changed(self, dur: float):
        self.progress.set_range(int(dur))
        self.time_total.setText(self._fmt(dur))

    def _on_finished(self):
        self.play_btn.setText("▶")
        self.vinyl.set_playing(False)
        self.spectrum.set_playing(False)
        self.progress.set_value(0)
        self._is_playing = False

    def _seek(self, pos: int):
        self.audio_player.set_position(pos * 1000)

    def _on_volume(self, val: int):
        self.audio_player.set_volume(val / 100.0)

    def _fmt(self, s: float) -> str:
        m, sec = int(s // 60), int(s % 60)
        return f"{m:02d}:{sec:02d}"