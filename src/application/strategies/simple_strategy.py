"""简单音频分析策略"""
from typing import List, Tuple
import numpy as np

from .base import AnalysisStrategy
from ...config import settings


class SimpleStrategy(AnalysisStrategy):
    """基于FFT的轻量级音频分析策略"""

    def __init__(self, sample_rate: int = None):
        self.sample_rate = sample_rate or settings.audio.sample_rate

    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        import soundfile as sf
        y, sr = sf.read(file_path)
        # 如果是立体声，转为单声道
        if len(y.shape) > 1:
            y = np.mean(y, axis=1)
        # 重采样
        if sr != self.sample_rate:
            from scipy import signal
            y = signal.resample(y, int(len(y) * self.sample_rate / sr))
            sr = self.sample_rate
        return y, sr

    def detect_pitch(self, y: np.ndarray, sr: int) -> List[Tuple[float, float]]:
        """使用自相关检测音高"""
        hop_length = 512
        frame_length = 2048

        pitch_list = []
        num_frames = (len(y) - frame_length) // hop_length

        for i in range(num_frames):
            start = i * hop_length
            frame = y[start:start + frame_length]

            # 自相关
            corr = np.correlate(frame, frame, mode='full')
            corr = corr[len(corr) // 2:]

            # 找峰值
            d = np.diff(corr)
            starts = np.where((d[:-1] < 0) & (d[1:] > 0))[0]

            if len(starts) > 0:
                # 找第一个有意义的峰值
                for idx in starts:
                    if idx > 20:  # 最低频率限制
                        pitch = sr / idx
                        if 80 < pitch < 2000:  # 合理频率范围
                            time = i * hop_length / sr
                            pitch_list.append((time, pitch))
                            break

        return pitch_list

    def pitch_to_note(self, pitch: float, base_freq: float = 261.63) -> str:
        """将频率转换为音符（使用半音计算）"""
        # 计算与C4的半音差
        semitones = 12 * np.log2(pitch / base_freq)
        note_index = int(round(semitones)) % 12

        # 简谱映射
        note_map = {
            0: '1',   # C
            1: '1',   # C#
            2: '2',   # D
            3: '3',   # D#
            4: '3',   # E
            5: '4',   # F
            6: '4',   # F#
            7: '5',   # G
            8: '5',   # G#
            9: '6',   # A
            10: '7',  # A#
            11: '7',  # B
        }

        # 计算八度
        octave_shift = int(round(semitones)) // 12

        note = note_map[note_index % 12]
        if octave_shift < 0:
            return f"({note})"
        elif octave_shift > 0:
            return f"[{note}]"
        return note

    @property
    def name(self) -> str:
        return "Simple"

    @property
    def description(self) -> str:
        return "轻量级分析（基于FFT自相关）"