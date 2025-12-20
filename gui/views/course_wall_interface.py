"""课程墙界面"""
from typing import Optional
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from qfluentwidgets import (
    ScrollArea,
    FlowLayout,
    SubtitleLabel,
    BodyLabel,
    InfoBar,
    PrimaryPushButton,
    PushButton,
)

from ..models.course import Course
from ..services.course_service import CourseService
from ..services.async_service import AsyncService
from ..services.auth_service import AuthService
from .components.course_card import CourseCard
from .components.sync_dialog import SyncDialog


class CourseWallInterface(QWidget):
    """课程墙界面"""

    course_clicked = pyqtSignal(Course)  # 课程点击信号

    def __init__(self, parent=None):
        """
        初始化课程墙界面

        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.course_service = CourseService()
        self.async_service = AsyncService()
        self.auth_service = AuthService()
        self._courses: list[Course] = []
        self._setup_ui()
        self._connect_signals()
        self._load_courses()

    def _setup_ui(self) -> None:
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # 标题栏（包含标题和同步按钮）
        title_layout = QHBoxLayout()
        self.title_label = SubtitleLabel("我的课程", self)
        title_layout.addWidget(self.title_label)
        title_layout.addStretch(1)
        
        # 同步按钮
        self.sync_button = PrimaryPushButton("同步课程", self)
        self.sync_button.clicked.connect(self._on_sync_click)
        title_layout.addWidget(self.sync_button)
        
        # 刷新按钮
        self.refresh_button = PushButton("刷新", self)
        self.refresh_button.clicked.connect(self._load_courses)
        title_layout.addWidget(self.refresh_button)
        
        layout.addLayout(title_layout)

        # 课程滚动区
        self.scroll_area = ScrollArea(self)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        self.scroll_area.setWidgetResizable(True)

        # 课程容器
        self.course_container = QWidget()
        # 使用 FlowLayout 实现瀑布流
        self.flow_layout = FlowLayout(self.course_container, needAni=True)
        self.flow_layout.setContentsMargins(30, 30, 30, 30)
        self.flow_layout.setVerticalSpacing(20)
        self.flow_layout.setHorizontalSpacing(20)

        self.scroll_area.setWidget(self.course_container)
        layout.addWidget(self.scroll_area)

    def _connect_signals(self) -> None:
        """连接信号"""
        self.course_service.courses_loaded.connect(self._on_courses_loaded)
        self.course_service.load_failed.connect(self._on_load_failed)
        self.course_service.sync_success.connect(self._on_sync_success)
        self.course_service.sync_failed.connect(self._on_sync_failed)

    def _load_courses(self) -> None:
        """加载课程列表"""
        def load_func():
            try:
                return self.course_service.load_courses()
            except Exception as e:
                self.course_service.load_failed.emit(str(e))
                raise

        self.async_service.execute_async(
            load_func, self._on_courses_loaded, self._on_load_failed
        )

    def _on_courses_loaded(self, courses: list[Course]) -> None:
        """课程列表加载成功"""
        self._courses = courses
        self._update_course_wall()

    def _on_load_failed(self, error_msg: str) -> None:
        """加载失败"""
        InfoBar.error("错误", error_msg, duration=2000, parent=self)

    def _update_course_wall(self) -> None:
        """更新课程墙显示"""
        # 清除现有组件 - 直接删除所有子 widget
        widgets_to_remove = []
        for i in range(self.flow_layout.count()):
            item = self.flow_layout.itemAt(i)
            if item and item.widget():
                widgets_to_remove.append(item.widget())
        
        # 删除所有 widget
        for widget in widgets_to_remove:
            self.flow_layout.removeWidget(widget)
            widget.deleteLater()

        if not self._courses:
            empty_label = BodyLabel("暂无课程，请先同步课程", self.course_container)
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.flow_layout.addWidget(empty_label)
            return

        # 颜色列表（用于装饰色条）
        colors = [
            "#0078D4",  # 蓝色
            "#107C10",  # 绿色
            "#FFB900",  # 黄色
            "#E81123",  # 红色
            "#B4009E",  # 紫色
            "#008272",  # 青色
        ]

        # 显示课程卡片
        for idx, course in enumerate(self._courses):
            color = colors[idx % len(colors)]
            # 暂时使用固定进度，后续可以从作业完成情况计算
            progress = 0.5  # 默认50%
            card = CourseCard(course, progress, color, self.course_container)
            card.clicked.connect(self.course_clicked.emit)
            self.flow_layout.addWidget(card)

    def _on_sync_click(self) -> None:
        """同步按钮点击"""
        # 获取当前用户信息
        user = self.auth_service.get_current_user()
        dialog = SyncDialog(
            self, 
            user=user,
            title="同步课程",
            description="请输入学校账号信息以同步课程"
        )
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
        InfoBar.info("提示", "正在同步课程，请稍候...", duration=3000, parent=self)
        
        def sync_func():
            try:
                return self.course_service.sync_courses(
                    cas_password=cas_password
                )
            except Exception as e:
                self.course_service.sync_failed.emit(str(e))
                raise

        def on_success(result: tuple[str, dict]):
            msg, stats = result
            self._on_sync_success(msg, stats)

        self.async_service.execute_async(
            sync_func, on_success, self._on_sync_failed
        )

    def _on_sync_confirm(self, username: str, password: str) -> None:
        """确认同步"""
        # 显示加载提示
        InfoBar.info("提示", "正在同步课程，请稍候...", duration=3000, parent=self)
        
        def sync_func():
            try:
                return self.course_service.sync_courses(
                    school_username=username,
                    school_password=password
                )
            except Exception as e:
                self.course_service.sync_failed.emit(str(e))
                raise

        def on_success(result: tuple[str, dict]):
            msg, stats = result
            self._on_sync_success(msg, stats)

        self.async_service.execute_async(
            sync_func, on_success, self._on_sync_failed
        )

    def _on_sync_success(self, msg: str, stats: dict) -> None:
        """同步成功"""
        # 构建详细的消息
        detail_msg = msg
        if stats:
            new_courses = stats.get("new_courses", 0)
            updated_courses = stats.get("updated_courses", 0)
            total_courses = stats.get("total_courses", 0)
            new_resources = stats.get("new_resources_added", 0)
            
            detail_parts = []
            if total_courses > 0:
                detail_parts.append(f"共{total_courses}门课程")
            if new_courses > 0:
                detail_parts.append(f"新增{new_courses}门")
            if updated_courses > 0:
                detail_parts.append(f"更新{updated_courses}门")
            if new_resources > 0:
                detail_parts.append(f"新增{new_resources}个资源")
            
            if detail_parts:
                detail_msg = f"{msg}（{', '.join(detail_parts)}）"
        
        InfoBar.success("成功", detail_msg, duration=3000, parent=self)
        # 刷新课程列表
        self._load_courses()

    def _on_sync_failed(self, error_msg: str) -> None:
        """同步失败"""
        InfoBar.error("错误", error_msg, duration=2000, parent=self)

