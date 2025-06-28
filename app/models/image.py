from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from .base import BaseModel

class ImageStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ImageBase(SQLModel):
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    width: int
    height: int
    format: str
    status: ImageStatus = Field(default=ImageStatus.UPLOADED)

class Image(ImageBase, BaseModel, table=True):
    user_id: int = Field(foreign_key="user.id")
    exif_data: Optional[str] = Field(default=None)  # JSON格式存储EXIF信息

class ImageCreate(ImageBase):
    user_id: int

class ImageRead(ImageBase):
    id: int
    user_id: int
    create_time: datetime
    update_time: Optional[datetime] = None
    exif_data: Optional[Dict[str, Any]] = None

class ImageUpdate(SQLModel):
    filename: Optional[str] = None
    status: Optional[ImageStatus] = None 