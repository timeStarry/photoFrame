from sqlmodel import SQLModel, create_engine, Session
from alembic.config import Config
from alembic import command
from pathlib import Path
import logging
from .config import settings

logger = logging.getLogger(__name__)

# 创建数据库引擎
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

def get_session():
    """获取数据库会话"""
    with Session(engine) as session:
        yield session

async def init_db():
    """使用Alembic初始化数据库"""
    try:
        # 获取Alembic配置
        alembic_cfg = Config("alembic.ini")
        
        # 检查数据库是否已经初始化
        db_path = Path("photoframe.db")
        if not db_path.exists():
            logger.info("数据库不存在，创建新数据库...")
            # 创建空数据库文件
            SQLModel.metadata.create_all(engine)
            # 标记为最新版本
            command.stamp(alembic_cfg, "head")
            logger.info("✅ 数据库初始化完成")
        else:
            try:
                # 尝试获取当前版本
                from alembic.runtime.migration import MigrationContext
                with engine.connect() as connection:
                    context = MigrationContext.configure(connection)
                    current_rev = context.get_current_revision()
                    
                if current_rev is None:
                    logger.warning("发现未版本控制的数据库，尝试自动迁移...")
                    # 标记为基础版本然后升级
                    command.stamp(alembic_cfg, "base")
                    command.upgrade(alembic_cfg, "head")
                    logger.info("✅ 数据库迁移完成")
                else:
                    # 升级到最新版本
                    command.upgrade(alembic_cfg, "head")
                    logger.info("✅ 数据库已更新到最新版本")
                    
            except Exception as e:
                logger.error(f"数据库迁移失败: {e}")
                # 回退到原来的方式
                SQLModel.metadata.create_all(engine)
                logger.warning("使用传统方式创建数据库表")
                
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        # 回退到原来的方式
        SQLModel.metadata.create_all(engine)
        logger.warning("使用传统方式创建数据库表")

def create_migration(message: str):
    """创建新的迁移文件"""
    try:
        alembic_cfg = Config("alembic.ini")
        command.revision(alembic_cfg, message=message, autogenerate=True)
        logger.info(f"✅ 迁移文件创建成功: {message}")
        return True
    except Exception as e:
        logger.error(f"创建迁移文件失败: {e}")
        return False

def upgrade_database(revision: str = "head"):
    """升级数据库"""
    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, revision)
        logger.info(f"✅ 数据库升级成功到: {revision}")
        return True
    except Exception as e:
        logger.error(f"数据库升级失败: {e}")
        return False

def get_current_revision():
    """获取当前数据库版本"""
    try:
        from alembic.runtime.migration import MigrationContext
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            return context.get_current_revision()
    except Exception as e:
        logger.error(f"获取数据库版本失败: {e}")
        return None 