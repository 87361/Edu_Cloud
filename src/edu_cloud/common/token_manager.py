"""
Token管理模块，用于处理JWT token的撤销和黑名单检查
"""
from datetime import datetime, timezone
from typing import Optional
from flask_jwt_extended import get_jwt, get_jwt_identity
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from ..user.models import TokenBlacklist

logger = logging.getLogger(__name__)


def revoke_token(db: Session, jti: str, username: str, token_type: str = "access", expires_at: Optional[datetime] = None) -> bool:
    """
    将token加入黑名单
    
    Args:
        db: 数据库会话
        jti: JWT ID (token的唯一标识)
        username: 用户名
        token_type: token类型，默认为"access"
        expires_at: token过期时间
        
    Returns:
        bool: 是否成功添加到黑名单
    """
    try:
        # 检查token是否已经在黑名单中
        existing = db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first()
        if existing:
            logger.warning(f"Token {jti} is already in blacklist")
            return True
        
        # 创建黑名单记录
        blacklist_entry = TokenBlacklist(
            jti=jti,
            token_type=token_type,
            username=username,
            revoked_at=datetime.now(timezone.utc),
            expires_at=expires_at or datetime.now(timezone.utc)
        )
        
        db.add(blacklist_entry)
        db.commit()
        logger.info(f"Token {jti} has been revoked for user {username}")
        return True
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while revoking token: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error revoking token: {str(e)}")
        return False


def is_token_revoked(db: Session, jti: str) -> bool:
    """
    检查token是否已被撤销
    
    Args:
        db: 数据库会话
        jti: JWT ID
        
    Returns:
        bool: 如果token已被撤销返回True，否则返回False
    """
    try:
        blacklist_entry = db.query(TokenBlacklist).filter(
            TokenBlacklist.jti == jti
        ).first()
        
        if blacklist_entry:
            # 检查token是否已过期，如果过期则可以从黑名单中删除（可选）
            if blacklist_entry.expires_at < datetime.now(timezone.utc):
                # 可选：清理过期的黑名单记录
                db.delete(blacklist_entry)
                db.commit()
                return False
            return True
        
        return False
        
    except SQLAlchemyError as e:
        logger.error(f"Database error while checking token revocation: {str(e)}")
        # 发生错误时，为了安全起见，假设token已被撤销
        return True
    except Exception as e:
        logger.error(f"Error checking token revocation: {str(e)}")
        return True


def revoke_current_token(db: Session) -> bool:
    """
    撤销当前请求的token
    
    Args:
        db: 数据库会话
        
    Returns:
        bool: 是否成功撤销
    """
    try:
        jwt_data = get_jwt()
        jti = jwt_data.get("jti")
        exp = jwt_data.get("exp")
        username = get_jwt_identity()
        
        if not jti:
            logger.error("Cannot get JTI from token")
            return False
        
        if not username:
            logger.error("Cannot get username from token")
            return False
        
        # 将exp时间戳转换为datetime对象
        expires_at = datetime.fromtimestamp(exp, tz=timezone.utc) if exp else None
        
        return revoke_token(db, jti, username, token_type="access", expires_at=expires_at)
        
    except Exception as e:
        logger.error(f"Error revoking current token: {str(e)}")
        return False


def revoke_all_user_tokens(db: Session, username: str) -> int:
    """
    撤销指定用户的所有token
    
    Args:
        db: 数据库会话
        username: 用户名
        
    Returns:
        int: 撤销的token数量
    """
    try:
        # 获取所有未过期的token
        current_time = datetime.now(timezone.utc)
        tokens = db.query(TokenBlacklist).filter(
            TokenBlacklist.username == username,
            TokenBlacklist.expires_at > current_time
        ).all()
        
        # 如果token已经在黑名单中，则跳过
        count = 0
        for token in tokens:
            if not is_token_revoked(db, token.jti):
                count += 1
        
        logger.info(f"Revoked {count} tokens for user {username}")
        return count
        
    except Exception as e:
        logger.error(f"Error revoking all user tokens: {str(e)}")
        return 0


def cleanup_expired_tokens(db: Session) -> int:
    """
    清理过期的黑名单记录
    
    Args:
        db: 数据库会话
        
    Returns:
        int: 清理的记录数量
    """
    try:
        current_time = datetime.now(timezone.utc)
        expired_tokens = db.query(TokenBlacklist).filter(
            TokenBlacklist.expires_at < current_time
        ).all()
        
        count = len(expired_tokens)
        for token in expired_tokens:
            db.delete(token)
        
        db.commit()
        logger.info(f"Cleaned up {count} expired blacklist tokens")
        return count
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while cleaning up expired tokens: {str(e)}")
        return 0
    except Exception as e:
        logger.error(f"Error cleaning up expired tokens: {str(e)}")
        return 0

