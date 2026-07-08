"""节奏训练服务"""
import time
import threading
from typing import List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class TimeSignature(Enum):
    """拍号"""
    TWO_FOUR = (2, 4)      # 2/4
    THREE_FOUR = (3, 4)    # 3/4
    FOUR_FOUR = (4, 4)     # 4/4
    SIX_EIGHT = (6, 8)     # 6/8


@dataclass
class BeatPattern:
    """节拍模式"""
    name: str
    time_signature: TimeSignature
    accents: List[float]  # 每拍的强弱 (0.0-1.0)
    description: str = ""


# 预设节拍模式
BEAT_PATTERNS = {
    "4/4_pop": BeatPattern(
        name="4/4 流行",
        time_signature=TimeSignature.FOUR_FOUR,
        accents=[1.0, 0.6, 0.8, 0.6],
        description="强-弱-次强-弱"
    ),
    "4/4_rock": BeatPattern(
        name="4/4 摇滚",
        time_signature=TimeSignature.FOUR_FOUR,
        accents=[1.0, 0.3, 1.0, 0.3],
        description="强-弱-强-弱"
    ),
    "3/4_waltz": BeatPattern(
        name="3/4 华尔兹",
        time_signature=TimeSignature.THREE_FOUR,
        accents=[1.0, 0.5, 0.5],
        description="强-弱-弱"
    ),
    "2/4_march": BeatPattern(
        name="2/4 进行曲",
        time_signature=TimeSignature.TWO_FOUR,
        accents=[1.0, 0.6],
        description="强-弱"
    ),
    "6/8_ballad": BeatPattern(
        name="6/8 抒情",
        time_signature=TimeSignature.SIX_EIGHT,
        accents=[1.0, 0.4, 0.4, 0.7, 0.4, 0.4],
        description="强-弱-弱-次强-弱-弱"
    ),
}


@dataclass
class RhythmExercise:
    """节奏练习"""
    name: str
    description: str
    pattern: BeatPattern
    bpm_range: tuple = (60, 120)
    difficulty: int = 1  # 1-5


# 预设练习
RHYTHM_EXERCISES = [
    RhythmExercise(
        name="基础4/4拍",
        description="熟悉4/4拍的基本节奏",
        pattern=BEAT_PATTERNS["4/4_pop"],
        bpm_range=(60, 100),
        difficulty=1
    ),
    RhythmExercise(
        name="华尔兹节奏",
        description="练习3/4拍的圆舞曲节奏",
        pattern=BEAT_PATTERNS["3/4_waltz"],
        bpm_range=(80, 120),
        difficulty=2
    ),
    RhythmExercise(
        name="进行曲节奏",
        description="练习2/4拍的进行曲节奏",
        pattern=BEAT_PATTERNS["2/4_march"],
        bpm_range=(100, 140),
        difficulty=2
    ),
    RhythmExercise(
        name="摇滚节奏",
        description="练习4/4拍的摇滚节奏",
        pattern=BEAT_PATTERNS["4/4_rock"],
        bpm_range=(100, 160),
        difficulty=3
    ),
    RhythmExercise(
        name="抒情节奏",
        description="练习6/8拍的抒情节奏",
        pattern=BEAT_PATTERNS["6/8_ballad"],
        bpm_range=(60, 100),
        difficulty=3
    ),
]


class Metronome:
    """节拍器"""

    def __init__(self):
        self.bpm: int = 80
        self.time_signature: tuple = (4, 4)
        self.is_playing: bool = False
        self.beat_callback: Optional[Callable] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def set_bpm(self, bpm: int):
        """设置BPM"""
        self.bpm = max(40, min(240, bpm))

    def set_time_signature(self, numerator: int, denominator: int):
        """设置拍号"""
        self.time_signature = (numerator, denominator)

    def play(self, callback: Optional[Callable] = None):
        """开始播放节拍"""
        if self.is_playing:
            return

        self.is_playing = True
        self._stop_event.clear()
        self.beat_callback = callback

        self._thread = threading.Thread(target=self._play_loop, daemon=True)
        self._thread.start()

    def _play_loop(self):
        """节拍播放循环"""
        beat_interval = 60.0 / self.bpm
        beat_count = 0

        while not self._stop_event.is_set():
            is_downbeat = (beat_count % self.time_signature[0] == 0)

            if self.beat_callback:
                self.beat_callback(beat_count, is_downbeat)

            beat_count += 1
            self._stop_event.wait(beat_interval)

    def stop(self):
        """停止播放"""
        self.is_playing = False
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1)
            self._thread = None

    def tap(self) -> float:
        """打Tap，返回检测到的BPM"""
        current_time = time.time()
        if not hasattr(self, '_tap_times'):
            self._tap_times = []

        self._tap_times.append(current_time)

        # 只保留最近8次点击
        if len(self._tap_times) > 8:
            self._tap_times = self._tap_times[-8:]

        # 计算平均间隔
        if len(self._tap_times) >= 2:
            intervals = []
            for i in range(1, len(self._tap_times)):
                intervals.append(self._tap_times[i] - self._tap_times[i-1])
            avg_interval = sum(intervals) / len(intervals)
            bpm = 60.0 / avg_interval
            return round(bpm)

        return 0

    def reset_tap(self):
        """重置Tap"""
        self._tap_times = []


class RhythmCoach:
    """节奏教练"""

    def __init__(self):
        self.metronome = Metronome()
        self.current_exercise: Optional[RhythmExercise] = None
        self.practice_history: List[dict] = []

    def start_exercise(self, exercise: RhythmExercise, bpm: int = None):
        """开始练习"""
        self.current_exercise = exercise
        self.metronome.set_time_signature(*exercise.pattern.time_signature.value)
        self.metronome.set_bpm(bpm or exercise.bpm_range[0])

    def set_pattern(self, pattern: BeatPattern):
        """设置节拍模式"""
        self.metronome.set_time_signature(*pattern.time_signature.value)

    def start(self, callback: Callable = None):
        """开始节拍"""
        self.metronome.play(callback)

    def stop(self):
        """停止节拍"""
        self.metronome.stop()

    def record_practice(self, duration: float, accuracy: float = None):
        """记录练习"""
        self.practice_history.append({
            'exercise': self.current_exercise.name if self.current_exercise else "自由练习",
            'duration': duration,
            'accuracy': accuracy,
            'bpm': self.metronome.bpm,
            'timestamp': time.time()
        })

    def get_practice_stats(self) -> dict:
        """获取练习统计"""
        if not self.practice_history:
            return {"total_time": 0, "total_sessions": 0}

        total_time = sum(p['duration'] for p in self.practice_history)
        accuracies = [p['accuracy'] for p in self.practice_history if p['accuracy'] is not None]
        avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else None

        return {
            "total_time": total_time,
            "total_sessions": len(self.practice_history),
            "avg_accuracy": avg_accuracy,
            "total_minutes": round(total_time / 60, 1)
        }


# 全局节奏教练实例
rhythm_coach = RhythmCoach()