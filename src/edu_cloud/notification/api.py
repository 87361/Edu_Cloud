from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..common.database import SessionLocal
from ..user.models import User
from .services import NotificationService

notification_bp = Blueprint('notification', __name__)

TEMP_SCHOOL_USERNAME = "" 
TEMP_SCHOOL_PASSWORD = "" 

@notification_bp.route("/sync", methods=["POST"])
@jwt_required()
def sync_notifications():
    current_username = get_jwt_identity()
    req = request.get_json() or {}
    s_user = req.get("school_username") or TEMP_SCHOOL_USERNAME
    s_pass = req.get("school_password") or TEMP_SCHOOL_PASSWORD
    
    if not s_user or not s_pass:
        return jsonify({"error": "Missing credentials"}), 400
        
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == current_username).first()
        if not user: return jsonify({"error": "User not found"}), 404
        
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