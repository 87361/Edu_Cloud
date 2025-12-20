"""作业列表界面"""
from typing import Optional
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QButtonGroup,
)
from PyQt6.QtGui import QColor

from qfluentwidgets import (
    ScrollArea,
    SubtitleLabel,
    BodyLabel,
    CaptionLabel,
    PrimaryPushButton,
    PushButton,
    ElevatedCardWidget,
    RadioButton,
    FluentIcon as FIF,
    InfoBar,
)

from ..models.assignment import Assignment
from ..models.course import Course
from ..services.assignment_service import AssignmentService
from ..services.async_service import AsyncService
from ..services.auth_service import AuthService
from .components.sync_dialog import SyncDialog
from .assignment_detail_interface import AssignmentDetailInterface
from .course_wall_interface import CourseWallInterface
from .course_detail_interface import CourseDetailInterface


class AssignmentListInterface(QWidget):
    """作业列表界面（类似WorkspaceInterface）"""

    logout_requested = pyqtSignal()  # 登出请求信号

    def __init__(self, parent=None):
        """
        初始化作业列表界面

        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.assignment_service = AssignmentService()
        self.async_service = AsyncService()
        self.auth_service = AuthService()
        self._assignments: list[Assignment] = []
        self._filter_status: Optional[str] = None
        self._setup_ui()
        self._connect_signals()
        self._load_assignments()

    def _setup_ui(self) -> None:
        """设置UI"""
        # 主布局：水平分割
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- 左侧栏：作业列表 ---
        self.left_panel = QWidget()
        self.left_panel.setFixedWidth(280)
        self.left_panel.setStyleSheet(
            "background-color: transparent; "
            "border-right: 1px solid rgba(255, 255, 255, 0.1);"
        )
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(10, 20, 10, 20)

        # 顶部工具栏
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(10)

        self.sync_button = PrimaryPushButton("同步", self.left_panel)
        self.sync_button.clicked.connect(self._on_sync_click)
        toolbar_layout.addWidget(self.sync_button)

        self.refresh_button = PushButton("刷新", self.left_panel)
        self.refresh_button.clicked.connect(self._load_assignments)
        toolbar_layout.addWidget(self.refresh_button)

        left_layout.addLayout(toolbar_layout)
        left_layout.addSpacing(10)

        self.left_title = SubtitleLabel("待办作业", self.left_panel)
        left_layout.addWidget(self.left_title)
        left_layout.addSpacing(10)

        # 作业列表滚动区
        self.task_scroll = ScrollArea(self.left_panel)
        self.task_scroll.setStyleSheet("background: transparent; border: none;")
        self.task_container = QWidget()
        self.task_v_layout = QVBoxLayout(self.task_container)
        self.task_v_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.task_v_layout.setSpacing(10)
        self.task_scroll.setWidget(self.task_container)
        self.task_scroll.setWidgetResizable(True)
        left_layout.addWidget(self.task_scroll)

        # --- 右侧栏：使用 StackedWidget 切换 课程墙/课程详情/作业详情 ---
        self.right_stack = QStackedWidget()

        # 页面 0: 课程墙（默认显示）
        self.course_wall = CourseWallInterface()
        self.course_wall.course_clicked.connect(self._show_course_detail)

        # 页面 1: 课程详情
        self.course_detail = CourseDetailInterface()
        self.course_detail.back_signal.connect(self._show_course_wall)

        # 页面 2: 作业详情
        self.assignment_detail = AssignmentDetailInterface()
        self.assignment_detail.back_signal.connect(self._show_course_wall)

        self.right_stack.addWidget(self.course_wall)
        self.right_stack.addWidget(self.course_detail)
        self.right_stack.addWidget(self.assignment_detail)

        layout.addWidget(self.left_panel)
        layout.addWidget(self.right_stack, 1)

    def _connect_signals(self) -> None:
        """连接信号"""
        self.assignment_service.assignments_loaded.connect(
            self._on_assignments_loaded
        )
        self.assignment_service.load_failed.connect(self._on_load_failed)
        self.assignment_service.sync_success.connect(self._on_sync_success)
        self.assignment_service.sync_failed.connect(self._on_sync_failed)

    def _load_assignments(self) -> None:
        """加载作业列表"""
        def load_func():
            try:
                return self.assignment_service.load_assignments()
            except Exception as e:
                self.assignment_service.load_failed.emit(str(e))
                raise

        self.async_service.execute_async(
            load_func, self._on_assignments_loaded, self._on_load_failed
        )

    def _on_assignments_loaded(self, assignments: list[Assignment]) -> None:
        """作业列表加载成功"""
        self._assignments = assignments
        self._update_assignment_list()

    def _on_load_failed(self, error_msg: str) -> None:
        """加载失败"""
        InfoBar.error("错误", error_msg, duration=2000, parent=self)

    def _update_assignment_list(self) -> None:
        """更新作业列表显示"""
        # 清除现有组件
        for i in reversed(range(self.task_v_layout.count())):
            item = self.task_v_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()

        # 过滤掉已提交的作业和无效的课程名称（未分类、待办事项、未知课程等）
        pending_assignments = [
            a for a in self._assignments 
            if not a.is_submitted() 
            and a.course_name 
            and "未分类" not in a.course_name 
            and "待办事项" not in a.course_name
            and a.course_name != "未知课程"
        ]

        if not pending_assignments:
            empty_label = BodyLabel("暂无待办作业", self.task_container)
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.task_v_layout.addWidget(empty_label)
            return

        # 显示作业列表（使用 ElevatedCardWidget）
        for assignment in pending_assignments:
            item_card = ElevatedCardWidget(self.task_container)
            item_card.setFixedHeight(70)
            item_card.setCursor(Qt.CursorShape.PointingHandCursor)

            # 列表项布局
            card_layout = QVBoxLayout(item_card)
            card_layout.setContentsMargins(15, 10, 15, 10)

            title_lbl = BodyLabel(assignment.title, item_card)
            info_text = f"{assignment.course_name} | {assignment.get_deadline_display()}"
            info_lbl = CaptionLabel(info_text, item_card)
            info_lbl.setTextColor(QColor(150, 150, 150), QColor(150, 150, 150))

            card_layout.addWidget(title_lbl)
            card_layout.addWidget(info_lbl)

            # 点击事件绑定（使用闭包处理循环变量）
            def make_click_handler(a: Assignment):
                return lambda event: self._show_detail(a)

            item_card.mousePressEvent = make_click_handler(assignment)

            self.task_v_layout.addWidget(item_card)

    def _show_detail(self, assignment: Assignment) -> None:
        """
        显示作业详情

        Args:
            assignment: 作业对象
        """
        # 先显示基础信息（从列表获取的）
        self.assignment_detail.update_data(assignment)
        # 切换堆叠页面到作业详情
        self.right_stack.setCurrentIndex(2)
        # 然后异步加载完整的详情（包括description）
        self.assignment_detail.load_assignment(assignment.id)

    def _show_course_wall(self) -> None:
        """显示课程墙"""
        self.right_stack.setCurrentIndex(0)

    def _show_course_detail(self, course: Course) -> None:
        """
        显示课程详情

        Args:
            course: 课程对象
        """
        self.course_detail.update_data(course)
        # 切换堆叠页面到课程详情
        self.right_stack.setCurrentIndex(1)


    def _on_sync_click(self) -> None:
        """同步按钮点击"""
        # 获取当前用户信息
        user = self.auth_service.get_current_user()
        dialog = SyncDialog(self, user=user)
        dialog.confirmed.connect(self._on_sync_confirm)
        dialog.use_bound_account.connect(self._on_use_bound_account)
        if dialog.exec() == dialog.DialogCode.Accepted:
            pass  # 对话框已关闭

    def _on_use_bound_account(self) -> None:
        """使用已绑定账户"""
        user = self.auth_service.get_current_user()
        if not user or not user.cas_is_bound:
            InfoBar.error("错误", "未绑定CAS账户", duration=2000, parent=self)
            return
        
        # 弹出密码输入框
        from qfluentwidgets import Dialog, LineEdit, PrimaryPushButton, PushButton
        password_dialog = Dialog("验证身份", f"请输入CAS密码以验证身份（学号：{user.cas_username}）", self)
        password_input = LineEdit()
        password_input.setPlaceholderText("请输入CAS密码")
        password_input.setEchoMode(LineEdit.EchoMode.Password)
        password_input.setMinimumWidth(300)
        password_dialog.vBoxLayout.addWidget(password_input)
        
        def on_confirm():
            password = password_input.text().strip()
            if not password:
                return
            password_dialog.accept()
            self._sync_with_bound_account(password)
        
        confirm_btn = PrimaryPushButton("确认")
        confirm_btn.clicked.connect(on_confirm)
        cancel_btn = PushButton("取消")
        cancel_btn.clicked.connect(password_dialog.reject)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(confirm_btn)
        button_layout.addWidget(cancel_btn)
        password_dialog.vBoxLayout.addLayout(button_layout)
        
        password_input.returnPressed.connect(on_confirm)
        password_input.setFocus()
        
        if password_dialog.exec() == password_dialog.DialogCode.Accepted:
            pass

    def _sync_with_bound_account(self, cas_password: str) -> None:
        """使用已绑定账户同步"""
        # 显示加载提示
        InfoBar.info("提示", "正在同步课程和作业，请稍候...", duration=3000, parent=self)
        
        def sync_func():
            try:
                return self.assignment_service.sync_all(
                    cas_password=cas_password
                )
            except Exception as e:
                self.assignment_service.load_failed.emit(str(e))
                raise

        def on_success(result: tuple[str, dict]):
            msg, stats = result
            # 从统计信息中提取作业数量用于显示
            assignment_stats = stats.get("assignments", {})
            new_count = assignment_stats.get("new_added", 0)
            total = assignment_stats.get("total_fetched", 0)
            self._on_sync_success(msg, new_count, total)
            # 注意：课程墙的刷新已经在 _on_sync_success 中处理了

        self.async_service.execute_async(
            sync_func, on_success, self._on_sync_failed
        )

    def _on_sync_confirm(self, username: str, password: str) -> None:
        """确认同步"""
        # 显示加载提示
        InfoBar.info("提示", "正在同步课程和作业，请稍候...", duration=3000, parent=self)
        
        def sync_func():
            try:
                return self.assignment_service.sync_all(
                    username, password
                )
            except Exception as e:
                self.assignment_service.load_failed.emit(str(e))
                raise

        def on_success(result: tuple[str, dict]):
            msg, stats = result
            # 从统计信息中提取作业数量用于显示
            assignment_stats = stats.get("assignments", {})
            new_count = assignment_stats.get("new_added", 0)
            total = assignment_stats.get("total_fetched", 0)
            self._on_sync_success(msg, new_count, total)

        self.async_service.execute_async(
            sync_func, on_success, self._on_sync_failed
        )

    def _on_sync_success(self, msg: str, new_count: int, total: int) -> None:
        """同步成功"""
        InfoBar.success("成功", msg, duration=3000, parent=self)
        # 刷新列表（延迟一小段时间确保后端已完成数据库更新）
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(500, self._load_assignments)
        # 同时刷新课程墙（因为同步操作会更新课程数据）
        QTimer.singleShot(500, self.course_wall._load_courses)

    def _on_sync_failed(self, error_msg: str) -> None:
        """同步失败"""
        InfoBar.error("错误", error_msg, duration=2000, parent=self)

    def update_user_info(self, username: str) -> None:
        """
        更新用户信息显示

        Args:
            username: 用户名
        """
        # 可以在这里添加用户信息显示
        pass
