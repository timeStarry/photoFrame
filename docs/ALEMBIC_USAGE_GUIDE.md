# Alembic 数据库迁移使用指南

## 概述
本项目现在使用 Alembic 进行数据库版本控制，提供了完整的数据库迁移解决方案。

## 🚀 快速开始

### 1. 方式一：使用管理工具 (推荐)
```bash
# 查看帮助
python scripts/db_manager.py help

# 初始化数据库（首次使用）
python scripts/db_manager.py init

# 查看当前版本
python scripts/db_manager.py current

# 查看迁移历史
python scripts/db_manager.py history
```

### 2. 方式二：直接使用 Alembic 命令
```bash
# 查看当前版本
alembic current

# 升级到最新版本
alembic upgrade head

# 降级到上一个版本
alembic downgrade -1

# 查看历史
alembic history --verbose
```

## 📝 开发流程

### 1. 修改模型后创建迁移
当你修改了 `app/models/` 中的任何模型时：

```bash
# 使用管理工具
python scripts/db_manager.py migrate "描述你的更改"

# 或直接使用 alembic
alembic revision --autogenerate -m "描述你的更改"
```

### 2. 应用迁移
```bash
# 使用管理工具
python scripts/db_manager.py upgrade

# 或直接使用 alembic
alembic upgrade head
```

### 3. 检查结果
```bash
python scripts/db_manager.py current
```

## 🔄 当前迁移状态

### 已完成的迁移
- ✅ **eec7e20cedbb**: 初始化数据库结构
  - 新增九宫格位置系统（9个位置）
  - 添加百分比边距字段（`margin_x_percent`, `margin_y_percent`）
  - 移除旧的像素边距字段（`margin_x`, `margin_y`）

## 🛠️ 常用操作

### 查看迁移状态
```bash
# 当前版本
alembic current

# 完整历史
alembic history --verbose

# 显示未应用的迁移
alembic heads
```

### 升级操作
```bash
# 升级到最新版本
alembic upgrade head

# 升级到特定版本
alembic upgrade eec7e20cedbb

# 升级 1 个版本
alembic upgrade +1
```

### 降级操作
```bash
# 降级到上一个版本
alembic downgrade -1

# 降级到特定版本
alembic downgrade eec7e20cedbb

# 降级到基础版本（清空）
alembic downgrade base
```

## 🔧 高级操作

### 手动标记版本（不执行迁移）
```bash
# 标记为当前版本（用于修复版本不一致）
alembic stamp head

# 标记为特定版本
alembic stamp eec7e20cedbb
```

### 生成空迁移文件
```bash
alembic revision -m "手动迁移描述"
```

### 合并分支迁移
```bash
alembic merge -m "合并迁移" <revision1> <revision2>
```

## 📂 文件结构
```
photoFrame/
├── alembic.ini              # Alembic 配置文件
├── scripts/                # 管理脚本目录
│   ├── db_manager.py       # 数据库管理工具
│   └── run.py             # 启动脚本
├── docs/                   # 项目文档
├── migrations/             # 迁移文件目录
│   ├── env.py             # Alembic 环境配置
│   ├── script.py.mako     # 迁移文件模板
│   └── versions/          # 迁移版本文件
│       └── eec7e20cedbb_init_database_digram.py
└── app/
    ├── models/            # 数据模型
    └── core/
        └── database.py    # 数据库配置
```

## ⚠️ 注意事项

### 1. 数据安全
- 生产环境升级前务必备份数据库
- 测试迁移在开发环境先运行
- 重要数据变更需要编写数据迁移脚本

### 2. 团队协作
- 修改模型后立即创建迁移文件
- 迁移文件需要提交到版本控制
- 合并代码前确保数据库版本一致

### 3. 迁移文件编辑
- 自动生成的迁移文件可能需要手动调整
- 复杂的数据迁移需要编写自定义 `upgrade()` 和 `downgrade()` 函数
- 确保 `downgrade()` 函数能正确回滚

## 🚨 故障排除

### 问题1：版本不一致
```bash
# 检查当前状态
alembic current
alembic heads

# 手动标记到正确版本
alembic stamp head
```

### 问题2：迁移失败
```bash
# 查看详细错误信息
alembic upgrade head --sql

# 回滚到上一个版本
alembic downgrade -1
```

### 问题3：从旧数据库迁移
```bash
# 使用管理工具
python scripts/db_manager.py migrate-old

# 或手动操作
alembic stamp base
alembic upgrade head
```

## 📚 相关文档
- [Alembic 官方文档](https://alembic.sqlalchemy.org/)
- [SQLModel 文档](https://sqlmodel.tiangolo.com/)
- [FastAPI 数据库指南](https://fastapi.tiangolo.com/tutorial/databases/) 