import sys
from PyQt6.QtCore import Qt, pyqtSignal, QUrl, QSize, QTimer
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QFrame, QTableWidgetItem, QHeaderView, QGraphicsDropShadowEffect)
from PyQt6.QtGui import QColor, QIcon, QAction

# 引入 Fluent Widgets 全套组件
from qfluentwidgets import (
    FluentWindow, SplitFluentWindow, SubtitleLabel, TitleLabel, BodyLabel, 
    CaptionLabel, CardWidget, ElevatedCardWidget, ImageLabel,
    PrimaryPushButton, PushButton, LineEdit, CheckBox, 
    HyperlinkButton, SwitchButton, TableWidget, InfoBar,
    ProgressBar, IndeterminateProgressBar, IconWidget,
    FluentIcon as FIF, setTheme, Theme, qconfig,
    ToggleToolButton, DropDownToolButton
)
from qfluentwidgets import FluentIcon as FIF

# --- 自定义组件：数据统计卡片 ---
class StatCard(ElevatedCardWidget):
    """
    后台首页的数据统计卡片
    显示：图标 + 数值 + 标题 + 增长率
    """
    def __init__(self, icon, title, value, growth, color="#0078D4", parent=None):
        super().__init__(parent)
        self.setFixedSize(220, 140)
        
        # 布局
        self.v_layout = QVBoxLayout(self)
        self.v_layout.setContentsMargins(20, 20, 20, 20)
        
        # 顶部：图标 + 增长率
        top_layout = QHBoxLayout()
        self.icon_widget = IconWidget(icon, self)
        self.icon_widget.setFixedSize(24, 24)
        # 简单的图标着色逻辑（实际可用 qfluentwidgets 的着色方法）
        
        self.growth_lbl = CaptionLabel(growth, self)
        if "+" in growth:
            self.growth_lbl.setTextColor(QColor("#107C10"), QColor("#107C10")) # 绿色
        else:
            self.growth_lbl.setTextColor(QColor("#E81123"), QColor("#E81123")) # 红色
            
        top_layout.addWidget(self.icon_widget)
        top_layout.addStretch(1)
        top_layout.addWidget(self.growth_lbl)
        
        # 中间：数值
        self.value_lbl = TitleLabel(value, self)
        self.value_lbl.setStyleSheet("font-size: 32px; font-weight: bold;")
        
        # 底部：标题
        self.title_lbl = BodyLabel(title, self)
        self.title_lbl.setTextColor(QColor(120,120,120), QColor(160,160,160))
        
        self.v_layout.addLayout(top_layout)
        self.v_layout.addWidget(self.value_lbl)
        self.v_layout.addWidget(self.title_lbl)

# --- 界面 1：后台仪表盘 (Dashboard) ---
class DashboardInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.v_layout = QVBoxLayout(self)
        self.v_layout.setContentsMargins(30, 30, 30, 30)
        self.v_layout.setSpacing(20)
        
        self.lbl_title = TitleLabel("系统概览", self)
        
        # 1. 统计卡片区
        self.cards_layout = QHBoxLayout()
        self.cards_layout.setSpacing(15)
        
        # 模拟数据
        stats = [
            (FIF.PEOPLE, "总用户数", "1,240", "+12%"),
            (FIF.EDUCATION, "活跃课程", "85", "+5%"),
            (FIF.DOCUMENT, "今日作业", "432", "+28%"),
            (FIF.FEEDBACK, "待处理工单", "12", "-2%"),
        ]
        
        for icon, title, val, growth in stats:
            card = StatCard(icon, title, val, growth)
            self.cards_layout.addWidget(card)
        self.cards_layout.addStretch(1) # 左对齐
        
        # 2. 模拟图表区 (使用 Progress Bar 模拟数据分布，因为不想引入 Matplotlib 增加复杂性)
        self.chart_card = CardWidget(self)
        self.chart_card.setFixedHeight(300)
        chart_layout = QVBoxLayout(self.chart_card)
        chart_layout.setContentsMargins(30,30,30,30)
        
        chart_layout.addWidget(SubtitleLabel("存储空间使用情况", self.chart_card))
        chart_layout.addSpacing(20)
        
        # 模拟几个进度条
        items = [("数据库 (PostgreSQL)", 75), ("文件存储 (S3)", 45), ("日志归档", 20)]
        for name, val in items:
            h_layout = QHBoxLayout()
            lbl = BodyLabel(name, self.chart_card)
            lbl.setFixedWidth(150)
            pb = ProgressBar(self.chart_card)
            pb.setValue(val)
            h_layout.addWidget(lbl)
            h_layout.addWidget(pb)
            chart_layout.addLayout(h_layout)
            chart_layout.addSpacing(10)
            
        chart_layout.addStretch(1)

        self.v_layout.addWidget(self.lbl_title)
        self.v_layout.addLayout(self.cards_layout)
        self.v_layout.addWidget(self.chart_card)
        self.v_layout.addStretch(1)

# --- 界面 2：用户管理表格 (User Management) ---
class UserTableInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.v_layout = QVBoxLayout(self)
        self.v_layout.setContentsMargins(30, 30, 30, 30)
        
        # 顶部工具栏
        tool_layout = QHBoxLayout()
        self.search_bar = LineEdit(self)
        self.search_bar.setPlaceholderText("搜索用户名或学号...")
        self.search_bar.setFixedWidth(300)
        self.btn_add = PrimaryPushButton(FIF.ADD, "添加学生", self)
        self.btn_export = PushButton(FIF.DOWNLOAD, "导出数据", self)
        
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
        
        # 填充模拟数据
        users = [
            ("2023001", "张伟", "计算机科学", "活跃"),
            ("2023002", "李娜", "数字媒体", "活跃"),
            ("2023003", "Mike Ross", "法律", "休学"),
            ("2023004", "Jessica", "工商管理", "活跃"),
            ("2023005", "Harvey", "金融学", "警告"),
        ]
        
        self.table.setRowCount(len(users))
        for i, row_data in enumerate(users):
            for j, val in enumerate(row_data):
                self.table.setItem(i, j, QTableWidgetItem(val))
            # 最后一列操作按钮 (这里仅放文本模拟，实际可放 Widget)
            self.table.setItem(i, 4, QTableWidgetItem("编辑 | 删除"))

        # 设置表头自适应
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.v_layout.addWidget(TitleLabel("学生信息管理", self))
        self.v_layout.addSpacing(10)
        self.v_layout.addLayout(tool_layout)
        self.v_layout.addSpacing(10)
        self.v_layout.addWidget(self.table)

# --- 主窗口：管理员后台 ---
class AdminWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EduAdmin - 教务管理后台")
        self.resize(1200, 800)
        self.windowEffect.setMicaEffect(self.winId())
        
        # 初始化子页面
        self.dashboard = DashboardInterface(self)
        self.user_interface = UserTableInterface(self)
        
        # 设置 objectName（必须，否则 addSubInterface 会报错）
        self.dashboard.setObjectName("dashboard")
        self.user_interface.setObjectName("user_management")
        
        # 创建占位页面
        self.course_page = QWidget()
        self.course_page.setObjectName("course_management")
        self.setting_page = QWidget()
        self.setting_page.setObjectName("system_setting")
        
        # 添加导航
        self.addSubInterface(self.dashboard, FIF.HOME, "仪表盘")
        self.addSubInterface(self.user_interface, FIF.PEOPLE, "学生管理")
        self.addSubInterface(self.course_page, FIF.BOOK_SHELF, "课程管理")
        self.navigationInterface.addSeparator()
        self.addSubInterface(self.setting_page, FIF.SETTING, "系统设置")

# --- 独立窗口：登录/注册页 ---
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("登录")
        self.resize(1000, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 布局容器
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        
        # 左侧：装饰图片区域
        self.left_panel = QFrame()
        self.left_panel.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d; 
                border-top-left-radius: 10px;
                border-bottom-left-radius: 10px;
            }
        """)
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 使用 IconWidget 来显示图标，而不是 ImageLabel
        logo = IconWidget(FIF.EDUCATION, self.left_panel)
        logo.setFixedSize(100, 100)
        
        welcome_lbl = TitleLabel("Edu Space", self.left_panel)
        welcome_lbl.setStyleSheet("color: white; font-family: 'Segoe UI';")
        
        left_layout.addWidget(logo)
        left_layout.addWidget(welcome_lbl)
        
        # 右侧：表单区域
        self.right_panel = QFrame()
        self.right_panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
            }
        """)
        
        # 关闭按钮 (自定义)
        self.close_btn = PushButton("×", self.right_panel)
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.move(460, 10) # 绝对定位
        
        self.form_layout = QVBoxLayout(self.right_panel)
        self.form_layout.setContentsMargins(60, 60, 60, 60)
        self.form_layout.setSpacing(15)
        
        # 标题
        self.title = SubtitleLabel("欢迎回来", self.right_panel)
        self.title.setStyleSheet("color: #333;")
        
        # 输入框
        self.user_input = LineEdit(self.right_panel)
        self.user_input.setPlaceholderText("用户名 / 邮箱")
        self.user_input.setClearButtonEnabled(True)
        
        self.pwd_input = LineEdit(self.right_panel)
        self.pwd_input.setPlaceholderText("密码")
        self.pwd_input.setEchoMode(LineEdit.EchoMode.Password)
        self.pwd_input.setClearButtonEnabled(True)
        
        # 记住我 & 忘记密码
        opt_layout = QHBoxLayout()
        self.remember_cb = CheckBox("记住我", self.right_panel)
        self.forget_btn = HyperlinkButton("http://localhost", "忘记密码?", self.right_panel)
        opt_layout.addWidget(self.remember_cb)
        opt_layout.addStretch(1)
        opt_layout.addWidget(self.forget_btn)
        
        # 登录按钮
        self.login_btn = PrimaryPushButton("登录", self.right_panel)
        self.login_btn.setFixedHeight(40)
        self.login_btn.clicked.connect(self.on_login)
        
        # 切换注册
        self.switch_btn = HyperlinkButton("#", "没有账号？点击注册", self.right_panel)
        self.switch_btn.clicked.connect(self.toggle_mode)

        # 添加到表单
        self.form_layout.addStretch(1)
        self.form_layout.addWidget(self.title)
        self.form_layout.addSpacing(20)
        self.form_layout.addWidget(self.user_input)
        self.form_layout.addWidget(self.pwd_input)
        self.form_layout.addLayout(opt_layout)
        self.form_layout.addSpacing(10)
        self.form_layout.addWidget(self.login_btn)
        self.form_layout.addWidget(self.switch_btn)
        self.form_layout.addStretch(1)

        layout.addWidget(self.left_panel, 1)
        layout.addWidget(self.right_panel, 1)

        # 窗口阴影
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.shadow.setOffset(0, 0)
        self.right_panel.setGraphicsEffect(self.shadow)
        
        self.is_login_mode = True

    def toggle_mode(self):
        if self.is_login_mode:
            self.title.setText("创建新账号")
            self.login_btn.setText("注册并登录")
            self.switch_btn.setText("已有账号？直接登录")
            self.remember_cb.hide()
            self.forget_btn.hide()
        else:
            self.title.setText("欢迎回来")
            self.login_btn.setText("登录")
            self.switch_btn.setText("没有账号？点击注册")
            self.remember_cb.show()
            self.forget_btn.show()
        self.is_login_mode = not self.is_login_mode

    def on_login(self):
        user = self.user_input.text()
        pwd = self.pwd_input.text()
        
        if not user or not pwd:
            InfoBar.error("错误", "请输入用户名和密码", duration=2000, parent=self.right_panel)
            return
            
        # 模拟登录验证
        # 只有 admin/admin 能进入管理后台
        if user == "admin" and pwd == "admin":
            InfoBar.success("登录成功", "正在进入管理后台...", duration=1000, parent=self.right_panel)
            QTimer.singleShot(1000, self.open_admin_dashboard)
        else:
             InfoBar.warning("登录失败", "用户名或密码错误 (提示: admin/admin)", duration=2000, parent=self.right_panel)

    def open_admin_dashboard(self):
        self.close()
        # 打开主界面
        self.admin_window = AdminWindow()
        self.admin_window.show()

if __name__ == '__main__':
    # 适配高分屏
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    app = QApplication(sys.argv)
    
    # 设置浅色主题适配 Login 界面 (Login界面通常使用浅色看起来更干净)
    # 当然也可以根据需要设置为 DARK
    setTheme(Theme.LIGHT) 
    
    w = LoginWindow()
    w.show()
    
    sys.exit(app.exec())