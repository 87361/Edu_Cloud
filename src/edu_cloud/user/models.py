from sqlalchemy import Column, Integer, String, Boolean, DateTime, Index
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
    
    # 角色字段：'user' 或 'admin'
    role = Column(String, default='user', nullable=False, index=True)
    
    # CAS 绑定相关字段
    cas_username = Column(String, unique=True, index=True, nullable=True)  # CAS 用户名（学号）
    cas_password_encrypted = Column(String, nullable=True)  # 加密的 CAS 密码
    cas_bound_at = Column(DateTime, nullable=True)  # CAS 绑定时间
    cas_is_bound = Column(Boolean, default=False)  # 是否已绑定 CAS
    
    def is_admin(self) -> bool:
        """检查用户是否为管理员"""
        return self.role == 'admin'


class TokenBlacklist(Base):
    """Token黑名单模型，用于存储已撤销的JWT token"""
    __tablename__ = "token_blacklist"
    
    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String, unique=True, nullable=False, index=True)  # JWT ID (JTI)
    token_type = Column(String, nullable=False)  # token类型，如 "access" 或 "refresh"
    username = Column(String, nullable=False, index=True)  # 用户名
    revoked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)  # 撤销时间
    expires_at = Column(DateTime, nullable=False, index=True)  # token过期时间
    
    # 创建复合索引以提高查询性能
    __table_args__ = (
        Index('idx_jti_expires', 'jti', 'expires_at'),
    )
    
    def __repr__(self):
        return f"<TokenBlacklist(jti={self.jti}, username={self.username}, revoked_at={self.revoked_at})>"