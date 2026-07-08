"""数据库相关异常"""
from .base import YuyinException


class DatabaseError(YuyinException):
    """数据库操作基础异常"""
    pass


class DatabaseConnectionError(DatabaseError):
    """数据库连接失败"""

    def __init__(self, db_path: str = "", reason: str = ""):
        msg = "数据库连接失败"
        if db_path:
            msg = f"无法连接数据库: {db_path}"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg, "DB_CONNECTION_ERROR")