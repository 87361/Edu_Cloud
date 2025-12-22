from datetime import datetime, timedelta
from typing import Optional
from flask import jsonify
from functools import wraps
from flask_jwt_extended import (
    JWTManager, create_access_token, get_jwt_identity, jwt_required, get_jwt
)
from sqlalchemy.orm import Session
from werkzeug.exceptions import HTTPException
import logging

from .config import settings
from .database import get_db, SessionLocal
from ..user.models import User

logger = logging.getLogger(__name__)

class FlaskAuthError(HTTPException):
    """Flask版本的自定义认证错误"""
    def __init__(self, description, code=401):
        super().__init__(description)
        self.code = code
        self.description = description

def create_user_access_token(username: str, expires_delta: Optional[timedelta] = None):
    """创建JWT访问令牌（保持与FastAPI版本兼容）"""
    if expires_delta:
        expires = timedelta(seconds=int(expires_delta.total_seconds()))
    else:
        expires = timedelta(minutes=30)  # 默认30分钟
    
    return create_access_token(
        identity=username,
        expires_delta=expires
    )

def get_current_user_identity():
    """获取当前用户身份（从JWT token中）"""
    try:
        current_user_id = get_jwt_identity()
        return current_user_id
    except Exception:
        return None
        return None

def get_current_user_from_db(db: Session) -> Optional[User]:
    """从数据库获取当前用户"""
    username = get_current_user_identity()
    if not username:
        return None
    
    user = db.query(User).filter(User.username == username).first()
    return user

def get_current_active_user(db_func=None):
    """Flask装饰器版本的获取当前活跃用户"""
    def decorator(f):
        def wrapped_function(*args, **kwargs):
            # 获取数据库会话
            if db_func:
                db = db_func()
            else:
                from .database import SessionLocal
                db = SessionLocal()
                close_db = True
            
            try:
                current_user = get_current_user_from_db(db)
                if not current_user:
                    return jsonify({"error": "Could not validate credentials"}), 401
                
                if not current_user.is_active:
                    return jsonify({"error": "Inactive user"}), 400
                
                # 将用户添加到kwargs中
                kwargs['current_user'] = current_user
                return f(*args, **kwargs)
            
            finally:
                if close_db:
                    db.close()
        
        return wrapped_function
    return decorator

# 简化版本的认证装饰器
def auth_required(f):
    """需要认证的装饰器"""
    @jwt_required()
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

def auth_required_with_user(db_func=None):
    """需要认证且需要用户对象的装饰器"""
    return get_current_active_user(db_func)

# 为了保持与原有代码兼容性的别名
def verify_token(token: str) -> Optional[str]:
    """验证JWT令牌并返回用户名（保持兼容性）"""
    # 这个函数在Flask-JWT-Extended中不需要，但保留以兼容旧代码
    try:
        from flask_jwt_extended import decode_token
        payload = decode_token(token)
        return payload.get('sub')
    except Exception:
        return None


def admin_required(f):
    """
    管理员权限检查装饰器
    需要用户已登录且角色为admin
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_username = get_jwt_identity()
        if not current_username:
            return jsonify({"error": "Could not validate credentials"}), 401
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == current_username).first()
            if not user:
                logger.warning(f"Admin required: User '{current_username}' not found in database")
                return jsonify({"error": "User not found", "message": f"User '{current_username}' not found"}), 404
            
            if not user.is_active:
                return jsonify({"error": "Inactive user"}), 400
            
            if not user.is_admin():
                return jsonify({
                    "error": "Forbidden",
                    "message": "Admin access required"
                }), 403
            
            # 将用户添加到kwargs中
            kwargs['current_user'] = user
            return f(*args, **kwargs)
        finally:
            db.close()
    
    return decorated_function
