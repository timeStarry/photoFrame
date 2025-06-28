from typing import Optional, Dict, Any, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from PIL.ExifTags import TAGS
import datetime
import os
import math
from enum import Enum

class WatermarkStyle(str, Enum):
    """水印风格枚举"""
    FUJI = "fuji"           # Fujifilm风格
    MINIMAL = "minimal"     # 极简风格
    CLASSIC = "classic"     # 经典摄影风格
    PROFESSIONAL = "professional"  # 专业风格
    YIYIN = "yiyin"        # 壹印风格

class BorderType(str, Enum):
    """边框类型枚举"""
    WHITE = "white"         # 白色边框
    BLUR = "blur"          # 模糊边框
    BLUR_ROUNDED = "blur_rounded"  # 圆角+阴影模糊边框
    NONE = "none"          # 无边框
    CUSTOM_COLOR = "custom_color"  # 自定义颜色边框

class TextPosition(str, Enum):
    """文字位置枚举"""
    BOTTOM_CENTER = "bottom_center"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    TOP_CENTER = "top_center"
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"

class WatermarkConfig:
    """水印配置类 - 参数化设计"""
    
    def __init__(self):
        # 边框设置
        self.border_type: BorderType = BorderType.WHITE
        self.border_size_ratio: float = 0.04  # 边框大小占短边的比例
        self.border_color: Tuple[int, int, int] = (248, 248, 248)
        self.image_scale_ratio: float = 0.85  # 原图缩放比例（仅用于圆角边框）
        
        # 文字设置
        self.font_size_ratio: float = 0.015  # 字体大小占宽度的比例
        self.font_color: Tuple[int, int, int, int] = (255, 255, 255, 255)
        self.font_shadow: bool = True
        self.font_shadow_color: Tuple[int, int, int, int] = (0, 0, 0, 128)
        self.font_shadow_offset: int = 1
        
        # 位置设置
        self.text_position: TextPosition = TextPosition.BOTTOM_CENTER
        self.margin_ratio: float = 0.03  # 边距占高度的比例
        self.line_spacing_ratio: float = 0.3  # 行间距占字体大小的比例
        
        # 水印内容设置
        self.show_camera_info: bool = True
        self.show_lens_info: bool = True
        self.show_settings: bool = True
        self.show_custom_text: bool = False
        self.custom_text: str = ""
        
        # 高级设置
        self.image_quality: int = 95
        self.auto_rotate: bool = False  # 是否自动旋转图片
        self.output_format: str = "JPEG"

class EnhancedWatermarkService:
    """增强版水印服务 - 借鉴壹印设计"""
    
    def __init__(self):
        self.font_cache: Dict[str, ImageFont.FreeTypeFont] = {}
    
    def add_watermark(self, 
                     image_path: str, 
                     config: WatermarkConfig,
                     custom_signature: Optional[str] = None) -> Image.Image:
        """
        添加水印 - 参数化配置
        
        Args:
            image_path: 图片路径
            config: 水印配置
            custom_signature: 自定义签名
        
        Returns:
            处理后的图片
        """
        # 打开并预处理图片
        img = Image.open(image_path)
        
        # 自动旋转（如果需要）
        if config.auto_rotate:
            img = self._auto_rotate_image(img)
        
        # 获取EXIF数据
        exif_data = self._get_exif_data(img)
        
        # 添加边框
        img_with_border = self._add_border(img, config)
        
        # 准备水印文字
        text_lines = self._prepare_text_lines(exif_data, config, custom_signature)
        
        # 添加文字水印
        if text_lines:
            img_with_border = self._add_text_watermark(img_with_border, text_lines, config)
        
        return img_with_border
    
    def _auto_rotate_image(self, img: Image.Image) -> Image.Image:
        """自动旋转图片基于EXIF方向信息"""
        try:
            exif = img._getexif()
            if exif is not None:
                orientation = exif.get(274)  # Orientation tag
                if orientation == 3:
                    img = img.rotate(180, expand=True)
                elif orientation == 6:
                    img = img.rotate(270, expand=True)
                elif orientation == 8:
                    img = img.rotate(90, expand=True)
        except:
            pass
        return img
    
    def _get_exif_data(self, image: Image.Image) -> Dict[str, Any]:
        """提取EXIF数据"""
        exif_data = {}
        try:
            exif = image._getexif()
            if exif:
                for tag_id in exif:
                    tag = TAGS.get(tag_id, tag_id)
                    data = exif.get(tag_id)
                    if isinstance(data, bytes):
                        data = data.decode(errors='ignore')
                    exif_data[tag] = data
        except:
            pass
        return exif_data
    
    def _add_border(self, img: Image.Image, config: WatermarkConfig) -> Image.Image:
        """添加边框"""
        if config.border_type == BorderType.NONE:
            return img
        
        border_size = int(min(img.width, img.height) * config.border_size_ratio)
        
        if config.border_type == BorderType.WHITE or config.border_type == BorderType.CUSTOM_COLOR:
            bordered = Image.new('RGB', 
                               (img.width + border_size*2, img.height + border_size*2), 
                               color=config.border_color)
            bordered.paste(img, (border_size, border_size))
            return bordered
        
        elif config.border_type == BorderType.BLUR:
            new_width = img.width + border_size * 2
            new_height = img.height + border_size * 2
            bordered = Image.new('RGB', (new_width, new_height), color=(248, 248, 248))
            blurred = img.copy()
            blurred = blurred.resize((new_width, new_height))
            blurred = blurred.filter(ImageFilter.GaussianBlur(radius=border_size/2))
            bordered.paste(blurred, (0, 0))
            bordered.paste(img, (border_size, border_size))
            return bordered
            
        elif config.border_type == BorderType.BLUR_ROUNDED:
            return self._add_blur_border_rounded(img, config.image_scale_ratio)
        
        return img
    
    def _add_blur_border_rounded(self, img: Image.Image, scale_ratio: float = 0.85) -> Image.Image:
        """添加圆角+柔和阴影模糊边框"""
        # 边框大小为短边的6%，减少阴影空间
        border_size = int(min(img.width, img.height) * 0.06)
        shadow_spread = int(border_size * 0.15)  # 阴影发散范围，减小到原来的一半
        
        # 计算缩放后的原图尺寸
        scaled_width = int(img.width * scale_ratio)
        scaled_height = int(img.height * scale_ratio)
        
        # 新图片尺寸，给阴影留少量空间
        new_width = img.width + border_size * 2 + shadow_spread * 2
        new_height = img.height + border_size * 2 + shadow_spread * 2
        
        # 创建背景 - 使用柔和的灰白色
        result = Image.new('RGB', (new_width, new_height), color=(245, 245, 245))
        
        # 创建模糊背景
        blurred_bg = img.copy()
        blurred_bg = blurred_bg.resize((new_width, new_height))
        blurred_bg = blurred_bg.filter(ImageFilter.GaussianBlur(radius=border_size/1.5))
        
        # 粘贴模糊背景
        result.paste(blurred_bg, (0, 0))
        
        # 创建圆角图片
        rounded_img = self._create_rounded_image(img, scaled_width, scaled_height, 
                                               corner_radius=int(min(scaled_width, scaled_height) * 0.02))
        
        # 创建柔和的环形阴影
        shadow = self._create_soft_shadow(scaled_width, scaled_height, shadow_spread, 
                                        corner_radius=int(min(scaled_width, scaled_height) * 0.02))
        
        # 计算居中位置
        center_x = (new_width - scaled_width) // 2
        center_y = (new_height - scaled_height) // 2
        
        # 粘贴阴影（居中，不偏移）
        shadow_x = center_x - shadow_spread
        shadow_y = center_y - shadow_spread
        result.paste(shadow, (shadow_x, shadow_y), shadow)
        
        # 粘贴圆角图片
        result.paste(rounded_img, (center_x, center_y), rounded_img)
        
        return result
    
    def _create_rounded_image(self, img: Image.Image, width: int, height: int, corner_radius: int) -> Image.Image:
        """创建圆角图片"""
        # 缩放原图
        resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        # 创建圆角蒙版
        mask = Image.new('L', (width, height), 0)
        mask_draw = ImageDraw.Draw(mask)
        
        # 绘制圆角矩形蒙版
        mask_draw.rounded_rectangle([0, 0, width, height], radius=corner_radius, fill=255)
        
        # 应用蒙版
        result = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        result.paste(resized_img, (0, 0))
        result.putalpha(mask)
        
        return result
    
    def _create_soft_shadow(self, width: int, height: int, shadow_spread: int, corner_radius: int) -> Image.Image:
        """创建柔和的环形阴影效果"""
        # 创建阴影画布，比原图稍大以容纳阴影发散
        shadow_width = width + shadow_spread * 2
        shadow_height = height + shadow_spread * 2
        
        # 创建阴影层
        shadow = Image.new('RGBA', (shadow_width, shadow_height), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        
        # 绘制圆角矩形阴影 - 使用更淡的灰色
        shadow_draw.rounded_rectangle(
            [shadow_spread, shadow_spread, width + shadow_spread, height + shadow_spread],
            radius=corner_radius,
            fill=(0, 0, 0, 40)  # 更淡的半透明灰色
        )
        
        # 应用柔和的模糊效果
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=shadow_spread * 0.8))
        
        return shadow

    def _create_shadow(self, width: int, height: int, blur_radius: int, corner_radius: int) -> Image.Image:
        """创建阴影效果（保留旧版本兼容性）"""
        # 创建阴影形状
        shadow = Image.new('RGBA', (width + blur_radius*2, height + blur_radius*2), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        
        # 绘制圆角矩形阴影
        shadow_draw.rounded_rectangle(
            [blur_radius, blur_radius, width + blur_radius, height + blur_radius],
            radius=corner_radius,
            fill=(0, 0, 0, 80)  # 半透明黑色
        )
        
        # 模糊阴影
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        
        return shadow
    
    def _prepare_text_lines(self, 
                          exif_data: Dict[str, Any], 
                          config: WatermarkConfig,
                          custom_signature: Optional[str] = None) -> list[str]:
        """准备水印文字行"""
        text_lines = []
        
        # 自定义文字
        if config.show_custom_text and config.custom_text:
            text_lines.append(config.custom_text)
        
        # 相机信息
        if config.show_camera_info:
            camera_info = self._get_camera_info(exif_data, custom_signature)
            if camera_info:
                text_lines.append(camera_info)
        
        # 镜头信息
        if config.show_lens_info:
            lens_info = self._get_lens_info(exif_data)
            if lens_info:
                text_lines.append(lens_info)
        
        # 拍摄设置
        if config.show_settings:
            settings_info = self._get_settings_info(exif_data)
            if settings_info:
                text_lines.append(settings_info)
        
        return text_lines
    
    def _get_camera_info(self, exif_data: Dict[str, Any], custom_signature: Optional[str] = None) -> str:
        """获取相机信息"""
        if custom_signature:
            return custom_signature
        
        if 'Make' in exif_data and 'Model' in exif_data:
            make = exif_data['Make'].strip()
            model = exif_data['Model'].strip()
            if not model.startswith(make):
                return f"{make} {model}"
            else:
                return model
        
        return ""
    
    def _get_lens_info(self, exif_data: Dict[str, Any]) -> str:
        """获取镜头信息"""
        lens_info = []
        
        # 镜头型号
        if 'LensModel' in exif_data:
            lens_info.append(exif_data['LensModel'])
        
        return " ".join(lens_info) if lens_info else ""
    
    def _get_settings_info(self, exif_data: Dict[str, Any]) -> str:
        """获取拍摄设置信息"""
        settings = []
        
        # 焦距
        if 'FocalLength' in exif_data:
            focal_length = exif_data['FocalLength']
            if isinstance(focal_length, tuple):
                focal_length = focal_length[0] / focal_length[1]
            settings.append(f"{int(focal_length)}mm")
        
        # 光圈
        if 'FNumber' in exif_data:
            fnumber = exif_data['FNumber']
            if isinstance(fnumber, tuple):
                fnumber = fnumber[0] / fnumber[1]
            settings.append(f"f/{fnumber}")
        
        # 快门速度
        if 'ExposureTime' in exif_data:
            exposure = exif_data['ExposureTime']
            if isinstance(exposure, tuple):
                if exposure[0] == 1:
                    settings.append(f"1/{exposure[1]}s")
                else:
                    settings.append(f"{exposure[0]/exposure[1]}s")
            else:
                settings.append(f"{exposure}s")
        
        # ISO
        if 'ISOSpeedRatings' in exif_data:
            settings.append(f"ISO {exif_data['ISOSpeedRatings']}")
        
        return " ".join(settings)
    
    def _add_text_watermark(self, 
                          img: Image.Image, 
                          text_lines: list[str], 
                          config: WatermarkConfig) -> Image.Image:
        """添加文字水印"""
        if not text_lines:
            return img
        
        draw = ImageDraw.Draw(img)
        
        # 获取字体
        font_size = int(img.width * config.font_size_ratio)
        font = self._get_font(font_size)
        
        # 计算文字位置
        positions = self._calculate_text_positions(img, text_lines, font, config)
        
        # 绘制文字
        for i, (line, (x, y)) in enumerate(zip(text_lines, positions)):
            # 绘制阴影
            if config.font_shadow:
                shadow_x = x + config.font_shadow_offset
                shadow_y = y + config.font_shadow_offset
                draw.text((shadow_x, shadow_y), line, fill=config.font_shadow_color, font=font)
            
            # 绘制主文字
            draw.text((x, y), line, fill=config.font_color, font=font)
        
        return img
    
    def _calculate_text_positions(self, 
                                img: Image.Image, 
                                text_lines: list[str], 
                                font: ImageFont.FreeTypeFont,
                                config: WatermarkConfig) -> list[Tuple[int, int]]:
        """计算文字位置"""
        positions = []
        
        # 创建临时draw对象计算尺寸
        temp_draw = ImageDraw.Draw(img)
        
        # 计算每行文字的尺寸
        line_sizes = []
        for line in text_lines:
            bbox = temp_draw.textbbox((0, 0), line, font=font)
            line_sizes.append((bbox[2] - bbox[0], bbox[3] - bbox[1]))
        
        # 计算总高度
        line_spacing = int(font.size * config.line_spacing_ratio)
        total_height = sum(size[1] for size in line_sizes) + line_spacing * (len(text_lines) - 1)
        
        # 根据位置设置计算起始位置
        margin = int(img.height * config.margin_ratio)
        
        if config.text_position == TextPosition.BOTTOM_CENTER:
            start_y = img.height - margin - total_height
        elif config.text_position == TextPosition.TOP_CENTER:
            start_y = margin
        # TODO: 添加其他位置的计算
        
        # 计算每行的具体位置
        current_y = start_y
        for i, (line, (line_width, line_height)) in enumerate(zip(text_lines, line_sizes)):
            if config.text_position in [TextPosition.BOTTOM_CENTER, TextPosition.TOP_CENTER]:
                x = (img.width - line_width) // 2
            # TODO: 添加其他对齐方式
            
            positions.append((x, current_y))
            current_y += line_height + line_spacing
        
        return positions
    
    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """获取字体（带缓存）"""
        cache_key = f"default_{size}"
        if cache_key not in self.font_cache:
            # 这里可以扩展支持自定义字体
            self.font_cache[cache_key] = self._load_system_font(size)
        return self.font_cache[cache_key]
    
    def _load_system_font(self, size: int) -> ImageFont.FreeTypeFont:
        """加载系统字体"""
        import platform
        
        font_paths = []
        system = platform.system()
        
        if system == "Linux":
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            ]
        elif system == "Windows":
            font_paths = [
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/calibri.ttf",
            ]
        elif system == "Darwin":
            font_paths = [
                "/System/Library/Fonts/Arial.ttf",
            ]
        
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    return ImageFont.truetype(font_path, size)
            except:
                continue
        
        return ImageFont.load_default()

# 预设配置工厂
class WatermarkPresets:
    """水印预设配置"""
    
    @staticmethod
    def fuji_style() -> WatermarkConfig:
        """Fujifilm风格预设"""
        config = WatermarkConfig()
        config.border_type = BorderType.WHITE
        config.border_color = (248, 248, 248)
        config.font_size_ratio = 0.015
        config.show_lens_info = False
        return config
    
    @staticmethod
    def minimal_style() -> WatermarkConfig:
        """极简风格预设"""
        config = WatermarkConfig()
        config.border_type = BorderType.WHITE
        config.show_camera_info = False
        config.show_settings = False
        config.show_custom_text = True
        config.custom_text = "Photography"
        return config
    
    @staticmethod
    def professional_style() -> WatermarkConfig:
        """专业风格预设"""
        config = WatermarkConfig()
        config.border_type = BorderType.WHITE
        config.show_lens_info = True
        config.font_size_ratio = 0.012
        return config
    
    @staticmethod
    def rounded_blur_style() -> WatermarkConfig:
        """圆角模糊风格预设"""
        config = WatermarkConfig()
        config.border_type = BorderType.BLUR_ROUNDED
        config.image_scale_ratio = 0.85
        config.font_size_ratio = 0.018
        config.show_lens_info = False
        config.margin_ratio = 0.04
        return config
    
    @staticmethod
    def compact_rounded_style() -> WatermarkConfig:
        """紧凑圆角风格预设"""
        config = WatermarkConfig()
        config.border_type = BorderType.BLUR_ROUNDED
        config.image_scale_ratio = 0.75
        config.font_size_ratio = 0.016
        config.show_lens_info = False
        config.margin_ratio = 0.04
        return config 