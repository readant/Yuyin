"""音乐库面板"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QLineEdit, QListWidget, QListWidgetItem,
                            QPushButton, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from .base_panel import BasePanel
from ..theme import theme_manager
from ...application.services.music_service import music_library, Track
from ...shared.i18n import texts


class LibraryPanel(BasePanel):
    """音乐库面板"""

    play_track = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(texts.LIBRARY_TITLE, parent)
        self._init_content()

    def _init_content(self):
        p = theme_manager.current_palette

        # 搜索框
        search_frame = self.create_section_frame()
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(10, 5, 10, 5)

        self.search = QLineEdit()
        self.search.setPlaceholderText(texts.LIBRARY_SEARCH)
        self.search.textChanged.connect(self._on_search)
        search_layout.addWidget(self.search)

        scan_btn = QPushButton(texts.LIBRARY_IMPORT)
        scan_btn.clicked.connect(self._scan_directory)
        search_layout.addWidget(scan_btn)

        self.add_content(search_frame)

        # 分类标签
        tags_frame = self.create_section_frame()
        tags_layout = QHBoxLayout(tags_frame)
        tags_layout.setContentsMargins(10, 5, 10, 5)

        self.tag_buttons = []
        for tag in [texts.LIBRARY_ALL, texts.LIBRARY_FAVORITE, texts.LIBRARY_RECENT]:
            btn = QPushButton(tag)
            btn.setCheckable(True)
            if tag == texts.LIBRARY_ALL:
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, b=btn, t=tag: self._on_tag(b, t))
            tags_layout.addWidget(btn)
            self.tag_buttons.append(btn)

        tags_layout.addStretch()
        self.add_content(tags_frame)

        # 歌曲列表
        list_frame = self.create_section_frame()
        list_layout = QVBoxLayout(list_frame)

        self.track_list = QListWidget()
        self.track_list.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: none;
            }}
            QListWidget::item {{
                padding: 10px;
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
        list_layout.addWidget(self.track_list)

        self.status_label = QLabel("共 0 首歌曲")
        self.status_label.setStyleSheet(f"color: {p.text_secondary};")
        list_layout.addWidget(self.status_label)

        self.add_content(list_frame)

    def _load_demo_tracks(self):
        """加载示例曲目"""
        demo_tracks = [
            ("妆台秋思", "经典古曲"),
            ("姑苏行", "江先渭"),
            ("牧民新歌", "简广易"),
            ("扬鞭催马运粮忙", "魏显忠"),
            ("春到湘江", "宁保生"),
        ]

        for title, artist in demo_tracks:
            item = QListWidgetItem(f"{title} - {artist}")
            item.setData(Qt.ItemDataRole.UserRole, None)
            self.track_list.addItem(item)

        self.status_label.setText(f"共 {len(demo_tracks)} 首歌曲")

    def _on_search(self, text: str):
        for i in range(self.track_list.count()):
            item = self.track_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def _on_tag(self, btn: QPushButton, tag: str):
        for b in self.tag_buttons:
            b.setChecked(b == btn)

    def _on_play(self, item: QListWidgetItem):
        track = item.data(Qt.ItemDataRole.UserRole)
        if track:
            self.play_track.emit(track)

    def _scan_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择音乐文件夹")
        if dir_path:
            music_library.add_scan_directory(dir_path)
            count = music_library.scan()
            self._refresh_list()
            self.status_label.setText(f"共 {count} 首歌曲")

    def _refresh_list(self):
        self.track_list.clear()
        for track in music_library.tracks:
            item = QListWidgetItem(f"{track.title} - {track.artist}")
            item.setData(Qt.ItemDataRole.UserRole, track)
            self.track_list.addItem(item)
        self.status_label.setText(f"共 {music_library.count} 首歌曲")