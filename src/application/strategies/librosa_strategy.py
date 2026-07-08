"""Librosa音频分析策略"""
from typing import List, Tuple
import numpy as np

from .base import AnalysisStrategy


class LibrosaStrategy(AnalysisStrategy):
    """基于Librosa的高精度音频分析策略"""

    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate

    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        import librosa
        y, sr = librosa.load(file_path, sr=self.sample_rate)
        return y, sr

    def detect_pitch(self, y: np.ndarray, sr: int) -> List[Tuple[float, float]]:
        import librosa

        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)

        pitch_list = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                time = librosa.frames_to_time(t, sr=sr)
                pitch_list.append((time, pitch))

        return pitch_list

    def pitch_to_note(self, pitch: float, base_freq: float = 261.63) -> str:
        import librosa

        note_name = librosa.hz_to_note(pitch)

        note_map = {
            'C3': '_1', 'D3': '_2', 'E3': '_3', 'F3': '_4',
            'G3': '_5', 'A3': '_6', 'B3': '_7',
            'C4': '1', 'D4': '2', 'E4': '3', 'F4': '4',
            'G4': '5', 'A4': '6', 'B4': '7',
            'C5': '[1]', 'D5': '[2]', 'E5': '[3]', 'F5': '[4]',
            'G5': '[5]', 'A5': '[6]', 'B5': '[7]'
        }

        return note_map.get(note_name, '1')

    @property
    def name(self) -> str:
        return "Librosa"

    @property
    def description(self) -> str:
        return "高精度音频分析（基于Librosa库）"