from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..common.database import SessionLocal
from ..user.models import User
from .services import AssignmentService  # 引入刚才写的 Service
from . import models

assignment_bp = Blueprint('assignment', __name__)

# 临时账号 (保持不变，方便调试)
TEMP_SCHOOL_USERNAME = "" 
TEMP_SCHOOL_PASSWORD = "" 

# --- 接口 1: 同步作业 (POST) ---
@assignment_bp.route("/sync", methods=["POST"])
@jwt_required()
def sync_assignments():
    current_username = get_jwt_identity()
    req_data = request.get_json() or {}
    
    # 优先用前端传的，其次用临时的
    s_user = req_data.get("school_username") or TEMP_SCHOOL_USERNAME
    s_pass = req_data.get("school_password") or TEMP_SCHOOL_PASSWORD
    
    if not s_user or not s_pass:
        return jsonify({"error": "缺少学校账号密码"}), 400
        
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == current_username).first()
        if not user:
            return jsonify({"error": "本地用户不存在"}), 404
            
        # 🟢 调用 Service 层处理业务
        added, updated, total = AssignmentService.sync_assignments(db, user.id, s_user, s_pass)
        
        return jsonify({
            "msg": f"同步完成！新增 {added} 条，更新 {updated} 条。",
            "stats": {"total_fetched": total, "new_added": added, "updated": updated}
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

# --- 接口 2: 获取作业列表 (GET) ---
@assignment_bp.route("/", methods=["GET"])
@jwt_required()
def list_assignments():
    current_username = get_jwt_identity()
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == current_username).first()
        if not user:
            return jsonify({"error": "用户未找到"}), 404
            
        # 简单列表只返回基础信息，不返回大段描述
        assignments = db.query(models.Assignment)\
            .filter(models.Assignment.owner_id == user.id)\
            .order_by(models.Assignment.deadline.desc())\
            .all()
            
        data = [{
            "id": a.id,
            "course_name": a.course_name,
            "title": a.title,
            "status": "已提交" if a.is_submitted else "未提交",
            "deadline": a.deadline.isoformat() if a.deadline else None,
            "score": a.score
        } for a in assignments]
            
        return jsonify({"data": data})
    finally:
        db.close()

# --- 接口 3: 获取作业详情 (GET /:id) ---
@assignment_bp.route("/<int:assignment_id>", methods=["GET"])
@jwt_required()
def get_assignment_detail(assignment_id):
    """
    获取单个作业的详细信息（包含描述 description）
    """
    current_username = get_jwt_identity()
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == current_username).first()
        
        # 🟢 调用 Service 层
        task = AssignmentService.get_assignment_detail(db, assignment_id, user.id)
        
        if not task:
            return jsonify({"error": "作业不存在或无权访问"}), 404
            
        return jsonify({
            "data": {
                "id": task.id,
                "course_name": task.course_name,
                "title": task.title,
                "description": task.description,  # 这里返回具体描述 HTML/Text
                "status": "已提交" if task.is_submitted else "未提交",
                "score": task.score,
                "deadline": task.deadline.isoformat() if task.deadline else None,
                "created_at": task.created_at.isoformat()
            }
        })
    finally:
        db.close()