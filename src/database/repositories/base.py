"""仓储基类"""
from typing import TypeVar, Generic, List, Optional, Type
from sqlalchemy.orm import Session

from ..models import Base, DatabaseManager

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """仓储基类"""

    def __init__(self, db: DatabaseManager, model: Type[ModelType]):
        self.db = db
        self.model = model

    def get_session(self) -> Session:
        return self.db.get_session()

    def get_by_id(self, id: int) -> Optional[ModelType]:
        """根据ID获取"""
        session = self.get_session()
        try:
            return session.query(self.model).filter(self.model.id == id).first()
        finally:
            session.close()

    def get_all(self) -> List[ModelType]:
        """获取所有"""
        session = self.get_session()
        try:
            return session.query(self.model).all()
        finally:
            session.close()

    def create(self, **kwargs) -> ModelType:
        """创建"""
        session = self.get_session()
        try:
            obj = self.model(**kwargs)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """更新"""
        session = self.get_session()
        try:
            obj = session.query(self.model).filter(self.model.id == id).first()
            if obj:
                for key, value in kwargs.items():
                    setattr(obj, key, value)
                session.commit()
                session.refresh(obj)
            return obj
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    def delete(self, id: int) -> bool:
        """删除"""
        session = self.get_session()
        try:
            obj = session.query(self.model).filter(self.model.id == id).first()
            if obj:
                session.delete(obj)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    def count(self) -> int:
        """计数"""
        session = self.get_session()
        try:
            return session.query(self.model).count()
        finally:
            session.close()

    def exists(self, id: int) -> bool:
        """检查是否存在"""
        session = self.get_session()
        try:
            return session.query(self.model).filter(self.model.id == id).first() is not None
        finally:
            session.close()