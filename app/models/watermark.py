from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class FrameType(str, Enum):
    WHITE_FRAME = "white_frame"
    BLUR_FRAME = "blur_frame"
    DEPTH_COLOR_CARD = "depth_color_card"

class WatermarkType(str, Enum):
    ARTISTIC = "artistic"
    COPYRIGHT = "copyright"

class PositionType(str, Enum):
    """九宫格位置定义"""
    TOP_LEFT = "top_left"           # 左上
    TOP_CENTER = "top_center"       # 正上
    TOP_RIGHT = "top_right"         # 右上
    MIDDLE_LEFT = "middle_left"     # 左中
    MIDDLE_CENTER = "middle_center" # 正中
    MIDDLE_RIGHT = "middle_right"   # 右中
    BOTTOM_LEFT = "bottom_left"     # 左下
    BOTTOM_CENTER = "bottom_center" # 正下
    BOTTOM_RIGHT = "bottom_right"   # 右下

class WatermarkTemplateBase(SQLModel):
    name: str
    watermark_type: WatermarkType
    frame_type: FrameType
    font_family: str
    font_size: int = Field(default=24, description="字体大小(像素)")
    font_color: str = Field(default="#FFFFFF", description="字体颜色")
    position: PositionType = Field(default=PositionType.BOTTOM_RIGHT, description="水印位置(九宫格)")
    opacity: float = Field(default=0.8, ge=0.0, le=1.0, description="透明度(0-1)")
    margin_x_percent: float = Field(default=2.0, ge=0.0, le=50.0, description="水平边距(图片宽度百分比)")
    margin_y_percent: float = Field(default=2.0, ge=0.0, le=50.0, description="垂直边距(图片高度百分比)")
    logo_path: Optional[str] = Field(default=None, description="Logo图片路径")
    is_public: bool = Field(default=False, description="是否为公共模板")

class WatermarkTemplate(WatermarkTemplateBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

class WatermarkTemplateCreate(WatermarkTemplateBase):
    user_id: int

class WatermarkTemplateRead(WatermarkTemplateBase):
    id: int
    user_id: int
    created_at: datetime

class WatermarkTemplateUpdate(SQLModel):
    name: Optional[str] = None
    font_family: Optional[str] = None
    font_size: Optional[int] = None
    font_color: Optional[str] = None
    position: Optional[PositionType] = None
    opacity: Optional[float] = None
    margin_x_percent: Optional[float] = Field(default=None, ge=0.0, le=50.0)
    margin_y_percent: Optional[float] = Field(default=None, ge=0.0, le=50.0)
    logo_path: Optional[str] = None
    is_public: Optional[bool] = None

# 水印处理请求模型
class WatermarkRequest(SQLModel):
    image_id: int
    template_id: Optional[int] = None
    custom_text: Optional[str] = None
    custom_config: Optional[Dict[str, Any]] = None 