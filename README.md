# PhotoFrame 相框服务

一个基于 FastAPI 的智能相框服务，支持图片处理、水印添加和用户认证。

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 数据库初始化
```bash
# 使用数据库管理工具（推荐）
python scripts/db_manager.py init

# 或者启动应用时自动初始化
python scripts/run.py
```

### 启动服务
```bash
# 开发模式
python scripts/run.py

# 或者直接运行
python main.py
```

访问 http://localhost:8000/docs 查看 API 文档。

## 📁 项目结构

```
photoFrame/
├── app/                    # 应用核心代码
│   ├── core/              # 核心配置
│   ├── models/            # 数据模型
│   ├── routers/           # API路由
│   └── services/          # 业务逻辑
├── scripts/               # 管理脚本
│   ├── run.py            # 启动脚本
│   └── db_manager.py     # 数据库管理
├── docs/                  # 项目文档
├── migrations/            # 数据库迁移文件
├── fonts/                 # 字体文件
├── templates/             # 模板文件
├── uploads/              # 上传文件目录
├── outputs/              # 输出文件目录
└── temp/                 # 临时文件目录
```

## 🔧 管理工具

### 数据库迁移
```bash
# 查看帮助
python scripts/db_manager.py help

# 创建迁移
python scripts/db_manager.py migrate "描述变更"

# 应用迁移
python scripts/db_manager.py upgrade

# 查看状态
python scripts/db_manager.py current
```

## 📚 文档

- [API 指南](docs/API_GUIDE.md) - 详细的API使用说明
- [数据库迁移指南](docs/ALEMBIC_USAGE_GUIDE.md) - Alembic使用说明
- [水印迁移指南](docs/WATERMARK_MIGRATION_GUIDE.md) - 水印系统升级说明
- [实现文档](docs/PHASE1_IMPLEMENTATION.md) - 第一阶段实现细节

## ✨ 主要功能

- 🔐 **用户认证** - JWT token 认证系统
- 🖼️ **图片管理** - 上传、存储、元数据提取
- 🎨 **水印系统** - 九宫格定位、百分比边距、多种相框
- 📱 **RESTful API** - 完整的REST API接口
- 🗄️ **数据库迁移** - Alembic版本控制
- 📊 **自动文档** - Swagger/OpenAPI文档

## 🎯 最新更新

### v1.1.0 - 水印系统增强
- ✅ 九宫格位置系统（9个精确位置）
- ✅ 响应式百分比边距
- ✅ 完整的数据库迁移支持
- ✅ 项目结构重组

## 🛠️ 开发

### 环境要求
- Python 3.8+
- SQLite 3.x（或其他支持的数据库）

### 开发流程
1. 克隆项目
2. 安装依赖：`pip install -r requirements.txt`
3. 初始化数据库：`python scripts/db_manager.py init`
4. 启动开发服务器：`python scripts/run.py`

### 模型变更
修改模型后，记得创建迁移：
```bash
python scripts/db_manager.py migrate "描述你的变更"
python scripts/db_manager.py upgrade
```

## 📄 许可证

MIT License - 详见 LICENSE 文件

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

📖 更多文档请查看 [docs/](docs/) 目录 