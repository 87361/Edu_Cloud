"""
GUI应用主入口
管理窗口切换和事件循环
"""
import customtkinter as ctk
from typing import Optional
from .views.login_view import LoginView
from .views.assignment_list_view import AssignmentListView
from .views.assignment_detail_view import AssignmentDetailView
from .utils.token_manager import token_manager
from .api_client import api_client

class EduCloudApp(ctk.CTk):
    """教育云应用主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 设置窗口
        self.title("云邮教学空间")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # 设置主题
        ctk.set_appearance_mode("light")  # 可选: "light", "dark", "system"
        ctk.set_default_color_theme("blue")  # 可选: "blue", "green", "dark-blue"
        
        # 当前视图
        self.current_view: Optional[ctk.CTkFrame] = None
        
        # 检查是否已登录
        if token_manager.get_token():
            self.show_assignment_list()
        else:
            self.show_login()
    
    def clear_current_view(self):
        """清除当前视图"""
        if self.current_view:
            self.current_view.destroy()
            self.current_view = None
    
    def show_login(self):
        """显示登录界面"""
        self.clear_current_view()
        
        login_view = LoginView(self, on_login_success=self.on_login_success)
        login_view.grid(row=0, column=0, sticky="nsew")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.current_view = login_view
    
    def show_assignment_list(self):
        """显示作业列表界面"""
        self.clear_current_view()
        
        assignment_list_view = AssignmentListView(
            self,
            on_assignment_click=self.on_assignment_click,
            on_logout=self.on_logout
        )
        assignment_list_view.grid(row=0, column=0, sticky="nsew")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.current_view = assignment_list_view
    
    def show_assignment_detail(self, assignment_id: int):
        """显示作业详情界面"""
        self.clear_current_view()
        
        assignment_detail_view = AssignmentDetailView(
            self,
            assignment_id=assignment_id,
            on_back=self.on_back_to_list
        )
        assignment_detail_view.grid(row=0, column=0, sticky="nsew")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.current_view = assignment_detail_view
    
    def on_login_success(self):
        """登录成功回调"""
        self.show_assignment_list()
    
    def on_logout(self):
        """登出回调"""
        try:
            api_client.logout()
        except:
            pass  # 即使API调用失败，也清除本地Token
        
        token_manager.clear_token()
        self.show_login()
    
    def on_assignment_click(self, assignment_id: int):
        """点击作业项回调"""
        self.show_assignment_detail(assignment_id)
    
    def on_back_to_list(self):
        """返回作业列表回调"""
        self.show_assignment_list()

def main():
    """主函数"""
    app = EduCloudApp()
    app.mainloop()

if __name__ == "__main__":
    main()


