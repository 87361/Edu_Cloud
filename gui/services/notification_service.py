"""公告服务"""
from typing import List, Optional
from PyQt6.QtCore import QObject, pyqtSignal

from ..api_client import api_client, APIError
from ..models.notification import Notification


class NotificationService(QObject):
    """公告服务类"""

    notifications_loaded = pyqtSignal(list)  # 公告列表加载成功信号
    sync_success = pyqtSignal(str, dict)  # 同步成功信号 (消息, 统计信息)
    load_failed = pyqtSignal(str)  # 加载失败信号
    sync_failed = pyqtSignal(str)  # 同步失败信号

    def __init__(self, parent: Optional[QObject] = None):
        """
        初始化公告服务

        Args:
            parent: 父对象
        """
        super().__init__(parent)

    def load_notifications(self) -> List[Notification]:
        """
        加载公告列表

        Returns:
            公告列表

        Raises:
            APIError: 加载失败
        """
        notifications_data = api_client.get_notifications()
        notifications = [Notification.from_dict(n) for n in notifications_data]
        return notifications

    def sync_notifications(
        self, school_username: str = None, school_password: str = None, cas_password: str = None
    ) -> tuple[str, dict]:
        """
        同步公告

        Args:
            school_username: 学校账号（学号），如果为None则使用已绑定账户
            school_password: 学校密码，如果为None则使用已绑定账户
            cas_password: CAS密码（用于验证已绑定账户）

        Returns:
            (消息, 统计信息)

        Raises:
            APIError: 同步失败
        """
        response = api_client.sync_notifications(school_username, school_password, cas_password)
        msg = response.get("msg", "同步完成")
        stats = response.get("stats", {})
        return (msg, stats)

