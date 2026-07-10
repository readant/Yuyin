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
| 淡入淡出 | 切换曲目自动淡入淡出 |
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
| 歌词编辑 | 在线编辑歌词并关联曲目 |
| LRC 导出 | 导出标准 LRC 文件 |

### 简谱编辑器

| 功能 | 说明 |
|------|------|
| 洞洞谱编辑 | 可视化音符编辑，指法实时预览 |
| 文本导入 | 简谱文本一键导入 |
| 节奏编辑 | 减时线、附点、小节线编辑 |
| 复制粘贴 | 多选音符复制粘贴 |
| JSON 导入/导出 | 乐谱文件序列化 |
| PDF 导出 | 简谱打印输出 |
| 指法键盘 | 点击指法音符快速输入 |

### 竹笛学习

| 功能 | 说明 |
|------|------|
| 指法查询 | 选择音符查看指法图示 |
| 多调性支持 | D、G、C、F、E 五种调性 |
| 多指法类型 | 筒音作5/1/2 三种指法 |
| 学习模式 | 播放时实时显示指法 |
| 跟吹练习 | 录音匹配，实时反馈准确率 |
| 练习记录 | 记录练习时长和准确率统计 |

### 节奏训练

| 功能 | 说明 |
|------|------|
| 节拍器 | 多种节拍模式（2/4, 3/4, 4/4, 6/8） |
| Tap 测速 | 敲击测量 BPM |
| 节奏练习 | 分级练习课程 |
| 练习统计 | 节奏练习数据追踪 |

### 音频工具

| 功能 | 说明 |
|------|------|
| 波形可视化 | 上传音频显示波形图 |
| 频谱分析 | 实时频谱显示 |
| AI 简谱生成 | 自动识别音高生成简谱 |
| 音频裁剪 | 按时间段裁剪音频 |
| 变调处理 | 半音级变调 |
| 音量归一化 | 响度标准化处理 |
| 录音 | 浏览器在线录音 |

### 主题与个性化

| 功能 | 说明 |
|------|------|
| 背景自定义 | 上传/切换背景图片 |
| 中国风主题 | 水墨素雅 / 朱砂浓墨 / 青瓷素雅 |
| 自动隐藏侧栏 | 鼠标触发展开侧边栏 |
| 系统托盘 | 任务栏图标，右键退出 |

---

## 项目结构

```
Yuyin/
|
|-- launcher.py                      # Web 端启动器（主入口，支持 PyQt6 启动动画和系统托盘）
|-- requirements.txt                 # Python 依赖
|-- README.md                        # 项目说明文档
|-- ACKNOWLEDGMENTS.md               # 致谢与项目缘起
|-- .gitignore                       # Git 忽略规则
|
|-- web/                             # Web 前端
|   |-- app.py                       # FastAPI 路由 + API（音乐/简谱/歌词/练习/工具/系统）
|   |-- gunicorn_config.py           # 生产部署配置
|   |-- static/
|   |   |-- css/style.css            # 全局样式表（中国风主题变量）
|   |   |-- js/player.js             # 播放器核心逻辑
|   |   |-- audio/                   # 音频工具处理输出
|   |   +-- backgrounds/             # 自定义背景图片
|   +-- templates/                   # Jinja2 模板
|       |-- base.html                # 基础布局（侧边栏导航 + 退出按钮）
|       |-- index.html               # 曲库首页
|       |-- player.html              # 播放器页面
|       |-- editor.html              # 简谱编辑器（洞洞谱编辑）
|       |-- fingering.html           # 指法速查
|       |-- practice.html            # 跟吹练习
|       |-- lyrics.html              # 歌词编辑器
|       |-- rhythm.html              # 节奏训练
|       |-- tools.html               # 音频工具（波形/频谱/AI简谱生成）
|       +-- settings.html            # 设置页面
|
|-- src/                             # 核心业务逻辑
|   |
|   |-- config/                      # 配置管理模块
|   |   +-- settings.py              # 统一配置（支持环境变量）
|   |
|   |-- domain/                      # 领域层
|   |   |-- models/                  # 领域模型
|   |   |   |-- notes.py             # 音符、调性、指法数据
|   |   |   +-- database.py          # SQLAlchemy ORM 模型（Score/Fingering/PracticeRecord/Setting）
|   |   +-- repositories/            # 数据访问层
|   |       |-- base.py              # 仓储基类
|   |       +-- score_repository.py  # 乐谱仓储
|   |
|   |-- application/                 # 应用层（业务逻辑）
|   |   |-- services/                # 业务服务
|   |   |   |-- music_service.py     # 音乐库管理
|   |   |   |-- lyrics_service.py    # 歌词解析
|   |   |   |-- score_service.py     # 乐谱业务
|   |   |   |-- rhythm_service.py    # 节奏训练（节拍器/模式管理）
|   |   |   |-- zhudi_service.py     # 竹笛学习（练习记录/跟吹匹配）
|   |   |   +-- fade_service.py      # 淡入淡出服务
|   |   +-- strategies/              # 策略模式
|   |       |-- base.py              # 分析策略基类
|   |       |-- librosa_strategy.py  # Librosa 分析
|   |       |-- simple_strategy.py   # FFT 分析
|   |       +-- context.py           # 策略上下文
|   |
|   |-- infrastructure/              # 基础设施层
|   |   |-- audio/                   # 音频处理
|   |   |   |-- analyzer.py          # 音频分析
|   |   |   |-- device_detector.py   # 设备检测
|   |   |   |-- player.py            # 音频播放
|   |   |   +-- realtime_analyzer.py # 实时分析
|   |   +-- database/                # 数据库连接
|   |       +-- connection.py
|   |
|   |-- shared/                      # 共享层
|   |   |-- exceptions/              # 异常处理（audio/base/database）
|   |   |-- logging/                 # 日志系统
|   |   |-- i18n/                    # 国际化（文本定义）
|   |   +-- utils/                   # 工具函数（PDF 导出等）
|   |
|   +-- ui/                          # UI 组件（PyQt6 桌面端）
|       |-- main_window.py           # 主窗口
|       |-- splash.py                # 水墨启动动画（Web启动器复用）
|       |-- components/              # UI 组件（频谱/指法/歌词/唱盘/迷你播放器）
|       |-- panels/                  # 功能面板（曲库/播放/指法/设置/节奏）
|       |-- navigation/              # 导航组件
|       +-- theme/                   # 主题管理（配色方案/管理器）
|
|-- gui/                             # GUI 桌面端入口（暂停开发）
|   |-- main.py
|   +-- launcher/
|
|-- tests/                           # 测试目录
|-- data/                            # 数据目录（运行时创建：歌词/练习记录/听歌记录/LRC文件）
|-- logs/                            # 运行日志
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
| 生产服务器 | gunicorn | 21.0+ |
| 模板引擎 | Jinja2 | 3.0+ |
| 数据库 | SQLAlchemy | 2.0+ |
| 音频分析 | librosa | 0.10+ |
| 音频处理 | sounddevice, soundfile | — |
| PDF导出 | reportlab | 4.0+ |
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

# 6. 浏览器自动打开 http://127.0.0.1:5000
#    （安装 PyQt6 后将显示水墨启动动画和系统托盘图标）
#    退出方式：系统托盘右键"退出" / 网页侧边栏 ✕ 按钮 / 终端 Ctrl+C
```

### 更新已克隆的仓库

当项目有新版本发布时，按以下步骤更新本地代码：

```bash
# 1. 进入项目目录
cd yuyin

# 2. 拉取最新代码
git pull origin main

# 3. 安装新增的依赖（如有）
pip install -r requirements.txt

# 4. 重启服务
python launcher.py
```

如果需要切换到开发分支：

```bash
# 切换到 dev 分支
git checkout dev
git pull origin dev
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