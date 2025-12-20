"""同步作业对话框"""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from qfluentwidgets import (
    Dialog,
    LineEdit,
    PrimaryPushButton,
    PushButton,
    BodyLabel,
)


class SyncDialog(Dialog):
    """同步对话框（通用，可用于同步课程、作业等）"""

    confirmed = pyqtSignal(str, str)  # 确认信号 (username, password)
    use_bound_account = pyqtSignal()  # 使用已绑定账户信号

    def __init__(self, parent=None, user=None, title="同步", description="请输入学校账号信息以同步"):
        """
        初始化同步对话框

        Args:
            parent: 父窗口
            user: 当前用户对象，用于检查是否已绑定CAS
            title: 对话框标题
            description: 对话框描述文本
        """
        super().__init__(title, description, parent=parent)
        self.user = user
        self._setup_ui()

    def _setup_ui(self) -> None:
        """设置UI"""
        # 输入框容器
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(10)

        # 学号输入
        self.username_edit = LineEdit()
        self.username_edit.setPlaceholderText("请输入学号")
        input_layout.addWidget(self.username_edit)

        # 密码输入
        self.password_edit = LineEdit()
        self.password_edit.setPlaceholderText("请输入密码")
        self.password_edit.setEchoMode(LineEdit.EchoMode.Password)
        input_layout.addWidget(self.password_edit)

        self.vBoxLayout.addWidget(input_widget, 0, Qt.AlignmentFlag.AlignTop)

        # 按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # 如果用户已绑定CAS，添加"使用已绑定账户"选项
        if self.user and self.user.cas_is_bound:
            self.use_bound_button = PushButton("使用已绑定账户")
            self.use_bound_button.clicked.connect(self._on_use_bound_account)
            button_layout.addWidget(self.use_bound_button)

        self.confirm_button = PrimaryPushButton("确认")
        self.confirm_button.clicked.connect(self._on_confirm)
        button_layout.addWidget(self.confirm_button)

        self.cancel_button = PushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.vBoxLayout.addLayout(button_layout, 0)

        # 绑定回车键
        self.username_edit.returnPressed.connect(self.password_edit.setFocus)
        self.password_edit.returnPressed.connect(self._on_confirm)

        # 设置焦点
        self.username_edit.setFocus()

    def _on_confirm(self) -> None:
        """确认按钮点击"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()

        if not username or not password:
            return

        self.confirmed.emit(username, password)
        self.accept()

    def _on_use_bound_account(self) -> None:
        """使用已绑定账户"""
        self.use_bound_account.emit()
        self.accept()

