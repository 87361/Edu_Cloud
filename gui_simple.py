import customtkinter as ctk
from tkinter import messagebox
import platform

def get_font_family():
    """根据操作系统获取合适的首选字体"""
    system = platform.system()
    if system == "Windows":
        return "Microsoft YaHei UI"
    elif system == "Darwin":  # macOS
        return "PingFang SC"
    else:  # Linux/Other
        return "WenQuanYi Micro Hei"

# 全局字体变量
FONT_FAMILY = get_font_family()

# 标题字体
FONT_TITLE = (FONT_FAMILY, 24, "bold")
# 卡片/副标题字体
FONT_CARD_TITLE = (FONT_FAMILY, 18, "bold")
# 正文/普通字体
FONT_NORMAL = (FONT_FAMILY, 14)
# 小字体
FONT_SMALL = (FONT_FAMILY, 12)

def get_system_font():
    sys_name = platform.system()
    if sys_name == "Windows":
        return "Microsoft YaHei UI"
    elif sys_name == "Darwin":
        return "PingFang SC"
    return "SimHei"  # Linux 兜底

# 定义全局字体常量
APP_FONT = get_system_font()

# 设置外观模式和默认颜色主题
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

class CourseCard(ctk.CTkFrame):
    """
    自定义组件：课程卡片
    用于在主页瀑布流中展示单个课程信息
    """
    def __init__(self, master, title, teacher, progress, color, **kwargs):
        super().__init__(master, **kwargs)
        
        # 卡片样式设置
        self.configure(fg_color="#2b2b2b", corner_radius=15, border_width=1, border_color="#3a3a3a")

        # 1. 顶部颜色条 (装饰用)
        self.header_bar = ctk.CTkFrame(self, height=10, corner_radius=5, fg_color=color)
        self.header_bar.pack(fill="x", padx=10, pady=(10, 5))

        # 2. 课程标题
        self.title_label = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=18, weight="bold"), anchor="w")
        self.title_label.pack(fill="x", padx=15, pady=5)

        # 3. 讲师信息
        self.teacher_label = ctk.CTkLabel(self, text=f"讲师: {teacher}", font=ctk.CTkFont(size=12), text_color="gray", anchor="w")
        self.teacher_label.pack(fill="x", padx=15, pady=0)

        # 4. 进度条区域
        self.progress_label = ctk.CTkLabel(self, text=f"进度: {int(progress*100)}%", font=ctk.CTkFont(size=12), anchor="e")
        self.progress_label.pack(fill="x", padx=15, pady=(10, 0))
        
        self.progress_bar = ctk.CTkProgressBar(self, height=8, progress_color=color)
        self.progress_bar.set(progress)
        self.progress_bar.pack(fill="x", padx=15, pady=(5, 15))


class StudentApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 窗口基础设置 ---
        self.title("Student Space - 课业管理")
        self.geometry("1100x700")
        
        # 定义网格布局: 1行2列
        # column 0 (sidebar) 宽度较小, column 1 (content) 宽度自适应
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- 数据模拟 ---
        self.courses_data = [
            {"title": "高等数学 (Calculus)", "teacher": "Dr. Wang", "progress": 0.75, "color": "#1f6aa5"},
            {"title": "计算机科学导论", "teacher": "Prof. Smith", "progress": 0.4, "color": "#2cc985"},
            {"title": "线性代数", "teacher": "Dr. Li", "progress": 0.9, "color": "#a51f1f"},
            {"title": "Python 编程实战", "teacher": "Guido", "progress": 0.2, "color": "#e0a71f"},
            {"title": "大学物理", "teacher": "Newton", "progress": 0.5, "color": "#8c1fa5"},
            {"title": "Web 前端设计", "teacher": "Mozilla", "progress": 0.6, "color": "#1fa598"},
        ]

        self.assignments_data = [
            {"id": 1, "course": "高等数学", "task": "微积分习题集 Chapter 3", "ddl": "2023-10-25", "desc": "完成第3章关于导数应用的所有偶数题。\n请拍照上传或扫描PDF。"},
            {"id": 2, "course": "计算机科学", "task": "Lab 2: 二进制转换", "ddl": "2023-10-26", "desc": "编写一个程序，实现十进制与二进制的互转。\n提交 .py 文件。"},
            {"id": 3, "course": "Python 编程", "task": "爬虫大作业", "ddl": "2023-11-01", "desc": "爬取任意新闻网站的前10条新闻标题。\n注意遵守robots.txt协议。"},
            {"id": 4, "course": "大学物理", "task": "牛顿定律实验报告", "ddl": "2023-11-05", "desc": "撰写关于滑块摩擦力的实验报告。\n格式要求：IEEE标准。"}
        ]

        # --- 初始化界面组件 ---
        self.create_sidebar()
        self.create_main_area()
        self.show_home()
        
        # 初始显示主页
        self.show_home()

    def create_sidebar(self):
        """创建左侧边栏"""
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        # Logo 字体
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Student Space", 
                                       font=(APP_FONT, 24, "bold")) # <--- 这里
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # 按钮字体
        self.home_btn = ctk.CTkButton(self.sidebar_frame, text="我的课程 (Dashboard)", 
                                      fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"),
                                      font=(APP_FONT, 14, "bold"),  # <--- 这里
                                      command=self.show_home)
        self.home_btn.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.divider = ctk.CTkFrame(self.sidebar_frame, height=2, fg_color="gray")
        self.divider.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.hw_label = ctk.CTkLabel(self.sidebar_frame, text="待办作业 (To-Do)", anchor="w", 
                                     font=(APP_FONT, 14, "bold"))   # <--- 这里
        self.hw_label.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="ew")

        self.hw_scroll_frame = ctk.CTkScrollableFrame(self.sidebar_frame, label_text="")
        self.hw_scroll_frame.grid(row=4, column=0, padx=20, pady=10, sticky="nsew")

        for task in self.assignments_data:
            btn = ctk.CTkButton(
                self.hw_scroll_frame, 
                text=f"{task['course']}\n{task['task']}", 
                height=50,
                anchor="w",
                fg_color="#333333",
                hover_color="#444444",
                font=(APP_FONT, 13), # <--- 这里
                command=lambda t=task: self.show_assignment_detail(t)
            )
            btn.pack(pady=5, fill="x")

    def create_main_area(self):
        """创建右侧主区域（包含主页和详情页两个容器）"""
        # 容器 1: 课程瀑布流主页 (使用 ScrollableFrame)
        self.home_frame = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)
        self.home_frame.grid_columnconfigure(1, weight=1)

        for i, course in enumerate(self.courses_data):
            card = CourseCard(self.home_frame, title=course["title"], teacher=course["teacher"], progress=course["progress"], color=course["color"])
            row = i // 2
            col = i % 2
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        self.detail_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.detail_frame.grid_columnconfigure(0, weight=1)

        self.detail_header = ctk.CTkFrame(self.detail_frame, height=100, corner_radius=10, fg_color="#4a4a4a")
        self.detail_header.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        # 详情页字体
        self.detail_title = ctk.CTkLabel(self.detail_header, text="Task Title", 
                                         font=(APP_FONT, 26, "bold")) # <--- 这里
        self.detail_title.place(relx=0.05, rely=0.3)
        self.detail_subtitle = ctk.CTkLabel(self.detail_header, text="Info", 
                                            font=(APP_FONT, 14))      # <--- 这里
        self.detail_subtitle.place(relx=0.05, rely=0.65)

        self.desc_label = ctk.CTkLabel(self.detail_frame, text="作业描述 / Description:", anchor="w", 
                                       font=(APP_FONT, 16, "bold"))   # <--- 这里
        self.desc_label.grid(row=1, column=0, padx=25, pady=(10,5), sticky="w")

        # 文本框字体 (很重要，否则输入中文很丑)
        self.desc_textbox = ctk.CTkTextbox(self.detail_frame, height=150, corner_radius=10, fg_color="#2b2b2b",
                                           font=(APP_FONT, 14))       # <--- 这里
        self.desc_textbox.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.desc_textbox.configure(state="disabled")

        self.submit_label = ctk.CTkLabel(self.detail_frame, text="你的答案 / Submission:", anchor="w", 
                                         font=(APP_FONT, 16, "bold")) # <--- 这里
        self.submit_label.grid(row=3, column=0, padx=25, pady=(10,5), sticky="w")

        self.submit_textbox = ctk.CTkTextbox(self.detail_frame, height=200, corner_radius=10,
                                             font=(APP_FONT, 14))     # <--- 这里
        self.submit_textbox.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="ew")

        self.submit_btn = ctk.CTkButton(self.detail_frame, text="提交作业 (Submit)", height=45, 
                                        fg_color="#1f6aa5", hover_color="#144870",
                                        font=(APP_FONT, 15, "bold"),  # <--- 这里
                                        command=self.submit_action)
        self.submit_btn.grid(row=5, column=0, padx=20, pady=10, sticky="e")

    def show_home(self):
        """切换到主页视图"""
        self.detail_frame.grid_forget() # 隐藏详情页
        self.home_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20) # 显示主页
        
        # 更新侧边栏按钮状态 (视觉反馈)
        self.home_btn.configure(fg_color=("gray75", "gray25")) 

    def show_assignment_detail(self, task_data):
        """切换到详情页视图并填充数据"""
        self.home_frame.grid_forget() # 隐藏主页
        self.detail_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20) # 显示详情页

        # 视觉反馈：重置主页按钮颜色
        self.home_btn.configure(fg_color="transparent")

        # --- 填充数据 ---
        self.detail_title.configure(text=task_data["task"])
        self.detail_subtitle.configure(text=f"{task_data['course']}  |  截止日期: {task_data['ddl']}")
        
        # 更新描述文本 (先启用编辑，写入后禁用)
        self.desc_textbox.configure(state="normal")
        self.desc_textbox.delete("0.0", "end")
        self.desc_textbox.insert("0.0", task_data["desc"])
        self.desc_textbox.configure(state="disabled")

        # 清空提交区域
        self.submit_textbox.delete("0.0", "end")

    def submit_action(self):
        content = self.submit_textbox.get("0.0", "end").strip()
        if not content:
            messagebox.showwarning("提示", "提交内容不能为空！")
        else:
            messagebox.showinfo("成功", "作业已提交！\n(此为演示)")
            self.show_home() # 提交后返回主页

if __name__ == "__main__":
    app = StudentApp()
    app.mainloop()