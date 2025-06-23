from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

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

class Image(ImageBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    exif_data: Optional[str] = Field(default=None)  # JSON格式存储EXIF信息
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

class ImageCreate(ImageBase):
    user_id: int

class ImageRead(ImageBase):
    id: int
    user_id: int
    created_at: datetime
    exif_data: Optional[Dict[str, Any]] = None

class ImageUpdate(SQLModel):
    filename: Optional[str] = None
    status: Optional[ImageStatus] = None 