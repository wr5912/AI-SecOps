"""
API响应封装模型
遵循设计文档规范的统一响应格式
"""
from pydantic import BaseModel
from typing import Any, Optional, Generic, TypeVar

T = TypeVar('T')


class APIResponse(BaseModel):
    """统一API响应格式 - 遵循设计文档规范"""
    trace_id: str
    success: bool
    data: Any
    meta: dict = {}


class PaginatedResponse(BaseModel):
    """分页响应基类"""
    total: int
    page: int
    page_size: int


class ErrorDetail(BaseModel):
    """错误详情"""
    code: str
    message: str
    details: Optional[dict] = None


class APIErrorResponse(BaseModel):
    """统一错误响应格式"""
    trace_id: str
    success: bool = False
    error: str
    detail: Optional[ErrorDetail] = None
