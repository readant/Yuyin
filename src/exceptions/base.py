"""基础异常类"""


class YuyinException(Exception):
    """余音应用基础异常"""

    def __init__(self, message: str = "", code: str = None):
        self.message = message
        self.code = code
        super().__init__(self.message)

    def __str__(self):
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message


class NotFoundError(YuyinException):
    """资源不存在"""

    def __init__(self, resource: str, resource_id=None):
        msg = f"{resource}不存在"
        if resource_id:
            msg = f"{resource}(ID: {resource_id})不存在"
        super().__init__(msg, "NOT_FOUND")


class ValidationError(YuyinException):
    """数据验证错误"""

    def __init__(self, field: str, message: str):
        super().__init__(f"验证错误: {field} - {message}", "VALIDATION_ERROR")
        self.field = field