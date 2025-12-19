"""
登录界面
支持本地账号登录和CAS登录
"""
import customtkinter as ctk
import threading
from typing import Callable, Optional
from ..api_client import api_client, APIError

class LoginView(ctk.CTkFrame):
    """登录界面"""
    
    def __init__(self, parent, on_login_success: Callable[[], None]):
        """
        初始化登录界面
        
        Args:
            parent: 父窗口
            on_login_success: 登录成功后的回调函数
        """
        super().__init__(parent)
        self.on_login_success = on_login_success
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI界面"""
        # 主容器
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # 内容框架
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=0, column=0, padx=50, pady=50, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        
        # 标题
        title_label = ctk.CTkLabel(
            content_frame,
            text="云邮教学空间",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(30, 10))
        
        subtitle_label = ctk.CTkLabel(
            content_frame,
            text="请选择登录方式",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        subtitle_label.grid(row=1, column=0, pady=(0, 30))
        
        # 登录方式选择（Tab切换）
        self.login_mode = ctk.StringVar(value="local")
        
        mode_frame = ctk.CTkFrame(content_frame)
        mode_frame.grid(row=2, column=0, pady=(0, 20), sticky="ew")
        mode_frame.grid_columnconfigure(0, weight=1)
        mode_frame.grid_columnconfigure(1, weight=1)
        
        local_radio = ctk.CTkRadioButton(
            mode_frame,
            text="本地账号",
            variable=self.login_mode,
            value="local",
            command=self.on_mode_change
        )
        local_radio.grid(row=0, column=0, padx=20, pady=15)
        
        cas_radio = ctk.CTkRadioButton(
            mode_frame,
            text="CAS登录",
            variable=self.login_mode,
            value="cas",
            command=self.on_mode_change
        )
        cas_radio.grid(row=0, column=1, padx=20, pady=15)
        
        # 输入框框架
        input_frame = ctk.CTkFrame(content_frame)
        input_frame.grid(row=3, column=0, pady=(0, 20), sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1)
        
        # 用户名/学号输入
        username_label = ctk.CTkLabel(input_frame, text="用户名:", width=100, anchor="w")
        username_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        self.username_entry = ctk.CTkEntry(input_frame, placeholder_text="请输入用户名或学号")
        self.username_entry.grid(row=0, column=1, padx=(0, 20), pady=15, sticky="ew")
        
        # 密码输入
        password_label = ctk.CTkLabel(input_frame, text="密码:", width=100, anchor="w")
        password_label.grid(row=1, column=0, padx=20, pady=15, sticky="w")
        
        self.password_entry = ctk.CTkEntry(input_frame, placeholder_text="请输入密码", show="*")
        self.password_entry.grid(row=1, column=1, padx=(0, 20), pady=15, sticky="ew")
        
        # 状态标签
        self.status_label = ctk.CTkLabel(
            content_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="red"
        )
        self.status_label.grid(row=4, column=0, pady=(0, 10))
        
        # 登录按钮
        self.login_button = ctk.CTkButton(
            content_frame,
            text="登录",
            command=self.on_login_click,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40
        )
        self.login_button.grid(row=5, column=0, pady=(0, 20), sticky="ew", padx=20)
        
        # 绑定回车键
        self.username_entry.bind("<Return>", lambda e: self.on_login_click())
        self.password_entry.bind("<Return>", lambda e: self.on_login_click())
        
        # 初始化界面
        self.on_mode_change()
    
    def on_mode_change(self):
        """切换登录模式时的回调"""
        mode = self.login_mode.get()
        if mode == "local":
            self.username_entry.configure(placeholder_text="请输入用户名")
        else:
            self.username_entry.configure(placeholder_text="请输入学号（CAS账号）")
        self.clear_status()
    
    def clear_status(self):
        """清除状态信息"""
        self.status_label.configure(text="")
    
    def set_status(self, message: str, is_error: bool = True):
        """设置状态信息"""
        color = "red" if is_error else "green"
        self.status_label.configure(text=message, text_color=color)
    
    def on_login_click(self):
        """登录按钮点击事件"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            self.set_status("请输入用户名和密码")
            return
        
        # 禁用登录按钮，显示加载状态
        self.login_button.configure(state="disabled", text="登录中...")
        self.clear_status()
        
        # 在后台线程中执行登录，避免阻塞GUI
        def do_login():
            try:
                if self.login_mode.get() == "local":
                    response = api_client.login(username, password)
                else:
                    response = api_client.login_cas(username, password)
                
                # 登录成功，在主线程中更新UI
                self.after(0, lambda: self._on_login_success())
            
            except APIError as e:
                error_msg = e.message
                self.after(0, lambda msg=error_msg: self._on_login_error(msg))
            
            except Exception as e:
                error_msg = str(e)
                self.after(0, lambda msg=error_msg: self._on_login_error(msg))
        
        # 启动后台线程
        thread = threading.Thread(target=do_login, daemon=True)
        thread.start()
    
    def _on_login_success(self):
        """登录成功回调（在主线程中执行）"""
        self.set_status("登录成功！", is_error=False)
        self.after(500, self.on_login_success)  # 延迟500ms后跳转
    
    def _on_login_error(self, error_msg: str):
        """登录失败回调（在主线程中执行）"""
        self.set_status(f"登录失败: {error_msg}")
        self.login_button.configure(state="normal", text="登录")


