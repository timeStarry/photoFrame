#!/usr/bin/env python3
"""
测试圆角+阴影模糊边框效果
"""

from watermark_script import add_blur_border_rounded, add_blur_border, get_exif_data, get_font
from PIL import Image, ImageDraw
import os

def add_text_to_rounded_image(img, signature, original_image_path):
    """为圆角模糊边框图片添加水印文字"""
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
    base_font_size = int(img.width * 0.018)  # 稍微大一点的字体
    font = get_font(base_font_size)
    
    # 计算文字位置
    margin_bottom = int(img.height * 0.04)  # 增加底部边距
    line_spacing = int(base_font_size * 0.4)
    
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
        
        # 绘制阴影 - 更柔和的阴影
        shadow_offset = max(2, base_font_size // 15)
        draw.text((x + shadow_offset, current_y + shadow_offset), line, fill=(0, 0, 0, 100), font=font)
        
        # 绘制主文字
        draw.text((x, current_y), line, fill=(255, 255, 255, 255), font=font)
        
        current_y += line_heights[i] + line_spacing
    
    return img

def test_rounded_blur_effects():
    """测试不同的圆角模糊效果"""
    image_path = "pexels-souvenirpixels-417074.jpg"
    
    if not os.path.exists(image_path):
        print(f"错误：找不到测试图片 {image_path}")
        return
    
    print("🎨 测试圆角+阴影模糊边框效果")
    print("=" * 60)
    
    img = Image.open(image_path)
    print(f"📷 原图尺寸: {img.width} x {img.height}")
    
    # 测试1: 标准圆角效果 (85%缩放)
    print("\n1️⃣ 标准圆角效果 (85%缩放)")
    rounded_85 = add_blur_border_rounded(img, scale_ratio=0.85)
    rounded_85_with_text = add_text_to_rounded_image(rounded_85, "Film Photography", image_path)
    rounded_85_with_text.save("rounded_blur_85.jpg", quality=95)
    print(f"   ✅ 已保存: rounded_blur_85.jpg ({rounded_85.width}x{rounded_85.height})")
    
    # 测试2: 更小的圆角效果 (75%缩放)
    print("2️⃣ 紧凑圆角效果 (75%缩放)")
    rounded_75 = add_blur_border_rounded(img, scale_ratio=0.75)
    rounded_75_with_text = add_text_to_rounded_image(rounded_75, "Vintage Camera", image_path)
    rounded_75_with_text.save("rounded_blur_75.jpg", quality=95)
    print(f"   ✅ 已保存: rounded_blur_75.jpg ({rounded_75.width}x{rounded_75.height})")
    
    # 测试3: 大尺寸圆角效果 (90%缩放)
    print("3️⃣ 大尺寸圆角效果 (90%缩放)")
    rounded_90 = add_blur_border_rounded(img, scale_ratio=0.90)
    rounded_90_with_text = add_text_to_rounded_image(rounded_90, "Professional Shot", image_path)
    rounded_90_with_text.save("rounded_blur_90.jpg", quality=95)
    print(f"   ✅ 已保存: rounded_blur_90.jpg ({rounded_90.width}x{rounded_90.height})")
    
    # 对比: 原版模糊边框
    print("4️⃣ 对比：原版模糊边框")
    classic_blur = add_blur_border(img)
    classic_blur_with_text = add_text_to_rounded_image(classic_blur, "Classic Blur", image_path)
    classic_blur_with_text.save("classic_blur_compare.jpg", quality=95)
    print(f"   ✅ 已保存: classic_blur_compare.jpg ({classic_blur.width}x{classic_blur.height})")
    
    print("\n" + "=" * 60)
    print("✨ 圆角+阴影效果测试完成！")
    
    # 显示文件信息
    generated_files = [
        "rounded_blur_85.jpg",
        "rounded_blur_75.jpg",
        "rounded_blur_90.jpg",
        "classic_blur_compare.jpg"
    ]
    
    print("\n📊 生成的文件信息：")
    print("-" * 50)
    for filename in generated_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"📁 {filename:<25} {size:>10,} bytes")
    
    print("\n🎯 新功能特点：")
    print("-" * 50)
    print("🔸 圆角效果：原图添加圆角，更现代的视觉效果")
    print("🔸 阴影效果：柔和的投影，增加立体感")
    print("🔸 可调缩放：原图占比可自定义调整")
    print("🔸 模糊背景：原图向外延伸的模糊效果")
    print("🔸 优化文字：更适合圆角风格的水印文字")

if __name__ == "__main__":
    test_rounded_blur_effects() 