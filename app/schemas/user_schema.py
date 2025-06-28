from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserResponseSchema(BaseModel):
    """用户响应"""
    id: int
    username: str
    email: str
    is_active: bool
    create_time: datetime
    update_time: Optional[datetime] = None

class UserListResponseSchema(BaseModel):
    """用户列表响应"""
    users: list[UserResponseSchema]
    total: int 