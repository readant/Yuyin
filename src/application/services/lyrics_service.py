"""歌词服务"""
import re
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class LyricLine:
    """歌词行"""
    time: float  # 时间戳（秒）
    text: str
    index: int = 0  # 行号

    def to_lrc(self) -> str:
        """转换为LRC格式"""
        minutes = int(self.time // 60)
        seconds = int(self.time % 60)
        milliseconds = int((self.time % 1) * 1000)
        return f"[{minutes:02d}:{seconds:02d}.{milliseconds:03d}]{self.text}"


class LyricsParser:
    """歌词解析器"""

    # LRC格式正则
    LRC_PATTERN = re.compile(r'\[(\d{2}):(\d{2})\.(\d{2,3})\](.*)')

    @staticmethod
    def parse_lrc(content: str) -> List[LyricLine]:
        """解析LRC格式歌词"""
        lines = []
        for i, line in enumerate(content.split('\n')):
            match = LyricsParser.LRC_PATTERN.match(line.strip())
            if match:
                minutes = int(match.group(1))
                seconds = int(match.group(2))
                milliseconds = int(match.group(3).ljust(3, '0'))
                text = match.group(4).strip()

                time = minutes * 60 + seconds + milliseconds / 1000
                if text:  # 忽略空行
                    lines.append(LyricLine(time=time, text=text, index=len(lines)))

        lines.sort(key=lambda x: x.time)
        return lines

    @staticmethod
    def parse_simple(content: str) -> List[LyricLine]:
        """解析简单格式歌词（每行一句）"""
        lines = []
        for i, line in enumerate(content.split('\n')):
            text = line.strip()
            if text:
                lines.append(LyricLine(time=i * 3.0, text=text, index=i))
        return lines

    @staticmethod
    def to_lrc(lines: List[LyricLine]) -> str:
        """将歌词行列表转换为LRC格式字符串"""
        sorted_lines = sorted(lines, key=lambda x: x.time)
        return '\n'.join(line.to_lrc() for line in sorted_lines)


class LyricsManager:
    """歌词管理器"""

    def __init__(self):
        self._lyrics: List[LyricLine] = []
        self._current_index: int = -1
        self._file_path: Optional[str] = None

    @property
    def lyrics(self) -> List[LyricLine]:
        return self._lyrics.copy()

    @property
    def current_line(self) -> Optional[LyricLine]:
        if 0 <= self._current_index < len(self._lyrics):
            return self._lyrics[self._current_index]
        return None

    @property
    def current_index(self) -> int:
        return self._current_index

    @property
    def has_lyrics(self) -> bool:
        return len(self._lyrics) > 0

    @property
    def file_path(self) -> Optional[str]:
        return self._file_path

    @property
    def count(self) -> int:
        return len(self._lyrics)

    def load_from_file(self, file_path: str) -> bool:
        """从文件加载歌词"""
        try:
            path = Path(file_path)
            if path.exists() and path.suffix.lower() == '.lrc':
                content = path.read_text(encoding='utf-8')
                self._lyrics = LyricsParser.parse_lrc(content)
                self._file_path = file_path
                return True
        except Exception:
            pass
        return False

    def load_from_text(self, text: str, format: str = 'lrc') -> bool:
        """从文本加载歌词"""
        if format == 'lrc':
            self._lyrics = LyricsParser.parse_lrc(text)
        else:
            self._lyrics = LyricsParser.parse_simple(text)
        self._file_path = None
        return len(self._lyrics) > 0

    def save_to_file(self, file_path: str) -> bool:
        """保存歌词到文件"""
        try:
            content = LyricsParser.to_lrc(self._lyrics)
            Path(file_path).write_text(content, encoding='utf-8')
            self._file_path = file_path
            return True
        except Exception:
            return False

    def save(self) -> bool:
        """保存到当前文件"""
        if self._file_path:
            return self.save_to_file(self._file_path)
        return False

    def clear(self):
        """清空歌词"""
        self._lyrics.clear()
        self._current_index = -1
        self._file_path = None

    def add_line(self, time: float, text: str, index: int = -1) -> LyricLine:
        """添加歌词行"""
        if index < 0:
            index = len(self._lyrics)
        line = LyricLine(time=time, text=text, index=index)
        self._lyrics.append(line)
        self._lyrics.sort(key=lambda x: x.time)
        self._reindex()
        return line

    def remove_line(self, index: int) -> bool:
        """删除歌词行"""
        if 0 <= index < len(self._lyrics):
            self._lyrics.pop(index)
            self._reindex()
            return True
        return False

    def update_line(self, index: int, time: float = None, text: str = None) -> bool:
        """更新歌词行"""
        if 0 <= index < len(self._lyrics):
            if time is not None:
                self._lyrics[index].time = time
            if text is not None:
                self._lyrics[index].text = text
            self._lyrics.sort(key=lambda x: x.time)
            self._reindex()
            return True
        return False

    def _reindex(self):
        """重新索引"""
        for i, line in enumerate(self._lyrics):
            line.index = i

    def search(self, keyword: str) -> List[Tuple[int, LyricLine]]:
        """搜索歌词"""
        keyword = keyword.lower()
        results = []
        for i, line in enumerate(self._lyrics):
            if keyword in line.text.lower():
                results.append((i, line))
        return results

    def update_position(self, current_time: float) -> Optional[LyricLine]:
        """根据播放时间更新当前歌词行"""
        if not self._lyrics:
            return None

        # 找到当前时间对应的歌词行
        new_index = -1
        for i, line in enumerate(self._lyrics):
            if line.time <= current_time:
                new_index = i
            else:
                break

        if new_index != self._current_index:
            self._current_index = new_index
            return self.current_line

        return None

    def get_lyrics_for_display(self, center_index: int = 5, count: int = 11) -> List[Tuple[int, LyricLine, bool]]:
        """获取用于显示的歌词列表

        Returns:
            [(index, line, is_current), ...]
        """
        result = []
        start = max(0, self._current_index - center_index)
        end = min(len(self._lyrics), start + count)

        for i in range(start, end):
            is_current = (i == self._current_index)
            result.append((i, self._lyrics[i], is_current))

        return result

    def get_all_as_text(self) -> str:
        """获取所有歌词文本"""
        return LyricsParser.to_lrc(self._lyrics)


# 全局歌词管理器实例
lyrics_manager = LyricsManager()