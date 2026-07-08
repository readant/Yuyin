"""音频处理模块"""
import numpy as np
from typing import List, Tuple, Optional
import sounddevice as sd
import threading
import queue

from .strategies import AudioAnalyzerContext, AnalysisStrategy
from .strategies import LibrosaStrategy, SimpleStrategy


class AudioAnalyzer:
    """音频分析器（使用策略模式）"""

    def __init__(self, strategy: Optional[AnalysisStrategy] = None):
        self.sample_rate = 22050
        self.is_recording = False
        self.audio_queue = queue.Queue()

        # 策略上下文
        self._context = AudioAnalyzerContext(strategy)

    @property
    def strategy(self) -> AnalysisStrategy:
        return self._context.strategy

    def set_strategy(self, strategy: AnalysisStrategy):
        """设置分析策略"""
        self._context.set_strategy(strategy)

    def set_strategy_by_name(self, name: str):
        """通过名称设置策略"""
        self._context.set_strategy_by_name(name)

    def get_available_strategies(self) -> List[dict]:
        """获取所有可用策略"""
        return self._context.get_available_strategies()

    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """加载音频文件"""
        return self._context.load_audio(file_path)

    def detect_pitch(self, y: np.ndarray, sr: int) -> List[Tuple[float, float]]:
        """检测音高"""
        return self._context.detect_pitch(y, sr)

    def pitch_to_note(self, pitch: float, base_freq: float = 261.63) -> str:
        """将频率转换为音符"""
        return self._context.pitch_to_note(pitch, base_freq)

    def analyze_audio_file(self, file_path: str) -> List[str]:
        """分析音频文件并返回音符列表"""
        return self._context.analyze(file_path)

    def start_recording(self, callback=None):
        """开始录音"""
        self.is_recording = True

        def record_audio():
            with sd.InputStream(samplerate=self.sample_rate, channels=1) as stream:
                while self.is_recording:
                    data, overflowed = stream.read(1024)
                    self.audio_queue.put(data[:, 0])

        self.record_thread = threading.Thread(target=record_audio)
        self.record_thread.daemon = True
        self.record_thread.start()

    def stop_recording(self) -> np.ndarray:
        """停止录音并返回音频数据"""
        self.is_recording = False
        audio_data = []

        while not self.audio_queue.empty():
            audio_data.append(self.audio_queue.get())

        if audio_data:
            return np.concatenate(audio_data)
        return np.array([])

    def record_and_analyze(self, duration: float = 5.0) -> List[str]:
        """录音并分析"""
        self.start_recording()

        import time
        time.sleep(duration)

        audio_data = self.stop_recording()

        if len(audio_data) > 0:
            pitch_list = self.detect_pitch(audio_data, self.sample_rate)
            notes = [self.pitch_to_note(pitch) for _, pitch in pitch_list]
            return notes

        return []


class Metronome:
    """节拍器"""

    def __init__(self):
        self.bpm = 80
        self.time_signature = (4, 4)
        self.is_playing = False
        self.beat_callback = None
        self._thread = None

    def set_bpm(self, bpm: int):
        """设置BPM"""
        self.bpm = max(40, min(200, bpm))

    def set_time_signature(self, numerator: int, denominator: int):
        """设置拍号"""
        self.time_signature = (numerator, denominator)

    def play(self, callback=None):
        """开始播放节拍"""
        self.is_playing = True
        self.beat_callback = callback

        def play_beats():
            import time

            beat_interval = 60.0 / self.bpm
            beat_count = 0

            while self.is_playing:
                is_downbeat = (beat_count % self.time_signature[0] == 0)

                if self.beat_callback:
                    self.beat_callback(beat_count, is_downbeat)

                beat_count += 1
                time.sleep(beat_interval)

        self._thread = threading.Thread(target=play_beats)
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        """停止播放"""
        self.is_playing = False