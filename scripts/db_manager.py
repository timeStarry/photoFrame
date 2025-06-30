#!/usr/bin/env python3
"""
数据库迁移管理工具
使用Alembic进行数据库版本控制
"""

import sys
import subprocess
import os
from pathlib import Path

# 确保从项目根目录运行
project_root = Path(__file__).parent.parent
os.chdir(project_root)

def run_command(command: str, description: str = ""):
    """运行命令并处理输出"""
    print(f"🔄 {description or command}")
    try:
        # 从项目根目录运行命令
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=project_root)
        if result.returncode == 0:
            print(f"✅ 成功: {description or command}")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ 失败: {description or command}")
            if result.stderr:
                print(result.stderr)
            return False
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def create_migration(message: str):
    """创建新的迁移文件"""
    command = f'alembic revision --autogenerate -m "{message}"'
    return run_command(command, f"创建迁移: {message}")

def upgrade_database(revision: str = "head"):
    """升级数据库到指定版本"""
    command = f"alembic upgrade {revision}"
    return run_command(command, f"升级数据库到: {revision}")

def downgrade_database(revision: str):
    """降级数据库到指定版本"""
    command = f"alembic downgrade {revision}"
    return run_command(command, f"降级数据库到: {revision}")

def show_history():
    """显示迁移历史"""
    command = "alembic history --verbose"
    return run_command(command, "显示迁移历史")

def show_current():
    """显示当前数据库版本"""
    command = "alembic current"
    return run_command(command, "显示当前数据库版本")

def stamp_database(revision: str):
    """标记数据库版本而不执行迁移"""
    command = f"alembic stamp {revision}"
    return run_command(command, f"标记数据库版本: {revision}")

def init_database():
    """初始化数据库"""
    print("🚀 初始化数据库...")
    
    # 检查是否存在现有数据库（现在从项目根目录查找）
    db_path = project_root / "photoframe.db"
    if db_path.exists():
        print("⚠️  发现现有数据库文件")
        response = input("是否要备份现有数据库? (y/n): ")
        if response.lower() == 'y':
            backup_path = db_path.with_suffix('.backup.db')
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"✅ 数据库已备份到: {backup_path}")
    
    # 升级到最新版本
    return upgrade_database()

def migrate_from_old_schema():
    """从旧的数据库模式迁移"""
    print("🔄 从旧模式迁移数据库...")
    
    # 首先标记为基础版本
    if stamp_database("base"):
        # 然后升级到最新版本
        return upgrade_database()
    return False

def show_help():
    """显示帮助信息"""
    help_text = """
🗄️  数据库迁移管理工具

用法: python scripts/db_manager.py <命令> [参数]

命令:
  init                    - 初始化数据库（首次设置）
  migrate <message>       - 创建新的迁移文件
  upgrade [revision]      - 升级数据库（默认到最新版本）
  downgrade <revision>    - 降级数据库到指定版本
  current                 - 显示当前数据库版本
  history                 - 显示迁移历史
  stamp <revision>        - 标记数据库版本
  migrate-old            - 从旧模式迁移
  help                   - 显示此帮助信息

示例:
  python scripts/db_manager.py init
  python scripts/db_manager.py migrate "添加新字段"
  python scripts/db_manager.py upgrade
  python scripts/db_manager.py downgrade -1
  python scripts/db_manager.py current
  python scripts/db_manager.py history
  
常用版本标识:
  head                   - 最新版本
  base                   - 基础版本（空数据库）
  -1                     - 上一个版本
  <revision_id>          - 具体的版本ID

注意: 此脚本会自动切换到项目根目录运行
"""
    print(help_text)

def main():
    """主函数"""
    print(f"📁 工作目录: {project_root}")
    
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "init":
        init_database()
    elif command == "migrate":
        if len(sys.argv) < 3:
            print("❌ 请提供迁移描述信息")
            return
        message = sys.argv[2]
        create_migration(message)
    elif command == "upgrade":
        revision = sys.argv[2] if len(sys.argv) > 2 else "head"
        upgrade_database(revision)
    elif command == "downgrade":
        if len(sys.argv) < 3:
            print("❌ 请提供目标版本")
            return
        revision = sys.argv[2]
        downgrade_database(revision)
    elif command == "current":
        show_current()
    elif command == "history":
        show_history()
    elif command == "stamp":
        if len(sys.argv) < 3:
            print("❌ 请提供版本标识")
            return
        revision = sys.argv[2]
        stamp_database(revision)
    elif command == "migrate-old":
        migrate_from_old_schema()
    elif command == "help":
        show_help()
    else:
        print(f"❌ 未知命令: {command}")
        show_help()

if __name__ == "__main__":
    main() 