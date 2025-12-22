"""管理员窗口"""
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget
from qfluentwidgets import FluentWindow, FluentIcon as FIF, MessageBox

from .admin.dashboard_interface import DashboardInterface
from .admin.user_management_interface import UserManagementInterface
from ..services.auth_service import AuthService


class AdminWindow(FluentWindow):
    """管理员窗口"""

    logout_requested = pyqtSignal()  # 登出请求信号

    def __init__(self):
        """初始化管理员窗口"""
        super().__init__()
        self.auth_service = AuthService()
        self._setup_window()
        self._setup_interfaces()
        self._connect_signals()

    def _setup_window(self) -> None:
        """设置窗口"""
        self.setWindowTitle("EduAdmin - 教务管理后台")
        self.resize(1200, 800)
        # 开启 Mica 特效 (Windows 11 有效)
        try:
            self.windowEffect.setMicaEffect(self.winId())
        except Exception:
            pass  # 非Windows系统或版本不支持

    def _setup_interfaces(self) -> None:
        """设置界面"""
        # 仪表盘
        self.dashboard = DashboardInterface(self)
        self.dashboard.setObjectName("dashboard")
        self.addSubInterface(self.dashboard, FIF.HOME, "仪表盘")

        # 学生管理
        self.user_interface = UserManagementInterface(self)
        self.user_interface.setObjectName("user_management")
        self.addSubInterface(self.user_interface, FIF.PEOPLE, "学生管理")

        # 课程管理（占位）
        self.course_page = QWidget()
        self.course_page.setObjectName("course_management")
        self.addSubInterface(self.course_page, FIF.BOOK_SHELF, "课程管理")

        # 分隔线
        self.navigationInterface.addSeparator()

        # 系统设置（占位）
        self.setting_page = QWidget()
        self.setting_page.setObjectName("system_setting")
        self.addSubInterface(self.setting_page, FIF.SETTING, "系统设置")

        # 登出按钮（添加到导航栏底部）
        self.navigationInterface.addSeparator()
        self.logout_page = QWidget()
        self.logout_page.setObjectName("logout")
        # 在登出页面中添加登出按钮
        from qfluentwidgets import VBoxLayout, PrimaryPushButton, BodyLabel
        logout_layout = VBoxLayout(self.logout_page)
        logout_layout.setContentsMargins(30, 30, 30, 30)
        logout_layout.setSpacing(20)
        
        logout_label = BodyLabel("账户管理", self.logout_page)
        logout_layout.addWidget(logout_label)
        
        logout_btn = PrimaryPushButton("登出", self.logout_page)
        logout_btn.clicked.connect(self._on_logout_clicked)
        logout_layout.addWidget(logout_btn)
        logout_layout.addStretch(1)
        
        # 使用addSubInterface添加登出项
        self.addSubInterface(self.logout_page, FIF.CLOSE, "登出")

        # 默认选中第一个
        self.navigationInterface.setCurrentItem(self.dashboard.objectName())

    def _connect_signals(self) -> None:
        """连接信号"""
        self.auth_service.logout_success.connect(self._on_logout_success)
        # 连接用户管理界面的数据刷新信号到仪表盘的刷新方法
        self.user_interface.data_refreshed.connect(self.dashboard.refresh_stats)

    def _on_logout_clicked(self) -> None:
        """登出按钮点击"""
        # 确认对话框
        w = MessageBox(
            "确认登出",
            "确定要退出当前账号吗？",
            self
        )
        if w.exec():
            self.auth_service.logout()

    def _on_logout_success(self) -> None:
        """登出成功"""
        if self.logout_requested:
            self.logout_requested.emit()
        self.close()

