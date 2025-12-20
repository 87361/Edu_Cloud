# 爬虫逻辑(fetch_topics, fetch_posts)
import time
from datetime import datetime
from typing import List, Dict
from buptmw import BUPT_Auth
from .models import ScrapedTopicData, ScrapedPostData

API_BASE = "https://apiucloud.bupt.edu.cn"

class DiscussionScraper:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = None
        self.user_id = None

    def _login(self):
        """复用认证逻辑"""
        try:
            auth = BUPT_Auth(cas={"username": self.username, "password": self.password})
            self.session = auth.get_Ucloud()
            self.user_id = self.session.cookies.get("iClass-uuid") or \
                           self.session.cookies.get("userId") or \
                           getattr(self.session, "user_id", None)
            if not self.user_id:
                raise ValueError("UserID 缺失")
        except Exception as e:
            raise RuntimeError(f"认证失败: {str(e)}")

    def _get_headers(self) -> Dict:
        headers = {"Content-Type": "application/json"}
        token = getattr(self.session, "access_token", None)
        if token:
            headers["Blade-Auth"] = f"bearer {token}"
        return headers

    def _parse_time(self, time_str) -> datetime:
        if not time_str: return None
        try:
            return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        except:
            return None

    def _fetch_course_list(self) -> List[str]:
        """获取所有课程 ID"""
        url = f"{API_BASE}/ykt-site/site/list/student/current"
        params = {"userId": self.user_id, "current": 1, "size": 50, "siteRoleCode": 2}
        site_ids = []
        try:
            resp = self.session.get(url, params=params, headers=self._get_headers())
            if resp.status_code == 200:
                for c in resp.json().get("data", {}).get("records", []):
                    if c.get("id"): site_ids.append(c.get("id"))
        except: pass
        return site_ids

    def _fetch_posts(self, topic_id) -> List[ScrapedPostData]:
        """3. 获取讨论回复列表 (对应接口3)"""
        url = f"{API_BASE}/ykt-activity/forum/list/topic-post"
        # 你的截图显示是用 GET，参数在 Query
        params = {"tid": topic_id, "userId": self.user_id, "current": 1, "size": 10}
        
        posts = []
        try:
            resp = self.session.get(url, params=params, headers=self._get_headers())
            if resp.status_code == 200:
                records = resp.json().get("data", {}).get("records", [])
                for item in records:
                    posts.append(ScrapedPostData(
                        id=item.get("id"),
                        author_name=item.get("userName"),
                        content=item.get("body", ""),
                        floor=item.get("floor", 1),
                        created_at=self._parse_time(item.get("createTime"))
                    ))
        except: pass
        return posts

    def _fetch_topics(self, site_id) -> List[ScrapedTopicData]:
        """1. 获取某门课的讨论列表 (对应接口1)"""
        url = f"{API_BASE}/ykt-activity/forum/page"
        params = {"siteId": site_id, "userId": self.user_id, "current": 1, "size": 5, "roleType": 1}
        
        topics = []
        try:
            resp = self.session.get(url, params=params, headers=self._get_headers())
            if resp.status_code == 200:
                records = resp.json().get("data", {}).get("records", [])
                for item in records:
                    t_id = item.get("id")
                    
                    # 顺便抓取回复
                    posts = self._fetch_posts(t_id)
                    
                    topics.append(ScrapedTopicData(
                        id=t_id,
                        course_id=site_id,
                        title=item.get("title"),
                        author_name=item.get("userName"),
                        content=item.get("body", ""),
                        view_count=item.get("viewNum", 0),
                        reply_count=item.get("replyNum", 0),
                        like_count=item.get("likeNum", 0),
                        created_at=self._parse_time(item.get("createTime")),
                        posts=posts
                    ))
        except Exception as e:
            print(f"抓取讨论区失败({site_id}): {e}")
            
        return topics

    def run(self) -> List[ScrapedTopicData]:
        """执行全流程"""
        self._login()
        
        all_topics = []
        # 1. 拿所有课程 ID
        course_ids = self._fetch_course_list()
        
        # 2. 遍历每门课查讨论区
        for cid in course_ids:
            course_topics = self._fetch_topics(cid)
            all_topics.extend(course_topics)
            
        return all_topics