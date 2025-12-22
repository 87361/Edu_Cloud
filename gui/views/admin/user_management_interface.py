"""管理员用户管理界面"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt, pyqtSignal
from datetime import datetime

from qfluentwidgets import (
    TitleLabel,
    LineEdit,
    PrimaryPushButton,
    PushButton,
    TableWidget,
    FluentIcon as FIF,
    InfoBar,
    ComboBox,
    BodyLabel,
    MessageBox,
)

from ...services.async_service import AsyncService
from ...api_client import api_client, APIError


class UserManagementInterface(QWidget):
    """用户管理界面"""
    
    # 数据刷新信号，当用户数据刷新时发出
    data_refreshed = pyqtSignal()

    def __init__(self, parent=None):
        """
        初始化用户管理界面

        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.async_service = AsyncService()
        self.current_page = 0
        self.page_size = 20
        self.total_users = 0
        self.all_users = []  # 存储所有用户数据用于搜索
        self.is_searching = False  # 标记是否正在搜索
        self.current_user_id = None  # 当前登录用户的ID，初始化为None
        self._setup_ui()
        # 先加载当前用户信息，然后再加载用户列表
        self._load_current_user_and_users()

    def _setup_ui(self) -> None:
        """设置UI"""
        self.v_layout = QVBoxLayout(self)
        self.v_layout.setContentsMargins(30, 30, 30, 30)

        # 顶部工具栏
        tool_layout = QHBoxLayout()
        
        # 搜索框
        self.search_bar = LineEdit(self)
        self.search_bar.setPlaceholderText("搜索用户名、邮箱或CAS学号...")
        self.search_bar.setFixedWidth(300)
        self.search_bar.textChanged.connect(self._on_search_text_changed)
        self.search_bar.returnPressed.connect(self._on_search)
        
        # 筛选下拉框
        self.role_filter = ComboBox(self)
        self.role_filter.addItems(["全部角色", "管理员", "普通用户"])
        self.role_filter.setCurrentIndex(0)
        self.role_filter.currentIndexChanged.connect(self._on_filter_changed)
        self.role_filter.setFixedWidth(120)
        
        self.status_filter = ComboBox(self)
        self.status_filter.addItems(["全部状态", "活跃", "禁用"])
        self.status_filter.setCurrentIndex(0)
        self.status_filter.currentIndexChanged.connect(self._on_filter_changed)
        self.status_filter.setFixedWidth(120)
        
        # 刷新按钮
        self.btn_refresh = PushButton(FIF.SYNC, "刷新", self)
        self.btn_refresh.clicked.connect(self._on_refresh)
        
        self.btn_add = PrimaryPushButton(FIF.ADD, "添加学生", self)
        self.btn_add.clicked.connect(self._on_add_user)
        
        self.btn_export = PushButton(FIF.DOWNLOAD, "导出数据", self)
        self.btn_export.clicked.connect(self._on_export)

        tool_layout.addWidget(self.search_bar)
        tool_layout.addWidget(self.role_filter)
        tool_layout.addWidget(self.status_filter)
        tool_layout.addWidget(self.btn_refresh)
        tool_layout.addStretch(1)
        tool_layout.addWidget(self.btn_add)
        tool_layout.addWidget(self.btn_export)

        # 表格
        self.table = TableWidget(self)
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            'ID', '用户名', '姓名', '邮箱', '角色', 'CAS学号', 'CAS绑定', '状态', '创建时间', '操作'
        ])
        self.table.verticalHeader().hide()
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)
        self.table.setWordWrap(False)

        # 设置表头自适应
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # 分页控件
        pagination_layout = QHBoxLayout()
        self.page_info_label = BodyLabel("", self)
        self.btn_prev = PushButton("上一页", self)
        self.btn_prev.clicked.connect(self._on_prev_page)
        self.btn_prev.setEnabled(False)
        self.btn_next = PushButton("下一页", self)
        self.btn_next.clicked.connect(self._on_next_page)
        self.btn_next.setEnabled(False)
        
        pagination_layout.addWidget(self.page_info_label)
        pagination_layout.addStretch(1)
        pagination_layout.addWidget(self.btn_prev)
        pagination_layout.addWidget(self.btn_next)

        self.v_layout.addWidget(TitleLabel("学生信息管理", self))
        self.v_layout.addSpacing(10)
        self.v_layout.addLayout(tool_layout)
        self.v_layout.addSpacing(10)
        self.v_layout.addWidget(self.table)
        self.v_layout.addSpacing(10)
        self.v_layout.addLayout(pagination_layout)

    def _load_users(self, reset_page: bool = False) -> None:
        """加载用户列表（分页）"""
        if reset_page:
            self.current_page = 0
        
        # 如果正在搜索，不执行分页加载
        if self.is_searching:
            return
        
        # 获取筛选条件
        role_filter = None
        if self.role_filter.currentIndex() == 1:  # 管理员
            role_filter = "admin"
        elif self.role_filter.currentIndex() == 2:  # 普通用户
            role_filter = "user"
        
        is_active_filter = None
        if self.status_filter.currentIndex() == 1:  # 活跃
            is_active_filter = True
        elif self.status_filter.currentIndex() == 2:  # 禁用
            is_active_filter = False
        
        offset = self.current_page * self.page_size
        
        def load_func():
            try:
                return api_client.get_admin_users(
                    limit=self.page_size,
                    offset=offset,
                    role=role_filter,
                    is_active=is_active_filter
                )
            except APIError as e:
                InfoBar.error("错误", f"加载用户列表失败: {e.message}", duration=2000, parent=self)
                return {"users": [], "total": 0}

        def on_success(result: dict):
            users = result.get("users", [])
            self.total_users = result.get("total", 0)
            self._update_table(users)
            self._update_pagination()

        self.async_service.execute_async(load_func, on_success, lambda e: None)

    def _update_table(self, users: list) -> None:
        """更新表格"""
        self.table.setRowCount(len(users))
        for i, user in enumerate(users):
            # ID
            self.table.setItem(i, 0, QTableWidgetItem(str(user.get("id", ""))))
            # 用户名
            self.table.setItem(i, 1, QTableWidgetItem(user.get("username", "")))
            # 姓名
            self.table.setItem(i, 2, QTableWidgetItem(user.get("full_name") or ""))
            # 邮箱
            self.table.setItem(i, 3, QTableWidgetItem(user.get("email") or ""))
            # 角色
            role = user.get("role", "user")
            role_text = "管理员" if role == "admin" else "普通用户"
            self.table.setItem(i, 4, QTableWidgetItem(role_text))
            # CAS学号
            self.table.setItem(i, 5, QTableWidgetItem(user.get("cas_username") or ""))
            # CAS绑定状态
            cas_bound = "已绑定" if user.get("cas_is_bound", False) else "未绑定"
            self.table.setItem(i, 6, QTableWidgetItem(cas_bound))
            # 状态
            status = "活跃" if user.get("is_active", False) else "禁用"
            status_item = QTableWidgetItem(status)
            if not user.get("is_active", False):
                status_item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(i, 7, status_item)
            # 创建时间
            created_at = user.get("created_at", "")
            if created_at:
                try:
                    # 解析ISO格式时间并格式化
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    formatted_time = dt.strftime("%Y-%m-%d %H:%M")
                    self.table.setItem(i, 8, QTableWidgetItem(formatted_time))
                except:
                    self.table.setItem(i, 8, QTableWidgetItem(created_at[:10] if len(created_at) >= 10 else created_at))
            else:
                self.table.setItem(i, 8, QTableWidgetItem(""))
            
            # 操作列 - 删除按钮
            user_id = user.get("id")
            delete_btn = PushButton("删除", self)
            delete_btn.setFixedWidth(60)
            # 如果是当前用户，禁用删除按钮（使用getattr确保属性存在）
            current_id = getattr(self, 'current_user_id', None)
            if current_id and user_id == current_id:
                delete_btn.setEnabled(False)
                delete_btn.setText("自己")
                delete_btn.setToolTip("不能删除自己的账号")
            else:
                delete_btn.clicked.connect(lambda checked, uid=user_id: self._on_delete_user(uid))
            self.table.setCellWidget(i, 9, delete_btn)
    
    def _update_pagination(self) -> None:
        """更新分页信息"""
        total_pages = (self.total_users + self.page_size - 1) // self.page_size if self.total_users > 0 else 1
        current_page_display = self.current_page + 1
        
        self.page_info_label.setText(
            f"共 {self.total_users} 条记录，第 {current_page_display}/{total_pages} 页"
        )
        
        # 更新按钮状态
        self.btn_prev.setEnabled(self.current_page > 0)
        self.btn_next.setEnabled(self.current_page < total_pages - 1)
    
    def _on_prev_page(self) -> None:
        """上一页"""
        if self.current_page > 0:
            self.current_page -= 1
            self._load_users()
    
    def _on_next_page(self) -> None:
        """下一页"""
        total_pages = (self.total_users + self.page_size - 1) // self.page_size if self.total_users > 0 else 1
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self._load_users()
    
    def _on_filter_changed(self) -> None:
        """筛选条件改变"""
        self.is_searching = False
        self._load_all_users(emit_signal=True)  # 重新加载所有数据，并通知dashboard刷新
    
    def _on_search_text_changed(self, text: str) -> None:
        """搜索文本改变（实时搜索）"""
        if not text.strip():
            # 如果搜索框为空，恢复分页显示
            self.is_searching = False
            self.current_page = 0
            self._load_users()
            return
        
        # 在前端进行搜索过滤
        self.is_searching = True
        search_text = text.lower()
        filtered_users = []
        for user in self.all_users:
            username = (user.get("username") or "").lower()
            email = (user.get("email") or "").lower()
            cas_username = (user.get("cas_username") or "").lower()
            full_name = (user.get("full_name") or "").lower()
            
            if (search_text in username or 
                search_text in email or 
                search_text in cas_username or
                search_text in full_name):
                filtered_users.append(user)
        
        # 更新分页信息（搜索模式下）
        self.total_users = len(filtered_users)
        self._update_table(filtered_users)
        self._update_pagination()
    
    def _load_all_users(self, emit_signal: bool = False) -> None:
        """加载所有用户数据（用于搜索）"""
        def load_func():
            try:
                # 加载大量数据用于搜索（最多1000条）
                return api_client.get_admin_users(limit=1000, offset=0)
            except APIError as e:
                return {"users": [], "total": 0}
        
        def on_success(result: dict):
            self.all_users = result.get("users", [])
            # 加载完所有数据后，再加载分页数据
            self._load_users()
            # 只在需要时发出数据刷新信号
            if emit_signal:
                self.data_refreshed.emit()
        
        self.async_service.execute_async(load_func, on_success, lambda e: None)

    def _on_search(self) -> None:
        """搜索（回车触发）"""
        # 搜索功能已在_on_search_text_changed中实现
        pass
    
    def _on_refresh(self) -> None:
        """刷新数据"""
        self.is_searching = False
        self.search_bar.clear()  # 清空搜索框
        self._load_all_users(emit_signal=True)  # 重新加载所有数据，并通知dashboard刷新
        InfoBar.success("成功", "数据已刷新", duration=1500, parent=self)

    def _load_current_user_and_users(self) -> None:
        """先加载当前用户信息，然后加载用户列表"""
        def load_current_user():
            try:
                return api_client.get_user_info()
            except APIError:
                return {"data": {}}
        
        def on_current_user_success(result: dict):
            user_data = result.get("data", {})
            self.current_user_id = user_data.get("id")
            # 当前用户信息加载完成后，再加载用户列表
            self._load_all_users(emit_signal=False)
        
        def on_current_user_error(error: str):
            # 即使加载当前用户失败，也继续加载用户列表
            self.current_user_id = None
            self._load_all_users(emit_signal=False)
        
        self.async_service.execute_async(load_current_user, on_current_user_success, on_current_user_error)
    
    def _on_delete_user(self, user_id: int) -> None:
        """删除用户"""
        # 查找用户信息用于显示
        user_info = None
        for user in self.all_users:
            if user.get("id") == user_id:
                user_info = user
                break
        
        username = user_info.get("username", "未知用户") if user_info else "未知用户"
        
        # 确认对话框
        msg_box = MessageBox(
            "确认删除",
            f"确定要删除用户 '{username}' 吗？\n\n"
            f"此操作将永久删除该用户及其所有关联数据：\n"
            f"- 所有作业\n"
            f"- 所有课程\n"
            f"- 所有通知\n"
            f"- Token记录\n\n"
            f"此操作不可恢复！",
            self
        )
        
        if msg_box.exec():
            def delete_func():
                try:
                    return api_client.delete_admin_user(user_id)
                except APIError as e:
                    raise Exception(e.message)
            
            def on_success(result: dict):
                deleted_data = result.get("deleted_data", {})
                message = result.get("message", "用户已删除")
                InfoBar.success(
                    "删除成功",
                    f"{message}\n"
                    f"已删除：{deleted_data.get('assignments', 0)}个作业，"
                    f"{deleted_data.get('courses', 0)}门课程，"
                    f"{deleted_data.get('notifications', 0)}条通知",
                    duration=3000,
                    parent=self
                )
                # 刷新数据
                self._load_all_users(emit_signal=True)
            
            def on_error(error: str):
                InfoBar.error("删除失败", f"删除用户失败: {error}", duration=3000, parent=self)
            
            self.async_service.execute_async(delete_func, on_success, on_error)
    
    def _on_add_user(self) -> None:
        """添加用户"""
        # TODO: 实现添加用户功能
        InfoBar.info("提示", "添加用户功能待实现", duration=2000, parent=self)

    def _on_export(self) -> None:
        """导出数据"""
        # TODO: 实现导出功能
        InfoBar.info("提示", "导出功能待实现", duration=2000, parent=self)


