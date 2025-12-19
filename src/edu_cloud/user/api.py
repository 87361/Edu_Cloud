from datetime import timedelta, datetime
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
from ..common.cas_auth import verify_cas_credentials, encrypt_cas_password
from ..common.token_manager import revoke_current_token
from . import models, schemas
from datetime import timezone

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
            'role': getattr(data, 'role', 'user'),  # 支持角色字段
            'created_at': data.created_at.isoformat() if data.created_at else None,
            # CAS 相关信息（不包含密码）
            'cas_username': data.cas_username if hasattr(data, 'cas_username') else None,
            'cas_is_bound': data.cas_is_bound if hasattr(data, 'cas_is_bound') else False,
            'cas_bound_at': data.cas_bound_at.isoformat() if hasattr(data, 'cas_bound_at') and data.cas_bound_at else None
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

@user_bp.route("/login/cas", methods=["POST"])
def login_with_cas():
    """
    直接使用 CAS 登录
    如果用户已存在（通过 CAS 用户名查找），则直接登录
    如果用户不存在，则自动创建用户并绑定 CAS
    """
    try:
        data = get_json_data()
        if data is None:
            return error_response("Invalid JSON data")
        
        # 验证数据
        cas_login_data, validation_error = validate_data(schemas.CASLogin, data)
        if validation_error:
            return error_response(f"Validation error: {validation_error}")
        
        # 验证 CAS 凭证
        is_valid, auth_object, error_msg = verify_cas_credentials(
            cas_login_data.cas_username, 
            cas_login_data.cas_password
        )
        
        if not is_valid:
            return error_response(error_msg or "CAS 认证失败", 401)
        
        db = SessionLocal()
        try:
            # 查找是否已有用户绑定此 CAS 账户
            user = db.query(models.User).filter(
                models.User.cas_username == cas_login_data.cas_username
            ).first()
            
            if user:
                # 用户已存在，更新 CAS 绑定信息（密码可能已更改）
                user.cas_password_encrypted = encrypt_cas_password(cas_login_data.cas_password)
                user.cas_is_bound = True
                user.cas_bound_at = datetime.now(timezone.utc)
                db.commit()
                db.refresh(user)
            else:
                # 用户不存在，创建新用户并绑定 CAS
                # 使用 CAS 用户名作为系统用户名（如果冲突则添加后缀）
                base_username = cas_login_data.cas_username
                username = base_username
                counter = 1
                while db.query(models.User).filter(models.User.username == username).first():
                    username = f"{base_username}_{counter}"
                    counter += 1
                
                # 创建用户（不需要密码，因为使用 CAS 登录）
                user = models.User(
                    username=username,
                    hashed_password=get_password_hash(""),  # 空密码，CAS 用户不使用密码登录
                    cas_username=cas_login_data.cas_username,
                    cas_password_encrypted=encrypt_cas_password(cas_login_data.cas_password),
                    cas_is_bound=True,
                    cas_bound_at=datetime.now(timezone.utc),
                    is_active=True
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            
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
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "cas_username": user.cas_username,
                    "cas_is_bound": user.cas_is_bound
                }
            })
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"CAS login error: {str(e)}")
        return error_response(f"CAS login failed: {str(e)}", 500)

@user_bp.route("/bind-cas", methods=["POST"])
@jwt_required()
def bind_cas():
    """
    注册用户绑定 CAS 账户
    需要先登录（使用数据库账号），然后绑定 CAS 账户
    """
    try:
        current_username = get_jwt_identity()
        if not current_username:
            return error_response("Could not validate credentials", 401)
        
        data = get_json_data()
        if data is None:
            return error_response("Invalid JSON data")
        
        # 验证数据
        cas_bind_data, validation_error = validate_data(schemas.CASBind, data)
        if validation_error:
            return error_response(f"Validation error: {validation_error}")
        
        db = SessionLocal()
        try:
            # 获取当前用户
            user = db.query(models.User).filter(models.User.username == current_username).first()
            if not user:
                return error_response("User not found", 404)
            
            # 检查 CAS 账户是否已被其他用户绑定
            existing_user = db.query(models.User).filter(
                models.User.cas_username == cas_bind_data.cas_username,
                models.User.id != user.id
            ).first()
            
            if existing_user:
                return error_response("该 CAS 账户已被其他用户绑定", 400)
            
            # 验证 CAS 凭证
            is_valid, auth_object, error_msg = verify_cas_credentials(
                cas_bind_data.cas_username, 
                cas_bind_data.cas_password
            )
            
            if not is_valid:
                return error_response(error_msg or "CAS 认证失败", 401)
            
            # 绑定 CAS 账户
            user.cas_username = cas_bind_data.cas_username
            user.cas_password_encrypted = encrypt_cas_password(cas_bind_data.cas_password)
            user.cas_is_bound = True
            user.cas_bound_at = datetime.now(timezone.utc)
            
            db.commit()
            db.refresh(user)
            
            return jsonify(success_response({
                "id": user.id,
                "username": user.username,
                "cas_username": user.cas_username,
                "cas_is_bound": user.cas_is_bound,
                "cas_bound_at": user.cas_bound_at.isoformat() if user.cas_bound_at else None
            }))
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Bind CAS error: {str(e)}")
        return error_response(f"Bind CAS failed: {str(e)}", 500)

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

@user_bp.route("/me/cas-status", methods=["GET"])
@jwt_required()
def get_cas_status():
    """获取当前用户的 CAS 绑定状态"""
    try:
        current_username = get_jwt_identity()
        if not current_username:
            return error_response("Could not validate credentials", 401)
        
        db = SessionLocal()
        try:
            user = db.query(models.User).filter(models.User.username == current_username).first()
            if not user:
                return error_response("User not found", 404)
            
            return jsonify(success_response({
                "cas_is_bound": user.cas_is_bound,
                "cas_username": user.cas_username,
                "cas_bound_at": user.cas_bound_at.isoformat() if user.cas_bound_at else None
            }))
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Get CAS status error: {str(e)}")
        return error_response(f"Get CAS status failed: {str(e)}", 500)

@user_bp.route("/me/verify-cas", methods=["POST"])
@jwt_required()
def verify_cas_credentials_endpoint():
    """
    验证 CAS 凭证（用于数据抓取前的验证）
    返回验证结果，但不返回密码
    """
    try:
        current_username = get_jwt_identity()
        if not current_username:
            return error_response("Could not validate credentials", 401)
        
        data = get_json_data()
        if data is None:
            return error_response("Invalid JSON data")
        
        cas_password = data.get("cas_password")
        if not cas_password:
            return error_response("CAS password is required")
        
        db = SessionLocal()
        try:
            user = db.query(models.User).filter(models.User.username == current_username).first()
            if not user:
                return error_response("User not found", 404)
            
            if not user.cas_is_bound or not user.cas_username:
                return error_response("用户未绑定 CAS 账户", 400)
            
            # 验证 CAS 凭证
            is_valid, auth_object, error_msg = verify_cas_credentials(
                user.cas_username,
                cas_password
            )
            
            if not is_valid:
                return error_response(error_msg or "CAS 凭证验证失败", 401)
            
            # 如果验证成功，更新存储的密码（可能用户更改了密码）
            user.cas_password_encrypted = encrypt_cas_password(cas_password)
            db.commit()
            
            return jsonify(success_response({
                "verified": True,
                "message": "CAS 凭证验证成功"
            }))
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Verify CAS credentials error: {str(e)}")
        return error_response(f"Verify CAS credentials failed: {str(e)}", 500)

@user_bp.route("/me/unbind-cas", methods=["POST"])
@jwt_required()
def unbind_cas():
    """解绑 CAS 账户"""
    try:
        current_username = get_jwt_identity()
        if not current_username:
            return error_response("Could not validate credentials", 401)
        
        db = SessionLocal()
        try:
            user = db.query(models.User).filter(models.User.username == current_username).first()
            if not user:
                return error_response("User not found", 404)
            
            if not user.cas_is_bound:
                return error_response("用户未绑定 CAS 账户", 400)
            
            # 解绑 CAS
            user.cas_username = None
            user.cas_password_encrypted = None
            user.cas_is_bound = False
            user.cas_bound_at = None
            
            db.commit()
            db.refresh(user)
            
            return jsonify({
                "message": "CAS 账户解绑成功"
            })
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Unbind CAS error: {str(e)}")
        return error_response(f"Unbind CAS failed: {str(e)}", 500)

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
    """用户登出，将当前token加入黑名单"""
    try:
        db = SessionLocal()
        try:
            # 撤销当前token
            success = revoke_current_token(db)
            
            if success:
                return jsonify({
                    "message": "Successfully logged out",
                    "instruction": "Token has been revoked. Please delete the access token from client storage."
                })
            else:
                logger.warning("Failed to revoke token during logout")
                return error_response("Logout failed: could not revoke token", 500)
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return error_response(f"Logout failed: {str(e)}", 500)

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
