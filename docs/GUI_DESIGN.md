# 余音 — 中国风古典 GUI 重构设计文档

## 1. 现有代码问题总结

| 文件 | 行数 | 问题 |
|------|------|------|
| `main_window.py` | 1005 | 所有功能塞在一个类，重复定义 FingeringWidget/NoteUnitWidget/ScorePreviewWidget |
| `main_window_new.py` | 1056 | 与旧版 90% 重复，仅加了 emoji 和 music_player |
| `player_widget.py` | 644 | 包含 VisualizerWidget/CircularProgressBar/GlowButton 等，职责混乱 |
| `theme.py` | 584 | 6 套赛博朋克主题，无中国风配色，样式表与主题耦合过重 |

核心矛盾：面板不可拖拽/重组，功能模块无法独立开发和测试。

---

## 2. 目标文件结构

```
src/gui/
├── __init__.py
├── main_window.py              # 精简：仅 DockWidget 框架 + 菜单栏
├── panels/
│   ├── __init__.py
│   ├── base_panel.py           # DockWidget 基类（标题栏样式、折叠逻辑）
│   ├── player_panel.py         # 音乐播放器
│   ├── editor_panel.py         # 简谱编辑器
│   ├── library_panel.py        # 乐谱管理
│   ├── rhythm_panel.py         # 节奏训练（节拍器 + 节奏练习）
│   ├── fingering_panel.py      # 指法查询
│   └── score_preview.py        # 乐谱预览（可被编辑器和播放器复用）
├── widgets/
│   ├── __init__.py
│   ├── fingering_widget.py     # 竹笛孔位图绘制
│   ├── spectrum_widget.py      # 频谱可视化
│   ├── chinese_button.py       # 中国风按钮（圆角 + 渐变 + hover 发光）
│   ├── chinese_slider.py       # 中国风滑块
│   └── decorative.py           # 云纹边框、水墨分隔线等装饰组件
├── theme/
│   ├── __init__.py
│   ├── manager.py              # ThemeManager 重构（合并原 theme.py + theme_settings.py）
│   ├── palettes.py             # 预定义配色方案（水墨/朱砂/青瓷等）
│   └── stylesheet.py           # 样式表生成器（从 palette dict 生成 QSS）
└── dialogs/
    ├── __init__.py
    └── theme_settings.py       # 主题设置对话框
```

---

## 3. 中国风配色方案

### 3.1 水墨素雅（默认主题）

| 语义名称 | 色值 | RGB | 用途 |
|----------|------|-----|------|
| background | `#F5F0E8` | 245,240,232 | 主背景（宣纸色） |
| surface | `#EDE6D6` | 237,230,214 | 面板背景 |
| primary | `#8B2500` | 139,37,0 | 主色调（朱红/赭石） |
| secondary | `#2F4F4F` | 47,79,79 | 辅助色（墨绿） |
| accent | `#C41E3A` | 196,30,58 | 强调色（中国红） |
| text | `#2C2C2C` | 44,44,44 | 正文（墨色） |
| text_secondary | `#7A6E5D` | 122,110,93 | 次要文字（淡墨） |
| border | `#C9B99A` | 201,185,154 | 边框（赭黄） |
| gold | `#B8860B` | 184,134,11 | 装饰金线 |
| ink | `#1C1C1C` | 28,28,28 | 水墨黑色 |
| paper | `#FFFEF7` | 255,254,247 | 纯纸白 |
| bamboo | `#6B8E23` | 107,142,35 | 竹绿色（指法高亮） |

### 3.2 朱砂浓墨

| 语义名称 | 色值 |
|----------|------|
| background | `#1A1410` |
| surface | `#2A221A` |
| primary | `#D4380D` |
| secondary | `#8B7355` |
| accent | `#FA541C` |
| text | `#E8DCC8` |
| text_secondary | `#A89880` |
| border | `#4A3C2E` |

### 3.3 青瓷素雅

| 语义名称 | 色值 |
|----------|------|
| background | `#F0F4F3` |
| surface | `#E2EBE8` |
| primary | `#3A7D6E` |
| secondary | `#5C8A80` |
| accent | `#2B7A5E` |
| text | `#2C3E38` |
| text_secondary | `#6B8A80` |
| border | `#B0C8C0` |

---

## 4. 字体方案

| 用途 | 字体 | 备选 | 说明 |
|------|------|------|------|
| 标题/面板名 | 方正清刻本悦宋 | 华文楷体 STKaiti | 宋体骨架 + 书法韵味 |
| 正文/标签 | 思源宋体 SC | 华文仿宋 STFangsong | 可读性优先的衬线体 |
| 简谱数字 | Consolas | JetBrains Mono | 等宽字体，音符对齐 |
| 状态栏 | 思源黑体 SC | 微软雅黑 | 无衬线，小字号清晰 |

Windows 回退链：`STKaiti → FangSong → SimSun → serif`

---

## 5. 核心架构设计

### 5.1 主窗口（精简后的 main_window.py）

```python
class MainWindow(QMainWindow):
    """仅负责：菜单栏 + DockWidget 管理 + 状态栏"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('余音')
        self.setMinimumSize(1280, 800)
        
        # 菜单栏
        self._setup_menu_bar()
        
        # Dock 面板
        self._setup_panels()
        
        # 状态栏
        self.statusBar().showMessage('就绪')
        
        # 恢复布局
        self._restore_layout()
    
    def _setup_panels(self):
        panels = {
            'library':   ('乐谱库', Qt.DockWidgetArea.LeftDockWidgetArea,  LibraryPanel),
            'editor':    ('简谱编辑', Qt.DockWidgetArea.RightDockWidgetArea, EditorPanel),
            'player':    ('音乐播放', Qt.DockWidgetArea.BottomDockWidgetArea, PlayerPanel),
            'fingering': ('指法查询', Qt.DockWidgetArea.RightDockWidgetArea, FingeringPanel),
            'rhythm':    ('节奏训练', Qt.DockWidgetArea.BottomDockWidgetArea, RhythmPanel),
        }
        for name, (title, area, cls) in panels.items():
            dock = cls(title, self)
            self.addDockWidget(area, dock)
            dock.setObjectName(f'dock_{name}')
    
    def closeEvent(self, event):
        # 保存面板布局状态到 QSettings
        self._save_layout()
        super().closeEvent(event)
```

用户可自由拖拽面板、调整大小、关闭/重开（菜单 → 视图 → 面板列表）。

### 5.2 面板基类（base_panel.py）

```python
class BasePanel(QDockWidget):
    """所有面板的公共基类"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        
        # 内容 widget
        self.content = QWidget()
        self.content.setObjectName('panelContent')
        self.setWidget(self.content)
        
        # 应用面板标题栏样式
        self._apply_title_style()
    
    def _apply_title_style(self):
        self.setStyleSheet("""
            QDockWidget::title {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8B2500, stop:0.5 #C41E3A, stop:1 #8B2500);
                text-align: center;
                padding: 6px;
                font-family: "STKaiti", "KaiTi", serif;
                font-size: 14px;
                color: #FFFEF7;
            }
        """)
```

### 5.3 各面板职责

| 面板类 | 文件 | 职责 |
|--------|------|------|
| `PlayerPanel` | player_panel.py | 播放/暂停/停止、频谱可视化、进度条、音量、歌曲信息 |
| `EditorPanel` | editor_panel.py | 简谱文本输入、实时预览、撤销/重做、导入/导出 |
| `LibraryPanel` | library_panel.py | 乐谱列表、搜索、分类标签、右键菜单（增删改） |
| `RhythmPanel` | rhythm_panel.py | 节拍器（BPM + 拍号）、节奏练习模式 |
| `FingeringPanel` | fingering_panel.py | 音符选择、竹笛孔位图、调性/指法切换 |
| `ScorePreview` | score_preview.py | 纯绘制组件，可嵌入编辑器和播放器 |

---

## 6. 中国风装饰组件设计

### 6.1 云纹边框（DecorativeFrame）

```python
class CloudBorderFrame(QFrame):
    """四角带云纹装饰的面板边框"""
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制内边框（双线效果）
        rect = self.rect().adjusted(4, 4, -4, -4)
        painter.setPen(QPen(QColor('#C9B99A'), 1))
        painter.drawRoundedRect(rect, 4, 4)
        
        rect2 = self.rect().adjusted(8, 8, -8, -8)
        painter.setPen(QPen(QColor('#B8860B'), 0.5))
        painter.drawRoundedRect(rect2, 2, 2)
        
        # 四角云纹（用简单弧线近似）
        self._draw_cloud_corner(painter, self.rect().topLeft(), 0, 0)
        self._draw_cloud_corner(painter, self.rect().topRight(), 1, 0)
        self._draw_cloud_corner(painter, self.rect().bottomLeft(), 0, 1)
        self._draw_cloud_corner(painter, self.rect().bottomRight(), 1, 1)
    
    def _draw_cloud_corner(self, painter, pos, flip_x, flip_y):
        """绘制一个角的云纹"""
        painter.save()
        painter.translate(pos)
        painter.scale(1 if flip_x == 0 else -1, 1 if flip_y == 0 else -1)
        painter.setPen(QPen(QColor('#B8860B'), 1.5))
        
        # 三段弧线组成云纹
        painter.drawArc(0, 0, 20, 20, 0, 90 * 16)
        painter.drawArc(5, 5, 12, 12, 0, 90 * 16)
        painter.drawArc(2, 2, 8, 8, 0, 90 * 16)
        
        painter.restore()
```

### 6.2 水墨分隔线

```python
class InkDivider(QWidget):
    """水墨风格水平分隔线"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(2)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0.0, QColor('#F5F0E8'))
        gradient.setColorAt(0.2, QColor('#C9B99A'))
        gradient.setColorAt(0.5, QColor('#8B2500'))
        gradient.setColorAt(0.8, QColor('#C9B99A'))
        gradient.setColorAt(1.0, QColor('#F5F0E8'))
        painter.fillRect(self.rect(), gradient)
```

### 6.3 中国风按钮

```python
class ChineseButton(QPushButton):
    """带渐变和 hover 效果的古典按钮"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #C41E3A, stop:1 #8B2500);
                color: #FFFEF7;
                border: 1px solid #B8860B;
                border-radius: 4px;
                padding: 4px 16px;
                font-family: "STKaiti", "KaiTi", serif;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #E8384F, stop:1 #A52A00);
                border-color: #DAA520;
            }
            QPushButton:pressed {
                background: #6B1D00;
            }
        """)
```

---

## 7. 频谱可视化（水墨风格）

将现有 `VisualizerWidget` 改为水墨渐变柱状图：

```python
class SpectrumWidget(QWidget):
    """水墨风格频谱可视化"""
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 宣纸背景
        painter.fillRect(self.rect(), QColor('#F5F0E8'))
        
        bar_width = (self.width() - 40) / len(self.bars)
        for i, value in enumerate(self.bars):
            if value <= 0:
                continue
            h = max(2, value * 2)
            x = 20 + i * bar_width
            y = self.height() - 10 - h
            
            # 从底部深墨到顶部淡墨的渐变
            grad = QLinearGradient(x, y + h, x, y)
            grad.setColorAt(0.0, QColor('#2C2C2C'))   # 浓墨
            grad.setColorAt(0.5, QColor('#8B2500'))    # 赭石
            grad.setColorAt(1.0, QColor('#C41E3A'))    # 朱砂尖
            
            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(int(x), int(y), int(bar_width - 2), int(h), 2, 2)
```

---

## 8. 主题系统重构

### 8.1 新 ThemeManager 设计

```python
# theme/manager.py
class ThemeManager:
    """单例主题管理器"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.palettes = load_all_palettes()  # 从 palettes.py 加载
        self.current = 'ink_wash'             # 默认水墨素雅
        self._load_user_choice()
    
    def switch(self, name: str):
        self.current = name
        self._apply()
        self._save_user_choice()
    
    def _apply(self):
        palette = self.palettes[self.current]
        app = QApplication.instance()
        
        # 设置 QPalette
        qpal = QPalette()
        qpal.setColor(QPalette.ColorRole.Window, QColor(palette['background']))
        qpal.setColor(QPalette.ColorRole.WindowText, QColor(palette['text']))
        qpal.setColor(QPalette.ColorRole.Base, QColor(palette['surface']))
        qpal.setColor(QPalette.ColorRole.Button, QColor(palette['surface']))
        qpal.setColor(QPalette.ColorRole.ButtonText, QColor(palette['text']))
        qpal.setColor(QPalette.ColorRole.Highlight, QColor(palette['primary']))
        qpal.setColor(QPalette.ColorRole.HighlightedText, QColor(palette['paper']))
        app.setPalette(qpal)
        
        # 生成全局 QSS
        qss = generate_stylesheet(palette)
        app.setStyleSheet(qss)
    
    def get(self, key: str) -> str:
        return self.palettes[self.current].get(key, '#000000')
```

### 8.2 样式表生成器

```python
# theme/stylesheet.py
def generate_stylesheet(p: dict) -> str:
    return f"""
    * {{
        font-family: "Source Han Serif SC", "STFangsong", "FangSong", serif;
    }}
    
    QMainWindow {{
        background-color: {p['background']};
    }}
    
    QDockWidget {{
        font-family: "STKaiti", "KaiTi", serif;
        font-size: 13px;
        color: {p['text']};
    }}
    
    QDockWidget::title {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 {p['primary']}, stop:0.5 {p['accent']}, stop:1 {p['primary']});
        text-align: center;
        padding: 5px;
        color: {p['paper']};
    }}
    
    QPushButton {{
        background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 {p['accent']}, stop:1 {p['primary']});
        color: {p['paper']};
        border: 1px solid {p.get('gold', '#B8860B')};
        border-radius: 4px;
        padding: 5px 14px;
        min-height: 20px;
    }}
    QPushButton:hover {{
        border-color: {p.get('gold', '#DAA520')};
    }}
    QPushButton:disabled {{
        background-color: {p['surface']};
        color: {p['text_secondary']};
    }}
    
    QLineEdit, QTextEdit, QSpinBox, QComboBox {{
        background-color: {p['paper']};
        color: {p['text']};
        border: 1px solid {p['border']};
        border-radius: 3px;
        padding: 5px 8px;
        selection-background-color: {p['primary']};
    }}
    QLineEdit:focus, QTextEdit:focus {{
        border-color: {p['primary']};
    }}
    
    QProgressBar {{
        background-color: {p['border']};
        border: none;
        border-radius: 3px;
        height: 6px;
    }}
    QProgressBar::chunk {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 {p['primary']}, stop:1 {p['accent']});
        border-radius: 3px;
    }}
    
    QSlider::groove:horizontal {{
        background-color: {p['border']};
        height: 4px;
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background-color: {p['primary']};
        width: 14px; height: 14px;
        margin: -5px 0;
        border-radius: 7px;
        border: 2px solid {p.get('gold', '#B8860B')};
    }}
    QSlider::sub-page:horizontal {{
        background-color: {p['primary']};
        border-radius: 2px;
    }}
    
    QTabWidget::pane {{
        border: 1px solid {p['border']};
        background-color: {p['surface']};
    }}
    QTabBar::tab {{
        background-color: {p['surface']};
        color: {p['text_secondary']};
        border: 1px solid {p['border']};
        border-bottom: none;
        padding: 6px 14px;
        font-family: "STKaiti", "KaiTi", serif;
    }}
    QTabBar::tab:selected {{
        background-color: {p['primary']};
        color: {p['paper']};
    }}
    
    QListWidget {{
        background-color: {p['paper']};
        border: 1px solid {p['border']};
        border-radius: 4px;
    }}
    QListWidget::item {{
        padding: 6px 8px;
    }}
    QListWidget::item:selected {{
        background-color: {p['primary']};
        color: {p['paper']};
    }}
    QListWidget::item:hover {{
        background-color: {p['surface']};
    }}
    
    QScrollBar:vertical {{
        background-color: {p['surface']};
        width: 8px;
    }}
    QScrollBar::handle:vertical {{
        background-color: {p['border']};
        border-radius: 4px;
        min-height: 20px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: {p['primary']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    
    QToolTip {{
        background-color: {p['surface']};
        color: {p['text']};
        border: 1px solid {p['primary']};
        border-radius: 3px;
        padding: 3px 6px;
    }}
    
    QStatusBar {{
        background-color: {p['surface']};
        color: {p['text_secondary']};
        border-top: 1px solid {p['border']};
        font-family: "Source Han Sans SC", "Microsoft YaHei", sans-serif;
    }}
    """
```

---

## 9. 播放器面板详细设计

```
┌─────────────────────────────────────────────────┐
│  《歌曲名称》  —  艺术家名                      │
│                                                 │
│  ╭──────────────────────────────────────────╮   │
│  │     ██  ▓▓  ░░  ▓▓  ██  ░░  ▓▓  ██     │   │
│  │    ▓▓▓▓ ░░░░ ▓▓▓▓ ░░░░ ▓▓▓▓ ░░░░ ▓▓▓▓ │   │
│  │   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │   │
│  │  (水墨渐变频谱可视化)                     │   │
│  ╰──────────────────────────────────────────╯   │
│                                                 │
│  当前音符: 5    指法: ○●●●●●                     │
│                                                 │
│  ────●──────────────────────────────────────    │
│  01:23                              03:45       │
│                                                 │
│        ◀◀    ▶/❚❚    ■    ▶▶                   │
│                                                 │
│  🔊 ═══════════════●═══ 75%                    │
└─────────────────────────────────────────────────┘
```

组件拆分：
- `SongInfoBar` — 歌名 + 艺术家
- `SpectrumWidget` — 频谱可视化（已有，重绘）
- `NoteDisplayWidget` — 当前音符 + 指法（复用 FingeringWidget）
- `SeekBar` — 进度条 + 时间标签
- `PlayerControls` — 播放/暂停/停止/上一曲/下一曲
- `VolumeControl` — 音量滑块

---

## 10. 编辑器面板详细设计

```
┌──────────────────────────────────┐
│  调性: [D ▾]  指法: [5 ▾]  BPM: [80] │
│──────────────────────────────────│
│  简谱输入:                        │
│  ┌────────────────────────────┐  │
│  │ (5) (6) (7) 1 | 2 3 4 5 | │  │
│  │ 6 5 4 3 2 1 | (7) (6) (5)| │  │
│  └────────────────────────────┘  │
│  [导入] [保存] [导出PDF]         │
│──────────────────────────────────│
│  乐谱预览:                        │
│  ╭────────────────────────────╮  │
│  │ (5) (6) (7)  1  |  2  3   │  │
│  │ ●●●●●● ●●●●●○ ●●●●○○ ●●●○○○ │  │
│  │  4  5  |  6  5  4  3      │  │
│  │ ○●●○○○ ○●●●●● ○○○○○● ○●●●●● │  │
│  ╰────────────────────────────╯  │
│  共 24 个音符                     │
└──────────────────────────────────┘
```

---

## 11. 指法查询面板详细设计

```
┌──────────────────────────────────┐
│  调性: [D ▾]  指法: [筒音作5 ▾]  │
│──────────────────────────────────│
│  选择音符: [5 ▾]                 │
│                                  │
│      ╭─────────────╮            │
│      │   ┌───┐     │            │
│      │   │ ○ │     │  中音5     │
│      │   └───┘     │            │
│      │   ┌───┐     │            │
│      │   │ ● │     │  ○●●●●●    │
│      │   └───┘     │            │
│      │   ┌───┐     │            │
│      │   │ ● │     │            │
│      │   └───┘     │            │
│      │   ┌───┐     │            │
│      │   │ ● │     │            │
│      │   └───┘     │            │
│      │   ┌───┐     │            │
│      │   │ ● │     │            │
│      │   └───┘     │            │
│      │   ┌───┐     │            │
│      │   │ ● │     │            │
│      │   └───┘     │            │
│      ╰─────────────╯            │
│                                  │
│  ═══════ 指法速查表 ═══════      │
│  (5)●●●●●●  (6)●●●●●○          │
│  (7)●●●●○○  1 ●●●○○○           │
│  2 ●●○○○○  3 ●○○○○○           │
│  4 ○●●○○○  5 ○●●●●●           │
│  6 ○○○○○●  7 ○○○○●●           │
└──────────────────────────────────┘
```

---

## 12. 乐谱管理面板详细设计

```
┌──────────────────────────────────┐
│  🔍 [搜索乐谱...        ]        │
│──────────────────────────────────│
│  分类: [全部 ▾]  排序: [最近 ▾]  │
│──────────────────────────────────│
│  ╭────────────────────────────╮  │
│  │  ★ 牧民新歌               │  │
│  │    D调 · 筒音作5 · 80BPM  │  │
│  │    标签: 经典 蒙古族       │  │
│  │    2024-01-15              │  │
│  ├────────────────────────────┤  │
│  │    姑苏行                  │  │
│  │    G调 · 筒音作2 · 72BPM  │  │
│  │    标名: 江南 春天         │  │
│  │    2024-01-10              │  │
│  ├────────────────────────────┤  │
│  │    扬鞭催马运粮忙          │  │
│  │    D调 · 筒音作5 · 120BPM│  │
│  │    标签: 欢快 北方         │  │
│  │    2024-01-05              │  │
│  ╰────────────────────────────╯  │
│                                  │
│  [新建] [编辑] [删除] [导入]    │
└──────────────────────────────────┘
```

---

## 13. 节奏训练面板详细设计

```
┌──────────────────────────────────┐
│  拍号: [4/4 ▾]  BPM: [80 ▾]     │
│──────────────────────────────────│
│         ╭───────────╮           │
│         │     ●     │           │
│         │   ╱   ╲   │  节拍器   │
│         │  ●       ●│  摆锤动画 │
│         │   ╲   ╱   │           │
│         │     ●     │           │
│         ╰───────────╯           │
│                                  │
│  ●  ○  ○  ○  │  ●  ○  ○  ○   │
│  1  2  3  4     1  2  3  4     │
│                                  │
│  [▶ 开始]  [■ 停止]  [🔊 声音] │
│                                  │
│  ──── 节奏练习 ────             │
│  模式: [跟打 ▾]                 │
│  点击按钮跟随节拍:               │
│  [拍] [拍] [拍] [拍]            │
│  得分: --                       │
└──────────────────────────────────┘
```

节拍器摆锤动画用 `QTimer` + `QPainter` 绘制正弦摆动弧线。

---

## 14. 菜单栏结构

```
余音
├── 文件
│   ├── 新建乐谱        Ctrl+N
│   ├── 打开乐谱        Ctrl+O
│   ├── 保存乐谱        Ctrl+S
│   ├── 导入简谱文件     Ctrl+I
│   ├── 导出PDF          Ctrl+E
│   └── 退出
├── 编辑
│   ├── 撤销            Ctrl+Z
│   ├── 重做            Ctrl+Y
│   └── 首选项...
├── 视图
│   ├── 面板
│   │   ├── ☑ 乐谱库
│   │   ├── ☑ 简谱编辑
│   │   ├── ☑ 音乐播放
│   │   ├── ☑ 指法查询
│   │   └── ☑ 节奏训练
│   ├── 重置布局
│   └── 主题
│       ├── 水墨素雅
│       ├── 朱砂浓墨
│       └── 青瓷素雅
└── 帮助
    ├── 快捷键
    └── 关于
```

---

## 15. 实施优先级

| 阶段 | 内容 | 预计工作量 |
|------|------|-----------|
| P0 | theme/ 目录：palette 定义 + 样式表生成 + ThemeManager 重构 | 小 |
| P0 | base_panel.py：DockWidget 基类 + 标题栏样式 | 小 |
| P0 | main_window.py：仅框架，5 个空 Dock 面板 | 小 |
| P1 | fingering_widget.py：从旧代码提取并中国风化 | 小 |
| P1 | library_panel.py：最简单的列表面板，验证架构 | 中 |
| P1 | editor_panel.py：核心功能面板 | 中 |
| P2 | player_panel.py：播放器 + 频谱 | 中 |
| P2 | fingering_panel.py：指法查询 | 小 |
| P2 | rhythm_panel.py：节拍器 | 中 |
| P3 | decorative.py：云纹边框、水墨分隔线等装饰 | 小 |
| P3 | 主题切换对话框 + 实时预览 | 中 |

---

## 16. 关键技术决策

1. **QDockWidget** 而非自定义拖拽框架 — Qt 原生支持浮动、停靠、tab 化，开箱即用
2. **QSettings** 持久化面板布局 — 用户下次启动恢复上次的面板位置
3. **单一 QSS 生成** 而非 inline style — 主题切换时一次性替换，避免逐组件更新
4. **FingeringWidget 纯绘制** — 继承 QWidget + paintEvent，不使用子控件嵌套
5. **信号总线** — 各面板通过 MainWindow 中转信号（如 `score_changed`），避免面板间直接耦合

---

## 17. 迁移注意事项

- 现有 `src/audio/`、`src/core/`、`src/database/` 完全不动，只重构 `src/gui/`
- `player_widget.py` 中的 `AudioPlayer` 实例在 `PlayerPanel` 中重新创建（当前 `MusicPlayerWidget` 自带一个 `AudioPlayer`，与 `MainWindow` 中的重复，需统一）
- 旧的 `main_window_new.py` 在新架构稳定后删除
- `theme.py` 中的 `PRESET_THEMES` 字典替换为 `theme/palettes.py` 中的中国风方案
