"""本地音乐库面板"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QLineEdit, QListWidget, QListWidgetItem,
                            QPushButton, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ..theme import theme_manager
from ...services.music_service import music_library, Track


class LibraryPanel(QWidget):
    """本地音乐库"""

    play_track = pyqtSignal(object)  # 发送Track对象

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._load_demo_tracks()

    def _init_ui(self):
        p = theme_manager.current_palette

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 标题
        header = QHBoxLayout()

        title = QLabel("📚 本地音乐库")
        title.setFont(QFont("FangSong", 18, QFont.Weight.Bold))
        header.addWidget(title)

        header.addStretch()

        # 扫描按钮
        scan_btn = QPushButton("📂 添加文件夹")
        scan_btn.clicked.connect(self._scan_directory)
        header.addWidget(scan_btn)

        layout.addLayout(header)

        # 搜索框
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 搜索歌曲、艺术家...")
        self.search.textChanged.connect(self._on_search)
        layout.addWidget(self.search)

        # 分类标签
        tags_layout = QHBoxLayout()
        tags_layout.setSpacing(8)

        self.tag_buttons = []
        for tag in ["全部", "收藏", "最近播放"]:
            btn = QPushButton(tag)
            btn.setCheckable(True)
            if tag == "全部":
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, b=btn, t=tag: self._on_tag(b, t))
            tags_layout.addWidget(btn)
            self.tag_buttons.append(btn)

        tags_layout.addStretch()
        layout.addLayout(tags_layout)

        # 歌曲列表
        self.track_list = QListWidget()
        self.track_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {p.panel_bg};
                border: 1px solid {p.border};
                border-radius: 8px;
                padding: 5px;
            }}
            QListWidget::item {{
                padding: 12px;
                border-radius: 6px;
                margin: 2px;
            }}
            QListWidget::item:selected {{
                background-color: {p.primary}30;
            }}
            QListWidget::item:hover {{
                background-color: {p.surface};
            }}
        """)
        self.track_list.itemDoubleClicked.connect(self._on_play)
        layout.addWidget(self.track_list, 1)

        # 底部统计
        stats_layout = QHBoxLayout()

        self.status_label = QLabel("共 0 首歌曲")
        self.status_label.setStyleSheet(f"color: {p.text_secondary};")
        stats_layout.addWidget(self.status_label)

        stats_layout.addStretch()

        # 导入本地文件按钮
        import_btn = QPushButton("🎵 导入文件")
        import_btn.clicked.connect(self._import_files)
        stats_layout.addWidget(import_btn)

        layout.addLayout(stats_layout)

    def _scan_directory(self):
        """扫描文件夹"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择音乐文件夹")
        if dir_path:
            music_library.add_scan_directory(dir_path)

            def on_progress(file_path, current, total):
                self.status_label.setText(f"扫描中... {current}/{total}")

            count = music_library.scan(callback=on_progress)
            self._refresh_list()
            self.status_label.setText(f"共 {count} 首歌曲")
            QMessageBox.information(self, "扫描完成", f"找到 {count} 首歌曲")

    def _import_files(self):
        """导入文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择音乐文件", "",
            "音频文件 (*.wav *.mp3 *.flac *.ogg *.m4a);;所有文件 (*.*)"
        )

        if files:
            for file_path in files:
                music_library.add_scan_directory(os.path.dirname(file_path))

            count = music_library.scan()
            self._refresh_list()
            self.status_label.setText(f"共 {count} 首歌曲")

    def _refresh_list(self):
        """刷新列表"""
        self.track_list.clear()

        for track in music_library.tracks:
            item = QListWidgetItem()
            item.setText(f"🎵  {track.title}  —  {track.artist}")
            item.setData(Qt.ItemDataRole.UserRole, track)
            self.track_list.addItem(item)

    def _load_demo_tracks(self):
        """加载示例曲目"""
        demo_tracks = [
            ("妆台秋思", "经典古曲"),
            ("姑苏行", "江先渭"),
            ("牧民新歌", "简广易"),
            ("扬鞭催马运粮忙", "魏显忠"),
            ("春到湘江", "宁保生"),
            ("帕米尔的春天", "李大同"),
            ("荫中鸟", "刘管乐"),
            ("小放牛", "陆春龄"),
        ]

        for title, artist in demo_tracks:
            item = QListWidgetItem(f"🎵  {title}  —  {artist}")
            item.setData(Qt.ItemDataRole.UserRole, None)
            self.track_list.addItem(item)

        self.status_label.setText(f"共 {len(demo_tracks)} 首歌曲（示例）")

    def _on_search(self, text: str):
        """搜索"""
        for i in range(self.track_list.count()):
            item = self.track_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def _on_tag(self, btn: QPushButton, tag: str):
        """标签切换"""
        for b in self.tag_buttons:
            b.setChecked(b == btn)

    def _on_play(self, item: QListWidgetItem):
        """双击播放"""
        track = item.data(Qt.ItemDataRole.UserRole)
        if track:
            self.play_track.emit(track)