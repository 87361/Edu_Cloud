from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..common.database import SessionLocal
from ..user.models import User
from .services import NotificationService
from . import models

notification_bp = Blueprint('notification', __name__)

TEMP_SCHOOL_USERNAME = "" 
TEMP_SCHOOL_PASSWORD = "" 

@notification_bp.route("/sync", methods=["POST"])
@jwt_required()
def sync_notifications():
    current_username = get_jwt_identity()
    req = request.get_json() or {}
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == current_username).first()
        if not user: 
            return jsonify({"error": "User not found"}), 404
        
        # 如果用户已绑定CAS且未提供完整账号密码，尝试使用已绑定账户
        if user.cas_is_bound and user.cas_username:
            if not req.get("school_username") and not req.get("school_password"):
                # 使用已绑定账户，但需要提供密码验证
                if req.get("cas_password"):
                    s_user = user.cas_username
                    s_pass = req.get("cas_password")
                else:
                    return jsonify({
                        "error": "请提供CAS密码以验证身份",
                        "requires_password": True,
                        "cas_username": user.cas_username
                    }), 400
            else:
                # 提供了账号密码，使用提供的
                s_user = req.get("school_username") or user.cas_username
                s_pass = req.get("school_password") or req.get("cas_password")
        else:
            # 未绑定CAS，必须提供账号密码
            s_user = req.get("school_username") or TEMP_SCHOOL_USERNAME
            s_pass = req.get("school_password") or TEMP_SCHOOL_PASSWORD
        
        if not s_user or not s_pass:
            return jsonify({"error": "Missing credentials"}), 400
        
        added, updated, total = NotificationService.sync_notifications(db, user.id, s_user, s_pass)
        
        return jsonify({
            "msg": "公告同步完成",
            "stats": {"total": total, "added": added, "updated": updated}
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@notification_bp.route("/", methods=["GET"])
@jwt_required()
def list_notifications():
    current_username = get_jwt_identity()
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == current_username).first()
        msgs = NotificationService.get_user_notifications(db, user.id)
        
        data = [{
            "id": m.id,
            "title": m.title,
            "type": m.msg_type,
            "content": m.content, # 这里通常包含HTML标签
            "is_read": m.is_read,
            "time": m.publish_time.isoformat() if m.publish_time else None
        } for m in msgs]
        
        return jsonify({"data": data})
    finally:
        db.close()

@notification_bp.route("/course/<path:course_name>", methods=["GET"])
@jwt_required()
def get_course_notifications(course_name):
    """
    获取某个课程的公告列表
    通过课程名称匹配，并过滤掉以前学期的公告
    使用 path 转换器以支持URL编码的课程名称
    """
    from urllib.parse import unquote
    from ..course.models import Course
    
    current_username = get_jwt_identity()
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == current_username).first()
        if not user:
            return jsonify({"error": "用户未找到"}), 404
        
        # URL解码课程名称（Flask的path转换器不会自动解码）
        decoded_course_name = unquote(course_name)
        
        # 查找该课程，获取学期信息
        course = db.query(Course).filter(
            Course.owner_id == user.id,
            Course.name == decoded_course_name
        ).first()
        
        # 获取该课程的所有公告（通过标题匹配课程名称）
        notifications = db.query(models.Notification).filter(
            models.Notification.owner_id == user.id,
            models.Notification.title == decoded_course_name
        ).order_by(models.Notification.publish_time.desc()).all()
        
        # 如果有课程信息，过滤掉以前学期的公告
        filtered_notifications = []
        if course and course.term_name:
            # 提取当前学期年份（例如："2025秋季" -> 2025）
            try:
                current_term_year = int(course.term_name[:4])
                for n in notifications:
                    if n.publish_time:
                        # 只显示当前学期及以后的公告
                        if n.publish_time.year >= current_term_year:
                            filtered_notifications.append(n)
                    else:
                        # 如果没有发布时间，保留（可能是系统通知）
                        filtered_notifications.append(n)
            except:
                # 如果解析失败，返回所有公告
                filtered_notifications = notifications
        else:
            # 如果没有课程信息，返回最近一年的公告
            from datetime import datetime, timedelta, timezone
            one_year_ago = datetime.now(timezone.utc) - timedelta(days=365)
            filtered_notifications = [
                n for n in notifications 
                if not n.publish_time or n.publish_time >= one_year_ago
            ]
        
        data = [{
            "id": n.id,
            "title": n.title,
            "type": n.msg_type,
            "content": n.content,
            "is_read": n.is_read,
            "time": n.publish_time.isoformat() if n.publish_time else None
        } for n in filtered_notifications]
        
        return jsonify({"data": data})
    finally:
        db.close()