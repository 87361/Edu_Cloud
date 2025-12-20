import time
from datetime import datetime
from typing import List, Dict
from buptmw import BUPT_Auth
from .models import ScrapedAssignmentData

# ================= 配置区 =================
# 修正后的 API 前缀
API_BASE = "https://apiucloud.bupt.edu.cn/ykt-site"
# ==========================================

class AssignmentScraper:
    """
    作业抓取器
    职责：CAS登录验证 + 爬取原始数据 + 转换为 ScrapedAssignmentData
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = None
        self.user_id = None

    def _login(self):
        """初始化 buptmw 并获取 Ucloud Session"""
        try:
            # 1. 初始化认证
            auth = BUPT_Auth(cas={"username": self.username, "password": self.password})
            # 2. 获取 Session (buptmw 自动处理 OAuth 换 Token)
            self.session = auth.get_Ucloud()
            
            # 3. 提取身份标识 (UserId)
            self.user_id = self.session.cookies.get("iClass-uuid") or \
                           self.session.cookies.get("userId") or \
                           getattr(self.session, "user_id", None)
            
            if not self.user_id:
                raise ValueError("登录成功但未能提取 UserID")
                
        except Exception as e:
            # 向上层抛出异常，不在此处打印
            raise RuntimeError(f"学校认证服务连接失败: {str(e)}")

    def _get_headers(self) -> Dict:
        """构造带有 Token 的请求头"""
        headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        # 关键补丁：手动添加 Blade-Auth 头
        token = getattr(self.session, "access_token", None)
        if token:
            headers["Blade-Auth"] = f"bearer {token}"
        return headers

    def _parse_time(self, time_val) -> datetime:
        """通用时间解析工具"""
        if not time_val:
            return None
        try:
            # 情况1: 时间戳
            if isinstance(time_val, (int, float)) or (isinstance(time_val, str) and time_val.isdigit()):
                ts = int(time_val)
                if ts > 10000000000: ts = ts / 1000
                return datetime.fromtimestamp(ts)
            # 情况2: 字符串
            if isinstance(time_val, str):
                if time_val.count(":") == 1: time_val += ":00"
                return datetime.strptime(time_val, "%Y-%m-%d %H:%M:%S")
        except:
            return None
        return None

    def _fetch_courses(self) -> List[Dict]:
        """获取本学期课程列表"""
        url = f"{API_BASE}/site/list/student/current"
        params = {"userId": self.user_id, "current": 1, "size": 50, "siteRoleCode": 2}
        
        resp = self.session.get(url, params=params, headers=self._get_headers())
        resp.raise_for_status()
        
        courses = []
        data = resp.json().get("data", [])
        if isinstance(data, dict): data = data.get("records", [])
        
        for c in data:
            courses.append({
                "id": c.get("id") or c.get("siteId"), 
                "name": c.get("name") or c.get("siteName")
            })
        return courses

    def _fetch_undone(self) -> List[ScrapedAssignmentData]:
        """抓取待办事项中的作业"""
        url = f"{API_BASE}/site/student/undone"
        results = []
        
        try:
            resp = self.session.get(url, params={"userId": self.user_id}, headers=self._get_headers())
            if resp.status_code == 200:
                records = resp.json().get("data", {}).get("undoneList", [])
                for item in records:
                    results.append(ScrapedAssignmentData(
                        course_name=item.get("siteName") or "未知课程",
                        title=item.get("activityName") or "无标题",
                        description="",
                        deadline=self._parse_time(item.get("endTime")),
                        is_submitted=False,
                        score=""
                    ))
        except:
            pass # 待办抓取失败不影响主流程
        return results

    def _fetch_course_details(self, site_id, course_name) -> List[ScrapedAssignmentData]:
        """抓取特定课程的所有作业"""
        url = f"{API_BASE}/work/student/list"
        payload = {"siteId": site_id, "userId": self.user_id, "current": 1, "size": 50}
        results = []
        
        try:
            resp = self.session.post(url, json=payload, headers=self._get_headers())
            if resp.status_code == 200:
                records = resp.json().get("data", {}).get("records", [])
                for item in records:
                    # 判断是否提交
                    submit_time = item.get("submitTime")
                    is_submitted = bool(submit_time and str(submit_time).strip())
                    
                    results.append(ScrapedAssignmentData(
                        course_name=course_name,
                        title=item.get("assignmentTitle") or item.get("title"),
                        description=item.get("description", ""),
                        deadline=self._parse_time(item.get("assignmentEndTime")),
                        is_submitted=is_submitted,
                        score=str(item.get("score") or "")
                    ))
        except:
            pass
        return results

    def run(self) -> List[ScrapedAssignmentData]:
        """
        [对外接口] 执行完整抓取流程
        """
        self._login() # 1. 登录
        
        all_data = {} # 使用字典去重: key=unique_key, value=ScrapedAssignmentData
        
        # 2. 先抓待办 (速度快)
        for item in self._fetch_undone():
            all_data[item.unique_key] = item
            
        # 3. 再抓课程详情 (数据全)
        courses = self._fetch_courses()
        for course in courses:
            details = self._fetch_course_details(course["id"], course["name"])
            for item in details:
                # 课程详情的数据更准确，直接覆盖待办的数据
                all_data[item.unique_key] = item
                
        return list(all_data.values())