"""乐谱仓储"""
from typing import List, Optional

from ..models import Score, DatabaseManager
from .base import BaseRepository


class ScoreRepository(BaseRepository[Score]):
    """乐谱仓储"""

    def __init__(self, db: DatabaseManager):
        super().__init__(db, Score)

    def get_by_title(self, title: str) -> Optional[Score]:
        """根据标题获取"""
        session = self.get_session()
        try:
            return session.query(Score).filter(Score.title == title).first()
        finally:
            session.close()

    def search(self, keyword: str) -> List[Score]:
        """搜索乐谱"""
        session = self.get_session()
        try:
            return session.query(Score).filter(
                Score.title.contains(keyword)
            ).all()
        finally:
            session.close()

    def get_by_key(self, key: str) -> List[Score]:
        """根据调性获取"""
        session = self.get_session()
        try:
            return session.query(Score).filter(Score.key_signature == key).all()
        finally:
            session.close()

    def get_recent(self, limit: int = 10) -> List[Score]:
        """获取最近的乐谱"""
        session = self.get_session()
        try:
            return session.query(Score).order_by(
                Score.created_at.desc()
            ).limit(limit).all()
        finally:
            session.close()