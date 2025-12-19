from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime, timezone
from ..common.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # CAS 绑定相关字段
    cas_username = Column(String, unique=True, index=True, nullable=True)  # CAS 用户名（学号）
    cas_password_encrypted = Column(String, nullable=True)  # 加密的 CAS 密码
    cas_bound_at = Column(DateTime, nullable=True)  # CAS 绑定时间
    cas_is_bound = Column(Boolean, default=False)  # 是否已绑定 CAS