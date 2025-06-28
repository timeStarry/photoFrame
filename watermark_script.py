import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from PIL.ExifTags import TAGS
import datetime
import math
import platform

def get_font(size):
    """获取适合的字体"""
    # 常见字体路径列表
    font_paths = []
    
    system = platform.system()
    if system == "Linux":
        # Linux常见字体路径
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 
            "/usr/share/fonts/TTF/DejaVuSans.ttf",
            "/usr/share/fonts/TTF/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
            "/System/Library/Fonts/Arial.ttf",  # 某些Linux发行版
            "/usr/share/fonts/corefonts/arial.ttf",
        ]
    elif system == "Windows":
        font_paths = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            "arial.ttf",
        ]
    elif system == "Darwin":  # macOS
        font_paths = [
            "/System/Library/Fonts/Arial.ttf",
            "/Library/Fonts/Arial.ttf",
            "arial.ttf",
        ]
    
    # 尝试加载字体
    for font_path in font_paths:
        try:
            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, size)
        except Exception as e:
            continue
    
    # 如果所有字体都加载失败，使用默认字体
    try:
        return ImageFont.load_default()
    except:
        # 最后的备选方案，创建一个基本字体
        return ImageFont.load_default()

def get_exif_data(image):
    """从图片中提取EXIF数据"""
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

def create_rounded_rectangle(draw, xy, radius, fill):
    """绘制圆角矩形"""
    x1, y1, x2, y2 = xy
    draw.rectangle([x1+radius, y1, x2-radius, y2], fill=fill)
    draw.rectangle([x1, y1+radius, x2, y2-radius], fill=fill)
    draw.pieslice([x1, y1, x1+radius*2, y1+radius*2], 180, 270, fill=fill)
    draw.pieslice([x2-radius*2, y1, x2, y1+radius*2], 270, 360, fill=fill)
    draw.pieslice([x1, y2-radius*2, x1+radius*2, y2], 90, 180, fill=fill)
    draw.pieslice([x2-radius*2, y2-radius*2, x2, y2], 0, 90, fill=fill)

def add_watermark(image_path, signature, watermark_level=2):
    """添加水印
    Args:
        image_path: 图片路径
        signature: 摄影师签名
        watermark_level: 水印等级(0-3)
    """
    # 打开图片
    img = Image.open(image_path)
    
    # 如果是0级水印,直接返回白色边框
    if watermark_level == 0:
        return add_white_border(img)
        
    # 获取EXIF数据
    exif_data = get_exif_data(img)
    
    # 准备水印文字 - 重新设计文字格式
    text_lines = []
    
    # 相机信息 (品牌 + 型号)
    camera_info = ""
    if 'Make' in exif_data and 'Model' in exif_data:
        make = exif_data['Make'].strip()
        model = exif_data['Model'].strip()
        # 避免重复品牌名
        if not model.startswith(make):
            camera_info = f"{make} {model}"
        else:
            camera_info = model
    elif signature:
        camera_info = signature
        
    if camera_info:
        text_lines.append(camera_info)
    
    # 拍摄参数 (焦距 光圈 快门 ISO)
    if watermark_level >= 2:
        camera_settings = []
        
        # 焦距
        if 'FocalLength' in exif_data:
            focal_length = exif_data['FocalLength']
            if isinstance(focal_length, tuple):
                focal_length = focal_length[0] / focal_length[1]
            camera_settings.append(f"{int(focal_length)}mm")
        
        # 光圈
        if 'FNumber' in exif_data:
            fnumber = exif_data['FNumber']
            if isinstance(fnumber, tuple):
                fnumber = fnumber[0] / fnumber[1]
            camera_settings.append(f"f/{fnumber}")
        
        # 快门速度
        if 'ExposureTime' in exif_data:
            exposure = exif_data['ExposureTime']
            if isinstance(exposure, tuple):
                if exposure[0] == 1:
                    camera_settings.append(f"1/{exposure[1]}s")
                else:
                    camera_settings.append(f"{exposure[0]/exposure[1]}s")
            else:
                camera_settings.append(f"{exposure}s")
        
        # ISO
        if 'ISOSpeedRatings' in exif_data:
            camera_settings.append(f"ISO {exif_data['ISOSpeedRatings']}")
            
        if camera_settings:
            text_lines.append(" ".join(camera_settings))
                
    # 添加白色边框
    img_with_border = add_white_border(img)
    
    # 如果没有文字,直接返回
    if not text_lines:
        return img_with_border
        
    # 添加文字水印
    draw = ImageDraw.Draw(img_with_border)
    
    # 计算字体大小 - 稍微小一些，更优雅
    base_font_size = int(img_with_border.width * 0.015)  # 1.5%
    font = get_font(base_font_size)
    
    # 计算文字位置 - 底部居中
    margin_bottom = int(img_with_border.height * 0.03)  # 底部边距3%
    line_spacing = int(base_font_size * 0.3)  # 行间距
    
    # 计算总文字高度
    total_text_height = 0
    line_heights = []
    for line in text_lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_height = bbox[3] - bbox[1]
        line_heights.append(line_height)
        total_text_height += line_height
    
    total_text_height += line_spacing * (len(text_lines) - 1) if len(text_lines) > 1 else 0
    
    # 起始Y位置
    start_y = img_with_border.height - margin_bottom - total_text_height
    
    # 绘制文字（白色文字，带黑色阴影）
    current_y = start_y
    for i, line in enumerate(text_lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (img_with_border.width - text_width) // 2
        
        # 绘制阴影效果（略微偏移的黑色文字）
        shadow_offset = max(1, base_font_size // 20)
        draw.text((x + shadow_offset, current_y + shadow_offset), line, fill=(0, 0, 0, 128), font=font)
        
        # 绘制主文字（白色）
        draw.text((x, current_y), line, fill=(255, 255, 255, 255), font=font)
        
        current_y += line_heights[i] + line_spacing
        
    return img_with_border

def add_white_border(img):
    """添加白色边框 - 类似Fujifilm风格"""
    # 边框大小为短边的3-5%
    border_size = int(min(img.width, img.height) * 0.04)
    
    # 创建新图片，带白色背景
    bordered = Image.new('RGB', 
                        (img.width + border_size*2, img.height + border_size*2), 
                        color=(248, 248, 248))  # 非纯白，稍微柔和一些
    
    # 粘贴原图到中心
    bordered.paste(img, (border_size, border_size))
    
    return bordered

def add_blur_border(img):
    """添加模糊边框（修复黑色边框问题）"""
    # 创建模糊边框
    border_size = int(min(img.width, img.height) * 0.03)  # 边框大小为短边的3%
    new_width = img.width + border_size * 2
    new_height = img.height + border_size * 2
    
    # 创建新图片，使用图片主色调作为背景（或白色）
    bordered = Image.new('RGB', (new_width, new_height), color=(248, 248, 248))
    
    # 复制并模糊原图，调整尺寸到新图片大小
    blurred = img.copy()
    blurred = blurred.resize((new_width, new_height))
    blurred = blurred.filter(ImageFilter.GaussianBlur(radius=border_size/2))
    
    # 先粘贴模糊的背景，再粘贴清晰的原图
    bordered.paste(blurred, (0, 0))
    bordered.paste(img, (border_size, border_size))
    
    return bordered

def add_blur_border_rounded(img, scale_ratio=0.85):
    """添加模糊边框 + 圆角 + 柔和阴影效果"""
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
    rounded_img = create_rounded_image(img, scaled_width, scaled_height, corner_radius=int(min(scaled_width, scaled_height) * 0.02))
    
    # 创建柔和的环形阴影
    shadow = create_soft_shadow(scaled_width, scaled_height, shadow_spread, corner_radius=int(min(scaled_width, scaled_height) * 0.02))
    
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

def create_rounded_image(img, width, height, corner_radius):
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

def create_soft_shadow(width, height, shadow_spread, corner_radius):
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

def create_shadow(width, height, blur_radius, corner_radius):
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

if __name__ == "__main__":
    # 使用示例
    image_path = "pexels-souvenirpixels-417074.jpg"
    signature = "Fujifilm X100F"  # 更符合目标效果的签名
    watermark_level = 2
    
    print("正在生成水印图片...")
    watermarked = add_watermark(image_path, signature, watermark_level)
    output_path = "watermarked_fuji_style.jpg"
    watermarked.save(output_path, quality=95)
    print(f"水印图片已保存为: {output_path}")
