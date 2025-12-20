"""作业服务"""
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal

from ..api_client import api_client, APIError
from ..models.assignment import Assignment


class AssignmentService(QObject):
    """作业服务类"""

    assignments_loaded = pyqtSignal(list)  # 作业列表加载成功
    assignment_loaded = pyqtSignal(Assignment)  # 作业详情加载成功
    load_failed = pyqtSignal(str)  # 加载失败
    sync_success = pyqtSignal(str, int, int)  # 同步成功 (消息, 新增数, 总数)
    sync_failed = pyqtSignal(str)  # 同步失败
    submit_success = pyqtSignal()  # 提交成功
    submit_failed = pyqtSignal(str)  # 提交失败

    def __init__(self, parent: Optional[QObject] = None):
        """
        初始化作业服务

        Args:
            parent: 父对象
        """
        super().__init__(parent)

    def load_assignments(self) -> list[Assignment]:
        """
        加载作业列表

        Returns:
            作业列表
        """
        assignments_data = api_client.get_assignments()
        return [Assignment.from_dict(data) for data in assignments_data]

    def load_assignment(self, assignment_id: int) -> Assignment:
        """
        加载作业详情

        Args:
            assignment_id: 作业ID

        Returns:
            作业对象

        Raises:
            ValueError: 作业不存在
        """
        assignments_data = api_client.get_assignments()
        assignment_data = next(
            (a for a in assignments_data if a.get("id") == assignment_id), None
        )

        if not assignment_data:
            raise ValueError("作业不存在")

        return Assignment.from_dict(assignment_data)

    def sync_assignments(
        self, school_username: str = None, school_password: str = None, cas_password: str = None
    ) -> tuple[str, int, int]:
        """
        同步作业

        Args:
            school_username: 学校账号（学号），如果为None则使用已绑定账户
            school_password: 学校密码，如果为None则使用已绑定账户
            cas_password: CAS密码（用于验证已绑定账户）

        Returns:
            (消息, 新增数, 总数)
        """
        response = api_client.sync_assignments(school_username, school_password, cas_password)
        msg = response.get("msg", "同步完成")
        stats = response.get("stats", {})
        new_count = stats.get("new_added", 0)
        total = stats.get("total_fetched", 0)
        return (msg, new_count, total)

    def submit_assignment(self, assignment_id: int, file_path: str) -> None:
        """
        提交作业

        Args:
            assignment_id: 作业ID
            file_path: 文件路径

        Raises:
            APIError: API调用失败
        """
        try:
            api_client.submit_assignment(assignment_id, file_path)
            self.submit_success.emit()
        except APIError as e:
            self.submit_failed.emit(e.message)
            raise
        except Exception as e:
            self.submit_failed.emit(str(e))
            raise

