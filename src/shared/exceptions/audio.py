"""音频相关异常"""
from .base import YuyinException


class AudioError(YuyinException):
    """音频处理基础异常"""
    pass


class AudioLoadError(AudioError):
    """音频加载失败"""

    def __init__(self, file_path: str, reason: str = ""):
        msg = f"无法加载音频文件: {file_path}"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg, "AUDIO_LOAD_ERROR")
        self.file_path = file_path


class AudioAnalysisError(AudioError):
    """音频分析失败"""

    def __init__(self, message: str = "音频分析失败"):
        super().__init__(message, "AUDIO_ANALYSIS_ERROR")