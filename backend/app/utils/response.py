"""统一响应格式"""
from typing import TypeVar, Generic, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")


class Result(BaseModel, Generic[T]):
    """统一 API 响应体，对应 Java 的 Result<T>"""
    code: int = 1
    msg: str = "success"
    data: Optional[T] = None

    @classmethod
    def success(cls, data: Any = None) -> "Result":
        return cls(code=1, msg="success", data=data)

    @classmethod
    def error(cls, msg: str = "error") -> "Result":
        return cls(code=0, msg=msg, data=None)
