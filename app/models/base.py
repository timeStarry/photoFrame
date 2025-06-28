from sqlalchemy import BigInteger, Column, DateTime, func
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class BaseModel(SQLModel):
    """基础模型类，包含通用字段"""
    __abstract__ = True

    id: Optional[int] = Field(
        default=None, 
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True)
    )
    create_time: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    )
    update_time: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    ) 