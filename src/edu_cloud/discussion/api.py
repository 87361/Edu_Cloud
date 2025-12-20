# 接口(/sync, /list, /detail)
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..common.database import SessionLocal
from .services import DiscussionService

discussion_bp = Blueprint('discussion', __name__)

# 临时账号
TEMP_SCHOOL_USERNAME = "" 
TEMP_SCHOOL_PASSWORD = "" 

# --- 1. 同步讨论区 ---
@discussion_bp.route("/sync", methods=["POST"])
@jwt_required()
def sync_discussions():
    req = request.get_json() or {}
    s_user = req.get("school_username") or TEMP_SCHOOL_USERNAME
    s_pass = req.get("school_password") or TEMP_SCHOOL_PASSWORD
    
    if not s_user or not s_pass:
        return jsonify({"error": "Missing credentials"}), 400
        
    db = SessionLocal()
    try:
        # 讨论区是公开的，不需要查本地 user_id，只需要 CAS 账号去爬
        stats = DiscussionService.sync_discussions(db, s_user, s_pass)
        return jsonify({"msg": "讨论区同步完成", "stats": stats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

# --- 2. 获取某门课的讨论列表 ---
@discussion_bp.route("/list", methods=["GET"])
@jwt_required()
def list_course_topics():
    # 参数: ?course_id=195769...
    course_id = request.args.get("course_id")
    if not course_id:
        return jsonify({"error": "Missing course_id"}), 400
        
    db = SessionLocal()
    try:
        topics = DiscussionService.get_course_topics(db, course_id)
        data = [{
            "id": t.id,
            "title": t.title,
            "author": t.author_name,
            "reply_count": t.reply_count,
            "view_count": t.view_count,
            "created_at": t.created_at.isoformat() if t.created_at else None
        } for t in topics]
        return jsonify({"data": data})
    finally:
        db.close()

# --- 3. 获取帖子详情和回复 ---
@discussion_bp.route("/<topic_id>", methods=["GET"])
@jwt_required()
def get_topic_detail(topic_id):
    db = SessionLocal()
    try:
        topic, posts = DiscussionService.get_topic_detail(db, topic_id)
        if not topic:
            return jsonify({"error": "Topic not found"}), 404
            
        return jsonify({
            "topic": {
                "id": topic.id,
                "title": topic.title,
                "content": topic.content, # HTML
                "author": topic.author_name,
                "created_at": topic.created_at.isoformat() if topic.created_at else None
            },
            "posts": [{
                "id": p.id,
                "author": p.author_name,
                "content": p.content,
                "floor": p.floor,
                "created_at": p.created_at.isoformat() if p.created_at else None
            } for p in posts]
        })
    finally:
        db.close()