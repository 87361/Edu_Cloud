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
        """初始化 buptmw 并获取 UCloud Session"""
        try:
            # 1. 初始化认证
            auth = BUPT_Auth(cas={"username": self.username, "password": self.password})
            # 2. 获取 Session (buptmw 自动处理 OAuth 换 Token)
            self.session = auth.get_UCloud()
            
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
            course_name = c.get("name") or c.get("siteName") or ""
            course_id = c.get("id") or c.get("siteId")
            
            # 过滤掉无效的课程名称（未分类、待办事项等）
            if not course_name or "未分类" in course_name or "待办事项" in course_name:
                continue
            
            # 确保课程ID和名称都存在
            if course_id and course_name:
                courses.append({
                    "id": course_id, 
                    "name": course_name
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
                    # 处理课程名称：如果siteName为空、None或包含"未分类"等无效值，则跳过
                    site_name = item.get("siteName") or ""
                    if not site_name or "未分类" in site_name or "待办事项" in site_name:
                        # 尝试从其他字段获取课程信息，如果都没有则跳过这条记录
                        # 因为未分类的作业无法关联到具体课程，不应该存储
                        continue
                    
                    results.append(ScrapedAssignmentData(
                        course_name=site_name,
                        title=item.get("activityName") or "无标题",
                        description="",
                        deadline=self._parse_time(item.get("endTime")),
                        is_submitted=False,
                        score=""
                    ))
        except:
            pass # 待办抓取失败不影响主流程
        return results

    def _fetch_assignment_detail(self, assignment_id: str) -> str:
        """获取单个作业的详情描述"""
        url = f"{API_BASE}/work/student/detail"
        payload = {"id": assignment_id, "userId": self.user_id}
        
        try:
            resp = self.session.post(url, json=payload, headers=self._get_headers())
            if resp.status_code == 200:
                data = resp.json().get("data", {})
                # 尝试多个可能的字段名
                description = (
                    data.get("description") or 
                    data.get("content") or 
                    data.get("detail") or 
                    data.get("assignmentDescription") or
                    ""
                )
                return description if description else ""
        except Exception as e:
            print(f"获取作业详情失败 (ID: {assignment_id}): {str(e)}")
        return ""

    def _fetch_course_details(self, site_id, course_name) -> List[ScrapedAssignmentData]:
        """抓取特定课程的所有作业（包含详情描述）"""
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
                    
                    # 确保课程名称有效（二次检查，防止传入无效值）
                    if not course_name or "未分类" in course_name or "待办事项" in course_name:
                        continue
                    
                    # 获取作业ID（用于获取详情）
                    assignment_id = item.get("id") or item.get("assignmentId") or item.get("workId")
                    
                    # 先从列表接口获取description（尝试多个可能的字段名）
                    description = (
                        item.get("description") or 
                        item.get("content") or 
                        item.get("detail") or 
                        item.get("assignmentDescription") or
                        item.get("workDescription") or
                        ""
                    )
                    
                    # 如果列表接口没有description，且作业ID存在，则调用详情接口
                    if not description and assignment_id:
                        print(f"  [调试] 列表接口无description，尝试获取详情 (作业ID: {assignment_id}, 标题: {item.get('assignmentTitle') or item.get('title')})")
                        description = self._fetch_assignment_detail(str(assignment_id))
                        if description:
                            print(f"  [调试] 成功获取详情，长度: {len(description)}")
                    
                    results.append(ScrapedAssignmentData(
                        course_name=course_name,
                        title=item.get("assignmentTitle") or item.get("title"),
                        description=description,
                        deadline=self._parse_time(item.get("assignmentEndTime")),
                        is_submitted=is_submitted,
                        score=str(item.get("score") or "")
                    ))
        except Exception as e:
            print(f"抓取课程作业失败 (课程: {course_name}): {str(e)}")
        return results

    def run(self) -> List[ScrapedAssignmentData]:
        """
        [对外接口] 执行完整抓取流程
        """
        self._login() # 1. 登录
        
        all_data = {} # 使用字典去重: key=unique_key, value=ScrapedAssignmentData
        
        # # 2. 先抓待办 (速度快)
        # for item in self._fetch_undone():
        #     all_data[item.unique_key] = item
            
        # 3. 再抓课程详情 (数据全)
        courses = self._fetch_courses()
        for course in courses:
            details = self._fetch_course_details(course["id"], course["name"])
            for item in details:
                # 课程详情的数据更准确，直接覆盖待办的数据
                all_data[item.unique_key] = item
                
        return list(all_data.values())