"""本地音乐库面板"""
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QLineEdit, QListWidget, QListWidgetItem,
                            QPushButton, QFrame, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ..theme import theme_manager
from ...database.models import DatabaseManager


class LibraryPanel(QWidget):
    """本地音乐库"""
    
    play_file = pyqtSignal(str)
    
    def __init__(self, db: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db = db
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
        scan_btn = QPushButton("扫描文件夹")
        scan_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {p.primary};
                color: {p.paper};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {p.primary_dark};
            }}
        """)
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
        
        for tag in ["全部", "收藏", "最近播放", "本地"]:
            btn = QPushButton(tag)
            btn.setCheckable(True)
            if tag == "全部":
                btn.setChecked(True)
            btn.setStyleSheet(self._get_tag_style(btn.isChecked()))
            btn.clicked.connect(lambda checked, b=btn, t=tag: self._on_tag(b, t))
            tags_layout.addWidget(btn)
        
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
        self.status_label = QLabel("共 0 首歌曲")
        self.status_label.setStyleSheet(f"color: {p.text_secondary};")
        layout.addWidget(self.status_label)
    
    def _get_tag_style(self, active: bool) -> str:
        p = theme_manager.current_palette
        if active:
            return f"""
                QPushButton {{
                    background-color: {p.primary};
                    color: {p.paper};
                    border: none;
                    border-radius: 15px;
                    padding: 6px 16px;
                    font-weight: bold;
                }}
            """
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {p.text_secondary};
                border: 1px solid {p.border};
                border-radius: 15px;
                padding: 6px 16px;
            }}
            QPushButton:hover {{
                border-color: {p.primary};
                color: {p.primary};
            }}
        """
    
    def _on_tag(self, btn: QPushButton, tag: str):
        for i in range(self.track_list.count()):
            item = self.track_list.item(i)
            # 简单过滤逻辑
            if tag == "全部":
                item.setHidden(False)
    
    def _on_search(self, text: str):
        for i in range(self.track_list.count()):
            item = self.track_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())
    
    def _on_play(self, item: QListWidgetItem):
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if file_path and os.path.exists(file_path):
            self.play_file.emit(file_path)
    
    def _load_demo_tracks(self):
        """加载示例曲目"""
        demo_tracks = [
            ("妆台秋思", "经典古曲", "D调"),
            ("姑苏行", "江先渭", "G调"),
            ("牧民新歌", "简广易", "D调"),
            ("扬鞭催马运粮忙", "魏显忠", "D调"),
            ("春到湘江", "宁保生", "A调"),
            ("帕米尔的春天", "李大同", "D调"),
            ("荫中鸟", "刘管乐", "D调"),
            ("小放牛", "陆春龄", "G调"),
        ]
        
        for title, artist, key in demo_tracks:
            item = QListWidgetItem(f"🎵  {title}  —  {artist}  [{key}]")
            item.setData(Qt.ItemDataRole.UserRole, None)
            self.track_list.addItem(item)
        
        self.status_label.setText(f"共 {len(demo_tracks)} 首歌曲")