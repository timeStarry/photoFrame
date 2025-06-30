# Scripts 管理脚本

这个目录包含项目的管理和运维脚本。

## 📁 脚本列表

### `run.py` - 应用启动脚本
用于启动PhotoFrame服务。

```bash
# 启动开发服务器
python scripts/run.py

# 或者从项目根目录
python main.py
```

**功能：**
- 自动加载环境配置
- 初始化数据库
- 启动FastAPI服务器
- 支持热重载（开发模式）

### `db_manager.py` - 数据库迁移管理工具
用于管理数据库版本和迁移。

```bash
# 查看帮助
python scripts/db_manager.py help

# 常用命令
python scripts/db_manager.py init        # 初始化数据库
python scripts/db_manager.py current     # 查看当前版本
python scripts/db_manager.py history     # 查看迁移历史
python scripts/db_manager.py upgrade     # 升级到最新版本
```

**功能：**
- 数据库初始化
- 自动生成迁移文件
- 版本升级/降级
- 迁移历史查看
- 数据库备份
- 自动路径处理

## 🔧 使用说明

### 首次设置
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 初始化数据库
python scripts/db_manager.py init

# 3. 启动服务
python scripts/run.py
```

### 开发流程
```bash
# 1. 修改模型后创建迁移
python scripts/db_manager.py migrate "描述你的变更"

# 2. 应用迁移
python scripts/db_manager.py upgrade

# 3. 启动/重启服务
python scripts/run.py
```

### 生产环境部署
```bash
# 1. 备份数据库
cp photoframe.db photoframe.backup.db

# 2. 应用迁移
python scripts/db_manager.py upgrade

# 3. 启动服务
python scripts/run.py
```

## ⚠️ 注意事项

### 工作目录
- 所有脚本都会自动切换到项目根目录执行
- 可以从任何位置运行这些脚本
- 确保从项目根目录运行以获得最佳体验

### 数据库操作
- 重要操作前会提示备份数据库
- 迁移失败时可以回滚到上一个版本
- 生产环境操作前务必测试

### 环境变量
- 支持 `.env` 文件配置
- 可以通过环境变量覆盖默认设置
- 开发/生产环境配置分离

## 🚨 故障排除

### 脚本无法运行
```bash
# 检查Python路径
which python
python --version

# 检查依赖安装
pip list | grep alembic
pip list | grep fastapi
```

### 数据库问题
```bash
# 检查数据库状态
python scripts/db_manager.py current

# 查看迁移历史
python scripts/db_manager.py history

# 重置数据库（谨慎使用）
rm photoframe.db
python scripts/db_manager.py init
```

### 路径问题
```bash
# 确认在正确的目录
pwd
ls -la

# 检查脚本权限（Linux/Mac）
chmod +x scripts/*.py
```

## 📚 相关文档

- [数据库迁移指南](../docs/ALEMBIC_USAGE_GUIDE.md)
- [API文档](../docs/API_GUIDE.md)
- [项目README](../README.md) 