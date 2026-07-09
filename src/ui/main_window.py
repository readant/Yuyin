"""主窗口 - 竹笛学习助手"""
import math
import random
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QStackedWidget, QLabel, QFrame, QSplitter,
                            QToolBar, QStatusBar, QMenu, QMenuBar)
from PyQt6.QtCore import Qt, QSettings, QTimer, QSize
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QBrush, QFont, QIcon, QAction

from .panels.player_panel import PlayerPanel
from .panels.library_panel import LibraryPanel
from .panels.fingering_panel import FingeringPanel
from .panels.settings_panel import SettingsPanel
from .panels.lyrics_editor_panel import LyricsEditorPanel
from .panels.rhythm_panel import RhythmPanel
from .navigation.nav_button import NavButton
from .components.transitions import TransitionManager
from .theme import theme_manager
from ..domain.models.database import DatabaseManager
from ..shared.i18n import texts


class MainWindow(QMainWindow):
    """主窗口 - 竹笛学习助手"""

    def __init__(self):
        super().__init__()

        self.db = DatabaseManager()
        self.settings = QSettings("Yuyin", "MainWindow")

        # 云纹动画
        self.clouds = []
        self._init_clouds()

        self._init_ui()
        self._connect_signals()
        self._restore_layout()

        theme_manager.apply_theme()

        # 启动云纹动画
        self.cloud_timer = QTimer()
        self.cloud_timer.setInterval(33)
        self.cloud_timer.timeout.connect(self._update_clouds)
        self.cloud_timer.start()

    def _init_clouds(self):
        """初始化云纹"""
        for _ in range(6):
            self.clouds.append({
                'x': random.uniform(-100, 1200),
                'y': random.uniform(0, 800),
                'size': random.uniform(100, 250),
                'speed': random.uniform(0.15, 0.5),
                'opacity': random.uniform(0.02, 0.06),
                'phase': random.uniform(0, 2 * math.pi)
            })

    def _update_clouds(self):
        """更新云纹位置"""
        for cloud in self.clouds:
            cloud['x'] += cloud['speed']
            cloud['phase'] += 0.02
            cloud['y'] += math.sin(cloud['phase']) * 0.2

            if cloud['x'] > self.width() + cloud['size']:
                cloud['x'] = -cloud['size']
                cloud['y'] = random.uniform(0, self.height())

        self.update()

    def paintEvent(self, event):
        """绘制动态背景"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        p = theme_manager.current_palette
        rect = self.rect()

        # 绘制渐变背景
        gradient = QLinearGradient(0, 0, rect.width(), rect.height())
        gradient.setColorAt(0, QColor(p.background))
        gradient.setColorAt(0.5, QColor(p.surface))
        gradient.setColorAt(1, QColor(p.background))
        painter.fillRect(rect, gradient)

        # 绘制云纹
        for cloud in self.clouds:
            self._draw_cloud(painter, cloud, p)

        painter.end()

    def _draw_cloud(self, painter, cloud, palette):
        """绘制单个云纹"""
        gradient = QLinearGradient(
            cloud['x'] - cloud['size'] / 2, cloud['y'],
            cloud['x'] + cloud['size'] / 2, cloud['y']
        )

        cloud_color = QColor(palette.secondary)
        cloud_color.setAlpha(int(cloud['opacity'] * 255))

        edge_color = QColor(cloud_color)
        edge_color.setAlpha(0)

        gradient.setColorAt(0, edge_color)
        gradient.setColorAt(0.3, cloud_color)
        gradient.setColorAt(0.5, cloud_color)
        gradient.setColorAt(0.7, cloud_color)
        gradient.setColorAt(1, edge_color)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(
            int(cloud['x']), int(cloud['y']),
            int(cloud['size']), int(cloud['size'] / 2)
        )

    def _init_ui(self):
        """初始化界面"""
        self.setWindowTitle("余音 - 竹笛学习助手")
        self.setMinimumSize(1200, 750)

        # 创建中心部件
        central = QWidget()
        central.setStyleSheet("background: transparent;")
        self.setCentralWidget(central)

        # 主布局
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 顶部标题栏
        self._create_title_bar(main_layout)

        # 中间内容区（使用分割器）
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        content_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: rgba(128,128,128,0.2);
                width: 1px;
            }
        """)

        # 左侧导航面板
        self.nav_panel = self._create_nav_panel()
        content_splitter.addWidget(self.nav_panel)

        # 中央内容区
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background: transparent;")
        content_splitter.addWidget(self.content_stack)

        # 右侧信息面板
        self.info_panel = self._create_info_panel()
        content_splitter.addWidget(self.info_panel)

        # 设置分割比例
        content_splitter.setSizes([200, 700, 250])

        main_layout.addWidget(content_splitter, 1)

        # 底部播放器栏
        self.player_bar = PlayerPanel()
        self.player_bar.setFixedHeight(120)
        main_layout.addWidget(self.player_bar)

        # 初始化页面
        self._init_pages()

        # 状态栏
        self.statusBar().showMessage("就绪")

    def _create_title_bar(self, parent_layout):
        """创建顶部标题栏"""
        p = theme_manager.current_palette

        title_bar = QFrame()
        title_bar.setFixedHeight(50)
        title_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {p.surface};
                border-bottom: 1px solid {p.border};
            }}
        """)

        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(20, 0, 20, 0)

        # 应用标题
        app_title = QLabel("余音")
        app_title.setFont(QFont("FangSong", 18, QFont.Weight.Bold))
        app_title.setStyleSheet(f"color: {p.primary};")
        layout.addWidget(app_title)

        # 副标题
        subtitle = QLabel("竹笛学习助手")
        subtitle.setStyleSheet(f"color: {p.text_secondary};")
        layout.addWidget(subtitle)

        layout.addStretch()

        # 搜索框
        search_frame = QFrame()
        search_frame.setFixedWidth(250)
        search_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {p.panel_bg};
                border: 1px solid {p.border};
                border-radius: 15px;
            }}
        """)
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(10, 5, 10, 5)

        search_icon = QLabel("🔍")
        search_layout.addWidget(search_icon)

        search_input = QLabel("寻曲...")
        search_input.setStyleSheet(f"color: {p.text_secondary};")
        search_layout.addWidget(search_input)

        layout.addWidget(search_frame)

        # 设置按钮
        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(35, 35)
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {p.text_secondary};
                border: none;
                border-radius: 17px;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: {p.surface};
                color: {p.primary};
            }}
        """)
        settings_btn.clicked.connect(lambda: self._switch_page(5))
        layout.addWidget(settings_btn)

        parent_layout.addWidget(title_bar)

    def _create_nav_panel(self) -> QWidget:
        """创建左侧导航面板"""
        p = theme_manager.current_palette

        nav = QFrame()
        nav.setStyleSheet(f"""
            QFrame {{
                background-color: {p.panel_bg};
                border-right: 1px solid {p.border};
            }}
        """)

        layout = QVBoxLayout(nav)
        layout.setContentsMargins(10, 15, 10, 15)
        layout.setSpacing(5)

        # 导航标签
        nav_label = QLabel("导航")
        nav_label.setStyleSheet(f"color: {p.text_secondary}; font-size: 11px;")
        layout.addWidget(nav_label)

        layout.addSpacing(5)

        self.nav_buttons = []
        pages = [
            (texts.NAV_PLAYER, 0),
            (texts.NAV_LIBRARY, 1),
            (texts.NAV_FINGERING, 2),
            (texts.NAV_LYRICS, 3),
            (texts.NAV_RHYTHM, 4),
            (texts.NAV_SETTINGS, 5),
        ]

        for text, index in pages:
            btn = NavButton(text, text)
            btn.clicked.connect(lambda checked, i=index: self._switch_page(i))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)

        layout.addStretch()

        # 版本信息
        version_label = QLabel("v2.0")
        version_label.setStyleSheet(f"color: {p.text_light}; font-size: 10px;")
        layout.addWidget(version_label)

        self.nav_buttons[0].set_active(True)

        return nav

    def _create_info_panel(self) -> QWidget:
        """创建右侧信息面板"""
        p = theme_manager.current_palette

        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {p.panel_bg};
                border-left: 1px solid {p.border};
            }}
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # 当前曲目信息
        info_label = QLabel("当前曲目")
        info_label.setStyleSheet(f"color: {p.text_secondary}; font-size: 11px;")
        layout.addWidget(info_label)

        self.current_track_label = QLabel("未播放")
        self.current_track_label.setFont(QFont("FangSong", 14, QFont.Weight.Bold))
        self.current_track_label.setStyleSheet(f"color: {p.text};")
        layout.addWidget(self.current_track_label)

        self.current_artist_label = QLabel("")
        self.current_artist_label.setStyleSheet(f"color: {p.text_secondary};")
        layout.addWidget(self.current_artist_label)

        # 分隔线
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {p.border};")
        layout.addWidget(sep)

        # 指法信息
        fingering_label = QLabel("指法信息")
        fingering_label.setStyleSheet(f"color: {p.text_secondary}; font-size: 11px;")
        layout.addWidget(fingering_label)

        self.current_fingering_label = QLabel("筒音作5")
        self.current_fingering_label.setStyleSheet(f"color: {p.text};")
        layout.addWidget(self.current_fingering_label)

        # 练习统计
        practice_label = QLabel("练习统计")
        practice_label.setStyleSheet(f"color: {p.text_secondary}; font-size: 11px;")
        layout.addWidget(practice_label)

        self.practice_stats_label = QLabel("今日练习: 0分钟")
        self.practice_stats_label.setStyleSheet(f"color: {p.text};")
        layout.addWidget(self.practice_stats_label)

        layout.addStretch()

        # 快捷操作
        quick_label = QLabel("快捷操作")
        quick_label.setStyleSheet(f"color: {p.text_secondary}; font-size: 11px;")
        layout.addWidget(quick_label)

        quick_btns = QHBoxLayout()
        quick_btns.setSpacing(8)

        for text in ["导入简谱", "导入音频"]:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {p.surface};
                    color: {p.text};
                    border: 1px solid {p.border};
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: {p.primary};
                    color: {p.paper};
                    border-color: {p.primary};
                }}
            """)
            quick_btns.addWidget(btn)

        layout.addLayout(quick_btns)

        return panel

    def _init_pages(self):
        """初始化页面"""
        # 创建页面
        self.player_page = PlayerPanel()
        self.library_page = LibraryPanel()
        self.fingering_page = FingeringPanel()
        self.lyrics_editor_page = LyricsEditorPanel()
        self.rhythm_page = RhythmPanel()
        self.settings_page = SettingsPanel()

        # 添加到内容栈
        self.content_stack.addWidget(self.player_page)
        self.content_stack.addWidget(self.library_page)
        self.content_stack.addWidget(self.fingering_page)
        self.content_stack.addWidget(self.lyrics_editor_page)
        self.content_stack.addWidget(self.rhythm_page)
        self.content_stack.addWidget(self.settings_page)

        # 转场管理器
        self.transition_manager = TransitionManager(self.content_stack)
        self.transition_manager.set_transition('ink')

    def _switch_page(self, index: int):
        """切换页面"""
        self.transition_manager.transition_to(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.set_active(i == index)

    def _connect_signals(self):
        """连接信号"""
        pass

    def _save_layout(self):
        """保存布局"""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())

    def _restore_layout(self):
        """恢复布局"""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

        window_state = self.settings.value("windowState")
        if window_state:
            self.restoreState(window_state)

    def closeEvent(self, event):
        """关闭事件"""
        self._save_layout()
        super().closeEvent(event)