from sqlmodel import SQLModel, create_engine, Session
from .config import settings

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
    """初始化数据库"""
    SQLModel.metadata.create_all(engine) 