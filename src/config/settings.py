"""配置管理"""
import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path


@dataclass
class DatabaseConfig:
    """数据库配置"""
    path: str = "data/zhudi.db"
    echo: bool = False


@dataclass
class AudioConfig:
    """音频配置"""
    sample_rate: int = 22050
    channels: int = 1
    buffer_size: int = 1024


@dataclass
class AppConfig:
    """应用配置"""
    name: str = "余音"
    version: str = "2.0.0"
    debug: bool = False


@dataclass
class Settings:
    """统一配置管理"""

    app: AppConfig = None
    database: DatabaseConfig = None
    audio: AudioConfig = None

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

        self.app = AppConfig()
        self.database = DatabaseConfig()
        self.audio = AudioConfig()

        self._load_from_env()

    def _load_from_env(self):
        """从环境变量加载配置"""
        self.app.debug = os.getenv("APP_DEBUG", "false").lower() == "true"
        self.database.path = os.getenv("DB_PATH", self.database.path)
        self.database.echo = os.getenv("DB_ECHO", "false").lower() == "true"
        self.audio.sample_rate = int(os.getenv("AUDIO_SAMPLE_RATE", str(self.audio.sample_rate)))

    def get_project_root(self) -> Path:
        """获取项目根目录"""
        return Path(__file__).parent.parent.parent

    def get_data_dir(self) -> Path:
        """获取数据目录"""
        data_dir = self.get_project_root() / "data"
        data_dir.mkdir(exist_ok=True)
        return data_dir

    def __repr__(self):
        return (
            f"Settings(\n"
            f"  app={self.app},\n"
            f"  database={self.database},\n"
            f"  audio={self.audio}\n"
            f")"
        )


# 全局配置实例
settings = Settings()