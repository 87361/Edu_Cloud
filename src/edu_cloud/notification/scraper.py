import time
from datetime import datetime
from typing import List, Dict
from buptmw import BUPT_Auth
from .models import ScrapedNotificationData

API_BASE = "https://apiucloud.bupt.edu.cn/ykt-basics/api"

class NotificationScraper:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = None
        self.user_id = None

    def _login(self):
        """复用认证逻辑"""
        print(f"--- [Scraper] 正在登录 CAS: {self.username} ---")
        try:
            auth = BUPT_Auth(cas={"username": self.username, "password": self.password})
            self.session = auth.get_Ucloud()
            
            self.user_id = self.session.cookies.get("iClass-uuid") or \
                           self.session.cookies.get("userId") or \
                           getattr(self.session, "user_id", None)
            
            token = getattr(self.session, "access_token", "未找到")
            print(f"✅ 登录成功!")
            print(f"   - 获取到的 UserID: {self.user_id}")
            print(f"   - 获取到的 Token: {str(token)[:10]}...")
            
            if not self.user_id:
                raise ValueError("登录成功但 UserID 为空")
                
        except Exception as e:
            raise RuntimeError(f"认证失败: {str(e)}")

    def _get_headers(self) -> Dict:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        token = getattr(self.session, "access_token", None)
        if token:
            headers["Blade-Auth"] = f"bearer {token}"
        return headers

    def _parse_time(self, time_str) -> datetime:
        if not time_str: return None
        try:
            if len(time_str) <= 16: time_str += ":00"
            return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        except:
            return None

    def run(self) -> List[ScrapedNotificationData]:
        """抓取公告列表（自动翻页版 - 修正参数传递）"""
        self._login()
        if not self.user_id: return []

        url = f"{API_BASE}/inform/news/list"
        all_results = []
        current_page = 1
        
        print(f"--- [Scraper] 开始全量抓取公告 ---")

        while True:
            # 【核心修改点】
            # 策略：把参数同时塞给 params (URL参数) 和 json (Body参数)
            # 这样无论服务器读哪里，都能读到页码
            req_data = {
                "newsCopyPersonId": self.user_id,
                "current": current_page,
                "size": 10  # 保持 10 条，稳扎稳打
            }
            
            try:
                print(f"   -> 正在请求第 {current_page} 页...")
                
                # 注意这里：params=req_data 把参数放URL里，json=req_data 把参数放Body里
                resp = self.session.post(url, params=req_data, json=req_data, headers=self._get_headers())
                
                if resp.status_code != 200:
                    print(f"❌ 第 {current_page} 页请求失败: {resp.status_code}")
                    break
                
                data = resp.json()
                records = data.get("data", {}).get("records", [])
                total_server = data.get("data", {}).get("total", 0)
                
                # 去重校验：如果这一页的第一条数据的ID，和我们已经抓到的最后一条ID一样
                # 说明翻页失败了，服务器一直在返回同一页
                if records and all_results and records[0].get("id") == all_results[-1].id:
                    print("⚠️ 警告：检测到重复数据，服务器可能忽略了翻页参数。停止抓取。")
                    break

                if not records:
                    print("✅ 数据为空，停止翻页。")
                    break
                
                # 解析当前页数据
                page_added_count = 0
                for item in records:
                    # 再次做一个内存级去重，防止列表里堆积重复数据
                    n_id = str(item.get("id"))
                    if any(x.id == n_id for x in all_results):
                        continue

                    all_results.append(ScrapedNotificationData(
                        id=n_id,
                        title=item.get("newsTitle"),
                        content=item.get("newsInfo"),
                        msg_type=item.get("type"),
                        is_read=bool(item.get("isRead", 0)),
                        publish_time=self._parse_time(item.get("createTime") or item.get("newsCopyTime"))
                    ))
                    page_added_count += 1
                
                print(f"      本页解析 {len(records)} 条，有效新增 {page_added_count} 条。当前累计: {len(all_results)}/{total_server}")

                # 判断是否抓够了
                if len(all_results) >= total_server or len(records) < 10:
                    print("✅ 所有页面抓取完毕！")
                    break
                
                current_page += 1
                time.sleep(0.2) 
                
            except Exception as e:
                print(f"❌ 抓取中断: {e}")
                break
            
        return all_results