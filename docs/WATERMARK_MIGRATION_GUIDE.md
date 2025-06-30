# 水印模板升级指南

## 概述
水印系统已升级，支持九宫格定位和百分比边距，以更好地适应不同尺寸的图片。

## 主要改进

### 1. 九宫格位置系统
从原来的5个位置扩展为9个位置：

**原有位置：**
- `TOP_LEFT` - 左上角
- `TOP_RIGHT` - 右上角  
- `BOTTOM_LEFT` - 左下角
- `BOTTOM_RIGHT` - 右下角
- `CENTER` - 中心

**新增位置：**
- `TOP_CENTER` - 正上方
- `MIDDLE_LEFT` - 左中
- `MIDDLE_RIGHT` - 右中
- `BOTTOM_CENTER` - 正下方

**位置映射：**
- 原有的 `CENTER` 现在对应 `MIDDLE_CENTER`

### 2. 百分比边距系统
- **旧字段：** `margin_x` (像素), `margin_y` (像素)
- **新字段：** `margin_x_percent` (图片宽度百分比), `margin_y_percent` (图片高度百分比)

**优势：**
- 自动适应不同尺寸的图片
- 更加统一的视觉效果
- 响应式设计

## 数据库迁移

### 手动迁移现有模板
如果您有现有的水印模板数据，需要手动转换：

```sql
-- 1. 添加新字段
ALTER TABLE watermarktemplate ADD COLUMN margin_x_percent REAL DEFAULT 2.0;
ALTER TABLE watermarktemplate ADD COLUMN margin_y_percent REAL DEFAULT 2.0;

-- 2. 根据图片平均尺寸转换现有数据 (假设平均宽度1920px，高度1080px)
UPDATE watermarktemplate 
SET margin_x_percent = (margin_x * 100.0 / 1920.0),
    margin_y_percent = (margin_y * 100.0 / 1080.0);

-- 3. 更新位置枚举 (如果有CENTER位置)
UPDATE watermarktemplate 
SET position = 'middle_center' 
WHERE position = 'center';

-- 4. 删除旧字段
ALTER TABLE watermarktemplate DROP COLUMN margin_x;
ALTER TABLE watermarktemplate DROP COLUMN margin_y;
```

### 推荐的百分比值

| 用途 | margin_x_percent | margin_y_percent | 说明 |
|------|------------------|------------------|------|
| 标准边距 | 2.0 | 2.0 | 适合大多数情况 |
| 紧凑布局 | 1.0 | 1.0 | 水印更靠近边缘 |
| 宽松布局 | 3.0 | 3.0 | 更多留白空间 |
| 居中水印 | 0.0 | 0.0 | 完全居中，无偏移 |

## 代码更新

### 模板创建示例
```python
template = WatermarkTemplateCreate(
    name="九宫格示例",
    watermark_type=WatermarkType.ARTISTIC,
    frame_type=FrameType.WHITE_FRAME,
    font_family="default",
    font_size=24,
    font_color="#FFFFFF",
    position=PositionType.TOP_CENTER,  # 使用新的九宫格位置
    opacity=0.8,
    margin_x_percent=2.0,  # 使用百分比边距
    margin_y_percent=1.5,
    user_id=user.id
)
```

### API调用示例
```json
{
    "name": "响应式水印",
    "watermark_type": "artistic",
    "frame_type": "white_frame", 
    "font_family": "default",
    "font_size": 24,
    "font_color": "#FFFFFF",
    "position": "middle_right",
    "opacity": 0.8,
    "margin_x_percent": 2.5,
    "margin_y_percent": 2.0
}
```

## 测试建议

1. **多尺寸测试：** 使用不同尺寸的图片测试水印位置
2. **边距验证：** 确认百分比边距在各种图片上的效果
3. **九宫格测试：** 验证所有9个位置的水印显示效果

## 兼容性说明

- 新系统向后兼容现有的位置枚举
- 建议尽快迁移到百分比边距系统
- 旧的像素边距字段将在未来版本中移除 