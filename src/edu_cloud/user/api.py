from datetime import timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import Dict, Any, Optional
import logging
import json

from ..common.database import get_db, SessionLocal
from ..common.security import verify_password, get_password_hash
from ..common.auth import create_user_access_token
from . import models, schemas

logger = logging.getLogger(__name__)

# 创建蓝图
user_bp = Blueprint('user', __name__)

def validate_data(schema_class, data: Dict[str, Any]):
    """使用Pydantic验证数据"""
    try:
        return schema_class(**data), None
    except Exception as e:
        return None, str(e)

def success_response(data: Any) -> Dict[str, Any]:
    """统一成功响应格式"""
    if hasattr(data, 'dict'):
        data = data.dict()
    elif hasattr(data, '__dict__'):
        # 处理SQLAlchemy对象
        data = {
            'id': data.id,
            'username': data.username,
            'email': data.email,
            'full_name': data.full_name,
            'is_active': data.is_active,
            'created_at': data.created_at.isoformat() if data.created_at else None
        }
    return {"data": data}

def error_response(message: str, code: int = 400) -> tuple:
    """统一错误响应格式"""
    return {"error": message}, code

def get_json_data():
    """安全获取JSON数据"""
    try:
        data = request.get_json()
        if data is None:
            return None
        return data
    except Exception as e:
        logger.error(f"JSON parsing error: {str(e)}")
        return None

@user_bp.route("/register", methods=["POST"])
def register():
    """用户注册"""
    try:
        data = get_json_data()
        if data is None:
            return error_response("Invalid JSON data")
        
        # 验证数据
        user_data, validation_error = validate_data(schemas.UserCreate, data)
        if validation_error:
            return error_response(f"Validation error: {validation_error}")
        
        db = SessionLocal()
        try:
            # 检查用户名是否已存在
            db_user = db.query(models.User).filter(models.User.username == user_data.username).first()
            if db_user:
                return error_response("Username already registered")
            
            # 检查邮箱是否已存在
            if user_data.email:
                db_email = db.query(models.User).filter(models.User.email == user_data.email).first()
                if db_email:
                    return error_response("Email already registered")
            
            # 创建新用户
            hashed_password = get_password_hash(user_data.password)
            db_user = models.User(
                username=user_data.username,
                email=user_data.email,
                full_name=user_data.full_name,
                hashed_password=hashed_password
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            return jsonify(success_response(db_user))
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error during registration: {str(e)}")
            return error_response("Registration failed due to database error", 500)
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return error_response(f"Registration failed: {str(e)}", 500)

@user_bp.route("/login", methods=["POST"])
def login():
    """用户登录"""
    try:
        data = get_json_data()
        if data is None:
            return error_response("Invalid JSON data")
        
        # 验证数据
        login_data, validation_error = validate_data(schemas.UserLogin, data)
        if validation_error:
            return error_response(f"Validation error: {validation_error}")
        
        db = SessionLocal()
        try:
            # 验证用户
            user = db.query(models.User).filter(models.User.username == login_data.username).first()
            
            if not user or not verify_password(login_data.password, user.hashed_password):
                return error_response("Incorrect username or password", 401)
            
            if not user.is_active:
                return error_response("Inactive user", 400)
            
            # 创建访问令牌
            access_token_expires = timedelta(minutes=30)
            access_token = create_user_access_token(
                username=user.username, 
                expires_delta=access_token_expires
            )
            
            return jsonify({
                "access_token": access_token, 
                "token_type": "bearer"
            })
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return error_response(f"Login failed: {str(e)}", 500)

@user_bp.route("/token", methods=["POST"])
def login_for_access_token():
    """OAuth2兼容的登录端点"""
    try:
        # 获取表单数据
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return error_response("Username and password are required")
        
        db = SessionLocal()
        try:
            # 验证用户
            user = db.query(models.User).filter(models.User.username == username).first()
            
            if not user or not verify_password(password, user.hashed_password):
                return error_response("Incorrect username or password", 401)
            
            if not user.is_active:
                return error_response("Inactive user", 400)
            
            access_token_expires = timedelta(minutes=30)
            access_token = create_user_access_token(
                username=user.username, 
                expires_delta=access_token_expires
            )
            
            return jsonify({
                "access_token": access_token, 
                "token_type": "bearer"
            })
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Token generation error: {str(e)}")
        return error_response(f"Token generation failed: {str(e)}", 500)

@user_bp.route("/me", methods=["GET"])
@jwt_required()
def read_users_me():
    """获取当前用户信息"""
    try:
        current_username = get_jwt_identity()
        if not current_username:
            return error_response("Could not validate credentials", 401)
        
        db = SessionLocal()
        try:
            user = db.query(models.User).filter(models.User.username == current_username).first()
            if not user:
                return error_response("User not found", 404)
            
            return jsonify(success_response(user))
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Get user info error: {str(e)}")
        return error_response(f"Get user info failed: {str(e)}", 500)

@user_bp.route("/me", methods=["PUT"])
@jwt_required()
def update_user_me():
    """更新当前用户信息"""
    try:
        current_username = get_jwt_identity()
        if not current_username:
            return error_response("Could not validate credentials", 401)
        
        data = get_json_data()
        if data is None:
            return error_response("Invalid JSON data")
        
        # 验证数据
        update_data, validation_error = validate_data(schemas.UserUpdate, data)
        if validation_error:
            return error_response(f"Validation error: {validation_error}")
        
        db = SessionLocal()
        try:
            user = db.query(models.User).filter(models.User.username == current_username).first()
            if not user:
                return error_response("User not found", 404)
            
            # 更新数据
            update_dict = update_data.model_dump(exclude_unset=True)
            
            if "password" in update_dict:
                update_dict["hashed_password"] = get_password_hash(update_dict.pop("password"))
            
            # 检查邮箱是否已被其他用户使用
            if "email" in update_dict and update_dict["email"]:
                existing_user = db.query(models.User).filter(
                    models.User.email == update_dict["email"],
                    models.User.id != user.id
                ).first()
                if existing_user:
                    return error_response("Email already registered by another user")
            
            for field, value in update_dict.items():
                setattr(user, field, value)
            
            db.commit()
            db.refresh(user)
            
            return jsonify(success_response(user))
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Update user error: {str(e)}")
        return error_response(f"Update user failed: {str(e)}", 500)

@user_bp.route("/", methods=["GET"])
@jwt_required()
def read_users():
    """获取用户列表（需要认证）"""
    try:
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 100))
        
        db = SessionLocal()
        try:
            users = db.query(models.User).offset(skip).limit(limit).all()
            
            users_data = [success_response(user)['data'] for user in users]
            return jsonify({"data": users_data})
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Get users error: {str(e)}")
        return error_response(f"Get users failed: {str(e)}", 500)

@user_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
def read_user(user_id: int):
    """获取指定用户信息"""
    try:
        db = SessionLocal()
        try:
            user = db.query(models.User).filter(models.User.id == user_id).first()
            if user is None:
                return error_response("User not found", 404)
            
            return jsonify(success_response(user))
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        return error_response(f"Get user failed: {str(e)}", 500)

@user_bp.route("/me", methods=["DELETE"])
@jwt_required()
def delete_user_me():
    """删除当前用户账户"""
    try:
        current_username = get_jwt_identity()
        if not current_username:
            return error_response("Could not validate credentials", 401)
        
        db = SessionLocal()
        try:
            user = db.query(models.User).filter(models.User.username == current_username).first()
            if not user:
                return error_response("User not found", 404)
            
            db.delete(user)
            db.commit()
            
            return jsonify({"message": "User account deleted successfully"})
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Delete user error: {str(e)}")
        return error_response(f"Delete user failed: {str(e)}", 500)

@user_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """用户登出（客户端需要删除token）"""
    try:
        # 在服务器端，我们主要返回成功响应
        # 实际的登出需要客户端删除存储的token
        return jsonify({
            "message": "Successfully logged out",
            "instruction": "Please delete the access token from client storage"
        })
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return error_response("Logout failed", 500)

@user_bp.route("/me", methods=["PATCH"])
@jwt_required()
def patch_user_me():
    """部分更新当前用户信息"""
    try:
        current_username = get_jwt_identity()
        if not current_username:
            return error_response("Could not validate credentials", 401)
        
        data = get_json_data()
        if data is None:
            return error_response("Invalid JSON data")
        
        # 验证数据
        update_data, validation_error = validate_data(schemas.UserUpdate, data)
        if validation_error:
            return error_response(f"Validation error: {validation_error}")
        
        db = SessionLocal()
        try:
            user = db.query(models.User).filter(models.User.username == current_username).first()
            if not user:
                return error_response("User not found", 404)
            
            # 更新数据
            update_dict = update_data.model_dump(exclude_unset=True)
            
            if "password" in update_dict:
                update_dict["hashed_password"] = get_password_hash(update_dict.pop("password"))
            
            # 检查邮箱是否已被其他用户使用
            if "email" in update_dict and update_dict["email"]:
                existing_user = db.query(models.User).filter(
                    models.User.email == update_dict["email"],
                    models.User.id != user.id
                ).first()
                if existing_user:
                    return error_response("Email already registered by another user")
            
            for field, value in update_dict.items():
                setattr(user, field, value)
            
            db.commit()
            db.refresh(user)
            
            return jsonify(success_response(user))
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error: {str(e)}")
            return error_response("Data integrity violation", 400)
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error: {str(e)}")
            return error_response("Database operation failed", 500)
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Patch user error: {str(e)}")
        return error_response(f"Update user failed: {str(e)}", 500)

@user_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    """修改密码"""
    try:
        current_username = get_jwt_identity()
        if not current_username:
            return error_response("Could not validate credentials", 401)
        
        data = get_json_data()
        if data is None:
            return error_response("Invalid JSON data")
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return error_response("Current password and new password are required")
        
        if len(new_password) < 6:
            return error_response("New password must be at least 6 characters long")
        
        db = SessionLocal()
        try:
            user = db.query(models.User).filter(models.User.username == current_username).first()
            if not user:
                return error_response("User not found", 404)
            
            # 验证当前密码
            if not verify_password(current_password, user.hashed_password):
                return error_response("Current password is incorrect", 401)
            
            # 更新密码
            user.hashed_password = get_password_hash(new_password)
            db.commit()
            
            return jsonify({
                "message": "Password changed successfully"
            })
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error in change_password: {str(e)}")
            return error_response("Password change failed", 500)
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        return error_response(f"Password change failed: {str(e)}", 500)

# 添加错误处理装饰器
def handle_database_errors(f):
    """数据库错误处理装饰器"""
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except IntegrityError as e:
            logger.error(f"Database integrity error: {str(e)}")
            return error_response("Data integrity violation", 400)
        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            return error_response("Database operation failed", 500)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return error_response("An unexpected error occurred", 500)
    return decorated_function

# 应用错误处理装饰器到关键路由
register = handle_database_errors(register)
login = handle_database_errors(login)
login_for_access_token = handle_database_errors(login_for_access_token)
read_users_me = handle_database_errors(read_users_me)
update_user_me = handle_database_errors(update_user_me)
read_users = handle_database_errors(read_users)
