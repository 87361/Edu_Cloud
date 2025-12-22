"""
管理员API模块，提供数据库查看和管理功能
"""
from datetime import datetime, timezone, timedelta
from flask import Blueprint, jsonify, request
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, Any, List
import logging

from ..common.database import SessionLocal, engine
from ..common.auth import admin_required
from ..user import models as user_models
from ..course import models as course_models
from ..assignment import models as assignment_models
from ..discussion import models as discussion_models
from ..notification import models as notification_models

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
    
    注意：敏感字段（如密码）会被标记，但不会在数据查看时返回
    """
    # 定义敏感字段列表
    SENSITIVE_FIELDS = {
        'hashed_password',
        'cas_password_encrypted',
        'password',
        'password_hash',
        'password_encrypted'
    }
    
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        table_info = []
        for table_name in tables:
            columns = inspector.get_columns(table_name)
            column_info = []
            for col in columns:
                col_name = col["name"]
                is_sensitive = col_name.lower() in SENSITIVE_FIELDS
                column_info.append({
                    "name": col_name,
                    "type": str(col["type"]),
                    "nullable": col.get("nullable", True),
                    "default": str(col.get("default", "")) if col.get("default") else None,
                    "sensitive": is_sensitive  # 标记是否为敏感字段
                })
            
            table_info.append({
                "name": table_name,
                "columns": column_info,
                "column_count": len(columns)
            })
        
        return jsonify(success_response({
            "tables": table_info,
            "table_count": len(tables),
            "note": "Sensitive fields (passwords) are marked but will not be returned when viewing table data"
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
            
            # 课程统计
            total_courses = db.query(course_models.Course).count()
            # 统计活跃课程（最近30天有更新的）
            thirty_days_ago = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            thirty_days_ago = thirty_days_ago - timedelta(days=30)
            active_courses = db.query(course_models.Course).filter(
                course_models.Course.last_updated >= thirty_days_ago
            ).count()
            
            stats["courses"] = {
                "total": total_courses,
                "active": active_courses,
                "inactive": total_courses - active_courses
            }
            
            # 作业统计
            total_assignments = db.query(assignment_models.Assignment).count()
            submitted_assignments = db.query(assignment_models.Assignment).filter(
                assignment_models.Assignment.is_submitted == True
            ).count()
            # 今日作业（今天创建的）
            today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            today_assignments = db.query(assignment_models.Assignment).filter(
                assignment_models.Assignment.created_at >= today_start
            ).count()
            # 待提交作业（未提交且未过期）
            pending_assignments = db.query(assignment_models.Assignment).filter(
                assignment_models.Assignment.is_submitted == False,
                assignment_models.Assignment.deadline >= datetime.now(timezone.utc)
            ).count()
            
            stats["assignments"] = {
                "total": total_assignments,
                "submitted": submitted_assignments,
                "pending": pending_assignments,
                "today": today_assignments
            }
            
            # 讨论统计
            total_topics = db.query(discussion_models.DiscussionTopic).count()
            total_posts = db.query(discussion_models.DiscussionPost).count()
            # 最近7天的讨论
            seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
            recent_topics = db.query(discussion_models.DiscussionTopic).filter(
                discussion_models.DiscussionTopic.created_at >= seven_days_ago
            ).count()
            
            stats["discussions"] = {
                "total_topics": total_topics,
                "total_posts": total_posts,
                "recent_topics": recent_topics
            }
            
            # 通知统计
            total_notifications = db.query(notification_models.Notification).count()
            unread_notifications = db.query(notification_models.Notification).filter(
                notification_models.Notification.is_read == False
            ).count()
            # 今日通知
            today_notifications = db.query(notification_models.Notification).filter(
                notification_models.Notification.created_at >= today_start
            ).count()
            
            stats["notifications"] = {
                "total": total_notifications,
                "unread": unread_notifications,
                "read": total_notifications - unread_notifications,
                "today": today_notifications
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
    
    注意：敏感字段（如密码哈希）会被自动过滤，不会返回
    
    Query参数:
    - limit: 限制返回的记录数（默认100，最大1000）
    - offset: 偏移量（默认0）
    """
    # 定义敏感字段列表（这些字段不会被返回）
    SENSITIVE_FIELDS = {
        'hashed_password',
        'cas_password_encrypted',
        'password',  # 通用密码字段
        'password_hash',
        'password_encrypted'
    }
    
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
            # 获取表的所有列名
            columns_info = inspector.get_columns(table_name)
            all_columns = [col['name'] for col in columns_info]
            
            # 过滤掉敏感字段
            safe_columns = [col for col in all_columns if col.lower() not in SENSITIVE_FIELDS]
            
            if not safe_columns:
                return error_response("No accessible columns in this table", 403)
            
            # 构建SELECT语句，只选择非敏感字段
            columns_str = ', '.join(safe_columns)
            result = db.execute(text(f"SELECT {columns_str} FROM {table_name} LIMIT :limit OFFSET :offset"), {
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
            
            # 记录被过滤的字段
            filtered_fields = [col for col in all_columns if col.lower() in SENSITIVE_FIELDS]
            
            response_data = {
                "table_name": table_name,
                "data": data,
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + len(data) < total
            }
            
            # 如果有字段被过滤，在响应中说明
            if filtered_fields:
                response_data["filtered_fields"] = filtered_fields
                response_data["note"] = "Sensitive fields (passwords) have been filtered for security"
            
            return jsonify(success_response(response_data))
            
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


@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(current_user, user_id: int):
    """
    删除用户（管理员专用）
    需要管理员权限
    
    注意：
    - 不能删除自己
    - 会级联删除该用户的所有关联数据（作业、课程、通知等）
    """
    logger.info(f"删除用户请求: 管理员={current_user.username}, 目标用户ID={user_id}")
    try:
        db = SessionLocal()
        try:
            # 检查不能删除自己
            if current_user.id == user_id:
                logger.warning(f"管理员 {current_user.username} 尝试删除自己的账号")
                return error_response("不能删除自己的账号", 400)
            
            # 查找要删除的用户
            user = db.query(user_models.User).filter(user_models.User.id == user_id).first()
            if not user:
                logger.warning(f"用户ID {user_id} 不存在")
                return error_response(f"用户ID {user_id} 不存在", 404)
            
            # 统计关联数据数量（用于返回信息）
            assignment_count = db.query(assignment_models.Assignment).filter(
                assignment_models.Assignment.owner_id == user_id
            ).count()
            
            course_count = db.query(course_models.Course).filter(
                course_models.Course.owner_id == user_id
            ).count()
            
            notification_count = db.query(notification_models.Notification).filter(
                notification_models.Notification.owner_id == user_id
            ).count()
            
            token_count = db.query(user_models.TokenBlacklist).filter(
                user_models.TokenBlacklist.username == user.username
            ).count()
            
            # 删除关联数据（按顺序删除，避免外键约束问题）
            # 1. 删除课程资源（如果存在）
            from ..course.models import CourseResource
            courses = db.query(course_models.Course).filter(
                course_models.Course.owner_id == user_id
            ).all()
            for course in courses:
                db.query(CourseResource).filter(
                    CourseResource.course_id == course.id
                ).delete()
            
            # 2. 删除课程
            db.query(course_models.Course).filter(
                course_models.Course.owner_id == user_id
            ).delete()
            
            # 3. 删除作业
            db.query(assignment_models.Assignment).filter(
                assignment_models.Assignment.owner_id == user_id
            ).delete()
            
            # 4. 删除通知
            db.query(notification_models.Notification).filter(
                notification_models.Notification.owner_id == user_id
            ).delete()
            
            # 5. 删除Token黑名单记录
            db.query(user_models.TokenBlacklist).filter(
                user_models.TokenBlacklist.username == user.username
            ).delete()
            
            # 6. 最后删除用户本身
            username = user.username
            db.delete(user)
            db.commit()
            
            logger.info(f"管理员 {current_user.username} 删除了用户 {username} (ID: {user_id})")
            
            return jsonify(success_response({
                "message": f"用户 {username} 已成功删除",
                "deleted_data": {
                    "assignments": assignment_count,
                    "courses": course_count,
                    "notifications": notification_count,
                    "tokens": token_count
                }
            }))
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"删除用户时数据库错误: {str(e)}")
            return error_response(f"删除用户失败: {str(e)}", 500)
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"删除用户错误: {str(e)}")
        return error_response(f"删除用户失败: {str(e)}", 500)


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

