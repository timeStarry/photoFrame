import os
import uuid
from typing import Optional, Tuple
from pathlib import Path
from PIL import Image as PILImage, ImageDraw, ImageFont, ImageFilter
from fastapi import HTTPException
from sqlmodel import Session, select

from ..core.config import settings
from ..models.image import Image, ImageStatus
from ..models.watermark import (
    WatermarkTemplate, FrameType, PositionType, WatermarkRequest
)
from ..models.user import User

class WatermarkService:
    
    @staticmethod
    def get_font(font_family: str, font_size: int) -> ImageFont.FreeTypeFont:
        """获取字体对象"""
        try:
            # 尝试加载指定字体
            font_path = Path("fonts") / f"{font_family}.ttf"
            if font_path.exists():
                return ImageFont.truetype(str(font_path), font_size)
            
            # 尝试系统默认字体
            try:
                return ImageFont.truetype("arial.ttf", font_size)
            except:
                return ImageFont.load_default()
                
        except Exception:
            return ImageFont.load_default()
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """将十六进制颜色转换为RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def calculate_position(
        image_size: Tuple[int, int],
        text_size: Tuple[int, int],
        position: PositionType,
        margin_x_percent: float,
        margin_y_percent: float
    ) -> Tuple[int, int]:
        """计算水印位置 - 支持九宫格定位和百分比边距"""
        img_width, img_height = image_size
        text_width, text_height = text_size
        
        # 将百分比转换为像素值
        margin_x = int(img_width * margin_x_percent / 100)
        margin_y = int(img_height * margin_y_percent / 100)
        
        # 九宫格位置计算
        if position == PositionType.TOP_LEFT:
            return (margin_x, margin_y)
        elif position == PositionType.TOP_CENTER:
            return ((img_width - text_width) // 2, margin_y)
        elif position == PositionType.TOP_RIGHT:
            return (img_width - text_width - margin_x, margin_y)
        elif position == PositionType.MIDDLE_LEFT:
            return (margin_x, (img_height - text_height) // 2)
        elif position == PositionType.MIDDLE_CENTER:
            return ((img_width - text_width) // 2, (img_height - text_height) // 2)
        elif position == PositionType.MIDDLE_RIGHT:
            return (img_width - text_width - margin_x, (img_height - text_height) // 2)
        elif position == PositionType.BOTTOM_LEFT:
            return (margin_x, img_height - text_height - margin_y)
        elif position == PositionType.BOTTOM_CENTER:
            return ((img_width - text_width) // 2, img_height - text_height - margin_y)
        elif position == PositionType.BOTTOM_RIGHT:
            return (img_width - text_width - margin_x, img_height - text_height - margin_y)
        else:
            # 默认右下角
            return (img_width - text_width - margin_x, img_height - text_height - margin_y)
    
    @staticmethod
    def apply_frame(image: PILImage.Image, frame_type: FrameType) -> PILImage.Image:
        """应用相框效果"""
        if frame_type == FrameType.WHITE_FRAME:
            # 白框相框
            frame_width = max(20, min(image.width, image.height) // 20)
            new_width = image.width + 2 * frame_width
            new_height = image.height + 2 * frame_width
            
            framed_image = PILImage.new('RGB', (new_width, new_height), 'white')
            framed_image.paste(image, (frame_width, frame_width))
            return framed_image
            
        elif frame_type == FrameType.BLUR_FRAME:
            # 模糊相框
            frame_width = max(30, min(image.width, image.height) // 15)
            new_width = image.width + 2 * frame_width
            new_height = image.height + 2 * frame_width
            
            # 创建模糊背景
            background = image.resize((new_width, new_height))
            background = background.filter(ImageFilter.GaussianBlur(radius=15))
            
            # 将原图粘贴到中心
            x = (new_width - image.width) // 2
            y = (new_height - image.height) // 2
            background.paste(image, (x, y))
            return background
            
        elif frame_type == FrameType.DEPTH_COLOR_CARD:
            # 景深色卡相框
            frame_width = max(40, min(image.width, image.height) // 12)
            new_width = image.width + 2 * frame_width
            new_height = image.height + 2 * frame_width
            
            # 创建渐变背景
            background = PILImage.new('RGB', (new_width, new_height))
            draw = ImageDraw.Draw(background)
            
            # 简单的径向渐变效果
            center_x, center_y = new_width // 2, new_height // 2
            for y in range(new_height):
                for x in range(new_width):
                    distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                    max_distance = (new_width ** 2 + new_height ** 2) ** 0.5 / 2
                    ratio = min(distance / max_distance, 1.0)
                    
                    # 从中心的深色到边缘的浅色
                    color_value = int(30 + ratio * 50)
                    draw.point((x, y), (color_value, color_value, color_value))
            
            # 将原图粘贴到中心
            x = (new_width - image.width) // 2
            y = (new_height - image.height) // 2
            background.paste(image, (x, y))
            return background
        
        return image
    
    @staticmethod
    def add_text_watermark(
        image: PILImage.Image,
        text: str,
        template: WatermarkTemplate
    ) -> PILImage.Image:
        """添加文字水印"""
        # 创建副本
        watermarked = image.copy()
        
        # 获取字体
        font = WatermarkService.get_font(template.font_family, template.font_size)
        
        # 创建透明层
        txt_layer = PILImage.new('RGBA', image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)
        
        # 获取文字尺寸
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 计算位置
        position = WatermarkService.calculate_position(
            image.size, 
            (text_width, text_height),
            template.position,
            template.margin_x_percent,
            template.margin_y_percent
        )
        
        # 解析颜色
        rgb_color = WatermarkService.hex_to_rgb(template.font_color)
        alpha = int(255 * template.opacity)
        color_with_alpha = rgb_color + (alpha,)
        
        # 绘制文字
        draw.text(position, text, font=font, fill=color_with_alpha)
        
        # 合并图层
        watermarked = PILImage.alpha_composite(watermarked.convert('RGBA'), txt_layer)
        return watermarked.convert('RGB')
    
    @staticmethod
    def add_logo_watermark(
        image: PILImage.Image,
        logo_path: str,
        template: WatermarkTemplate
    ) -> PILImage.Image:
        """添加Logo水印"""
        try:
            logo = PILImage.open(logo_path).convert('RGBA')
            
            # 根据图片大小调整Logo大小
            max_logo_size = min(image.width, image.height) // 4
            if logo.width > max_logo_size or logo.height > max_logo_size:
                logo.thumbnail((max_logo_size, max_logo_size), PILImage.Resampling.LANCZOS)
            
            # 计算位置
            position = WatermarkService.calculate_position(
                image.size,
                logo.size,
                template.position,
                template.margin_x_percent,
                template.margin_y_percent
            )
            
            # 调整透明度
            if template.opacity < 1.0:
                alpha = logo.split()[-1]
                alpha = alpha.point(lambda p: int(p * template.opacity))
                logo.putalpha(alpha)
            
            # 粘贴Logo
            watermarked = image.convert('RGBA')
            watermarked.paste(logo, position, logo)
            return watermarked.convert('RGB')
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Logo处理失败: {str(e)}")
    
    @staticmethod
    async def process_watermark(
        request: WatermarkRequest,
        user: User,
        session: Session
    ) -> str:
        """处理水印请求"""
        # 获取图片
        statement = select(Image).where(Image.id == request.image_id, Image.user_id == user.id)
        image_record = session.exec(statement).first()
        if not image_record:
            raise HTTPException(status_code=404, detail="图片不存在")
        
        # 获取模板
        template = None
        if request.template_id:
            template_statement = select(WatermarkTemplate).where(
                WatermarkTemplate.id == request.template_id,
                (WatermarkTemplate.user_id == user.id) | (WatermarkTemplate.is_public == True)
            )
            template = session.exec(template_statement).first()
            if not template:
                raise HTTPException(status_code=404, detail="水印模板不存在")
        
        try:
            # 更新图片状态
            image_record.status = ImageStatus.PROCESSING
            session.commit()
            
            # 加载原图
            original_image = PILImage.open(image_record.file_path)
            
            # 应用相框效果
            if template and template.frame_type:
                processed_image = WatermarkService.apply_frame(original_image, template.frame_type)
            else:
                processed_image = original_image.copy()
            
            # 添加文字水印
            if request.custom_text and template:
                processed_image = WatermarkService.add_text_watermark(
                    processed_image, request.custom_text, template
                )
            
            # 添加Logo水印
            if template and template.logo_path and Path(template.logo_path).exists():
                processed_image = WatermarkService.add_logo_watermark(
                    processed_image, template.logo_path, template
                )
            
            # 保存结果
            output_dir = Path(settings.output_dir)
            output_dir.mkdir(exist_ok=True)
            
            output_filename = f"watermarked_{uuid.uuid4()}.jpg"
            output_path = output_dir / output_filename
            
            processed_image.save(output_path, "JPEG", quality=95)
            
            # 更新图片状态
            image_record.status = ImageStatus.COMPLETED
            session.commit()
            
            return str(output_path)
            
        except Exception as e:
            # 更新失败状态
            image_record.status = ImageStatus.FAILED
            session.commit()
            raise HTTPException(status_code=500, detail=f"水印处理失败: {str(e)}")
    
    @staticmethod
    def create_default_templates(user: User, session: Session) -> None:
        """为用户创建默认水印模板"""
        default_templates = [
            {
                "name": "经典白框",
                "watermark_type": "artistic",
                "frame_type": FrameType.WHITE_FRAME,
                "font_family": "default",
                "font_size": 24,
                "font_color": "#000000",
                "position": PositionType.BOTTOM_RIGHT,
                "opacity": 0.8,
                "margin_x_percent": 2.0,
                "margin_y_percent": 2.0,
                "is_public": False
            },
            {
                "name": "模糊艺术框",
                "watermark_type": "artistic", 
                "frame_type": FrameType.BLUR_FRAME,
                "font_family": "default",
                "font_size": 20,
                "font_color": "#FFFFFF",
                "position": PositionType.BOTTOM_LEFT,
                "opacity": 0.9,
                "margin_x_percent": 3.0,
                "margin_y_percent": 3.0,
                "is_public": False
            },
            {
                "name": "居中版权",
                "watermark_type": "copyright",
                "frame_type": FrameType.WHITE_FRAME,
                "font_family": "default",
                "font_size": 18,
                "font_color": "#666666",
                "position": PositionType.MIDDLE_CENTER,
                "opacity": 0.5,
                "margin_x_percent": 0.0,
                "margin_y_percent": 0.0,
                "is_public": False
            },
            {
                "name": "顶部居中标题",
                "watermark_type": "artistic",
                "frame_type": FrameType.DEPTH_COLOR_CARD,
                "font_family": "default",
                "font_size": 28,
                "font_color": "#FFFFFF",
                "position": PositionType.TOP_CENTER,
                "opacity": 0.9,
                "margin_x_percent": 0.0,
                "margin_y_percent": 1.5,
                "is_public": False
            }
        ]
        
        for template_data in default_templates:
            template = WatermarkTemplate(**template_data, user_id=user.id)
            session.add(template)
        
        session.commit() 