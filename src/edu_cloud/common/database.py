from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from .config import settings
# 创建数据库引擎
engine = create_engine(
    settings.database_url, connect_args={"check_same_thread": False} # 仅SQLite需要
)
# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# 创建一个Base类，所有数据模型都继承自它
Base = declarative_base()
# 依赖注入函数，用于在API中获取数据库会话
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()