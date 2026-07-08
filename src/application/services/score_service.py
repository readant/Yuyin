"""乐谱服务"""
from typing import List, Optional
from ..database.models import DatabaseManager


class ScoreService:
    """乐谱业务服务"""

    def __init__(self, db: DatabaseManager = None):
        self.db = db or DatabaseManager("data/zhudi.db")

    def get_all_scores(self) -> List[dict]:
        """获取所有乐谱"""
        scores = self.db.get_all_scores()
        return [
            {
                'id': s.id,
                'title': s.title,
                'artist': s.artist or '未知',
                'key': s.key_signature or 'D',
            }
            for s in scores
        ]

    def search_scores(self, keyword: str) -> List[dict]:
        """搜索乐谱"""
        all_scores = self.get_all_scores()
        if not keyword:
            return all_scores
        return [s for s in all_scores if keyword.lower() in s['title'].lower()]

    def add_score(self, title: str, artist: str = None, key: str = 'D') -> int:
        """添加乐谱"""
        return self.db.add_score(title=title, artist=artist, key_signature=key)

    def delete_score(self, score_id: int) -> bool:
        """删除乐谱"""
        try:
            self.db.delete_score(score_id)
            return True
        except Exception:
            return False