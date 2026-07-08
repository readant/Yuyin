# 余音 v2.0

专业的音乐播放器，兼具竹笛学习功能。中国风设计，支持多主题切换。

## 功能特性

- **音乐播放**：支持 MP3、WAV、FLAC、OGG 等格式
- **本地音乐库**：扫描本地音乐文件，分类管理
- **歌词显示**：支持 LRC 格式歌词，实时滚动
- **频谱可视化**：水墨风格频谱动画
- **黑胶唱片**：旋转动画效果
- **竹笛指法**：实时指法查询和学习
- **多主题**：三套中国风主题可切换
- **学习模式**：播放时显示当前音符指法

## 项目结构

```
Yuyin/
├── main.py                    # 主入口
├── requirements.txt           # 依赖列表
│
└── src/                       # 源码
    ├── config/                # 配置管理
    │   └── settings.py        # 统一配置（支持环境变量）
    │
    ├── domain/                # 领域层
    │   ├── models/            # 核心实体
    │   │   ├── notes.py       # 音符、调性、指法数据
    │   │   └── database.py    # ORM 模型
    │   └── repositories/      # 仓储接口
    │       ├── base.py        # 仓储基类
    │       └── score_repository.py
    │
    ├── application/           # 应用层
    │   ├── services/          # 业务服务
    │   │   ├── music_service.py    # 音乐库管理
    │   │   ├── lyrics_service.py   # 歌词管理
    │   │   └── score_service.py    # 乐谱服务
    │   └── strategies/        # 策略模式
    │       ├── base.py        # 分析策略基类
    │       ├── librosa_strategy.py  # 高精度分析
    │       ├── simple_strategy.py   # 轻量级分析
    │       └── context.py     # 策略上下文
    │
    ├── infrastructure/        # 基础设施层
    │   ├── audio/             # 音频处理
    │   │   ├── analyzer.py    # 音频分析器
    │   │   ├── player.py      # 播放器
    │   │   └── realtime_analyzer.py
    │   └── database/          # 数据库
    │
    ├── shared/                # 共享层
    │   ├── exceptions/        # 异常处理
    │   ├── logging/           # 日志系统
    │   └── utils/             # 工具函数
    │
    └── ui/                    # 界面层
        ├── main_window.py     # 主窗口
        ├── splash.py          # 启动动画
        ├── components/        # 可复用组件
        │   ├── vinyl.py       # 黑胶唱片
        │   ├── spectrum.py    # 频谱可视化
        │   ├── progress.py    # 进度条
        │   ├── lyrics.py      # 歌词显示
        │   └── fingering.py   # 指法图示
        ├── panels/            # 功能面板
        │   ├── player_panel.py
        │   ├── library_panel.py
        │   ├── fingering_panel.py
        │   └── settings_panel.py
        ├── navigation/        # 导航组件
        └── theme/             # 主题系统
            ├── manager.py     # 主题管理器
            └── palettes.py    # 配色方案
│
├── tests/                     # 测试
│   └── unit/
│       └── test_strategies.py
│
└── data/                      # 数据目录（运行时创建）
```

## 技术栈

- Python 3.11+
- PyQt6 (GUI)
- SQLAlchemy (数据库)
- librosa (音频分析)
- sounddevice (音频播放)
- reportlab (PDF导出)

## 快速开始

### 环境配置

```bash
# 创建虚拟环境
python -m venv venv

# 激活环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 运行应用

```bash
python main.py
```

## 开发指南

### 代码规范

- 遵循 PEP 8
- 使用类型注解
- 编写文档字符串

### 提交规范

```
feat: 新功能
fix: 修复bug
refactor: 重构
docs: 文档
test: 测试
chore: 构建/工具
```

## 许可证

MIT License