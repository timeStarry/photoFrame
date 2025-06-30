# PhotoFrame 相框服务 API 使用指南

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动服务
```bash
python run.py
```

### 3. 访问API文档
- Swagger文档: http://localhost:8000/docs
- ReDoc文档: http://localhost:8000/redoc

## 📁 项目结构

```
photoFrame/
├── app/                    # 应用核心代码
│   ├── core/              # 核心配置
│   │   ├── config.py      # 配置管理
│   │   └── database.py    # 数据库连接
│   ├── models/            # 数据模型
│   │   ├── user.py        # 用户模型
│   │   ├── image.py       # 图片模型
│   │   └── watermark.py   # 水印模板模型
│   ├── services/          # 业务逻辑
│   │   ├── auth_service.py     # 认证服务
│   │   ├── image_service.py    # 图片处理服务
│   │   └── watermark_service.py # 水印处理服务
│   └── routers/           # API路由
│       ├── auth.py        # 认证接口
│       ├── image_management.py # 图片管理接口
│       └── watermark.py   # 水印处理接口
├── uploads/               # 上传的图片文件
├── outputs/               # 处理后的图片文件
├── fonts/                 # 字体文件
├── main.py               # 应用入口
├── run.py                # 启动脚本
└── requirements.txt      # 依赖列表
```

## 🔐 认证流程

### 1. 用户注册
```http
POST /api/auth/register
Content-Type: application/json

{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "is_active": true
}
```

### 2. 用户登录
```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=testuser&password=password123
```

响应：
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com"
    }
}
```

### 3. 使用Token访问API
在后续请求中添加Authorization头：
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## 📸 图片管理

### 1. 上传图片
```http
POST /api/images/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [图片文件]
clean_exif: true
```

### 2. 获取图片列表
```http
GET /api/images/
Authorization: Bearer {token}
```

### 3. 下载图片
```http
GET /api/images/{image_id}/download
Authorization: Bearer {token}
```

## 🎨 水印处理

### 1. 获取预设模板
```http
GET /api/watermark/presets
```

### 2. 创建自定义模板
```http
POST /api/watermark/templates
Authorization: Bearer {token}
Content-Type: application/json

{
    "name": "我的水印模板",
    "watermark_type": "artistic",
    "frame_type": "white_frame",
    "font_family": "default",
    "font_size": 24,
    "font_color": "#000000",
    "position": "bottom_right",
    "opacity": 0.8,
    "margin_x": 20,
    "margin_y": 20,
    "is_public": false
}
```

### 3. 处理水印
```http
POST /api/watermark/process
Authorization: Bearer {token}
Content-Type: application/json

{
    "image_id": 1,
    "template_id": 1,
    "custom_text": "我的水印文字"
}
```

## 🎯 相框类型说明

### 白框相框 (white_frame)
- 添加经典白色边框
- 适合各种类型的照片
- 简洁优雅的设计

### 模糊相框 (blur_frame)
- 使用原图模糊作为背景
- 营造浅景深效果
- 突出主体内容

### 景深色卡相框 (depth_color_card)
- 径向渐变背景
- 专业的色彩效果
- 适合艺术摄影

## 🔧 配置说明

### 环境变量配置
创建 `.env` 文件：
```env
# 应用配置
APP_NAME=PhotoFrame 相框服务
DEBUG=True

# 数据库配置
DATABASE_URL=sqlite:///./photoframe.db

# JWT配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# 文件配置
UPLOAD_DIR=./uploads
OUTPUT_DIR=./outputs
MAX_FILE_SIZE=10485760
```

### 支持的图片格式
- JPG/JPEG
- PNG
- BMP
- TIFF

### 文件大小限制
- 默认最大10MB
- 可通过配置文件调整

## ⚠️ 注意事项

1. **安全性**：生产环境请修改默认的SECRET_KEY
2. **存储**：图片文件默认存储在本地，生产环境建议使用对象存储
3. **字体**：将需要的字体文件放在fonts目录下
4. **权限**：确保应用有读写uploads、outputs等目录的权限

## 🐛 常见问题

### Q: 上传图片失败
A: 检查文件格式是否支持，文件大小是否超限

### Q: 水印处理失败  
A: 确认模板ID是否存在，图片是否已上传成功

### Q: 字体显示异常
A: 检查fonts目录下是否有对应的字体文件

## 📞 技术支持

如有问题请查看：
1. API文档: http://localhost:8000/docs
2. 健康检查: http://localhost:8000/health
3. 应用日志输出 