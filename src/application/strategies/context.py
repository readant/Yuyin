"""音频分析上下文"""
from typing import List, Tuple, Optional
import numpy as np

from .base import AnalysisStrategy
from .librosa_strategy import LibrosaStrategy
from .simple_strategy import SimpleStrategy


class AudioAnalyzerContext:
    """音频分析上下文 - 管理分析策略"""

    def __init__(self, strategy: Optional[AnalysisStrategy] = None):
        self._strategy = strategy or LibrosaStrategy()
        self._strategies = {
            'librosa': LibrosaStrategy,
            'simple': SimpleStrategy,
        }

    @property
    def strategy(self) -> AnalysisStrategy:
        return self._strategy

    def set_strategy(self, strategy: AnalysisStrategy):
        """设置分析策略"""
        self._strategy = strategy

    def set_strategy_by_name(self, name: str):
        """通过名称设置策略"""
        strategy_class = self._strategies.get(name.lower())
        if strategy_class:
            self._strategy = strategy_class()
        else:
            raise ValueError(f"未知策略: {name}. 可用策略: {list(self._strategies.keys())}")

    def get_available_strategies(self) -> List[dict]:
        """获取所有可用策略"""
        return [
            {
                'name': key,
                'class': cls,
                'instance': cls()
            }
            for key, cls in self._strategies.items()
        ]

    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """加载音频文件"""
        return self._strategy.load_audio(file_path)

    def detect_pitch(self, y: np.ndarray, sr: int) -> List[Tuple[float, float]]:
        """检测音高"""
        return self._strategy.detect_pitch(y, sr)

    def pitch_to_note(self, pitch: float, base_freq: float = 261.63) -> str:
        """将频率转换为音符"""
        return self._strategy.pitch_to_note(pitch, base_freq)

    def analyze(self, file_path: str) -> List[str]:
        """分析音频文件"""
        return self._strategy.analyze(file_path)

    def record_and_analyze(self, duration: float = 5.0,
                          sample_rate: int = None) -> List[str]:
        """录音并分析"""
        import sounddevice as sd
        from ...config import settings

        if sample_rate is None:
            sample_rate = settings.audio.sample_rate

        # 录音
        audio_data = sd.rec(int(duration * sample_rate),
                           samplerate=sample_rate,
                           channels=1)
        sd.wait()

        # 转换为numpy数组
        y = audio_data.flatten()

        # 分析
        pitch_list = self.detect_pitch(y, sample_rate)
        return [self.pitch_to_note(pitch) for _, pitch in pitch_list]

    @property
    def current_strategy_name(self) -> str:
        return self._strategy.name