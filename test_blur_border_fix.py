#!/usr/bin/env python3
"""
专门测试模糊边框修复的脚本
验证黑色边框问题是否解决
"""

from watermark_script import add_blur_border
from PIL import Image
import os

def test_blur_border_fix():
    """测试模糊边框修复"""
    image_path = "pexels-souvenirpixels-417074.jpg"
    
    if not os.path.exists(image_path):
        print(f"错误：找不到测试图片 {image_path}")
        return
    
    print("🔧 测试模糊边框修复...")
    print("=" * 50)
    
    # 加载原图
    img = Image.open(image_path)
    print(f"📷 原图尺寸: {img.width} x {img.height}")
    
    # 生成修复后的模糊边框
    blurred_img = add_blur_border(img)
    print(f"🖼️  边框图尺寸: {blurred_img.width} x {blurred_img.height}")
    
    # 保存测试结果
    output_path = "test_blur_border_fixed.jpg"
    blurred_img.save(output_path, quality=95)
    
    # 显示结果
    file_size = os.path.getsize(output_path)
    print(f"✅ 已保存: {output_path}")
    print(f"📊 文件大小: {file_size:,} bytes")
    
    print("\n" + "🎯 修复要点".center(50, "="))
    print("✅ 1. 添加了白色背景色，避免黑色边框")
    print("✅ 2. 模糊图片调整到正确尺寸，完全覆盖背景")
    print("✅ 3. 边框效果更加自然和美观")
    
    print(f"\n📋 检查点:")
    print(f"   • 边框应该是柔和的模糊效果，而不是黑色")
    print(f"   • 右侧和下方应该没有黑色边缘")
    print(f"   • 整体效果应该是原图向外模糊延伸")

if __name__ == "__main__":
    test_blur_border_fix() 