#!/usr/bin/env python3
"""
增强版水印服务测试脚本
借鉴壹印项目的参数化设计
"""

from app.services.watermark_service_enhanced import (
    EnhancedWatermarkService, 
    WatermarkConfig, 
    WatermarkPresets,
    BorderType,
    TextPosition
)
import os

def test_enhanced_watermark():
    """测试增强版水印服务"""
    image_path = "pexels-souvenirpixels-417074.jpg"
    
    if not os.path.exists(image_path):
        print(f"错误：找不到测试图片 {image_path}")
        return
    
    service = EnhancedWatermarkService()
    
    print("🚀 开始测试增强版水印服务...")
    print("=" * 60)
    
    # 测试1: Fujifilm预设风格
    print("1️⃣ 测试 Fujifilm 预设风格")
    fuji_config = WatermarkPresets.fuji_style()
    result1 = service.add_watermark(image_path, fuji_config, "Fujifilm X100F")
    result1.save("enhanced_fuji.jpg", quality=95)
    print("   ✅ 已保存: enhanced_fuji.jpg")
    
    # 测试2: 极简预设风格
    print("2️⃣ 测试极简预设风格")
    minimal_config = WatermarkPresets.minimal_style()
    result2 = service.add_watermark(image_path, minimal_config)
    result2.save("enhanced_minimal.jpg", quality=95)
    print("   ✅ 已保存: enhanced_minimal.jpg")
    
    # 测试3: 专业预设风格
    print("3️⃣ 测试专业预设风格")
    professional_config = WatermarkPresets.professional_style()
    result3 = service.add_watermark(image_path, professional_config, "Professional Photographer")
    result3.save("enhanced_professional.jpg", quality=95)
    print("   ✅ 已保存: enhanced_professional.jpg")
    
    # 测试4: 自定义配置（类似壹印的参数化）
    print("4️⃣ 测试自定义配置")
    custom_config = WatermarkConfig()
    # 边框设置
    custom_config.border_type = BorderType.CUSTOM_COLOR
    custom_config.border_color = (240, 240, 240)
    custom_config.border_size_ratio = 0.05
    # 文字设置
    custom_config.font_size_ratio = 0.018
    custom_config.font_color = (50, 50, 50, 255)  # 深灰色文字
    custom_config.font_shadow = True
    custom_config.font_shadow_color = (255, 255, 255, 128)  # 白色阴影
    # 内容设置
    custom_config.show_custom_text = True
    custom_config.custom_text = "© 2024 Photography Studio"
    custom_config.show_camera_info = True
    custom_config.show_settings = True
    custom_config.show_lens_info = False
    
    result4 = service.add_watermark(image_path, custom_config, "Canon EOS R5")
    result4.save("enhanced_custom.jpg", quality=95)
    print("   ✅ 已保存: enhanced_custom.jpg")
    
    # 测试5: 模糊边框风格
    print("5️⃣ 测试模糊边框风格")
    blur_config = WatermarkConfig()
    blur_config.border_type = BorderType.BLUR
    blur_config.border_size_ratio = 0.03
    blur_config.show_custom_text = True
    blur_config.custom_text = "Film Photography"
    blur_config.show_camera_info = False
    blur_config.show_settings = False
    
    result5 = service.add_watermark(image_path, blur_config)
    result5.save("enhanced_blur.jpg", quality=95)
    print("   ✅ 已保存: enhanced_blur.jpg")
    
    # 测试6: 圆角模糊风格预设
    print("6️⃣ 测试圆角模糊风格预设")
    rounded_config = WatermarkPresets.rounded_blur_style()
    result6 = service.add_watermark(image_path, rounded_config, "Vintage Film")
    result6.save("enhanced_rounded_blur.jpg", quality=95)
    print("   ✅ 已保存: enhanced_rounded_blur.jpg")
    
    # 测试7: 紧凑圆角风格预设
    print("7️⃣ 测试紧凑圆角风格预设")
    compact_config = WatermarkPresets.compact_rounded_style()
    result7 = service.add_watermark(image_path, compact_config, "Art Photography")
    result7.save("enhanced_compact_rounded.jpg", quality=95)
    print("   ✅ 已保存: enhanced_compact_rounded.jpg")
    
    print("\n" + "=" * 60)
    print("✨ 增强版水印服务测试完成！")
    
    # 显示文件信息
    generated_files = [
        "enhanced_fuji.jpg",
        "enhanced_minimal.jpg", 
        "enhanced_professional.jpg",
        "enhanced_custom.jpg",
        "enhanced_blur.jpg",
        "enhanced_rounded_blur.jpg",
        "enhanced_compact_rounded.jpg"
    ]
    
    print("\n📊 生成的文件信息：")
    print("-" * 50)
    for filename in generated_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"📁 {filename:<25} {size:>10,} bytes")
    
    print("\n🎯 设计特点对比：")
    print("-" * 50)
    print("🔸 参数化配置：类似壹印的灵活参数设置")
    print("🔸 预设风格：快速应用常用效果")
    print("🔸 自定义能力：用户可精确控制每个细节")
    print("🔸 字体缓存：提升性能")
    print("🔸 EXIF智能解析：自动提取相机信息")

def demo_config_options():
    """演示配置选项的强大功能"""
    print("\n" + "🎨 配置选项演示".center(60, "="))
    
    config = WatermarkConfig()
    
    print("📋 边框选项:")
    print("   • BorderType.WHITE - 白色边框")
    print("   • BorderType.BLUR - 模糊边框") 
    print("   • BorderType.CUSTOM_COLOR - 自定义颜色边框")
    print("   • BorderType.NONE - 无边框")
    
    print("\n📍 文字位置选项:")
    print("   • TextPosition.BOTTOM_CENTER - 底部居中")
    print("   • TextPosition.BOTTOM_LEFT - 底部左对齐")
    print("   • TextPosition.BOTTOM_RIGHT - 底部右对齐")
    print("   • TextPosition.TOP_CENTER - 顶部居中")
    
    print("\n🎛️ 可调节参数:")
    print(f"   • 边框大小比例: {config.border_size_ratio}")
    print(f"   • 字体大小比例: {config.font_size_ratio}")
    print(f"   • 边距比例: {config.margin_ratio}")
    print(f"   • 行间距比例: {config.line_spacing_ratio}")
    print(f"   • 图片质量: {config.image_quality}")

if __name__ == "__main__":
    test_enhanced_watermark()
    demo_config_options() 