"""音乐服务 - 本地音乐库管理"""
import os
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

from ...shared.exceptions import AudioLoadError
from ...domain.models.database import DatabaseManager


@dataclass
class Track:
    """曲目信息"""
    id: int
    title: str
    artist: str
    album: str
    duration: float
    file_path: str
    file_size: int

    @property
    def display_name(self) -> str:
        return f"{self.title} - {self.artist}"


class MusicLibrary:
    """本地音乐库"""

    SUPPORTED_FORMATS = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.wma'}

    def __init__(self):
        self._tracks: List[Track] = []
        self._scan_dirs: List[str] = []
        self._id_counter = 0
        self._db = DatabaseManager()
        # 启动时从数据库恢复扫描目录
        self._load_scan_dirs()

    @property
    def tracks(self) -> List[Track]:
        return self._tracks.copy()

    @property
    def count(self) -> int:
        return len(self._tracks)

    def add_scan_directory(self, dir_path: str):
        """添加扫描目录"""
        if os.path.isdir(dir_path) and dir_path not in self._scan_dirs:
            self._scan_dirs.append(dir_path)
            self._db.add_scan_directory(dir_path)

    def remove_scan_directory(self, dir_path: str):
        """移除扫描目录"""
        if dir_path in self._scan_dirs:
            self._scan_dirs.remove(dir_path)
            self._db.remove_scan_directory(dir_path)

    def clear_scan_directories(self):
        """清空所有扫描目录"""
        self._scan_dirs.clear()
        self._db.clear_scan_directories()

    def _load_scan_dirs(self):
        """从数据库加载扫描目录"""
        try:
            dirs = self._db.get_scan_directories()
            # 只加载仍然存在的目录
            self._scan_dirs = [d for d in dirs if os.path.isdir(d)]
        except Exception:
            self._scan_dirs = []

    def get_scan_directories(self) -> List[str]:
        """获取扫描目录列表"""
        return self._scan_dirs.copy()

    def scan(self, callback=None) -> int:
        """扫描音乐库

        Args:
            callback: 扫描进度回调 (file_path, current, total)

        Returns:
            扫描到的曲目数量
        """
        self._tracks.clear()
        self._id_counter = 0

        # 收集所有音乐文件
        all_files = []
        for scan_dir in self._scan_dirs:
            if os.path.isdir(scan_dir):
                for root, dirs, files in os.walk(scan_dir):
                    for f in files:
                        if Path(f).suffix.lower() in self.SUPPORTED_FORMATS:
                            all_files.append(os.path.join(root, f))

        # 处理每个文件
        total = len(all_files)
        for i, file_path in enumerate(all_files):
            if callback:
                callback(file_path, i + 1, total)

            track = self._create_track(file_path)
            if track:
                self._tracks.append(track)

        # 按标题排序
        self._tracks.sort(key=lambda t: t.title.lower())

        return len(self._tracks)

    def _create_track(self, file_path: str) -> Optional[Track]:
        """创建曲目信息"""
        try:
            # 尝试从文件名提取信息
            file_name = Path(file_path).stem
            file_size = os.path.getsize(file_path)

            # 简单解析 "艺术家 - 标题" 格式
            if ' - ' in file_name:
                parts = file_name.split(' - ', 1)
                artist = parts[0].strip()
                title = parts[1].strip()
            else:
                artist = "未知艺术家"
                title = file_name

            # 获取时长（简单估算，实际应该用mutagen等库）
            duration = self._estimate_duration(file_path)

            self._id_counter += 1
            return Track(
                id=self._id_counter,
                title=title,
                artist=artist,
                album="未知专辑",
                duration=duration,
                file_path=file_path,
                file_size=file_size
            )
        except Exception:
            return None

    def _estimate_duration(self, file_path: str) -> float:
        """估算音频时长"""
        try:
            # 简单估算：文件大小 / 平均比特率
            file_size = os.path.getsize(file_path)
            # 假设 128kbps 比特率
            estimated_seconds = file_size / (128 * 1024 / 8)
            return min(estimated_seconds, 600)  # 最大10分钟
        except Exception:
            return 0.0

    def get_track_by_id(self, track_id: int) -> Optional[Track]:
        """根据ID获取曲目"""
        for track in self._tracks:
            if track.id == track_id:
                return track
        return None

    def search(self, keyword: str) -> List[Track]:
        """搜索曲目"""
        keyword = keyword.lower()
        return [
            t for t in self._tracks
            if keyword in t.title.lower() or keyword in t.artist.lower()
        ]

    def get_recent_tracks(self, limit: int = 10) -> List[Track]:
        """获取最近播放的曲目"""
        # TODO: 从播放历史获取
        return self._tracks[:limit]

    def get_favorites(self) -> List[Track]:
        """获取收藏曲目"""
        # TODO: 从收藏列表获取
        return []


class Playlist:
    """播放列表"""

    def __init__(self, name: str, playlist_id: int = 0):
        self.id = playlist_id
        self.name = name
        self._tracks: List[Track] = []
        self._current_index = -1

    @property
    def tracks(self) -> List[Track]:
        return self._tracks.copy()

    @property
    def current_track(self) -> Optional[Track]:
        if 0 <= self._current_index < len(self._tracks):
            return self._tracks[self._current_index]
        return None

    @property
    def current_index(self) -> int:
        return self._current_index

    @property
    def count(self) -> int:
        return len(self._tracks)

    def add_track(self, track: Track):
        """添加曲目"""
        self._tracks.append(track)

    def remove_track(self, track_id: int):
        """移除曲目"""
        self._tracks = [t for t in self._tracks if t.id != track_id]

    def clear(self):
        """清空播放列表"""
        self._tracks.clear()
        self._current_index = -1

    def next_track(self) -> Optional[Track]:
        """下一首"""
        if self._tracks:
            self._current_index = (self._current_index + 1) % len(self._tracks)
            return self.current_track
        return None

    def prev_track(self) -> Optional[Track]:
        """上一首"""
        if self._tracks:
            self._current_index = (self._current_index - 1) % len(self._tracks)
            return self.current_track
        return None

    def set_track(self, index: int) -> Optional[Track]:
        """设置当前播放位置"""
        if 0 <= index < len(self._tracks):
            self._current_index = index
            return self.current_track
        return None

    def shuffle(self):
        """随机打乱"""
        import random
        random.shuffle(self._tracks)
        self._current_index = -1


# 全局音乐库实例
music_library = MusicLibrary()