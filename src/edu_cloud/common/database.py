from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool, QueuePool
from sqlalchemy import pool
from .config import settings
import logging

logger = logging.getLogger(__name__)

# 数据库引擎配置参数
engine_kwargs = {
    "echo": False,  # 是否打印SQL语句
    "future": True,  # 使用SQLAlchemy 2.0风格
}

# 根据数据库类型配置连接池和并发控制
if settings.database_url.startswith("sqlite"):
    # SQLite配置：使用StaticPool支持多线程，设置WAL模式提高并发性能
    engine_kwargs.update({
        "poolclass": StaticPool,
        "connect_args": {
            "check_same_thread": False,  # 允许多线程访问
            "timeout": 20.0,  # 连接超时时间（秒）
        },
        "pool_pre_ping": True,  # 连接前检查连接是否有效
    })
else:
    # PostgreSQL/MySQL等其他数据库配置
    engine_kwargs.update({
        "poolclass": QueuePool,
        "pool_size": 10,  # 连接池大小
        "max_overflow": 20,  # 最大溢出连接数
        "pool_pre_ping": True,  # 连接前检查连接是否有效
        "pool_recycle": 3600,  # 连接回收时间（秒）
        "pool_reset_on_return": "commit",  # 返回连接池时重置
    })

# 创建数据库引擎
engine = create_engine(settings.database_url, **engine_kwargs)

# 为SQLite启用WAL模式以提高并发性能（需要在engine创建后注册）
if settings.database_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging模式
        cursor.execute("PRAGMA synchronous=NORMAL")  # 平衡性能和安全性
        cursor.execute("PRAGMA foreign_keys=ON")  # 启用外键约束
        cursor.execute("PRAGMA busy_timeout=30000")  # 30秒忙等待超时
        cursor.close()

# 创建会话工厂，配置隔离级别和并发控制
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,  # 提交后不使对象过期，提高性能
)

# 创建一个Base类，所有数据模型都继承自它
Base = declarative_base()

# 依赖注入函数，用于在API中获取数据库会话
def get_db() -> Session:
    """
    获取数据库会话
    使用上下文管理器确保会话正确关闭
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        db.close()