"""管理员用户管理界面"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt

from qfluentwidgets import (
    TitleLabel,
    LineEdit,
    PrimaryPushButton,
    PushButton,
    TableWidget,
    FluentIcon as FIF,
    InfoBar,
)

from ...services.async_service import AsyncService
from ...api_client import api_client, APIError


class UserManagementInterface(QWidget):
    """用户管理界面"""

    def __init__(self, parent=None):
        """
        初始化用户管理界面

        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.async_service = AsyncService()
        self._setup_ui()
        self._load_users()

    def _setup_ui(self) -> None:
        """设置UI"""
        self.v_layout = QVBoxLayout(self)
        self.v_layout.setContentsMargins(30, 30, 30, 30)

        # 顶部工具栏
        tool_layout = QHBoxLayout()
        self.search_bar = LineEdit(self)
        self.search_bar.setPlaceholderText("搜索用户名或学号...")
        self.search_bar.setFixedWidth(300)
        self.search_bar.returnPressed.connect(self._on_search)
        
        self.btn_add = PrimaryPushButton(FIF.ADD, "添加学生", self)
        self.btn_add.clicked.connect(self._on_add_user)
        
        self.btn_export = PushButton(FIF.DOWNLOAD, "导出数据", self)
        self.btn_export.clicked.connect(self._on_export)

        tool_layout.addWidget(self.search_bar)
        tool_layout.addStretch(1)
        tool_layout.addWidget(self.btn_add)
        tool_layout.addWidget(self.btn_export)

        # 表格
        self.table = TableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['ID', '姓名', '专业', '状态', '操作'])
        self.table.verticalHeader().hide()
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)
        self.table.setWordWrap(False)

        # 设置表头自适应
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.v_layout.addWidget(TitleLabel("学生信息管理", self))
        self.v_layout.addSpacing(10)
        self.v_layout.addLayout(tool_layout)
        self.v_layout.addSpacing(10)
        self.v_layout.addWidget(self.table)

    def _load_users(self) -> None:
        """加载用户列表"""
        def load_func():
            try:
                return api_client.get_admin_users(limit=100, offset=0)
            except APIError as e:
                InfoBar.error("错误", f"加载用户列表失败: {e.message}", duration=2000, parent=self)
                return {"data": [], "total": 0}

        def on_success(result: dict):
            users = result.get("data", [])
            self._update_table(users)

        self.async_service.execute_async(load_func, on_success, lambda e: None)

    def _update_table(self, users: list) -> None:
        """更新表格"""
        self.table.setRowCount(len(users))
        for i, user in enumerate(users):
            self.table.setItem(i, 0, QTableWidgetItem(str(user.get("id", ""))))
            self.table.setItem(i, 1, QTableWidgetItem(user.get("username", "")))
            # 专业信息可能需要从其他字段获取
            self.table.setItem(i, 2, QTableWidgetItem(user.get("dept", "未知")))
            status = "活跃" if user.get("is_active", False) else "禁用"
            self.table.setItem(i, 3, QTableWidgetItem(status))
            # 操作列
            self.table.setItem(i, 4, QTableWidgetItem("编辑 | 删除"))

    def _on_search(self) -> None:
        """搜索"""
        # TODO: 实现搜索功能
        InfoBar.info("提示", "搜索功能待实现", duration=2000, parent=self)

    def _on_add_user(self) -> None:
        """添加用户"""
        # TODO: 实现添加用户功能
        InfoBar.info("提示", "添加用户功能待实现", duration=2000, parent=self)

    def _on_export(self) -> None:
        """导出数据"""
        # TODO: 实现导出功能
        InfoBar.info("提示", "导出功能待实现", duration=2000, parent=self)

