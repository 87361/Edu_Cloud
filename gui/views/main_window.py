"""主窗口"""
from PyQt6.QtCore import pyqtSignal
from qfluentwidgets import FluentWindow, FluentIcon as FIF

from .assignment_list_interface import AssignmentListInterface
from .schedule_interface import ScheduleInterface
from .setting_interface import SettingInterface
from ..services.auth_service import AuthService


class MainWindow(FluentWindow):
    """主窗口"""

    logout_requested = pyqtSignal()  # 登出请求信号

    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        self.auth_service = AuthService()
        self._setup_window()
        self._setup_interfaces()
        self._connect_signals()

    def _setup_window(self) -> None:
        """设置窗口"""
        self.setWindowTitle("云邮教学空间")
        self.resize(1200, 800)
        # 开启 Mica 特效 (Windows 11 有效)
        try:
            self.windowEffect.setMicaEffect(self.winId())
        except Exception:
            pass  # 非Windows系统或版本不支持

    def _setup_interfaces(self) -> None:
        """设置界面"""
        # 我的课业界面（包含作业列表和课程墙）
        self.assignment_list = AssignmentListInterface(self)
        self.assignment_list.setObjectName("assignment_list")
        self.addSubInterface(self.assignment_list, FIF.EDUCATION, "我的课业")

        # 日程表界面
        self.schedule_interface = ScheduleInterface(self)
        self.schedule_interface.setObjectName("schedule")
        self.addSubInterface(self.schedule_interface, FIF.CALENDAR, "日程表")

        # 分隔线
        self.navigationInterface.addSeparator()

        # 设置界面
        self.setting_interface = SettingInterface(self)
        self.setting_interface.setObjectName("setting")
        self.addSubInterface(self.setting_interface, FIF.SETTING, "设置")

        # 默认选中第一个
        self.navigationInterface.setCurrentItem(
            self.assignment_list.objectName()
        )

    def _connect_signals(self) -> None:
        """连接信号"""
        self.assignment_list.logout_requested.connect(self._on_logout)
        self.setting_interface.logout_requested.connect(self._on_logout)

        # 加载用户信息
        self.auth_service.user_info_loaded.connect(
            self.assignment_list.update_user_info
        )
        self.auth_service.logout_success.connect(self._on_logout_success)
        self.auth_service.load_user_info()

    def _on_logout(self) -> None:
        """登出"""
        self.auth_service.logout()

    def _on_logout_success(self) -> None:
        """登出成功"""
        if self.logout_requested:
            self.logout_requested.emit()
        self.close()

