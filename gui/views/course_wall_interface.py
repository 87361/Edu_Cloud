"""课程墙界面"""
from typing import Optional
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QApplication

from qfluentwidgets import (
    ScrollArea,
    FlowLayout,
    SubtitleLabel,
    BodyLabel,
    InfoBar,
    PrimaryPushButton,
    PushButton,
    FluentWindow,
)

from ..models.course import Course
from ..services.course_service import CourseService
from ..services.assignment_service import AssignmentService
from ..services.async_service import AsyncService
from ..services.auth_service import AuthService
from ..api_client import api_client
from .components.course_card import CourseCard
from .components.sync_dialog import SyncDialog


class CourseWallInterface(QWidget):
    """课程墙界面"""

    course_clicked = pyqtSignal(Course)  # 课程点击信号
    sync_completed = pyqtSignal()  # 同步完成信号，用于通知父组件刷新作业列表

    def __init__(self, parent=None):
        """
        初始化课程墙界面

        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.course_service = CourseService()
        self.assignment_service = AssignmentService()
        self.async_service = AsyncService()
        self.auth_service = AuthService()
        self._courses: list[Course] = []
        self._course_cards: dict[str, CourseCard] = {}  # 存储课程卡片，key为课程名称
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
        self.sync_button = PrimaryPushButton("同步", self)
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
        # 先显示课程卡片（使用临时进度），然后异步加载作业完成率
        self._update_course_wall()
        # 异步计算每个课程的作业完成率
        self._calculate_course_progress()

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
        
        # 清空课程卡片字典（因为widget已被删除）
        self._course_cards.clear()

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

        # 显示课程卡片（先使用None进度，表示正在计算）
        self._course_cards = {}  # 存储课程卡片，key为课程名称
        for idx, course in enumerate(self._courses):
            color = colors[idx % len(colors)]
            # 初始显示为None（会显示"---"），等待作业数据加载后更新
            card = CourseCard(course, progress=None, color_hex=color, parent=self.course_container)
            card.clicked.connect(self.course_clicked.emit)
            self.flow_layout.addWidget(card)
            self._course_cards[course.name] = card

    def _on_sync_click(self) -> None:
        """同步按钮点击"""
        # 获取当前用户信息
        user = self.auth_service.get_current_user()
        if not user or not user.cas_is_bound:
            InfoBar.error("错误", "未绑定CAS账户，请先绑定账户", duration=2000, parent=self)
            return
        
        dialog = SyncDialog(self, user=user)
        dialog.confirmed.connect(self._on_sync_confirm)
        dialog.exec()
        # 对话框关闭后，修复主窗口和导航栏状态（无论是否真的同步）
        self._fix_main_window_after_dialog()

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
        
        password_dialog.exec()
        # 对话框关闭后，修复主窗口和导航栏状态
        self._fix_main_window_after_dialog()

    def _sync_with_bound_account(self, cas_password: str) -> None:
        """使用已绑定账户同步"""
        # 显示加载提示
        InfoBar.info("提示", "正在同步所有内容，请稍候...", duration=3000, parent=self)
        
        def sync_func():
            try:
                return self.assignment_service.sync_all(
                    cas_password=cas_password
                )
            except Exception as e:
                raise

        def on_success(result: tuple[str, dict]):
            msg, stats = result
            self._on_sync_success(msg, stats)

        self.async_service.execute_async(
            sync_func, on_success, self._on_sync_failed
        )

    def _on_sync_confirm(self, password: str) -> None:
        """确认同步"""
        # 获取当前用户信息
        user = self.auth_service.get_current_user()
        if not user or not user.cas_username:
            InfoBar.error("错误", "无法获取用户信息", duration=2000, parent=self)
            return
        
        # 显示加载提示
        InfoBar.info("提示", "正在同步所有内容，请稍候...", duration=3000, parent=self)
        
        def sync_func():
            try:
                return self.assignment_service.sync_all(
                    cas_password=password
                )
            except Exception as e:
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
            # 课程统计
            course_stats = stats.get("courses", {})
            new_courses = course_stats.get("new_courses", 0)
            updated_courses = course_stats.get("updated_courses", 0)
            total_courses = course_stats.get("total_courses", 0)
            new_resources = course_stats.get("new_resources_added", 0)
            
            # 作业统计
            assignment_stats = stats.get("assignments", {})
            new_assignments = assignment_stats.get("new_added", 0)
            total_assignments = assignment_stats.get("total_fetched", 0)
            
            detail_parts = []
            if total_courses > 0:
                detail_parts.append(f"课程{total_courses}门")
            if new_courses > 0:
                detail_parts.append(f"新增课程{new_courses}门")
            if updated_courses > 0:
                detail_parts.append(f"更新课程{updated_courses}门")
            if new_resources > 0:
                detail_parts.append(f"新增资源{new_resources}个")
            if total_assignments > 0:
                detail_parts.append(f"作业{total_assignments}个")
            if new_assignments > 0:
                detail_parts.append(f"新增作业{new_assignments}个")
            
            if detail_parts:
                detail_msg = f"{msg}（{', '.join(detail_parts)}）"
        
        InfoBar.success("成功", detail_msg, duration=3000, parent=self)
        # 刷新课程列表
        self._load_courses()
        # 通知父组件刷新作业列表
        self.sync_completed.emit()
        # 确保主窗口导航栏状态正常（修复同步后主题切换问题）
        self._ensure_navigation_state()

    def _fix_main_window_after_dialog(self) -> None:
        """对话框关闭后修复主窗口和导航栏状态"""
        try:
            # 获取主窗口（FluentWindow）
            parent = self.parent()
            main_window = None
            while parent is not None:
                if isinstance(parent, FluentWindow):
                    main_window = parent
                    break
                parent = parent.parent()
            
            if main_window is not None:
                # 立即恢复主窗口焦点和激活状态
                main_window.activateWindow()
                main_window.raise_()
                main_window.setFocus()
                
                # 延迟修复导航栏状态，确保对话框完全关闭
                def fix_navigation():
                    try:
                        if hasattr(main_window, 'navigationInterface'):
                            nav = main_window.navigationInterface
                            # 确保导航栏样式正确应用
                            style = nav.style()
                            if style:
                                style.unpolish(nav)
                                style.polish(nav)
                            # 更新导航栏
                            nav.update()
                            nav.repaint()
                            # 处理事件队列
                            QApplication.processEvents()
                    except Exception as e:
                        print(f"修复导航栏状态失败: {e}")
                
                # 延迟100ms执行，确保对话框完全关闭
                QTimer.singleShot(100, fix_navigation)
        except Exception as e:
            print(f"查找主窗口失败: {e}")

    def _ensure_navigation_state(self) -> None:
        """确保主窗口导航栏状态正常（修复同步后主题切换问题）"""
        try:
            # 获取主窗口（FluentWindow）
            parent = self.parent()
            main_window = None
            while parent is not None:
                if isinstance(parent, FluentWindow):
                    main_window = parent
                    break
                parent = parent.parent()
            
            if main_window is not None and hasattr(main_window, 'navigationInterface'):
                # 延迟执行，确保同步操作完全完成
                def fix_navigation():
                    try:
                        nav = main_window.navigationInterface
                        # 确保导航栏样式正确应用
                        nav.style().unpolish(nav)
                        nav.style().polish(nav)
                        # 更新导航栏
                        nav.update()
                        nav.repaint()
                        # 处理事件队列
                        QApplication.processEvents()
                    except Exception as e:
                        print(f"修复导航栏状态失败: {e}")
                
                # 延迟200ms执行，确保同步操作完全完成
                QTimer.singleShot(200, fix_navigation)
        except Exception as e:
            print(f"查找主窗口失败: {e}")

    def _on_sync_failed(self, error_msg: str) -> None:
        """同步失败"""
        InfoBar.error("错误", error_msg, duration=2000, parent=self)
    
    def _calculate_course_progress(self) -> None:
        """异步计算每个课程的作业完成率"""
        if not self._courses:
            return
        
        def calculate_func():
            """计算所有课程的作业完成率"""
            course_progress = {}
            # 获取所有作业
            try:
                all_assignments = api_client.get_assignments()
            except Exception as e:
                print(f"获取作业列表失败: {e}")
                return course_progress
            
            # 按课程名称分组统计
            for course in self._courses:
                course_name = course.name
                # 获取该课程的所有作业
                course_assignments = [
                    a for a in all_assignments 
                    if a.get("course_name") == course_name
                ]
                
                if not course_assignments:
                    # 没有作业，进度为None
                    course_progress[course_name] = None
                else:
                    # 计算完成率
                    total = len(course_assignments)
                    completed = sum(1 for a in course_assignments if a.get("status") == "已提交")
                    progress = completed / total if total > 0 else 0.0
                    course_progress[course_name] = progress
            
            return course_progress
        
        def on_success(progress_dict: dict):
            """更新课程卡片的进度"""
            for course_name, progress in progress_dict.items():
                if course_name in self._course_cards:
                    card = self._course_cards[course_name]
                    # 更新进度显示
                    if progress is None:
                        # 没有作业
                        card.progress_lbl.setText("进度 ---")
                        card.progress_bar.setVisible(False)
                    else:
                        # 有作业，显示完成率
                        card.progress_lbl.setText(f"进度 {int(progress*100)}%")
                        card.progress_bar.setValue(int(progress * 100))
                        card.progress_bar.setVisible(True)
        
        def on_error(error_msg: str):
            """计算失败时的处理"""
            print(f"计算课程进度失败: {error_msg}")
            # 失败时，所有课程显示"---"
            for card in self._course_cards.values():
                card.progress_lbl.setText("进度 ---")
                card.progress_bar.setVisible(False)
        
        self.async_service.execute_async(
            calculate_func, on_success, on_error
        )

