"""
管理员API模块，提供数据库查看和管理功能
"""
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, Any, List
import logging

from ..common.database import SessionLocal, engine
from ..common.auth import admin_required
from ..user import models as user_models

logger = logging.getLogger(__name__)

# 创建管理员蓝图
admin_bp = Blueprint('admin', __name__)


def success_response(data: Any) -> Dict[str, Any]:
    """统一成功响应格式"""
    return {"data": data}


def error_response(message: str, code: int = 400) -> tuple:
    """统一错误响应格式"""
    return {"error": message}, code


@admin_bp.route("/database/tables", methods=["GET"])
@admin_required
def get_database_tables(current_user):
    """
    获取所有数据库表列表
    需要管理员权限
    """
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        table_info = []
        for table_name in tables:
            columns = inspector.get_columns(table_name)
            table_info.append({
                "name": table_name,
                "columns": [
                    {
                        "name": col["name"],
                        "type": str(col["type"]),
                        "nullable": col.get("nullable", True),
                        "default": str(col.get("default", "")) if col.get("default") else None
                    }
                    for col in columns
                ],
                "column_count": len(columns)
            })
        
        return jsonify(success_response({
            "tables": table_info,
            "table_count": len(tables)
        }))
        
    except Exception as e:
        logger.error(f"Error getting database tables: {str(e)}")
        return error_response(f"Failed to get database tables: {str(e)}", 500)


@admin_bp.route("/database/stats", methods=["GET"])
@admin_required
def get_database_stats(current_user):
    """
    获取数据库统计信息
    需要管理员权限
    """
    try:
        db = SessionLocal()
        try:
            stats = {}
            
            # 用户统计
            total_users = db.query(user_models.User).count()
            active_users = db.query(user_models.User).filter(user_models.User.is_active == True).count()
            admin_users = db.query(user_models.User).filter(user_models.User.role == 'admin').count()
            cas_bound_users = db.query(user_models.User).filter(user_models.User.cas_is_bound == True).count()
            
            stats["users"] = {
                "total": total_users,
                "active": active_users,
                "inactive": total_users - active_users,
                "admins": admin_users,
                "cas_bound": cas_bound_users
            }
            
            # Token黑名单统计
            current_time = datetime.now(timezone.utc)
            total_revoked = db.query(user_models.TokenBlacklist).count()
            active_revoked = db.query(user_models.TokenBlacklist).filter(
                user_models.TokenBlacklist.expires_at > current_time
            ).count()
            
            stats["tokens"] = {
                "total_revoked": total_revoked,
                "active_revoked": active_revoked,
                "expired_revoked": total_revoked - active_revoked
            }
            
            # 数据库大小（SQLite）
            if engine.url.drivername == 'sqlite':
                result = db.execute(text("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()"))
                size_row = result.fetchone()
                if size_row:
                    stats["database"] = {
                        "size_bytes": size_row[0],
                        "size_mb": round(size_row[0] / (1024 * 1024), 2)
                    }
            
            return jsonify(success_response(stats))
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")
        return error_response(f"Failed to get database stats: {str(e)}", 500)


@admin_bp.route("/database/table/<table_name>", methods=["GET"])
@admin_required
def get_table_data(current_user, table_name: str):
    """
    获取指定表的数据
    需要管理员权限
    
    Query参数:
    - limit: 限制返回的记录数（默认100，最大1000）
    - offset: 偏移量（默认0）
    """
    try:
        # 安全检查：只允许查询已知的表
        inspector = inspect(engine)
        allowed_tables = inspector.get_table_names()
        
        if table_name not in allowed_tables:
            return error_response(f"Table '{table_name}' not found or access denied", 404)
        
        # 获取分页参数
        limit = min(int(request.args.get('limit', 100)), 1000)  # 最大1000条
        offset = int(request.args.get('offset', 0))
        
        db = SessionLocal()
        try:
            # 动态查询表数据
            result = db.execute(text(f"SELECT * FROM {table_name} LIMIT :limit OFFSET :offset"), {
                "limit": limit,
                "offset": offset
            })
            
            columns = result.keys()
            rows = result.fetchall()
            
            # 转换为字典列表
            data = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    # 处理datetime对象
                    if hasattr(value, 'isoformat'):
                        row_dict[col] = value.isoformat()
                    else:
                        row_dict[col] = value
                data.append(row_dict)
            
            # 获取总数
            count_result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            total = count_result.scalar()
            
            return jsonify(success_response({
                "table_name": table_name,
                "data": data,
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + len(data) < total
            }))
            
        finally:
            db.close()
            
    except SQLAlchemyError as e:
        logger.error(f"Database error getting table data: {str(e)}")
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        logger.error(f"Error getting table data: {str(e)}")
        return error_response(f"Failed to get table data: {str(e)}", 500)


@admin_bp.route("/users", methods=["GET"])
@admin_required
def get_all_users(current_user):
    """
    获取所有用户列表（管理员专用）
    需要管理员权限
    
    Query参数:
    - limit: 限制返回的记录数（默认100）
    - offset: 偏移量（默认0）
    - role: 按角色筛选（可选：'user' 或 'admin'）
    - is_active: 按活跃状态筛选（可选：'true' 或 'false'）
    """
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        role_filter = request.args.get('role')
        is_active_filter = request.args.get('is_active')
        
        db = SessionLocal()
        try:
            query = db.query(user_models.User)
            
            # 应用筛选条件
            if role_filter:
                query = query.filter(user_models.User.role == role_filter)
            if is_active_filter is not None:
                is_active = is_active_filter.lower() == 'true'
                query = query.filter(user_models.User.is_active == is_active)
            
            # 获取总数
            total = query.count()
            
            # 获取分页数据
            users = query.order_by(user_models.User.created_at.desc()).offset(offset).limit(limit).all()
            
            users_data = []
            for user in users:
                users_data.append({
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "cas_username": user.cas_username,
                    "cas_is_bound": user.cas_is_bound,
                    "cas_bound_at": user.cas_bound_at.isoformat() if user.cas_bound_at else None
                })
            
            return jsonify(success_response({
                "users": users_data,
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + len(users_data) < total
            }))
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error getting all users: {str(e)}")
        return error_response(f"Failed to get users: {str(e)}", 500)


@admin_bp.route("/tokens/blacklist", methods=["GET"])
@admin_required
def get_token_blacklist(current_user):
    """
    获取token黑名单列表（管理员专用）
    需要管理员权限
    
    Query参数:
    - limit: 限制返回的记录数（默认100）
    - offset: 偏移量（默认0）
    - username: 按用户名筛选（可选）
    """
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        username_filter = request.args.get('username')
        
        db = SessionLocal()
        try:
            query = db.query(user_models.TokenBlacklist)
            
            # 应用筛选条件
            if username_filter:
                query = query.filter(user_models.TokenBlacklist.username == username_filter)
            
            # 获取总数
            total = query.count()
            
            # 获取分页数据
            tokens = query.order_by(user_models.TokenBlacklist.revoked_at.desc()).offset(offset).limit(limit).all()
            
            tokens_data = []
            for token in tokens:
                tokens_data.append({
                    "id": token.id,
                    "jti": token.jti,
                    "token_type": token.token_type,
                    "username": token.username,
                    "revoked_at": token.revoked_at.isoformat() if token.revoked_at else None,
                    "expires_at": token.expires_at.isoformat() if token.expires_at else None
                })
            
            return jsonify(success_response({
                "tokens": tokens_data,
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + len(tokens_data) < total
            }))
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error getting token blacklist: {str(e)}")
        return error_response(f"Failed to get token blacklist: {str(e)}", 500)


@admin_bp.route("/health", methods=["GET"])
@admin_required
def admin_health_check(current_user):
    """
    管理员健康检查端点
    需要管理员权限
    """
    return jsonify(success_response({
        "status": "healthy",
        "admin": current_user.username,
        "message": "Admin access verified"
    }))

