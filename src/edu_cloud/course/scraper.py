# 只负责调用那3个API，清洗数据，返回 Dataclass
import time
from datetime import datetime
from typing import List, Dict
from buptmw import BUPT_Auth
from .models import ScrapedCourseData, ScrapedResourceData

# API 配置
API_BASE = "https://apiucloud.bupt.edu.cn/ykt-site"

class CourseScraper:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = None
        self.user_id = None

    def _login(self):
        """初始化 buptmw (复用 assignment 的成功逻辑)"""
        try:
            auth = BUPT_Auth(cas={"username": self.username, "password": self.password})
            self.session = auth.get_Ucloud()
            
            # 尝试多种方式获取 ID
            self.user_id = self.session.cookies.get("iClass-uuid") or \
                           self.session.cookies.get("userId") or \
                           getattr(self.session, "user_id", None)
            
            if not self.user_id:
                raise ValueError("登录成功但 UserID 缺失")
        except Exception as e:
            raise RuntimeError(f"认证失败: {str(e)}")

    def _get_headers(self) -> Dict:
        headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        token = getattr(self.session, "access_token", None)
        if token:
            headers["Blade-Auth"] = f"bearer {token}"
        return headers

    def _fetch_course_list_raw(self) -> List[Dict]:
        """1. 获取本学期课程列表 (对应你提供的接口3)"""
        url = f"{API_BASE}/site/list/student/current"
        # 使用你截图里的参数
        params = {
            "userId": self.user_id,
            "current": 1, 
            "size": 50, # 足够大了
            "siteRoleCode": 2
        }
        try:
            resp = self.session.get(url, params=params, headers=self._get_headers())
            if resp.status_code == 200:
                data = resp.json()
                return data.get("data", {}).get("records", [])
        except Exception as e:
            print(f"获取课程列表失败: {e}")
        return []

    def _fetch_course_detail_raw(self, site_id) -> Dict:
        """2. 获取课程详细信息 (对应你提供的接口2)"""
        url = f"{API_BASE}/site/detail"
        try:
            resp = self.session.get(url, params={"id": site_id}, headers=self._get_headers())
            if resp.status_code == 200:
                return resp.json().get("data", {})
        except:
            pass
        return {}

    def _fetch_course_resources(self, site_id) -> List[ScrapedResourceData]:
        """3. 获取课程主页讲义/资源 (对应你提供的接口1)"""
        url = f"{API_BASE}/site-resource/tree/student"
        params = {"siteId": site_id, "userId": self.user_id}
        
        resources = []
        try:
            # 这是一个 POST 请求，虽然截图显示 Params 里有参数，但通常 POST 也要发 body 或者 query
            # 根据截图，参数在 Query 里。
            resp = self.session.post(url, params=params, headers=self._get_headers())
            
            if resp.status_code == 200:
                # 这是一个树状结构，我们需要递归或者双层循环
                # 数据结构: data -> list[Node] -> attachmentVOs -> list[File]
                nodes = resp.json().get("data", [])
                
                for node in nodes:
                    chapter_name = node.get("resourceName", "未知章节") # e.g. "第01章 Python概述"
                    
                    # 遍历该节点下的附件
                    attachments = node.get("attachmentVOs", [])
                    for att in attachments:
                        res_info = att.get("resource", {})
                        
                        # 提取我们需要的信息
                        resources.append(ScrapedResourceData(
                            resource_id=res_info.get("id"),
                            title=res_info.get("name"), # e.g. "第01章-Python概述.pptx"
                            file_type=res_info.get("ext"),
                            file_size=res_info.get("fileSizeUnit"),
                            download_url=res_info.get("url"),
                            parent_section=chapter_name,
                            upload_time=self._parse_time(res_info.get("createTime"))
                        ))
        except Exception as e:
            print(f"抓取资源失败({site_id}): {e}")
            
        return resources

    def _parse_time(self, time_str) -> datetime:
        if not time_str: return None
        try:
            if "T" in time_str:
                return datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
            return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        except:
            return None

    def run(self) -> List[ScrapedCourseData]:
        """执行全流程抓取"""
        self._login()
        
        final_results = []
        
        # 1. 拿列表
        raw_courses = self._fetch_course_list_raw()
        
        # 2. 遍历每门课，补充详情和资源
        for raw in raw_courses:
            site_id = raw.get("id")
            if not site_id: continue
            
            # 基础信息 (优先用列表里的，不够再去查详情接口)
            # 列表接口里的 teachers 字段已经很全了
            teachers = raw.get("teachers", [])
            teacher_name = teachers[0].get("name") if teachers else raw.get("teacherName", "")
            
            # 3. 抓取资源 (这是最耗时的，如果需要速度可以异步，但现在先同步)
            resources = self._fetch_course_resources(site_id)
            
            course_data = ScrapedCourseData(
                site_id=site_id,
                name=raw.get("siteName"),
                course_code=raw.get("courseCode"),
                term_name=raw.get("termName"),
                teacher_name=teacher_name,
                dept_name=raw.get("departmentName"),
                pic_url=raw.get("picUrl"),
                description=raw.get("briefIntroduction", ""), # 简介
                resources=resources # 把抓到的资源列表挂载上去
            )
            final_results.append(course_data)
            
        return final_results