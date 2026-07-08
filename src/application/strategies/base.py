"""音频分析策略基类"""
from abc import ABC, abstractmethod
from typing import List, Tuple
import numpy as np


class AnalysisStrategy(ABC):
    """音频分析策略抽象基类"""

    @abstractmethod
    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """加载音频文件

        Args:
            file_path: 音频文件路径

        Returns:
            (音频数据, 采样率)
        """
        pass

    @abstractmethod
    def detect_pitch(self, y: np.ndarray, sr: int) -> List[Tuple[float, float]]:
        """检测音高

        Args:
            y: 音频数据
            sr: 采样率

        Returns:
            [(时间, 频率), ...]
        """
        pass

    @abstractmethod
    def pitch_to_note(self, pitch: float, base_freq: float = 261.63) -> str:
        """将频率转换为音符

        Args:
            pitch: 频率
            base_freq: 基础频率（C4）

        Returns:
            简谱音符
        """
        pass

    def analyze(self, file_path: str) -> List[str]:
        """分析音频文件（模板方法）

        Args:
            file_path: 音频文件路径

        Returns:
            音符列表
        """
        y, sr = self.load_audio(file_path)
        pitch_list = self.detect_pitch(y, sr)
        return [self.pitch_to_note(pitch) for _, pitch in pitch_list]

    @property
    def name(self) -> str:
        """策略名称"""
        return self.__class__.__name__

    @property
    def description(self) -> str:
        """策略描述"""
        return "音频分析策略"