"""登录窗口 - 修复版"""
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtGui import QColor, QMouseEvent

from qfluentwidgets import (
    IconWidget,
    TitleLabel,
    SubtitleLabel,
    LineEdit,
    CheckBox,
    PrimaryPushButton,
    PushButton,
    HyperlinkButton,
    InfoBar,
    FluentIcon as FIF,
    MessageBoxBase,
    BodyLabel,
)

from ..services.auth_service import AuthService
# 如果有异步服务，确保导入路径正确，或者暂时注释掉相关逻辑
from ..services.async_service import AsyncService 
from ..api_client import api_client, APIError

class LoginWindow(QWidget):
    """登录窗口"""

    login_success = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.auth_service = AuthService()
        self.auth_service.login_success.connect(self._on_login_success)
        self.auth_service.login_failed.connect(self._on_login_failed)
        
        # 异步服务
        self.async_service = AsyncService()

        # 拖动窗口所需的变量
        self._is_dragging = False
        self._drag_position = QPoint()

        self._setup_ui()

    def _setup_ui(self) -> None:
        """设置UI"""
        self.setWindowTitle("登录 - 云邮Mini")
        self.resize(1000, 600)
        
        # 关键设置：无边框 + 背景透明
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # === 主布局 (用于容纳阴影) ===
        # 我们需要给主窗口留出边距(Margins)，以便阴影能显示出来，否则会被切掉
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20) 

        # === 中心容器 ===
        # 所有的可见内容都放在这个 container 里
        self.container = QFrame(self)
        self.container.setObjectName("Container")
        self.container.setStyleSheet("""
            QFrame#Container {
                background-color: transparent;
                border-radius: 10px;
            }
        """)
        
        # 给容器添加阴影，而不是给右边面板添加
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setColor(QColor(0, 0, 0, 100)) # 稍微加深一点阴影
        self.shadow.setOffset(0, 0)
        self.container.setGraphicsEffect(self.shadow)
        
        self.main_layout.addWidget(self.container)

        # === 内容布局 ===
        container_layout = QHBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # --- 左侧：装饰面板 ---
        self.left_panel = QFrame()
        self.left_panel.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-top-left-radius: 10px;
                border-bottom-left-radius: 10px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
            }
        """)
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo = IconWidget(FIF.EDUCATION, self.left_panel)
        logo.setFixedSize(100, 100)
        
        # 标题样式微调
        welcome_lbl = TitleLabel("云邮Mini", self.left_panel)
        welcome_lbl.setStyleSheet("QLabel { color: white; font-family: 'Microsoft YaHei UI'; font-weight: bold; }")

        left_layout.addWidget(logo)
        left_layout.addSpacing(20)
        left_layout.addWidget(welcome_lbl)

        # --- 右侧：表单面板 ---
        self.right_panel = QFrame()
        self.right_panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
            }
        """)

        # 关闭按钮 (手动绝对定位)
        self.close_btn = PushButton("×", self.right_panel)
        self.close_btn.setFixedSize(32, 32)
        # 简单的红色悬停样式
        self.close_btn.setStyleSheet("""
            QPushButton { border: none; background: transparent; font-size: 16px; border-radius: 5px; }
            QPushButton:hover { background-color: #e81123; color: white; }
        """)
        self.close_btn.clicked.connect(self.close)
        # 注意：因为有了 margins，这里的 move 坐标是相对于 right_panel 的
        # right_panel 大约占窗口一半，所以位置需要调整，建议用布局或者固定右上角
        # 这里为了简单，我们把它放到布局里，或者手动调整位置
        self.close_btn.setParent(self.right_panel)
        self.close_btn.move(440, 10) # 假设右面板宽约500，稍微靠右

        self.form_layout = QVBoxLayout(self.right_panel)
        self.form_layout.setContentsMargins(60, 60, 60, 60)
        self.form_layout.setSpacing(15)

        # 表单内容
        self.title = SubtitleLabel("欢迎回来", self.right_panel)
        self.title.setStyleSheet("color: #333; font-weight: bold;")

        self.login_mode_label = SubtitleLabel("登录方式", self.right_panel)
        self.login_mode_label.setStyleSheet("color: #666; font-size: 14px;")

        # 单选按钮组
        from PyQt6.QtWidgets import QButtonGroup, QRadioButton
        self.mode_group = QButtonGroup(self.right_panel)
        self.local_radio = QRadioButton("本地账号", self.right_panel)
        self.cas_radio = QRadioButton("CAS登录", self.right_panel)
        self.local_radio.setChecked(True)
        self.mode_group.addButton(self.local_radio, 0)
        self.mode_group.addButton(self.cas_radio, 1)

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(self.local_radio)
        mode_layout.addWidget(self.cas_radio)
        mode_layout.addStretch()

        self.user_input = LineEdit(self.right_panel)
        self.user_input.setPlaceholderText("用户名 / 学号")
        self.user_input.setClearButtonEnabled(True)

        self.pwd_input = LineEdit(self.right_panel)
        self.pwd_input.setPlaceholderText("密码")
        self.pwd_input.setEchoMode(LineEdit.EchoMode.Password)
        self.pwd_input.setClearButtonEnabled(True)

        opt_layout = QHBoxLayout()
        self.remember_cb = CheckBox("记住我", self.right_panel)
        self.forget_btn = HyperlinkButton("http://localhost", "忘记密码?", self.right_panel)
        opt_layout.addWidget(self.remember_cb)
        opt_layout.addStretch(1)
        opt_layout.addWidget(self.forget_btn)

        self.login_btn = PrimaryPushButton("登录", self.right_panel)
        self.login_btn.setFixedHeight(40)
        self.login_btn.clicked.connect(self._on_login)

        self.switch_btn = HyperlinkButton("#", "没有账号？点击注册", self.right_panel)
        self.switch_btn.clicked.connect(self._show_register_dialog)

        # 组装表单
        self.form_layout.addStretch(1)
        self.form_layout.addWidget(self.title)
        self.form_layout.addSpacing(20)
        self.form_layout.addWidget(self.login_mode_label)
        self.form_layout.addLayout(mode_layout)
        self.form_layout.addSpacing(10)
        self.form_layout.addWidget(self.user_input)
        self.form_layout.addWidget(self.pwd_input)
        self.form_layout.addLayout(opt_layout)
        self.form_layout.addSpacing(20)
        self.form_layout.addWidget(self.login_btn)
        self.form_layout.addWidget(self.switch_btn)
        self.form_layout.addStretch(1)

        # 左右面板加入容器
        container_layout.addWidget(self.left_panel, 1)
        container_layout.addWidget(self.right_panel, 1)

        # 绑定回车键
        self.user_input.returnPressed.connect(self.pwd_input.setFocus)
        self.pwd_input.returnPressed.connect(self._on_login)

    # === 关键：实现拖动逻辑 ===
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下时记录位置"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            # 记录鼠标相对于窗口左上角的偏移量
            # PyQt6 使用 globalPosition().toPoint()
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动时移动窗口"""
        if self._is_dragging and event.buttons() & Qt.MouseButton.LeftButton:
            # 新的窗口位置 = 当前鼠标全局位置 - 偏移量
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放时停止拖动"""
        self._is_dragging = False

    def _on_login(self) -> None:
        """登录逻辑"""
        user = self.user_input.text()
        pwd = self.pwd_input.text()

        if not user or not pwd:
            InfoBar.error("错误", "请输入用户名和密码", duration=2000, parent=self.right_panel)
            return

        self.login_btn.setEnabled(False)
        self.login_btn.setText("登录中...")
        is_cas = self.cas_radio.isChecked()

        # 定义异步任务
        def login_func():
            return self.auth_service.login(user, pwd, is_cas)

        # 执行异步任务
        self.async_service.execute_async(
            login_func, self._on_login_success, self._on_login_failed
        )

    def _on_login_success(self, user=None) -> None:
        """登录成功"""
        InfoBar.success("登录成功", "正在进入系统...", duration=1000, parent=self.right_panel)
        # 延迟一下发送信号，让用户看到提示
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(500, self.login_success.emit)

    def _on_login_failed(self, error_msg: str) -> None:
        """登录失败"""
        self.login_btn.setEnabled(True)
        self.login_btn.setText("登录")
        InfoBar.error("登录失败", str(error_msg), duration=2000, parent=self.right_panel)

    def _show_register_dialog(self) -> None:
        """显示注册对话框"""
        dialog = RegisterDialog(self)
        if dialog.exec():
            # 注册成功，自动填充用户名并切换到登录模式
            username = dialog.get_username()
            if username:
                self.user_input.setText(username)
                self.local_radio.setChecked(True)
                self.pwd_input.setFocus()


class RegisterDialog(MessageBoxBase):
    """注册对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._username = ""
        self._setup_ui()
        self.widget.setMinimumWidth(400)
        self.yesButton.setText("注册")
        self.cancelButton.setText("取消")
    
    def _setup_ui(self):
        """设置UI"""
        # 标题
        title_label = SubtitleLabel("注册新账号", self.widget)
        
        # 输入框
        self.username_edit = LineEdit(self.widget)
        self.username_edit.setPlaceholderText("请输入用户名")
        self.username_edit.setClearButtonEnabled(True)
        
        self.email_edit = LineEdit(self.widget)
        self.email_edit.setPlaceholderText("请输入邮箱（可选）")
        self.email_edit.setClearButtonEnabled(True)
        
        self.full_name_edit = LineEdit(self.widget)
        self.full_name_edit.setPlaceholderText("请输入全名（可选）")
        self.full_name_edit.setClearButtonEnabled(True)
        
        self.password_edit = LineEdit(self.widget)
        self.password_edit.setPlaceholderText("请输入密码（至少6位）")
        self.password_edit.setEchoMode(LineEdit.EchoMode.Password)
        self.password_edit.setClearButtonEnabled(True)
        
        self.password_confirm_edit = LineEdit(self.widget)
        self.password_confirm_edit.setPlaceholderText("请再次输入密码")
        self.password_confirm_edit.setEchoMode(LineEdit.EchoMode.Password)
        self.password_confirm_edit.setClearButtonEnabled(True)
        
        # 管理员选项
        self.admin_checkbox = CheckBox("注册为管理员", self.widget)
        self.admin_checkbox.setToolTip("勾选此项将创建管理员账号，拥有系统管理权限")
        
        # 状态标签
        self.status_label = BodyLabel("", self.widget)
        self.status_label.setStyleSheet("color: red;")
        
        # 组装布局
        self.viewLayout.addWidget(title_label)
        self.viewLayout.addSpacing(15)
        self.viewLayout.addWidget(self.username_edit)
        self.viewLayout.addWidget(self.email_edit)
        self.viewLayout.addWidget(self.full_name_edit)
        self.viewLayout.addWidget(self.password_edit)
        self.viewLayout.addWidget(self.password_confirm_edit)
        self.viewLayout.addSpacing(10)
        self.viewLayout.addWidget(self.admin_checkbox)
        self.viewLayout.addWidget(self.status_label)
        self.viewLayout.addSpacing(10)
        
        # 绑定信号
        self.yesButton.clicked.connect(self._on_register)
        self.username_edit.returnPressed.connect(self.email_edit.setFocus)
        self.email_edit.returnPressed.connect(self.full_name_edit.setFocus)
        self.full_name_edit.returnPressed.connect(self.password_edit.setFocus)
        self.password_edit.returnPressed.connect(self.password_confirm_edit.setFocus)
        self.password_confirm_edit.returnPressed.connect(self._on_register)
        
        # 自动聚焦
        self.username_edit.setFocus()
    
    def _on_register(self):
        """处理注册逻辑"""
        username = self.username_edit.text().strip()
        email = self.email_edit.text().strip()
        full_name = self.full_name_edit.text().strip()
        password = self.password_edit.text()
        password_confirm = self.password_confirm_edit.text()
        is_admin = self.admin_checkbox.isChecked()
        
        # 验证输入
        if not username:
            self.status_label.setText("请输入用户名")
            self.username_edit.setFocus()
            return
        
        if not password:
            self.status_label.setText("请输入密码")
            self.password_edit.setFocus()
            return
        
        if len(password) < 6:
            self.status_label.setText("密码长度至少为6位")
            self.password_edit.setFocus()
            return
        
        if password != password_confirm:
            self.status_label.setText("两次输入的密码不一致")
            self.password_confirm_edit.setFocus()
            return
        
        # 禁用按钮
        self.yesButton.setEnabled(False)
        self.yesButton.setText("注册中...")
        self.status_label.setText("")
        
        # 在后台线程中执行注册
        def do_register():
            try:
                role = "admin" if is_admin else "user"
                response = api_client.register(
                    username=username,
                    password=password,
                    email=email if email else None,
                    full_name=full_name if full_name else None,
                    role=role
                )
                # 注册成功，在主线程中更新UI
                self._username = username
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(0, lambda: self.accept())
            except APIError as e:
                error_msg = e.message
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(0, lambda msg=error_msg: self._on_register_error(msg))
            except Exception as e:
                error_msg = str(e)
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(0, lambda msg=error_msg: self._on_register_error(msg))
        
        from PyQt6.QtCore import QThread
        import threading
        thread = threading.Thread(target=do_register, daemon=True)
        thread.start()
    
    def _on_register_error(self, error_msg: str):
        """注册失败"""
        self.status_label.setText(f"注册失败: {error_msg}")
        self.yesButton.setEnabled(True)
        self.yesButton.setText("注册")
    
    def get_username(self) -> str:
        """获取注册的用户名"""
        return self._username