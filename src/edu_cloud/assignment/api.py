from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from datetime import datetime

# 导入公共工具
from ..common.database import SessionLocal
from ..user.models import User
from . import models, schemas, scraper  # 导入你刚才写的 scraper

# 创建蓝图
assignment_bp = Blueprint('assignment', __name__)

# ==========================================
# 🛑 临时测试区：在这里填你的账号密码
# 测完记得删掉，或者不要提交到 GitHub！
# ==========================================
TEMP_SCHOOL_USERNAME = ""  # 已清空，由前端传递
TEMP_SCHOOL_PASSWORD = ""  # 已清空，由前端传递
# ==========================================

def success_response(data):
    """统一成功返回格式"""
    return {"data": data}

def error_response(msg, code=400):
    return jsonify({"error": msg}), code

# --- 接口 1: 获取我的作业列表 (给前端展示用) ---
@assignment_bp.route("/", methods=["GET"])
@jwt_required()
def get_my_assignments():
    """获取当前登录用户的所有作业"""
    current_username = get_jwt_identity()
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == current_username).first()
        if not user:
            return error_response("User not found", 404)
        
        # 按截止时间倒序排列
        assignments = db.query(models.Assignment)\
            .filter(models.Assignment.owner_id == user.id)\
            .order_by(models.Assignment.deadline.desc())\
            .all()
        
        # 整理成 JSON 格式
        result = []
        for a in assignments:
            result.append({
                "id": a.id,
                "course_name": a.course_name,
                "title": a.title,
                "description": a.description,
                "status": "已提交" if a.is_submitted else "未提交",
                "deadline": a.deadline.isoformat() if a.deadline else "无截止日期",
                "score": a.score
            })
        return jsonify({"data": result})
    finally:
        db.close()

# --- 接口 2: 一键同步作业 (爬虫入口) ---
@assignment_bp.route("/sync", methods=["POST"])
@jwt_required()
def sync_from_school():
    """
    调用 buptmw 爬虫抓取数据
    优先使用前端传来的账号密码，如果没有，就用上面写死的 TEMP 账号密码
    """
    # === 新增这两行调试代码 ===
    import sys
    print("【调试】收到同步请求了！正在准备处理...", flush=True) 
    # ========================

    current_username = get_jwt_identity()
    # ... 后面的代码保持不变
    current_username = get_jwt_identity()
    req_data = request.get_json() or {} # 防止报错
    
    # 1. 确定使用哪个账号密码
    s_user = req_data.get("school_username") or TEMP_SCHOOL_USERNAME
    s_pass = req_data.get("school_password") or TEMP_SCHOOL_PASSWORD
    
    # 简单的检查
    if "xxxx" in s_user or not s_pass:
        return error_response("请在 api.py 中填写临时账号密码，或者通过前端传递！")
        
    db = SessionLocal()
    try:
        # 2. 找到当前登录系统的用户（要把作业挂在他名下）
        user = db.query(User).filter(User.username == current_username).first()
        if not user:
            return error_response("本地用户未找到", 404)
            
        print(f"开始同步作业，使用学号: {s_user}...")
        
        # 3. 调用 scraper (这是最耗时的一步)
        crawled_data = scraper.fetch_assignments_all(s_user, s_pass)
        
        # 检查是不是报错了
        if isinstance(crawled_data, dict) and "error" in crawled_data:
             return error_response(crawled_data["error"], 500)
             
        # 4. 存入数据库 (查重逻辑)
        new_count = 0
        update_count = 0
        
        for task in crawled_data:
            # 查重条件：同一个用户 + 同一门课 + 同一个作业名
            exists = db.query(models.Assignment).filter(
                models.Assignment.owner_id == user.id,
                models.Assignment.title == task["title"],
                models.Assignment.course_name == task["course_name"]
            ).first()
            
            if exists:
                # 如果已存在，更新状态和分数
                exists.is_submitted = task["is_submitted"]
                exists.score = task["score"]
                exists.deadline = task["deadline"]
                update_count += 1
            else:
                # 如果不存在，创建新的
                new_assign = models.Assignment(
                    owner_id=user.id,
                    course_name=task["course_name"],
                    title=task["title"],
                    description=task["description"],
                    deadline=task["deadline"],
                    is_submitted=task["is_submitted"],
                    score=task["score"]
                )
                db.add(new_assign)
                new_count += 1
        
        db.commit()
        
        msg = f"同步完成！新增 {new_count} 条，更新 {update_count} 条。"
        print(msg)
        return jsonify({
            "msg": msg, 
            "new_added": new_count, 
            "total_synced": len(crawled_data)
        })
        
    except Exception as e:
        print(f"同步出错: {e}")
        return error_response(str(e), 500)
    finally:
        db.close()