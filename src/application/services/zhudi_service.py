"""竹笛学习服务"""
import time
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path

from ...domain.models.notes import (
    Note, KEY_CONFIGS, get_fingering_map, get_fingering_display,
    get_all_notes_for_fingering, parse_notes
)


@dataclass
class ScoreTimeline:
    """简谱时间轴"""
    notes: List[dict]  # [{value, start_time, duration, fingering}, ...]
    total_duration: float = 0.0
    bpm: int = 80

    @classmethod
    def from_notes(cls, notes: List[Note], bpm: int = 80) -> 'ScoreTimeline':
        """从音符列表创建时间轴"""
        timeline = []
        current_time = 0.0
        beat_duration = 60.0 / bpm

        for note in notes:
            if note.is_bar or note.is_space:
                continue

            timeline.append({
                'value': note.value,
                'start_time': current_time,
                'duration': beat_duration * note.duration,
                'index': len(timeline)
            })
            current_time += beat_duration * note.duration

        return cls(notes=timeline, total_duration=current_time, bpm=bpm)

    def get_current_note(self, current_time: float) -> Optional[dict]:
        """根据当前时间获取当前音符"""
        for note in self.notes:
            if note['start_time'] <= current_time < note['start_time'] + note['duration']:
                return note
        return None

    def get_note_at_index(self, index: int) -> Optional[dict]:
        """根据索引获取音符"""
        if 0 <= index < len(self.notes):
            return self.notes[index]
        return None


@dataclass
class PracticeRecord:
    """练习记录"""
    score_id: int
    score_title: str
    duration: float  # 练习时长（秒）
    notes_played: int  # 弹奏的音符数
    accuracy: float  # 准确率（0-100）
    timestamp: float = field(default_factory=time.time)
    key: str = "D"
    fingering: str = "5"


class ZhudiService:
    """竹笛学习服务"""

    def __init__(self):
        self.current_timeline: Optional[ScoreTimeline] = None
        self.current_key: str = "D"
        self.current_fingering: str = "5"
        self.practice_records: List[PracticeRecord] = []
        self._load_practice_records()

    def set_key(self, key: str):
        """设置调性"""
        self.current_key = key

    def set_fingering(self, fingering: str):
        """设置指法类型"""
        self.current_fingering = fingering

    def load_score(self, notes: List[Note], bpm: int = 80) -> ScoreTimeline:
        """加载简谱"""
        self.current_timeline = ScoreTimeline.from_notes(notes, bpm)
        return self.current_timeline

    def get_fingering(self, note_value: str) -> List[int]:
        """获取音符的指法"""
        fingering_map = get_fingering_map(self.current_fingering)
        return fingering_map.get(note_value, [0, 0, 0, 0, 0, 0])

    def get_fingering_display(self, note_value: str) -> str:
        """获取音符的指法显示"""
        fingering = self.get_fingering(note_value)
        return get_fingering_display(fingering)

    def get_all_notes(self) -> List[str]:
        """获取所有可用音符"""
        return get_all_notes_for_fingering(self.current_fingering)

    def get_key_info(self) -> dict:
        """获取当前调性信息"""
        return KEY_CONFIGS.get(self.current_key, {})

    def record_practice(self, score_id: int, score_title: str,
                       duration: float, notes_played: int, accuracy: float):
        """记录练习"""
        record = PracticeRecord(
            score_id=score_id,
            score_title=score_title,
            duration=duration,
            notes_played=notes_played,
            accuracy=accuracy,
            key=self.current_key,
            fingering=self.current_fingering
        )
        self.practice_records.append(record)
        self._save_practice_records()

    def get_practice_stats(self) -> dict:
        """获取练习统计"""
        if not self.practice_records:
            return {
                'total_time': 0,
                'total_sessions': 0,
                'avg_accuracy': 0,
                'total_notes': 0
            }

        total_time = sum(r.duration for r in self.practice_records)
        total_notes = sum(r.notes_played for r in self.practice_records)
        accuracies = [r.accuracy for r in self.practice_records if r.accuracy > 0]
        avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0

        return {
            'total_time': total_time,
            'total_time_formatted': self._format_time(total_time),
            'total_sessions': len(self.practice_records),
            'avg_accuracy': round(avg_accuracy, 1),
            'total_notes': total_notes
        }

    def get_recent_practices(self, limit: int = 10) -> List[PracticeRecord]:
        """获取最近的练习记录"""
        return sorted(self.practice_records, key=lambda r: r.timestamp, reverse=True)[:limit]

    def _format_time(self, seconds: float) -> str:
        """格式化时间"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        if hours > 0:
            return f"{hours}小时{minutes}分钟"
        return f"{minutes}分钟"

    def _load_practice_records(self):
        """加载练习记录"""
        records_file = Path("data/practice_records.json")
        if records_file.exists():
            try:
                with open(records_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.practice_records = [PracticeRecord(**r) for r in data]
            except Exception:
                self.practice_records = []

    def _save_practice_records(self):
        """保存练习记录"""
        records_file = Path("data/practice_records.json")
        records_file.parent.mkdir(exist_ok=True)

        data = []
        for record in self.practice_records:
            data.append({
                'score_id': record.score_id,
                'score_title': record.score_title,
                'duration': record.duration,
                'notes_played': record.notes_played,
                'accuracy': record.accuracy,
                'timestamp': record.timestamp,
                'key': record.key,
                'fingering': record.fingering
            })

        with open(records_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


# 全局竹笛学习服务实例
zhudi_service = ZhudiService()