"""讨论服务"""
from typing import List, Optional
from PyQt6.QtCore import QObject, pyqtSignal

from ..api_client import api_client, APIError
from ..models.discussion import DiscussionTopic


class DiscussionService(QObject):
    """讨论服务类"""

    discussions_loaded = pyqtSignal(list)  # 讨论列表加载成功信号
    discussion_loaded = pyqtSignal(DiscussionTopic)  # 讨论详情加载成功信号
    sync_success = pyqtSignal(str, dict)  # 同步成功信号 (消息, 统计信息)
    load_failed = pyqtSignal(str)  # 加载失败信号
    sync_failed = pyqtSignal(str)  # 同步失败信号

    def __init__(self, parent: Optional[QObject] = None):
        """
        初始化讨论服务

        Args:
            parent: 父对象
        """
        super().__init__(parent)

    def load_course_discussions(self, course_id: int) -> List[DiscussionTopic]:
        """
        加载课程讨论列表

        Args:
            course_id: 课程ID

        Returns:
            讨论列表

        Raises:
            APIError: 加载失败
        """
        discussions_data = api_client.get_course_discussions(course_id)
        discussions = [DiscussionTopic.from_dict(d) for d in discussions_data]
        return discussions

    def load_discussion_detail(self, topic_id: int) -> DiscussionTopic:
        """
        加载讨论详情

        Args:
            topic_id: 讨论主题ID

        Returns:
            讨论主题对象

        Raises:
            APIError: 加载失败
        """
        response = api_client.get_discussion_detail(topic_id)
        # 后端返回格式：{"data": {"topic": {...}, "posts": [...]}}
        data = response.get("data", {})
        topic_data = data.get("topic", {})
        posts = data.get("posts", [])
        
        # 将posts转换为replies格式
        topic_data["replies"] = posts
        return DiscussionTopic.from_dict(topic_data)

    def sync_discussions(
        self, school_username: str = None, school_password: str = None, cas_password: str = None
    ) -> tuple[str, dict]:
        """
        同步讨论

        Args:
            school_username: 学校账号（学号），如果为None则使用已绑定账户
            school_password: 学校密码，如果为None则使用已绑定账户
            cas_password: CAS密码（用于验证已绑定账户）

        Returns:
            (消息, 统计信息)

        Raises:
            APIError: 同步失败
        """
        response = api_client.sync_discussions(school_username, school_password, cas_password)
        msg = response.get("msg", "同步完成")
        stats = response.get("stats", {})
        return (msg, stats)

