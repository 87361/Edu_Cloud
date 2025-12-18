import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from buptmw import BUPT_Auth

# ================= 配置区 =================
API_BASE = "https://apiucloud.bupt.edu.cn/ykt-site"
# ==========================================

def get_auth_session(username, password):
    print(f"正在通过 buptmw 登录: {username}...")
    try:
        auth = BUPT_Auth(cas={"username": username, "password": password})
        return auth.get_Ucloud()
    except Exception as e:
        raise RuntimeError(f"buptmw 登录失败: {e}")

def get_headers(session):
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    token = getattr(session, "access_token", None)
    if token:
        headers["Blade-Auth"] = f"bearer {token}"
    return headers

def extract_user_id(session) -> str:
    user_id = session.cookies.get("iClass-uuid") or session.cookies.get("userId")
    if not user_id and hasattr(session, "user_id"): user_id = str(session.user_id)
    return str(user_id) if user_id else ""

def parse_time_str(time_str):
    """兼容多种时间格式"""
    if not time_str: return None
    # 格式: 2026-01-09 23:59
    if isinstance(time_str, str) and "-" in time_str:
        try:
            # 补全秒数，有些接口返回不带秒
            if time_str.count(":") == 1:
                time_str += ":00"
            return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        except:
            pass
    # 格式: 时间戳
    try:
        ts = int(time_str)
        if ts > 10000000000: ts = ts / 1000
        return datetime.fromtimestamp(ts)
    except:
        return None

def fetch_semester_courses(session, user_id: str) -> List[Dict]:
    """获取课程列表"""
    url = f"{API_BASE}/site/list/student/current"
    # 参数根据抓包修正，current 接口似乎比较严格
    params = {"userId": user_id, "current": 1, "size": 50, "siteRoleCode": 2}
    courses = []
    
    try:
        resp = session.get(url, params=params, headers=get_headers(session))
        if resp.status_code == 200:
            data = resp.json()
            raw_list = data.get("data", [])
            if isinstance(raw_list, dict): raw_list = raw_list.get("records", [])
            
            for c in raw_list:
                site_id = c.get("id") or c.get("siteId")
                name = c.get("name") or c.get("siteName")
                if site_id:
                    courses.append({"id": str(site_id), "name": name})
            print(f"📚 成功获取 {len(courses)} 门课程")
    except Exception as e:
        print(f"❌ 获取课程异常: {e}")
    return courses

def fetch_undone_assignments(session, user_id: str) -> List[Dict]:
    """
    【待办接口】字段名适配
    """
    url = f"{API_BASE}/site/student/undone"
    print(f"正在抓取待办作业...")
    tasks = []
    try:
        resp = session.get(url, params={"userId": user_id}, headers=get_headers(session))
        if resp.status_code == 200:
            data = resp.json()
            records = data.get("data", {}).get("undoneList", [])
            
            for item in records:
                tasks.append({
                    "course_name": item.get("siteName") or "待办事项(未分类)",
                    "title": item.get("activityName") or "无标题待办", # 修正: activityName
                    "description": "", 
                    "deadline": parse_time_str(item.get("endTime")),
                    "is_submitted": False,
                    "score": ""
                })
            print(f"✅ 抓取到 {len(tasks)} 条待办作业")
    except:
        pass
    return tasks

def fetch_course_assignments(session, user_id: str, site_id: str, course_name: str) -> List[Dict]:
    """
    【课程作业接口】字段名适配
    """
    url = f"{API_BASE}/work/student/list"
    
    # 修正：去掉 status 过滤，确保抓到所有作业
    payload = {
        "siteId": site_id, 
        "userId": user_id, 
        "current": 1, 
        "size": 50
        # "status": 0  <-- 去掉这个！
    }
    
    tasks = []
    try:
        resp = session.post(url, json=payload, headers=get_headers(session))
        if resp.status_code == 200:
            data = resp.json()
            records = data.get("data", {}).get("records", [])
            
            for item in records:
                # 修正：通过 submitTime 是否为空来判断提交状态
                submit_time = item.get("submitTime")
                is_submitted = bool(submit_time and submit_time.strip())
                
                # 修正：字段名为 assignmentTitle
                title = item.get("assignmentTitle") or item.get("title") or "无标题作业"
                
                tasks.append({
                    "course_name": course_name,
                    "title": title,
                    "description": item.get("description", ""),
                    "deadline": parse_time_str(item.get("assignmentEndTime")), # 修正: assignmentEndTime
                    "is_submitted": is_submitted,
                    "score": str(item.get("score") or "")
                })
    except Exception as e:
        print(f"   └─ 抓取 {course_name} 失败: {e}")
    return tasks

def fetch_assignments_all(school_username, school_password):
    """主入口"""
    try:
        session = get_auth_session(school_username, school_password)
        user_id = extract_user_id(session)
        print(f"✅ 身份确认: UserID = {user_id}")
    except Exception as e:
        return {"error": str(e)}

    all_tasks = []
    unique_ids = set()

    # 1. 抓待办
    undone_tasks = fetch_undone_assignments(session, user_id)
    for t in undone_tasks:
        uid = f"{t['course_name']}_{t['title']}"
        if uid not in unique_ids:
            all_tasks.append(t)
            unique_ids.add(uid)

    # 2. 抓课程
    courses = fetch_semester_courses(session, user_id)
    
    # 3. 抓详情
    if courses:
        print(f"开始遍历 {len(courses)} 门课程...")
        for course in courses:
            c_tasks = fetch_course_assignments(session, user_id, course["id"], course["name"])
            for t in c_tasks:
                uid = f"{t['course_name']}_{t['title']}"
                
                if uid not in unique_ids:
                    all_tasks.append(t)
                    unique_ids.add(uid)
                else:
                    # 如果已存在，更新状态 (课程接口的数据通常比待办接口更全)
                    for existing in all_tasks:
                        if f"{existing['course_name']}_{existing['title']}" == uid:
                            existing['is_submitted'] = t['is_submitted']
                            existing['score'] = t['score']
                            # 补全课程名
                            if "待办" in existing['course_name']:
                                existing['course_name'] = t['course_name']
                            break
    
    # === 打印核对清单 (给你确认用的) ===
    print(f"\n📊 最终抓取结果汇总 (共 {len(all_tasks)} 个):")
    print("-" * 60)
    print(f"{'课程名称':<15} | {'作业标题':<25} | {'状态'}")
    print("-" * 60)
    for t in all_tasks:
        status = "✅已交" if t['is_submitted'] else "❌未交"
        c_name = t['course_name'][:13] + '..' if len(t['course_name']) > 13 else t['course_name']
        t_title = t['title'][:23] + '..' if len(t['title']) > 23 else t['title']
        print(f"{c_name:<15} | {t_title:<25} | {status}")
    print("-" * 60)
    
    return all_tasks