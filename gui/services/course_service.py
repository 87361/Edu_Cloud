"""课程服务"""
from typing import List, Optional
from PyQt6.QtCore import QObject, pyqtSignal

from ..api_client import api_client, APIError
from ..models.course import Course


class CourseService(QObject):
    """课程服务类"""

    courses_loaded = pyqtSignal(list)  # 课程列表加载成功信号
    course_loaded = pyqtSignal(Course)  # 课程详情加载成功信号
    resources_loaded = pyqtSignal(list)  # 资源列表加载成功信号
    sync_success = pyqtSignal(str, dict)  # 同步成功信号 (消息, 统计信息)
    load_failed = pyqtSignal(str)  # 加载失败信号
    sync_failed = pyqtSignal(str)  # 同步失败信号

    def __init__(self, parent: Optional[QObject] = None):
        """
        初始化课程服务

        Args:
            parent: 父对象
        """
        super().__init__(parent)

    def load_courses(self) -> List[Course]:
        """
        加载课程列表

        Returns:
            课程列表

        Raises:
            APIError: 加载失败
        """
        courses_data = api_client.get_courses()
        courses = [Course.from_dict(c) for c in courses_data]
        return courses

    def load_course_detail(self, course_id: int) -> Course:
        """
        加载课程详情

        Args:
            course_id: 课程ID

        Returns:
            课程对象

        Raises:
            APIError: 加载失败
        """
        course_data = api_client.get_course_detail(course_id)
        return Course.from_dict(course_data)

    def load_course_resources(self, course_id: int) -> List[dict]:
        """
        加载课程资源列表

        Args:
            course_id: 课程ID

        Returns:
            资源列表

        Raises:
            APIError: 加载失败
        """
        resources = api_client.get_course_resources(course_id)
        return resources

    def sync_courses(
        self, school_username: str = None, school_password: str = None, cas_password: str = None
    ) -> tuple[str, dict]:
        """
        同步课程

        Args:
            school_username: 学校账号（学号），如果为None则使用已绑定账户
            school_password: 学校密码，如果为None则使用已绑定账户
            cas_password: CAS密码（用于验证已绑定账户）

        Returns:
            (消息, 统计信息)

        Raises:
            APIError: 同步失败
        """
        response = api_client.sync_courses(school_username, school_password, cas_password)
        msg = response.get("msg", "同步完成")
        stats = response.get("stats", {})
        return (msg, stats)

