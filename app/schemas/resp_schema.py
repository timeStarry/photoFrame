from typing import Any, Dict, Optional, TypeVar, Generic, Callable
from pydantic import BaseModel
from functools import wraps
from fastapi import HTTPException

T = TypeVar('T')

class BaseResponse(BaseModel, Generic[T]):
    """基础响应模型"""
    code: int = 200
    message: str = "success"
    data: Optional[T] = None

class ErrorResponse(BaseModel):
    """错误响应模型"""
    code: int
    message: str
    detail: Optional[str] = None

class SuccessResponse(BaseResponse[T]):
    """成功响应模型"""
    pass

class PageResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    total: int
    page: int
    size: int
    pages: int
    items: list[T]

class PagedResponse(BaseResponse[PageResponse[T]]):
    """分页数据响应模型"""
    pass

def response_model(success_model: type = None, error_model: type = ErrorResponse):
    """
    响应模型装饰器
    
    Args:
        success_model: 成功时的数据模型
        error_model: 错误时的响应模型
    
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                
                # 如果结果已经是BaseResponse类型，直接返回
                if isinstance(result, BaseResponse):
                    return result
                
                # 如果指定了成功模型，则包装数据
                if success_model:
                    return SuccessResponse[success_model](data=result)
                else:
                    return SuccessResponse(data=result)
                    
            except HTTPException as e:
                return ErrorResponse(
                    code=e.status_code,
                    message=str(e.detail),
                    detail=str(e.detail)
                )
            except Exception as e:
                return ErrorResponse(
                    code=500,
                    message="内部服务器错误",
                    detail=str(e)
                )
        
        # 如果是同步函数，使用同步包装器
        if not hasattr(func, '__await__'):
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    result = func(*args, **kwargs)
                    
                    if isinstance(result, BaseResponse):
                        return result
                    
                    if success_model:
                        return SuccessResponse[success_model](data=result)
                    else:
                        return SuccessResponse(data=result)
                        
                except HTTPException as e:
                    return ErrorResponse(
                        code=e.status_code,
                        message=str(e.detail),
                        detail=str(e.detail)
                    )
                except Exception as e:
                    return ErrorResponse(
                        code=500,
                        message="内部服务器错误",
                        detail=str(e)
                    )
            return sync_wrapper
        
        return wrapper
    return decorator

def success_response(data: Any = None, message: str = "操作成功") -> SuccessResponse:
    """创建成功响应"""
    return SuccessResponse(data=data, message=message)

def error_response(code: int = 500, message: str = "操作失败", detail: str = None) -> ErrorResponse:
    """创建错误响应"""
    return ErrorResponse(code=code, message=message, detail=detail)

def paged_response(items: list, total: int, page: int, size: int, message: str = "获取成功") -> PagedResponse:
    """创建分页响应"""
    pages = (total + size - 1) // size  # 计算总页数
    page_data = PageResponse(
        total=total,
        page=page,
        size=size,
        pages=pages,
        items=items
    )
    return PagedResponse(data=page_data, message=message) 