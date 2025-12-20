from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..common.database import SessionLocal
from ..user.models import User
from .services import AssignmentService  # 引入刚才写的 Service
from ..course.services import CourseService  # 引入课程服务
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
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == current_username).first()
        if not user:
            return jsonify({"error": "本地用户不存在"}), 404
        
        # 如果用户已绑定CAS且未提供完整账号密码，尝试使用已绑定账户
        if user.cas_is_bound and user.cas_username:
            if not req_data.get("school_username") and not req_data.get("school_password"):
                # 使用已绑定账户，但需要提供密码验证
                if req_data.get("cas_password"):
                    s_user = user.cas_username
                    s_pass = req_data.get("cas_password")
                else:
                    return jsonify({
                        "error": "请提供CAS密码以验证身份",
                        "requires_password": True,
                        "cas_username": user.cas_username
                    }), 400
            else:
                # 提供了账号密码，使用提供的
                s_user = req_data.get("school_username") or user.cas_username
                s_pass = req_data.get("school_password") or req_data.get("cas_password")
        else:
            # 未绑定CAS，必须提供账号密码
            s_user = req_data.get("school_username") or TEMP_SCHOOL_USERNAME
            s_pass = req_data.get("school_password") or TEMP_SCHOOL_PASSWORD
        
        if not s_user or not s_pass:
            return jsonify({"error": "缺少学校账号密码"}), 400
            
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

# --- 接口 1.5: 统一同步（课程+作业） (POST) ---
@assignment_bp.route("/sync/all", methods=["POST"])
@jwt_required()
def sync_all():
    """
    统一同步接口：同时同步课程和作业
    这样可以确保课程和作业数据的一致性
    """
    current_username = get_jwt_identity()
    req_data = request.get_json() or {}
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == current_username).first()
        if not user:
            return jsonify({"error": "本地用户不存在"}), 404
        
        # 如果用户已绑定CAS且未提供完整账号密码，尝试使用已绑定账户
        if user.cas_is_bound and user.cas_username:
            if not req_data.get("school_username") and not req_data.get("school_password"):
                # 使用已绑定账户，但需要提供密码验证
                if req_data.get("cas_password"):
                    s_user = user.cas_username
                    s_pass = req_data.get("cas_password")
                else:
                    return jsonify({
                        "error": "请提供CAS密码以验证身份",
                        "requires_password": True,
                        "cas_username": user.cas_username
                    }), 400
            else:
                # 提供了账号密码，使用提供的
                s_user = req_data.get("school_username") or user.cas_username
                s_pass = req_data.get("school_password") or req_data.get("cas_password")
        else:
            # 未绑定CAS，必须提供账号密码
            s_user = req_data.get("school_username") or TEMP_SCHOOL_USERNAME
            s_pass = req_data.get("school_password") or TEMP_SCHOOL_PASSWORD
        
        if not s_user or not s_pass:
            return jsonify({"error": "缺少学校账号密码"}), 400
        
        # 1. 先同步课程（课程是基础数据）
        course_stats = CourseService.sync_courses(db, user.id, s_user, s_pass)
        
        # 2. 再同步作业（作业依赖课程）
        assignment_added, assignment_updated, assignment_total = AssignmentService.sync_assignments(db, user.id, s_user, s_pass)
        
        return jsonify({
            "msg": f"同步完成！课程：新增 {course_stats['new_courses']} 门，更新 {course_stats['updated_courses']} 门；作业：新增 {assignment_added} 条，更新 {assignment_updated} 条。",
            "stats": {
                "courses": course_stats,
                "assignments": {
                    "total_fetched": assignment_total,
                    "new_added": assignment_added,
                    "updated": assignment_updated
                }
            }
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

# --- 接口 4: 获取某个课程的作业列表 (GET /course/:course_name) ---
@assignment_bp.route("/course/<path:course_name>", methods=["GET"])
@jwt_required()
def get_course_assignments(course_name):
    """
    获取某个课程的所有作业
    使用 path 转换器以支持URL编码的课程名称
    """
    from urllib.parse import unquote
    current_username = get_jwt_identity()
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == current_username).first()
        if not user:
            return jsonify({"error": "用户未找到"}), 404
        
        # URL解码课程名称（Flask的path转换器不会自动解码）
        decoded_course_name = unquote(course_name)
        
        # 查询该课程的所有作业
        assignments = db.query(models.Assignment)\
            .filter(
                models.Assignment.owner_id == user.id,
                models.Assignment.course_name == decoded_course_name
            )\
            .order_by(models.Assignment.deadline.desc())\
            .all()
        
        data = [{
            "id": a.id,
            "course_name": a.course_name,
            "title": a.title,
            "status": "已提交" if a.is_submitted else "未提交",
            "deadline": a.deadline.isoformat() if a.deadline else None,
            "score": a.score,
            "description": a.description
        } for a in assignments]
        
        return jsonify({"data": data})
    finally:
        db.close()