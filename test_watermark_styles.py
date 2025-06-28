#!/usr/bin/env python3
"""
水印样式测试脚本
展示不同的水印风格效果
"""

from watermark_script import add_watermark, add_white_border, add_blur_border, get_exif_data, get_font
from PIL import Image, ImageDraw
import os

def add_text_to_image(img, signature, original_image_path):
    """为已有边框的图片添加水印文字"""
    # 获取原图的EXIF数据
    original_img = Image.open(original_image_path)
    exif_data = get_exif_data(original_img)
    
    # 准备文字
    text_lines = []
    text_lines.append(signature)
    
    # 拍摄参数
    camera_settings = []
    if 'FocalLength' in exif_data:
        focal_length = exif_data['FocalLength']
        if isinstance(focal_length, tuple):
            focal_length = focal_length[0] / focal_length[1]
        camera_settings.append(f"{int(focal_length)}mm")
    
    if 'FNumber' in exif_data:
        fnumber = exif_data['FNumber']
        if isinstance(fnumber, tuple):
            fnumber = fnumber[0] / fnumber[1]
        camera_settings.append(f"f/{fnumber}")
    
    if 'ExposureTime' in exif_data:
        exposure = exif_data['ExposureTime']
        if isinstance(exposure, tuple):
            if exposure[0] == 1:
                camera_settings.append(f"1/{exposure[1]}s")
            else:
                camera_settings.append(f"{exposure[0]/exposure[1]}s")
        else:
            camera_settings.append(f"{exposure}s")
    
    if 'ISOSpeedRatings' in exif_data:
        camera_settings.append(f"ISO {exif_data['ISOSpeedRatings']}")
    
    if camera_settings:
        text_lines.append(" ".join(camera_settings))
    
    # 在图片上添加文字
    draw = ImageDraw.Draw(img)
    base_font_size = int(img.width * 0.015)
    font = get_font(base_font_size)
    
    # 计算文字位置
    margin_bottom = int(img.height * 0.03)
    line_spacing = int(base_font_size * 0.3)
    
    total_text_height = 0
    line_heights = []
    for line in text_lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_height = bbox[3] - bbox[1]
        line_heights.append(line_height)
        total_text_height += line_height
    
    total_text_height += line_spacing * (len(text_lines) - 1) if len(text_lines) > 1 else 0
    start_y = img.height - margin_bottom - total_text_height
    
    # 绘制文字
    current_y = start_y
    for i, line in enumerate(text_lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (img.width - text_width) // 2
        
        # 绘制阴影
        shadow_offset = max(1, base_font_size // 20)
        draw.text((x + shadow_offset, current_y + shadow_offset), line, fill=(0, 0, 0, 128), font=font)
        
        # 绘制主文字
        draw.text((x, current_y), line, fill=(255, 255, 255, 255), font=font)
        
        current_y += line_heights[i] + line_spacing
    
    return img

def test_watermark_styles():
    """测试不同的水印风格"""
    image_path = "pexels-souvenirpixels-417074.jpg"
    
    if not os.path.exists(image_path):
        print(f"错误：找不到测试图片 {image_path}")
        return
    
    print("开始生成不同风格的水印效果...")
    
    # 1. Fujifilm风格（白色边框 + 简洁水印）
    print("1. 生成 Fujifilm 风格水印...")
    fuji_watermarked = add_watermark(image_path, "Fujifilm X100F", watermark_level=2)
    fuji_watermarked.save("style1_fuji.jpg", quality=95)
    
    # 2. 经典摄影风格（模糊边框 + 详细信息）
    print("2. 生成经典摄影风格水印...")
    img = Image.open(image_path)
    # 先添加模糊边框
    classic_bordered = add_blur_border(img)
    # 再添加水印文字（手动添加到模糊边框图片上）
    classic_with_text = add_text_to_image(classic_bordered, "Canon EOS R5", image_path)
    classic_with_text.save("style2_classic.jpg", quality=95)
    
    # 3. 极简风格（仅白色边框）
    print("3. 生成极简风格...")
    img = Image.open(image_path)
    minimal = add_white_border(img)
    minimal.save("style3_minimal.jpg", quality=95)
    
    # 4. 专业风格（完整信息）
    print("4. 生成专业摄影师风格...")
    professional = add_watermark(image_path, "Professional Photographer", watermark_level=3)
    professional.save("style4_professional.jpg", quality=95)
    
    print("\n✅ 所有风格已生成完成：")
    print("   - style1_fuji.jpg          (Fujifilm风格 - 类似您的目标)")
    print("   - style2_classic.jpg       (经典风格 - 模糊边框)")
    print("   - style3_minimal.jpg       (极简风格 - 仅白色边框)")
    print("   - style4_professional.jpg  (专业风格 - 完整信息)")
    
    # 显示文件信息
    styles = [
        "style1_fuji.jpg",
        "style2_classic.jpg", 
        "style3_minimal.jpg",
        "style4_professional.jpg"
    ]
    
    print("\n📊 文件信息：")
    for style in styles:
        if os.path.exists(style):
            size = os.path.getsize(style)
            print(f"   {style:<25} {size:>10,} bytes")

if __name__ == "__main__":
    test_watermark_styles() 