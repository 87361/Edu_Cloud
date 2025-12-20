"""
作业列表界面
显示所有作业，支持筛选、排序和同步功能
"""
import customtkinter as ctk
import threading
from datetime import datetime
from typing import Callable, Optional, List, Dict, Any
from ..api_client import api_client, APIError

class AssignmentListViewModel:
    """作业列表视图模型"""
    
    def __init__(self):
        self.assignments: List[Dict[str, Any]] = []
        self.filter_status: Optional[str] = None  # None, "pending", "submitted"
        self.sort_by: str = "deadline"  # "deadline", "course", "title"
    
    def set_assignments(self, assignments: List[Dict[str, Any]]):
        """设置作业列表"""
        self.assignments = assignments
    
    def get_filtered_assignments(self) -> List[Dict[str, Any]]:
        """获取筛选后的作业列表"""
        filtered = self.assignments
        
        # 过滤掉无效的课程名称（未分类、待办事项、未知课程等）
        filtered = [
            a for a in filtered 
            if a.get("course_name") 
            and "未分类" not in a.get("course_name", "") 
            and "待办事项" not in a.get("course_name", "")
            and a.get("course_name") != "未知课程"
        ]
        
        # 状态筛选
        if self.filter_status == "pending":
            filtered = [a for a in filtered if a.get("status") == "未提交"]
        elif self.filter_status == "submitted":
            filtered = [a for a in filtered if a.get("status") == "已提交"]
        
        # 排序
        if self.sort_by == "deadline":
            filtered.sort(key=lambda x: self._parse_deadline(x.get("deadline", "")), reverse=True)
        elif self.sort_by == "course":
            filtered.sort(key=lambda x: x.get("course_name", ""))
        elif self.sort_by == "title":
            filtered.sort(key=lambda x: x.get("title", ""))
        
        return filtered
    
    def _parse_deadline(self, deadline_str: str) -> datetime:
        """解析截止时间字符串"""
        try:
            if deadline_str and deadline_str != "无截止日期":
                return datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
        except:
            pass
        return datetime.min

class AssignmentListWidget(ctk.CTkFrame):
    """作业项组件"""
    
    def __init__(self, parent, assignment: Dict[str, Any], on_click: Callable[[int], None]):
        super().__init__(parent)
        self.assignment = assignment
        self.on_click = on_click
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.grid_columnconfigure(0, weight=1)
        
        # 主容器（可点击）
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        container.grid_columnconfigure(1, weight=1)
        container.bind("<Button-1>", lambda e: self.on_click(self.assignment["id"]))
        
        # 状态指示器
        status = self.assignment.get("status", "未提交")
        status_color = "#10b981" if status == "已提交" else "#ef4444"
        status_dot = ctk.CTkLabel(
            container,
            text="●",
            font=ctk.CTkFont(size=20),
            text_color=status_color,
            width=20
        )
        status_dot.grid(row=0, column=0, padx=(10, 5), pady=10)
        
        # 作业信息
        info_frame = ctk.CTkFrame(container, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="ew", padx=5)
        info_frame.grid_columnconfigure(0, weight=1)
        
        # 课程名和标题
        title_text = f"{self.assignment.get('course_name', '未知课程')} - {self.assignment.get('title', '无标题')}"
        title_label = ctk.CTkLabel(
            info_frame,
            text=title_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="ew", pady=(5, 0))
        
        # 截止时间和分数
        deadline = self.assignment.get("deadline", "无截止日期")
        if deadline != "无截止日期":
            try:
                dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                deadline = dt.strftime("%Y-%m-%d %H:%M")
            except:
                pass
        
        score = self.assignment.get("score") or "未评分"
        info_text = f"截止: {deadline} | 分数: {score}"
        info_label = ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w"
        )
        info_label.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        
        # 状态标签
        status_label = ctk.CTkLabel(
            container,
            text=status,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=status_color,
            width=80
        )
        status_label.grid(row=0, column=2, padx=10, pady=10)
        
        # 绑定点击事件到所有子组件
        for widget in [container, status_dot, info_frame, title_label, info_label, status_label]:
            widget.bind("<Button-1>", lambda e: self.on_click(self.assignment["id"]))
            if hasattr(widget, "configure"):
                widget.configure(cursor="hand2")

class AssignmentListView(ctk.CTkFrame):
    """作业列表界面"""
    
    def __init__(
        self,
        parent,
        on_assignment_click: Callable[[int], None],
        on_logout: Callable[[], None]
    ):
        """
        初始化作业列表界面
        
        Args:
            parent: 父窗口
            on_assignment_click: 点击作业项的回调函数
            on_logout: 登出回调函数
        """
        super().__init__(parent)
        self.on_assignment_click = on_assignment_click
        self.on_logout = on_logout
        self.view_model = AssignmentListViewModel()
        self.user_info: Optional[Dict[str, Any]] = None
        self.setup_ui()
        self.load_user_info()
        self.refresh_assignments()
    
    def setup_ui(self):
        """设置UI界面"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # 顶部工具栏
        toolbar = ctk.CTkFrame(self)
        toolbar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        toolbar.grid_columnconfigure(1, weight=1)
        
        # 左侧按钮组
        left_buttons = ctk.CTkFrame(toolbar, fg_color="transparent")
        left_buttons.grid(row=0, column=0, padx=10, pady=10)
        
        sync_button = ctk.CTkButton(
            left_buttons,
            text="同步作业",
            command=self.on_sync_click,
            width=100
        )
        sync_button.pack(side="left", padx=5)
        
        refresh_button = ctk.CTkButton(
            left_buttons,
            text="刷新",
            command=self.refresh_assignments,
            width=100
        )
        refresh_button.pack(side="left", padx=5)
        
        # 中间筛选和排序
        filter_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        filter_frame.grid(row=0, column=1, padx=10, pady=10)
        
        filter_label = ctk.CTkLabel(filter_frame, text="筛选:")
        filter_label.pack(side="left", padx=5)
        
        self.filter_var = ctk.StringVar(value="all")
        filter_all = ctk.CTkRadioButton(
            filter_frame,
            text="全部",
            variable=self.filter_var,
            value="all",
            command=self.on_filter_change
        )
        filter_all.pack(side="left", padx=5)
        
        filter_pending = ctk.CTkRadioButton(
            filter_frame,
            text="未提交",
            variable=self.filter_var,
            value="pending",
            command=self.on_filter_change
        )
        filter_pending.pack(side="left", padx=5)
        
        filter_submitted = ctk.CTkRadioButton(
            filter_frame,
            text="已提交",
            variable=self.filter_var,
            value="submitted",
            command=self.on_filter_change
        )
        filter_submitted.pack(side="left", padx=5)
        
        # 右侧用户信息和登出
        right_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        right_frame.grid(row=0, column=2, padx=10, pady=10)
        
        self.user_label = ctk.CTkLabel(right_frame, text="加载中...")
        self.user_label.pack(side="left", padx=10)
        
        logout_button = ctk.CTkButton(
            right_frame,
            text="登出",
            command=self.on_logout,
            width=80,
            fg_color="#ef4444",
            hover_color="#dc2626"
        )
        logout_button.pack(side="left", padx=5)
        
        # 作业列表（可滚动）
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # 状态标签
        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.status_label.grid(row=2, column=0, pady=5)
    
    def on_filter_change(self):
        """筛选条件改变"""
        filter_value = self.filter_var.get()
        self.view_model.filter_status = None if filter_value == "all" else filter_value
        self.update_assignment_list()
    
    def load_user_info(self):
        """加载用户信息（在后台线程执行）"""
        def do_load():
            try:
                response = api_client.get_user_info()
                user_info = response.get("data", {})
                username = user_info.get("username", "未知用户")
                self.after(0, lambda: self._update_user_info(username))
            except Exception as e:
                self.after(0, lambda: self.user_label.configure(text="用户信息加载失败"))
        
        thread = threading.Thread(target=do_load, daemon=True)
        thread.start()
    
    def _update_user_info(self, username: str):
        """更新用户信息显示（在主线程中执行）"""
        self.user_label.configure(text=f"用户: {username}")
    
    def refresh_assignments(self):
        """刷新作业列表（在后台线程执行）"""
        self.status_label.configure(text="加载中...", text_color="gray")
        
        def do_refresh():
            try:
                assignments = api_client.get_assignments()
                self.after(0, lambda: self._on_refresh_success(assignments))
            except APIError as e:
                error_msg = e.message
                self.after(0, lambda msg=error_msg: self._on_refresh_error(msg))
            except Exception as e:
                error_msg = str(e)
                self.after(0, lambda msg=error_msg: self._on_refresh_error(msg))
        
        thread = threading.Thread(target=do_refresh, daemon=True)
        thread.start()
    
    def _on_refresh_success(self, assignments: List[Dict[str, Any]]):
        """刷新成功回调（在主线程中执行）"""
        self.view_model.set_assignments(assignments)
        self.update_assignment_list()
        count = len(assignments)
        self.status_label.configure(
            text=f"共 {count} 个作业",
            text_color="gray"
        )
    
    def _on_refresh_error(self, error_msg: str):
        """刷新失败回调（在主线程中执行）"""
        self.status_label.configure(
            text=f"加载失败: {error_msg}",
            text_color="red"
        )
    
    def update_assignment_list(self):
        """更新作业列表显示"""
        # 清除现有组件
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # 获取筛选后的作业
        assignments = self.view_model.get_filtered_assignments()
        
        if not assignments:
            empty_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="暂无作业",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            )
            empty_label.grid(row=0, column=0, pady=50)
            return
        
        # 显示作业列表
        for idx, assignment in enumerate(assignments):
            widget = AssignmentListWidget(
                self.scrollable_frame,
                assignment,
                self.on_assignment_click
            )
            widget.grid(row=idx, column=0, sticky="ew", padx=5, pady=5)
    
    def on_sync_click(self):
        """同步作业按钮点击"""
        # 创建同步对话框
        dialog = SyncDialog(self, self.on_sync_confirm)
        dialog.focus()
    
    def on_sync_confirm(self, school_username: str, school_password: str):
        """确认同步作业（在后台线程执行）"""
        self.status_label.configure(text="同步中，请稍候...", text_color="blue")
        
        def do_sync():
            try:
                response = api_client.sync_assignments(school_username, school_password)
                msg = response.get("msg", "同步完成")
                new_count = response.get("new_added", 0)
                total = response.get("total_synced", 0)
                
                self.after(0, lambda: self._on_sync_success(msg, new_count, total))
            
            except APIError as e:
                error_msg = e.message
                self.after(0, lambda msg=error_msg: self._on_sync_error(msg))
            except Exception as e:
                error_msg = str(e)
                self.after(0, lambda msg=error_msg: self._on_sync_error(msg))
        
        # 启动后台线程执行同步操作
        thread = threading.Thread(target=do_sync, daemon=True)
        thread.start()
    
    def _on_sync_success(self, msg: str, new_count: int, total: int):
        """同步成功回调（在主线程中执行）"""
        self.status_label.configure(
            text=f"{msg} (新增: {new_count}, 总计: {total})",
            text_color="green"
        )
        # 刷新列表
        self.refresh_assignments()
    
    def _on_sync_error(self, error_msg: str):
        """同步失败回调（在主线程中执行）"""
        self.status_label.configure(
            text=f"同步失败: {error_msg}",
            text_color="red"
        )

class SyncDialog(ctk.CTkToplevel):
    """同步作业对话框"""
    
    def __init__(self, parent, on_confirm: Callable[[str, str], None]):
        super().__init__(parent)
        self.on_confirm = on_confirm
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.title("同步作业")
        self.geometry("400x200")
        self.resizable(False, False)
        
        # 居中显示
        self.transient(self.master)
        # 延迟设置grab，确保窗口已显示
        self.after(100, self.grab_set)
        
        self.grid_columnconfigure(0, weight=1)
        
        # 说明文字
        info_label = ctk.CTkLabel(
            self,
            text="请输入学校账号信息以同步作业",
            font=ctk.CTkFont(size=14)
        )
        info_label.grid(row=0, column=0, pady=20)
        
        # 输入框
        input_frame = ctk.CTkFrame(self)
        input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1)
        
        username_label = ctk.CTkLabel(input_frame, text="学号:", width=80, anchor="w")
        username_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.username_entry = ctk.CTkEntry(input_frame)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        password_label = ctk.CTkLabel(input_frame, text="密码:", width=80, anchor="w")
        password_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        self.password_entry = ctk.CTkEntry(input_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # 按钮
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=2, column=0, pady=20)
        
        confirm_button = ctk.CTkButton(
            button_frame,
            text="确认",
            command=self.on_confirm_click,
            width=100
        )
        confirm_button.pack(side="left", padx=10)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="取消",
            command=self.destroy,
            width=100,
            fg_color="gray",
            hover_color="darkgray"
        )
        cancel_button.pack(side="left", padx=10)
        
        # 绑定回车键
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.on_confirm_click())
        self.username_entry.focus()
    
    def on_confirm_click(self):
        """确认按钮点击"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            return
        
        self.on_confirm(username, password)
        self.destroy()

