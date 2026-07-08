# 余音 - 配置文件（兼容旧接口）
from src.config import settings

# 应用信息
APP_NAME = settings.app.name
APP_VERSION = settings.app.version
APP_DESCRIPTION = "专业的简谱学习工具"

# 数据库配置
DATABASE_PATH = settings.database.path

# 默认设置
DEFAULT_KEY = "D"
DEFAULT_FINGERING = "5"
DEFAULT_BPM = 80
DEFAULT_TIME_SIGNATURE = (4, 4)

# 支持的调性
SUPPORTED_KEYS = ['D', 'G', 'C', 'F', 'E']

# 支持的指法类型
SUPPORTED_FINGERINGS = ['5', '1', '2']

# 音频配置
SAMPLE_RATE = settings.audio.sample_rate
SUPPORTED_AUDIO_FORMATS = ['wav', 'mp3', 'flac']

# 界面配置
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 800