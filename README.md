# 余音 v0.2.0

竹笛学习助手 - 专业的音乐播放与学习 Web 应用。

---

## 项目简介

余音是一款专为竹笛爱好者设计的 Web 音乐播放器。基于 FastAPI + Jinja2 构建，支持音乐播放、指法查询、歌词同步等功能。采用中国风设计语言，提供优雅的用户体验。

### 核心亮点

- 全格式支持：MP3、WAV、FLAC、OGG、M4A
- 智能指法：实时显示当前音符的竹笛指法
- 歌词同步：支持 LRC 格式歌词，自动滚动
- 中国风 UI：水墨风格界面设计

---

## 功能特性

### 音乐播放

| 功能 | 说明 |
|------|------|
| 播放控制 | 播放/暂停/停止/上一首/下一首 |
| 进度控制 | 点击进度条跳转，拖动滑块 |
| 音量调节 | 0-100% 无级调节 |
| 频谱显示 | 实时音频频谱可视化 |

### 本地音乐库

| 功能 | 说明 |
|------|------|
| 文件夹扫描 | 递归扫描指定目录 |
| 智能识别 | 自动解析文件名获取曲目信息 |
| 搜索过滤 | 按歌曲名、艺术家搜索 |
| 分类管理 | 全部/收藏/最近播放 |

### 歌词系统

| 功能 | 说明 |
|------|------|
| LRC 解析 | 标准 LRC 格式歌词解析 |
| 实时同步 | 根据播放时间高亮当前行 |
| 滚动显示 | 自动滚动到当前歌词位置 |

### 竹笛学习

| 功能 | 说明 |
|------|------|
| 指法查询 | 选择音符查看指法图示 |
| 多调性支持 | D、G、C、F、E 五种调性 |
| 多指法类型 | 筒音作5/1/2 三种指法 |
| 学习模式 | 播放时实时显示指法 |

### 主题系统

| 主题 | 风格 | 特点 |
|------|------|------|
| 水墨素雅 | 默认 | 宣纸白底，朱红点缀 |
| 朱砂浓墨 | 深色 | 深褐背景，朱砂红主色 |
| 青瓷素雅 | 浅色 | 浅青背景，瓷绿主色 |

---

## 项目结构

```
Yuyin/
|
|-- launcher.py                      # Web 端启动器（主入口）
|-- requirements.txt                 # Web 端依赖
|-- README.md                        # 项目说明文档
|-- .gitignore                       # Git 忽略规则
|
|-- web/                             # Web 前端
|   |-- app.py                       # FastAPI 路由 + API
|   |-- gunicorn_config.py           # 生产部署配置
|   |-- static/css/                  # 样式表
|   |-- static/js/                   # JavaScript
|   +-- templates/                   # Jinja2 模板
|
|-- src/                             # 核心业务逻辑
|   |
|   |-- config/                      # 配置管理模块
|   |   +-- settings.py              # 统一配置（支持环境变量）
|   |
|   |-- domain/                      # 领域层
|   |   |-- models/                  # 领域模型
|   |   |   |-- notes.py             # 音符、调性、指法数据
|   |   |   +-- database.py          # SQLAlchemy ORM 模型
|   |   +-- repositories/            # 数据访问层
|   |       |-- base.py              # 仓储基类
|   |       +-- score_repository.py  # 乐谱仓储
|   |
|   |-- application/                 # 应用层（业务逻辑）
|   |   |-- services/                # 业务服务
|   |   |   |-- music_service.py     # 音乐库管理
|   |   |   |-- lyrics_service.py    # 歌词解析
|   |   |   +-- score_service.py     # 乐谱业务
|   |   +-- strategies/              # 策略模式
|   |       |-- base.py              # 分析策略基类
|   |       |-- librosa_strategy.py  # Librosa 分析
|   |       |-- simple_strategy.py   # FFT 分析
|   |       +-- context.py           # 策略上下文
|   |
|   |-- infrastructure/              # 基础设施层
|   |   |-- audio/                   # 音频处理
|   |   +-- database/                # 数据库
|   |
|   |-- shared/                      # 共享层
|   |   |-- exceptions/              # 异常处理
|   |   |-- logging/                 # 日志系统
|   |   |-- i18n/                    # 国际化
|   |   +-- utils/                   # 工具函数
|   |
|   +-- ui/                          # UI 组件
|       +-- splash.py                # 水墨启动动画（Web启动器复用）
|
|-- gui/                             # GUI 桌面端（暂停开发）
|   |-- main.py                      # 桌面端入口
|   +-- launcher/                    # 桌面端启动器
|
|-- tests/                           # 测试目录
|-- data/                            # 数据目录（运行时创建）
+-- docs/                            # 文档
```

---

## 架构设计

### 分层架构

```
+-----------------------------------------------------------+
|                      UI 层 (界面)                          |
|  main_window.py  components/  panels/  theme/             |
+-----------------------------------------------------------+
|                   Application 层 (业务)                    |
|  services/  strategies/                                    |
+-----------------------------------------------------------+
|                   Domain 层 (领域)                         |
|  models/  repositories/                                    |
+-----------------------------------------------------------+
|                Infrastructure 层 (基础设施)                 |
|  audio/  database/                                         |
+-----------------------------------------------------------+
|                    Shared 层 (共享)                         |
|  exceptions/  logging/  utils/                             |
+-----------------------------------------------------------+
```

### 依赖方向

```
UI --> Application --> Domain <-- Infrastructure
                     Shared <-------+
```

### 设计模式

| 模式 | 应用位置 | 说明 |
|------|----------|------|
| 单例 | Settings, MusicLibrary | 全局唯一实例 |
| 策略 | AnalysisStrategy | 音频分析算法可切换 |
| 仓储 | BaseRepository | 数据访问抽象 |

---

## 技术栈

| 类别 | 技术 | 版本 |
|------|------|------|
| 语言 | Python | 3.11+ |
| Web 框架 | FastAPI | 0.104+ |
| ASGI 服务器 | uvicorn | 0.24+ |
| 模板引擎 | Jinja2 | 3.0+ |
| 数据库 | SQLAlchemy | 2.0+ |
| 音频分析 | librosa | 0.10+ |
| 启动动画 | PyQt6 | 6.5+（可选） |

---

## 安装与运行

### 环境要求

- Python 3.11 或更高版本
- Windows 10/11, macOS, Linux

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/readant/Yuyin.git
cd yuyin

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 启动 Web 服务
python launcher.py

# 6. 浏览器自动打开 http://localhost:5000
```

### 环境变量配置

```bash
# 调试模式
set APP_DEBUG=true

# 自定义数据库路径
set DB_PATH=data/custom.db

# 自定义采样率
set AUDIO_SAMPLE_RATE=44100
```

---

## 测试

```bash
# 运行所有测试
python -m unittest discover tests

# 运行特定测试
python -m unittest tests.unit.test_strategies
```

---

## 主题定制

### 添加新主题

1. 在 `src/ui/theme/palettes.py` 中定义配色方案：

```python
CUSTOM_THEME = Palette(
    name="custom",
    display_name="自定义主题",
    background="#FFFFFF",
    surface="#F5F5F5",
    # ... 其他颜色配置
)

# 添加到预设列表
PRESETS["custom"] = CUSTOM_THEME
```

2. 在设置页面选择新主题即可。

---

## 开发规范

### 提交信息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 类型**：
- feat: 新功能
- fix: 修复 bug
- refactor: 重构
- docs: 文档
- test: 测试
- chore: 构建/工具

**示例**：
```
feat(ui): 添加歌词显示组件

- 支持 LRC 格式解析
- 实时同步滚动
- 高亮当前歌词行
```

### 代码规范

- 遵循 PEP 8
- 使用类型注解
- 编写文档字符串
- 单个函数不超过 50 行

---

## 许可证

MIT License

---

## 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (git checkout -b feature/amazing-feature)
3. 提交更改 (git commit -m 'feat: add amazing feature')
4. 推送到分支 (git push origin feature/amazing-feature)
5. 创建 Pull Request

---

## 联系方式

- Issues: GitHub Issues