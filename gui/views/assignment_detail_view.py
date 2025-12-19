"""
作业详情界面
显示作业详细信息，支持文件上传和提交
"""
import customtkinter as ctk
import threading
from tkinter import filedialog
from datetime import datetime
from typing import Callable, Optional, Dict, Any
from pathlib import Path
from ..api_client import api_client, APIError

class AssignmentDetailView(ctk.CTkFrame):
    """作业详情界面"""
    
    def __init__(
        self,
        parent,
        assignment_id: int,
        on_back: Callable[[], None]
    ):
        """
        初始化作业详情界面
        
        Args:
            parent: 父窗口
            assignment_id: 作业ID
            on_back: 返回按钮回调函数
        """
        super().__init__(parent)
        self.assignment_id = assignment_id
        self.on_back = on_back
        self.selected_file: Optional[str] = None
        self.assignment: Optional[Dict[str, Any]] = None
        self.setup_ui()
        self.load_assignment()
    
    def setup_ui(self):
        """设置UI界面"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # 顶部工具栏
        toolbar = ctk.CTkFrame(self)
        toolbar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        toolbar.grid_columnconfigure(1, weight=1)
        
        back_button = ctk.CTkButton(
            toolbar,
            text="← 返回",
            command=self.on_back,
            width=100
        )
        back_button.grid(row=0, column=0, padx=10, pady=10)
        
        title_label = ctk.CTkLabel(
            toolbar,
            text="作业详情",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=1, padx=10, pady=10)
        
        # 主内容区域（可滚动）
        scrollable_frame = ctk.CTkScrollableFrame(self)
        scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # 作业信息框架
        info_frame = ctk.CTkFrame(scrollable_frame)
        info_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        info_frame.grid_columnconfigure(0, weight=1)
        
        # 标题
        self.title_label = ctk.CTkLabel(
            info_frame,
            text="加载中...",
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w"
        )
        self.title_label.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        # 课程名和状态
        self.meta_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        self.meta_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        self.course_label = ctk.CTkLabel(
            self.meta_frame,
            text="课程: 加载中...",
            font=ctk.CTkFont(size=14),
            anchor="w"
        )
        self.course_label.pack(side="left", padx=5)
        
        self.status_label = ctk.CTkLabel(
            self.meta_frame,
            text="状态: 加载中...",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        self.status_label.pack(side="left", padx=20)
        
        # 截止时间
        self.deadline_label = ctk.CTkLabel(
            info_frame,
            text="截止时间: 加载中...",
            font=ctk.CTkFont(size=14),
            anchor="w",
            text_color="red"
        )
        self.deadline_label.grid(row=2, column=0, sticky="ew", padx=20, pady=5)
        
        # 分数
        self.score_label = ctk.CTkLabel(
            info_frame,
            text="分数: 加载中...",
            font=ctk.CTkFont(size=14),
            anchor="w"
        )
        self.score_label.grid(row=3, column=0, sticky="ew", padx=20, pady=5)
        
        # 分隔线
        separator = ctk.CTkFrame(info_frame, height=2, fg_color="gray")
        separator.grid(row=4, column=0, sticky="ew", padx=20, pady=10)
        
        # 作业描述
        desc_title = ctk.CTkLabel(
            info_frame,
            text="作业描述:",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        desc_title.grid(row=5, column=0, sticky="ew", padx=20, pady=(10, 5))
        
        self.description_text = ctk.CTkTextbox(
            info_frame,
            height=150,
            wrap="word",
            state="disabled"
        )
        self.description_text.grid(row=6, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # 提交区域
        submit_frame = ctk.CTkFrame(scrollable_frame)
        submit_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        submit_frame.grid_columnconfigure(0, weight=1)
        
        submit_title = ctk.CTkLabel(
            submit_frame,
            text="提交作业",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        submit_title.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        # 文件选择区域
        file_frame = ctk.CTkFrame(submit_frame)
        file_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        file_frame.grid_columnconfigure(1, weight=1)
        
        file_label = ctk.CTkLabel(
            file_frame,
            text="选择文件:",
            width=100,
            anchor="w"
        )
        file_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.file_path_label = ctk.CTkLabel(
            file_frame,
            text="未选择文件",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w"
        )
        self.file_path_label.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        select_button = ctk.CTkButton(
            file_frame,
            text="浏览...",
            command=self.on_select_file,
            width=100
        )
        select_button.grid(row=0, column=2, padx=10, pady=10)
        
        # 提交按钮
        button_frame = ctk.CTkFrame(submit_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, pady=20)
        
        self.submit_button = ctk.CTkButton(
            button_frame,
            text="提交作业",
            command=self.on_submit_click,
            width=150,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#10b981",
            hover_color="#059669"
        )
        self.submit_button.pack(side="left", padx=10)
        
        # 状态标签
        self.status_message_label = ctk.CTkLabel(
            submit_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.status_message_label.grid(row=3, column=0, pady=10)
    
    def load_assignment(self):
        """加载作业详情（在后台线程执行）"""
        def do_load():
            try:
                assignments = api_client.get_assignments()
                assignment = next((a for a in assignments if a["id"] == self.assignment_id), None)
                
                if not assignment:
                    self.after(0, lambda: self.title_label.configure(text="作业不存在"))
                    return
                
                self.after(0, lambda: self._on_load_success(assignment))
            
            except APIError as e:
                error_msg = e.message
                self.after(0, lambda msg=error_msg: self.title_label.configure(text=f"加载失败: {msg}"))
            except Exception as e:
                error_msg = str(e)
                self.after(0, lambda msg=error_msg: self.title_label.configure(text=f"加载失败: {msg}"))
        
        thread = threading.Thread(target=do_load, daemon=True)
        thread.start()
    
    def _on_load_success(self, assignment: Dict[str, Any]):
        """加载成功回调（在主线程中执行）"""
        self.assignment = assignment
        self.update_ui()
    
    def update_ui(self):
        """更新UI显示"""
        if not self.assignment:
            return
        
        # 标题
        self.title_label.configure(text=self.assignment.get("title", "无标题"))
        
        # 课程名
        course_name = self.assignment.get("course_name", "未知课程")
        self.course_label.configure(text=f"课程: {course_name}")
        
        # 状态
        status = self.assignment.get("status", "未提交")
        status_color = "#10b981" if status == "已提交" else "#ef4444"
        self.status_label.configure(
            text=f"状态: {status}",
            text_color=status_color
        )
        
        # 截止时间
        deadline = self.assignment.get("deadline", "无截止日期")
        if deadline != "无截止日期":
            try:
                dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                deadline_str = dt.strftime("%Y-%m-%d %H:%M")
                # 检查是否已过期
                if dt < datetime.now(dt.tzinfo):
                    deadline_str += " (已过期)"
            except:
                deadline_str = deadline
        else:
            deadline_str = deadline
        
        self.deadline_label.configure(text=f"截止时间: {deadline_str}")
        
        # 分数
        score = self.assignment.get("score") or "未评分"
        self.score_label.configure(text=f"分数: {score}")
        
        # 描述
        description = self.assignment.get("description", "无描述")
        self.description_text.configure(state="normal")
        self.description_text.delete("1.0", "end")
        self.description_text.insert("1.0", description)
        self.description_text.configure(state="disabled")
        
        # 如果已提交，禁用提交按钮
        if status == "已提交":
            self.submit_button.configure(
                state="disabled",
                text="已提交",
                fg_color="gray"
            )
    
    def on_select_file(self):
        """选择文件"""
        file_path = filedialog.askopenfilename(
            title="选择作业文件",
            filetypes=[("ZIP文件", "*.zip"), ("所有文件", "*.*")]
        )
        
        if file_path:
            self.selected_file = file_path
            file_name = Path(file_path).name
            self.file_path_label.configure(
                text=file_name,
                text_color="white"
            )
            self.status_message_label.configure(text="")
    
    def on_submit_click(self):
        """提交作业按钮点击"""
        if not self.selected_file:
            self.status_message_label.configure(
                text="请先选择要提交的文件",
                text_color="red"
            )
            return
        
        # 检查文件是否存在
        if not Path(self.selected_file).exists():
            self.status_message_label.configure(
                text="文件不存在，请重新选择",
                text_color="red"
            )
            return
        
        # 确认对话框
        confirm = ctk.CTkToplevel(self)
        confirm.title("确认提交")
        confirm.geometry("400x150")
        confirm.resizable(False, False)
        confirm.transient(self.master)
        confirm.grab_set()
        
        file_name = Path(self.selected_file).name
        confirm_label = ctk.CTkLabel(
            confirm,
            text=f"确认提交文件:\n{file_name}\n\n此操作不可撤销",
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        confirm_label.pack(pady=20)
        
        button_frame = ctk.CTkFrame(confirm, fg_color="transparent")
        button_frame.pack(pady=10)
        
        def do_submit():
            confirm.destroy()
            self.submit_file()
        
        yes_button = ctk.CTkButton(
            button_frame,
            text="确认",
            command=do_submit,
            width=100,
            fg_color="#10b981"
        )
        yes_button.pack(side="left", padx=10)
        
        no_button = ctk.CTkButton(
            button_frame,
            text="取消",
            command=confirm.destroy,
            width=100,
            fg_color="gray"
        )
        no_button.pack(side="left", padx=10)
    
    def submit_file(self):
        """提交文件（在后台线程执行）"""
        self.submit_button.configure(state="disabled", text="提交中...")
        self.status_message_label.configure(
            text="正在提交，请稍候...",
            text_color="blue"
        )
        
        def do_submit():
            try:
                # 尝试调用提交API
                response = api_client.submit_assignment(self.assignment_id, self.selected_file)
                self.after(0, lambda: self._on_submit_success())
            
            except APIError as e:
                if e.status_code == 404:
                    self.after(0, lambda: self._on_submit_error(
                        "提示: 后端提交接口尚未实现，文件已选择但未上传",
                        is_warning=True
                    ))
                else:
                    error_msg = e.message
                    self.after(0, lambda msg=error_msg: self._on_submit_error(msg))
            except Exception as e:
                error_msg = str(e)
                self.after(0, lambda msg=error_msg: self._on_submit_error(msg))
        
        thread = threading.Thread(target=do_submit, daemon=True)
        thread.start()
    
    def _on_submit_success(self):
        """提交成功回调（在主线程中执行）"""
        self.status_message_label.configure(
            text="提交成功！",
            text_color="green"
        )
        # 刷新作业信息
        self.after(1000, self.load_assignment)
    
    def _on_submit_error(self, error_msg: str, is_warning: bool = False):
        """提交失败回调（在主线程中执行）"""
        color = "orange" if is_warning else "red"
        self.status_message_label.configure(
            text=f"提交失败: {error_msg}" if not is_warning else error_msg,
            text_color=color
        )
        self.submit_button.configure(state="normal", text="提交作业")


