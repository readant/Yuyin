"""主窗口"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QStackedWidget, QLabel, QFrame)
from PyQt6.QtCore import Qt, QSettings

from .panels.player_panel import PlayerPanel
from .panels.library_panel import LibraryPanel
from .panels.fingering_panel import FingeringPanel
from .panels.settings_panel import SettingsPanel
from .panels.lyrics_editor_panel import LyricsEditorPanel
from .panels.rhythm_panel import RhythmPanel
from .navigation.nav_button import NavButton
from .theme import theme_manager
from ..domain.models.database import DatabaseManager
from ..shared.i18n import texts


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()

        self.db = DatabaseManager()
        self.settings = QSettings("Yuyin", "MainWindow")

        self._init_ui()
        self._connect_signals()
        self._restore_layout()

        theme_manager.apply_theme()

    def _init_ui(self):
        self.setWindowTitle("余音 - 音乐播放器")
        self.setMinimumSize(1100, 700)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 导航栏
        nav = self._create_nav_bar()
        main_layout.addWidget(nav)

        # 分隔线
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("color: rgba(128,128,128,0.3);")
        main_layout.addWidget(sep)

        # 内容区
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, 1)

        self.player_page = PlayerPanel()
        self.library_page = LibraryPanel()
        self.fingering_page = FingeringPanel()
        self.lyrics_editor_page = LyricsEditorPanel()
        self.rhythm_page = RhythmPanel()
        self.settings_page = SettingsPanel()

        self.content_stack.addWidget(self.player_page)       # 0
        self.content_stack.addWidget(self.library_page)      # 1
        self.content_stack.addWidget(self.fingering_page)    # 2
        self.content_stack.addWidget(self.lyrics_editor_page) # 3
        self.content_stack.addWidget(self.rhythm_page)       # 4
        self.content_stack.addWidget(self.settings_page)     # 5

        # 学习面板
        self.learning_panel = self._create_learning_panel()
        self.learning_panel.hide()
        main_layout.addWidget(self.learning_panel)

        self.statusBar().showMessage("就绪")

    def _create_nav_bar(self) -> QWidget:
        from .theme import theme_manager
        p = theme_manager.current_palette

        nav = QFrame()
        nav.setFixedWidth(70)
        nav.setStyleSheet(f"QFrame {{ background-color: {p.surface}; border: none; }}")

        layout = QVBoxLayout(nav)
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(5)

        logo = QLabel("Y")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setFont(logo.font())
        layout.addWidget(logo)

        layout.addSpacing(20)

        self.nav_buttons = []
        pages = [
            (texts.NAV_PLAYER, "P", 0),
            (texts.NAV_LIBRARY, "L", 1),
            (texts.NAV_FINGERING, "F", 2),
            (texts.NAV_LYRICS, "G", 3),
            (texts.NAV_RHYTHM, "R", 4),
            (texts.NAV_SETTINGS, "S", 5),
        ]

        for text, icon, index in pages:
            btn = NavButton(icon, text)
            btn.clicked.connect(lambda checked, i=index: self._switch_page(i))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)

        layout.addStretch()

        self.nav_buttons[0].set_active(True)

        return nav

    def _create_learning_panel(self) -> QFrame:
        panel = QFrame()
        panel.setFixedWidth(200)
        panel.setStyleSheet("""
            QFrame {
                background-color: rgba(0,0,0,0.05);
                border-left: 1px solid rgba(128,128,128,0.2);
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 15, 10, 15)

        title = QLabel("学习模式")
        title.setFont(title.font())
        layout.addWidget(title)

        layout.addSpacing(10)

        layout.addWidget(QLabel("当前音符:"))
        self.note_display = QLabel("--")
        self.note_display.setFont(self.note_display.font())
        self.note_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.note_display.setStyleSheet("padding: 10px; background: rgba(255,255,255,0.1); border-radius: 8px;")
        layout.addWidget(self.note_display)

        layout.addSpacing(10)

        layout.addWidget(QLabel("指法提示:"))
        self.fingering_display = QLabel("------")
        self.fingering_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.fingering_display)

        layout.addStretch()

        return panel

    def _switch_page(self, index: int):
        self.content_stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.set_active(i == index)

    def _connect_signals(self):
        self.player_page.learning_mode_changed.connect(self._toggle_learning_panel)
        self.player_page.note_changed.connect(self._on_note_changed)

    def _toggle_learning_panel(self, enabled: bool):
        self.learning_panel.setVisible(enabled)

    def _on_note_changed(self, note: str):
        self.note_display.setText(note if note else "--")

    def _save_layout(self):
        self.settings.setValue("geometry", self.saveGeometry())

    def _restore_layout(self):
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

    def closeEvent(self, event):
        self._save_layout()
        super().closeEvent(event)