"""数据库连接管理"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from typing import Optional

from ...config import settings


class DatabaseConnection:
    """数据库连接管理"""

    _instance = None
    _engine = None
    _session_factory = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._setup_connection()

    def _setup_connection(self):
        """设置数据库连接"""
        db_path = settings.database.path
        self._engine = create_engine(
            f'sqlite:///{db_path}',
            echo=settings.database.echo,
            connect_args={'check_same_thread': False}
        )
        self._session_factory = sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False
        )

    @property
    def engine(self):
        """获取数据库引擎"""
        return self._engine

    def get_session(self):
        """获取数据库会话"""
        return self._session_factory()

    def create_all(self):
        """创建所有表"""
        from ...domain.models.database import Base
        Base.metadata.create_all(self._engine)

    def drop_all(self):
        """删除所有表"""
        from ...domain.models.database import Base
        Base.metadata.drop_all(self._engine)


# 全局数据库连接实例
db_connection = DatabaseConnection()