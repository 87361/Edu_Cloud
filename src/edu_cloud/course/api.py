# 负责接口：/sync, /list, /resources
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..common.database import SessionLocal
from ..user.models import User
from .services import CourseService
from . import models

course_bp = Blueprint('course', __name__)

# 临时账号 (开发用)
TEMP_SCHOOL_USERNAME = "" 
TEMP_SCHOOL_PASSWORD = "" 

# --- 1. 同步课程 (包含资源) ---
@course_bp.route("/sync", methods=["POST"])
@jwt_required()
def sync_courses():
    current_username = get_jwt_identity()
    req = request.get_json() or {}
    
    s_user = req.get("school_username") or TEMP_SCHOOL_USERNAME
    s_pass = req.get("school_password") or TEMP_SCHOOL_PASSWORD
    
    if not s_user or not s_pass:
        return jsonify({"error": "Missing school credentials"}), 400
        
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == current_username).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        stats = CourseService.sync_courses(db, user.id, s_user, s_pass)
        
        return jsonify({
            "msg": "课程同步完成",
            "stats": stats
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

# --- 2. 获取课程列表 ---
@course_bp.route("/", methods=["GET"])
@jwt_required()
def list_courses():
    current_username = get_jwt_identity()
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == current_username).first()
        
        courses = db.query(models.Course).filter(models.Course.owner_id == user.id).all()
        
        data = [{
            "id": c.id, # siteId
            "name": c.name,
            "teacher": c.teacher,
            "term": c.term_name,
            "pic_url": c.pic_url,
            "dept": c.dept_name
        } for c in courses]
        
        return jsonify({"data": data})
    finally:
        db.close()

# --- 3. 获取某门课的详情 (包含简介) ---
@course_bp.route("/<course_id>", methods=["GET"])
@jwt_required()
def get_course_detail(course_id):
    db = SessionLocal()
    try:
        course = db.query(models.Course).filter(models.Course.id == course_id).first()
        if not course:
            return jsonify({"error": "Course not found"}), 404
            
        return jsonify({
            "data": {
                "id": course.id,
                "name": course.name,
                "description": course.description, # HTML简介
                "teacher": course.teacher,
                "updated_at": course.last_updated.isoformat() if course.last_updated else None
            }
        })
    finally:
        db.close()

# --- 4. 获取某门课的资源列表 (PPT/讲义) ---
@course_bp.route("/<course_id>/resources", methods=["GET"])
@jwt_required()
def list_course_resources(course_id):
    db = SessionLocal()
    try:
        resources = CourseService.get_course_resources(db, course_id)
        
        data = [{
            "id": r.id,
            "title": r.title,
            "type": r.file_type,
            "size": r.file_size,
            "section": r.parent_section, # 章节名
            "url": r.download_url
        } for r in resources]
        
        return jsonify({"data": data})
    finally:
        db.close()