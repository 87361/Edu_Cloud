"""课程详情界面 - Fluent Design 重构版"""
from typing import Optional
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QFrame, QSizePolicy

from qfluentwidgets import (
    TransparentToolButton,
    LargeTitleLabel,   # 确保库版本支持
    TitleLabel,
    BodyLabel,
    CaptionLabel,      
    ElevatedCardWidget,
    SimpleCardWidget,  # 确保库版本支持
    ScrollArea,
    Pivot,             
    FluentIcon as FIF,
    InfoBar,
    IconWidget,        
    PrimaryPushButton,
    HyperlinkButton
)

from ..models.course import Course
from ..models.assignment import Assignment
from ..models.notification import Notification
from ..services.course_service import CourseService
from ..services.async_service import AsyncService
from ..api_client import api_client


class ResourceItemCard(SimpleCardWidget):
    """自定义资源列表项卡片"""
    def __init__(self, resource: dict, parent=None):
        super().__init__(parent)
        self.resource = resource
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)

        # 1. 左侧图标 (根据类型判断，使用通用图标防报错)
        res_type = self.resource.get('type', 'file').lower()
        if 'pdf' in res_type:
            icon = FIF.DOCUMENT  # 修正：用通用文档图标
        elif 'video' in res_type or 'mp4' in res_type:
            icon = FIF.VIDEO
        elif 'img' in res_type or 'png' in res_type:
            icon = FIF.PHOTO
        else:
            icon = FIF.FOLDER
        
        self.icon_widget = IconWidget(icon, self)
        self.icon_widget.setFixedSize(24, 24)

        # 2. 中间信息
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        self.title_label = BodyLabel(self.resource.get("title", "未知资源"), self)
        
        size = self.resource.get('size', '未知大小')
        type_text = self.resource.get('type', '未知类型')
        self.meta_label = CaptionLabel(f"{type_text} • {size}", self)
        self.meta_label.setTextColor(Qt.GlobalColor.gray, Qt.GlobalColor.gray)
        
        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.meta_label)

        # 3. 右侧操作按钮
        self.action_btn = TransparentToolButton(FIF.DOWNLOAD, self)
        self.action_btn.setToolTip("下载资源")

        layout.addWidget(self.icon_widget)
        layout.addLayout(info_layout)
        layout.addStretch(1)
        layout.addWidget(self.action_btn)


class CourseDetailInterface(QWidget):
    """课程详情界面"""

    back_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.course: Optional[Course] = None
        self.course_service = CourseService()
        self.async_service = AsyncService()
        
        # 启用背景透明，配合主窗口的 Mica/Acrylic 效果
        self.setObjectName("CourseDetailInterface")
        
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        # 主布局使用 VBoxLayout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 滚动区域
        self.scroll_area = ScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("ScrollArea {background: transparent; border: none;}")
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(self.scroll_content)
        self.content_layout.setContentsMargins(36, 20, 36, 36) # 舒适的边距
        self.content_layout.setSpacing(24) 

        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)

        # === 1. 顶部导航栏 ===
        header_layout = QHBoxLayout()
        self.back_btn = TransparentToolButton(FIF.RETURN, self)
        self.back_btn.clicked.connect(self.back_signal.emit)
        
        self.page_title = TitleLabel("课程详情", self)
        
        header_layout.addWidget(self.back_btn)
        header_layout.addSpacing(10)
        header_layout.addWidget(self.page_title)
        header_layout.addStretch(1)
        
        self.content_layout.addLayout(header_layout)

        # === 2. 课程 Hero 卡片 ===
        self.hero_card = ElevatedCardWidget(self)
        self.hero_card.setBorderRadius(10)
        hero_layout = QHBoxLayout(self.hero_card)
        hero_layout.setContentsMargins(24, 24, 24, 24)
        hero_layout.setSpacing(24)

        # 左侧：课程图标/封面占位
        self.course_icon = IconWidget(FIF.EDUCATION, self.hero_card)
        self.course_icon.setFixedSize(64, 64)
        
        # 右侧：文本信息
        text_layout = QVBoxLayout()
        text_layout.setSpacing(8)
        
        self.course_name_label = LargeTitleLabel("加载中...", self.hero_card)
        self.teacher_btn = HyperlinkButton(url="", text="讲师: --", parent=self.hero_card)
        
        self.description_label = BodyLabel("正在获取课程详情...", self.hero_card)
        self.description_label.setWordWrap(True)
        self.description_label.setTextColor(Qt.GlobalColor.darkGray, Qt.GlobalColor.gray)

        text_layout.addWidget(self.course_name_label)
        text_layout.addWidget(self.teacher_btn)
        text_layout.addWidget(self.description_label)
        
        hero_layout.addWidget(self.course_icon, 0, Qt.AlignmentFlag.AlignTop)
        hero_layout.addLayout(text_layout, 1)

        self.content_layout.addWidget(self.hero_card)

        # === 3. Pivot 导航栏 ===
        self.pivot = Pivot(self)
        self.pivot.addItem(routeKey="resources", text="课件资源")
        self.pivot.addItem(routeKey="assignments", text="作业任务")
        self.pivot.addItem(routeKey="notifications", text="课程公告")
        self.pivot.addItem(routeKey="discussions", text="讨论区")
        
        self.content_layout.addWidget(self.pivot)

        # === 4. 内容切换区 ===
        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.setStyleSheet("background: transparent;")
        
        # -- 资源页 --
        self.resources_page = QWidget()
        self.resources_layout = QVBoxLayout(self.resources_page)
        self.resources_layout.setContentsMargins(0, 10, 0, 0)
        self.resources_layout.setSpacing(10)
        self.resources_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.stacked_widget.addWidget(self.resources_page)

        # -- 作业页 --
        self.assignments_page = QWidget()
        self.assignments_layout = QVBoxLayout(self.assignments_page)
        self.assignments_layout.setContentsMargins(0, 10, 0, 0)
        self.assignments_layout.setSpacing(10)
        self.assignments_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.stacked_widget.addWidget(self.assignments_page)

        # -- 公告页 --
        self.notifications_page = QWidget()
        self.notifications_layout = QVBoxLayout(self.notifications_page)
        self.notifications_layout.setContentsMargins(0, 10, 0, 0)
        self.notifications_layout.setSpacing(10)
        self.notifications_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.stacked_widget.addWidget(self.notifications_page)

        # -- 讨论页 --
        self.discussions_page = self._create_placeholder_page("暂无讨论", FIF.CHAT)
        self.stacked_widget.addWidget(self.discussions_page)

        self.content_layout.addWidget(self.stacked_widget)
        self.content_layout.addStretch(1)

        # 连接 Pivot 切换
        self.pivot.currentItemChanged.connect(
            lambda k: self.stacked_widget.setCurrentIndex(
                ["resources", "assignments", "notifications", "discussions"].index(k)
            )
        )

    def _create_placeholder_page(self, text: str, icon: FIF) -> QWidget:
        """辅助方法：创建占位页面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 40, 0, 40)
        
        icon_w = IconWidget(icon, widget)
        icon_w.setFixedSize(48, 48)
        
        label = BodyLabel(text, widget)
        label.setTextColor(Qt.GlobalColor.gray, Qt.GlobalColor.gray)
        
        layout.addWidget(icon_w, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(16)
        layout.addWidget(label, 0, Qt.AlignmentFlag.AlignCenter)
        return widget

    def _connect_signals(self) -> None:
        """连接信号（如果需要的话）"""
        # 注意：当前使用异步服务的回调方式，不需要连接信号
        # 如果需要通过信号方式，可以在这里连接
        pass

    def update_data(self, course: Course) -> None:
        self.course = course
        # 重置 UI 状态
        self.pivot.setCurrentItem("resources")
        self.course_name_label.setText("加载中...")
        self.description_label.setText("正在获取...")
        
        self._update_basic_info()
        self._load_course_detail()
        self._load_resources()
        self._load_assignments()
        self._load_notifications()

    def _update_basic_info(self) -> None:
        if not self.course:
            return

        self.course_name_label.setText(self.course.name or "未知课程")
        teacher_text = self.course.teacher or "未知讲师"
        self.teacher_btn.setText(f"讲师: {teacher_text}")
        
        description = self.course.description or "暂无描述"
        self.description_label.setText(description)

    def _load_course_detail(self) -> None:
        """异步加载课程详情"""
        if not self.course or not self.course.id:
            return
        
        def load_func():
            try:
                return self.course_service.load_course_detail(self.course.id)
            except Exception as e:
                self.course_service.load_failed.emit(str(e))
                raise

        self.async_service.execute_async(
            load_func, self._on_course_loaded, self._on_load_failed
        )

    def _load_resources(self) -> None:
        """异步加载课程资源"""
        if not self.course or not self.course.id:
            return
        
        def load_func():
            try:
                return self.course_service.load_course_resources(self.course.id)
            except Exception as e:
                self.course_service.load_failed.emit(str(e))
                raise

        self.async_service.execute_async(
            load_func, self._on_resources_loaded, self._on_load_failed
        )

    def _on_course_loaded(self, course: Course) -> None:
        """课程详情加载成功"""
        self.course = course
        self._update_basic_info()

    def _on_resources_loaded(self, resources: list) -> None:
        """资源列表加载成功"""
        # 清除现有资源
        widgets_to_remove = []
        for i in range(self.resources_layout.count()):
            item = self.resources_layout.itemAt(i)
            if item and item.widget():
                widgets_to_remove.append(item.widget())
        
        for widget in widgets_to_remove:
            self.resources_layout.removeWidget(widget)
            widget.deleteLater()

        # 显示资源列表
        if not resources:
            empty_label = BodyLabel("暂无资源", self.resources_page)
            empty_label.setTextColor(Qt.GlobalColor.gray, Qt.GlobalColor.gray)
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.resources_layout.addWidget(empty_label)
            return

        for resource in resources:
            card = ResourceItemCard(resource, self.resources_page)
            self.resources_layout.addWidget(card)

    def _load_assignments(self) -> None:
        """异步加载课程作业"""
        if not self.course or not self.course.name:
            return
        
        def load_func():
            try:
                assignments_data = api_client.get_course_assignments(self.course.name)
                return [Assignment.from_dict(data) for data in assignments_data]
            except Exception as e:
                self._on_load_failed(str(e))
                raise

        self.async_service.execute_async(
            load_func, self._on_assignments_loaded, self._on_load_failed
        )

    def _on_assignments_loaded(self, assignments: list[Assignment]) -> None:
        """作业列表加载成功"""
        # 清除现有作业
        widgets_to_remove = []
        for i in range(self.assignments_layout.count()):
            item = self.assignments_layout.itemAt(i)
            if item and item.widget():
                widgets_to_remove.append(item.widget())
        
        for widget in widgets_to_remove:
            self.assignments_layout.removeWidget(widget)
            widget.deleteLater()

        # 显示作业列表
        if not assignments:
            empty_label = BodyLabel("暂无作业", self.assignments_page)
            empty_label.setTextColor(Qt.GlobalColor.gray, Qt.GlobalColor.gray)
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.assignments_layout.addWidget(empty_label)
            return

        # 过滤掉无效的课程名称
        valid_assignments = [
            a for a in assignments 
            if a.course_name 
            and "未分类" not in a.course_name 
            and "待办事项" not in a.course_name
            and a.course_name != "未知课程"
        ]

        if not valid_assignments:
            empty_label = BodyLabel("暂无作业", self.assignments_page)
            empty_label.setTextColor(Qt.GlobalColor.gray, Qt.GlobalColor.gray)
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.assignments_layout.addWidget(empty_label)
            return

        for assignment in valid_assignments:
            card = ElevatedCardWidget(self.assignments_page)
            card.setBorderRadius(8)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(20, 15, 20, 15)
            card_layout.setSpacing(8)

            # 作业标题
            title_label = BodyLabel(assignment.title, card)
            card_layout.addWidget(title_label)

            # 作业信息（截止时间、状态、分数）
            info_parts = []
            if assignment.deadline:
                deadline = assignment.get_deadline_display()
                info_parts.append(f"截止: {deadline}")
            info_parts.append(f"状态: {assignment.status}")
            if assignment.score:
                info_parts.append(f"分数: {assignment.score}")
            
            info_label = CaptionLabel(" • ".join(info_parts), card)
            info_label.setTextColor(Qt.GlobalColor.gray, Qt.GlobalColor.gray)
            card_layout.addWidget(info_label)

            self.assignments_layout.addWidget(card)

    def _load_notifications(self) -> None:
        """异步加载课程公告"""
        if not self.course or not self.course.name:
            return
        
        def load_func():
            try:
                notifications_data = api_client.get_course_notifications(self.course.name)
                return [Notification.from_dict(data) for data in notifications_data]
            except Exception as e:
                self._on_load_failed(str(e))
                raise

        self.async_service.execute_async(
            load_func, self._on_notifications_loaded, self._on_load_failed
        )

    def _on_notifications_loaded(self, notifications: list[Notification]) -> None:
        """公告列表加载成功"""
        # 注意：PyQt的信号系统会自动将信号发送到主线程，所以这里应该已经在主线程了
        # 清除现有公告
        widgets_to_remove = []
        for i in range(self.notifications_layout.count()):
            item = self.notifications_layout.itemAt(i)
            if item and item.widget():
                widgets_to_remove.append(item.widget())
        
        for widget in widgets_to_remove:
            self.notifications_layout.removeWidget(widget)
            widget.deleteLater()

        # 显示公告列表
        if not notifications:
            empty_label = BodyLabel("暂无公告", self.notifications_page)
            empty_label.setTextColor(Qt.GlobalColor.gray, Qt.GlobalColor.gray)
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.notifications_layout.addWidget(empty_label)
            return

        for notification in notifications:
            card = ElevatedCardWidget(self.notifications_page)
            card.setBorderRadius(8)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(20, 15, 20, 15)
            card_layout.setSpacing(8)

            # 公告标题和类型
            header_layout = QHBoxLayout()
            title_label = BodyLabel(notification.title or "无标题", card)
            header_layout.addWidget(title_label)
            header_layout.addStretch()
            
            # 类型标签
            if notification.type:
                type_label = CaptionLabel(notification.type, card)
                type_label.setTextColor(Qt.GlobalColor.gray, Qt.GlobalColor.gray)
                header_layout.addWidget(type_label)
            
            card_layout.addLayout(header_layout)

            # 公告内容（简化显示，只显示前100字符）
            if notification.content:
                import re
                # 简单去除HTML标签
                content_text = re.sub(r'<[^>]+>', '', notification.content)
                if len(content_text) > 100:
                    content_text = content_text[:100] + "..."
                content_label = BodyLabel(content_text, card)
                content_label.setWordWrap(True)
                content_label.setTextColor(Qt.GlobalColor.gray, Qt.GlobalColor.gray)
                card_layout.addWidget(content_label)

            # 公告信息（时间、阅读状态）
            info_parts = []
            if notification.time:
                try:
                    from datetime import datetime
                    time_str = notification.time
                    if 'T' in time_str:
                        time_str = time_str.split('T')[0]
                    info_parts.append(f"时间: {time_str}")
                except:
                    pass
            info_parts.append("已读" if notification.is_read else "未读")
            
            info_label = CaptionLabel(" • ".join(info_parts), card)
            info_label.setTextColor(Qt.GlobalColor.gray, Qt.GlobalColor.gray)
            card_layout.addWidget(info_label)

            self.notifications_layout.addWidget(card)

    def _on_load_failed(self, error_msg: str) -> None:
        """加载失败"""
        InfoBar.error("错误", error_msg, duration=2000, parent=self)