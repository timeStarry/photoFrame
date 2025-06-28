from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from .base import BaseModel

class FrameType(str, Enum):
    WHITE_FRAME = "white_frame"
    BLUR_FRAME = "blur_frame"
    DEPTH_COLOR_CARD = "depth_color_card"

class WatermarkType(str, Enum):
    ARTISTIC = "artistic"
    COPYRIGHT = "copyright"

class PositionType(str, Enum):
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    CENTER = "center"

class WatermarkTemplateBase(SQLModel):
    name: str
    watermark_type: WatermarkType
    frame_type: FrameType
    font_family: str
    font_size: int = Field(default=24)
    font_color: str = Field(default="#FFFFFF")
    position: PositionType = Field(default=PositionType.BOTTOM_RIGHT)
    opacity: float = Field(default=0.8, ge=0.0, le=1.0)
    margin_x: int = Field(default=20)
    margin_y: int = Field(default=20)
    logo_path: Optional[str] = Field(default=None)
    is_public: bool = Field(default=False)

class WatermarkTemplate(WatermarkTemplateBase, BaseModel, table=True):
    user_id: int = Field(foreign_key="user.id")

class WatermarkTemplateCreate(WatermarkTemplateBase):
    user_id: int

class WatermarkTemplateRead(WatermarkTemplateBase):
    id: int
    user_id: int
    create_time: datetime
    update_time: Optional[datetime] = None

class WatermarkTemplateUpdate(SQLModel):
    name: Optional[str] = None
    font_family: Optional[str] = None
    font_size: Optional[int] = None
    font_color: Optional[str] = None
    position: Optional[PositionType] = None
    opacity: Optional[float] = None
    margin_x: Optional[int] = None
    margin_y: Optional[int] = None
    logo_path: Optional[str] = None
    is_public: Optional[bool] = None

# 水印处理请求模型
class WatermarkRequest(SQLModel):
    image_id: int
    template_id: Optional[int] = None
    custom_text: Optional[str] = None
    custom_config: Optional[Dict[str, Any]] = None 